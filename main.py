import os
import random
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from fal_data import FAL_DATABASE, ESTEKHARE_DATABASE

# ---------------------------------------------------------
# ۱. سرور Flask برای زنده نگه داشتن وب سرویس در Render
# ---------------------------------------------------------
app_flask = Flask(__name__)

@app_flask.route('/')
def health_check():
    return "Fal Bot is running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

# ---------------------------------------------------------
# ۲. دریافت توکن ربات
# ---------------------------------------------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# منوی اصلی دکمه‌های شیشه‌ای
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔮 گرفتن فال آنلاین (تصویری)", callback_data="get_fal")],
        [InlineKeyboardButton("📿 استخاره آنلاین", callback_data="get_estekhare")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ---------------------------------------------------------
# ۳. هاندر دستور /start
# ---------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "سلام! به ربات فال و طالع‌بینی خوش آمدید. 🌟\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard())

# ---------------------------------------------------------
# ۴. پردازش کلیک روی دکمه‌ها
# ---------------------------------------------------------
async def button_click_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "get_fal":
        # انتخاب یک فال به صورت تصادفی
        selected_fal = random.choice(FAL_DATABASE)
        
        caption_text = (
            f"📜 **فال شماره {selected_fal['id']}**\n\n"
            f"✨ **{selected_fal['title']}**\n\n"
            f"📝 {selected_fal['description']}"
        )
        
        # ارسال عکس به همراه شماره فال و تعبیر
        await query.message.reply_photo(
            photo=selected_fal["photo_url"],
            caption=caption_text,
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )

    elif query.data == "get_estekhare":
        selected_estekhare = random.choice(ESTEKHARE_DATABASE)
        await query.message.reply_text(
            selected_estekhare["text"],
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )

# ---------------------------------------------------------
# ۵. اجرای برنامه
# ---------------------------------------------------------
def main():
    if not TELEGRAM_TOKEN:
        print("خطا: TELEGRAM_TOKEN تنظیم نشده است!")
        return

    # اجرای وب‌سرور Flask در یک Thread جداگانه
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # ساخت ربات تلگرام
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click_handler))

    print("ربات فال با موفقیت روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
