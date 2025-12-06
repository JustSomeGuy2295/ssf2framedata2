import json
import sqlite3

char = 'Bandana Dee'


con = sqlite3.connect("data/academy.db")
cur = con.cursor()

db_char_id = cur.execute("SELECT id FROM characters WHERE name=?", (char,)).fetchone()[0]

hitboxes = cur.execute("""
    SELECT hit, startup, active, endlag, damage, first_actionable_frame, landing_lag, image, 
           sourspot_damage, sweetspot_damage, tipper_damage, notes,
           intangible, invulnerable, armored, slowmo, angle, cooldown, autocancel_window, move_id
    FROM hitboxes 
    WHERE char_id=?
""", (db_char_id,)).fetchall()

con.close()

hits = []

for idx, row in enumerate(hitboxes):
        hits.append(row[0])
        
        con = sqlite3.connect("data/academy.db")
        cur = con.cursor()
        move = cur.execute("SELECT display_name FROM moves WHERE id=?", (row[19],)).fetchone()[0]
        con.close()
        
        info = {
            'Startup': row[1], 'Active': row[2], 'Endlag': row[3],
            'Damage': row[4], 'FAF': row[5], 'Landing Lag': row[6], 'Autocancel': row[18],
            'Sweetspot Damage': row[9], 'Tipper Damage': row[10], 'Sourspot Damage': row[8],
            'Angle': row[16], 'Cooldown': row[17],
            'Intangible': row[12], 'Invulnerable': row[13], 'Armored': row[14],
            'Notes': row[11]
        }
        print(move)
        if row[0] != None:
            print(row[0])
        else:
            print(move)
        for i, j in enumerate(info):          
            if info[j] != None:
                print(f'{j}: {info[j]}')

        desc = "\n".join(f"{k}: {v}" for k, v in info.items() if v is not None)