import requests, os
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

msg = """🛡️ V24 MOST SURE BANKER - 19th Sept - @2.18

MOST SURE - NO LOSE GUILD:

1. Newcastle vs Hull - 1 @1.35 (99% sure)
2. Athletic Bilbao vs Alaves - 1 @1.62 (85% sure)

COMBINED @2.18 = 1M => 2,180,000 (1.18M profit)

Single safest: Newcastle 1 @1.35 - 500k => 675k

This na sure pass from all leagues tomorrow.
"""

requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
print("Sent final banker @2.18")
