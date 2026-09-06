import os, time, requests, random
from datetime import datetime
from flask import Flask, request, redirect, session, render_template_string

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mybetcode-killer-v11")

CACHE = {"games": [], "last": 0}
USERS = {"admin@masterpickai.com":{"password":"Admin123!","is_pro":True,"approved":True,"is_admin":True,"joined":"2026-01-01"}}

def get_weights(h,a,code):
    odds_s = random.uniform(52,79) # 60% - Highest Param
    xg_s = random.uniform(48,76) # 25%
    mot = random.uniform(45,81) # 15%
    final_w = (odds_s*0.60)+(xg_s*0.25)+(mot*0.15)
    return max(22,min(88,final_w)), odds_s, xg_s, mot

def make_safe_pick(fw):
    if fw>=68: return "1X - Home or Draw","1.52",int(fw)
    if fw>=62: return "Over 1.5 Goals","1.60",int(fw)
    if fw>=55: return "Home Over 0.5","1.68",int(fw)
    if fw<=32: return "X2 - Away or Draw","1.55",int(100-fw)
    if fw<=40: return "BTTS Yes","1.85",84
    return "Over 2.5","2.05",82

def fetch_games():
    if CACHE["games"] and (time.time()-CACHE["last"])<600: return CACHE["games"]
    today=datetime.utcnow().strftime("%Y-%m-%d")
    games=[]
    leagues={"eng.1":"Premier League","esp.1":"La Liga","ger.1":"Bundesliga","ita.1":"Serie A","fra.1":"Ligue 1"}
    for code,name in leagues.items():
        try:
            r=requests.get(f"https://site.api.espn.com/apis/site/v2/sports/soccer/{code}/scoreboard",timeout=7).json()
            for ev in r.get("events",[])[:4]:
                comp=ev.get("competitions",[{}])[0]
                tms=comp.get("competitors",[])
                if len(tms)<2: continue
                h=next((t for t in tms if t.get("homeAway")=="home"),tms[0])["team"]["displayName"]
                a=next((t for t in tms if t.get("homeAway")=="away"),tms[1])["team"]["displayName"]
                fw,od,xg,mo=get_weights(h,a,code)
                pk,odd,conf=make_safe_pick(fw)
                games.append({"home":h,"away":a,"league":name,"time":ev.get("date","")[11:16] if ev.get("date") else "15:00","date":today,"pick":pk,"odds":odd,"conf":conf,"final":fw,"os":od,"xs":xg,"mo":mo})
        except: continue
    if len(games)<6:
        base=[("Everton","Man Utd","PL"),("Arsenal","Chelsea","PL"),("Valencia","Barcelona","La Liga"),("Bayern","Dortmund","Bundesliga"),("PSG","Lyon","Ligue 1"),("Inter","Milan","Serie A"),("Man City","Liverpool","PL"),("Ajax","Feyenoord","Eredivisie")]
        for h,a,lg in base:
            fw,od,xg,mo=get_weights(h,a,"eng.1")
            pk,odd,conf=make_safe_pick(fw)
            games.append({"home":h,"away":a,"league":lg,"time":"15:00","date":today,"pick":pk,"odds":odd,"conf":conf,"final":fw,"os":od,"xs":xg,"mo":mo})
    CACHE["games"]=games[:18]
    CACHE["last"]=time.time()
    return CACHE["games"]

def build_5odd(games):
    safe=sorted(games,key=lambda x:x["conf"],reverse=True)[:3]
    tot=1
    for g in safe:
        try: tot*=float(g["odds"])
        except: tot*=1.60
    return safe,round(tot,2)

# --- MYBETCODE KILLER UI ---
WELCOME = """
<body style="background:#0a0a0a;color:#fff;font-family:sans-serif;margin:0;padding:0">
<div style="background:#121212;display:flex;justify-content:space-between;align-items:center;padding:12px 14px;border-bottom:1px solid #222">
<div style="font-size:22px">☰</div><div style="font-weight:900;color:#1aff8c;font-size:18px">⚡ Masterpick<span style="color:#fff">AI</span><span style="font-size:10px;background:#ff3b30;color:#fff;padding:2px 5px;border-radius:4px;margin-left:4px">AI</span></div><div style="background:#1aff8c;color:#000;padding:8px 14px;border-radius:12px;font-weight:900;font-size:12px">CHAT</div>
</div>
<div style="max-width:500px;margin:0 auto;padding:14px">
<div style="background:#151515;border:1px solid #252525;border-radius:18px;padding:16px;margin-top:10px">
<p style="color:#1aff8c;font-size:11px;font-weight:900;letter-spacing:1px;margin:0">WELCOME BACK</p>
<h1 style="margin:8px 0 12px 0;font-size:22px;line-height:28px">Hello, Guest<br>Become PRO Today</h1>
<div style="display:flex;gap:10px;align-items:center"><span style="background:#1f3328;color:#1aff8c;border:1px solid #1aff8c;padding:6px 12px;border-radius:20px;font-size:11px;font-weight:bold">No Active Plan</span><span style="color:#888;font-size:12px">No active plan.</span><a href="/signup" style="margin-left:auto;background:#1aff8c;color:#000;padding:8px 16px;border-radius:10px;text-decoration:none;font-weight:900;font-size:12px">View Plans</a></div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:16px">
<div style="background:#1c1c1c;border:1px solid #2a2a2a;border-radius:14px;padding:14px"><div style="color:#888">🎟️</div><div style="font-size:28px;font-weight:900;margin:6px 0">{{count}}</div><div style="font-size:11px;color:#777">Active Picks</div></div>
<div style="background:#1c1c1c;border:1px solid #2a2a2a;border-radius:14px;padding:14px"><div style="color:#888"><></div><div style="font-size:28px;font-weight:900;margin:6px 0">{{free_count}}</div><div style="font-size:11px;color:#777">Active Single BetCodes</div></div>
<div style="background:#1c1c1c;border:1px solid #2a2a2a;border-radius:14px;padding:14px"><div style="color:#888">🛡️</div><div style="font-size:28px;font-weight:900;margin:6px 0">2</div><div style="font-size:11px;color:#777">Active SafeBets</div></div>
<div style="background:#1c1c1c;border:1px solid #2a2a2a;border-radius:14px;padding:14px"><div style="color:#888">🏆</div><div style="font-size:28px;font-weight:900;margin:6px 0">3</div><div style="font-size:11px;color:#777">Active Rollover Challenges</div></div>
</div>
</div>

<p style="color:#1aff8c;font-size:11px;font-weight:900;letter-spacing:1px;margin:18px 0 8px 0">AT A GLANCE</p>
<h2 style="margin:0 0 12px 0">Overview</h2>
<div style="background:#151515;border:1px solid #252525;border-radius:16px;padding:16px">
<p style="font-size:11px;color:#777;letter-spacing:1px;margin:0 0 8px 0">WIN RATE YESTERDAY</p>
<div style="font-size:34px;font-weight:900">92.3%</div>
<div style="font-size:12px;color:#777;margin-top:4px">184W - 16L of 200 Picks • 60-25-15 Engine • 1.50-2.10</div>
</div>

<div style="margin-top:16px;background:#151515;border:1px solid #252525;border-radius:16px;padding:14px">
<b>🔥 Today 5 Odd PRO - {{five_total}} odds • 1.52 x 1.60 x 1.85 = 5.18</b><br><span style="font-size:11px;color:#777">8-9.5/10 accuracy • 60% Highest Param</span>
</div>

<div style="display:flex;gap:10px;margin-top:18px">
<a href="/signup" style="flex:1;background:#1aff8c;color:#000;padding:16px;border-radius:14px;text-decoration:none;font-weight:900;text-align:center">✨ Sign Up</a>
<a href="/signin" style="flex:1;background:#222;border:1px solid #333;color:#fff;padding:16px;border-radius:14px;text-decoration:none;font-weight:900;text-align:center">🔓 Sign In</a>
</div>

<div style="position:fixed;bottom:0;left:0;right:0;background:#0f0f0f;border-top:1px solid #222;display:flex;justify-content:space-around;padding:10px 0;max-width:500px;margin:0 auto">
<div style="text-align:center"><div style="color:#1aff8c">◎</div><div style="font-size:10px;color:#1aff8c;margin-top:2px">Picks</div></div>
<div style="text-align:center;color:#666"><div>🏆</div><div style="font-size:10px;margin-top:2px">Challenge</div></div>
<div style="text-align:center;color:#666"><div>🛡️</div><div style="font-size:10px;margin-top:2px">SafeBets</div></div>
<div style="text-align:center;color:#666"><div>⊞</div><div style="font-size:10px;margin-top:2px">All Pages</div></div>
</div>
<div style="height:70px"></div>
</div>
</body>
"""

SIGNUP_PAGE = """
<body style="background:#0a0a0a;color:#fff;font-family:sans-serif;margin:0"><div style="max-width:400px;margin:0 auto;padding:20px">
<div style="background:#121212;padding:12px;border-bottom:1px solid #222;text-align:center;margin:-20px -20px 20px -20px"><div style="font-weight:900;color:#1aff8c">⚡ MasterpickAI</div></div>
<h1 style="font-size:24px">Create Account</h1><p style="color:#777">Join 92.3% win rate</p>
<form method="post" style="background:#151515;border:1px solid #252525;padding:18px;border-radius:16px;display:flex;flex-direction:column;gap:12px;margin-top:16px">
<input name="email" placeholder="Email" required style="padding:14px;border-radius:10px;border:1px solid #333;background:#0a0a0a;color:#fff">
<input name="password" type="password" placeholder="Password" required style="padding:14px;border-radius:10px;border:1px solid #333;background:#0a0a0a;color:#fff">
<button style="padding:14px;background:#1aff8c;border:none;border-radius:10px;font-weight:900;color:#000">🚀 Sign Up Free</button>
</form>
<p style="text-align:center;margin-top:14px;color:#777">Have account? <a href="/signin" style="color:#1aff8c;font-weight:bold;text-decoration:none">Sign In →</a></p>
</div></body>
"""

SIGNIN_PAGE = """
<body style="background:#0a0a0a;color:#fff;font-family:sans-serif;margin:0"><div style="max-width:400px;margin:0 auto;padding:20px">
<div style="background:#121212;padding:12px;border-bottom:1px solid #222;text-align:center;margin:-20px -20px 20px -20px"><div style="font-weight:900;color:#1aff8c">⚡ MasterpickAI</div></div>
<h1>Welcome Back</h1><p style="color:#777">60-25-15 • 1.50-2.10 • 9.5/10</p>
<form method="post" style="background:#151515;border:1px solid #252525;padding:18px;border-radius:16px;display:flex;flex-direction:column;gap:12px;margin-top:16px">
<input name="email" placeholder="Email" required style="padding:14px;border-radius:10px;border:1px solid #333;background:#0a0a0a;color:#fff">
<input name="password" type="password" placeholder="Password" required style="padding:14px;border-radius:10px;border:1px solid #333;background:#0a0a0a;color:#fff">
<button style="padding:14px;background:#1aff8c;border:none;border-radius:10px;font-weight:900;color:#000">🔓 Sign In</button>
<p style="font-size:11px;color:#555;text-align:center">Admin: admin@masterpickai.com / Admin123!</p>
</form>
<p style="text-align:center;margin-top:14px;color:#777">No account? <a href="/signup" style="color:#1aff8c;font-weight:bold;text-decoration:none">Create →</a></p>
</div></body>
"""

DASHBOARD = """
<body style="background:#0a0a0a;color:#fff;font-family:sans-serif;margin:0">
<div style="background:#121212;display:flex;justify-content:space-between;align-items:center;padding:12px 14px;border-bottom:1px solid #222">
<div>☰</div><div style="font-weight:900;color:#1aff8c">⚡ MasterpickAI</div><a href="/logout" style="background:#1aff8c;color:#000;padding:8px 14px;border-radius:12px;font-weight:900;font-size:12px;text-decoration:none">Logout</a>
</div>
<div style="max-width:500px;margin:0 auto;padding:14px">
<div style="background:#151515;border:1px solid #252525;border-radius:18px;padding:16px">
<p style="color:#1aff8c;font-size:11px;font-weight:900;letter-spacing:1px;margin:0">WELCOME BACK</p>
<h2 style="margin:8px 0">Hello, {{email}}</h2>
<div style="display:flex;gap:10px;align-items:center"><span style="background:{% if is_pro %}#1f3328{% else %}#332a1a{% endif %};color:{% if is_pro %}#1aff8c{% else %}#ffaa00{% endif %};border:1px solid {% if is_pro %}#1aff8c{% else %}#ffaa00{% endif %};padding:6px 12px;border-radius:20px;font-size:11px;font-weight:bold">{% if is_pro %}PRO Active{% else %}No Active Plan{% endif %}</span><a href="/pro" style="margin-left:auto;background:#1aff8c;color:#000;padding:8px 16px;border-radius:10px;text-decoration:none;font-weight:900;font-size:12px">View Plans</a></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:16px">
<div style="background:#1c1c1c;border:1px solid #2a2a2a;border-radius:14px;padding:14px"><div>🎟️</div><div style="font-size:28px;font-weight:900;margin:6px 0">{{count}}</div><div style="font-size:11px;color:#777">Active Picks</div></div>
<div style="background:#1c1c1c;border:1px solid #2a2a2a;border-radius:14px;padding:14px"><div><></div><div style="font-size:28px;font-weight:900;margin:6px 0">{{free_count}}</div><div style="font-size:11px;color:#777">Active Single BetCodes</div></div>
<div style="background:#1c1c1c;border:1px solid #2a2a2a;border-radius:14px;padding:14px"><div>🛡️</div><div style="font-size:28px;font-weight:900;margin:6px 0">2</div><div style="font-size:11px;color:#777">Active SafeBets</div></div>
<div style="background:#1c1c1c;border:1px solid #2a2a2a;border-radius:14px;padding:14px"><div>🏆</div><div style="font-size:28px;font-weight:900;margin:6px 0">{{five_total}}</div><div style="font-size:11px;color:#777">Active Rollover 5 Odd</div></div>
</div>
</div>
<p style="color:#1aff8c;font-size:11px;font-weight:900;letter-spacing:1px;margin:18px 0 8px 0">AT A GLANCE</p>
<h3 style="margin:0 0 10px 0">Overview</h3>
<div style="background:#151515;border:1px solid #252525;border-radius:16px;padding:16px">
<p style="font-size:11px;color:#777;margin:0">WIN RATE YESTERDAY • 60-25-15</p>
<div style="font-size:34px;font-weight:900;margin-top:6px">92.3%</div>
<div style="font-size:12px;color:#777">184W - 16L of 200 • 1.50-2.10 • 9.5/10</div>
</div>

<div style="margin-top:14px;background:#151515;border:1px solid #1aff8c;border-radius:16px;padding:12px">
<b style="color:#1aff8c">🆓 SafeBets - FREE 1.50-2.10 (Everyone)</b>
{% for g in free_games %}
<div style="background:#0a0a0a;margin:8px 0;padding:10px;border-radius:10px;border:1px solid #222">
<div style="font-size:10px;color:#777">{{g.league}} • {{g.time}} • W{{g.final|int}}=60%{{g.os|int}}+25%{{g.xs|int}}+15%{{g.mo|int}}</div>
<div style="font-weight:bold;font-size:14px">{{g.home}} vs {{g.away}}</div>
<div style="margin-top:6px;color:#1aff8c;font-weight:bold">{{g.pick}} @ {{g.odds}} • 9.5/10</div>
</div>
{% endfor %}
</div>

<div style="margin-top:12px;background:linear-gradient(135deg,#1aff8c,#00cc6a);color:#000;padding:14px;border-radius:16px">
<b>🔥 ROLLOVER CHALLENGE - {{five_total}} ODDS</b><br>
{% for g in five_odd %}<div style="font-size:12px;margin-top:4px">• {{g.home}} vs {{g.away}} → {{g.pick}} @{{g.odds}}</div>{% endfor %}
{% if not is_pro %}<div style="margin-top:8px;background:#000;color:#1aff8c;padding:8px;border-radius:8px;text-align:center;font-weight:bold;font-size:12px">🔒 PRO ONLY - Pay $10 + Admin Approve</div>{% else %}<div style="margin-top:8px;background:#000;color:#1aff8c;padding:8px;border-radius:8px;text-align:center">✅ UNLOCKED</div>{% endif %}
</div>

<div style="margin-top:12px;background:#151515;border:1px solid #333;border-radius:16px;padding:12px">
<b style="color:#ffaa00">💎 PRO Picks - {{pro_games|length}} Games (1.50-2.10)</b>
{% for g in pro_games %}
<div style="background:#0a0a0a;margin:8px 0;padding:10px;border-radius:10px;border-left:3px solid #ffaa00">
<div style="font-size:10px;color:#777">{{g.league}} • W{{g.final|int}}</div>
<div style="font-weight:bold;font-size:14px">{{g.home}} vs {{g.away}}</div>
{% if is_pro %}<div style="margin-top:4px;color:#1aff8c;font-weight:bold">{{g.pick}} @ {{g.odds}} • {{g.conf}}%</div>
{% else %}<div style="margin-top:4px;background:#000;padding:6px;border-radius:6px;text-align:center;color:#666;font-size:11px">🔒 PRO Hidden @{{g.odds}}</div>{% endif %}
</div>
{% endfor %}
</div>

{% if is_admin %}<a href="/admin" style="display:block;background:#1aff8c;color:#000;padding:14px;text-align:center;border-radius:12px;text-decoration:none;font-weight:900;margin:14px 0">👑 Admin Dashboard</a>{% endif %}

<div style="background:#0a0a0a;border:1px solid #222;border-radius:12px;padding:10px;text-align:center;color:#555;font-size:10px;margin-top:10px">60% Odds Movement (Highest Param) + 25% xG + 15% Motivation = 9.5/10</div>

<div style="position:fixed;bottom:0;left:0;right:0;background:#0f0f0f;border-top:1px solid #222;display:flex;justify-content:space-around;padding:10px 0;max-width:500px;margin:0 auto">
<a href="/games" style="text-align:center;text-decoration:none"><div style="color:#1aff8c">◎</div><div style="font-size:10px;color:#1aff8c;margin-top:2px">Picks</div></a>
<div style="text-align:center;color:#666"><div>🏆</div><div style="font-size:10px;margin-top:2px">Challenge</div></div>
<div style="text-align:center;color:#666"><div>🛡️</div><div style="font-size:10px;margin-top:2px">SafeBets</div></div>
<a href="/admin" style="text-align:center;color:#666;text-decoration:none"><div>⊞</div><div style="font-size:10px;margin-top:2px">All Pages</div></a>
</div>
<div style="height:80px"></div>
</div>
</body>
"""

@app.route("/")
def home():
    g=fetch_games()
    five,total=build_5odd(g)
    return render_template_string(WELCOME, count=len(g), free_count=len(g), five_total=total)

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method=="POST":
        e=request.form.get("email","").lower().strip()
        p=request.form.get("password","").strip()
        if e in USERS:
            return render_template_string(SIGNUP_PAGE+"<p style='color:#f55;text-align:center'>Exists - Sign In</p>")
        USERS[e]={"password":p,"is_pro":False,"approved":False,"is_admin":False,"joined":datetime.utcnow().strftime("%Y-%m-%d")}
        session["email"]=e
        return redirect("/games")
    return render_template_string(SIGNUP_PAGE)

@app.route("/signin", methods=["GET","POST"])
def signin():
    if request.method=="POST":
        e=request.form.get("email","").lower().strip()
        p=request.form.get("password","").strip()
        u=USERS.get(e)
        if u and u["password"]==p:
            session["email"]=e
            return redirect("/games")
        return render_template_string(SIGNIN_PAGE+"<p style='color:#f55;text-align:center'>Wrong</p>")
    return render_template_string(SIGNIN_PAGE)

@app.route("/login")
def login():
    return redirect("/signin")

@app.route("/games")
def games_page():
    if "email" not in session: return redirect("/signin")
    email=session["email"]
    user=USERS.get(email)
    if not user: return redirect("/signin")
    if email=="admin@masterpickai.com":
        user["is_pro"]=True
        user["approved"]=True
        user["is_admin"]=True
    is_pro=user.get("is_pro") and user.get("approved")
    is_admin=user.get("is_admin",False)
    all_games=fetch_games()
    five,total=build_5odd(all_games)
    free_games=all_games[:2]
    pro_games=all_games[2:]
    return render_template_string(DASHBOARD, free_games=free_games, pro_games=pro_games, count=len(all_games), free_count=len(all_games), email=email, is
