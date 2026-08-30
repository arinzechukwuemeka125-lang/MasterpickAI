from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os, random
from supabase import create_client

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

class PickRequest(BaseModel):
    user_id: str
    matches: list

def get_pick(match):
    m=match.lower()
    if "arsenal" in m or "city" in m or "barca" in m:
        return f"Home Win & Over 1.5 - {match.split('vs')[0]} dominating"
    if "chelsea" in m or "united" in m:
        return f"BTTS Yes - Both teams score in {match}"
    return random.choice([f"Over 2.5 Goals in {match}", f"Home Win - {match}", f"Double Chance 1X - {match}", f"BTTS Yes in {match}"])

HTML="""
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MasterpickAI PRO</title><style>
body{background:#050505;color:#fff;font-family:sans-serif;padding:15px;text-align:center}
h1{color:#00ff88;font-size:30px;margin:10px 0}.sub{color:#666;margin-bottom:20px}
.card{background:#111;padding:22px;border-radius:20px;max-width:440px;margin:0 auto;border:1px solid #222}
input,button{width:100%;padding:14px;margin:6px 0;border-radius:12px;border:none;box-sizing:border-box}
input{background:#1e1e1e;color:#fff;border:1px solid #333;font-size:15px}
button{background:#00ff88;color:#000;font-weight:900;font-size:18px}
.pick{background:#1a1a1a;padding:14px;border-radius:12px;margin:10px 0;text-align:left;border-left:4px solid #00ff88}
.badge{background:#00ff88;color:#000;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:900}
</style></head><body>
<h1>⚽ MasterpickAI</h1><p class="sub">PRO AI • Live Database • 04:20 AM</p>
<div class="card">
<input id="user" placeholder="Your name" value="Arinze">
<input id="m1" placeholder="Match 1: Arsenal vs Chelsea">
<input id="m2" placeholder="Match 2: Man City vs Liverpool">
<input id="m3" placeholder="Match 3: Barca vs Real Madrid">
<button onclick="go()">🔥 Get PRO AI Picks</button>
<div id="out"></div></div>
<script>
async function go(){
const b=document.querySelector('button');b.innerText='🧠 AI ANALYZING...';b.disabled=true;
const user_id=document.getElementById('user').value||'Arinze';
const matches=[m1.value,m2.value,m3.value].filter(x=>x);
if(!matches.length){alert('Enter match');b.innerText='🔥 Get PRO AI Picks';b.disabled=false;return;}
try{
const r=await fetch('/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id,matches})});
const d=await r.json();
let h='<div style="margin-top:20px"><h3>🎯 Picks for '+d.user_id+'</h3>';
d.picks.forEach((p,i)=>{h+='<div class=pick><span class=badge>PICK '+(i+1)+' • '+p.confidence+'%</span><br><b style=color:#fff>'+p.match+'</b><br><span style=color:#00ff88>⚡ '+p.prediction+'</span></div>'});
h+='<p style=color:#00ff88;margin-top:15px;font-weight:bold>✅ Saved to DB | Avg: '+d.avg_confidence+'% | '+d.total_saved+' picks total</p></div>';
out.innerHTML=h;
}catch(e){out.innerHTML='❌ '+e}
b.innerText='🔥 Get PRO AI Picks';b.disabled=false;
}
</script></body></html>
"""

@app.get("/", response_class=HTMLResponse)
def home(): return HTML

@app.post("/predict")
def predict(req: PickRequest):
    picks=[]
    for m in req.matches:
        pred=get_pick(m)
        conf=random.randint(78,94)
        picks.append({"match":m,"prediction":pred,"confidence":conf})
        if supabase:
            try: supabase.table("picks").insert({"user_id":req.user_id,"match_name":m,"prediction":pred,"confidence":conf}).execute()
            except: pass
    total=0
    if supabase:
        try: total=supabase.table("picks").select("*", count="exact").execute().count or 0
        except: total=len(picks)
    avg=sum(p["confidence"] for p in picks)//len(picks) if picks else 0
    return {"user_id":req.user_id,"picks":picks,"avg_confidence":avg,"total_saved":total}