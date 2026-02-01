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

# 🔒 MAJBURIY KANAL
REQUIRED_CHANNEL = "@aiyordamchi"

YOUTUBE_REGEX = re.compile(
    r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"
)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ========= A'ZOLIK TEKSHIRISH =========
async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# ========= START =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    is_subscribed = await check_subscription(user_id, context)
    if not is_subscribed:
        await update.message.reply_text(
            "❌ Botdan foydalanish uchun kanalga a’zo bo‘lishingiz kerak.\n\n"
            "👉 https://t.me/aiyordamchi\n\n"
            "A’zo bo‘lgach, /start ni qayta bosing."
        )
        return

    await update.message.reply_text(
        "👋 Salom!\n\n"
        "Men sizga YouTube videoni **audio**ga aylantirib beraman 🤖🎧\n\n"
        "YouTube link yuboring."
    )


# ========= MESSAGE =========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    # 🔒 A'ZOLIKNI HAR SAFAR TEKSHIRAMIZ
    is_subscribed = await check_subscription(user.id, context)
    if not is_subscribed:
        await update.message.reply_text(
            "❌ Avval kanalga a’zo bo‘ling:\n"
            "👉 https://t.me/aiyordamchi"
        )
        return

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
        await update.message.reply_text(
            "❌ Xatolik yuz berdi.\n"
            "Boshqa video urinib ko‘ring."
        )
        print("ERROR:", e)


# ========= RUN =========
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
