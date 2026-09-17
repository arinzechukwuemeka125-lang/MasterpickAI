import os, requests, datetime, random

def send_telegram(text):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=15)
    except Exception as e:
        print(f"Telegram error: {e}")

today = datetime.date.today()
today_str = today.strftime("%Y-%m-%d")
today_espn = today.strftime("%Y%m%d")
print(f"=== MasterpickAI V24 AUTO FETCH {today_str} ===")

LEAGUES = {
    "eng.1": "EPL",
    "esp.1": "La Liga",
    "ita.1": "Serie A",
    "ger.1": "Bundesliga",
    "fra.1": "Ligue 1"
}

all_games = []

for code, name in LEAGUES.items():
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{code}/scoreboard?dates={today_espn}"
        r = requests.get(url, timeout=10)
        data = r.json()
        for ev in data.get("events", []):
            comp = ev["competitions"][0]
            home = comp["competitors"][0]
            away = comp["competitors"][1]
            # Fix home/away
            if home["homeAway"]!= "home":
                home, away = away, home

            # Try get win prob from ESPN predictor, else use form + home advantage
            h_pct = 50
            a_pct = 30
            try:
                # ESPN odds
                if "odds" in comp and comp["odds"]:
                    h_pct = float(comp["odds"][0].get("homeWinPercentage", 55))
                    a_pct = float(comp["odds"][0].get("awayWinPercentage", 25))
                else:
                    # fallback: use record + home advantage 15%
                    h_wins = int(home.get("records", [{}])[0].get("summary", "0-0").split("-")[0]) if home.get("records") else 5
                    a_wins = int(away.get("records", [{}])[0].get("summary", "0-0").split("-")[0]) if away.get("records") else 3
                    h_pct = 45 + (h_wins - a_wins)*3 + 15 # home advantage
                    h_pct = max(10, min(85, h_pct))
                    a_pct = 100 - h_pct - 20 # draw 20%
            except:
                h_pct = random.randint(50, 75)
                a_pct = random.randint(15, 35)

            gap = abs(h_pct - a_pct)
            status = "PASS" if gap >= 38 else "SKIP"

            all_games.append({
                "league": name,
                "home": home["team"]["displayName"],
                "away": away["team"]["displayName"],
                "h_pct": h_pct,
                "a_pct": a_pct,
                "gap": gap,
                "status": status
            })
            print(f"{home['team']['displayName']} {h_pct:.0f}% vs {away['team']['displayName']} {a_pct:.0f}% | Gap {gap:.0f}% {status} [{name}]")
    except Exception as e:
        print(f"Error {name}: {e}")
        continue

# Filter PASS games sorted by gap
pass_games = sorted([g for g in all_games if g["status"]=="PASS"], key=lambda x: x["gap"], reverse=True)

if not pass_games:
    print("No PASS games today, using backup")
    # backup from top gaps
    pass_games = sorted(all_games, key=lambda x: x["gap"], reverse=True)[:4]

# Build tickets
if len(pass_games) >= 2:
    g1 = pass_games[0]
    g2 = pass_games[1] if len(pass_games)>1 else pass_games[0]
    g3 = pass_games[2] if len(pass_games)>2 else g1

    odd_a = round(1.6 + (g1["gap"]/100)*2 + (g2["gap"]/100)*1.5, 2)
    odd_b = round(2.2 + (g1["gap"]/100)*2.5 + (g2["gap"]/100)*2 + (g3["gap"]/100)*1.5, 2)

    # Cap odds
    odd_a = min(odd_a, 4.5)
    odd_b = min(odd_b, 6.5)

    stake_a = 600000
    stake_b = 400000
    ret_a = stake_a * odd_a
    ret_b = stake_b * odd_b

    print(f"TICKET A SAFE 600k @{odd_a} = {ret_a:,.0f} Naira")
    print(f"TICKET B 5ODD 400k @{odd_b} = {ret_b:,.0f} Naira")

    # Telegram message
    msg_lines = [f"🔥 MasterpickAI V24 AUTO - {today_str}", ""]
    for g in pass_games[:5]:
        msg_lines.append(f"{'✅' if g['status']=='PASS' else '⚪'} {g['home']} {g['h_pct']:.0f}% vs {g['away']} {g['a_pct']:.0f}% | Gap {g['gap']:.0f}% {g['status']} [{g['league']}]")
    msg_lines.append("")
    msg_lines.append(f"💰 TICKET A SAFE 600k @{odd_a} = {ret_a:,.0f} Naira")
    msg_lines.append(f" -> {g1['home']} to Win + {g2['home']} to Win")
    msg_lines.append("")
    msg_lines.append(f"💰 TICKET B 5ODD 400k @{odd_b} = {ret_b:,.0f} Naira")
    msg_lines.append(f" -> {g1['home']}, {g2['home']}, {g3['home']}")
    msg_lines.append("")
    msg_lines.append("Auto-fetch GitHub - 10AM WAT daily")

    send_telegram("\n".join(msg_lines))
else:
    print("No games today")
    send_telegram(f"MasterpickAI {today_str}: No games found today")

print(f"=== V24 DONE ===")
