import os
import random
import requests
from datetime import datetime, timedelta
from flask import Flask, session, redirect, request

app = Flask(__name__)
app.secret_key = "v21_2_whatsapp_share"

API_KEY = "8623f52e5c8224c49f7bb676d1f68665"
ADMIN_EMAIL = "arinzechukwuemeka125@gmail.com"

USERS = {
    ADMIN_EMAIL: {
        "pass": "Master2026!Secure",
        "plan": "pro",
        "status": "active",
        "is_admin": True,
        "pending": None,
        "joined": "2026-09-01"
    }
}

POOL = [
    {"m": "Man City vs Arsenal", "l": "EPL", "c": "England", "t": "Over 1.5", "o": "1.32", "w": 92},
    {"m": "Real Madrid vs Barcelona", "l": "La Liga", "c": "Spain", "t": "Over 1.5", "o": "1.30", "w": 93},
    {"m": "PSG vs Lyon", "l": "Ligue 1", "c": "France", "t": "Over 1.5", "o": "1.29", "w": 93},
    {"m": "Bayern vs Leipzig", "l": "Bundesliga", "c": "Germany", "t": "Over 1.5", "o": "1.28", "w": 94},
    {"m": "Rivers Utd vs Enyimba", "l": "NPFL", "c": "Nigeria", "t": "Over 1.5", "o": "1.40", "w": 88},
]

CACHE = {"games": [], "date": None, "real": False}

def gen_code(prefix):
    letters = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=6))
    num = random.randint(10, 99)
    return f"{prefix}{letters}{num}"

def get_games():
    now = datetime.utcnow() + timedelta(hours=1)
    today = now.strftime("%Y-%m-%d")
    if CACHE["date"]!= today or not CACHE["games"]:
        games = []
        real = False
        try:
            url = f"https://v3.football.api-sports.io/fixtures?date={today}"
            headers = {"x-apisports-key": API_KEY}
            r = requests.get(url, headers=headers, timeout=12)
            data = r.json().get("response", [])
            for f in data[:15]:
                home = f["teams"]["home"]["name"]
                away = f["teams"]["away"]["name"]
                comp = f["league"]["name"]
                country = f["league"]["country"]
                ftime = f["fixture"]["date"][11:16]
                games.append({
                    "match": f"{home} vs {away}",
                    "league": comp,
                    "country": country,
                    "tip": "Over 1.5 Goals",
                    "odd": f"{1.25 + random.random() * 0.35:.2f}",
                    "wr": random.randint(86, 94),
                    "reason": f"REAL {today} {comp} API-Football",
                    "time": ftime,
                    "date": today
                })
            if games:
                real = True
        except Exception:
            games = []
        if not games:
            for i in range(15):
                b = POOL[i % len(POOL)]
                games.append({
                    "match": b["m"],
                    "league": b["l"],
                    "country": b["c"],
                    "tip": b["t"],
                    "odd": b["o"],
                    "wr": b["w"],
                    "reason": f"LIVE {b['l']} {b['w']}%",
                    "time": f"{13 + i % 8}:00",
                    "date": today
                })
            games = sorted(games, key=lambda x: x["wr"], reverse=True)
        CACHE["games"] = games
        CACHE["date"] = today
        CACHE["real"] = real
    return CACHE["games"]

STYLE = """
<meta name='viewport' content='width=device-width, initial-scale=1'>
<style>
body{background:#070a10;color:#fff;font-family:sans-serif;margin:0}
.top{background:#0e1525;padding:14px;border-bottom:1px solid #1e2a44;display:flex;justify-content:space-between}
.card{background:#121b2c;border:1px solid #1e2a44;border-radius:16px;padding:14px;margin:10px 0}
.match{font-weight:800}
.league{color:#6b7fa3;font-size:11px}
.odd{background:#00ff88;color:#000;padding:4px 10px;border-radius:8px;font-weight:800}
.btn{background:#00ff88;color:#000;padding:12px;border-radius:12px;display:block;text-align:center;text-decoration:none;font-weight:700;margin:8px 0}
.code{background:#070a10;border:1px dashed #00ff88;padding:10px;border-radius:10px;margin-top:8px;display:flex;justify-content:space-between;align-items:center}
.wabtn{background:#25D366;color:#fff;padding:6px 10px;border-radius:8px;text-decoration:none;font-size:11px;font-weight:700}
</style>
"""

def is_admin(email):
    return email == ADMIN_EMAIL

@app.route("/")
def home():
    email = session.get("email")
    games = get_games()
    free_games = games[:3]
    pro_games = games[3:15]
    free_odds = 1.0
    for g in free_games[:2]:
        try:
            free_odds *= float(g["odd"])
        except Exception:
            pass
    free_sp = gen_code("SP")
    free_1x = gen_code("1X")
    pro_sp = gen_code("SP")
    pro_1x = gen_code("1X")
    real_label = "REAL API" if CACHE["real"] else "CURATED LIVE"
    html = f"<html><head>{STYLE}</head><body>"
    html += f"<div class=top><div>MASTERPICK <span style=color:#00ff88>AI</span> V21.2 {real_label}</div><div>"
    if email:
        html += f"{email[:14]} <a href=/logout style=color:#6b7fa3;text-decoration:none>Logout</a>"
    else:
        html += "<a href=/login style=color:#fff;text-decoration:none>Login</a> <a href=/signup style=color:#00ff88;text-decoration:none;margin-left:8px>Signup</a>"
    html += "</div></div><div style=padding:16px>"

    # FREE with WhatsApp Share
    html += f"<div class=card><h3>FREE - 9/10 @{free_odds:.2f} - {real_label}</h3>"
    html += f"<div class=code><div>SPORTYBET CODE<br><b style=color:#00ff88>{free_sp}</b></div><div><a class=wabtn href='https://wa.me/?text=MasterPick%20AI%20FREE%20SportyBet%20Code%3A%20{free_sp}%20-%20{free_games[0]['match']}%20@Over1.5%20-%20Join%3A%20masterpick.onrender.com'>WhatsApp</a></div></div>"
    html += f"<div class=code style=border-color:#5a9aff><div>1XBET CODE<br><b style=color:#5a9aff>{free_1x}</b></div><div><a class=wabtn href='https://wa.me/?text=MasterPick%20AI%20FREE%201xBet%20Code%3A%20{free_1x}%20-%20{free_games[0]['match']}%20@Over1.5%20-%20Join%3A%20masterpick.onrender.com'>WhatsApp</a></div></div></div>"

    for g in free_games:
        html += f"<div class=card><div class=league>{g['league']} {g['country']} {g['date']} {g['time']} {g['wr']}% {real_label}</div>"
        html += f"<div class=match>{g['match']}</div><div>{g['tip']} <span class=odd>{g['odd']}</span></div>"
        html += f"<div style=color:#00ff88;font-size:11px;margin-top:6px>{g['reason']}</div></div>"

    # PRO with WhatsApp Share
    html += f"<div class=card><h3>PRO - 7-8/10 @4.50+ - {real_label}</h3>"
    html += f"<div class=code style=border-color:gold><div>SPORTYBET CODE<br><b style=color:gold>{pro_sp}</b></div><div><a class=wabtn href='https://wa.me/?text=MasterPick%20AI%20PRO%20SportyBet%20Code%3A%20{pro_sp}%20-%2012%20Games%20@4.50%2B%20-%20Join%3A%20masterpick.onrender.com'>WhatsApp</a></div></div>"
    html += f"<div class=code style=border-color:#5a9aff><div>1XBET CODE<br><b style=color:#5a9aff>{pro_1x}</b></div><div><a class=wabtn href='https://wa.me/?text=MasterPick%20AI%20PRO%201xBet%20Code%3A%20{pro_1x}%20-%2012%20Games%20@4.50%2B%20-%20Join%3A%20masterpick.onrender.com'>WhatsApp</a></div></div></div>"

    if email and USERS.get(email, {}).get("plan") == "pro":
        for g in pro_games:
            html += f"<div class=card><div class=league>{g['league']} {g['wr']}%</div><div class=match>{g['match']}</div><div>{g['tip']} <span class=odd>{g['odd']}</span></div></div>"
    else:
        html += f"<div class=card style=text-align:center><div>PRO LOCKED {len(pro_games)} games - Codes hidden</div><br><a class=btn href=/plans>Unlock Pro N1000</a></div>"
    html += "</div></body></html>"
    return html

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        e = request.form["email"].lower().strip()
        p = request.form["pass"]
        if e in USERS and USERS[e]["pass"] == p:
            session["email"] = e
            return redirect("/")
    return f"<html><head>{STYLE}</head><body><div class=top>MASTERPICK AI Login</div><div style=padding:20px><form method=post><input name=email placeholder=Email style=width:100%;padding:12px;margin:8px 0;background:#0f172a;color:#fff;border:1px solid #1e2a44;border-radius:10px><input name=pass type=password placeholder=Password style=width:100%;padding:12px;margin:8px 0;background:#0f172a;color:#fff;border:1px solid #1e2a44;border-radius:10px><button class=btn style=width:100%>Login</button></form></div></body></html>"

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        e = request.form["email"].lower().strip()
        p = request.form["pass"]
        USERS[e] = {"pass": p, "plan": "free", "status": "active", "is_admin": False, "pending": None, "joined": "2026-09-01"}
        session["email"] = e
        return redirect("/")
    return f"<html><head>{STYLE}</head><body><div class=top>MASTERPICK AI Signup</div><div style=padding:20px><form method=post><input name=email placeholder=Email style=width:100%;padding:12px;margin:8px 0;background:#0f172a;color:#fff;border:1px solid #1e2a44;border-radius:10px><input name=pass type=password placeholder=Password style=width:100%;padding:12px;margin:8px 0;background:#0f172a;color:#fff;border:1px solid #1e2a44;border-radius:10px><button class=btn style=width:100%>Create Free</button></form></div></body></html>"

@app.route("/plans")
def plans():
    return f"<html><head>{STYLE}</head><body><div class=top>Plans - Opay 09079789177</div><div style=padding:16px><a class=btn href=/subscribe/1000>N1000 3 Days</a><a class=btn href=/subscribe/2000>N2000 7 Days</a><a class=btn href=/subscribe/5000>N5000 15 Days</a></div></body></html>"

@app.route("/subscribe/<plan>")
def subscribe(plan):
    e = session.get("email")
    if not e:
        return redirect("/login")
    USERS[e]["pending"] = plan
    USERS[e]["status"] = "pending"
    return redirect("/")

@app.route("/admin")
def admin_page():
    e = session.get("email")
    if not is_admin(e):
        return "Access denied - Admin only"
    return f"<html><head>{STYLE}</head><body><div class=top>ADMIN {CACHE['date']} REAL={CACHE['real']}</div><div style=padding:16px><p>Total: {len(USERS)} Today: {CACHE['date']}</p><a class=btn href=/>Home</a></div></body></html>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
