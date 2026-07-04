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
    
    # أرقام للتحويل من العربية إلى الإنجليزية
    arabic_digits = '٠١٢٣٤٥٦٧٨٩'
    english_digits = '0123456789'
    trans_table = str.maketrans(arabic_digits, english_digits)
    
    for url in urls:
        try:
            res = scraper.get(url, timeout=15)
            if res.status_code == 200:
                # تحويل الأرقام العربية لإنجليزية ومسح الفواصل
                text = res.text.translate(trans_table).replace("،", "").replace(".", "")
                
                # نبحث عن كلمة "الكفاح"
                if "الكفاح" in text:
                    # نحدد موقع الكلمة
                    idx = text.find("الكفاح")
                    # نقتطع بس 200 حرف بعد كلمة الكفاح (حتى نتجاهل باقي المحافظات والأخبار)
                    context = text[idx:idx+200]
                    
                    # هسه نستخرج الأرقام من هذا المربع الصغير فقط
                    prices = re.findall(r'15[3-6]\d', context)
                    
                    if len(prices) >= 2:
                        prices = sorted(list(set([int(p) for p in prices])))
                        return prices[-1], prices[0] # الأعلى بيع والأقل شراء من ضمن الكفاح فقط
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue
    return None, None
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
