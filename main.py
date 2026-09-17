# main.py - V24 CRON - Runs and exits
from datetime import datetime

class V24:
    def depth_audit(self, a, b):
        sa = (a["form_score"]*0.4 + a["squad_depth"]*0.4 + a["motivation"]*0.2)
        if a["home"]: sa+=5
        sa-= len(a["injuries"])*5
        sb = (b["form_score"]*0.4 + b["squad_depth"]*0.4 + b["motivation"]*0.2)
        if b["home"]: sb+=5
        sb-= len(b["injuries"])*5
        return max(0,min(100,sa)), max(0,min(100,sb)), abs(sa-sb)

def run_v24():
    v24 = V24()
    print(f"=== MasterpickAI V24 AUDIT {datetime.now()} ===")
    betis = {"name":"Betis","form_score":80,"squad_depth":85,"motivation":85,"home":True,"injuries":["Llorente","Ruibal","Ezzalzouli","Barea"]}
    getafe = {"name":"Getafe","form_score":35,"squad_depth":60,"motivation":60,"home":False,"injuries":["Kiko","Abqar","Uche","Juanmi","Serrano"]}
    malaga = {"name":"Malaga","form_score":20,"squad_depth":45,"motivation":70,"home":True,"injuries":["Lobete","Calero","Diarra","Murillo","Ochoa","Nino","Sanchez"]}
    villarreal = {"name":"Villarreal","form_score":30,"squad_depth":70,"motivation":80,"home":False,"injuries":["Foyth"]}
    alvarez = {"name":"Alvarez","form_score":85,"squad_depth":88,"motivation":90,"home":False,"injuries":[]}
    tallakson = {"name":"Tallakson","form_score":30,"squad_depth":45,"motivation":60,"home":False,"injuries":["fatigue"]}
    katpelly = {"name":"Katpelly","form_score":70,"squad_depth":72,"motivation":90,"home":False,"injuries":[]}
    stephens = {"name":"Stephens","form_score":25,"squad_depth":35,"motivation":50,"home":False,"injuries":["form"]}
    matches = [(betis,getafe),(malaga,villarreal),(alvarez,tallakson),(katpelly,stephens)]
    for a,b in matches:
        sa,sb,gap = v24.depth_audit(a,b)
        status = "PASS" if gap >= 20 else "REJECT"
        print(f"{a['name']} {sa:.0f}% vs {b['name']} {sb:.0f}% | Gap {gap:.0f}% {status}")
    ticket_a = 1.22*1.35*1.35*1.50*1.18
    ticket_b = 1.65*1.35*1.35*1.50*1.18
    print(f"\nTICKET A SAFE 600k @ {ticket_a:.2f} = Return {600000*ticket_a:.0f}")
    print(f"TICKET B 5ODD 400k @ {ticket_b:.2f} = Return {400000*ticket_b:.0f}")
    print("=== V24 DONE ===")

if __name__ == "__main__":
    run_v24()
