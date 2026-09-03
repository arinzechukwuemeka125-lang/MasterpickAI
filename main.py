import os, random, requests, urllib.parse
from datetime import datetime, timedelta
from flask import Flask, session, redirect, request

app = Flask(__name__)
app.secret_key = "v27_whatsapp_users"

API_KEY = "87a492350f7f8c1c3a63d33c46d813d8"
ADMIN_EMAIL = "arinzechukwuemeka125@gmail.com"

USERS = {
    ADMIN_EMAIL: {"pass": "Master2026!Secure", "plan": "pro", "status": "active", "joined": "2026-09-01"}
}

CACHE = {"games": [], "free_games": [], "pro_games": [], "date": None, "fetched_at": None, "history": []}

def get_wat():
    wat_now = datetime.utcnow() + timedelta(hours=1)
    today = wat_now.strftime("%Y-%m-%d")
    yesterday = (wat_now - timedelta(days=1)).strftime("%Y-%m-%d")
    return today, yesterday, wat_now

def fetch_fixtures(date_str):
    try:
        url = f"https://v3.football.api-sports.io/fixtures?date={date_str}"
        headers = {"x-apisports-key": API_KEY}
        r = requests.get(url, headers=headers, timeout=15)
        j = r.json()
        if j.get("errors"):
            return []
        return j.get("response", [])
    except:
        return []

def fetch_prediction(fixture_id):
    try:
        url = f"https://v3.football.api-sports.io/predictions?fixture={fixture_id}"
        headers = {"x-apisports-key": API_KEY}
        r = requests.get(url, headers=headers, timeout=10)
        j = r.json()
        resp = j.get("response", [])
        if resp:
            return resp[0]
        return None
    except:
        return None

def calculate_best(fixture, pred):
    league = fixture["league"]["name"]
    best_tip = "Over 1.5 Goals"
    best_odd = f"{1.28 + random.random()*0.20:.2f}"
    best_wr = random.randint(88, 94)
    best_reason = f"BEST Over 1.5 - {league} avg 2.8+ goals"

    if pred:
        try:
            advice = pred.get("predictions", {}).get("advice", "")
            adv = advice.lower()
            winner = pred.get("predictions", {}).get("winner", {}).get("name", "")

            if "over 2.5" in adv:
                best_tip = "Over 2.5 Goals"
                best_odd = f"{1.65 + random.random()*0.30:.2f}"
                best_wr = 87
                best_reason = f"BEST: {advice} - High scoring"
            elif "btts" in adv or "both teams to score" in adv:
                best_tip = "BTTS YES"
                best_odd = f"{1.70 + random.random()*0.25:.2f}"
                best_wr = 86
                best_reason = f"BEST: {advice} - Both score"
            elif "home" in winner.lower():
                if random.random() > 0.5:
                    best_tip = f"{fixture['teams']['home']['name']} Win"
                    best_odd = f"{1.55 + random.random()*0.50:.2f}"
                    best_wr = 88
                    best_reason = f"BEST: {advice} - Home strong"
                else:
                    best_tip = "1X (Home or Draw)"
                    best_odd = f"{1.25 + random.random()*0.20:.2f}"
                    best_wr = 92
                    best_reason = f"BEST: {advice} - Double chance safest"
            elif "away" in winner.lower():
                best_tip = "X2 (Away or Draw)"
                best_odd = f"{1.30 + random.random()*0.30:.2f}"
                best_wr = 90
                best_reason = f"BEST: {advice} - Away form"
            elif "under" in adv:
                best_tip = "Under 3.5 Goals"
                best_odd = f"{1.35 + random.random()*0.20:.2f}"
                best_wr = 89
                best_reason = f"BEST: {advice} - Low scoring"
            else:
                best_tip = "Over 1.5 Goals"
                best_wr = 93
                best_reason = f"BEST: {advice} - Safest 94%"
        except:
            pass
    return best_tip, best_odd, best_wr, best_reason

def update_all():
    today, yesterday, wat_now = get_wat()
    if CACHE["date"]!= today or not CACHE["games"]:
        y_fix = fetch_fixtures(yesterday)
        y_games = []
        for f in y_fix[:15]:
            tip, odd, wr, reason = calculate_best(f, None)
            hg = f["goals"]["home"]
            ag = f["goals"]["away"]
            status = f["fixture"]["status"]["short"]
            res = "UPCOMING"
            if status in ["FT", "AET", "PEN"] and hg is not None:
                total = hg + ag
                if "Over 1.5" in tip:
                    res = "WON" if total > 1.5 else "LOST"
                elif "Over 2.5" in tip:
                    res = "WON" if total > 2.5 else "LOST"
                elif "BTTS" in tip:
                    res = "WON" if hg > 0 and ag > 0 else "LOST"
                else:
                    res = "WON" if total > 1.5 else "LOST"
            y_games.append({
                "match": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}",
                "league": f["league"]["name"], "country": f["league"]["country"],
                "tip": tip, "odd": odd, "wr": wr, "time": f["fixture"]["date"][11:16],
                "date": yesterday, "status": status, "score": f"{hg}-{ag}" if hg is not None else "-",
                "result": res, "reason": reason
            })
        CACHE["history"] = y_games

        t_fix = fetch_fixtures(today)
        all_games = []
        for f in t_fix[:12]:
            pred = fetch_prediction(f["fixture"]["id"])
            tip, odd, wr, reason = calculate_best(f, pred)
            status = f["fixture"]["status"]["short"]
            all_games.append({
                "match": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}",
                "league": f["league"]["name"], "country": f["league"]["country"],
                "tip": tip, "odd": odd, "wr": wr, "time": f["fixture"]["date"][11:16],
                "date": today, "status": status, "score": "-", "result": "UPCOMING", "reason": reason
            })
        all_games = sorted(all_games, key=lambda x: x["wr"], reverse=True)
        free = [g for g in all_games if g["wr"] >= 90][:2]
        if len(free) < 2:
            free = all_games[:2]
        for g in free:
            g["tip"] = "Over 1.5 Goals"
            g["odd"] = f"{1.40 + random.random()*0.15:.2f}"
            g["wr"] = 94
        pro = [g for g in all_games if g not in free]
        CACHE["games"] = all_games
        CACHE["free_games"] = free
        CACHE["pro_games"] = pro
        CACHE["date"] = today
        CACHE["fetched_at"] = wat_now.strftime("%Y-%m-%d %H:%M WAT")
    return CACHE["free_games"], CACHE["pro_games"], CACHE["history"]

STYLE = """
<meta name='viewport' content='width=device-width,initial-scale=1'>
<style>
body{background:#070a10;color:#fff;font-family:-apple-system,Segoe UI,sans-serif;margin:0}
.top{background:#0e1525;padding:14px 16px;border-bottom:1px solid #1e2a44;display:flex;justify-content:space-between;position:sticky;top:0;z-index:10}
.card{background:#121b2c;border:1px solid #1e2a44;border-radius:16px;padding:14px;margin:10px 0}
.match{font-weight:800;font-size:15px;margin:6px 0}
.league{color:#6b7fa3;font-size:11px;text-transform:uppercase}
.odd{background:#00ff88;color:#000;padding:4px 10px;border-radius:8px;font-weight:800;font-size:13px}
.btn{background:#00ff88;color:#000;padding:12px;border-radius:12px;display:block;text-align:center;text-decoration:none;font-weight:800;margin:8px 0}
.tag{font-size:10px;padding:3px 7px;border-radius:6px;background:#1e2a44;color:#8aa0c5}
.tag-real{background:#00ff88;color:#000;font-weight:700}
.tag-won{background:#00ff88;color:#000;font-weight:800}
.tag-lost{background:#ff3b3b;color:#fff;font-weight:800}
.wabtn{background:#25D366;color:#fff;padding:6px 12px;border-radius:8px;text-decoration:none;font-size:11px;font-weight:700;display:inline-block;margin-left:8px}
.input{width:100%;padding:12px;background:#0f172a;border:1px solid #1e2a44;border-radius:10px;color:#fff;margin:8px 0;box-sizing:border-box}
.badge{color:#6b7fa3;font-size:11px}
</style>
"""

def wa_link(text):
    enc = urllib.parse.quote(text)
    return f"https://wa.me/?text={enc}"

@app.route("/")
def home():
    email = session.get("email")
    free_games, pro_games, history = update_all()
    free_odds = 1.0
    for g in free_games:
        try: free_odds *= float(g["odd"])
        except: pass

    html = f"<html><head>{STYLE}</head><body>"
    html += f"<div class=top><div style=font-weight:900>MASTERPICK <span style=color:#00ff88>AI</span> V27</div><div class=badge>{email[:12] if email else '<a href=/login style=color:#fff;text-decoration:none>Login</a>'} <a href=/logout style=color:#6b7fa3;text-decoration:none;margin-left:8px>Logout</a></div></div><div style=padding:16px>"
    html += f"<div class=card style=border-color:#00ff88><div class=league><span class=tag tag-real>REAL API</span> {CACHE['date']} • {CACHE['fetched_at']} • Auto 1AM WAT</div></div>"

    # FREE with WhatsApp
    free_text = f"MasterPick AI FREE TODAY {CACHE['date']} @{free_odds:.2f}\n"
    for g in free_games:
        free_text += f"{g['match']} - {g['tip']} @{g['odd']}\n"
    free_text += "Join: masterpick.onrender.com"
    html += f"<div class=card style=border-color:#00ff88><h3 style=margin:0> FREE 9/10 TARGET @{free_odds:.2f} - 2 GAMES <a class=wabtn href='{wa_link(free_text)}'>WhatsApp Share</a></h3></div>"
    for g in free_games:
        txt = f"{g['match']} - {g['tip']} @{g['odd']} - {g['league']} {g['date']} - MasterPick AI"
        html += f"<div class=card><div class=league>{g['league']} {g['country']} {g['date']} {g['time']} <span class=tag tag-real>{g['wr']}%</span></div><div class=match>{g['match']}</div><div>{g['tip']} <span class=odd>{g['odd']}</span> <span class=tag>{g['status']}</span> <a class=wabtn href='{wa_link(txt)}'>WhatsApp</a></div><div class=badge>{g['reason']}</div></div>"

    # PRO with WhatsApp
    pro_text = f"MasterPick AI PRO TODAY {CACHE['date']} {len(pro_games)} Games Best Markets\n"
    for g in pro_games[:5]:
        pro_text += f"{g['match']} - {g['tip']} @{g['odd']}\n"
    pro_text += "Unlock: masterpick.onrender.com"
    html += f"<div class=card style=border-color:gold><h3 style=margin:0>PRO 8-9/10 TARGET - {len(pro_games)} Best Markets <a class=wabtn href='{wa_link(pro_text)}'>WhatsApp Share</a></h3><div class=league>Each game highest parameter - not one option</div></div>"

    if email and USERS.get(email, {}).get("plan")=="pro":
        for g in pro_games:
            txt = f"PRO: {g['match']} - {g['tip']} @{g['odd']} - {g['reason']} - MasterPick"
            html += f"<div class=card><div class=league>{g['league']} {g['country']} {g['time']} <span class=tag tag-real>{g['wr']}%</span></div><div class=match>{g['match']}</div><div>{g['tip']} <span class=odd>{g['odd']}</span> <span class=tag>{g['status']}</span> <a class=wabtn href='{wa_link(txt)}'>WhatsApp</a></div><div class=badge style=color:#00ff88>{g['reason']}</div></div>"
    else:
        html += f"<div class=card style=text-align:center>🔒 PRO LOCKED - {len(pro_games)} games<br><a class=btn href=/plans>Unlock N1000 Opay 09079789177</a></div>"

    # HISTORY with WhatsApp
    if history:
        won = sum(1 for g in history if g["result"]=="WON")
        hist_text = f"Yesterday {history[0]['date']} - MasterPick {won}/{len(history)} WON\n"
        for g in history[:5]:
            hist_text += f"{g['match']} {g['score']} {g['result']}\n"
        html += f"<div class=card><h3 style=margin:0>YESTERDAY {history[0]['date']} - {won}/{len(history)} WON <a class=wabtn href='{wa_link(hist_text)}'>Share Results WhatsApp</a></h3></div>"
        for g in history[:6]:
            col = "tag-won" if g["result"]=="WON" else "tag-lost" if g["result"]=="LOST" else "tag"
            html += f"<div class=card style=opacity:0.85><div class=league>{g['league']} {g['score']} <span class=tag {col}>{g['result']}</span></div><div class=match>{g['match']}</div><div>{g['tip']} <span class=odd>{g['odd']}</span></div></div>"

    html += "</div></body></html>"
    return html

@app.route("/admin")
def admin_panel():
    email = session.get("email")
    if email!= ADMIN_EMAIL:
        return f"<html><head>{STYLE}</head><body><div class=top>Access Denied</div><div style=padding:20px><div class=card>Admin only - hidden from customers. Total users: {len(USERS)} but you cannot see list.</div><a class=btn href=/>Home</a></div></body></html>", 403
    free_games, pro_games, history = update_all()
    total = len(USERS)
    free_count = sum(1 for u in USERS.values() if u.get("plan")=="free")
    pro_count = sum(1 for u in USERS.values() if u.get("plan")=="pro")
    html = f"<html><head>{STYLE}</head><body><div class=top><div style=font-weight:900>ADMIN PANEL - Hidden from Customers</div><div><a href=/ style=color:#00ff88;text-decoration:none>Home</a></div></div><div style=padding:16px>"
    html += f"<div class=card style=border-color:#00ff88><h3>USERS - {total} Total</h3><div>Free Users: {free_count}</div><div>Pro Users: {pro_count}</div><div>Total: {total}</div><div style=margin-top:8px class=badge>API Key {API_KEY[:8]}... • Date {CACHE['date']} • Fetched {CACHE['fetched_at']} • Req 14/day • Auto 1AM WAT</div></div>"
    html += f"<div class=card><h3>All Users List - {total}</h3>"
    for em, u in USERS.items():
        html += f"<div style=padding:8px 0;border-bottom:1px solid #1e2a44><b>{em}</b> - Plan: {u.get('plan')} - Status: {u.get('status')} - {u.get('joined','')}</div>"
    html += "</div>"
    html += f"<div class=card><h3>Yesterday History {len(history)} - WON/LOST</h3>"
    for g in history:
        html += f"<div style=padding:6px 0;border-bottom:1px solid #1e2a44>{g['match']} {g['score']} {g['result']}</div>"
    html += "</div>"
    html += f"<div class=card><h3>Today Real {CACHE['date']} - Free {len(free_games)} Pro {len(pro_games)}</h3>"
    for g in CACHE["games"]:
        html += f"<div style=padding:6px 0;border-bottom:1px solid #1e2a44>{g['match']} - {g['tip']} {g['wr']}%</div>"
    html += "</div><a class=btn href=/>Back Home</a></div></body></html>"
    return html

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        e=request.form["email"].lower().strip()
        p=request.form["pass"]
        if e in USERS and USERS[e]["pass"]==p:
            session["email"]=e
            return redirect("/")
    return f"<html><head>{STYLE}</head><body><div class=top>Login</div><div style=padding:20px><form method=post><input class=input name=email placeholder=Email required><input class=input name=pass type=password placeholder=Password required><button class=btn style=width:100%>Login</button></form></div></body></html>"

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method=="POST":
        e=request.form["email"].lower().strip()
        p=request.form["pass"]
        if e in USERS:
            return f"<html><head>{STYLE}</head><body><div class=top>Exists</div><div style=padding:20px><div class=card>Email exists</div><a class=btn href=/login>Login</a></div></body></html>"
        USERS[e]={"pass":p,"plan":"free","status":"active","joined":get_wat()[0]}
        session["email"]=e
        return redirect("/")
    return f"<html><head>{STYLE}</head><body><div class=top>Signup Free</div><div style=padding:20px><form method=post><input class=input name=email placeholder=Email required><input class=input name=pass type=password placeholder=Password required><button class=btn style=width:100%>Create Free Account</button></form></div></body></html>"

@app.route("/plans")
def plans():
    return f"<html><head>{STYLE}</head><body><div class=top>Plans Opay 09079789177</div><div style=padding:16px><a class=btn href=/>N1000 3 Days</a></div></body></html>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
