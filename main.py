import os, time, requests
from datetime import datetime
from flask import Flask, request, redirect, session, render_template_string, jsonify
import pytz

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "masterpick44-any-league")

TOKEN = (os.environ.get("SOCCER_API_KEY") or os.environ.get("API_KEY") or "eX1YOAIGVy").strip()
CACHE = {"games":[], "raw":0, "calls":0, "error":"", "last":0, "date":""}
USERS = {}
USERS["admin@masterpickai.com"] = {"password":"Admin123!", "is_pro":True, "approved":True, "is_admin":True}

def get_wat():
    return datetime.now(pytz.timezone("Africa/Lagos"))

def fetch_any_league():
    now_ts = time.time()
    today = get_wat().strftime("%Y-%m-%d")
    if CACHE["games"] and CACHE["date"]==today and (now_ts-CACHE["last"])<900:
        return CACHE["games"]
    try:
        url = f"https://api.soccersapi.com/v2.2/fixtures/?t={TOKEN}&d={today}"
        r = requests.get(url, timeout=25)
        j = r.json()
        CACHE["calls"] += 1
        data = j.get("data") or []
        games = []
        for f in data:
            status = str(f.get("status") or "").upper()
            if status not in ["NS","TBD","","NOT STARTED"]:
                continue # only yet to be played
            games.append({
                "home": f.get("home_name") or "Home",
                "away": f.get("away_name") or "Away",
                "league": f.get("league_name") or f.get("competition_name") or "League",
                "country": f.get("country_name") or "",
                "time": (f.get("date_time") or f"{today}T15:00:00Z")[11:16],
                "status": "NS"
            })
        # Sort by time, any league - no premier filter
        games = sorted(games, key=lambda x: x["time"])[:30]
        CACHE["games"]=games; CACHE["raw"]=len(games); CACHE["last"]=now_ts; CACHE["date"]=today
        CACHE["error"]=f"Live Any League - {len(games)} games" if games else "API 0 - No NS today"
        return games
    except Exception as e:
        CACHE["error"]=str(e)[:120]
        CACHE["games"]=[]; CACHE["raw"]=0; return []

LANDING = """
<body style="margin:0;background:#060b1a;color:#fff;font-family:sans-serif"><div style="max-width:420px;margin:0 auto;padding:24px">
<h1>⚽ Masterpick AI</h1><p style="color:#8aa0c8">Real fixtures - Any league - Today {{date}}</p>
<div style="background:#111b36;border-radius:16px;padding:20px"><p>RAW {{cache.raw}} | {{cache.error}}</p>
<p>🔒 Sign up to view real games today (any league)</p>
<a href="/signup" style="display:block;background:#22c55e;color:#000;text-align:center;padding:14px;border-radius:12px;font-weight:bold;text-decoration:none">Create Account</a>
<a href="/login" style="display:block;background:#1f2d5a;color:#fff;text-align:center;padding:14px;border-radius:12px;font-weight:bold;text-decoration:none;margin-top:10px">Login</a>
</div></div></body>
"""

LOGIN_HTML = """<body style="margin:0;background:#060b1a;color:#fff;font-family:sans-serif"><div style="max-width:380px;margin:60px auto;padding:24px;background:#111b36;border-radius:16px">
<h2>Login</h2><form method="post"><input name="email" placeholder="Email" required style="width:100%;padding:12px;border-radius:8px;border:1px solid #2a3a6a;background:#0b1020;color:#fff;margin:8px 0"><input name="password" type="password" placeholder="Password" required style="width:100%;padding:12px;border-radius:8px;border:1px solid #2a3a6a;background:#0b1020;color:#fff;margin:8px 0"><button style="width:100%;padding:12px;background:#22c55e;border:none;border-radius:8px;font-weight:bold;margin-top:12px">Login</button></form><p style="color:#ff6b6b">{{msg}}</p><a href="/signup" style="color:#8aa0c8">Sign up</a></div></body>"""

SIGNUP_HTML = """<body style="margin:0;background:#060b1a;color:#fff;font-family:sans-serif"><div style="max-width:380px;margin:60px auto;padding:24px;background:#111b36;border-radius:16px">
<h2>Create Account</h2><form method="post"><input name="email" placeholder="Email" required style="width:100%;padding:12px;border-radius:8px;border:1px solid #2a3a6a;background:#0b1020;color:#fff;margin:8px 0"><input name="password" type="password" placeholder="Password" required style="width:100%;padding:12px;border-radius:8px;border:1px solid #2a3a6a;background:#0b1020;color:#fff;margin:8px 0"><label style="font-size:13px"><input type="checkbox" name="want_pro"> Request Pro (admin approval)</label><button style="width:100%;padding:12px;background:#22c55e;border:none;border-radius:8px;font-weight:bold;margin-top:12px">Sign Up</button></form><p style="color:#8aa0c8">{{msg}}</p><a href="/login" style="color:#8aa0c8">Login</a></div></body>"""

GAMES_HTML = """
<body style="margin:0;background:#060b1a;color:#fff;font-family:sans-serif"><div style="max-width:520px;margin:0 auto;padding:16px">
<div style="display:flex;justify-content:space-between"><div style="font-size:11px;color:#8aa0c8">Hi {{email}} | {{cache.error}}</div><a href="/logout" style="color:#8aa0c8;font-size:12px">Logout</a></div>
<h2>{{date}} - Any League - {{games|length}} Games</h2>
{% if not games %}<div style="background:#1a233f;padding:20px;border-radius:12px;text-align:center;color:#8aa0c8">No yet-to-be-played fixtures today from API.<br>API key {{tok[:4]}}... returned 0. Check SoccersAPI quota.</div>{% endif %}
{% for g in games %}
<div style="background:#141d38;border:1px solid #1f2d5a;border-radius:14px;padding:14px;margin:10px 0">
<div style="font-size:11px;color:#8aa0c8">{{g.league}} {{g.country}} | {{g.time}} WAT | {{g.status}}</div>
<div style="font-size:18px;font-weight:bold;margin:8px 0">{{g.home}} vs {{g.away}}</div>
<div style="display:flex;gap:8px"><span style="background:#22c55e;color:#000;padding:4px 10px;border-radius:8px;font-weight:bold;font-size:12px">Over 1.5 @ 1.42</span><a href="/pro" style="background:#f59e0b;color:#000;padding:4px 10px;border-radius:8px;font-weight:bold;font-size:12px;text-decoration:none">Pro 🔒</a></div>
</div>
{% endfor %}
{% if is_admin %}<a href="/admin" style="color:#8aa0c8">Admin Panel</a>{% endif %}
</div></body>
"""

PRO_HTML = """<body style="margin:0;background:#060b1a;color:#fff;font-family:sans-serif"><div style="max-width:500px;margin:20px auto;padding:16px">
<h2>Pro Section</h2>{% if not user.approved %}<div style="background:#3a1f1f;padding:20px;border-radius:12px">⛔ Pending admin approval - {{email}}<br><a href="/games" style="color:#8aa0c8">Back</a></div>{% else %}<div style="background:#1e3a2f;border:1px solid #22c55e;padding:16px;border-radius:12px">{% for g in games %}<div style="margin:8px 0">{{g.home}} vs {{g.away}} → <b>BTTS Yes @ 1.85</b> - {{g.league}}</div>{% endfor %}</div>{% endif %}</div></body>"""

ADMIN_HTML = """<body style="margin:0;background:#060b1a;color:#fff;font-family:sans-serif;padding:16px"><h2>Admin - Approve Pro</h2><div style="font-size:12px;color:#8aa0c8">{{cache.error}} | Calls {{cache.calls}}</div>{% for email,u in users.items() %}<div style="background:#141d38;padding:12px;margin:8px 0;border-radius:10px;display:flex;justify-content:space-between"><div>{{email}} Pro:{{u.is_pro}} Approved:{{u.approved}}</div><div><a href="/admin/approve?email={{email}}" style="background:#22c55e;color:#000;padding:6px 10px;border-radius:6px;text-decoration:none">Approve</a> <a href="/admin/reject?email={{email}}" style="background:#ef4444;color:#fff;padding:6px 10px;border-radius:6px;text-decoration:none">Reject</a></div></div>{% endfor %}<a href="/games" style="color:#8aa0c8">Back</a></body>"""

@app.route("/")
def landing():
    if "email" in session: return redirect("/games")
    fetch_any_league()
    return render_template_string(LANDING, date=get_wat().strftime("%Y-%m-%d"), cache=CACHE)

@app.route("/login", methods=["GET","POST"])
def login():
    msg=""
    if request.method=="POST":
        email=request.form.get("email","").lower().strip()
        pwd=request.form.get("password","")
        u=USERS.get(email)
        if u and u["password"]==pwd:
            session["email"]=email
            return redirect("/games")
        msg="Invalid credentials"
    return render_template_string(LOGIN_HTML, msg=msg)

@app.route("/signup", methods=["GET","POST"])
def signup():
    msg=""
    if request.method=="POST":
        email=request.form.get("email","").lower().strip()
        pwd=request.form.get("password","")
        want_pro=bool(request.form.get("want_pro"))
        if email in USERS: msg="Exists"
        else:
            USERS[email]={"password":pwd, "is_pro":want_pro, "approved":False, "is_admin":False}
            msg="Created! Login" + (" - Pro pending" if want_pro else "")
    return render_template_string(SIGNUP_HTML, msg=msg)

@app.route("/games")
def games_page():
    email=session.get("email")
    if not email: return redirect("/login")
    games=fetch_any_league()
    user=USERS.get(email, {})
    return render_template_string(GAMES_HTML, games=games, date=get_wat().strftime("%Y-%m-%d"), cache=CACHE, email=email, is_admin=user.get("is_admin", False), tok=TOKEN)

@app.route("/pro")
def pro_page():
    email=session.get("email")
    if not email: return redirect("/login")
    games=fetch_any_league()
    return render_template_string(PRO_HTML, games=games, user=USERS.get(email, {}), email=email)

@app.route("/admin")
def admin_panel():
    email=session.get("email")
    if not USERS.get(email, {}).get("is_admin"): return "Admin only: admin@masterpickai.com / Admin123!",403
    return render_template_string(ADMIN_HTML, users=USERS, cache=CACHE)

@app.route("/admin/approve")
def approve():
    if not USERS.get(session.get("email"), {}).get("is_admin"): return "Admin only",403
    t=request.args.get("email","")
    if t in USERS: USERS[t]["approved"]=True; USERS[t]["is_pro"]=True
    return redirect("/admin")

@app.route("/admin/reject")
def reject():
    if not USERS.get(session.get("email"), {}).get("is_admin"): return "Admin only",403
    t=request.args.get("email","")
    if t in USERS: USERS[t]["approved"]=False; USERS[t]["is_pro"]=False
    return redirect("/admin")

@app.route("/logout")
def logout():
    session.pop("email",None); return redirect("/")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
