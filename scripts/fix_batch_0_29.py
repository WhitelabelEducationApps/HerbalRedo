# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import sqlite3
from pathlib import Path

DB = Path(r"C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db")
conn = sqlite3.connect(DB)
conn.text_factory = lambda b: b.decode("utf-8", errors="replace")

fixes = [
    # ID 0 Acai palm — wrong IT (different plant!) and FR (Latin not French)
    (0,  "paintingname_it", "Açaí"),
    (0,  "paintingname_fr", "Palmier açaí"),

    # ID 8 Belladonna — AR and HI are wrong plants
    (8,  "paintingname_ar", "البلادونا"),
    (8,  "paintingname_hi", "बेलाडोना"),

    # ID 10 Bitter melon — AR is "sweet potato"
    (10, "paintingname_ar", "الكريلا"),

    # ID 11 Bitter leaf — AR is "lemon leaves"
    (11, "paintingname_ar", "ورق الفيرنونيا"),

    # ID 17 Cat's Claw — AR is "blackberry", HI is "black berry"
    (17, "paintingname_ar", "مخلب القط"),
    (17, "paintingname_hi", "बिल्ली का पंजा"),

    # ID 18 Cayenne pepper — AR is "lemon", HI is "lemon"
    (18, "paintingname_ar", "فلفل كايان"),
    (18, "paintingname_hi", "लाल मिर्च"),

    # ID 21 Clove — AR is "cinnamon"
    (21, "paintingname_ar", "القرنفل"),

    # ID 26 Woolly Foxglove — AR is "cannabis herbs", HI is Spanish transliteration
    (26, "paintingname_ar", "القفاز الرقمي"),
    (26, "paintingname_hi", "ऊनी फॉक्सग्लव"),

    # ID 27 Dong Quai — AR is "milk herbs", HI is Spanish transliteration
    (27, "paintingname_ar", "دونغ كواي"),
    (27, "paintingname_hi", "डोंग क्वाई"),

    # ID 28 Elderberry — AR is "cannabis herbs", HI is "caper" (wrong plant)
    (28, "paintingname_ar", "البزيلاء السوداء"),
    (28, "paintingname_hi", "एल्डरबेरी"),

    # ID 29 Chinese Ephedra — HI is English transliteration, AR minor fix
    (29, "paintingname_hi", "चीनी एफेड्रा"),
]

for row_id, col, val in fixes:
    conn.execute(f"UPDATE museum_item SET {col}=? WHERE id=?", (val, row_id))
    print(f"  {row_id:3d}  {col:<25}  = {val}")

conn.commit()
conn.close()
print(f"\nApplied {len(fixes)} fixes.")
