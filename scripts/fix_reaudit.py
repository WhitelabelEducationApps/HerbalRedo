# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import sqlite3
from pathlib import Path

DB = Path(r"C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db")
conn = sqlite3.connect(DB)
conn.text_factory = lambda b: b.decode("utf-8", errors="replace")

# ── Section 1: paintingname fixes (Latin names → English) ─────────────────────
name_fixes = [
    # Latin paintingnames not yet converted
    (4,   "Ashoka Tree"),
    (5,   "Garden Spurge"),
    (7,   "Common Barberry"),
    (9,   "Bilberry"),        # "Billberry" typo fix
    (14,  "Cnicus benedictus"),
    (22,  "Coffee Senna"),
    (101, "Hoja Santa"),
    (102, "Dog Rose"),
    (106, "Birthwort (Aristolochia)"),
    (110, "Blackberry"),      # "BlackBerry" → "Blackberry"
    (116, "Sweet Violet"),
    (122, "Rue (Ruta graveolens)"),
]
for row_id, new_name in name_fixes:
    conn.execute("UPDATE museum_item SET paintingname=? WHERE id=?", (new_name, row_id))
    print(f"  {row_id:3d}  paintingname  = {new_name}")

# ── Section 2: field-level fixes ──────────────────────────────────────────────
fixes = [
    # --- Batches 1–6 (IDs 0–141) ---
    # ID 28 Elderberry — AR "البزيلاء السوداء" = black peas (wrong!)
    (28,  "paintingname_ar", "الخمان"),
    # ID 29 Chinese Ephedra — JA garbled, has "center for research" text
    (29,  "paintingname_ja", "チュウゴクマオウ"),
    # ID 55 Lotus — DE "Hornklee" = bird's-foot trefoil (wrong plant!)
    (55,  "paintingname_de", "Heilige Lotosblume"),
    # ID 60 Oregano — JA "ダンゴムシ" = pill bug appended (wrong!)
    (60,  "paintingname_ja", "オレガノ"),
    # ID 106 Aristolochia — JA "タウバー川" = Tauber River (wrong!)
    (106, "paintingname_ja", "ウマノスズクサ"),
    # ID 110 Blackberry — DE "Stachel (Botanik)" = thorn/prickle (wrong!)
    (110, "paintingname_de", "Brombeere"),
    # ID 112 Hyssop — JA "ハーブの一覧" = list of herbs (wrong!)
    (112, "paintingname_ja", "ヒソップ"),
    # ID 116 Sweet Violet — AR "البرتقال العطرية" = fragrant orange (wrong!)
    (116, "paintingname_ar", "البنفسج العطري"),
    # ID 131 Marigold — catastrophically wrong translations
    (131, "paintingname_de", "Ringelblume"),
    (131, "paintingname_ru", "Ноготки лекарственные"),
    (131, "paintingname_fr", "Souci des jardins"),
    (131, "paintingname_it", "Calendula officinalis"),

    # --- Batch 7 (IDs 142–198) ---
    # ID 151 Chinese Goldthread — ZH wrong plant (orchid), JA wrong plant
    (151, "paintingname_zh", "黄连"),
    (151, "paintingname_ja", "オウレン"),
    # ID 155 Seville Orange — RU "Лимон"=lemon, JA "シトロン"=citron (wrong plants!)
    (155, "paintingname_ru", "Горький апельсин"),
    (155, "paintingname_ja", "セビリアオレンジ"),
    # ID 180 Corn Poppy — RU garbled English, ZH "罂粟"=opium poppy (wrong species!)
    (180, "paintingname_ru", "Мак полевой"),
    (180, "paintingname_zh", "虞美人"),
    # ID 181 Common Plantain — RU garbled
    (181, "paintingname_ru", "Подорожник большой"),
    # ID 182 Vervain — RO has "?" artifact, AR garbled
    (182, "paintingname_ro", "Verbina"),
    (182, "paintingname_ar", "الفربيون"),
    # ID 183 Mezereum — RO full description text
    (183, "paintingname_ro", "Tulichina"),
    # ID 187 Sugar Maple — RU "Сахарная береза"=sugar birch (береза=birch!)
    (187, "paintingname_ru", "Сахарный клён"),
    # ID 190 Mastic — ZH "乳香"=frankincense (wrong plant; frankincense is ID 200)
    (190, "paintingname_zh", "乳香树"),
    # ID 193 Asian Ginseng — RU garbled
    (193, "paintingname_ru", "Женьшень"),
    # ID 194 American Ginseng — RU garbled
    (194, "paintingname_ru", "Американский женьшень"),
    # ID 195 Birthwort — RO full description text, ZH "牛膝草"=hyssop (wrong plant!)
    (195, "paintingname_ro", "Mărul lupului"),
    (195, "paintingname_zh", "马兜铃"),
    # ID 196 Silver Birch — JA "シルバービーチ"=Silver Beach (beach≠birch!), AR/HI same
    (196, "paintingname_ja", "シラカンバ"),
    (196, "paintingname_ar", "البتولا الفضية"),
    (196, "paintingname_hi", "सिल्वर बर्च"),

    # --- Batch 8 (IDs 200–222) ---
    # ID 200 Frankincense — RU "Французский кедр"=French cedar (wrong!)
    (200, "paintingname_ru", "Ладан"),
    # ID 202 Moringa — JA "モロング" garbled
    (202, "paintingname_ja", "モリンガ"),
    # ID 204 Cinnamon — RU "Кинза"=coriander/cilantro (WRONG PLANT!)
    (204, "paintingname_ru", "Корица"),
    # ID 205 Autumn Crocus — ZH "秋郁金香"=autumn tulip (wrong!), RU garbled
    (205, "paintingname_zh", "秋水仙"),
    (205, "paintingname_ru", "Безвременник осенний"),
    # ID 206 Houseleek — RU "Домовая лилия"=house lily (lily≠leek!)
    (206, "paintingname_ru", "Молодило кровельное"),
    # ID 209 Persimmon — RU "Пассифлора"=passionflower (WRONG PLANT!)
    (209, "paintingname_ru", "Хурма"),
    # ID 214 Umckaloabo — RO has text artifact
    (214, "paintingname_ro", "Umckaloabo"),
    # ID 215 Chinese Foxglove — RU "Китайский флокс"=Chinese phlox, HI same
    (215, "paintingname_ru", "Ремания китайская"),
    (215, "paintingname_hi", "चीनी फॉक्सग्लोव"),
    # ID 216 Scaevola — IT "scabiosa"=scabious plant (wrong!)
    (216, "paintingname_it", "Scaevola"),
    # ID 217 Blackcurrant — JA "ブラックカーネル"=black kernel (wrong)
    (217, "paintingname_ja", "クロスグリ"),
    # ID 218 Witch Hazel — RU garbled, JA garbled
    (218, "paintingname_ru", "Гамамелис"),
    (218, "paintingname_ja", "ウィッチヘーゼル"),
    # ID 220 Phacelia — ZH "飞廉属"=Carduus/thistle genus (wrong!)
    (220, "paintingname_zh", "法切利亚"),
    # ID 222 Black Walnut — AR "اللوز الأسود"=black almond (اللوز=almond, not walnut!)
    (222, "paintingname_ar", "الجوز الأسود"),

    # --- Batch 9 (IDs 223–248) ---
    # ID 223 Bay Laurel — JA "ベイ・ローラー"=bay roller (roller≠laurel!), AR truncated
    (223, "paintingname_ja", "ゲッケイジュ"),
    (223, "paintingname_ar", "شجرة الغار"),
    # ID 227 Magnolia Bark — RO encoding artifact, JA garbled
    (227, "paintingname_ro", "Scoarța de magnolie (Hou Po)"),
    (227, "paintingname_ja", "コウボク"),
    # ID 236 Nutmeg — RU garbled
    (236, "paintingname_ru", "Мускатный орех"),
    # ID 242 Wood Sorrel — RU "Деревянный купидон"=wooden cupid (!), JA garbled, ZH wrong plant
    (242, "paintingname_ru", "Кислица"),
    (242, "paintingname_ja", "カタバミ"),
    (242, "paintingname_zh", "酢浆草"),
    # ID 243 Saw Palmetto — JA garbled
    (243, "paintingname_ja", "のこぎりヤシ"),
    # ID 247 Pokeroot — HI garbled
    (247, "paintingname_hi", "पोकेरूट"),

    # --- Batch 10 (IDs 250–270) ---
    # ID 258 Cowslip — DE "Küchenschelle"=Pulsatilla/pasqueflower (WRONG PLANT!)
    (258, "paintingname_de", "Schlüsselblume"),
    # ID 264 Meadowsweet — FR=marigold, IT=lotus, PT=fennel, HI=sugarcane (all wrong!)
    (264, "paintingname_fr", "Reine des prés"),
    (264, "paintingname_it", "Olmaria"),
    (264, "paintingname_pt", "Ulmária"),
    (264, "paintingname_hi", "मीडोस्वीट"),
    # ID 267 Aspen — ES "abedul"=birch (WRONG PLANT!), RU garbled
    (267, "paintingname_es", "álamo temblón"),
    (267, "paintingname_ru", "Осина"),
    # ID 269 Soapnuts — RU garbled
    (269, "paintingname_ru", "Мыльный орех"),

    # --- Batch 11 (IDs 271–290) ---
    # ID 276 Black Nightshade — RU "папоротник"=fern (wrong!)
    (276, "paintingname_ru", "Паслён чёрный"),
    # ID 277 Bladdernut — IT "Stafisagria"=Delphinium (wrong plant!), RU garbled
    (277, "paintingname_it", "Noce soffiato"),
    (277, "paintingname_ru", "Клекачка перистая"),
    # ID 284 Linden — RO English word, ES garbled, RU garbled, PT "Tilândia"=Tillandsia (WRONG!)
    (284, "paintingname_ro", "Tei"),
    (284, "paintingname_es", "Tilo"),
    (284, "paintingname_ru", "Липа"),
    (284, "paintingname_pt", "Tília"),
    # ID 288 Slippery Elm — RU garbled
    (288, "paintingname_ru", "Вяз красный"),

    # --- Batch 12 (IDs 291–315) ---
    # ID 291 Spikenard — DE "Helenium"=sneezeweed genus (WRONG PLANT!), RO truncated
    (291, "paintingname_de", "Indische Narde"),
    (291, "paintingname_ro", "Nard"),
    # ID 303 Mango — DE has Wikidata metadata in name field
    (303, "paintingname_de", "Mango"),
    # ID 307 Khella — RO "mătăsă"=silk (wrong)
    (307, "paintingname_ro", "Khella"),
    # ID 315 Japanese Aralia — RU mixed Cyrillic/Latin, JA wrong name
    (315, "paintingname_ru", "Фатсия японская"),
    (315, "paintingname_ja", "ヤツデ"),

    # --- Batch 13 (IDs 318–405) ---
    # ID 327 Wormwood — ES garbled, RU "арника"=Arnica (WRONG PLANT!)
    (327, "paintingname_es", "Ajenjo"),
    (327, "paintingname_ru", "Полынь горькая"),
    # ID 349 Immortelle — DE "unsterblich"=adjective "immortal" (not a plant name!)
    (349, "paintingname_de", "Strohblume"),
    # ID 357 Tansy Ragwort — RO encoding artifact
    (357, "paintingname_ro", "Crucea-pământului"),
    # ID 400 Hound's Tongue — FR "Bignonia"=wrong plant, IT "Lappa"=burdock (wrong!)
    (400, "paintingname_fr", "Cynoglosse officinale"),
    (400, "paintingname_it", "Cynoglossum officinale"),
    # ID 405 Viper's Bugloss — ES garbled, FR "Euphrasie"=eyebright (WRONG PLANT!), RU garbled
    (405, "paintingname_es", "Viborera"),
    (405, "paintingname_fr", "Vipérine commune"),
    (405, "paintingname_ru", "Синяк обыкновенный"),

    # --- Batch 14 (IDs 410–592) ---
    # ID 438 Horseradish — DE=clove, IT=mustard, RU=mustard (ALL WRONG PLANTS!)
    (438, "paintingname_de", "Meerrettich"),
    (438, "paintingname_it", "Rafano rusticano"),
    (438, "paintingname_ru", "Хрен"),
    # ID 451 Woad — FR=red cabbage, IT=lazurite mineral (WRONG!), RO=locust, HI garbled
    (451, "paintingname_fr", "Pastel des teinturiers"),
    (451, "paintingname_it", "Guado"),
    (451, "paintingname_ro", "Drobușor"),
    (451, "paintingname_hi", "वोड"),
    # ID 461 Radish — RU "репа"=turnip (WRONG PLANT!), IT "radice"=root (too generic)
    (461, "paintingname_ru", "Редька"),
    (461, "paintingname_it", "Ravanello"),
    # ID 502 Prickly Pear — RU "агава"=agave (WRONG PLANT!)
    (502, "paintingname_ru", "Опунция"),
    # ID 512 Sweetshrub — JA garbled
    (512, "paintingname_ja", "アメリカロウバイ"),
    # ID 530 Balloon Flower — FR "Plumbago"=wrong plant, IT=balloon orchid (WRONG!)
    (530, "paintingname_fr", "Ballon-fleur"),
    (530, "paintingname_it", "Platycodon"),
    # ID 551 Japanese Honeysuckle — multiple wrong plants
    (551, "paintingname_ro", "Caprifol japonez"),
    (551, "paintingname_de", "Japanisches Geißblatt"),
    (551, "paintingname_fr", "Chèvrefeuille du Japon"),
    (551, "paintingname_it", "Caprifoglio del Giappone"),
    # ID 574 Guelder Rose — all wrong (Rosa gallica, rose bush, rose, camphor rose, red willow)
    (574, "paintingname_es", "Mundillo"),
    (574, "paintingname_de", "Gemeiner Schneeball"),
    (574, "paintingname_fr", "Viorne obier"),
    (574, "paintingname_it", "Viburno opulo"),
    (574, "paintingname_ru", "Калина обыкновенная"),

    # --- Batch 15 (IDs 595–637) ---
    # ID 595 American Holly — IT full article text in name field
    (595, "paintingname_it", "Agrifoglio americano"),
    # ID 605 Sarcandra — JA garbled
    (605, "paintingname_ja", "センリョウ"),
    # ID 617 Flame Lily — AR "النرجس الناري"=fiery narcissus (wrong plant!)
    (617, "paintingname_ar", "الزنبق الناري"),
    # ID 635 Biting Stonecrop — AR "طحلب الصخور"=rock algae (wrong!)
    (635, "paintingname_ar", "الفتنة الحارة"),

    # --- Batch 16 (IDs 639–677) ---
    # ID 641 Cobweb Houseleek — JA garbled (lick instead of leek)
    (641, "paintingname_ja", "クモノスバンダイソウ"),
    # ID 657 Hinoki Cypress — HI garbled
    (657, "paintingname_hi", "हिनोकी सरू"),

    # --- Batch 17 (IDs 679–719) ---
    # ID 679 Black Bog Rush — RO encoding artifact
    (679, "paintingname_ro", "Pipirig negru de mlaștină"),
    # ID 693 Mexican Yam — RO=olives, DE=hemp nettle, HI=star (all wrong!)
    (693, "paintingname_ro", "Dioscorea mexicana"),
    (693, "paintingname_de", "Mexikanische Yamswurzel"),
    (693, "paintingname_hi", "मेक्सिकन यम"),

    # --- Batch 18 (IDs 721–761) ---
    # ID 721 Lesser Burdock — RO "Arțarul mai mic"=lesser maple (wrong!), FR=Artemisia (wrong!)
    (721, "paintingname_ro", "Brusture mic"),
    (721, "paintingname_fr", "Petite bardane"),
    # ID 725 White Sage — IT full article text (list of Artemisia species)
    (725, "paintingname_it", "Salvia bianca"),
    # ID 731 Coyote Brush — IT full article text (list of Baccharis species)
    (731, "paintingname_it", "Baccharis"),
    # ID 735 Blumea — RO "Flor"=truncated
    (735, "paintingname_ro", "Blumea"),

    # --- Batch 19 (IDs 763–805) ---
    # ID 763 Bugle — RU "Камомилл"=chamomile (WRONG PLANT!), RO encoding artifact, AR=wild mint (wrong)
    (763, "paintingname_ru", "Живучка ползучая"),
    (763, "paintingname_ro", "Vinărița (Ajuga reptans)"),
    (763, "paintingname_ar", "أجوغا"),
    # ID 793 Pennyroyal — ZH "留兰香薄荷"=spearmint (wrong species)
    (793, "paintingname_zh", "胡薄荷"),

    # --- Batch 20 (IDs 809–849) ---
    # ID 809 Master Of The Wood — RO encoding artifact
    (809, "paintingname_ro", "Vinăriță (Asperula odorata)"),
    # ID 849 Zanthorhiza — ZH "黄连木"=Pistacia chinensis (WRONG PLANT!)
    (849, "paintingname_zh", "黄根草"),

    # --- Batch 21 (IDs 851–893) ---
    # ID 857, 859, 865 — RO encoding artifacts
    (857, "paintingname_ro", "Turița mare"),
    (859, "paintingname_ro", "Turița mirositoare"),
    (865, "paintingname_ro", "Turița bastardă"),
    # ID 875 Indian Physic — RU "Роза индийская"=Indian rose (wrong!)
    (875, "paintingname_ru", "Гиллениа трёхлистная"),

    # --- Batch 22 (IDs 894–914) ---
    # ID 896 False Indigo — JA "アメリカイチゴツナギ"=American bluegrass (wrong!)
    (896, "paintingname_ja", "イタチハギ"),
    # ID 910 Variegated Coral Tree — RO encoding artifact
    (910, "paintingname_ro", "Erythrina variegata (Arbore de coral pestriț)"),

    # --- Batch 23 (IDs 917–937) ---
    # ID 923 Eastern Columbine — IT full article text, FR=Anemone (wrong plant mix)
    (923, "paintingname_it", "Aquilegia orientalis"),
    (923, "paintingname_fr", "Ancolie de l'Est"),

    # --- Batch 24 (IDs 938–959) ---
    # ID 940 Hop Tree — AR "شجرة الحشيشة"=cannabis/hashish tree (wrong!)
    (940, "paintingname_ar", "شجرة الجناح"),
    # ID 944 Northern Prickly Ash — JA "キハダ"=cork tree (wrong plant!)
    (944, "paintingname_ja", "アメリカサンショウ"),

    # --- Batch 25 (IDs 961–982) ---
    # ID 979 Wood Poppy — JA "キサントセラス"=yellowhorn tree (wrong!)
    (979, "paintingname_ja", "ウッドポピー"),
    # ID 982 Dutchman's Breeches — FR=Corydalis (wrong plant!)
    (982, "paintingname_fr", "Cœurs-de-Marie"),

    # --- Batch 26 (IDs 983–985) ---
    # ID 985 Common Fumitory — JA "ケマンソウ"=bleeding heart (wrong plant!)
    (985, "paintingname_ja", "フマリア"),
]

for row_id, col, val in fixes:
    conn.execute(f"UPDATE museum_item SET {col}=? WHERE id=?", (val, row_id))
    print(f"  {row_id:3d}  {col:<25}  = {val}")

conn.commit()
conn.close()
print(f"\nApplied {len(name_fixes)} paintingname fixes and {len(fixes)} field-level fixes.")
