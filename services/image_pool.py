"""
services/image_pool.py
-----------------------
ImagePool — multi-provider, sequential-fallback image generator.

Provider priority:
  1. HuggingFace Inference API (FLUX.1-schnell) — HF_TOKEN_1...5
  2. Cloudflare Workers AI  (flux-1-schnell)    — CLOUDFLARE_ACCOUNT_ID_N + CLOUDFLARE_API_TOKEN_N pairs 1...5
  3. Pollinations.ai (free, no key needed)       — permanent fallback

Usage:
    pool = ImagePool()
    path = pool.generate(
        prompt="a serene mountain landscape",
        filename="scene_01.png",
        output_dir="output/images",
    )
"""

import base64
import logging
import os
from pathlib import Path
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
HF_API_URL = (
    "https://api-inference.huggingface.co/models/"
    "black-forest-labs/FLUX.1-schnell"
)
CF_API_URL_TEMPLATE = (
    "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/"
    "@cf/black-forest-labs/flux-1-schnell"
)
POLLINATIONS_URL_TEMPLATE = (
    "https://image.pollinations.ai/prompt/{prompt}"
    "?width=1280&height=720&nologo=true&model=flux"
)

MAX_KEYS = 5
REQUEST_TIMEOUT = 120  # seconds — image generation can be slow


class ImagePool:
    """
    Sequential multi-provider image generation pool.

    Reads credentials from environment variables, skipping any that are
    empty or incomplete.  `.generate()` works through the provider list,
    falling through to the next on any error.
    """

    def __init__(self) -> None:
        # ------------------------------------------------------------------
        # HuggingFace tokens
        # ------------------------------------------------------------------
        self.hf_tokens: list = []
        for i in range(1, MAX_KEYS + 1):
            token = os.getenv(f"HF_TOKEN_{i}", "").strip()
            if token:
                self.hf_tokens.append(token)

        # ------------------------------------------------------------------
        # Cloudflare account/token pairs
        # ------------------------------------------------------------------
        self.cf_pairs: list = []  # list of (account_id, api_token) tuples
        for i in range(1, MAX_KEYS + 1):
            account_id = os.getenv(f"CLOUDFLARE_ACCOUNT_ID_{i}", "").strip()
            api_token  = os.getenv(f"CLOUDFLARE_API_TOKEN_{i}", "").strip()
            if account_id and api_token:
                self.cf_pairs.append((account_id, api_token))

        logger.info(
            "ImagePool initialised — HF tokens: %d, CF pairs: %d",
            len(self.hf_tokens),
            len(self.cf_pairs),
        )

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _save_bytes(
        self,
        image_bytes: bytes,
        filename: str,
        output_dir: str,
    ) -> str:
        """Persist raw image bytes and return the absolute file path."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        out_path = str(Path(output_dir) / filename)
        with open(out_path, "wb") as fh:
            fh.write(image_bytes)
        return out_path

    def _try_hf(
        self,
        token: str,
        idx: int,
        prompt: str,
        filename: str,
        output_dir: str,
    ) -> str:
        """Attempt image generation via HuggingFace Inference API."""
        logger.info("Trying HuggingFace token %d (%s...)", idx, token[:8])
        resp = requests.post(
            HF_API_URL,
            headers={"Authorization": f"Bearer {token}"},
            json={"inputs": prompt},
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code in (429, 503):
            raise RuntimeError(
                f"HF token {idx} rate-limited / unavailable: HTTP {resp.status_code}"
            )
        resp.raise_for_status()

        # HF Inference API returns raw image bytes for image generation models
        content_type = resp.headers.get("Content-Type", "")
        if "image" not in content_type and len(resp.content) < 1000:
            # Likely a JSON error body rather than image data
            raise RuntimeError(
                f"HF token {idx} returned non-image response: {resp.text[:200]}"
            )

        path = self._save_bytes(resp.content, filename, output_dir)
        logger.info("HuggingFace token %d succeeded -> %s", idx, path)
        return path

    def _try_cloudflare(
        self,
        account_id: str,
        api_token: str,
        idx: int,
        prompt: str,
        filename: str,
        output_dir: str,
    ) -> str:
        """Attempt image generation via Cloudflare Workers AI."""
        logger.info("Trying Cloudflare pair %d (account: %s...)", idx, account_id[:8])
        url = CF_API_URL_TEMPLATE.format(account_id=account_id)
        resp = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json",
            },
            json={"prompt": prompt},
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code in (429, 503):
            raise RuntimeError(
                f"Cloudflare pair {idx} rate-limited: HTTP {resp.status_code}"
            )
        resp.raise_for_status()

        # CF Workers AI returns raw bytes OR {"result": {"image": "<base64>"}}
        content_type = resp.headers.get("Content-Type", "")
        if "image" in content_type:
            image_bytes = resp.content
        else:
            data = resp.json()
            if not data.get("success"):
                errors = data.get("errors", [])
                raise RuntimeError(f"Cloudflare pair {idx} error: {errors}")
            image_b64 = data["result"]["image"]
            image_bytes = base64.b64decode(image_b64)

        path = self._save_bytes(image_bytes, filename, output_dir)
        logger.info("Cloudflare pair %d succeeded -> %s", idx, path)
        return path

    def _try_pollinations(
        self,
        prompt: str,
        filename: str,
        output_dir: str,
    ) -> str:
        """Fallback: Pollinations.ai (free, no API key required)."""
        logger.info("Falling back to Pollinations.ai...")
        encoded = quote(prompt, safe="")
        url = POLLINATIONS_URL_TEMPLATE.format(prompt=encoded)
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        path = self._save_bytes(resp.content, filename, output_dir)
        logger.info("Pollinations succeeded -> %s", path)
        return path

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        filename: str,
        output_dir: str,
    ) -> str:
        """
        Generate an image from *prompt* and save it to *output_dir/filename*.

        Returns the absolute path of the saved image file.
        Raises RuntimeError only if Pollinations also fails (very unlikely).
        """
        errors = []

        # --- HuggingFace ---
        for idx, token in enumerate(self.hf_tokens, start=1):
            try:
                return self._try_hf(token, idx, prompt, filename, output_dir)
            except Exception as exc:
                msg = f"HF token {idx}: {exc}"
                logger.warning(msg)
                errors.append(msg)

        # --- Cloudflare ---
        for idx, (account_id, api_token) in enumerate(self.cf_pairs, start=1):
            try:
                return self._try_cloudflare(
                    account_id, api_token, idx, prompt, filename, output_dir
                )
            except Exception as exc:
                msg = f"Cloudflare pair {idx}: {exc}"
                logger.warning(msg)
                errors.append(msg)

        # --- Pollinations fallback (last resort, always attempted) ---
        try:
            return self._try_pollinations(prompt, filename, output_dir)
        except Exception as exc:
            errors.append(f"Pollinations: {exc}")

        raise RuntimeError(
            "ImagePool: All image providers failed.\n" + "\n".join(errors)
        )
