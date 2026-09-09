"""
services/llm_pool.py
---------------------
LLMPool — multi-key, sequential fallback LLM provider for BizzoraAI.

Strategy:
  1. Try GEMINI_API_KEY_1 → GEMINI_API_KEY_5 in order.
  2. On any error move to the next key.
  3. After all Gemini keys exhausted, try GROQ_API_KEY_1 → GROQ_API_KEY_5,
     each key tries multiple Groq models in order.
  5. If every provider fails, raise RuntimeError.
"""

import logging
import os

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ─── Model names ─────────────────────────────────────────────────────────────
# Based on Google API recommendations for active models
GEMINI_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
]

# Groq models currently available on the configured API key
GROQ_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.6-27b",
    "groq/compound",
]

MAX_KEYS = 5


class LLMPool:
    """
    Sequential multi-key, multi-model LLM pool.

    Reads GEMINI_API_KEY_1..5 and GROQ_API_KEY_1..5 from the environment.
    .generate(prompt) works through every available key and model combination,
    falling through to the next on any exception.
    """

    def __init__(self) -> None:
        self.gemini_keys: list = []
        for i in range(1, MAX_KEYS + 1):
            key = os.getenv(f"GEMINI_API_KEY_{i}", "").strip()
            if key:
                self.gemini_keys.append(key)

        self.groq_keys: list = []
        for i in range(1, MAX_KEYS + 1):
            key = os.getenv(f"GROQ_API_KEY_{i}", "").strip()
            if key:
                self.groq_keys.append(key)

        if not self.gemini_keys and not self.groq_keys:
            raise RuntimeError(
                "LLMPool: No LLM API keys found. "
                "Set GEMINI_API_KEY_1 or GROQ_API_KEY_1 in .env"
            )

        logger.info(
            "LLMPool ready — Gemini keys: %d, Groq keys: %d",
            len(self.gemini_keys),
            len(self.groq_keys),
        )

    # ─── Gemini ──────────────────────────────────────────────────────────────

    def _try_gemini(self, key: str, key_idx: int, model: str, prompt: str) -> str:
        from google import genai  # type: ignore

        logger.info("Gemini key %d | model %s", key_idx, model)
        client = genai.Client(api_key=key)
        response = client.models.generate_content(model=model, contents=prompt)
        text = response.text
        if not text:
            raise ValueError("Gemini returned empty response.")
        logger.info("[SUCCESS] Gemini key %d / %s succeeded", key_idx, model)
        return text

    # ─── Groq ────────────────────────────────────────────────────────────────

    def _try_groq(self, key: str, key_idx: int, model: str, prompt: str) -> str:
        from groq import Groq  # type: ignore

        logger.info("Groq key %d | model %s", key_idx, model)
        client = Groq(api_key=key)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        text = response.choices[0].message.content
        if not text:
            raise ValueError("Groq returned empty response.")
        logger.info("[SUCCESS] Groq key %d / %s succeeded", key_idx, model)
        return text

    # ─── Public API ──────────────────────────────────────────────────────────

    def generate(self, prompt: str) -> str:
        """
        Try every Gemini key x model combo, then every Groq key x model combo.
        Raises RuntimeError only when everything fails.
        """
        errors: list = []

        # ── Gemini ──
        for idx, key in enumerate(self.gemini_keys, start=1):
            for model in GEMINI_MODELS:
                try:
                    return self._try_gemini(key, idx, model, prompt)
                except Exception as exc:
                    msg = f"Gemini key {idx} / {model} failed: {exc}"
                    logger.warning(msg)
                    errors.append(msg)

        if self.gemini_keys:
            logger.warning("All Gemini keys exhausted — switching to Groq.")

        # ── Groq ──
        for idx, key in enumerate(self.groq_keys, start=1):
            for model in GROQ_MODELS:
                try:
                    return self._try_groq(key, idx, model, prompt)
                except Exception as exc:
                    msg = f"Groq key {idx} / {model} failed: {exc}"
                    logger.warning(msg)
                    errors.append(msg)

        raise RuntimeError(
            "LLMPool: All providers and models failed.\n" + "\n".join(errors)
        )
