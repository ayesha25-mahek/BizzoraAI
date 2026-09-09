from services.video_composer import VideoComposer


# ==========================================
# YOUR GENERATED SCENES
# ==========================================

images = [
    "output/images/scene_1.png",
    "output/images/scene_2.png",
    "output/images/scene_3.png",
    "output/images/scene_4.png"
]


# ==========================================
# GENERATED VOICE
# ==========================================

voice = (
    "output/audio/"
    "oak_tree_cafe_ad.mp3"
)


# ==========================================
# CREATE VIDEO
# ==========================================

composer = VideoComposer()


try:

    output = composer.create_video(
        image_paths=images,
        voice_path=voice,
        output_filename=(
            "oak_tree_cafe_ad.mp4"
        )
    )

    print("\n")
    print("=" * 60)
    print("          BIZZORAAI VIDEO READY")
    print("=" * 60)

    print(
        f"\nVideo: {output}"
    )


except Exception as e:

    print("\n❌ VIDEO GENERATION FAILED")
    print(e)