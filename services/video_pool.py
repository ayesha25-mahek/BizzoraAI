"""
services/video_pool.py
-----------------------
VideoPool — checkpoint-based, multi-provider video generation for BizzoraAI.

Provider sequence (interleaved):
  Runway1, Luma1, Runway2, Luma2, ..., Runway5, Luma5

Two independent generation methods
───────────────────────────────────
PRIMARY  — generate_direct()
  Sends a rich text prompt straight to Runway / Luma with NO image required.
  Checkpoint logic: each successfully generated scene clip is stored immediately.
  If a provider fails on Scene N, the next provider picks up from Scene N,
  NOT from Scene 1.  All previously completed scenes are preserved.
  Raises AllProvidersExhaustedError when every provider+key combo is exhausted
  so the caller (routes.py) can switch to the FALLBACK path.

FALLBACK — generate_scenes()
  Used only when generate_direct() raises AllProvidersExhaustedError.
  Accepts a pre-generated image path per scene and converts them to video clips
  using the same Runway / Luma providers (image-to-video mode).
  Falls back further to a static PIL clip if all API providers are exhausted.
"""

import logging
import os
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MAX_KEYS = 5
CLIP_DURATION = 5  # seconds per scene clip


# ---------------------------------------------------------------------------
# Custom exception — raised when every T2V provider/key combo is exhausted
# ---------------------------------------------------------------------------

class AllProvidersExhaustedError(Exception):
    """
    Raised by VideoPool.generate_direct() when every Runway and Luma
    API key / provider combination has failed or hit its quota.
    routes.py catches this to activate the FALLBACK pipeline.
    """


# ---------------------------------------------------------------------------
# Helper: build the interleaved provider sequence
# ---------------------------------------------------------------------------

def _build_provider_sequence() -> List[Dict]:
    """
    Build the list of available providers in order:
    [Runway_1, Luma_1, Runway_2, Luma_2, ...]
    Skips any key that is empty / missing.
    """
    providers = []
    for i in range(1, MAX_KEYS + 1):
        runway_key = os.getenv(f"RUNWAY_API_KEY_{i}", "").strip()
        luma_key   = os.getenv(f"LUMA_API_KEY_{i}", "").strip()

        if runway_key:
            providers.append({"provider": "runway", "key": runway_key, "index": i})
        if luma_key:
            providers.append({"provider": "luma", "key": luma_key, "index": i})

    return providers


# ---------------------------------------------------------------------------
# Fallback: PIL static image -> video clip (no FFmpeg required)
# ---------------------------------------------------------------------------

def _image_to_video_fallback(
    image_path: str,
    output_path: str,
    duration: int = CLIP_DURATION,
) -> str:
    """
    Create a simple video clip from a static image using imageio / Pillow.
    Falls back further to just returning the image path if imageio is unavailable.
    """
    try:
        import imageio                  # type: ignore
        from PIL import Image           # type: ignore

        fps = 24
        n_frames = duration * fps

        img = Image.open(image_path).convert("RGB").resize((1280, 720))

        writer = imageio.get_writer(output_path, fps=fps)
        for _ in range(n_frames):
            import numpy as np          # type: ignore
            writer.append_data(np.array(img))
        writer.close()

        logger.info("Fallback video clip saved: %s", output_path)
        return output_path

    except Exception as exc:
        logger.warning("imageio fallback failed (%s); using placeholder path.", exc)
        return image_path


# ---------------------------------------------------------------------------
# PRIMARY path — Runway text-to-video (no image required)
# ---------------------------------------------------------------------------

def _generate_runway_text_to_video(
    key: str,
    prompt: str,
    output_path: str,
    duration: int = CLIP_DURATION,
) -> str:
    """
    Generate a video clip using Runway ML text-to-video.
    No keyframe image is supplied — purely prompt-driven generation.
    """
    try:
        import runwayml  # type: ignore
    except ImportError:
        raise RuntimeError("runwayml package not installed.")

    client = runwayml.RunwayML(api_key=key)

    task = client.image_to_video.create(
        model="gen3a_turbo",
        prompt_text=prompt,          # text-only — no prompt_image
        duration=duration,
        ratio="1280:720",
    )

    # Poll for completion (max 5 min)
    task_id = task.id
    for _ in range(60):
        time.sleep(5)
        task = client.tasks.retrieve(task_id)
        if task.status == "SUCCEEDED":
            break
        if task.status in ("FAILED", "CANCELLED"):
            raise RuntimeError(f"Runway task {task_id} failed: {task.failure}")

    if not task.output:
        raise RuntimeError("Runway returned no output.")

    video_url = task.output[0]

    import requests  # type: ignore
    resp = requests.get(video_url, timeout=120)
    resp.raise_for_status()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(resp.content)

    return output_path


# ---------------------------------------------------------------------------
# PRIMARY path — Luma text-to-video (no image required)
# ---------------------------------------------------------------------------

def _generate_luma_text_to_video(
    key: str,
    prompt: str,
    output_path: str,
    duration: int = CLIP_DURATION,
) -> str:
    """
    Generate a video clip using Luma AI text-to-video.
    No keyframe image is supplied — purely prompt-driven generation.
    """
    try:
        import lumaai  # type: ignore
    except ImportError:
        raise RuntimeError("lumaai package not installed.")

    client = lumaai.LumaAI(auth_token=key)

    generation = client.generations.create(
        prompt=prompt,
        model="ray-2",
        aspect_ratio="16:9",
        loop=False,
        # No keyframes -> pure text-to-video
    )

    # Poll for completion (max 5 min)
    gen_id = generation.id
    for _ in range(60):
        time.sleep(5)
        generation = client.generations.get(gen_id)
        if generation.state == "completed":
            break
        if generation.state == "failed":
            raise RuntimeError(
                f"Luma generation {gen_id} failed: {generation.failure_reason}"
            )

    if not generation.assets or not generation.assets.video:
        raise RuntimeError("Luma returned no video asset.")

    video_url = generation.assets.video

    import requests  # type: ignore
    resp = requests.get(video_url, timeout=120)
    resp.raise_for_status()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(resp.content)

    return output_path


# ---------------------------------------------------------------------------
# FALLBACK path — Runway image-to-video
# ---------------------------------------------------------------------------

def _generate_runway(
    key: str,
    image_path: str,
    prompt: str,
    output_path: str,
    duration: int = CLIP_DURATION,
) -> str:
    """Generate a video clip using Runway ML (image-to-video). Used in FALLBACK only."""
    try:
        import runwayml  # type: ignore
    except ImportError:
        raise RuntimeError("runwayml package not installed.")

    client = runwayml.RunwayML(api_key=key)

    with open(image_path, "rb") as f:
        import base64
        img_b64 = base64.b64encode(f.read()).decode()

    ext = Path(image_path).suffix.lstrip(".")
    data_uri = f"data:image/{ext};base64,{img_b64}"

    task = client.image_to_video.create(
        model="gen3a_turbo",
        prompt_image=data_uri,
        prompt_text=prompt,
        duration=duration,
        ratio="16:9",
    )

    # Poll for completion (max 5 min)
    task_id = task.id
    for _ in range(60):
        time.sleep(5)
        task = client.tasks.retrieve(task_id)
        if task.status == "SUCCEEDED":
            break
        if task.status in ("FAILED", "CANCELLED"):
            raise RuntimeError(f"Runway task {task_id} failed: {task.failure}")

    if not task.output:
        raise RuntimeError("Runway returned no output.")

    video_url = task.output[0]

    import requests  # type: ignore
    resp = requests.get(video_url, timeout=120)
    resp.raise_for_status()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(resp.content)

    return output_path


# ---------------------------------------------------------------------------
# FALLBACK path — Luma image-to-video
# ---------------------------------------------------------------------------

def _generate_luma(
    key: str,
    image_path: str,
    prompt: str,
    output_path: str,
    duration: int = CLIP_DURATION,
) -> str:
    """Generate a video clip using Luma AI (image-to-video). Used in FALLBACK only."""
    try:
        import lumaai  # type: ignore
    except ImportError:
        raise RuntimeError("lumaai package not installed.")

    client = lumaai.LumaAI(auth_token=key)

    generation = client.generations.create(
        prompt=prompt,
        keyframes={
            "frame0": {
                "type": "image",
                "url": _upload_or_use_local(image_path),
            }
        },
        aspect_ratio="16:9",
        loop=False,
    )

    # Poll for completion (max 5 min)
    gen_id = generation.id
    for _ in range(60):
        time.sleep(5)
        generation = client.generations.get(gen_id)
        if generation.state == "completed":
            break
        if generation.state == "failed":
            raise RuntimeError(f"Luma generation {gen_id} failed: {generation.failure_reason}")

    if not generation.assets or not generation.assets.video:
        raise RuntimeError("Luma returned no video asset.")

    video_url = generation.assets.video

    import requests  # type: ignore
    resp = requests.get(video_url, timeout=120)
    resp.raise_for_status()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(resp.content)

    return output_path


def _upload_or_use_local(image_path: str) -> str:
    """
    Luma needs a publicly accessible URL for the keyframe image.
    If we can not provide one, we raise an informative error.
    In production you would upload to S3/GCS and return the URL here.
    """
    if image_path.startswith("http"):
        return image_path
    raise RuntimeError(
        "Luma AI requires a public URL for the keyframe image. "
        "Upload the image to a public host and pass the URL."
    )


# ---------------------------------------------------------------------------
# Helper: build a rich video prompt from a scene dict
# ---------------------------------------------------------------------------

def _build_video_prompt(scene: Dict) -> str:
    """
    Combine image_prompt and optional narration/text_overlay into a strong T2V prompt.
    """
    parts = []
    image_prompt = scene.get("image_prompt", "").strip()
    narration    = scene.get("narration", "").strip()
    text_overlay = scene.get("text_overlay", "").strip()

    if image_prompt:
        parts.append(image_prompt)
    if narration:
        parts.append(f"Narration context: {narration}")
    if text_overlay:
        parts.append(f"On-screen text: {text_overlay}")

    return " | ".join(parts) if parts else f"Scene {scene.get('scene_number', 1)}"


# ---------------------------------------------------------------------------
# Main VideoPool class
# ---------------------------------------------------------------------------

class VideoPool:
    """
    Checkpoint-based multi-provider video generation pool.

    PRIMARY path (text-to-video, no images):
        clips = pool.generate_direct(scenes, output_dir, progress_callback)
        Raises AllProvidersExhaustedError when every provider+key fails.

    FALLBACK path (image-to-video):
        clips = pool.generate_scenes(scenes, output_dir, progress_callback)
        Called by routes.py only when generate_direct() raises AllProvidersExhaustedError.
    """

    def __init__(self) -> None:
        self.providers = _build_provider_sequence()
        logger.info(
            "VideoPool initialised — %d provider slots available.",
            len(self.providers),
        )

    # -----------------------------------------------------------------------
    # PRIMARY: Direct text-to-video (no images needed)
    # -----------------------------------------------------------------------

    def generate_direct(
        self,
        scenes: List[Dict],
        output_dir: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> List[str]:
        """
        PRIMARY path — direct text-to-video generation.

        Converts each scene's image_prompt (+ optional narration / text_overlay)
        into a rich video prompt and sends it straight to Runway or Luma.
        No images are required or generated.

        Checkpoint logic:
          - Each successfully generated clip is stored immediately.
          - A provider failure on Scene N advances the provider index and retries
            Scene N with the next provider — completed scenes are NOT restarted.
          - If ALL providers are exhausted for any single scene, raises
            AllProvidersExhaustedError so the caller activates the FALLBACK.

        Args:
            scenes:            List of scene dicts (scene_number, image_prompt,
                               duration_seconds, optionally narration / text_overlay).
            output_dir:        Directory for clip files.
            progress_callback: Optional fn(scene_number, total, message).

        Returns:
            Ordered list of clip file paths (one per scene).

        Raises:
            AllProvidersExhaustedError: when every provider+key fails.
        """
        if not self.providers:
            raise AllProvidersExhaustedError(
                "No Runway or Luma API keys configured. "
                "Set RUNWAY_API_KEY_N / LUMA_API_KEY_N in .env"
            )

        os.makedirs(output_dir, exist_ok=True)

        total = len(scenes)
        completed: Dict[int, str] = {}   # scene_number -> clip_path
        provider_index = 0               # global across scenes (checkpoint logic)

        for scene in scenes:
            scene_num   = scene.get("scene_number", 0)
            duration    = scene.get("duration_seconds", CLIP_DURATION)
            output_path = os.path.join(output_dir, f"clip_direct_{scene_num:02d}.mp4")
            prompt      = _build_video_prompt(scene)

            if scene_num in completed:
                logger.info("Scene %d already completed — skipping.", scene_num)
                continue

            scene_done = False

            while provider_index < len(self.providers):
                prov      = self.providers[provider_index]
                prov_name = f"{prov['provider'].title()} key {prov['index']}"
                logger.info(
                    "Scene %d (direct T2V) — trying %s", scene_num, prov_name
                )

                try:
                    if prov["provider"] == "runway":
                        clip = _generate_runway_text_to_video(
                            prov["key"], prompt, output_path, duration
                        )
                    else:
                        clip = _generate_luma_text_to_video(
                            prov["key"], prompt, output_path, duration
                        )

                    completed[scene_num] = clip
                    scene_done = True
                    logger.info(
                        "Scene %d (direct T2V) succeeded with %s", scene_num, prov_name
                    )
                    if progress_callback:
                        progress_callback(
                            scene_num, total,
                            f"Scene {scene_num} generated via {prov_name} (direct T2V)"
                        )
                    # Keep provider_index at the working provider for next scene
                    break

                except Exception as exc:
                    logger.warning(
                        "Scene %d (direct T2V) failed with %s: %s — advancing provider.",
                        scene_num, prov_name, exc,
                    )
                    provider_index += 1  # checkpoint: only advance on failure

            if not scene_done:
                raise AllProvidersExhaustedError(
                    f"All Runway/Luma providers exhausted at Scene {scene_num}. "
                    "Switching to FALLBACK pipeline."
                )

        return [completed[s["scene_number"]] for s in scenes if s["scene_number"] in completed]

    # -----------------------------------------------------------------------
    # FALLBACK: Image-to-video (requires pre-generated images per scene)
    # -----------------------------------------------------------------------

    def generate_scenes(
        self,
        scenes: List[Dict],
        output_dir: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> List[str]:
        """
        FALLBACK path — image-to-video generation.

        Called only when generate_direct() raises AllProvidersExhaustedError.
        Each scene must have a valid `image_path`. Uses the same Runway / Luma
        providers in image-to-video mode. Falls back further to a static PIL
        clip if all API providers are exhausted.

        Checkpoint logic is identical to the PRIMARY path — completed scenes are
        never restarted when a provider fails mid-batch.

        Args:
            scenes:            List of scene dicts, each with:
                               { scene_number, image_path, image_prompt,
                                 duration_seconds }
            output_dir:        Directory to save clip files.
            progress_callback: Optional fn(scene_number, total, message).

        Returns:
            Ordered list of clip file paths (one per scene).
        """
        os.makedirs(output_dir, exist_ok=True)

        total = len(scenes)
        completed: Dict[int, str] = {}   # scene_number -> clip_path
        provider_index = 0               # global across scenes (checkpoint logic)

        for scene in scenes:
            scene_num   = scene.get("scene_number", 0)
            image_path  = scene.get("image_path", "")
            prompt      = scene.get("image_prompt", f"Scene {scene_num}")
            duration    = scene.get("duration_seconds", CLIP_DURATION)
            output_path = os.path.join(output_dir, f"clip_scene_{scene_num:02d}.mp4")

            if scene_num in completed:
                logger.info("Scene %d already completed — skipping.", scene_num)
                continue

            if not image_path or not os.path.exists(image_path):
                logger.warning(
                    "Scene %d: image not found at %s — using static-image fallback.",
                    scene_num, image_path,
                )
                result = _image_to_video_fallback(image_path or "", output_path, duration)
                completed[scene_num] = result
                if progress_callback:
                    progress_callback(
                        scene_num, total,
                        f"Scene {scene_num} generated (static-image fallback)"
                    )
                continue

            scene_done = False
            while provider_index < len(self.providers):
                prov      = self.providers[provider_index]
                prov_name = f"{prov['provider'].title()} key {prov['index']}"
                logger.info(
                    "Scene %d (image-to-video) — trying %s", scene_num, prov_name
                )

                try:
                    if prov["provider"] == "runway":
                        clip = _generate_runway(
                            prov["key"], image_path, prompt, output_path, duration
                        )
                    else:
                        clip = _generate_luma(
                            prov["key"], image_path, prompt, output_path, duration
                        )

                    completed[scene_num] = clip
                    scene_done = True
                    logger.info(
                        "Scene %d (image-to-video) succeeded with %s", scene_num, prov_name
                    )
                    if progress_callback:
                        progress_callback(
                            scene_num, total,
                            f"Scene {scene_num} generated via {prov_name} (image-to-video)"
                        )
                    break

                except Exception as exc:
                    logger.warning(
                        "Scene %d (image-to-video) failed with %s: %s — advancing provider.",
                        scene_num, prov_name, exc,
                    )
                    provider_index += 1

            if not scene_done:
                logger.warning(
                    "Scene %d: all providers exhausted. Using static-image fallback.",
                    scene_num,
                )
                result = _image_to_video_fallback(image_path, output_path, duration)
                completed[scene_num] = result
                if progress_callback:
                    progress_callback(
                        scene_num, total,
                        f"Scene {scene_num} completed (static-image fallback)"
                    )

        return [completed[s["scene_number"]] for s in scenes if s["scene_number"] in completed]
