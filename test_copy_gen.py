"""
Standalone test script for ad script generation.
Run this before integrating with FastAPI to verify ad generation.
"""

from services.copy_gen import generate_ad_script


def test_script(user_request):
    """Test script generation and print results"""

    print(f"\n{'=' * 60}")
    print("USER REQUEST")
    print(f"{'=' * 60}")
    print(user_request)
    print(f"{'=' * 60}")

    script = generate_ad_script(user_request)

    print("\nGenerated Ad Script:")
    print(f"  {script}")

    print(f"\nWord count: {len(script.split())}")
    print(f"Character count: {len(script)}")

    # Rough timing estimate
    word_count = len(script.split())

    if 30 <= word_count <= 50:
        print(f"✓ Timing: Good ({word_count} words ≈ 15-20 seconds)")
    elif word_count < 30:
        print(f"⚠ Timing: Short ({word_count} words)")
    else:
        print(f"⚠ Timing: Long ({word_count} words)")

    return script


if __name__ == "__main__":

    print("AI Ad Script Generator - Standalone Test")
    print("Enter any business/ad request below.\n")

    user_request = input("Describe the advertisement you want:\n> ")

    test_script(user_request)

    print(f"\n{'=' * 60}")
    print("Testing complete!")
    print(f"{'=' * 60}\n")