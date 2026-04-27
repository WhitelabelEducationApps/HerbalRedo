#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix 19: Autonomous quality pass on ALL 11 languages × 539 plants.
   Rules on every cell. qwen3 for suspicious cells only.
   Progress bar + log file."""
import sqlite3, sys, io, json, urllib.request, time, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH    = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'
OLLAMA_URL = 'http://localhost:11434/api/generate'
MODEL      = 'qwen3:8b-ctx16k'
LOG        = 'fix19_changes.log'

# ── script validators ────────────────────────────────────────────────────────
CYR   = re.compile(r'[\u0400-\u04ff]')
CJK   = re.compile(r'[\u4e00-\u9fff\u3040-\u30ff]')
ARAB  = re.compile(r'[\u0600-\u06ff]')
DEVA  = re.compile(r'[\u0900-\u097f]')
RO_D  = re.compile(r'[șțăîâȘȚĂÎÂ]')
LATIN = re.compile(r'[a-zA-Z]')

def latin_ratio(t):
    c = re.sub(r'[\s\d\(\)\[\].,;:\-/]', '', t)
    return len(LATIN.findall(c)) / len(c) if c else 0.0

SCRIPT_VALIDATORS = {
    'ro': lambda t: bool(RO_D.search(t)) and latin_ratio(t) > 0.5,
    'es': lambda t: latin_ratio(t) > 0.5 and bool(re.search(r'\b(es|una|planta|del|las|los|se|en|de|que|con|para)\b', t, re.I)),
    'de': lambda t: latin_ratio(t) > 0.5 and bool(re.search(r'\b(ist|die|der|das|und|eine|in|von|als|wird|wurde)\b', t, re.I)),
    'fr': lambda t: latin_ratio(t) > 0.5 and bool(re.search(r'\b(est|une|les|des|dans|qui|pour|avec|sur|par|au)\b', t, re.I)),
    'it': lambda t: latin_ratio(t) > 0.5 and bool(re.search(r'\b(è|una|le|della|del|che|con|per|nel|si|viene)\b', t, re.I)),
    'pt': lambda t: latin_ratio(t) > 0.5 and bool(re.search(r'\b(é|uma|da|do|que|com|para|em|se|no|na|os|as)\b', t, re.I)),
    'ru': lambda t: bool(CYR.search(t)) and latin_ratio(t) < 0.5,
    'ja': lambda t: bool(CJK.search(t)) and latin_ratio(t) < 0.7,
    'zh': lambda t: bool(CJK.search(t)) and latin_ratio(t) < 0.7,
    'ar': lambda t: bool(ARAB.search(t)) and latin_ratio(t) < 0.5,
    'hi': lambda t: bool(DEVA.search(t)) and latin_ratio(t) < 0.5,
}

LANG_PROMPTS = {
    'ro': lambda n, s: f'Botanist expert. Scrie descriere medicinală română pentru "{n}"{s}. 4-5 propoziții: origine, principii active, utilizări tradiționale, beneficii. DOAR textul în română. /no_think',
    'es': lambda n, s: f'Experto botánico. Escribe descripción medicinal en español para "{n}"{s}. 4-5 oraciones: origen, principios activos, usos tradicionales, beneficios. SOLO el texto en español. /no_think',
    'de': lambda n, s: f'Botanischer Experte. Schreibe medizinische Beschreibung auf Deutsch für "{n}"{s}. 4-5 Sätze: Herkunft, Wirkstoffe, traditionelle Verwendung, Vorteile. NUR der deutsche Text. /no_think',
    'fr': lambda n, s: f'Expert botaniste. Écris une description médicinale en français pour "{n}"{s}. 4-5 phrases: origine, principes actifs, usages traditionnels, bénéfices. SEULEMENT le texte en français. /no_think',
    'it': lambda n, s: f'Esperto botanico. Scrivi descrizione medicinale in italiano per "{n}"{s}. 4-5 frasi: origine, principi attivi, usi tradizionali, benefici. SOLO il testo in italiano. /no_think',
    'pt': lambda n, s: f'Especialista botânico. Escreva descrição medicinal em português para "{n}"{s}. 4-5 frases: origem, princípios ativos, usos tradicionais, benefícios. APENAS o texto em português. /no_think',
    'ru': lambda n, s: f'Эксперт-ботаник. Напиши медицинское описание на русском для "{n}"{s}. 4-5 предложений: происхождение, активные вещества, традиционное применение, польза. ТОЛЬКО русский текст. /no_think',
    'ja': lambda n, s: f'植物学の専門家として「{n}」{s}の薬用説明を日本語で書いてください。4〜5文：産地、有効成分、伝統的用途、効能。日本語のテキストのみ。/no_think',
    'zh': lambda n, s: f'植物学专家，用中文为"{n}"{s}写一段药用描述。4-5句话：产地、活性成分、传统用途、功效。只输出中文文本。/no_think',
    'ar': lambda n, s: f'خبير نباتي. اكتب وصفاً طبياً بالعربية لنبات "{n}"{s}. 4-5 جمل: الموطن، المواد الفعالة، الاستخدامات التقليدية، الفوائد. النص العربي فقط. /no_think',
    'hi': lambda n, s: f'वनस्पति विशेषज्ञ। "{n}"{s} के लिए हिंदी में औषधीय विवरण लिखें। 4-5 वाक्य: उत्पत्ति, सक्रिय तत्व, पारंपरिक उपयोग, लाभ। केवल हिंदी पाठ। /no_think',
}

LANG_NAMES = {
    'ro': 'Romanian', 'es': 'Spanish', 'de': 'German', 'fr': 'French',
    'it': 'Italian',  'pt': 'Portuguese', 'ru': 'Russian', 'ja': 'Japanese',
    'zh': 'Chinese',  'ar': 'Arabic', 'hi': 'Hindi',
}

EN_SENT = re.compile(r'\b(is a plant|commonly (known|used)|native to|it is used|are used|has been used|which is|the root|the leaves)\b', re.I)
GENUS_STUB = re.compile(r'^[A-Za-zÀ-ž][\w\s\-]+ este un gen de (plante|conifere) din familia', re.I)

def rule_pass(desc, lang):
    if not desc:
        return desc, False
    orig = desc
    if lang in ('ro', 'es', 'de', 'fr', 'it', 'pt', 'ru'):
        desc = re.sub(r'\bgenus\b', {'ro':'gen','es':'género','de':'Gattung','fr':'genre','it':'genere','pt':'género','ru':'род'}.get(lang,'gen'), desc)
        desc = re.sub(r'\bGenusul\b', 'Genul', desc)
        # Remove purely English paragraphs
        paras = desc.split('\n')
        out = []
        for p in paras:
            s = p.strip()
            en_w = len(re.findall(r'\b(the|is|are|was|were|has|have|been|plant|used|known|native|grows|contains|traditionally)\b', s, re.I))
            ro_w = len(re.findall(r'\b(este|sont|ist|est|è|é|является|的|是|و)\b', s, re.I))
            if en_w > 4 and ro_w == 0 and len(s) > 20:
                continue
            out.append(p)
        desc = '\n'.join(out).strip()
    return desc, desc != orig

def is_suspicious(desc, lang):
    if not desc or len(desc) < 180:
        return True
    validator = SCRIPT_VALIDATORS.get(lang)
    if validator and not validator(desc):
        return True
    if lang in ('ro', 'es', 'de', 'fr', 'it', 'pt') and EN_SENT.search(desc):
        return True
    if lang == 'ro' and GENUS_STUB.match(desc.strip()):
        return True
    return False

def ollama_call(prompt):
    data = json.dumps({
        'model': MODEL, 'prompt': prompt, 'stream': False,
        'options': {'num_predict': 500, 'temperature': 0.15}
    }).encode()
    req = urllib.request.Request(OLLAMA_URL, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=150) as r:
            text = json.loads(r.read())['response'].strip()
        idx = text.find('</think>')
        text = text[idx+8:].strip() if idx != -1 else text
        text = re.sub(r'^[\*#\s]*(Descriere|Răspuns|Plantă|Description|Beschreibung|Описание)[:\*\s]+', '', text, flags=re.I).strip()
        return text
    except:
        return None

def validate(text, lang):
    if not text or len(text) < 120:
        return False
    v = SCRIPT_VALIDATORS.get(lang)
    return v(text) if v else True

def bar(n, total, w=40):
    f = int(w * n / total)
    return f'[{"█"*f}{"░"*(w-f)}] {n}/{total}'

# ─── main ────────────────────────────────────────────────────────────────────
conn = sqlite3.connect(DB_PATH)
conn.execute('PRAGMA encoding = "UTF-8"')
conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
cur  = conn.cursor()

cur.execute("SELECT id, paintingname FROM museum_item ORDER BY id")
plants = cur.fetchall()
total  = len(plants)

LANGS = ['ro','es','de','fr','it','pt','ru','ja','zh','ar','hi']

log = open(LOG, 'w', encoding='utf-8')
rule_n = llm_n = fail_n = ok_n = 0
grand_total = total * len(LANGS)
done = 0

for pid, en_name in plants:
    sci = ''
    m = re.search(r'\(([A-Z][a-z]+ [a-z]+(?:\s+[a-z]+)?)\)', en_name)
    if m:
        sci = m.group(1)
    sci_str = f' ({sci})' if sci else ''

    for lang in LANGS:
        col = f'description_{lang}'
        cur.execute(f'SELECT {col} FROM museum_item WHERE id=?', (pid,))
        desc = cur.fetchone()[0]

        done += 1
        pct = done / grand_total
        print(f'\r{bar(done, grand_total)}  {lang} [{pid}] {en_name[:25]:<25}  rule:{rule_n} llm:{llm_n} fail:{fail_n}', end='', flush=True)

        # Rule pass
        new_desc, changed = rule_pass(desc, lang)
        if changed:
            cur.execute(f'UPDATE museum_item SET {col}=? WHERE id=?', (new_desc, pid))
            log.write(f'RULE {lang} [{pid}] {en_name}\n')
            rule_n += 1
            desc = new_desc

        # LLM for suspicious
        if is_suspicious(desc, lang):
            prompt = LANG_PROMPTS[lang](en_name, sci_str)
            result = ollama_call(prompt)
            if validate(result, lang):
                cur.execute(f'UPDATE museum_item SET {col}=? WHERE id=?', (result, pid))
                log.write(f'LLM  {lang} [{pid}] {en_name}\n')
                llm_n += 1
            else:
                log.write(f'FAIL {lang} [{pid}] {en_name} | {repr((result or "")[:50])}\n')
                fail_n += 1
            time.sleep(0.2)
        else:
            ok_n += 1

    if done % (len(LANGS) * 10) == 0:
        conn.commit()

conn.commit()
conn.close()
log.close()

print(f'\n\nDone!  rule:{rule_n}  llm:{llm_n}  fail:{fail_n}  ok:{ok_n}')
print(f'Log: {LOG}')
