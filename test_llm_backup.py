from services.llm_provider import LLMProvider


print("=" * 60)
print("        BIZZORAAI LLM PROVIDER TEST")
print("=" * 60)


provider = LLMProvider()


prompt = """
You are the AI marketing strategist for BizzoraAI.

Create a short advertising strategy for:

Business:
Oak Tree Cafe

Product:
Crispy Chicken Lollipop

Price:
₹149

Platform:
Instagram

Language:
English

Tone:
Energetic and appetizing.

Return:
1. Hook
2. Main message
3. Call to action
"""


try:

    result = provider.generate(prompt)

    print("\n")
    print("=" * 60)
    print("GENERATED RESULT")
    print("=" * 60)

    print(result)

except Exception as e:

    print("\n❌ ERROR:")
    print(e)