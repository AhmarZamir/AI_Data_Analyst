import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def resolve_question(
    question,
    conversation_history
):

    if not conversation_history:
        return question

    recent_history = conversation_history[-6:]

    prompt = f"""
You rewrite conversational business analytics questions
into standalone questions.

Conversation history:
{recent_history}

Current user question:
{question}

Your job:
Rewrite the current question so it can be understood
without seeing the previous conversation.

Rules:
- Preserve the user's meaning.
- Resolve references such as "them", "that", "those",
  "same period", "previous month", or "what about Lahore".
- Use only context clearly present in the conversation.
- Do not invent missing details.
- If the current question is already standalone,
  return it unchanged.
- Return only the rewritten question.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    if not response.text:

        raise ValueError(
            "Context resolver returned an empty response."
        )

    return response.text.strip()
