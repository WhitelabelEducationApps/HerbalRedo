#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix 6: Replace garbage AR/HI plant names from original Ollama run."""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'

# List of (id, lang, correct_name)
FIXES = [
    # AR garbage entries
    (0,   'ar', 'أكاي'),
    (1,   'ar', 'الفصفصة'),
    (2,   'ar', 'الصبار'),
    (3,   'ar', 'أرنيكا'),
    (5,   'ar', 'فربيون'),
    (6,   'ar', 'الأستراغالوس'),
    (12,  'ar', 'البرتقال المر'),
    (13,  'ar', 'الكوخوش الأسود'),
    (16,  'ar', 'الأرقطيون'),
    (19,  'ar', 'الكرفس'),
    (20,  'ar', 'الكينا'),
    (24,  'ar', 'التوت البري'),
    (30,  'ar', 'الكافور'),
    (31,  'ar', 'الهدال'),
    (32,  'ar', 'حوذانة الليل'),
    (33,  'ar', 'الحلبة'),
    (34,  'ar', 'عشبة الأم'),
    (35,  'ar', 'الكتان'),
    (36,  'ar', 'الثوم'),
    (37,  'ar', 'الزنجبيل'),
    (38,  'ar', 'الجنكة'),
    (39,  'ar', 'الجنسنغ'),
    (40,  'ar', 'الجذر الذهبي'),
    (41,  'ar', 'العنب'),
    (42,  'ar', 'الجوافا'),
    (43,  'ar', 'الزعرور'),
    (44,  'ar', 'الحناء'),
    (45,  'ar', 'كستناء الحصان'),
    (46,  'ar', 'ذيل الحصان'),
    (47,  'ar', 'شجرة سم الأسماك الجامايكية'),
    (48,  'ar', 'الكافا'),
    (50,  'ar', 'كونجاك'),
    (51,  'ar', 'الكراتوم'),
    (52,  'ar', 'الخزامى'),
    (53,  'ar', 'الليمون'),
    (54,  'ar', 'عرق السوس'),
    (55,  'ar', 'اللوتس'),
    (56,  'ar', 'الأقحوان'),
    (57,  'ar', 'الخطمي'),
    (58,  'ar', 'شوك الحليب'),
    (59,  'ar', 'الخشخاش'),
    (60,  'ar', 'أوريغانو'),
    (62,  'ar', 'النعناع الفلفلي'),
    (63,  'ar', 'القنفذية الشرقية'),
    (64,  'ar', 'إكليل الجبل'),
    (65,  'ar', 'المريمية'),
    (66,  'ar', 'عشبة القديس يوحنا'),
    (67,  'ar', 'مردقوش الصيف'),
    (68,  'ar', 'الزعتر'),
    (69,  'ar', 'حشيشة القط'),
    (70,  'ar', 'الصفصاف الأبيض'),
    (81,  'ar', 'البابونج'),
    (86,  'ar', 'الخمان الأسود'),
    (87,  'ar', 'صمغ عربي'),
    (91,  'ar', 'نوني'),
    (124, 'ar', 'المريمية'),
    (129, 'ar', 'المر'),
    (179, 'ar', 'الفلفل الحار'),
    (187, 'ar', 'قيقب السكر'),
    (268, 'ar', 'خشب الصندل'),
    (287, 'ar', 'البردي'),

    # HI garbage/wrong entries
    (4,   'hi', 'अशोक'),
    (21,  'hi', 'लौंग'),
    (23,  'hi', 'कॉमफ्री'),
    (24,  'hi', 'क्रैनबेरी'),
    (35,  'hi', 'अलसी'),
    (40,  'hi', 'गोल्डनसील'),
    (47,  'hi', 'जमैकन डॉगवुड'),
    (61,  'hi', 'पपीता'),
    (87,  'hi', 'गोंद अरबी'),
    (94,  'hi', 'हरमल'),
    (96,  'hi', 'ट्रिप्टेरिजियम'),
    (685, 'hi', 'झूठा भांग'),
]

conn = sqlite3.connect(DB_PATH)
conn.execute('PRAGMA encoding = "UTF-8"')
cur = conn.cursor()

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
conn.close()
