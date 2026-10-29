import os
import time
import telebot
from google import genai
from google.genai import types, errors
from dotenv import load_dotenv
from flask import Flask
import multiprocessing

from formatting import markdown_to_html, split_message

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("API tokens are missing in .env file")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
ai_client = genai.Client(api_key=GEMINI_API_KEY)

AI_CONFIG = types.GenerateContentConfig(
    system_instruction=(
        "You are a friendly and smart AI assistant in Telegram. "
        "Answer clearly and keep your answers well structured, use emojis to make them look nice. "
        "If someone asks you to write code, always put it in code blocks. "
        "Reply in English unless the user writes to you in another language."
    ),
    temperature=0.7
)

ERROR_MSG = "❌ Something went wrong, please try again later."

app = Flask('')

@app.route('/')
def home():
    return "I'm alive and running!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Hi! 🤖 I'm your personal AI assistant.\n"
        "You can ask me anything, get me to write some code "
        "or translate a text. Just send me a message!"
    )
    bot.reply_to(message, welcome_text)

def ask_gemini(text):
    for attempt in range(3):
        try:
            response = ai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=text,
                config=AI_CONFIG
            )
            answer = (response.text or '').strip()
            if not answer:
                # happens when gemini blocks the answer
                return "🤔 I couldn't answer that one. Try asking in a different way."
            return answer
        except errors.APIError as e:
            print(f"Gemini error: {e}")
            if e.code in (500, 503) and attempt < 2:
                time.sleep(2)
                continue
            if e.code in (500, 503):
                return "⚠️ Google's servers are overloaded right now. Please try again in a minute!"
            if e.code == 429:
                return "⏳ Too many requests. Wait a minute and try again!"
            return ERROR_MSG
        except Exception as e:
            print(f"Error: {e}")
            return ERROR_MSG

def send_part(chat_id, text, edit_id=None):
    try:
        if edit_id:
            bot.edit_message_text(markdown_to_html(text), chat_id, edit_id, parse_mode='HTML')
        else:
            bot.send_message(chat_id, markdown_to_html(text), parse_mode='HTML')
    except telebot.apihelper.ApiTelegramException:
        # telegram couldn't parse the html, send plain text instead
        if edit_id:
            bot.edit_message_text(text, chat_id, edit_id)
        else:
            bot.send_message(chat_id, text)

@bot.message_handler(content_types=['text'])
def handle_ai_request(message):
    waiting_msg = bot.send_message(message.chat.id, "🤖 Thinking...")
    answer = ask_gemini(message.text)

    # telegram messages can't be longer than 4096 chars so long answers go in parts
    parts = split_message(answer)
    send_part(message.chat.id, parts[0], edit_id=waiting_msg.message_id)
    for part in parts[1:]:
        send_part(message.chat.id, part)

if __name__ == "__main__":
    flask_process = multiprocessing.Process(target=run_flask)
    flask_process.daemon = True
    flask_process.start()

    print("AI Bot successfully started...")
    bot.infinity_polling()
