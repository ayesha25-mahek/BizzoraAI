"""
api/routes.py
-------------
FastAPI router for BizzoraAI.

Endpoints:
  POST /api/generate   — SSE streaming content generation
  GET  /api/download/{filename} — serve generated files
  GET  /api/health     — health check
  GET  /api/outputs    — list supported output types with metadata
"""

import asyncio
import json
import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Output type metadata
# ---------------------------------------------------------------------------

OUTPUT_META = [
    {
        "id": "linkedin",
        "label": "LinkedIn Post",
        "description": "Professional LinkedIn post ready to publish",
        "icon": "Linkedin",
        "estimated_time": "~30 sec",
        "badge": "Popular",
    },
    {
        "id": "twitter",
        "label": "Twitter/X Post",
        "description": "Platform-optimised tweets or tweet thread",
        "icon": "Twitter",
        "estimated_time": "~20 sec",
        "badge": None,
    },
    {
        "id": "executive_summary",
        "label": "Executive Summary",
        "description": "Concise C-suite briefing document",
        "icon": "BarChart2",
        "estimated_time": "~30 sec",
        "badge": "Popular",
    },
    {
        "id": "presentation",
        "label": "Presentation",
        "description": "PPTX slides with speaker notes",
        "icon": "Presentation",
        "estimated_time": "~1 min",
        "badge": None,
    },
    {
        "id": "advisory",
        "label": "Advisory Document",
        "description": "Structured advisory with recommendations",
        "icon": "FileText",
        "estimated_time": "~45 sec",
        "badge": "New",
    },
    {
        "id": "infographic",
        "label": "Infographic",
        "description": "Key messaging and layout guide",
        "icon": "Layout",
        "estimated_time": "~45 sec",
        "badge": None,
    },
    {
        "id": "article",
        "label": "Article",
        "description": "Full-length article or blog post",
        "icon": "PenTool",
        "estimated_time": "~1 min",
        "badge": None,
    },
    {
        "id": "video",
        "label": "AI Video Package",
        "description": "Script, storyboard, scenes, narration, subtitles",
        "icon": "Video",
        "estimated_time": "3–5 min",
        "badge": "AI Video",
    },
]

SUPPORTED_OUTPUT_IDS = [m["id"] for m in OUTPUT_META]

# ---------------------------------------------------------------------------
# SSE helper
# ---------------------------------------------------------------------------

def _sse(event: str, data: dict) -> str:
    """Format a single Server-Sent Event."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


# ---------------------------------------------------------------------------
# Generator helpers (imported lazily to keep startup fast)
# ---------------------------------------------------------------------------

def _get_document_reader():
    from services.document_reader import DocumentReader
    return DocumentReader()


def _get_content_intelligence():
    from services.content_intelligence import ContentIntelligence
    # Patch to use LLMPool instead of old LLMProvider
    ci = ContentIntelligence.__new__(ContentIntelligence)
    from services.llm_pool import LLMPool
    ci.llm = LLMPool()
    return ci


def _build_router_and_generators():
    from services.output_router import OutputRouter
    from services.llm_pool import LLMPool

    pool = LLMPool()

    # LinkedIn
    from services.linkedin_generator import LinkedInGenerator
    linkedin = LinkedInGenerator.__new__(LinkedInGenerator)
    linkedin.llm = pool

    # Twitter — reuse LinkedIn generator with a twitter prompt wrapper
    from services.twitter_generator import TwitterGenerator
    twitter = TwitterGenerator.__new__(TwitterGenerator)
    twitter.llm = pool

    # Executive Summary
    from services.executive_summary_generator import ExecutiveSummaryGenerator
    exec_sum = ExecutiveSummaryGenerator.__new__(ExecutiveSummaryGenerator)
    exec_sum.llm = pool

    # Advisory
    from services.advisory_generator import AdvisoryGenerator
    advisory = AdvisoryGenerator.__new__(AdvisoryGenerator)
    advisory.llm = pool

    # Infographic
    from services.infographic_generator import InfographicGenerator
    infographic = InfographicGenerator.__new__(InfographicGenerator)
    infographic.llm = pool

    # Article
    from services.article_generator import ArticleGenerator
    article = ArticleGenerator.__new__(ArticleGenerator)
    article.llm = pool

    # Presentation
    from services.slide_planner import SlidePlanner
    from services.ppt_generator import PPTGenerator

    class PresentationGenerator:
        def __init__(self):
            self.planner = SlidePlanner.__new__(SlidePlanner)
            self.planner.llm = pool
            self.ppt = PPTGenerator()

        def generate(self, content_model, output_request):
            slide_plan = self.planner.create_slide_plan(content_model, output_request)
            filename = f"presentation_{uuid.uuid4().hex[:8]}.pptx"
            path = self.ppt.generate(slide_plan, filename)
            return {"type": "file", "path": path, "filename": filename}

    presentation = PresentationGenerator()

    # Video
    class VideoGenerator:
        def __init__(self):
            self.llm = pool

        def generate(self, content_model, output_request):
            from services.scene_planner import ScenePlanner
            from services.image_pool import ImagePool
            from services.voice_pool import VoicePool
            from services.video_pool import VideoPool, AllProvidersExhaustedError
            from services.video_composer import VideoComposer

            logger.info("Video generation started...")

            # ── STEP 1: Plan scenes (shared by both paths) ───────────────────
            # ScenePlanner structures content into scenes with narration text
            # that drives voice generation regardless of which video path runs.
            sp = ScenePlanner.__new__(ScenePlanner)
            sp.llm = pool
            scenes = sp.create_plan_from_natural_language(
                content_model.get("summary", "") + "\n" + str(content_model.get("key_points", []))
            )
            # ScenePlanner returns a dict with a "scenes" list
            scene_list = scenes.get("scenes", scenes) if isinstance(scenes, dict) else scenes

            # ── STEP 2: Voice (shared by both paths) ─────────────────────────
            vp = VoicePool()
            script = " ".join([s.get("narration", s.get("visual_description", "")) for s in scene_list])
            voice_filename = f"video_voice_{uuid.uuid4().hex[:8]}.mp3"
            voice_path = vp.generate_sync(script, f"output/audio/{voice_filename}")

            vid_pool = VideoPool()
            clip_paths = None

            # ── STEP 3a: PRIMARY — Direct Text-to-Video ──────────────────────
            # Sends the scene prompt directly to Runway / Luma. No images needed.
            try:
                logger.info("Video: attempting PRIMARY path (direct text-to-video)...")
                clip_paths = vid_pool.generate_direct(scene_list, "output/videos")
                logger.info("Video: PRIMARY path succeeded — %d clips generated.", len(clip_paths))

            except AllProvidersExhaustedError as exc:
                # ── STEP 3b: FALLBACK — Scene → Image → Video ────────────────
                # All T2V providers are exhausted. Generate images first, then
                # convert each image to a video clip via the existing pipeline.
                logger.warning(
                    "Video: PRIMARY path exhausted all providers (%s). "
                    "Activating FALLBACK pipeline (image → video).", exc
                )

                ip = ImagePool()
                image_dir = "output/images"
                for scene in scene_list:
                    p    = scene.get("image_prompt", f"Scene {scene.get('scene_number')}")
                    name = f"scene_{scene.get('scene_number')}_{uuid.uuid4().hex[:4]}.png"
                    img_path = ip.generate(p, name, image_dir)
                    scene["image_path"] = img_path

                clip_paths = vid_pool.generate_scenes(scene_list, "output/videos")
                logger.info(
                    "Video: FALLBACK path completed — %d clips generated.", len(clip_paths)
                )

            # ── STEP 4: Compose final MP4 (shared by both paths) ─────────────
            composer = VideoComposer()
            final_name = f"bizzora_video_{uuid.uuid4().hex[:8]}.mp4"
            final_path = composer.create_from_clips(clip_paths, voice_path, final_name)

            return {"type": "file", "path": final_path, "filename": final_name}

    video_gen = VideoGenerator()

    router_obj = OutputRouter()
    router_obj.register("linkedin", linkedin)
    router_obj.register("twitter", twitter)
    router_obj.register("executive_summary", exec_sum)
    router_obj.register("advisory", advisory)
    router_obj.register("infographic", infographic)
    router_obj.register("article", article)
    router_obj.register("presentation", presentation)
    router_obj.register("video", video_gen)

    return router_obj


# ---------------------------------------------------------------------------
# /api/health
# ---------------------------------------------------------------------------

@router.get("/health")
async def health():
    return {"status": "ok", "service": "BizzoraAI"}


# ---------------------------------------------------------------------------
# /api/outputs
# ---------------------------------------------------------------------------

@router.get("/outputs")
async def get_outputs():
    return OUTPUT_META


# ---------------------------------------------------------------------------
# /api/generate  — SSE streaming
# ---------------------------------------------------------------------------

@router.post("/generate")
async def generate(
    prompt: Optional[str] = Form(default=""),
    outputs: str = Form(default="[]"),
    language: str = Form(default="English"),
    tone: str = Form(default="Professional"),
    target_audience: str = Form(default="General"),
    detail_level: str = Form(default="Standard"),
    files: List[UploadFile] = File(default=[]),
):
    # Parse output types
    try:
        output_list: List[str] = json.loads(outputs)
    except Exception:
        output_list = []

    # Validate
    invalid = [o for o in output_list if o not in SUPPORTED_OUTPUT_IDS]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Unsupported output types: {invalid}")

    if not output_list:
        raise HTTPException(status_code=400, detail="Select at least one output type.")

    if not prompt and not files:
        raise HTTPException(status_code=400, detail="Provide a prompt or upload files.")

    # Save uploaded files
    upload_dir = Path("output/uploads") / uuid.uuid4().hex
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: List[str] = []

    for upload in files:
        if upload.filename:
            dest = upload_dir / upload.filename
            with open(dest, "wb") as f:
                shutil.copyfileobj(upload.file, f)
            saved_paths.append(str(dest))

    async def event_stream():
        try:
            # ── STAGE 1: Read documents ──────────────────────────────────────
            yield _sse("progress", {"stage": "reading", "message": "Reading uploaded files…", "percent": 5})

            extracted_texts = []

            if saved_paths:
                reader = await asyncio.to_thread(_get_document_reader)
                for path in saved_paths:
                    ext = Path(path).suffix.lower()
                    if ext in (".pdf", ".docx", ".pptx", ".txt"):
                        try:
                            text = await asyncio.to_thread(reader.read, path)
                            extracted_texts.append(text)
                        except Exception as e:
                            logger.warning("Could not read %s: %s", path, e)

            combined_text = "\n\n".join(filter(None, [prompt] + extracted_texts)).strip()

            if not combined_text:
                yield _sse("error", {"message": "No readable content found. Provide a text prompt or supported file."})
                return

            # ── STAGE 2: Analyse content ─────────────────────────────────────
            yield _sse("progress", {"stage": "analyzing", "message": "Analysing source content with AI…", "percent": 20})

            try:
                ci = await asyncio.to_thread(_get_content_intelligence)
                source_filenames = [Path(p).name for p in saved_paths]
                content_model = await asyncio.to_thread(ci.analyze, combined_text, source_filenames)
            except Exception as e:
                yield _sse("error", {"message": f"Content analysis failed: {e}"})
                return

            # ── STAGE 3: Build output request ────────────────────────────────
            yield _sse("progress", {"stage": "preparing", "message": "Preparing generation pipeline…", "percent": 35})

            from services.output_request import OutputRequest
            try:
                output_request = OutputRequest(
                    outputs=output_list,
                    language=language,
                    tone=tone,
                    target_audience=target_audience,
                )
            except ValueError as e:
                yield _sse("error", {"message": str(e)})
                return

            # ── STAGE 4: Generate each output ────────────────────────────────
            out_router = await asyncio.to_thread(_build_router_and_generators)

            total = len(output_list)
            for i, output_type in enumerate(output_list):
                pct = 40 + int((i / total) * 55)
                label = next((m["label"] for m in OUTPUT_META if m["id"] == output_type), output_type)
                yield _sse("progress", {
                    "stage": "generating",
                    "message": f"Generating {label}…",
                    "percent": pct,
                    "current": output_type,
                })

                try:
                    generator = out_router.generators.get(output_type)
                    if generator is None:
                        yield _sse("result", {
                            "output_type": output_type,
                            "status": "not_implemented",
                            "content": f"Generator for '{output_type}' is not yet available.",
                        })
                        continue

                    result = await asyncio.to_thread(generator.generate, content_model, output_request)

                    # Normalise result
                    if isinstance(result, str):
                        yield _sse("result", {
                            "output_type": output_type,
                            "status": "success",
                            "content": result,
                        })

                    elif isinstance(result, dict):
                        if result.get("type") == "file":
                            file_path = result.get("path", "")
                            filename  = result.get("filename", "")
                            dl_url    = f"/files/{Path(file_path).relative_to('output').as_posix()}" if file_path else ""
                            yield _sse("result", {
                                "output_type": output_type,
                                "status": "success",
                                "content": f"Your {label} has been generated.",
                                "download_url": dl_url,
                                "filename": filename,
                            })
                        else:
                            yield _sse("result", {
                                "output_type": output_type,
                                "status": "success",
                                "content": json.dumps(result, indent=2),
                            })
                    else:
                        yield _sse("result", {
                            "output_type": output_type,
                            "status": "success",
                            "content": str(result),
                        })

                except Exception as e:
                    logger.exception("Generator failed for %s", output_type)
                    yield _sse("result", {
                        "output_type": output_type,
                        "status": "error",
                        "content": f"Generation failed: {e}",
                    })

            # ── DONE ─────────────────────────────────────────────────────────
            yield _sse("progress", {"stage": "done", "message": "All outputs generated!", "percent": 100})
            yield _sse("done", {})

        except Exception as e:
            logger.exception("Unhandled error in generate stream")
            yield _sse("error", {"message": f"Unexpected error: {e}"})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# /api/download/{filepath:path}
# ---------------------------------------------------------------------------

@router.get("/download/{filepath:path}")
async def download_file(filepath: str):
    full_path = Path("output") / filepath
    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(
        path=str(full_path),
        filename=full_path.name,
        media_type="application/octet-stream",
    )
