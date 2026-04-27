#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix corrupted non-Latin translations in plants.db.
Uses Ollama qwen3:8b-ctx16k to batch-translate plant names.
"""

import sqlite3
import json
import requests
import sys
import time

DB_PATH = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'
OLLAMA_URL = 'http://localhost:11434/api/generate'
MODEL = 'qwen3:8b-ctx16k'
BATCH_SIZE = 20

LANG_NAMES = {
    'ja': 'Japanese',
    'zh': 'Chinese (Simplified)',
    'ru': 'Russian',
    'ar': 'Arabic',
    'hi': 'Hindi',
}

def ollama_translate(batch, langs_needed):
    """
    batch: list of (id, english_name)
    langs_needed: set of lang codes needed for at least one plant in the batch
    Returns: dict of {id: {lang: translated_name}}
    """
    lines = '\n'.join(f'{pid}|{name}' for pid, name in batch)
    lang_list = ', '.join(f'{LANG_NAMES[l]} ({l})' for l in sorted(langs_needed))

    prompt = f"""Translate these medicinal plant names into {lang_list}.
Use the most common local/vernacular name in each language. If no common name exists, use the scientific/Latin name.
Return ONLY valid JSON, no markdown, no explanation, no thinking.
Format: [{{"id": <number>, "ja": "...", "zh": "...", "ru": "...", "ar": "...", "hi": "..."}}]
Only include language keys that are in this list: {sorted(langs_needed)}

Plants (id|english_name):
{lines}"""

    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.1, "num_predict": 4096}},
            timeout=180
        )
        resp.raise_for_status()
        raw = resp.json().get('response', '')

        # Strip /think blocks if present
        if '</think>' in raw:
            raw = raw[raw.rfind('</think>') + 8:].strip()

        # Extract JSON array
        start = raw.find('[')
        end = raw.rfind(']') + 1
        if start == -1 or end == 0:
            print(f"  WARNING: No JSON array found in response. Raw: {raw[:200]}")
            return {}

        parsed = json.loads(raw[start:end])
        return {item['id']: {k: v for k, v in item.items() if k != 'id'} for item in parsed}
    except Exception as e:
        print(f"  ERROR in ollama_translate: {e}")
        return {}


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA encoding = "UTF-8"')
    cur = conn.cursor()

    # Fetch all corrupted entries and which langs they need
    cur.execute("""
        SELECT id, paintingname,
               CASE WHEN unicode(paintingname_ja) = 63 THEN 1 ELSE 0 END,
               CASE WHEN unicode(paintingname_zh) = 63 THEN 1 ELSE 0 END,
               CASE WHEN unicode(paintingname_ru) = 63 THEN 1 ELSE 0 END,
               CASE WHEN unicode(paintingname_ar) = 63 THEN 1 ELSE 0 END,
               CASE WHEN unicode(paintingname_hi) = 63 THEN 1 ELSE 0 END
        FROM museum_item
        WHERE unicode(paintingname_ja) = 63
           OR unicode(paintingname_zh) = 63
           OR unicode(paintingname_ru) = 63
           OR unicode(paintingname_ar) = 63
           OR unicode(paintingname_hi) = 63
        ORDER BY id
    """)
    rows = cur.fetchall()
    print(f"Found {len(rows)} plants needing translation fixes")

    # Build per-plant needs
    plants = []
    for row in rows:
        pid, name, ja_bad, zh_bad, ru_bad, ar_bad, hi_bad = row
        needs = set()
        if ja_bad: needs.add('ja')
        if zh_bad: needs.add('zh')
        if ru_bad: needs.add('ru')
        if ar_bad: needs.add('ar')
        if hi_bad: needs.add('hi')
        plants.append((pid, name, needs))

    total_updated = 0
    batch_num = 0

    for i in range(0, len(plants), BATCH_SIZE):
        batch = plants[i:i + BATCH_SIZE]
        batch_ids = [(p[0], p[1]) for p in batch]
        langs_needed = set()
        for _, _, needs in batch:
            langs_needed |= needs

        batch_num += 1
        print(f"Batch {batch_num}: plants {batch[0][0]}-{batch[-1][0]} | langs: {sorted(langs_needed)}")

        translations = ollama_translate(batch_ids, langs_needed)

        if not translations:
            print(f"  SKIP: empty result")
            continue

        for pid, name, needs in batch:
            if pid not in translations:
                print(f"  MISSING id={pid} ({name}) in response")
                continue

            t = translations[pid]
            sets = []
            vals = []
            for lang in needs:
                val = t.get(lang, '')
                if val and val.strip():
                    sets.append(f'paintingname_{lang} = ?')
                    vals.append(val.strip())
                else:
                    print(f"  MISSING {lang} for id={pid} ({name})")

            if sets:
                vals.append(pid)
                cur.execute(f"UPDATE museum_item SET {', '.join(sets)} WHERE id = ?", vals)
                total_updated += 1

        conn.commit()
        print(f"  Committed. Total updated so far: {total_updated}")

        # Small pause between batches to avoid overwhelming Ollama
        if i + BATCH_SIZE < len(plants):
            time.sleep(1)

    conn.close()
    print(f"\nDone. {total_updated} plants updated across {batch_num} batches.")

    # Verify
    conn2 = sqlite3.connect(DB_PATH)
    cur2 = conn2.cursor()
    for lang in ['ja', 'zh', 'ru', 'ar', 'hi']:
        cur2.execute(f"SELECT COUNT(*) FROM museum_item WHERE unicode(paintingname_{lang}) = 63")
        count = cur2.fetchone()[0]
        print(f"  Remaining corrupted {lang}: {count}")
    conn2.close()


if __name__ == '__main__':
    main()
