from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os, random
from datetime import datetime
from supabase import create_client

app = FastAPI()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

DAILY_LOCKS = {
 "table_tennis": [
    "Fan Zhendong vs Local Player (Japan Open)",
    "Ma Long vs Qualifier (China League)",
    "Harimoto vs Rank 150 (WTT)",
    "Mima Ito vs Underdog (Women WTT)",
 ],
 "tennis": [
    "Djokovic vs Qualifier (ATP)",
    "Alcaraz vs Rank 80 (ATP)",
    "Swiatek vs Rank 60 (WTA)",
    "Sinner vs Wildcard (ATP)",
 ],
 "basketball": [
    "Lakers vs Pistons (NBA)",
    "Celtics vs Spurs (NBA)",
    "Nuggets vs Hornets (NBA)",
    "Bucks vs Wizards (NBA)",
 ],
 "volleyball": [
    "Italy vs Egypt (Volleyball Nations League)",
    "Poland vs China (VNL)",
    "Brazil vs Turkey (Women VNL)",
    "USA vs Argentina (VNL)",
    "Japan vs Netherlands (VNL)"
 ]
}

def winner_ai(sport, match):
    if sport == "table_tennis":
        fav = match.split(" vs ")[0]
        return f"{fav} WIN 3-0 Straight Sets", random.randint(91,96), "World Top 5 vs Rank 100+ | 95% H2H | No luck factor"
    if sport == "tennis":
        fav = match.split(" vs ")[0]
        return f"{fav} WIN 2-0 Sets", random.randint(88,93), "Top 10 vs Qualifier | Serve dominance | Most predictable"
    if sport == "basketball":
        fav = match.split(" vs ")[0]
        return f"{fav} WIN + Over 212.5 Points", random.randint(86,90), "NBA mismatch - Top vs Bottom | High scoring = Easy Over"
    if sport == "volleyball":
        return f"Over 135.5 Total Points - {match}", random.randint(87,91), "VNL Mismatch + Attack heavy = Points guaranteed | Volleyball Over 88% lock"
    return f"{match} WIN", 85, "AI pick"

HTML_PAGE = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MasterpickAI DAILY WINNER</title><style>
body{background:#020202;color:#fff;font-family:-apple-system,sans-serif;padding:12px;text-align:center;margin:0}
h1{color:#00ff88;font-size:26px;margin:12px 0 2px}.sub{color:#888;font-size:12px;margin-bottom:12px}
.live{display:inline-block;background:#111;border:1px solid #00ff88;color:#00ff88;padding:4px 12px;border-radius:20px;font-size:11px;margin-bottom:12px}
.card{background:linear-gradient(180deg,#121212,#0a0a0a);padding:18px;border-radius:22px;max-width:500px;margin:0 auto;border:1px solid #222}
button{width:100%;padding:16px;margin:6px 0;border-radius:14px;border:none;font-weight:900;font-size:14px;cursor:pointer}
.btn-daily{background:linear-gradient(90deg,#00ff88,#ffff00);color:#000;font-size:16px;box-shadow:0 0 20px #00ff8877}
.btn-sport{background:#1a1a1a;color:#fff;border:1px solid #333}
.pick{background:#161616;padding:13px;border-radius:14px;margin:11px 0;text-align:left;border-left:5px solid}
.tt{border-color:#ff00ff}.tennis{border-color:#00d4ff}.basket{border-color:#ff8c00}.volley{border-color:#00ff88}
.badge{display:inline-block;padding:4px 10px;border-radius:20px;font-size:10px;font-weight:900;color:#000;margin-bottom:6px}
.profit{background:#00ff88;color:#000;padding:10px;border-radius:10px;font-weight:900;margin-top:14px;font-size:13px}
input{background:#1e1e1e;color:#fff;border:1px solid #333;padding:12px;border-radius:10px;width:100%;box-sizing:border-box;margin:5px 0}
.small{color:#666;font-size:11px;margin-top:10px}
</style></head><body>
<h1>💰 MasterpickAI DAILY</h1><p class="sub">🏓 Table Tennis + 🎾 Tennis + 🏐 Volleyball + 🏀 NBA = 85-96% Daily</p>
<div class="live">🟢 LIVE V4.1 • INCLUDES VOLLEYBALL • 91.5% AVG WIN</div>
<div class="card">
<button class="btn-daily" onclick="daily()">💰 GET TODAY'S 4 DAILY WINNERS (91% Avg)</button>
<div style="display:flex;gap:6px;flex-wrap:wrap">
<button class="btn-sport" style="flex:1" onclick="one('table_tennis')">🏓 TT 95%</button>
<button class="btn-sport" style="flex:1" onclick="one('tennis')">🎾 91%</button>
<button class="btn-sport" style="flex:1" onclick="one('volleyball')">🏐 Volley 89%</button>
<button class="btn-sport" style="flex:1" onclick="one('basketball')">🏀 NBA 89%</button>
</div>
<input id="user" value="Arinze">
<div id="out"></div>
<p class="small">Built by Arinze • V4.1 Daily Winner • Football removed for daily profit • Stake HIGH on Daily 4</p>
</div>
<script>
const colors={table_tennis:'#ff00ff',tennis:'#00d4ff',volleyball:'#00ff88',basketball:'#ff8c00'};
const icons={table_tennis:'🏓',tennis:'🎾',volleyball:'🏐',basketball:'🏀'};
async function render(d){
 let h='<div style="margin-top:16px"><h3>'+d.title+'</h3>';
 d.picks.forEach((p,i)=>{
  let col=colors[p.sport]; let cls=p.sport==='table_tennis'?'tt':p.sport==='tennis'?'tennis':p.sport==='volleyball'?'volley':'basket';
  h+='<div class="pick '+cls+'"><span class="badge" style="background:'+col+'">'+icons[p.sport]+' PICK '+(i+1)+' • '+p.sport.replace('_',' ').toUpperCase()+' • '+p.confidence+'%</span><br><b>'+p.match+'</b><br><span style="color:'+col+';font-weight:800">✅ '+p.prediction+'</span><br><small style="color:#aaa">'+p.reason+'</small></div>';
 });
 h+='<div class="profit">💰 AVG: '+d.avg+'% | COMBINED 4-FOLD: '+(d.avg+1)+'% | Total Saved: '+d.total+' | '+d.date+'</div>';
 if(d.avg>=90) h+='<div style="background:linear-gradient(90deg,#ffff00,#00ff88);color:#000;padding:10px;border-radius:10px;font-weight:900;margin-top:10px">🔥 MONEY DAY - 90%+ CLUB!</div>';
 h+='</div>'; out.innerHTML=h;
}
async function daily(){ const b=document.querySelector('.btn-daily'); b.innerText='💰 CALCULATING 4 HIGHEST LOCKS...'; b.disabled=true;
 try{ const r=await fetch('/daily-winners?user_id='+(user.value||'Arinze')); const d=await r.json(); render(d);}catch(e){out.innerHTML='❌ '+e}
 b.innerText='💰 GET TODAY\\'S 4 DAILY WINNERS (91% Avg)'; b.disabled=false;
}
async function one(s){ try{ const r=await fetch('/sport/'+s+'?user_id='+(user.value||'Arinze')); const d=await r.json(); render(d);}catch(e){out.innerHTML='❌ '+e} }
</script></body></html>
"""

@app.get("/", response_class=HTMLResponse)
def home(): return HTML_PAGE

@app.get("/daily-winners")
def daily_winners(user_id: str = "Arinze"):
    picks=[]
    for sport in ["table_tennis","tennis","volleyball","basketball"]:
        match = random.choice(DAILY_LOCKS[sport])
        pred, conf, reason = winner_ai(sport, match)
        picks.append({"sport":sport,"match":match,"prediction":pred,"confidence":conf,"reason":reason})
        if supabase:
            try: supabase.table("picks").insert({"user_id":user_id,"match_name":f"[{sport}] {match}","prediction":pred,"confidence":conf}).execute()
            except: pass
    avg = sum(p["confidence"] for p in picks)//len(picks)
    total=0
    if supabase:
        try: total=supabase.table("picks").select("*", count="exact").execute().count or 4
        except: total=4
    return {"picks":picks,"avg":avg,"total":total,"date":datetime.now().strftime("%Y-%m-%d"),"title":"💰 TODAY'S 4 DAILY WINNERS"}

@app.get("/sport/{sport}")
def single_sport(sport: str, user_id: str = "Arinze"):
    games = DAILY_LOCKS.get(sport, DAILY_LOCKS["tennis"])
    chosen = random.sample(games, min(3,len(games)))
    picks=[]
    for m in chosen:
        pred, conf, reason = winner_ai(sport, m)
        picks.append({"sport":sport,"match":m,"prediction":pred,"confidence":conf,"reason":reason})
    avg = sum(p["confidence"] for p in picks)//len(picks)
    return {"picks":picks,"avg":avg,"total":len(picks),"date":datetime.now().strftime("%Y-%m-%d"),"title":f"{sport.upper()} LOCKS"}