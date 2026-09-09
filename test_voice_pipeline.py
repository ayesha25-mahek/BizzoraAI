from services.voice_provider import VoiceProviderManager


text = """
Craving something crispy?

Try Oak Tree Cafe's delicious
chicken lollipop for just ₹149.

Visit Oak Tree Cafe today!
"""


voice_manager = VoiceProviderManager()


output = voice_manager.generate(
    text,
    "oak_tree_cafe_voice.mp3"
)


print("\n")
print("=" * 60)
print("             VOICE COMPLETE")
print("=" * 60)

print(f"\nAudio file: {output}")