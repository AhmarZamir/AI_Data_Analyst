import os 
from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_sql(question):
    schema = """
    customers(
        customer_id,
        name,
        email,
        city,
        country,
        created_at
    )

    products(
        product_id,
        name,
        category,
        price
    )

    orders(
        order_id,
        customer_id,
        status,
        created_at
    )

    order_items(
        order_item_id,
        order_id,
        product_id,
        quantity,
        unit_price
    )

    payments(
        payment_id,
        order_id,
        amount,
        payment_status,
        payment_method,
        paid_at
    )

    """

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

    