# Telegram AI Assistant Bot 🤖

A lightweight and secure Telegram bot powered by Google's **Gemini 2.5 Flash** model. This assistant can answer general questions, generate code snippets, and translate texts with structured Markdown formatting.

## Features
- ⚡ **Fast Responses:** Utilizes the efficient `gemini-2.5-flash` model via the official Google GenAI SDK.
- 🎨 **Rich Formatting:** Full Markdown support for code blocks, lists, and typography in Telegram.
- 🛠️ **Robust Architecture:** Includes error handling (`try-except` blocks) to prevent crashes during API downtime.
- 🔒 **Security First:** Implements environment variables (`.env`) to isolate and protect sensitive API tokens.

## Tech Stack
- **Language:** Python 3.12
- **Framework:** `pyTelegramBotAPI` (Telebot)
- **AI Integration:** `google-genai` SDK
- **Environment Management:** `python-dotenv`

## Project Structure
```text
├── ai_bot.py          # Main bot application logic
├── .env               # Secret API keys (Excluded from GitHub)
├── .gitignore         # Git rules to ignore sensitive files
└── requirements.txt   # List of project dependencies