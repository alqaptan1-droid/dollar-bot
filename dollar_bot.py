import cloudscraper
from bs4 import BeautifulSoup
import re
import requests
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@DollarNowIQ"

# نستخدم مواقع متعددة كخطة احتياطية
sites = ["https://dollar-iraq.com", "https://iraqprices.com"]

def get_price_details():
    scraper = cloudscraper.create_scraper()
    for site in sites:
        try:
            response = scraper.get(site, timeout=15)
            if response.status_code == 200:
                text = response.text.replace("،", ".") # معالجة الفواصل
                # نبحث عن أي رقم يتكون من 3 أرقام (154x)
                prices = re.findall(r'15[3-5]\d', text)
                prices = sorted(list(set([int(p) for p in prices])))
                
                if len(prices) >= 2:
                    return "بورصة الكفاح🔺", max(prices), min(prices)
        except:
            continue
    return None

def send_message(msg):
    api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(api, json={"chat_id": CHANNEL_ID, "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    result = get_price_details()
    if result:
        market, sell_p, buy_p = result
        message = (
            f"💵 *تحديث سعر الدولار الآن*\n\n"
            f"📍 *{market}*\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"📈 *البيع:* {sell_p:,} دينار ➔ *{sell_p * 100:,}*\n"
            f"📉 *الشراء:* {buy_p:,} دينار ➔ *{buy_p * 100:,}*\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"https://t.me/DollarNowIQ"
        )
        send_message(message)
    else:
        print("❌ لم يتم العثور على أسعار، جرب زيادة نطاق البحث في الكود.")
