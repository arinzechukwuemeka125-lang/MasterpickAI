import os, requests, urllib.parse
from datetime import datetime, timedelta
from flask import Flask, request, redirect, session

app = Flask(__name__)
app.secret_key = "v10_8_signup_fixed"
API_KEY = "8623f52e5c8224c49f7bb676d1f68665"

USERS = {
    "arinzechukwuemeka125@gmail.com": {
        "pass": "admin123", "plan": "pro", "status": "active",
        "expiry": datetime.now() + timedelta(days=365), "is_admin": True, "pending": None
    }
}

ALLOW = ["brazil","saudi","mls","major league","premier league","la liga","serie a","bundesliga","ligue 1","eredivisie","primeira","super lig","champions","europa","conference","world cup","qualification"]

def is_allowed(name):
    low = name.lower()
    for k in ALLOW:
        if k in low:
            return True
    return False

def get_fixtures():
    try:
        headers = {"x-apisports-key": API_KEY}
        today = datetime.now().strftime("%Y-%m-%d")
        url = "https://v3.football.api-sports.io/fixtures?date=" + today
        r = requests.get(url, headers=headers, timeout=12).json()
        out = []
        for f in r.get("response", [])[:80]:
            league = f["league"]["name"]
            if is_allowed(league):
                home = f["teams"]["home"]["name"]
                away = f["teams"]["away"]["name"]
                time = f["fixture"]["date"][11:16]
                out.append({"match": home + " vs " + away, "league": league, "time": time, "tip": "Over 1.5 Goals", "odd": "1.40", "conf": "8.5/10"})
        return out
    except:
        return []

def wa_link(text):
    return "https://wa.me/?text=" + urllib.parse.quote(text)

STYLE = "<meta name='viewport' content='width=device-width, initial-scale=1'><style>*{font-family:sans-serif;box-sizing:border-box;margin:0;padding:0}body{background:#070a10;color:#fff}.topbar{background:#0e1525;padding:14px 18px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1e2a44}.logo{font-weight:800;font-size:18px}.logo span{color:#00ff88}.badge{background:#00ff88;color:#000;font-size:10px;padding:3px 8px;border-radius:20px;font-weight:800;margin-left:8px}.btn{border:none;padding:12px 18px;border-radius:12px;font-weight:700;text-decoration:none;display:inline-block;text-align:center}.btn-primary{background:#00ff88;color:#000;width:100%}.btn-dark{background:#162032;color:#fff;border:1px solid #23324f;width:100%}.btn-wa{background:#25D366;color:#fff;padding:10px 12px;border-radius:10px;font-size:12px;font-weight:700;text-decoration:none;display:inline-block}.card{background:#121b2c;border:1px solid #1e2a44;border-radius:18px;padding:16px;margin:12px 0}.match{font-weight:800;font-size:15px;margin:6px 0}.league{color:#6b7fa3;font-size:11px}.tipbox{background:#0a121f;border:1px dashed #1e3a5f;border-radius:12px;padding:10px;margin-top:10px;display:flex;justify-content:space-between}.odd{background:#00ff88;color:#000;padding:6px 12px;border-radius:10px;font-weight:800}.input{width:100%;padding:14px;background:#0f172a;border:1px solid #1e2a44;border-radius:12px;color:#fff;margin:8px 0}.hero{background:#0e1525;border:1px solid #1e2a44;border-radius:24px;padding:24px;margin:16px;text-align:center}.login-wrap{max-width:400px;margin:40px auto;padding:24px}</style>"

def header_html(email=None):
    if email:
        nav = "<div style='font-size:11px'><span style='background:#162032;padding:6px 10px;border-radius:20px;border:1px solid #23324f'>" + email[:18] + "</span> <a href='/logout' style='color:#6b7fa3;margin-left:8px;text-decoration:none'>Logout</a></div>"
    else:
        nav = "<a href='/login' style='background:#162032;color:#fff;padding:8px 16px;border-radius:10px;font-size:13px;text-decoration:none'>Login</a> <a href='/signup' style='background:#00ff88;color:#000;padding:8px 16px;border-radius:10px;font-size:13px;text-decoration:none;margin-left:6px;font-weight:700'>Sign Up</a>"
    return "<div class='topbar'><div class='logo'>MASTERPICK<span>AI</span><span class='badge'>V10.8</span></div>" + nav + "</div>"

@app.route("/")
def home():
    email = session.get("email")
    user = USERS.get(email) if email else None
    fixtures = get_fixtures()
    html = "<html><head>" + STYLE + "</head><body>" + header_html(email)
    if not email:
        html += "<div class='hero'><h1>Real Games On SportyBet</h1><p style='color:#8aa0c5;font-size:13px'>Kenya removed - Only SportyBet - Over 1.5 @1.40</p><br><a href='/signup' class='btn btn-primary'>Create Free Account</a><br><br><a href='/login' class='btn btn-dark'>Already have account? Login</a></div></body></html>"
        return html
    html += "<div style='padding:16px'>"
    if user and user["status"] == "pending":
        html += "<div class='card'><div class='league' style='color:orange'>PENDING</div><div class='match'>Paid N" + str(user["pending"]) + "</div></div>"
    if fixtures:
        all_text = "MASTERPICKAI - SportyBet - Over 1.5:\n\n"
        for f in fixtures[:4]:
            all_text += f["match"] + " - Over 1.5 @" + f["odd"] + "\n"
        wa_all = wa_link(all_text)
        html += "<a href='" + wa_all + "' target='_blank' class='btn-wa' style='width:100%;text-align:center;padding:12px;margin-bottom:12px;display:block'>SHARE ALL TO WHATSAPP</a>"
    html += "<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px'><div class='card' style='margin:0;text-align:center'><div style='font-size:18px;font-weight:800'>" + str(len(fixtures)) + "</div><div class='league'>Sporty</div></div><div class='card' style='margin:0;text-align:center'><div style='font-size:18px;font-weight:800;color:#00ff88'>2.80</div><div class='league'>Free</div></div><div class='card' style='margin:0;text-align:center'><div style='font-size:18px;font-weight:800;color:gold'>7.50</div><div class='league'>Pro</div></div></div>"
    if len(fixtures) == 0:
        html += "<div class='card'><div class='league'>NO SPORTYBET GAMES THIS HOUR</div><div style='font-size:13px;margin-top:6px;color:#8aa0c5'>International break - Check 7PM MLS/Brazil</div></div>"
    else:
        html += "<h3 style='margin:14px 4px'>FREE 2 Games @2.80 - Over 1.5</h3>"
        for f in fixtures[:2]:
            wa = wa_link("FREE: " + f["match"] + " - Over 1.5 @" + f["odd"] + " - SportyBet OK")
            html += "<div class='card'><div class='league'>" + f["league"] + " - " + f["time"] + "</div><div class='match'>" + f["match"] + "</div><div class='tipbox'><div>Over 1.5 Goals</div><div class='odd'>" + f["odd"] + "</div></div><div style='margin-top:10px'><a href='" + wa + "' target='_blank' class='btn-wa'>WhatsApp Share</a></div></div>"
        html += "<h3 style='margin:18px 4px 8px'>PRO 6 Games @7.50</h3>"
        if user["plan"] == "pro" and user["status"] == "active":
            for f in fixtures:
                wa = wa_link("PRO: " + f["match"] + " Over 1.5")
                html += "<div class='card'><div class='league'>" + f["league"] + "</div><div class='match'>" + f["match"] + "</div><div class='tipbox'><div>Over 1.5</div><div class='odd'>" + f["odd"] + "</div></div><a href='" + wa + "' class='btn-wa'>Share</a></div>"
        else:
            html += "<div class='card' style='text-align:center'><div class='match'>PRO LOCKED @7.50</div><div style='color:#8aa0c5;font-size:13px'>Over 1.5 - SportyBet</div><br><a href='/plans' class='btn btn-primary'>View Plans</a></div>"
    html += "<br><a href='/plans' class='btn btn-dark'>Plans N1000-N15000</a> <a href='/admin' style='display:block;text-align:center;color:#4a5f85;font-size:12px;margin-top:12px;text-decoration:none'>Admin</a></div></body></html>"
    return html

@app.route("/plans")
def plans():
    html = "<html><head>" + STYLE + "</head><body>" + header_html(session.get("email")) + "<div style='padding:16px;max-width:500px;margin:0 auto'><h2>Plans - Over 1.5 Only</h2>"
    for price, days in [("1000","3 Days"),("2000","7 Days"),("5000","15 Days"),("10000","25 Days"),("15000","30 Days")]:
        html += "<div class='card'><div style='display:flex;justify-content:space-between'><div><div class='match'>N" + price + " - " + days + "</div></div><a href='/subscribe/" + price + "' class='btn btn-primary' style='width:auto'>I Paid</a></div></div>"
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
    if not email or not USERS.get(email, {}).get("is_admin"):
        return "<html><head>" + STYLE + "</head><body>" + header_html(email) + "<div style='padding:16px'>Not admin - login arinzechukwuemeka125@gmail.com</div></body></html>"
    html = "<html><head>" + STYLE + "</head><body>" + header_html(email) + "<div style='padding:16px'><h2>Admin</h2>"
    for em, u in USERS.items():
        if u["status"] == "pending":
            html += "<div class='card'>" + em + " - N" + str(u["pending"]) + " <a href='/admin/approve/" + em + "' class='btn btn-primary' style='width:auto'>APPROVE</a></div>"
    html += "</div></body></html>"
    return html

@app.route("/admin/approve/<path:email>")
def approve(email):
    USERS[email]["status"] = "active"
    USERS[email]["plan"] = "pro"
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
        err = "Wrong email or password"
    html = "<html><head>" + STYLE + "</head><body><div class='topbar'><div class='logo'>MASTERPICK<span>AI</span></div></div><div class='login-wrap'><h2>Welcome Back</h2>"
    if err:
        html += "<div class='card' style='border-color:red;color:#ff6b6b'>" + err + "</div>"
    html += "<form method='post'><input class='input' name='email' placeholder='Email' required><input class='input' name='pass' type='password' placeholder='Password' required><br><br><button class='btn btn-primary'>Login</button></form><br><p style='text-align:center;color:#8aa0c5;font-size:14px'>No account? <a href='/signup' style='color:#00ff88;text-decoration:none;font-weight:800'>Create Free Account Here</a></p><br><a href='/' class='btn btn-dark'>Back to Home</a></div></body></html>"
    return html

@app.route("/signup", methods=["GET","POST"])
def signup():
    err = ""
    if request.method == "POST":
        em = request.form["email"].lower().strip()
        pw = request.form["pass"]
        if em in USERS:
            err = "Email already exists - please login"
        else:
            USERS[em] = {"pass": pw, "plan": "free", "status": "active", "expiry": None, "is_admin": False, "pending": None}
            session["email"] = em
            return redirect("/")
    html = "<html><head>" + STYLE + "</head><body><div class='topbar'><div class='logo'>MASTERPICK<span>AI</span></div></div><div class='login-wrap'><h2>Create Free Account</h2><p style='color:#8aa0c5;font-size:13px'>Get 2 Free Games @2.80 daily - Over 1.5 SportyBet</p><br>"
    if err:
        html += "<div class='card' style='border-color:red;color:#ff6b6b'>" + err + "</div>"
    html += "<form method='post'><input class='input' name='email' placeholder='Enter your Email' required><input class='input' name='pass' type='password' placeholder='Create Password' required><br><br><button class='btn btn-primary'>Create Free Account</button></form><br><p style='text-align:center;color:#8aa0c5;font-size:14px'>Already have account? <a href='/login' style='color:#00ff88;text-decoration:none;font-weight:800'>Login Here</a></p><br><a href='/' class='btn btn-dark'>Back to Home</a></div></body></html>"
    return html

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
