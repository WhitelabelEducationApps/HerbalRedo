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
# (drawable stems listed; False = shared file, True = unique file to remove)
DUPS = [
    (960, "mandrake",        False),  # dup of 109; shared drawable
    (976, "greatercelandine",False),  # dup of 105; shared drawable
    (785, "whitehorehound",  False),  # dup of 127; shared drawable
]
for dup_id, stem, remove_file in DUPS:
    conn.execute("DELETE FROM museum_item WHERE id=?", (dup_id,))
    if remove_file:
        f = DRAWABLE / (stem + ".jpg")
        if f.exists(): f.unlink()
    print(f"  DEL dup id={dup_id} ({stem})")

# --- All field-level fixes ---
fixes = [
    # IDs 391-500
    # ID 400 Hound's Tongue — ZH "毒芹" = poison hemlock (Conium maculatum), different plant!
    (400, "paintingname_zh", "犬舌草"),

    # ID 421 Lungwort — AR "النعناع الوردي" = "pink mint" (wrong)
    (421, "paintingname_ar", "نبات الرئة"),

    # ID 438 Horseradish — AR=clove, ZH=wasabi, JA=mustard, RO=sapodilla (all wrong plants!)
    (438, "paintingname_ar", "الفجل الحار"),
    (438, "paintingname_hi", "हॉर्सरेडिश"),
    (438, "paintingname_zh", "辣根"),
    (438, "paintingname_ja", "ホースラディッシュ"),
    (438, "paintingname_ro", "hrean"),

    # ID 451 Woad — AR "النعناع الأزرق" = "blue mint"
    (451, "paintingname_ar", "النيل البري"),

    # ID 461 Radish — AR "البصل" = ONION, HI "अदभुत" = "wonderful" (not a plant!)
    (461, "paintingname_ar", "الفجل"),
    (461, "paintingname_hi", "मूली"),

    # ID 470 Pinguin (Bromelia) — ZH/JA both "penguin" (the bird)!
    (470, "paintingname_zh", "凤梨科品葛"),
    (470, "paintingname_ja", "ブロメリア"),

    # IDs 501-620
    # ID 502 Prickly Pear — AR "التفاح المُخَرَّب" = "vandalized apple", HI "पेप्पर"=pepper, RO=dandelion
    (502, "paintingname_ar", "التين الشوكي"),
    (502, "paintingname_hi", "नागफनी"),
    (502, "paintingname_ro", "Smochin spinuros (Opuntia)"),

    # ID 512 Sweetshrub — AR "الزاجل" = homing pigeon(!), ZH "紫珠" = Callicarpa (wrong plant!)
    (512, "paintingname_ar", "الكالي كانثوس"),
    (512, "paintingname_zh", "美国蜡梅"),

    # ID 530 Balloon Flower — HI garbled, JA "ふぶきばら" = "snowstorm rose"
    (530, "paintingname_hi", "गुब्बारा फूल"),
    (530, "paintingname_ja", "キキョウ"),

    # ID 551 Japanese Honeysuckle — AR "Japanese honey mint", HI = "Japanese saffron"!, JA = "Japanese headband"!
    (551, "paintingname_ar", "زهرة العسل اليابانية"),
    (551, "paintingname_hi", "जापानी हनीसकल"),
    (551, "paintingname_ja", "スイカズラ"),

    # ID 574 Guelder Rose — ZH "金蔷薇" = "golden rose" (not guelder rose)
    (574, "paintingname_zh", "欧洲荚蒾"),

    # ID 577 Blackhaw — AR "Cornus sericea" = dogwood (Latin name wrong plant), JA = "white birch"!
    (577, "paintingname_ar", "قضبان السياج الأسود"),
    (577, "paintingname_ja", "クロナナカマド"),

    # ID 595 American Holly — JA "アメリカン・ホolly" has stray English lowercase chars
    (595, "paintingname_ja", "アメリカヒイラギ"),

    # ID 609 Pepperbush — ZH has full article text
    (609, "paintingname_zh", "桤叶树"),

    # IDs 621-760
    # ID 639 Orpine — JA "オロバンチ" = Orobanche/broomrape (wrong plant!)
    (639, "paintingname_ja", "ベンケイソウ"),

    # ID 641 Cobweb Houseleek — AR and HI are garbled/wrong
    (641, "paintingname_ar", "ورد العنكبوت"),
    (641, "paintingname_hi", "मकड़ी के जाले वाला हाउसलीक"),

    # ID 653 Luffa — ZH has full article text
    (653, "paintingname_zh", "丝瓜"),

    # ID 693 Mexican Yam — JA "サツマイモ" = sweet potato (different plant!)
    (693, "paintingname_ja", "メキシコヤム"),

    # ID 721 Lesser Burdock — AR "الكركديه الصغيرة" = "small hibiscus" (wrong plant!)
    (721, "paintingname_ar", "أرقطيون صغير"),

    # ID 729 Aster — ZH "波斯菊" = Cosmos (different plant!)
    (729, "paintingname_zh", "紫菀"),

    # ID 737 Chinese Thorowax — all translations are garbled; correct names are 柴胡/ミシマサイコ
    (737, "paintingname_zh", "柴胡"),
    (737, "paintingname_ja", "ミシマサイコ"),
    (737, "paintingname_ar", "بوبليوروم صيني"),

    # ID 743 Bristly Thistle — ZH has full article text
    (743, "paintingname_zh", "丝毛飞廉"),

    # ID 745 Carline Thistle — ZH has full article text
    (745, "paintingname_zh", "刺苞菊"),

    # IDs 761-985
    # ID 763 Bugle (Ajuga reptans) — ZH "鼠尾草" = sage, JA "カモミール" = chamomile, HI "chamomile"!
    (763, "paintingname_zh", "筋骨草"),
    (763, "paintingname_ja", "アジュガ"),
    (763, "paintingname_hi", "अजुगा"),

    # ID 767 Betony — ZH has full article text
    (767, "paintingname_zh", "药水苏"),

    # ID 785 White Horehound — deleted as duplicate; remaining fix: HI was Wikipedia list header
    # (already deleted)

    # ID 793 Pennyroyal — ZH "薄荷脑" = "menthol" (chemical compound, not plant name!)
    (793, "paintingname_zh", "留兰香薄荷"),

    # ID 821 Cowbane — ZH has full article text
    (821, "paintingname_zh", "毒芹"),

    # ID 841 Red Ginger — ZH has full article text
    (841, "paintingname_zh", "红花月桃"),

    # ID 857 Agrimony — ZH has full article text
    (857, "paintingname_zh", "龙芽草"),

    # ID 875 Indian Physic — ZH has full article text
    (875, "paintingname_zh", "美国吐根"),

    # ID 897 Wild Indigo — RO has full description text
    (897, "paintingname_ro", "Baptisia"),

    # ID 903 Bladder Senna — ZH has full article text
    (903, "paintingname_zh", "鱼鳔槐"),

    # ID 906 Sissoo — ZH has full article text
    (906, "paintingname_zh", "印度黄檀"),

    # ID 914 Monkshood — PT has full description text
    (914, "paintingname_pt", "Acónito"),

    # ID 926 Black Cohosh — ZH has full article text
    (926, "paintingname_zh", "升麻"),

    # ID 927 Upright Clematis — RO has full description text
    (927, "paintingname_ro", "Clematis erecta"),

    # ID 931 Winter Aconite — PT has full description text
    (931, "paintingname_pt", "Erântis"),

    # ID 938 Evodia — PT has full description text
    (938, "paintingname_pt", "Evodia"),

    # ID 961 Apple of Peru — RO has full description text
    (961, "paintingname_ro", "Nicandra"),

    # ID 967 Scopolia — ZH has full article text
    (967, "paintingname_zh", "赛茛菪"),

    # ID 985 Common Fumitory — ZH has full article text
    (985, "paintingname_zh", "球果紫菫"),
]

for row_id, col, val in fixes:
    conn.execute(f"UPDATE museum_item SET {col}=? WHERE id=?", (val, row_id))
    print(f"  {row_id:3d}  {col:<25}  = {val}")

conn.commit()
conn.close()
print(f"\nApplied all fixes for IDs 391-985.")
