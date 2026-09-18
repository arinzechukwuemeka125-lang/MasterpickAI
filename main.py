import requests, os
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
msg = """🛡️ V24 BANKER - 18th Sept

MAIN @1.78 (88% CONFIDENCE) - 800k
1. Brentford vs Chelsea - X2 @1.32
2. Monza vs Sassuolo - 1X @1.35
Return: 1M = 1.78M

SIDE @2.90 (65% CONF) - 200k
USA Davis Cup win @1.55
Real Madrid win @1.38
"""
requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
print("Sent @1.78")
