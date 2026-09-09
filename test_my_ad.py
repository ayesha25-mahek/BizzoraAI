import os
from pathlib import Path
from tkinter import Tk, filedialog

from services.scene_planner import ScenePlanner
from services.hf_image_gen import HFImageGenerator


# =====================================================
# FILE SELECTOR
# =====================================================

def select_one_image(title):

    root = Tk()
    root.withdraw()

    path = filedialog.askopenfilename(
        title=title,
        filetypes=[
            (
                "Image files",
                "*.png *.jpg *.jpeg *.webp"
            )
        ]
    )

    root.destroy()

    return path


def select_multiple_images(title):

    root = Tk()
    root.withdraw()

    paths = filedialog.askopenfilenames(
        title=title,
        filetypes=[
            (
                "Image files",
                "*.png *.jpg *.jpeg *.webp"
            )
        ]
    )

    root.destroy()

    return list(paths)


# =====================================================
# USER REQUEST
# =====================================================

print("=" * 60)
print("                 BIZZORAAI")
print("=" * 60)

print("\nDescribe the advertisement you want.")

user_request = input(
    "\nYour advertisement request:\n> "
)


# =====================================================
# UPLOAD LOGO
# =====================================================

print("\n")
print("-" * 60)
print("STEP 1: Select your business logo")
print("-" * 60)

logo = select_one_image(
    "Select your business logo"
)

if not logo:

    print("❌ No logo selected.")
    exit()

print(f"✓ Logo selected: {logo}")


# =====================================================
# BUSINESS PHOTOS
# =====================================================

print("\n")
print("-" * 60)
print("STEP 2: Select business / restaurant photos")
print("-" * 60)

business_images = select_multiple_images(
    "Select your business photos"
)

print(
    f"✓ {len(business_images)} "
    f"business image(s) selected."
)


# =====================================================
# PRODUCT PHOTOS
# =====================================================

print("\n")
print("-" * 60)
print("STEP 3: Select product photos")
print("-" * 60)

product_images = select_multiple_images(
    "Select your product photos"
)

print(
    f"✓ {len(product_images)} "
    f"product image(s) selected."
)


# =====================================================
# ALL REFERENCES
# =====================================================

reference_images = []

reference_images.append(logo)

reference_images.extend(
    business_images
)

reference_images.extend(
    product_images
)


print("\n")
print("=" * 60)
print(
    f"TOTAL REFERENCES: "
    f"{len(reference_images)}"
)
print("=" * 60)


# =====================================================
# SCENE PLANNER
# =====================================================

print("\n🧠 Creating advertisement strategy...")

planner = ScenePlanner()

ad_plan = planner.create_plan_from_natural_language(
    user_request
)

planner.print_plan(ad_plan)

planner.save_plan(
    ad_plan,
    "my_ad_plan.json"
)


# =====================================================
# IMAGE GENERATOR
# =====================================================

print("\n")
print("=" * 60)
print("🎨 GENERATING ADVERTISEMENT SCENES")
print("=" * 60)

generator = HFImageGenerator()


generated_images = []


# =====================================================
# GENERATE EACH SCENE
# =====================================================

for scene in ad_plan["scenes"]:

    scene_number = scene["scene_number"]

    print(
        f"\nPreparing Scene {scene_number}..."
    )

    # -------------------------------------------------
    # Choose reference image
    # -------------------------------------------------

    if scene_number == 1:

        reference = business_images[0] \
            if business_images \
            else logo

    else:

        reference = product_images[0] \
            if product_images \
            else logo

    # -------------------------------------------------
    # Build prompt
    # -------------------------------------------------

    prompt = f"""
Create a premium commercial advertisement image.

BUSINESS:
{ad_plan['business_name']}

CATEGORY:
{ad_plan['business_category']}

PRODUCT:
{ad_plan['product']}

OFFER:
{ad_plan['offer']}

TONE:
{ad_plan['tone']}

PLATFORM:
{ad_plan['platform']}

SCENE:
{scene['visual_description']}

SCENE IMAGE INSTRUCTIONS:
{scene['image_prompt']}

IMPORTANT:

Use the uploaded reference image as the
PRIMARY visual reference.

Preserve the actual identity of the
business/product shown in the reference.

Do NOT replace the main product with
an unrelated product.

Do NOT invent a different restaurant,
business or product.

Create a realistic professional
advertisement.

Improve lighting, composition and
presentation while maintaining the
identity of the reference.

Do not create fake logos.

Leave clean space for advertisement
text.

Make the image visually suitable for
a professional social-media advertisement.

Cinematic commercial photography.
High detail.
Realistic.
16:9 composition.
"""

    try:

        output = generator.generate_from_reference(
            image_path=reference,
            prompt=prompt,
            scene_number=scene_number
        )

        generated_images.append(output)

    except Exception as e:

        print(
            f"\n❌ Scene {scene_number} failed:"
        )

        print(e)


# =====================================================
# FINAL
# =====================================================

print("\n")
print("=" * 60)
print("              GENERATION COMPLETE")
print("=" * 60)

print("\nGenerated advertisement scenes:")

for image in generated_images:

    print(f"✓ {image}")

print("\nPlan:")
print("output/plans/my_ad_plan.json")

print("\nImages:")

for image in generated_images:

    print(image)