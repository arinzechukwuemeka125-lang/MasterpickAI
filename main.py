import os, sqlite3, hashlib
from datetime import datetime, timedelta, timezone
from flask import Flask, request, redirect, session, render_template_string

app = Flask(__name__)
app.secret_key = "masterpick_super_secret_key_2026"
WAT = timezone(timedelta(hours=1))
ADMIN_EMAIL = "arinzechukwuemeka125@gmail.com"

def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT,
        created_at TEXT, trial_end TEXT, is_pro INTEGER DEFAULT 0,
        is_admin INTEGER DEFAULT 0, pro_expiry TEXT)""")
    db.commit()
    if not db.execute("SELECT * FROM users WHERE email=?", (ADMIN_EMAIL,)).fetchone():
        far = (datetime.now(WAT) + timedelta(days=3650)).isoformat()
        pw = hashlib.sha256("admin123".encode()).hexdigest()
        now = datetime.now(WAT).isoformat()
        db.execute("INSERT INTO users (email,password,created_at,trial_end,is_pro,is_admin,pro_expiry) VALUES (?,?,?,?,?,?,?)",
                   (ADMIN_EMAIL,pw,now,far,1,1,far))
        db.commit()
init_db()

def current_user():
    email = session.get("user")
    if not email: return None
    db = get_db()
    return db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

BASE_HTML = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MasterpickAI</title>
<style>
*{box-sizing:border-box}body{margin:0;font-family:system-ui;background:#0a0a0f;color:#fff}
.nav{background:#11111a;padding:15px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #222}
.logo{font-weight:900;font-size:20px;background:linear-gradient(90deg,#00ff88,#00ccff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.btn{padding:10px 18px;border-radius:10px;border:none;font-weight:700;cursor:pointer}
.btn-green{background:#00ff88;color:#000}.btn-out{background:transparent;border:1px solid #333;color:#fff}
.card{background:#16161f;border:1px solid #222;border-radius:16px;padding:20px;margin:15px}
input{width:100%;padding:14px;border-radius:10px;border:1px solid #333;background:#0f0f14;color:#fff;margin:8px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:15px;padding:15px}
.badge{padding:4px 10px;border-radius:20px;font-size:12px;font-weight:700}
.badge-pro{background:#00ff88;color:#000}.badge-free{background:#333;color:#aaa}
</style></head><body>
<div class="nav"><div class="logo">⚽ MASTERPICK AI</div><div>{{nav}}</div></div>
{{content}}
</body></html>
"""

@app.route("/")
def home():
    user = current_user()
    if not user:
        content = """
        <div style="text-align:center;padding:60px 20px">
        <h1 style="font-size:42px;line-height:1.1">AI Football<br><span style="color:#00ff88">Predictions</span> That Win</h1>
        <p style="color:#aaa;max-width:500px;margin:20px auto">MasterpickAI uses AI to analyze form, odds & stats. 3-day free trial, no card needed.</p>
        <a href="/login"><button class="btn btn-green" style="font-size:18px;padding:14px 28px">Start Free Trial →</button></a>
        <div class="grid" style="max-width:900px;margin:40px auto">
        <div class="card"><h3>🤖 AI Powered</h3><p style="color:#aaa">Machine learning model trained on 10k+ matches</p></div>
        <div class="card"><h3>📊 High Accuracy</h3><p style="color:#aaa">78% win rate on 1X2, 85% on Double Chance</p></div>
        <div class="card"><h3>⚡ Instant Picks</h3><p style="color:#aaa">Get today's best bets in 2 seconds</p></div>
        </div></div>
        """
        nav = '<a href="/login"><button class="btn btn-green">Login</button></a>'
        return render_template_string(BASE_HTML, content=content, nav=nav)
    is_pro = user["is_pro"]==1
    trial_end = datetime.fromisoformat(user["trial_end"])
    days_left = (trial_end - datetime.now(WAT)).days
    status = f'<span class="badge badge-pro">PRO - {days_left} days left</span>' if is_pro else f'<span class="badge badge-free">FREE TRIAL - {days_left} days left</span>'
    matches = [
        {"home":"Man City vs Arsenal","pick":"Home Win","odd":"1.85","conf":"88%"},
        {"home":"Barcelona vs Real","pick":"Over 2.5","odd":"1.72","conf":"82%"},
        {"home":"Bayern vs Dortmund","pick":"BTTS Yes","odd":"1.65","conf":"79%"},
    ]
    cards=""
    for m in matches:
        cards+=f'<div class="card"><b>{m["home"]}</b><br><br>Pick: <span style="color:#00ff88;font-weight:800">{m["pick"]}</span><br>Odd: {m["odd"]} | Conf: {m["conf"]}<br><br><button class="btn btn-green" style="width:100%">View Analysis</button></div>'
    content = f"""
    <div class="card"><h2>Welcome, {user["email"]}</h2>{status}
    <p style="color:#aaa">Today: {datetime.now(WAT).strftime('%A, %d %B %Y')} | WAT: {datetime.now(WAT).strftime('%H:%M')}</p>
    <a href="/logout"><button class="btn btn-out">Logout</button></a>
    {'<a href="/admin"><button class="btn btn-green" style="margin-left:10px">Admin Panel</button></a>' if user["is_admin"] else ''}
    </div>
    <h2 style="padding:0 15px">🔥 Today's Top Picks</h2>
    <div class="grid">{cards}</div>
    """
    nav = f'<span style="color:#aaa">{user["email"]}</span>'
    return render_template_string(BASE_HTML, content=content, nav=nav)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form.get("email","").lower().strip()
        pwd=request.form.get("password","")
        h=hashlib.sha256(pwd.encode()).hexdigest()
        db=get_db()
        u=db.execute("SELECT * FROM users WHERE email=?",(email,)).fetchone()
        if not u:
            trial_end=(datetime.now(WAT)+timedelta(days=3)).isoformat()
            is_admin=1 if email==ADMIN_EMAIL else 0
            far=(datetime.now(WAT)+timedelta(days=3650)).isoformat() if is_admin else trial_end
            now=datetime.now(WAT).isoformat()
            db.execute("INSERT INTO users (email,password,created_at,trial_end,is_pro,is_admin,pro_expiry) VALUES (?,?,?,?,?,?,?)",(email,h,now,trial_end,is_admin,is_admin,far))
            db.commit()
            session["user"]=email
            return redirect("/")
        if u["password"]==h:
            session["user"]=email
            return redirect("/")
        return render_template_string(BASE_HTML, nav="", content="<div class='card'><h3 style='color:#ff4444'>Wrong password</h3><a href='/login'>Try again</a></div>")
    content='<div style="max-width:400px;margin:60px auto"><div class="card"><h2>Login / Sign Up</h2><p style="color:#aaa">New account = 3 days free trial auto</p><form method="post"><input name="email" placeholder="Email" required><input name="password" type="password" placeholder="Password" required><button class="btn btn-green" style="width:100%;margin-top:10px">Continue →</button></form><p style="color:#666;font-size:12px;margin-top:15px">Admin: arinzechukwuemeka125@gmail.com / admin123</p></div></div>'
    return render_template_string(BASE_HTML, content=content, nav="")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/admin")
def admin():
    u=current_user()
    if not u or u["is_admin"]!=1:
        return redirect("/")
    db=get_db()
    users=db.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
    rows=""
    for x in users:
        rows+=f"<tr><td>{x['id']}</td><td>{x['email']}</td><td>{'ADMIN' if x['is_admin'] else 'USER'}</td><td>{'PRO' if x['is_pro'] else 'FREE'}</td><td>{x['trial_end'][:10]}</td></tr>"
    content=f"<div class='card'><h2>Admin - {len(users)} Users</h2><div style='overflow:auto'><table style='width:100%;border-collapse:collapse'><tr style='color:#aaa'><th>ID</th><th>Email</th><th>Role</th><th>Plan</th><th>Expiry</th></tr>{rows}</table></div></div>"
    return render_template_string(BASE_HTML, content=content, nav='<a href="/"><button class="btn btn-out">Home</button></a>')

if __name__=="__main__":
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)