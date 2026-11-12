"""
Styled terminal chatbot powered by Google Gemini.

Run:  python app.py
Commands inside the chat:
    /reset  -> clear conversation history
    /exit   -> quit  (Ctrl+C also works)
"""

import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.markup import escape
from rich.panel import Panel
from rich.rule import Rule

# ---------------------------------------------------------------------------
# 1. Configuration (loaded from the .env file)
# ---------------------------------------------------------------------------
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

SYSTEM_PROMPT = (
    "You are a helpful, friendly assistant. "
    "Keep answers clear and concise unless the user asks for detail."
)

# ---------------------------------------------------------------------------
# 2. Look & feel  -- change these to customize the appearance
# ---------------------------------------------------------------------------
APP_TITLE = "🤖 My Gemini Chatbot"

USER_LABEL = "🫵 You"
USER_COLOR = "cyan"

BOT_LABEL = "🤖 Bot"
BOT_COLOR = "green"

HEADER_COLOR = "magenta"
DIVIDER_COLOR = "grey50"

console = Console()


def print_header() -> None:
    """Banner shown once at the very top."""
    console.clear()
    console.print(
        Panel(
            f"[bold {HEADER_COLOR}]{APP_TITLE}[/]\n"
            f"[dim]Model: {MODEL_NAME}[/dim]",
            border_style=HEADER_COLOR,
            padding=(1, 4),
        ),
        justify="center",
    )
    console.print("[dim]Commands: /reset to clear history, /exit to quit[/dim]\n")


def check_config() -> None:
    """Stop early with a clear message if the API key is missing."""
    if not API_KEY or API_KEY == "your_api_key_here":
        console.print("[bold red]Error:[/] GEMINI_API_KEY is missing. Add it to your .env file.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# 3. Chat session
# ---------------------------------------------------------------------------
def create_chat(client: genai.Client):
    """Create a chat session. The SDK stores the history for us."""
    return client.chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7,
        ),
    )


def bot_panel(content) -> Panel:
    """The box the bot's reply is drawn in."""
    return Panel(
        content,
        title=f"[bold {BOT_COLOR}]{BOT_LABEL}[/]",
        title_align="left",
        border_style=BOT_COLOR,
        padding=(1, 2),
    )


def stream_reply(chat, user_message: str) -> None:
    """Send a message and render the reply live as it streams in."""
    full_text = ""
    with Live(
        bot_panel("[dim]Thinking...[/dim]"),
        console=console,
        refresh_per_second=10,
        vertical_overflow="visible",
    ) as live:
        for chunk in chat.send_message_stream(user_message):
            if chunk.text:
                full_text += chunk.text
                live.update(bot_panel(Markdown(full_text)))


# ---------------------------------------------------------------------------
# 4. Main loop
# ---------------------------------------------------------------------------
def main() -> None:
    check_config()
    client = genai.Client(api_key=API_KEY)
    chat = create_chat(client)

    print_header()

    while True:
        console.print(Rule(style=DIVIDER_COLOR))
        try:
            user_input = console.input(f"[bold {USER_COLOR}]{USER_LABEL}:[/] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold]Goodbye! 👋[/]")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/exit", "/quit"):
            console.print("[bold]Goodbye! 👋[/]")
            break

        if user_input.lower() == "/reset":
            chat = create_chat(client)
            print_header()
            console.print("[yellow]Conversation cleared.[/yellow]")
            continue

        console.print()
        try:
            stream_reply(chat, user_input)
        except Exception as e:
            console.print(f"[bold red][Error][/] {escape(str(e))}")


if __name__ == "__main__":
    main()
