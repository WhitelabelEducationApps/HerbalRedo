# -*- coding: utf-8 -*-
"""
Fix all BAD_NAME paintingname rows:
- Strip Latin name from parentheses
- Merge duplicate rows (keep old row with better descriptions)
- Rename drawables for non-conflict cases
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import sqlite3, re, shutil
from pathlib import Path

DB = Path(r"C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db")
DRAWABLE = Path(r"C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\res\drawable-nodpi")

def sanitize(name):
    s = re.sub(r"[^a-z0-9]", "", name.lower())
    return ("a" + s) if s and s[0].isdigit() else s

def clean_name(name):
    """Extract primary common name, removing Latin in parens and aliases."""
    cleaned = re.sub(r'\s*\(.*?\)', '', name).strip()
    # Take first of comma-separated or "or"-separated names
    cleaned = re.split(r'\s*,\s*|\s+or\s+', cleaned)[0].strip()
    cleaned = cleaned.rstrip('.,;: ')
    # Apply manual overrides for specific cases
    overrides = {
        "Wooly Foxglove": "Woolly Foxglove",
        "Liquorice": "Liquorice",
        "Pot marigold": "Pot Marigold",
        "Milk thistle": "Milk Thistle",
        "Opium poppy": "Opium Poppy",
        "Horse-chestnut": "Horse Chestnut",
        "Florida fishpoison tree": "Jamaican Dogwood",
        "Cat's claw": "Cat's Claw",
        "Cayenne pepper": "Cayenne Pepper",
        "Dong quai": "Dong Quai",
        "Chinese Ephedra": "Chinese Ephedra",
    }
    return overrides.get(cleaned, cleaned)

conn = sqlite3.connect(DB)
conn.text_factory = lambda b: b.decode("utf-8", errors="replace")

rows = conn.execute("SELECT id, paintingname, full_image_uri FROM museum_item ORDER BY id").fetchall()
all_rows = {r[0]: {"name": r[1], "uri": r[2]} for r in rows}

# Build map: sanitize(clean_name) -> existing row id (for CONFLICT detection)
sanitized_to_id = {}
for rid, data in all_rows.items():
    sn = sanitize(data["name"])
    sanitized_to_id[sn] = rid

# Explicit merge pairs: (bad_id_to_keep, dup_id_to_delete)
# For each, we keep bad_id's descriptions but use better URI if available
MERGE_PAIRS = {
    17: 186,   # Cat's Claw
    18: 179,   # Cayenne Pepper
    19: 807,   # Celery
    30: 237,   # Eucalyptus
    33: 145,   # Fenugreek
    34: 354,   # Feverfew
    36: 188,   # Garlic
    37: 135,   # Ginger
    38: 152,   # Ginkgo
    40: 150,   # Goldenseal
    43: 178,   # Hawthorn
    45: 219,   # Horse Chestnut
    48: 249,   # Kava
    53: 154,   # Lemon
    57: 228,   # Marshmallow
    58: 134,   # Milk Thistle
    59: 977,   # Opium Poppy
}

stats = {"name_fixed": 0, "dup_deleted": 0, "drawable_renamed": 0, "uri_updated": 0}

# Process all BAD_NAME rows
bad_rows = [(rid, data["name"]) for rid, data in all_rows.items()
            if data["name"] and ('(' in data["name"] or len(data["name"]) > 50)]

for rid, old_name in bad_rows:
    new_name = clean_name(old_name)
    if new_name == old_name:
        continue  # clean_name didn't change it

    old_sani = sanitize(old_name)
    new_sani = sanitize(new_name)
    old_file = DRAWABLE / (old_sani + ".jpg")
    new_file = DRAWABLE / (new_sani + ".jpg")

    # Determine best URI
    best_uri = all_rows[rid]["uri"] or ""
    if rid in MERGE_PAIRS:
        dup_id = MERGE_PAIRS[rid]
        dup_uri = all_rows.get(dup_id, {}).get("uri") or ""
        # Prefer thumb/wikimedia URI over raw/blog URI
        def uri_score(u):
            if not u: return 0
            if "wikimedia" in u and "/thumb/" in u: return 3
            if "wikimedia" in u: return 2
            if u.startswith("https"): return 1
            return 0
        if uri_score(dup_uri) > uri_score(best_uri):
            best_uri = dup_uri
            stats["uri_updated"] += 1

    # Update paintingname (and URI if needed)
    conn.execute("UPDATE museum_item SET paintingname=?, full_image_uri=? WHERE id=?",
                 (new_name, best_uri, rid))
    stats["name_fixed"] += 1
    print(f"  {rid:4d}  NAME: '{old_name[:40]}' -> '{new_name}'")

    # Delete duplicate row
    if rid in MERGE_PAIRS:
        dup_id = MERGE_PAIRS[rid]
        conn.execute("DELETE FROM museum_item WHERE id=?", (dup_id,))
        stats["dup_deleted"] += 1
        print(f"         DEL dup id={dup_id}")

    # Handle drawable
    if old_file.exists() and not new_file.exists():
        shutil.move(str(old_file), str(new_file))
        stats["drawable_renamed"] += 1
        print(f"         RENAME {old_sani}.jpg -> {new_sani}.jpg")
    elif old_file.exists() and new_file.exists() and old_file != new_file:
        old_file.unlink()  # new file already exists (from dup row's download), remove old
        print(f"         DEL old drawable {old_sani}.jpg (new exists)")
    elif not old_file.exists() and not new_file.exists():
        print(f"         WARN: neither drawable exists!")

conn.commit()
conn.close()

print(f"\nSummary:")
print(f"  Names fixed:       {stats['name_fixed']}")
print(f"  Duplicates deleted:{stats['dup_deleted']}")
print(f"  Drawables renamed: {stats['drawable_renamed']}")
print(f"  URIs updated:      {stats['uri_updated']}")
