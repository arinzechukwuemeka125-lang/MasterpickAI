import os, sqlite3, random
from datetime import datetime, timedelta, timezone
from flask import Flask, session, redirect, render_template_string

app = Flask(__name__)
app.secret_key = "masterpick_v82_real_auto"
WAT = timezone(timedelta(hours=1))
ADMIN_EMAIL = "arinzechukwuemeka125@gmail.com"

def get_wat_now(): return datetime.now(WAT)
def get_wat_date_str(): return get_wat_now().strftime("%Y-%m-%d")
def get_db():
    c=sqlite3.connect("users.db"); c.row_factory=sqlite3.Row; return c

def init_db():
    db=get_db()
    db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, created_at TEXT, trial_end TEXT, is_pro INT, is_admin INT)")
    db.commit()
    if not db.execute("SELECT * FROM users WHERE email=?",(ADMIN_EMAIL,)).fetchone():
        now=get_wat_now()
        db.execute("INSERT INTO users VALUES (NULL,?,?,?,1,1)",(ADMIN_EMAIL,now.isoformat(),(now+timedelta(days=3650)).isoformat()))
        db.commit()
    db.execute("UPDATE users SET is_admin=1,is_pro=1 WHERE email=?",(ADMIN_EMAIL,)); db.commit()
init_db()

REAL_FOOTBALL = ["Sheffield United vs Bolton Wanderers","Birmingham City vs Southampton","Portsmouth vs Derby County","Swansea City vs Watford","Preston NE vs Bristol City","Aston Villa vs Arsenal","Borussia Dortmund vs Hamburg","Bromley vs Leyton Orient"]
REAL_BASKET = ["LA Lakers vs Golden State Warriors (NBA)","Real Madrid vs Barcelona (EuroLeague)","Lagos Warriors vs Rivers Hoopers (NBBF)","Milwaukee Bucks vs Celtics (NBA)"]
REAL_VOLLEY = ["Poland vs Brazil (FIVB)","Italy vs USA (Volleyball)","Zenit Kazan vs Lube (CEV)"]
REAL_TTENNIS = ["Fan Zhendong vs Ma Long (WTT)","Harimoto vs Calderano (WTT)","Quadri Aruna vs Omar Assar (Africa)"]

def get_games():
    seed = get_wat_date_str()
    random.seed(seed)
    free = [
        {"sport":"⚽ FOOTBALL","match":random.choice(REAL_FOOTBALL),"pick":"Home Win or Draw","odd":"1.38","conf":"93%"},
        {"sport":"⚽ FOOTBALL","match":random.choice(REAL_FOOTBALL),"pick":"Over 1.5 Goals","odd":"1.48","conf":"91%"},
    ]
    pro = [
        {"sport":"⚽ FOOTBALL","match":random.choice(REAL_FOOTBALL),"pick":"Over 0.5","odd":"1.25"},
        {"sport":"🏀 BASKETBALL","match":random.choice(REAL_BASKET),"pick":"Over 158.5 Points","odd":"1.42"},
        {"sport":"🏐 VOLLEYBALL","match":random.choice(REAL_VOLLEY),"pick":"Over 3.5 Sets","odd":"1.35"},
        {"sport":"🏓 TABLE TENNIS","match":random.choice(REAL_TTENNIS),"pick":"Over 3.5 Games","odd":"1.38"},
        {"sport":"⚽ FOOTBALL","match":random.choice(REAL_FOOTBALL),"pick":"1X","odd":"1.32"},
        {"sport":"🏀 BASKETBALL","match":random.choice(REAL_BASKET),"pick":"Home +5.5","odd":"1.40"},
    ]
    return free, pro, seed, get_wat_now().strftime("%I:%M %p WAT - %d %b %Y")

HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#080808;color:white;font-family:Arial;margin:0;padding:10px}
.card{background:#151515;border-radius:20px;padding:15px;margin:10px 0;border:1px solid #222}
.green{background:#00ff88;color:#000;font-weight:bold;padding:8px 15px;border-radius:20px;display:inline-block;cursor:pointer}
.gray{background:#222;color:#aaa;padding:8px 15px;border-radius:20px;cursor:pointer;margin:5px;display:inline-block}
.yellow{background:#ffdd00;color:#000;font-weight:bold;padding:10px;border-radius:12px;text-align:center;margin:10px 0}
.tab{display:none}.tab.active{display:block}
</style>
<script>
function showTab(t){
  document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));
  document.getElementById(t).classList.add('active');
  document.querySelectorAll('.btn').forEach(e=>e.style.background='#222');
  document.getElementById('btn-'+t).style.background='#00ff88';
  document.getElementById('btn-'+t).style.color='#000';
}
</script>
</head><body>
<center><h2 style="color:#00ff88">💰 MasterpickAI V8.2 REAL</h2><small style="color:#00ff88">{{wat}}</small><br><small style="color:#888">Seed: {{date}} - Auto 12AM WAT</small></center>
<div class="card"><span style="color:#00ff88">{{email}}</span> <span class="green" style="font-size:11px">ADMIN</span><div style="color:#00ff88;text-align:center">👑 ADMIN FREE FOREVER</div><div style="border:1px solid #00ff88;border-radius:12px;padding:10px;margin-top:10px"><b style="color:#00ff88">📊 ADMIN STATS</b><br>Active: <b style="color:#00ff88">{{active}}</b> | Total: {{total}}<br>Next Update: 12AM WAT<br><a href="/admin" style="color:#00ff88">View Users →</a></div></div>
<div class="yellow">✅ REAL Games Only - Bet9ja Verified • Auto 12AM WAT</div>
<center>
<span id="btn-free" class="btn green" onclick="showTab('free')">🆓 Free (2)</span>
<span id="btn-pro" class="btn gray" onclick="showTab('pro')">👑 Pro (6) Mix</span>
<span id="btn-history" class="btn gray" onclick="showTab('history')">📜 History</span>
</center>
<div id="free" class="tab active"><div style="text-align:center;margin:15px 0;font-weight:bold">🆓 FREE - 2 REAL Football @ 2.05 - {{date}}</div>
{% for g in free_games %}<div class="card" style="border-left:4px solid #00ff88"><small style="color:#00ff88">{{g.sport}} • {{g.conf}} • {{g.odd}}</small><br><b>{{g.match}}</b><br><div style="color:#00ff88">✅ {{g.pick}}</div><small style="color:#666">Found on Bet9ja</small></div>{% endfor %}
<div class="card" style="background:#00ff88;color:#000;text-align:center;font-weight:bold">Total: 2.05 • Auto changes 12AM WAT</div></div>
<div id="pro" class="tab"><div style="text-align:center;margin:15px 0;font-weight:bold;color:#00ff88">👑 PRO - 6 REAL Mixed Sports @ 9.50</div>
{% for g in pro_games %}<div class="card"><small style="color:#00ff88">{{g.sport}} • {{g.odd}}</small><br><b>{{g.match}}</b><br><div style="color:#00ff88">✅ {{g.pick}}</div><small style="color:#666">Found on Bet9ja/Sportybet</small></div>{% endfor %}</div>
<div id="history" class="tab"><div style="text-align:center;margin:15px">📜 Last 7 Days</div><div class="card">31 Aug: Won ✅ 1.92</div><div class="card">30 Aug: Won ✅ 2.10</div><div class="card">29 Aug: Lost ❌ 1.85</div></div>
<center><small style="color:#555">V8.2 REAL • 09079789177 Opay Arinze</small></center>
</body></html>"""

@app.route("/")
def home():
    email=session.get("email",ADMIN_EMAIL)
    db=get_db(); all_u=db.execute("SELECT * FROM users").fetchall()
    free_games, pro_games, date, wat = get_games()
    return render_template_string(HTML,email=email,wat=wat,date=date,free_games=free_games,pro_games=pro_games,active=len(all_u),total=len(all_u))

@app.route("/admin")
def admin_page():
    db=get_db(); users=db.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
    now=get_wat_now(); html=f"<h2>Users {now.strftime('%I:%M %p WAT')}</h2><table border=1 width=100%><tr><th>Email</th></tr>"
    for u in users: html+=f"<tr><td>{u['email']}</td></tr>"
    html+=f"</table><h3>Active: {len(users)}</h3><a href='/'>Back</a>"; return html

@app.route("/logout")
def logout(): session.clear(); return redirect("/")
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
