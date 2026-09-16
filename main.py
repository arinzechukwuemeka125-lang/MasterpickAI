# V24 - MyBetCode Safe Bet System
# Version: 24.2 - After Fleetwood 1-0 Lesson Sep 16
# Rule: No depth sheet = No pick
# Author: V24 Engine for Arinze - 1M Split System

from datetime import datetime

class V24:
    def __init__(self):
        self.min_conf = 75
        self.min_depth_gap = 20  # Increased from 10 after Fleetwood lesson
        self.safe_risks = ["LOW"]
        self.vip_risks = ["LOW", "MED"]
    
    def depth_audit(self, team_a, team_b):
        """Independent depth audit per team - V24 core"""
        score_a = (team_a["form_score"]*0.4 + team_a["squad_depth"]*0.4 + team_a["motivation"]*0.2)
        if team_a["home"]:
            score_a += 5
        score_a -= len(team_a["injuries"])*5
        score_a = max(0, min(100, score_a))
        
        score_b = (team_b["form_score"]*0.4 + team_b["squad_depth"]*0.4 + team_b["motivation"]*0.2)
        if team_b["home"]:
            score_b += 5
        score_b -= len(team_b["injuries"])*5
        score_b = max(0, min(100, score_b))
        
        gap = abs(score_a - score_b)
        return score_a, score_b, gap

    def screen(self, pick):
        """MyBetCode 3 screens"""
        if pick["data_completeness"] < 75:
            return "REJECT - Data <75%"
        if pick["odds"] < 1.15 or pick["odds"] > 4.0:
            return "REJECT - Odds extreme"
        if pick["conf"] < self.min_conf:
            return "WATCHLIST - Conf <75%"
        if pick["risk"] not in self.safe_risks and pick["ticket_type"] == "FREE":
            return "WATCHLIST - MED/HIGH for FREE"
        if pick["depth_gap"] < self.min_depth_gap:
            return "WATCHLIST - Gap <20%"
        # Today's lesson: Cup Over with defence <70% = REJECT
        if pick.get("cup_game") and pick.get("pick_type") == "Over" and pick.get("def_depth",100) < 70:
            return "REJECT - Lesson: Cup Over defence <70%"
        return "APPROVED"

# ========== DEPTH SHEETS - SEP 17 - INDEPENDENT AUDIT ==========
# Tennis - UTR - Tomorrow Sep 17 2026 11AM PDT (19:00 Lagos)

alvarez = {
    "name": "Alvarez",
    "form_score": 85,  # 3-0 group, H2H 6-1 6-2 vs Tallakson
    "squad_depth": 88,
    "motivation": 90,
    "home": False,
    "injuries": []
}

tallakson = {
    "name": "Tallakson",
    "form_score": 30,  # 0-3 group, 3 losses last 4
    "squad_depth": 45,
    "motivation": 60,
    "home": False,
    "injuries": ["fatigue", "serve 51%"]
}

katpelly = {
    "name": "Katpelly",
    "form_score": 70,  # Won yesterday 6-2 6-4 vs Sherif
    "squad_depth": 72,
    "motivation": 90,
    "home": False,
    "injuries": []
}

stephens = {
    "name": "Stephens",
    "form_score": 25,  # 5-12 season, lost 6-1 6-2 last
    "squad_depth": 35,
    "motivation": 50,
    "home": False,
    "injuries": ["form", "confidence"]
}

# Football - La Liga - Tomorrow Sep 17 2026

betis = {
    "name": "Betis",
    "form_score": 80,  # W-W-L-W-W 4 wins last 5
    "squad_depth": 85,  # Isco, Antony, Fornals, Roca, Hernandez fit
    "motivation": 85,
    "home": True,
    "injuries": ["Llorente", "Ruibal", "Ezzalzouli", "Barea"]  # 4 out but not core
}

getafe = {
    "name": "Getafe",
    "form_score": 35,  # L-W-L-D-D 1 win last 5
    "squad_depth": 60,  # 5 injuries
    "motivation": 60,
    "home": False,
    "injuries": ["Kiko", "Abqar", "Uche", "Juanmi", "Serrano", "Garcia doubt"]  # 5+1
}

malaga = {
    "name": "Malaga",
    "form_score": 20,  # L-D-L-D-D 0 wins
    "squad_depth": 45,  # 7 injuries
    "motivation": 70,
    "home": True,
    "injuries": ["Lobete", "Calero", "Diarra", "Murillo", "Ochoa", "Nino", "Sanchez"]  # 7 out
}

villarreal = {
    "name": "Villarreal",
    "form_score": 30,  # D-D-L-L-L 0 wins but stronger squad
    "squad_depth": 70,  # Only Foyth out
    "motivation": 80,
    "home": False,
    "injuries": ["Foyth"]
}

barca = {
    "name": "Barcelona",
    "form_score": 90,  # Top of table
    "squad_depth": 95,
    "motivation": 90,
    "home": True,
    "injuries": []
}

racing = {
    "name": "Racing Santander",
    "form_score": 40,
    "squad_depth": 55,
    "motivation": 60,
    "home": False,
    "injuries": []
}

# ========== RUN AUDIT ==========
v24 = V24()

print("========== V24 DEPTH AUDIT - SEP 17 ==========")
pairs = [
    (alvarez, tallakson),
    (katpelly, stephens),
    (betis, getafe),
    (malaga, villarreal),
    (barca, racing)
]

for a, b in pairs:
    sa, sb, gap = v24.depth_audit(a, b)
    print(f"{a['name']} {sa:.0f}% vs {b['name']} {sb:.0f}% = Gap {gap:.0f}%")

# ========== PICKS - FINAL 1M SPLIT ==========
picks = [
    {
        "match": "Betis vs Getafe",
        "pick": "1X",
        "odds": 1.22,
        "conf": 86,
        "risk": "LOW",
        "depth_gap": 25,
        "data_completeness": 85,
        "ticket_type": "FREE",
        "cup_game": False,
        "pick_type": "1X",
        "def_depth": 85
    },
    {
        "match": "Betis vs Getafe",
        "pick": "WIN",
        "odds": 1.65,
        "conf": 78,
        "risk": "MED",
        "depth_gap": 25,
        "data_completeness": 85,
        "ticket_type": "VIP",
        "cup_game": False,
        "pick_type": "WIN",
        "def_depth": 85
    },
    {
        "match": "Malaga vs Villarreal",
        "pick": "Over 1.5",
        "odds": 1.35,
        "conf": 82,
        "risk": "LOW",
        "depth_gap": 25,
        "data_completeness": 80,
        "ticket_type": "FREE",
        "cup_game": False,
        "pick_type": "Over",
        "def_depth": 60
    },
    {
        "match": "Alvarez vs Tallakson",
        "pick": "Alvarez WIN",
        "odds": 1.35,
        "conf": 85,
        "risk": "LOW",
        "depth_gap": 43,
        "data_completeness": 80,
        "ticket_type": "FREE",
        "cup_game": False,
        "pick_type": "WIN",
        "def_depth": 100
    },
    {
        "match": "Katpelly vs Stephens",
        "pick": "Katpelly WIN",
        "odds": 1.50,
        "conf": 80,
        "risk": "LOW",
        "depth_gap": 37,
        "data_completeness": 80,
        "ticket_type": "FREE",
        "cup_game": False,
        "pick_type": "WIN",
        "def_depth": 100
    },
    {
        "match": "Barca vs Racing",
        "pick": "Barca WIN",
        "odds": 1.18,
        "conf": 87,
        "risk": "LOW",
        "depth_gap": 50,
        "data_completeness": 90,
        "ticket_type": "FREE",
        "cup_game": False,
        "pick_type": "WIN",
        "def_depth": 95
    },
]

print("\n========== V24 SCREEN - MyBetCode 3 Screens ==========")
for p in picks:
    status = v24.screen(p)
    print(f"{p['match']} {p['pick']} @{p['odds']} Gap{p['depth_gap']}% Conf{p['conf']}% {p['risk']} -> {status}")

# ========== TICKET BUILDER - 1M SPLIT ==========
ticket_a_odds = 1.22 * 1.35 * 1.35 * 1.50 * 1.18  # 3.933
ticket_b_odds = 1.65 * 1.35 * 1.35 * 1.50 * 1.18  # 5.319

print("\n========== FINAL TICKETS - 1M SPLIT ==========")
print(f"Ticket A - V24-SAFE-393 - 600k stake - 3.93 ODD")
print(f"  Betis 1X @1.22 x Malaga Over1.5 @1.35 x Alvarez @1.35 x Katpelly @1.50 x Barca WIN @1.18")
print(f"  Return: {600000*ticket_a_odds:.0f} Naira | Profit: {600000*ticket_a_odds - 600000:.0f}")

print(f"\nTicket B - V24-5ODD-532 - 400k stake - 5.32 ODD")
print(f"  Betis WIN @1.65 x Malaga Over1.5 @1.35 x Alvarez @1.35 x Katpelly @1.50 x Barca WIN @1.18")
print(f"  Return: {400000*ticket_b_odds:.0f} Naira | Profit: {400000*ticket_b_odds - 400000:.0f}")

print(f"\nTotal staked: 1,000,000 | Total possible return: {600000*ticket_a_odds + 400000*ticket_b_odds:.0f}")

# ========== AUTO UPDATE CHECK ==========
now = datetime.now()
print(f"\nLast audit: {now} Lagos time")
print("Next auto re-audit: 12AM, 10AM, 6PM Lagos")
print("If Isco out for Betis, downgrade Ticket B WIN->1X (back to 3.93)")
print("Lesson from Sep 16: Fleetwood 1-0 - Cup Over with defence <70% rejected - Applied in screen()")

# End
