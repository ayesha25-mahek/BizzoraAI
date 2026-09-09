import json

from services.ppt_generator import PPTGenerator


PLAN_PATH = (
    "output/slide_plans/"
    "cybersecurity_slide_plan.json"
)


with open(
    PLAN_PATH,
    "r",
    encoding="utf-8"
) as file:

    slide_plan = json.load(file)


generator = PPTGenerator()


output_path = generator.generate(
    slide_plan,
    "cybersecurity_presentation.pptx"
)


print("\n")
print("=" * 60)
print("        BIZZORAAI PPT GENERATION")
print("=" * 60)

print(
    f"\n✓ Generated successfully:"
    f"\n{output_path}"
)