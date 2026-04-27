#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix 20: Critical wrong content — garbage text, wrong-plant, wrong-language, DE Wikidata stubs, HI list-template."""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'

# (id, lang, new_description)
FIXES = [

# ── [671] Black Tree Fern — IT was ". . . . . . . ."
(671,'it','La felce arborea nera (Cyathea medullaris) è una delle felci arboree più grandi del mondo, originaria della Nuova Zelanda e delle isole del Pacifico. I Maori la chiamano māmaku e la usavano tradizionalmente come alimento e medicina — il midollo del tronco era commestibile e le fronde giovani venivano applicate su ferite e scottature. Contiene tannini e composti fenolici con proprietà antinfiammatorie e antimicrobiche. I tronchi secchi venivano usati come contenitori per la conservazione degli alimenti.'),

# ── [673] Cardboard Palm — PT was ". . . . . . . ."
(673,'pt','A Zamia furfuracea, conhecida como zamia-cartão ou palmeira-cartão, é uma cicadácea nativa do México. Apesar de ser venenosa — contém cicasina e outras toxinas — os índios mexicanos utilizavam sementes longamente cozidas como alimento após processamento especial para eliminar os compostos tóxicos. Não tem uso medicinal reconhecido na medicina moderna; toda a planta é considerada tóxica para humanos e animais domésticos. É amplamente cultivada como planta ornamental resistente.'),

# ── [691] Air Potato — HI was ". . . . . . . ."
(691,'hi','वायु आलू (Dioscorea bulbifera) एक बहुवर्षीय लता है जो उष्णकटिबंधीय अफ्रीका और एशिया में पाई जाती है। इसके हवाई कंद जो पत्तियों की धुरी में लगते हैं, कुछ किस्मों में खाद्य होते हैं परंतु अधिकांश कड़वी और विषाक्त होती हैं। आयुर्वेद में इसका उपयोग रक्तस्राव रोकने, बवासीर और श्वास रोगों में किया जाता है। इसमें डायोसजेनिन होता है जो स्टेरॉइड हार्मोन के संश्लेषण में उपयोग किया जाता है।'),

# ── [693] Mexican Yam — JA was "The user's query was to translate..."
(693,'ja','メキシカンヤム（Dioscorea mexicana）はメキシコ原産のヤマノイモ科の多年生つる性植物。根茎にジオスゲニンが豊富に含まれており、1950年代に経口避妊薬の原料となるプロゲステロン合成に利用されたことで製薬産業に革命をもたらした。メキシコの先住民族は根茎を消炎剤・リウマチ・月経不順の治療に伝統的に使用してきた。現在もステロイド系医薬品の重要な原料植物の一つである。'),

# ── [713] Himalayan Ephedra — JA was model noise
(713,'ja','ヒマラヤ麻黄（Ephedra gerardiana）はヒマラヤ山脈の高地に自生するマオウ科の低木で、標高3000〜5000mの岩場に生育する。アーユルヴェーダおよびチベット伝統医学では気管支喘息・感冒・浮腫の治療に用いられる。エフェドリンおよびシュードエフェドリンを含み気管支拡張作用を持つ。他のエフェドラ種と同様、心血管疾患を持つ患者には注意が必要である。'),

# ── [739] Pale Indian Plantain — PT was English
(739,'pt','A cacália pálida (Cacalia atriplicifolia) é uma planta herbácea perene da família Asteraceae, nativa das florestas e campos do leste da América do Norte. Raízes e folhas eram utilizadas pelos indígenas para tratar inflamações, feridas e como antisséptico. Contém lactonas sesquiterpênicas com propriedades anti-inflamatórias e antimicrobianas. É uma planta pouco estudada na fitoterapia moderna, mas valorizada na medicina tradicional dos povos nativos norte-americanos.'),

# ── [739] Pale Indian Plantain — RU was English
(739,'ru','Бледный индейский подорожник (Cacalia atriplicifolia) — многолетнее травянистое растение семейства Астровые, произрастающее в лесах и прериях восточной части Северной Америки. Коренные народы использовали корни и листья для лечения воспалений, ран и как антисептик. Содержит сесквитерпеновые лактоны и алкалоиды с противовоспалительными и антимикробными свойствами. В современной фитотерапии мало изучено, однако ценится в традиционной медицине коренных американцев.'),

# ── [739] Pale Indian Plantain — ZH was English
(739,'zh','淡印度车前草（Cacalia atriplicifolia）是菊科多年生草本植物，原产于北美洲东部的森林和草原。北美原住民传统上将根和叶用于治疗炎症、伤口愈合和感染。含有倍半萜内酯和生物碱，具有抗炎和抗菌活性。在现代植物医学中研究较少，但在北美原住民传统医学中有重要地位。'),

# ── [803] American Angelica — JA was description of a butterfly (Papilio polyxenes)!
(803,'ja','アメリカトウキ（Angelica atropurpurea）は北アメリカ東部原産のセリ科の大型二年草。紫みがかった茎と大きな白い花序が特徴。北米先住民族は根を発熱・呼吸器疾患・消化不良の治療に使用した。フラノクマリン類と精油を含み、抗菌・鎮痙作用がある。皮膚に触れた後に日光にさらされると光過敏性皮膚炎を引き起こすことがあるため注意が必要。'),

# ── [228] Marshmallow — JA was about marshmallow candy
(228,'ja','マシュマロ（Althaea officinalis）はアオイ科の多年草で、ヨーロッパ・西アジア・北アフリカ原産。根・葉・花いずれも薬用に用いられ、粘液質を豊富に含む。伝統的に咳・喉の炎症・胃炎・膀胱炎の治療に使われてきた。根の抽出物を固めてお菓子（マシュマロ）が作られたのがお菓子名の由来。現代でも喉のトローチや消化器系の炎症に対する植物療法として評価されている。'),

# ── [228] Marshmallow — ZH was about marshmallow candy
(228,'zh','药蜀葵（Althaea officinalis），又称棉花糖草，是锦葵科多年生草本植物，原产于欧洲西部和中亚。根、叶、花均含大量黏液质，具有消炎、祛痰、保护黏膜的功效。传统上用于治疗咳嗽、喉炎、胃炎和膀胱炎。其根提取物曾被制作成软糖（即今日棉花糖名称的来源）。现代植物医学中仍广泛用于呼吸道和消化道炎症的辅助治疗。'),

# ── [192] Periwinkle — ZH was about the color periwinkle
(192,'zh','长春花（Catharanthus roseus）原产于马达加斯加，是夹竹桃科多年生草本植物。含有长春碱和长春新碱，是现代医学中重要的抗癌药物原料，广泛用于白血病和淋巴瘤的治疗。传统医学中用于降血糖、降血压和治疗糖尿病。植株含有多种有毒生物碱，不宜自行使用。现为世界重要的药用植物之一，也是常见的观赏植物。'),

# ── [279] Benzoin — ZH was disambiguation page "安息香可以指："
(279,'zh','安息香（Styrax benzoin）是安息香科乔木，原产于苏门答腊及爪哇岛。树干受伤后分泌的芳香树脂用于焚香、香水和传统医药。传统医学用于治疗咳嗽、支气管炎、皮肤伤口和真菌感染。含苯甲酸、桂皮酸及安息香酸酯，具有防腐、祛痰和抗真菌活性。在中医和阿育吠陀医学中均有应用，也是重要的香水定香剂。'),

# ── [366] Touch-me-not — ZH was about a 2018 film
(366,'zh','勿碰我（Impatiens noli-tangere）又称野凤仙花，是凤仙花科一年生草本，原产于欧洲及亚洲温带。果实成熟后受触碰会弹射种子。传统上用于治疗皮肤病、风湿、痔疮和蜂蜇伤，新鲜汁液局部涂抹可减轻荨麻疹和虫咬瘙痒。含萘醌类化合物，具有抗真菌和抗炎活性。在欧洲民间医学中用于伤口愈合和皮肤炎症。'),

# ── [952] Day Jasmine — IT was biography of pop singer Jasmine Kaur!
(952,'it','Il gelsomino diurno (Cestrum diurnum) è un arbusto sempreverde della famiglia Solanaceae, originario delle Antille. Emette un intenso profumo dolce durante il giorno per attirare gli impollinatori. Contiene glucosidi cardiotonici e solanocapsina che possono essere tossici per animali e persone. Nella medicina tradizionale delle Antille era usato per trattare ulcere cutanee e infezioni. Va tenuto lontano da bambini e animali domestici per via della tossicità dei suoi frutti.'),

# ── [823] Cnidium — PT was about parsley
(823,'pt','O cnídio (Cnidium monnieri) é uma planta anual da família Apiaceae, nativa da China e da Ásia Oriental. Os frutos secos são amplamente usados na medicina tradicional chinesa para tratar disfunção erétil, infertilidade, doenças de pele e como afrodisíaco. Contém osthol e outros cumarinos com propriedades antifúngicas, anti-inflamatórias e antiparasitárias. Estudos modernos confirmam atividade antifúngica e potencial osteoprotector dos extratos de ostol.'),

# ── [913] Dyer's Greenweed — PT was about genistein compound formula
(913,'pt','A ginesta tintureira (Genista tinctoria) é um arbusto caduco da família Fabaceae, nativo da Europa e da Ásia Ocidental. Flores e brotos foram usados para tingir tecidos de amarelo e verde. Na medicina tradicional era usada como diurético, para tratar gota, reumatismo e doenças de pele. Contém genisteína, lupinina e espartina com propriedades anti-inflamatórias e estrogénicas. A genisteína tem sido estudada por possíveis propriedades anticancerígenas e osteoprotetoras.'),

# ── [83] Capsicum frutescens — JA was about chili powder spice blend
(83,'ja','タバスコペッパー（Capsicum frutescens）は中央アメリカ・南アメリカ原産のナス科多年草。タバスコソースの原料として有名。強い辛味成分カプサイシンを多量に含み、鎮痛・血行促進・新陳代謝向上の効果がある。伝統医学では消化促進・関節痛の外用療法・抗菌剤として利用されてきた。カプサイシンを含むクリームは神経障害性疼痛や変形性関節症の治療に医薬品として承認されている。'),

# ── [227] Magnolia Bark — IT was "Elenco delle Specie di Magnolia:"
(227,'it','La corteccia di magnolia (Magnolia officinalis) è un albero ornamentale e medicinale della famiglia Magnoliaceae, originario della Cina centrale. La corteccia è un rimedio fondamentale nella medicina tradizionale cinese (Hou Po) usato per trattare ansia, stress, insonnia, disturbi digestivi e asma bronchiale. Contiene magnololo e onokiolo con spiccate proprietà ansiolitiche, antinfiammatorie e antimicrobiche. Studi clinici confermano l\'effetto antistress e antidepressivo degli estratti di corteccia.'),

# ── [595] American Holly — IT was "Il genere Ilex comprende 560 specie:"
(595,'it','L\'agrifoglio americano (Ilex opaca) è un albero sempreverde della famiglia Aquifoliaceae, nativo dell\'est degli Stati Uniti. Le foglie, la corteccia e i frutti venivano usati dai nativi americani per trattare febbre, reumatismi e come emmenagogo. Contiene saponine, tannini e alcaloidi con proprietà antinfiammatorie e diuretiche. I frutti rossi sono tossici per l\'uomo ma costituiscono una fonte importante di cibo per gli uccelli in inverno.'),

# ── [683] Winter Daphne — IT was "Elenco delle specie di Daphne:"
(683,'it','Il dafne odoroso (Daphne odora) è un arbusto sempreverde della famiglia Thymelaeaceae, originario della Cina e del Giappone. I fiori rosa-purpurei emanano un intenso profumo dolce in inverno. Nella medicina tradizionale cinese la corteccia e le radici venivano usate come antinfiammatori e analgesici per dolori reumatici. Contiene dafnetossina e altri composti; il contatto con la linfa può causare irritazioni cutanee. L\'ingestione di qualsiasi parte della pianta è tossica.'),

# ── [701] Malabar Ebony — IT was "Elenco delle specie di Diospyros."
(701,'it','Il Diospyros malabarica, noto come ebano del Malabar, è un albore della famiglia Ebenaceae originario dell\'Asia meridionale. Il legno duro è molto apprezzato nella falegnameria di pregio. Nell\'Ayurveda, la corteccia, i frutti e le foglie vengono impiegati per trattare diarrea, dissenteria, malattie cutanee e come astringente. I frutti acerbi contengono elevate quantità di tannini con proprietà emostatiche e antidiarroiche.'),

# ── [725] White Sage — IT was "Elenco delle 484 specie di Artemisia:" (WRONG — plant is White Sage, not Artemisia)
(725,'it','La salvia bianca (Salvia apiana) è un arbusto aromatico sempreverde della famiglia Lamiaceae, originario della California meridionale. Le foglie bianco-argentate vengono utilizzate nella tradizione dei nativi americani per la purificazione rituale attraverso la fumigazione. Contiene cineolo, canfora e terpeni con proprietà antisettiche, antinfiammatorie e antifungine. In fitoterapia si usa per trattare infezioni delle vie respiratorie e come digestivo.'),

# ── [731] Coyote Brush — IT was "Elenco delle 431 specie di Baccharis:"
(731,'it','Il Baccharis pilularis, noto come coyote brush, è un arbusto sempreverde della famiglia Asteraceae, originario della California. È una pianta pioniera fondamentale negli ecosistemi della macchia californiana. Nella medicina tradizionale dei nativi americani le foglie venivano usate per trattare ferite, bruciature e come analgesico topico. Contiene flavonoidi e sesquiterpeni con proprietà antiossidanti e antinfiammatorie.'),

# ── [236] Nutmeg — DE was "Wikidata: Muskatnuss (Q83165)"
(236,'de','Die Muskatnuss (Myristica fragrans) ist ein immergrüner Baum aus den Molukken (Indonesien), Familie Myristicaceae. Samen und Samenmantel (Macis) sind wichtige Gewürze und Heilmittel. In der traditionellen Medizin wird sie gegen Übelkeit, Verdauungsstörungen, Schmerzen und Schlaflosigkeit eingesetzt. Enthält Myristicin, Elemicin und ätherische Öle mit krampflösenden und leicht sedierenden Eigenschaften. In hohen Dosen toxisch und halluzinogen — daher nur in kleinen Mengen verwenden.'),

# ── [303] Mango — DE was "Wikidata: Mango (Q169)"
(303,'de','Die Mango (Mangifera indica) ist ein immergrüner Obstbaum aus Südasien, Familie Anacardiaceae. Die saftigen Früchte sind reich an Vitamin C, Betacarotin und Polyphenolen. In der Ayurveda-Medizin werden Früchte, Blätter, Rinde und Samen gegen Durchfall, Fieber, Mundkrankheiten und Diabetes verwendet. Enthält Mangiferin, ein Polyphenol mit antioxidativen, antidiabetischen und entzündungshemmenden Eigenschaften. Blätter und Rinde werden auch bei Atemwegserkrankungen eingesetzt.'),

# ── [318] Areca Nut — DE was "Wikidata: Betelnuss (Q1816679)"
(318,'de','Die Betelnusspalme (Areca catechu) ist eine schlanke Palme aus Südostasien, Familie Arecaceae. Die Nüsse werden von über 600 Millionen Menschen zusammen mit Betelblättern und Branntkalk gekaut und wirken stimulierend. Enthält Arecolin, ein Alkaloid mit anregender Wirkung auf das Nervensystem. In der traditionellen Medizin gegen Würmer, Magenprobleme und als Munddesinfektionsmittel eingesetzt. Regelmäßiger Konsum erhöht das Risiko für Mundkrebs und Herzerkrankungen.'),

# ── [849] Zanthorhiza — FR was about Kaempferia (wrong genus entirely)
(849,'fr','Le zanthorhiza (Xanthorhiza simplicissima) est un petit arbuste caduc de la famille des Renonculacées, originaire de l\'est de l\'Amérique du Nord. Ses racines et tiges sont d\'un jaune vif caractéristique dû à la berbérine qu\'elles contiennent. Dans la médecine traditionnelle amérindienne, les racines étaient utilisées pour traiter la fièvre, les douleurs abdominales, les maladies hépatiques et le diabète. La berbérine possède des propriétés antibactériennes, anti-inflammatoires et hypoglycémiantes scientifiquement prouvées.'),

# ── [849] Zanthorhiza — ZH was about Kaempferia (wrong genus)
(849,'zh','黄根草（Xanthorhiza simplicissima）是毛茛科落叶小灌木，原产于北美洲东部。根茎和茎呈鲜黄色，富含小檗碱。美洲原住民传统上将根用于治疗发热、腹痛、肝病和糖尿病。小檗碱具有科学证实的抗菌、抗炎和降血糖活性。现代研究显示其提取物对多种细菌和真菌有抑制作用，也用作天然染料。'),

# ── [851] Kacip Fatimah — ZH was about Kaempferia galanga (wrong plant)
(851,'zh','卡西普法蒂玛（Labisia pumila）是紫金牛科多年生草本，原产于马来西亚和东南亚热带雨林。在马来西亚传统医学中用于调节女性激素、减轻分娩疼痛、治疗月经不规律和更年期症状。含皂苷、黄酮类和酚酸类化合物，具有雌激素样活性和抗氧化效果。马来西亚女性历来在产后饮用其叶片煎汤以恢复体力。现代研究证实其雌激素活性及骨保护效果。'),

# ── [851] Kacip Fatimah — PT was about Kaempferia genus (wrong plant)
(851,'pt','O Kacip Fatimah (Labisia pumila) é uma planta herbácea perene da família Myrsinaceae, nativa das florestas tropicais da Península Malaia. Na medicina tradicional malaia, é amplamente usada pelas mulheres para regular os hormônios femininos, aliviar as dores do parto, tratar irregularidades menstruais e sintomas da menopausa. Contém saponinas, flavonóides e ácidos fenólicos com atividade estrogênica e antioxidante. Estudos modernos confirmam sua atividade estrogênica e potencial osteoprotetor.'),

# ── [121] Silybum marianum — ES was about Lactuca serriola (wrong plant!)
(121,'es','El cardo mariano (Silybum marianum) es una planta anual o bienal de la familia Asteraceae, originaria del Mediterráneo. Sus semillas contienen silimarina, un complejo de flavonolignanos con potente actividad hepatoprotectora. Se usa ampliamente para tratar enfermedades hepáticas, cirrosis, hepatitis y daño hepático por toxinas y alcohol. La silimarina actúa como antioxidante, estimula la regeneración celular hepática e inhibe la penetración de toxinas. Es uno de los suplementos fitoterápicos más vendidos del mundo para la salud del hígado.'),

# ── [101] Piper auritum — ES was about Eriodictyon (wrong plant!)
(101,'es','El maconaxtle (Piper auritum) es una planta aromática de la familia Piperaceae, nativa de Mesoamérica. Sus grandes hojas en forma de corazón contienen safrol y eugenol con propiedades analgésicas, antiinflamatorias y antifúngicas. En la medicina tradicional mexicana se usa externamente para aliviar el dolor de cabeza, artritis y heridas. Las hojas frescas se emplean como condimento en la cocina mexicana y oaxaqueña. Extractos han demostrado actividad antibacteriana y antiprotozoaria en laboratorio.'),

# ── [101] Piper auritum — PT was about Eriodictyon (wrong plant!)
(101,'pt','O maconaxtle (Piper auritum) é uma planta aromática da família Piperaceae, nativa da América Central tropical. Suas grandes folhas em forma de coração contêm safrol e eugenol com propriedades analgésicas, anti-inflamatórias e antifúngicas. Na medicina tradicional mexicana é usado externamente para aliviar dores de cabeça, artrite e ferimentos. É amplamente usado como condimento na culinária mexicana e mesoamericana. Extratos demonstraram atividade antibacteriana e antiparasitária em estudos laboratoriais.'),

# ── HI "औषधीय पादपों की सूची इस प्रकार है-" template fixes ──

# ── [148] St. John's Wort
(148,'hi','सेंट जॉन्स वोर्ट (Hypericum perforatum) यूरोप और एशिया की एक बारहमासी जड़ी-बूटी है जो हल्के से मध्यम अवसाद, चिंता और नींद विकारों के लिए सबसे प्रसिद्ध औषधीय पौधों में से एक है। इसमें हाइपेरिसिन और हाइपरफोरिन होते हैं जो सेरोटोनिन और नोरएड्रेनालिन के स्तर को बढ़ाते हैं। नैदानिक अध्ययनों ने हल्के अवसाद में इसकी प्रभावशीलता की पुष्टि की है। बाह्य रूप से तेल के रूप में घाव और तंत्रिका दर्द में उपयोगी है। यह कई दवाओं के साथ परस्पर क्रिया करता है — विशेषकर एंटीडिप्रेसेंट के साथ।'),

# ── [150] Goldenseal
(150,'hi','गोल्डनसील (Hydrastis canadensis) उत्तरी अमेरिका की एक बारहमासी जड़ी-बूटी है जो रैनुनकुलेसी परिवार से संबंधित है। इसकी जड़ों में बेर्बेरिन और हाइड्रैस्टिन होते हैं जिनमें शक्तिशाली रोगाणुरोधी और प्रतिरक्षा-उत्तेजक गुण हैं। पारंपरिक रूप से श्वास संक्रमण, पाचन विकार, नेत्र रोग और त्वचा संक्रमण में उपयोग किया जाता है। बेर्बेरिन की जीवाणुरोधी गतिविधि वैज्ञानिक रूप से प्रमाणित है। अत्यधिक दोहन के कारण यह संकटग्रस्त प्रजाति बन गई है।'),

# ── [181] Common Plantain
(181,'hi','सामान्य केला (Plantago major) यूरोप और एशिया की एक बारहमासी जड़ी-बूटी है जो अब पूरी दुनिया में पाई जाती है। इसकी चौड़ी पत्तियाँ घाव भरने, कीड़े के काटने, एलर्जी और श्वास रोगों में बाह्य रूप से लगाई जाती हैं। पत्तियों में औकुबिन, एलेंटोइन और फ्लेवोनॉइड्स होते हैं जो सूजनरोधी और जीवाणुरोधी गुण प्रदान करते हैं। बीजों की भूसी कब्ज और कोलेस्ट्रॉल कम करने में उपयोगी है। आयुर्वेद में इसे "सर्पण" नाम से जाना जाता है।'),

# ── [272] Foxglove
(272,'hi','फॉक्सग्लोव (Digitalis purpurea) यूरोप की एक द्विवार्षिक जड़ी-बूटी है जो हृदय रोग चिकित्सा में ऐतिहासिक महत्व रखती है। इसमें डिजिटॉक्सिन और डिगॉक्सिन नामक कार्डियक ग्लाइकोसाइड होते हैं जो हृदय की गति को धीमा और शक्तिशाली बनाते हैं। डिगॉक्सिन आज भी हृदय विफलता और अलिंद फिब्रिलेशन में उपयोगी दवा है। यह पौधा अत्यंत विषाक्त है — चिकित्सीय और घातक खुराक के बीच का अंतर बहुत कम है। बिना चिकित्सक की देखरेख के कभी न लें।'),

# ── [273] Mullein
(273,'hi','लम्बाई की जड़ी (Verbascum thapsus) यूरोप और एशिया की एक द्विवार्षिक जड़ी-बूटी है। इसके मखमली पत्ते और पीले फूल पारंपरिक चिकित्सा में खांसी, ब्रोंकाइटिस, और कान के संक्रमण में उपयोग किए जाते हैं। इसमें म्यूसिलेज, सैपोनिन, फ्लेवोनॉइड्स और वर्बैस्कोसाइड होते हैं जिनमें कफ निस्सारक और सूजनरोधी गुण हैं। फूलों में भिगोया हुआ तेल कान के दर्द में लोक उपाय के रूप में प्रसिद्ध है।'),

# ── [326] Yarrow
(326,'hi','यारो (Achillea millefolium) यूरोप और एशिया की एक बारहमासी जड़ी-बूटी है जो पुरातन काल से उपयोग में है। इसका नाम ट्रोजन नायक अकिलीज़ के नाम पर पड़ा जो घावों पर इसका उपयोग करते थे। यह रक्तस्राव रोकने, बुखार कम करने, पाचन सुधारने और माहवारी को नियमित करने में उपयोगी है। इसमें अज़ुलीन, अल्कलॉइड और फ्लेवोनॉइड्स होते हैं। गर्भावस्था में इसका उपयोग वर्जित है।'),

# ── [331] Sweet Wormwood
(331,'hi','मीठा वर्मवुड (Artemisia annua) एशिया का एक वार्षिक पौधा है जिसने आधुनिक चिकित्सा में क्रांति ला दी। इसमें आर्टेमिसिनिन होता है जो मलेरिया के सबसे प्रभावी उपचारों में से एक है और जिसकी खोज के लिए Youyou Tu को 2015 में नोबेल पुरस्कार मिला। इसमें कैम्फर और टेर्पेनोइड भी होते हैं जो एंटीवायरल गुण दिखाते हैं। अफ्रीका और एशिया में मलेरिया के उपचार के लिए इसकी चाय का उपयोग किया जाता है।'),

# ── [785] White Horehound
(785,'hi','सफेद होरहाउंड (Marrubium vulgare) भूमध्यसागरीय क्षेत्र की एक बारहमासी जड़ी-बूटी है। यह खांसी, ब्रोंकाइटिस, गले की खराश और श्वास नली की सूजन के लिए सबसे पुराने ज्ञात उपचारों में से एक है। इसमें मेरुबिन और फ्लेवोनॉइड्स होते हैं जिनमें शक्तिशाली कफ निस्सारक और ब्रोंकोडाइलेटर गुण हैं। इसका उपयोग कैंडी, खांसी की दवाओं और चाय में किया जाता है। यह पाचन में भी सुधार करता है।'),

# ── [851] Kacip Fatimah — HI
(851,'hi','काचिप फातिमा (Labisia pumila) मलेशिया और दक्षिण-पूर्व एशिया के उष्णकटिबंधीय वर्षावनों की एक बारहमासी जड़ी-बूटी है। मलय पारंपरिक चिकित्सा में यह महिलाओं के हार्मोन संतुलन, प्रसव पीड़ा, माहवारी विकार और रजोनिवृत्ति के लक्षणों के लिए उपयोग की जाती है। इसमें सैपोनिन, फ्लेवोनॉइड्स और फेनोलिक एसिड होते हैं जिनमें एस्ट्रोजेनिक और एंटीऑक्सीडेंट गुण हैं। आधुनिक अध्ययनों ने इसके हड्डी-संरक्षण प्रभाव की भी पुष्टि की है।'),

]

conn = sqlite3.connect(DB_PATH)
conn.execute('PRAGMA encoding = "UTF-8"')
conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
cur = conn.cursor()

count = 0
for pid, lang, text in FIXES:
    cur.execute(f'UPDATE museum_item SET description_{lang}=? WHERE id=?', (text, pid))
    print(f'[{pid}] {lang}  ✓')
    count += 1

conn.commit()
conn.close()
print(f'\nTotal fixed: {count}')
