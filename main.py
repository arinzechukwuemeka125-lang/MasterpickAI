import os,sqlite3,hashlib
from datetime import datetime,timedelta,timezone
from flask import Flask,request,redirect,session,render_template_string
app=Flask(__name__)
app.secret_key="a"
WAT=timezone(timedelta(hours=1))
ADMIN="arinzechukwuemeka125@gmail.com"
def get_db():
 db=sqlite3.connect("users.db")
 db.row_factory=sqlite3.Row
 return db
def init():
 db=get_db()
 db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY,email TEXT UNIQUE,password TEXT,created_at TEXT,trial_end TEXT,is_pro INTEGER DEFAULT 0,is_admin INTEGER DEFAULT 0,pro_expiry TEXT)")
 db.commit()
 if not db.execute("SELECT * FROM users WHERE email=?",(ADMIN,)).fetchone():
  far=(datetime.now(WAT)+timedelta(days=3650)).isoformat()
  db.execute("INSERT INTO users VALUES (NULL,?,?,?,?,?,?,?)",(ADMIN,hashlib.sha256("admin123".encode()).hexdigest(),datetime.now(WAT).isoformat(),far,1,1,far))
  db.commit()
init()
@app.route("/")
def home():
 return "<h1>MasterpickAI LIVE - Fixed!</h1><a href='/login'>Login</a>"
@app.route("/login",methods=["GET","POST"])
def login():
 if request.method=="POST":
  e=request.form["email"].lower()
  pw=hashlib.sha256(request.form["password"].encode()).hexdigest()
  db=get_db()
  u=db.execute("SELECT * FROM users WHERE email=?",(e,)).fetchone()
  if not u:
   te=(datetime.now(WAT)+timedelta(days=3)).isoformat()
   is_ad=1 if e==ADMIN else 0
   ex=(datetime.now(WAT)+timedelta(days=3650)).isoformat() if is_ad else te
   db.execute("INSERT INTO users VALUES (NULL,?,?,?,?,?,?,?)",(e,pw,datetime.now(WAT).isoformat(),te,is_ad,is_ad,ex))
   db.commit()
   session["user"]=e
   return redirect("/")
  if u["password"]==pw:
   session["user"]=e
   return redirect("/")
  return "Wrong"
 return "<form method=post><input name=email><input name=password type=password><button>Login</button></form>"
@app.route("/logout")
def logout():
 session.clear()
 return redirect("/")
if __name__=="__main__":
 app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
