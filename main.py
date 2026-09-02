
import os, requests, urllib.parse
from datetime import datetime, timedelta
from flask import Flask, request, redirect, session

app = Flask(__name__)
app.secret_key = "masterpick_v10_5_whatsapp_2026"
API_KEY = "8623f52e5c8224c49f7bb676d1f68665"

USERS = {
    "arinzechukwuemeka125@gmail.com": {
        "pass": "admin123", "plan": "pro", "status": "active",
        "expiry": datetime.now() + timedelta(days=365),
        "is_admin": True, "pending": None
    }
}

SPORTYBET_LEAGUES = [
    "Premier League","La Liga","Serie A","Bundesliga","Ligue 1",
    "Eredivisie","Primeira Liga","Championship","Super Lig","Pro League",
    "Major League Soccer","MLS","Brasileiro","Serie A Brazil","Saudi",
    "Jupiler","Premiership","Scottish","Liga Profesional","Primera Division",
    "J-League","K League","Super League","Allsvenskan","Eliteserien","PSL",
    "Botola","Copa do Brasil","Copa Libertadores","Copa Sudamericana",
    "World Cup","Qualification","Friendly","Nations League","FA Cup"
]

def is_sportybet_league(name):
    n=name.lower()
    for k in SPORTYBET_LEAGUES:
        if k.lower() in n: return True
    return False

def get_fixtures():
    try:
        headers={"x-apisports-key":API_KEY}
        today=datetime.now().strftime("%Y-%m-%d")
        url=f"https://v3.football.api-sports.io/fixtures?date={today}"
        r=requests.get(url,headers=headers,timeout=12).json()
        out=[]
        for f in r.get("response",[])[:80]:
            league=f["league"]["name"]
            if is_sportybet_league(league):
                home=f["teams"]["home"]["name"]; away=f["teams"]["away"]["name"]
                out.append({
                    "match":f"{home} vs {away}",
                    "league":f"{league} - {f['league']['country']}",
                    "time":f["fixture"]["date"][11:16],
                    "tip":"Over 0.5 Goals","odd":"1.25","conf":"9/10 SUREST"
                })
        return out
    except: return []

def wa_link(text):
    enc=urllib.parse.quote(text)
    return f"https://wa.me/?text={enc}"

STYLE="""
<meta name='viewport' content='width=device-width, initial-scale=1'>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
*{font-family:'Inter',sans-serif;box-sizing:border-box;margin:0;padding:0}
body{background:#070a10;color:#fff}
.topbar{background:#0e1525;padding:14px 18px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1e2a44;position:sticky;top:0;z-index:10}
.logo{font-weight:800;font-size:18px}.logo span{color:#00ff88}
.badge{background:#00ff88;color:#000;font-size:10px;padding:3px 8px;border-radius:20px;font-weight:800;margin-left:8px}
.btn{border:none;padding:12px 18px;border-radius:12px;font-weight:700;cursor:pointer;text-decoration:none;display:inline-block;text-align:center}
.btn-primary{background:#00ff88;color:#000;width:100%}.btn-dark{background:#162032;color:#fff;border:1px solid #23324f;width:100%}
.btn-wa{background:#25D366;color:#fff;padding:8px 12px;border-radius:10px;font-size:12px;font-weight:700;text-decoration:none;display:inline-flex;align-items:center;gap:6px}
.card{background:linear-gradient(145deg,#121b2c,#0f172a);border:1px solid #1e2a44;border-radius:18px;padding:16px;margin:12px 0;position:relative}
.card::before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:#00ff88}
.card.gold::before{background:gold}.card.pending::before{background:orange}
.league{color:#6b7fa3;font-size:11px;font-weight:600;text-transform:uppercase}
.match{font-weight:800;font-size:15px;margin:6px 0}
.tipbox{background:#0a121f;border:1px dashed #1e3a5f;border-radius:12px;padding:10px;margin-top:10px;display:flex;justify-content:space-between;align-items:center}
.odd{background:#00ff88;color:#000;padding:6px 12px;border-radius:10px;font-weight:800}
.conf{font-size:11px;color:#00ff88;font-weight:700}
.login-wrap{max-width:400px;margin:40px auto;padding:24px}
.input{width:100%;padding:14px 16px;background:#0f172a;border:1px solid #1e2a44;border-radius:12px;color:#fff;margin:8px 0}
.hero{background:radial-gradient(800px 300px at 50% -10%,rgba(0,255,136,0.15),transparent),#0e1525;border:1px solid #1e2a44;border-radius:24px;padding:24px;margin:16px;text-align:center}
</style>
"""

def header_html(email=None):
    if email:
        u=USERS.get(email); plan=u["plan"].upper() if u else "FREE"
        nav=f"<div style='font-size:11px'><span style='background:#162032;padding:6px 10px;border-radius:20px;border:1px solid #23324f'>{email[:18]} | {plan}</span> <a href='/logout' style='color:#6b7fa3;margin-left:8px;text-decoration:none'>Logout</a></div>"
    else:
        nav="<a href='/login' class='btn' style='background:#162032;color:#fff;padding:8px 16px;border-radius:10px;font-size:13px;border:1px solid #23324f'>Login</a>"
    return f"<div class='topbar'><div class='logo'>MASTERPICK<span>AI</span><span class='badge'>V10.5 SHARE</span></div>{nav}</div>"

@app.route("/")
def home():
    email=session.get("email"); user=USERS.get(email) if email else None
    fixtures=get_fixtures()
    html=f"<html><head>{STYLE}</head><body>"+header_html(email)
    if not email:
        html+="<div class='hero'><h1 style='font-size:26px;font-weight:800'>Real Games You Can<br>Find On SportyBet</h1><p style='color:#8aa0c5;font-size:13px;margin-top:8px'>MLS, Brazil, Saudi, EPL - All SportyBet verified. Share to WhatsApp!</p><br><a href='/signup' class='btn btn-primary'>Start Free</a><br><br><a href='/login' class='btn btn-dark'>Login</a></div></body></html>"
        return html
    html+="<div style='padding:16px'>"
    if user["status"]=="pending":
        html+=f"<div class='card pending'><div class='league' style='color:orange'>PENDING APPROVAL</div><div class='match'>Paid ₦{user['pending']}</div></div>"

    # Share All Button
    if fixtures:
        all_text="🔥 MASTERPICKAI TODAY - SportyBet Verified Real Fixtures:\n\n"
        for f in fixtures[:4]:
            all_text+=f"✅ {f['match']} - {f['tip']} @{f['odd']} - {f['league']}\n"
        all_text+=f"\nFree 2 games @1.56 - Pro 6 games @4.80\nJoin: https://masterpickai.onrender.com\nOpay: 09079789177"
        wa_all=wa_link(all_text)
        html+=f"<div style='display:flex;gap:8px;margin-bottom:12px'><a href='{wa_all}' target='_blank' class='btn-wa' style='width:100%;justify-content:center;padding:12px'>📲 SHARE ALL GAMES TO WHATSAPP</a></div>"

    html+=f"<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px'><div class='card' style='margin:0;text-align:center;padding:12px'><div style='font-size:20px;font-weight:800'>{len(fixtures)}</div><div class='league'>Real Today</div></div><div class='card' style='margin:0;text-align:center;padding:12px'><div style='font-size:20px;font-weight:800;color:#00ff88'>1.56</div><div class='league'>Free</div></div><div class='card' style='margin:0;text-align:center;padding:12px'><div style='font-size:20px;font-weight:800;color:gold'>4.80</div><div class='league'>Pro</div></div></div>"

    if len(fixtures)==0:
        html+="<div class='card'><div class='league'>No SportyBet games at this hour - Check later 12AM WAT when MLS/Brazil kickoff</div></div>"
    else:
        html+="<h3 style='margin:14px 4px'>🆓 FREE 2 Games @1.56</h3>"
        for f in fixtures[:2]:
            share_txt=f"MASTERPICKAI FREE TIP 🔥\n\n{f['match']}\n{f['league']} - {f['time']}\nTip: {f['tip']} @{f['odd']} - {f['conf']}\n\nVerified on SportyBet ✅\nJoin free: https://masterpickai.onrender.com"
            wa=wa_link(share_txt)
            html+=f"<div class='card'><div class='league'>{f['league']} • {f['time']} • SPORTYBET OK</div><div class='match'>{f['match']}</div><div class='tipbox'><div><div style='font-weight:700;font-size:13px'>✅ {f['tip']}</div><div class='conf'>{f['conf']}</div></div><div class='odd'>{f['odd']}</div></div><div style='margin-top:10px;display:flex;gap:8px'><a href='{wa}' target='_blank' class='btn-wa'>📲 WhatsApp Share</a><span style='color:#4a5f85;font-size:11px;margin-left:auto'>SportyBet verified</span></div></div>"

        html+="<h3 style='margin:18px 4px 8px'>👑 PRO 6 Games @4.80</h3>"
        if user["plan"]=="pro" and user["status"]=="active":
            for f in fixtures:
                share_txt=f"MASTERPICKAI PRO TIP 👑\n\n{f['match']}\n{f['league']}\nTip: {f['tip']} @{f['odd']}\n\nPro Acca @4.80\nhttps://masterpickai.onrender.com"
                wa=wa_link(share_txt)
                html+=f"<div class='card gold'><div class='league'>{f['league']} • {f['time']}</div><div class='match'>{f['match']}</div><div class='tipbox'><div><div style='font-weight:700;font-size:13px'>🔥 {f['tip']}</div></div><div class='odd' style='background:gold'>{f['odd']}</div></div><div style='margin-top:10px'><a href='{wa}' target='_blank' class='btn-wa'>📲 Share Pro Game</a></div></div>"
        else:
            html+="<div class='card' style='text-align:center;padding:22px'><div style='font-size:32px'>🔒</div><div class='match'>Pro Locked</div><div style='color:#8aa0c5;font-size:13px'>Pay to Opay 09079789177 to unlock + share</div><br><a href='/plans' class='btn btn-primary'>View Plans</a></div>"

    html+="<br><a href='/plans' class='btn btn-dark'>💳 Plans ₦1000-₦15000</a></div></body></html>"
    return html

@app.route("/plans")
def plans():
    html=f"<html><head>{STYLE}</head><body>{header_html(session.get('email'))}<div style='padding:16px;max-width:500px;margin:0 auto'><h2>Plans</h2><p style='color:#8aa0c5;font-size:13px'>Opay 09079789177 - Arinze</p>"
    for price,days in [("1000","3 Days"),("2000","7 Days"),("5000","15 Days"),("10000","25 Days"),("15000","30 Days")]:
        html+=f"<div class='card'><div style='display:flex;justify-content:space-between;align-items:center'><div><div class='match'>₦{price} - {days}</div></div><a href='/subscribe/{price}' class='btn btn-primary' style='width:auto'>I Paid</a></div></div>"
    html+="<br><a href='/' class='btn btn-dark'>← Home</a></div></body></html>"
    return html

@app.route("/subscribe/<plan>")
def subscribe(plan):
    email=session.get("email")
    if not email: return redirect("/login")
    USERS[email]["pending"]=plan; USERS[email]["status"]="pending"
    return redirect("/")

@app.route("/admin")
def admin_page():
    email=session.get("email")
    if not email or not USERS.get(email,{}).get("is_admin"):
        return f"<html><head>{STYLE}</head><body>{header_html(email)}<div style='padding:16px'>Not admin</div></body></html>"
    html=f"<html><head>{STYLE}</head><body>{header_html(email)}<div style='padding:16px'><h2>Admin Panel
