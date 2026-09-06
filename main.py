import os, time, requests
from datetime import datetime
from flask import Flask, request, redirect, session, render_template_string
try:
    import pytz
    HAS_PYTZ = True
except:
    HAS_PYTZ = False

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "masterpick-any-league-2026")

TOKEN = (os.environ.get("SOCCER_API_KEY") or os.environ.get("API_KEY") or "eX1YOAIGVy").strip()
CACHE = {"games":[], "raw":0, "calls":0, "error":"", "last":0, "date":""}
USERS = {}
USERS["admin@masterpickai.com"] = {"password":"Admin123!", "is_pro":True, "approved":True, "is_admin":True}

def get_today():
    if HAS_PYTZ:
        try:
            return datetime.now(pytz.timezone("Africa/Lagos")).strftime("%Y-%m-%d")
        except:
            pass
    return datetime.utcnow().strftime("%Y-%m-%d")

def fetch_any():
    now = time.time()
    today = get_today()
    if CACHE["games"] and CACHE["date"]==today and (now-CACHE["last"])<900:
        return CACHE["games"]
    try:
        url = f"https://api.soccersapi.com/v2.2/fixtures/?t={TOKEN}&d={today}"
        r = requests.get(url, timeout=20)
        j = r.json()
        CACHE["calls"] += 1
        data = j.get("data") or []
        games=[]
        for f in data:
            st = str(f.get("status","")).upper()
            if st not in ["NS","TBD","","NOT STARTED"]:
                continue
            games.append({
                "home": f.get("home_name","Home"),
                "away": f.get("away_name","Away"),
                "league": f.get("league_name","League"),
                "time": (f.get("date_time",f"{today}T15:00:00Z")[11:16]),
            })
        games = sorted(games, key=lambda x: x["time"])[:30]
        CACHE["games"]=games; CACHE["raw"]=len(games); CACHE["last"]=now; CACHE["date"]=today
        CACHE["error"]=f"Live Any League {len(games)}" if games else "API returned 0 today"
        return games
    except Exception as e:
        CACHE["error"]=str(e)[:100]
        return []

@app.route("/")
def home():
    if "email" in session:
        return redirect("/games")
    games = fetch_any()
    today = get_today()
    return render_template_string(f"""
    <body style="margin:0;background:#060b1a;color:#fff;font-family:sans-serif"><div style="max-width:420px;margin:0 auto;padding:24px">
    <h1>Masterpick AI</h1><p style="color:#8aa0c8">Today {today} - Any League - RAW {CACHE['raw']} - {CACHE['error']}</p>
    <div style="background:#111b36;border-radius:16px;padding:20px">
    <p>Sign up to view REAL games today</p>
    <a href="/signup" style="display:block;background:#22c55e;color:#000;text-align:center;padding:14px;border-radius:12px;font-weight:bold;text-decoration:none">Create Account</a>
    <a href="/login" style="display:block;background:#1f2d5a;color:#fff;text-align:center;padding:14px;border-radius:12px;font-weight:bold;text-decoration:none;margin-top:10px">Login</a>
    </div></div></body>
    """)

@app.route("/login", methods=["GET","POST"])
def login():
    msg=""
    if request.method=="POST":
        e=request.form.get("email","").lower().strip(); p=request.form.get("password","")
        u=USERS.get(e)
        if u and u["password"]==p:
            session["email"]=e
            return redirect("/games")
        msg="Invalid"
    return render_template_string(f'<body style="background:#060b1a;color:#fff;font-family:sans-serif"><div style="max-width:380px;margin:60px auto;padding:24px;background:#111b36;border-radius:16px"><h2>Login</h2><form method="post"><input name="email" placeholder="Email" required style="width:100%;padding:12px;margin:6px 0"><input name="password" type="password" placeholder="Password" required style="width:100%;padding:12px;margin:6px 0"><button style="width:100%;padding:12px;background:#22c55e">Login</button></form><p style="color:red">{msg}</p><a href="/signup" style="color:#8aa0c8">Signup</a></div></body>')

@app.route("/signup", methods=["GET","POST"])
def signup():
    msg=""
    if request.method=="POST":
        e=request.form.get("email","").lower().strip(); p=request.form.get("password","")
        want = bool(request.form.get("want_pro"))
        if e in USERS: msg="Exists"
        else:
            USERS[e]={"password":p, "is_pro":want, "approved":False, "is_admin":False}
            msg="Created! Login now"
    return render_template_string(f'<body style="background:#060b1a;color:#fff;font-family:sans-serif"><div style="max-width:380px;margin:60px auto;padding:24px;background:#111b36;border-radius:16px"><h2>Signup</h2><form method="post"><input name="email" placeholder="Email" required style="width:100%;padding:12px;margin:6px 0"><input name="password" type="password" placeholder="Password" required style="width:100%;padding:12px;margin:6px 0"><label><input type="checkbox" name="want_pro"> Request Pro</label><button style="width:100%;padding:12px;background:#22c55e;margin-top:10px">Signup</button></form><p>{msg}</p><a href="/login" style="color:#8aa0c8">Login</a></div></body>')

@app.route("/games")
def games_page():
    if "email" not in session: return redirect("/login")
    games=fetch_any()
    email=session["email"]
    user=USERS.get(email,{})
    html="<body style='margin:0;background:#060b1a;color:#fff;font-family:sans-serif'><div style='max-width:520px;margin:0 auto;padding:16px'>"
    html+=f"<div style='font-size:11px;color:#8aa0c8'>Hi {email} | {CACHE['error']} | RAW {CACHE['raw']} <a href='/logout' style='color:#8aa0c8;float:right'>Logout</a></div>"
    html+=f"<h2>{get_today()} Any League {len(games)} Games</h2>"
    if not games:
        html+=f"<div style='background:#1a233f;padding:20px;border-radius:12px;text-align:center'>No NS fixtures today. API returned 0. Key {TOKEN[:4]}... check quota.</div>"
    for g in games:
        html+=f"<div style='background:#141d38;border:1px solid #1f2d5a;border-radius:12px;padding:12px;margin:8px 0'><div style='font-size:11px;color:#8aa0c8'>{g['league']} | {g['time']} WAT</div><div style='font-size:18px;font-weight:bold'>{g['home']} vs {g['away']}</div></div>"
    if user.get("is_admin"):
        html+="<a href='/admin' style='color:#8aa0c8'>Admin Panel</a>"
    html+="</div></body>"
    return html

@app.route("/admin")
def admin_p():
    if not USERS.get(session.get("email"),{}).get("is_admin"): return "Admin only: admin@masterpickai.com / Admin123!",403
    html="<body style='background:#060b1a;color:#fff;padding:16px'><h2>Admin Approve Pro</h2>"
    for em,u in USERS.items():
        html+=f"<div style='background:#141d38;padding:10px;margin:6px 0;border-radius:8px'>{em} Pro:{u['is_pro']} Approved:{u['approved']} <a href='/admin/approve?email={em}' style='background:#22c55e;color:#000;padding:4px 8px;border-radius:6px;text-decoration:none;margin-left:10px'>Approve</a> <a href='/admin/reject?email={em}' style='background:#ef4444;color:#fff;padding:4px 8px;border-radius:6px;text-decoration:none'>Reject</a></div>"
    html+="</body>"
    return html

@app.route("/admin/approve")
def approve():
    if not USERS.get(session.get("email"),{}).get("is_admin"): return "Admin only",403
    t=request.args.get("email","");
    if t in USERS: USERS[t]["approved"]=True; USERS[t]["is_pro"]=True
    return redirect("/admin")

@app.route("/admin/reject")
def reject():
    if not USERS.get(session.get("email"),{}).get("is_admin"): return "Admin only",403
    t=request.args.get("email","");
    if t in USERS: USERS[t]["approved"]=False
    return redirect("/admin")

@app.route("/logout")
def logout():
    session.pop("email",None); return redirect("/")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
