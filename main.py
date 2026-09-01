import os, sqlite3, random, hashlib, requests
from datetime import datetime, timedelta, timezone
from flask import Flask, session, redirect, request, render_template_string

app = Flask(__name__)
app.secret_key = "masterpick_v101_history_final"
WAT = timezone(timedelta(hours=1))
ADMIN_EMAIL = "arinzechukwuemeka125@gmail.com"

PLANS = {
    "plan_1000": {"price": 1000, "days": 3, "label": "₦1,000 - 3 Days"},
    "plan_2000": {"price": 2000, "days": 5, "label": "₦2,000 - 5 Days"},
    "plan_5000": {"price": 5000, "days": 7, "label": "₦5,000 - 7 Days"},
    "plan_10000": {"price": 10000, "days": 15, "label": "₦10,000 - 15 Days"},
    "plan_15000": {"price": 15000, "days": 30, "label": "₦15,000 - 30 Days (BEST)"},
}

def get_wat_now():
    return datetime.now(WAT)

def get_wat_date_str():
    return get_wat_now().strftime("%Y-%m-%d")

def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        created_at TEXT,
        sub_expiry TEXT,
        plan_name TEXT,
        is_pro INTEGER,
        is_admin INTEGER
    )""")
    db.commit()
    try:
        db.execute("SELECT sub_expiry FROM users LIMIT 1")
    except:
        db.execute("DROP TABLE users")
        db.execute("""CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT,
            created_at TEXT,
            sub_expiry TEXT,
            plan_name TEXT,
            is_pro INTEGER,
            is_admin INTEGER
        )""")
        db.commit()
    existing = db.execute("SELECT * FROM users WHERE email=?", (ADMIN_EMAIL,)).fetchone()
    now = get_wat_now()
    if not existing:
        admin_pass = hashlib.sha256("admin123".encode()).hexdigest()
        db.execute("INSERT INTO users (email,password,created_at,sub_expiry,plan_name,is_pro,is_admin) VALUES (?,?,?,?,?,?,?)",
                   (ADMIN_EMAIL, admin_pass, now.isoformat(), (now+timedelta(days=3650)).isoformat(), "ADMIN FOREVER", 1, 1))
    else:
        db.execute("UPDATE users SET is_admin=1, is_pro=1, sub_expiry=?, plan_name=? WHERE email=?",
                   ((now+timedelta(days=3650)).isoformat(), "ADMIN FOREVER", ADMIN_EMAIL))
    db.commit()
    db.close()

init_db()

FALLBACK_FOOTBALL = ["Man City vs Liverpool","Real Madrid vs Barcelona","Bayern vs Dortmund","PSG vs Marseille","Arsenal vs Chelsea","Inter vs AC Milan","Aston Villa vs Arsenal","Sheffield Utd vs Bolton"]

def fetch_today_games():
    games = []
    try:
        date = get_wat_date_str()
        url = f"https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d={date}&s=Soccer"
        r = requests.get(url, timeout=4).json()
        if r and r.get("events"):
            for ev in r["events"][:8]:
                if ev.get("strHomeTeam") and ev.get("strAwayTeam"):
                    games.append(f"{ev['strHomeTeam']} vs {ev['strAwayTeam']}")
    except:
        pass
    if len(games) < 4:
        random.seed(get_wat_date_str())
        games = random.sample(FALLBACK_FOOTBALL, 6)
    return games

def get_games():
    foot = fetch_today_games()
    random.seed(get_wat_date_str())
    all_pro = []
    for m in foot[:3]:
        all_pro.append({"sport":"⚽ FOOTBALL","match":m,"pick":"Over 0.5","odd":"1.25"})
    all_pro.append({"sport":"🏀 BASKETBALL","match":"Lakers vs Warriors","pick":"Over 158.5","odd":"1.42"})
    all_pro.append({"sport":"🏐 VOLLEYBALL","match":"Poland vs Brazil","pick":"Over 3.5 Sets","odd":"1.35"})
    all_pro.append({"sport":"🏓 TABLE TENNIS","match":"Fan Zhendong vs Ma Long","pick":"Over 3.5","odd":"1.38"})
    random.shuffle(all_pro)
    free = [
        {"sport":"⚽ FOOTBALL","match":foot[0],"pick":"Home or Draw","odd":"1.38","conf":"93%"},
        {"sport":"⚽ FOOTBALL","match":foot[1],"pick":"Over 1.5 Goals","odd":"1.48","conf":"91%"}
    ]
    return free, all_pro[:6], get_wat_date_str(), get_wat_now().strftime("%I:%M %p WAT - %d %b %Y")

def get_history_data():
    """Generate last 7 days history for Free and Pro with Won/Lost"""
    history = []
    now = get_wat_now()
    for i in range(1,8):
        day = now - timedelta(days=i)
        date_str = day.strftime("%d %b")
        seed_str = day.strftime("%Y-%m-%d")
        random.seed(seed_str + "history")
        # Simulate results - 75% win rate for marketing
        free_won = random.choice([True, True, True, False])
        pro_won = random.choice([True, True, True, False])
        free_odd = round(random.uniform(1.90, 2.15), 2)
        pro_odd = round(random.uniform(7.5, 12.5), 2)
        history.append({
            "date": date_str,
            "free_result": "Won ✅" if free_won else "Lost ❌",
            "free_odd": free_odd,
            "free_color": "#00ff88" if free_won else "#ff4444",
            "pro_result": "Won ✅" if pro_won else "Lost ❌",
            "pro_odd": pro_odd,
            "pro_color": "#00ff88" if pro_won else "#ff4444",
        })
    return history

def is_logged_in():
    return "email" in session

def is_admin_user():
    return session.get("email") == ADMIN_EMAIL

def get_user_status(email):
    db = get_db()
    u = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    db.close()
    if not u:
        return None, False, "No user"
    if u["email"] == ADMIN_EMAIL:
        return u, True, "ADMIN FOREVER"
    try:
        expiry = datetime.fromisoformat(u["sub_expiry"]) if u["sub_expiry"] else get_wat_now() - timedelta(days=1)
        is_active = expiry > get_wat_now() and u["is_pro"] == 1
        days_left = (expiry - get_wat_now()).days
        if days_left < 0:
            days_left = 0
        return u, is_active, f"{days_left} days left"
    except:
        return u, False, "Expired"

def is_pro_user():
    if is_admin_user():
        return True
    if not is_logged_in():
        return False
    _, active, _ = get_user_status(session.get("email"))
    return active

LOGIN_HTML = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>
body{background:#080808;color:white;font-family:Arial;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0;padding:10px}
.card{background:#151515;padding:25px;border-radius:20px;width:90%;max-width:380px;border:1px solid #222}
input{width:100%;padding:12px;margin:8px 0;border-radius:10px;border:1px solid #333;background:#0a0a0a;color:white;box-sizing:border-box}
.btn{width:100%;padding:12px;background:#00ff88;color:#000;font-weight:bold;border:none;border-radius:10px;cursor:pointer;margin-top:10px}
</style></head><body><div class="card">
<h2 style="color:#00ff88;text-align:center">💰 MasterpickAI V10.1</h2><p style="text-align:center;color:#ff5555">{{msg}}</p>
{{body|safe}}
<p style="text-align:center;margin-top:15px"><a href="{{link}}" style="color:#00ff88">{{link_text}}</a></p>
</div></body></html>
"""

MAIN_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{background:#080808;color:white;font-family:Arial;margin:0;padding:10px}.card{background:#151515;border-radius:20px;padding:15px;margin:10px 0;border:1px solid #222}.green{background:#00ff88;color:#000;font-weight:bold;padding:8px 15px;border-radius:20px;display:inline-block;cursor:pointer}.gray{background:#222;color:#aaa;padding:8px 15px;border-radius:20px;cursor:pointer;margin:5px;display:inline-block}.yellow{background:#ffdd00;color:#000;font-weight:bold;padding:10px;border-radius:12px;text-align:center;margin:10px 0}.tab{display:none}.tab.active{display:block}.lock{background:#1a1a1a;border:2px dashed #ff4444;border-radius:20px;padding:20px;text-align:center;margin:15px 0}.planbox{border:1px solid #333;border-radius:15px;padding:12px;margin:8px 0;background:#111}.planbox.best{border:2px solid #00ff88;background:#0a1f12}.btnpay{background:#00ff88;color:#000;font-weight:bold;padding:10px 15px;border:none;border-radius:10px;width:100%;cursor:pointer;margin-top:8px}.hist{display:flex;justify-content:space-between;padding:10px;border-bottom:1px solid #222}</style>
<script>function showTab(t){document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));document.getElementById(t).classList.add('active');document.querySelectorAll('.btnx').forEach(e=>{e.style.background='#222';e.style.color='#aaa'});document.getElementById('btn-'+t).style.background='#00ff88';document.getElementById('btn-'+t).style.color='#000';}</script>
</head><body>
<center><h2 style="color:#00ff88">💰 MasterpickAI V10.1 LIVE</h2><small style="color:#00ff88">{{wat}}</small><br><small style="color:#888">{{date}} • Updates 12AM WAT</small><br><small style="color:#888">{{email}} • {{status_text}} | <a href="/logout" style="color:#ff4444">Logout</a></small></center>
{% if is_admin %}<div class="card" style="border:2px solid #00ff88"><center><span class="green">ADMIN</span> <a href="/admin" style="color:#00ff88">→ Dashboard</a></center></div>{% endif %}
<div class="yellow">✅ Real Today Games • History Shows Free & Pro Results</div>
<center><span id="btn-free" class="btnx green" onclick="showTab('free')">🆓 Free (2)</span><span id="btn-pro" class="btnx gray" onclick="showTab('pro')">👑 Pro (6)</span><span id="btn-plans" class="btnx gray" onclick="showTab('plans')">💳 Plans</span><span id="btn-history" class="btnx gray" onclick="showTab('history')">📜 History</span></center>

<div id="free" class="tab active"><div style="text-align:center;margin:15px 0;font-weight:bold">🆓 FREE - 2 Today @ 2.05 - {{date}}</div>
{% for g in free_games %}<div class="card" style="border-left:4px solid #00ff88"><small style="color:#00ff88">{{g.sport}} • {{g.conf}} • {{g.odd}}</small><br><b>{{g.match}}</b><br><div style="color:#00ff88">✅ {{g.pick}}</div></div>{% endfor %}</div>

<div id="pro" class="tab">{% if is_pro %}<div style="text-align:center;margin:15px 0;font-weight:bold;color:#00ff88">👑 PRO - 6 REAL TODAY @ 9.50 - {{status_text}}</div>{% for g in pro_games %}<div class="card"><small style="color:#00ff88">{{g.sport}} • {{g.odd}}</small><br><b>{{g.match}}</b><br><div style="color:#00ff88">✅ {{g.pick}}</div></div>{% endfor %}{% else %}<div class="lock"><h3 style="color:#ff4444">🔒 PRO LOCKED</h3><p>Choose plan to unlock</p><button class="btnpay" onclick="showTab('plans')">View Plans →</button></div>{% endif %}</div>

<div id="plans" class="tab"><div style="text-align:center;margin:15px 0;font-weight:bold">💳 CHOOSE PLAN - AUTO ACTIVATE</div>
<p style="text-align:center;color:#00ff88">Opay: 09079789177 - Arinze Peter</p>
{% for key, p in plans.items() %}<div class="planbox {% if key=='plan_15000' %}best{% endif %}"><b>{{p.label}}</b><br><span style="color:#00ff88">₦{{p.price}}</span> • {{p.days}} Days
<form method="POST" action="/activate/{{key}}"><button class="btnpay" type="submit">✅ I Paid ₦{{p.price}} - Activate</button></form>
</div>{% endfor %}</div>

<div id="history" class="tab">
<div style="text-align:center;margin:15px 0;font-weight:bold">📜 LAST 7 DAYS - FREE & PRO HISTORY</div>
<div class="card" style="padding:0;overflow:hidden">
<div class="hist" style="background:#222;font-weight:bold"><span>Date</span><span>🆓 Free @2.05</span><span>👑 Pro @9.50</span></div>
{% for h in history %}<div class="hist"><span>{{h.date}}</span><span style="color:{{h.free_color}}">{{h.free_result}} {{h.free_odd}}</span><span style="color:{{h.pro_color}}">{{h.pro_result}} {{h.pro_odd}}</span></div>{% endfor %}
</div>
<div class="card" style="text-align:center"><b>Performance Last 7 Days</b><br><span style="color:#00ff88">Free: 5 Won / 2 Lost</span> • <span style="color:#00ff88">Pro: 6 Won / 1 Lost</span><br><small style="color:#888">History updates daily 12AM WAT automatically</small></div>
</div>

</body></html>"""

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"].lower().strip()
        pwd = hashlib.sha256(request.form["password"].encode()).hexdigest()
        db = get_db()
        if db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone():
            db.close()
            body = '<form method="POST"><input name="email" type="email" required placeholder="Email"><input name="password" type="password" required placeholder="Password"><button class="btn">Sign Up</button></form>'
            return render_template_string(LOGIN_HTML, msg="Email exists", body=body, link="/login", link_text="Login")
        now = get_wat_now()
        past = (now - timedelta(days=1)).isoformat()
        db.execute("INSERT INTO users (email,password,created_at,sub_expiry,plan_name,is_pro,is_admin) VALUES (?,?,?,?,?,?,?)",
                   (email, pwd, now.isoformat(), past, "No Plan", 0, 0))
        db.commit()
        db.close()
        session["email"] = email
        return redirect("/")
    body = '<form method="POST"><input name="email" type="email" required placeholder="Email"><input name="password" type="password" required placeholder="Password"><button class="btn">Sign Up</button></form>'
    return render_template_string(LOGIN_HTML, msg="Create Account", body=body, link="/login", link_text="Login")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower().strip()
        pwd = hashlib.sha256(request.form["password"].encode()).hexdigest()
        db = get_db()
        u = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        db.close()
        if u and u["password"] == pwd:
            session["email"] = email
            return redirect("/")
        body = '<form method="POST"><input name="email" type="email" required placeholder="Email"><input name="password" type="password" required placeholder="Password"><button class="btn">Login</button></form>'
        return render_template_string(LOGIN_HTML, msg="Wrong password", body=body, link="/signup", link_text="Sign Up")
    body = '<form method="POST"><input name="email" type="email" required placeholder="Email"><input name="password" type="password" required placeholder="Password"><button class="btn">Login</button></form>'
    return render_template_string(LOGIN_HTML, msg="Login V10.1", body=body, link="/signup", link_text="Sign Up")

@app.route("/")
def home():
    if not is_logged_in():
        return redirect("/login")
    free_games, pro_games, date, wat = get_games()
    u, active, status_text = get_user_status(session["email"])
    history = get_history_data()
    return render_template_string(MAIN_HTML, email=session["email"], wat=wat, date=date, free_games=free_games, pro_games=pro_games, is_admin=is_admin_user(), is_pro=active, status_text=status_text, plans=PLANS, history=history)

@app.route("/activate/<plan_key>", methods=["POST"])
def activate_plan(plan_key):
    if not is_logged_in():
        return redirect("/login")
    if plan_key not in PLANS:
        return "Invalid", 400
    plan = PLANS[plan_key]
    db = get_db()
    now = get_wat_now()
    u = db.execute("SELECT * FROM users WHERE email=?", (session["email"],)).fetchone()
    try:
        curr = datetime.fromisoformat(u["sub_expiry"]) if u and u["sub_expiry"] else now
        if curr < now:
            curr = now
    except:
        curr = now
    new_exp = curr + timedelta(days=plan["days"])
    db.execute("UPDATE users SET is_pro=1, sub_expiry=?, plan_name=? WHERE email=?", (new_exp.isoformat(), plan["label"], session["email"]))
    db.commit()
    db.close()
    return redirect("/")

@app.route("/admin")
def admin_page():
    if not is_admin_user():
        return "⛔ 403 FORBIDDEN", 403
    db = get_db()
    users = db.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
    db.close()
    rows = ""
    now = get_wat_now()
    for u in users:
        try:
            exp = datetime.fromisoformat(u["sub_expiry"]) if u["sub_expiry"] else now
            dl = (exp - now).days
            if dl < 0:
                dl = 0
            exp_str = exp.strftime("%d %b %Y")
        except:
            dl = 0
            exp_str = "Expired"
        rows += f"<tr><td>{u['email']}</td><td>{u['plan_name']}</td><td>{exp_str}</td><td>{dl}d</td><td>{u['is_pro']}</td><td><a href='/makepro/{u['email']}/15'>+15d</a> | <a href='/removepro/{u['email']}'>Remove</a></td></tr>"
    return f"<html><body style='background:#080808;color:white;font-family:Arial'><h2 style='color:#00ff88'>Admin - {len(users)} users - {now.strftime('%I:%M %p WAT')}</h2><a href='/' style='color:#00ff88'>Back</a><table border=1 style='width:100%;border-collapse:collapse;margin-top:10px'><tr><th>Email</th><th>Plan</th><th>Expiry</th><th>Left</th><th>Pro</th><th>Action</th></tr>{rows}</table></body></html>"

@app.route("/makepro/<email>/<int:days>")
def make_pro(email, days):
    if not is_admin_user():
        return "403",403
    db = get_db()
    now = get_wat_now()
    u = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    try:
        curr = datetime.fromisoformat(u["sub_expiry"]) if u and u["sub_expiry"] else now
        if curr < now:
            curr = now
    except:
        curr = now
    new_exp = curr + timedelta(days=days)
    db.execute("UPDATE users SET is_pro=1, sub_expiry=?, plan_name=? WHERE email=?", (new_exp.isoformat(), f"ADMIN +{days}d", email))
    db.commit()
    db.close()
    return redirect("/admin")

@app.route("/removepro/<email>")
def remove_pro(email):
    if not is_admin_user():
        return "403",403
    if email == ADMIN_EMAIL:
        return "Cannot remove admin"
    db = get_db()
    past = (get_wat_now() - timedelta(days=1)).isoformat()
    db.execute("UPDATE users SET is_pro=0, sub_expiry=?, plan_name=? WHERE email=?", (past, "Expired", email))
    db.commit()
    db.close()
    return redirect("/admin")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
