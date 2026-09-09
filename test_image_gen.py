import tkinter as tk
from tkinter import filedialog

from services.image_gen_gemini_old import generate_ad_image


# =====================================================
# FILE PICKER
# =====================================================

def select_image(title):

    file_path = filedialog.askopenfilename(

        title=title,

        filetypes=[

            (
                "Image files",
                "*.png *.jpg *.jpeg *.webp"
            ),

            (
                "PNG files",
                "*.png"
            ),

            (
                "JPEG files",
                "*.jpg *.jpeg"
            ),

            (
                "WebP files",
                "*.webp"
            )
        ]
    )

    return file_path


# =====================================================
# START TKINTER
# =====================================================

root = tk.Tk()

root.withdraw()


print(
    "\n=========================================="
)

print(
    "       AI AD IMAGE GENERATOR"
)

print(
    "==========================================\n"
)


# =====================================================
# GET USER PROMPT
# =====================================================

print(
    "Describe the advertisement you want."
)

print(
    "You can write it naturally."
)

print(
    "Example:"
)

print(
    "Create a premium burger advertisement for"
)

print(
    "my restaurant. The burger costs ₹149."
)

print()

user_prompt = input(
    "Your advertisement request:\n> "
)


# =====================================================
# LOGO
# =====================================================

print(
    "\n------------------------------------------"
)

print(
    "STEP 1: Select your business logo"
)

print(
    "------------------------------------------"
)

logo = select_image(
    "Select your business logo"
)


if not logo:

    print(
        "\nNo logo selected."
    )

else:

    print(
        f"✓ Logo selected: {logo}"
    )


# =====================================================
# BUSINESS PHOTOS
# =====================================================

print(
    "\n------------------------------------------"
)

print(
    "STEP 2: Select business/product photos"
)

print(
    "------------------------------------------"
)

print(
    "You can select multiple images."
)

print(
    "Press Cancel when you are finished."
)


photos = []


while True:

    photo = select_image(
        "Select a business/product photo"
    )

    if not photo:

        break

    photos.append(photo)

    print(
        f"✓ Added: {photo}"
    )


# =====================================================
# COMBINE ALL REFERENCES
# =====================================================

reference_images = []


if logo:

    reference_images.append(
        logo
    )


reference_images.extend(
    photos
)


# =====================================================
# CHECK
# =====================================================

if not reference_images:

    print(
        "\n❌ No images were selected."
    )

    root.destroy()

    exit()


print(
    "\n=========================================="
)

print(
    f"Total reference images: "
    f"{len(reference_images)}"
)

print(
    "=========================================="
)


# =====================================================
# BUILD AI INSTRUCTION
# =====================================================

final_prompt = f"""

You are an expert commercial advertising
creative director and photographer.

USER'S REQUEST:

{user_prompt}


REFERENCE IMAGES:

The uploaded images belong to the user's
real business.

Use these images as visual references.

IMPORTANT RULES:

1. Preserve the real identity of the business.

2. If a logo is provided, preserve its
   appearance and branding.

3. If real product photographs are provided,
   use those products as references.

4. If real restaurant/store/interior
   photographs are provided, preserve their
   recognizable appearance.

5. Do not replace the business with a
   completely fictional business.

6. You may improve lighting, composition,
   camera angle, atmosphere and presentation.

7. You may creatively combine the uploaded
   photographs with newly generated elements.

8. Do not invent factual information.

9. Do not invent prices, offers or claims.

10. Do not add random text to the image.

11. Leave appropriate clean space where
    advertisement text can be added later.

Create ONE highly polished,
photorealistic commercial advertisement image.

Make it visually attractive and suitable
for social media advertising.

Use a cinematic commercial photography style.

Sharp details.

Professional lighting.

Premium composition.

16:9 landscape format.

"""


# =====================================================
# GENERATE
# =====================================================

try:

    output = generate_ad_image(

        prompt=final_prompt,

        reference_images=reference_images,

        output_filename="generated_ad.jpg"
    )

    print(
        "\n🎉 SUCCESS!"
    )

    print(
        f"Generated image:"
        f" {output}"
    )


except Exception as e:

    print(
        "\n❌ ERROR:"
    )

    print(e)


finally:

    root.destroy()