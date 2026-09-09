from services.linkedin_generator import LinkedInGenerator
from services.output_request import OutputRequest


content_model = {

    "title": "Cybersecurity Awareness",

    "content_type": "Report",

    "summary": (
        "Organizations must improve cybersecurity "
        "awareness and protect sensitive information."
    ),

    "language": "English",

    "main_topic": "Cybersecurity",

    "key_points": [
        "Strong passwords improve account security.",
        "Multi-factor authentication provides "
        "additional protection."
    ],

    "important_facts": [
        "Cybersecurity awareness is important "
        "for organizations."
    ],

    "statistics": [],

    "entities": [
        "BizzoraAI"
    ],

    "events": [],

    "quotes": [],

    "recommendations": [
        "Use strong passwords.",
        "Enable multi-factor authentication."
    ],

    "target_audience": [
        "General public"
    ],

    "important_visuals": [],

    "keywords": [
        "cybersecurity",
        "security",
        "MFA"
    ],

    "source_files": [
        "test_document.pdf"
    ]
}


request = OutputRequest(

    outputs=[
        "linkedin"
    ],

    language="English",

    tone="Professional",

    target_audience="General public"
)


generator = LinkedInGenerator()


try:

    result = generator.generate(
        content_model,
        request
    )

    print("\n")
    print("=" * 60)
    print("             LINKEDIN POST")
    print("=" * 60)

    print("\n")
    print(result)

    print("\n")
    print("=" * 60)
    print("       ✓ LINKEDIN GENERATION SUCCESSFUL")
    print("=" * 60)


except Exception as e:

    print("\n❌ ERROR:")
    print(e)