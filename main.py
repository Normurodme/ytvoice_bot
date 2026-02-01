import os
import re
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ================== SOZLAMALAR ==================
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REQUIRED_CHANNEL = "@aiyordamchi"

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

YOUTUBE_REGEX = re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+")
INSTAGRAM_REGEX = re.compile(r"(https?://)?(www\.)?(instagram\.com|instagr\.am)/.+")

# ================== A'ZOLIK TEKSHIRISH ==================
async def check_subscription(user_id, context):
    try:
        member = await context.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ================== A'ZOLIK XABARI ==================
async def send_subscribe_message(update: Update):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 AIyordamchi", url="https://t.me/aiyordamchi")],
        [InlineKeyboardButton("✅ Tasdiqlash", callback_data="check_sub")]
    ])

    await update.message.reply_text(
        "❌ Botdan foydalanish uchun kanalga a’zo bo‘lishingiz kerak.\n\n"
        "👉 Kanalga a’zo bo‘ling va **Tasdiqlash** tugmasini bosing.",
        reply_markup=keyboard
    )

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(update.message.from_user.id, context):
        await send_subscribe_message(update)
        return

    await update.message.reply_text(
        "👋 Salom!\n\n"
        "Men sizga **Instagram va YouTube** videolarini audio formatga aylantirib beraman 🎧\n\n"
        "🔗 Link yuborishingiz mumkin."
    )

# ================== CALLBACK ==================
async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check_sub":
        if await check_subscription(query.from_user.id, context):
            await query.message.edit_text(
                "✅ A’zolik tasdiqlandi!\n\n"
                "Instagram yoki YouTube link yuboring 🎧"
            )
        else:
            await query.answer("❌ Hali kanalga a’zo emassiz!", show_alert=True)

# ================== ASOSIY HANDLER ==================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(update.message.from_user.id, context):
        await send_subscribe_message(update)
        return

    url = update.message.text.strip()

    is_youtube = YOUTUBE_REGEX.match(url)
    is_instagram = INSTAGRAM_REGEX.match(url)

    if not is_youtube and not is_instagram:
        await update.message.reply_text(
            "❌ Bu Instagram yoki YouTube link emas."
        )
        return

    await update.message.reply_text(
        "🎵 Link qabul qilindi\n"
        "⚡ Audio tayyorlanmoqda..."
    )

    output = os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s")

    # ===== yt-dlp universal buyruq =====
    cmd = [
        "yt-dlp",
        "-f", "bestaudio/best",
        "--no-playlist",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",
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

        file_path = os.path.join(DOWNLOAD_DIR, files[0])

        await update.message.reply_audio(
            audio=open(file_path, "rb"),
            caption="🎧 Tayyor!"
        )

        os.remove(file_path)

    except:
        await update.message.reply_text(
            "❌ Audio chiqarilmadi.\n"
            "👉 Video yopiq, juda uzun yoki muammoli bo‘lishi mumkin."
        )

# ================== RUN ==================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Instagram + YouTube Audio Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
