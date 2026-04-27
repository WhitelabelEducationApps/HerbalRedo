#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix 3: Replace Wikipedia-description name fields with proper short plant names."""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'

# Format: {id: {lang: 'correct short name'}}
# Only entries confirmed to have Wikipedia-description garbage in name fields
FIXES = {
    # --- ZH ---
    143:  {'zh': '当归属'},          # Angelica genus
    247:  {'zh': '商陆'},            # Pokeroot
    273:  {'zh': '毛蕊花'},          # Mullein
    277:  {'zh': '省沽油'},          # Bladdernut
    281:  {'zh': '柽柳'},            # Tamarisk
    307:  {'zh': '阿米芹'},          # Khella
    351:  {'zh': '土木香'},          # Elecampane
    601:  {'zh': '美登木'},          # Mayten
    677:  {'zh': '莎草'},            # Galingale
    733:  {'zh': '白花鬼针草'},      # Spanish Needles
    739:  {'zh': '淡印度车前'},      # Pale Indian Plantain (was dots)
    747:  {'zh': '山矢车菊'},        # Mountain Bluet
    749:  {'zh': '大花矢车菊'},      # Greater Knapweed
    803:  {'zh': '美洲当归'},        # American Angelica
    845:  {'zh': '姜花'},            # White Ginger Lily
    881:  {'zh': '委陵菜'},          # Tormentil
    904:  {'zh': '菽麻'},            # Sunn Hemp
    931:  {'zh': '冬菟葵'},          # Winter Aconite
    971:  {'zh': '素馨叶白英'},      # Jasmine Nightshade
    982:  {'zh': '美国荷包牡丹'},    # Dutchman's Breeches
    983:  {'zh': '野荷包牡丹'},      # Wild Bleeding Heart

    # --- ES ---
    30:   {'es': 'Eucalipto'},
    47:   {'es': 'Palo de leche'},
    66:   {'es': 'Hierba de San Juan'},
    601:  {'es': 'Maitén'},
    677:  {'es': 'Galinga'},
    693:  {'es': 'Cocolmeca'},
    747:  {'es': 'Centaurea de montaña'},
    753:  {'es': 'Cardo cundidor'},
    761:  {'es': 'Acinos'},
    771:  {'es': 'Clinopodio común'},
    775:  {'es': 'Cáñamo bastardo'},
    873:  {'es': 'Geum rivale'},
    903:  {'es': 'Espantalobos'},
    919:  {'es': 'Anémona de ruda'},
    923:  {'es': 'Aguileña roja'},
    927:  {'es': 'Clemátide recta'},
    938:  {'es': 'Evodia'},
    941:  {'es': 'Esquimia japonesa'},
    945:  {'es': 'Zanthoxylum'},
    982:  {'es': 'Calzones holandeses'},

    # --- PT ---
    52:   {'pt': 'Lavanda'},
    55:   {'pt': 'Lótus'},
    206:  {'pt': 'Sempreviva'},
    230:  {'pt': 'Melastoma'},
    232:  {'pt': 'Tinospora'},
    253:  {'pt': 'Dentelária'},
    259:  {'pt': 'Protea'},
    261:  {'pt': 'Ramno'},
    273:  {'pt': 'Verbasco'},
    275:  {'pt': 'Quássia'},
    277:  {'pt': 'Estalagem'},
    281:  {'pt': 'Tamargueira'},
    369:  {'pt': 'Bérberis'},
    609:  {'pt': 'Clethra'},
    629:  {'pt': 'Corniso vermelho'},
    631:  {'pt': 'Corniso americano'},
    641:  {'pt': 'Sempreviva-teia-de-aranha'},
    731:  {'pt': 'Baccharis'},
    757:  {'pt': 'Cardo-bento'},
    767:  {'pt': 'Betónica'},
    769:  {'pt': 'Calaminta'},
    861:  {'pt': 'Alquimila'},
    865:  {'pt': 'Aremónia'},
    873:  {'pt': 'Erva-benta'},
    875:  {'pt': 'Gillenia'},
    897:  {'pt': 'Baptísia'},
    906:  {'pt': 'Sissoo'},
    923:  {'pt': 'Aquilégia'},
    967:  {'pt': 'Escopólia'},
    983:  {'pt': 'Dicentra'},

    # --- RU (shorten verbose compound names) ---
    18:   {'ru': 'Кайенский перец'},
    34:   {'ru': 'Пижма девичья'},
    45:   {'ru': 'Конский каштан'},
    46:   {'ru': 'Хвощ полевой'},
    54:   {'ru': 'Солодка голая'},
    56:   {'ru': 'Календула лекарственная'},
    57:   {'ru': 'Алтей лекарственный'},
    69:   {'ru': 'Валериана лекарственная'},
    765:  {'ru': 'Белокудренник чёрный'},
    861:  {'ru': 'Манжетка'},
    906:  {'ru': 'Дальбергия'},

    # --- DE ---
    34:   {'de': 'Mutterkraut'},
    35:   {'de': 'Gemeiner Lein'},
    52:   {'de': 'Echter Lavendel'},
    685:  {'de': 'Scheinhanf'},
    875:  {'de': 'Gillenie'},

    # --- FR ---
    38:   {'fr': 'Ginkgo'},
    45:   {'fr': "Marronnier d'Inde"},
    52:   {'fr': 'Lavande officinale'},
    216:  {'fr': 'Scévole'},
    865:  {'fr': 'Aremone'},
    881:  {'fr': 'Potentille'},
    897:  {'fr': 'Baptisia'},
    967:  {'fr': 'Scopolia'},

    # --- IT ---
    21:   {'it': 'Garofano'},
    52:   {'it': 'Lavanda'},
    143:  {'it': 'Angelica'},
    250:  {'it': 'Pittosporo'},
    261:  {'it': 'Ranno'},
    273:  {'it': 'Verbasco'},
    275:  {'it': 'Quassia'},           # CRITICAL: had <think> tag + garbage
    279:  {'it': 'Storace del Bengiui'},
    307:  {'it': 'Visciola'},
    629:  {'it': 'Corniolo rosso'},
    653:  {'it': 'Luffa'},
    769:  {'it': 'Mentuccia'},
    803:  {'it': 'Angelica americana'},
    821:  {'it': 'Cicuta'},
    835:  {'it': 'Chionanto cinese'},
    841:  {'it': 'Zenzero rosso'},
    857:  {'it': 'Agrimonia'},
    861:  {'it': 'Erba stella'},
    873:  {'it': 'Cariofillata acquatica'},
    898:  {'it': 'Caiano'},
    952:  {'it': 'Gelsomino diurno'},  # CRITICAL: was describing a Punjabi singer!

    # --- RO ---
    60:   {'ro': 'Oregano'},
    62:   {'ro': 'Mentă piperita'},
    273:  {'ro': 'Lumânărică'},
    743:  {'ro': 'Ciulin'},
    747:  {'ro': 'Centaurea de munte'},
    749:  {'ro': 'Centaurea'},
    799:  {'ro': 'Pătrunjelul câinelui'},
    813:  {'ro': 'Torilis'},
    821:  {'ro': 'Cucută de apă'},
    871:  {'ro': 'Cerențel'},
    932:  {'ro': 'Limeta'},
}

# Merge multi-lang entries per id
merged = {}
for pid, langs in FIXES.items():
    if pid not in merged:
        merged[pid] = {}
    merged[pid].update(langs)

conn = sqlite3.connect(DB_PATH)
conn.execute('PRAGMA encoding = "UTF-8"')
cur = conn.cursor()

updated_rows = 0
updated_cells = 0
for pid, langs in sorted(merged.items()):
    sets = [f'paintingname_{lang}=?' for lang in langs]
    vals = list(langs.values()) + [pid]
    cur.execute(f'UPDATE museum_item SET {",".join(sets)} WHERE id=?', vals)
    if cur.rowcount:
        updated_rows += 1
        updated_cells += len(langs)
        print(f'  id={pid}: {list(langs.keys())}')

conn.commit()
print(f'\nRows updated: {updated_rows}, cells updated: {updated_cells}')

# Verify remaining long names
print('\nRemaining > 60 chars per lang:')
conn2 = sqlite3.connect(DB_PATH)
conn2.text_factory = lambda b: b.decode('utf-8', errors='replace')
cur2 = conn2.cursor()
for lang in ['zh','es','pt','ru','de','fr','it','ro']:
    cur2.execute(f'SELECT COUNT(*) FROM museum_item WHERE length(paintingname_{lang}) > 60')
    c = cur2.fetchone()[0]
    if c: print(f'  {lang}: {c}')

# Check for <think> tags anywhere in name fields
print('\nChecking for <think> tags in name fields...')
for lang in ['ro','es','de','fr','it','ru','pt','ja','zh','ar','hi']:
    cur2.execute(f"SELECT COUNT(*) FROM museum_item WHERE paintingname_{lang} LIKE '%<think>%'")
    c = cur2.fetchone()[0]
    if c: print(f'  paintingname_{lang}: {c} entries with <think> tag')
print('Done.')
conn2.close()
