import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")

if not api_key:
    raise ValueError(
        "ELEVENLABS_API_KEY not found in .env"
    )

client = ElevenLabs(
    api_key=api_key
)

text = """
Craving something crispy?

Try Oak Tree Cafe's delicious
chicken lollipop for just one forty nine rupees!

Visit Oak Tree Cafe today!
"""

print("Generating voice...")

audio = client.text_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    output_format="mp3_44100_128",
    text=text,
    model_id="eleven_multilingual_v2"
)

output_path = "output/voice_test.mp3"

os.makedirs("output", exist_ok=True)

with open(output_path, "wb") as f:
    for chunk in audio:
        f.write(chunk)

print("\n✓ Voice generated!")
print(f"Saved: {output_path}")