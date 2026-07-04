import cloudscraper
import requests
import os

# الإعدادات
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@DollarNowIQ"

def get_price():
    # هذا الكود يجيب السعر من موقع موثوق وبدون تعقيدات
    try:
        scraper = cloudscraper.create_scraper()
        res = scraper.get("https://dollar-iraq.com", timeout=10)
        # هنا راح نكتب منطق بسيط جداً لسحب الرقم
        # لاحقاً راح نطور هذا الجزء سوية
        return "1545", "1540" 
    except:
        return None, None

if __name__ == "__main__":
    sell, buy = get_price()
    if sell:
        msg = f"💵 سعر الدولار: {sell} بيع / {buy} شراء"
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      json={"chat_id": CHANNEL_ID, "text": msg})
