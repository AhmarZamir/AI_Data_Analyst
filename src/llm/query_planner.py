import json
import os

from dotenv import load_dotenv
from google import genai

from src.semantic.metrics import format_business_metrics


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def _clean_json_response(text):

    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


def create_plan(question, schema):

    business_metrics = format_business_metrics()

    prompt = f"""
You are a business analytics query planner.

Determine whether the user's question can be answered reliably
with one SQL query or should be broken into multiple factual
database questions.

User question:
{question}

Relevant database schema:
{schema}

Business definitions:
{business_metrics}

Return valid JSON only using this exact structure:

{{
    "is_complex": true,
    "steps": [
        "first analytical database question",
        "second analytical database question"
    ]
}}

Rules:
- Use is_complex=false when one SQL query is enough.
- A query with multiple joins is not automatically complex.
- For simple questions, return an empty steps list.
- For complex questions, use only independent factual questions answerable with SQL.
- Do not add reasoning-only steps such as compare, explain, recommend, or calculate.
- Keep the plan minimal.
- Maximum 5 steps.
- Do not include markdown or any text outside the JSON.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    if not response.text:

        raise ValueError(
            "The query planner returned an empty response."
        )

    plan = json.loads(
        _clean_json_response(response.text)
    )

    steps = plan.get("steps", [])

    if not isinstance(steps, list):

        raise ValueError(
            "The query planner returned an invalid steps value."
        )

    steps = [
        step.strip()
        for step in steps[:5]
        if isinstance(step, str) and step.strip()
    ]

    is_complex = bool(
        plan.get("is_complex", False)
    ) and bool(steps)

    return {
        "is_complex": is_complex,
        "steps": steps if is_complex else []
    }
