import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_ad_script(user_request):

    prompt = f"""
You are an expert AI advertising copywriter.

The user wants to create an advertisement for their business.

USER REQUEST:
{user_request}

Analyze the user's request and understand:
- What type of business it is
- Business name, if provided
- Products or services
- Prices, if provided
- Offers or discounts
- Target audience, if mentioned
- Language
- Tone
- Desired duration
- Any other important information

The business can be ANY type of business, including but not limited to:
restaurants, cafes, hospitals, clinics, salons, clothing stores,
grocery stores, gyms, schools, coaching centers, hotels, real-estate
businesses, automobile businesses, local shops, services, or any
other business.

Generate a short advertisement script based ONLY on the information
provided by the user.

Rules:
- Do not invent facts about the business.
- Do not invent prices, offers, locations, services, or claims.
- If the user specifies a language, write the advertisement in that language.
- If no language is specified, use English.
- Match the requested tone.
- Make it suitable for a short video advertisement.
- Include a strong opening hook.
- Clearly communicate the main product/service or offer.
- End with a natural call to action.
- Keep it around 15-20 seconds when spoken.
- Maximum 40 words.
- Output ONLY the advertisement script.
- Do not provide explanations or labels.

"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text.strip()