#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix 8: style CP1252 recode, wrong descriptions/names from content audit."""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'

# ── 1. Recode style CP1252 columns ───────────────────────────────────────────
STYLE_COLS = ['style_ro','style_es','style_de','style_fr','style_it','style_pt']

def try_recode(raw_bytes):
    try:
        raw_bytes.decode('utf-8')
        return None
    except UnicodeDecodeError:
        try:
            return raw_bytes.decode('cp1252')
        except Exception:
            return raw_bytes.decode('utf-8', errors='replace')

conn_r = sqlite3.connect(DB_PATH)
conn_r.text_factory = bytes
cur_r = conn_r.cursor()
cur_r.execute(f'SELECT id, {", ".join(STYLE_COLS)} FROM museum_item ORDER BY id')
style_rows = cur_r.fetchall()
conn_r.close()

style_updates = []
for row in style_rows:
    pid = row[0]
    changes = {}
    for i, col in enumerate(STYLE_COLS):
        raw = row[i + 1]
        if raw is None: continue
        recoded = try_recode(raw)
        if recoded is not None:
            changes[col] = recoded
    if changes:
        style_updates.append((pid, changes))

conn_w = sqlite3.connect(DB_PATH)
conn_w.execute('PRAGMA encoding = "UTF-8"')
cur_w = conn_w.cursor()
for pid, changes in style_updates:
    sets = [f'{c}=?' for c in changes]
    vals = list(changes.values()) + [pid]
    cur_w.execute(f'UPDATE museum_item SET {",".join(sets)} WHERE id=?', vals)
conn_w.commit()
print(f'Style CP1252 recoded: {len(style_updates)} rows')

# ── 2. Fix ID 45 wrong content ───────────────────────────────────────────────
# Correct Horse-chestnut (Aesculus hippocastanum) descriptions
DESC_45_EN = (
    "Horse-chestnut (Aesculus hippocastanum) is a large deciduous tree native to the Balkan Peninsula, "
    "widely cultivated across Europe and temperate regions. The seeds (conkers) contain aescin, a triterpene "
    "saponin used medicinally to improve venous tone and reduce capillary permeability. Horse-chestnut seed "
    "extract (HCSE) is used to treat chronic venous insufficiency, varicose veins, leg oedema and haemorrhoids. "
    "Topical preparations are applied for bruising, sprains and phlebitis. The tree grows to 30 m, with "
    "distinctive palmate leaves and white flower spikes appearing in spring."
)
DESC_45_JA = (
    "セイヨウトチノキ（Aesculus hippocastanum）はバルカン半島原産の落葉高木で、ヨーロッパ各地に広く植栽されている。"
    "種子（トチの実）にはエスシンというトリテルペンサポニンが含まれており、静脈壁を強化し毛細血管の透過性を低下させる作用がある。"
    "馬栗種子エキスは慢性静脈不全、静脈瘤、下肢浮腫、痔の治療に使用される。"
    "外用製剤は打撲傷、捻挫、静脈炎に塗布される。高さ30メートルに達し、春には特徴的な掌状葉と白い花穂をつける。"
)
DESC_45_ZH = (
    "欧洲七叶树（Aesculus hippocastanum）原产于巴尔干半岛，是一种大型落叶乔木，广泛种植于欧洲各地。"
    "其种子（板栗）含有七叶苷（aescin），一种三萜皂苷，具有增强静脉张力和降低毛细血管通透性的作用。"
    "欧洲七叶树种子提取物（HCSE）用于治疗慢性静脉功能不全、静脉曲张、下肢水肿和痔疮。"
    "外用制剂用于治疗瘀伤、扭伤和静脉炎。树高可达30米，春季开出白色花穗，具有典型的掌状叶。"
)
DESC_45_AR = (
    "كستناء الحصان (Aesculus hippocastanum) شجرة كبيرة متساقطة الأوراق، موطنها شبه جزيرة البلقان، وتُزرع على "
    "نطاق واسع في أوروبا والمناطق المعتدلة. تحتوي البذور على مادة الإيسين (aescin)، وهي سابونين تربيني يُحسّن "
    "توتر الأوردة ويقلل نفاذية الشعيرات الدموية. يُستخدم مستخلص بذور كستناء الحصان لعلاج القصور الوريدي "
    "المزمن، دوالي الأوردة، وذمة الساقين، والبواسير. تصل الشجرة إلى 30 متراً، وتتميز بأوراقها النجمية "
    "وعناقيدها الزهرية البيضاء في فصل الربيع."
)
DESC_45_HI = (
    "घोड़े का शाहबलूत (Aesculus hippocastanum) बाल्कन प्रायद्वीप का मूल निवासी एक बड़ा पर्णपाती वृक्ष है, "
    "जो यूरोप और समशीतोष्ण क्षेत्रों में व्यापक रूप से लगाया जाता है। इसके बीजों में एस्सिन (aescin) नामक "
    "ट्राइटर्पीन सैपोनिन होता है जो शिरापरक दीवारों को मजबूत करता है। घोड़े के शाहबलूत के बीज का अर्क "
    "दीर्घकालिक शिरा अपर्याप्तता, वैरिकाज़ नसों, पैरों की सूजन और बवासीर के उपचार में उपयोग किया जाता है। "
    "यह वृक्ष 30 मीटर तक ऊँचा होता है और वसंत में सफेद फूलों के गुच्छे लगाता है।"
)

# ── 3. Fix ID 801 wrong content ──────────────────────────────────────────────
DESC_801_EN = (
    "Ammi visnaga (khella) and Ammi majus are annual or biennial herbs in the family Apiaceae, native to "
    "the Mediterranean region and western Asia. Ammi visnaga contains khellin and visnagin, compounds with "
    "antispasmodic and bronchodilatory properties. Khellin was the precursor for the development of sodium "
    "cromoglycate (used in asthma) and nifedipine (calcium channel blocker). Ammi majus contains "
    "furanocoumarins (psoralens) used in PUVA therapy for psoriasis and vitiligo. Both species have been "
    "used in traditional medicine across North Africa and the Middle East."
)
DESC_801_RO = (
    "Ammi visnaga (khella) și Ammi majus sunt plante erbacee anuale sau bienale din familia Apiaceae, "
    "originare din bazinul mediteranean și Asia de Vest. Ammi visnaga conține khellin și visnagin, compuși "
    "cu proprietăți antispasmodice și bronhodilatatoare. Khellin-ul a stat la baza dezvoltării cromoglicatului "
    "de sodiu (utilizat în astm) și nifedipinei (blocant al canalelor de calciu). Ammi majus conține "
    "furanocumarine (psoraleni) folosite în terapia PUVA pentru psoriazis și vitiligo. Ambele specii sunt "
    "folosite în medicina tradițională din Africa de Nord și Orientul Mijlociu."
)
DESC_801_DE = (
    "Ammi visnaga (Knorpelmöhre, Zahnstocherpflanze) und Ammi majus sind ein- bis zweijährige Kräuter der "
    "Familie Apiaceae, heimisch im Mittelmeerraum und Westasien. Ammi visnaga enthält Khellin und Visnagin, "
    "Verbindungen mit antispasmodischen und bronchodilatatorischen Eigenschaften. Khellin war der Vorläufer "
    "bei der Entwicklung von Natriumcromoglicat (bei Asthma) und Nifedipin (Calciumkanalblocker). Ammi majus "
    "enthält Furocumarine (Psoralene), die in der PUVA-Therapie bei Psoriasis und Vitiligo eingesetzt werden."
)
DESC_801_JA = (
    "アミ・ヴィスナガ（ケラ）およびアミ・マユスはセリ科の一・二年草で、地中海沿岸および西アジア原産。"
    "アミ・ヴィスナガにはケリンおよびヴィスナギンが含まれ、抗痙攣・気管支拡張作用を持つ。"
    "ケリンはクロモグリク酸ナトリウム（喘息治療薬）およびニフェジピン（カルシウム拮抗薬）開発の先駆となった。"
    "アミ・マユスにはフラノクマリン（ソラレン）が含まれ、乾癬および白斑のPUVA療法に用いられる。"
    "両種は北アフリカおよび中東の伝統医学で広く使われてきた。"
)
DESC_801_HI = (
    "अम्मी विस्नागा (खेला) और अम्मी माजस एपियासी परिवार की एकवर्षीय या द्विवर्षीय जड़ी-बूटियाँ हैं, "
    "जो भूमध्यसागरीय क्षेत्र और पश्चिमी एशिया की मूल निवासी हैं। अम्मी विस्नागा में खेलिन और विस्नागिन "
    "होते हैं, जिनमें ऐंठनरोधी और श्वासनली-फैलाने वाले गुण होते हैं। खेलिन से सोडियम क्रोमोग्लाइकेट "
    "(अस्थमा में उपयोगी) और निफेडिपिन (कैल्शियम चैनल ब्लॉकर) विकसित किए गए। अम्मी माजस में "
    "फ्यूरानोकुमारिन (सोरालेन) होते हैं जो सोरायसिस और विटिलिगो के PUVA उपचार में उपयोग किए जाते हैं।"
)

cur_w.execute('UPDATE museum_item SET '
    'paintingname_hi=?, '
    'description=?, description_ja=?, description_zh=?, description_ar=?, description_hi=? '
    'WHERE id=45',
    ('घोड़े का शाहबलूत', DESC_45_EN, DESC_45_JA, DESC_45_ZH, DESC_45_AR, DESC_45_HI))
print(f'ID 45 updated: {cur_w.rowcount} row(s)')

cur_w.execute('UPDATE museum_item SET '
    'paintingname_es=?, paintingname_zh=?, '
    'description=?, description_ro=?, description_de=?, description_ja=?, description_hi=? '
    'WHERE id=801',
    ('Ammi', '阿米芹',
     DESC_801_EN, DESC_801_RO, DESC_801_DE, DESC_801_JA, DESC_801_HI))
print(f'ID 801 updated: {cur_w.rowcount} row(s)')

conn_w.commit()
conn_w.close()

# ── Final verify ─────────────────────────────────────────────────────────────
print()
conn2 = sqlite3.connect(DB_PATH)
conn2.text_factory = lambda b: b.decode('utf-8', errors='replace')
cur2 = conn2.cursor()
langs = ['ro','es','de','fr','it','ru','pt','ja','zh','ar','hi']
issues = 0

print('[CP1252] Replacement chars in style cols:')
any_s = False
for lang in langs:
    cur2.execute(f'SELECT COUNT(*) FROM museum_item WHERE style_{lang} LIKE ?',('%\ufffd%',))
    c = cur2.fetchone()[0]
    if c: any_s = True; issues += c; print(f'  style_{lang}: {c}')
if not any_s: print('  None.')

print('[unicode=63] Non-Latin name/style fields:')
any_u = False
for lang in ['ja','zh','ru','ar','hi']:
    for f in ['paintingname','style']:
        col = f'{f}_{lang}'
        cur2.execute(f'SELECT COUNT(*) FROM museum_item WHERE unicode({col})=63')
        c = cur2.fetchone()[0]
        if c: any_u = True; issues += c; print(f'  {col}: {c}')
if not any_u: print('  None.')

print(f'\nTotal style/name issues: {issues}')
conn2.close()
