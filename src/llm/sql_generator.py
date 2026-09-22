import os 
from dotenv import load_dotenv
from google import genai
from src.retrieval.schema_retriever import retrieve_tables
from src.semantic.metrics import format_business_metrics



load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_sql(question):
    schema = retrieve_tables(question)

    business_metrics = format_business_metrics()

    prompt = f"""
        You are a PostgreSQL expert.

        Convert the user's question into a PostgreSQL query.

        Database schema: {schema}

        Business definitions:{business_metrics}


        User question: {question}

Rules:
- Return SQL only.
- Do not explain anything.
- Do not use markdown.

"""

    response = client.models.generate_content(
        model = "gemini-3.5-flash-lite",
        contents = prompt
    )

    return response.text.strip()

    