import os
import re
import asyncio
import subprocess
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

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom!\n\n"
        "YouTube video linkini yubor.\n"
        "Men senga **audio (m4a)** qilib beraman 🎧"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not YOUTUBE_REGEX.match(text):
        await update.message.reply_text("❌ Bu YouTube linkga o‘xshamaydi.")
        return

    await update.message.reply_text("🎵 YouTube link qabul qilindi\n⏳ Audio tayyorlanyapti...")

    output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    cmd = [
        "yt-dlp",
        "-f", "bestaudio",
        "-x",
        "--audio-format", "m4a",
        "--audio-quality", "0",
        "-o", output_template,
        text
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()

        files = os.listdir(DOWNLOAD_DIR)
        if not files:
            raise Exception("Audio topilmadi")

        audio_path = os.path.join(DOWNLOAD_DIR, files[0])

        await update.message.reply_audio(
            audio=open(audio_path, "rb"),
            caption="🎧 Tayyor!"
        )

        os.remove(audio_path)

    except Exception as e:
        await update.message.reply_text("❌ Xatolik yuz berdi. Boshqa video urinib ko‘r.")
        print("ERROR:", e)


def main():
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN topilmadi")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 YT Audio bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
