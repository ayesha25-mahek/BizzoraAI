import asyncio
import os
import edge_tts


class EdgeTTSGenerator:

    def __init__(self):
        self.output_dir = "output/audio"
        os.makedirs(self.output_dir, exist_ok=True)

        self.voice = "en-IN-NeerjaNeural"

    async def _generate(self, text, output_path):

        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice
        )

        await communicate.save(output_path)

    def generate(
        self,
        text,
        output_filename="edge_voice.mp3"
    ):

        print("\n🗣️ Trying Edge TTS...")

        output_path = os.path.join(
            self.output_dir,
            output_filename
        )

        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    pool.submit(asyncio.run, self._generate(text, output_path)).result()
            else:
                asyncio.run(self._generate(text, output_path))

            if not os.path.exists(output_path):
                print("❌ Edge TTS produced no file.")
                return None

            print(
                f"[SUCCESS] Edge TTS saved: {output_path}"
            )

            return output_path

        except Exception as e:

            print(f"❌ Edge TTS failed: {e}")

            return None