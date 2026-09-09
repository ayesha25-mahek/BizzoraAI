from services.llm_pool import LLMPool


class InfographicGenerator:

    def __init__(self):
        self.llm = LLMPool()

    def generate(self, content_model, output_request):

        prompt = f"""
You are an expert infographic content designer for BizzoraAI.

Create a detailed infographic content plan and layout guide
using ONLY the information in the content model below.

CONTENT MODEL:
{content_model}

OUTPUT FORMAT:
Return a structured plan with the following sections:

## INFOGRAPHIC TITLE
(compelling, max 10 words)

## HEADLINE STATISTIC / HERO FACT
(the single most impactful data point or statement)

## KEY SECTIONS (3-6 sections)
For each section provide:
- Section Title
- Visual Type (e.g. bar chart, icon list, timeline, pie chart, flow diagram)
- Content Points (2-4 bullet points of data/text)
- Suggested Color: (choose from violet, blue, emerald, amber, rose)

## CALL TO ACTION
(short, clear action statement)

## LAYOUT RECOMMENDATION
(e.g. vertical scroll, two-column grid, timeline, hub-and-spoke)

## DESIGN NOTES
(typography suggestions, icon style, brand colour palette notes)

REQUIREMENTS:
- Only use facts present in the content model.
- Tone: {output_request.tone}
- Language: {output_request.language}
- Target audience: {output_request.target_audience}
- Do not mention AI.
"""
        result = self.llm.generate(prompt)
        if not result:
            raise ValueError("Infographic generator returned empty output.")
        return result.strip()
