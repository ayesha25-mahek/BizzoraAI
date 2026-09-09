import os
from dotenv import load_dotenv

from services.hf_image_gen import HFImageGenerator
from services.cloudflare_image_gen import CloudflareImageGenerator


load_dotenv()


prompt = """
Create a premium food advertisement for Oak Tree Cafe.
Show crispy chicken lollipop as the hero product.
Make it extremely appetizing, realistic and energetic,
suitable for an Instagram advertisement.
"""


output_path = "output/images/fallback_test.png"

os.makedirs(
    "output/images",
    exist_ok=True
)


print("=" * 60)
print("        BIZZORAAI IMAGE FALLBACK TEST")
print("=" * 60)


# ==========================================================
# PRIMARY: HUGGING FACE
# ==========================================================

try:

    print("\n🥇 Trying Hugging Face...")

    hf = HFImageGenerator()

    result = hf.generate(
        prompt=prompt,
        output_path=output_path
    )

    if result:

        print("✓ Hugging Face succeeded")
        print(f"✓ Image saved: {output_path}")

        exit()


except Exception as e:

    print("❌ Hugging Face failed")
    print(e)


# ==========================================================
# BACKUP: CLOUDFLARE
# ==========================================================

try:

    print("\n🥈 Switching to Cloudflare...")

    cloudflare = CloudflareImageGenerator()

    result = cloudflare.generate(
        prompt=prompt,
        output_path=output_path
    )

    if result:

        print("✓ Cloudflare succeeded")
        print(f"✓ Image saved: {output_path}")

        exit()


except Exception as e:

    print("❌ Cloudflare failed")
    print(e)


# ==========================================================
# EVERYTHING FAILED
# ==========================================================

print("\n❌ All image generation providers failed.")