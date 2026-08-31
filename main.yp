import random
from datetime import datetime
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# --- ADMIN TRACKING (WORKS - NO BUG) ---
VISITORS = {"total": 0, "unique_ips": set()}

@app.before_request
def track():
    VISITORS["total"] += 1
    VISITORS["unique_ips"].add(request.remote_addr or "unknown")

GAMES = [
    {"home": "Arsenal", "away": "Man City", "league": "Premier League", "sport": "football", "time": "Today 16:00"},
    {"home": "Barcelona", "away": "Real Madrid", "league": "La Liga", "sport": "football", "time": "Today 19:00"},
    {"home": "USA", "away": "Brazil", "league": "Volleyball", "sport": "volleyball", "time": "Today 14:30"},
    {"home": "Italy", "away": "Poland", "league": "Nations League", "sport": "volleyball", "time": "Today 18:00"},
    {"home": "Ma Long", "away": "Fan Zhendong", "league": "WTT Championship", "sport": "table-tennis", "time": "Today 12:00"},
    {"home": "Bayern", "away": "Dortmund", "league": "Bundesliga", "sport": "football", "time": "Tomorrow 17:30"},
]

def get_preds():
    games = GAMES.copy()
    random.shuffle(games)
    free, pro = [], []
    for i, g in enumerate(games[:6]):
        time = g["time"]
        match = f"{g['home']} vs {g['away']} ({g['league']}) - {time}"
        options = [
            {"prediction": "Home Win or Draw", "odd": 1.35, "confidence": 93, "reason": f"{g['home']} strong home {time}"},
            {"prediction": "Over 2.5 Goals", "odd": 1.85, "confidence": 90, "reason": f"Over 2.5 expected - {g['league']} {time}"},
            {"prediction": "GG - Both Teams To Score YES", "odd": 1.78, "confidence": 89, "reason": f"Both to score {g['home']} vs {g['away']} {time}"},
            {"prediction": "Over 1.5 Goals", "odd": 1.42, "confidence": 91, "reason": f"At least 2 goals {time}"},
            {"prediction": "GG & Over 2.5", "odd": 2.15, "confidence": 88, "reason": f"GG & Over 2.5 - Open game {time}"},
            {"prediction": "Away Win or Draw", "odd": 1.55, "confidence": 87, "reason": f"{g['away']} good away {time}"},
        ]
        p = options[i % len(options)]
        pick = {"sport": g["sport"], "match": match, "prediction": p["prediction"], "odd": p["odd"], "confidence": p["confidence"], "reason": p["reason"]}
        if len(free) < 2: free.append(pick)
        pro.append(pick)
    return free, pro

HTML = """<!DOCTYPE html><html><head><title>MasterpickAI</title><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{background:#0f0f0f;color:#fff;font-family:Arial;padding:20px}.card{background:#1e1e1e;padding:15px;margin:10px 0;border-radius:10px;border-left:4px solid #00ff88}.sport{font-size:11px;color:#00ff88;text-transform:uppercase}.match{font-weight:bold;margin:6px 0}.pred{color:#ffcc00;font-weight:bold}.confidence{float:right;background:#00ff88;color:#000;padding:2px 8px;border-radius:10px;font-size:12px}a{color:#00ff88;text-decoration:none}h2{margin-top:30px}</style></head><body><h1>🔥 MasterpickAI - All Odds</h1><p><a href='/admin'>📊 Admin Dashboard</a></p><h2>Free Picks</h2><div id="free"></div><h2>Pro Picks (6 Types - GG + Over 2.5 Included)</h2><div id="pro"></div><script>fetch('/api/predictions').then(r=>r.json()).then(d=>{let a='';d.free.forEach(p=>{a+=`<div class="card"><span class="sport">${p.sport} • ${p.match.split(' - ').pop()}</span><span class="confidence">${p.confidence}%</span><div class="match">${p.match}</div><div class="pred">${p.prediction} @ ${p.odd}</div><small>${p.reason}</small></div>`});document.getElementById('free').innerHTML=a;let b='';d.pro.forEach(p=>{b+=`<div class="card"><span class="sport">${p.sport}</span><span class="confidence">${p.confidence}%</span><div class="match">${p.match}</div><div class="pred">${p.prediction} @ ${p.odd}</div><small>${p.reason}</small></div>`});document.getElementById('pro').innerHTML=b})</script></body></html>"""

ADMIN = """<!DOCTYPE html><html><head><title>Admin</title><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{background:#111;color:#fff;font-family:Arial;padding:20px}.box{background:#1e1e1e;padding:20px;margin:15px 0;border-radius:10px}.big{font-size:40px;color:#ffcc00}h2{color:#00ff88}</style></head><body><h1>📊 Admin Dashboard - MasterpickAI</h1><a href='/' style='color:#00ff88'>← Home</a><div class="box"><h2>Total Views</h2><div class="big">{{total}}</div></div><div class="box"><h2>Unique Visitors</h2><div class="big">{{unique}}</div></div><div class="box"><h2>Time</h2><p>{{time}}</p></div><div class="box"><h2>Features Active</h2><p>✅ GG YES</p><p>✅ Over 2.5</p><p>✅ GG & Over 2.5</p><p>✅ Football + Volleyball + Table Tennis</p><p>✅ Match Time</p></div></body></html>"""

@app.route("/")
def home(): return render_template_string(HTML)

@app.route("/admin")
def admin(): return render_template_string(ADMIN, total=VISITORS["total"], unique=len(VISITORS["unique_ips"]), time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route("/api/predictions")
def api(): f,p = get_preds(); return jsonify({"free": f, "pro": p, "generated_at": datetime.now().isoformat()})

if __name__ == "__main__": app.run(host="0.0.0.0", port=10000)
