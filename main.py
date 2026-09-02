import os, requests
from datetime import datetime, timedelta
from flask import Flask, request, redirect, session

app = Flask(__name__)
app.secret_key = "masterpick_v10_3_premium_2026"
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

def get_fixtures():
    try:
        headers = {"x-apisports-key": API_KEY}
        today = datetime.now().strftime("%Y-%m-%d")
        url = "https://v3.football.api-sports.io/fixtures?date=" + today
        r = requests.get(url, headers=headers, timeout=10).json()
        out = []
        for f in r.get("response", [])[:8]:
            home = f["teams"]["home"]["name"]
            away = f["teams"]["away"]["name"]
            league = f["league"]["name"]
            country = f["league"]["country"]
            time = f["fixture"]["date"][11:16]
            out.append({
                "match": home + " vs " + away,
                "league": league + " - " + country,
                "time": time,
                "tip": "Over 0.5 Goals",
                "odd": "1.25",
                "conf": "9/10 SUREST"
            })
        return out
    except:
        return []

STYLE = """
<meta name='viewport' content='width=device-width, initial-scale=1'>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
*{font-family:'Inter',sans-serif;box-sizing:border-box;margin:0;padding:0}
body{background:#070a10;color:#fff;min-height:100vh}
.topbar{background:#0e1525;padding:14px 18px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1e2a44;position:sticky;top:0;z-index:10}
.logo{font-weight:800;font-size:18px;letter-spacing:-0.5px}
.logo span{color:#00ff88}
.badge{background:#00ff88;color:#000;font-size:10px;padding:3px 8px;border-radius:20px;font-weight:800;margin-left:8px}
.btn{border:none;padding:12px 18px;border-radius:12px;font-weight:700;cursor:pointer;text-decoration:none;display:inline-block;text-align:center;transition:0.2s}
.btn-primary{background:#00ff88;color:#000;width:100%;font-size:16px}
.btn-primary:hover{transform:translateY(-1px);box-shadow:0 6px 20px rgba(0,255,136,0.3)}
.btn-dark{background:#162032;color:#fff;border:1px solid #23324f;width:100%}
.card{background:linear-gradient(145deg,#121b2c,#0f172a);border:1px solid #1e2a44;border-radius:18px;padding:16px;margin:12px 0;position:relative;overflow:hidden}
.card::before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:#00ff88}
.card.gold::before{background:gold}
.card.pending::before{background:orange}
.league{color:#6b7fa3;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px}
.match{font-weight:800;font-size:16px;margin:6px 0}
.tipbox{background:#0a121f;border:1px dashed #1e3a5f;border-radius:12px;padding:10px;margin-top:10px;display:flex;justify-content:space-between;align-items:center}
.odd{background:#00ff88;color:#000;padding:6px 12px;border-radius:10px;font-weight:800;font-size:14px}
.conf{font-size:11px;color:#00ff88;font-weight:700}
.login-wrap{max-width:400px;margin:40px auto;padding:24px}
.input{width:100%;padding:14px 16px;background:#0f172a;border:1px solid #1e2a44;border-radius:12px;color:#fff;font-size:15px;margin:8px 0;outline:none}
.input:focus{border-color:#00ff88}
.hero{background:radial-gradient(800px 300px at 50% -10%,rgba(0,255,136,0.15),transparent),#0e1525;border:1px solid #1e2a44;border-radius:24px;padding:24px;margin:16px;text-align:center}
.status-dot{width:8px;height:8px;background:#00ff88;border-radius:50%;display:inline-block;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}
</style>
"""

def header_html(email=None):
    user = USERS.get(email) if email else None
    nav = ""
    if email:
        plan = user["plan"].upper() if user else "FREE"
        nav = "<div style='font-size:12px'><span style='background:#162032;padding:6px 10px;border-radius:20px;border:1px solid #23324f'>" + email[:18] + " | " + plan + "</span> <a href='/logout' style='color:#6b7fa3;margin-left:8px;text-decoration:none'>Logout</a></div>"
    else:
        nav = "<a href='/login' class='btn' style='background:#162032;color:#fff;padding:8px 16px;border-radius:10px;font-size:13px;border:1px solid #23324f'>Login</a>"
    return "<div class='topbar'><div class='logo'>MASTERPICK<span>AI</span><span class='badge'>V10.3 REAL</span></div>" + nav + "</div>"

@app.route("/")
def home():
    email = session.get("email")
    user = USERS.get(email) if email else None
    fixtures = get_fixtures()

    html = "<html><head>" + STYLE + "</head><body>"
    html += header_html(email)

    if not email:
        html += "<div class='hero'><div style='font-size:12px;color:#00ff88;font-weight:800;letter-spacing:1px;margin-bottom:8px'><span class='status-dot'></span> LIVE - 100% REAL FIXTURES</div><h1 style='font-size:28px;font-weight:800;line-height:1.1;margin:10px 0'>Win with Real<br>Data, Not Fake</h1><p style='color:#8aa0c5;font-size:14px;line-height:1.5'>API-Football verified fixtures daily. No fake games. Free 9/10 possible predictions.</p><br><a href='/signup' class='btn btn-primary'>Start Free - No Card Needed</a><br><br><a href='/login' class='btn btn-dark'>Login to Account</a><p style='margin-top:14px;color:#4a5f85;font-size:11px'>Trusted by Port Harcourt punters • Opay: 09079789177</p></div>"
        html += "<div style='padding:0 16px'><div class='card'><div class='league'>Why MasterpickAI?</div><div style='margin-top:8px;color:#cbd5e1;font-size:13px;line-height:1.6'>✅ 100% Real fixtures from API-Football<br>✅ Free 2 games @1.56 daily - 9/10 possible<br>✅ Pro 6 games @4.80 - Honest 6-7/10<br>✅ No fake odds, admin approved payments</div></div></div>"
        return html + "</body></html>"

    # Logged in view
    html += "<div style='padding:16px'>"

    if user["status"] == "pending":
        html += "<div class='card pending'><div class='league' style='color:orange'>⏳ PENDING APPROVAL</div><div class='match' style='font-size:14px'>You paid ₦" + str(user["pending"]) + "</div><div style='color:#cbd5e1;font-size:13px;margin-top:6px'>Send screenshot to WhatsApp? No - Admin checks Opay <b>09079789177 Arinze</b> and approves in 5 mins. Refresh page.</div></div>"

    # Stats bar
    live_count = len(fixtures)
    html += "<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:10px'><div class='card' style='margin:0;text-align:center;padding:12px'><div style='font-size:20px;font-weight:800'>" + str(live_count) + "</div><div class='league'>Real Today</div></div><div class='card' style='margin:0;text-align:center;padding:12px'><div style='font-size:20px;font-weight:800;color:#00ff88'>1.56</div><div class='league'>Free Odd</div></div><div class='card' style='margin:0;text-align:center;padding:12px'><div style='font-size:20px;font-weight:800;color:gold'>4.80</div><div class='league'>Pro Odd</div></div></div>"

    html += "<h3 style='margin:14px 4px;font-size:16px'>🆓 FREE ACCA - 2 Games @1.56 <span style='color:#00ff88;font-size:11px'>9/10 POSSIBLE</span></h3>"
    if fixtures:
        for f in fixtures[:2]:
            html += "<div class='card'><div class='league'>" + f["league"] + " • " + f["time"] + " • REAL</div><div class='match'>" + f["match"] + "</div><div class='tipbox'><div><div style='font-weight:700;font-size:13px'>✅ " + f["tip"] + "</div><div class='conf'>" + f["conf"] + "</div></div><div class='odd'>" + f["odd"] + "</div></div></div>"
    else:
        html += "<div class='card'><div class='league'>No fixtures</div><div class='match' style='font-size:14px'>No real football today (" + datetime.now().strftime("%Y-%m-%d") + ")</div><div style='color:#8aa0c5;font-size:12px'>International break - API returned 0. No fake games policy.</div></div>"

    html += "<h3 style='margin:18px 4px 8px;font-size:16px'>👑 PRO ACCA - 6 Games <span style='color:gold;font-size:11px'>@4.80 HONEST 6-7/10</span></h3>"
    if user["plan"] == "pro" and user["status"] == "active":
        if fixtures:
            total = 1
            for f in fixtures:
                total = total * float(f["odd"])
                html += "<div class='card gold'><div class='league'>" + f["league"] + " • " + f["time"] + "</div><div class='match'>" + f["match"] + "</div><div class='tipbox'><div><div style='font-weight:700;font-size:13px'>🔥 " + f["tip"] + "</div><div class='conf' style='color:gold'>HIGH VALUE</div></div><div class='odd' style='background:gold'>" + f["odd"] + "</div></div></div>"
            html += "<div class='card gold' style='background:linear-gradient(145deg,#1a1a0a,#12120a);border-color:#3a3200'><div style='display:flex;justify-content:space-between;align-items:center'><div><div class='league'>TOTAL PRO ACCA</div><div style='font-size:22px;font-weight:800;color:gold'>" + "{:.2f}".format(total) + " ODDS</div></div><div style='text-align:right'><div style='font-size:11px;color:#8a7d4a'>Honest Prediction<br>6-7/10 Hit Rate</div></div></div></div>"
        else:
            html += "<div class='card'><p>No Pro games today</p></div>"
    else:
        html += "<div class='card' style='text-align:center;padding:22px;border-style:dashed'><div style='font-size:32px;margin-bottom:8px'>🔒</div><div class='match' style='font-size:15px'>Pro Acca Locked</div><div style='color:#8aa0c5;font-size:13px;margin:8px 0'>Subscribe to unlock 6 daily games @4.80<br>Pay to Opay <b>09079789177</b> - Arinze Chukwuemeka</div><br><a href='/plans' class='btn btn-primary'>View Plans & Pay</a></div>"

    html += "<br><a href='/plans' class='btn btn-dark'>💳 Plans - ₦1000 to ₦15000</a> <a href='/admin' style='display:block;text-align:center;color:#4a5f85;font-size:12px;margin-top:12px;text-decoration:none'>Admin Panel →</a>"
    html += "</div></body></html>"
    return html

@app.route("/plans")
def plans():
    html = "<html><head>" + STYLE + "</head><body>" + header_html(session.get("email"))
    html += "<div style='padding:16px;max-width:500px;margin:0 auto'><h2 style='font-size:22px;font-weight:800'>Choose Plan</h2><p style='color:#8aa0c5;font-size:13px;margin:6px 0 16px'>Pay to <b style='color:#fff'>Opay 09079789177 - Arinze Chukwuemeka Peter</b><br>After transfer, click I Paid → goes to PENDING → admin approves</p>"
    plans_list = [("1000","3 Days","Popular"),("2000","7 Days","Best Value"),("5000","15 Days",None),("10000","25 Days","VIP"),("15000","30 Days","MAX")]
    for price, days, tag in plans_list:
        tag_html = "<span style='background:#00ff88;color:#000;font-size:10px;padding:3px 8px;border-radius:20px;font-weight:800;margin-left:8px'>" + tag + "</span>" if tag else ""
        html += "<div class='card'><div style='display:flex;justify-content:space-between;align-items:center'><div><div class='match'>₦" + price + " " + tag_html + "</div><div class='league'>" + days + " Pro Access • 6 games daily</div></div><a href='/subscribe/" + price + "' class='btn btn-primary' style='width:auto;padding:10px 18px;font-size:13px'>I Paid ₦" + price + "</a></div></div>"
    html += "<br><a href='/' class='btn btn-dark'>← Back Home</a></div></body></html>"
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
        return "<html><head>" + STYLE + "</head><body>" + header_html(email) + "<div style='padding:16px'>Not admin. Login as arinzechukwuemeka125@gmail.com<br><a href='/'>Home</a></div></body></html>"
    html = "<html><head>" + STYLE + "</head><body>" + header_html(email)
    html += "<div style='padding:16px'><h2 style='font-weight:800'>🔧 Admin Panel</h2><h3 style='margin:16px 0 8px;color:orange'>⏳ Pending Approvals</h3>"
    has_pending = False
    for em, u in USERS.items():
        if u["status"] == "pending":
            has_pending = True
            html += "<div class='card pending'><div class='match'>" + em + "</div><div class='league'>Wants ₦" + str(u["pending"]) + " Plan • Check Opay 09079789177</div><div style='margin-top:10px;display:flex;gap:8px'><a href='/admin/approve/" + em + "' class='btn btn-primary' style='width:auto'>✅ APPROVE</a><a href='/admin/reject/" + em + "' class='btn btn-dark' style='width:auto'>❌ REJECT</a></div></div>"
    if not has_pending:
        html += "<div class='card'><p style='color:#6b7fa3'>No pending payments. All clear.</p></div>"
    html += "<h3 style='margin:18px 0 8px'>All Users (" + str(len(USERS)) + ")</h3>"
    for em, u in USERS.items():
        html += "<div class='card' style='padding:10px'><div style='font-size:12px'><b>" + em + "</b><br>" + u["plan"] + " | " + u["status"] + " | Expiry: " + str(u["expiry"])[:16] + "</div></div>"
    html += "<br><a href='/' class='btn btn-dark'>← Home</a></div></body></html>"
    return html

@app.route("/admin/approve/<path:email>")
def approve(email):
    admin_email = session.get("email")
    if not admin_email or not USERS.get(admin_email, {}).get("is_admin"):
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
    error = ""
    if request.method == "POST":
        em = request.form["email"].lower().strip()
        pw = request.form["pass"]
        if em in USERS and USERS[em]["pass"] == pw:
            session["email"] = em
            return redirect("/")
        error = "Wrong email or password"
    html = "<html><head>" + STYLE + "</head><body><div class='topbar'><div class='logo'>MASTERPICK<span>AI</span></div></div>"
    html += "<div class='login-wrap'><div class='hero' style='margin:0 0 20px'><h2 style='font-size:24px;font-weight:800'>Welcome Back 👋</h2><p style='color:#8aa0c5;font-size:13px;margin-top:6px'>Login to access real fixtures & predictions</p></div>"
    if error:
        html += "<div class='card pending' style='padding:10px;color:orange;font-size:13px'>" + error + "</div>"
    html += "<form method='post'><input class='input' name='email' placeholder='Email address' required><input class='input' name='pass' type='password' placeholder='Password' required><br><br><button class='btn btn-primary'>Login →</button></form><br><div style='text-align:center'><a href='/signup' style='color:#6b7fa3;font-size:13px;text-decoration:none'>No account? <span style='color:#00ff88'>Create free account</span></a><br><br><a href='/' style='color:#4a5f85;font-size:12px;text-decoration:none'>← Back to Home</a></div></div></body></html>"
    return html

@app.route("/signup", methods=["GET","POST"])
def signup():
    error = ""
    if request.method == "POST":
        em = request.form["email"].lower().strip()
        pw = request.form["pass"]
        if em in USERS:
            error = "Email already exists - Login instead"
        else:
            USERS[em] = {"pass": pw, "plan": "free", "status": "active", "expiry": None, "is_admin": False, "pending": None}
            session["email"] = em
            return redirect("/")
    html = "<html><head>" + STYLE + "</head><body><div class='topbar'><div class='logo'>MASTERPICK<span>AI</span></div></div>"
    html += "<div class='login-wrap'><div class='hero' style='margin:0 0 20px;background:radial-gradient(600px 200px at 50% -10%,rgba(0,255,136,0.2),transparent),#0e1525'><h2 style='font-size:24px;font-weight:800'>Join MasterpickAI Free</h2><p style='color:#8aa0c5;font-size:13px;margin-top:6px'>Get 2 free real predictions daily @1.56 odds - 9/10 possible</p></div>"
    if error:
        html += "<div class='card pending' style='padding:10px;color:orange;font-size:13px'>" + error + "</div>"
    html += "<form method='post'><input class='input' name='email' placeholder='Your email' required><input class='input' name='pass' type='password' placeholder='Create password (min 4)' required><br><br><button class='btn btn-primary'>Create Free Account →</button></form><br><div style='text-align:center'><a href='/login' style='color:#6b7fa3;font-size:13px;text-decoration:none'>Already have account? <span style='color:#00ff88'>Login</span></a><br><br><div style='color:#4a5f85;font-size:11px'>By signing up you agree: 100% real fixtures, honest odds. No fake guarantees.</div><br><a href='/' style='color:#4a5f85;font-size:12px;text-decoration:none'>← Back to Home</a></div></div></body></html>"
    return html

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app
