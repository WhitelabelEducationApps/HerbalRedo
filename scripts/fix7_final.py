#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix 7: style_ja/zh/ru bulk update, description_ja CP1252 recode, final verification."""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'

STYLE_JA = {
    'adaptogen':'アダプトゲン','analgesic':'鎮痛','anti-inflammatory':'抗炎症',
    'antibacterial':'抗菌','antifungal':'抗真菌','antimicrobial':'抗微生物',
    'antiparasitic':'駆虫','antispasmodic':'鎮痙','antiviral':'抗ウイルス',
    'aromatic':'芳香','cardiovascular':'心臓血管','circulatory':'循環',
    'dermatological':'皮膚科','detoxifying':'解毒','digestive':'消化',
    'diuretic':'利尿','gynecological':'婦人科','hepatoprotective':'肝保護',
    'immunomodulatory':'免疫調節','laxative':'緩下','nervine':'神経鎮静',
    'nutritive':'栄養','respiratory':'呼吸器','tonic':'強壮',
    'toxic':'毒性','wound-healing':'創傷治癒',
}
STYLE_ZH = {
    'adaptogen':'适应原','analgesic':'镇痛','anti-inflammatory':'抗炎',
    'antibacterial':'抗菌','antifungal':'抗真菌','antimicrobial':'抗微生物',
    'antiparasitic':'驱虫','antispasmodic':'解痉','antiviral':'抗病毒',
    'aromatic':'芳香','cardiovascular':'心血管','circulatory':'循环',
    'dermatological':'皮肤科','detoxifying':'解毒','digestive':'消化',
    'diuretic':'利尿','gynecological':'妇科','hepatoprotective':'保肝',
    'immunomodulatory':'免疫调节','laxative':'通便','nervine':'镇神经',
    'nutritive':'滋补','respiratory':'呼吸','tonic':'强壮',
    'toxic':'有毒','wound-healing':'愈创',
}
STYLE_RU = {
    'adaptogen':'Адаптоген','analgesic':'Обезболивающее','anti-inflammatory':'Противовоспалительное',
    'antibacterial':'Антибактериальное','antifungal':'Противогрибковое','antimicrobial':'Антимикробное',
    'antiparasitic':'Противопаразитарное','antispasmodic':'Спазмолитическое','antiviral':'Противовирусное',
    'aromatic':'Ароматическое','cardiovascular':'Сердечно-сосудистое','circulatory':'Кровообращение',
    'dermatological':'Дерматологическое','detoxifying':'Детоксикационное','digestive':'Пищеварительное',
    'diuretic':'Мочегонное','gynecological':'Гинекологическое','hepatoprotective':'Гепатопротекторное',
    'immunomodulatory':'Иммуномодулирующее','laxative':'Слабительное','nervine':'Успокаивающее',
    'nutritive':'Питательное','respiratory':'Дыхательное','tonic':'Тонизирующее',
    'toxic':'Токсичное','wound-healing':'Ранозаживляющее',
}

conn = sqlite3.connect(DB_PATH)
conn.execute('PRAGMA encoding = "UTF-8"')
cur = conn.cursor()

total = 0
for style in STYLE_JA:
    cur.execute('UPDATE museum_item SET style_ja=?, style_zh=?, style_ru=? WHERE style=?',
                (STYLE_JA[style], STYLE_ZH[style], STYLE_RU[style], style))
    total += cur.rowcount
conn.commit()
print(f'Style JA/ZH/RU updated: {total} rows')

# Fix description_ja id=935 (Sweet Orange - garbled encoding)
conn_r = sqlite3.connect(DB_PATH)
conn_r.text_factory = bytes
cur_r = conn_r.cursor()
cur_r.execute('SELECT description_ja FROM museum_item WHERE id=935')
raw = cur_r.fetchone()[0]
conn_r.close()

if raw:
    try:
        raw.decode('utf-8')
        print('description_ja id=935: already valid UTF-8')
    except UnicodeDecodeError:
        try:
            recoded = raw.decode('cp1252')
            cur.execute('UPDATE museum_item SET description_ja=? WHERE id=935', (recoded,))
            conn.commit()
            print('description_ja id=935: recoded from CP1252')
        except Exception as e:
            print(f'description_ja id=935: could not recode - {e}')

conn.close()

# ── Final comprehensive health check ──────────────────────────────────────────
print()
print('=== FINAL DATABASE HEALTH CHECK ===')
conn2 = sqlite3.connect(DB_PATH)
conn2.text_factory = lambda b: b.decode('utf-8', errors='replace')
cur2 = conn2.cursor()
langs = ['ro','es','de','fr','it','ru','pt','ja','zh','ar','hi']

issues = 0

# 1. Missing fields
cur2.execute("SELECT COUNT(*) FROM museum_item")
total_rows = cur2.fetchone()[0]
print(f'\nTotal rows: {total_rows}')
print('\n[1] Missing (NULL/empty) translations:')
any_miss = False
for lang in langs:
    for field in ['paintingname','description','style']:
        col = f'{field}_{lang}'
        cur2.execute(f"SELECT COUNT(*) FROM museum_item WHERE {col} IS NULL OR {col}=''")
        c = cur2.fetchone()[0]
        if c:
            any_miss = True; issues += c
            print(f'  {col}: {c}')
if not any_miss: print('  None.')

# 2. unicode=63 corruption
print('\n[2] Corrupted (unicode=63) in non-Latin scripts:')
any_corrupt = False
for lang in ['ja','zh','ru','ar','hi']:
    for field in ['paintingname','style']:
        col = f'{field}_{lang}'
        cur2.execute(f'SELECT COUNT(*) FROM museum_item WHERE unicode({col})=63')
        c = cur2.fetchone()[0]
        if c:
            any_corrupt = True; issues += c
            print(f'  {col}: {c}')
if not any_corrupt: print('  None.')

# 3. CP1252 replacement chars
print('\n[3] CP1252 replacement chars:')
any_cp = False
for lang in langs:
    for field in ['paintingname','description']:
        col = f'{field}_{lang}'
        cur2.execute(f"SELECT COUNT(*) FROM museum_item WHERE {col} LIKE ?", ('%\ufffd%',))
        c = cur2.fetchone()[0]
        if c:
            any_cp = True; issues += c
            print(f'  {col}: {c}')
if not any_cp: print('  None.')

# 4. <think> tags
print('\n[4] <think> tags:')
any_think = False
for lang in langs:
    for field in ['paintingname','description','style']:
        col = f'{field}_{lang}'
        cur2.execute(f"SELECT COUNT(*) FROM museum_item WHERE {col} LIKE '%<think>%'")
        c = cur2.fetchone()[0]
        if c:
            any_think = True; issues += c
            print(f'  {col}: {c}')
if not any_think: print('  None.')

# 5. Long name fields
print('\n[5] Name fields > 60 chars:')
any_long = False
for lang in langs:
    cur2.execute(f'SELECT COUNT(*) FROM museum_item WHERE length(paintingname_{lang}) > 60')
    c = cur2.fetchone()[0]
    if c:
        any_long = True; issues += c
        print(f'  paintingname_{lang}: {c}')
if not any_long: print('  None.')

print(f'\n=== Total issues remaining: {issues} ===')
conn2.close()
