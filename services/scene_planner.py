import os
import json
from dotenv import load_dotenv

from services.llm_provider import LLMProvider

load_dotenv()


class ScenePlanner:

    def __init__(self):

        # Provider manager handles:
        # Gemini → Groq fallback
        self.llm = LLMProvider()


    # ==================================================
    # CREATE AD PLAN
    # ==================================================

    def create_plan_from_natural_language(self, user_request):

        prompt = f"""
You are an expert AI advertising strategist.

Convert the following business advertising request
into a structured advertisement plan.

USER REQUEST:
{user_request}

Return ONLY valid JSON.
Do NOT use markdown.
Do NOT use ```json.
Do NOT add explanations before or after the JSON.

The JSON must contain:

{{
    "business_name": "",
    "business_category": "",
    "product": "",
    "offer": "",
    "language": "",
    "tone": "",
    "platform": "",
    "scenes": [
        {{
            "scene_number": 1,
            "duration_seconds": 5,
            "visual_description": "",
            "image_prompt": "",
            "text_overlay": ""
        }}
    ]
}}

IMPORTANT:

1. Understand the user's natural language request.

2. The business can be ANY type:
   restaurant,
   cafe,
   salon,
   hospital,
   clinic,
   clothing store,
   gym,
   bakery,
   hotel,
   school,
   college,
   shop,
   automobile business,
   real estate business,
   or any other business.

3. Do NOT assume information that the user did not provide.

4. Create 3 to 5 scenes.

5. Make sure the total scene duration matches
   the requested advertisement duration when provided.

6. Each scene must have a clear visual description.

7. Each scene must have a detailed image_prompt
   suitable for an AI image generation model.

8. If the user mentions uploaded/reference images,
   instruct the image generation stage to preserve
   the actual business/product identity.

9. Do not invent a different business name,
   product, logo, price, or offer.

10. Text overlays must be short and suitable
    for advertisements.

11. The advertisement should be suitable for
    the requested platform.

12. If the user requests a language such as Hindi,
    Telugu, Tamil, Kannada, or Roman Telugu,
    generate the advertisement text in that language.

13. If language is not specified, use the language
    naturally implied by the user's request.

14. Make the scenes visually connected so that
    they can later be converted into a complete
    advertisement video.

USER REQUEST:
{user_request}
"""

        print("\n[AI] Generating advertisement strategy...")

        # IMPORTANT:
        # Gemini is tried first.
        # Groq is automatically used if Gemini fails.
        text = self.llm.generate(prompt)

        if not text:
            raise RuntimeError(
                "LLM returned an empty response."
            )

        # --------------------------------------------------
        # CLEAN JSON RESPONSE
        # --------------------------------------------------

        text = text.strip()

        if text.startswith("```json"):
            text = text[len("```json"):].strip()

        elif text.startswith("```"):
            text = text[len("```"):].strip()

        if text.endswith("```"):
            text = text[:-3].strip()

        # --------------------------------------------------
        # CONVERT JSON STRING → PYTHON DICTIONARY
        # --------------------------------------------------

        try:

            plan = json.loads(text)

        except json.JSONDecodeError as e:

            print("\n❌ Invalid JSON returned by LLM.")
            print("\nRaw response:")
            print(text)

            raise ValueError(
                f"Scene Planner received invalid JSON: {e}"
            )

        return plan


    # ==================================================
    # PRINT PLAN
    # ==================================================

    def print_plan(self, plan):

        print("\n")
        print("=" * 60)
        print("              GENERATED AD PLAN")
        print("=" * 60)

        print(f"\nBusiness: {plan.get('business_name', '')}")
        print(f"Category: {plan.get('business_category', '')}")
        print(f"Product: {plan.get('product', '')}")
        print(f"Offer: {plan.get('offer', '')}")
        print(f"Language: {plan.get('language', '')}")
        print(f"Tone: {plan.get('tone', '')}")
        print(f"Platform: {plan.get('platform', '')}")

        print("\nSCENES")
        print("-" * 60)

        for scene in plan.get("scenes", []):

            print(
                f"\nScene {scene.get('scene_number', '')}"
            )

            print(
                f"Duration: "
                f"{scene.get('duration_seconds', '')} sec"
            )

            print(
                f"Visual: "
                f"{scene.get('visual_description', '')}"
            )

            print(
                f"Image prompt: "
                f"{scene.get('image_prompt', '')}"
            )

            print(
                f"Text: "
                f"{scene.get('text_overlay', '')}"
            )


    # ==================================================
    # SAVE PLAN
    # ==================================================

    def save_plan(self, plan, filename):

        os.makedirs(
            "output/plans",
            exist_ok=True
        )

        path = os.path.join(
            "output/plans",
            filename
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                plan,
                f,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"\n[SUCCESS] Plan saved to: {path}"
        )

        return path