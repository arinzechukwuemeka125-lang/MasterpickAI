import requests
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    print("ERROR: Secrets missing! Check TELEGRAM_TOKEN and TELEGRAM_CHAT_ID in GitHub Settings > Secrets")
    exit(1)

msg = """🛡️ V24 MOST SURE BANKER - 19th Sept - @2.18

MOST SURE - NO LOSE GUILD:

1. Newcastle vs Hull - 1 @1.35 (99% sure)
2. Athletic Bilbao vs Alaves - 1 @1.62 (85% sure)

COMBINED @2.18 = 1M => 2,180,000 (1.18M profit)

Single safest: Newcastle 1 @1.35 - 500k => 675k
"""

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
data = {"chat_id": CHAT_ID, "text": msg}

try:
    r = requests.post(url, data=data, timeout=15)
    print(f"Status: {r.status_code}")
    print(r.text)
    if r.status_code == 200:
        print("Sent final banker @2.18 - SUCCESS")
    else:
        print(f"Telegram error: {r.text}")
except Exception as e:
    print(f"Request failed: {e}")
