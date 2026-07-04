import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@DollarNowIQ"

# 1. دالة الرد على /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    now = datetime.now()
    message = (
        f"🙋🏼‍♂️¦ مرحبا عزيزي {user_name}\n"
        f"🔹¦ البوت مربوط بكل البورصات الرئيسيه:\n"
        f"• بورصة الكفاح🔺\n• بورصة الحارثية🔺\n• بورصة أربيل🔹\n"
        f"• بورصة البصرة🔹\n• بورصة السليمانية🔹\n• السوق المحلي🏬\n\n"
        f"البوت تابع الى قناة https://t.me/DollarNowIQ\n\n"
        f"﹎﹎﹎﹎﹎﹎﹎﹎﹎﹎﹎﹎﹎\n"
        f"⏰┊ Time : {now.strftime('%I:%M:%S %p')}\n"
        f"📆┊ Date : {now.strftime('%Y/%m/%d')}"
    )
    await update.message.reply_text(message)

# 2. دالة إرسال التحديث (تستدعى كل ساعة)
def send_update_to_channel():
    # هنا تضع منطق سحب الأسعار الذي اتفقنا عليه
    sell, buy = 1558, 1535 # هذه قيم افتراضية، استبدلها بمنطق السحب
    message = (
        f"💵 *تحديث سعر الدولار الآن*\n\n"
        f"📍 *بورصة الكفاح🔺*\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"📈 *البيع:* {sell:,} دينار ➔ {sell * 100:,}\n"
        f"📉 *الشراء:* {buy:,} دينار ➔ {buy * 100:,}\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"https://t.me/DollarNowIQ"
    )
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                  json={"chat_id": CHANNEL_ID, "text": message, "parse_mode": "Markdown"})

# تشغيل البوت
if __name__ == "__main__":
    # إذا كان الكود يعمل في GitHub Actions للنشر، نحتاج فصله
    # هذه البداية فقط للرد على الرسائل.
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("البوت يعمل الآن...")
    app.run_polling()
