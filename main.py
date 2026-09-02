import os, requests, urllib.parse
from datetime import datetime, timedelta
from flask import Flask, request, redirect, session

app = Flask(__name__)
app.secret_key = "v11_6_1_fixed"
API_KEY = "8623f52e5c8224c49f7bb676d1f68665"
ADMIN_EMAIL = "arinzechukwuemeka125@gmail.com"

USERS = {
    ADMIN_EMAIL: {"pass": "Master2026!Secure", "plan": "pro", "status": "active", "expiry": datetime.now() + timedelta(days=365), "is_admin": True, "pending": None, "joined": "2026-09-01"}
}

def get_live_fixtures():
    football = []
    volleyball = []
    headers = {"x-apisports-key": API_KEY}
    try:
        for day_offset in [0,1]:
            d = (datetime.now() + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            url = f"https://v3.football.api-sports.io/fixtures?date={d}"
            r = requests.get(url, headers=headers, timeout=10).json()
            for f in r.get("response", [])[:100]:
                try:
                    home = f["teams"]["home"]["name"]
                    away = f["teams"]["away"]["name"]
                    time = f["fixture"]["date"][11:16]
                    league = f["league"]["name"]
                    football.append({"match": home + " vs " + away, "league": league, "time": time, "date": d, "tip": "Over 1.5 Goals", "odd": "1.40"})
                except:
                    continue
    except:
        pass
    try:
        for day_offset in [0,1]:
            d = (datetime.now() + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            url = f"https://v1.volleyball.api-sports.io/games?date={d}"
            r = requests.get(url, headers=headers, timeout=10).json()
            for v in r.get("response", [])[:50]:
                try:
                    home = v.get("teams",{}).get("home",{}).get("name","Team A")
                    away = v.get("teams",{}).get("away",{}).get("name","Team B")
                    league = v.get("league",{}).get("name","Volleyball League")
                    date_str = v.get("date","")
                    time = date_str[11:16] if len(date_str)>=16 else "18:00"
                    volleyball.append({"match": home + " vs " + away, "league": league, "time": time, "date": d, "tip": "Over 144.5 Points", "odd": "1.38"})
                except:
                    continue
    except:
        pass
    return football[:20], volleyball[:10]

def wa_link(t): return "https://wa.me/?text=" + urllib.parse.quote(t)
STYLE = "<meta name='viewport' content='width=device-width, initial-scale=1'><style>*{font-family:sans-serif;box-sizing:border-box;margin:0;padding:0}body{background:#070a10;color:#fff}.topbar{background:#0e1525;padding:14px 18px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1e2a44}.logo{font-weight:800;font-size:18px}.logo span{color:#00ff88}.badge{background:#00ff88;color:#000;font-size:10px;padding:3px 8px;border-radius:20px;font-weight:800;margin-left:8px}.btn{border:none;padding:12px 18px;border-radius:12px;font-weight:700;text-decoration:none;display:inline-block;text-align:center}.btn-primary{background:#00ff88;color:#000;width:100%}.btn-dark{background:#162032;color:#fff;border:1px solid #23324f;width:100%}.btn-wa{background:#25D366;color:#fff;padding:8px 12px;border-radius:10px;font-size:12px;font-weight:700;text-decoration:none;display:inline-block}.card{background:#121b2c;border:1px solid #1e2a44;border-radius:18px;padding:16px;margin:10px 0}.card-v{background:#0f1a14;border:1px solid #1a3a2a;border-radius:18px;padding:16px;margin:10px 0}.match{font-weight:800;font-size:15px;margin:6px 0}.league{color:#6b7fa3;font-size:11px}.tipbox{background:#0a121f;border:1px dashed #1e3a5f;border-radius:12px;padding:10px;margin-top:10px;display:flex;justify-content:space-between}.odd{background:#00ff88;color:#000;padding:6px 12px;border-radius:10px;font-weight:800}.odd-v{background:#ffcc00;color:#000;padding:6px 12px;border-radius:10px;font-weight:800}.input{width:100%;padding:14px;background:#0f172a;border:1px solid #1e2a44;border-radius:12px;color:#fff;margin:8px 0}.login-wrap{max-width:400px;margin:40px auto;padding:24px}.stat{display:inline-block;background:#121b2c;border:1px solid #1e2a44;border-radius:14px;padding:12px 16px;margin:6px;min-width:80px;text-align:center}.tab{padding:6px 12px;border-radius:20px;font-weight:800;font-size:11px}.tab-f{background:#00ff88;color:#000}.tab-v{background:#ffcc00;color:#000}</style>"
def is_admin_user(email): return email == ADMIN_EMAIL and USERS.get(email, {}).get("is_admin")
def header_html(email=None):
    if email:
        admin_btn = "<a href='/admin' style='background:gold;color:#000;padding:6px 10px;border-radius:8px;font-size:11px;text-decoration:none;margin-right:8px;font-weight:800'>ADMIN</a>" if is_admin_user(email) else ""
        nav = f"<div style='font-size:11px'>{admin_btn}<span style='background:#162032;padding:6px 10px;border-radius:20px'>{email[:14]}</span> <a href='/logout' style='color:#6b7fa3;margin-left:8px;text-decoration:none'>Logout</a></div>"
    else:
        nav = "<a href='/login' style='background:#162032;color:#fff;padding:8px 14px;border-radius:10px;font-size:13px;text-decoration:none'>Login</a> <a href='/signup' style='background:#00ff88;color:#000;padding:8px 14px;border-radius:10px;font-size:13px;text-decoration:none;margin-left:6px;font-weight:700'>Sign Up</a>"
    return f"<div class='topbar'><div class='logo'>MASTERPICK<span>AI</span><span class='badge'>V11.6.1 FIXED</span></div>{nav}</div>"
@app.route("/")
def home():
    email = session.get("email")
    user = USERS.get(email) if email else None
    football, volleyball = get_live_fixtures()
    total = len(football) + len(volleyball)
    html = f"<html><head>{STYLE}</head><body>{header_html(email)}"
    if not email:
        html += f"<div style='padding:16px'><div style='background:#0e1525;border:1px solid #1e2a44;border-radius:24px;padding:24px;text-align:center'><h1>{len(football)} Football + {len(volleyball)} Volleyball = {total} Live Real</h1><p style='color:#8aa0c5'>Same Key - No Fake - Fixed</p><br><a href='/signup' class='btn btn-primary'>Create Account</a><br><br><a href='/login' class='btn btn-dark'>Login</a></div></div></body></html>"
        return html
    html += "<div style='padding:16px'>"
    if is_admin_user(email):
        html += "<div style='display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px'><a href='/history' class='btn-wa' style='background:#162032;border:1px solid #23324f'>History</a><a href='/plans' class='btn-wa' style='background:#162032;border:1px solid #23324f'>Plans</a><a href='/admin' class='btn-wa' style='background:gold;color:#000'>Admin</a></div>"
    else:
        html += "<div style='display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px'><a href='/history' class='btn-wa' style='background:#162032;border:1px solid #23324f'>History</a><a href='/plans' class='btn-wa' style='background:#162032;border:1px solid #23324f'>Upgrade</a></div>"
    html += f"<div style='margin:10px 0'><span class='stat'><b>{len(football)}</b><br><span class='league'>Football Live</span></span><span class='stat'><b>{len(volleyball)}</b><br><span class='league'>Volley Live</span></span><span class='stat'><b>{total}</b><br><span class='league'>Total</span></span></div>"
    if total == 0:
        html += "<div class='card' style='text-align:center;border-color:#ff6b6b'><div class='match'>No Live Games - API limit or no fixtures today</div><div class='league'>API 100/day - Resets midnight UTC</div></div>"
    else:
        if len(football) > 0:
            html += "<h3 style='margin:14px 4px'><span class='tab tab-f'>FOOTBALL LIVE REAL</span> Free 2 @2.80</h3>"
            for f in football[:2]:
                wa = wa_link(f"FOOTBALL LIVE: {f['match']} - {f['tip']} @{f['odd']} - {f['date']}")
                html += f"<div class='card'><div class='league'>{f['league']} - {f['date']} {f['time']} - REAL</div><div class='match'>{f['match']}</div><div class='tipbox'><div>{f['tip']}</div><div class='odd'>{f['odd']}</div></div><a href='{wa}' target='_blank' class='btn-wa'>Share</a></div>"
        if len(volleyball) > 0:
            html += "<h3 style='margin:18px 4px 8px'><span class='tab tab-v'>VOLLEYBALL LIVE REAL - EASIER</span> Free 2 @1.90</h3>"
            for v in volleyball[:2]:
                wa = wa_link(f"VOLLEYBALL LIVE: {v['match']} - {v['tip']} @{v['odd']} - {v['date']}")
                html += f"<div class='card-v'><div class='league'>{v['league']} - {v['date']} {v['time']} - REAL</div><div class='match'>{v['match']}</div><div class='tipbox'><div>{v['tip']}</div><div class='odd-v'>{v['odd']}</div></div><a href='{wa}' target='_blank' class='btn-wa'>Share Volley</a></div>"
        html += "<h3 style='margin:18px 4px 8px'>PRO @8.50</h3>"
        if user and user["plan"] == "pro" and user["status"] == "active":
            for f in football[:4]:
                html += f"<div class='card'><div class='league'>{f['league']} - {f['date']}</div><div class='match'>{f['match']}</div><div class='tipbox'><div>Over 1.5</div><div class='odd'>{f['odd']}</div></div></div>"
            for v in volleyball[:4]:
                html += f"<div class='card-v'><div class='league'>{v['league']} - {v['date']}</div><div class='match'>{v['match']}</div><div class='tipbox'><div>{v['tip']}</div><div class='odd-v'>{v['odd']}</div></div></div>"
        else:
            html += "<div class='card' style='text-align:center'><div class='match'>PRO LOCKED - Live Football + Volleyball @8.50</div><br><a href='/plans' class='btn btn-primary'>Unlock Plans</a></div>"
    html += "</div></body></html>"
    return html
@app.route("/plans")
def plans():
    html = f"<html><head>{STYLE}</head><body>{header_html(session.get('email'))}<div style='padding:16px;max-width:500px;margin:0 auto'><h2>Plans - Live Football + Volleyball</h2><p style='color:#8aa0c5'>Same API Key - Opay 09079789177</p>"
    for price, days in [("1000","3 Days"),("2000","7 Days"),("5000","15 Days"),("10000","25 Days"),("15000","30 Days")]:
        html += f"<div class='card'><div style='display:flex;justify-content:space-between'><div><div class='match'>N{price} - {days}</div><div class='league'>Football + Volleyball Live</div></div><a href='/subscribe/{price}' class='btn btn-primary' style='width:auto'>I Paid</a></div></div>"
    html += "</div></body></html>"
    return html
@app.route("/history")
def history_page():
    email = session.get("email")
    return f"<html><head>{STYLE}</head><body>{header_html(email)}<div style='padding:16px;max-width:600px;margin:0 auto'><h2>History</h2><br><a href='/' class='btn btn-dark'>Home</a></div></body></html>"
@app.route("/subscribe/<plan>")
def subscribe(plan):
    email = session.get("email")
    if not email: return redirect("/login")
    USERS[email]["pending"] = plan
    USERS[email]["status"] = "pending"
    return redirect("/")
@app.route("/admin")
def admin_page():
    email = session.get("email")
    if not email or not is_admin_user(email):
        return f"<html><head>{STYLE}</head><body>{header_html(email)}<div style='padding:40px;text-align:center'><h2>Access Denied</h2><br><a href='/' class='btn btn-dark'>Home</a></div></body></html>"
    football, volleyball = get_live_fixtures()
    total = len(football) + len(volleyball)
    pending = len([u for u in USERS.values() if u["status"]=="pending"])
    html = f"<html><head>{STYLE}</head><body>{header_html(email)}<div style='padding:16px'><h2>Admin V11.6.1 - {len(football)}F + {len(volleyball)}V = {total} Live Real - Fixed</h2><div style='margin:12px 0'><span class='stat'><b>{total}</b><br><span class='league'>Live Real</span></span><span class='stat'><b>{pending}</b><br><span class='league'>Pending</span></span></div>"
    if pending>0:
        for em, u in USERS.items():
            if u["status"]=="pending":
                html += f"<div class='card' style='border-color:orange'><div class='match'>{em}</div><div class='league'>N{u['pending']}</div><br><a href='/admin/approve/{em}' class='btn btn-primary' style='width:auto'>APPROVE</a> <a href='/admin/reject/{em}' class='btn btn-dark' style='width:auto'>REJECT</a></div>"
    for em, u in USERS.items():
        html += f"<div class='card'><div class='match' style='font-size:13px'>{em}</div><div class='league'>{u['plan']} - {u['status']}</div></div>"
    html += "</div></body></html>"
    return html
@app.route("/admin/approve/<path:email>")
def approve(email):
    if not is_admin_user(session.get("email")): return redirect("/")
    if email in USERS:
        USERS[email]["status"] = "active"
        USERS[email]["plan"] = "pro"
        USERS[email]["pending"] = None
    return redirect("/admin")
@app.route("/admin/reject/<path:email>")
def reject(email):
    if not is_admin_user(session.get("email")): return redirect("/")
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
    return f"<html><head>{STYLE}</head><body><div class='topbar'><div class='logo'>MASTERPICK<span>AI</span></div></div><div class='login-wrap'><h2>Login</h2>{'<div class=card style=border-color:red>'+err+'</div>' if err else ''}<form method='post'><input class='input' name='email' placeholder='Email' required><input class='input' name='pass' type='password' placeholder='Password' required><br><br><button class='btn btn-primary'>Login</button></form></div></body></html>"
@app.route("/signup", methods=["GET","POST"])
def signup():
    err = ""
    if request.method == "POST":
        em = request.form["email"].lower().strip()
        pw = request.form["pass"]
        if em in USERS:
            err = "Exists"
        else:
            USERS[em] = {"pass": pw, "plan": "free", "status": "active", "expiry": None, "is_admin": False, "pending": None, "joined": datetime.now().strftime("%Y-%m-%d")}
            session["email"] = em
            return redirect("/")
    return f"<html><head>{STYLE}</head><body><div class='topbar'><div class='logo'>MASTERPICK<span>AI</span></div></div><div class='login-wrap'><h2>Sign Up Free</h2>{'<div class=card style=border-color:red>'+err+'</div>' if err else ''}<form method='post'><input class='input' name='email' placeholder='Email' required><input class='input' name='pass' type='password' placeholder='Password' required><br><br><button class='btn btn-primary'>Create</button></form></div></body></html>"
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
