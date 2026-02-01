import os
import re
import asyncio
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REQUIRED_CHANNEL = "@aiyordamchi"

YOUTUBE_REGEX = re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+")
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ========= A'ZOLIK =========
async def check_subscription(user_id, context):
    try:
        member = await context.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def send_subscribe_message(update: Update):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 AIyordamchi", url="https://t.me/aiyordamchi")],
        [InlineKeyboardButton("✅ Tasdiqlash", callback_data="check_sub")]
    ])
    await update.message.reply_text(
        "❌ Botdan foydalanish uchun kanalga a’zo bo‘lishingiz kerak.\n\n"
        "👉 A’zo bo‘lib, **Tasdiqlash** ni bosing.",
        reply_markup=keyboard
    )

# ========= START =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(update.message.from_user.id, context):
        await send_subscribe_message(update)
        return

    await update.message.reply_text(
        "👋 Salom!\n\n"
        "Men YouTube videoni **tezkor audio**ga aylantirib beraman 🎧\n\n"
        "YouTube link yuboring."
    )

# ========= CALLBACK =========
async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "check_sub":
        if await check_subscription(query.from_user.id, context):
            await query.message.edit_text("✅ A’zolik tasdiqlandi!\n\nLink yuboring 🎧")
        else:
            await query.answer("❌ Kanalga a’zo emassiz!", show_alert=True)

# ========= MESSAGE =========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(update.message.from_user.id, context):
        await send_subscribe_message(update)
        return

    text = update.message.text.strip()
    if not YOUTUBE_REGEX.match(text):
        await update.message.reply_text("❌ Bu YouTube link emas.")
        return

    await update.message.reply_text(
        "🎵 Link qabul qilindi\n"
        "⚡ Audio tez tayyorlanmoqda..."
    )

    output = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    cmd = [
        "yt-dlp",
        "-f", "bestaudio[ext=m4a]/bestaudio",
        "--no-playlist",
        "--no-check-certificate",
        "--no-warnings",
        "-o", output,
        text
    ]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await proc.communicate()

        files = os.listdir(DOWNLOAD_DIR)
        if not files:
            raise Exception("Audio topilmadi")

        path = os.path.join(DOWNLOAD_DIR, files[0])

        await update.message.reply_audio(
            audio=open(path, "rb"),
            caption="🎧 Tayyor!"
        )

        os.remove(path)

    except:
        await update.message.reply_text(
            "❌ Audio chiqarilmadi.\n"
            "👉 Juda uzun yoki yopiq video bo‘lishi mumkin."
        )

# ========= RUN =========
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
