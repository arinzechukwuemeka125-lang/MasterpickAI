import os, requests, urllib.parse
from datetime import datetime, timedelta
from flask import Flask, request, redirect, session

app = Flask(__name__)
app.secret_key = "v11_6_football_volleyball_live"
API_KEY = "8623f52e5c8224c49f7bb676d1f68665"
ADMIN_EMAIL = "arinzechukwuemeka125@gmail.com"

USERS = {
    ADMIN_EMAIL: {"pass": "Master2026!Secure", "plan": "pro", "status": "active", "expiry": datetime.now() + timedelta(days=365), "is_admin": True, "pending": None, "joined": "2026-09-01"}
}

def get_live_fixtures():
    football = []
    volleyball = []
    headers = {"x-apisports-key": API_KEY}

    # FOOTBALL - Today + Tomorrow - LIVE REAL ONLY
    try:
        for day_offset in [0,1]:
            d = (datetime.now() + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            url = f"https://v3.football.api-sports.io/fixtures?date={d}"
            r = requests.get(url, headers=headers, timeout=10).json()
            for f in r.get("response", [])[:100]:
                home = f["teams"]["home"]["name"]
                away = f["teams"]["away"]["name"]
                time = f["fixture"]["date"][11:16]
                league = f["league"]["name"]
                football.append({"match": home + " vs " + away, "league": league, "time": time, "date": d, "tip": "Over 1.5 Goals", "odd": "1.40", "sport": "football"})
    except Exception as e:
        print("Football API error", e)

    # VOLLEYBALL - Today + Tomorrow - SAME KEY, DIFFERENT ENDPOINT - LIVE REAL ONLY
    try:
        for day_offset in [0,1]:
            d = (datetime.now() + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            url = f"https://v1.volleyball.api-sports.io/games?date={d}"
            r = requests.get(url, headers=headers, timeout=10).json()
            for v in r.get("response", [])[:50]:
                home = v["teams"]["home"]["name"]
                away = v["teams"]["away"]["name"]
                time = v["date"][11:16] if len(v["date"])>11 else "18:00"
                league = v["league"]["name"]
                volleyball.append({"match": home + " vs " + away, "league": league, "time": time, "date": d, "tip": "Over 144.5 Points", "odd": "1.38", "sport": "volleyball"})
    except Exception as e:
        print("Volleyball API error", e)

    # Deduplicate
    seen=set()
    uniq_f=[]
    for x in football:
        if x["match"] not in seen:
            uniq_f.append(x)
            seen.add(x["match"])
    seen=set()
    uniq_v=[]
    for x in volleyball:
        if x["match"] not in seen:
            uniq_v.append(x)
            seen.add(x["match"])

    return uniq_f, uniq_v

def wa_link(t): return "https://wa.me/?text=" + urllib.parse.quote(t)

STYLE = "<meta name='viewport' content='width=device-width, initial-scale=1'><style>*{font-family:sans-serif;box-sizing:border-box;margin:0;padding:0}body{background:#070a10;color:#fff}.topbar{background:#0e1525;padding:14px 18px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1e2a44}.logo{font-weight:800;font-size:18px}.logo span{color:#00ff88}.badge{background:#00ff88;color:#000;font-size:10px;padding:3px 8px;border-radius:20px;font-weight:800;margin-left:8px}.btn{border:none;padding:12px 18px;border-radius:12px;font-weight:700;text-decoration:none;display:inline-block;text-align:center}.btn-primary{background:#00ff88;color:#000;width:100%}.btn-dark{background:#162032;color:#fff;border:1px solid #23324f;width:100%}.btn-wa{background:#25D366;color:#fff;padding:8px 12px;border-radius:10px;font-size:12px;font-weight:700;text-decoration:none;display:inline-block}.card{background:#121b2c;border:1px solid #1e2a44;border-radius:18px;padding:16px;margin:10px 0}.card-v{background:#0f1a14;border:1px solid #1a3a2a;border-radius:18px;padding:16px;margin:10px 0}.match{font-weight:800;font-size:15px;margin:6px 0}.league{color:#6b7fa3;font-size:11px}.tipbox{background:#0a121f;border:1px dashed #1e3a5f;border-radius:12px;padding:10px;margin-top:10px;display:flex;justify-content:space-between}.odd{background:#00ff88;color:#000;padding:6px 12px;border-radius:10px;font-weight:800}.odd-v{background:#ffcc00;color:#000;padding:6px 12px;border-radius:10px;font-weight:800}.input{width:100%;padding:14px;background:#0f172a;border:1px solid #1e2a44;border-radius:12px;color:#fff;margin:8px 0}.login-wrap{max-width:400px;margin:40px auto;padding:24px}.stat{display:inline-block;background:#121b2c;border:1px solid #1e2a44;border-radius:14px;padding:12px 16px;margin:6px;min-width:80px;text-align:center}.tab{padding:6px 12px;border-radius:20px;font-weight:800;font-size:11px}.tab-f{background:#00ff88;color:#000}.tab-v{background:#ffcc00;color:#000}</style>"

def is_admin_user(email): return email == ADMIN_EMAIL and USERS.get(email, {}).get("is_admin")

def header_html(email=None):
    if email:
        admin_btn = "<a href='/admin' style='background:gold;color:#000;padding:6px 10px;border-radius:8px;font-size:11px;text-decoration:none;margin-right:8px;font-weight:800'>ADMIN</a>" if is_admin_user(email) else ""
        nav = f"<div style='font-size:11px'>{admin_btn}<span style='background:#162032;padding:6px 10px;border-radius:20px'>{email[:14]}</span> <a href='/logout' style='color:#6b7fa3;margin-left:8px;text-decoration:none'>Logout</a></div>"
    else:
        nav = "<a href='/login' style='background:#162032;color:#fff;padding:8px 14px;border-radius:10px;font-size:13px;text-decoration:none'>Login</a> <a href='/signup' style='background:#00ff88;color:#000;padding:8px 14px;border-radius:10px;font-size:13px;text-decoration:none;margin-left:6px;font-weight:700'>Sign Up</a>"
    return f"<div class='topbar'><div class='logo'>MASTERPICK<span>AI</span><span class='badge'>V11.6 F+V LIVE</span></div>{nav}</div>"

@app.route("/")
def home():
    email = session.get("email")
    user = USERS.get(email) if email else None
    football, volleyball = get_live_fixtures()
    total = len(football) + len(volleyball)
    html = f"<html><head>{STYLE}</head><body>{header_html(email)}"
    if not email:
        html += f"<div style='padding:16px'><div style='background:#0e1525;border:1px solid #1e2a44;border-radius:24px;padding:24px;text-align:center'><h1>{len(football)} Football + {len(volleyball)} Volleyball = {total} Live Real - Today+Tomorrow</h1><p style='color:#8aa0c5'>Same API Key - 2 Endpoints - No Fake - 100% Live</p><br><a href='/signup' class='btn btn-primary'>Create Free Account</a><br><br><a href='/login' class='btn btn-dark'>Login</a></div></div></body></html>"
        return html
    html += "<div style='padding:16px'>"
    if is_admin_user(email):
        html += "<div style='display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px'><a href='/history' class='btn-wa' style='background:#162032;border:1px solid #23324f'>History</a><a href='/plans' class='btn-wa' style='background:#162032;border:1px solid #23324f'>Plans</a><a href='/admin' class='btn-wa' style='background:gold;color:#000'>Admin</a></div>"
    else:
        html += "<div style='display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px'><a href='/history' class='btn-wa' style='background:#162032;border:1px solid #23324f'>History</a><a href='/plans' class='btn-wa' style='background:#162032;border:1px solid #23324f'>Upgrade</a></div>"
    html += f"<div style='margin:10px 0'><span class='stat'><b>{len(football)}</b><br><span class='league'>Football Live</span></span><span class='stat'><b>{len(volleyball)}</b><br><span class='league'>Volley Live</span></span><span class='stat'><b>{total}</b><br><span class='league'>Total T+TMW</span></span><span class='stat'><b>Same Key</b><br><span class='league'>Live Only</span></span></div>"

    if total == 0:
        html += "<div class='card' style='text-align:center;border-color:#ff6b6b'><div class='match'>No Live Games Today & Tomorrow - API Returned 0</div><div class='league'>Both Football + Volleyball endpoints returned 0 - Check API limit at api-sports.io (100/day free) - Resets midnight UTC -
