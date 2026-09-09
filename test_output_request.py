from services.output_request import OutputRequest


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


request.print_request()

print("\nDictionary:")
print(request.to_dict())