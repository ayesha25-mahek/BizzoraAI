import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("HF_TOKEN")

if not token:
    raise ValueError("HF_TOKEN not found in .env")

client = InferenceClient(
    api_key=token,
    provider="fal-ai"
)

prompt = """
Create a premium food advertisement for a restaurant.
Show an extremely appetizing plate of chicken lollipop
on a stylish restaurant table.
Professional commercial photography,
cinematic lighting, realistic food photography,
Instagram advertisement quality.
"""

print("Generating image...")

image = client.text_to_image(
    prompt,
    model="black-forest-labs/FLUX.1-Krea-dev"
)

image.save("test_hf_output.png")

print("SUCCESS!")
print("Saved: test_hf_output.png")