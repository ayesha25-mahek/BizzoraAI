import os
from pathlib import Path
from tkinter import Tk, filedialog

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found in .env")

# --------------------------------------------------
# SELECT IMAGE
# --------------------------------------------------

def select_image():
    root = Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select your business/product image",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.webp"),
            ("All files", "*.*")
        ]
    )

    root.destroy()

    return file_path


print("=" * 50)
print("       HUGGING FACE IMAGE EDIT TEST")
print("=" * 50)

print("\nSelect the image you want to transform.")

image_path = select_image()

if not image_path:
    print("❌ No image selected.")
    exit()

print(f"\n✓ Selected: {image_path}")

# --------------------------------------------------
# HUGGING FACE CLIENT
# --------------------------------------------------

client = InferenceClient(
    provider="fal-ai",
    api_key=HF_TOKEN
)

# --------------------------------------------------
# PROMPT
# --------------------------------------------------

prompt = """
Transform the uploaded image into a premium commercial
advertisement scene.

Preserve the actual identity and important visual
details of the uploaded business or product.

Do not replace the main product with a different product.

Make the image look realistic, professional and
cinematic, like a high-quality advertisement.

Create attractive lighting and composition.

Leave some clean space for advertisement text.

Do not add fake logos or fake business information.

16:9 advertising composition.
"""

# --------------------------------------------------
# GENERATE
# --------------------------------------------------

print("\nGenerating advertisement...")
print("Please wait...\n")

with open(image_path, "rb") as f:
    image_bytes = f.read()

try:

    result = client.image_to_image(
        image_bytes,
        prompt=prompt,
        model="black-forest-labs/FLUX.1-Kontext-dev"
    )

    # --------------------------------------------------
    # SAVE
    # --------------------------------------------------

    output_dir = Path("output/images")
    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = output_dir / "hf_ad_test.png"

    result.save(output_path)

    print("=" * 50)
    print("✅ SUCCESS!")
    print("=" * 50)

    print(f"\nGenerated image:")
    print(output_path)

except Exception as e:

    print("=" * 50)
    print("❌ ERROR")
    print("=" * 50)

    print(e)