class VoiceScriptGenerator:

    def generate(self, ad_plan):

        scenes = ad_plan.get("scenes", [])

        if not scenes:
            raise ValueError(
                "No scenes found in advertisement plan."
            )

        lines = []

        for scene in scenes:

            text = scene.get(
                "text_overlay",
                ""
            ).strip()

            if text:
                lines.append(text)

        if not lines:
            raise ValueError(
                "No text found in advertisement scenes."
            )

        # Combine scene text into natural voiceover
        script = " ".join(lines)

        return script