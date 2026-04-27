#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix 10: Category D (wrong content) + Category F (HI English) fresh descriptions.
   Categories C (CJK-in-AR) are handled in fix11_ar_regen.py via Ollama."""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'

# ── Category D: Wrong description content ──────────────────────────────────────
DESC_216_FR = (
    "Scaevola (famille Goodeniaceae) est un genre d'environ 130 espèces de plantes à fleurs, "
    "principalement originaires d'Australie et de la région du Pacifique. Les espèces les plus connues "
    "sont Scaevola taccada (lilas marin) et Scaevola aemula (fleur de fan australienne). Les fleurs en "
    "éventail, caractéristiques du genre, sont formées de cinq pétales fusionnés d'un côté. Scaevola "
    "taccada est une plante pionnière des littoraux tropicaux; ses feuilles et ses fruits sont utilisés "
    "dans la médecine traditionnelle polynésienne pour traiter les affections cutanées, les maux de tête "
    "et les infections oculaires. Des études phytochimiques ont mis en évidence des flavonoïdes, des "
    "alcaloïdes et des composés ayant des propriétés anti-inflammatoires et antioxydantes."
)

DESC_669_RO = (
    "Dodărul comun (Cuscuta europaea) este o plantă parazită anuală din familia Convolvulaceae, "
    "lipsită de clorofilă și incapabilă de fotosinteză. Planta se înfășoară în jurul gazdei și "
    "extrage nutrienți prin structuri specializate numite haustori. Este răspândit în Europa, Asia "
    "și Africa de Nord, parazitând urzicula, hameiul și alte plante erbacee. Dodărul a fost folosit "
    "în medicina tradițională ca purgativ și diuretic, și pentru tratamentul icterului și afecțiunilor "
    "hepatice. Conține flavonoide și alcaloizi cu proprietăți antioxidante. Toate speciile de Cuscuta "
    "sunt dăunătoare pentru agricultură, putând distruge culturi întregi de linte, lucernă și trifoi."
)

# ── Category F: HI descriptions with English text ─────────────────────────────
DESC_51_HI = (
    "क्रेटम (Mitragyna speciosa) दक्षिण-पूर्व एशिया, विशेष रूप से थाईलैंड, मलेशिया और इंडोनेशिया का "
    "एक उष्णकटिबंधीय सदाबहार वृक्ष है। इसकी पत्तियों में मित्रागाइनिन और 7-हाइड्रोक्सीमित्रागाइनिन "
    "नामक अल्कलॉइड होते हैं जो ओपिओइड रिसेप्टर्स पर कार्य करते हैं। पारंपरिक रूप से इसकी ताजी "
    "पत्तियों को चबाया जाता था या उनकी चाय बनाई जाती थी। कम मात्रा में उत्तेजक प्रभाव और अधिक "
    "मात्रा में दर्दनिवारक और शामक प्रभाव देखा गया है। दक्षिण-पूर्व एशिया में इसका उपयोग थकान "
    "दूर करने और अफीम की लत छुड़ाने में किया जाता रहा है। इसके सुरक्षा और दुरुपयोग की चिंताओं "
    "के कारण कई देशों में इसे प्रतिबंधित या नियंत्रित किया गया है।"
)

DESC_711_HI = (
    "क्राउबेरी (Empetrum nigrum) एक छोटी, सदाबहार झाड़ी है जो उत्तरी गोलार्ध के आर्कटिक और "
    "सबआर्कटिक क्षेत्रों, उच्च पर्वतीय इलाकों और मूर में पाई जाती है। इसके छोटे काले-बैंगनी "
    "जामुन खाने योग्य होते हैं और आर्कटिक के मूल निवासियों द्वारा भोजन और औषधि के रूप में "
    "उपयोग किए जाते हैं। इनुइट और अन्य आर्कटिक जनजातियाँ इसे आँखों की सूजन, स्कर्वी और "
    "पाचन समस्याओं के उपचार में प्रयोग करती हैं। जामुन में एंटीऑक्सीडेंट, एंथोसायनिन और "
    "विटामिन C प्रचुर मात्रा में होते हैं। पारंपरिक चिकित्सा में इसकी पत्तियों का उपयोग "
    "मूत्रवर्धक और ज्वरनाशक के रूप में किया जाता है।"
)

# id=899: just strip the English bracket from start
# Original: "अमलतास [English : golden shower, purging cassia, Indian laburnum, pudding-pipe tree] पीले..."
# Fix: remove "[English : ...] " part

conn = sqlite3.connect(DB_PATH)
conn.execute('PRAGMA encoding = "UTF-8"')
cur = conn.cursor()

updated = 0

# Apply fresh descriptions
for pid, col, text in [
    (216, 'description_fr', DESC_216_FR),
    (669, 'description_ro', DESC_669_RO),
    (51,  'description_hi', DESC_51_HI),
    (711, 'description_hi', DESC_711_HI),
]:
    cur.execute(f'UPDATE museum_item SET {col}=? WHERE id=?', (text, pid))
    if cur.rowcount:
        updated += 1
        print(f'  Fixed {col} id={pid}')

# id=899: strip English bracket
cur.execute('SELECT description_hi FROM museum_item WHERE id=899')
val = cur.fetchone()[0] or ''
import re
cleaned = re.sub(r'\[English\s*:.*?\]\s*', '', val).strip()
if cleaned != val:
    cur.execute('UPDATE museum_item SET description_hi=? WHERE id=899', (cleaned,))
    updated += 1
    print('  Stripped English bracket from description_hi id=899')

conn.commit()
print(f'\nTotal updates: {updated}')
conn.close()
