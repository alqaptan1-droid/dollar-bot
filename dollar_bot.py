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
    sites = {"Iraq-Prices": "https://iraqprices.com"}
    scraper = cloudscraper.create_scraper()
    
    # تصحيح الأرقام: كل رقم عربي يقابله رقم إنجليزي واحد
    arabic_digits = '٠١٢٣٤٥٦٧٨٩'
    english_digits = '0123456789'
    trans_table = str.maketrans(arabic_digits, english_digits)
    
    for name, url in sites.items():
        try:
            res = scraper.get(url, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                clean_text = soup.get_text(separator=" ").translate(trans_table).replace("،", "").replace(",", "").replace(".", "")
                
                if "الكفاح" in clean_text:
                    idx = clean_text.find("الكفاح")
                    context = clean_text[idx:idx+150]
                    prices = re.findall(r'15\d{2}', context)
                    
                    if len(prices) >= 2:
                        prices = sorted(list(set([int(p) for p in prices])))
                        return prices[-1], prices[0], name 
        except Exception as e:
            print(f"Error reading {name}: {e}")
            continue
    return None, None, None

# ================= دالة قراءة آخر رسالة =================
def get_last_channel_message():
    try:
        scraper = cloudscraper.create_scraper()
        channel_name = CHANNEL_ID.replace("@", "")
        res = scraper.get(f"https://t.me/s/{channel_name}")
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            messages = soup.find_all('div', class_='tgme_widget_message_text')
            return messages[-1].text if messages else ""
    except:
        pass
    return ""

# ================= نقطة التشغيل =================
if __name__ == "__main__":
    sell, buy, source = get_real_price()
    
    if sell and buy:
        print(f"📡 تم جلب الأسعار بنجاح من موقع: {source}")
        sell_str = f"{sell:,}"
        last_message = get_last_channel_message()
        
        if sell_str in last_message:
            print(f"⏸️ السعر مطابق لآخر رسالة ({sell}).")
        else:
            message = (
                f"💵 *تحديث سعر الدولار الآن*\n\n"
                f"📍¦ *بورصة الكفاح*\n"
                f"🔻¦ {sell_str} دينار ➔ {sell * 100:,}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"https://t.me/DollarNowIQ"
            )
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                json={"chat_id": CHANNEL_ID, "text": message, "parse_mode": "Markdown"}
            )
            print(f"✅ تم النشر بنجاح: {sell}")
    else:
        print("❌ لم يتم العثور على أسعار مطابقة.")




