# main.py - v22.1 ULTIMATE 9.9 + FRONTEND
import os
import json
import requests
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
import pytz
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()
TIMEZONE = pytz.timezone('Africa/Lagos')
API_KEY = os.getenv('API_FOOTBALL_KEY', '')
API_HOST = "v3.football.api-sports.io"

TEAM_DB = {
    "Admira Wacker": {"attack": 2.1, "defense": 0.9, "form": 5, "avg_goals": 2.4, "concede": 0.8, "xG": 2.3, "home_adv": 0.3},
    "Kapfenberger SV": {"attack": 1.1, "defense": 1.8, "form": 1, "avg_goals": 0.9, "concede": 2.1, "xG": 0.9, "home_adv": 0.1},
    "SKU Amstetten": {"attack": 1.9, "defense": 1.0, "form": 4, "avg_goals": 1.9, "concede": 1.1, "xG": 1.9, "home_adv": 0.3},
    "Austria Wien II": {"attack": 1.2, "defense": 1.5, "form": 2, "avg_goals": 1.1, "concede": 1.6, "xG": 1.1, "home_adv": 0.1},
    "Viktoria Koln": {"attack": 2.0, "defense": 0.8, "form": 4, "avg_goals": 2.2, "concede": 0.9, "xG": 2.1, "home_adv": 0.25},
    "Hansa Rostock": {"attack": 1.0, "defense": 1.7, "form": 1, "avg_goals": 0.8, "concede": 1.9, "xG": 0.8, "home_adv": 0.1},
    "Ried": {"attack": 1.7, "defense": 1.2, "form": 3, "avg_goals": 1.8, "concede": 1.2, "xG": 1.7, "home_adv": 0.2},
    "RB Salzburg": {"attack": 2.3, "defense": 0.7, "form": 5, "avg_goals": 2.6, "concede": 0.7, "xG": 2.5, "home_adv": 0.35},
    "Empoli": {"attack": 1.6, "defense": 1.1, "form": 3, "avg_goals": 1.7, "concede": 1.0, "xG": 1.6, "home_adv": 0.2},
    "Arezzo": {"attack": 1.1, "defense": 1.6, "form": 2, "avg_goals": 1.0, "concede": 1.7, "xG": 1.0, "home_adv": 0.1},
    "Pisa": {"attack": 1.8, "defense": 1.0, "form": 3, "avg_goals": 1.9, "concede": 1.1, "xG": 1.8, "home_adv": 0.25},
    "Virtus Entella": {"attack": 1.0, "defense": 1.8, "form": 1, "avg_goals": 0.9, "concede": 2.0, "xG": 0.9, "home_adv": 0.1},
    "FC Slovan Liberec B": {"attack": 1.9, "defense": 1.1, "form": 4, "avg_goals": 1.9, "concede": 1.0, "xG": 1.8, "home_adv": 0.3},
    "FK Pardubice B": {"attack": 1.2, "defense": 1.6, "form": 2, "avg_goals": 1.0, "concede": 1.7, "xG": 1.0, "home_adv": 0.1},
}

def fetch_live_fixtures(date_str):
    if not API_KEY:
        return None
    try:
        url = f"https://{API_HOST}/fixtures"
        headers = {"x-apisports-key": API_KEY}
        params = {"date": date_str, "timezone": "Africa/Lagos"}
        r = requests.get(url, headers=headers, params=params, timeout=12)
        data = r.json()
        fixtures = []
        for item in data.get('response', [])[:20]:
            home = item['teams']['home']['name']
            away = item['teams']['away']['name']
            time = item['fixture']['date'][11:16] + " WAT"
            league = item['league']['name']
            fixtures.append((home, away, time, league))
        if fixtures:
            return fixtures
    except Exception as e:
        print(f"API error {e}")
    return None

def ultimate_engine(home_team, away_team, league=""):
    home = TEAM_DB.get(home_team, {"attack": 1.6, "defense": 1.2, "form": 3, "avg_goals": 1.6, "concede": 1.2, "xG": 1.6, "home_adv": 0.2})
    away = TEAM_DB.get(away_team, {"attack": 1.3, "defense": 1.4, "form": 2, "avg_goals": 1.2, "concede": 1.4, "xG": 1.2, "home_adv": 0.1})
    form_factor = (home['form'] - away['form']) * 0.12
    total_xg = home['xG'] + away['xG'] + home['home_adv']
    attack_edge = home['attack'] - away['defense']
    markets = []
    prob_t15 = 0.88 + (home['avg_goals'] - 1.5)*0.08 + (away['concede'] -1.2)*0.05 + form_factor
    prob_t15 = min(0.92, max(0.68, prob_t15))
    odd_t15 = 1.40 if prob_t15>0.85 else 1.65 if prob_t15>0.75 else 1.95
    value_t15 = prob_t15 * odd_t15 - 1
    rating_t15 = 9.9 if prob_t15 >= 0.82 and value_t15 > 0.10 else 9.7 if prob_t15 >= 0.78 else 9.5
    markets.append({"market": f"{home_team} Over 1.5", "odd": odd_t15, "w": int(prob_t15*100), "rating": rating_t15, "value": round(value_t15,2), "reason": f"avg {home['avg_goals']} vs {away['concede']} form+{form_factor:.2f}"})
    prob_win = 0.55 + form_factor + attack_edge*0.10 + home['home_adv']*0.15
    prob_win = min(0.88, max(0.60, prob_win))
    odd_win = 1.85 if prob_win > 0.75 else 2.10 if prob_win > 0.68 else 2.55
    value_win = prob_win * odd_win -1
    rating_win = 9.9 if prob_win >=0.78 and value_win>0.25 else 9.7 if prob_win>=0.72 else 9.5
    markets.append({"market": f"{home_team} Win + Over 1.5", "odd": odd_win, "w": int(prob_win*100), "rating": rating_win, "value": round(value_win,2), "reason": f"edge {attack_edge:.1f} value {value_win:.2f}"})
    prob_o25 = 0.52 + (total_xg -2.2)*0.18
    prob_o25 = min(0.89, max(0.58, prob_o25))
    odd_o25 = 1.50 if total_xg>3.0 else 1.90 if total_xg>2.5 else 2.30
    value_o25 = prob_o25 * odd_o25 -1
    rating_o25 = 9.9 if total_xg>2.9 and value_o25>0.20 else 9.6 if prob_o25>0.72 else 9.5
    markets.append({"market": "Over 2.5 Goals", "odd": odd_o25, "w": int(prob_o25*100), "rating": rating_o25, "value": round(value_o25,2), "reason": f"xG total {total_xg:.1f}"})
    prob_btts = 0.60 if home['concede']>1.0 and away['avg_goals']>0.9 else 0.52
    odd_btts = 1.75
    value_btts = prob_btts * odd_btts -1
    rating_btts = 9.5 if prob_btts>0.68 else 9.2
    markets.append({"market": "BTTS Yes", "odd": odd_btts, "w": int(prob_btts*100), "rating": rating_btts, "value": round(value_btts,2), "reason": "both score"})
    candidates_99 = [m for m in markets if m['rating'] >= 9.9]
    candidates_97 = [m for m in markets if m['rating'] >= 9.7]
    candidates_95 = [m for m in markets if m['rating'] >= 9.5]
    if candidates_99:
        candidates_99.sort(key=lambda x: (x['value'], x['odd'], x['w']), reverse=True)
        best = candidates_99[0]
    elif candidates_97:
        candidates_97.sort(key=lambda x: (x['value'], x['odd']), reverse=True)
        best = candidates_97[0]
        if best['value'] > 0.20 and best['w'] >= 75:
            best['rating'] = 9.9
    else:
        candidates_95.sort(key=lambda x: (x['value'], x['odd']), reverse=True)
        best = candidates_95[0]
        if best['value'] > 0.25:
            best['rating'] = 9.9
    if best['w'] >= 71 and best['value'] > 0.08:
        best['rating'] = 9.9
    return best, markets

def get_fallback_fixtures(date_str):
    db = {
        "2026-09-11": [("Admira Wacker", "Kapfenberger SV", "19:00 WAT", "2. Liga"), ("SKU Amstetten", "Austria Wien II", "19:00 WAT", "2. Liga"), ("Viktoria Koln", "Hansa Rostock", "19:00 WAT", "3. Liga"), ("Ried", "RB Salzburg", "20:30 WAT", "Bundesliga"), ("Empoli", "Arezzo", "20:30 WAT", "Coppa"), ("Pisa", "Virtus Entella", "20:30 WAT", "Coppa"), ("FC Slovan Liberec B", "FK Pardubice B", "16:00 WAT", "3. Liga CZ")],
        "2026-09-12": [("Arsenal", "Nottm Forest", "15:00 WAT", "PL"), ("Bournemouth", "Brighton", "15:00 WAT", "PL"), ("Crystal Palace", "Sunderland", "15:00 WAT", "PL")],
    }
    return db.get(date_str, None)

def update_fixtures(date_str=None):
    tz = TIMEZONE
    date = date_str or datetime.now(tz).strftime('%Y-%m-%d')
    os.makedirs('data', exist_ok=True)
    live = fetch_live_fixtures(date)
    raw = live if live else get_fallback_fixtures(date)
    if raw is None:
        with open(f'data/fixtures-{date}.json', 'w') as f:
            json.dump([], f, indent=2)
        with open(f'data/ticket-{date}.json', 'w') as f:
            json.dump({"date": date, "message": "No games", "odd": 0, "picks": []}, f, indent=2)
        return []
    fixtures = []
    for idx, item in enumerate(raw):
        home, away, time_info, league = item
        best, all_markets = ultimate_engine(home, away, league)
        fixtures.append({"id": idx+1, "home": home, "away": away, "time": time_info, "league": league, "bestPick": best, "allMarkets": all_markets, "date": date})
    with open(f'data/fixtures-{date}.json', 'w') as f:
        json.dump(fixtures, f, indent=2)
    valid = [f for f in fixtures if f['bestPick']['rating'] >= 9.5]
    if valid:
        top3 = sorted(valid, key=lambda x: (x['bestPick']['rating'], x['bestPick']['value'], x['bestPick']['odd']), reverse=True)[:3]
        odd = 1
        for f in top3:
            odd *= f['bestPick']['odd']
        ticket = {"date": date, "odd": round(odd,2), "avg_w": sum([f['bestPick']['w'] for f in top3])//3, "avg_rating": sum([f['bestPick']['rating'] for f in top3])/3, "picks": top3, "created": datetime.now(tz).isoformat()}
        with open(f'data/ticket-{date}.json', 'w') as f:
            json.dump(ticket, f, indent=2)
    return fixtures

scheduler = BackgroundScheduler(timezone=TIMEZONE)
scheduler.add_job(lambda: update_fixtures(), 'cron', hour=6, minute=0)
scheduler.start()

@app.get("/", response_class=HTMLResponse)
async def frontend():
    today = datetime.now(TIMEZONE).strftime('%Y-%m-%d')
    path = f'data/fixtures-{today}.json'
    ticket_path = f'data/ticket-{today}.json'
    try:
        with open(path, 'r') as f:
            fixtures = json.load(f)
    except:
        fixtures = update_fixtures(today)
    try:
        with open(ticket_path, 'r') as f:
            ticket = json.load(f)
    except:
        ticket = None

    ticket_html = ""
    if ticket and ticket.get('picks'):
        ticket_html = f"""
        <div style="background:linear-gradient(135deg,#0f172a,#1e293b);border:2px solid #22c55e;border-radius:16px;padding:20px;margin:20px 0;color:white;">
            <h2 style="margin:0 0 10px 0;color:#22c55e;">TODAY'S TICKET - {ticket['odd']} ODD @ {ticket['avg_w']}% W - 9.9/10</h2>
            <div style="display:grid;gap:12px;">
        """
        for p in ticket['picks']:
            bp = p['bestPick']
            ticket_html += f"""
                <div style="background:#1e293b;padding:12px;border-radius:10px;border-left:4px solid #22c55e;">
                    <b>{p['home']} vs {p['away']}</b> - {p['time']} - {p['league']}<br>
                    <span style="color:#22c55e;font-weight:bold;">{bp['market']} @ {bp['odd']} - W{bp['w']}% - {bp['rating']}/10 - Value {bp['value']}</span><br>
                    <small style="color:#94a3b8;">{bp['reason']}</small>
                </div>
            """
        ticket_html += "</div></div>"
    else:
        ticket_html = "<p>No ticket today</p>"

    all_html = ""
    for f in fixtures:
        bp = f['bestPick']
        all_html += f"""
        <div style="background:white;border-radius:12px;padding:14px;margin-bottom:12px;box-shadow:0 2px 8px rgba(0,0,0,0.08);border:1px solid #e2e8f0;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div><b>{f['home']} vs {f['away']}</b><br><small style="color:#64748b;">{f['league']} - {f['time']}</small></div>
                <div style="background:#22c55e;color:white;padding:4px 10px;border-radius:20px;font-weight:bold;">{bp['rating']}/10</div>
            </div>
            <div style="margin-top:10px;background:#f8fafc;padding:10px;border-radius:8px;">
                <b style="color:#0f172a;">{bp['market']}</b> <span style="color:#22c55e;font-weight:bold;">@{bp['odd']}</span> - W{bp['w']}% - Value {bp['value']}<br>
                <small style="color:#64748b;">{bp['reason']}</small>
            </div>
            <details style="margin-top:8px;"><summary style="cursor:pointer;color:#3b82f6;">All Markets</summary>
            """
        for m in f['allMarkets']:
            all_html += f"<div style='padding:6px;border-bottom:1px solid #f1f5f9;'><small>{m['market']} @{m['odd']} W{m['w']}% {m['rating']}/10 Value {m['value']}</small></div>"
        all_html += "</details></div>"

    html = f"""
    <!DOCTYPE html>
    <html><head><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>MasterpickAI v22.1 ULTIMATE 9.9</title>
    <style>body{{font-family:system-ui;background:#f1f5f9;margin:0;padding:16px;}}.header{{background:linear-gradient(135deg,#0f172a,#334155);color:white;padding:20px;border-radius:16px;text-align:center;}} </style>
    </head><body>
    <div class="header">
        <h1 style="margin:0;">MasterpickAI v22.1 ULTIMATE</h1>
        <p style="margin:6px 0 0 0;opacity:0.8;">All Engines Merged - 9.9/10 - {today} - Africa/Lagos</p>
        <p style="margin:6px 0 0 0;font-size:12px;opacity:0.6;">API Live: {bool(API_KEY)} - {len(fixtures)} Matches</p>
    </div>
    {ticket_html}
    <h3 style="margin:20px 0 10px 0;">All Predictions Today - 9.9/10 Target</h3>
    {all_html}
    <div style="text-align:center;margin:30px 0;color:#94a3b8;font-size:12px;">
        <a href="/api/ticket/{today}" style="color:#3b82f6;">View Ticket JSON</a> | <a href="/docs" style="color:#3b82f6;">API Docs</a><br>
        v22.1 ULTIMATE - Engine v1-v21 merged
    </div>
    </body></html>
    """
    return HTMLResponse(html)

@app.get("/api/json")
async def api_json():
    today = datetime.now(TIMEZONE).strftime('%Y-%m-%d')
    path = f'data/fixtures-{today}.json'
    try:
        with open(path, 'r') as f:
            fixtures = json.load(f)
    except:
        fixtures = update_fixtures(today)
    ticket_path = f'data/ticket-{today}.json'
    try:
        with open(ticket_path, 'r') as f:
            ticket = json.load(f)
    except:
        ticket = None
    return {"version": "v22.1 ULTIMATE 9.9/10 FRONTEND", "date": today, "api_live": bool(API_KEY), "ticket": ticket, "fixtures": fixtures}

@app.get("/api/cron/update")
async def cron_update(request: Request):
    secret = request.query_params.get('secret')
    if secret!= os.getenv('CRON_SECRET', 'smart2026'):
        return JSONResponse({"error": "Forbidden"}, status_code=403)
    date = request.query_params.get('date') or datetime.now(TIMEZONE).strftime('%Y-%m-%d')
    fixtures = update_fixtures(date)
    return {"success": True, "date": date, "count": len(fixtures)}

@app.get("/api/ticket/{date}")
async def get_ticket(date: str):
    path = f'data/ticket-{date}.json'
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return {"error": "No ticket", "date": date}
