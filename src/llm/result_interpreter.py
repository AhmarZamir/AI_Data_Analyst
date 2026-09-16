import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def interpret_result(question, sql, result):

    prompt = f"""
You are a business data analyst.

User question:
{question}

Executed SQL:
{sql}

Database result:
{result}

Provide a concise, natural-language answer.

Rules:
- Treat the database result as the only source of truth.
- Never invent, estimate, or modify numbers.
- Do not mention SQL unless the user specifically asks about it.
- Do not say "the database returned".
- If the result is empty, say no matching data was found.
- Keep the response short and business-friendly.
"""

    
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text.strip()