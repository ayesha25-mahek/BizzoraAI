from services.output_router import OutputRouter
from services.output_request import OutputRequest

from services.linkedin_generator import LinkedInGenerator
from services.executive_summary_generator import ExecutiveSummaryGenerator


content_model = {

    "title": "Cybersecurity Awareness",

    "content_type": "Report",

    "summary": "Cybersecurity awareness is important for protecting organizational information.",

    "language": "English",

    "main_topic": "Cybersecurity",

    "key_points": [
        "Strong passwords improve security.",
        "Multi-factor authentication provides additional protection."
    ],

    "important_facts": [
        "Organizations need effective cybersecurity practices."
    ],

    "statistics": [],

    "entities": [],

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
        "MFA"
    ],

    "source_files": [
        "test_document.pdf"
    ]
}


request = OutputRequest(

    outputs=[
        "linkedin",
        "executive_summary"
    ],

    language="English",

    tone="Professional",

    target_audience="General public"
)


router = OutputRouter()


router.register(
    "linkedin",
    LinkedInGenerator()
)


router.register(
    "executive_summary",
    ExecutiveSummaryGenerator()
)


print("=" * 60)
print("        BIZZORAAI REAL OUTPUT ROUTER")
print("=" * 60)


results = router.route(
    content_model,
    request
)


print("\n")
print("=" * 60)
print("                  RESULTS")
print("=" * 60)


for output_type, result in results.items():

    print(f"\n{output_type}:")
    print(result)