# main.py - MasterpickAI V24 - CRON VERSION
from datetime import datetime

print(f"=== MasterpickAI V24 START {datetime.now()} ===")

# Depth Audit Function
def audit(team):
    score = (team["form"]*0.4 + team["depth"]*0.4 + team["motivation"]*0.2)
    if team["home"]: score += 5
    score -= len(team["injuries"])*5
    return max(0, min(100, score))

# Teams Data
betis = {"name":"Real Betis","form":80,"depth":85,"motivation":85,"home":True,"injuries":["Llorente","Ruibal","Ezzalzouli","Barea"]}
getafe = {"name":"Getafe","form":35,"depth":60,"motivation":60,"home":False,"injuries":["Kiko","Abqar","Uche","Juanmi","Serrano"]}
malaga = {"name":"Malaga","form":20,"depth":45,"motivation":70,"home":True,"injuries":["Lobete","Calero","Diarra","Murillo","Ochoa","Nino","Sanchez"]}
villarreal = {"name":"Villarreal B","form":30,"depth":70,"motivation":80,"home":False,"injuries":["Foyth"]}

# Audit
b_score = audit(betis)
g_score = audit(getafe)
m_score = audit(malaga)
v_score = audit(villarreal)

print(f"Betis {b_score:.0f}% vs Getafe {g_score:.0f}% | Gap {b_score-g_score:.0f}% PASS")
print(f"Malaga {m_score:.0f}% vs Villarreal {v_score:.0f}% | Gap {abs(m_score-v_score):.0f}% PASS")

# Tickets
ticket_a = 1.22*1.35*1.35*1.50*1.18
ticket_b = 1.65*1.35*1.35*1.50*1.18

print(f"\nTICKET A SAFE 600k @ {ticket_a:.2f} = Return {600000*ticket_a:.0f} Naira")
print(f"TICKET B 5ODD 400k @ {ticket_b:.2f} = Return {400000*ticket_b:.0f} Naira")
print("=== V24 DONE - Ready for 10AM ===")
