import os, requests
from datetime import datetime, timedelta
from flask import Flask, request, redirect, session

app = Flask(__name__)
app.secret_key = "masterpick_secure_final"
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
        fixtures = []
        for f in r.get("response", [])[:6]:
            home = f["teams"]["home"]["name"]
            away = f["teams"]["away"]["name"]
            league = f["league"]["name"]
            fixtures.append(home + " vs " + away + " - " + league + " - Over 0.5 @1.25")
        return fixtures
    except Exception as ex:
        print(ex)
        return []

@app.route("/")
def home():
    email = session.get("email")
    user = USERS.get(email) if email else None
    fixtures = get_fixtures()

    html = "<html><body style='background:#0a0e13;color:#fff;font-family:sans-serif;padding:15px'>"
    html += "<h2>MasterpickAI V10.2 REAL</h2>"

    if not email:
        html += "<a href='/login'>Login</a> | <a href='/signup'>Signup</a><br><br>"
        html += "<p>100 percent real fixtures. No fake games.</p>"
    else:
        html += "<p>" + email + " | " + user["plan"] + " | " + user["status"] + "<br>"
        html += "<a href='/logout'>Logout</a> | <a href='/admin'>Admin</a> | <a href='/plans'>Plans</a></p>"

        if user["status"] == "pending":
            html += "<div style='background:orange;color:#000;padding:12px;border-radius:8px'>PENDING APPROVAL<br>You paid N" + str(user["pending"]) + ". Wait for admin to check Opay 09079789177</div>"

        html += "<h3>FREE 2 games @1.56 - 9/10</h3>"
        if fixtures:
            for f in fixtures[:2]:
                html += "<div style='background:#1a242f;padding:10px;margin:8px 0;border-radius:8px;border-left:4px solid #00ff88'>" + f + "</div>"
        else:
            html += "<div style='background:#1a242f;padding:10px'>No real games today - No fake policy - Check tomorrow 12AM</div>"

        html += "<h3>PRO 6 games @4.8 - 6-7/10 honest</h3>"
        if user["plan"] == "pro" and user["status"] == "active":
            if fixtures:
                for f in fixtures:
                    html += "<div style='background:#1a242f;padding:10px;margin:8px 0;border-left:4px solid gold'>" + f + "</div>"
            else:
                html += "<p>No games today</p>"
        else:
            html += "<div style='background:#222;padding:10px'><p>LOCKED - Pay first</p><a href='/plans'>View Plans</a></div>"

    html += "</body></html>"
    return html

@app.route("/plans")
def plans():
    html = "<html><body style='background:#0a0e13;color:#fff;padding:15px'>"
    html += "<h2>Pay to Opay 09079789177 - Arinze Chukwuemeka Peter</h2>"
    html += "<a href='/subscribe/1000'>N1000 3Days I Paid</a><br><br>"
    html += "<a href='/subscribe/2000'>N2000 7Days</a><br><br>"
    html += "<a href='/subscribe/5000'>N5000 15Days</a><br><br>"
    html += "<a href='/subscribe/10000'>N10000 25Days</a><br><br>"
    html += "<a href='/subscribe/15000'>N15000 30Days</a><br><br>"
    html += "<a href='/'>Home</a></body></html>"
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
        return "Not admin <a href='/'>Home</a>"
    html = "<html><body style='background:#0a0e13;color:#fff;padding:15px'><h2>Admin Panel</h2><h3>Pending</h3>"
    for em, u in USERS.items():
        if u["status"] == "pending":
            html += em + " - N" + str(u["pending"]) + " <a href='/admin/approve/" + em + "'>APPROVE</a> | <a href='/admin/reject/" + em + "'>REJECT</a><br><br>"
    html += "<h3>All Users</h3>"
    for em, u in USERS.items():
        html += em + " - " + u["plan"] + " - " + u["status"] + "<br>"
    html += "<br><a href='/'>Home</a></body></html>"
    return html

@app.route("/admin/approve/<path:email>")
def approve(email):
    admin_email = session.get("email")
    if not admin_email or not USERS.get(admin_email, {}).get("is_admin"):
        return "Not admin"
    days_map = {"1000": 3, "2000": 7, "5000": 15, "10000": 25, "15000": 30}
    pending = USERS[email].get("pending", "1000")
    USERS[email]["status"] = "active"
    USERS[email]["plan"] = "pro"
    USERS[email]["expiry"] = datetime.now() + timedelta(days=days_map.get(pending, 3))
    USERS[email]["pending"] = None
    return redirect("/admin")

@app.route("/admin/reject/<path:email>")
def reject(email):
    USERS[email]["status"] = "free"
    USERS[email]["pending"] = None
    return redirect("/admin")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        em = request.form["email"].lower().strip()
        pw = request.form["pass"]
        if em in USERS and USERS[em]["pass"] == pw:
            session["email"] = em
            return redirect("/")
        return "Wrong password <a href='/login'>Retry</a>"
    return "<form method='post'><input name='email' placeholder='email'><input name='pass' type='password' placeholder='pass'><button>Login</button></form>"

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        em = request.form["email"].lower().strip()
        pw = request.form["pass"]
        if em in USERS:
            return "Exists <a href='/login'>Login</a>"
        USERS[em] = {"pass": pw, "plan": "free", "status": "active", "expiry": None, "is_admin": False, "pending": None}
        session["email"] = em
        return redirect("/")
    return "<form method='post'><input name='email' placeholder='email'><input name='pass' type='password' placeholder='pass'><button>Signup</button></form>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
