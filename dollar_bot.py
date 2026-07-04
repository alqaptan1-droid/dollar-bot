import cloudscraper
from bs4 import BeautifulSoup
import re
import requests
import os

# ================= الإعدادات =================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@DollarNowIQ"

sites = [
    "https://dollar-iraq.com",
    "https://iraqprices.com"
]

def normalize_arabic_numbers(text):
    arabic_digits = '٠١٢٣٤٥٦٧٨٩'
    english_digits = '0123456789'
    translation_table = str.maketrans(arabic_digits, english_digits)
    return text.translate(translation_table).replace("،", ".")

def get_price_details():
    scraper = cloudscraper.create_scraper()
    for site in sites:
        try:
            response = scraper.get(site, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                text = normalize_arabic_numbers(soup.get_text(" ", strip=True))
                
                # البحث عن كلمة "الكفاح" كمفتاح أساسي
                if "الكفاح" in text:
                    idx = text.find("الكفاح")
                    context = text[idx:idx+400]
                    # استخراج الأرقام التي تتراوح بين 1530 و 1560 (سعر السوق الموازي)
                    prices = re.findall(r'\b(15[3-5]\d)\b', context)
                    prices = sorted(list(set([int(p) for p in prices])))
                    
                    if len(prices) >= 2:
                        # أعلى رقم هو البيع، وأقل رقم هو الشراء
                        sell_p = max(prices)
                        buy_p = min(prices)
                        return "بورصة الكفاح🔺", sell_p, buy_p
        except:
            continue
    return None

def send_message(msg):
    api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(api, json={
        "chat_id": CHANNEL_ID, 
        "text": msg, 
        "parse_mode": "Markdown", 
        "disable_web_page_preview": True
    })

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
        print(f"✅ تم نشر السعر: البيع {sell_p} - الشراء {buy_p}")
    else:
        print("❌ لم يتم العثور على الأسعار، تأكد من تحديث الموقع.")
