#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import keys
from src.functions import initialize_tweepy

BOT_TOKEN = keys.telegram_bot_token

if not BOT_TOKEN or BOT_TOKEN == "your_telegram_bot_token_here":
    print("Error: TELEGRAM_BOT_TOKEN not set in .env")
    sys.exit(1)

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send me any message and I'll post it as a tweet!"
    )


async def tweet_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if len(text) > 280:
        await update.message.reply_text(
            f"Tweet is too long ({len(text)}/280 characters). Please shorten it."
        )
        return

    try:
        client, _ = initialize_tweepy()
        client.create_tweet(text=text)
        await update.message.reply_text(f"Posted! {text}")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tweet_message))

    print("Telegram bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
