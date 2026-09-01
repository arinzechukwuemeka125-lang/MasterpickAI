import os, requests
from datetime import datetime, timedelta
from flask import Flask, request, redirect, session, render_template_string

app = Flask(__name__)
app.secret_key = "masterpick_v10_2_secure_final_2026_ph"

# YOUR REAL API-FOOTBALL KEY
API_KEY = os.environ.get("API_SPORTS_KEY", "8623f52e5c8224c49f7bb676d1f68665")

USERS = {
    "arinzechukwuemeka125@gmail.com": {
        "pass": "admin123",
        "plan": "pro",
        "status": "active",
        "expiry": datetime.now() + timedelta(days=365),
        "is_admin": True,
        "pending_plan": None
    }
}

def get_real_fixtures():
    if not API_KEY or API_KEY == "YOUR_KEY_HERE":
        return []
    try:
        headers = {"x-apisports-key": API_KEY}
        today = datetime.now().strftime("%Y-%m-%d")
        r = requests.get(f"https://v3.football.api-sports.io/fixtures?date={today}", headers=headers, timeout=15).json()
        fixtures = []
        for f in r.get("response", [])[:6]:
            fixtures.append({
                "match": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}",
                "league": f"{f['league']['name']} - {f['league']['country']}",
                "time": f['fixture']['date'][11:16],
                "tip": "Over 0.5 Goals @ 1.25 - SUREST 9/10",
                "odd": 1.25
            })
        return fixtures
    except Exception as e:
        print("API Error:", e)
        return []

BASE_HTML = """
<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'>
<style>
body{background:#0a0e13;color:#fff;font-family:Arial;padding:15px;margin:0}
.card{background:#1a242f;padding:14px;margin:12px 0;border-radius:12px;border-left:4px solid #00ff88}
.pending{border-left-color:orange;background:#2a2210}
.locked{background:#222;opacity:0.6}
.btn{background:#00ff88;color:#000;padding:14px;border:none;border-radius:10px;font-weight:bold;width:100%;margin:6px 0;font-size:16px}
.btn2{background:#1e3a5f;color:#fff}
.header{background:#0f172a;padding:12px;border-radius:10px;margin-bottom:10px}
small{color:#8aa}
</style></head><body>
<div class='header'><h2 style='margin:0'>⚽ MasterpickAI V10.2 - 100% REAL</h2><small>Secure • No Fake • Admin Approve</small></div>
"""

FOOTER = "</body></html>"

@app.route("/")
def home():
    fixtures = get_real_fixtures()
    email = session.get("email")
    user = USERS.get(email) if email else None
    
    html = BASE_HTML
    if not email:
        html += "<div class='card'><h3>Welcome to MasterpickAI</h3><p>100% Real fixtures from API-Football. No fake games.</p><a href='/login'><button class='btn'>Login</button></a><a href='/signup'><button class='btn btn2'>Signup Free</button></a></div>"
    else:
        status = user.get("status","free")
        html += f"<div class='card'><b>{email}</b><br>Plan: {user.get('plan')} | Status: {status}<br>Expiry: {user.get('expiry').strftime('%Y-%m-%d %H:%M') if user.get('expiry') else 'N/A'}<br><a href='/logout'>Logout</a> | <a href='/admin'>Admin</a> | <a href='/plans'>Plans</a></div>"
        
        if status == "pending":
            html += f"<div class='card pending'><h3>⏳ PENDING APPROVAL</h3><p>You selected ₦{user.get('pending_plan')}. Send to <b>Opay 09079789177 - Arinze Chukwuemeka Peter</b>.<br>Admin will check Opay and approve within 5 mins. Refresh this page.</p></div>"
        
        # FREE
        html += "<h3>🆓 FREE (2) @
