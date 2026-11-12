"""
Chainlit web UI for the Gemini chatbot.

Run:  chainlit run app2.py -w
Then open http://localhost:8000
"""

import os

import chainlit as cl
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# 1. Configuration (loaded from the .env file)
# ---------------------------------------------------------------------------
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

SYSTEM_PROMPT = (
    "You are a helpful, friendly assistant. "
    "Keep answers clear and concise unless the user asks for detail. "
    "Use Markdown formatting (lists, bold, code blocks) when it helps readability."
)

BOT_NAME = "Gemini"

# 0 = thinking off (fastest). Remove the thinking_config line below if your
# model doesn't support it (e.g. some Pro models).
THINKING_BUDGET = 0

if not API_KEY or API_KEY == "your_api_key_here":
    raise SystemExit("GEMINI_API_KEY is missing. Add it to your .env file.")

client = genai.Client(api_key=API_KEY)


# ---------------------------------------------------------------------------
# 2. Chat session helpers
# ---------------------------------------------------------------------------
def create_chat():
    """Create an async chat session. The SDK stores the history for us."""
    return client.aio.chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7,
            thinking_config=types.ThinkingConfig(thinking_budget=THINKING_BUDGET),
        ),
    )


# ---------------------------------------------------------------------------
# 3. UI events
# ---------------------------------------------------------------------------
@cl.set_starters
async def set_starters():
    """Clickable suggestion cards shown on an empty chat."""
    return [
        cl.Starter(
            label="Explain something simply",
            message="Explain how the internet works like I'm 12.",
        ),
        cl.Starter(
            label="Help me write code",
            message="Write a Python function that checks if a string is a palindrome, and explain it.",
        ),
        cl.Starter(
            label="Brainstorm ideas",
            message="Give me 5 creative project ideas for learning Python.",
        ),
        cl.Starter(
            label="Draft a message",
            message="Help me write a polite email asking for an extension on a deadline.",
        ),
    ]


@cl.on_chat_start
async def on_chat_start():
    """Runs once per new chat: each browser chat gets its own history."""
    cl.user_session.set("chat", create_chat())


@cl.on_message
async def on_message(message: cl.Message):
    chat = cl.user_session.get("chat")
    reply = cl.Message(content="", author=BOT_NAME)

    try:
        async for chunk in await chat.send_message_stream(message.content):
            if chunk.text:
                await reply.stream_token(chunk.text)
    except Exception as e:
        reply.content = f"⚠️ Something went wrong:\n\n`{e}`"

    await reply.send()
