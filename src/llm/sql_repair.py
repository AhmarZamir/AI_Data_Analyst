import os

from dotenv import load_dotenv
from google import genai

from src.semantic.metrics import format_business_metrics


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def _clean_sql(sql):

    sql = sql.strip()

    if sql.startswith("```sql"):
        sql = sql[6:]
    elif sql.startswith("```"):
        sql = sql[3:]

    if sql.endswith("```"):
        sql = sql[:-3]

    return sql.strip()


def repair_sql(question, schema, failed_sql, db_error):

    business_metrics = format_business_metrics()

    prompt = f"""
You are an expert PostgreSQL SQL repair assistant.

The previous SQL query failed during execution.

Original question:
{question}

Database schema:
{schema}

Business definitions:
{business_metrics}

Failed SQL:
{failed_sql}

PostgreSQL error:
{db_error}

Rules:
- Fix the SQL based on the database error.
- Use only tables and columns from the provided schema.
- Preserve the user's original analytical intent.
- Follow the business metric definitions.
- Generate only one read-only SELECT query.
- Do not use INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, or TRUNCATE.
- Do not invent tables or columns.
- Return SQL only.
- Do not use markdown or explanations.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    if not response.text:

        raise ValueError(
            "The SQL repair model returned an empty response."
        )

    return _clean_sql(response.text)
