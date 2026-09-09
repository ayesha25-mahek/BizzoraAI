import os
import requests
from PIL import Image
from io import BytesIO
from urllib.parse import quote
from dotenv import load_dotenv
from google import genai

load_dotenv()


class FreeImageGenerator:
    """
    Free AI image generation for advertisements.

    Uses:
    - Gemini: converts the user's advertisement request into visual scenes
    - Pollinations: generates images for those scenes
    """

    def __init__(self):
        self.output_dir = "output/images"
        os.makedirs(self.output_dir, exist_ok=True)

        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

        self.base_url = "https://image.pollinations.ai/prompt/"

    # ---------------------------------------------------------
    # 1. Convert user request into visual scenes
    # ---------------------------------------------------------

    def create_visual_scenes(self, user_request, ad_script):
        """
        Ask Gemini to decide what visuals are needed for the advertisement.
        """

        prompt = f"""
You are an expert advertising video director.

USER'S ADVERTISEMENT REQUEST:
{user_request}

GENERATED AD SCRIPT:
{ad_script}

Create 3 visual scenes for a short advertisement.

The business can be ANY type:
restaurant, cafe, salon, hospital, clinic, gym,
clothing store, grocery store, school, hotel,
automobile business, real estate, electronics,
local shop, service business, or anything else.

For each scene:
- Describe exactly what should be visible.
- Focus on the business/product/service.
- Make the visuals suitable for a professional advertisement.
- Do not invent specific facts that are not present in the request.
- Keep the scenes visually different.
- Make them suitable for a 16:9 video.

Return ONLY 3 scene descriptions.

Format:

SCENE 1:
description

SCENE 2:
description

SCENE 3:
description
"""

        try:
            response = self.client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            return response.text.strip()

        except Exception as e:
            print(f"✗ Scene generation error: {e}")
            return None

    # ---------------------------------------------------------
    # 2. Generate image from a scene
    # ---------------------------------------------------------

    def generate_image(self, scene, filename):
        """
        Generate one image using Pollinations.
        """

        try:
            prompt = f"""
Create a high-quality professional advertisement image.

{scene}

Requirements:
- cinematic commercial photography
- realistic
- attractive lighting
- professional composition
- suitable for a business advertisement
- 16:9 landscape composition
- leave some visual space for text overlay
- no unnecessary text
- no watermark
"""

            encoded_prompt = quote(prompt)

            url = (
                f"{self.base_url}{encoded_prompt}"
                f"?width=1280"
                f"&height=720"
                f"&nologo=true"
                f"&private=true"
                f"&model=flux"
            )

            print(f"\nGenerating: {filename}")

            response = requests.get(
                url,
                timeout=120
            )

            if response.status_code != 200:
                print(
                    f"✗ Failed to generate image "
                    f"(HTTP {response.status_code})"
                )
                return None

            image = Image.open(
                BytesIO(response.content)
            )

            filepath = os.path.join(
                self.output_dir,
                filename
            )

            image.save(filepath, "PNG")

            print(f"[SUCCESS] Image saved: {filepath}")

            return image

        except requests.exceptions.Timeout:
            print("✗ Image generation timed out.")
            return None

        except Exception as e:
            print(f"✗ Image generation error: {e}")
            return None

    # ---------------------------------------------------------
    # 3. Generate all advertisement images
    # ---------------------------------------------------------

    def generate_ad_images(self, user_request, ad_script):

        print("\n" + "=" * 60)
        print("CREATING VISUAL SCENES")
        print("=" * 60)

        scenes_text = self.create_visual_scenes(
            user_request,
            ad_script
        )

        if not scenes_text:
            return {
                "success": False,
                "images": []
            }

        print("\nGenerated scenes:")
        print(scenes_text)

        # Split Gemini's response into scenes
        scenes = []

        current_scene = ""

        for line in scenes_text.splitlines():

            line = line.strip()

            if line.startswith("SCENE "):

                if current_scene:
                    scenes.append(current_scene.strip())

                current_scene = line

            else:
                current_scene += " " + line

        if current_scene:
            scenes.append(current_scene.strip())

        # Limit to 3 scenes
        scenes = scenes[:3]

        generated_images = []

        print("\n" + "=" * 60)
        print("GENERATING AD IMAGES")
        print("=" * 60)

        for index, scene in enumerate(
            scenes,
            start=1
        ):

            filename = f"scene_{index}.png"

            image = self.generate_image(
                scene,
                filename
            )

            if image:
                generated_images.append({
                    "scene": scene,
                    "image": image,
                    "path": os.path.join(
                        self.output_dir,
                        filename
                    )
                })

        return {
            "success": len(generated_images) > 0,
            "images": generated_images,
            "scenes": scenes
        }


# -------------------------------------------------------------
# Simple function
# -------------------------------------------------------------

def generate_free_images(user_request, ad_script):

    generator = FreeImageGenerator()

    return generator.generate_ad_images(
        user_request,
        ad_script
    )