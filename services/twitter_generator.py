from services.llm_pool import LLMPool


class TwitterGenerator:

    def __init__(self):
        self.llm = LLMPool()

    def generate(self, content_model, output_request):

        prompt = f"""
You are a professional social media writer for BizzoraAI.

Create a Twitter/X post (or short thread of 2-4 tweets if content warrants it)
using ONLY the information in the content model below.

CONTENT MODEL:
{content_model}

REQUIREMENTS:
1. Each tweet must be under 280 characters.
2. If writing a thread, number each tweet (1/N, 2/N …).
3. Use relevant hashtags (max 3 per tweet).
4. Make the opening tweet attention-grabbing.
5. Keep the tone: {output_request.tone}
6. Write in: {output_request.language}
7. Target audience: {output_request.target_audience}
8. Do NOT mention AI generated this.
9. Return ONLY the tweet text(s), separated by blank lines.
"""
        result = self.llm.generate(prompt)
        if not result:
            raise ValueError("Twitter generator returned empty output.")
        return result.strip()
