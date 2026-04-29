# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "androidApp/src/main/assets/plants.db"

new_ro = (
    "Cimbrul de grădină (Satureja hortensis) este o plantă anuală aromatică din familia Lamiaceae, "
    "cultivată pe scară largă ca plantă condimentară și medicinală. Crește până la 30–60 cm înălțime "
    "și are frunze înguste, de culoare verde-bronzat, cu un miros intens și plăcut. Florile sunt mici, "
    "tubulare, de culoare lila sau alb-roz, și înfloresc din iulie până în septembrie.\n\n"
    "Cimbrul este una dintre cele mai importante plante aromatice din bucătăria românească. Este "
    "ingredientul esențial în prepararea sarmalelor, dar se folosește și la condimentarea tocănițelor, "
    "supelor, mâncărurilor din fasole și a cărnii la grătar. Aroma sa este dulce și delicată, ușor "
    "pipărată, ceea ce îl face ideal atât în preparate simple, cât și în rețete mai elaborate.\n\n"
    "În medicina naturistă, infuzia de cimbru este recomandată împotriva tusei, bronșitei și "
    "afecțiunilor căilor respiratorii. Are proprietăți antiseptice, antispastice și digestive, "
    "fiind util și în calmarea tulburărilor gastrointestinale.\n\n"
    "Se cultivă ușor din semințe, semănate primăvara devreme în locuri însorite, în sol ușor și "
    "permeabil. Plantele recoltate în perioada înfloririi se usucă pentru a fi folosite pe tot "
    "parcursul anului."
)

conn = sqlite3.connect(str(DB))
conn.execute("UPDATE museum_item SET description_ro=? WHERE id=67", (new_ro,))
conn.commit()

result = conn.execute("SELECT description_ro FROM museum_item WHERE id=67").fetchone()
print("OK — new description:")
print(result[0].encode("utf-8", errors="replace").decode("utf-8", errors="replace"))
conn.close()
