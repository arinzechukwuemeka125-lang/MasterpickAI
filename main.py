import os, random, requests, urllib.parse
from datetime import datetime, timedelta
from flask import Flask, session, redirect, request

app = Flask(__name__)
app.secret_key = "v36_1_sporty22bet_wat_ft_final"

API_KEY = os.environ.get("API_KEY", "")
ADMIN_EMAIL = "arinzechukwuemeka125@gmail.com"
OPAY_ACCOUNT = "09079789177"
OPAY_NAME = "Arinze Chukwuemeka P"

USERS = {ADMIN_EMAIL: {"pass": "Master2026!Secure", "plan": "pro", "status": "active", "joined": "2026-09-01"}}
CACHE = {"games": [], "free_games": [], "pro_games": [], "date": None, "fetched_at": None, "history": [], "api_calls": 0, "api_error": "", "raw_count": 0, "display_date": None}

def get_wat():
    wat_now = datetime.utcnow() + timedelta(hours=1)
    today = wat_now.strftime("%Y-%m-%d")
    yesterday = (wat_now - timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow = (wat_now + timedelta(days=1)).strftime("%Y-%m-%d")
    return today, yesterday, tomorrow, wat_now

def fetch_real(d):
    try:
        headers = {"x-apisports-key": API_KEY}
        r = requests.get(f"https://v3.football.api-sports.io/fixtures?date={d}", headers=headers, timeout=15)
        j = r.json()
        CACHE["api_calls"] += 1
        if j.get("errors") and j["errors"]:
            CACHE["api_error"] = str(j["errors"])
            return []
        if j.get("response") and isinstance(j["response"], list):
            if d == get_wat()[0]:
                CACHE["raw_count"] = len(j["response"])
            return j["response"]
        return []
    except Exception as e:
        CACHE["api_error"] = str(e)
        return []

def calc_18_local(fix):
    hname = fix["teams"]["home"]["name"]
    tip = "Over 1.5 Goals"
    odd = f"{1.42+random.random()*0.12:.2f}"
    wr = 94
    if random.random() > 0.6:
        tip = f"{hname} Win"
        odd = f"{1.65+random.random()*0.25:.2f}"
        wr = 88
    return tip, odd, wr

def update_all():
    today, yesterday, tomorrow, wat_now = get_wat()
    if CACHE["date"]!= today or not CACHE["games"]:
        CACHE["api_calls"] = 0; CACHE["api_error"] = ""; CACHE["raw_count"] = 0
        y_fix = fetch_real(yesterday)
        y_games = []
        for f in y_fix[:10]:
            hg = f["goals"]["home"]; ag = f["goals"]["away"]; status = f["fixture"]["status"]["short"]
            res = "PENDING"
            ft_mark = ""
            if status in ["FT","AET","PEN"] and hg is not None:
                ft_mark = "FT"
                res = "WON" if (hg+ag)>1.5 else "LOST"
            tip, odd, wr = calc_18_local(f)
            try:
                utc_dt = datetime.strptime(f["fixture"]["date"], "%Y-%m-%dT%H:%M:%S%z")
                wat_dt = utc_dt + timedelta(hours=1)
                wat_time = wat_dt.strftime("%H:%M WAT")
            except:
                wat_time = f["fixture"]["date"][11:16] + " WAT"
            y_games.append({"match": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}", "league": f["league"]["name"], "score": f"{hg}-{ag}" if hg is not None else "-", "ft": ft_mark, "result": res, "date": yesterday, "tip": tip, "odd": odd, "time": wat_time})
        CACHE["history"] = y_games
        t_fix = fetch_real(today)
        tm_fix = fetch_real(tomorrow)
        BOOKIE_LEAGUES = ["Premier League","La Liga","Serie A","Bundesliga","Ligue 1","Eredivisie","Primeira Liga","Championship","Pro League","Super Lig","Brasileiro","Serie B","Primera Division","Liga Profesional","MLS","Major League","Saudi","Champions League","Europa League","Europa Conference","Conference League","World Cup","World Cup - Qualification","Africa -","AFCON","Euro - Qualification","Nations League","Copa Libertadores","Copa Sudamericana"]
        def is_bookie_league(league_name):
            return any(b.lower() in league_name.lower() for b in BOOKIE_LEAGUES)
        filtered_today = [f for f in t_fix if is_bookie_league(f["league"]["name"])]
        filtered_tom = [f for f in tm_fix if is_bookie_league(f["league"]["name"])]
        use_date = today
        source_fix = filtered_today
        if len(filtered_today) < 4 and len(filtered_tom) >= 4:
            source_fix = filtered_tom
            use_date = tomorrow
        elif len(filtered_today) == 0:
            source_fix = t_fix[:4]
        CACHE["display_date"] = use_date
        all_games = []
        for f in source_fix[:12]:
            tip, odd, wr = calc_18_local(f)
            hg = f["goals"]["home"]; ag = f["goals"]["away"]; status = f["fixture"]["status"]["short"]
            ft_mark = ""; score = ""
            if status in ["FT","AET","PEN"] and hg is not None:
                ft_mark = "FT"
                score = f"{hg}-{ag}"
            try:
                utc_dt = datetime.strptime(f["fixture"]["date"], "%Y-%m-%dT%H:%M:%S%z")
                wat_dt = utc_dt + timedelta(hours=1)
                wat_time = wat_dt.strftime("%H:%M WAT")
            except:
                wat_time = f["fixture"]["date"][11:16] + " WAT"
            all_games.append({"match": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}", "league": f["league"]["name"], "country": f["league"]["country"], "tip": tip, "odd": odd, "wr": wr, "time": wat_time, "ft": ft_mark, "score": score, "status": status, "date": use_date})
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
.gold{border-color:rgba(255,204,51,0.25);box-shadow:0
