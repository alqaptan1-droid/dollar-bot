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
# ===============================================

def normalize_arabic_numbers(text):
    """تحويل الأرقام والـفواصل العربية لضمان دقة القراءة"""
    arabic_digits = '٠١٢٣٤٥٦٧٨٩'
    english_digits = '0123456789'
    translation_table = str.maketrans(arabic_digits, english_digits)
    return text.translate(translation_table).replace("،", ",")

def get_last_posted_prices():
    """خدعة ذكية: قراءة آخر رسالة من القناة حتى نتجنب التكرار"""
    try:
        channel_name = CHANNEL_ID.replace("@", "")
        # ندخل لنسخة الويب من القناة
        res = requests.get(f"https://t.me/s/{channel_name}")
        soup = BeautifulSoup(res.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        if messages:
            return messages[-1].text # نرجع نص آخر رسالة
    except:
        pass
    return ""

def get_price_details():
    scraper = cloudscraper.create_scraper()
    
    for site in sites:
        try:
            response = scraper.get(site, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                normalized_text = normalize_arabic_numbers(soup.get_text(" ", strip=True))

                markets = {
                    "الكفاح": "بورصة الكفاح🔺",
                    "الحارثية": "بورصة الحارثية🔺",
                    "أربيل": "بورصة أربيل🔹",
                    "البصرة": "بورصة البصرة🔹",
                    "السليمانية": "بورصة السليمانية🔹",
                    "الصيرفة": "السوق المحلي (الصيرفة)🏬",
                    "المحلي": "السوق المحلي (الصيرفة)🏬"
                }

                for keyword, market_name in markets.items():
                    if keyword in normalized_text:
                        idx = normalized_text.find(keyword)
                        start_pos = max(0, idx - 100)
                        end_pos = min(len(normalized_text), idx + 200)
                        context_text = normalized_text[start_pos:end_pos]
                        
                        context_cleaned = context_text.replace(",", "").replace(".", "")
                        all_numbers = re.findall(r'\b\d{4,6}\b', context_cleaned)
                        valid_prices = []
                        
                        for num in all_numbers:
                            val = int(num)
                            if 140000 <= val <= 170000:
                                val = round(val / 100)
                            if 1400 <= val <= 1700:
                                if val not in valid_prices:
                                    valid_prices.append(val)
                        
                        # 🎯 التعديل هنا: ناخذ أعلى وأقل سعر من "كل" الأرقام الموجودة بالمربع
                        if len(valid_prices) >= 2:
                            sell_p = max(valid_prices)
                            buy_p = min(valid_prices)
                            return market_name, sell_p, buy_p
                        
                        elif len(valid_prices) == 1:
                            return market_name, valid_prices[0], valid_prices[0]
                            
        except Exception as e:
            print(f"❌ فشل فحص {site}: {e}")

    return None

def send_message(msg):
    api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": msg,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    requests.post(api, json=data)

# ================= نقطة التشغيل =================
if __name__ == "__main__":
    print("🔄 جاري فحص الأسعار من المواقع...")
    result = get_price_details()

    if result:
        market, sell_price, buy_price = result
        
        sell_formatted = f"{sell_price:,}"
        buy_formatted = f"{buy_price:,}"
        sell_100 = f"{sell_price * 100:,}"
        buy_100 = f"{buy_price * 100:,}"
        
        # فحص الذاكرة: هل السعر نفسه موجود بآخر رسالة؟
        last_message_text = get_last_posted_prices()
        clean_market_name = market.replace("🔺", "").replace("🔹", "").replace("🏬", "").strip()
        
        # إذا اسم السوق وسعر البيع وسعر الشراء موجودات نصاً بالرسالة السابقة.. نغلس!
        if clean_market_name in last_message_text and sell_formatted in last_message_text and buy_formatted in last_message_text:
            print("⏸️ الأسعار مطابقة لآخر رسالة في القناة. لن يتم النشر لتجنب الإزعاج.")
        else:
            # 🎯 السعر جديد! صياغة الكليشة الملكية والنشر
            if sell_price != buy_price:
                message = (
                    f"💵 *تحديث سعر الدولار الآن*\n\n"
                    f"📍 *{market}*\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"📈 *البيع:* {sell_formatted} دينار ➔ *{sell_100}*\n"
                    f"📉 *الشراء:* {buy_formatted} دينار ➔ *{buy_100}*\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"https://t.me/DollarNowIQ"
                )
            else:
                message = (
                    f"💵 *تحديث سعر الدولار الآن*\n\n"
                    f"📍 *{market}*\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"💰 *السعر:* {sell_formatted} دينار ➔ *{sell_100}*\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"https://t.me/DollarNowIQ"
                )
            
            send_message(message)
            print(f"📨 تم النشر بنجاح بالتنسيق الاحترافي لـ {market}")
    else:
        print("❌ لم يتم العثور على أسعار حالياً.")
