import os
import telebot
from google import genai
from google.genai import types
from dotenv import load_dotenv
from flask import Flask
import threading

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

@bot.message_handler(content_types=['text'])
def handle_ai_request(message):
    waiting_msg = bot.send_message(message.chat.id, "🤖 Думаю над ответом...")
    
    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=message.text,
            config=AI_CONFIG
        )
        bot.edit_message_text(response.text, message.chat.id, waiting_msg.message_id, parse_mode='Markdown')
        
    except Exception as e:
        error_text = f"❌ Error contacting AI: {str(e)}"
        bot.edit_message_text(error_text, message.chat.id, waiting_msg.message_id)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    print("AI Bot successfully started...")
    bot.infinity_polling()