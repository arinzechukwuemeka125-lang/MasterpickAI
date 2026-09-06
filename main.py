import os,time,requests
from datetime import datetime,timedelta
from flask import Flask,request,redirect,session,render_template_string
app=Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY","mpai2026")
TOKEN=(os.environ.get("SOCCER_TOKEN") or os.environ.get("SOCCER_API_KEY") or "eX1YOAIGVy").strip()
USER=(os.environ.get("SOCCER_USER") or "ArinzeChukwuemeka").strip()
CACHE={"games":[],"raw":0,"calls":0,"error":"","last":0,"date":""}
USERS={"admin@masterpickai.com":{"password":"Admin123!","is_pro":True,"approved":True,"is_admin":True}}
def get_today():
 try:
  import pytz
  return datetime.now(pytz.timezone("Africa/Lagos")).strftime("%Y-%m-%d")
 except:
  return datetime.utcnow().strftime("%Y-%m-%d")
def fetch_any():
 now=time.time()
 today=get_today()
 if CACHE["games"] and CACHE["date"]==today and (now-CACHE["last"])<900:
  return CACHE["games"]
 try:
  all_games=[]
  base=datetime.utcnow()
  for delta in [0,1,-1]:
   d=(base+timedelta(days=delta)).strftime("%Y-%m-%d")
   url=f"https://api.soccersapi.com/v2.2/fixtures/?user={USER}&token={TOKEN}&t=schedule&d={d}"
   r=requests.get(url,timeout=20)
   j=r.json()
   CACHE["calls"]+=1
   data=j.get("data") or []
   for f in data:
    if not isinstance(f,dict): continue
    all_games.append({"home":f.get("home_name","Home"),"away":f.get("away_name","Away"),"league":f.get("league_name","League"),"time":(f.get("date_time","")[11:16] if f.get("date_time") else "15:00"),"date":d})
   if len(all_games)>=8: break
  seen=set();uniq=[]
  for g in all_games:
   k=g["home"]+g["away"]+g["date"]
   if k not in seen:
    seen.add(k);uniq.append(g)
  uniq=sorted(uniq,key=lambda x:x["date"])[:30]
  CACHE["games"]=uniq;CACHE["raw"]=len(uniq);CACHE["last"]=now;CACHE["date"]=today
  CACHE["error"]=f"Live ANY {len(uniq)} USER {USER[:5]}"
  if len(uniq)==0: CACHE["error"]=f"API 0 keys {list(j.keys())[:4]}"
  return uniq
 except Exception as e:
  CACHE["error"]=str(e)[:100];return []
@app.route("/")
def home():
 games=fetch_any()
 return f'<body style="background:#060b1a;color:#fff;font-family:sans-serif"><div style="max-width:420px;margin:0 auto;padding:24px"><h1>Masterpick AI</h1><p>RAW {CACHE["raw"]} {CACHE["error"]}</p><a href="/login" style="display:block;background:#22c55e;color:#000;padding:14px;text-align:center;border-radius:12px;text-decoration:none">Login</a></div></body>'
@app.route("/login",methods=["GET","POST"])
def login():
 if request.method=="POST":
  e=request.form.get("email","").lower().strip();p=request.form.get("password","")
  u=USERS.get(e)
  if u and u["password"]==p:
   session["email"]=e
   return redirect("/games")
 return '<form method="post" style="max-width:320px;margin:80px auto"><input name="email" placeholder="Email"><input name="password" type="password"><button>Login</button></form>'
@app.route("/games")
def games_page():
 if "email" not in session: return redirect("/login")
 games=fetch_any()
 html=f'<body style="background:#060b1a;color:#fff"><h2>{get_today()} ANY LEAGUE {len(games)}</h2><p>{CACHE["error"]}</p>'
 for g in games:
  html+=f'<div style="background:#141d38;margin:6px;padding:10px;border-radius:8px">{g["league"]} | {g["date"]} {g["time"]}<br><b>{g["home"]} vs {g["away"]}</b></div>'
 html+='</body>'
 return html
@app.route("/logout")
def logout():
 session.pop("email",None)
 return redirect("/")
if __name__=="__main__":
 app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
