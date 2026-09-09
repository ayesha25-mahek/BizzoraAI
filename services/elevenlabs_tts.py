import os

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs


load_dotenv()


class ElevenLabsTTS:

    def __init__(self):

        api_key = os.getenv(
            "ELEVENLABS_API_KEY"
        )

        if not api_key:

            raise ValueError(
                "ELEVENLABS_API_KEY not found."
            )

        self.client = ElevenLabs(
            api_key=api_key
        )

        self.voice_id = (
            "JBFqnCBsd6RMkjVDRZzb"
        )

        self.model_id = (
            "eleven_multilingual_v2"
        )

        self.output_dir = (
            "output/audio"
        )

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

    def generate(
        self,
        text,
        output_filename="advertisement.mp3"
    ):

        output_path = os.path.join(
            self.output_dir,
            output_filename
        )

        audio = self.client.text_to_speech.convert(

            voice_id=self.voice_id,

            output_format="mp3_44100_128",

            text=text,

            model_id=self.model_id
        )

        with open(
            output_path,
            "wb"
        ) as file:

            for chunk in audio:

                file.write(chunk)

        if not os.path.exists(output_path):

            raise RuntimeError(
                "ElevenLabs did not create audio."
            )

        return output_path