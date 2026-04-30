"""
match_plants.py — Fuzzy-match extracted book plants to plants.db entries.

Reads:  extracted_book1.jsonl (or any extracted_bookN.jsonl)
Output: matched_book1.jsonl — each record adds db_id, db_name, match_score, match_status

match_status:
  AUTO    — score >= 90, safe to use automatically
  REVIEW  — score 70-89, needs human check
  SKIP    — score < 70, no reliable match found

Usage:
  python match_plants.py
  python match_plants.py --extracted extracted_book1.jsonl --out matched_book1.jsonl
"""

import json
import sqlite3
import argparse
import sys
import os

# Force UTF-8 output on Windows terminals
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from rapidfuzz import fuzz, process

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import DB_PATH

AUTO_THRESHOLD = 90
REVIEW_THRESHOLD = 70


def load_db_plants(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, paintingname FROM museum_item")
    rows = cur.fetchall()
    conn.close()
    return rows  # list of (id, paintingname)


def best_match(book_scientific, book_common, db_plants):
    """
    Match book plant to DB entry by common name (paintingname).
    Tries token_set_ratio (handles subset names like "Aloe" -> "Aloe Vera")
    and falls back to genus matching.
    Returns (db_id, db_name, score, matched_on)
    """
    candidates = {str(row[0]): row[1] or "" for row in db_plants}

    best_result = None
    best_on = "none"

    # Collect candidate common name strings (handles both "common_name" and "common_names" formats)
    common_parts = []
    for part in book_common.split(","):
        p = part.strip()
        if p and not p.startswith(book_scientific.split()[0]):
            common_parts.append(p)

    # Try each common name with token_set_ratio (best for partial-word matches)
    for name in common_parts[:5]:
        for scorer in (fuzz.token_set_ratio, fuzz.token_sort_ratio):
            r = process.extractOne(name, candidates, scorer=scorer)
            if r and (best_result is None or r[1] > best_result[1]):
                best_result = r
                best_on = "common"

    # Fallback: genus + first species word
    genus_species = " ".join(book_scientific.split()[:2])
    r_sci = process.extractOne(genus_species, candidates, scorer=fuzz.token_set_ratio)
    if r_sci and (best_result is None or r_sci[1] > best_result[1]):
        best_result = r_sci
        best_on = "scientific"

    if not best_result:
        return None, None, 0, "none"

    # rapidfuzz returns (matched_value, score, key) for dict inputs
    _, score, db_id_str = best_result
    db_id = int(db_id_str)
    db_row = next(r for r in db_plants if r[0] == db_id)
    return db_id, db_row[1], score, best_on


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--extracted", default="extracted_book1.jsonl")
    parser.add_argument("--out", default="matched_book1.jsonl")
    args = parser.parse_args()

    print(f"Loading DB from: {DB_PATH}")
    db_plants = load_db_plants(DB_PATH)
    print(f"  {len(db_plants)} entries in DB")

    print(f"Loading extracted: {args.extracted}")
    with open(args.extracted, encoding="utf-8") as f:
        book_plants = [json.loads(l) for l in f if l.strip()]
    print(f"  {len(book_plants)} extracted plants")

    stats = {"AUTO": 0, "REVIEW": 0, "SKIP": 0}
    results = []

    for plant in book_plants:
        # Support both Book1 ("common_names") and Book2 ("common_name") field names
        common = plant.get("common_names") or plant.get("common_name") or ""
        db_id, db_name, score, matched_on = best_match(
            plant["scientific_name"],
            common,
            db_plants,
        )

        if score >= AUTO_THRESHOLD:
            status = "AUTO"
        elif score >= REVIEW_THRESHOLD:
            status = "REVIEW"
        else:
            status = "SKIP"

        stats[status] += 1
        plant["db_id"] = db_id
        plant["db_name"] = db_name
        plant["match_score"] = score
        plant["matched_on"] = matched_on
        plant["match_status"] = status
        results.append(plant)

    with open(args.out, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\nResults -> {args.out}")
    print(f"  AUTO   (>={AUTO_THRESHOLD}): {stats['AUTO']}")
    print(f"  REVIEW (>={REVIEW_THRESHOLD}): {stats['REVIEW']}")
    print(f"  SKIP   (<{REVIEW_THRESHOLD}):  {stats['SKIP']}")

    # Print REVIEW cases for manual inspection
    reviews = [r for r in results if r["match_status"] == "REVIEW"]
    if reviews:
        print("\n--- REVIEW cases (check manually) ---")
        for r in reviews:
            print(f"  Book: '{r['scientific_name']}' ({r['common_names'][:40]})")
            print(f"    DB: id={r['db_id']} '{r['db_name']}' [score={r['match_score']}, on={r['matched_on']}]")

    skips = [r for r in results if r["match_status"] == "SKIP"]
    if skips:
        print("\n--- SKIP cases (no match) ---")
        for r in skips:
            print(f"  Book: '{r['scientific_name']}' [score={r['match_score']}]")


if __name__ == "__main__":
    main()
