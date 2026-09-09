import os
import base64
from pathlib import Path

from dotenv import load_dotenv
from google import genai


load_dotenv()


class AdImageGenerator:

    def __init__(self):

        # ---------------------------------------------
        # API KEY
        # ---------------------------------------------

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in .env file"
            )

        # ---------------------------------------------
        # GEMINI CLIENT
        # ---------------------------------------------

        self.client = genai.Client(
            api_key=api_key
        )

        # ---------------------------------------------
        # IMAGE MODEL
        # ---------------------------------------------

        self.model = "gemini-3.1-flash-image"

        # ---------------------------------------------
        # OUTPUT DIRECTORY
        # ---------------------------------------------

        self.output_dir = Path(
            "output/images"
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    # =================================================
    # MIME TYPE
    # =================================================

    def get_mime_type(self, filepath):

        extension = Path(
            filepath
        ).suffix.lower()

        mime_types = {

            ".png": "image/png",

            ".jpg": "image/jpeg",

            ".jpeg": "image/jpeg",

            ".webp": "image/webp"
        }

        if extension not in mime_types:

            raise ValueError(
                f"Unsupported image format: {extension}"
            )

        return mime_types[extension]

    # =================================================
    # LOAD IMAGE
    # =================================================

    def load_image(self, filepath):

        filepath = str(filepath)

        with open(
            filepath,
            "rb"
        ) as file:

            image_bytes = file.read()

        return {

            "type": "image",

            "data": base64.b64encode(
                image_bytes
            ).decode("utf-8"),

            "mime_type": self.get_mime_type(
                filepath
            )
        }

    # =================================================
    # GENERATE AD IMAGE
    # =================================================

    def generate(
        self,
        prompt,
        reference_images,
        output_filename="ad.jpg"
    ):

        # ---------------------------------------------
        # CHECK IMAGES
        # ---------------------------------------------

        if not reference_images:

            raise ValueError(
                "No reference images were provided."
            )

        print(
            "\nPreparing reference images..."
        )

        # ---------------------------------------------
        # CREATE INPUT
        # ---------------------------------------------

        inputs = [

            {
                "type": "text",
                "text": prompt
            }

        ]

        # ---------------------------------------------
        # ADD USER IMAGES
        # ---------------------------------------------

        valid_images = 0

        for image_path in reference_images:

            if not os.path.exists(image_path):

                print(
                    f"WARNING: File not found:"
                    f" {image_path}"
                )

                continue

            print(
                f"[SUCCESS] Adding reference:"
                f" {image_path}"
            )

            image_data = self.load_image(
                image_path
            )

            inputs.append(
                image_data
            )

            valid_images += 1

        # ---------------------------------------------
        # CHECK
        # ---------------------------------------------

        if valid_images == 0:

            raise ValueError(
                "None of the selected images could be found."
            )

        print(
            f"\n{valid_images} reference image(s) loaded."
        )

        # ---------------------------------------------
        # GENERATE
        # ---------------------------------------------

        print(
            "\nGenerating advertisement..."
        )

        print(
            "Please wait...\n"
        )

        interaction = (
            self.client.interactions.create(

                model=self.model,

                input=inputs,

                response_format={

                    "type": "image",

                    # Gemini currently expects JPEG here
                    "mime_type": "image/jpeg",

                    "aspect_ratio": "16:9",

                    "image_size": "2K"
                }
            )
        )

        # ---------------------------------------------
        # CHECK RESPONSE
        # ---------------------------------------------

        if not interaction.output_image:

            raise RuntimeError(
                "Gemini did not return an image."
            )

        # ---------------------------------------------
        # OUTPUT FILE
        # ---------------------------------------------

        output_path = (
            self.output_dir /
            output_filename
        )

        # ---------------------------------------------
        # DECODE IMAGE
        # ---------------------------------------------

        image_bytes = base64.b64decode(
            interaction.output_image.data
        )

        # ---------------------------------------------
        # SAVE
        # ---------------------------------------------

        with open(
            output_path,
            "wb"
        ) as file:

            file.write(image_bytes)

        print(
            "\n===================================="
        )

        print(
            "[SUCCESS] Advertisement generated!"
        )

        print(
            f"[SUCCESS] Saved at:"
            f" {output_path}"
        )

        print(
            "====================================\n"
        )

        return str(output_path)


# =====================================================
# SIMPLE FUNCTION
# =====================================================

def generate_ad_image(
    prompt,
    reference_images,
    output_filename="ad.jpg"
):

    generator = AdImageGenerator()

    return generator.generate(

        prompt=prompt,

        reference_images=reference_images,

        output_filename=output_filename
    )