#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix 12: Regenerate Category E CORRUPT(?) descriptions (RU/JA/ZH/AR/HI) via Ollama.
   Uses English description as source. Generates all corrupt langs per row in one call.
   Checkpoint file: fix12_done.txt to allow resume."""
import sqlite3, sys, io, json, urllib.request, time, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH   = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'
CHECKPOINT = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\fix12_done.txt'
OLLAMA_URL = 'http://localhost:11434/api/generate'
MODEL      = 'qwen3:8b-ctx16k'

LANG_NAMES = {'ru': 'Russian', 'ja': 'Japanese', 'zh': 'Chinese (Simplified)',
              'ar': 'Arabic',   'hi': 'Hindi'}
LANG_LABELS = {'ru': 'RU', 'ja': 'JA', 'zh': 'ZH', 'ar': 'AR', 'hi': 'HI'}

def load_done():
    if not os.path.exists(CHECKPOINT):
        return set()
    with open(CHECKPOINT, 'r', encoding='utf-8') as f:
        return set(int(x.strip()) for x in f if x.strip())

def mark_done(pid):
    with open(CHECKPOINT, 'a', encoding='utf-8') as f:
        f.write(f'{pid}\n')

def strip_think(text):
    idx = text.find('</think>')
    return text[idx + 8:].strip() if idx != -1 else text

def ollama_call(prompt, tokens=600):
    data = json.dumps({
        'model': MODEL, 'prompt': prompt, 'stream': False,
        'options': {'num_predict': tokens, 'temperature': 0.2}
    }).encode('utf-8')
    req = urllib.request.Request(OLLAMA_URL, data=data,
                                  headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return strip_think(json.loads(r.read())['response'].strip())
    except Exception as e:
        return None

def parse_sections(text, langs):
    """Parse response split by ##LANG## markers."""
    result = {}
    for lang in langs:
        label = LANG_LABELS[lang]
        pattern = rf'##\s*{label}\s*##\s*(.*?)(?=##\s*(?:{"|".join(LANG_LABELS[l] for l in langs)})\s*##|$)'
        m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if m:
            result[lang] = m.group(1).strip()
    return result

conn = sqlite3.connect(DB_PATH)
conn.execute('PRAGMA encoding = "UTF-8"')
conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
cur = conn.cursor()

# Find all rows with at least one corrupt non-Latin description
cur.execute('''SELECT id, paintingname, description,
    description_ru, description_ja, description_zh, description_ar, description_hi
    FROM museum_item WHERE
    unicode(description_ru)=63 OR unicode(description_ja)=63 OR
    unicode(description_zh)=63 OR unicode(description_ar)=63 OR
    unicode(description_hi)=63 ORDER BY id''')
rows = cur.fetchall()

done = load_done()
total = len(rows)
updated = 0

print(f'Total rows to process: {total}')
print(f'Already done: {len(done)}')

for row in rows:
    pid       = row[0]
    en_name   = row[1] or ''
    en_desc   = row[2] or ''

    if pid in done:
        continue

    desc_vals = {'ru': row[3], 'ja': row[4], 'zh': row[5], 'ar': row[6], 'hi': row[7]}
    corrupt_langs = [l for l, v in desc_vals.items() if v and ord(v[0]) == 63]
    if not corrupt_langs:
        mark_done(pid)
        continue

    print(f'\n[{pid}] {en_name[:40]} — regenerate {corrupt_langs}', flush=True)

    if len(en_desc) < 50:
        print(f'  SKIP: English desc too short ({len(en_desc)} chars)')
        mark_done(pid)
        continue

    # Build prompt requesting all corrupt langs at once
    lang_list = '\n'.join(f'## {LANG_LABELS[l]} ## ({LANG_NAMES[l]}):' for l in corrupt_langs)
    prompt = (
        f"Translate the following medicinal plant description into each requested language.\n"
        f"Plant: {en_name}\n\n"
        f"English description:\n{en_desc[:800]}\n\n"
        f"Provide the translation for each language below, using the exact section headers shown.\n"
        f"Write only the translation text after each header. No explanations.\n\n"
        f"{lang_list}\n"
    )

    response = ollama_call(prompt, tokens=len(corrupt_langs) * 300 + 200)

    if not response:
        print(f'  ERROR: Ollama failed')
        continue

    parsed = parse_sections(response, corrupt_langs)

    sets = []
    vals = []
    for lang in corrupt_langs:
        text = parsed.get(lang, '').strip()
        if len(text) > 30:
            sets.append(f'description_{lang}=?')
            vals.append(text)
            print(f'  {lang}: {len(text)} chars')
        else:
            print(f'  {lang}: PARSE FAILED (got: {text[:50]!r})')

    if sets:
        vals.append(pid)
        cur.execute(f'UPDATE museum_item SET {",".join(sets)} WHERE id=?', vals)
        conn.commit()
        updated += 1

    mark_done(pid)
    time.sleep(0.5)

print(f'\n=== Done: {updated} rows updated ===')
conn.close()
