#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix 1: Bulk update style_ar and style_hi for all 549 entries."""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'

STYLE_AR = {
    'adaptogen':        'مُكَيِّف',
    'analgesic':        'مُسَكِّن الألم',
    'anti-inflammatory':'مُضَاد الالتهاب',
    'antibacterial':    'مُضَاد للبكتيريا',
    'antifungal':       'مُضَاد للفطريات',
    'antimicrobial':    'مُضَاد للميكروبات',
    'antiparasitic':    'مُضَاد للطفيليات',
    'antispasmodic':    'مُضَاد للتشنج',
    'antiviral':        'مُضَاد للفيروسات',
    'aromatic':         'عطري',
    'cardiovascular':   'قلبي وعائي',
    'circulatory':      'دوري',
    'dermatological':   'جلدي',
    'detoxifying':      'مُزيل السموم',
    'digestive':        'هضمي',
    'diuretic':         'مُدِرّ البول',
    'gynecological':    'نسائي',
    'hepatoprotective': 'واقٍ للكبد',
    'immunomodulatory': 'مُعَدِّل المناعة',
    'laxative':         'مُلَيِّن',
    'nervine':          'مُهَدِّئ عصبي',
    'nutritive':        'مُغَذٍّ',
    'respiratory':      'تنفسي',
    'tonic':            'مُقَوٍّ',
    'toxic':            'سام',
    'wound-healing':    'مُلتئم الجروح',
}

STYLE_HI = {
    'adaptogen':        'एडाप्टोजेन',
    'analgesic':        'दर्दनाशक',
    'anti-inflammatory':'सूजनरोधी',
    'antibacterial':    'जीवाणुरोधी',
    'antifungal':       'फफूंदरोधी',
    'antimicrobial':    'रोगाणुरोधी',
    'antiparasitic':    'परजीवीरोधी',
    'antispasmodic':    'ऐंठनरोधी',
    'antiviral':        'विषाणुरोधी',
    'aromatic':         'सुगंधित',
    'cardiovascular':   'हृदय-संवहनी',
    'circulatory':      'परिसंचरण',
    'dermatological':   'त्वचा संबंधी',
    'detoxifying':      'विषहरण',
    'digestive':        'पाचक',
    'diuretic':         'मूत्रवर्धक',
    'gynecological':    'स्त्री रोग संबंधी',
    'hepatoprotective': 'यकृत-रक्षक',
    'immunomodulatory': 'प्रतिरक्षा-नियामक',
    'laxative':         'रेचक',
    'nervine':          'तंत्रिका-शामक',
    'nutritive':        'पोषक',
    'respiratory':      'श्वसन',
    'tonic':            'टॉनिक',
    'toxic':            'विषैला',
    'wound-healing':    'घाव भरने वाला',
}

conn = sqlite3.connect(DB_PATH)
conn.execute('PRAGMA encoding = "UTF-8"')
cur = conn.cursor()

total = 0
for style, ar in STYLE_AR.items():
    hi = STYLE_HI[style]
    cur.execute(
        'UPDATE museum_item SET style_ar=?, style_hi=? WHERE style=?',
        (ar, hi, style)
    )
    n = cur.rowcount
    total += n
    print(f'  {style}: {n} rows → AR={ar} | HI={hi}')

conn.commit()
print(f'\nTotal updated: {total}')

# Verify
cur.execute("SELECT COUNT(*) FROM museum_item WHERE unicode(style_ar)=63 OR style_ar IS NULL OR style_ar=''")
print(f'style_ar still bad: {cur.fetchone()[0]}')
cur.execute("SELECT COUNT(*) FROM museum_item WHERE unicode(style_hi)=63 OR style_hi IS NULL OR style_hi=''")
print(f'style_hi still bad: {cur.fetchone()[0]}')
conn.close()
