import os

from moviepy import (
    ImageClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips
)


class VideoComposer:

    def __init__(self):

        self.output_dir = "output/videos"

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

    def create_video(
        self,
        image_paths,
        voice_path,
        output_filename="bizzoraai_ad.mp4"
    ):

        if not image_paths:

            raise ValueError(
                "No images provided."
            )

        if not voice_path:

            raise ValueError(
                "Voice file is required."
            )

        print("\n[Video] Creating video...")

        # -----------------------------------------
        # LOAD VOICE
        # -----------------------------------------

        audio = AudioFileClip(
            voice_path
        )

        total_duration = audio.duration

        # -----------------------------------------
        # CALCULATE SCENE DURATION
        # -----------------------------------------

        scene_duration = (
            total_duration /
            len(image_paths)
        )

        clips = []

        # -----------------------------------------
        # CREATE IMAGE SCENES
        # -----------------------------------------

        for index, image_path in enumerate(
            image_paths
        ):

            print(
                f"Preparing scene {index + 1}..."
            )

            clip = (
                ImageClip(image_path)
                .with_duration(
                    scene_duration
                )
            )

            # Slight zoom effect
            clip = clip.resized(
                lambda t:
                1 + (0.03 * t / scene_duration)
            )

            clips.append(clip)

        # -----------------------------------------
        # COMBINE SCENES
        # -----------------------------------------

        video = concatenate_videoclips(
            clips,
            method="compose"
        )

        # -----------------------------------------
        # ADD VOICE
        # -----------------------------------------

        video = video.with_audio(
            audio
        )

        # -----------------------------------------
        # OUTPUT
        # -----------------------------------------

        output_path = os.path.join(
            self.output_dir,
            output_filename
        )

        print("\nRendering video...")
        print("This may take some time...\n")

        video.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac"
        )

        # -----------------------------------------
        # CLEANUP
        # -----------------------------------------

        audio.close()

        for clip in clips:
            clip.close()

        video.close()

        print(
            f"\n[SUCCESS] Video saved: {output_path}"
        )

        return output_path

    def create_from_clips(self, clip_paths, voice_path, output_filename="final_video.mp4"):
        from moviepy import VideoFileClip
        if not clip_paths:
            raise ValueError("No video clips provided.")
        if not voice_path:
            raise ValueError("Voice file is required.")
        
        print("\n[Video] Combining video clips...")
        
        audio = AudioFileClip(voice_path)
        video_clips = [VideoFileClip(p) for p in clip_paths]
        
        final_video = concatenate_videoclips(video_clips, method="compose")
        final_video = final_video.with_audio(audio)
        
        output_path = os.path.join(self.output_dir, output_filename)
        final_video.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac"
        )
        
        audio.close()
        for c in video_clips:
            c.close()
        final_video.close()
        
        return output_path