# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import sqlite3, shutil
from pathlib import Path

DB = Path(r"C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db")
DRAWABLE = Path(r"C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\res\drawable-nodpi")

conn = sqlite3.connect(DB)
conn.text_factory = lambda b: b.decode("utf-8", errors="replace")

# --- Delete confirmed duplicates ---
DUPS = {
    85:  "angelicasinensis",    # duplicate of ID 27 Dong Quai
    121: "silybummarianum",     # duplicate of ID 58 Milk Thistle
    124: "sage",                # duplicate of ID 65 Sage (drawable already shared)
}
for dup_id, drawable_stem in DUPS.items():
    conn.execute("DELETE FROM museum_item WHERE id=?", (dup_id,))
    f = DRAWABLE / (drawable_stem + ".jpg")
    if f.exists() and drawable_stem != "sage":  # sage.jpg is shared with ID 65
        f.unlink()
        print(f"  DEL dup id={dup_id}, removed {drawable_stem}.jpg")
    else:
        print(f"  DEL dup id={dup_id} (drawable not removed)")

# --- paintingname fixes: Latin → English (includes drawable rename) ---
RENAME_PLANTS = [
    (82,  "Vitex agnus-castus",       "Chaste Tree",       "vitexagnuscastus",      "chastetree"),
    (83,  "Capsicum frutescens",       "Bird's Eye Chili",  "capsicumfrutescens",    "birdseyechili"),
    (90,  "Azadirachta indica",        "Neem",              "azadirachtaindica",     "neem"),
    (91,  "Morinda citrifolia",        "Noni",              "morindacitrifolia",     "noni"),
    (93,  "Trifolium pratense",        "Red Clover",        "trifoliumpratense",     "redclover"),
    (97,  "Ocimum tenuiflorum",        "Holy Basil",        "ocimumtenuiflorum",     "holybasil"),
    (105, "Chelidonium",               "Greater Celandine", "chelidonium",           "greatercelandine"),
    (108, "Ricinus",                   "Castor Bean",       "ricinus",               "castorbean"),
    (109, "Mandragora officinarum",    "Mandrake",          "mandragoraofficinarum", "mandrake"),
    (112, "Hyssopus officinalis",      "Hyssop",            "hyssopusofficinalis",   "hyssop"),
    (125, "Achillea millefolium",      "Yarrow",            "achilleamillefolium",   "yarrow"),
]
for row_id, old_name, new_name, old_stem, new_stem in RENAME_PLANTS:
    conn.execute("UPDATE museum_item SET paintingname=? WHERE id=?", (new_name, row_id))
    old_f = DRAWABLE / (old_stem + ".jpg")
    new_f = DRAWABLE / (new_stem + ".jpg")
    if old_f.exists() and not new_f.exists():
        shutil.move(str(old_f), str(new_f))
        print(f"  {row_id:3d}  '{old_name}' -> '{new_name}' + renamed drawable")
    elif new_f.exists():
        if old_f.exists() and old_f != new_f:
            old_f.unlink()
        print(f"  {row_id:3d}  '{old_name}' -> '{new_name}' (drawable exists)")
    else:
        print(f"  {row_id:3d}  '{old_name}' -> '{new_name}' WARN: no drawable!")

# --- Field-level fixes (wrong plant names, corrupted data) ---
field_fixes = [
    # ID 83 Bird's Eye Chili — ZH is "People's Republic of China" (!), JA is "chili powder"
    (83,  "paintingname_zh", "朝天椒"),
    (83,  "paintingname_ja", "タバスコペッパー"),
    (83,  "paintingname_ar", "فلفل الطيور"),
    (83,  "paintingname_hi", "लाल मिर्च"),  # tabasco / bird's eye chili

    # ID 87 Gum Arabic — JA is English/Japanese mixed "ガム Arabic"
    (87,  "paintingname_ja", "アラビアゴム"),

    # ID 90 Neem — JA is "insecticide/pesticide" (駆虫薬), AR is transliteration
    (90,  "paintingname_ja", "ニーム"),
    (90,  "paintingname_ar", "النيم"),
    (90,  "paintingname_hi", "नीम"),

    # ID 91 Noni — JA is "damnacanthal" (a compound, not the plant), HI is transliteration
    (91,  "paintingname_ja", "ノニ"),
    (91,  "paintingname_hi", "नोनी"),

    # ID 92 Passiflora — AR is corrupted "باتشفلORA" with English
    (92,  "paintingname_ar", "زهرة الآلام"),

    # ID 93 Red Clover — AR is corrupted "tríفوليوم", HI is transliteration
    (93,  "paintingname_ar", "البرسيم الأحمر"),
    (93,  "paintingname_hi", "लाल तिपतिया घास"),

    # ID 95 Tea Tree Oil — HI "तीन ट्री ओइल" = "three tree oil" (तीन=three in Hindi!)
    (95,  "paintingname_hi", "टी ट्री ऑयल"),

    # ID 96 Tripterygium — AR is corrupted "tríبتيريجيوم"
    (96,  "paintingname_ar", "تريبتيريجيوم ويلفوردي"),

    # ID 99 Watercress — AR is "cabbage", JA is "lettuce"
    (99,  "paintingname_ar", "الكرس الطرة"),
    (99,  "paintingname_ja", "クレソン"),

    # ID 101 Piper auritum — JA is "chamomile pepper" (wrong plant)
    (101, "paintingname_ja", "メキシココショウ"),

    # ID 103 Fennel — AR is "mint" (النعناع), wrong plant
    (103, "paintingname_ar", "الشمر"),

    # ID 105 Greater Celandine — AR is "clove" (القرنفل), HI is "ring extension" (nonsense)
    (105, "paintingname_ar", "خشخاش أصفر"),
    (105, "paintingname_hi", "बड़ा कलैंडिन"),

    # ID 107 Juniper — AR is "yoke/burden" (النير), not juniper
    (107, "paintingname_ar", "العرعر"),

    # ID 108 Castor Bean — AR is "clove" (القرنفل), HI "राजनु" is incorrect
    (108, "paintingname_ar", "نبات الخروع"),
    (108, "paintingname_hi", "अरंडी"),

    # ID 111 Oak — AR is "straw" (القش), HI is "walnut" (अखरोट)
    (111, "paintingname_ar", "البلوط"),
    (111, "paintingname_hi", "बांज"),

    # ID 118 Cabbage — HI is "onion" (प्याज), JA is "kale" (ケール)
    (118, "paintingname_hi", "पत्ता गोभी"),
    (118, "paintingname_ja", "キャベツ"),

    # ID 119 Pomegranate — AR is "orange" (البرتقال), HI is "ring" (अंगूठी)
    (119, "paintingname_ar", "الرمان"),
    (119, "paintingname_hi", "अनार"),

    # ID 120 Chicory — AR is "clove" (القرنفل)
    (120, "paintingname_ar", "الهندباء"),

    # ID 123 Saffron — AR is "turmeric" (الكركم), completely different plant
    (123, "paintingname_ar", "الزعفران"),

    # ID 127 White Horehound — JA is "list of herbs" (ハーブの一覧), not a plant name
    (127, "paintingname_ja", "マルビウム"),

    # ID 128 Mugwort — AR is "black mint", HI is "yarrow" (different plant!), JA is "Chernobyl" (!!)
    (128, "paintingname_ar", "الشيح البري"),
    (128, "paintingname_hi", "माजरो"),
    (128, "paintingname_ja", "ヨモギ"),

    # ID 130 Anise — AR is "mint" (النعناع), wrong plant
    (130, "paintingname_ar", "اليانسون"),

    # ID 131 Marigold — AR is "the star" (النجمة), HI is English transliteration
    (131, "paintingname_ar", "القطيفة"),
    (131, "paintingname_hi", "गेंदा"),
]

for row_id, col, val in field_fixes:
    conn.execute(f"UPDATE museum_item SET {col}=? WHERE id=?", (val, row_id))
    print(f"  {row_id:3d}  {col:<25}  = {val}")

# --- URI fix for ID 85 — image was foxglove (Digitalis), not Angelica sinensis
# ID 85 has been deleted (duplicate), no action needed for URI

conn.commit()
conn.close()
print(f"\nApplied all fixes for IDs 81-132.")
