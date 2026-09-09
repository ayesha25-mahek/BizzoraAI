from services.edge_tts import EdgeTTSGenerator


generator = EdgeTTSGenerator()


text = """
Craving something crispy?

Try Oak Tree Cafe's delicious
chicken lollipop for just one forty nine rupees.

Visit Oak Tree Cafe today!
"""


output = generator.generate(
    text,
    "edge_test.mp3"
)


if output:

    print("\n==============================")
    print("       SUCCESS!")
    print("==============================")

    print(f"Audio: {output}")

else:

    print("\n❌ Voice generation failed.")