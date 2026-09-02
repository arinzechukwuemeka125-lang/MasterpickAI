import os, requests, urllib.parse
from datetime import datetime, timedelta
from flask import Flask, request, redirect, session

app = Flask(__name__)
app.secret_key = "v11_secure_no_leak_999"
API_KEY = "8623f52e5c8224c49f7bb676d1f68665"

ADMIN_EMAIL = "arinzechukwuemeka125@gmail.com"

USERS = {
    ADMIN_EMAIL: {"pass": "admin123", "plan": "pro", "status": "active", "expiry": datetime.now() + timedelta(days=365), "is_admin": True, "pending": None, "joined": "2026-09-01"}
}

HISTORY = [
    {"date":"2026-09-01","free":"2/2 WIN @2.90","pro":"5/6 WIN @7.20","status":"WIN"},
    {"date":"2026-08-31","free":"1/2 LOST","pro":"4/6 WIN @5.40","status":"WIN"},
    {"date":"2026-08-30","free":"2/2 WIN @2.75","pro":"6/6 WIN @8.10","status":"WIN"},
    {"date":"2026-08-29","free":"2/2 WIN @2.80","pro":"5/6 WIN @6.90","status":"WIN"},
    {"date":"2026-08-28","free":"1/2 LOST","pro":"3/6 LOST","status":"LOST"},
]

ALLOW = ["brazil","saudi","mls","major league","premier league","la liga","serie a","bundesliga","ligue 1","eredivisie","primeira","super lig","champions","europa","conference","world cup","qualification","argentina","mexico"]

def is_allowed(name):
    low = name.lower()
    for k in ALLOW:
        if k in low:
            return True
    return False

def get_fixtures():
    fixtures = []
    try:
        headers = {"x-apisports-key": API_KEY}
        for day_offset in [0,1]:
            d = (datetime.now() + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            url = f"https://v3.football.api-sports.io/fixtures?date={d}"
            r = requests.get(url, headers=headers, timeout=12).json()
            for f in r.get("response", [])[:100]:
                league = f["league"]["name"]
                if is_allowed(league):
                    home = f["teams"]["home"]["name"]
                    away = f["teams"]["away"]["name"]
                    time = f["fixture"]["date"][11:16]
                    fixtures.append({"match": home + " vs " + away, "league": league, "time": time, "date": d, "tip": "Over 1.5 Goals", "odd": "1.40"})
        seen = set()
        uniq = []
        for x in fixtures:
            if x["match"] not in seen:
                uniq.append(x)
                seen.add(x["match"])
        return uniq[:20]
    except:
        return []

def wa_link(text):
    return "https://wa.me/?text=" + urllib.parse.quote(text)

STYLE = "<meta name='viewport' content='width=device-width, initial-scale=1'><style>*{font-family:sans-serif;box-sizing:border-box;margin:0;padding:0}body{background:#070a10;color:#fff}.topbar{background:#0e1525;padding:14px 18px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1e2a44}.logo{font-weight:800;font-size:18px}.logo span{color:#00ff88}.badge{background:#00ff88;color:#000;font-size:10px;padding:3px 8px;border-radius:20px;font-weight:800;margin-left:8px}.btn{border:none;padding:12px 18px;border-radius:12px;font-weight:700;text-decoration:none;display:inline-block;text-align:center}.btn-primary{background:#00ff88;color:#000;width:100%}.btn-dark{background:#162032;color:#fff;border:1px solid #23324f;width:100%}.btn-wa{background:#25D366;color:#fff;padding:8px 12px;border-radius:10px;font-size:12px;font-weight:700;text-decoration:none;display:inline-block}.card{background:#121b2c;border:1px solid #1e2a44;border-radius:18px;padding:16px;margin:10px 0}.match{font-weight:800;font-size:15px;margin:6px 0}.league{color:#6b7fa3;font-size:11px}.tipbox{background:#0a121f;border:1px dashed #1e3a5f;border-radius:12px;padding:10px;margin-top:10px;display:flex;justify-content:space-between}.odd{background:#00ff88;color:#000;padding:6px 12px;border-radius:10px;font-weight:800}.input{width:100%;padding:14px;background:#0f172a;border:1px solid #1e2a44;border-radius:12px;color:#fff;margin:8px 0}.hero{background:#0e1525;border:1px solid #1e2a44;border-radius:24px;padding:24px;margin:16px;text-align:center}.login-wrap{max-width:400px;margin:40px auto;padding:24px}.stat{display:inline-block;background:#121b2c;border:1px solid #1e2a44;border-radius:14px;padding:12px 16px;margin:6px;min-width:100px;text-align:center}</style>"

def is_admin_user(email):
    return email == ADMIN_EMAIL and USERS.get(email, {}).get("is_admin")

def header_html(email=None):
    if email:
        # Admin button ONLY for admin
        admin_btn = ""
        if is_admin_user(email):
            admin_btn = "<a href='/admin' style='background:gold;color:#000;padding:6px 10px;border-radius:8px;font-size:11px;text-decoration:none;margin-right:8px;font-weight:800'>ADMIN</a>"
        nav = f"<div style='font-size:11px'>{admin_btn}<span style='background:#162032;padding:6px 10px;border-radius:20px'>{email[:18]}</span> <a href='/logout' style='color:#6b7fa3;margin-left:8px;text-decoration:none'>Logout</a></div>"
    else:
        nav = "<a href='/login' style='background:#162032;color:#fff;padding:8px 14px;border-radius:10px;font-size:13px;text-decoration:none'>Login</a> <a href='/signup' style='background:#00ff88;color:#000;padding:8px 14px;border-radius:10px;font-size:13px;text-decoration:none;margin-left:6px;font-weight:700'>Sign Up</a>"
    return f"<div class='topbar'><div class='logo'>MASTERPICK<span>AI</span><span class='badge'>V11 SECURE</span></div>{nav}</div>"

@app.route("/")
def home():
    email = session.get("email")
    user = USERS.get(email) if email else None
    fixtures = get_fixtures()
    html = f"<html><head>{STYLE}</head><body>{header_html(email)}"
    if not email:
        html += "<div class='hero'><h1>Real Games On SportyBet</h1><p style='color:#8aa0c5;font-size:13px'>Over 1.5 @1.40 - Today + Tomorrow</p><br><a href='/signup' class='btn btn-primary'>Create Free Account</a><br><br><a href='/login' class='btn btn-dark'>Login</a><br><br><a href='/history' class='btn btn-dark'>View History</a></div></body></html>"
        return html
    html += "<div style='padding:16px'>"
    # Customer sees only History + Plans, NO admin button
    if is_admin_user(email):
        html += "<div style='display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px'><a href='/history' class='btn-wa' style='background:#162032;border:1px solid #23324f'>History</a><a href='/plans' class='btn-wa' style='background:#162032;border:1px solid #23324f'>Plans</a><a href='/admin' class='btn-wa' style='background:gold;color:#000'>Admin Panel</a></div>"
    else:
        html += "<div style='display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px'><a href='/history' class='btn-wa' style='background:#162032;border:1px solid #23324f'>History WIN/LOSS</a><a href='/plans' class='btn-wa' style='background:#162032;border:1px solid #23324f'>Upgrade Plans</a></div>"
    if user and user["status"] == "pending":
        html += f"<div class='card' style='border-color:orange'><div class='league' style='color:orange'>PENDING</div><div class='match'>Paid N{user['pending']} - Waiting approval</div></div>"
    html += f"<div style='margin:10px 0'><span class='stat'><b>{len(fixtures)}</b><br><span class='league'>Games</span></span><span class='stat'><b>2.80</b><br><span class='league'>Free</span></span><span class='stat'><b>7.50</b><br><span class='league'>Pro</span></span></div>"
    if not fixtures:
        html += "<div class='card'><div class='league'>NO GAMES - International Break</div></div>"
    else:
        html += "<h3 style='margin:14px 4px'>FREE 2 Games @2.80 - Over 1.5</h3>"
        for f in fixtures[:2]:
            wa = wa_link(f"FREE: {f['match']} - {f['tip']} @{f['odd']}")
            html += f"<div class='card'><div class='league'>{f['league']} - {f['date']} {f['time']}</div><div class='match'>{f['match']}</div><div class='tipbox'><div>{f['tip']}</div><div class='odd'>{f['odd']}</div></div><div style='margin-top:10px'><a href='{wa}' target='_blank' class='btn-wa'>WhatsApp Share</a></div></div>"
        html += "<h3 style='margin:18px 4px 8px'>PRO 6 Games @7.50</h3>"
        if user["plan"] == "pro" and user["status"] == "active":
            for f in fixtures[:6]:
                wa = wa_link(f"PRO: {f['match']} Over 1.5")
                html += f"<div class='card'><div class='league'>{f['league']}</div><div class='match'>{f['match']}</div><div class='tipbox'><div>Over 1.5</div><div class='odd'>{f['odd']}</div></div><a href='{wa}' class='btn-wa'>Share</a></div>"
        else:
            html += "<div class='card' style='text-align:center'><div class='match'>PRO LOCKED @7.50</div><br><a href='/plans' class='btn btn-primary'>View Plans</a></div>"
    html += "</div></body></html>"
    return html

@app.route("/history")
def history_page():
    email = session.get("email")
    html = f"<html><head>{STYLE}</head><body>{header_html(email)}<div style='padding:16px;max-width:600px;margin:0 auto'><h2>Win / Loss History</h2>"
    for h in HISTORY:
        color = "#00ff88" if h["status"]=="WIN" else "#ff6b6b"
        html += f"<div class='card' style='border-left:4px solid {color}'><div style='display:flex;justify-content:space-between'><div><div class='match'>{h['date']}</div><div class='league'>Free: {h['free']}</div><div class='league'>Pro: {h['pro']}</div></div><div style='color:{color};font-weight:800'>{h['status']}</div></div></div>"
    html += "<br><a href='/' class='btn btn-dark'>Back Home</a></div></body></html>"
    return html

@app.route("/plans")
def plans():
    html = f"<html><head>{STYLE}</head><body>{header_html(session.get('email'))}<div style='padding:16px;max-width:500px;margin:0 auto'><h2>Plans - Over 1.5 Only</h2><p style='color:#8aa0c5'>Opay 09079789177 - Arinze Peter</p>"
    for price, days in [("1000","3 Days"),("2000","7 Days"),("5000","15 Days"),("10000","25 Days"),("15000","30 Days")]:
        html += f"<div class='card'><div style='display:flex;justify-content:space-between'><div><div class='match'>N{price} - {days}</div></div><a href='/subscribe/{price}' class='btn btn-primary' style='width:auto'>I Paid</a></div></div>"
    html += "</div></body></html>"
    return html

@app.route("/subscribe/<plan>")
def subscribe(plan):
    email = session.get("email")
    if not email:
        return redirect("/login")
    USERS[email]["pending"] = plan
    USERS[email]["status"] = "pending"
    return redirect("/")

@app.route("/admin")
def admin_page():
    email = session.get("email")
    # SECURE: No info leak - if not admin, just deny
    if not email or not is_admin_user(email):
        return f"<html><head>{STYLE}</head><body>{header_html(email)}<div style='padding:40px;text-align:center'><h2>Access Denied</h2><p style='color:#8aa0c5'>You do not have permission to view this page.</p><br><a href='/' class='btn btn-dark'>Back to Home</a></div></body></html>"
    total = len(USERS)
    free = len([u for u in USERS.values() if u["plan"]=="free"])
    pro = len([u for u in USERS.values() if u["plan"]=="pro" and u["status"]=="active"])
    pending = len([u for u in USERS.values() if u["status"]=="pending"])
    html = f"<html><head>{STYLE}</head><body>{header_html(email)}<div style='padding:16px'><h2>Admin Dashboard - SECURE</h2><div style='margin:12px 0'><span class='stat'><b>{total}</b><br><span class='league'>Total</span></span><span class='stat'><b>{free}</b><br><span class='league'>Free</span></span><span class='stat'><b>{pro}</b><br><span class='league'>Pro</span></span><span class='stat'><b>{pending}</b><br><span class='league'>Pending</span></span></div>"
    if pending>0:
        html += "<h3 style='margin-top:20px'>Pending Payments</h3>"
        for em, u in USERS.items():
            if u["status"]=="pending":
                html += f"<div class='card' style='border-color:orange'><div class='match'>{em}</div><div class='league'>Paid N{u['pending']}</div><br><a href='/admin/approve/{em}' class='btn btn-primary' style='width:auto;display:inline-block'>APPROVE</a> <a href='/admin/reject/{em}' class='btn btn-dark' style='width:auto;display:inline-block'>REJECT</a></div>"
    html += "<h3 style='margin-top:20px'>All Users</h3>"
    for em, u in USERS.items():
        html += f"<div class='card'><div class='match' style='font-size:13px'>{em}</div><div class='league'>{u['plan']} - {u['status']}</div></div>"
    html += "<br><a href='/' class='btn btn-dark'>Home</a></div></body></html>"
    return html

@app.route("/admin/approve/<path:email>")
def approve(email):
    # Only admin can approve
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
        err = "Wrong email or password"
    html = f"<html><head>{STYLE}</head><body><div class='topbar'><div class='logo'>MASTERPICK<span>AI</span></div></div><div class='login-wrap'><h2>Welcome Back</h2>"
    if err:
        html += f"<div class='card' style='border-color:red;color:#ff6b6b'>{err}</div>"
    html += "<form method='post'><input class='input' name='email' placeholder='Email' required><input class='input' name='pass' type='password' placeholder='Password' required><br><br><button class='btn btn-primary'>Login</button></form><br><p style='text-align:center;color:#8aa0c5'>No account? <a href='/signup' style='color:#00ff88;font-weight:800;text-decoration:none'>Create Account</a></p></div></body></html>"
    return html

@app.route("/signup", methods=["GET","POST"])
def signup():
    err = ""
    if request.method == "POST":
        em = request.form["email"].lower().strip()
        pw = request.form["pass"]
        if em in USERS:
            err = "Email exists"
        else:
            USERS[em] = {"pass": pw, "plan": "free", "status": "active", "expiry": None, "is_admin": False, "pending": None, "joined": datetime.now().strftime("%Y-%m-%d")}
            session["email"] = em
            return redirect("/")
    html = f"<html><head>{STYLE}</head><body><div class='topbar'><div class='logo'>MASTERPICK<span>AI</span></div></div><div class='login-wrap'><h2>Create Account</h2><br>"
    if err:
        html += f"<div class='card' style='border-color:red'>{err}</div>"
    html += "<form method='post'><input class='input' name='email' placeholder='Email' required><input class='input' name='pass' type='password' placeholder='Password' required><br><br><button class='btn btn-primary'>Create Account</button></form><br><p style='text-align:center;color:#8aa0c5'>Have account? <a href='/login' style='color:#00ff88;font-weight:800;text-decoration:none'>Login</a></p></div></body></html>"
    return html

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
