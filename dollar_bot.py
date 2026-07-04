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
    
    arabic_digits = '٠١٢٣٤٥٦٧٨٩'
    english_digits = '0123456789'
    trans_table = str.maketrans(arabic_digits, english_digits)
    
    for url in urls:
        try:
            res = scraper.get(url, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                # تحويل النص وتنظيفه
                clean_text = soup.get_text(separator=" ").translate(trans_table).replace("،", "").replace(",", "").replace(".", "")
                
                # البحث عن أي أرقام من 4 مراتب تبدأ بـ 1 (لأن السعر حالياً 1400-1699)
                # وتستثني السنة (2026) والسعر الرسمي (1310)
                all_numbers = re.findall(r'\b(1[4-6]\d{2})\b', clean_text)
                
                prices = sorted(list(set([int(p) for p in all_numbers])))
                
                if len(prices) >= 2:
                    return prices[-1], prices[0] # الأعلى والاقل
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
    except Exception:
        pass
    return ""

# ================= نقطة التشغيل والنشر =================
if __name__ == "__main__":
    sell, buy = get_real_price()
    
    if sell and buy:
        sell_str = f"{sell:,}"
        buy_str = f"{buy:,}"
        
        last_message = get_last_channel_message()
        
        if sell_str in last_message and buy_str in last_message:
            print(f"⏸️ السعر مطابق لآخر رسالة ({sell}/{buy}). لن يتم النشر.")
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
            print(f"✅ تم النشر بنجاح: {sell} بيع / {buy} شراء")
    else:
        print("❌ فشل في جلب أسعار منطقية من المواقع.")
