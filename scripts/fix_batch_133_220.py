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
# (drawable: "licorice" and "stjohnswort" are unique so remove them;
#  "valerian", "whitewillow", "noni", "castorbean" are shared — keep the file)
DUPS = [
    (144, "licorice",       True),   # dup of 54 Liquorice; different drawable
    (148, "stjohnswort",    True),   # dup of 66 Common Saint John's wort; different drawable
    (149, "valerian",       False),  # dup of 69 Valerian; shared drawable
    (153, "whitewillow",    False),  # dup of 70 White willow; shared drawable
    (185, "noni",           False),  # dup of 91 Noni; shared drawable
    (203, "thundergodvine", False),  # dup of 96 Thunder God Vine; will be created by rename below
    (211, "castorbean",     False),  # dup of 108 Castor Bean; shared drawable
]
for dup_id, stem, remove_file in DUPS:
    conn.execute("DELETE FROM museum_item WHERE id=?", (dup_id,))
    if remove_file:
        f = DRAWABLE / (stem + ".jpg")
        if f.exists():
            f.unlink()
            print(f"  DEL dup id={dup_id}, removed {stem}.jpg")
        else:
            print(f"  DEL dup id={dup_id} (file not found)")
    else:
        print(f"  DEL dup id={dup_id} (drawable shared, not removed)")

# --- Rename ID 96: Tripterygium wilfordii → Thunder God Vine ---
old_f = DRAWABLE / "tripterygiumwilfordii.jpg"
new_f = DRAWABLE / "thundergodvine.jpg"
conn.execute("UPDATE museum_item SET paintingname='Thunder God Vine' WHERE id=96")
if old_f.exists() and not new_f.exists():
    shutil.move(str(old_f), str(new_f))
    print("   96  renamed: tripterygiumwilfordii.jpg -> thundergodvine.jpg")
elif old_f.exists() and new_f.exists():
    old_f.unlink()
    print("   96  renamed: deleted tripterygiumwilfordii.jpg (thundergodvine.jpg exists)")

# --- Field-level fixes ---
fixes = [
    # ID 156 Rosehip — HI "बालू के बीज" = "sand seeds" (nonsense)
    (156, "paintingname_hi", "गुलाब का फल"),

    # ID 180 Corn Poppy — AR is vague transliteration
    (180, "paintingname_ar", "خشخاش الحقل"),

    # ID 181 Common Plantain — AR "النبات العشبي" = generic "herbaceous plant", HI/JA garbled
    (181, "paintingname_ar", "لسان الحمل"),
    (181, "paintingname_hi", "चौड़ी पत्ती का केला"),
    (181, "paintingname_ja", "オオバコ"),

    # ID 182 Vervain — ZH "鼠尾草" = SAGE (wrong plant!)
    (182, "paintingname_zh", "马鞭草"),
    (182, "paintingname_ar", "الأفربقاء"),
    (182, "paintingname_ja", "バーベイン"),

    # ID 183 Mezereum — ZH "毛茛" = buttercup (wrong!)
    (183, "paintingname_zh", "欧瑞香"),

    # ID 184 Bitter Melon — AR "البطاطا الحلوة" = sweet potato(!), HI/JA are kukui/candlenut
    (184, "paintingname_ar", "الكريلا"),
    (184, "paintingname_hi", "करेला"),
    (184, "paintingname_ja", "ゴーヤ"),

    # ID 189 Onion — HI "बैंगन" = EGGPLANT(!), JA "ニンジン" = CARROT(!)
    (189, "paintingname_hi", "प्याज"),
    (189, "paintingname_ja", "タマネギ"),

    # ID 191 Soursop — ZH "酸角" = tamarind (wrong plant!)
    (191, "paintingname_zh", "刺果番荔枝"),

    # ID 192 Periwinkle — AR corrupted ("البيري وينكيل"), JA has stray English char
    (192, "paintingname_ar", "نبتة القرن الصغير"),
    (192, "paintingname_ja", "ペリウィンクル"),

    # ID 200 Frankincense — AR "العنبر" = ambergris/amber, different substance entirely
    (200, "paintingname_ar", "اللبان"),

    # ID 202 Moringa — ZH "莫琳加" is a transliteration, should be 辣木
    (202, "paintingname_zh", "辣木"),

    # ID 204 Cinnamon — AR "القرنفل" = CLOVE (completely different plant!)
    (204, "paintingname_ar", "القرفة"),

    # ID 208 Wild Yam — AR "اليا مILD" = corrupted data with English
    (208, "paintingname_ar", "اليام البري"),

    # ID 209 Persimmon — ZH "番石榴" = GUAVA(!), JA "パッションフルーツ" = passion fruit(!)
    #   AR "التفاح الحار" = "hot apple", HI "पास्टेन फल" = garbled
    (209, "paintingname_zh", "柿子"),
    (209, "paintingname_ja", "カキ"),
    (209, "paintingname_ar", "الكاكي"),
    (209, "paintingname_hi", "तेंदू"),

    # ID 213 Yellow Gentian — JA "黄ジンチョウ" = "yellow daphne" (wrong plant)
    (213, "paintingname_ja", "キバナリンドウ"),

    # ID 214 Umckaloabo — PT "dextrometorfano" = dextromethorphan (a cough drug, not the plant!)
    (214, "paintingname_pt", "Umckaloabo"),

    # ID 215 Chinese Foxglove — AR "الفلوكس الصيني" = "Chinese phlox" (wrong!),
    #   ZH "中国毛茛" = "Chinese buttercup" (wrong!), JA "中国フロックス" = "Chinese phlox"
    (215, "paintingname_ar", "ريهمانيا صينية"),
    (215, "paintingname_zh", "地黄"),
    (215, "paintingname_ja", "ジオウ"),

    # ID 218 Witch Hazel — ZH "接骨木" = ELDERBERRY (completely different plant!)
    (218, "paintingname_zh", "金缕梅"),

    # ID 96 Thunder God Vine — fix ZH (was "雷神之花", correct is 雷公藤), AR (was generic)
    (96,  "paintingname_zh", "雷公藤"),
    (96,  "paintingname_ar", "كرمة إله الرعد"),
]

for row_id, col, val in fixes:
    conn.execute(f"UPDATE museum_item SET {col}=? WHERE id=?", (val, row_id))
    print(f"  {row_id:3d}  {col:<25}  = {val}")

conn.commit()
conn.close()
print(f"\nApplied fixes for IDs 133-220.")
