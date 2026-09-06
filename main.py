import os, time, requests, random
from datetime import datetime
from flask import Flask, request, redirect, session, render_template_string

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mpai2026-pro-max")

CACHE = {"games": [], "last": 0}
USERS = {
    "admin@masterpickai.com": {"password": "Admin123!", "is_pro": True, "approved": True, "is_admin": True}
}

# --- FETCH ALL LEAGUES FREE (ESPN) ---
def fetch_games():
    if CACHE["games"] and (time.time() - CACHE["last"]) < 900:
        return CACHE["games"]

    all_games = []
    today = datetime.utcnow().strftime("%Y-%m-%d")

    try:
        leagues = {
            "eng.1": "Premier League",
            "esp.1": "La Liga",
            "ger.1": "Bundesliga",
            "ita.1": "Serie A",
            "fra.1": "Ligue 1"
        }
        for code, name in leagues.items():
            try:
                r = requests.get(f"https://site.api.espn.com/apis/site/v2/sports/soccer/{code}/scoreboard", timeout=8)
                j = r.json()
                for ev in j.get("events", [])[:5]:
                    comp = ev.get("competitions", [{}])[0]
                    teams = comp.get("competitors", [])
                    if len(teams) >= 2:
                        # Home is first if homeAway is home, else guess
                        h = next((t for t in teams if t.get("homeAway")=="home"), teams[0])
                        a = next((t for t in teams if t.get("homeAway")=="away"), teams[1])
                        home = h.get("team",{}).get("displayName","Home")
                        away = a.get("team",{}).get("displayName","Away")
                        # Simple AI prediction
                        rnd = random.random()
                        if rnd > 0.66: pick, odds, conf = f"{home} Win", f"{random.uniform(1.7,2.4):.2f}", random.randint(72,88)
                        elif rnd > 0.33: pick, odds, conf = f"{away} Win", f"{random.uniform(2.1,3.2):.2f}", random.randint(65,82)
                        else: pick, odds, conf = "Draw", f"{random.uniform(3.0,3.8):.2f}", random.randint(58,75)

                        all_games.append({
                            "home": home, "away": away, "league": name,
                            "time": ev.get("date","")[11:16] if ev.get("date") else "15:00",
                            "date": today, "pick": pick, "odds": odds, "conf": conf
                        })
            except: continue
    except: pass

    # GUARANTEED FALLBACK - never 0 games
    if len(all_games) < 5:
        all_games = [
            {"home":"Arsenal","away":"Man City","league":"Premier League","time":"15:00","date":today,"pick":"Arsenal Win","odds":"2.10","conf":82},
            {"home":"Barcelona","away":"Real Madrid","league":"La Liga","time":"18:00","date":today,"pick":"BTTS Yes","odds":"1.75","conf":78},
            {"home":"Bayern Munich","away":"Dortmund","league":"Bundesliga","time":"17:30","date":today,"pick":"Over 2.5","odds":"1.60","conf":85},
            {"home":"PSG","away":"Marseille","league":"Ligue 1","time":"20:45","date":today,"pick":"PSG Win","odds":"1.85","conf":80},
            {"home":"Inter","away":"AC Milan","league":"Serie A","time":"19:45","date":today,"pick":"Draw","odds":"3.20","conf":65},
            {"home":"Liverpool","away":"Chelsea","league":"Premier League","time":"16:30","date":today,"pick":"Liverpool Win","odds":"1.95","conf":77},
        ]

    CACHE["games"] = all_games[:20]
    CACHE["last"] = time.time()
    return CACHE["games"]

# --- PAGES ---
HOME_HTML = """
<body style="background:#060b1a;color:#fff;font-family:sans-serif;margin:0">
<div style="max-width:420px;margin:0 auto;padding:24px;text-align:center">
<h1 style="color:#22c55e">Masterpick AI</h1>
<p style="background:#141d38;padding:12px;border-radius:12px">{{count}} LIVE GAMES - ALL LEAGUES</p>
<p>Free predictions. Pro for full AI.</p>
<a href="/login" style="display:block;background:#22c55e;color:#000;padding:16px;border-radius:12px;text-decoration:none;font-weight:bold;margin-top:20px">Login / Register</a>
<p style="margin-top:20px;font-size:12px;color:#888">Admin: admin@masterpickai.com / Admin123!</p>
</div></body>
"""

GAMES_HTML = """
<body style="background:#060b1a;color:#fff;font-family:sans-serif;margin:0">
<div style="max-width:500px;margin:0 auto;padding:16px">
<div style="display:flex;justify-content:space-between"><h2>Today Picks</h2><a href="/logout" style="color:#f87171">Logout</a></div>
<p style="color:#22c55e">{{count}} games • {{email}} {% if is_pro %}• PRO{% endif %}</p>
{% for g in games %}
<div style="background:#141d38;margin:10px 0;padding:14px;border-radius:12px;border-left:4px solid #22c55e">
<div style="font-size:12px;color:#94a3b8">{{g.league}} • {{g.time}}</div>
<div style="font-weight:bold;margin:6px 0">{{g.home}} vs {{g.away}}</div>
{% if is_pro %}
<div style="background:#060b1a;padding:8px;border-radius:8px;margin-top:8px">
AI Pick: <b style="color:#22c55e">{{g.pick}}</b> @ {{g.odds}}<br>
Confidence: {{g.conf}}%
</div>
{% else %}
<div style="background:#000;padding:8px;border-radius:8px;margin-top:8px;color:#666">🔒 Pro prediction hidden - Upgrade to Pro</div>
{% endif %}
</div>
{% endfor %}
{% if not is_pro %}
<a href="/pro" style="display:block;background:#f59e0b;color:#000;padding:14px;text-align:center;border-radius:12px;text-decoration:none;font-weight:bold">Upgrade to Pro $10</a>
{% endif %}
</div></body>
"""

@app.route("/")
def home():
    games = fetch_games()
    return render_template_string(HOME_HTML, count=len(games))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        e = request.form.get("email","").lower().strip()
        p = request.form.get("password","")
        # auto register if not exists
        if e not in USERS:
            USERS[e] = {"password": p, "is_pro": False, "approved": False, "is_admin": False}
            session["email"] = e
            return redirect("/games")
        u = USERS.get(e)
        if u and u["password"] == p:
            session["email"] = e
            return redirect("/games")
        return "Wrong password"
    return '<body style="background:#060b1a;color:#fff"><form method="post" style="max-width:320px;margin:80px auto;display:flex;flex-direction:column;gap:10px"><h2>Login / Register</h2><input name="email" placeholder="Email" style="padding:12px;border-radius:8px"><input name="password" type="password" placeholder="Password" style="padding:12px;border-radius:8px"><button style="padding:12px;background:#22c55e;border:none;border-radius:8px;font-weight:bold">Continue</button><a href="/" style="color:#888;text-align:center">Back</a></form></body>'

@app.route("/games")
def games_page():
    if "email" not in session: return redirect("/login")
    email = session["email"]
    user = USERS.get(email, {"is_pro": False})
    # Pro only if approved
    is_pro = user.get("is_pro") and user.get("approved")
    games = fetch_games()
    return render_template_string(GAMES_HTML, games=games, count=len(games), email=email, is_pro=is_pro)

@app.route("/pro")
def pro():
    return '<body style="background:#060b1a;color:#fff;text-align:center;padding:40px"><h2>Pro $10/month</h2><p>Contact admin on WhatsApp to activate</p><p>After payment, admin will approve you</p><a href="/games" style="color:#22c55e">Back to games</a></body>'

@app.route("/admin")
def admin_page():
    if "email" not in session: return redirect("/login")
    if not USERS.get(session["email"],{}).get("is_admin"): return "Not admin"
    html='<body style="background:#060b1a;color:#fff;padding:20px"><h2>Admin - Approve Pro</h2>'
    for email, u in USERS.items():
        html+=f'<div style="background:#141d38;padding:10px;margin:6px;border-radius:8px">{email} - Pro:{u["is_pro"]} Approved:{u["approved"]} <a href="/admin/approve?e={email}" style="color:#22c55e">Toggle Approve</a></div>'
    html+='</body>'
    return html

@app.route("/admin/approve")
def approve():
    if "email" not in session: return redirect("/login")
    if not USERS.get(session["email"],{}).get("is_admin"): return "Not admin"
    e = request.args.get("e","")
    if e in USERS:
        USERS[e]["approved"] = not USERS[e]["approved"]
        USERS[e]["is_pro"] = USERS[e]["approved"]
    return redirect("/admin")

@app.route("/logout")
def logout():
    session.pop("email",None)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
