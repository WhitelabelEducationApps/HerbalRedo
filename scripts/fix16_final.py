#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix 16: Final 8 flagged rows."""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'

conn = sqlite3.connect(DB_PATH)
conn.execute('PRAGMA encoding = "UTF-8"')
conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
cur = conn.cursor()

# [759] description_hi: strip "(Hindi):\n" prefix
cur.execute('SELECT description_hi FROM museum_item WHERE id=759')
val = cur.fetchone()[0]
if val.startswith('(Hindi):'):
    val = val[len('(Hindi):'):].lstrip('\n').strip()
    cur.execute('UPDATE museum_item SET description_hi=? WHERE id=759', (val,))
    print('[759] description_hi prefix stripped')

# [807] paintingname_ro: Telina (celery in Romanian)
cur.execute("UPDATE museum_item SET paintingname_ro='Țelina' WHERE id=807")
print('[807] paintingname_ro = Țelina')

# [833] Fingerroot description_ru
cur.execute("UPDATE museum_item SET description_ru=? WHERE id=833", (
    'Бозенбергия круглолистная (Boesenbergia rotunda) — тропическое травянистое растение семейства имбирных, родом из Юго-Восточной Азии. '
    'Корневища широко применяются в традиционной тайской, малайской и индонезийской медицине при болях в животе, '
    'воспалениях, инфекциях и как афродизиак. Содержит пандурин, кардамонин и флавоноиды с выраженным антибактериальным действием. '
    'В кулинарии используется как ароматическая приправа.',
))
print('[833] description_ru written')

# [847] Spiked Ginger Lily description_ru
cur.execute("UPDATE museum_item SET description_ru=? WHERE id=847", (
    'Хедихиум колосистый (Hedychium spicatum) — многолетнее травянистое растение семейства имбирных, произрастающее в Гималаях, '
    'Китае и Южной Азии. Корневища используются в аюрведической медицине при астме, бронхите, желудочно-кишечных расстройствах '
    'и как болеутоляющее средство. Эфирное масло обладает антибактериальными и противовоспалительными свойствами. '
    'В парфюмерии применяется как компонент восточных ароматов.',
))
print('[847] description_ru written')

# [855] Biddy-Biddy description_ru
cur.execute("UPDATE museum_item SET description_ru=? WHERE id=855", (
    'Акена гусинолистная (Acaena anserinifolia) — стелющееся многолетнее растение семейства розоцветных, '
    'распространённое в Австралии, Новой Зеландии и Южной Америке. Традиционно использовалась маори и аборигенами '
    'при кожных заболеваниях, воспалениях и как вяжущее средство. Плоды с шипами цепляются за шерсть животных, '
    'распространяя семена. Содержит дубильные вещества и флавоноиды.',
))
print('[855] description_ru written')

# [865] Bastard Agrimony description_ru
cur.execute("UPDATE museum_item SET description_ru=? WHERE id=865", (
    'Аремония агримоновидная (Aremonia agrimonoides) — редкое многолетнее растение семейства розоцветных, '
    'произрастающее на Балканском полуострове и в Юго-Западной Азии. В народной медицине применялась при '
    'заболеваниях печени, желчного пузыря, диарее и воспалениях. Содержит дубильные вещества, флавоноиды '
    'и кумарины. По свойствам близка к репешку (Agrimonia eupatoria).',
))
print('[865] description_ru written')

# [971] Jasmine Nightshade description_ru
cur.execute("UPDATE museum_item SET description_ru=? WHERE id=971", (
    'Паслён лежачий (Solanum laxum) — вечнозелёная лиана семейства паслёновых, родом из Южной Америки. '
    'Культивируется как декоративное растение за белые цветки с жёлтыми тычинками. '
    'В народной медицине некоторых регионов применялась наружно при кожных заболеваниях. '
    'Содержит соланин и другие алкалоиды, поэтому все части растения токсичны при употреблении внутрь. '
    'Требует осторожного обращения.',
))
print('[971] description_ru written')

# [979] Wood Poppy description_ru
cur.execute("UPDATE museum_item SET description_ru=? WHERE id=979", (
    'Стилофорум двулистный (Stylophorum diphyllum) — многолетнее лесное растение семейства маковых, '
    'произрастающее на востоке Северной Америки. Оранжево-жёлтый сок корней использовался коренными народами '
    'для окрашивания тканей и как лечебное средство при кожных инфекциях, язвах и воспалениях. '
    'Содержит берберин, хелидонин и другие алкалоиды. В больших дозах токсично.',
))
print('[979] description_ru written')

conn.commit()
conn.close()
print('\nAll done.')
