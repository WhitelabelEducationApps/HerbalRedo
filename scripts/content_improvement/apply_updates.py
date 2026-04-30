"""
apply_updates.py — Apply generated/translated descriptions to plants.db.

Reads:  descriptions_to_apply.jsonl
Writes: plants.db (museum_item table)

Usage:
  python apply_updates.py --dry-run    # show SQL without committing
  python apply_updates.py              # commit to DB
"""

import json
import sqlite3
import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import DB_PATH

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LANG_COLUMN = {
    "en": "description",
    "ro": "description_ro", "es": "description_es", "de": "description_de",
    "fr": "description_fr", "it": "description_it", "ru": "description_ru",
    "pt": "description_pt", "zh": "description_zh", "ja": "description_ja",
    "ar": "description_ar", "hi": "description_hi",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="descriptions_to_apply.jsonl")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        records = [json.loads(l) for l in f if l.strip()]

    print(f"Loaded {len(records)} updates from {args.input}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    applied = 0
    skipped = 0
    for rec in records:
        db_id = rec["db_id"]
        lang = rec["lang"]
        text = rec["text"]
        col = LANG_COLUMN.get(lang)

        if not col:
            print(f"  SKIP unknown lang: {lang}")
            skipped += 1
            continue
        if not text or len(text.strip()) < 30:
            print(f"  SKIP too short (id={db_id}, lang={lang})")
            skipped += 1
            continue

        sql = f"UPDATE museum_item SET {col} = ? WHERE id = ?"
        if args.dry_run:
            print(f"  [DRY] id={db_id} lang={lang}: {text[:80]}...")
        else:
            cur.execute(sql, (text.strip(), db_id))
            applied += 1
            print(f"  UPDATED id={db_id} lang={lang} ({len(text)} chars)")

    if not args.dry_run:
        conn.commit()
        print(f"\nCommitted {applied} updates, skipped {skipped}.")
    else:
        print(f"\n[DRY RUN] Would apply {len(records) - skipped} updates.")

    conn.close()


if __name__ == "__main__":
    main()
