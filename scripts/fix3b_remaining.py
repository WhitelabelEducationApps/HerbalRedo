#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix 3b: Remaining long names and <think> tags missed due to dict key collision."""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'

# Correct format: list of (id, lang, value) to avoid dict key collision
FIXES = [
    # ZH still bad
    (143,  'zh', '当归属'),
    (273,  'zh', '毛蕊花'),
    (277,  'zh', '省沽油'),
    (281,  'zh', '柽柳'),
    (307,  'zh', '阿米芹'),
    (601,  'zh', '美登木'),
    (677,  'zh', '莎草'),
    (747,  'zh', '山矢车菊'),
    (749,  'zh', '大花矢车菊'),
    (803,  'zh', '美洲当归'),
    (881,  'zh', '委陵菜'),
    (982,  'zh', '美国荷包牡丹'),
    (983,  'zh', '野荷包牡丹'),
    # ES still bad
    (747,  'es', 'Centaurea de montaña'),
    (873,  'es', 'Geum de río'),
    (923,  'es', 'Aguileña roja'),
    # PT still bad
    (52,   'pt', 'Lavanda'),
    (261,  'pt', 'Ramno'),
    (273,  'pt', 'Verbasco'),
    (275,  'pt', 'Quássia'),
    (629,  'pt', 'Corniso vermelho'),
    (769,  'pt', 'Calaminta'),
    (861,  'pt', 'Alquimila'),
    (865,  'pt', 'Aremónia'),
    (873,  'pt', 'Erva-benta'),
    (875,  'pt', 'Gillenia'),
    (897,  'pt', 'Baptísia'),
    (906,  'pt', 'Sissoo'),
    (967,  'pt', 'Escopólia'),
    # RU still bad
    (34,   'ru', 'Пижма девичья'),
    (45,   'ru', 'Конский каштан'),
    (861,  'ru', 'Манжетка'),
    # DE still bad
    (52,   'de', 'Echter Lavendel'),
    # FR still bad
    (52,   'fr', 'Lavande officinale'),
    # IT still bad
    (273,  'it', 'Verbasco'),
    (821,  'it', 'Cicuta'),
    # RO <think> tag
    (149,  'ro', 'Valeriană'),
]

conn = sqlite3.connect(DB_PATH)
conn.execute('PRAGMA encoding = "UTF-8"')
cur = conn.cursor()

# Group by id
from collections import defaultdict
by_id = defaultdict(dict)
for pid, lang, val in FIXES:
    by_id[pid][lang] = val

updated = 0
for pid, langs in sorted(by_id.items()):
    sets = [f'paintingname_{l}=?' for l in langs]
    vals = list(langs.values()) + [pid]
    cur.execute(f'UPDATE museum_item SET {",".join(sets)} WHERE id=?', vals)
    if cur.rowcount:
        updated += 1
        print(f'  id={pid}: {list(langs.keys())}')

conn.commit()
print(f'\nRows updated: {updated}')

# Final check
conn2 = sqlite3.connect(DB_PATH)
conn2.text_factory = lambda b: b.decode('utf-8', errors='replace')
cur2 = conn2.cursor()
print('\nRemaining > 60 chars:')
any_left = False
for lang in ['zh','es','pt','ru','de','fr','it','ro']:
    cur2.execute(f'SELECT COUNT(*) FROM museum_item WHERE length(paintingname_{lang}) > 60')
    c = cur2.fetchone()[0]
    if c:
        any_left = True
        print(f'  {lang}: {c}')
if not any_left:
    print('  None.')
print('\nChecking <think> tags in all name fields:')
any_think = False
for lang in ['ro','es','de','fr','it','ru','pt','ja','zh','ar','hi']:
    cur2.execute(f"SELECT COUNT(*) FROM museum_item WHERE paintingname_{lang} LIKE '%<think>%'")
    c = cur2.fetchone()[0]
    if c:
        any_think = True
        print(f'  {lang}: {c}')
if not any_think:
    print('  None.')
conn2.close()
