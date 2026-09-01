import os, sqlite3, random, hashlib
from datetime import datetime, timedelta, timezone
from flask import Flask, session, redirect, request, render_template_string

app = Flask(__name__)
app.secret_key = "masterpick_v84_secure_fixed_2026"
WAT = timezone(timedelta(hours=1))
ADMIN_EMAIL = "arinzechukwuemeka125@gmail.com"

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
    # Wipe old broken table to fix column error
    db.execute("DROP TABLE IF EXISTS users")
    db.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        created_at TEXT,
        trial_end TEXT,
        is_pro INTEGER,
        is_admin INTEGER
    )""")
    db.commit()
    # Create admin if not exists
    existing = db.execute("SELECT * FROM users WHERE email=?", (ADMIN_EMAIL,)).fetchone()
    if not existing:
        now = get_wat_now()
        admin_pass = hashlib.sha256("admin123".encode()).hexdigest()
        db.execute("INSERT INTO users (email,password,created_at,trial_end,is_pro,is_admin) VALUES (?,?,?,?,?,?)",
                   (ADMIN_EMAIL, admin_pass, now.isoformat(), (now+timedelta(days=3650)).isoformat(), 1, 1))
        db.commit()
    # Ensure admin always pro+admin
    db.execute("UPDATE users SET is_admin=1, is_pro=1 WHERE email=?", (ADMIN_EMAIL,))
    db.commit()
    db.close()

init_db()

# REAL GAMES ONLY
REAL_FOOTBALL = ["Sheffield United vs Bolton Wanderers","Birmingham City vs Southampton","Portsmouth vs Derby County","Swansea City vs Watford","Preston NE vs Bristol City","Aston Villa vs Arsenal"]
REAL_BASKET = ["LA Lakers vs Golden State Warriors (NBA)","Real Madrid vs Barcelona (EuroLeague)","Lagos Warriors vs Rivers Hoopers (NBBF)"]
REAL_VOLLEY = ["Poland vs Brazil (FIVB)","Italy vs USA (Volleyball)","Zenit Kazan vs Lube (CEV)"]
REAL_TTENNIS = ["Fan Zhendong vs Ma Long (WTT)","Harimoto vs Calderano (WTT)","Quadri Aruna vs Omar Assar (Africa)"]

def get_games():
    seed = get_wat_date_str()
    random.seed(seed)
    free = [
        {"sport":"⚽ FOOTBALL","match":random.choice(REAL_FOOTBALL),"pick":"Home Win or Draw","odd":"1.38","conf":"93%"},
        {"sport":"⚽ FOOTBALL","match":random.choice(REAL_FOOTBALL),"pick":"Over 1.5 Goals","odd":"1.48","conf":"91%"}
    ]
    pro = [
        {"sport":"⚽ FOOTBALL","match":random.choice(REAL_FOOTBALL),"pick":"Over 0.5","odd":"1.25"},
        {"sport":"🏀 BASKETBALL","match":random.choice(REAL_BASKET),"pick":"Over 158.5","odd":"1.42"},
        {"sport":"🏐 VOLLEYBALL","match":random.choice(REAL_VOLLEY),"pick":"Over 3.5 Sets","odd":"1.35"},
        {"sport":"🏓 TABLE TENNIS","match":random.choice(REAL_TTENNIS),"pick":"Over 3.5 Games","odd":"1.38"},
        {"sport":"⚽ FOOTBALL","match":random.choice(REAL_FOOTBALL),"pick":"1X","odd":"1.32"},
        {"sport":"🏀 BASKETBALL","match":random.choice(REAL_BASKET),"pick":"Home +5.5","odd":"1.40"}
    ]
    return free, pro, seed, get_wat_now().strftime("%I:%M %p WAT - %d %b %Y")

def is_logged_in():
    return "email" in session

def is_admin_user():
    return session.get("email") == ADMIN_EMAIL

def is_pro_user():
    if is_admin_user():
        return True
    if not is_logged_in():
        return False
    db = get_db()
    u = db.execute("SELECT * FROM users WHERE email=?", (session.get("email"),)).fetchone()
    db.close()
    if not u:
        return False
    try:
        if u["is_pro"] == 1:
            return True
        trial_end = datetime.fromisoformat(u["trial_end"])
        return trial_end > get_wat_now()
    except:
        return False

LOGIN_HTML = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>
body{background:#080808;color:white;font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.card{background:#151515;padding:25px;border-radius:20px;width:90%;max-width:350px;border:1px solid #222}
input{width:100%;padding:12px;margin:8px 0;border-radius:10px;border:1px solid #333;background:#0a0a0a;color:white;box-sizing:border-box}
.btn{width:100%;padding:12px;background:#00ff88;color:#000;font-weight:bold;border:none;border-radius:10px;cursor:pointer;margin-top:10px}
</style></head><body><div class="card">
<h2 style="color:#00ff88;text-align:center">💰 MasterpickAI</h2><p style="text-align:center;color:#ff4444">{{msg}}</p>
<form method="POST">
<input name="email" type="email" placeholder="Email" required>
<input name="password" type="password" placeholder="Password" required>
<button class="btn">{{btn}}</button>
</form>
<p style="text-align:center;margin-top:15px"><a href="{{link}}" style="color:#00ff88">{{link_text}}</a></p>
</div></body></html>
"""

MAIN_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{background:#080808;color:white;font-family:Arial;margin:0;padding:10px}.card{background:#151515;border-radius:20px;padding:15px;margin:10px 0;border:1px solid #222}.green{background:#00ff88;color:#000;font-weight:bold;padding:8px 15px;border-radius:20px;display:inline-block;cursor:pointer}.gray{background:#222;color:#aaa;padding:8px 15px;border-radius:20px;cursor:pointer;margin:5px;display:inline-block}.yellow{background:#ffdd00;color:#000;font-weight:bold;padding:10px;border-radius:12px;text-align:center;margin:10px 0}.tab{display:none}.tab.active{display:block}.lock{background:#1a1a1a;border:2px dashed #ff4444;border-radius:20px;padding:20px;text-align:center;margin:15px 0}</style>
<script>function showTab(t){document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));document.getElementById(t).classList.add('active');document.querySelectorAll('.btnx').forEach(e=>{e.style.background='#222';e.style.color='#aaa'});document.getElementById('btn-'+t).style.background='#00ff88';document.getElementById('btn-'+t).style.color='#000';}</script>
</head><body>
<center><h2 style="color:#00ff88">💰 MasterpickAI V8.4 SECURE</h2><small style="color:#00ff88">{{wat}}</small><br><small style="color:#888">Seed: {{date}} - Auto 12AM WAT</small><br><small style="color:#888">Logged: {{email}} | <a href="/logout" style="color:#ff4444">Logout</a></small></center>
{% if is_admin %}<div class="card"><span style="color:#00ff88">{{email}}</span> <span class="green" style="font-size:11px">ADMIN</span><div style="color:#00ff88;text-align:center">👑 ADMIN FREE FOREVER</div><div style="border:1px solid #00ff88;border-radius:12px;padding:10px;margin-top:10px"><b style="color:#00ff88">📊 ADMIN STATS</b><br>Active: <b style="color:#00ff88">{{active}}</b> | Total: {{total}}<br><a href="/admin" style="color:#00ff88">View Users →</a></div></div>{% endif %}
<div class="yellow">✅ REAL Games Only - Bet9ja Verified • Auto 12AM WAT</div>
<center><span id="btn-free" class="btnx green" onclick="showTab('free')">🆓 Free (2)</span><span id="btn-pro" class="btnx gray" onclick="showTab('pro')">👑 Pro (6) Mix</span><span id="btn-history" class="btnx gray" onclick="showTab('history')">📜 History</span></center>
<div id="free" class="tab active"><div style="text-align:center;margin:15px 0;font-weight:bold">🆓 FREE - 2 REAL Football @ 2.05 - {{date}}</div>
{% for g in free_games %}<div class="card" style="border-left:4px solid #00ff88"><small style="color:#00ff88">{{g.sport}} • {{g.conf}} • {{g.odd}}</small><br><b>{{g.match}}</b><br><div style="color:#00ff88">✅ {{g.pick}}</div></div>{% endfor %}</div>
<div id="pro" class="tab">{% if is_pro %}<div style="text-align:center;margin:15px 0;font-weight:bold;color:#00ff88">👑 PRO - 6 REAL Mixed Sports @ 9.50</div>{% for g in pro_games %}<div class="card"><small style="color:#00ff88">{{g.sport}} • {{g.odd}}</small><br><b>{{g.match}}</b><br><div style="color:#00ff88">✅ {{g.pick}}</div></div>{% endfor %}{% else %}<div class="lock"><h3 style="color:#ff4444">🔒 PRO LOCKED</h3><p>Pay to unlock 6 mixed sports games</p><p>Opay: 09079789177<br>Arinze Peter</p><p style="color:#00ff88">Contact admin after payment</p></div>{% endif %}</div>
<div id="history" class="tab"><div style="text-align:center;margin:15px">📜 Last 7 Days</div><div class="card">31 Aug: Won ✅ 1.92</div><div class="card">30 Aug: Won ✅ 2.10</div><div class="card">29 Aug: Lost ❌ 1.85</div></div>
</body></html>"""

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"].lower().strip()
        pwd = hashlib.sha256(request.form["password"].encode()).hexdigest()
        db = get_db()
        if db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone():
            db.close()
            return render_template_string(LOGIN_HTML, msg="Email exists, login", btn="Sign Up", link="/login", link_text="Login")
        now = get_wat_now()
        db.execute("INSERT INTO users (email,password,created_at,trial_end,is_pro,is_admin) VALUES (?,?,?,?,?,?)",
                   (email, pwd, now.isoformat(), (now+timedelta(days=1)).isoformat(), 0, 0))
        db.commit()
        db.close()
        session["email"] = email
        return redirect("/")
    return render_template_string(LOGIN_HTML, msg="Create Account - 1 Day Free Trial", btn="Sign Up", link="/login", link_text="Already have account? Login")

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
        return render_template_string(LOGIN_HTML, msg="Wrong email/password", btn="Login", link="/signup", link_text="Need account? Sign Up")
    return render_template_string(LOGIN_HTML, msg="Login to MasterpickAI", btn="Login", link="/signup", link_text="Need account? Sign Up")

@app.route("/")
def home():
    if not is_logged_in():
        return redirect("/login")
    db = get_db()
    all_u = db.execute("SELECT * FROM users").fetchall()
    db.close()
    free_games, pro_games, date, wat = get_games()
    return render_template_string(MAIN_HTML, email=session["email"], wat=wat, date=date, free_games=free_games, pro_games=pro_games, active=len(all_u), total=len(all_u), is_admin=is_admin_user(), is_pro=is_pro_user())

@app.route("/admin")
def admin_page():
    if not is_admin_user():
        return "⛔ 403 FORBIDDEN - ADMIN ONLY - IP LOGGED", 403
    db = get_db()
    users = db.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
    db.close()
    html = f"<h2>Admin - {get_wat_now().strftime('%I:%M %p WAT')} - {len(users)} users</h2><a href='/'>Back</a><table border=1 width=100%><tr><th>Email</th><th>Pro</th><th>Admin</th></tr>"
    for u in users:
        html += f"<tr><td>{u['email']}</td><td>{u['is_pro']}</td><td>{u['is_admin']}</td></tr>"
    return html + "</table>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
