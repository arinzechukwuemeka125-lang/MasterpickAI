# main.py - v20.3 SMART MODE - Python - Render Ready - No Emoji
import os
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
import json
import random

app = FastAPI()
TIMEZONE = pytz.timezone('Africa/Lagos')

def smart_pick(home_team, away_team, stats):
    markets = []

    home_goals = stats.get('home_avg', 1.8)
    away_goals = stats.get('away_avg', 1.2)
    home_concede = stats.get('home_concede', 1.0)
    away_concede = stats.get('away_concede', 1.5)

    # Team Over 1.5
    prob = 0.88 if home_goals > 1.8 else 0.75
    markets.append({
        "market": f"{home_team} Team Over 1.5",
        "odd": 1.32 if home_goals > 2.2 else 1.55,
        "w": int(prob*100),
        "rating": 9.9 if prob > 0.85 else 9.5
    })

    # Win + Over
    prob2 = 0.83 if home_goals > 1.5 and away_concede > 1.3 else 0.70
    markets.append({
        "market": f"{home_team} Win + Over 1.5",
        "odd": 1.35,
        "w": int(prob2*100),
        "rating": 9.8 if prob2 > 0.80 else 9.3
    })

    # Over 2.5
    prob3 = 0.82 if (home_goals + away_goals) > 2.5 else 0.71
    markets.append({
        "market": "Over 2.5",
        "odd": 1.45 if (home_goals + away_goals) > 2.8 else 2.05,
        "w": int(prob3*100),
        "rating": 9.7 if prob3 > 0.80 else 9.3
    })

    # BTTS
    prob4 = 0.75 if home_concede > 1.0 and away_goals > 0.9 else 0.60
    markets.append({
        "market": "BTTS Yes",
        "odd": 1.70,
        "w": int(prob4*100),
        "rating": 9.5 if prob4 > 0.72 else 9.0
    })

    markets.sort(key=lambda x: (x['w'], x['odd']), reverse=True)
    return markets[0]

def update_fixtures(date_str=None):
    tz = TIMEZONE
    date = date_str or datetime.now(tz).strftime('%Y-%m-%d')
    print(f"[{datetime.now(tz)}] Updating fixtures for {date} - SMART MODE")

    os.makedirs('data', exist_ok=True)

    mock = [
        ("Bayern Munich", "Bodo Glimt"),
        ("Man Utd", "Sabah"),
        ("PSV", "Shakhtar Donetsk"),
        ("Fenerbahce", "AS Roma"),
        ("Como", "RB Leipzig"),
        ("Slavia Praha", "Lens")
    ]

    fixtures = []
    for idx, (home, away) in enumerate(mock):
        stats = {
            'home_avg': random.uniform(1.5, 2.5),
            'away_avg': random.uniform(0.8, 1.6),
            'home_concede': random.uniform(0.8, 1.3),
            'away_concede': random.uniform(1.0, 1.8)
        }
        best = smart_pick(home, away, stats)
        fixtures.append({
            "id": idx+1,
            "home": home,
            "away": away,
            "time": datetime.now(tz).strftime('%H:%M WAT'),
            "bestPick": best,
            "date": date
        })

    with open(f'data/fixtures-{date}.json', 'w') as f:
        json.dump(fixtures, f, indent=2)

    top3 = sorted(fixtures, key=lambda x: x['bestPick']['w'], reverse=True)[:3]
    odd = 1
    for f in top3:
        odd *= f['bestPick']['odd']

    avg_w = sum([f['bestPick']['w'] for f in top3]) // 3
    print(f"Updated {len(fixtures)} fixtures - Ticket {odd:.2f} W{avg_w}")
    return fixtures

# CRON - 06:00 WAT DAILY
scheduler = BackgroundScheduler(timezone=TIMEZONE)
scheduler.add_job(lambda: update_fixtures(), 'cron', hour=6, minute=0)
scheduler.start()
print(f"Timezone set: Africa/Lagos - Current: {datetime.now(TIMEZONE)}")

@app.get("/")
async def root():
    today = datetime.now(TIMEZONE).strftime('%Y-%m-%d')
    path = f'data/fixtures-{today}.json'
    try:
        with open(path, 'r') as f:
            fixtures = json.load(f)
    except:
        fixtures = update_fixtures(today)
    return {"version": "v20.3 SMART", "timezone": "Africa/Lagos", "date": today, "fixtures": fixtures}

@app.get("/api/cron/update")
async def cron_update(request: Request):
    secret = request.query_params.get('secret')
    if secret!= os.getenv('CRON_SECRET', 'smart2026'):
        return JSONResponse({"error": "Forbidden"}, status_code=403)
    date = request.query_params.get('date') or datetime.now(TIMEZONE).strftime('%Y-%m-%d')
    fixtures = update_fixtures(date)
    return {"success": True, "fixtures": fixtures}
