#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Automated quality audit of all 539 rows. Prints only flagged issues."""
import sqlite3, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'

LANGS = ['ro','es','de','fr','it','ru','pt','ja','zh','ar','hi']
NON_LATIN = ['ja','zh','ar','hi','ru']
CJK   = re.compile(r'[\u4e00-\u9fff\u3000-\u303f\u3040-\u30ff\u31f0-\u31ff]')
CYR   = re.compile(r'[\u0400-\u04ff]')
ARAB  = re.compile(r'[\u0600-\u06ff]')
DEVA  = re.compile(r'[\u0900-\u097f]')
LATIN = re.compile(r'[a-zA-Z]')

def latin_ratio(text):
    clean = re.sub(r'[\s()\[\].,;:\-/0-9]', '', text)
    if not clean: return 0.0
    return len(LATIN.findall(clean)) / len(clean)

def check_name(val, lang, pid, name, issues):
    if not val:
        issues.append(f'EMPTY paintingname_{lang}')
        return
    # unicode=63 corruption
    if ord(val[0]) == 63:
        issues.append(f'CORRUPT(?) paintingname_{lang}: {val[:20]}')
    # replacement char
    if '\ufffd' in val:
        issues.append(f'CP1252 paintingname_{lang}: {val[:30]}')
    # think tag
    if '<think>' in val.lower():
        issues.append(f'THINK paintingname_{lang}')
    # length
    if len(val) > 60:
        issues.append(f'LONG({len(val)}) paintingname_{lang}: {val[:50]}')
    # wrong script
    if lang == 'ar':
        if CJK.search(val): issues.append(f'CJK-in-AR paintingname_ar: {val[:40]}')
        if CYR.search(val): issues.append(f'CYR-in-AR paintingname_ar: {val[:40]}')
        if DEVA.search(val): issues.append(f'DEVA-in-AR paintingname_ar: {val[:40]}')
        if latin_ratio(val) > 0.5: issues.append(f'LATIN-in-AR({latin_ratio(val):.0%}) paintingname_ar: {val[:40]}')
    if lang == 'hi':
        if CJK.search(val): issues.append(f'CJK-in-HI paintingname_hi: {val[:40]}')
        if CYR.search(val): issues.append(f'CYR-in-HI paintingname_hi: {val[:40]}')
        if ARAB.search(val): issues.append(f'ARAB-in-HI paintingname_hi: {val[:40]}')
        if latin_ratio(val) > 0.6: issues.append(f'LATIN-in-HI({latin_ratio(val):.0%}) paintingname_hi: {val[:40]}')
    if lang in ('ja','zh'):
        if CYR.search(val): issues.append(f'CYR-in-{lang.upper()} paintingname_{lang}: {val[:40]}')
        if ARAB.search(val): issues.append(f'ARAB-in-{lang.upper()} paintingname_{lang}: {val[:40]}')
        if latin_ratio(val) > 0.7: issues.append(f'LATIN-in-{lang.upper()}({latin_ratio(val):.0%}) paintingname_{lang}: {val[:40]}')
    if lang == 'ru':
        if CJK.search(val): issues.append(f'CJK-in-RU paintingname_ru: {val[:40]}')
        if ARAB.search(val): issues.append(f'ARAB-in-RU paintingname_ru: {val[:40]}')

def check_desc(val, lang, issues):
    if not val:
        issues.append(f'EMPTY description_{lang}')
        return
    if ord(val[0]) == 63:
        issues.append(f'CORRUPT(?) description_{lang}: {val[:20]}')
    if '\ufffd' in val:
        issues.append(f'CP1252 description_{lang}: {val[:30]}')
    if '<think>' in val.lower():
        issues.append(f'THINK description_{lang}')
    # wrong plant check: description in a translated lang starts with different plant name
    # (detect by checking if first 80 chars contain known disambiguation keywords)
    snippet = val[:120].lower()
    BAD_PATTERNS = ['may refer to', 'bezeichnet:', 'peut se rapporter',
                    'disambiguation', 'footballer', 'born 19', 'singer',
                    'est un cours d', 'este un curs de apă', 'este un sat',
                    'este un rau', 'este un râu']
    for bp in BAD_PATTERNS:
        if bp in snippet:
            issues.append(f'WRONG-CONTENT description_{lang}: [{val[:60]}]')
            break
    # wrong script
    if lang == 'ar' and CJK.search(val[:200]):
        issues.append(f'CJK-in-AR description_ar snippet')
    if lang == 'hi' and latin_ratio(val[:100]) > 0.7:
        issues.append(f'LATIN-heavy-HI description_hi: {val[:40]}')

def check_style(val, lang, issues):
    if not val:
        issues.append(f'EMPTY style_{lang}')
        return
    if ord(val[0]) == 63:
        issues.append(f'CORRUPT(?) style_{lang}: {val[:20]}')
    if '\ufffd' in val:
        issues.append(f'CP1252 style_{lang}: {val[:20]}')
    if lang == 'ar' and latin_ratio(val) > 0.5:
        issues.append(f'LATIN-in-AR style_ar: {val[:30]}')
    if lang == 'hi' and latin_ratio(val) > 0.6:
        issues.append(f'LATIN-in-HI style_hi: {val[:30]}')

conn = sqlite3.connect(DB_PATH)
conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
cur = conn.cursor()
cur.execute('SELECT id, paintingname FROM museum_item ORDER BY id')
all_ids = cur.fetchall()

flagged = 0
for pid, en_name in all_ids:
    issues = []

    # Fetch name cols
    cur.execute(f'SELECT {",".join(f"paintingname_{l}" for l in LANGS)} FROM museum_item WHERE id=?', (pid,))
    names = dict(zip(LANGS, cur.fetchone()))
    for lang, val in names.items():
        check_name(val or '', lang, pid, en_name, issues)

    # Fetch desc cols
    cur.execute(f'SELECT {",".join(f"description_{l}" for l in LANGS)} FROM museum_item WHERE id=?', (pid,))
    descs = dict(zip(LANGS, cur.fetchone()))
    for lang, val in descs.items():
        check_desc(val or '', lang, issues)

    # Fetch style cols
    cur.execute(f'SELECT {",".join(f"style_{l}" for l in LANGS)} FROM museum_item WHERE id=?', (pid,))
    styles = dict(zip(LANGS, cur.fetchone()))
    for lang, val in styles.items():
        check_style(val or '', lang, issues)

    if issues:
        flagged += 1
        print(f'\n[{pid}] {en_name}')
        for iss in issues:
            print(f'  ! {iss}')

conn.close()
print(f'\n{"="*50}')
print(f'Flagged rows: {flagged} / {len(all_ids)}')
print(f'Clean rows:   {len(all_ids) - flagged} / {len(all_ids)}')
