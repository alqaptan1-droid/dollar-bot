import os
import re
import requests
import cloudscraper
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

# ================= الإعدادات =================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@DollarNowIQ"

# ================= 1. دالة سحب الأسعار الحقيقية من الموقع =================
def get_real_price():
    urls = ["https://dollar-iraq.com", "https://iraqprices.com"]
    scraper = cloudscraper.create_scraper()
    
    for url in urls:
        try:
            res = scraper.get(url, timeout=15)
            if res.status_code == 200:
                text = res.text.replace("،", "").replace(".", "")
                # استخراج الأرقام من 1530 إلى 1560
                prices = re.findall(r'15[3-6]\d', text)
                if len(prices) >= 2:
                    prices = sorted(list(set([int(p) for p in prices])))
                    return prices[-1], prices[0] # الأعلى بيع والأقل شراء
        except Exception:
            continue
    return None, None

# ================= 2. دالة الرد على /start =================
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

# ================= 3. دالة إرسال التحديث للقناة =================
def send_update_to_channel():
    sell, buy = get_real_price()
    
    if sell and buy:
        message = (
            f"💵 *تحديث سعر الدولار الآن*\n\n"
            f"📍 *بورصة الكفاح🔺*\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"📈 *البيع:* {sell:,} دينار ➔ *{sell * 100:,}*\n"
            f"📉 *الشراء:* {buy:,} دينار ➔ *{buy * 100:,}*\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"https://t.me/DollarNowIQ"
        )
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      json={"chat_id": CHANNEL_ID, "text": message, "parse_mode": "Markdown"})
        print(f"✅ تم سحب الأسعار ونشرها بالقناة: {sell} بيع / {buy} شراء")
    else:
        print("❌ لم يتم العثور على أسعار في الموقع حالياً.")

# ================= نقطة التشغيل =================
if __name__ == "__main__":
    # 1. أولاً: نرسل السعر للقناة (هذا اللي يهمنا بالـ GitHub Actions)
    send_update_to_channel()
    
    # 2. ثانياً: نشغل البوت للرد على رسائل الخاص
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("البوت يعمل الآن للرد على الرسائل الخاصة...")
    app.run_polling()
