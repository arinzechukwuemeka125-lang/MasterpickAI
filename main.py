def fetch_any():
    now = time.time()
    today = get_today()
    if CACHE["games"] and CACHE["date"]==today and (now-CACHE["last"])<900:
        return CACHE["games"]
    USER = (os.environ.get("SOCCER_USER") or "ArinzeChukwuemeka").strip()
    TOK = (os.environ.get("SOCCER_TOKEN") or os.environ.get("SOCCER_API_KEY") or TOKEN).strip()
    try:
        all_games=[]
        # Check 3 days to always find games on FREE plan
        from datetime import timedelta
        import pytz
        try:
            base = datetime.now(pytz.timezone("Africa/Lagos"))
        except:
            base = datetime.utcnow()
        for delta in [0,1,-1]:
            d = (base + timedelta(days=delta)).strftime("%Y-%m-%d")
            url = f"https://api.soccersapi.com/v2.2/fixtures/?user={USER}&token={TOK}&t=schedule&d={d}"
            r = requests.get(url, timeout=20)
            j = r.json()
            CACHE["calls"]+=1
            data = j.get("data") or []
            for f in data:
                if not isinstance(f, dict): continue
                all_games.append({
                    "home": f.get("home_name","Home"),
                    "away": f.get("away_name","Away"),
                    "league": f.get("league_name","League"),
                    "time": (f.get("date_time","")[11:16] or "15:00"),
                    "date": d,
                })
            if len(all_games)>=10: break # enough
        # Any league, remove duplicates
        seen=set(); uniq=[]
        for g in all_games:
            k=g["home"]+g["away"]+g["date"]
            if k not in seen:
                seen.add(k); uniq.append(g)
        uniq=sorted(uniq, key=lambda x: x["date"])[:30]
        CACHE["games"]=uniq; CACHE["raw"]=len(uniq); CACHE["last"]=now; CACHE["date"]=today
        CACHE["error"]=f"Live ANY {len(uniq)} USER {USER[:4]} TOK {TOK[:4]}" if uniq else f"API 0 - Free plan no games? Resp {str(j)[:60]}"
        return uniq
    except Exception as e:
        CACHE["error"]=str(e)[:100]; return []
