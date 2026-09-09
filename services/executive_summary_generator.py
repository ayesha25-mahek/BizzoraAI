from services.llm_provider import LLMProvider


class ExecutiveSummaryGenerator:

    def __init__(self):

        self.llm = LLMProvider()

    def generate(
        self,
        content_model,
        output_request
    ):

        prompt = f"""
You are an expert executive briefing writer
for BizzoraAI.

Create a concise and accurate executive summary
from the supplied content model.

CONTENT MODEL:

{content_model}

REQUIREMENTS:

1. Use ONLY information present in the content model.
2. Never invent facts.
3. Preserve names, numbers and dates accurately.
4. Clearly explain the main topic.
5. Include the most important findings.
6. Include important recommendations when available.
7. Remove unnecessary details.
8. Make the result easy for a decision maker to read.
9. Use headings and bullet points where appropriate.
10. Write in the requested language.
11. Match the requested tone.
12. Do not mention AI.

LANGUAGE:
{output_request.language}

TONE:
{output_request.tone}

TARGET AUDIENCE:
{output_request.target_audience}

Return ONLY the executive summary.
"""

        print("\nGenerating executive summary...")

        result = self.llm.generate(prompt)

        if not result:

            raise ValueError(
                "Executive summary generator returned empty output."
            )

        return result.strip()