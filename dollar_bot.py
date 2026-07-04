import os
import requests
import re
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@DollarNowIQ"

def get_real_price():
    # استخدمنا موقع مختلف كلياً
    url = "https://iraqprices.com/dollar-to-iqd"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        # هنا نستخدم requests العادية مع headers حتى لا يكتشفنا كـ "بوت"
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            text = soup.get_text()
            
            # بحث مباشر عن أي رقم بين 1400 و 1600 في نص الموقع
            prices = re.findall(r'\b(1[4-6]\d{2})\b', text)
            
            if len(prices) >= 2:
                unique_prices = sorted(list(set([int(p) for p in prices])))
                return unique_prices[-1], unique_prices[0]
    except Exception as e:
        print(f"Error: {e}")
    return None, None

if __name__ == "__main__":
    sell, buy = get_real_price()
    if sell and buy:
        print(f"✅ تم سحب الأسعار: {sell} بيع / {buy} شراء")
        # .. (باقي كود النشر تليجرام) ..
    else:
        print("❌ فشل سحب البيانات - حاول تغيير الموقع أو المصدر.")
