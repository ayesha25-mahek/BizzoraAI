import os
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()


class HFImageGenerator:

    def __init__(self):

        token = os.getenv("HF_TOKEN")

        if not token:
            raise ValueError(
                "HF_TOKEN not found in .env"
            )

        self.client = InferenceClient(
            provider="fal-ai",
            api_key=token
        )

        self.model = "black-forest-labs/FLUX.1-Kontext-dev"

        self.output_dir = Path("output/images")
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    def generate_from_reference(
        self,
        image_path,
        prompt,
        scene_number
    ):

        print(
            f"\n[Design] Generating Scene {scene_number}..."
        )

        print(
            f"Reference: {image_path}"
        )

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        image = self.client.image_to_image(
            image_bytes,
            prompt=prompt,
            model=self.model
        )

        output_path = (
            self.output_dir /
            f"scene_{scene_number}.png"
        )

        image.save(output_path)

        print(
            f"[SUCCESS] Scene {scene_number} saved: "
            f"{output_path}"
        )

        return str(output_path)