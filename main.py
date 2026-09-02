import os, requests, urllib.parse
from datetime import datetime, timedelta
from flask import Flask, request, redirect, session

app = Flask(__name__)
app.secret_key = "masterpick_fixed_no_fstring"
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

SPORTY_LEAGUES = ["Premier League","La Liga","Serie A","Bundesliga","Ligue 1","Eredivisie","Major League Soccer","MLS","Brasileiro","Saudi","Pro League","Jupiler","Premiership","Copa do Brasil","Libertadores","World Cup","Qualification","Friendly"]

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
        for f in r.get("response", [])[:60]:
            league = f["league"]["name"]
            if is_sporty(league):
                home = f["teams"]["home"]["name"]
                away = f["teams"]["away"]["name"]
                time = f["fixture"]["date"][11:16]
                out.append({"match": home + " vs " + away, "league": league + " - " + f["league"]["country"], "time": time, "tip": "Over 0.5 Goals", "odd": "1.25", "conf": "9/10"})
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
    return "<div class='topbar'><div class='logo'>MASTERPICK<span>AI</span><span class='badge'>V10.5 FIXED</span></div>" + nav + "</div>"

@app.route("/")
def home():
    email = session.get("email")
    user = USERS.get(email) if email else None
    fixtures = get_fixtures()
    html = "<html><head>" + STYLE + "</head><body>" + header_html(email)
    if not email:
        html += "<div class='hero'><h1>Real Games On SportyBet</h1><p style='color:#8aa0c5;font-size:13px;margin-top:8px'>MLS, Brazil, Saudi - All SportyBet verified</p><br><a href='/signup' class='btn btn-primary'>Start Free</a><br><br><a href='/login' class='btn btn-dark'>Login</a></div></body></html>"
        return html
    html += "<div style='padding:16px'>"
    if user["status"] == "pending":
        html += "<div class='card'><div class='league' style='color:orange'>PENDING</div><div class='match'>Paid N" + str(user["pending"]) + " - Opay 09079789177</div></div>"
    if fixtures:
        all_text = "MASTERPICKAI TODAY:\n\n"
        for f in fixtures[:4]:
            all_text += f["match"] + " - " + f["tip"] + " @" + f["odd"] + "\n"
        all_text += "\nJoin: https://masterpickai.onrender.com"
        wa_all = wa_link(all_text)
        html += "<a href='" + wa_all + "' target='_blank' class='btn-wa' style='width:100%;text-align:center;padding:12px;margin-bottom:12px'>SHARE ALL TO WHATSAPP</a>"
    html += "<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px'><div class='card' style='margin:0;text-align:center'><div style='font-size:18px;font-weight:800'>" + str(len(fixtures)) + "</div><div class='league'>Real Today</div></div><div class='card' style='margin:0;text-align:center'><div style='font-size:18px;font-weight:800;color:#00ff88'>1.56</div><div class='league'>Free</div></div><div class='card' style='margin:0;text-align:center'><div style='font-size:18px;font-weight:800;color:gold'>4.80</div><div class='league'>Pro</div></div></div>"
    if len(fixtures) == 0:
        html += "<div class='card'><div class='league'>No SportyBet games this hour - check later 12AM</div></div>"
    else:
        html += "<h3 style='margin:14px 4px'>FREE 2 Games @1.56</h3>"
        for f in fixtures[:2]:
            share_txt = "MASTERPICKAI FREE TIP: " + f["match"] + " - " + f["tip"] + " @" + f["odd"] + " - " + f["league"] + " Join: https://masterpickai.onrender.com"
            wa = wa_link(share_txt)
            html += "<div class='card'><div class='league'>" + f["league"] + " - " + f["time"] + "</div><div class='match'>" + f["match"] + "</div><div class='tipbox'><div>" + f["tip"] + " - " + f["conf"] + "</div><div class='odd'>" + f["odd"] + "</div></div><div style='margin-top:10px'><a href='" + wa + "' target='_blank' class='btn-wa'>WhatsApp Share</a></div></div>"
        html += "<h3 style='margin:18px 4px 8px'>PRO 6 Games @4.80</h3>"
        if user["plan"] == "pro" and user["status"] == "active":
            for f in fixtures:
                share_txt = "MASTERPICKAI PRO: " + f["match"] + " - " + f["tip"] + " @" + f["odd"] + " https://masterpickai.onrender.com"
                wa = wa_link(share_txt)
                html += "<div class='card'><div class='league'>" + f["league"] + "</div><div class='match'>" + f["match"] + "</div><div class='tipbox'><div>" + f["tip"] + "</div><div class='odd'>" + f["odd"] + "</div></div><div style='margin-top:10px'><a href='" + wa + "' target='_blank' class='btn-wa'>Share Pro</a></div></div>"
        else:
            html += "<div class='card' style='text-align:center'><div style='font-size:32px'>LOCKED</div><div class='match'>Pro Locked</div><br><a href='/plans' class='btn btn-primary'>View Plans</a></div>"
    html += "<br><a href='/plans' class='btn btn-dark'>Plans</a></div></body></html>"
    return html

@app.route("/plans")
def plans():
    html = "<html><head>" + STYLE + "</head><body>" + header_html(session.get("email")) + "<div style='padding:16px;max-width:500px;margin:0 auto'><h2>Plans</h2><p style='color:#8aa0c5'>Opay 09079789177 - Arinze</p>"
    for price, days in [("1000","3 Days"),("2000","7 Days"),("5000","15 Days"),("10000","25 Days"),("15000","30 Days")]:
        html += "<div class='card'><div style='display:flex;justify-content:space-between;align-items:center'><div><div class='match'>N" + price + " - " + days + "</div></div><a href='/subscribe/" + price + "' class='btn btn-primary' style='width:auto'>I Paid</a></div></div>"
    html += "<br><a href='/' class='btn btn-dark'>Home</a></div></body></html>"
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
    if not email or not USERS.get(email, {}).get("is_admin"):
        return "<html><head>" + STYLE + "</head><body>" + header_html(email) + "<div style='padding:16px'>Not admin</div></body></html>"
    html = "<html><head>" + STYLE + "</head><body>" + header_html(email) + "<div style='padding:16px'><h2>Admin Panel</h2>"
    for em, u in USERS.items():
        if u["status"] == "pending":
            html += "<div class='card'>" + em + " - N" + str(u["pending"]) + " <a href='/admin/approve/" + em + "' class='btn btn-primary' style='width:auto'>APPROVE</a> <a href='/admin/reject/" + em + "' class='btn btn-dark' style='width:auto'>REJECT</a></div>"
    html += "</div></body></html>"
    return html

@app.route("/admin/approve/<path:email>")
def approve(email):
    if not session.get("email") or not USERS.get(session.get("email"), {}).get("is_admin"):
        return "Not admin"
    days_map = {"1000":3,"2000":7,"5000":15,"10000":25,"15000":30}
    pending = USERS[email].get("pending","1000")
    USERS[email]["status"] = "active"
    USERS[email]["plan"] = "pro"
    USERS[email]["expiry"] = datetime.now() + timedelta(days=days_map.get(pending,3))
    USERS[email]["pending"] = None
    return redirect("/admin")

@app.route("/admin/reject/<path:email>")
def reject(email):
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
        err = "Wrong password"
    html = "<html><head>" + STYLE + "</head><body><div class='topbar'><div class='logo'>MASTERPICK<span>AI</span></div></div><div class='login-wrap'><h2>Login</h2>"
    if err:
        html += "<div class='card'>" + err + "</div>"
    html += "<form method='post'><input class='input' name='email' placeholder='Email' required><input class='input' name='pass' type='password' placeholder='Password' required><br><br><button class='btn btn-primary'>Login</button></form><br><a href='/signup' style='color:#00ff88'>Create account</a></div></body></html>"
    return html

@app.route("/signup", methods=["GET","POST"])
def signup():
    err = ""
    if request.method == "POST":
        em = request.form["email"].lower().strip()
        pw = request.form["pass"]
        if em in USERS:
            err = "Exists"
        else:
            USERS[em] = {"pass": pw, "plan": "free", "status": "active", "expiry": None, "is_admin": False, "pending": None}
            session["email"] = em
            return redirect("/")
    html = "<html><head>" + STYLE + "</head><body><div class='topbar'><div class='logo'>MASTERPICK<span>AI</span></div></div><div class='login-wrap'><h2>Join Free</h2>"
    if err:
        html += "<div class='card'>" + err + "</div>"
    html += "<form method='post'><input class='input' name='email' placeholder='Email' required><input class='input' name='pass' type='password' placeholder='Password' required><br><br><button class='btn btn-primary'>Create Account</button></form><br><a href='/login' style='color:#00ff88'>Login</a></div></body></html>"
    return html

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
