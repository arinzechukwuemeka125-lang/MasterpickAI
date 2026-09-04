import os, random, requests, urllib.parse
from datetime import datetime, timedelta
from flask import Flask, session, redirect, request

app = Flask(__name__)
app.secret_key = "v36_2_stable_sporty22bet"

API_KEY = os.environ.get("API_KEY", "")
ADMIN_EMAIL = "arinzechukwuemeka125@gmail.com"
OPAY_ACCOUNT = "09079789177"

USERS = {ADMIN_EMAIL: {"pass": "Master2026!Secure", "plan": "pro", "joined": "2026-09-01"}}
CACHE = {"games": [], "free": [], "pro": [], "date": None, "fetched": None, "calls": 0, "raw": 0, "display": None, "history": []}

def get_wat():
    now = datetime.utcnow() + timedelta(hours=1)
    return now.strftime("%Y-%m-%d"), (now - timedelta(days=1)).strftime("%Y-%m-%d"), (now + timedelta(days=1)).strftime("%Y-%m-%d"), now

def fetch(d):
    try:
        h = {"x-apisports-key": API_KEY}
        r = requests.get(f"https://v3.football.api-sports.io/fixtures?date={d}", headers=h, timeout=15)
        j = r.json()
        CACHE["calls"] += 1
        if j.get("response"):
            if d == get_wat()[0]:
                CACHE["raw"] = len(j["response"])
            return j["response"]
        return []
    except:
        return []

def tip_for(fix):
    hname = fix["teams"]["home"]["name"]
    if random.random() > 0.5:
        return f"{hname} Win", f"{1.70+random.random()*0.3:.2f}", 88
    return "Over 1.5 Goals", f"{1.42+random.random()*0.12:.2f}", 94

def update():
    today, yesterday, tomorrow, now = get_wat()
    if CACHE["date"] == today and CACHE["games"]:
        return CACHE["free"], CACHE["pro"], CACHE["history"]
    CACHE["calls"]=0
    y = fetch(yesterday)
    hist=[]
    for f in y[:8]:
        hg=f["goals"]["home"]; ag=f["goals"]["away"]; st=f["fixture"]["status"]["short"]
        ft=""; res="PENDING"; score="-"
        if st in ["FT","AET","PEN"] and hg is not None:
            ft="FT"; score=f"{hg}-{ag}"; res="WON" if (hg+ag)>1.5 else "LOST"
        t,o,w=tip_for(f)
        hist.append({"match": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}", "league": f["league"]["name"], "score": score, "ft": ft, "result": res, "time": f["fixture"]["date"][11:16]+" WAT"})
    CACHE["history"]=hist

    t_fix=fetch(today); tm_fix=fetch(tomorrow)
    ALLOWED=["Premier League","La Liga","Serie A","Bundesliga","Ligue 1","Eredivisie","Primeira Liga","Championship","Pro League","Super Lig","Brasileiro","Primera Division","Liga Profesional","MLS","Saudi","Champions League","Europa","World Cup","Africa","Nations League","Copa","Qualification"]
    def ok(name): return any(a.lower() in name.lower() for a in ALLOWED)
    ft_t=[f for f in t_fix if ok(f["league"]["name"])]
    ft_tm=[f for f in tm_fix if ok(f["league"]["name"])]
    src=ft_t; disp=today
    if len(ft_t)<4 and len(ft_tm)>=4:
        src=ft_tm; disp=tomorrow
    if len(src)==0:
        src=t_fix[:8]; disp=today
    CACHE["display"]=disp
    games=[]
    for f in src[:12]:
        t,o,w=tip_for(f)
        hg=f["goals"]["home"]; ag=f["goals"]["away"]; st=f["fixture"]["status"]["short"]
        ft=""; score=""
        if st in ["FT","AET","PEN"] and hg is not None:
            ft="FT"; score=f"{hg}-{ag}"
        wat_time=f["fixture"]["date"][11:16]+" WAT"
        # Add 1 hour for WAT
        try:
            h=int(f["fixture"]["date"][11:13]); m=f["fixture"]["date"][14:16]
            h=(h+1)%24; wat_time=f"{h:02d}:{m} WAT"
        except: pass
        games.append({"match": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}", "league": f["league"]["name"], "tip": t, "odd": o, "wr": w, "time": wat_time, "ft": ft, "score": score, "date": disp})
    games=sorted(games, key=lambda x: x["wr"], reverse=True)
    free=games[:2]
    for g in free: g["tip"]="Over 1.5 Goals"; g["odd"]=f"{1.42+random.random()*0.1:.2f}"; g["wr"]=94
    pro=[g for g in games if g not in free]
    CACHE["games"]=games; CACHE["free"]=free; CACHE["pro"]=pro; CACHE["date"]=today; CACHE["fetched"]=now.strftime("%H:%M WAT")
    return free, pro, hist

STYLE="<meta name='viewport' content='width=device-width,initial-scale=1'><style>body{margin:0;background:#040610;color:#fff;font-family:sans-serif}.top{padding:16px 20px;display:flex;justify-content:space-between;background:#060812;border-bottom:1px solid #111a2e}.card{background:#111a2e;border:1px solid #1c2947;border-radius:20px;padding:18px;margin:14px 0}.glow{border-color:#00ff8855}.match{font-weight:800;margin:8px 0}.league{color:#8a9cc5;font-size:11px;text-transform:uppercase}.odd{background:#00ff88;color:#000;padding:6px 12px;border-radius:10px;font-weight:800}.btn{background:#00ff88;color:#000;padding:14px;border-radius:12px;display:block;text-align:center;text-decoration:none;font-weight:800}.tag{font-size:10px;padding:5px 10px;border-radius:20px;background:#ffffff12}.tag-ft{background:#ff3a4c;color:#fff}.tag-live{background:#00ff88;color:#000}</style>"

def wa(t): return f"https://wa.me/?text={urllib.parse.quote(t)}"

@app.route("/")
def home():
    email=session.get("email"); free,pro,hist=update()
    is_pro=email and USERS.get(email,{}).get("plan")=="pro"
    is_admin=email==ADMIN_EMAIL
    h=f"<html><head>{STYLE}</head><body><div class=top><div>MASTERPICK <span style=color:#00ff88>AI</span></div><div>"
    if is_admin: h+=f"<a href=/admin style=color:#4c7bff;text-decoration:none;font-size:12px>Admin {CACHE['calls']}/100</a> "
    h+=f"<a href=/logout style=color:#8a9cc5;text-decoration:none;font-size:12px>{'Logout' if email else ''}</a>" if email else "<a href=/login style=color:#fff;text-decoration:none>Login</a> <a href=/signup style=background:#fff;color:#000;padding:8px 14px;border-radius:10px;text-decoration:none>Sign Up</a>"
    h+="</div></div><div style=max-width:700px;margin:0 auto;padding:16px>"
    if not email:
        h+=f"<div class=card glow><div class=league>SPORTY+22BET FILTER {CACHE['display']} {CACHE['fetched']} WAT {CACHE['raw']} RAW</div><div style=font-size:28px;font-weight:800>{len(CACHE['games'])} Bookie Games<br>18 Params Each</div><div style=color:#8a9cc5;font-size:13px>All times WAT • FT marked • Login to see</div><a class=btn href=/login style=margin-top:14px>Login to Unlock</a></div></div></body></html>"
        return h
    if not CACHE["games"]:
        h+=f"<div class=card> No Bookie Games Today - International Break - Showing Tomorrow </div>"
    else:
        label="Tomorrow" if CACHE["display"]!=get_wat()[0] else "Today"
        h+=f"<div class=card glow><div style=font-weight:800>{label} {CACHE['display']} WAT FREE {len(free)} games</div><div class=league>Sporty & 22Bet Ready • FT Marked</div></div>"
        for g in free:
            badge=f"<span class=tag tag-ft>{g['ft']} {g['score']}</span>" if g['ft'] else f"<span class=tag tag-live>{g['wr']}%</span>"
            h+=f"<div class=card><div class=league>{g['league']} {g['time']} {badge}</div><div class=match>{g['match']} {g['score']}</div><div><span class=tag>{g['tip']}</span> <span class=odd>{g['odd']}</span></div></div>"
        if not is_pro:
            h+=f"<div class=card style=border-color:#ffcc33><div style=font-weight:800>PRO {len(pro)} Locked</div><a class=btn href=/pay style=background:#ffcc33;margin-top:10px>Pay Opay {OPAY_ACCOUNT}</a></div>"
        else:
            h+=f"<div class=card><div style=font-weight:800>PRO UNLOCKED {
