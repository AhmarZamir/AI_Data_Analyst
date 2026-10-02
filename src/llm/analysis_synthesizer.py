import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def synthesize_analysis(question, step_results):

    prompt = f"""
You are a business data analyst.

Answer the original user question using only the factual
database evidence supplied below.

Original question:
{question}

Evidence:
{step_results}

Rules:
- Use only the supplied evidence.
- Do not invent, estimate, or change database values.
- Perform any required calculations carefully.
- Mention meaningful comparisons when relevant.
- If the evidence is insufficient, say so clearly.
- Do not mention internal planning or SQL unless necessary.
- Keep the final answer concise and business-friendly.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    if not response.text:

        raise ValueError(
            "The analysis synthesizer returned an empty response."
        )

    return response.text.strip()
