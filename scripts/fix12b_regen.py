#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix 12b: Regenerate CORRUPT(?) descriptions one language at a time with script validation.
   Checkpoint: fix12b_done_<lang>.txt per language to allow resume."""
import sqlite3, sys, io, json, urllib.request, time, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH    = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'
OLLAMA_URL = 'http://localhost:11434/api/generate'
MODEL      = 'qwen3:8b-ctx16k'

# Script validation patterns
CYR  = re.compile(r'[\u0400-\u04ff]')
CJK  = re.compile(r'[\u4e00-\u9fff\u3040-\u30ff]')
ARAB = re.compile(r'[\u0600-\u06ff]')
DEVA = re.compile(r'[\u0900-\u097f]')
LATIN = re.compile(r'[a-zA-Z]')

def latin_ratio(text):
    clean = re.sub(r'[\s()\[\].,;:\-/0-9]', '', text)
    return len(LATIN.findall(clean)) / len(clean) if clean else 0.0

def validate(text, lang):
    if not text or len(text) < 40:
        return False
    if lang == 'ru':
        return bool(CYR.search(text)) and latin_ratio(text) < 0.5
    if lang in ('ja', 'zh'):
        return bool(CJK.search(text)) and latin_ratio(text) < 0.7
    if lang == 'ar':
        return bool(ARAB.search(text)) and latin_ratio(text) < 0.5
    if lang == 'hi':
        return bool(DEVA.search(text)) and latin_ratio(text) < 0.5
    return True

LANG_PROMPTS = {
    'ru': lambda name, desc: f"Переведи на русский язык следующее описание лекарственного растения '{name}'. Дай только перевод, без пояснений:\n\n{desc[:600]}",
    'ja': lambda name, desc: f"次の薬用植物「{name}」の説明を日本語に翻訳してください。翻訳のみを出力し、説明は不要です：\n\n{desc[:600]}",
    'zh': lambda name, desc: f'请将以下药用植物《{name}》的描述翻译成中文（简体）。只输出翻译，不要解释：\n\n{desc[:600]}',
    'ar': lambda name, desc: f"ترجم الوصف التالي للنبات الطبي '{name}' إلى اللغة العربية. أعطِ الترجمة فقط بدون تعليقات:\n\n{desc[:600]}",
    'hi': lambda name, desc: f"निम्नलिखित औषधीय पौधे '{name}' के विवरण को हिंदी में अनुवाद करें। केवल अनुवाद दें, कोई स्पष्टीकरण नहीं:\n\n{desc[:600]}",
}

def ollama_call(prompt, tokens=450):
    data = json.dumps({
        'model': MODEL, 'prompt': prompt, 'stream': False,
        'options': {'num_predict': tokens, 'temperature': 0.2}
    }).encode('utf-8')
    req = urllib.request.Request(OLLAMA_URL, data=data,
                                  headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            text = json.loads(r.read())['response'].strip()
        idx = text.find('</think>')
        return text[idx+8:].strip() if idx != -1 else text
    except Exception as e:
        return None

def load_done(lang):
    f = f'fix12b_done_{lang}.txt'
    if not os.path.exists(f):
        return set()
    with open(f, 'r', encoding='utf-8') as fh:
        return set(int(x.strip()) for x in fh if x.strip())

def mark_done(lang, pid):
    with open(f'fix12b_done_{lang}.txt', 'a', encoding='utf-8') as f:
        f.write(f'{pid}\n')

conn = sqlite3.connect(DB_PATH)
conn.execute('PRAGMA encoding = "UTF-8"')
conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
cur = conn.cursor()

LANGS = ['ru', 'ja', 'zh', 'ar', 'hi']

for lang in LANGS:
    col = f'description_{lang}'
    cur.execute(f'SELECT id, paintingname, description FROM museum_item WHERE unicode({col})=63 ORDER BY id')
    rows = cur.fetchall()
    done = load_done(lang)
    todo = [(pid, name, desc) for pid, name, desc in rows if pid not in done]

    print(f'\n=== {lang.upper()}: {len(todo)} rows to fix ===', flush=True)

    fixed = skipped = failed = 0

    for pid, name, en_desc in todo:
        if not en_desc or len(en_desc) < 50:
            print(f'  [{pid}] SKIP: short English desc')
            mark_done(lang, pid)
            skipped += 1
            continue

        print(f'  [{pid}] {name[:35]}...', end=' ', flush=True)
        prompt = LANG_PROMPTS[lang](name, en_desc)
        result = ollama_call(prompt)

        if result and validate(result, lang):
            cur.execute(f'UPDATE museum_item SET {col}=? WHERE id=?', (result, pid))
            conn.commit()
            mark_done(lang, pid)
            fixed += 1
            print(f'OK ({len(result)} chars)')
        elif result:
            # Script mismatch — try once more with stronger instruction
            prompt2 = prompt + f'\n\nIMPORTANT: Respond ONLY in {"Russian" if lang=="ru" else "Japanese" if lang=="ja" else "Chinese" if lang=="zh" else "Arabic" if lang=="ar" else "Hindi"} script. No Latin characters in the response except for scientific plant names.'
            result2 = ollama_call(prompt2)
            if result2 and validate(result2, lang):
                cur.execute(f'UPDATE museum_item SET {col}=? WHERE id=?', (result2, pid))
                conn.commit()
                mark_done(lang, pid)
                fixed += 1
                print(f'OK-retry ({len(result2)} chars)')
            else:
                mark_done(lang, pid)
                failed += 1
                print(f'FAIL (got: {(result2 or result or "")[:40]!r})')
        else:
            mark_done(lang, pid)
            failed += 1
            print(f'OLLAMA ERROR')

        time.sleep(0.3)

    print(f'  {lang.upper()} summary: fixed={fixed} skipped={skipped} failed={failed}')

print('\n=== All languages done ===')
conn.close()
