import os, requests, urllib.parse
from datetime import datetime, timedelta
from flask import Flask, request, redirect, session

app = Flask(__name__)
app.secret_key = "v10_6_sportybet_final"
API_KEY = "8623f52e5c8224c49f7bb676d1f68665"

USERS = {
    "arinzechukwuemeka125@gmail.com": {
        "pass": "admin123",
        "plan": "pro",
        "status": "active",
        "expiry": datetime.now() + timedelta(days=365),
        "is_admin": True,
        "pending": None
    }
}

# ONLY leagues SportyBet Nigeria actually lists + has Over 1.5 market
SPORTY_LEAGUES = [
    "Brasileiro", "Serie A Brazil", "Saudi", "Pro League",
    "Major League Soccer", "MLS",
    "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1",
    "Eredivisie", "Primeira Liga", "Super Lig",
    "Champions League", "Europa League", "Conference League",
    "World Cup", "Qualification", "Friendly"
]

def is_sporty(name):
    low = name.lower()
    for k in SPORTY_LEAGUES:
        if k.lower() in low:
            return True
    return False

def get_fixtures():
    try:
        headers = {"x-apisports-key": API_KEY}
        today = datetime.now().strftime("%Y-%m-%d")
        url = "https://v3.football.api-sports.io/fixtures?date=" + today
        r = requests.get(url, headers=headers, timeout=10).json()
        out = []
        for f in r.get("response", [])[:100]:
            league = f["league"]["name"]
            if is_sporty(league):
                home = f["teams"]["home"]["name"]
                away = f["teams"]["away"]["name"]
                time = f["fixture"]["date"][11:16]
                out.append({
                    "match": home + " vs " + away,
                    "league": league + " - " + f["league"]["country"],
                    "time": time,
                    "tip": "Over 1.5 Goals",
                    "odd": "1.40",
                    "conf": "8.5/10"
                })
        return out
    except:
        return []

def wa_link(text):
    return "https://wa.me/?text=" + urllib.parse.quote(text)

STYLE = "<meta name='viewport' content='width=device-width, initial-scale=1'><style>*{font-family:sans-serif;box-sizing:border-box;margin:0;padding:0}body{background:#070a10;color:#fff}.topbar{background:#0e1525;padding:14px 18px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1e2a44}.logo{font-weight:800;font-size:18px}.logo span{color:#00ff88}.badge{background:#00ff88;color:#000;font-size:10px;padding:3px 8px;border-radius:20px;font-weight:800;margin-left:8px}.btn{border:none;padding:12px 18px;border-radius:12px;font-weight:700;text-decoration:none;display:inline-block;text-align:center}.btn-primary{background:#00ff88;color:#000;width:100%}.btn-dark{background:#162032;color:#fff;border:1px solid #23324f;width:100%}.btn-wa{background:#25D366;color:#fff;padding:10px 12px;border-radius:10px;font-size:12px;font-weight:700;text-decoration:none;display:inline-block}.card{background:#121b2c;border:1px solid #1e2a44;border-radius:18px;padding:16px;margin:12px 0}.match{font-weight:800;font-size:15px;margin:6px 0}.league{color:#6b7fa3;font-size:11px}.tipbox{background:#0a121f;border:1px dashed #1e3a5f;border-radius:12px;padding:10px;margin-top:10px;display:flex;justify-content:space-between}.odd{background:#00ff88;color:#000;padding:6px 12px;border-radius:10px;font-weight:800}.input{width:100%;padding:14px;background:#0f172a;border:1px solid #1e2a44;border-radius:12px;color:#fff;margin:8px 0}.hero{background:#0e1525;border:1px solid #1e2a44;border-radius:24px;padding:24px;margin:16px;text-align:center}.login-wrap{max-width:400px;margin:40px auto;padding:24px}</style>"

def header_html(email=None):
    if email:
        u = USERS.get(email)
        plan = u["plan"].upper() if u else "FREE"
        nav = "<div style='font-size:11px'><span style='background:#162032;padding:6px 10px;border-radius:20px;border:1px solid #23324f'>" + email[:18] + " | " + plan + "</span> <a href='/logout' style='color:#6b7fa3;margin-left:8px;text-decoration:none'>Logout</a></div>"
    else:
        nav = "<a href='/login' class='btn' style='background:#162032;color:#fff;padding:8px 16px;border-radius:10px;font-size:13px'>Login</a>"
    return "<div class='topbar'><div class='logo'>MASTERPICK<span>AI</span><span class='badge'>V10.6 SPORTY</span></div>" + nav + "</div>"

@app.route("/")
def home():
    email = session.get("email")
    user = USERS.get(email) if email else None
    fixtures = get_fixtures()
    html = "<html><head>" + STYLE + "</head><body>" + header_html(email)
    if not email:
        html += "<div class='hero'><h1>Real Games Found On SportyBet</h1><p style='color:#8aa0c5;font-size:13px;margin-top:8px'>Only leagues SportyBet lists - Over 1.5 Goals available</p><br><a href='/signup' class='btn btn-primary'>Start Free</a><br><br><a href='/login' class='btn btn-dark'>Login</a></div></body></html>"
        return html
    html += "<div style='padding:16px'>"
    if user["status"] == "pending":
        html += "<div class='card'><div class='league' style='color:orange'>PENDING APPROVAL</div><div class='match'>Paid N" + str(user["pending"]) + " - Check Opay 09079789177</div></div>"
    if fixtures:
        all_text = "MASTERPICKAI TODAY - SportyBet Verified:\n\n"
        for f in fixtures[:4]:
            all_text += f["match"] + " - " + f["tip"] + " @" + f["odd"] + "\n"
        all_text += "\nFree @2.80 - Pro @7.50\nJoin: https://masterpickai.onrender.com"
        wa_all = wa_link(all_text)
        html += "<a href='" + wa_all + "' target='_blank' class='btn-wa' style='width:100%;text-align:center;padding:12px;margin-bottom:12px;display:block'>📲 SHARE ALL GAMES TO WHATSAPP</a>"
    html += "<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px'><div class='card' style='margin:0;text-align:center'><div style='font-size:18px;font-weight:800'>" + str(len(fixtures)) + "</div><div class='league'>Sporty Today</div></div><div class='card' style='margin:0;text-align:center'><div style='font-size:18px;font-weight:800;color:#00ff88'>2.80</div><div class='league'>Free Odd</div></div><div class='card' style='margin:0;text-align:center'><div style='font-size:18px;font-weight:800;color:gold'>7.50</div><div class='league'>Pro Odd</div></div></div>"
    if len(fixtures) == 0:
        html += "<div class='card'><div class='league' style='color:#ff6b6b'>NO SPORTYBET GAMES THIS HOUR</div><div style='font-size:13px;margin-top:6px;color:#8aa0c5'>International break - EPL paused. Come back 7PM when MLS/Brazil Serie A starts. We filter Kenya etc so you only see games you can find on SportyBet.</div></div>"
    else:
        html += "<h3 style='margin:14px 4px'>FREE 2 Games @2.80 - Over 1.5</h3>"
        for f in fixtures[:2]:
            share_txt =
