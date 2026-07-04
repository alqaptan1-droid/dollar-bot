import cloudscraper
from bs4 import BeautifulSoup
import re
import requests
import os
import time

# قراءة التوكن من إعدادات GitHub بأمان
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@DollarNowIQ"
sites = ["https://dollar-iraq.com", "https://iraqprices.com"]

def normalize_arabic_numbers(text):
    arabic_digits = '٠١٢٣٤٥٦٧٨٩'
    english_digits = '0123456789'
    translation_table = str.maketrans(arabic_digits, english_digits)
    return text.translate(translation_table).replace("،", ",")

def get_price_details():
    scraper = cloudscraper.create_scraper()
    for site in sites:
        try:
            response = scraper.get(site, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                normalized_text = normalize_arabic_numbers(soup.get_text(" ", strip=True))
                # (هنا بقية الكود الخاص بك اللي يحلل السعر...)
                # تأكد أن الكود يرجع النتيجة بشكل صحيح
        except: continue
    return None

# أضف باقي دوال الإرسال وتنسيق الرسالة هنا...
# ملاحظة: احذف جزئية الـ HTTPServer والـ threading لأنها لا تعمل في GitHub Actions
