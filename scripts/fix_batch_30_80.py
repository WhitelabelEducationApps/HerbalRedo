# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import sqlite3
from pathlib import Path

DB = Path(r"C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db")
conn = sqlite3.connect(DB)
conn.text_factory = lambda b: b.decode("utf-8", errors="replace")

fixes = [
    # ID 30 Eucalyptus — AR is "camphor" (completely different plant)
    (30, "paintingname_ar", "الكينا"),

    # ID 32 Evening Primrose — paintingname is Latin genus, HI is transliteration
    (32, "paintingname",    "Evening Primrose"),
    (32, "paintingname_hi", "संध्या प्रिमरोज़"),

    # ID 39 Ginseng — PT is "Ginkgo biloba" (completely wrong plant!)
    (39, "paintingname_pt", "Ginseng"),

    # ID 40 Goldenseal — ZH is "buttercup" (毛茛), JA is garbled
    (40, "paintingname_zh", "北美黄连"),
    (40, "paintingname_ja", "ゴールデンシール"),

    # ID 43 Hawthorn — ZH is garbage English/Chinese mix, HI is "prickly pear cactus" (wrong!)
    (43, "paintingname_zh", "山楂"),
    (43, "paintingname_hi", "हॉथॉर्न"),

    # ID 47 Jamaican Dogwood — ZH is garbage English/Chinese mix
    (47, "paintingname_zh", "毒鱼豆"),

    # ID 49 Khat — ZH has "贻贝" (mussels?!) mixed in, JA is garbled
    (49, "paintingname_zh", "恰特草"),
    (49, "paintingname_ja", "カート"),

    # ID 51 Kratom — ZH and JA start with English "Kratom"
    (51, "paintingname_zh", "卡痛"),
    (51, "paintingname_ja", "クラトム"),

    # ID 68 Thyme — paintingname is Latin, HI is transliteration of Latin
    (68, "paintingname",    "Thyme"),
    (68, "paintingname_hi", "थाइम"),

    # ID 70 White Willow — RO is Spanish text ("Salguero o sauce blanco")!
    (70, "paintingname_ro", "Salcie albă"),

    # ID 80 Creosote Bush — paintingname is Latin, HI is transliteration of Latin
    (80, "paintingname",    "Creosote Bush"),
    (80, "paintingname_hi", "क्रियोसोट झाड़ी"),
]

# Image URI fixes (replacing unstable blog/photoshelter URLs)
uri_fixes = [
    # ID 46 Horsetail — photoshelter.com URL
    (46, "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Equisetum_arvense_foliage.jpg/500px-Equisetum_arvense_foliage.jpg"),
    # ID 47 Jamaican Dogwood — levypreserve.org URL
    (47, "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Piscidia_piscipula_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-109.jpg/500px-Piscidia_piscipula_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-109.jpg"),
    # ID 60 Oregano — whatsinbloom.wordpress.com URL
    (60, "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Origanum_vulgare_-_harilik_pune.jpg/500px-Origanum_vulgare_-_harilik_pune.jpg"),
]

for row_id, col, val in fixes:
    conn.execute(f"UPDATE museum_item SET {col}=? WHERE id=?", (val, row_id))
    print(f"  {row_id:3d}  {col:<25}  = {val}")

for row_id, url in uri_fixes:
    conn.execute("UPDATE museum_item SET full_image_uri=? WHERE id=?", (url, row_id))
    print(f"  {row_id:3d}  full_image_uri  = {url[:70]}")

conn.commit()
conn.close()
print(f"\nApplied {len(fixes)} name fixes + {len(uri_fixes)} URI fixes.")
