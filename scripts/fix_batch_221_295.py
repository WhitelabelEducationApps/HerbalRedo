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
DUPS = [
    (231, "neem",      False),  # dup of 90; shared drawable
    (294, "grapevine", True),   # dup of 41 Grape; different drawable name
]
for dup_id, stem, remove_file in DUPS:
    conn.execute("DELETE FROM museum_item WHERE id=?", (dup_id,))
    if remove_file:
        f = DRAWABLE / (stem + ".jpg")
        if f.exists():
            f.unlink()
            print(f"  DEL dup id={dup_id}, removed {stem}.jpg")
        else:
            print(f"  DEL dup id={dup_id} ({stem}.jpg not found)")
    else:
        print(f"  DEL dup id={dup_id} (shared drawable, not removed)")

# --- Field-level fixes ---
fixes = [
    # ID 221 Blue Flag — AR "اللون الأزرق" is "the blue color" (too generic)
    (221, "paintingname_ar", "الإيريس الأزرق"),

    # ID 224 Avocado — AR "الخوخ" = PEACH (completely wrong plant!)
    (224, "paintingname_ar", "الأفوكادو"),

    # ID 232 Guduchi — ZH "千层塔" = Huperzia serrata (wrong plant!), RO "Centella asiatica" (wrong!)
    (232, "paintingname_zh", "宽筋藤"),
    (232, "paintingname_ro", "Guduchi (Tinospora cordifolia)"),

    # ID 234 Common Fig — AR "التفاح العادي" = "common apple" (wrong!), HI is transliteration
    (234, "paintingname_ar", "التين"),
    (234, "paintingname_hi", "अंजीर"),

    # ID 236 Nutmeg — AR "النوت ميج" is garbled, HI is transliteration
    (236, "paintingname_ar", "جوزة الطيب"),
    (236, "paintingname_hi", "जायफल"),

    # ID 241 Vanilla — AR "الفيانيل" is garbled
    (241, "paintingname_ar", "الفانيليا"),

    # ID 242 Wood Sorrel — AR "النعناع الأخضر" = "green mint", HI "कागज के बीज" = "paper seeds"
    (242, "paintingname_ar", "الحميض"),
    (242, "paintingname_hi", "खट्टी बूटी"),

    # ID 243 Saw Palmetto — AR "القرنفل" = CLOVE (wrong!)
    (243, "paintingname_ar", "نخيل المنشار"),

    # ID 251 Psyllium — JA "ペシウム" is garbled
    (251, "paintingname_ja", "サイリウム"),

    # ID 253 Leadwort — ZH has FULL ARTICLE TEXT (entire Wikipedia paragraph)
    (253, "paintingname_zh", "白花丹"),

    # ID 256 Bistort — ZH has FULL ARTICLE TEXT
    (256, "paintingname_zh", "拳参"),

    # ID 258 Cowslip — AR "النجمة الحمراء" = "red star", ZH "牛舌草" = Anchusa (wrong plant!)
    (258, "paintingname_ar", "الربيعية"),
    (258, "paintingname_zh", "黄花九轮草"),

    # ID 260 Pulsatilla — PT and RO have FULL DESCRIPTION TEXT in name fields
    (260, "paintingname_pt", "Pulsatilla"),
    (260, "paintingname_ro", "Pulsatilă"),

    # ID 261 Buckthorn — ZH has FULL ARTICLE TEXT
    (261, "paintingname_zh", "鼠李"),

    # ID 266 Rue — HI "सड़क" = "road" (wrong!)
    (266, "paintingname_hi", "सदाब"),

    # ID 269 Soapnuts — AR "البندورة الصابونية" = "soap tomato" (البندورة = tomato!)
    (269, "paintingname_ar", "الريثا"),

    # ID 270 Houttuynia — ZH "胡秃草" is wrong; correct ZH is 蕺菜; RO "spider plant" is wrong
    (270, "paintingname_zh", "蕺菜"),
    (270, "paintingname_ro", "Houttuynia cordata"),

    # ID 275 Quassia — AR "كواسي아" has Korean char (corruption!); ZH has FULL ARTICLE TEXT
    (275, "paintingname_ar", "كواسيا"),
    (275, "paintingname_zh", "苦木"),

    # ID 278 Cacao — AR has Wikipedia redirect notice text(!); ZH has full description text
    (278, "paintingname_ar", "الكاكاو"),
    (278, "paintingname_zh", "可可"),

    # ID 279 Benzoin — ZH "安息香可以指：" = disambiguation page text!
    (279, "paintingname_zh", "安息香"),

    # ID 280 Symplocos — ZH "柿树" = persimmon tree (wrong plant!)
    (280, "paintingname_zh", "山矾"),

    # ID 282 English Yew — AR "التوت الإنجليزي" = "English mulberry" (wrong!)
    (282, "paintingname_ar", "الطقسوس"),

    # ID 283 Tea Plant — JA "ティーパート" is garbled
    (283, "paintingname_ja", "チャノキ"),

    # ID 284 Linden — AR "ليمن" = LEMON (wrong!), ZH/JA are transliterations
    (284, "paintingname_ar", "زيزفون"),
    (284, "paintingname_zh", "椴树"),
    (284, "paintingname_ja", "セイヨウシナノキ"),

    # ID 285 Nasturtium — ZH "凤仙花" = impatiens/balsam (wrong plant!)
    (285, "paintingname_zh", "金莲花"),

    # ID 291 Spikenard — ZH "红花" = safflower (completely different plant!), JA garbled
    (291, "paintingname_zh", "甘松"),
    (291, "paintingname_ja", "ナルドスタキス"),
]

for row_id, col, val in fixes:
    conn.execute(f"UPDATE museum_item SET {col}=? WHERE id=?", (val, row_id))
    print(f"  {row_id:3d}  {col:<25}  = {val}")

conn.commit()
conn.close()
print(f"\nApplied fixes for IDs 221-295.")
