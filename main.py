"""
main.py  —  BizzoraAI FastAPI application entry point
"""

import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import router

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="BizzoraAI",
    description="AI-powered content transformation engine",
    version="2.0.0",
)

# ---------------------------------------------------------------------------
# CORS — allow the Vite dev server and any localhost origin
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
app.include_router(router, prefix="/api")

# ---------------------------------------------------------------------------
# Static file serving for generated output files
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/files", StaticFiles(directory=str(OUTPUT_DIR)), name="files")

# ---------------------------------------------------------------------------
# Startup: ensure all output sub-directories exist
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def create_output_dirs():
    for sub in ["uploads", "images", "videos", "audio", "plans",
                "presentations", "content", "slide_plans"]:
        (OUTPUT_DIR / sub).mkdir(parents=True, exist_ok=True)
    logger.info("BizzoraAI started — output directory ready at '%s'", OUTPUT_DIR)


# ---------------------------------------------------------------------------
# Frontend Static Files (Single Unified URL)
# ---------------------------------------------------------------------------
FRONTEND_DIST = Path("frontend/dist")
if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
else:
    @app.get("/")
    async def root():
        return {
            "service": "BizzoraAI",
            "version": "2.0.0",
            "docs": "/docs",
            "health": "/api/health",
        }


# ---------------------------------------------------------------------------
# Dev runner
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)