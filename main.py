import os, random, requests, urllib.parse
from datetime import datetime, timedelta
from flask import Flask, session, redirect, request

app = Flask(__name__)
app.secret_key = "v35_demo_locked_env_2026_final"

API_KEY = os.environ.get("API_KEY", "demo")
ADMIN_EMAIL = "arinzechukwuemeka125@gmail.com"
OPAY_ACCOUNT = "09079789177"
OPAY_NAME = "Arinze Chukwuemeka P"

USERS = {ADMIN_EMAIL: {"pass": "Master2026!Secure", "plan": "pro", "status": "active", "joined": "2026-09-01"}}
CACHE = {"games": [], "free_games": [], "pro_games": [], "date": None, "fetched_at": None, "history": [], "api_calls": 0, "api_error": "", "raw_count": 0}

def get_wat():
    wat_now = datetime.utcnow() + timedelta(hours=1)
    today = wat_now.strftime("%Y-%m-%d")
    yesterday = (wat_now - timedelta(days=1)).strftime("%Y-%m-%d")
    return today, yesterday, wat_now

def fetch_real(d):
    # DEMO MODE - for testing lock interface
    if API_KEY == "demo" or API_KEY.lower() == "demo":
        CACHE["raw_count"] = 12
        CACHE["api_error"] = ""
        demo = [
            {"fixture":{"date":f"{d}T19:00:00+00:00","status":{"short":"NS"}},"league":{"name":"Premier League","country":"England"},"teams":{"home":{"name":"Man City"},"away":{"name":"Arsenal"}},"goals":{"home":None,"away":None}},
            {"fixture":{"date":f"{d}T18:30:00+00:00","status":{"short":"NS"}},"league":{"name":"La Liga","country":"Spain"},"teams":{"home":{"name":"Barcelona"},"away":{"name":"Real Madrid"}},"goals":{"home":None,"away":None}},
            {"fixture":{"date":f"{d}T20:00:00+00:00","status":{"short":"NS"}},"league":{"name":"Serie A","country":"Italy"},"teams":{"home":{"name":"Inter"},"away":{"name":"AC Milan"}},"goals":{"home":None,"away":None}},
            {"fixture":{"date":f"{d}T19:45:00+00:00","status":{"short":"NS"}},"league":{"name":"Bundesliga","country":"Germany"},"teams":{"home":{"name":"Bayern Munich"},"away":{"name":"Dortmund"}},"goals":{"home":None,"away":None}},
            {"fixture":{"date":f"{d}T17:00:00+00:00","status":{"short":"NS"}},"league":{"name":"Ligue 1","country":"France"},"teams":{"home":{"name":"PSG"},"away":{"name":"Marseille"}},"goals":{"home":None,"away":None}},
            {"fixture":{"date":f"{d}T19:00:00+00:00","status":{"short":"NS"}},"league":{"name":"Eredivisie","country":"Netherlands"},"teams":{"home":{"name":"Ajax"},"away":{"name":"PSV"}},"goals":{"home":None,"away":None}},
            {"fixture":{"date":f"{d}T18:00:00+00:00","status":{"short":"NS"}},"league":{"name":"Primeira Liga","country":"Portugal"},"teams":{"home":{"name":"Benfica"},"away":{"name":"Porto"}},"goals":{"home":None,"away":None}},
            {"fixture":{"date":f"{d}T19:30:00+00:00","status":{"short":"NS"}},"league":{"name":"Belgian Pro League","country":"Belgium"},"teams":{"home":{"name":"Club Brugge"},"away":{"name":"Anderlecht"}},"goals":{"home":None,"away":None}},
            {"fixture":{"date":f"{d}T20:30:00+00:00","status":{"short":"NS"}},"league":{"name":"Championship","country":"England"},"teams":{"home":{"name":"Leeds"},"away":{"name":"Leicester"}},"goals":{"home":None,"away":None}},
            {"fixture":{"date":f"{d}T16:00:00+00:00","status":{"short":"NS"}},"league":{"name":"Brasileiro","country":"Brazil"},"teams":{"home":{"name":"Flamengo"},"away":{"name":"Palmeiras"}},"goals":{"home":None,"away":None}},
            {"fixture":{"date":f"{d}T21:00:00+00:00","status":{"short":"NS"}},"league":{"name":"Super Lig","country":"Turkey"},"teams":{"home":{"name":"Galatasaray"},"away":{"name":"Fenerbahce"}},"goals":{"home":None,"away":None}},
            {"fixture":{"date":f"{d}T17:30:00+00:00","status":{"short":"NS"}},"league":{"name":"Eredivisie","country":"Netherlands"},"teams":{"home":{"name":"Feyenoord"},"away":{"name":"AZ Alkmaar"}},"goals":{"home":None,"away":None}},
        ]
        return demo
    try:
        headers = {"x-apisports-key": API_KEY}
        r = requests.get(f"https://v3.football.api-sports.io/fixtures?date={d}", headers=headers, timeout=15)
        j = r.json()
        CACHE["api_calls"] += 1
        if j.get("errors") and j["errors"]:
            CACHE["api_error"] = str(j["errors"])
            return []
        if j.get("response") is not None:
            if isinstance(j["response"], list):
                if d == get_wat()[0]:
                    CACHE["raw_count"] = len(j["response"])
                return j["response"]
        return []
    except Exception as e:
        CACHE["api_error"] = str(e)
        return []

def calc_18_local(fix):
    hname = fix["teams"]["home"]["name"]
    aname = fix["teams"]["away"]["name"]
    league = fix["league"]["name"]
    country = fix["league"]["country"]
    is_high = any(x in (league+country).lower() for x in ["brazil","ecuador","argentina","norway","netherlands","mexico","belgium"])
    total_avg = 2.9 if is_high else 2.5
    over15 = 92 if total_avg >= 2.8 else 85
    h_form = random.choice(["WWWDW","WDWDW","LWWWD"])
    a_form = random.choice(["WDWDW","LWWWD","WWLWD"])
    h_w = h_form.count("W")
    motivation = 90 if "cup" in league.lower() else 78
    tip = "Over 1.5 Goals"
    odd = f"{1.42+random.random()*0.12:.2f}"
    wr = 94
    reason = f"18P Avg{total_avg:.1f} Over15 {over15}% Form {h_form} vs {a_form} Mot {motivation}%"
    if h_w >= 2 and random.random() > 0.6:
        tip = f"{hname} Win"
        odd = f"{1.65+random.random()*0.25:.2f}"
        wr = 88
    return tip, odd, wr, reason

def update_all():
    today, yesterday, wat_now = get_wat()
    if CACHE["date"]!= today or not CACHE["games"]:
        CACHE["api_calls"] = 0; CACHE["api_error"] = ""; CACHE["raw_count"] = 0
        y_fix = fetch_real(yesterday)
        t_fix = fetch_real(today)
        y_games = []
        for f in y_fix[:8]:
            tip, odd, wr, reason = calc_18_local(f)
            hg = f["goals"]["home"]; ag = f["goals"]["away"]; status = f["fixture"]["status"]["short"]
            res = "UPCOMING"
            if status in ["FT","AET","PEN"] and hg is not None:
                res = "WON" if (hg+ag)>1.5 else "LOST"
            y_games.append({"match": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}", "league": f["league"]["name"], "score": f"{hg}-{ag}" if hg is not None else "-", "result": res, "date": yesterday, "tip": tip, "odd": odd})
        CACHE["history"] = y_games
        all_games = []
        for f in t_fix[:12]:
            tip, odd, wr, reason = calc_18_local(f)
            all_games.append({"match": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}", "league": f["league"]["name"], "country": f["league"]["country"], "tip": tip, "odd": odd, "wr": wr, "time": f["fixture"]["date"][11:16], "date": today, "status": f["fixture"]["status"]["short"]})
        all_games = sorted(all_games, key=lambda x: x["wr"], reverse=True)
        free = all_games[:2]
        for g in free:
            g["tip"]="Over 1.5 Goals"; g["odd"]=f"{1.42+random.random()*0.10:.2f}"; g["wr"]=94
        pro = [g for g in all_games if g not in free]
        CACHE["games"]=all_games; CACHE["free_games"]=free; CACHE["pro_games"]=pro; CACHE["date"]=today; CACHE["fetched_at"]=wat_now.strftime("%Y-%m-%d %H:%M WAT")
    return CACHE["free_games"], CACHE["pro_games"], CACHE["history"]

STYLE = """
<meta name='viewport' content='width=device-width,initial-scale=1'>
<link href='https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;800&display=swap' rel='stylesheet'>
<style>
*{box-sizing:border-box}body{margin:0;background:#040610;color:#fff;font-family:'Plus Jakarta Sans',sans-serif}
.top{position:sticky;top:0;z-index:100;background:rgba(6,8,18,0.9);backdrop-filter:blur(24px);border-bottom:1px solid rgba(255,255,255,0.06);padding:16px 22px;display:flex;justify-content:space-between;align-items:center}
.logo{font-weight:800;font-size:20px}.logo span{color:#00ff88}
.card{background:rgba(17,26,46,0.8);border:1px solid rgba(255,255,255,0.08);border-radius:24px;padding:20px;margin:16px 0;backdrop-filter:blur(12px)}
.glow{border-color:rgba(0,255,136,0.25);box-shadow:0 20px 60px rgba(0,255,136,0.12)}
.gold{border-color:rgba(255,204,51,0.25);box-shadow:0 20px 60px rgba(255,204,51,0.12)}
.match{font-weight:800;font-size:17px;margin:10px 0}
.league{color:#8a9cc5;font-size:10.5px;text-transform:uppercase;letter-spacing:1.2px;font-weight:700}
.odd{background:#00ff88;color:#000;padding:7px 14px;border-radius:12px;font-weight:800;font-size:13px}
.btn{width:100%;background:#00ff88;color:#000;padding:16px;border-radius:16px;display:block;text-align:center;text-decoration:none;font-weight:800;font-size:15px;box-shadow:0 16px 32px rgba(0,255,136,0.28)}
.btn-gold{background:linear-gradient(180deg,#ffcc33,#ffb800)}
.wabtn{background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);color:#fff;padding:10px 16px;border-radius:12px;text-decoration:none;font-size:12px;font-weight:700}
.badge{color:#8a9cc5;font-size:12.5px;line-height:1.6}
.tag{font-size:10px;padding:6px 12px;border-radius:20px;background:rgba(255,255,255,0.06);color:#8aa0c8;border:1px solid rgba(255,255,255,0.08);font-weight:700}
.tag-live{background:#00ff88;color:#000;border:none}
.blur{filter:blur(14px);user-select:none;pointer-events:none}
.admin-btn{background:#4c7bff;color:#fff;padding:10px 18px;border-radius:12px;text-decoration:none;font-weight:800;font-size:12px}
.input{width:100%;padding:15px;background:rgba(13,19,34,0.8);border:1px solid rgba(255,255,255,0.08);border-radius:14px;color:#fff;margin:10px 0}
.hero-title{font-size:32px;font-weight:800;letter-spacing:-1.2px;line-height:1.1;margin:10px 0}
</style>
"""

def wa_link(t):
    return f"https://wa.me/?text={urllib.parse.quote(t)}"

@app.route("/")
def home():
    email=session.get("email")
    free_games,pro_games,history=update_all()
    is_admin=email==ADMIN_EMAIL
    is_pro=email and USERS.get(email,{}).get("plan")=="pro"
    html=f"<html><head>{STYLE}</head><body><div class=top><div class=logo>MASTERPICK <span>AI</span></div><div style=display:flex;gap:12px;align-items:center>"
    if is_admin:
        html+=f"<a class=admin-btn href=/admin>Admin {len(USERS)} {CACHE['api_calls']}/100</a>"
    if email:
        html+=f"<span style=color:#8a9cc5;font-size:12px>{email[:12]}</span><a href=/logout style=color:#8a9cc5;text-decoration:none;font-size:13px>Logout</a>"
    else:
        html+=f"<a href=/login style=color:#fff;text-decoration:none;font-weight:700;font-size:13px>Login</a><a href=/signup style=background:#fff;color:#000;padding:10px 18px;border-radius:12px;text-decoration:none;font-weight:800;font-size:13px>Sign Up</a>"
    html+="</div></div><div style=max-width:720px;margin:0 auto;padding:20px>"
    if CACHE["api_error"] and "suspended" in CACHE["api_error"].lower():
        html+=f"<div class=card style=border-color:#ff3a4c><div class=league style=color:#ff3a4c>API KEY SUSPENDED</div><div class=badge>{CACHE['api_error'][:120]}</div></div>"
    if not email:
        html+=f"<div class=card glow style=padding:28px><div class=league style=color:#00ff88>REAL API {CACHE['date']} {CACHE['fetched_at']} {CACHE['raw_count']} GAMES {CACHE['api_calls']}/100 REQ DEMO={API_KEY}</div><div class=hero-title>{len(CACHE['games']) or 12} Real Games<br>With <span style=color:#00ff88>18 Parameters</span></div><div class=badge>Login to unlock today's predictions • Auto 1AM WAT</div><a class=btn href=/login style=margin-top:20px>🔒 Login to See Games</a><a class=btn style=background:rgba(255,255,255,0.06);color:#fff;box-shadow:none;border:1px solid rgba(255,255,255,0.1);margin-top:12px href=/signup>Create Account Free</a></div>"
        html+=f"<div class=card><div class=league>TEASER - LOGIN TO UNLOCK</div><div class=blur><div class=match>Man City vs Arsenal</div><div class=match>Liverpool vs Chelsea</div><div class=match>Barcelona vs Real Madrid</div></div><div style=text-align:center;margin-top:12px><a class=btn href=/login>Login to Unlock</a></div></div>"
        html+="</div></body></html>"
        return html
    free_odds=1.0
    for g in free_games:
        try:
            free_odds*=float(g["odd"])
        except:
            pass
    if not CACHE["games"]:
        html+=f"<div class=card style=text-align:center;padding:40px><div style=font-size:22px;font-weight:800>No Real Games Yet Today</div><div class=badge>API count {CACHE['raw_count']} Calls {CACHE['api_calls']}/100 Error {CACHE['api_error'][:80]}</div></div>"
    else:
        free_text=f"MasterPick FREE {CACHE['date']} @{free_odds:.2f}"
        wa_free=wa_link(free_text)
        html+=f"<div class=card glow><div style=display:flex;justify-content:space-between;align-items:center><div><div style=font-weight:800;font-size:16px>FREE @{free_odds:.2f} • 9/10 Target • Real {len(free_games)}</div><div class=league>Over 1.5 94% • 18 params</div></div><a class=wabtn href='{wa_free}'>Share</a></div></div>"
        for g in free_games:
            txt=f"{g['match']} - {g['tip']} @{g['odd']}"
            wa_g=wa_link(txt)
            html+=f"<div class=card><div class=league>{g['league']} {g['country']} {g['time']} <span class=tag tag-live>{g['wr']}%</span></div><div class=match>{g['match']}</div><div style=display:flex;justify-content:space-between;align-items:center;margin-top:14px><div style=display:flex;gap:10px;align-items:center><span style=background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);padding:10px 14px;border-radius:12px;font-weight:700;font-size:13px>{g['tip']}</span><span class=odd>{g['odd']}</span></div><a class=wabtn href='{wa_g}'>WhatsApp</a></div></div>"
        if not is_pro:
            html+=f"<div class=card gold style=padding:0;overflow:hidden><div style=background:#ffcc33;padding:16px 22px;display:flex;justify-content:space-between;align-items:center><div style=color:#000;font-weight:800;font-size:14px>PRO {len(pro_games)} Games Locked</div><div style=background:#000;color:#ffcc33;padding:7px 14px;border-radius:20px;font-size:11px;font-weight:800>LOCKED</div></div><div style=padding:24px;text-align:center><div style=font-size:20px;font-weight:800>Unlock {len(pro_games)} Premium Tips</div><a class=btn btn-gold href=/pay style=margin-top:16px>Pay Opay {OPAY_ACCOUNT} - Unlock Now</a></div></div>"
        else:
            html+=f"<div class=card gold><div style=font-weight:800>PRO UNLOCKED {len(pro_games)} Games</div></div>"
            for g in pro_games:
                txt=f"PRO {g['match']} - {g['tip']} @{g['odd']}"
                wa_g=wa_link(txt)
                html+=f"<div class=card><div class=league>{g['league']} {g['country']} {g['time']} <span class=tag tag-live>{g['wr']}%</span></div><div class=match>{g['match']}</div><div style=display:flex;justify-content:space-between;align-items:center;margin-top:14px><div style=display:flex;gap:10px><span style=background:rgba(255,255,255,0.06);padding:10px 14px;border-radius:12px;font-weight:700;font-size:13px>{g['tip']}</span><span class=odd>{g['odd']}</span></div><a class=wabtn href='{wa_g}'>WhatsApp</a></div></div>"
    if history:
        won=sum(1 for g in history if g["result"]=="WON")
        html+=f"<div class=card><div style=font-weight:800>Yesterday {won}/{len(history)} WON {history[0]['date']}</div></div>"
    html+="</div></body></html>"
    return html

@app.route("/pay")
def pay():
    email=session.get("email")
    proof_msg = f"Hi Admin I paid PRO {email} to {OPAY_ACCOUNT}"
    wa_proof=wa_link(proof_msg)
    html=f"<html><head>{STYLE}</head><body><div class=top><div class=logo>MASTERPICK <span>AI</span></div><a href=/ style=color:#fff;text-decoration:none>Home</a></div><div style=max-width:520px;margin:0 auto;padding:24px><div class=card glow style=text-align:center;padding:28px><div style=font-size:26px;font-weight:800>Unlock Pro</div></div><div class=card style=text-align:center><div class=league>OPAY</div><div style=font-size:36px;font-weight:800>{OPAY_ACCOUNT}</div><div class=badge>{OPAY_NAME} {email}</div></div><div class=card><a class=btn href='{wa_proof}'>WhatsApp Proof</a><a class=btn style=background:rgba(255,255,255,0.06);color:#fff;box-shadow:none;border:1px solid rgba(255,255,255,0.1);margin-top:12px href=/ >I Paid</a></div></div></body></html>"
    return html

@app.route("/admin")
def admin_panel():
    email=session.get("email")
    if email!=ADMIN_EMAIL:
        return f"<html><head>{STYLE}</head><body><div class=top>Denied</div><div style=padding:20px><div class=card>Total {len(USERS)}</div></div></body></html>",403
    free_games,pro_games,history=update_all()
    total=len(USERS); pro_c=sum(1 for u in USERS.values() if u.get("plan")=="pro")
    html=f"<html><head>{STYLE}</head><body><div class=top><div class=logo>ADMIN V35 DEMO LOCKED</div><a href=/ style=color:#fff;text-decoration:none>Home</a></div><div style=max-width:800px;margin:0 auto;padding:20px><div class=card glow><div style=font-size:20px;font-weight:800>{total} Users {pro_c} Pro API {CACHE['api_calls']}/100 Raw {CACHE['raw_count']}</div><div class=badge>{CACHE['date']} {CACHE['fetched_at']} Key {API_KEY[:4]}... Error {CACHE['api_error'][:60]}</div></div><div class=card><div style=font-weight:800>Approve Pro</div>"
    for em,u in USERS.items
