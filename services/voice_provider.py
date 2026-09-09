from services.elevenlabs_tts import ElevenLabsTTS
from services.edge_tts import EdgeTTSGenerator


class VoiceProviderManager:

    def __init__(self):

        self.elevenlabs = ElevenLabsTTS()
        self.edge = EdgeTTSGenerator()

    def generate(
        self,
        text,
        output_filename="advertisement.mp3"
    ):

        print("\n")
        print("=" * 60)
        print("             VOICE GENERATION")
        print("=" * 60)

        # ==========================================
        # PRIMARY: ELEVENLABS
        # ==========================================

        try:

            print("\n🥇 Trying ElevenLabs...")

            result = self.elevenlabs.generate(
                text,
                output_filename
            )

            if result:

                print("[SUCCESS] ElevenLabs succeeded")

                return result

        except Exception as e:

            print(
                f"❌ ElevenLabs failed: {e}"
            )

        # ==========================================
        # BACKUP: EDGE TTS
        # ==========================================

        try:

            print("\n🥈 Switching to Edge TTS...")

            result = self.edge.generate(
                text,
                output_filename
            )

            if result:

                print("[SUCCESS] Edge TTS succeeded")

                return result

        except Exception as e:

            print(
                f"❌ Edge TTS failed: {e}"
            )

        # ==========================================
        # EVERYTHING FAILED
        # ==========================================

        raise RuntimeError(
            "All voice generation providers failed."
        )