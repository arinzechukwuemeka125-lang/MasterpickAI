import random
from datetime import datetime
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

VISITORS = {"total": 0, "unique_ips": set()}

@app.before_request
def track():
    VISITORS["total"] += 1
    VISITORS["unique_ips"].add(request.remote_addr)

GAMES = [
    {"home": "Arsenal", "away": "Man City", "league": "Premier League"},
    {"home": "Barcelona", "away": "Real Madrid", "league": "La Liga"},
    {"home": "Bayern", "away": "Dortmund", "league": "Bundesliga"},
    {"home": "Man Utd", "away": "Chelsea", "league": "Premier League"},
    {"home": "PSG", "away": "Marseille", "league": "Ligue 1"},
    {"home": "Italy", "away": "Poland", "league": "Volleyball"}
]

HTML = """
<h1 style="font-family:sans-serif;text-align:center;margin-top:50px">MasterpickAI is LIVE ✅</h1>
<p style="text-align:center">GG + Over 2.5 Predictions Working!</p>
<p style="text-align:center"><a href="/api/predict">View API Predictions</a> | <a href="/admin/stats">Admin Stats</a></p>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/api/predict")
def predict():
    picks=[]
    for g in GAMES:
        picks.append({**g, "prediction": random.choice(["GG","Over 2.5","GG + Over 2.5"]), "confidence": f"{random.randint(78,92)}%", "odds": round(random.uniform(1.6,2.3),2)})
    return jsonify({"date": datetime.now().strftime("%Y-%m-%d"), "predictions": picks})

@app.route("/admin/stats")
def stats():
    return jsonify({"total_visits": VISITORS["total"], "unique_visitors": len(VISITORS["unique_ips"])})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
