import os
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class CloudflareImageGenerator:

    def __init__(self):

        self.account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.api_token = os.getenv("CLOUDFLARE_API_TOKEN")

        if not self.account_id:
            raise ValueError(
                "CLOUDFLARE_ACCOUNT_ID not found in .env"
            )

        if not self.api_token:
            raise ValueError(
                "CLOUDFLARE_API_TOKEN not found in .env"
            )

        self.model = "@cf/black-forest-labs/flux-1-schnell"

        self.url = (
            f"https://api.cloudflare.com/client/v4/accounts/"
            f"{self.account_id}/ai/run/{self.model}"
        )

        self.output_dir = Path("output/images")
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )


    def generate(
        self,
        prompt,
        output_filename="cloudflare_image.png"
    ):

        print("\n☁️ Trying Cloudflare Image Generation...")

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "prompt": prompt
        }

        try:

            response = requests.post(
                self.url,
                headers=headers,
                json=payload,
                timeout=120
            )

            if response.status_code != 200:

                print(
                    f"❌ Cloudflare failed: "
                    f"{response.status_code}"
                )

                print(response.text[:500])

                return None

            result = response.json()

            if not result.get("success"):

                print("❌ Cloudflare returned an error.")
                print(result)

                return None

            image_data = result["result"]

            # Cloudflare may return base64 encoded image data
            if isinstance(image_data, dict):

                image_data = (
                    image_data.get("image")
                    or image_data.get("data")
                )

            if not image_data:

                print(
                    "❌ Cloudflare returned no image data."
                )

                return None

            image_bytes = base64.b64decode(image_data)

            output_path = (
                self.output_dir /
                output_filename
            )

            with open(output_path, "wb") as f:
                f.write(image_bytes)

            print(
                f"[SUCCESS] Cloudflare image saved: "
                f"{output_path}"
            )

            return str(output_path)

        except Exception as e:

            print(
                f"❌ Cloudflare error: {e}"
            )

            return None