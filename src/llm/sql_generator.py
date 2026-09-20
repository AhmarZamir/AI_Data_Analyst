import os 
from dotenv import load_dotenv
from google import genai
from src.retrieval.schema_retriever import retrieve_tables



load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_sql(question):
    schema = retrieve_schema(question)

    prompt = f"""
        You are a PostgreSQL expert.

        Convert the user's question into a PostgreSQL query.

        Database schema: {schema}

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

    