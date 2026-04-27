#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix23_wiki_translate.py
=======================
Auto-fix bad plant descriptions and names via Wikipedia + Google Translate.

Detection:
  • Wrong/missing script characters for the language
  • Too short (< 180 chars for descriptions, < 2 chars for names)
  • Genus-taxonomy stubs (Wikipedia copy-paste)
  • Template boilerplate (e.g. JA/ZH auto-generated stubs)
  • English text leaked into a non-English slot
  • Name identical to English when it shouldn't be

Fix strategy (per field, in order):
  1. Wikipedia      — fetch the intro paragraph of the plant's article in
                      the target language (via Latin name, langlinks, or search)
  2. Google Translate — translate the English description/name (only when the
                      English source itself is good)
  3. Ollama LLM     — generate a fresh medicinal description from scratch when
                      both Wikipedia and the English source are bad (e.g. genus
                      stubs). Uses qwen3:8b-ctx16k running locally.

Atomic commits: every successful fix is committed immediately.
Safe to interrupt at any time — partial progress is preserved.

Usage:
  python fix23_wiki_translate.py              # all languages, all plants
  python fix23_wiki_translate.py --langs ro,es --ids 100-200
  python fix23_wiki_translate.py --names-only
  python fix23_wiki_translate.py --descs-only
  python fix23_wiki_translate.py --dry-run    # detect only, no writes
"""

import sqlite3, sys, io, re, json, time, argparse, urllib.request, urllib.parse
from typing import Optional, Tuple

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── Config ──────────────────────────────────────────────────────────────────
DB_PATH  = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'
LANGS    = ['ro', 'es', 'de', 'fr', 'it', 'pt', 'ru', 'ja', 'zh', 'ar', 'hi']
WIKI_DELAY   = 0.4   # seconds between Wikipedia requests
GTRANS_DELAY = 2.0   # seconds between Google Translate requests (avoid rate-limiting)
HTTP_TIMEOUT = 15    # seconds per request
OLLAMA_URL   = 'http://localhost:11434/api/generate'
OLLAMA_MODEL = 'qwen3:8b-ctx16k'
MAX_DESC_CHARS = 750 # trim Wikipedia extracts to this length

# ── Script / language validators ────────────────────────────────────────────
CYR  = re.compile(r'[\u0400-\u04ff]')
CJK  = re.compile(r'[\u4e00-\u9fff\u3040-\u30ff]')   # CJK + hiragana + katakana
ARAB = re.compile(r'[\u0600-\u06ff]')
DEVA = re.compile(r'[\u0900-\u097f]')
RO_D = re.compile(r'[șțăîâȘȚĂÎÂ]')
LATIN = re.compile(r'[a-zA-Z]')

def _latin_ratio(t: str) -> float:
    c = re.sub(r'[\s\d\(\)\[\].,;:\-/]', '', t)
    return len(LATIN.findall(c)) / len(c) if c else 0.0

SCRIPT_OK = {
    'ro': lambda t: bool(RO_D.search(t)) and _latin_ratio(t) > 0.4,
    'es': lambda t: _latin_ratio(t) > 0.5 and bool(re.search(
        r'\b(es|una|planta|del|las|los|se|en|de|que|con|para|su|por)\b', t, re.I)),
    'de': lambda t: _latin_ratio(t) > 0.5 and bool(re.search(
        r'\b(ist|die|der|das|und|eine|in|von|als|wird|wurde|im)\b', t, re.I)),
    'fr': lambda t: _latin_ratio(t) > 0.5 and bool(re.search(
        r'\b(est|une|les|des|dans|qui|pour|avec|sur|par|au|la|le)\b', t, re.I)),
    'it': lambda t: _latin_ratio(t) > 0.5 and bool(re.search(
        r'\b(è|una|le|della|del|che|con|per|nel|si|viene|un|la)\b', t, re.I)),
    'pt': lambda t: _latin_ratio(t) > 0.5 and bool(re.search(
        r'\b(é|uma|da|do|que|com|para|em|se|no|na|os|as|sua|seu)\b', t, re.I)),
    'ru': lambda t: bool(CYR.search(t)) and _latin_ratio(t) < 0.5,
    'ja': lambda t: bool(CJK.search(t)) and _latin_ratio(t) < 0.7,
    'zh': lambda t: bool(CJK.search(t)) and _latin_ratio(t) < 0.7,
    'ar': lambda t: bool(ARAB.search(t)) and _latin_ratio(t) < 0.5,
    'hi': lambda t: bool(DEVA.search(t)) and _latin_ratio(t) < 0.5,
}

# ── Bad-content detectors ────────────────────────────────────────────────────
_GENUS_STUB = re.compile(
    r'\b(es un género|est un genre|ist eine Gattung|è un genere|'
    r'é um género|é um gênero|es el género|is a genus of|'
    r'Gattung von|ist eine Art)\b', re.I)
_JA_TPL  = re.compile(r'は伝統的な用途を持つ薬用植物です')
_ZH_TPL  = re.compile(r'是一种具有传统用途的药用植物')
_EN_LEAK = re.compile(
    r'\b(is a plant|commonly (known|used)|native to|it is used|'
    r'are used|has been used|which is|the root|the leaves|'
    r'the plant|is native|also known)\b', re.I)
_WIKIDATA = re.compile(r'\bQ\d{3,}\b')          # "Wikidata: Q12345"
_THINK_TAG = re.compile(r'</?think>', re.I)      # leftover model noise
_HI_LIST  = re.compile(r'औषधीय पादपों की सूची')  # "List of medicinal plants"
_LATIN_BINOMIAL = re.compile(r'^[A-Z][a-z]+\s+[a-z]+')

def _is_bad_desc(text: Optional[str], lang: str) -> Tuple[bool, str]:
    """Return (is_bad, reason_code)."""
    if not text or len(text.strip()) < 10:
        return True, 'EMPTY'
    text = text.strip()
    if len(text) < 180:
        return True, 'SHORT'
    ok_fn = SCRIPT_OK.get(lang)
    if ok_fn and not ok_fn(text):
        return True, 'WRONG_SCRIPT'
    if _GENUS_STUB.search(text):
        return True, 'GENUS_STUB'
    if lang == 'ja' and _JA_TPL.search(text):
        return True, 'JA_TEMPLATE'
    if lang == 'zh' and _ZH_TPL.search(text):
        return True, 'ZH_TEMPLATE'
    if lang in ('es', 'fr', 'it', 'pt', 'de', 'ru') and _EN_LEAK.search(text):
        return True, 'EN_LEAK'
    if _WIKIDATA.search(text) and len(text) < 300:
        return True, 'WIKIDATA_STUB'
    if _THINK_TAG.search(text):
        return True, 'MODEL_NOISE'
    if lang == 'hi' and _HI_LIST.search(text):
        return True, 'HI_LIST_TEMPLATE'
    return False, ''

_EN_WORDS = re.compile(
    r'\b(tree|berry|flower|root|herb|plant|common|wild|sweet|bitter|'
    r'black|white|water|wood|mountain|valley|coast|sea|river|field|'
    r'marsh|false|true|leaf|leaves|bark|seed|fruit|grass|weed|'
    r'healing|medicinal|sacred|holy|thorny|spiny|climbing|creeping)\b', re.I)

def _is_bad_name(name: Optional[str], lang: str, en_name: str) -> Tuple[bool, str]:
    """Return (is_bad, reason_code)."""
    if not name or len(name.strip()) < 2:
        return True, 'EMPTY'
    name = name.strip()
    en = en_name.strip()
    # Identical to English name
    if name == en:
        # Non-Latin-script languages: always bad if no target script
        if lang == 'ru' and not CYR.search(name):
            return True, 'COPY_EN'
        if lang in ('ja', 'zh') and not CJK.search(name):
            return True, 'COPY_EN'
        if lang == 'ar' and not ARAB.search(name):
            return True, 'COPY_EN'
        if lang == 'hi' and not DEVA.search(name):
            return True, 'COPY_EN'
        # Latin-script languages: bad if EN name contains English common words
        # AND is not a pure Latin binomial
        if lang in ('ro', 'es', 'de', 'fr', 'it', 'pt'):
            if not _LATIN_BINOMIAL.match(en) and _EN_WORDS.search(en):
                return True, 'COPY_EN'
    return False, ''

# ── Google Translate language code mapping ───────────────────────────────────
# Google Translate uses different codes from our internal ISO codes in a few cases.
GTRANS_LANG = {
    'zh': 'zh-CN',   # Simplified Chinese (zh alone is rejected by the API)
    'pt': 'pt',      # Portuguese — 'pt' works; 'pt-BR'/'pt-PT' also accepted
    # all other langs (ro, es, de, fr, it, ru, ja, ar, hi) match directly
}

def _gtrans_code(lang: str) -> str:
    return GTRANS_LANG.get(lang, lang)

# ── HTTP helpers ─────────────────────────────────────────────────────────────
_HEADERS = {'User-Agent': 'HerbalRedoBot/1.0 (plant-db-fix; educational)'}

def _http_get(url: str, params: dict, retries: int = 2) -> Optional[bytes]:
    qs = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    full_url = f'{url}?{qs}'
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(full_url, headers=_HEADERS)
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
                return r.read()
        except Exception as e:
            print(f'\n    [HTTP ERR attempt {attempt+1}] {type(e).__name__}: {e}  url={full_url[:120]}')
            if attempt < retries:
                time.sleep(1.5)
    return None

def _json_get(url: str, params: dict) -> Optional[dict]:
    raw = _http_get(url, params)
    if not raw:
        return None
    try:
        return json.loads(raw.decode('utf-8', errors='replace'))
    except Exception as e:
        print(f'\n    [JSON ERR] {type(e).__name__}: {e}  raw={raw[:80]}')
        return None

# ── Wikipedia helpers ────────────────────────────────────────────────────────
def _truncate_sentences(text: str, max_chars: int) -> str:
    """Return text trimmed to at most max_chars, cutting at sentence boundary."""
    if len(text) <= max_chars:
        return text
    # Find last sentence-ending punctuation before max_chars
    cut = text[:max_chars]
    for sep in ('.', '。', '।', '۔'):
        idx = cut.rfind(sep)
        if idx > max_chars // 2:
            return cut[:idx + 1].strip()
    return cut.rstrip() + '…'

def wiki_langlink_title(en_title: str, target_lang: str) -> Optional[str]:
    """Return the article title in target_lang via English Wikipedia langlinks."""
    data = _json_get('https://en.wikipedia.org/w/api.php', {
        'action': 'query', 'prop': 'langlinks', 'lllang': target_lang,
        'titles': en_title, 'format': 'json', 'redirects': 1,
    })
    if not data:
        return None
    for page in data.get('query', {}).get('pages', {}).values():
        for ll in page.get('langlinks', []):
            if ll.get('lang') == target_lang:
                return ll['*']
    return None

def wiki_intro(title: str, lang: str) -> Optional[str]:
    """Fetch the intro paragraph(s) of a Wikipedia article in target language."""
    data = _json_get(f'https://{lang}.wikipedia.org/w/api.php', {
        'action': 'query', 'prop': 'extracts', 'exintro': 1,
        'explaintext': 1, 'titles': title, 'format': 'json', 'redirects': 1,
    })
    if not data:
        return None
    for page in data.get('query', {}).get('pages', {}).values():
        if 'missing' in page:
            return None
        extract = (page.get('extract') or '').strip()
        if extract and len(extract) > 100:
            return _truncate_sentences(extract, MAX_DESC_CHARS)
    return None

def wiki_search_first(query: str, lang: str) -> Optional[str]:
    """Search Wikipedia in lang, return first hit title."""
    data = _json_get(f'https://{lang}.wikipedia.org/w/api.php', {
        'action': 'query', 'list': 'search', 'srsearch': query,
        'srlimit': 1, 'format': 'json',
    })
    if not data:
        return None
    results = data.get('query', {}).get('search', [])
    return results[0]['title'] if results else None

def get_wiki_description(en_name: str, latin: str, lang: str) -> Optional[str]:
    """
    Try to get a Wikipedia intro in `lang` for this plant.
    Tries (in order): latin direct → langlink from latin → langlink from EN name → search.
    """
    candidates = []
    if latin:
        candidates.append((latin, lang))           # direct Latin name in target lang
    if latin:
        ll = wiki_langlink_title(latin, lang)
        if ll:
            candidates.append((ll, lang))
    if en_name:
        ll = wiki_langlink_title(en_name, lang)
        if ll:
            candidates.append((ll, lang))
    if latin:
        hit = wiki_search_first(latin, lang)
        if hit:
            candidates.append((hit, lang))

    seen = set()
    for title, lg in candidates:
        if title in seen:
            continue
        seen.add(title)
        time.sleep(WIKI_DELAY)
        print(f'\n    [WIKI] trying {lg}.wikipedia.org/wiki/{title}')
        intro = wiki_intro(title, lg)
        if not intro:
            print(f'\n    [WIKI] no extract returned')
            continue
        if len(intro) < 180:
            print(f'\n    [WIKI] too short ({len(intro)} chars): {intro[:60]!r}')
            continue
        bad, reason = _is_bad_desc(intro, lang)
        if bad:
            print(f'\n    [WIKI] extract rejected ({reason}): {intro[:60]!r}')
            continue
        return intro
    print(f'\n    [WIKI] all candidates exhausted for {lang}')
    return None

def get_wiki_name(en_name: str, latin: str, lang: str) -> Optional[str]:
    """Return the article title in target lang (= local common name) from Wikipedia."""
    for en_title in filter(None, [latin, en_name]):
        time.sleep(WIKI_DELAY)
        title = wiki_langlink_title(en_title, lang)
        if title and len(title) > 1:
            return title
    return None

# ── Google Translate fallback ────────────────────────────────────────────────
def _gtranslate_chunk(text: str, tl: str, sl: str = 'en') -> Optional[str]:
    """Translate one chunk via the unofficial Google Translate endpoint."""
    tl_code = _gtrans_code(tl)
    print(f'\n    [GTRANS] sl={sl} tl={tl_code} len={len(text)} text[:40]={text[:40]!r}')
    raw = _http_get('https://translate.googleapis.com/translate_a/single', {
        'client': 'gtx', 'sl': sl, 'tl': tl_code, 'dt': 't', 'q': text,
    })
    if not raw:
        print(f'\n    [GTRANS] no response from server')
        return None
    try:
        result = json.loads(raw.decode('utf-8', errors='replace'))
        translation = ''.join(seg[0] for seg in result[0] if seg and seg[0])
        print(f'\n    [GTRANS] got {len(translation)} chars: {translation[:60]!r}')
        return translation
    except Exception as e:
        print(f'\n    [GTRANS ERR] {type(e).__name__}: {e}  raw={raw[:120]}')
        return None

def google_translate(text: str, tl: str, sl: str = 'en') -> Optional[str]:
    """Translate full text to tl, splitting into ≤4500-char chunks if needed."""
    if not text:
        return None
    # Split at paragraph/sentence boundary under 4500 chars
    chunks: list[str] = []
    while len(text) > 4500:
        cut = text[:4500].rfind('. ')
        if cut < 2000:
            cut = 4499
        chunks.append(text[:cut + 1])
        text = text[cut + 1:].lstrip()
    chunks.append(text)

    parts = []
    for chunk in chunks:
        time.sleep(GTRANS_DELAY)
        translated = _gtranslate_chunk(chunk, tl, sl)
        if translated is None:
            return None
        parts.append(translated)
    return ' '.join(parts)

# ── Ollama LLM fallback (used when EN source is itself bad) ──────────────────
_LLM_PROMPTS = {
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

def ollama_generate(en_name: str, latin: str, lang: str) -> Optional[str]:
    """Generate a fresh medicinal description via local Ollama LLM."""
    prompt_fn = _LLM_PROMPTS.get(lang)
    if not prompt_fn:
        return None
    sci_str = f' ({latin})' if latin else ''
    prompt  = prompt_fn(en_name, sci_str)
    print(f'\n    [LLM] generating {lang} description for "{en_name}{sci_str}"')
    data = json.dumps({
        'model': OLLAMA_MODEL, 'prompt': prompt, 'stream': False,
        'options': {'num_predict': 500, 'temperature': 0.15},
    }).encode()
    req = urllib.request.Request(
        OLLAMA_URL, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=150) as r:
            text = json.loads(r.read())['response'].strip()
        # Strip <think>…</think> block if model included reasoning
        idx = text.find('</think>')
        text = text[idx + 8:].strip() if idx != -1 else text
        # Strip any leading label like "**Descriere:**"
        text = re.sub(
            r'^[\*#\s]*(Descriere|Răspuns|Plantă|Description|Beschreibung|'
            r'Описание|説明|描述|وصف|विवरण)[:\*\s]+',
            '', text, flags=re.I).strip()
        print(f'\n    [LLM] got {len(text)} chars: {text[:60]!r}')
        return text
    except Exception as e:
        print(f'\n    [LLM ERR] {type(e).__name__}: {e}')
        return None

# ── Extract Latin name from English plant name ───────────────────────────────
def extract_latin(en_name: str) -> str:
    """Extract Latin binomial from e.g. 'Marigold (Calendula officinalis)'."""
    m = re.search(r'\(([A-Z][a-z]+(?:\s+[a-z]+){1,2})\)', en_name)
    return m.group(1) if m else ''

# ── Main ─────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description='Fix bad plant descriptions/names via Wikipedia + Google Translate')
    p.add_argument('--langs',       default=','.join(LANGS), help='Comma-separated language codes to process')
    p.add_argument('--ids',         default='',   help='ID range like 100-200, or comma list like 5,10,15')
    p.add_argument('--descs-only',  action='store_true', help='Only fix descriptions')
    p.add_argument('--names-only',  action='store_true', help='Only fix names')
    p.add_argument('--dry-run',     action='store_true', help='Detect problems only, no DB writes')
    p.add_argument('--wiki-only',   action='store_true', help='Skip Google Translate fallback')
    return p.parse_args()

def parse_id_filter(ids_str: str) -> Optional[set]:
    if not ids_str:
        return None
    ids = set()
    for part in ids_str.split(','):
        part = part.strip()
        if '-' in part:
            lo, hi = part.split('-', 1)
            ids.update(range(int(lo), int(hi) + 1))
        elif part:
            ids.add(int(part))
    return ids

def _print_fix(pid, en_name, lang, field, reason, method, new_val, dry_run):
    tag = '[DRY]' if dry_run else '✓'
    preview = (new_val or '')[:65].replace('\n', ' ')
    print(f'\n  {tag} [{pid}] {lang} {field} ({reason}) → {method}: {preview}')

def _print_fail(pid, en_name, lang, field, reason):
    print(f'\n  ✗ [{pid}] {lang} {field} ({reason}) → no fix found')

def main():
    args = parse_args()
    langs = [l.strip() for l in args.langs.split(',') if l.strip() in LANGS]
    id_filter = parse_id_filter(args.ids)
    fix_descs = not args.names_only
    fix_names = not args.descs_only

    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA encoding = "UTF-8"')
    conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
    cur = conn.cursor()

    # Load all plants
    lang_desc_cols = ', '.join(f'description_{l}, paintingname_{l}' for l in langs)
    cur.execute(f'SELECT id, paintingname, description, {lang_desc_cols} FROM museum_item ORDER BY id')
    rows = cur.fetchall()

    if id_filter:
        rows = [r for r in rows if r[0] in id_filter]

    total = len(rows)
    stats = {'wiki_desc': 0, 'gtrans_desc': 0, 'llm_desc': 0,
             'wiki_name': 0, 'gtrans_name': 0,
             'fail_desc': 0, 'fail_name': 0, 'skip': 0}

    print(f'Processing {total} plants × {len(langs)} languages'
          + (' [DRY RUN]' if args.dry_run else ''))
    print(f'Fix descriptions: {fix_descs}   Fix names: {fix_names}')
    print(f'Langs: {langs}\n')

    for i, row in enumerate(rows):
        pid     = row[0]
        en_name = row[1] or ''
        en_desc = row[2] or ''
        latin   = extract_latin(en_name)

        print(f'\r[{i+1}/{total}] {pid} {en_name[:35]:<35}', end='', flush=True)

        # Build per-lang index into row (columns come in pairs: desc, name)
        base = 3  # row[3] = desc_langs[0], row[4] = name_langs[0], etc.
        for j, lang in enumerate(langs):
            desc = row[base + j * 2]
            name = row[base + j * 2 + 1]

            # ── Description ──────────────────────────────────
            if fix_descs:
                bad, reason = _is_bad_desc(desc, lang)
                if bad:
                    new_desc = None
                    method   = None

                    # 1. Wikipedia
                    wiki = get_wiki_description(en_name, latin, lang)
                    if wiki:
                        new_desc = wiki
                        method   = 'WIKI'

                    # 2. Google Translate fallback (only when EN source is itself good)
                    if not new_desc and not args.wiki_only and en_desc and len(en_desc) > 50:
                        en_bad, en_reason = _is_bad_desc(en_desc, 'en')
                        if en_bad:
                            print(f'\n    [GTRANS SKIP] EN source is itself bad ({en_reason}) — skipping to LLM')
                        else:
                            time.sleep(GTRANS_DELAY)
                            gt = google_translate(en_desc, lang)
                            if gt:
                                gt_bad, gt_reason = _is_bad_desc(gt, lang)
                                if not gt_bad:
                                    new_desc = gt
                                    method   = 'GTRANS'
                                else:
                                    print(f'\n    [GTRANS REJECT] translation failed validator ({gt_reason}): {gt[:60]!r}')

                    # 3. Ollama LLM — generate from scratch when source is bad or
                    #    both Wikipedia and Google Translate failed
                    if not new_desc and not args.wiki_only:
                        llm = ollama_generate(en_name, latin, lang)
                        if llm:
                            llm_bad, llm_reason = _is_bad_desc(llm, lang)
                            if not llm_bad:
                                new_desc = llm
                                method   = 'LLM'
                            else:
                                print(f'\n    [LLM REJECT] output failed validator ({llm_reason}): {llm[:60]!r}')

                    if new_desc:
                        _print_fix(pid, en_name, lang, 'DESC', reason, method, new_desc, args.dry_run)
                        if not args.dry_run:
                            cur.execute(f'UPDATE museum_item SET description_{lang}=? WHERE id=?',
                                        (new_desc, pid))
                            conn.commit()  # ATOMIC — safe to interrupt
                        stats[f'{method.lower()}_desc'] += 1
                    else:
                        _print_fail(pid, en_name, lang, 'DESC', reason)
                        stats['fail_desc'] += 1
                else:
                    stats['skip'] += 1

            # ── Name ─────────────────────────────────────────
            if fix_names:
                bad, reason = _is_bad_name(name, lang, en_name)
                if bad:
                    new_name = None
                    method   = None

                    # 1. Wikipedia article title
                    wn = get_wiki_name(en_name, latin, lang)
                    if wn and wn != name:
                        new_name = wn
                        method   = 'WIKI'

                    # 2. Google Translate fallback
                    if not new_name and not args.wiki_only:
                        time.sleep(GTRANS_DELAY)
                        gt = google_translate(en_name, lang)
                        if gt and len(gt) > 1:
                            new_name = gt
                            method   = 'GTRANS'

                    if new_name:
                        _print_fix(pid, en_name, lang, 'NAME', reason, method, new_name, args.dry_run)
                        if not args.dry_run:
                            cur.execute(f'UPDATE museum_item SET paintingname_{lang}=? WHERE id=?',
                                        (new_name, pid))
                            conn.commit()  # ATOMIC
                        stats[f'{method.lower()}_name'] += 1
                    else:
                        _print_fail(pid, en_name, lang, 'NAME', reason)
                        stats['fail_name'] += 1
                else:
                    stats['skip'] += 1

    conn.close()

    print(f'\n\n{"─"*60}')
    print(f'Done!  Plants: {total}  Langs: {len(langs)}')
    print(f'  Descriptions fixed — wiki: {stats["wiki_desc"]}  gtrans: {stats["gtrans_desc"]}  llm: {stats["llm_desc"]}  failed: {stats["fail_desc"]}')
    print(f'  Names fixed       — wiki: {stats["wiki_name"]}  gtrans: {stats["gtrans_name"]}  failed: {stats["fail_name"]}')
    print(f'  Already OK: {stats["skip"]}')

if __name__ == '__main__':
    main()
