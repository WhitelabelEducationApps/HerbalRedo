#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix 17: Romanian Phase 1 — wrong language, wrong content, ? diacritics, genus stubs, short stubs, name fixes."""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'

# ── NAME FIXES ──────────────────────────────────────────────────────────────
NAME_FIXES = {
    17:  'Gheara pisicii',          # was "Ardei chilli" — completely wrong
    98:  'Curcumă',                 # was "Turmeric"
    143: 'Angelică',               # was "Angelica" — missing diacritic
    235: 'Banană',                  # was "Banana" — missing diacritic
}

# ── DESCRIPTION FIXES ────────────────────────────────────────────────────────
DESC_FIXES = {

# ── Wrong language: Spanish ──
70: ('White willow (Salix alba)',
'Salcia albă (Salix alba) este un arbore foios cu creștere rapidă din familia Salicaceae, originar din Europa centrală și Asia. '
'Scoarța sa conține salicină, precursorul chimic al aspirinei, și a fost folosită timp de milenii pentru combaterea febrei și a durerilor. '
'Ceaiurile și extractele din scoarță de salcie albă sunt utilizate în tratamentul reumatismului, artritei și migrenelor. '
'Prezintă proprietăți antiinflamatoare, analgezice și antipiretice demonstrate științific. '
'Arborele crește de obicei în zonele umede, pe malurile râurilor și lacurilor din Europa și Asia.'),

# ── Wrong language: English ──
94: ('Syrian Rue',
'Peganul (Peganum harmala), cunoscut și ca ruta sălbatică sau harmală, este o plantă perenă din familia Nitrariaceae, originară din stepele Asiei Centrale și Mediterana. '
'Semințele conțin harmalină și harminul, alcaloizi cu proprietăți halucinogene și antidepresive. '
'În medicina tradițională a Orientului Mijlociu și Asiei Centrale, semințele sunt folosite ca fumigant ritual, antiparazitic și antiinflamator. '
'Planta este considerată sacră în tradiția zoroastriană și islamică. '
'Datorită conținutului ridicat de alcaloizi beta-carbolinici, utilizarea sa necesită precauție.'),

# ── Wrong language: English + markdown ──
687: ('Ube',
'Ignamele violet (Dioscorea alata), numită și „ube" în Filipine, este o plantă agățătoare perenă din familia Dioscoreaceae, originară din Asia de Sud-Est. '
'Tuberculii de culoare violet-intens sunt bogați în antocianine cu puternice proprietăți antioxidante. '
'În medicina tradițională asiatică, tuberculii sunt folosiți pentru îmbunătățirea circulației, reducerea inflamației și reglarea glicemiei. '
'Este o plantă alimentară importantă în Filipine, Japonia și alte țări din Pacific. '
'Conține diosgenină, utilizată ca precursor în sinteza hormonilor steroizi.'),

689: ('Chinese Yam',
'Ignamea chinezească (Dioscorea polystachya, sin. D. batatas) este o liana perenă din familia Dioscoreaceae, cultivată în Asia de Est. '
'Tuberculii alungiti, cunoscuți în China ca „shān yào", sunt o plantă medicinală de bază în medicina tradițională chineză. '
'Sunt utilizați pentru tonifierea splinei, stomacului și rinichilor, pentru tratarea diareei cronice și a tusei. '
'Conțin mucilaj, diosgenină și alantoină cu proprietăți antiinflamatoare și regeneratoare. '
'În Japonia, tuberculul ras crud (nagaimo) este un aliment funcțional apreciat pentru beneficiile digestive.'),

# ── Completely wrong content ──
592: ('English Holly',
'Ilex sau laurul-ghimpos (Ilex aquifolium) este un arbust sau arbore mic din familia Aquifoliaceae, răspândit în Europa de Vest și sudul Europei. '
'Frunzele lucioase, cu margini dințate și ascuțite, și fructele roșii sunt caracteristice. '
'În medicina populară europeană, frunzele erau folosite pentru febră, reumatism și ca diuretic. '
'Conțin ilexantă, taninuri și saponine. Fructele sunt toxice pentru om, dar sunt o sursă importantă de hrană pentru păsări iarna. '
'Este un simbol tradițional al Crăciunului în cultura europeană.'),

910: ('Variegated Coral Tree',
'Arborele de coral pestri (Erythrina variegata) este un arbore tropical ornamental din familia Fabaceae, originar din Asia de Sud-Est și insulele Pacificului. '
'Se remarcă prin flori tubulare roșu-stacojiu și frunze cu pete galbene-verzi. '
'În medicina tradițională asiatică, scoarța și frunzele sunt folosite ca sedativ, miorelaxant și antiinflamator. '
'Conține eritralina și alți alcaloizi cu efecte calmante asupra sistemului nervos. '
'Lemnul ușor este utilizat pentru confecționarea de plute și articole artizanale în Indonezia și Filipine.'),

# ── ? substituting diacritics → rewrite clean ──
769: ('Calamint',
'Calamintha (Clinopodium nepeta) este o plantă perenă aromatică din familia Lamiaceae, originară din regiunea mediteraneană. '
'Conține pulegonă, menton și uleiuri esențiale cu miros asemănător mentei. '
'Utilizată tradițional ca stimulent digestiv, expectorant și în tratamentul colicilor abdominale. '
'Ceaiul din frunze ameliorează tusea, răceala și spasmele gastrice. '
'Prezintă proprietăți antimicrobiene și antispasmodice dovedite experimental.'),

773: ('Moldavian Balm',
'Mătăciunea (Dracocephalum moldavica) este o plantă anuală din familia Lamiaceae, originară din Asia Centrală și cultivată în Europa. '
'Conține citral, geraniol și uleiuri esențiale cu aromă florală intensă. '
'Utilizată tradițional ca sedativ ușor, tonic cardiac și remediu împotriva anxietății. '
'Ceaiul din frunze și flori are efect calmant și antispasmodic. '
'Este cultivată și ca plantă meliferă, mierea produsă din florile sale fiind de calitate superioară.'),

819: ('Douglas\' Waterhemlook',
'Cucuta de apă Douglas (Cicuta douglasii) este una dintre cele mai otrăvitoare plante din America de Nord, din familia Apiaceae. '
'Conține cicutoxină, o toxină care atacă sistemul nervos central, provocând convulsii severe și moarte. '
'Nu are utilizare medicinală recunoscută datorită toxicității sale extreme. '
'Poate fi confundată cu plante comestibile din aceeași familie (morcov, pătrunjel sălbatic), ceea ce a cauzat numeroase intoxicații accidentale. '
'Este prezentă în zone umede, pe malurile râurilor și mlaștinilor din vestul Americii de Nord.'),

825: ('Grains Of Paradise',
'Grăunțele de paradis (Aframomum melegueta) sunt fructele unei plante perene din familia Zingiberaceae, originare din Africa de Vest. '
'Conțin 6-paradol, 6-gingerol și shogaol, substanțe cu proprietăți termogenice și antiinflamatoare. '
'Utilizate tradițional ca stimulent digestiv, afrodiziac și condiment în Africa de Vest și în bucătăria medievală europeană. '
'Studiile moderne arată potențial în tratamentul obezității prin activarea țesutului adipos brun. '
'Au un gust picant-aromatic asemănător piperului, cu note citrice și florale.'),

859: ('Fragrant Agrimony',
'Turița mirositoare (Agrimonia repens) este o plantă perenă din familia Rosaceae, răspândită în Europa și Asia temperată. '
'Conține taninuri, flavonoide, uleiuri volatile și vitamina K cu proprietăți astringente și hemostatice. '
'Utilizată tradițional pentru afecțiuni digestive, diaree, inflamații ale gâtului și ca cicatrizant pentru răni. '
'Ceaiul din planta întreagă are efecte benefice asupra ficatului și vezicii biliare. '
'Seamănă cu turița comună (Agrimonia eupatoria) dar are o aromă mai intensă și proprietăți similare.'),

896: ('False Indigo',
'Indigoul fals (Amorpha fruticosa) este un arbust foios din familia Fabaceae, originar din America de Nord, naturalizat în Europa. '
'Conține rotenoide și flavonoide cu proprietăți insecticide și antiinflamatoare. '
'Triburile native americane foloseau scoarța ca tonic, antiseptic și insecticid natural. '
'În Europa a fost cultivat ca plantă ornamentală și pentru fixarea nisipurilor. '
'Extractele din frunze prezintă activitate antipruriginoasă și sunt studiate pentru aplicații dermatologice.'),

912: ('Goat\'s Rue',
'Ciumăfaia de capre (Galega officinalis) este o plantă perenă din familia Fabaceae, originară din sudul Europei și Asia Mică. '
'Conține galegină, un alcaloid care a stat la baza dezvoltării metforminei, cel mai prescris medicament antidiabetic din lume. '
'Utilizată tradițional pentru reducerea glicemiei, stimularea lactației și ca diuretic. '
'Studiile moderne confirmă efectele hipoglicemiante ale extractelor din plantă. '
'Trebuie utilizată cu prudență deoarece în cantități mari poate fi toxică pentru animale.'),

917: ('Red Baneberry',
'Christoforiana roșie (Actaea rubra) este o plantă extrem de otrăvitoare din familia Ranunculaceae, originară din America de Nord. '
'Fructele roșii strălucitoare sunt atractive vizual dar letale — câteva bace pot provoca stop cardiac. '
'Conține protoanemonină și glicozide toxice care afectează inima și sistemul nervos. '
'Mici doze de extract din rădăcini erau folosite de triburile amerindiene ca sedativ și pentru inducerea menstruației. '
'Nu se recomandă nicio utilizare domestică datorită marjei înguste dintre doza activă și cea letală.'),

957: ('Pituri',
'Pituri (Duboisia hopwoodii) este un arbust australian din familia Solanaceae, folosit tradițional de aborigeni ca stimulent prin mestecare. '
'Conține nicotină și alți alcaloizi cu efecte psihoactive — mestecat, produce euforie și reduce foamea și oboseala. '
'Triburile australiene îl foloseau în ritualuri și în expediții lungi de vânătoare. '
'Frunzele conțin și scopolamină, utilizată modern în tratamentul răului de mișcare și ca preanestezie. '
'Datorită conținutului ridicat de nicotină, utilizarea imprudentă poate provoca intoxicații grave.'),

973: ('Jerusalem Cherry',
'Cireșul de Ierusalim (Solanum pseudocapsicum) este un arbust peren din familia Solanaceae, originar din America de Sud, cultivat ornamental. '
'Fructele mici, rotunde, de culoare portocalie-roșie sunt ușor toxice pentru om și animale de companie. '
'Conțin solanocapsină și solanine care provoacă greață, vărsături și dureri abdominale. '
'Nu are utilizări medicinale recunoscute; este cultivat exclusiv ca plantă decorativă de apartament. '
'Trebuie ținut departe de copii și animale de companie datorită toxicității fructelor sale atrăgătoare.'),

981: ('Squirrel Corn',
'Porumbița veveriței (Dicentra canadensis) este o plantă perenă erbacee din familia Papaveraceae, originară din estul Americii de Nord. '
'Tuberculii albi, asemănători unor boabe de porumb, conțin bulbocapnină și protopin cu efecte miorelaxante. '
'Triburile native americane foloseau tuberculii pentru boli de piele, sifilis și ca tonic. '
'Studiile moderne arată că bulbocapnina inhibă transmisia dopaminergică și a fost investigată în cercetarea Parkinsonului. '
'Planta întreagă este considerată toxică și nu se recomandă utilizarea domestică.'),

# ── Genus-only stubs → full descriptions ──
128: ('Mugwort',
'Pelinul (Artemisia vulgaris) este o plantă perenă aromatic-amară din familia Asteraceae, răspândită în Europa, Asia și America de Nord. '
'Conține tujonă, camfor, flavonoide și sesquiterpene cu proprietăți antispasmodice, emenagoge și antibacteriene. '
'Utilizat tradițional pentru stimularea digestiei, reglarea menstruației, tratamentul anxietății și ca antiparazitar. '
'În medicina tradițională chineză este baza pentru moxibusție — arderea plantei uscate pe puncte de acupunctură. '
'Trebuie evitat în sarcină deoarece poate declanșa contracții uterine.'),

240: ('Ephedra',
'Efedra (Ephedra sinica), sau Ma-huang, este o plantă arbusticolă din familia Ephedraceae, originară din Asia Centrală și China. '
'Conține efedrină și pseudoefedrină, alcaloizi simpatominetici cu efecte bronhodilatatoare și vasoconstrictoare. '
'Utilizată în medicina tradițională chineză de peste 5000 de ani pentru tratarea astmului, bronșitei și răcelilor. '
'Efedrina izolată este utilizată în medicamente decongestionante și bronhodilatatoare. '
'Utilizarea recreativă ca stimulent este interzisă în multe țări datorită riscurilor cardiovasculare.'),

260: ('Pulsatilla',
'Pulsatila (Pulsatilla vulgaris) este o plantă perenă din familia Ranunculaceae, protejată în multe țări europene. '
'Florile sale violete cu frunzele argintii sunt caracteristice pajiștilor calcaroase. '
'Conține protoanemonină (transformată prin uscare în anemonin) cu proprietăți analgezice și antiinflamatoare. '
'Utilizată tradițional în homeopatie și fitoterapie pentru afecțiuni ginecologice, infecții oculare și nevralgii. '
'Planta proaspătă este iritantă și toxică; se utilizează numai sub formă uscată sau în preparate homeopatice.'),

296: ('Mioga Ginger',
'Ghimbirul mioga (Zingiber mioga) este o plantă perenă din familia Zingiberaceae, originară din China și cultivată în Japonia. '
'Mugurii florali și lăstarii tineri sunt consumați ca legumă și condiment în bucătăria japoneză. '
'Conține uleiuri esențiale, compuși fenolici și beta-eudesmol cu proprietăți antioxidante și antiinflamatoare. '
'În medicina tradițională japoneză, rădăcinile sunt folosite pentru tratarea răcelilor, durerilor de cap și tulburărilor digestive. '
'Spre deosebire de ghimbirul comun, rizomul său nu are gust picant pronunțat.'),

667: ('Oriental Arborvitae',
'Tuia orientală (Platycladus orientalis, sin. Thuja orientalis) este un conifer din familia Cupressaceae, originar din China de Nord și Coreea. '
'Semințele, ramurile tinere și frunzele sunt utilizate în medicina tradițională chineză sub numele de Ce Bai Ye. '
'Conțin pinene, cedrol, flavonoide și taninuri cu proprietăți hemostatice, astringente și expectorante. '
'Utilizate tradițional pentru oprirea sângerărilor, tratarea tusei cu sânge și a arsurilor. '
'Este frecvent cultivat ca arbore ornamental în parcuri și grădini din întreaga lume.'),

715: ('Major Ephedra',
'Efedra majoră (Ephedra major) este un arbust din familia Ephedraceae, răspândit în bazinul mediteranean și Asia Centrală. '
'La fel ca celelalte specii de efedra, conține efedrină și pseudoefedrină cu efecte bronhodilatatoare. '
'Utilizată tradițional în medicina populară mediteraneană pentru tratarea astmului, bronșitei și răcelilor severe. '
'Tulpinile verzi articulate sunt caracteristice genului Ephedra, frunzele fiind reduse la solzi mici. '
'Conținutul de efedrină variază semnificativ față de Ephedra sinica (Ma-huang), utilizată în medicina chineză.'),

719: ('Common Ephedra',
'Efedra comună (Ephedra distachya) este un arbust peren din familia Ephedraceae, răspândit în Europa de Sud, Asia Centrală și Siberia. '
'Este singura specie de efedra nativă în Europa, crescând pe terenuri nisipoase și pietroase. '
'Conține efedrină în concentrații mai mici decât Ephedra sinica, cu efecte bronhodilatatoare și decongestive. '
'Utilizată tradițional în medicina populară europeană pentru afecțiunile respiratorii și ca diuretic. '
'Fructele roșii cărnoase (strobili) sunt comestibile și au gust dulce-acrișor.'),

743: ('Bristly Thistle',
'Ciulinul aspru (Carduus acanthoides) este o plantă bienală din familia Asteraceae, răspândită în Europa și Asia. '
'Florile violet-purpurii, înconjurate de bractee acoperite cu spini, atrag fluturi și albine. '
'Rădăcinile și frunzele tinere erau folosite tradițional în tratamentul afecțiunilor hepatice și biliare. '
'Conține flavonoide și compuși polifenolici cu proprietăți antioxidante și hepatoprotectoare. '
'Deși mai puțin studiat decât armurarul (Silybum marianum), prezintă proprietăți similare de susținere a ficatului.'),

747: ('Mountain Bluet',
'Albăstrica de munte (Centaurea montana) este o plantă perenă din familia Asteraceae, originară din munții Europei. '
'Florile albastre-violete cu petalele marginale radiante sunt caracteristice și decorative. '
'Conține sesquiterpene lactonice, flavonoide și substanțe amare cu proprietăți diuretice și tonice. '
'Utilizată tradițional pentru tratarea febrei, afecțiunilor digestive și a bolilor oculare sub formă de colir. '
'Este frecvent cultivată în grădini ca plantă ornamentală și este valoroasă pentru polenizatori.'),

749: ('Greater Knapweed',
'Albăstrica mare (Centaurea scabiosa) este o plantă perenă robustă din familia Asteraceae, răspândită în Europa și Asia. '
'Conține cnicine și sesquiterpene lactonice cu proprietăți antiinflamatoare, antimicrobiene și tonice amare. '
'Utilizată tradițional pentru stimularea digestiei, ca tonic amar, în tratamentul febrei și al rănilor. '
'Ceaiul din florile și frunzele uscate era recomandat pentru afecțiunile renale și ca diuretic ușor. '
'Este o plantă valoroasă pentru fluturi și albine datorită florilor sale bogate în nectar.'),

777: ('Ground Ivy',
'Iederița (Glechoma hederacea) este o plantă perenă târâtoare din familia Lamiaceae, răspândită în Europa și Asia. '
'Conține acid rozmarinic, flavonoide și uleiuri volatile cu proprietăți expectorante, diuretice și antiinflamatoare. '
'Utilizată tradițional pentru bronșite, sinuzite, inflamații renale și ca purificator al sângelui primăvara. '
'Ceaiul din planta proaspătă sau uscată ameliorează tusea, curgerea nasului și inflamațiile căilor respiratorii. '
'În Evul Mediu european era folosită la fabricarea berii înainte de introducerea hameiului.'),

897: ('Wild Indigo',
'Indigoul sălbatic (Baptisia australis) este o plantă perenă viguroasă din familia Fabaceae, originară din estul Americii de Nord. '
'Florile albastre-violete și frunzele albăstrui-verzi sunt caracteristice. '
'Conține alcaloizi (citisina, N-metilcitisina) și flavonoide cu proprietăți imunostimulatoare și antibacteriene. '
'Utilizată tradițional de triburile amerindiene ca antiseptic, emetice și în tratamentul febrei tifoide. '
'Extractele sunt studiate modern pentru efectele imunomodulatoare și potențialul antiviral.'),

927: ('Upright Clematis',
'Clematita erectă (Clematis recta) este o plantă perenă erbacee din familia Ranunculaceae, originară din Europa Centrală și de Sud. '
'Florile albe mici, grupate în buchete, au un parfum plăcut și apar la începutul verii. '
'Conține anemonin și protoanemonin cu proprietăți antiinflamatoare și antireumatismale. '
'Utilizată tradițional homeopatic (Clematis recta) și în fitoterapie pentru afecțiuni reumatice, nevralgii și dureri articulare. '
'Toate părțile plantei sunt iritante și ușor toxice la consumul intern.'),

928: ('Traveler\'s Joy',
'Clematita albă (Clematis vitalba), numită și „barba lui Moș Crăciun", este o liană viguroasă din familia Ranunculaceae. '
'Crește pe garduri vii, liziere de pădure și maluri de râuri din Europa, Africa de Nord și Asia Mică. '
'Conține anemonin, protoanemonin și saponine cu efecte iritante, diuretice și antiinflamatoare. '
'Utilizată tradițional extern pentru tratamentul reumatismului și al durerilor musculare, cu precauție. '
'Fructele plumoase argintii sunt caracteristice toamnei și iernii, dând plantei un aspect decorativ.'),

953: ('Night Jasmine',
'Iasomia de noapte (Cestrum nocturnum) este un arbust din familia Solanaceae, originar din America Centrală și Caraibe. '
'Florile tubulare alb-gălbui eliberează o aromă intensă și dulce mai ales noaptea, pentru a atrage polenizatorii nocturni. '
'Conține alcaloizi steroizi și glicozide care pot provoca iritații și simptome toxice la ingestie. '
'Utilizată în aromă terapie și parfumerie; extractele florale sunt studiate pentru proprietăți sedative ușoare. '
'Trebuie cultivată în spații ventilate deoarece parfumul intens poate provoca dureri de cap la unele persoane.'),

961: ('Apple Of Peru',
'Mărul din Peru (Nicandra physalodes) este o plantă anuală din familia Solanaceae, originară din Peru. '
'Conține nicandroide și withanolide cu proprietăți insecticide — prezența sa în grădină respinge musculița albă (Trialeurodes vaporariorum). '
'Utilizată tradițional în America de Sud ca sedativ ușor, anticonvulsivant și antiparazitar. '
'Fructele, acoperite de un calix papirus caracteristic, sunt vizual atrăgătoare dar toxice. '
'Este cultivată în grădini ca plantă ornamentală și ca insecticid biologic natural.'),

965: ('Ground Cherry',
'Fizalița comestibilă (Physalis pubescens) este o plantă anuală din familia Solanaceae, originară din America tropicală. '
'Fructele dulci-acrișoare, acoperite de un înveliș papirus în formă de lampion, sunt comestibile și nutritive. '
'Conțin vitamine C și A, fiselinę și withanolide cu proprietăți antioxidante și potențial antitumoral. '
'Utilizată tradițional în America Latină pentru tratamentul febrei, infecțiilor urinare și bolilor hepatice. '
'Fructele coapte se consumă crude, în gemuri sau prăjeli; frunzele și fructele verzi sunt ușor toxice.'),

# ── Short stubs needing expansion ──
15: ('Blueberry',
'Afinul american (Vaccinium corymbosum) și speciile înrudite sunt arbuști fructiferi din familia Ericaceae, originari din America de Nord. '
'Fructele albastre-negre sunt printre cele mai bogate surse de antociani și antioxidanți din regnul vegetal. '
'Studiile clinice confirmă efectele benefice asupra sănătății cardiovasculare, cognitive și a vederii. '
'Utilizate tradițional de triburile amerindiene ca antiseptic, pentru tratarea diareei și ca tonic general. '
'Extractele sunt recomandate în prevenirea infecțiilor urinare, îmbunătățirea memoriei și protecția retinei.'),

110: ('BlackBerry',
'Murul (Rubus fruticosus) este un arbust peren spinos din familia Rosaceae, răspândit în Europa, Asia și America de Nord. '
'Fructele negre-violete sunt bogate în vitamina C, antociani, acid elagic și taninuri cu proprietăți antioxidante. '
'Frunzele și rădăcinile sunt utilizate tradițional ca astringente pentru tratamentul diareei, faringitei și inflamațiilor bucale. '
'Ceaiul din frunze ameliorează diareea, gâtul iritat și are proprietăți antiinflamatoare. '
'Fructele proaspete sau sub formă de sucuri au efecte benefice cardiovasculare și antiinflamatoare dovedite.'),

273: ('Mullein',
'Lumânărica (Verbascum thapsus) este o plantă bienală impozantă din familia Scrophulariaceae, răspândită în Europa și Asia. '
'Florile galbene și frunzele pufoase, catifelate sunt caracteristice; tulpina poate depăși 2 metri înălțime. '
'Conțin mucilaj, saponine, flavonoide și verbascozide cu proprietăți expectorante, emoliente și antiinflamatoare. '
'Utilizată tradițional pentru tratarea bronșitelor, tusei convulsive, astmului și durerilor de urechi. '
'Uleiul din flori macerate este un remediu popular pentru infecțiile de ureche la copii.'),

331: ('Sweet Wormwood',
'Peliniță dulce sau pelinul lui Artemis (Artemisia annua) este o plantă anuală din familia Asteraceae, originară din China. '
'Conține artemisinină, un compus sesquiterpenic cu activitate antimalarică remarcabilă. '
'Artemisina și derivații săi sintetici sunt medicamente esențiale de primă linie în tratamentul malariei. '
'Descoperirea activității antimalarice a artemisinei i-a adus Youyou Tu Premiul Nobel pentru Medicină în 2015. '
'Ceaiul din planta uscată este utilizat în Africa și Asia pentru tratamentul malariei necomplicatele.'),

795: ('Spearmint',
'Menta verde (Mentha spicata) este o plantă perenă aromatică din familia Lamiaceae, originară din Europa și Asia Mică. '
'Conține carvonă, limonen și dihidrocarvon, care îi conferă aroma caracteristică mai dulce decât menta obișnuită. '
'Utilizată tradițional pentru tratamentul afecțiunilor digestive, greației, balonării și durerilor de cap. '
'Uleiul esențial are proprietăți antibacteriene, antifungice și antispasmodice demonstrate experimental. '
'Este una dintre cele mai utilizate plante aromatice la nivel global — în ceaiuri, produse cosmetice și culinar.'),

799: ('Fool\'s Parsley',
'Pătrunjelul câinesc (Aethusa cynapium) este o plantă anuală toxică din familia Apiaceae, răspândită în Europa și Asia de Vest. '
'Seamănă periculos cu pătrunjelul de grădină, de unde și numele popular, dar toate părțile sale sunt otrăvitoare. '
'Conține cinahidrolă și aetusol care provoacă salivație excesivă, colici, paralizie și convulsii. '
'Nu are utilizări medicinale terapeutice; a fost studiat izolat în toxicologie. '
'Identificarea sa corectă este esențială: se distinge prin absența mirosului de pătrunjel și prin bractee reflexe.'),

813: ('Spreading Hedge Parsley',
'Torilidă (Torilis arvensis) este o plantă anuală sau bienală din familia Apiaceae, originară din Europa, Africa de Nord și Asia. '
'Fructele ovale cu spini curbați se agață de haine și blana animalelor pentru dispersie. '
'Conține flavonoide, uleiuri volatile și cumarine cu proprietăți antiinflamatoare și antimicrobiene moderate. '
'Utilizată sporadic în medicina populară ca diuretic și tonic digestiv ușor. '
'Este considerată o buruiană în culturile agricole din Europa temperată.'),

871: ('Herb Bennet',
'Cerențelul (Geum urbanum) este o plantă perenă din familia Rosaceae, răspândită în pădurile și tuferișurile din Europa și Asia. '
'Rădăcinile cărnoase au un miros plăcut de cuișoare, datorită eugenolului conținut. '
'Utilizate tradițional ca astringente, pentru tratamentul diareei, afecțiunilor bucale, febrei și ca antiseptic. '
'Conțin taninuri, eugenol, flavonoide și acid galic cu proprietăți antibacteriene demonstrate. '
'Rădăcinile uscate și măcinate erau folosite ca condiment și aromatizant pentru băuturi în Evul Mediu.'),

703: ('American Persimmon',
'Curmalul american (Diospyros virginiana) este un arbore din familia Ebenaceae, originar din estul Americii de Nord. '
'Fructele dulci-astringente devin comestibile după primele înghețuri când taninii se oxidează. '
'Conțin taninuri, betacaroten, vitamina C și licopenă cu proprietăți antioxidante. '
'Utilizat tradițional de triburile amerindiene ca astringent pentru tratamentul febrei, diareei și afecțiunilor bucale. '
'Scoarța era folosită în remedii populare pentru tratamentul sifilisului și malariei.'),

803: ('American Angelica',
'Angelica americană (Angelica atropurpurea) este o plantă bianuală impozantă din familia Apiaceae, originară din estul Americii de Nord. '
'Tulpinile purpurii și umbele mari alb-verzui o fac ușor de recunoscut în zonele umede și riverane. '
'Conțin furanocumarine, uleiuri esențiale și flavonoide cu proprietăți antifungice, antibacteriene și spasmolitice. '
'Utilizată tradițional de triburile amerindiene pentru tratarea febrei, afecțiunilor respiratorii și digestive. '
'Poate provoca fotodermatite la contact cu pielea expusă la soare datorită furanocumarinelor.'),

956: ('Jimsonweed',
'Ciumăfaia (Datura stramonium) este o plantă toxică din familia Solanaceae, răspândită pe tot globul. '
'Conține atropină, scopolamină și hiosciamină — alcaloizi tropani puternici cu efecte anticolinergice. '
'Utilizată în medicina tradițională ca analgezic, antispasmodic și în tratamentul astmului bronșic. '
'Toate părțile plantei sunt extrem de toxice; ingestia accidentală provoacă halucinații, tahicardie, comă și moarte. '
'Alcaloizii din Datura sunt utilizați în medicamente moderne pentru răul de mișcare și preanestezie.'),

122: ('Ruta graveolens',
'Ruta (Ruta graveolens) este o plantă perenă aromatică din familia Rutaceae, originară din sudul Europei și Asia Mică. '
'Poate fi cultivată ca plantă ornamentală și condimentară; crește spontan pe coaste însorite și stâncoase. '
'Conține rutină, flavonoide, furanocumarine și uleiuri volatile cu proprietăți antispasmodice și vasotone. '
'Utilizată tradițional pentru menstruații neregulate, spasme abdominale, afecțiuni reumatice și ca insecticid natural. '
'Trebuie evitată în sarcină deoarece poate declanșa avortul; contactul cu pielea poate produce fotodermatite severe.'),

290: ('Stinging Nettle',
'Urzica (Urtica dioica) este o plantă perenă erbacee din familia Urticaceae, răspândită în toată emisfera nordică. '
'Conține flavonoide, lectine, histamină, serotonină și acizi organici cu proprietăți diuretice, antiinflamatoare și hemostatice. '
'Utilizată tradițional pentru tratamentul artritei, anemiei, afecțiunilor prostatei, alergiilor și ca sursă de fier și vitamina C. '
'Studiile clinice confirmă efectele benefice ale extractelor de urzică în hiperplazia benignă de prostată. '
'Lăstarii tineri sunt comestibili — bogați în proteine, fier și vitamine — și se prepară ca spanacul.'),

}

conn = sqlite3.connect(DB_PATH)
conn.execute('PRAGMA encoding = "UTF-8"')
conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
cur = conn.cursor()

# Apply name fixes
name_count = 0
for pid, new_name in NAME_FIXES.items():
    cur.execute('SELECT paintingname_ro FROM museum_item WHERE id=?', (pid,))
    old = cur.fetchone()[0]
    cur.execute('UPDATE museum_item SET paintingname_ro=? WHERE id=?', (new_name, pid))
    print(f'[{pid}] name: {old!r} → {new_name!r}')
    name_count += 1

# Apply description fixes
desc_count = 0
for pid, (plant_name, new_desc) in DESC_FIXES.items():
    cur.execute('UPDATE museum_item SET description_ro=? WHERE id=?', (new_desc, pid))
    print(f'[{pid}] desc rewritten: {plant_name}')
    desc_count += 1

conn.commit()
conn.close()
print(f'\nNames fixed: {name_count}')
print(f'Descriptions fixed: {desc_count}')
print(f'Total: {name_count + desc_count}')
