#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix 18: Autonomous RO quality pass — rules on all 539, qwen3 for suspicious rows only."""
import sqlite3, sys, io, json, urllib.request, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH    = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'
OLLAMA_URL = 'http://localhost:11434/api/generate'
MODEL      = 'qwen3:8b-ctx16k'
LOG        = 'fix18_changes.log'

RO_DIACR   = re.compile(r'[șțăîâȘȚĂÎÂ]')
EN_SENT    = re.compile(r'\b(is a plant|commonly (known|used)|native to|it is used|are used|has been used|which is|the root|the leaves|the plant)\b', re.I)
GENUS_ONLY = re.compile(r'^[A-Za-zÀ-ž][\w\s\-]+ este un gen de (plante|conifere) din familia\s+[\w]+[,.]', re.I)

def rule_pass(desc):
    if not desc:
        return desc, False
    orig = desc
    desc = re.sub(r'\bgenus\b', 'gen', desc)
    desc = re.sub(r'\bGenusul\b', 'Genul', desc)
    desc = re.sub(r'\bspecies\b', 'specii', desc)
    # Remove purely English paragraphs (>4 EN function words, 0 RO function words)
    paras = desc.split('\n')
    out = []
    for p in paras:
        s = p.strip()
        en = len(re.findall(r'\b(the|is|are|was|were|has|have|been|plant|used|known|native|grows|contains|traditionally|a |an )\b', s, re.I))
        ro = len(re.findall(r'\b(este|sunt|unui|unei|din|care|pentru|cu|și|în|la|de|se|un|o|al|ai|ale|cel|cea|plantă|specie)\b', s, re.I))
        if en > 4 and ro == 0 and len(s) > 20:
            continue
        out.append(p)
    desc = '\n'.join(out).strip()
    return desc, desc != orig

def is_suspicious(desc):
    if not desc or len(desc) < 180:
        return True
    if not RO_DIACR.search(desc):
        return True
    if EN_SENT.search(desc):
        return True
    if GENUS_ONLY.match(desc.strip()):
        return True
    return False

def ollama(prompt, tries=2):
    data = json.dumps({
        'model': MODEL, 'prompt': prompt, 'stream': False,
        'options': {'num_predict': 480, 'temperature': 0.15}
    }).encode()
    req = urllib.request.Request(OLLAMA_URL, data=data, headers={'Content-Type': 'application/json'})
    for _ in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=150) as r:
                text = json.loads(r.read())['response'].strip()
            idx = text.find('</think>')
            text = text[idx+8:].strip() if idx != -1 else text
            # strip any leading label like "**Descriere:**" or "Răspuns:"
            text = re.sub(r'^[\*#\s]*(Descriere|Răspuns|Plantă)[:\*\s]+', '', text, flags=re.I).strip()
            return text
        except Exception as e:
            time.sleep(3)
    return None

def validate(text):
    return text and len(text) > 120 and RO_DIACR.search(text) and \
           len(re.findall(r'\b(este|sunt|din|care|pentru|cu|și|în)\b', text, re.I)) >= 3

def bar(n, total, w=45):
    f = int(w * n / total)
    return f'\r[{"█"*f}{"░"*(w-f)}] {n}/{total}'

# ─── main ────────────────────────────────────────────────────────────────────
conn = sqlite3.connect(DB_PATH)
conn.execute('PRAGMA encoding = "UTF-8"')
conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
cur  = conn.cursor()

cur.execute("SELECT id, paintingname, paintingname_ro, description_ro FROM museum_item ORDER BY id")
rows  = cur.fetchall()
total = len(rows)

log = open(LOG, 'w', encoding='utf-8')
rule_n = llm_n = fail_n = ok_n = 0

for i, (pid, en, ro_name, ro_desc) in enumerate(rows):
    label = f'{pid} {en[:28]}'
    print(f'{bar(i+1, total)}  {label:<35}', end='', flush=True)

    # ── Rule pass ──
    new_desc, changed = rule_pass(ro_desc)
    if changed:
        cur.execute('UPDATE museum_item SET description_ro=? WHERE id=?', (new_desc, pid))
        log.write(f'RULE [{pid}] {en}\n')
        rule_n += 1
        ro_desc = new_desc

    # ── LLM for suspicious rows ──
    if is_suspicious(ro_desc):
        sci = (re.search(r'\(([A-Z][a-z]+ [a-z]+(?:\s+[a-z]+)?)\)', en) or ['',''])[1] if '(' in en else ''
        plant_id = f'"{en}"' + (f' ({sci})' if sci else '')
        prompt = (
            f'Ești botanist expert. Scrie o descriere medicinală în română pentru {plant_id}. '
            f'4-5 propoziții: origine, principii active, utilizări tradiționale, beneficii dovedite. '
            f'Răspunde DOAR cu textul în română, fără titlu sau introducere. /no_think'
        )
        result = ollama(prompt)
        if validate(result):
            cur.execute('UPDATE museum_item SET description_ro=? WHERE id=?', (result, pid))
            log.write(f'LLM  [{pid}] {en}\n  → {result[:80]}\n')
            llm_n += 1
        else:
            log.write(f'FAIL [{pid}] {en} | got={repr((result or "")[:60])}\n')
            fail_n += 1
        time.sleep(0.25)
    else:
        ok_n += 1

    if (i + 1) % 25 == 0:
        conn.commit()

conn.commit()
conn.close()
log.close()

print(f'\n\nDone — rule:{rule_n}  llm:{llm_n}  fail:{fail_n}  ok:{ok_n}')
print(f'All changes logged to {LOG}')
