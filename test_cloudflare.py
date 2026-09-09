from services.cloudflare_image_gen import CloudflareImageGenerator


generator = CloudflareImageGenerator()


prompt = """
Create a premium food advertisement image
for Oak Tree Cafe.

Show crispy golden chicken lollipops on a
beautiful restaurant table.

The food should look extremely appetizing,
realistic and professionally photographed.

Warm restaurant lighting.
Cinematic food photography.
High detail.
Suitable for an Instagram advertisement.
"""


image = generator.generate(
    prompt,
    "test_cloudflare.png"
)


if image:

    print("\n================================")
    print("       SUCCESS!")
    print("================================")
    print(f"Image: {image}")

else:

    print("\n❌ Cloudflare image generation failed.")