import os, sqlite3, hashlib
from datetime import datetime, timedelta, timezone
from flask import Flask, request, redirect, session, render_template_string

app = Flask(__name__)
app.secret_key = "v9_4_1_final_live"
WAT = timezone(timedelta(hours=1))
ADMIN_EMAIL = "arinzechukwuemeka125@gmail.com"
DB = "users.db"

def get_db():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT, created_at TEXT, trial_end TEXT, is_pro INTEGER DEFAULT 0, is_admin INTEGER DEFAULT 0, pro_expiry TEXT)""")
    db.commit()
    if not db.execute("SELECT * FROM users WHERE email=?", (ADMIN_EMAIL,)).fetchone():
        far = (datetime.now(WAT)+timedelta(days=3650)).isoformat()
        db.execute("INSERT INTO users VALUES (NULL,?,?,?,?,?,?,?)",(ADMIN_EMAIL, hashlib.sha256("admin123".encode()).hexdigest(), datetime.now(WAT).isoformat(), far, 1, 1, far))
        db.commit()

def get_games():
    now_wat = datetime.now(WAT)
    today = now_wat.date()
    seed = f"{today}-12AM-WAT-V9.4.1-SAFE"
    games = [
        ("Arsenal vs Brentford","Over 1.5 Goals","92%","Football","1.28","PL - Over 1.5"),
        ("Man City vs Luton","Double Chance 1X","93%","Football","1.25","PL - Double Chance"),
        ("Barcelona vs Sevilla","Over 0.5 Goals","94%","Football","1.18","La Liga - Over 0.5"),
        ("Real Madrid vs Getafe","Handicap +1 Home","89%","Football","1.35","La Liga - Handicap"),
        ("Inter vs Napoli","Double Chance X2","88%","Football","1.32","Serie A - Double Chance"),
        ("Bayern vs Dortmund","Under 3.5 Goals","87%","Football","1.40","Bundesliga - Under 3.5"),
        ("Djokovic vs Alcaraz","Over 18.5 Games","90%","Tennis","1.30","ATP - Over"),
        ("Lakers vs Warriors","Over 200.5 Points","88%","Basketball","1.32","NBA - Over"),
        ("Italy vs Brazil","Over 2.5 Sets","85%","Volleyball","1.38","Nations - Over"),
        ("Poland vs USA","Double Chance 1X","86%","Volleyball","1.30","Nations - Double Chance"),
        ("Swiatek vs Sabalenka","Handicap +2.5 Games","89%","Tennis","1.35","WTA - Handicap"),
        ("Celtics vs Bucks","Under 2.5 Sets Handicap","87%","Basketball","1.30","NBA - Handicap +5.5"),
    ]
    import hashlib as hl
    return today, sorted(games, key=lambda x: hl.md5((seed+x[0]).encode()).hexdigest())[:8], now_wat.strftime("%Y-%m-%d %H:%M:%S WAT")

def get_countdown(s):
    try:
        e = datetime.fromisoformat(s); d = e - datetime.now(WAT)
        if d.total_seconds()<=0: return "EXPIRED"
        return f"{d.days}d {d.seconds//3600}h {(d.seconds%3600)//60}m left" if d.days>0 else f"{d.seconds//3600}h {(d.seconds%3600)//60}m left"
    except: return "Active"

init_db()
BASE="""<!DOCTYPE html><html><head><meta name=viewport content="width=device-width,initial-scale=1"><title>MasterpickAI LIVE</title><style>body{margin:0;background:#0a0a0a;color:#fff;font-family:Arial}.header{background:#00ff88;color:#000;padding:14px;text-align:center;font-weight:bold;font-size:18px}.sub{background:#1a1a1a;padding:8px;text-align:center;color:#00ff88;font-size:11px}.card{background:#1a1a1a;margin:10px;padding:14px;border-radius:12px;border-left:4px solid #00ff88}.card.football{border-left-color:#00ff88}.card.tennis{border-left-color:#ffaa00}.card.basketball{border-left-color:#ff4444}.card.volleyball{border-left-color:#00aaff}.sport-tag{font-size:9px;padding:2px 6px;border-radius:10px;color:#000;font-weight:bold;float:right}.sport-football{background:#00ff88}.sport-tennis{background:#ffaa00}.sport-basketball{background:#ff4444;color:#fff}.sport-volleyball{background:#00aaff;color:#fff}.badge{background:#00ff88;color:#000;padding:4px 8px;border-radius:6px;font-size:11px;font-weight:bold}.badge-pro{background:#ffaa00;color:#000}.btn{background:#00ff88;color:#000;padding:12px 18px;border-radius:8px;display:inline-block;font-weight:bold;border:0;margin:5px;font-size:13px;text-decoration:none}.btn-pay{background:#ffaa00;color:#000;width:90%;text-align:center;padding:14px;border-radius:8px;display:block;margin:8px auto;font-weight:bold;text-decoration:none}.countdown{background:#ffaa00;color:#000;padding:6px 12px;border-radius:20px;font-weight:bold;display:inline-block;margin:8px 0}</style></head><body><div class=header>⚽🎾🏀🏐 MasterpickAI LIVE - ULTRA SAFE</div><div class=sub>Seed: {{today}} • WAT: {{now}} • {{admin_status}} • 12:00 AM WAT Update</div>{{content}}</body></html>"""

@app.route("/")
def home():
    today,games,now_full=get_games(); now=datetime.now(WAT); email=session.get("user"); is_pro=False; is_admin=False; cd=""; exp_str=""
    if email:
        u=get_db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if u: is_admin=bool(u["is_admin"]); exp_str=u["pro_expiry"]; pe=datetime.fromisoformat(exp_str) if exp_str else now; is_pro=now<pe or is_admin; cd=get_countdown(exp_str) if not is_admin else "ADMIN FOREVER"
    free=games[:2]; pro=games[2:]; admin_status=f"{email} 👑 ADMIN" if is_admin else f"{email} • PRO • {cd}" if is_pro and email else f"{email} • FREE" if email else "Guest - Ultra Safe"
    content=""
    if email and is_pro: content+=f"""<div style="text-align:center"><div class=countdown>⏰ {cd}</div><p style="font-size:11px;color:#888">Expires: {exp_str[:16] if not is_admin else 'Never'} WAT</p></div>"""
    def render(n,p,c,s,o,l,pro_c=False):
        sc=s.lower()
        return f"""<div class="card {sc}"><b>{n}</b> <span class="sport-tag sport-{sc}">{s.upper()}</span><br><small style="color:#888">{l}</small><span style="float:right;color:#00ff88">{o}</span><br>Tip: <span class="{'badge-pro' if pro_c else 'badge'}">{p} - {c}</span></div>"""
    for g in free: content+=render(*g,False)
    if is_pro or is_admin:
        content+=f"""<div style="text-align:center;margin:10px"><span class=badge-pro>🔓 PRO UNLOCKED - {cd}</span><br><small>Double Chance • Over 0.5/1.5 • Under 2.5/3.5 • Handicap</small></div>"""
        for g in pro: content+=render(*g,True)
    else:
        content+=f"""<div class="card" style="text-align:center;border-left-color:#ffaa00"><h3>🔒 {len(pro)} ULTRA SAFE Games Locked</h3><p>Double Chance • Over 1.5 • Under 2.5 • Handicap +1<br>Football + Tennis + Basketball + Volleyball<br>All on Bet9ja/1xBet/SportyBet</p><p style="background:#222;padding:10px;border-radius:8px"><b>Opay/PalmPay:</b> 9079783177<br>Arinze Chukwuemeka Peter</p><a class=btn-pay href='/pay/3'>💰 I Paid ₦500 - 3 Days</a><a class=btn-pay href='/pay/7'>💰 I Paid ₦1000 - 7 Days</a><a class=btn-pay href='/pay/14' style="background:#00ff88">💰 I Paid ₦1977 - 14 Days BEST</a><p style="font-size:11px;color:#888">Tap after payment - PRO opens instantly • Updates 12:00 AM WAT</p><a class=btn href='https://wa.me/2349079783177' style="background:#222;color:#00ff88;border:1px solid #00ff88">📱 WhatsApp Proof</a></div>"""
    if is_admin: content+=f"<div style='text-align:center;padding:15px'><a class=btn href='/admin/users'>👑 ADMIN DASHBOARD - {len(games)} Games • See Active Users</a></div>"
    elif not email: content=f"<div style='text-align:center;padding:25px'><h3>Welcome - Ultra Safe AI</h3><p>Double Chance • Over 1.5 • Under 2.5 • Handicap<br>⚽🎾🏀🏐 Multi-Sport • 3 Days FREE<br><small>Updates 12:00 AM WAT</small></p><a class=btn href='/login'>Login / Signup</a></div>"+content
    return render_template_string(BASE, today=today, now=now_full, admin_status=admin_status, content=content)

@app.route("/pay/<int:days>")
def pay(days):
    if "user" not in session: return redirect("/login")
    expiry=(datetime.now(WAT)+timedelta(days=days)).isoformat()
    db=get_db(); db.execute("UPDATE users SET is_pro=1, pro_expiry=? WHERE email=?", (expiry,session["user"])); db.commit()
    return redirect("/")

@app.route("/admin/users")
def admin_users():
    if session.get("user")!=ADMIN_EMAIL: return "Only Admin", 403
    today,_,now_full=get_games(); db=get_db(); users=db.execute("SELECT * FROM users ORDER BY id DESC").fetchall(); now=datetime.now(WAT); total=len(users); active=0; trial=0; exp=0; adm=0; rows=""
    for u in users:
        te=datetime.fromisoformat(u["trial_end"]); pe=datetime.fromisoformat(u["pro_expiry"]) if u["pro_expiry"] else now; is_ad=bool(u["is_admin"]); is_p=now<pe
        if is_ad: adm+=1
        elif is_p and u["is_pro"]: active+=1
        elif now<te: trial+=1
        else: exp+=1
        cd=get_countdown(u["pro_expiry"]) if not is_ad else "FOREVER"; st="👑 ADMIN" if is_ad else "✅ ACTIVE PRO" if is_p else "⏳ TRIAL" if now<te else "❌ EXPIRED"; col="#00ff88" if is_p else "#ffaa00" if now<te else "#ff4444"
        rows+=f"<tr><td style='font-size:10px'>{u['email']}</td><td>{u['created_at'][:10]}</td><td style='color:{col};font-weight:bold'>{cd}</td><td>{pe.strftime('%m-%d %H:%M')}</td><td>{st}</td></tr>"
    dash=f"""<div style="background:#111;padding:15px;border-radius:12px;margin:10px"><h3 style="text-align:center;color:#00ff88">👑 ADMIN DASHBOARD - LIVE</h3><p style="text-align:center;font-size:11px;color:#888">{today} • {now_full} • 12:00 AM WAT Update</p><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:15px 0"><div style="background:#1a1a1a;padding:15px;border-radius:10px;text-align:center;border-left:4px solid #00ff88"><h2 style="margin:0;color:#00ff88;font-size:28px">{total}</h2><small>TOTAL USERS</small></div><div style="background:#1a1a1a;padding:15px;border-radius:10px;text-align:center;border-left:4px solid #ffaa00"><h2 style="margin:0;color:#ffaa00;font-size:32px">{active}</h2><small>ACTIVE PRO</small></div><div style="background:#1a1a1a;padding:15px;border-radius:10px;text-align:center;border-left:4px solid #00aaff"><h2 style="margin:0;color:#00aaff;font-size:28px">{trial}</h2><small>ON TRIAL</small></div><div style="background:#1a1a1a;padding:15px;border-radius:10px;text-align:center;border-left:4px solid #ff4444"><h2 style="margin:0;color:#ff4444;font-size:28px">{exp}</h2><small>EXPIRED</small></div></div><div style="background:#1a1a1a;padding:12px;border-radius:8px;text-align:center"><small>Opay/PalmPay 9079783177 • Est ₦{active*1000:,} • Safe: Double Chance/Over 1.5/Under 2.5/Handicap • Admins:{adm}</small></div></div>"""
    table=f"{dash}<div style='overflow-x:auto'><table border=1 style='width:100%;font-size:10px;color:#fff;border-collapse:collapse'><tr style='background:#222'><th>Email</th><th>Joined</th><th>Countdown</th><th>Expiry</th><th>Status</th></tr>{rows}</table></div><br><a class=btn href='/'>Back</a>"
    return render_template_string(BASE, today=today, now=now_full, admin_status=f"ADMIN - {active} ACTIVE PRO", content=table)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        e=request.form["email"].lower().strip(); pw=hashlib.sha256(request.form["password"].encode()).hexdigest(); db=get_db(); u=db.execute("SELECT * FROM users WHERE email=?", (e,)).fetchone()
        if not u:
            te=(datetime.now(WAT)+timedelta(days=3)).isoformat(); is_ad=1 if e==ADMIN_EMAIL else 0; ex=(datetime.now(WAT)+timedelta(days=3650)).isoformat() if is_ad else te
            db.execute("INSERT INTO users VALUES (NULL,?,?,?,?,?,?,?)",(e,pw,datetime.now(WAT).isoformat(),te,is_ad,is_ad,ex)); db.commit(); session["user"]=e; return redirect("/")
        if u["password"]==pw: session["user"]=e; return redirect("/")
        return "Wrong password"
    return "<div style='background:#0a0a0a;color:#fff;padding:40px;text-align:center'><h3>Login - Ultra Safe</h3><p>Double Chance • Over 1.5 • Under 2.5 • Handicap<br>3 Days FREE</p><form method=post><input name=email placeholder='Email' required style='padding:12px;width:85%;border-radius:8px;border:0'><br><br><input name=password type=password placeholder='Password' required style='padding:12px;width:85%;border-radius:8px;border:0'><br><br><button style='background:#00ff88;padding:12px 30px;border:0;border-radius:8px;font-weight:bold'>Login / Signup</button></form></div>"

@app.route("/logout")
def logout():
    session.clear(); return redirect("/")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
