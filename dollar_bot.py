import os
import re
import requests
import cloudscraper
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@DollarNowIQ"
URL = "https://dollar-iraq.com/"

def get_real_price():
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
    try:
        # إضافة headers قوية لتبدو كأننا متصفح حقيقي
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        res = scraper.get(URL, headers=headers, timeout=20)
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # استخراج النص من كامل الصفحة
            text = soup.get_text(separator=" ")
            text = text.replace(",", "").replace(".", "")
            
            # البحث عن الأسعار (نطاق 1400 - 1699)
            prices = re.findall(r'\b(1[4-6]\d{2})\b', text)
            
            if prices:
                unique_prices = sorted(list(set([int(p) for p in prices])))
                # إذا وجدنا أكثر من سعر، الأول هو الشراء والأخير هو البيع
                if len(unique_prices) >= 2:
                    return unique_prices[-1], unique_prices[0]
    except Exception as e:
        print(f"Error fetching data: {e}")
    return None, None

if __name__ == "__main__":
    sell, buy = get_real_price()
    if sell and buy:
        print(f"✅ تم السحب: {sell} بيع / {buy} شراء")
        # هنا أضف كود النشر الخاص بك
    else:
        print("❌ فشل السحب - الموقع يحتاج تحديث كود أو حظر الـ IP")
