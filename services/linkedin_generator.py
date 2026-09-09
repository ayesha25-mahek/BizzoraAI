from services.llm_provider import LLMProvider


class LinkedInGenerator:

    def __init__(self):

        self.llm = LLMProvider()

    def generate(
        self,
        content_model,
        output_request
    ):

        prompt = f"""
You are a professional LinkedIn content writer
for BizzoraAI.

Create a high-quality LinkedIn post using ONLY
the information provided in the content model.

CONTENT MODEL:

{content_model}

REQUIREMENTS:

1. Do not invent facts.
2. Do not change numbers, dates or names.
3. Keep the main message accurate.
4. Make the opening engaging.
5. Use a professional but natural tone.
6. Use short readable paragraphs.
7. Use bullet points where appropriate.
8. Add a clear conclusion.
9. Add relevant hashtags.
10. Do not mention that AI generated the post.
11. Write in the requested language.
12. Adapt the writing to the requested audience.

LANGUAGE:
{output_request.language}

TONE:
{output_request.tone}

TARGET AUDIENCE:
{output_request.target_audience}

Return ONLY the LinkedIn post text.
"""

        print("\nGenerating LinkedIn post...")

        result = self.llm.generate(prompt)

        if not result:

            raise ValueError(
                "LinkedIn generator returned empty output."
            )

        return result.strip()