import os,sqlite3,hashlib
from datetime import datetime,timedelta,timezone
from flask import Flask,request,redirect,session,render_template_string
app=Flask(__name__)
app.secret_key="final941"
WAT=timezone(timedelta(hours=1))
ADMIN="arinzechukwuemeka125@gmail.com"
DB="users.db"
def get_db():
    db=sqlite3.connect(DB)
    db.row_factory=sqlite3.Row
    return db
def init_db():
    db=get_db()
    db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY,email TEXT UNIQUE,password TEXT,created_at TEXT,trial_end TEXT,is_pro INTEGER DEFAULT 0,is_admin INTEGER DEFAULT 0,pro_expiry TEXT)")
    db.commit()
    if not db.execute("SELECT * FROM users WHERE email=?",(ADMIN,)).fetchone():
        far=(datetime.now(WAT)+timedelta(days=3650)).isoformat()
        db.execute("INSERT INTO users VALUES (NULL,?,?,?,?,?,?,?)",(ADMIN,hashlib.sha256("admin123".encode()).hexdigest(),datetime.now(WAT).isoformat(),far,1,1,far))
        db.commit()
def get_games():
    now=datetime.now(WAT)
    today=now.date()
    games=[
        ("Arsenal vs Brentford","Over 1.5 Goals","92%","Football","1.28","PL Over 1.5"),
        ("Man City vs Luton","Double Chance 1X","93%","Football","1.25","PL Double Chance"),
        ("Barcelona vs Sevilla","Over 0.5 Goals","94%","Football","1.18","La Liga Over 0.5"),
        ("Real Madrid vs Getafe","Handicap +1","89%","Football","1.35","La Liga Handicap"),
        ("Inter vs Napoli","Double Chance X2","88%","Football","1.32","Serie A DC"),
        ("Bayern vs Dortmund","Under 3.5 Goals","87%","Football","1.40","Bundesliga Under"),
        ("Djokovic vs Alcaraz","Over 18.5 Games","90%","Tennis","1.30","ATP Over"),
        ("Lakers vs Warriors","Over 200.5 Points","88%","Basketball","1.32","NBA Over"),
    ]
    return today,games,now.strftime("%Y-%m-%d %H:%M WAT")
def cd_func(s):
    try:
        e=datetime.fromisoformat(s)
        d=e-datetime.now(WAT)
        if d.total_seconds()<=0:
            return "EXPIRED"
        h=d.seconds//3600
        m=(d.seconds%3600)//60
        if d.days>0:
            return f"{d.days}d {h}h {m}m"
        return f"{h}h {m}m left"
    except:
        return "Active"
init_db()
BASE="""<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>MasterpickAI</title><style>body{margin:0;background:#0a0a0a;color:#fff;font-family:Arial}.h{background:#00ff88;color:#000;padding:14px;text-align:center;font-weight:bold}.sub{background:#1a1a1a;padding:8px;text-align:center;color:#00ff88;font-size:11px}.card{background:#1a1a1a;margin:10px;padding:14px;border-radius:12px;border-left:4px solid #00ff88}.b{background:#00ff88;color:#000;padding:4px 8px;border-radius:6px;font-size:11px;font-weight:bold}.bp{background:#ffaa00;color:#000;padding:4px 8px;border-radius:6px;font-size:11px;font-weight:bold}.btn{background:#00ff88;color:#000;padding:12px 18px;border-radius:8px;display:inline-block;font-weight:bold;border:0;margin:5px;text-decoration:none}.pay{background:#ffaa00;color:#000;width:90%;text-align:center;padding:14px;border-radius:8px;display:block;margin:8px auto;font-weight:bold;text-decoration:none}.count{background:#ffaa00;color:#000;padding:6px 12px;border-radius:20px;font-weight:bold;display:inline-block}</style></head><body><div class=h>⚽ MasterpickAI LIVE - SAFE</div><div class=sub>{{today}} • {{now}} • {{admin}}</div>{{content}}</body></html>"""
@app.route("/")
def home():
    today,games,now_full=get_games()
    now=datetime.now(WAT)
    email=session.get("user")
    is_pro=False
    is_admin=False
    cd=""
    exp=""
    if email:
        u=get_db().execute("SELECT * FROM users WHERE email=?",(email,)).fetchone()
        if u:
            is_admin=bool(u["is_admin"])
            exp=u["pro_expiry"]
            pe=datetime.fromisoformat(exp) if exp else now
            is_pro=now<pe or is_admin
            cd=cd_func(exp) if not is_admin else "ADMIN FOREVER"
    free=games[:2]
    pro=games[2:]
    adm_txt=f"{email} ADMIN" if is_admin else f"{email} PRO {cd}" if is_pro and email else f"{email}" if email else "Guest"
    content=""
    if email and is_pro:
        content+=f"<div style=text-align:center><div class=count>{cd}</div><p style=font-size:11px;color:#888>Expires {exp[:16] if not is_admin else 'Never'}</p></div>"
    for n,p,c,s,o,l in free:
        content+=f"<div class=card><b>{n}</b><br><small>{l}</small><span style=float:right;color:#00ff88>{o}</span><br>Tip: <span class=b>{p} - {c}</span></div>"
    if is_pro or is_admin:
        content+=f"<div style=text-align:center><span class=bp>PRO UNLOCKED - {cd}</span></div>"
        for n,p,c,s,o,l in pro:
            content+=f"<div class=card><b>{n}</b><br><small>{l}</small><span style=float:right;color:#00ff88>{o}</span><br>Tip: <span class=bp>{p} - {c}</span></div>"
    else:
        content+=f"<div class=card style=text-align:center;border-left-color:#ffaa00><h3>🔒 {len(pro)} SAFE Games Locked</h3><p>Double Chance • Over 1.5 • Under 2.5 • Handicap</p><p style=background:#222;padding:10px;border-radius:8px><b>Opay/PalmPay: 9079783177</b><br>Arinze Chukwuemeka Peter</p><a class=pay href='/pay/3'>Paid N500 - 3 Days</a><a class=pay href='/pay/7'>Paid N1000 - 7 Days</a><a class=pay href='/pay/14' style=background:#00ff88>Paid N1977 - 14 Days BEST</a><a class=btn href='https://wa.me/2349079783177' style=background:#222;color:#00ff88;border:1px solid #00ff88>WhatsApp Proof</a></div>"
    if is_admin:
        content+=f"<div style=text-align:center><a class=btn href='/admin/users'>ADMIN DASHBOARD</a></div>"
    elif not email:
        content=f"<div style=text-align:center;padding:25px><h3>Welcome - SAFE AI</h3><p>Double Chance • Over 1.5 • 3 Days FREE<br><small>12:00 AM WAT Update</small></p><a class=btn href='/login'>Login / Signup</a></div>"+content
    return render_template_string(BASE,today=today,now=now_full,admin=adm_txt,content=content)
@app.route("/pay/<int:days>")
def pay(days):
    if "user" not in session:
        return redirect("/login")
    exp=(datetime.now(WAT)+timedelta(days=days)).isoformat()
    db=get_db()
    db.execute("UPDATE users SET is_pro=1,pro_expiry=? WHERE email=?",(exp,session["user"]))
    db.commit()
    return redirect("/")
@app.route("/admin/users")
def admin_users():
    if session.get("user")!=ADMIN:
        return "Only Admin",403
    today,g,now_full=get_games()
    db=get_db()
    users=db.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
    now=datetime.now(WAT)
    total=len(users)
    active=0
    trial=0
    expc=0
    rows=""
    for u in users:
        te=datetime.fromisoformat(u["trial_end"])
        pe=datetime.fromisoformat(u["pro_expiry"]) if u["pro_expiry"] else now
        is_ad=bool(u["is_admin"])
        is_p=now<pe
        if not is_ad:
            if is_p and u["is_pro"]:
                active+=1
            elif now<te:
                trial+=1
            else:
                expc+=1
        cd=cd_func(u["pro_expiry"]) if not is_ad else "FOREVER"
        st="ADMIN" if is_ad else "ACTIVE PRO" if is_p else "TRIAL" if now<te else "EXPIRED"
        rows+=f"<tr><td>{u['email'][:20]}</td><td>{cd}</td><td>{st}</td></tr>"
    dash=f"<div style=background:#111;padding:15px;border-radius:12px;margin:10px><h3 style=text-align:center;color:#00ff88>ADMIN DASHBOARD</h3><div style=display:grid;grid-template-columns:1fr 1fr;gap:10px><div style=background:#1a1a1a;padding:15px;border-radius:10px;text-align:center><h2 style=color:#00ff88>{total}</h2>TOTAL</div><div style=background:#1a1a1a;padding:15px;border-radius:10px;text-align:center><h2 style=color:#ffaa00>{active}</h2>ACTIVE PRO</div><div style=background:#1a1a1a;padding:15px;border-radius:10px;text-align:center><h2>{trial}</h2>TRIAL</div><div style=background:#1a1a1a;padding:15px;border-radius:10px;text-align:center><h2>{expc}</h2>EXPIRED</div></div><p style=text-align:center><small>Opay 9079783177 • Est N{active*1000}</small></p></div>"
    table=f"{dash}<table border=1 style=width:100%;font-size:10px;color:#fff><tr><th>Email</th><th>Countdown</th><th>Status</th></tr>{rows}</table><br><a class=btn href='/'>Back</a>"
    return render_template_string(BASE,today=today,now=now_full,admin=f"ADMIN {active} ACTIVE",content=table)
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        e=request.form["email"].lower().strip()
        pw=hashlib.sha256(request.form["password"].encode()).hexdigest()
        db=get_db()
        u=db.execute("SELECT * FROM users WHERE email=?",(e,)).fetchone()
        if not u:
            te=(datetime.now(WAT)+timedelta(days=3)).isoformat()
            is_ad=1 if e==ADMIN else 0
            ex=(datetime.now(WAT)+timedelta(days=3650)).isoformat() if is_ad else te
            db.execute("INSERT INTO users VALUES (NULL,?,?,?,?,?,?,?)",(e,pw,datetime.now(WAT).isoformat(),te,is_ad,is_ad,ex))
            db.commit()
            session["user"]=e
            return redirect("/")
        if u["password"]==pw:
            session["user"]=e
            return redirect("/")
        return "Wrong password"
    return "<div style=background:#0a0a0a;color:#fff;padding:40px;text-align:center><h3>Login</h3><form method=post><input name=email placeholder=Email required style=padding:12px;width:85%;border-radius:8px;border:0><br><br><input name=password type=password placeholder=Password required style=padding:12px;width:85%;border-radius:8px;border:0><br><br><button style=background:#00ff88;padding:12px 30px;border:0;border-radius:8px;font-weight:bold>Login / Signup</button></form></div>"
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
