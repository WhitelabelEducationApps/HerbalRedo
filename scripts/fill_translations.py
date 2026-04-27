#!/usr/bin/env python3
"""
Fill missing plant translations using local LLM with simple single-item requests.

Translates one plant field at a time for reliability; uses concurrent requests for speed.

Usage:
    python fill_translations.py
    python fill_translations.py --dry-run
    python fill_translations.py --test (single plant test)
    python fill_translations.py --workers 5

Requires:
    pip install requests
"""

import argparse
import sqlite3
import sys
import time
from collections import defaultdict
from threading import Lock
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import DB_PATH, LANGUAGES, DB_COLUMNS


def log(msg=""):
    """Print with immediate flush so progress shows up under buffered stdout."""
    print(msg, flush=True)


def fmt_eta(seconds):
    if seconds <= 0 or seconds != seconds:  # NaN guard
        return "--:--"
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"

OLLAMA_API = "http://localhost:11434/api/generate"
DEFAULT_MODEL = 'qwen3:8b-ctx16k'
DEFAULT_WORKERS = 3

LANG_NAMES = {
    'ro': 'Romanian', 'es': 'Spanish', 'de': 'German', 'fr': 'French',
    'it': 'Italian', 'ru': 'Russian', 'pt': 'Portuguese', 'zh': 'Chinese',
    'ja': 'Japanese', 'ar': 'Arabic', 'hi': 'Hindi',
}


def translate_single(text, target_lang='es', model=None):
    """Translate a single text string to one language. Simple and reliable."""
    if model is None:
        model = DEFAULT_MODEL

    if not text or len(text.strip()) < 2:
        return text

    target_name = LANG_NAMES.get(target_lang, target_lang)
    prompt = f"Translate to {target_name} only, no explanation:\n{text}"

    t0 = time.time()
    try:
        response = requests.post(
            OLLAMA_API,
            json={'model': model, 'prompt': prompt, 'stream': False},
            timeout=300
        )
        elapsed = time.time() - t0
        if response.status_code == 200:
            resp_text = response.json().get('response', '').strip()

            # Strip thinking tags if present
            if '<think>' in resp_text and '</think>' in resp_text:
                resp_text = resp_text.split('</think>')[-1].strip()

            return (resp_text if resp_text else text, elapsed, None)
        return (text, elapsed, f"HTTP {response.status_code}")
    except requests.RequestException as e:
        return (text, time.time() - t0, f"{type(e).__name__}: {e}")


def analyze_gaps(db_path):
    """Analyze missing translations in database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    gaps = {lang: {'names': 0, 'descriptions': 0} for lang in LANGUAGES if lang != 'en'}

    cursor.execute("SELECT COUNT(*) FROM museum_item")
    total_plants = cursor.fetchone()[0]

    for lang in LANGUAGES:
        if lang == 'en':
            continue

        name_col, desc_col, _ = DB_COLUMNS.get(lang, (None, None, None))
        if not name_col:
            continue

        cursor.execute(f"SELECT COUNT(*) FROM museum_item WHERE {name_col} IS NULL OR {name_col} = ''")
        gaps[lang]['names'] = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM museum_item WHERE {desc_col} IS NULL OR {desc_col} = ''")
        gaps[lang]['descriptions'] = cursor.fetchone()[0]

    conn.close()
    return total_plants, gaps


def get_translation_tasks(db_path):
    """Generate list of (plant_id, lang, field_type, english_text) tuples for all missing translations."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tasks = []

    cursor.execute("SELECT id, paintingname, description FROM museum_item ORDER BY id")
    plants = cursor.fetchall()

    for plant_id, english_name, english_desc in plants:
        for lang in LANGUAGES:
            if lang == 'en':
                continue

            name_col, desc_col, _ = DB_COLUMNS.get(lang, (None, None, None))
            if not name_col:
                continue

            # Check if name is missing
            cursor.execute(f"SELECT {name_col} FROM museum_item WHERE id = ?", (plant_id,))
            result = cursor.fetchone()
            current_name = result[0] if result else None

            if (not current_name or current_name.strip() == '') and english_name:
                tasks.append((plant_id, lang, 'name', english_name))

            # Check if description is missing
            cursor.execute(f"SELECT {desc_col} FROM museum_item WHERE id = ?", (plant_id,))
            result = cursor.fetchone()
            current_desc = result[0] if result else None

            if (not current_desc or current_desc.strip() == '') and english_desc:
                tasks.append((plant_id, lang, 'desc', english_desc))

    conn.close()
    return tasks


def fill_translations(db_path, dry_run=False, limit=-1, model=None, test_mode=False, workers=DEFAULT_WORKERS):
    """Fill missing translations using concurrent single-item requests."""
    if model is None:
        model = DEFAULT_MODEL

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    total_plants, gaps = analyze_gaps(db_path)

    log("Translation Gap Analysis")
    log("=" * 70)
    log(f"Total plants: {total_plants}\n")
    log(f"{'Language':<12} {'Missing Names':<20} {'Missing Descriptions':<20}")
    log("-" * 70)

    total_gaps = 0
    for lang in sorted(gaps.keys()):
        names_gap = gaps[lang]['names']
        desc_gap = gaps[lang]['descriptions']
        total_gaps += names_gap + desc_gap
        log(f"{lang:<12} {names_gap:<20} {desc_gap:<20}")

    log("-" * 70)
    log(f"{'TOTAL':<12} {sum(g['names'] for g in gaps.values()):<20} {sum(g['descriptions'] for g in gaps.values()):<20}")
    log(f"\nTotal fields to fill: {total_gaps}")
    log(f"Concurrent workers: {workers}\n")

    if dry_run:
        log("(DRY RUN - no changes made)")
        conn.close()
        return

    if test_mode:
        log("(TEST MODE - single plant only)\n")

    response = input(f"Fill {total_gaps} missing translations with {model}? (y/n): ")
    if response.lower() != 'y':
        log("Cancelled.")
        conn.close()
        return

    log(f"\nFilling translations with {model}...")
    log(f"Ollama endpoint: {OLLAMA_API}")
    log(f"Workers: {workers}\n")

    # Get all tasks
    log("Scanning database for missing translations...")
    scan_t0 = time.time()
    all_tasks = get_translation_tasks(db_path)
    log(f"  -> {len(all_tasks)} tasks queued in {time.time() - scan_t0:.1f}s")

    if test_mode:
        all_tasks = all_tasks[:5]  # Only first 5 tasks

    if limit > 0:
        all_tasks = all_tasks[:limit]

    # Break down by language for visibility
    per_lang = defaultdict(int)
    for t in all_tasks:
        per_lang[t[1]] += 1
    log("Breakdown by language: " + ", ".join(f"{k}={v}" for k, v in sorted(per_lang.items())))
    log("")

    total = len(all_tasks)
    filled = 0
    failed = 0
    unchanged = 0
    started = time.time()
    db_lock = Lock()
    per_lang_done = defaultdict(int)
    log_every = max(1, min(25, total // 50)) if total > 0 else 1
    log(f"Starting batch: {total} tasks (progress line every {log_every} completions)")
    log(f"First request sent at {time.strftime('%H:%M:%S')}. Watching Ollama...\n")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_task = {
            executor.submit(translate_single, task[3], task[1], model): task
            for task in all_tasks
        }
        log(f"  [submit] {total} requests submitted to executor, {workers} workers\n")

        for i, future in enumerate(as_completed(future_to_task), 1):
            task = future_to_task[future]
            plant_id, lang, field_type, english_text = task

            try:
                translation, req_elapsed, err = future.result()

                if err:
                    failed += 1
                    log(f"  [{i}/{total}] FAIL  {lang}/{field_type} id={plant_id} ({req_elapsed:.1f}s) :: {err}")
                    continue

                if translation and translation != english_text:
                    name_col, desc_col, _ = DB_COLUMNS.get(lang, (None, None, None))
                    if not name_col:
                        continue

                    col = name_col if field_type == 'name' else desc_col
                    with db_lock:
                        cursor.execute(f"UPDATE museum_item SET {col} = ? WHERE id = ?",
                                       (translation, plant_id))
                        conn.commit()
                    filled += 1
                    per_lang_done[lang] += 1
                else:
                    unchanged += 1

                if i % log_every == 0 or i == total:
                    elapsed = time.time() - started
                    rate = i / elapsed if elapsed > 0 else 0
                    eta = (total - i) / rate if rate > 0 else 0
                    preview = (translation or "")[:40].replace("\n", " ")
                    log(
                        f"  [{i}/{total}] {i*100//total}% "
                        f"filled={filled} fail={failed} skip={unchanged} "
                        f"| {rate:.2f}/s ETA {fmt_eta(eta)} "
                        f"| last: {lang}/{field_type} ({req_elapsed:.1f}s) \"{preview}\""
                    )

            except Exception as e:
                failed += 1
                log(f"  [{i}/{total}] EXCEPTION on {lang}/{field_type} id={plant_id}: {type(e).__name__}: {e}")

    conn.close()

    elapsed = time.time() - started
    log(f"\n[OK] Complete in {fmt_eta(elapsed)} ({elapsed:.1f}s)")
    log(f"  Total processed: {total}")
    log(f"  Filled:          {filled}")
    log(f"  Unchanged:       {unchanged}")
    log(f"  Failed:          {failed}")
    if per_lang_done:
        log("  Per language:    " + ", ".join(f"{k}={v}" for k, v in sorted(per_lang_done.items())))
    if elapsed > 0:
        log(f"  Avg throughput:  {total/elapsed:.2f} tasks/s")


def main():
    parser = argparse.ArgumentParser(
        description="Fill missing plant translations using local LLM (concurrent mode)"
    )
    parser.add_argument('--model', type=str, default=DEFAULT_MODEL,
                        help=f'Ollama model to use (default: {DEFAULT_MODEL})')
    parser.add_argument('--dry-run', action='store_true', help='Show gaps without making changes')
    parser.add_argument('--test', action='store_true', help='Test mode - translate only 5 items')
    parser.add_argument('--workers', type=int, default=DEFAULT_WORKERS,
                        help=f'Concurrent workers (default: {DEFAULT_WORKERS})')
    parser.add_argument('--limit', type=int, default=-1, help='Max items to translate (for testing)')
    args = parser.parse_args()

    log("Plant Translation Filler (Concurrent Mode)")
    log("=" * 70)
    log(f"Database: {DB_PATH}")
    log(f"Model:    {args.model}")
    log(f"Workers:  {args.workers}")
    log(f"Started:  {time.strftime('%Y-%m-%d %H:%M:%S')}")
    if args.test:
        log("Mode:     TEST (5 items only)\n")
    else:
        log("")

    fill_translations(DB_PATH, dry_run=args.dry_run, limit=args.limit, model=args.model,
                     test_mode=args.test, workers=args.workers)


if __name__ == '__main__':
    main()
