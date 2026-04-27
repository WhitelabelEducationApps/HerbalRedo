# DB Full Audit Progress

**Total rows:** 503 (down from 537 — 34 duplicate rows deleted)
**ID range:** 0 – 985 (many gaps)
**Audit completed:** 2026-04-25 (full re-audit pass — all 503 rows re-checked)

## Summary of work done this session

### Scripts run (in order):
1. `fix_bad_names.py` — Fixed 50 BAD_NAME paintingnames (stripped Latin from parens), deleted 17 duplicate rows, renamed 29 drawables
2. `fix_batch_0_29.py` — Fixed 18 wrong AR/HI name translations (wrong plants) for IDs 0-29
3. `fix_287.py` — Fixed Cattail image (spider photo), fixed 4 translations
4. `fix_batch_30_80.py` — Fixed IDs 30-80: wrong translations, 3 unstable image URIs, renamed 3 drawables
5. `fix_batch_81_132.py` — Fixed IDs 81-132: renamed 11 Latin plantnames to English, deleted 3 duplicates, fixed 45 wrong translations
6. `fix_batch_133_220.py` — Fixed IDs 133-220: deleted 7 duplicates, renamed Thunder God Vine, fixed 35 wrong translations
7. `fix_batch_221_295.py` — Fixed IDs 221-295: deleted 2 duplicates, fixed 38 wrong translations (incl. Wikipedia article text in name fields)
8. `fix_batch_296_390.py` — Fixed IDs 296-390: renamed Centaurea cyanus→Cornflower, deleted 2 duplicates, fixed 5 translations
9. `fix_batch_391_985.py` — Fixed IDs 391-985: deleted 3 duplicates, fixed 60+ wrong translations and article-text-in-name-fields

### HTTP→HTTPS fix:
- Fixed 46 Wikimedia URIs from http:// to https://

### Final state:
- 0 missing URIs
- 0 PDF thumbnail URIs
- 0 Latin names in paintingname (BAD_NAME pattern)
- 0 missing drawable files
- All 503 plants have images

## Description audit (2026-04-25):

### Script: `fix_descriptions.py` — 76 fixes applied

#### Celebrity/person bios replaced with correct plant descriptions:
- **ID 763 Bugle** (Ajuga reptans) — 10 langs had brass instrument article (EN/RO/DE/FR/IT/ES/RU/JA/ZH/AR fixed; PT/HI were already correct)
- **ID 809 Master Of The Wood** (Astrantia major) — ALL 12 langs had Tiger Woods bio → replaced
- **ID 855 Biddy-Biddy** (Acaena anserinifolia) — EN/DE/ES/PT/JA/ZH had Biddy Mason bio → replaced (RO/FR/IT/RU/AR/HI correct)
- **ID 900 Senna** (Senna alata) — ALL 12 langs had Ayrton Senna bio → replaced
- **ID 952 Day Jasmine** (Cestrum diurnum) — EN/DE/ES/RU/PT/JA/ZH/HI had Jasmine Sandlas bio → replaced (RO/FR/IT/AR correct)

#### Wikipedia disambiguation pages replaced:
- **ID 205** Autumn Crocus, **ID 208** Wild Yam (+DE/RO), **ID 216** Scaevola (+RO)
- **ID 221** Blue Flag (+DE/RO), **ID 277** Bladdernut (+RO), **ID 279** Benzoin (+RO)
- **ID 619** White Hellebore, **ID 677** Galingale, **ID 687** Ube (+DE)
- **ID 733** Spanish Needles (+DE/RO), **ID 767** Betony (+RO), **ID 791** Horse Mint (+DE)
- **ID 821** Cowbane (+RO), **ID 899** Golden Shower Tree (+RO)

## Re-audit (2026-04-25): `fix_reaudit.py` — 156 fixes applied

### paintingname fixes (Latin → English):
- IDs 4, 5, 7, 9, 14, 22, 101, 102, 106, 110, 116, 122 — renamed to common English names

### Critical wrong-plant translation fixes:
- **ID 55 Lotus** `de`: Hornklee (birdsfoot trefoil) → Heilige Lotosblume
- **ID 131 Marigold** `ru`: кальмар (squid!) → Ноготки; `fr`: gazania → Souci; `it`: Gardenia → Calendula
- **ID 155 Seville Orange** `ru`: Лимон (lemon!) → Горький апельсин; `ja`: シトロン (citron) → correct
- **ID 180 Corn Poppy** `ru`: Попpy (English!) → Мак полевой; `zh`: 罂粟 (opium poppy!) → 虞美人
- **ID 204 Cinnamon** `ru`: Кинза (coriander/cilantro!) → Корица
- **ID 209 Persimmon** `ru`: Пассифлора (passionflower!) → Хурма
- **ID 258 Cowslip** `de`: Küchenschelle (Pulsatilla!) → Schlüsselblume
- **ID 264 Meadowsweet** `fr`: fleur de souci (marigold!) → Reine des prés; `it`: fior di loto (lotus!) → Olmaria; `pt`: erva-doce (fennel!) → Ulmária
- **ID 267 Aspen** `es`: abedul (birch!) → álamo temblón
- **ID 276 Black Nightshade** `ru`: Чёрная ночная папоротник (fern!) → Паслён чёрный
- **ID 284 Linden** `pt`: Tilândia (Tillandsia airplant!) → Tília
- **ID 291 Spikenard** `de`: Helenium (sneezeweed!) → Indische Narde
- **ID 327 Wormwood** `ru`: арника (Arnica!) → Полынь горькая
- **ID 438 Horseradish** `de`: Gewürznelke (clove!) → Meerrettich; `it`: senape (mustard!) → Rafano; `ru`: горчица (mustard!) → Хрен
- **ID 451 Woad** `fr`: chou rouge (red cabbage!) → Pastel; `it`: Lazurite (mineral!) → Guado
- **ID 461 Radish** `ru`: репа (turnip!) → Редька
- **ID 502 Prickly Pear** `ru`: агава (agave!) → Опунция
- **ID 530 Balloon Flower** `fr`: Plumbago (wrong plant!) → Ballon-fleur; `it`: Orchidea (orchid!) → Platycodon
- **ID 551 Japanese Honeysuckle** all 4 langs had different wrong plants (lilac, snowball Viburnum, bindweed, privet) → fixed
- **ID 574 Guelder Rose** all 5 langs had various roses and red willow → fixed to Viburnum opulus names
- **IDs 595, 725, 731, 923** — "Elenco delle..." full article text in IT name fields → fixed
- **ID 763 Bugle** `ru`: Камомилл (chamomile!) → Живучка ползучая

### Wrong image URIs (require manual Wikimedia search):
- **ID 314 Siberian Ginseng** — URI is `Touch_Me_not.jpg` (Impatiens/touch-me-not plant)
- **ID 962 Winged Tobacco** — URI is `Leaf_epidermis.jpg` (microscopy image)

## What was NOT fully checked:
- Style field correctness
- Image species match (some blog-hosted images remain but plants were verified earlier)
- Remaining description quality (stubs, low-quality content in non-EN fields not systematically audited)

## Issues found patterns:
- **القرنفل** (Arabic for clove) was incorrectly assigned to many plants: Horseradish, Chicory, Saw Palmetto, Carnation, Cinnamon, Castor Bean, Chelidonium
- **النعناع** (Arabic for mint) was incorrectly assigned to: Fennel, White Horehound, Mugwort, Anise
- **ZH full Wikipedia article text** inserted in paintingname_zh field for ~20 rows
- **Identical wrong-plant AR/HI translations**: Cayenne→Lemon, Clove→Cinnamon, Cat's Claw→Blackberry, etc.
- **34 duplicate rows** (same plant, two DB entries): now all deleted
