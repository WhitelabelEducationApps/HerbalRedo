# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import sqlite3
from pathlib import Path

DB = Path(r"C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db")
conn = sqlite3.connect(DB)
conn.text_factory = lambda b: b.decode("utf-8", errors="replace")

fixes = [
    # ============================================================
    # ID 763 BUGLE (Ajuga reptans)
    # ALL langs except PT and HI had brass instrument description
    # ============================================================
    (763, "description",
     "Bugle (Ajuga reptans) is a low-growing, creeping perennial herb in the family Lamiaceae, native to Europe, Asia, and North Africa. It spreads by stolons forming dense ground cover with oval leaves and spikes of blue-violet flowers in spring. Traditionally used as a wound-healing herb, bugle contains iridoid glycosides, tannins, and flavonoids. It has been used in folk medicine to treat bleeding, throat inflammation, and digestive complaints."),

    (763, "description_ro",
     "Bugle (Ajuga reptans) este o plantă erbacee perenă, de mică înălțime, din familia Lamiaceae, originară din Europa, Asia și Africa de Nord. Se răspândește prin stoloni, formând o acoperire densă a solului cu frunze ovale și inflorescențe de flori albastre-violet în primăvară. Tradițional folosită ca plantă medicinală pentru vindecarea rănilor, conține glicozide iridoid, tanine și flavonoide. A fost folosită în medicina populară pentru a trata sângerările, inflamația gâtului și problemele digestive."),

    (763, "description_de",
     "Bugle (Ajuga reptans) ist eine niedrigwachsende, kriechende mehrjährige Krautpflanze aus der Familie der Lamiaceae, heimisch in Europa, Asien und Nordafrika. Sie verbreitet sich durch Stolonen und bildet eine dichte Bodendecke mit ovalen Blättern und Blütenähren in Blauviolett im Frühjahr. Traditionell als Wundheilkraut verwendet, enthält Bugle Iridoidglykoside, Tannine und Flavonoide. Es wurde in der Volksmedizin zur Behandlung von Blutungen, Halsentzündungen und Verdauungsbeschwerden eingesetzt."),

    (763, "description_fr",
     "Le bugle (Ajuga reptans) est une plante herbacée vivace, rampante, de la famille des Lamiaceae, originaire d'Europe, d'Asie et du nord de l'Afrique. Il se propage par des stolons formant une couverture dense au sol avec des feuilles ovales et des épis de fleurs bleu-violettes au printemps. Traditionnellement utilisé comme plante cicatrisante, le bugle contient des glycosides iridoïdes, des tanins et des flavonoïdes. Il a été utilisé en médecine populaire pour traiter les saignements, l'inflammation de la gorge et les troubles digestifs."),

    (763, "description_it",
     "Il bugle (Ajuga reptans) è una pianta erbacea perenne, strisciante, della famiglia delle Lamiaceae, originaria d'Europa, Asia e Nord Africa. Si diffonde attraverso stoloni formando una copertura densa al suolo con foglie ovali e spighe di fiori blu-violetto in primavera. Tradizionalmente utilizzato come erba cicatrizante, il bugle contiene glicosidi iridoidi, tannini e flavonoidi. È stato utilizzato nella medicina popolare per trattare emorragie, infiammazioni della gola e disturbi digestivi."),

    (763, "description_es",
     "El bugle (Ajuga reptans) es una hierba perenne, rastrera, de la familia Lamiaceae, nativa de Europa, Asia y el norte de África. Se propaga por estolones formando una cubierta densa del suelo con hojas ovales y espigas de flores azul-violeta en primavera. Tradicionalmente utilizado como hierba cicatrizante, el bugle contiene glucósidos iridoides, taninos y flavonoides. Ha sido utilizado en la medicina popular para tratar hemorragias, inflamación de la garganta y problemas digestivos."),

    (763, "description_ru",
     "Живучка ползучая (Ajuga reptans) — низкорослое стелющееся многолетнее травянистое растение из семейства Яснотковых, родом из Европы, Азии и Северной Африки. Распространяется с помощью побегов, образуя плотный почвенный покров с овальными листьями и кистями сине-фиолетовых цветков весной. Традиционно используется как ранозаживляющая трава и содержит иридоидные гликозиды, дубильные вещества и флавоноиды. В народной медицине применялась для лечения кровотечений, воспаления горла и расстройств пищеварения."),

    (763, "description_ja",
     "ブギル（Ajuga reptans）は、ヨーロッパ、アジア、北アフリカに分布するシソ科の多年草で、低く這う性質を持ちます。ストロンが広がって、春に卵形の葉と青紫色の花穂を持つ密な地表のカバーを形成します。伝統的に傷の癒しに使われ、イリドイドグリコシド、タンニン、フラボノイドが含まれています。民間療法では出血、喉の炎症、消化器系の不快症状の治療に使用されてきました。"),

    (763, "description_zh",
     "筋骨草（Ajuga reptans）是一种低矮的匍匐多年生草本植物，属于唇形科，原产于欧洲、亚洲和北非。它通过匍匐茎扩散，形成密集的地面覆盖，春季开出卵形叶片和蓝紫色的花穗。传统上用作伤口愈合的草药，含有环烯醚萜苷、鞣质和黄酮类化合物。在民间医学中，被用于治疗出血、喉咙炎症和消化问题。"),

    (763, "description_ar",
     "البُغيل (Ajuga reptans) نبات عشبي معمر منخفض الارتفاع من عائلة الشفويات، أصيل في أوروبا وآسيا وشمال إفريقيا. ينتشر عبر سيقان زاحفة مشكلاً غطاءً كثيفاً على الأرض بأوراق بيضوية وسنابل زهور زرقاء-بنفسجية في الربيع. استُخدم تقليدياً في علاج الجروح ويحتوي على غليكوسيدات إيريدية وعفص وفلافونويدات. استخدم في الطب الشعبي لعلاج النزيف والتهاب الحلق واضطرابات الجهاز الهضمي."),

    # ============================================================
    # ID 809 MASTER OF THE WOOD (Astrantia major)
    # ALL 12 langs were Tiger Woods bio
    # ============================================================
    (809, "description",
     "Masterwort (Astrantia major) is a perennial flowering plant in the family Apiaceae, native to central and southern Europe and the Caucasus. It grows 60–90 cm tall with distinctive star-shaped flower heads surrounded by papery bracts in white or pinkish-purple. Traditionally used in European herbal medicine as a digestive tonic, carminative, and remedy for fever and respiratory ailments. The plant contains flavonoids and saponins."),

    (809, "description_ro",
     "Astranția (Astrantia major) este o plantă erbacee perenă din familia Apiaceae, originară din Europa centrală și sudică și Caucaz. Atinge 60–90 cm înălțime și are flori distinctive în formă de stea, înconjurate de bractee subțiri în alb sau roz-purpuriu. Folosită tradițional în medicina herbală europeană ca tonic digestiv, carminativ și remediu pentru febră și afecțiuni respiratorii. Planta conține flavonoide și saponine."),

    (809, "description_de",
     "Große Sterndolde (Astrantia major) ist eine mehrjährige Blütenpflanze aus der Familie der Apiaceae, heimisch in Mittel- und Südeuropa sowie dem Kaukasus. Sie wird 60–90 cm hoch und trägt charakteristische sternförmige Blütenköpfe, die von papierartigen Hochblättern in Weiß oder Rosaviolett umgeben sind. Traditionell in der europäischen Kräutermedizin als Verdauungstonikum, Karminativum und Heilmittel bei Fieber und Atemwegserkrankungen eingesetzt. Die Pflanze enthält Flavonoide und Saponine."),

    (809, "description_fr",
     "La grande astrance (Astrantia major) est une plante herbacée pérenne de la famille des Apiaceae, originaire d'Europe centrale et méridionale et du Caucase. Elle atteint 60–90 cm de hauteur avec des têtes florales en forme d'étoile entourées de bractées papier en blanc ou rose-violet. Utilisée traditionnellement en médecine herboristique européenne comme tonique digestif, carminatif et remède contre la fièvre et les maladies respiratoires. La plante contient des flavonoïdes et des saponines."),

    (809, "description_it",
     "L'astranzia maggiore (Astrantia major) è una pianta erbacea perenne della famiglia Apiaceae, originaria dell'Europa centrale e meridionale e del Caucaso. Raggiunge 60–90 cm di altezza con caratteristiche teste fiorali a forma di stella circondate da brattee cartacee bianche o rosa-violette. Tradizionalmente usata nella medicina erboristica europea come tonico digestivo, carminativo e rimedio per febbre e malattie respiratorie. La pianta contiene flavonoidi e saponine."),

    (809, "description_es",
     "La astrantia mayor (Astrantia major) es una planta herbácea perenne de la familia Apiaceae, nativa del centro y sur de Europa y el Cáucaso. Alcanza 60–90 cm de altura con cabezas florales en forma de estrella características, rodeadas de brácteas de papel en blanco o rosa-violeta. Utilizada tradicionalmente en la medicina herbal europea como tónico digestivo, carminativo y remedio para la fiebre y las enfermedades respiratorias. La planta contiene flavonoides y saponinas."),

    (809, "description_ru",
     "Звездовка крупная (Astrantia major) — многолетнее цветущее растение из семейства Зонтичных, родом из Центральной и Южной Европы и Кавказа. Вырастает до 60–90 см в высоту с характерными звездообразными соцветиями, окружёнными бумажистыми прицветниками белого или розово-фиолетового цвета. Традиционно используется в европейской народной медицине как пищеварительный тоник, ветрогонное и средство от жара и болезней дыхательных путей. Растение содержит флавоноиды и сапонины."),

    (809, "description_pt",
     "A astrantia-maior (Astrantia major) é uma planta herbácea perene da família Apiaceae, nativa da Europa central e meridional e do Cáucaso. Atinge 60–90 cm de altura com cabeças florais estreladas distintas, rodeadas por brácteas papeladas em branco ou rosa-violeta. Utilizada tradicionalmente na medicina herbal europeia como tónico digestivo, carminativo e remédio para febre e doenças respiratórias. A planta contém flavonoides e saponinas."),

    (809, "description_ja",
     "マスターワート（Astrantia major）は、セリ科の多年生草本植物で、中央・南ヨーロッパおよびコーカサス地方が原産です。高さ60〜90cmに育ち、白またはピンク紫色の紙状の苞に囲まれた特徴的な星形の花序を持ちます。ヨーロッパの伝統薬草医学において消化促進剤、ガス排出剤、発熱や呼吸器疾患の治療薬として利用されてきました。フラボノイドとサポニンを含んでいます。"),

    (809, "description_zh",
     "大星芹（Astrantia major）是一种伞形科多年生草本植物，原产于中欧、南欧和高加索地区。植株高60–90厘米，具有独特的星形花序，被白色或粉紫色的纸状苞片包围。在欧洲传统草药医学中用作消化促进剂、排气剂，以及治疗发热和呼吸系统疾病的药物。该植物含有黄酮类化合物和皂苷。"),

    (809, "description_ar",
     "أسترانتيا الكبيرة (Astrantia major) نبات معمر مزهر من عائلة الخيمية، أصيل في وسط وجنوب أوروبا والقوقاز. يصل ارتفاعه إلى 60–90 سم وتتميز أزهاره بشكل نجمي محاطة بأوراق قنابية ورقية بيضاء أو وردية-بنفسجية. استُخدم تقليدياً في الطب العشبي الأوروبي كمقوٍّ للجهاز الهضمي ومطرِّد للغازات وعلاجاً للحمى وأمراض الجهاز التنفسي. يحتوي النبات على فلافونويدات وصابونينات."),

    (809, "description_hi",
     "मास्टरवर्ट (Astrantia major) एक बहुवर्षीय फूलदार पौधा है जो अपियासी कुल में आता है और मध्य तथा दक्षिणी यूरोप व काकेशस क्षेत्र में पाया जाता है। यह 60–90 सेमी ऊंचा होता है और सफेद या गुलाबी-बैंगनी रंग के कागजी ब्रैक्ट से घिरे विशिष्ट तारे के आकार के फूल होते हैं। यूरोपीय हर्बल चिकित्सा में इसे पाचक टॉनिक, वायुनाशक और बुखार व श्वास रोगों के उपचार के रूप में उपयोग किया जाता है। इसमें फ्लेवोनॉइड और सैपोनिन पाए जाते हैं।"),

    # ============================================================
    # ID 855 BIDDY-BIDDY (Acaena anserinifolia)
    # EN, DE, ES, PT, JA, ZH had Biddy Mason bio; RO/FR/IT/RU/AR/HI correct
    # ============================================================
    (855, "description",
     "Biddy-biddy (Acaena anserinifolia) is a low-growing, mat-forming perennial shrub in the family Rosaceae, native to New Zealand and Australia. Its leaves were traditionally used by Māori people as a tea for stomach complaints, and the plant has astringent properties due to its tannin content. The plant's burred fruits attach to wool and clothing, making it a familiar sight in pastures and open areas. It has been used in traditional medicine for skin conditions and inflammation."),

    (855, "description_de",
     "Biddy-biddy (Acaena anserinifolia) ist ein niedrigwachsender, mattenbildender Strauch aus der Familie der Rosaceae, heimisch in Neuseeland und Australien. Die Blätter wurden traditionell von den Māori als Tee bei Magenbeschwerden verwendet, und das Kraut besitzt adstringierende Eigenschaften aufgrund seines Tannin-Gehalts. Die widerhakigen Früchte haften an Wolle und Kleidung und sind in Weiden und offenen Geländen häufig anzutreffen. In der traditionellen Medizin wurde es zur Behandlung von Hauterkrankungen und Entzündungen eingesetzt."),

    (855, "description_es",
     "Biddy-biddy (Acaena anserinifolia) es un arbusto perenne de crecimiento bajo, perteneciente a la familia Rosaceae, nativo de Nueva Zelanda y Australia. Sus hojas fueron utilizadas tradicionalmente por los maoríes como té para problemas estomacales, y la planta tiene propiedades astringentes por su contenido en taninos. Sus frutos con espinas se adhieren a la lana y la ropa, siendo comunes en pastos y áreas abiertas. Ha sido utilizado en medicina tradicional para tratar afecciones cutáneas e inflamaciones."),

    (855, "description_pt",
     "Biddy-biddy (Acaena anserinifolia) é um arbusto perene de crescimento baixo da família Rosaceae, nativo da Nova Zelândia e da Austrália. As suas folhas foram utilizadas pelos maoris como chá para problemas gastrointestinais, e a planta possui propriedades adstringentes devidas ao seu teor em taninos. Os seus frutos com espinhas aderem à lã e à roupa, sendo comuns em pastagens e áreas abertas. Foi utilizado na medicina tradicional para tratar condições da pele e inflamações."),

    (855, "description_ja",
     "ビディービディー（Acaena anserinifolia）は、ニュージーランドとオーストラリア原産のバラ科の低木で、マット状に生育します。マオリの人々が胃の不調のために葉をお茶として利用しており、タンニンを含むため収斂作用があります。バーリのある果実が羊毛や衣服にくっつき、草地や開けた場所でよく見られます。皮膚の疾患や炎症の治療に伝統的に用いられてきました。"),

    (855, "description_zh",
     "Biddy-biddy（Acaena anserinifolia）是一种低矮的垫状多年生灌木，属于蔷薇科，原产于新西兰和澳大利亚。毛利人曾用其叶片泡茶以缓解胃部不适，因其富含单宁而具有收敛性。其带刺果实会粘附在毛发和衣物上，常见于草地和开阔地带。传统医学中用于治疗皮肤疾病和炎症。"),

    # ============================================================
    # ID 900 SENNA (Senna alata)
    # ALL 12 langs were Ayrton Senna bio
    # ============================================================
    (900, "description",
     "Senna (Senna alata) is a tropical shrub in the family Fabaceae, native to Mexico and Central America, now widespread in tropical regions worldwide. It bears large pinnate leaves and upright clusters of bright yellow flowers resembling candelabras, giving rise to the common name candle bush. The leaves and pods contain anthraquinone glycosides (sennosides) that act as a stimulant laxative, and the plant is widely used as an antifungal remedy for ringworm and other skin conditions. It is used in traditional medicine across Africa, Asia, and the Americas."),

    (900, "description_ro",
     "Senna (Senna alata) este un arbust tropical din familia Fabaceae, originar din Mexic și America Centrală, acum răspândit în toate regiunile tropicale. Are frunze pinnate mari și inflorescențe de flori galbene strălucitoare cu forma de candelabru, de unde primește denumirea de arbuștele-lumânare. Frunzele și semințele conțin glicozide antrachinone (sennoside) care acționează ca laxativ stimulant, iar planta este folosită ca remediu antifungic pentru afecțiuni cutanate. Este folosită în medicina tradițională din Africa, Asia și America."),

    (900, "description_de",
     "Senna (Senna alata) ist ein tropischer Strauch aus der Familie der Fabaceae, ursprünglich aus Mexiko und Mittelamerika, heute in tropischen Regionen weltweit verbreitet. Sie trägt große gefiederte Blätter und aufrechte Büschel leuchtend gelber Blüten, die an Kandelaber erinnern und der Pflanze den Namen Kerzenstrauch einbrachten. Die Blätter und Hülsen enthalten Anthraquinon-Glykoside (Sennoside), die als Laxativ wirken, und die Pflanze wird als antifungales Mittel gegen Hauterkrankungen wie Ringwurm eingesetzt. Sie wird in der traditionellen Medizin in Afrika, Asien und Amerika verwendet."),

    (900, "description_fr",
     "Le séné (Senna alata) est un arbuste tropical de la famille des Fabaceae, originaire du Mexique et d'Amérique centrale, maintenant répandu dans les régions tropicales du monde entier. Il porte de grandes feuilles pennées et des grappes dressées de fleurs jaunes vives ressemblant à des candélabres, d'où le surnom de buisson-chandelle. Les feuilles et les gousses contiennent des glycosides anthraquinoniques (sennosides) qui agissent comme laxatif stimulant, et la plante est largement utilisée comme remède antifongique pour les affections cutanées. Elle est utilisée en médecine traditionnelle en Afrique, en Asie et en Amérique."),

    (900, "description_it",
     "La senna (Senna alata) è un arbusto tropicale della famiglia delle Fabaceae, originaria del Messico e dell'America centrale, ora diffusa nelle regioni tropicali di tutto il mondo. Porta grandi foglie pennate e grappoli eretti di fiori giallo brillante che ricordano candelabri, da cui il nome cespuglio delle candele. Le foglie e i baccelli contengono glicosidi antrachinoniici (sennosidi) che agiscono come lassativo stimolante, e la pianta è ampiamente utilizzata come rimedio antifungino per malattie della pelle. È usata nella medicina tradizionale in Africa, Asia e America."),

    (900, "description_es",
     "La senna (Senna alata) es un arbusto tropical de la familia Fabaceae, nativo de México y América Central, ahora ampliamente distribuido en regiones tropicales. Lleva grandes hojas pinnadas y racimos erguidos de flores amarillas brillantes parecidos a candelabros, de donde recibe el nombre de arbusto-vela. Las hojas y vainas contienen glucósidos de antraquinona (sennosidos) que actúan como laxante estimulante, y la planta se usa ampliamente como remedio antifúngico para afecciones cutáneas. Se utiliza en medicina tradicional en África, Asia y América."),

    (900, "description_ru",
     "Сенна (Senna alata) — тропический кустарник из семейства Бобовых, родом из Мексики и Центральной Америки, ныне распространённый в тропических регионах по всему миру. Имеет крупные перистые листья и прямостоячие кисти ярко-жёлтых цветков, напоминающих канделябры, за что растение называют кустарником-свечой. Листья и стручки содержат антрахинонгликозиды (сеннозиды), действующие как слабительное, и широко применяются как противогрибковое средство при кожных заболеваниях. Используется в традиционной медицине Африки, Азии и Америки."),

    (900, "description_pt",
     "A senna (Senna alata) é um arbusto tropical da família Fabaceae, nativo do México e da América Central, agora amplamente distribuído em regiões tropicais. Possui grandes folhas pinnadas e cachos eretos de flores amarelas brilhantes semelhantes a candelabros, daí o nome arbusto-vela. As folhas e vagens contêm glicosídeos de antraquinona (sennosídeos) que atuam como laxante estimulante, e a planta é amplamente usada como remédio antifúngico para condições da pele. É utilizada na medicina tradicional na África, Ásia e América."),

    (900, "description_ja",
     "セナ（Senna alata）は、マメ科の熱帯灌木で、メキシコおよび中央アメリカ原産ですが、現在は世界中の熱帯地域に広く分布しています。大きな羽状複葉とキャンドルのような鮮やかな黄色の直立した花序を持ち、「キャンドルブッシュ」と呼ばれます。葉と実にはアントラキノングリコシド（セノシド）が含まれており、刺激性の下剤として作用し、皮膚疾患（特にたむし）の抗真菌療法にも広く使われます。アフリカ、アジア、アメリカの伝統医学で用いられています。"),

    (900, "description_zh",
     "翅荚决明（Senna alata）是一种豆科热带灌木，原产于墨西哥和中美洲，现已广泛分布于世界各热带地区。植株具有大型羽状复叶和形似烛台的鲜黄色直立花序，因此俗称烛台灌木。叶和荚含有蒽醌苷（Sennosides），具有刺激性泻药作用，并被广泛用于治疗皮肤疾病（如癣）的抗真菌疗法。在非洲、亚洲和美洲的传统医学中均有应用。"),

    (900, "description_ar",
     "سنا حرجي (Senna alata) شجيرة استوائية من فصيلة البقوليات، أصيلة في المكسيك وأمريكا الوسطى، منتشرة الآن في جميع المناطق الاستوائية. تتميز بأوراق ريشية كبيرة وعناقيد مستقيمة من الأزهار الصفراء البراقة التي تشبه الشمعدانات، مما جعلها تُعرف باسم شجيرة الشموع. تحتوي الأوراق والقرون على غليكوسيدات الأنثراكينون (سينوسيدات) التي تعمل كملين منبه، وتُستخدم على نطاق واسع كعلاج مضاد للفطريات لأمراض الجلد. تُستخدم في الطب التقليدي في أفريقيا وآسيا وأمريكا."),

    (900, "description_hi",
     "सेना (Senna alata) एक उष्णकटिबंधीय झाड़ी है जो फैबेसी कुल में आती है और मेक्सिको व मध्य अमेरिका में मूल रूप से पाई जाती है, अब विश्व के सभी उष्णकटिबंधीय क्षेत्रों में फैल गई है। इसकी बड़ी पिन्नेट पत्तियां और मोमबत्ती के आकार के चमकीले पीले फूलों के गुच्छे होते हैं, जिसके कारण इसे मोमबत्ती झाड़ी कहा जाता है। पत्तियों और फलियों में एंथ्राक्विनोन ग्लाइकोसाइड (सेनोसाइड) पाए जाते हैं जो रेचक की तरह काम करते हैं; यह त्वचा रोगों के उपचार में भी व्यापक रूप से उपयोग होती है। अफ्रीका, एशिया और अमेरिका की पारंपरिक चिकित्सा में इसका उपयोग किया जाता है।"),

    # ============================================================
    # ID 952 DAY JASMINE (Cestrum diurnum)
    # EN, DE, ES, RU, PT, JA, ZH, HI had Jasmine Sandlas bio; RO/FR/IT/AR correct
    # ============================================================
    (952, "description",
     "Day jasmine (Cestrum diurnum) is an evergreen shrub in the family Solanaceae, native to the Caribbean and naturalized in tropical and subtropical regions worldwide. It bears clusters of small white tubular flowers that release their fragrance during the day. The plant contains vitamin D3 glycosides and calcinogenic compounds and is toxic to livestock; leaf preparations have been used in traditional medicine for their sedative and analgesic properties."),

    (952, "description_de",
     "Taglicher Jasmin (Cestrum diurnum) ist ein immergrüner Strauch aus der Familie Solanaceae, ursprünglich aus der Karibik und weltweit in tropischen und subtropischen Regionen eingebürgert. Er bildet Büschel kleiner weißer röhrenförmiger Blüten, die ihren Duft tagsüber verströmen. Die Pflanze enthält Vitamin-D3-Glykoside und calcinogene Verbindungen und ist für Nutztiere giftig; Blattzubereitungen wurden in der traditionellen Medizin wegen ihrer beruhigenden und schmerzstillenden Eigenschaften verwendet."),

    (952, "description_es",
     "El jazmín de día (Cestrum diurnum) es un arbusto siempreverde de la familia Solanaceae, nativo del Caribe y naturalizado en regiones tropicales y subtropicales. Produce racimos de pequeñas flores tubulares blancas que liberan su fragancia durante el día. La planta contiene glucósidos de vitamina D3 y compuestos calcinogénicos y es tóxica para el ganado; las preparaciones de hojas se han utilizado en medicina tradicional por sus propiedades sedantes y analgésicas."),

    (952, "description_ru",
     "Дневной жасмин (Cestrum diurnum) — вечнозелёный кустарник из семейства Паслёновых, родом из Карибского региона и натурализованный в тропических и субтропических зонах по всему миру. Образует пучки небольших белых трубчатых цветков, которые испускают аромат в дневное время. Растение содержит гликозиды витамина D3 и кальциногенные соединения, токсично для скота; препараты из листьев использовались в традиционной медицине как седативное и анальгетическое средство."),

    (952, "description_pt",
     "O jasmim-de-dia (Cestrum diurnum) é um arbusto sempre-verde da família Solanaceae, nativo do Caribe e naturalizado em regiões tropicais e subtropicais em todo o mundo. Produz cachos de pequenas flores tubulares brancas que libertam o seu perfume durante o dia. A planta contém glicosídeos de vitamina D3 e compostos calcinogénicos e é tóxica para o gado; preparações de folhas foram utilizadas na medicina tradicional pelas suas propriedades sedativas e analgésicas."),

    (952, "description_ja",
     "デイジャスミン（Cestrum diurnum）は、カリブ海地方原産のナス科の常緑灌木で、世界中の熱帯・亜熱帯地域に帰化しています。小さな白い管状の花を束状に咲かせ、昼間に香りを放出します。ビタミンD3グリコシドとカルシノゲン系化合物を含み、家畜に対して毒性があります。伝統的な医療では、葉から作られた製剤が鎮静および鎮痛効果として用いられてきました。"),

    (952, "description_zh",
     "白天茉莉（Cestrum diurnum）是茄科的一种常绿灌木，原产于加勒比地区，现已广泛分布于世界各地的热带和亚热带地区。其花朵呈簇状，为小型白色管状花，白天散发香气。该植物含有维生素D3糖苷和钙化生成化合物，对牲畜有毒；其叶片提取物在传统医学中被用于镇静和止痛。"),

    (952, "description_hi",
     "दिन जास्मिन (Cestrum diurnum) सोलेनेसी कुल का एक सदाबहार झाड़ीदार पौधा है जो कैरिबियन क्षेत्र में मूल रूप से पाया जाता है और विश्व के उष्णकटिबंधीय व उपोष्णकटिबंधीय क्षेत्रों में फैल गया है। इसमें छोटे गुच्छे में सफेद नलिकाकार फूल होते हैं जो दिन के समय सुगंध छोड़ते हैं। इस पौधे में विटामिन D3 ग्लाइकोसाइड और कैल्सिनोजेनिक यौगिक होते हैं और यह पशुओं के लिए विषाक्त होता है; पत्तियों की तैयारी पारंपरिक चिकित्सा में शामक और दर्दनाशक गुणों के लिए उपयोग की जाती है।"),

    # ============================================================
    # DISAMBIGUATION PAGE FIXES
    # ============================================================

    # ID 205 AUTUMN CROCUS (Colchicum autumnale) — EN only
    (205, "description",
     "Autumn crocus (Colchicum autumnale) is a perennial plant in the family Colchicaceae, native to meadows and woodlands across Europe. Despite its crocus-like appearance, it is unrelated to true crocuses (Crocus spp.) and belongs to a different family. All parts of the plant are highly toxic, containing colchicine, an alkaloid used medically to treat gout and familial Mediterranean fever. It flowers in autumn before its leaves emerge in spring, giving rise to the common name naked ladies."),

    # ID 208 WILD YAM (Dioscorea villosa) — EN, DE, RO
    (208, "description",
     "Wild yam (Dioscorea villosa) is a climbing vine in the family Dioscoreaceae, native to eastern North America. The tuberous roots contain diosgenin, a steroidal saponin used as a starting material for pharmaceutical synthesis of steroid hormones. In traditional herbal medicine, wild yam root has been used for menstrual cramps, muscle spasms, and as an anti-inflammatory and antispasmodic remedy. Modern research has explored its potential hormonal and anti-inflammatory effects."),

    (208, "description_ro",
     "Ignamă sălbatică (Dioscorea villosa) este o plantă agățătoare din familia Dioscoreaceae, originară din America de Nord de Est. Rădăcinile tuberoase conțin diosgenină, un saponin sterolic folosit ca materie primă în sinteza farmaceutică a hormonilor steroizi. În medicina tradițională, rădăcina a fost utilizată pentru crampe menstruale, spasme musculare și ca antiinflamator și antispastic. Cercetările moderne explorează efectele sale hormonale și antiinflamatoare potențiale."),

    (208, "description_de",
     "Wilde Yamswurzel (Dioscorea villosa) ist eine kletternde Pflanze aus der Familie Dioscoreaceae, heimisch im östlichen Nordamerika. Die knolligen Wurzeln enthalten Diosgenin, ein sterisches Saponin, das als Ausgangsmaterial für die pharmazeutische Synthese von Steroidhormonen dient. In der traditionellen Kräutermedizin wurde die Yamswurzel gegen Menstruationskrämpfe, Muskelkrämpfe und als entzündungshemmendes und krampflösendes Mittel eingesetzt. Die moderne Forschung untersucht ihre potenzielle hormonelle und entzündungshemmende Wirkung."),

    # ID 216 SCAEVOLA (Scaevola taccada) — EN, RO
    (216, "description",
     "Scaevola taccada is a coastal shrub in the family Goodeniaceae, native to tropical beaches and shores across the Indo-Pacific region. Its distinctive half-shaped white flowers, which appear as if cut in half, inspired the Hawaiian name naupaka and local names across the Pacific. It is extremely salt-tolerant and plays an important role in stabilizing coastal vegetation. It has been used in traditional Pacific Island medicine to treat ear infections, eye conditions, and skin wounds."),

    (216, "description_ro",
     "Scaevola taccada este un arbust costier din familia Goodeniaceae, originar de pe plajele și coastele tropicale din Indo-Pacific. Florile sale distinctive, de culoare albă și în formă de jumătate, au inspirat denumirea de naupaka în Hawaii. Extrem de tolerantă la sare, planta joacă un rol important în stabilizarea vegetației costiere. A fost folosită în medicina tradițională a insulelor din Pacific pentru tratarea infecțiilor auriculare, afecțiunilor oculare și rănilor cutanate."),

    # ID 221 BLUE FLAG (Iris versicolor) — EN, DE, RO
    (221, "description",
     "Blue flag (Iris versicolor) is a perennial flowering plant in the family Iridaceae, native to eastern North America, growing in wet meadows, marshes, and along stream banks. It bears striking violet-blue flowers with distinctive yellow patches and purple veining on the falls. The rhizomes were used by various Native American peoples as a cathartic, emetic, and treatment for liver and skin ailments, though they contain toxic irisin and require careful preparation. It is also widely grown as an ornamental pond plant."),

    (221, "description_ro",
     "Iris versicolor este o plantă erbacee perenă din familia Iridaceae, originară din America de Nord de Est, crescând în pășuni umede și mlaștini. Are flori violet-azurii cu pete galbene și vene violacee distinctive. Rizomii au fost utilizați de diverse popoare amerindiene ca purgativ, emetic și tratament pentru afecțiunile hepatice și cutanate, deși conțin irisin toxic. Este cultivat pe scară largă ca plantă ornamentală pentru iazuri."),

    (221, "description_de",
     "Bunter Schwertlilie (Iris versicolor) ist eine mehrjährige Blütenpflanze aus der Familie Iridaceae, heimisch im östlichen Nordamerika, wachsend in feuchten Wiesen, Marschen und an Bachufern. Sie trägt auffällige violett-blaue Blüten mit charakteristischen gelben Flecken und violetten Adern. Die Rhizome wurden von verschiedenen indigenen Völkern als Abführ- und Brechmittel sowie zur Behandlung von Leber- und Hauterkrankungen verwendet, obwohl sie das toxische Irisin enthalten. Sie wird auch als Zierpflanze für Teiche kultiviert."),

    # ID 277 BLADDERNUT (Staphylea pinnata) — EN, RO
    (277, "description",
     "European bladdernut (Staphylea pinnata) is a deciduous shrub in the family Staphyleaceae, native to central and southern Europe. It produces clusters of white bell-shaped flowers and distinctive inflated papery seed pods that rattle when dry, giving rise to the common name. Seeds and bark have been used in folk medicine as an astringent and remedy for rheumatism and skin ailments. The seeds were historically eaten roasted or used to produce oil in some regions."),

    (277, "description_ro",
     "Clopoțeii (Staphylea pinnata) este un arbust caducifoliat din familia Staphyleaceae, originar din Europa centrală și sudică. Produce grupuri de flori albe în formă de clopot și capsule de semințe gonflate, caracteristice, care zornăie când se usucă. Semințele și scoarța au fost folosite în medicina populară ca astringent și remediu pentru reumatism și afecțiuni cutanate. Semințele au fost consumate prăjite sau utilizate pentru producerea de ulei în unele regiuni."),

    # ID 279 BENZOIN (Styrax benzoin) — EN, RO
    (279, "description",
     "Benzoin (Styrax benzoin) is a tropical tree in the family Styracaceae, native to Sumatra and Java. It produces an aromatic balsamic resin obtained by tapping the bark, used for centuries in incense, perfumery, and traditional medicine throughout Asia and the Middle East. The resin has documented antiseptic and anti-inflammatory properties and is used in preparations for treating skin infections, respiratory ailments, and as a wound-healing agent. Benzoin tincture is still used in modern pharmacy as a skin protectant."),

    (279, "description_ro",
     "Benzoinul (Styrax benzoin) este un arbore tropical din familia Styracaceae, originar din Sumatra și Java. Produce o rășină balsamică aromată obținută prin incizia scoarței, folosită de secole în incensuri, parfumerie și medicină tradițională în Asia și Orientul Mijlociu. Rășina are proprietăți antiseptice și antiinflamatoare și este utilizată în tratamentul infecțiilor cutanate, afecțiunilor respiratorii și ca agent de vindecare a rănilor. Tinctura de benzoin este încă utilizată în farmacia modernă ca protector cutanat."),

    # ID 619 WHITE HELLEBORE (Veratrum album) — EN only
    (619, "description",
     "White hellebore (Veratrum album) is a tall perennial herb in the family Melanthiaceae, native to mountain meadows and open woodlands across Europe and western Asia. Despite its name, it is unrelated to true hellebores (Helleborus spp.). The plant is highly toxic, containing steroidal alkaloids including veratrine and cyclopamine, which cause severe cardiac and neurological effects. Historically used in small doses as an emetic, insecticide, and treatment for hypertension, it is now rarely used medicinally due to its narrow therapeutic window."),

    # ID 677 GALINGALE (Cyperus longus) — EN only
    (677, "description",
     "Galingale (Cyperus longus) is a perennial sedge in the family Cyperaceae, native to southern Europe and North Africa, growing in wet habitats such as marshes and riverbanks. The aromatic rhizomes have been used since antiquity in perfumery and herbal medicine. In traditional medicine, galingale has been employed as a digestive stimulant, tonic, and treatment for fever and urinary complaints. It should not be confused with galangal (Alpinia galanga), an unrelated spice plant."),

    # ID 687 UBE / PURPLE YAM (Dioscorea alata) — EN, DE
    (687, "description",
     "Purple yam (Dioscorea alata), also known as ube, is a tropical climbing vine in the family Dioscoreaceae, native to Southeast Asia. It produces large tubers with vivid purple flesh, which are an important food crop across Asia and the Pacific, particularly in the Philippines where ube is used in desserts and confectionery. The tubers are rich in antioxidants including anthocyanins. Purple yam has also been used in traditional medicine for its antioxidant and anti-inflammatory properties."),

    (687, "description_de",
     "Lila Yamswurzel (Dioscorea alata), auch als Ube bekannt, ist eine tropische kletternde Pflanze aus der Familie Dioscoreaceae, heimisch in Südostasien. Sie bildet große Knollen mit intensiv violettem Fruchtfleisch, die eine wichtige Nahrungspflanze in Asien und im Pazifik darstellen, besonders auf den Philippinen. Die Knollen sind reich an Antioxidantien, darunter Anthocyane. In der traditionellen Medizin wird sie wegen ihrer antioxidativen und entzündungshemmenden Eigenschaften eingesetzt."),

    # ID 733 SPANISH NEEDLES (Bidens pilosa) — EN, DE, RO
    (733, "description",
     "Spanish needles (Bidens pilosa) is a tropical annual herb in the family Asteraceae, native to the Americas and now widespread as a cosmopolitan weed in tropical and subtropical regions worldwide. It bears small white flowers with yellow centres and produces elongated needle-like seeds with barbed awns that cling to clothing and fur. Despite being considered a weed in many areas, it is one of the most extensively studied medicinal plants, used in traditional medicine across Africa, Asia, and Latin America for its anti-inflammatory, antimicrobial, and wound-healing properties."),

    (733, "description_ro",
     "Bidens pilosa este o plantă erbacee anuală tropicală din familia Asteraceae, originară din Americi și acum răspândită ca buruiană cosmopolită în regiunile tropicale și subtropicale. Are flori mici albe cu centru galben și produce semințe lungi, în formă de ac, cu ariste barbate care se atașează de haine și blănuri. Deși este considerată buruiană în multe zone, este una dintre cele mai studiate plante medicinale, utilizată în Africa, Asia și America Latină pentru proprietățile sale antiinflamatoare, antimicrobiene și de vindecare a rănilor."),

    (733, "description_de",
     "Spanische Nadeln (Bidens pilosa) ist ein tropisches einjähriges Kraut aus der Familie Asteraceae, heimisch in Amerika und heute als kosmopolitisches Unkraut in tropischen und subtropischen Regionen weltweit verbreitet. Es hat kleine weiße Blüten mit gelben Zentren und produziert lange, nadelförmige Samen mit widerhakigen Grannen. Obwohl sie in vielen Gebieten als Unkraut gilt, ist sie eine der am intensivsten erforschten Heilpflanzen und wird in Afrika, Asien und Lateinamerika für ihre entzündungshemmenden, antimikrobiellen und wundheilenden Eigenschaften eingesetzt."),

    # ID 767 BETONY (Stachys officinalis) — EN, RO
    (767, "description",
     "Betony (Stachys officinalis, syn. Betonica officinalis) is a perennial herb in the family Lamiaceae, native to Europe and western Asia, growing in meadows, open woodlands, and heathlands. It bears dense spikes of pinkish-purple flowers in summer and has aromatic, wrinkled leaves. Historically one of the most important medicinal plants in European herbalism, it was used for headaches, anxiety, digestive disorders, and as a general tonic. The plant contains stachydrine, tannins, and iridoid glycosides."),

    (767, "description_ro",
     "Betonia (Stachys officinalis) este o plantă erbacee perenă din familia Lamiaceae, originară din Europa și Asia de Vest, crescând în pășuni și păduri deschise. Are inflorescențe dense de flori roz-violacee în vară și frunze aromate, zbârcite. Istoric una dintre cele mai importante plante medicinale din fitoterapia europeană, a fost folosită pentru dureri de cap, anxietate, probleme digestive și ca tonic general. Conține stachydrine, tanine și glicozide iridoide."),

    # ID 791 HORSE MINT (Mentha longifolia) — EN, DE
    (791, "description",
     "Horse mint (Mentha longifolia) is a strongly aromatic perennial herb in the family Lamiaceae, native across Europe, Asia, and parts of Africa, growing in moist habitats. It has lance-shaped leaves with a woolly texture and produces spikes of pale lilac to white flowers. The plant contains menthol and various monoterpenes and has been used in traditional medicine as an antispasmodic, digestive aid, and antimicrobial remedy. Horse mint oil is used in aromatherapy and as a flavouring agent."),

    (791, "description_de",
     "Rossminze (Mentha longifolia) ist eine stark aromatische mehrjährige Krautpflanze aus der Familie Lamiaceae, heimisch in Europa, Asien und Teilen Afrikas, wachsend in feuchten Lebensräumen. Sie hat lanzettförmige Blätter mit wolligem Textur und produziert Blütenstände aus hellvioletten bis weißen Blüten. Die Pflanze enthält Menthol und verschiedene Monoterpene und wurde in der Volksmedizin als krampflösend, Verdauungshilfe und antimikrobiell eingesetzt. Rossmünze-Öl wird in der Aromatherapie und als Geschmacksstoff verwendet."),

    # ID 821 COWBANE (Cicuta virosa) — EN, RO
    (821, "description",
     "Cowbane (Cicuta virosa) is a highly poisonous perennial plant in the family Apiaceae, native to northern and central Europe and northern Asia, growing in marshy habitats and along slow-moving waterways. It closely resembles edible umbellifers such as wild parsnip and water parsley, making accidental ingestion a serious hazard to humans and livestock. The roots contain cicutoxin, one of the most potent plant toxins known, causing violent convulsions and death even in small doses. There is no specific antidote for cicutoxin poisoning."),

    (821, "description_ro",
     "Cucuta de apă (Cicuta virosa) este o plantă perenă extrem de toxică din familia Apiaceae, originară din nordul și centrul Europei și nordul Asiei, crescând în habitate mlăștinoase. Seamănă cu plante comestibile precum pătrunjelul sălbatic, ceea ce face ca ingestia accidentală să fie un risc serios pentru oameni și animale. Rădăcinile conțin cicutoxina, una dintre cele mai puternice toxine vegetale cunoscute, care provoacă convulsii violente și poate fi fatală chiar și în doze mici. Nu există antidot specific pentru intoxicația cu cicutoxină."),

    # ID 899 GOLDEN SHOWER TREE (Cassia fistula) — EN, RO
    (899, "description",
     "Golden shower tree (Cassia fistula) is a tropical flowering tree in the family Fabaceae, native to the Indian subcontinent and widely cultivated in tropical regions worldwide. It is renowned for its spectacular cascading clusters of bright yellow flowers and is the national tree and flower of Thailand. The long cylindrical pods contain a sweet dark pulp used as a mild laxative in Ayurvedic medicine, and the bark, leaves, and flowers are also used medicinally for skin diseases, fever, and as an antimicrobial."),

    (899, "description_ro",
     "Cassia fistula este un arbore tropical din familia Fabaceae, originar din subcontinentul indian și cultivat pe scară largă în regiunile tropicale. Este renumit pentru ciorchinele sale spectaculoase de flori galbene strălucitoare care acoperă arborele primăvara; este arborele național al Thailandei. Păstăile cilindrice conțin o pulpă dulce folosită ca laxativ ușor în medicina Ayurvedică, iar scoarța, frunzele și florile sunt utilizate medicinal pentru boli de piele, febră și ca antimicrobian."),
]

for row_id, col, val in fixes:
    conn.execute(f"UPDATE museum_item SET {col}=? WHERE id=?", (val, row_id))
    print(f"  {row_id:3d}  {col:<30}  updated")

conn.commit()
conn.close()
print(f"\nDone. Applied {len(fixes)} description fixes.")
