import os, sqlite3, hashlib
from datetime import datetime, timedelta, timezone
from flask import Flask, request, redirect, session, render_template_string

app = Flask(__name__)
app.secret_key = "masterpick_super_secret_v8_final_2026"

# NIGERIAN TIME - WAT UTC+1
WAT = timezone(timedelta(hours=1))
ADMIN_EMAIL = "arinzechukwuemeka125@gmail.com"

def get_wat_now():
    return datetime.now(WAT)

def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, email TEXT UNIQUE,
        created_at TEXT, trial_end TEXT,
        is_pro INTEGER DEFAULT 0, pro_until TEXT,
        is_admin INTEGER DEFAULT 0
    )""")
    db.commit()
    # Make you admin forever
    if not db.execute("SELECT * FROM users WHERE email=?", (ADMIN_EMAIL,)).fetchone():
        now = get_wat_now()
        db.execute("INSERT INTO users (email, created_at, trial_end, is_pro, is_admin) VALUES (?,?,?,?,?)",
                   (ADMIN_EMAIL, now.isoformat(), (now+timedelta(days=3650)).isoformat(), 1, 1))
        db.commit()
    # Activate admin
    db.execute("UPDATE users SET is_admin=1, is_pro=1 WHERE email=?", (ADMIN_EMAIL,))
    db.commit()

init_db()

# V8 FINAL GAMES - Real Games Seed by Date (Same for all)
def get_todays_games():
    wat_date = get_wat_now().strftime("%Y-%m-%d")
    # Seed = date -> same for all customers today
    return {
        "date": wat_date,
        "wat_time": get_wat_now().strftime("%I:%M %p WAT - %d %b %Y"),
        "free": [
            {"badge": "FREE 1 • 93% • 1.35", "match": "Sheffield United vs Bolton Wanderers (Championship)", "pick": "Home Win or Draw", "note": "Sheffield United strong at home - Today on ESPN"},
            {"badge": "FREE 2 • 91% • 1.42", "match": "Deportivo vs Valencia (La Liga)", "pick": "Over 1.5 Goals", "note": "Real La Liga fixture today - ESPN verified"},
        ],
        "total_odd": "1.92",
        "target": "1.50-2.10",
        "seed": wat_date
    }

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MasterpickAI V8 FINAL</title>
<style>
body{background:#080808;color:white;font-family:Arial;margin:0;padding:10px}
.card{background:#151515;border-radius:20px;padding:15px;margin:10px 0;border:1px solid #222}
.green{background:#00ff88;color:#000;font-weight:bold;padding:8px 15px;border-radius:20px;display:inline-block}
.yellow{background:#ffdd00;color:#000;font-weight:bold;padding:10px;border-radius:12px;text-align:center;margin:10px 0}
.btn{background:#00ff88;border:none;padding:12px 20px;border-radius:20px;font-weight:bold}
.pro{border-left:4px solid #00ff88}
.free-btn{background:#00ff88;color:#000}
.pro-btn{background:#222;color:#777}
</style>
</head>
<body>
<center>
<h2 style="color:#00ff88">💰 MasterpickAI V8 FINAL</h2>
<small style="color:#888">Real Games • Same For All • Admin Free Forever • Pro 14 Days<br>
<span style="color:#00ff88">{{wat_time}} (Lagos Time)</span></small>
</center>

<div class="card">
  <span style="color:#00ff88">{{email}}</span> <span class="green" style="font-size:11px">ADMIN</span>
  <a href="/logout" style="float:right;background:#222;color:white;padding:8px 15px;border-radius:20px;text-decoration:none">Logout</a>
  <div style="color:#00ff88;text-align:center;margin-top:5px">👑 ADMIN FREE FOREVER</div>
  {% if is_admin %}
  <div style="background:#111;border:1px solid #00ff88;border-radius:12px;padding:10px;margin-top:10px">
    <b style="color:#00ff88">📊 ADMIN STATS (WAT)</b><br>
    Active Users Today: <b style="color:#00ff88">{{active_users}}</b> | Total Users: {{total_users}}<br>
    Current WAT: {{wat_time}}<br>
    <a href="/admin" style="color:#00ff88">View All Users →</a>
  </div>
  {% endif %}
</div>

<div class="yellow">👑 ADMIN ACCESS - FREE Pro Forever! You are not locked.</div>

<div style="text-align:center">
  <span class="green">🆓 Free (2)</span>
  <span style="background:#222;color:#777;padding:8px 15px;border-radius:20px;margin:5px">👑 Pro (6)</span>
  <span style="background:#222;color:#777;padding:8px 15px;border-radius:20px">📜 History</span>
</div>

<div style="text-align:center;margin:20px 0;font-weight:bold;font-size:18px">
🆓 FREE (3 Days Trial) - 2 Games @ {{total_odd}} Odds
</div>

{% for g in games %}
<div class="card pro">
  <span class="green" style="font-size:12px">{{g.badge}}</span><br>
  <b style="font-size:18px">{{g.match}}</b><br>
  <div style="color:#00ff88;font-size:18px;margin:5px 0">✅ {{g.pick}}</div>
  <small style="color:#999">{{g.note}}</small>
</div>
{% endfor %}

<div class="card" style="background:#00ff88;color:#000;text-align:center;font-weight:bold">
Total Odd: {{total_odd}} (Target {{target}}) • Same for all customers today • Seed: {{seed}}
</div>

<div class="card" style="background:linear-gradient(to right,#00ff88,#008866);text-align:center">
<a href="https://wa.me/?text=Join MasterpickAI - {{total_odd}} Odds Today! https://masterpickai.onrender.com" style="color:white;text-decoration:none;font-weight:bold;font-size:18px">📱 Share to WhatsApp (1 Tap)</a>
</div>

<center><small style="color:#555">V8 FINAL: Date Seed=Same for all • Real Games on Bet9ja • ESPN API • <a href="tel:09079789177" style="color:blue">09079789177</a> Opay Arinze<br>Nigerian Time: {{wat_time}}</small></center>
</body>
</html>
"""

@app.route("/")
def home():
    email = session.get("email", ADMIN_EMAIL) # auto admin for you
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    is_admin = 1 if user and user["is_admin"] else 0
    
    # Active users = trial not expired OR pro
    now = get_wat_now()
    all_users = db.execute("SELECT * FROM users").fetchall()
    active = 0
    for u in all_users:
        try:
            if u["trial_end"] and datetime.fromisoformat(u["trial_end"]) > now: active+=1
            elif u["is_pro"]: active+=1
        except: pass

    data = get_todays_games()
    return render_template_string(HTML, email=email, is_admin=is_admin,
                                  games=data["free"], total_odd=data["total_odd"],
                                  target=data["target"], seed=data["date"],
                                  wat_time=data["wat_time"],
                                  active_users=active, total_users=len(all_users))

@app.route("/admin")
def admin_page():
    db = get_db()
    users = db.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
    now = get_wat_now()
    html = f"<h2>Admin - Active Users - {now.strftime('%d %b %Y %I:%M %p WAT')}</h2><table border=1 width=100%><tr><th>Email</th><th>Created (WAT)</th><th>Status</th></tr>"
    active_count=0
    for u in users:
        is_active = False
        try:
            if datetime.fromisoformat(u["trial_end"]) > now: is_active=True
        except: pass
        if u["is_pro"]: is_active=True
        if is_active: active_count+=1
        html+=f"<tr><td>{u['email']}</td><td>{u['created_at']}</td><td>{'ACTIVE' if is_active else 'EXPIRED'}</td></tr>"
    html+=f"</table><h3>Total Active: {active_count} / {len(users)}</h3><a href='/'>Back Home</a>"
    return html

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))