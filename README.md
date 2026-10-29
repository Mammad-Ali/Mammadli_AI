# Mammadli AI Bot 🤖

[![Open in Telegram](https://img.shields.io/badge/Telegram-@Mammadli__AI__Bot-26A5E4?logo=telegram&logoColor=white)](https://t.me/Mammadli_AI_Bot)

A Telegram bot that answers your questions using Google's Gemini 2.5 Flash. You can ask it anything, get it to write code or translate a text.

👉 **Try it here: [t.me/Mammadli_AI_Bot](https://t.me/Mammadli_AI_Bot)**

## Features
- answers any message with `gemini-2.5-flash`
- proper formatting in Telegram: bold, lists, code blocks, links
- long answers are split into several messages instead of getting cut off
- retries when Google's servers are busy and tells you when something goes wrong

## Built with
- Python
- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)
- [google-genai](https://github.com/googleapis/python-genai)
- python-dotenv
- Flask (small web server so the bot can run on Render)

## Running it yourself
1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file with your keys:
   ```
   TELEGRAM_TOKEN=your_telegram_bot_token
   GEMINI_API_KEY=your_gemini_api_key
   ```
3. Start the bot:
   ```bash
   python firstatempt.py
   ```

## Files
- `firstatempt.py` - the bot itself
- `formatting.py` - converts Gemini's markdown to Telegram HTML and splits long messages
- `requirements.txt` - dependencies
