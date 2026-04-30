"""
generate_descriptions.py — Use local Ollama LLM to:
  1. Generate a clean English description for a matched plant from book source text
  2. Translate that description into target languages where the DB description is "crap"

What counts as "crap" (poor quality) for a language slot:
  - Empty or None
  - Length < 80 chars
  - Same text as English (untranslated)
  - Starts with common garbage prefixes

Input:  matched_book1.jsonl (or any matchedN.jsonl)
Output: descriptions_to_apply.jsonl — one record per (db_id, lang) pair to update

Usage:
  python generate_descriptions.py --dry-run       # show what would be updated, no LLM calls
  python generate_descriptions.py                  # run full pipeline
  python generate_descriptions.py --status AUTO   # only process AUTO-matched plants
  python generate_descriptions.py --langs en ro hi ar  # only these languages

The script checkpoints after each plant. Re-running skips already-done db_id entries.
"""

import json
import sqlite3
import argparse
import sys
import os
import time
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import DB_PATH, LANGUAGES

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OLLAMA_MODEL = "qwen3:8b-ctx16k"
CHECKPOINT_FILE = "descriptions_to_apply.jsonl"
MIN_GOOD_DESC_LEN = 80  # chars — below this is considered crap

GARBAGE_PREFIXES = [
    "<think>", "think>", "I cannot", "I don't know",
    "No information", "Not available",
]

LANG_NAMES = {
    "en": "English", "ro": "Romanian", "es": "Spanish", "de": "German",
    "fr": "French", "it": "Italian", "ru": "Russian", "pt": "Portuguese",
    "zh": "Chinese (Simplified)", "ja": "Japanese", "ar": "Arabic", "hi": "Hindi",
}

LANG_SCRIPT_CHECK = {
    "zh": lambda t: any("\u4e00" <= c <= "\u9fff" for c in t),
    "ja": lambda t: any("\u3040" <= c <= "\u30ff" for c in t),
    "ar": lambda t: any("\u0600" <= c <= "\u06ff" for c in t),
    "hi": lambda t: any("\u0900" <= c <= "\u097f" for c in t),
    "ru": lambda t: any("\u0400" <= c <= "\u04ff" for c in t),
}


def load_db_descriptions(db_path, db_id):
    """Load all language description slots for a given museum_item id."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    query = "SELECT " + ", ".join(
        [f"description_{lang}" if lang != "en" else "description" for lang in LANGUAGES]
    ) + " FROM museum_item WHERE id = ?"
    cur.execute(query, (db_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {}
    return {lang: row[i] for i, lang in enumerate(LANGUAGES)}


def is_crap(text, lang, en_text=""):
    """Return True if the description is low quality."""
    if not text or len(text.strip()) < MIN_GOOD_DESC_LEN:
        return True
    t = text.strip()
    for prefix in GARBAGE_PREFIXES:
        if t.startswith(prefix):
            return True
    # Wrong script
    if lang in LANG_SCRIPT_CHECK:
        if not LANG_SCRIPT_CHECK[lang](t):
            return True
    # Same as English (untranslated) for non-Latin languages
    if lang in ("zh", "ja", "ar", "hi", "ru") and en_text and t == en_text.strip():
        return True
    return False


def call_ollama(prompt, model=OLLAMA_MODEL, timeout=120):
    """Call local Ollama via HTTP. Returns response text."""
    import urllib.request
    import json as _json

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 512},
    }
    data = _json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = _json.loads(resp.read())
            return result.get("response", "").strip()
    except Exception as e:
        return f"ERROR: {e}"


def strip_think_tags(text):
    """Remove <think>...</think> reasoning blocks from qwen3 output."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return text.strip()


def generate_english_description(plant):
    """Use book source text to generate a clean English description.
    Handles both Book1 fields (description/traditional_uses/origin)
    and Book2 fields (intro/therapeutic_uses/how_to_use)."""
    source_parts = []

    # Book1 fields
    if plant.get("description"):
        source_parts.append(f"Botanical description: {plant['description'][:600]}")
    if plant.get("traditional_uses"):
        uses = plant["traditional_uses"]
        if isinstance(uses, list):
            uses = "; ".join(uses[:10])
        source_parts.append(f"Traditional uses: {str(uses)[:600]}")
    if plant.get("origin"):
        source_parts.append(f"Origin: {plant['origin'][:200]}")

    # Book2 fields
    if plant.get("intro"):
        source_parts.append(f"Description: {plant['intro'][:600]}")
    if plant.get("therapeutic_uses"):
        uses = plant["therapeutic_uses"]
        if isinstance(uses, list):
            uses = "; ".join(str(u) for u in uses[:10])
        source_parts.append(f"Therapeutic uses: {str(uses)[:400]}")
    if plant.get("how_to_use"):
        source_parts.append(f"How to use: {plant['how_to_use'][:300]}")

    if not source_parts:
        return "ERROR: no source text available"

    # Common name: handle both field name variants
    common = plant.get("common_names") or plant.get("common_name") or "unknown"

    source = "\n".join(source_parts)
    prompt = f"""/no_think
Write a concise, factual description of the medicinal plant {plant['scientific_name']} (common name: {common}).

Use the following source information:
{source}

Write 3-5 sentences covering: what the plant looks like, where it grows, and its main traditional/medicinal uses.
Do NOT include citations, references, or chemical compound lists.
Write in plain English. Output ONLY the description, no preamble.
"""
    return strip_think_tags(call_ollama(prompt))


def translate_description(en_text, target_lang):
    """Translate an English description to the target language."""
    lang_name = LANG_NAMES.get(target_lang, target_lang)
    prompt = f"""/no_think
Translate the following medicinal plant description into {lang_name}.
Output ONLY the translation, no preamble, no explanation.

Description:
{en_text}
"""
    return strip_think_tags(call_ollama(prompt))


def load_checkpoint(checkpoint_file):
    """Return set of already-processed (db_id, lang) pairs."""
    done = set()
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rec = json.loads(line)
                    done.add((rec["db_id"], rec["lang"]))
    return done


def append_result(checkpoint_file, record):
    with open(checkpoint_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--matched", default="matched_book1.jsonl")
    parser.add_argument("--out", default=CHECKPOINT_FILE)
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be updated without calling LLM")
    parser.add_argument("--status", choices=["AUTO", "REVIEW", "SKIP", "ALL"],
                        default="AUTO",
                        help="Which match_status to process (default: AUTO)")
    parser.add_argument("--langs", nargs="+", default=LANGUAGES,
                        help="Languages to check/translate (default: all)")
    args = parser.parse_args()

    print(f"Loading matched plants from: {args.matched}")
    with open(args.matched, encoding="utf-8") as f:
        matched = [json.loads(l) for l in f if l.strip()]

    # Filter by status
    if args.status != "ALL":
        candidates = [p for p in matched if p.get("match_status") == args.status]
    else:
        candidates = [p for p in matched if p.get("match_status") in ("AUTO", "REVIEW")]

    print(f"  {len(candidates)} plants to process (status={args.status})")

    done = load_checkpoint(args.out)
    print(f"  {len(done)} (db_id, lang) pairs already done (checkpoint)")

    total_updated = 0

    for plant in candidates:
        db_id = plant.get("db_id")
        if db_id is None:
            continue

        print(f"\n[{plant['scientific_name']}] db_id={db_id} '{plant['db_name']}'")

        # Load current DB descriptions
        db_descs = load_db_descriptions(DB_PATH, db_id)
        en_text = db_descs.get("en", "") or ""

        # Find which language slots need work
        crap_langs = [
            lang for lang in args.langs
            if lang in db_descs and is_crap(db_descs.get(lang, ""), lang, en_text)
        ]

        if not crap_langs:
            print("  All description slots OK, skipping.")
            continue

        print(f"  Crap langs: {crap_langs}")

        if args.dry_run:
            print(f"  [DRY RUN] Would generate/translate for: {crap_langs}")
            continue

        # Generate English if needed
        new_en = None
        if "en" in crap_langs or (not en_text and any(l != "en" for l in crap_langs)):
            if (db_id, "en") not in done:
                print("  Generating English description from book...")
                new_en = generate_english_description(plant)
                if new_en.startswith("ERROR:"):
                    print(f"  LLM error: {new_en}")
                    continue
                print(f"  EN: {new_en[:100]}...")
                append_result(args.out, {
                    "db_id": db_id,
                    "lang": "en",
                    "text": new_en,
                    "source": plant.get("source", "book"),
                    "scientific_name": plant["scientific_name"],
                })
                done.add((db_id, "en"))
                total_updated += 1
                time.sleep(0.5)
            else:
                # Load previously generated EN from checkpoint
                with open(args.out, encoding="utf-8") as f:
                    for line in f:
                        rec = json.loads(line)
                        if rec["db_id"] == db_id and rec["lang"] == "en":
                            new_en = rec["text"]
                            break

        # Use new English or existing good English for translation base
        translation_base = new_en or en_text
        if not translation_base or len(translation_base) < 50:
            print("  No usable English text for translation, skipping non-EN langs.")
            crap_langs = [l for l in crap_langs if l == "en"]

        # Translate into each crap language
        for lang in crap_langs:
            if lang == "en":
                continue
            if (db_id, lang) in done:
                print(f"  [{lang}] already done, skipping.")
                continue

            print(f"  Translating -> {lang} ({LANG_NAMES.get(lang)})...")
            translated = translate_description(translation_base, lang)
            if translated.startswith("ERROR:"):
                print(f"  LLM error: {translated}")
                continue

            print(f"  [{lang}]: {translated[:80]}...")
            append_result(args.out, {
                "db_id": db_id,
                "lang": lang,
                "text": translated,
                "source": plant.get("source", "book"),
                "scientific_name": plant["scientific_name"],
            })
            done.add((db_id, lang))
            total_updated += 1
            time.sleep(0.5)

    print(f"\nDone. {total_updated} new entries written to {args.out}")
    if not args.dry_run:
        print(f"Run apply_updates.py --dry-run to preview, then apply_updates.py to commit.")


if __name__ == "__main__":
    main()
