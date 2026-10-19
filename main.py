import os
import logging
import telebot
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is missing!")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "📚 *Welcome to Forex Academy!*\n\n"
        "Learn currency pairs, economic terms, and market fundamentals with simple interactive guides.\n\n"
        "Type any question about forex to chat!"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_ai_chat(message):
    status_msg = bot.reply_to(message, "Thinking... 📊")
    try:
        response = requests.post(
            "https://text.pollinations.ai/",
            json={
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful educational tutor explaining basic foreign exchange concepts. Keep explanations strictly educational, simple, and factual without financial advice."
                    },
                    {"role": "user", "content": message.text}
                ]
            },
            timeout=25
        )
        if response.status_code == 200:
            bot.edit_message_text(response.text, chat_id=message.chat.id, message_id=status_msg.message_id)
        else:
            bot.edit_message_text("⚠️ Educational assistant is busy right now. Try again shortly.", chat_id=message.chat.id, message_id=status_msg.message_id)
    except Exception as e:
        logger.error(f"Error: {e}")
        bot.edit_message_text("⚠️ Could not process your request.", chat_id=message.chat.id, message_id=status_msg.message_id)

if __name__ == "__main__":
    logger.info("Bot started polling...")
    bot.infinity_polling()
