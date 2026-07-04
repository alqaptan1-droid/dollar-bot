import os
import re
import requests
import cloudscraper
from bs4 import BeautifulSoup

# ================= الإعدادات =================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@DollarNowIQ"

# ================= دالة سحب الأسعار =================
def get_real_price():
    urls = ["https://dollar-iraq.com", "https://iraqprices.com"]
    scraper = cloudscraper.create_scraper()
    
    for url in urls:
        try:
            res = scraper.get(url, timeout=15)
            if res.status_code == 200:
                text = res.text.replace("،", "").replace(".", "")
                prices = re.findall(r'15[3-6]\d', text)
                if len(prices) >= 2:
                    prices = sorted(list(set([int(p) for p in prices])))
                    return prices[-1], prices[0]
        except Exception:
            continue
    return None, None

# ================= دالة قراءة آخر رسالة بالقناة =================
def get_last_channel_message():
    try:
        scraper = cloudscraper.create_scraper()
        channel_name = CHANNEL_ID.replace("@", "")
        res = scraper.get(f"https://t.me/s/{channel_name}")
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            messages = soup.find_all('div', class_='tgme_widget_message_text')
            if messages:
                return messages[-1].text
    except Exception as e:
        print(f"Error reading channel: {e}")
    return ""

# ================= دالة النشر للقناة =================
if __name__ == "__main__":
    sell, buy = get_real_price()
    
    if sell and buy:
        sell_str = f"{sell:,}"
        buy_str = f"{buy:,}"
        
        # نقرأ آخر رسالة بالقناة
        last_message = get_last_channel_message()
        
        # نقارن: إذا السعرين موجودات بآخر رسالة، معناها السعر ما تغير
        if sell_str in last_message and buy_str in last_message:
            print(f"⏸️ السعر ما تغير ({sell}/{buy}). ماكو داعي ننشر رسالة جديدة.")
        else:
            message = (
                f"💵 *تحديث سعر الدولار الآن*\n\n"
                f"📍 *بورصة الكفاح🔺*\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"📈 *البيع:* {sell_str} دينار ➔ *{sell * 100:,}*\n"
                f"📉 *الشراء:* {buy_str} دينار ➔ *{buy * 100:,}*\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"https://t.me/DollarNowIQ"
            )
            
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                json={"chat_id": CHANNEL_ID, "text": message, "parse_mode": "Markdown"}
            )
            print(f"✅ تم النشر بالقناة بنجاح: {sell} بيع / {buy} شراء")
    else:
        print("❌ لم يتم العثور على أسعار.")
