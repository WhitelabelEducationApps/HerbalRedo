#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix 9: Category A (HI names with Latin parens + wrong Hindi) + Category B (specific garbage names)."""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'

# (id, column, correct_value)
FIXES = [
    # ── Category A: HI names — wrong Hindi replaced outright ──────────────────
    (5,   'paintingname_hi', 'दूधी'),            # Euphorbia hirta
    (19,  'paintingname_hi', 'अजमोद'),           # Celery (केली = banana)
    (33,  'paintingname_hi', 'मेथी'),            # Fenugreek (मूंगड़ी = wrong)
    (36,  'paintingname_hi', 'लहसुन'),           # Garlic (लौं = clove)
    (44,  'paintingname_hi', 'मेहंदी'),          # Henna (हेनन = garbled)
    (53,  'paintingname_hi', 'नींबू'),           # Lemon (nimbu = Latin)
    (54,  'paintingname_hi', 'मुलेठी'),          # Licorice (मिठटी = wrong)
    (59,  'paintingname_hi', 'अफीम पोस्त'),     # Opium poppy
    (65,  'paintingname_hi', 'सेज'),             # Sage (remove "तर्जमा:")
    (124, 'paintingname_hi', 'सेज'),             # Sage (शाक = wrong)

    # ── Category A: HI names — strip Latin parens, use proper Hindi ───────────
    (0,   'paintingname_hi', 'आसाई पाम'),        # Acai palm
    (1,   'paintingname_hi', 'अल्फाल्फा'),       # Alfalfa
    (30,  'paintingname_hi', 'नीलगिरी'),         # Eucalyptus
    (31,  'paintingname_hi', 'अमरबेल'),          # Mistletoe
    (34,  'paintingname_hi', 'फीवरफ्यू'),        # Feverfew
    (37,  'paintingname_hi', 'अदरक'),            # Ginger (correct, just strip parens)
    (38,  'paintingname_hi', 'गिंकगो'),          # Ginkgo
    (39,  'paintingname_hi', 'जिनसेंग'),         # Ginseng
    (41,  'paintingname_hi', 'अंगूर'),           # Grape
    (42,  'paintingname_hi', 'अमरूद'),           # Guava
    (43,  'paintingname_hi', 'नागफनी'),          # Hawthorn
    (46,  'paintingname_hi', 'घोड़े की पूँछ'),   # Horsetail
    (48,  'paintingname_hi', 'कावा'),            # Kava
    (49,  'paintingname_hi', 'खात'),             # Khat
    (50,  'paintingname_hi', 'कोनजाक'),          # Konjac
    (51,  'paintingname_hi', 'क्रेटम'),          # Kratom
    (52,  'paintingname_hi', 'लैवेंडर'),         # Lavender
    (55,  'paintingname_hi', 'कमल'),             # Lotus (correct, strip parens)
    (56,  'paintingname_hi', 'गेंदे का फूल'),   # Pot marigold
    (57,  'paintingname_hi', 'मार्शमैलो'),       # Marshmallow
    (58,  'paintingname_hi', 'दूध थीस्ल'),       # Milk thistle
    (60,  'paintingname_hi', 'अजवायन फूल'),      # Oregano
    (62,  'paintingname_hi', 'पुदीना'),          # Peppermint
    (63,  'paintingname_hi', 'इचिनेशिया'),       # Echinacea
    (64,  'paintingname_hi', 'रोज़मेरी'),        # Rosemary
    (66,  'paintingname_hi', 'सेंट जॉन्स वॉर्ट'), # St John's wort
    (67,  'paintingname_hi', 'ग्रीष्मकालीन सेवरी'), # Summer savory
    (69,  'paintingname_hi', 'वेलेरियन'),         # Valerian
    (70,  'paintingname_hi', 'सफेद विलो'),        # White willow

    # ── Category B: other garbage names ───────────────────────────────────────
    (46,  'paintingname_zh', '木贼'),            # Horsetail ZH (had English mix)
    (67,  'paintingname_zh', '夏季香薄荷'),       # Summer savory ZH
    (67,  'paintingname_ja', 'ナツセイボリー'),    # Summer savory JA
    (88,  'paintingname_zh', '霍迪亚'),          # Hoodia ZH (was "hoodia")
    (191, 'paintingname_ja', 'グラビオラ'),       # Soursop JA (was "スoursop")
    (309, 'paintingname_zh', '欧当归'),          # Lovage ZH (was "lovage")
    (617, 'paintingname_ja', 'グロリオサ'),       # Flame Lily JA (was "炎ラilies")
]

from collections import defaultdict
by_id = defaultdict(dict)
for pid, col, val in FIXES:
    by_id[pid][col] = val

conn = sqlite3.connect(DB_PATH)
conn.execute('PRAGMA encoding = "UTF-8"')
cur = conn.cursor()

updated = 0
for pid, cols in sorted(by_id.items()):
    sets = [f'{c}=?' for c in cols]
    vals = list(cols.values()) + [pid]
    cur.execute(f'UPDATE museum_item SET {",".join(sets)} WHERE id=?', vals)
    if cur.rowcount:
        updated += 1
        print(f'  id={pid}: {list(cols.keys())}')

conn.commit()
print(f'\nRows updated: {updated}')
conn.close()
