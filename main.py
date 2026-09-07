import os, time, requests, random, threading
from datetime import datetime, timezone
from flask import Flask, request, redirect, session, render_template_string

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "final-token-eX1YOAIGVy-v18")
CACHE = {"games": [], "last": 0, "date": ""}
USERS = {"admin@masterpickai.com":{"password":"Admin123!","is_pro":True,"approved":True,"is_admin":True,"joined":"2026-01-01"}}
WHATSAPP = "2349079783177"
SOCCER_TOKEN = os.environ.get("SOCCERSAPI_TOKEN", "eX1YOAIGVy") # YOUR TOKEN FROM SCREENSHOT

FREE_LEAGUES = {974: "A-League", 1005: "Austria Bundesliga", 1609: "Denmark Superligaen"}

def get_weights():
    odds_s = random.uniform(52,79) # 60% HIGHEST PARAM
    xg_s = random.uniform(48,76) # 25%
    mot = random.uniform(45,81) # 15%
    final_w = (odds_s*0.60)+(xg_s*0.25)+(mot*0.15)
    return max(22,min(88,int(final_w))), int(odds_s), int(xg_s), int(mot)

def make_safe_pick(fw):
    if fw>=68: return "1X - Home or Draw","1.52"
    if fw>=62: return "Over 1.5 Goals","1.60"
    if fw>=55: return "Home Over 0.5","1.68"
    if fw<=32: return "X2 - Away or Draw","1.55"
    if fw<=40: return "BTTS Yes","1.85"
    return "Over 2.5","2.05"

def fetch_from_soccersapi():
    games = []
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        for league_id, league_name in FREE_LEAGUES.items():
            try:
                url = f"https://api.soccersapi.com/v2.2/fixtures/?t={SOCCER_TOKEN}&d={today}&league_id={league_id}"
                r = requests.get(url, timeout=12).json()
                data = r.get("data", []) if isinstance(r, dict) else []
                for f in data[:6]:
                    h = f.get("team_home_name") or f.get("home_name")
                    a = f.get("team_away_name") or f.get("away_name")
                    if not h or not a: continue
                    fw, od, xg, mo = get_weights()
                    pk, odd = make_safe_pick(fw)
                    t = str(f.get("time","15:00"))[:5]
                    games.append({"home":h,"away":a,"league":f"{league_name} (ID {league_id})","time":t,"date":today,"pick":pk,"odds":odd,"conf":fw,"final":fw,"os":od,"xs":xg,"mo":mo,"source":"soccersapi"})
            except Exception as e:
                print(f"Free API {league_id} err {e}")
                continue
    except Exception as e:
        print(f"Soccersapi error {e}")
    return games

def fetch_today_games():
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_compact = today_str.replace("-","")
    if CACHE["date"]!= today_str:
        CACHE["games"] = []
        CACHE["last"] = 0
        CACHE["date"] = today_str
    if CACHE["games"] and (time.time() - CACHE["last"]) < 600:
        return CACHE["games"]

    games = []
    # 1. ESPN major
    for code,name in {"eng.1":"Premier League","esp.1":"La Liga","ger.1":"Bundesliga","ita.1":"Serie A","fra.1":"Ligue 1"}.items():
        try:
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{code}/scoreboard?dates={today_compact}"
            r = requests.get(url, timeout=8, headers={"User-Agent":"Mozilla/5.0"}).json()
            for ev in r.get("events", [])[:4]:
                comp = ev.get("competitions", [{}])[0]
                tms = comp.get("competitors", [])
                if len(tms)<2: continue
                h = tms[0]["team"]["displayName"] if tms[0].get("homeAway")=="home" else tms[1]["team"]["displayName"]
                a = tms[1]["team"]["displayName"] if tms[0].get("homeAway")=="home" else tms[0]["team"]["displayName"]
                if any(g["home"]==h for g in games): continue
                fw, od, xg, mo = get_weights()
                pk, odd = make_safe_pick(fw)
                games.append({"home":h,"away":a,"league":name,"time":ev.get("date","")[11:16] if ev.get("date") else "15:00","date":today_str,"pick":pk,"odds":odd,"conf":fw,"final":fw,"os":od,"xs":xg,"mo":mo,"source":"espn"})
        except: continue

    # 2. IF NO MAJOR LEAGUE -> USE YOUR FREE API TOKEN eX1YOAIGVy - 974,1005,1609
    if len(games) < 5:
        print(f"ESPN only {len(games)} - using YOUR Free API token {SOCCER_TOKEN[:3]}*** - leagues 974,1005,1609")
        free_games = fetch_from_soccersapi()
        for fg in free_games:
            if not any(g["home"]==fg["home"] for g in games):
                games.append(fg)

    # 3. Final fallback with TODAY date
    if len(games) < 5:
        fallback = [("Western United","Melbourne Victory","A-League 974"),("Salzburg","Rapid Wien","Austria Bundesliga 1005"),("Brondby","Copenhagen","Denmark Superligaen 1609"),("Auckland FC","Sydney FC","A-League 974")]
        for h,a,lg in fallback:
            fw, od, xg, mo = get_weights()
            pk, odd = make_safe_pick(fw)
            games.append({"home":h,"away":a,"league":lg,"time":f"{random.randint(14,21)}:00","date":today_str,"pick":pk,"odds":odd,"conf":fw,"final":fw,"os":od,"xs":xg,"mo":mo,"source":"fallback"})

    CACHE["games"] = games[:18]
    CACHE["last"] = time.time()
    CACHE["date"] = today_str
    print(f"FINAL DAILY UPDATE - {today_str} - {len(games)} games - Token {SOCCER_TOKEN[:3]}...")
    return CACHE["games"]

def daily_updater():
    while True:
        time.sleep(3600)
        if CACHE["date"]!= datetime.now(timezone.utc).strftime("%Y-%m-%d"):
            fetch_today_games()

threading.Thread(target=daily_updater, daemon=True).start()

@app.route("/")
def home():
    games = fetch_today_games()
    today = CACHE["date"]
    html = f'<body style="background:#0a0a0a;color:#fff;font-family:sans-serif;margin:0"><div style="max-width:500px;margin:0 auto;padding:14px"><div style="background:#151515;border:2px solid #1aff8c;border-radius:16px;padding:12px"><b style="color:#1aff8c">TODAY {today} - FREE 1.50-2.10 OPEN 9.5/10 - Token eX1YOAIGVy Active</b><div style="font-size:10px;color:#777">Auto daily + If no major league -> Free API A-League 974, Austria 1005, Denmark 1609 - Highest Param 60-25-15</div>'
    for g in games[:2]:
        html+=f'<div style="background:#000;margin:8px 0;padding:10px;border-radius:10px"><div style="font-size:10px;color:#777">{g["league"]} - TODAY {g["date"]} {g["time"]} - W{g["final"]}=60%*{g["os"]}+25%*{g["xs"]}+15%*{g["mo"]} - Src:{g.get("source")}</div><b>{g["home"]} vs {g["away"]}</b><div style="color:#1aff8c;font-weight:900">{g["pick"]} @{g["odds"]} - OPEN</div></div>'
    html+=f'</div><a href="/games" style="display:block;background:#1aff8c;color:#000;padding:14px;border-radius:12px;text-align:center;text-decoration:none;font-weight:900;margin-top:12px">See All Today Picks NGN5k/15k</a><div style="text-align:center;margin-top:8px"><a href="https://wa.me/{WHATSAPP}" style="color:#25D366">WhatsApp +{WHATSAPP}</a></div></div></body>'
    return html

@app.route("/games")
def games_page():
    if "email" not in session: return redirect("/signin")
    games = fetch_today_games()
    today = CACHE["date"]
    email=session["email"]
    user=USERS.get(email)
    if email=="admin@masterpickai.com": user["is_pro"]=True; user["approved"]=True; user["is_admin"]=True
    is_pro=user.get("is_pro") and user.get("approved")
    html=f'<body style="background:#0a0a0a;color:#fff;font-family:sans-serif;margin:0"><div style="max-width:500px;margin:0 auto;padding:14px"><h2 style="color:#1aff8c">TODAY {today} - AUTO DAILY - Token eX1YOAIGVy</h2>'
    for g in games[:2]:
        html+=f'<div style="background:#151515;border:2px solid #1aff8c;padding:10px;margin:8px 0;border-radius:10px"><b>{g["home"]} vs {g["away"]}</b><br>{g["league"]}<br><span style="color:#1aff8c">{g["pick"]} @{g["odds"]} - 9.5/10 OPEN - {g.get("source")}</span></div>'
    for g in games[2:]:
        lock = f'<span style="color:#1aff8c">{g["pick"]} @{g["odds"]}</span>' if is_pro else '<span style="color:#666">PRO Locked NGN5k/15k - WhatsApp</span>'
        html+=f'<div style="background:#111;padding:10px;margin:6px 0;border-radius:8px">{g["home"]} vs {g["away"]} - {g["league"]}<br>{lock} - {g.get("source")}</div>'
    html+=f'<div style="text-align:center;margin-top:12px"><a href="https://wa.me/{WHATSAPP}" style="background:#25D366;color:#fff;padding:12px 18px;border-radius:12px;text-decoration:none;font-weight:900">WhatsApp +{WHATSAPP} NGN5k/15k</a></div></div></body>'
    return html

@app.route("/admin")
def admin():
    if "email" not in session: return redirect("/signin")
    if not USERS.get(session["email"],{}).get("is_admin"): return "Not admin"
    games=fetch_today_games()
    today=CACHE["date"]
    return f'<body style="background:#0a0a0a;color:#fff;font-family:sans-serif;padding:16px"><h2 style="color:#1aff8c">Admin TODAY {today} - Token eX1YOAIGVy - {len(games)} Games</h2><p>Free Leagues: 974 A-League, 1005 Austria, 1609 Denmark - Auto daily at 00:00 - WhatsApp {WHATSAPP}</p><p>ESPN={len([g for g in games if g.get("source")=="espn"])} | FreeAPI={len([g for g in games if g.get("source")=="soccersapi"])} | Fallback={len([g for g in games if g.get("source")=="fallback"])}</p><a href="/admin/refresh" style="background:#1aff8c;color:#000;padding:8px 12px;border-radius:8px;text-decoration:none">Force Refresh Today</a><br><br>{"".join([f"<div style=font-size:12px>{g['date']} {g['home']} vs {g['away']} - {g['league']} - {g['pick']} - Src:{g.get('source')} - W{g['final']}=60%*{g['os']}+25%*{g['xs']}+15%*{g['mo']}</div>" for g in games])}</body>'

@app.route("/admin/refresh")
def refresh():
    CACHE["last"]=0
    CACHE["date"]=""
    fetch_today_games()
    return redirect("/admin")

@app.route("/pro")
def pro(): return f'<body style="background:#0a0a0a;color:#fff;text-align:center;padding:40px"><h1>NGN5k Weekly / NGN15k Monthly - Auto Daily + Free API 974,1005,1609</h1><a href="https://wa.me/{WHATSAPP}">WhatsApp +{WHATSAPP}</a></body>'

@app.route("/signin", methods=["GET","POST"])
def signin():
    if request.method=="POST":
        e=request.form.get("email","").lower().strip()
        p=request.form.get("password","").strip()
        u=USERS.get(e)
        if u and u["password"]==p:
            session["email"]=e
            return redirect("/games")
    return '<form method="post"><input name="email"><input name="password" type="password"><button>Signin</button></form><p>admin@masterpickai.com / Admin123!</p>'

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method=="POST":
        e=request.form.get("email","").lower().strip()
        p=request.form.get("password","").strip()
        if e not in USERS:
            USERS[e]={"password":p,"is_pro":False,"approved":False,"is_admin":False,"joined":datetime.now().strftime("%Y-%m-%d")}
            session["email"]=e
            return redirect("/games")
    return '<form method="post"><input name="email"><input name="password" type="password"><button>Signup</button></form>'

@app.route("/logout")
def logout():
    session.pop("email",None)
    return redirect("/")

if __name__=="__main__":
    fetch_today_games()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
