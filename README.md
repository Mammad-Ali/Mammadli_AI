# Telegram AI Assistant Bot 🤖

A lightweight and secure Telegram bot powered by Google's **Gemini 2.5 Flash** model. This assistant can answer general questions, generate code snippets, and translate texts with structured Markdown formatting.

## Features
- ⚡ **Fast Responses:** Utilizes the efficient `gemini-2.5-flash` model via the official Google GenAI SDK.
- 🎨 **Rich Formatting:** Gemini's Markdown (code blocks, lists, bold, links) is converted to Telegram HTML, with a plain-text fallback.
- 📜 **Long Answers:** Replies longer than Telegram's 4096-character limit are split into several messages.
- 🛠️ **Robust Architecture:** Retries when Google's servers are busy and shows a clear message for rate limits, blocked answers, and other errors.
- 🔒 **Security First:** Implements environment variables (`.env`) to isolate and protect sensitive API tokens.

## Tech Stack
- **Language:** Python 3.12
- **Framework:** `pyTelegramBotAPI` (Telebot)
- **AI Integration:** `google-genai` SDK
- **Environment Management:** `python-dotenv`
- **Hosting:** `flask` keep-alive server for Render

## Project Structure
```text
├── firstatempt.py     # Main bot application logic
├── formatting.py      # Markdown to Telegram HTML conversion and message splitting
├── .env               # Secret API keys (Excluded from GitHub)
├── .gitignore         # Git rules to ignore sensitive files
└── requirements.txt   # List of project dependencies
```