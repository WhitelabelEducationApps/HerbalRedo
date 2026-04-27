# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import sqlite3, shutil
from pathlib import Path

DB = Path(r"C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db")
DRAWABLE = Path(r"C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\res\drawable-nodpi")

conn = sqlite3.connect(DB)
conn.text_factory = lambda b: b.decode("utf-8", errors="replace")

# --- Rename ID 104: Centaurea cyanus → Cornflower (better common name) ---
old_f = DRAWABLE / "centaureacyanus.jpg"
new_f = DRAWABLE / "cornflower.jpg"
conn.execute("UPDATE museum_item SET paintingname='Cornflower' WHERE id=104")
if old_f.exists() and not new_f.exists():
    shutil.move(str(old_f), str(new_f))
    print("  104  Centaurea cyanus -> Cornflower + renamed drawable")
elif old_f.exists() and new_f.exists():
    old_f.unlink()
    print("  104  Centaurea cyanus -> Cornflower (cornflower.jpg already existed, deleted old)")
else:
    print("  104  Centaurea cyanus -> Cornflower (drawable check: old missing)")

# --- Delete duplicates ---
DUPS = [
    (326, "yarrow",     False),  # dup of 125 Yarrow; shared drawable
    (338, "cornflower", False),  # dup of 104; file now shared
]
for dup_id, stem, remove_file in DUPS:
    conn.execute("DELETE FROM museum_item WHERE id=?", (dup_id,))
    print(f"  DEL dup id={dup_id} ({stem})")

# --- Field-level fixes ---
fixes = [
    # ID 327 Wormwood — AR "الأسبرين" = ASPIRIN(!), HI "काली मेथी" = black fenugreek(!), JA garbled
    (327, "paintingname_ar", "الشيح"),
    (327, "paintingname_hi", "वर्मवुड"),
    (327, "paintingname_ja", "ニガヨモギ"),

    # ID 349 Immortelle — HI "अमरत्व" = "immortality" (the abstract concept, not the plant)
    (349, "paintingname_hi", "इम्मोर्टेल"),

    # ID 387 Annatto — HI "अंजीर" = FIG (wrong plant!)
    (387, "paintingname_hi", "अनातो"),
]

for row_id, col, val in fixes:
    conn.execute(f"UPDATE museum_item SET {col}=? WHERE id=?", (val, row_id))
    print(f"  {row_id:3d}  {col:<25}  = {val}")

conn.commit()
conn.close()
print(f"\nApplied fixes for IDs 296-390.")
