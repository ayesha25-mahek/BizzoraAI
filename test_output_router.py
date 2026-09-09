from services.output_router import OutputRouter
from services.output_request import OutputRequest


class DummyLinkedInGenerator:

    def generate(
        self,
        content_model,
        output_request
    ):

        return {
            "platform": "LinkedIn",
            "text": (
                "This is a test LinkedIn post "
                "generated from the content model."
            )
        }


class DummySummaryGenerator:

    def generate(
        self,
        content_model,
        output_request
    ):

        return {
            "title": content_model.get(
                "title",
                ""
            ),
            "summary": (
                "This is a test executive summary."
            )
        }


content_model = {

    "title": "Cybersecurity Awareness",

    "summary": (
        "This is a sample cybersecurity report."
    ),

    "main_topic": "Cybersecurity",

    "key_points": [
        "Strong passwords are important.",
        "Users should enable MFA."
    ]
}


request = OutputRequest(

    outputs=[
        "linkedin",
        "executive_summary",
        "video"
    ],

    language="English",

    tone="Professional",

    target_audience="General public"
)


router = OutputRouter()


router.register(
    "linkedin",
    DummyLinkedInGenerator()
)


router.register(
    "executive_summary",
    DummySummaryGenerator()
)


print("=" * 60)
print("              BIZZORAAI OUTPUT ROUTER")
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

    print(
        f"\n{output_type}:"
    )

    print(result)