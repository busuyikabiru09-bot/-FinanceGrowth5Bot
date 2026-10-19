import logging
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Policy-Safe Welcome Text
WELCOME_TEXT = (
    "📚 **Welcome to Forex Academy!**\n\n"
    "Learn the fundamentals of foreign exchange, currency pairs, "
    "and market concepts with clean, structured educational guides."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /start command with an educational menu."""
    user = update.effective_user
    if not update.message:
        return

    keyboard = [
        [
            InlineKeyboardButton("📖 Forex Basics", callback_data="basics"),
            InlineKeyboardButton("💱 Currency Pairs", callback_data="pairs")
        ],
        [
            InlineKeyboardButton("📊 Technical Terms", callback_data="terms"),
            InlineKeyboardButton("ℹ️ About Academy", callback_data="about")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"Hello {user.first_name}! 👋\n\n{WELCOME_TEXT}\n\nSelect a topic below or type any question about forex education!"
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles button menu selections."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "basics":
        text = (
            "📖 **Forex Basics:**\n\n"
            "The Foreign Exchange (Forex) market is a global decentralized marketplace "
            "for trading national currencies. It determines exchange rates for every currency.\n\n"
            "• **Market Hours:** Operates 24/5 globally across major centers.\n"
            "• **Base & Quote:** In EUR/USD, EUR is the base currency, and USD is the quote."
        )
        await query.message.reply_text(text, parse_mode="Markdown")

    elif data == "pairs":
        text = (
            "💱 **Currency Pair Categories:**\n\n"
            "1. **Majors:** Pairs involving USD (e.g., EUR/USD, GBP/USD, USD/JPY).\n"
            "2. **Minors:** Major currencies excluding USD (e.g., EUR/GBP, EUR/AUD).\n"
            "3. **Exotics:** One major currency paired with an emerging economy currency."
        )
        await query.message.reply_text(text, parse_mode="Markdown")

    elif data == "terms":
        text = (
            "📊 **Key Educational Terms:**\n\n"
            "• **Pip:** Percentage in Point (smallest price change).\n"
            "• **Spread:** Difference between bid and ask prices.\n"
            "• **Leverage:** Ratio of margin to trading capital.\n"
            "• **Risk Management:** Strategies used to protect capital."
        )
        await query.message.reply_text(text, parse_mode="Markdown")

    elif data == "about":
        text = (
            "ℹ️ **About Forex Academy:**\n\n"
            "This bot provides educational reference materials and terminology "
            "guides for economic literacy."
        )
        await query.message.reply_text(text, parse_mode="Markdown")


async def handle_ai_educational_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles freeform questions using Pollinations keyless AI."""
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    status_msg = await update.message.reply_text("Thinking... 📊")

    try:
        response = requests.post(
            "https://text.pollinations.ai/",
            json={
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are an educational tutor explaining basic foreign exchange concepts. "
                            "Do NOT give financial advice, buy/sell signals, or guarantee profits. "
                            "Keep explanations factual, simple, and strictly educational."
                        )
                    },
                    {"role": "user", "content": user_text}
                ]
            },
            timeout=25
        )
        if response.status_code == 200:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                text=response.text
            )
        else:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                text="⚠️ Education assistant is busy right now. Try again shortly."
            )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=status_msg.message_id,
            text="⚠️ Could not process your educational request."
        )


def main() -> None:
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is missing!")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_ai_educational_chat))

    logger.info("Forex Education Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
