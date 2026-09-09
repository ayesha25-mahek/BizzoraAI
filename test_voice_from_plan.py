import json

from services.voice_script import VoiceScriptGenerator
from services.voice_provider import VoiceProviderManager


# ==========================================
# LOAD GENERATED AD PLAN
# ==========================================

plan_path = "output/plans/my_ad_plan.json"

with open(
    plan_path,
    "r",
    encoding="utf-8"
) as file:

    ad_plan = json.load(file)


# ==========================================
# GENERATE VOICE SCRIPT
# ==========================================

script_generator = VoiceScriptGenerator()

voice_script = script_generator.generate(
    ad_plan
)


print("\n")
print("=" * 60)
print("                 VOICE SCRIPT")
print("=" * 60)

print("\n")
print(voice_script)


# ==========================================
# GENERATE VOICE
# ==========================================

voice_manager = VoiceProviderManager()

audio_path = voice_manager.generate(
    voice_script,
    "oak_tree_cafe_ad.mp3"
)


print("\n")
print("=" * 60)
print("             VOICE GENERATION COMPLETE")
print("=" * 60)

print(f"\nAudio: {audio_path}")