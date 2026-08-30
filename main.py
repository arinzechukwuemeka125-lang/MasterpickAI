from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
from supabase import create_client

app = FastAPI(title="MasterpickAI")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

class PickRequest(BaseModel):
    user_id: str
    matches: list

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MasterpickAI - Live</title>
<style>
body{background:#0a0a0a;color:#fff;font-family:sans-serif;padding:20px;text-align:center}
h1{color:#00ff88}
.card{background:#1a1a1a;padding:20px;border-radius:15px;margin:20px auto;max-width:400px}
input,button{width:100%;padding:12px;margin:8px 0;border-radius:8px;border:none}
button{background:#00ff88;color:#000;font-weight:bold;font-size:16px}
#picks{margin-top:20px;text-align:left}
</style>
</head>
<body>
<h1>⚽ MasterpickAI</h1>
<p>AI Football Predictions - LIVE</p>
<div class="card">
<input id="user" placeholder="Your name" value="Arinze">
<input id="m1" placeholder="Match 1" value="Arsenal vs Chelsea">
<input id="m2" placeholder="Match 2" value="Man City vs Liverpool">
<input id="m3" placeholder="Match 3" value="Barcelona vs Real Madrid">
<button onclick="getPicks()">Get AI Picks 🔥</button>
<div id="picks"></div>
</div>
<script>
async function getPicks(){
 const user_id=document.getElementById('user').value;
 const matches=[document.getElementById('m1').value,document.getElementById('m2').value,document.getElementById('m3').value];
 const res=await fetch('/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id,matches})});
 const data=await res.json();
 document.getElementById('picks').innerHTML='<h3>🔥 AI Picks for '+data.user_id+':</h3>'+data.picks.map(p=>'✅ '+p).join('<br>')+'<br><br>Confidence: '+data.confidence*100+'%';
}
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_PAGE

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/predict")
def predict(req: PickRequest):
    return {"user_id": req.user_id, "picks": req.matches[:3], "confidence": 0.85}