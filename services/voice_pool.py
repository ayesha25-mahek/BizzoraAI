"""
services/voice_pool.py
-----------------------
VoicePool — multi-provider, sequential-fallback text-to-speech generator.

Provider priority:
  1. ElevenLabs API — ELEVENLABS_API_KEY_1...5
     Voice: Rachel (ID: 21m00Tcm4TlvDq8ikWAM)
  2. edge-tts (Microsoft Azure TTS via edge-tts library) — free, no key
     Voice: en-US-JennyNeural

Usage:
    pool = VoicePool()
    path = await pool.generate(
        text="Hello world, this is a voice-over.",
        output_path="output/audio/scene_01.mp3",
    )

    # Sync wrapper also available:
    path = pool.generate_sync(text, output_path)
"""

import asyncio
import logging
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# ElevenLabs constants
# ---------------------------------------------------------------------------
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel
ELEVENLABS_TTS_URL  = (
    f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
)
ELEVENLABS_HEADERS_BASE = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
}

# edge-tts voice to use as final fallback
EDGE_TTS_VOICE = "en-US-JennyNeural"

MAX_KEYS = 5
REQUEST_TIMEOUT = 60  # seconds


class VoicePool:
    """
    Sequential multi-provider TTS pool.

    Reads ELEVENLABS_API_KEY_1..5 from the environment, skipping empty ones.
    Falls back to edge-tts (free, offline-capable) if all ElevenLabs keys
    are exhausted or unavailable.
    """

    def __init__(self) -> None:
        # Collect ElevenLabs API keys (skip empty / missing)
        self.elevenlabs_keys: list = []
        for i in range(1, MAX_KEYS + 1):
            key = os.getenv(f"ELEVENLABS_API_KEY_{i}", "").strip()
            if key:
                self.elevenlabs_keys.append(key)

        # Check if edge-tts is installed (optional library)
        try:
            import edge_tts as _edge_tts_module  # noqa: F401
            self._edge_tts_available = True
        except ImportError:
            self._edge_tts_available = False
            logger.warning(
                "edge-tts library not installed; it won't be available as fallback. "
                "Install with: pip install edge-tts"
            )

        logger.info(
            "VoicePool initialised — ElevenLabs keys: %d, edge-tts available: %s",
            len(self.elevenlabs_keys),
            self._edge_tts_available,
        )

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _ensure_parent_dir(self, output_path: str) -> None:
        """Create parent directories for output_path if they don't exist."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    def _try_elevenlabs(
        self,
        api_key: str,
        idx: int,
        text: str,
        output_path: str,
    ) -> str:
        """
        Attempt TTS via ElevenLabs REST API.
        Returns output_path on success; raises on any error.
        """
        logger.info(
            "Trying ElevenLabs key %d (%s...)...", idx, api_key[:8]
        )
        headers = {**ELEVENLABS_HEADERS_BASE, "xi-api-key": api_key}
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            },
        }
        resp = requests.post(
            ELEVENLABS_TTS_URL,
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )

        if resp.status_code in (401, 422):
            raise RuntimeError(
                f"ElevenLabs key {idx} invalid / quota exceeded: "
                f"HTTP {resp.status_code} — {resp.text[:200]}"
            )
        if resp.status_code == 429:
            raise RuntimeError(
                f"ElevenLabs key {idx} rate-limited: HTTP 429"
            )
        resp.raise_for_status()

        # Response should be audio/mpeg bytes
        content_type = resp.headers.get("Content-Type", "")
        if "audio" not in content_type and len(resp.content) < 500:
            raise RuntimeError(
                f"ElevenLabs key {idx} returned unexpected content: "
                f"{resp.text[:200]}"
            )

        self._ensure_parent_dir(output_path)
        with open(output_path, "wb") as fh:
            fh.write(resp.content)

        logger.info("ElevenLabs key %d succeeded -> %s", idx, output_path)
        return output_path

    async def _try_edge_tts(self, text: str, output_path: str) -> str:
        """
        Async TTS via edge-tts (Microsoft edge neural voices — free).
        Returns output_path on success.
        """
        import edge_tts  # type: ignore

        logger.info("Falling back to edge-tts (voice: %s)...", EDGE_TTS_VOICE)
        self._ensure_parent_dir(output_path)
        communicate = edge_tts.Communicate(text, EDGE_TTS_VOICE)
        await communicate.save(output_path)
        logger.info("edge-tts succeeded -> %s", output_path)
        return output_path

    # -----------------------------------------------------------------------
    # Public API — async
    # -----------------------------------------------------------------------

    async def generate(self, text: str, output_path: str) -> str:
        """
        Generate TTS audio asynchronously.

        Tries ElevenLabs keys in order, then falls back to edge-tts.
        Returns the path of the saved audio file.
        Raises RuntimeError only if all providers fail.
        """
        errors = []

        # --- ElevenLabs (blocking HTTP — run in thread) ---
        for idx, key in enumerate(self.elevenlabs_keys, start=1):
            try:
                return await asyncio.to_thread(
                    self._try_elevenlabs, key, idx, text, output_path
                )
            except Exception as exc:
                msg = f"ElevenLabs key {idx}: {exc}"
                logger.warning(msg)
                errors.append(msg)

        # --- edge-tts fallback ---
        if self._edge_tts_available:
            try:
                return await self._try_edge_tts(text, output_path)
            except Exception as exc:
                errors.append(f"edge-tts: {exc}")

        raise RuntimeError(
            "VoicePool: All TTS providers failed.\n" + "\n".join(errors)
        )

    # -----------------------------------------------------------------------
    # Public API — sync wrapper (for non-async callers)
    # -----------------------------------------------------------------------

    def generate_sync(self, text: str, output_path: str) -> str:
        """
        Synchronous wrapper around `.generate()`.
        Runs the async method safely regardless of whether called from a thread,
        an active event loop, or without any event loop.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, self.generate(text, output_path))
                return future.result()
        else:
            return asyncio.run(self.generate(text, output_path))

