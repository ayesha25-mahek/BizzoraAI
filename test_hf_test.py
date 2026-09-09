import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("HF_TOKEN")

if not token:
    raise ValueError("HF_TOKEN not found in .env")

client = InferenceClient(
    provider="fal-ai",
    api_key=token
)

input_image = "your_restaurant_photo.jpg"

prompt = """
Transform this restaurant photo into a premium
commercial advertisement scene.

Preserve the actual restaurant identity,
architecture and important visual details.

Create an energetic, appetizing atmosphere.
Make the food look premium and professionally
photographed.

Do not replace the restaurant with a different one.
Do not invent a different logo.

Leave clean space for advertisement text.
Instagram advertising style.
Landscape composition.
"""

print("Generating advertisement...")

with open(input_image, "rb") as f:
    image_bytes = f.read()

result = client.image_to_image(
    image_bytes,
    prompt=prompt,
    model="black-forest-labs/FLUX.2-klein-9B"
)

result.save("restaurant_ad.png")

print("SUCCESS!")
print("Saved: restaurant_ad.png")