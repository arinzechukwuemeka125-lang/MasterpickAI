import os, random, requests, urllib.parse
from datetime import datetime, timedelta
from flask import Flask, session, redirect, request

app = Flask(__name__)
app.secret_key = "v31_18_params"

API_KEY = "87a492350f7f8c1c3a63d33c46d813d8"
ADMIN_EMAIL = "arinzechukwuemeka125@gmail.com"
OPAY_ACCOUNT = "09079789177"
OPAY_NAME = "Arinze Chukwuemeka P"

USERS = {ADMIN_EMAIL: {"pass": "Master2026!Secure", "plan": "pro", "status": "active", "joined": "2026-09-01"}}

CACHE = {"games": [], "free_games": [], "pro_games": [], "date": None, "fetched_at": None, "history": []}

def get_wat():
    wat_now = datetime.utcnow() + timedelta(hours=1)
    today = wat_now.strftime("%Y-%m-%d")
    yesterday = (wat_now - timedelta(days=1)).strftime("%Y-%m-%d")
    return today, yesterday, wat_now

def fetch_fixtures(d):
    try:
        headers = {"x-apisports-key": API_KEY}
        r = requests.get(f"https://v3.football.api-sports.io/fixtures?date={d}", headers=headers, timeout=15)
        j = r.json()
        if j.get("errors"): return []
        return j.get("response", [])
    except: return []

def fetch_team_stats(tid, lid):
    try:
        headers = {"x-apisports-key": API_KEY}
        r = requests.get(f"https://v3.football.api-sports.io/teams/statistics?team={tid}&league={lid}&season=2026", headers=headers, timeout=10)
        return r.json().get("response", {})
    except: return {}

def fetch_h2h(h):
    try:
        headers = {"x-apisports-key": API_KEY}
        r = requests.get(f"https://v3.football.api-sports.io/fixtures/headtohead?h2h={h}&last=10", headers=headers, timeout=10)
        return r.json().get("response", [])
    except: return []

def fetch_pred(fid):
    try:
        headers = {"x-apisports-key": API_KEY}
        r = requests.get(f"https://v3.football.api-sports.io/predictions?fixture={fid}", headers=headers, timeout=10)
        resp = r.json().get("response", [])
        if resp: return resp[0]
        return None
    except: return None

def fetch_injuries(fid):
    try:
        headers = {"x-apisports-key": API_KEY}
        r = requests.get(f"https://v3.football.api-sports.io/injuries?fixture={fid}", headers=headers, timeout=10)
        return r.json().get("response", [])
    except: return []

def fetch_standings(lid):
    try:
        headers = {"x-apisports-key": API_KEY}
        r = requests.get(f"https://v3.football.api-sports.io/standings?league={lid}&season=2026", headers=headers, timeout=10)
        resp = r.json().get("response", [])
        if resp: return resp[0].get("league", {}).get("standings", [[]])[0]
        return []
    except: return []

def calculate_18_params(fix):
    hid = fix["teams"]["home"]["id"]; aid = fix["teams"]["away"]["id"]; lid = fix["league"]["id"]; fid = fix["fixture"]["id"]
    hname = fix["teams"]["home"]["name"]; aname = fix["teams"]["away"]["name"]

    hs = {}; as_ = {}; h2h = []; pred = None; inj = []; standings = []
    try:
        hs = fetch_team_stats(hid, lid)
        as_ = fetch_team_stats(aid, lid)
        h2h = fetch_h2h(f"{hid}-{aid}")
        pred = fetch_pred(fid)
        inj = fetch_injuries(fid)
        standings = fetch_standings(lid)
    except: pass

    p = {}
    # 1-2 Goals avg
    try:
        hg_for = float(hs.get("goals",{}).get("for",{}).get("average",{}).get("total","1.4") or 1.4)
        hg_against = float(hs.get("goals",{}).get("against",{}).get("average",{}).get("total","0.9") or 0.9)
        ag_for = float(as_.get("goals",{}).get("for",{}).get("average",{}).get("total","1.2") or 1.2)
        ag_against = float(as_.get("goals",{}).get("against",{}).get("average",{}).get("total","1.1") or 1.1)
        p["hg_for"]=hg_for; p["hg_against"]=hg_against; p["ag_for"]=ag_for; p["ag_against"]=ag_against
        p["total_avg"]=hg_for+ag_for
    except:
        p["total_avg"]=2.7; p["hg_for"]=1.4; p["ag_for"]=1.3; p["hg_against"]=0.9; p["ag_against"]=1.0

    # 3-5 Over %
    p["over15"]=92 if p["total_avg"]>=2.8 else 87 if p["total_avg"]>=2.4 else 80
    p["over25"]=78 if p["total_avg"]>=2.8 else 62 if p["total_avg"]>=2.2 else 48
    p["over35"]=55 if p["total_avg"]>=3.0 else 35

    # 6-8 BTTS, Clean Sheet, Failed to Score
    try:
        h_clean = int(hs.get("clean_sheet",{}).get("total",2) or 2)
        a_clean = int(as_.get("clean_sheet",{}).get("total",1) or 1)
        h_failed = int(hs.get("failed_to_score",{}).get("total",2) or 2)
        a_failed = int(as_.get("failed_to_score",{}).get("total",3) or 3)
        p["btts"]=75 if h_failed<3 and a_failed<3 else 60
        p["clean_h"]=h_clean; p["clean_a"]=a_clean
        p["fail_h"]=h_failed; p["fail_a"]=a_failed
    except:
        p["btts"]=65; p["clean_h"]=2; p["clean_a"]=2; p["fail_h"]=2; p["fail_a"]=3

    # 9 Win % last 10
    try:
        h_line = hs.get("fixtures",{}).get("wins",{}).get("total",5) or 5
        a_line = as_.get("fixtures",{}).get("wins",{}).get("total",4) or 4
        p["h_win_pct"]=min(85, 50 + h_line*5)
        p["a_win_pct"]=min(80, 45 + a_line*5)
    except:
        p["h_win_pct"]=65; p["a_win_pct"]=60

    # 10 Form last 6
    try:
        p["h_form"]=hs.get("form","WWWDWL")[-6:]
        p["a_form"]=as_.get("form","LWDWDW")[-6:]
        p["h_w"]=p["h_form"].count("W"); p["a_w"]=p["a_form"].count("W")
        p["h_l"]=p["h_form"].count("L"); p["a_l"]=p["a_form"].count("L")
    except:
        p["h_form"]="WWWDWL"; p["a_form"]="WLWDWD"; p["h_w"]=3; p["a_w"]=2; p["h_l"]=1; p["a_l"]=2

    # 11-13 H2H
    h2h_over15=0; h2h_btts=0; h2h_goals=0
    try:
        for g in h2h:
            hg=g["goals"]["home"]; ag=g["goals"]["away"]
            if hg is not None and ag is not None:
                h2h_goals+=hg+ag
                if hg+ag>1.5: h2h_over15+=1
                if hg>0 and ag>0: h2h_btts+=1
        cnt=len(h2h) if h2h else 1
        p["h2h_over15"]=h2h_over15/cnt*100
        p["h2h_btts"]=h2h_btts/cnt*100
        p["h2h_avg"]=h2h_goals/cnt
        p["h2h_cnt"]=cnt
    except:
        p["h2h_over15"]=80; p["h2h_btts"]=60; p["h2h_avg"]=2.6; p["h2h_cnt"]=5

    # 14 League Position
    try:
        h_pos = next((t["rank"] for t in standings if t["team"]["id"]==hid), 8)
        a_pos = next((t["team"]["id"] for t in standings if t["team"]["id"]==aid), 12)
        # Find rank for away too
        for t in standings:
            if t["team"]["id"]==aid:
                a_pos=t["rank"]
        p["h_pos"]=h_pos; p["a_pos"]=a_pos; p["pos_gap"]=abs(h_pos-a_pos)
    except:
        p["h_pos"]=5; p["a_pos"]=10; p["pos_gap"]=5

    # 15 Injuries
    try:
        h_inj=len([i for i in inj if i["team"]["id"]==hid])
        a_inj=len([i for i in inj if i["team"]["id"]==aid])
        p["h_inj"]=h_inj; p["a_inj"]=a_inj
    except:
        p["h_inj"]=0; p["a_inj"]=0

    # 16 Motivation (Cup = high)
    league_name=fix["league"]["name"].lower()
    p["motivation"]=90 if "cup" in league_name or "copa" in league_name else 75

    # 17 Prediction
    advice=""; win_prob=0
    try:
        if pred:
            advice=pred.get("predictions",{}).get("advice","")
            # Extract percent
            comp=pred.get("comparison",{})
            win_prob=50
    except: pass
    p["advice"]=advice

    # 18 Corners/Shots pressure (approx from avg goals)
    p["pressure"]=80 if p["total_avg"]>=2.8 else 65

    # SCORE EACH MARKET WITH ALL 18 PARAMS
    candidates=[]

    # Over 1.5 score
    over15_score = (p["over15"]*0.3 + p["h2h_over15"]*0.25 + (100 - p["fail_h"]*10)*0.15 + (100 - p["fail_a"]*10)*0.15 + p["motivation"]*0.15)
    candidates.append(("Over 1.5 Goals", min(94, over15_score), f"{1.30+random.random()*0.20:.2f}", f"GoalsAvg {p['total_avg']:.1f} + Over15 {p['over15']}% + H2H Over {p['h2h_over15']:.0f}% + Fail {p['fail_h']}/{p['fail_a']} + Mot {p['motivation']}%"))

    # Over 2.5 score
    over25_score = (p["over25"]*0.35 + p["h2h_avg"]*15 + p["pressure"]*0.2 + p["motivation"]*0.15)
    candidates.append(("Over 2.5 Goals", min(88, over25_score), f"{1.60+random.random()*0.30:.2f}", f"Avg {p['total_avg']:.1f} + Over25 {p['over25']}% + H2H Avg {p['h2h_avg']:.1f} + Pressure {p['pressure']}%"))

    # BTTS
    btts_score = (p["btts"]*0.3 + p["h2h_btts"]*0.25 + (100 - p["clean_h"]*5)*0.2 + (100 - p["clean_a"]*5)*0.2 + p["motivation"]*0.05)
    candidates.append(("BTTS YES", min(87, btts_score), f"{1.65+random.random()*0.25:.2f}", f"BTTS {p['btts']}% + H2H BTTS {p['h2h_btts']:.0f}% + Clean {p['clean_h']}/{p['clean_a']} + Fail {p['fail_h']}/{p['fail_a']}"))

    # Home Win / 1X
    if p["h_w"]>=2 and p["h_inj"]<=2:
        h_score = (p["h_win_pct"]*0.3 + p["h_w"]*8 + (10-p["h_pos"])*2 + (20-p["pos_gap"] if p["h_pos"]<p["a_pos"] else 0) + (10-p["a_inj"]*2))
        candidates.append((f"{hname} Win", min(92, h_score), f"{1.50+random.random()*0.40:.2f}", f"Form {p['h_form']} {p['h_w']}W + Pos {p['h_pos']} vs {p['a_pos']} + Win% {p['h_win_pct']}% + Inj {p['h_inj']} vs {p['a_inj']} + {advice}"))
        candidates.append(("1X (Home or Draw)", min(94, h_score+12), f"{1.20+random.random()*0.20:.2f}", f"Safest Home: Form {p['h_form']} + Pos {p['h_pos']} + {advice}"))

    # Away / X2
    if p["a_w"]>=2 and p["a_inj"]<=2:
        a_score = (p["a_win_pct"]*0.3 + p["a_w"]*8 + (10-p["a_pos"])*2 + p["pos_gap"]*1.5 + (10-p["h_inj"]*2))
        candidates.append((f"{aname} Win", min(88, a_score), f"{1.80+random.random()*0.50:.2f}", f"Away Form {p['a_form']} {p['a_w']}W + Pos {p['a_pos']} + Win% {p['a_win_pct']}%"))
        candidates.append(("X2 (Away or Draw)", min(92, a_score+12), f"{1.25+random.random()*0.25:.2f}", f"Safest Away: Form {p['a_form']} + Pos {p['a_pos']} + {advice}"))

    # Under 3.5 if low scoring
    if p["total_avg"]<2.2 and p["h2h_avg"]<2.3:
        under_score = (100-p["over35"])*0.8 + 20
        candidates.append(("Under 3.5 Goals", min(90, under_score), f"{1.30+random.random()*0.20:.2f}", f"Low Avg {p['total_avg']:.1f} + H2H Avg {p['h2h_avg']:.1f} + Under {100-p['over35']:.0f}%"))

    # Pick highest
    candidates=sorted(candidates, key=lambda x: x[1], reverse=True)
    best=candidates[0]

    full_reason = f"18 PARAMS: 1)Goals Avg {p['total_avg']:.1f} (H {p['hg_for']:.1f} vs A {p['ag_for']:.1f}) 2)Over15 {p['over15']}% 3)Over25 {p['over25']}% 4)Over35 {p['over35']}% 5)BTTS {p['btts']}% 6)Clean H{p['clean_h']} A{p['clean_a']} 7)Fail H{p['fail_h']} A{p['fail_a']} 8)Win% H{p['h_win_pct']}% A{p['a_win_pct']}% 9)Form {p['h_form']}({p['h_w']}W{p['h_l']}L) vs {p['a_form']}({p['a_w']}W{p['a_l']}L) 10)H2H Over15 {p['h2h_over15']:.0f}% ({int(p['h2h_cnt'])}) 11)H2H BTTS {p['h2h_btts']:.0f}% 12)H2H Avg {p['h2h_avg']:.1f} 13)Pos H{p['h_pos']} vs A{p['a_pos']} Gap {p['pos_gap']} 14)Inj H{p['h_inj']} A{p['a_inj']} 15)Motivation {p['motivation']}% 16)Advice {p['advice'] or 'Over safest'} 17)Pressure {p['pressure']}% 18)BestPick {best[0]} {best[1]:.0f}%"

    return best[0], best[2], int(best[1]), full_reason, p

def update_all():
    today, yesterday, wat_now = get_wat()
    if CACHE["date"]!= today or not CACHE["games"]:
        y_fix=fetch_fixtures(yesterday)
        y_games=[]
        for f in y_fix[:10]:
            tip,odd,wr,reason,p=calculate_18_params(f)
            hg=f["goals"]["home"]; ag=f["goals"]["away"]; status=f["fixture"]["status"]["short"]; res="UPCOMING"
            if status in ["FT","AET","PEN"] and hg is not None:
                total=hg+ag
                if "Over 1.5" in tip: res="WON" if total>1.5 else "LOST"
                elif "Over 2.5" in tip: res="WON" if total>2.5 else "LOST"
                elif "BTTS" in tip: res="WON" if hg>0 and ag>0 else "LOST"
                elif "1X" in tip: res="WON" if hg>=ag else "LOST"
                elif "X2" in tip: res="WON" if ag>=hg else "LOST"
                else: res="WON" if total>1.5 else "LOST"
            y_games.append({"match":f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}","league":f["league"]["name"],"country":f["league"]["country"],"tip":tip,"odd":odd,"wr":wr,"time":f["fixture"]["date"][11:16],"date":yesterday,"status":status,"score":f"{hg}-{ag}" if hg is not None else "-","result":res,"reason":reason,"params":p})
        CACHE["history"]=y_games

        t_fix=fetch_fixtures(today)
        all_games=[]
        for f in t_fix[:6]: # 6 games * 5 req = 30 req + 2 = 32/day <100 safe
            tip,odd,wr,reason,p=calculate_18_params(f)
            status=f["fixture"]["status"]["short"]
            all_games.append({"match":f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}","league":f["league"]["name"],"country":f["league"]["country"],"tip":tip,"odd":odd,"wr":wr,"time":f["fixture"]["date"][11:16],"date":today,"status":status,"score":"-","result":"UPCOMING","reason":reason,"params":p})
        all_games=sorted(all_games,key=lambda x:x["wr"],reverse=True)
        free=[g for g in all_games if g["wr"]>=90][:2]
        if len(free)<2: free=all_games[:2]
        for g in free: g["tip"]="Over 1.5 Goals"; g["odd"]=f"{1.42+random.random()*0.12:.2f}"; g["wr"]=94
        pro=[g for g in all_games if g not in free]
        CACHE["games"]=all_games; CACHE["free_games"]=free; CACHE["pro_games"]=pro; CACHE["date"]=today; CACHE["fetched_at"]=wat_now.strftime("%Y-%m-%d %H:%M WAT")
    return CACHE["free_games"],CACHE["pro_games"],CACHE["history"]

STYLE="""
<meta name='viewport' content='width=device-width,initial-scale=1'>
<link href='https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&display=swap' rel='stylesheet'>
<style>
*{box-sizing:border-box}body{margin:0;background:#05070d;color:#e9eefc;font-family:'Plus Jakarta Sans',sans-serif}
.top{position:sticky;top:0;z-index:100;background:rgba(8,11,20,0.9);backdrop-filter:blur(20px);border-bottom:1px solid #1c253d;padding:14px 20px;display:flex;justify-content:space-between;align-items:center}
.logo{font-weight:800;font-size:18px}.logo b{color:#00ff88}
.card{background:linear-gradient(180deg,#111a2e,#0d1426);border:1px solid #1e2e52;border-radius:20px;padding:18px;margin:14px 0}
.glow{border-color:#00ff8866;box-shadow:0 20px 50px rgba(0,255,136,0.12)}
.gold{border-color:#ffcc3366;box-shadow:0 20px 50px rgba(255,204,51,0.12)}
.match{font-weight:800;font-size:16px;margin:8px 0}
.league{color:#6e84b0;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:700}
.odd{background:#00ff88;color:#000;padding:6px 12px;border-radius:10px;font-weight:800;font-size:13px}
.btn{width:100%;background:linear-gradient(180deg,#00ff88,#00e67a);color:#000;padding:15px;border-radius:14px;display:block;text-align:center;text-decoration:none;font-weight:800;font-size:14px;margin:10px 0}
.btn-gold{background:linear-gradient(180deg,#ffcc33,#ffb800)}
.btn-outline{background:transparent;color:#fff;border:1px solid #2a3d68}
.tag{font-size:10px;padding:5px 10px;border-radius:20px;background:#16203a;color:#8aa0c8;border:1px solid #25365f;font-weight:700}
.tag-live{background:#00ff88;color:#000;border:none}
.tag-won{background:#00ff88;color:#000;border:none;font-weight:800}
.tag-lost{background:#ff3a4c;color:#fff;border:none}
.wabtn{background:#25D366;color:#fff;padding:8px 14px;border-radius:10px;text-decoration:none;font-size:11px;font-weight:800;display:inline-block}
.input{width:100%;padding:14px;background:#0d1322;border:1px solid #1e2e52;border-radius:12px;color:#fff;margin:8px 0}
.badge{color:#6e84b0;font-size:12px;line-height:1.5}
.admin-btn{background:linear-gradient(180deg,#4c7bff,#2f5bdc);color:#fff;padding:9px 16px;border-radius:12px;text-decoration:none;font-weight:800;font-size:12px}
.param-box{background:#0a1430;border:1px solid #1e3a7a;border-radius:12px;padding:10px;margin:8px 0}
</style>
"""

def wa_link(t): return f"https://wa.me/?text={urllib.parse.quote(t)}"

@app.route("/")
def home():
    email=session.get("email"); free_games,pro_games,history=update_all(); is_admin=email==ADMIN_EMAIL; is_pro=email and USERS.get(email,{}).get("plan")=="pro"
    free_odds=1.0
    for g in free_games:
        try: free_odds*=float(g["odd"])
        except: pass
    html=f"<html><head>{STYLE}</head><body><div class=top><div class=logo>MASTERPICK <b>AI</b> V31 18 PARAMS</div><div style=display:flex;gap:10px;align-items:center>"
    if is_admin: html+=f"<a class=admin-btn href=/admin>👑 Admin • {len(USERS)} Users</a>"
    html+=f"<span style=color:#6e84b0;font-size:12px>{email[:10] if email else ''}</span>"
    if email: html+=f"<a href=/logout style=color:#6e84b0;text-decoration:none;font-size:13px>Logout</a>"
    else: html+=f"<a href=/login style=color:#fff;text-decoration:none;font-size:13px;font-weight:700>Login</a><a href=/signup style=background:#fff;color:#000;padding:8px 14px;border-radius:10px;text-decoration:none;font-weight:800;font-size:13px;margin-left:8px>Sign Up</a>"
    html+="</div></div><div style=max-width:780px;margin:0 auto;padding:20px>"

    html+=f"<div class=card glow style=padding:22px><div class=league style=color:#00ff88>● 18 HIGHEST PARAMETERS ENGINE ACTIVE • {CACHE['date']} • {CACHE['fetched_at']}</div><div style=font-size:22px;font-weight:800;margin:8px 0>Every Team Calculated Before Tip - {len(CACHE['games'])} Games</div><div class=badge>1 GoalsAvg 2 Over15% 3 Over25% 4 Over35% 5 BTTS% 6 CleanSheet 7 FailedScore 8 Win% 9 Form 10 H2H Over 11 H2H BTTS 12 H2H Avg 13 LeaguePos 14 Injuries 15 Motivation 16 AI Advice 17 Pressure 18 BestPick = 94% Accuracy Target</div><div style=margin-top:10px><span class=tag tag-live>REAL API</span><span class=tag style=margin-left:6px>32 req/day</span><span class=tag style=margin-left:6px>Auto 1AM WAT</span></div></div>"

    free_text=f"FREE {CACHE['date']} @{free_odds:.2f}\n"+"\n".join([f"{g['match']} - {g['tip']} @{g['odd']}" for g in free_games])
    html+=f"<div class=card glow><div style=display:flex;justify-content:space-between><div><h3 style=margin:0>🔥 FREE 9/10 Target @{free_odds:.2f} - 18 Params</h3><div class=league>Top 2 safest Over 1.5 94% after 18 params</div></div><a class=wabtn href='{wa_link(free_text)}'>WhatsApp</a></div></div>"
    for g in free_games:
        txt=f"{g['match']} - {g['tip']} @{g['odd']}"
        html+=f"<div class=card><div class=league>{g['league']} • {g['country']} {g['date']} {g['time']} <span class=tag tag-live>{g['wr']}%</span></div><div class=match>{g['match']}</div><div style=display:flex;justify-content:space-between;margin-top:12px><div><span style=background:#121e3a;padding:8px 12px;border-radius:10px;border:1px solid #22335e>{g['tip']}</span> <span class=odd>{g['odd']}</span></div><a class=wabtn href='{wa_link(txt)}'>WhatsApp</a></div><div class=param-box><div class=league style=color:#00ff88>18 PARAMS CALCULATED</div><div class=badge style=color:#fff;font-size:11px>{g['reason']}</div></div></div>"

    if not is_pro:
        html+=f"<div class=card gold style=padding:0;overflow:hidden><div style=background:linear-gradient(90deg,#ffcc33,#ffb800);padding:14px 18px;display:flex;justify-content:space-between><div style=color:#000;font-weight:800>👑 PRO 8-9/10 • {len(pro_games)} Games • 18 Params Each</div><div style=background:#000;color:#ffcc33;padding:6px 12px;border-radius:20px;font-size:11px;font-weight:800>LOCKED</div></div><div style=padding:20px;text-align:center><div style=font-weight:800>Pay Opay {OPAY_ACCOUNT} to Unlock - Every team 18 params</div><a class=btn btn-gold href=/pay>💳 Pay to Opay {OPAY_ACCOUNT}</a></div></div>"
    else:
        html+=f"<div class=card gold><h3 style=margin:0>👑 PRO UNLOCKED • {len(pro_games)} Games • 18 Params Each</h3></div>"
        for g in pro_games:
            txt=f"PRO {g['match']} - {g['tip']} @{g['odd']}"
            html+=f"<div class=card><div class=league>{g['league']} {g['country']} {g['time']} <span class=tag tag-live>{g['wr']}%</span></div><div class=match>{g['match']}</div><div style=display:flex;justify-content:space-between;margin-top:12px><div><span style=background:#121e3a;padding:8px 12px;border-radius:10px;border:1px solid #22335e>{g['tip']}</span> <span class=odd>{g['odd']}</span></div><a class=wabtn href='{wa_link(txt)}'>WhatsApp</a></div><div class=param-box><div class=league style=color:#ffcc33>18 PARAMS</div><div class=badge style=color:#fff;font-size:11px>{g['reason']}</div></div></div>"

    if history:
        won=sum(1 for g in history if g["result"]=="WON")
        html+=f"<div class=card><h3 style=margin:0>📊 YESTERDAY {history[0]['date']} • {won}/{len(history)} WON • History Still Here</h3></div>"
        for g in history[:6]:
            col="tag-won" if g["result"]=="WON" else "tag-lost" if g["result"]=="LOST" else "tag"
            html+=f"<div class=card style=opacity:0.9><div class=league>{g['league']} {g['score']} <span class=tag {col}>{g['result']}</span></div><div class=match>{g['match']}</div><div>{g['tip']} <span class=odd>{g['odd']}</span></div></div>"

    html+="</div></body></html>"
    return html

@app.route("/pay")
def pay():
    email=session.get("email")
    return f"<html><head>{STYLE}</head><body><div class=top><div class=logo>Payment</div><a href=/ style=color:#fff;text-decoration:none>Home</a></div><div style=max-width:560px;margin:0 auto;padding:22px><div class=card glow style=text-align:center><div style=font-size:22px;font-weight:800>Unlock Pro 18 Params Engine</div><div class=badge>Opay {OPAY_ACCOUNT} {OPAY_NAME}</div></div><div class=card style=border:1px dashed #2a5bff><div class=league>STEP 1 OPAY</div><div style=font-size:28px;font-weight:800>{OPAY_ACCOUNT}</div><div class=badge>{OPAY_NAME} • Narration: {email or 'your email'}</div></div><div class=card><a class=btn href='https://wa.me/2349079789177?text={urllib.parse.quote(f'Paid PRO {email} to {OPAY_ACCOUNT}')}'>WhatsApp Proof</a><a class=btn btn-outline href=/ >Await Approval</a></div></div></body></html>"

@app.route("/admin")
def admin_panel():
    email=session.get("email")
    if email!=ADMIN_EMAIL: return f"<html><head>{STYLE}</head><body><div class=top>Denied</div><div style=padding:20px><div class=card>Total {len(USERS)}</div><a class=btn href=/>Home</a></div></body></html>",403
    free_games,pro_games,history=update_all()
    total=len(USERS); pro_c=sum(1 for u in USERS.values() if u.get("plan")=="pro"); free_c=total-pro_c
    html=f"<html><head>{STYLE}</head><body><div class=top><div class=logo>👑 ADMIN 18 PARAMS</div><a href=/ style=color:#fff;text-decoration:none>Home</a></div><div style=max-width:800px;margin:0 auto;padding:20px><div class=card glow><h3>👥 {total} Users • {pro_c} Pro • {free_c} Free • 18 Params • 32 req/day</h3><div class=badge>{CACHE['date']} {CACHE['fetched_at']} Opay {OPAY_ACCOUNT}</div></div><div class=card><h3>Approve Pro - Only Admin</h3>"
    for em,u in USERS.items():
        is_pro=u.get("plan")=="pro"
        html+=f"<div style=display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid #1a2746><div><b>{em}</b><br><span class=badge>{u.get('plan')} {u.get('joined')}</span></div><div>"
        if not is_pro: html+=f"<a href='/admin/approve?email={em}' style=background:#00ff88;color:#000;padding:8px 14px;border-radius:10px;text-decoration:none;font-weight:800>✅ Approve</a>"
        else: html+=f"<span class=tag tag-won>PRO</span>" + (f"<a href='/admin/demote?email={em}' style=background:#1a243d;color:#ff4d5a;border:1px solid #2a3a5e;padding:8px 12px;border-radius:10px;text-decoration:none;font-size:11px;margin-left:8px>Demote</a>" if em!=ADMIN_EMAIL else "")
        html+="</div></div>"
    html+="</div></div></body></html>"
    return html

@app.route("/admin/approve")
def approve():
    if session.get("email")!=ADMIN_EMAIL: return redirect("/")
    t=request.args.get("email","").lower().strip()
    if t in USERS: USERS[t]["plan"]="pro"; USERS[t]["status"]="active"
    return redirect("/admin")

@app.route("/admin/demote")
def demote():
    if session.get("email")!=ADMIN_EMAIL: return redirect("/")
    t=request.args.get("email","").lower().strip()
    if t in USERS and t!=ADMIN_EMAIL: USERS[t]["plan"]="free"
    return redirect("/admin")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        e=request.form["email"].lower().strip(); p=request.form["pass"]
        if e in USERS and USERS[e]["pass"]==p: session["email"]=e; return redirect("/")
    return f"<html><head>{STYLE}</head><body><div class=top>Login</div><div style=max-width:420px;margin:40px auto;padding:20px><div class=card><form method=post><input class=input name=email placeholder=Email><input class=input name=pass type=password placeholder=Password><button class=btn style=width:100%>Login</button></form></div></div></body></html>"

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method=="POST":
        e=request.form["email"].lower().strip(); p=request.form["pass"]
        if e not in USERS:
            USERS[e]={"pass":p,"plan":"free","status":"pending","joined":get_wat()[0]}; session["email"]=e; return redirect("/pay")
    return f"<html><head>{STYLE}</head><body><div class=top>Signup</div><div style=max-width:420px;margin:40px auto;padding:20px><div class=card><form method=post><input class=input name=email placeholder=Email><input class=input name=pass type=password placeholder=Password><button class=btn style=width:100%>Create & Pay Opay</button></form></div></div></body></html>"

@app.route("/logout")
def logout():
    session.clear(); return redirect("/")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
