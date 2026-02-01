import os
import re
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

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

YOUTUBE_REGEX = re.compile(
    r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"
)

# ========= COMMAND =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom!\n\n"
        "YouTube video linkini yubor.\n"
        "Men senga audiosini (mp3) qilib beraman 🎧"
    )

# ========= MESSAGE =========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    if not YOUTUBE_REGEX.match(text):
        await update.message.reply_text("❌ Bu YouTube linkga o‘xshamaydi.")
        return

    wait_msg = await update.message.reply_text("⏳ Audio tayyorlanyapti, kut...")

    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    command = [
        "yt-dlp",
        "-x",
        "--audio-format",
        "mp3",
        "-o",
        output_path,
        text
    ]

    try:
        subprocess.run(command, check=True)

        files = os.listdir(DOWNLOAD_DIR)
        if not files:
            raise Exception("Audio topilmadi")

        file_path = os.path.join(DOWNLOAD_DIR, files[0])

        with open(file_path, "rb") as audio:
            await context.bot.send_audio(
                chat_id=update.message.chat_id,
                audio=audio
            )

        await wait_msg.delete()

    except Exception as e:
        await update.message.reply_text("❌ Xatolik yuz berdi. Boshqa video urinib ko‘r.")
        print(e)

    finally:
        for f in os.listdir(DOWNLOAD_DIR):
            try:
                os.remove(os.path.join(DOWNLOAD_DIR, f))
            except:
                pass

# ========= RUN =========
def main():
    if not TOKEN:
        raise RuntimeError("TOKEN topilmadi")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 YT Audio bot ishga tushdi")
    app.run_polling()

if __name__ == "__main__":
    main()
