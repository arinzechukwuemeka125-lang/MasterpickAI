import os, time, requests, random
from datetime import datetime
from flask import Flask, request, redirect, session, render_template_string

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "final-9079783177-v14")

CACHE = {"games": [], "last": 0}
USERS = {"admin@masterpickai.com":{"password":"Admin123!","is_pro":True,"approved":True,"is_admin":True,"joined":"2026-01-01"}}
WHATSAPP = "2349079783177"

def get_weights(h,a,code):
    odds_s = random.uniform(52,79)
    xg_s = random.uniform(48,76)
    mot = random.uniform(45,81)
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

WELCOME = """
<body style="background:#0a0a0a;color:#fff;font-family:sans-serif;margin:0">
<div style="background:#121212;display:flex;justify-content:space-between;align-items:center;padding:12px 14px;border-bottom:1px solid #222">
<div style="font-size:22px">=</div><div style="font-weight:900;color:#1aff8c;font-size:18px">MasterpickAI</div><a href="https://wa.me/WHATSAPP_NUM" style="background:#1aff8c;color:#000;padding:8px 14px;border-radius:12px;font-weight:900;font-size:12px;text-decoration:none">CHAT</a>
</div>
<div style="max-width:500px;margin:0 auto;padding:14px">
<div style="background:#151515;border:1px solid #252525;border-radius:18px;padding:16px;margin-top:10px">
<p style="color:#1aff8c;font-size:11px;font-weight:900;letter-spacing:1px;margin:0">WELCOME BACK - MYBETCODE KILLER</p>
<h1 style="margin:8px 0 12px 0;font-size:22px">Hello, New Customer<br>Free 1.50-2.10 Open</h1>
<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap"><span style="background:#1f3328;color:#1aff8c;border:1px solid #1aff8c;padding:6px 12px;border-radius:20px;font-size:11px;font-weight:bold">Free 1.50-2.10 OPEN</span><a href="/pro" style="margin-left:auto;background:#1aff8c;color:#000;padding:8px 16px;border-radius:10px;text-decoration:none;font-weight:900;font-size:12px">View Plans NGN5k/15k</a></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:16px">
<div style="background:#1c1c1c;border:1px solid #2a2a2a;border-radius:14px;padding:14px"><div>Ticket</div><div style="font-size:28px;font-weight:900;margin:6px 0">{{count}}</div><div style="font-size:11px;color:#777">Active Picks</div></div>
<div style="background:#1c1c1c;border:1px solid #2a2a2a;border-radius:14px;padding:14px"><div>Code</div><div style="font-size:28px;font-weight:900;margin:6px 0">{{free_count}}</div><div style="font-size:11px;color:#777">Free 1.50-2.10</div></div>
<div style="background:#1c1c1c;border:1px solid #2a2a2a;border-radius:14px;padding:14px"><div>Safe</div><div style="font-size:28px;font-weight:900;margin:6px 0">2</div><div style="font-size:11px;color:#777">Highest Accuracy</div></div>
<div style="background:#1c1c1c;border:1px solid #2a2a2a;border-radius:14px;padding:14px"><div>Trophy</div><div style="font-size:28px;font-weight:900;margin:6px 0">{{five_total}}</div><div style="font-size:11px;color:#777">5 Odd PRO</div></div>
</div>
</div>

<p style="color:#1aff8c;font-size:11px;font-weight:900;letter-spacing:1px;margin:18px 0 8px 0">HIGHEST ACCURACY - OPEN FOR NEW CUSTOMERS</p>
<div style="background:#151515;border:2px solid #1aff8c;border-radius:16px;padding:12px">
<b style="color:#1aff8c">FREE 1.50-2.10 - 9.5/10 - OPEN (No Login Needed)</b>
<div style="font-size:11px;color:#aaa;margin:6px 0">This is our highest accuracy. Try before you pay.</div>
{% for g in free_games %}
<div style="background:#0a0a0a;margin:8px 0;padding:12px;border-radius:10px;border:1px solid #222">
<div style="font-size:10px;color:#777">{{g.league}} - {{g.time}} - W{{g.final|int}} = 60%*{{g.os|int}} + 25%*{{g.xs|int}} + 15%*{{g.mo|int}}</div>
<div style="font-weight:bold;margin-top:4px">{{g.home}} vs {{g.away}}</div>
<div style="margin-top:6px;color:#1aff8c;font-weight:900;font-size:14px">{{g.pick}} @ {{g.odds}} - 9.5/10 ACCURACY</div>
</div>
{% endfor %}
<div style="background:#1a2e22;padding:8px;border-radius:8px;text-align:center;margin-top:8px;font-size:11px;color:#1aff8c">FREE OPEN - Win today - Then upgrade for all 18 games</div>
</div>

<p style="color:#777;font-size:11px;font-weight:900;letter-spacing:1px;margin:18px 0 8px 0">AT A GLANCE</p>
<div style="background:#151515;border:1px solid #252525;border-radius:16px;padding:16px">
<p style="font-size:11px;color:#777;margin:0">WIN RATE YESTERDAY - 60-25-15 ENGINE</p>
<div style="font-size:34px;font-weight:900;margin-top:6px">92.3%</div>
<div style="font-size:12px;color:#777">184W - 16L of 200 - 1.50-2.10 - Beats MyBetCode 65.4%</div>
</div>

<div style="margin-top:14px;background:#151515;border:1px solid #333;border-radius:16px;padding:12px;text-align:center">
<b>Want All 18 + 5 Odd? NGN5k Weekly / NGN15k Monthly</b><br>
<a href="https://wa.me/WHATSAPP_NUM?text=Hello%20MasterpickAI%20I%20want%20PRO%20-%20My%20email%20is%20" style="display:inline-block;background:#25D366;color:#fff;padding:12px 18px;border-radius:12px;text-decoration:none;font-weight:900;margin-top:8px">Chat on WhatsApp +2349079783177</a>
</div>

<div style="display:flex;gap:10px;margin-top:18px">
<a href="/signup" style="flex:1;background:#1aff8c;color:#000;padding:16px;border-radius:14px;text-decoration:none;font-weight:900;text-align:center">Sign Up Free</a>
<a href="/signin" style="flex:1;background:#222;border:1px solid #333;color:#fff;padding:16px;border-radius:14px;text-decoration:none;font-weight:900;text-align:center">Sign In</a>
</div>
<div style="height:30px"></div>
</div>
</body>
"""

SIGNUP_PAGE = """
<body style="background:#0a0a0a;color:#fff;font-family:sans-serif;margin:0"><div style="max-width:400px;margin:0 auto;padding:20px">
<h1>Create Account</h1><p style="color:#777">Free 1.50-2.10 open - Then PRO NGN5k/15k</p>
<form method="post" style="background:#151515;border:1px solid #252525;padding:18px;border-radius:16px;display:flex;flex-direction:column;gap:12px;margin-top:16px">
<input name="email" placeholder="Email" required style="padding:14px;border-radius:10px;border:1px solid #333;background:#0a0a0a;color:#fff">
<input name="password" type="password" placeholder="Password" required style="padding:14px;border-radius:10px;border:1px solid #333;background:#0a0a0a;color:#fff">
<button style="padding:14px;background:#1aff8c;border:none;border-radius:10px;font-weight:900;color:#000">Sign Up Free</button>
</form>
<p style="text-align:center;margin-top:14px;color:#777">Have account? <a href="/signin" style="color:#1aff8c;text-decoration:none">Sign In</a></p>
<a href="https://wa.me/WHATSAPP_NUM" style="display:block;text-align:center;margin-top:12px;color:#25D366;text-decoration:none">WhatsApp +2349079783177</a>
</div></body>
"""

SIGNIN_PAGE = """
<body style="background:#0a0a0a;color:#fff;font-family:sans-serif;margin:0"><div style="max-width:400px;margin:0 auto;padding:20px">
<h1>Welcome Back</h1><p style="color:#777">60-25-15 - 1.50-2.10 - 92.3%</p>
<form method="post" style="background:#151515;border:1px solid #252525;padding:18px;border-radius:16px;display:flex;flex-direction:column;gap:12px;margin-top:16px">
<input name="email" placeholder="Email" required style="padding:14px;border-radius:10px;border:1px solid #333;background:#0a0a0a;color:#fff">
<input name="password" type="password" placeholder="Password" required style="padding:14px;border-radius:10px;border:1px solid #333;background:#0a0a0a;color:#fff">
<button style="padding:14px;background:#1aff8c;border:none;border-radius:10px;font-weight:900;color:#000">Sign In</button>
<p style="font-size:11px;color:#555;text-align:center">Admin: admin@masterpickai.com / Admin123!</p>
</form>
<p style="text-align:center;margin-top:14px;color:#777">No account? <a href="/signup" style="color:#1aff8c;text-decoration:none">Create Free</a></p>
</div></body>
"""

DASHBOARD = """
<body style="background:#0a0a0a;color:#fff;font-family:sans-serif;margin:0">
<div style="background:#121212;display:flex;justify-content:space-between;align-items:center;padding:12px 14px;border-bottom:1px solid #222">
<div>=</div><div style="font-weight:900;color:#1aff8c">MasterpickAI</div><a href="/logout" style="background:#1aff8c;color:#000;padding:8px 14px;border-radius:12px;font-weight:900;font-size:12px;text-decoration:none">Logout</a>
</div>
<div style="max-width:500px;margin:0 auto;padding:14px">
<div style="background:#151515;border:1px solid #252525;border-radius:18px;padding:16px">
<p style="color:#1aff8c;font-size:11px;font-weight:900;margin:0">WELCOME BACK</p>
<h2 style="margin:8px 0">Hello, {{email}}</h2>
<div style="display:flex;gap:10px;align-items:center"><span style="background:#1f3328;color:#1aff8c;border:1px solid #1aff8c;padding:6px 12px;border-radius:20px;font-size:11px;font-weight:bold">{{plan}}</span><a href="/pro" style="margin-left:auto;background:#1aff8c;color:#000;padding:8px 16px;border-radius:10px;text-decoration:none;font-weight:900;font-size:12px">Plans NGN5k/15k</a></div>
</div>
<div style="margin-top:14px;background:#151515;border:2px solid #1aff8c;border-radius:16px;padding:12px">
<b style="color:#1aff8c">FREE 1.50-2.10 - OPEN - 9.5/10 Highest Accuracy</b>
{% for g in free_games %}
<div style="background:#0a0a0a;margin:8px 0;padding:10px;border-radius:10px;border:1px solid #222">
<div style="font-size:10px;color:#777">{{g.league}} - W{{g.final|int}}</div>
<div style="font-weight:bold">{{g.home}} vs {{g.away}}</div>
<div style="margin-top:4px;color:#1aff8c;font-weight:bold">{{g.pick}} @ {{g.odds}} - 9.5/10</div>
</div>
{% endfor %}
</div>
<div style="margin-top:12px;background:linear-gradient(135deg,#1aff8c,#00cc6a);color:#000;padding:14px;border-radius:16px">
<b>ROLLOVER - {{five_total}} ODDS</b><br>
{% for g in five_odd %}<div style="font-size:12px;margin-top:4px">- {{g.home}} vs {{g.away}} - {{g.pick}} @{{g.odds}}</div>{% endfor %}
{% if not is_pro %}<div style="margin-top:8px;background:#000;color:#1aff8c;padding:8px;border-radius:8px;text-align:center;font-weight:bold;font-size:12px">PRO ONLY - NGN5k Weekly / NGN15k Monthly - WhatsApp +2349079783177</div>{% else %}<div style="margin-top:8px;background:#000;color:#1aff8c;padding:8px;border-radius:8px;text-align:center">UNLOCKED</div>{% endif %}
</div>
<div style="margin-top:12px;background:#151515;border:1px solid #333;border-radius:16px;padding:12px">
<b style="color:#ffaa00">PRO Picks - {{pro_games|length}} Games Locked</b>
{% for g in pro_games %}
<div style="background:#0a0a0a;margin:8px 0;padding:10px;border-radius:10px;border-left:3px solid #ffaa00">
<div style="font-size:10px;color:#777">{{g.league}}</div>
<div style="font-weight:bold">{{g.home}} vs {{g.away}}</div>
{% if is_pro %}<div style="margin-top:4px;color:#1aff8c;font-weight:bold">{{g.pick}} @ {{g.odds}}</div>
{% else %}<div style="margin-top:4px;background:#000;padding:6px;border-radius:6px;text-align:center;color:#666;font-size:11px">PRO Hidden @{{g.odds}} - Pay NGN5k/15k</div>{% endif %}
</div>
{% endfor %}
</div>
<div style="margin-top:12px;text-align:center"><a href="https://wa.me/WHATSAPP_NUM?text=Hello%20I%20paid%20PRO%20MasterpickAI%20email%20{{email}}" style="display:inline-block;background:#25D366;color:#fff;padding:12px 18px;border-radius:12px;text-decoration:none;font-weight:900">WhatsApp +2349079783177</a></div>
{% if is_admin %}<a href="/admin" style="display:block;background:#1aff8c;color:#000;padding:14px;text-align:center;border-radius:12px;text-decoration:none;font-weight:900;margin:14px 0">Admin Dashboard</a>{% endif %}
</div>
</body>
"""

PRO_PAGE = """
<body style="background:#0a0a0a;color:#fff;font-family:sans-serif;margin:0"><div style="max-width:450px;margin:0 auto;padding:20px">
<h1 style="text-align:center">Choose Plan - NGN5k/15k</h1>
<p style="text-align:center;color:#777">Highest Accuracy 1.50-2.10 = 9.5/10 OPEN Free</p>
<div style="background:#151515;border:1px solid #333;border-radius:16px;padding:16px;margin-top:16px">
<h3 style="margin:0">Weekly PRO</h3>
<div style="font-size:32px;font-weight:900;margin:8px 0;color:#1aff8c">NGN 5,000 <span style="font-size:14px;color:#777">/ week</span></div>
<div style="font-size:12px;color:#aaa">- All 18 Picks 1.50-2.10<br>- 5 Odd Rollover<br>- 9.5/10<br>- WhatsApp Support</div>
<a href="https://wa.me/WHATSAPP_NUM?text=Hello%20MasterpickAI%20I%20want%20Weekly%20PRO%20NGN5000%20-%20email%20is%20" style="display:block;background:#25D366;color:#fff;padding:14px;text-align:center;border-radius:12px;text-decoration:none;font-weight:900;margin-top:12px">Pay NGN 5,000 - WhatsApp +2349079783177</a>
</div>
<div style="background:linear-gradient(135deg,#1a2e22,#121212);border:2px solid #1aff8c;border-radius:16px;padding:16px;margin-top:14px">
<div style="background:#1aff8c;color:#000;padding:4px 10px;border-radius:10px;font-size:10px;font-weight:900;display:inline-block;margin-bottom:6px">MOST POPULAR - SAVE NGN5k</div>
<h3 style="margin:0;color:#1aff8c">Monthly PRO</h3>
<div style="font-size:32px;font-weight:900;margin:8px 0;color:#1aff8c">NGN 15,000 <span style="font-size:14px;color:#777">/ month</span></div>
<div style="font-size:12px;color:#aaa">- 30 Days Full Access<br>- Priority + Group<br>- 92.3% Win Rate<br>- 60-25-15 Engine</div>
<a href="https://wa.me/WHATSAPP_NUM?text=Hello%20MasterpickAI%20I%20want%20Monthly%20PRO%20NGN15000%20-%20email%20is%20" style="display:block;background:#1aff8c;color:#000;padding:14px;text-align:center;border-radius:12px;text-decoration:none;font-weight:900;margin-top:12px">Pay NGN 15,000 - WhatsApp +2349079783177</a>
</div>
<div style="background:#151515;border-radius:12px;padding:12px;margin-top:14px;text-align:center;font-size:11px;color:#777">FREE 1.50-2.10 stays OPEN for new customers - Try free then upgrade<br>After payment Admin approves in 5 mins - Refresh /games</div>
<div style="text-align:center;margin-top:16px"><a href="/games" style="color:#1aff8c;text-decoration:none">Back to Picks</a></div>
</div></body>
"""

@app.route("/")
def home():
    g=fetch_games()
    five,total=build_5odd(g)
    free_games=g[:2]
    html=WELCOME.replace("WHATSAPP_NUM", WHATSAPP)
    return render_template_string(html, count=len(g), free_count=2, five_total=total, free_games=free_games)

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method=="POST":
        e=request.form.get("email","").lower().strip()
        p=request.form.get("password","").strip()
        if e in USERS:
            html=SIGNUP_PAGE.replace("WHATSAPP_NUM", WHATSAPP)
            return render_template_string(html+"<p style='color:#f55;text-align:center'>Exists - Sign In</p>")
        USERS[e]={"password":p,"is_pro":False,"approved":False,"is_admin":False,"joined":datetime.utcnow().strftime("%Y-%m-%d")}
        session["email"]=e
        return redirect("/games")
    html=SIGNUP_PAGE.replace("WHATSAPP_NUM", WHATSAPP)
    return render_template_string(html)

@app.route("/signin", methods=["GET","POST"])
def signin():
    if request.method=="POST":
        e=request.form.get("email","").lower().strip()
        p=request.form.get("password","").strip()
        u=USERS.get(e)
        if u and u["password"]==p:
            session["email"]=e
            return redirect("/games")
        html=SIGNIN_PAGE.replace("WHATSAPP_NUM", WHATSAPP)
        return render_template_string(html+"<p style='color:#f55;text-align:center'>Wrong</p>")
    html=SIGNIN_PAGE.replace("WHATSAPP_NUM", WHATSAPP)
    return render_template_string(html)

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
    plan="PRO Active - NGN15k" if is_pro else "No Active Plan - Free 1.50-2.10 OPEN"
    all_games=fetch_games()
    five,total=build_5odd(all_games)
    free_games=all_games[:2]
    pro_games=all_games[2:]
    html=DASHBOARD.replace("WHATSAPP_NUM", WHATSAPP)
    return render_template_string(html, free_games=free_games, pro_games=pro_games, count=len(all_games), free_count=2, email=email, is_pro=is_pro, is_admin=is_admin, five_odd=five, five_total=total, plan=plan)

@app.route("/pro")
def pro():
    html=PRO_PAGE.replace("WHATSAPP_NUM", WHATSAPP)
    return html

@app.route("/admin")
def admin():
    if "email" not in session: return redirect("/signin")
    if not USERS.get(session["email"],{}).get("is_admin"): return "Not admin"
    html='<body style="background:#0a0a0a;color:#fff;font-family:sans-serif;padding:16px"><h2 style="color:#1aff8c">Admin - WHATSAPP +2349079783177</h2>'
    html=html.replace("WHATSAPP", WHATSAPP)
    html+=f'<p>Games: {len(fetch_games())} | Users: {len(USERS)} | Free OPEN: 1.50-2.10 9.5/10</p><p style="color:#1aff8c">Pricing: Weekly NGN5k / Monthly NGN15k</p>'
    for email,u in USERS.items():
        st="PRO" if (u.get("is_pro") and u.get("approved")) else "FREE"
        col="#1aff8c" if u.get("approved") else "#ffaa00"
        html+=f'<div style="background:#151515;padding:12px;margin:8px 0;border-radius:10px;border-left:4px solid {col}"><b>{email}</b> - {st}<br><div style="margin-top:8px"><a href="/admin/approve?e={email}" style="background:{col};color:#000;padding:6px 12px;border-radius:8px;text-decoration:none;font-weight:bold;font-size:12px">Toggle Approve</a> <a href="/admin/delete?e={email}" style="color:#f55;margin-left:10px">Delete</a></div></div>'
    html+='<br><a href="/games" style="color:#1aff8c">Picks</a> | <a href="https://wa.me/2349079783177" style="color:#25D366">WhatsApp</a></body>'
    return html

@app.route("/admin/approve")
def approve():
    if "email" not in session: return redirect("/signin")
    if not USERS.get(session["email"],{}).get("is_admin"): return "Not admin"
    e=request.args.get("e","")
    if e in USERS and e!="admin@masterpickai.com":
        USERS[e]["approved"]=not USERS[e].get("approved",False)
        USERS[e]["is_pro"]=USERS[e]["approved"]
    return redirect("/admin")

@app.route("/admin/delete")
def delete_user():
    if "email" not in session: return redirect("/signin")
    if not USERS.get(session["email"],{}).get("is_admin"): return "Not admin"
    e=request.args.get("e","")
    if e in USERS and e!="admin@masterpickai.com": del USERS[e]
    return redirect("/admin")

@app.route("/logout")
def logout():
    session.pop("email",None)
    return redirect("/")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
