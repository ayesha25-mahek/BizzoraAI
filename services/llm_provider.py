import os
from dotenv import load_dotenv
from google import genai
from groq import Groq

load_dotenv()


class LLMProvider:

    def __init__(self):

        # -----------------------------
        # GEMINI
        # -----------------------------

        gemini_key = os.getenv("GEMINI_API_KEY")

        if not gemini_key:
            raise ValueError("GEMINI_API_KEY missing")

        self.gemini = genai.Client(
            api_key=gemini_key
        )

        # Use the currently available Gemini text model
        self.gemini_model = "gemini-3.6-flash"

        # -----------------------------
        # GROQ
        # -----------------------------

        groq_key = os.getenv("GROQ_API_KEY")

        if not groq_key:
            raise ValueError("GROQ_API_KEY missing")

        self.groq = Groq(
            api_key=groq_key
        )

        self.groq_model = "llama-3.3-70b-versatile"


    # ==================================================
    # GEMINI
    # ==================================================

    def generate_with_gemini(self, prompt):

        response = self.gemini.models.generate_content(
            model=self.gemini_model,
            contents=prompt
        )

        return response.text


    # ==================================================
    # GROQ
    # ==================================================

    def generate_with_groq(self, prompt):

        response = self.groq.chat.completions.create(

            model=self.groq_model,

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.7
        )

        return response.choices[0].message.content


    # ==================================================
    # AUTOMATIC FALLBACK
    # ==================================================

    def generate(self, prompt):

        # Try Gemini first

        try:

            print("\n[AI] Trying Gemini...")

            result = self.generate_with_gemini(prompt)

            if result:
                print("[SUCCESS] Gemini succeeded")

                return result

        except Exception as e:

            print(
                f"⚠ Gemini failed: {e}"
            )

            print(
                "↪ Switching to Groq..."
            )


        # Try Groq

        try:

            print("\n🤖 Trying Groq...")

            result = self.generate_with_groq(prompt)

            if result:

                print(
                    "[SUCCESS] Groq succeeded"
                )

                return result

        except Exception as e:

            print(
                f"❌ Groq failed: {e}"
            )


        raise RuntimeError(
            "All LLM providers failed."
        )