import os
import re
import requests
import cloudscraper
from bs4 import BeautifulSoup

# ================= الإعدادات =================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@DollarNowIQ"
TARGET_URL = "https://dollar-iraq.com"

# ================= دالة سحب الأسعار الموجهة =================
def get_real_price():
    scraper = cloudscraper.create_scraper()
    try:
        res = scraper.get(TARGET_URL, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # استخراج النص وتنظيفه
            text = soup.get_text(separator=" ")
            text = text.replace("،", "").replace(",", "").replace(".", "")
            
            # فلتر: أي رقم يتكون من 4 مراتب ويبدأ بـ 14, 15, أو 16
            # هذا يضمن استبعاد (1310 الرسمي) واستبعاد (2026 السنة)
            prices = re.findall(r'\b(1[4-6]\d{2})\b', text)
            
            if prices:
                # تحويل الأرقام لنوع int وعزل القيم الفريدة
                unique_prices = sorted(list(set([int(p) for p in prices])))
                
                # نأخذ أكبر رقم للبيع وأصغر رقم للشراء من القائمة المفلترة
                if len(unique_prices) >= 2:
                    return unique_prices[-1], unique_prices[0]
                elif len(unique_prices) == 1:
                    return unique_prices[0], unique_prices[0]
    except Exception as e:
        print(f"Error: {e}")
    return None, None

# ================= دالة فحص التغيير والنشر =================
def get_last_channel_message():
    try:
        scraper = cloudscraper.create_scraper()
        res = scraper.get(f"https://t.me/s/{CHANNEL_ID.replace('@', '')}")
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            messages = soup.find_all('div', class_='tgme_widget_message_text')
            return messages[-1].text if messages else ""
    except:
        return ""

if __name__ == "__main__":
    sell, buy = get_real_price()
    
    if sell and buy:
        sell_str, buy_str = f"{sell:,}", f"{buy:,}"
        last_msg = get_last_channel_message()
        
        if sell_str in last_msg and buy_str in last_msg:
            print(f"⏸️ السعر ثابت ({sell}/{buy})")
        else:
            message = (
                f"💵 *تحديث سعر الدولار الآن*\n\n"
                f"📍 *بورصة الكفاح🔺*\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"📈 *البيع:* {sell_str} دينار\n"
                f"📉 *الشراء:* {buy_str} دينار\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"المصدر: dollar-iraq.com"
            )
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                          json={"chat_id": CHANNEL_ID, "text": message, "parse_mode": "Markdown"})
            print(f"✅ تم النشر: {sell} بيع / {buy} شراء")
