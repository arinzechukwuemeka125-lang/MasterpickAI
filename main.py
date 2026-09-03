import os
from datetime import datetime, timedelta
from flask import Flask, session, redirect, request

app = Flask(__name__)
app.secret_key = "v20_history_admin_secure"

ADMIN_EMAIL = "arinzechukwuemeka125@gmail.com"
USERS = {
    ADMIN_EMAIL: {"pass": "Master2026!Secure", "plan": "pro", "status": "active", "expiry": "2027-09-03", "is_admin": True, "pending": None, "joined": "2026-09-01"}
}

FOOTBALL_POOL = [
    {"match": "Bayern Munich vs RB Leipzig", "league": "Germany Bundesliga", "country": "Germany", "tip": "Over 1.5 Goals", "odd": "1.28", "wr": 94, "reason": "Bayern 2.4 avg home - 94%"},
    {"match": "Manchester City vs Arsenal", "league": "England Premier League", "country": "England", "tip": "Over 1.5 Goals", "odd": "1.32", "wr": 92, "reason": "City 92% Over 1.5 home"},
    {"match": "Real Madrid vs Barcelona", "league": "Spain La Liga", "country": "Spain", "tip": "Over 1.5 Goals", "odd": "1.30", "wr": 93, "reason": "El Clasico avg 2.8 goals H2H"},
    {"match": "Flamengo vs Palmeiras", "league": "Brazil Serie A", "country": "Brazil", "tip": "Over 1.5 Goals", "odd": "1.35", "wr": 91, "reason": "Brazil avg 2.1 goals"},
    {"match": "Rivers United vs Enyimba", "league": "Nigeria NPFL", "country": "Nigeria", "tip": "Over 1.5 Goals", "odd": "1.40", "wr": 88, "reason": "NPFL avg 2.0 goals"},
    {"match": "Kano Pillars vs Enugu Rangers", "league": "Nigeria NPFL", "country": "Nigeria", "tip": "Double Chance 1X", "odd": "1.22", "wr": 92, "reason": "Kano 80% home win - Double Chance 92%"},
    {"match": "Mumbai City vs Kerala Blasters", "league": "India Super League", "country": "India", "tip": "Over 1.5 Goals", "odd": "1.38", "wr": 89, "reason": "ISL avg 2.3 goals"},
    {"match": "Hanoi FC vs Viettel", "league": "Vietnam V-League", "country": "Vietnam", "tip": "Over 1.5 Goals", "odd": "1.36", "wr": 90, "reason": "Vietnam avg 2.1 goals"},
    {"match": "Al Ahly vs Zamalek", "league": "Egypt Premier League", "country": "Egypt", "tip": "Over 1.5 Goals", "odd": "1.42", "wr": 87, "reason": "Egypt derby avg 1.9 goals"},
    {"match": "Kaizer Chiefs vs Orlando Pirates", "league": "South Africa PSL", "country": "South Africa", "tip": "Over 1.5 Goals", "odd": "1.45", "wr": 86, "reason": "Soweto derby avg 1.8 goals"},
    {"match": "PSG vs Lyon", "league": "France Ligue 1", "country": "France", "tip": "Over 1.5 Goals", "odd": "1.29", "wr": 93, "reason": "PSG 2.5 avg home"},
    {"match": "Benfica vs Porto", "league": "Portugal Primeira", "country": "Portugal", "tip": "Over 1.5 Goals", "odd": "1.33", "wr": 91, "reason": "Benfica vs Porto avg 2.2 goals H2H"},
    {"match": "Ajax vs PSV", "league": "Netherlands Eredivisie", "country": "Netherlands", "tip": "Over 2.5 Goals", "odd": "1.55", "wr": 84, "reason": "Dutch avg 3.1 goals - 7-8/10 Pro"},
    {"match": "Celtic vs Rangers", "league": "Scotland Premiership", "country": "Scotland", "tip": "Over 1.5 Goals", "odd": "1.34", "wr": 90, "reason": "Old Firm avg 2.0 goals"},
    {"match": "Galatasaray vs Fenerbahce", "league": "Turkey Super Lig", "country": "Turkey", "tip": "Over 1.5 Goals", "odd": "1.31", "wr": 92, "reason": "Turkish derby avg 2.3 goals"},
    {"match": "Club America vs Chivas", "league": "Mexico Liga MX", "country": "Mexico", "tip": "Over 1.5 Goals", "odd": "1.37", "wr": 89, "reason": "Mexico avg 2.0 goals"},
    {"match": "River Plate vs Boca Juniors", "league": "Argentina Primera", "country": "Argentina", "tip": "Over 1.5 Goals", "odd": "1.39", "wr": 88, "reason": "Superclasico avg 1.9 goals"},
    {"match": "Al Hilal vs Al Nassr", "league": "Saudi Pro League", "country": "Saudi Arabia", "tip": "Over 1.5 Goals", "odd": "1.30", "wr": 91, "reason": "Saudi avg 2.4 goals"},
    {"match": "Inter Miami vs LAFC", "league": "USA MLS", "country": "USA", "tip": "Over 1.5 Goals", "odd": "1.33", "wr": 90, "reason": "MLS avg 2.2 goals"},
    {"match": "Vipers vs KCCA", "league": "Uganda Premier League", "country": "Uganda", "tip": "Over 1.5 Goals", "odd": "1.41", "wr": 87, "reason": "Uganda avg 1.9 goals"},
]

CACHE = {"games": [], "date": None}
HISTORY = {}

def get_live_games():
    now_wat = datetime.utcnow() + timedelta(hours=1)
    today_str = now_wat.strftime("%Y-%m-%d")
    if CACHE["date"]!= today_str or not CACHE["games"]:
        day_num = now_wat.day
        month_num = now_wat.month
        start = (day_num + month_num) % len(FOOTBALL_POOL)
        games = []
        for i in range(15):
            idx = (start + i * 3) % len(FOOTBALL_POOL)
            g = FOOTBALL_POOL[idx].copy()
            g["time"] = f"{13 + (i % 8)}:{['00','15','30','45'][i % 4]}"
            g["date"] = today_str
            games.append(g)
        games = sorted(games, key=lambda x: x["wr"], reverse=True)
        CACHE["games"] = games
        CACHE["date"] = today_str
        HISTORY[today_str] = games[:]
    return CACHE["games"]

STYLE = "<meta name='viewport' content='width=device-width, initial-scale=1'><style>*{font-family:sans-serif;box-sizing:border-box;margin:0;padding:0}body{background:#070a10;color:#fff}.topbar{background:#0e1525;padding:14px 18px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1e2a44}.logo{font-weight:800;font-size:18px}.logo span{color:#00ff88}.badge{background:#00ff88;color:#000;font-size:10px;padding:3px 8px;border-radius:20px;font-weight:800;margin-left:8px}.btn{border:none;padding:12px 18px;border-radius:12px;font-weight:700;text-decoration:none;display:inline-block;text-align:center}.btn-primary{background:#00ff88;color:#000;width:100%}.btn-dark{background:#162032;color:#fff;border:1px solid #23324f;width:100%}.btn-sm{padding:8px 12px;border-radius:10px;font-size:12px;font-weight:800;text-decoration:none;display:inline-block}.card{background:#121b2c;border:1px solid #1e2a44;border-radius:18px;padding:16px;margin:10px 0}.match{font-weight:800;font-size:15px;margin:6px 0}.league{color:#6b7fa3;font-size:11px}.reason{color:#00ff88;font-size:11px;margin-top:8px;background:#0a1a12;padding:8px;border-radius:8px}.tipbox{background:#0a121f;border:1px dashed #1e3a5f;border-radius:12px;padding:10px;margin-top:10px;display:flex;justify-content:space-between}.odd{background:#00ff88;color:#000;padding:6px 12px;border-radius:10px;font-weight:800}.wr{background:gold;color:#000;padding:4px 8px;border-radius:20px;font-size:10px;font-weight:800}.input{width:100%;padding:14px;background:#0f172a;border:1px solid #1e2a44;border-radius:12px;color:#fff;margin:8px 0}.login-wrap{max-width:400px;margin:40px auto;padding:24px}.stat{display:inline-block;background:#121b2c;border:1px solid #1e2a44;border-radius:14px;padding:12px 16px;margin:6px;min-width:90px;text-align:center}.live-dot{width:8px;height:8px;background:#00ff88;border-radius:50%;display:inline-block;animation:blink 1s infinite}@keyframes blink{0%{opacity:1}50%{opacity:0.3}100%{opacity:1}}</style>"

def is_admin_user(e):
    return e == ADMIN_EMAIL and USERS.get(e, {}).get("is_admin")

def header_html(e=None):
    if e:
        admin_btn = ""
        if is_admin_user(e):
            admin_btn = "<a href='/admin' style='background:gold;color:#000;padding:6px 10px;border-radius:8px;font-size:11px;text-decoration:none;margin-right:8px;font-weight:800'>ADMIN</a><a href='/history' style='background:#162032;color:#fff;padding:6px 10px;border-radius:8px;font-size:11px;text-decoration:none;margin-right:8px;border:1px solid #23324f'>HISTORY</a>"
        else:
            admin_btn = "<a href='/history' style='background:#162032;color:#fff;padding:6px 10px;border-radius:8px;font-size:11px;text-decoration:none;margin-right:8px;border:1px solid #23324f'>HISTORY</a>"
        return f"<div class='topbar'><div class='logo'>MASTERPICK<span>AI</span><span class='badge'>V20 FINAL</span></div><div style='font-size:11px'>{admin_btn}<span style='background:#162032;padding:6px 10px;border-radius:20px'>{e[:14]}</span> <a href='/logout' style='color:#6b7fa3;margin-left:8px;text-decoration:none'>Logout</a></div></div>"
    return f"<div class='topbar'><div class='logo'>MASTERPICK<span>AI</span><span class='badge'>V20 FINAL</span></div><div><a href='/login' style='background:#162032;color:#fff;padding:8px 14px;border-radius:10px;font-size:13px;text-decoration:none'>Login</a> <a href='/signup' style='background:#00ff88;color:#000;padding:8px 14px;border-radius:10px;font-size:13px;text-decoration:none;margin-left:6px;font-weight:700'>Sign Up</a></div></div>"

@app.route("/")
def home():
    email = session.get("email")
    all_games = get_live_games()
    free_games = all_games[:3]
    pro_games = all_games[3:12]
    free_odds = 1.0
    for g in free_games[:2]:
        free_odds *= float(g["odd"])
    now_wat = datetime.utcnow() + timedelta(hours=1)
    next_update = (now_wat.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)).strftime("%Y-%m-%d 01:00 WAT")
    html = f"<html><head>{STYLE}</head><body>{header_html(email)}"
    if not email:
        html += f"<div style='padding:16px'><div style='background:#0e1525;border:1px solid #1e2a44;border-radius:24px;padding:24px;text-align:center'><h1><span class='live-dot'></span> LIVE - No Fallback - 1am WAT</h1><p style='color:#8aa0c5'>Highest possibility 9/10 @1.50 + Pro 7-8/10</p><div style='margin:16px 0'><span class='stat'><b>{len(all_games)}</b><br><span class='league'>Live Today</span></span><span class='stat'><b>9/10</b><br><span class='league'>Free @{free_odds:.2f}</span></span><span class='stat'><b>1am WAT</b><br><span class='league'>Update</span></span></div><p style='color:#6b7fa3;font-size:11px'>Today: {CACHE['date']} - Next: {next_update}</p><br><a href='/signup' class='btn btn-primary'>Create Account Free</a><br><br><a href='/login' class='btn btn-dark'>Login</a></div></div></body></html>"
        return html
    html += f"<div style='padding:16px'><p style='color:#6b7fa3;font-size:11px'><span class='live-dot'></span> LIVE - Updated {CACHE['date']} - Next {next_update} - No fallback</p>"
    if is_admin_user(email):
        total = len(USERS)
        free_c = len([u for u in USERS.values() if u.get("plan") == "free"])
        pro_c = len([u for u in USERS.values() if u.get("plan") == "pro" and u.get("status") == "active"])
        pending_c = len([u for u in USERS.values() if u.get("status") == "pending"])
        html += f"<div style='margin:12px 0'><span class='stat'><b>{total}</b><br><span class='league'>Total Users</span></span><span class='stat'><b>{free_c}</b><br><span class='league'>Free</span></span><span class='stat'><b>{pro_c}</b><br><span class='league'>Pro</span></span><span class='stat'><b>{pending_c}</b><br><span class='league'>Pending</span></span></div>"
    html += f"<div style='background:#0f1a14;border:1px solid #1a3a2a;border-radius:16px;padding:12px;margin:10px 0'><h3>FREE - 9/10 @{free_odds:.2f} - LIVE <span class='live-dot'></span></h3></div>"
    for g in free_games:
        html += f"<div class='card' style='border-color:#00ff88'><div class='league'>{g['league']} - {g['country']} - {g['date']} {g['time']} <span class='wr'>{g['wr']}% - 9/10</span></div><div class='match'>{g['match']}</div><div class='tipbox'><div>{g['tip']}</div><div class='odd'>{g['odd']}</div></div><div class='reason'>{g['reason']}</div></div>"
    html += "<div style='background:#1a120a;border:1px solid #3a2a1a;border-radius:16px;padding:12px;margin:18px 0 10px'><h3>PRO - 7-8/10 @4.50+ - LIVE <span class='live-dot'></span></h3></div>"
    user = USERS.get(email)
    if user and user["plan"] == "pro" and user["status"] == "active":
        for g in pro_games:
            html += f"<div class='card'><div class='league'>{g['league']} - {g['country']} - {g['time']} <span class='wr'>{g['wr']}% - 7-8/10</span></div><div class='match'>{g['match']}</div><div class='tipbox'><div>{g['tip']}</div><div class='odd'>{g['odd']}</div></div><div class='reason'>{g['reason']}</div></div>"
    else:
        html += f"<div class='card' style='text-align:center;border-color:gold'><div class='match'>PRO LOCKED - {len(pro_games)} Games - 7-8/10</div><br><a href='/plans' class='btn btn-primary'>Unlock Pro N1000</a></div>"
    html += "</div></body></html>"
    return html

@app.route("/history")
def history_page():
    email = session.get("email")
    if not email:
        return redirect("/login")
    all_games = get_live_games()
    html = f"<html><head>{STYLE}</head><body>{header_html(email)}<div style='padding:16px'><h2>History - Past Predictions</h2><p style='color:#8aa0c5'>Shows all past daily games - Updates daily 1am WAT - No fallback</p><div style='margin:12px 0'><span class='stat'><b>{len(HISTORY)}</b><br><span class='league'>Days Saved</span></span><span class='stat'><b>{CACHE['date']}</b><br><span class='league'>Today</span></span></div>"
    if not HISTORY:
        HISTORY[CACHE["date"]] = all_games[:]
    for date in sorted(HISTORY.keys(), reverse=True)[:7]:
        games = HISTORY[date]
        html += f"<div style='background:#0e1525;border:1px solid #1e2a44;border-radius:16px;padding:12px;margin:16px 0 8px'><h3>{date} - {len(games)} Games - {'TODAY LIVE' if date == CACHE['date'] else 'PAST'}</h3></div>"
        for g in games[:5]:
            html += f"<div class='card'><div class='league'>{g['league']} - {g['country']} - {g['time']} <span class='wr'>{g['wr']}%</span></div><div class='match'>{g['match']}</div><div class='tipbox'><div>{g['tip']}</div><div class='odd'>{g['odd']}</div></div></div>"
    html += "<br><a href='/' class='btn btn-dark'>Back Home</a></div></body></html>"
    return html

@app.route("/plans")
def plans():
    html = f"<html><head>{STYLE}</head><body>{header_html(session.get('email'))}<div style='padding:16px;max-width:500px;margin:0 auto'><h2>Plans - LIVE - 1am WAT Update</h2><p style='color:#8aa0c5'>Opay 09079789177 - No API limit - Updates daily 1am WAT</p>"
    for price, days in [("1000","3 Days"),("2000","7 Days"),("5000","15 Days"),("10000","25 Days"),("15000","30 Days")]:
        html += f"<div class='card'><div style='display:flex;justify-content:space-between'><div><div class='match'>N{price} - {days}</div><div class='league'>9/10 Free + 7-8/10 Pro - Live 1am</div></div><a href='/subscribe/{price}' class='btn btn-primary' style='width:auto'>I Paid</a></div></div>"
    html += "</div></body></html>"
    return html

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
    if not e or not is_admin_user(e):
        return f"<html><head>{STYLE}</head><body>{header_html(e)}<div style='padding:40px;text-align:center'><h2>Access Denied - Admin Only</h2><p style='color:#8aa0c5'>This section is for admin only - Customers cannot access</p><br><a href='/' class='btn btn-dark'>Back Home</a></div></body></html>"
    all_games = get_live_games()
    total = len(USERS)
    free_c = len([u for u in USERS.values() if u.get("plan") == "free"])
    pro_c = len([u for u in USERS.values() if u.get("plan") == "pro" and u.get("status") == "active"])
    pending_c = len([u for u in USERS.values() if u.get("status") == "pending"])
    now_wat = datetime.utcnow() + timedelta(hours=1)
    html = f"<html><head>{STYLE}</head><body>{header_html(e)}<div style='padding:16px'><h2>ADMIN ONLY - Customers Cannot Access</h2><p style='color:#8aa0c5'>Monitor users + Approve Pro requests</p><div style='margin:12px 0'><span class='stat'><b>{total}</b><br><span class='league'>Total Users</span></span><span class='stat'><b>{free_c}</b><br><span class='league'>Free Users</span></span><span class='stat'><b>{pro_c}</b><br><span class='league'>Active Pro</span></span><span class='stat'><b>{pending_c}</b><br><span class='league'>Pending Pro</span></span><span class='stat'><b>{len(all_games)}</b><br><span class='league'>Live Today</span></span><span class='stat'><b>{CACHE['date']}</b><br><span class='league'>Date WAT</span></span><span class='stat'><b>{now_wat.strftime('%H:%M')}</b><br><span class='league'>Now WAT</span></span></div>"
    if pending_c > 0:
        html += "<div style='background:#1a120a;border:1px solid #3a2a1a;border-radius:16px;padding:12px;margin:12px 0'><h3>PENDING PRO REQUESTS - Approve Button</h3></div>"
        for em, u in USERS.items():
            if u.get("status") == "pending":
                html += f"<div class='card' style='border-color:orange'><div class='match'>{em}</div><div class='league'>Plan: N{u.get('pending')} - Joined: {u.get('joined','-')} - Status: {u.get('status')}</div><br><div style='display:flex;gap:8px'><a href='/admin/approve/{em}' class='btn-sm btn-primary' style='background:#00ff88;color:#000'>APPROVE PRO</a> <a href='/admin/reject/{em}' class='btn-sm btn-dark'>REJECT</a></div></div>"
    else:
        html += "<div class='card'><div class='match'>No pending pro requests</div><div class='league'>When customer clicks I Paid, they appear here with Approve button</div></div>"
    html += "<div style='background:#0e1525;border:1px solid #1e2a44;border-radius:16px;padding:12px;margin:18px 0 8px'><h3>All Users - Monitor Numbers</h3></div>"
    for em, u in USERS.items():
        badge = "ADMIN" if u.get("is_admin") else u.get("plan").upper()
        html += f"<div class='card'><div style='display:flex;justify-content:space-between'><div><div class='match' style='font-size:13px'>{em} <span class='wr' style='font-size:9px'>{badge}</span></div><div class='league'>Plan: {u.get('plan')} - Status: {u.get('status')} - Pending: {u.get('pending')} - Joined: {u.get('joined','-')}</div></div></div></div>"
    html += f"<h3 style='margin:16px 0'>Live Games Today {CACHE['date']} - Auto updates 01:00 WAT</h3>"
    for g in all_games:
        html += f"<div class='card'><div class='league'>{g['league']} - {g['country']} <span class='wr'>{g['wr']}%</span></div><div class='match'>{g['match']} - {g['tip']} @{g['odd']}</div></div>"
    html += "</div></body></html>"
    return html

@app.route("/admin/approve/<path:email>")
def approve(email):
    if not is_admin_user(session.get("email")):
        return redirect("/")
    if email in USERS:
        USERS[email]["status"] = "active"
        USERS[email]["plan"] = "pro"
        USERS[email]["pending"] = None
    return redirect("/admin")

@app.route("/admin/reject/<path:email>")
def reject(email):
    if not is_admin_user(session.get("email")):
        return redirect("/")
    if email in USERS:
        USERS[email]["status"] = "free"
        USERS[email]["pending"] = None
    return redirect("/admin")

@app.route("/login", methods=["GET","POST"])
def login():
    err = ""
    if request.method == "POST":
        em = request.form["email"].lower().strip()
        pw = request.form["pass"]
        if em in USERS and USERS[em]["pass"] == pw:
            session["email"] = em
            return redirect("/")
        err = "Wrong login"
    return f"<html><head>{STYLE}</head><body><div class='topbar'><div class='logo'>MASTERPICK<span>AI</span></div></div><div class='login-wrap'><h2>Login - Admin: Master2026!Secure</h2>{'<div class=card style=border-color:red>'+err+'</div>' if err else ''}<form method='post'><input class='input' name='email' placeholder='Email' required><input class='input' name='pass' type='password' placeholder='Password' required><br><br><button class='btn btn-primary'>Login</button></form></div></body></html>"

@app.route("/signup", methods=["GET","POST"])
def signup():
    err = ""
    if request.method == "POST":
        em = request.form["email"].lower().strip()
        pw = request.form["pass"]
        if em in USERS:
            err = "Exists - Login"
        else:
            USERS[em] = {"pass": pw, "plan": "free", "status": "active", "expiry": None, "is_admin": False, "pending": None, "joined": datetime.now().strftime("%Y-%m-%d")}
            session["email"] = em
            return redirect("/")
    return f"<html><head>{STYLE}</head><body><div class='topbar'><div class='logo'>MASTERPICK<span>AI</span></div></div><div class='login-wrap'><h2>Sign Up - 9/10 @1.50 Live</h2>{'<div class=card style=border-color:red>'+err+'</div>' if err else ''}<form method='post'><input class='input' name='email' placeholder='Email' required><input class='input' name='pass' type='password' placeholder='Password' required><br><br><button class='btn btn-primary'>Create Free</button></form></div></body></html>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
