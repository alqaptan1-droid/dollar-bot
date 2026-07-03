import cloudscraper
from bs4 import BeautifulSoup
import re
import time
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ================= الإعدادات =================
BOT_TOKEN = "784339631:AAEP7nCs_foR04V-jZ7ujiylnkDC5eeMewc"
CHANNEL_ID = "@DollarNowIQ"

sites = [
    "https://dollar-iraq.com",
    "https://iraqprices.com"
]

# ===== سيرفر وهمي لإبقاء المنصة شغال 24 ساعة =====
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("البوت شغال توب ضلعي!".encode("utf-8"))

def run_server():
    # Hugging Face يطلب تشغيل السيرفر على بورت 7860 حصراً
    server = HTTPServer(("0.0.0.0", 7860), DummyServer)
    server.serve_forever()
# ===============================================

def normalize_arabic_numbers(text):
    """تحويل الأرقام والـفواصل العربية لضمان دقة القراءة"""
    arabic_digits = '٠١٢٣٤٥٦٧٨٩'
    english_digits = '0123456789'
    translation_table = str.maketrans(arabic_digits, english_digits)
    text = text.translate(translation_table)
    text = text.replace("،", ",")
    return text

def get_price_details():
    scraper = cloudscraper.create_scraper()
    
    for site in sites:
        try:
            response = scraper.get(site, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                raw_text = soup.get_text(" ", strip=True)
                normalized_text = normalize_arabic_numbers(raw_text)

                # تنسيق الأسماء لتتناسب مع التنسيق العريض داخل النجمات
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
                        
                        if len(valid_prices) >= 2:
                            sell_p = max(valid_prices[:2])
                            buy_p = min(valid_prices[:2])
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
        "parse_mode": "Markdown",       # 🎯 تفعيل التنسيق الاحترافي (الخط العريض)
        "disable_web_page_preview": True # إلغاء المعاينة للروابط تماماً
    }
    try:
        response = requests.post(api, json=data)
        if response.status_code != 200:
            print(f"⚠️ خطأ في التيليجرام: {response.text}")
    except Exception as e:
        print(f"❌ فشل إرسال الرسالة: {e}")

# ================= نقطة التشغيل =================
if __name__ == "__main__":
    print("🤖 جاري تشغيل السيرفر الوهمي وبدء البوت...")
    
    # تشغيل السيرفر في مسار منفصل (Thread) لخدع المنصة
    threading.Thread(target=run_server, daemon=True).start()
    
    send_message("✅ *البوت اشتغل وبدأ مراقبة الأسعار بالتنسيق الجديد*")

    last_state = (None, None, None) 

    while True:
        print("\n🔄 جاري فحص الأسعار من المواقع...")
        result = get_price_details()

        if result:
            market, sell_price, buy_price = result
            
            if (market, sell_price, buy_price) != last_state:
                
                # تنسيق الأرقام مع الفواصل (مثل: 1,543 و 154,300)
                sell_formatted = f"{sell_price:,}"
                buy_formatted = f"{buy_price:,}"
                sell_100 = f"{sell_price * 100:,}"
                buy_100 = f"{buy_price * 100:,}"
                
                # 🎯 صياغة الكليشة الملكية مالتك بالملي
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
                print(f"📨 تم النشر بالتنسيق الاحترافي لـ {market}")
                last_state = (market, sell_price, buy_price)
            else:
                print(f"⏸️ الأسعار مستقرة في {market}.")
        else:
            print("❌ لم يتم العثور على أسعار حالياً.")

        # ⏳ الفحص الذكي كل 5 دقائق
        time.sleep(300)