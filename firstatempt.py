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
        "Ты — дружелюбный и умный AI-помощник в Telegram. "
        "Отвечай четко, структурировано, используй эмодзи для красоты. "
        "Если тебя просят написать код, обязательно выделяй его в блоки кода."
    ),
    temperature=0.7
)

OVERLOADED_TEXT = "⚠️ Сервера Google сейчас перегружены. Пожалуйста, попробуй отправить сообщение еще раз через минуту!"
RATE_LIMIT_TEXT = "⏳ Слишком много запросов. Подожди минуту и попробуй снова!"
EMPTY_TEXT = "🤔 Не получилось ответить на это сообщение. Попробуй сформулировать вопрос по-другому."
ERROR_TEXT = "❌ Что-то пошло не так. Попробуй еще раз чуть позже."

app = Flask('')

@app.route('/')
def home():
    return "I'm alive and running!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Привет! 🤖 Я твой персональный AI-ассистент.\n"
        "Ты можешь задать мне любой вопрос, попросить написать код "
        "или перевести текст. Напиши что-нибудь!"
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
            # response.text is None when Gemini blocks the answer or returns nothing
            return (response.text or '').strip() or EMPTY_TEXT
        except errors.APIError as e:
            print(f"Gemini error (attempt {attempt + 1}): {e}")
            if e.code in (500, 503):
                if attempt < 2:
                    time.sleep(2)
                    continue
                return OVERLOADED_TEXT
            if e.code == 429:
                return RATE_LIMIT_TEXT
            return ERROR_TEXT
        except Exception as e:
            print(f"Unexpected error: {e}")
            return ERROR_TEXT

def send_part(chat_id, text, edit_message_id=None):
    try:
        if edit_message_id:
            bot.edit_message_text(markdown_to_html(text), chat_id, edit_message_id, parse_mode='HTML')
        else:
            bot.send_message(chat_id, markdown_to_html(text), parse_mode='HTML')
    except telebot.apihelper.ApiTelegramException:
        # Telegram didn't accept the formatting, so send the text without it
        if edit_message_id:
            bot.edit_message_text(text, chat_id, edit_message_id)
        else:
            bot.send_message(chat_id, text)

@bot.message_handler(content_types=['text'])
def handle_ai_request(message):
    waiting_msg = bot.send_message(message.chat.id, "🤖 Думаю над ответом...")
    response_text = ask_gemini(message.text)

    # Long answers don't fit in one Telegram message, so they are sent in parts
    parts = split_message(response_text)
    send_part(message.chat.id, parts[0], edit_message_id=waiting_msg.message_id)
    for part in parts[1:]:
        send_part(message.chat.id, part)

if __name__ == "__main__":
    flask_process = multiprocessing.Process(target=run_flask)
    flask_process.daemon = True
    flask_process.start()
    
    print("AI Bot successfully started...")
    bot.infinity_polling()