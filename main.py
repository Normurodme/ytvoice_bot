import os
import re
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

YOUTUBE_REGEX = re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+")
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ================= AUDIO YUKLASH =================
async def download_audio(url, chat_id, context):
    output = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    cmd = [
        "yt-dlp",
        "-f", "bestaudio[ext=m4a]/bestaudio",
        "--extract-audio",
        "--audio-format", "mp3",
        "--no-playlist",
        "--geo-bypass",
        "--no-check-certificate",
        "--socket-timeout", "10",
        "-o", output,
        url
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await process.communicate()

        files = os.listdir(DOWNLOAD_DIR)
        if not files:
            raise Exception("Audio topilmadi")

        path = os.path.join(DOWNLOAD_DIR, files[0])

        await context.bot.send_audio(
            chat_id=chat_id,
            audio=open(path, "rb"),
            caption="🎧 Audio tayyor!"
        )

        os.remove(path)

    except:
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Audio yuklashda xatolik bo‘ldi."
        )

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom!\n\n"
        "Men YouTube videoni audio formatga aylantirib beraman 🎧\n\n"
        "YouTube link yuboring."
    )

# ================= MESSAGE =================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not YOUTUBE_REGEX.match(text):
        await update.message.reply_text("❌ Bu YouTube link emas.")
        return

    await update.message.reply_text(
        "⚡ Video qabul qilindi\n"
        "🎧 Audio tayyorlanmoqda, biroz kuting..."
    )

    asyncio.create_task(
        download_audio(text, update.message.chat_id, context)
    )

# ================= RUN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 YT Audio bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
