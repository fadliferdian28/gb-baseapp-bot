from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime, timedelta

# === GANTI DENGAN TOKEN BOT KAMU ===
BOT_TOKEN = "8210598767:AAHjF7B5JGAb8Nf8Uw3NlR7WA4jRl7riyMg"

# Data disimpan sementara
posts = {}   # { link: {"user": username, "done": set(), "time": datetime } }
user_posts = {}  # { username: [timestamps] }

MAX_LINKS_PER_DAY = 2

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hai! Kirim link BaseApp kamu di sini untuk ikut GB Like/Recast!\n"
        "Setiap user bisa kirim maksimal 2 link per hari.\n"
        "Format: https://base.app/post/..."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user = update.message.from_user.username or update.message.from_user.first_name
    now = datetime.now()

    # Bersihkan data user_posts yang sudah lebih dari 24 jam
    if user in user_posts:
        user_posts[user] = [t for t in user_posts[user] if now - t < timedelta(hours=24)]

    # Jika pesan berupa link BaseApp
    if "base.app/post/" in text:
        # Cek batas harian user
        count_today = len(user_posts.get(user, []))
        if count_today >= MAX_LINKS_PER_DAY:
            await update.message.reply_text(f"🚫 @{user}, kamu sudah drop {MAX_LINKS_PER_DAY} link hari ini. Coba lagi besok!")
            return

        # Simpan link baru
        posts[text] = {"user": user, "done": set(), "time": now}
        user_posts.setdefault(user, []).append(now)

        await update.message.reply_text(
            f"✅ Link disimpan dari @{user}\n\n"
            f"🔗 {text}\n\n"
            "Silakan like & recast post ini.\nKetik 'done' setelah selesai."
        )

    elif text.lower() == "done":
        if posts:
            last_link = list(posts.keys())[-1]
            posts[last_link]["done"].add(user)
            await update.message.reply_text(f"✅ @{user} sudah like/recast link terakhir.")
        else:
            await update.message.reply_text("❌ Belum ada link yang disimpan.")
    else:
        return  # Abaikan pesan lain

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not posts:
        await update.message.reply_text("📭 Belum ada link yang disimpan.")
        return

    msg = "📋 Status GB Like/Recast BaseApp:\n\n"
    for link, data in posts.items():
        waktu = data['time'].strftime('%H:%M')
        msg += f"🔗 {link}\n👤 {data['user']} ({waktu})\n✅ Done: {', '.join(data['done']) or '-'}\n\n"

    await update.message.reply_text(msg)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("status", status))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 Bot GB BaseApp sedang berjalan...")
app.run_polling()
