#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix 5: Strip <think> tags, replace wrong descriptions, fix wrong RO content."""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'

# Fresh correct descriptions for entries with no </think> or wrong content
FRESH = {
    # FR ID 671 - Black Tree Fern
    (671, 'description_fr'): (
        "Les fougères arborescentes sont des fougères qui développent un tronc élévant leurs frondes "
        "au-dessus du sol. La fougère arborescente noire (Cyathea medullaris), connue en maori sous le "
        "nom de mamaku, est originaire de Nouvelle-Zélande et peut atteindre 20 mètres de hauteur. "
        "Son stipe et ses jeunes pousses étaient utilisés comme aliment par les Maoris. En phytothérapie "
        "traditionnelle, les extraits de cette fougère sont utilisés pour leurs propriétés anti-inflammatoires "
        "et pour traiter les affections cutanées."
    ),
    # ZH ID 671 - Black Tree Fern
    (671, 'description_zh'): (
        "树蕨是一类具有直立茎干的蕨类植物，茎干将叶片高高撑起，形如树木。黑树蕨（Cyathea medullaris）"
        "原产于新西兰，毛利语称其为mamaku，茎干可高达20米，是世界上最高大的蕨类植物之一。"
        "其茎髓和嫩叶芽在历史上被毛利人用作食物。传统医学中，其提取物具有抗炎和护肤功效，"
        "用于治疗皮肤疾病和关节疼痛。"
    ),
    # AR ID 20 - Cinchona
    (20, 'description_ar'): (
        "الكينا (Cinchona) جنس من النباتات يضم نحو 25 نوعاً من عائلة الفوية (Rubiaceae)، موطنها الأصلي "
        "غابات جبال الأنديز الاستوائية في غرب أمريكا الجنوبية. تُعدّ الكينا من أهم النباتات الطبية في "
        "التاريخ؛ إذ تُستخرج من لحاء شجرتها مادة الكينين (quinine)، وهي أول علاج فعّال للملاريا. "
        "استُخدمت الكينا في علاج الملاريا منذ القرن السابع عشر، وتُزرع حالياً بشكل رئيسي في "
        "إندونيسيا والكونغو وبوليفيا. كما يُستخدم الكينين في علاج تشنجات الساقين الليلية."
    ),
    # AR ID 107 - Juniper
    (107, 'description_ar'): (
        "العَرعَر (Juniperus) جنس من النباتات الصنوبرية في عائلة السروية (Cupressaceae)، يضم ما بين "
        "50 و67 نوعاً موزعة على نطاق واسع في نصف الكرة الشمالي. ثمار العَرعَر، المعروفة بتوت العرعر، "
        "تُستخدم في الطب التقليدي كمُدِرّ للبول ومُطهِّر للجهاز البولي، وفي علاج التهابات المفاصل. "
        "تُستخدم أيضاً في صناعة مشروب الجن وتطعيم اللحوم. زيت العرعر المُستخرج من الثمار يُستعمل "
        "خارجياً لعلاج آلام الروماتيزم والأمراض الجلدية."
    ),
    # AR ID 230 - Indian Rhododendron
    (230, 'description_ar'): (
        "ملاستوما مالاباثريكم (Melastoma malabathricum) المعروف بالرودودندرون الهندي أو السندودوك، "
        "نبات مزهر من عائلة ملاستوماتاسيا (Melastomataceae)، ينتشر في آسيا الاستوائية وأستراليا. "
        "تُستخدم أوراقه وجذوره في الطب التقليدي لعلاج الإسهال وجروح الجلد والنزيف والأمراض الجلدية. "
        "تمتلك الأوراق خصائص مضادة للميكروبات ومضادة للالتهابات. الثمار أرجوانية اللون وصالحة للأكل، "
        "وتُستخدم تقليدياً في الطب الشعبي في ماليزيا وإندونيسيا والفلبين."
    ),
    # HI ID 22 - Senna occidentalis
    (22, 'description_hi'): (
        "सेना ऑक्सिडेंटलिस एक उष्णकटिबंधीय पौधे की प्रजाति है जो दुनिया भर में पाई जाती है। "
        "इसे कॉफी सेना, कॉफीवीड या स्टिंकवीड के नाम से भी जाना जाता है। यह पौधा मूल रूप से "
        "मध्य और दक्षिण अमेरिका का है, लेकिन अब अफ्रीका, एशिया और भारत में भी व्यापक रूप से "
        "फैला हुआ है। इसके बीजों का उपयोग पारंपरिक रूप से कॉफी के विकल्प के रूप में किया जाता है। "
        "आयुर्वेद में इसे रेचक, ज्वरनाशक और त्वचा रोगों के उपचार में उपयोगी माना जाता है।"
    ),
    # HI ID 685 - False Hemp
    (685, 'description_hi'): (
        "डेटिस्का कैनाबिना, जिसे झूठा भांग (False Hemp) कहते हैं, डेटिस्कासिया परिवार का एक ऊँचा "
        "बहुवर्षीय शाकाहारी पौधा है जो 2.5 मीटर तक बढ़ता है। यह भूमध्यसागरीय क्षेत्र, एनाटोलिया, "
        "मध्य एशिया, अफगानिस्तान, पाकिस्तान और भारत के उत्तर-पश्चिमी भागों में पाया जाता है। "
        "इस पौधे से पीला रंग निकाला जाता है जिसका उपयोग वस्त्रों को रंगने में होता है। "
        "पारंपरिक चिकित्सा में इसकी जड़ों का उपयोग घाव भरने और जोड़ों के दर्द को कम करने में होता है।"
    ),
    # HI ID 687 - Ube (Purple Yam)
    (687, 'description_hi'): (
        "उबे (Dioscorea alata), जिसे बैंगनी रतालू भी कहते हैं, रतालू परिवार की एक खाद्य प्रजाति है। "
        "यह मूल रूप से दक्षिण-पूर्व एशिया का पौधा है और अब फिलीपींस, भारत, श्रीलंका तथा कैरेबियाई "
        "देशों में उगाया जाता है। इसका कंद गहरे बैंगनी रंग का होता है और इसमें एंथोसायनिन की "
        "प्रचुरता होती है, जो एंटीऑक्सीडेंट गुण प्रदान करती है। पारंपरिक चिकित्सा में इसका उपयोग "
        "पाचन सुधार, एनीमिया और उच्च रक्तचाप के उपचार में किया जाता है।"
    ),
    # HI ID 689 - Chinese Yam
    (689, 'description_hi'): (
        "चीनी रतालू (Dioscorea polystachya) आयुर्वेद और पारंपरिक चीनी चिकित्सा में अत्यंत महत्वपूर्ण "
        "औषधि है। इसे 'शान याओ' (Shan Yao) के नाम से भी जाना जाता है। यह पौधा चीन, जापान और कोरिया "
        "में उगाया जाता है। इसकी जड़ें पाचन, गुर्दे और प्रतिरक्षा प्रणाली को मजबूत बनाने के लिए "
        "उपयोग की जाती हैं। इसके कंद में डायोस्जेनिन पाया जाता है जो हार्मोन संबंधी समस्याओं में "
        "उपयोगी है। चीनी चिकित्सा में इसे 'प्लीहा और फेफड़ों को पोषण देने वाला' माना जाता है।"
    ),
    # RO ID 631 - Red-osier Dogwood (was village description)
    (631, 'description_ro'): (
        "Cornul roșu (Cornus stolonifera sau Cornus sericea) este un arbust foios originar din America "
        "de Nord, cunoscut pentru ramurile sale roșii strălucitoare, mai ales iarna. Fructele sale mici, "
        "albe sau albăstrui, sunt consumate de păsări. Scoarța și frunzele au fost folosite în medicina "
        "tradițională a populațiilor indigene nord-americane pentru tratarea febrei, durerilor de cap și "
        "afecțiunilor cutanate. Are proprietăți astringente și antiinflamatoare."
    ),
    # RO ID 677 - Galingale (was river description)
    (677, 'description_ro'): (
        "Galinga (Cyperus longus) este o plantă erbacee perenă din familia Cyperaceae, răspândită în "
        "Europa de Sud, Africa de Nord și Asia. Rizomul său aromatic a fost folosit încă din Antichitate "
        "ca condiment și în medicină. Are proprietăți diuretice, stomahice și stimulatoare ale digestiei. "
        "În medicina tradițională, rizomul este utilizat pentru tratarea tulburărilor digestive, a greților "
        "și a infecțiilor urinare. Planta crește de obicei în zone umede, lângă râuri și lacuri."
    ),
    # RO ID 823 - Cnidium (was parsley description)
    (823, 'description_ro'): (
        "Cnidium monnieri este o plantă anuală din familia Apiaceae (Umbeliferae), originară din China "
        "și Asia de Est. Fructele sale conțin osthol, un compus cu proprietăți antifungice, antiparazitare "
        "și afrodiziace. În medicina tradițională chineză, fructele de cnidium sunt utilizate pentru "
        "tratarea afecțiunilor cutanate, a mâncărimilor, a impotentei și a infertilității feminine. "
        "Osthol are și proprietăți antiinflamatoare și poate îmbunătăți densitatea osoasă."
    ),
}

# HI entries with valid content after </think> — just strip the think block
STRIP_THINK_HI = [0, 2, 3, 4, 5]

conn = sqlite3.connect(DB_PATH)
conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
conn.execute('PRAGMA encoding = "UTF-8"')
cur = conn.cursor()

updated = 0

# Strip <think> blocks for HI descriptions
for pid in STRIP_THINK_HI:
    cur.execute('SELECT description_hi FROM museum_item WHERE id=?', (pid,))
    val = cur.fetchone()[0] or ''
    end = val.find('</think>')
    if end != -1:
        cleaned = val[end + 8:].strip()
        cur.execute('UPDATE museum_item SET description_hi=? WHERE id=?', (cleaned, pid))
        print(f'  Stripped <think> from description_hi id={pid}')
        updated += 1

# Apply fresh content
for (pid, col), text in FRESH.items():
    cur.execute(f'UPDATE museum_item SET {col}=? WHERE id=?', (text, pid))
    if cur.rowcount:
        print(f'  Fixed {col} id={pid}')
        updated += 1

conn.commit()
print(f'\nTotal updates: {updated}')

# Final verification
print('\n=== Final checks ===')
conn2 = sqlite3.connect(DB_PATH)
conn2.text_factory = lambda b: b.decode('utf-8', errors='replace')
cur2 = conn2.cursor()

# think tags
print('Description <think> tags:')
found = False
for lang in ['','_ro','_es','_de','_fr','_it','_ru','_pt','_ja','_zh','_ar','_hi']:
    col = f'description{lang}'
    cur2.execute(f"SELECT COUNT(*) FROM museum_item WHERE {col} LIKE '%<think>%'")
    c = cur2.fetchone()[0]
    if c:
        found = True
        print(f'  {col}: {c}')
if not found:
    print('  None.')

# CP1252 in name fields
print('Name field replacement chars:')
found2 = False
for lang in ['ro','es','de','fr','it','pt']:
    cur2.execute(f"SELECT COUNT(*) FROM museum_item WHERE paintingname_{lang} LIKE ?", ('%\ufffd%',))
    c = cur2.fetchone()[0]
    if c:
        found2 = True
        print(f'  paintingname_{lang}: {c}')
if not found2:
    print('  None.')

# Long names
print('Name fields > 60 chars:')
found3 = False
for lang in ['zh','es','pt','ru','de','fr','it','ro']:
    cur2.execute(f'SELECT COUNT(*) FROM museum_item WHERE length(paintingname_{lang}) > 60')
    c = cur2.fetchone()[0]
    if c:
        found3 = True
        print(f'  {lang}: {c}')
if not found3:
    print('  None.')

conn2.close()
