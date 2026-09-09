from services.slide_planner import SlidePlanner


content_model = {

    "title": "Cybersecurity Awareness",

    "summary":
        "Organizations must improve cybersecurity "
        "awareness to protect sensitive information.",

    "key_points": [
        "Use strong passwords.",
        "Enable multi-factor authentication.",
        "Train employees about phishing."
    ],

    "statistics": [
        "Sample statistic from source document."
    ],

    "recommendations": [
        "Implement MFA.",
        "Conduct security awareness training."
    ]
}


planner = SlidePlanner()

slides = planner.create_plan(
    content_model
)

planner.print_plan(
    slides
)
planner.save_plan(
    slides,
    "cybersecurity_slide_plan.json"
)