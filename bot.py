import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")


# ================= جلب السعر =================
def get_real_price():
    # المصدر الأساسي
    try:
        response = requests.get(
            "https://prices-api.alawe6663.workers.dev/prices", timeout=10
        )
        data = response.json()
        raw_price = data["dollar"]["parallel"]

        # تحويل السعر إلى رقم صحيح لتجنب مشاكل المقارنة
        price = int(float(str(raw_price).replace(",", "").strip()))

        print(f"المصدر: IraqPrices")
        print(f"السعر: {price}")
        return price, "IraqPrices"

    except Exception as e:
        print(f"فشل المصدر الأساسي: {e}")

    # المصدر الاحتياطي
    try:
        response = requests.get(
            "https://market-rate.m-tbeshe.workers.dev/", timeout=10
        )
        data = response.json()
        raw_price = data["kifah"]

        # تحويل السعر إلى رقم صحيح
        price = int(float(str(raw_price).replace(",", "").strip()))

        print(f"المصدر: MarketRate")
        print(f"السعر: {price}")
        return price, "MarketRate"

    except Exception as e:
        print(f"فشل المصدر الاحتياطي: {e}")

    return None, None


# ================= إرسال =================
def send_message(message):
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHANNEL_ID,
                "text": message,
                "parse_mode": "Markdown",
            },
        )
        print(f"الإرسال: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"خطأ الإرسال: {e}")
        return False


# ================= التشغيل =================
if __name__ == "__main__":
    price, source = get_real_price()

    if price is not None:
        last_price = None

        if os.path.exists("last_price.txt"):
            with open("last_price.txt", "r") as f:
                try:
                    last_price = int(f.read().strip())
                except:
                    pass

        print(f"الحالي: {price} (النوع: {type(price).__name__})")
        print(f"السابق: {last_price} (النوع: {type(last_price).__name__})")

        if price != last_price:
            message = (
                f"🟢 *تحديث سعر الدولار الآن*\n\n"
                f"📍 *بورصة الكفاح *\n"
                f"💵 الـ 100 دولار ➜ *{price*100:,}* دينار\n"
                f"🔸 السعر المفرد ➜ *{price:,}* دينار\n\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"🔗 https://t.me/DollarNowIQ"
             )

            if send_message(message):
                with open("last_price.txt", "w") as f:
                    f.write(str(price))
                print("تم النشر وتحديث ملف السعر القديم.")
        else:
            print("السعر لم يتغير، تم تخطي النشر.")
    else:
        print("فشل جلب السعر من جميع المصادر.")
