import os
import re
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

YOUTUBE_REGEX = re.compile(
    r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom!\n\nYouTube video linkini yubor.\nMen senga audiosini tayyorlab beraman 🎧"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if YOUTUBE_REGEX.match(text):
        await update.message.reply_text(
            "🎵 YouTube link qabul qilindi\nAudio tayyorlanmoqda..."
        )
    else:
        await update.message.reply_text(
            "❌ Bu YouTube linkga o‘xshamaydi.\nIltimos, to‘g‘ri link yubor."
        )

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 YT Audio bot ishga tushdi")
    app.run_polling()

if __name__ == "__main__":
    main()
