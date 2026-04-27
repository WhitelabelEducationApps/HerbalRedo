# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import re, sqlite3, time, requests
from io import BytesIO
from pathlib import Path

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

ROOT = Path(r"C:\Users\rsavu\AndroidStudioProjects\HerbalRedo")
DB = ROOT / "androidApp/src/main/assets/plants.db"
DRAWABLE = ROOT / "androidApp/src/main/res/drawable-nodpi"
HEADERS = {"User-Agent": "HerbalRedo/1.0 (educational medicinal plant app)"}

def to_thumb_320(url):
    """Convert any Wikimedia URL to a 320px thumbnail URL (pre-cached, less rate-limited)."""
    if not url:
        return url
    # Already a thumb URL — just swap the size
    m = re.match(r'(https://upload\.wikimedia\.org/wikipedia/[^/]+/thumb/[a-f0-9]/[a-f0-9]+/(.+?))/\d+px-', url)
    if m:
        return f"{m.group(1)}/320px-{m.group(2)}"
    # Direct file URL — insert /thumb/ and append size
    m2 = re.match(r'(https://upload\.wikimedia\.org/wikipedia/([^/]+))/([a-f0-9]/[a-f0-9]+)/(.+)', url)
    if m2:
        base, wiki, hashes, fname = m2.group(1), m2.group(2), m2.group(3), m2.group(4)
        return f"{base}/thumb/{hashes}/{fname}/320px-{fname}"
    return url

def sanitize(name):
    s = re.sub(r"[^a-z0-9]", "", name.lower())
    return ("a" + s) if s and s[0].isdigit() else s

# id -> (plant_name, image_url)
FIXES = {
    144: ("Licorice",                  "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Illustration_Glycyrrhiza_glabra0.jpg/960px-Illustration_Glycyrrhiza_glabra0.jpg"),
    154: ("Lemon",                     "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/P1030323.JPG/960px-P1030323.JPG"),
    186: ("Cat's Claw",                "https://upload.wikimedia.org/wikipedia/commons/c/c4/Uncaria_tomentosa.png"),
    193: ("Asian Ginseng",             "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Ginsengpflanze.jpg/960px-Ginsengpflanze.jpg"),
    216: ("Scaevola",                  "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Starr_010209-0286_Scaevola_taccada.jpg/960px-Starr_010209-0286_Scaevola_taccada.jpg"),
    242: ("Wood Sorrel",               "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Oxalis_acetosella_LC0190.jpg/960px-Oxalis_acetosella_LC0190.jpg"),
    243: ("Saw Palmetto",              "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Serenoa_repens_USDA1.jpg/500px-Serenoa_repens_USDA1.jpg"),
    256: ("Bistort",                   "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Bloemen_van_adderwortel_%28Persicaria_bistorta%2C_synoniem%2C_Polygonum_bistorta%29_06-06-2021._%28d.j.b%29.jpg/500px-Bloemen_van_adderwortel_%28Persicaria_bistorta%2C_synoniem%2C_Polygonum_bistorta%29_06-06-2021._%28d.j.b%29.jpg"),
    257: ("Rhubarb",                   "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Apothekergarten_Seligenstadt_Rheum_Palmatum_Medizinalrhabarber2.jpg/960px-Apothekergarten_Seligenstadt_Rheum_Palmatum_Medizinalrhabarber2.jpg"),
    259: ("Protea",                    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Peninsula_Sandstone_Fynbos_-_KingProtea_-_Table_Mountain.JPG/960px-Peninsula_Sandstone_Fynbos_-_KingProtea_-_Table_Mountain.JPG"),
    267: ("Aspen",                     "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/PopulusTremula001.JPG/960px-PopulusTremula001.JPG"),
    271: ("Bergenia",                  "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Bergenia_crassifolia_a1.jpg/960px-Bergenia_crassifolia_a1.jpg"),
    274: ("Resurrection Plant",        "https://upload.wikimedia.org/wikipedia/commons/0/05/Selaginella_lepidophylla_gruen.jpeg"),
    275: ("Quassia",                   "https://upload.wikimedia.org/wikipedia/commons/4/44/Quassia_amara_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-117.jpg"),
    277: ("Bladdernut",                "https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Staphylea_pinnata_MS_4410.jpg/960px-Staphylea_pinnata_MS_4410.jpg"),
    279: ("Benzoin",                   "https://upload.wikimedia.org/wikipedia/commons/1/1f/Styrax_benzoin_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-133.jpg"),
    286: ("Damiana",                   "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Turnera_diffusa_var._aphrodisiaca_002.JPG/960px-Turnera_diffusa_var._aphrodisiaca_002.JPG"),
    288: ("Slippery Elm",              "https://upload.wikimedia.org/wikipedia/commons/e/eb/Mature_Ulmus_rubra_in_graveyard.jpg"),
    290: ("Stinging Nettle",           "https://upload.wikimedia.org/wikipedia/commons/6/6f/Fen_nettle_%28Urtica_dioica_ssp._galeopsifolia%29_-_geograph.org.uk_-_5423125.jpg"),
    291: ("Spikenard",                 "https://upload.wikimedia.org/wikipedia/commons/6/6b/Nardostachys_jatamansi_rhizome_with_a_scale_to_asses_its_size_Photo_N_C_SHAH.jpg"),
    292: ("Lemon Verbena",             "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Aloysia_citriodora_002.jpg/960px-Aloysia_citriodora_002.jpg"),
    304: ("Sumac",                     "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Sommacco.jpg/960px-Sommacco.jpg"),
    344: ("Narrow-leaved Coneflower",  "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Pale_Purple-Coneflower_%28Echinacea_angustifolia%29_2016-07-12_963.jpg/960px-Pale_Purple-Coneflower_%28Echinacea_angustifolia%29_2016-07-12_963.jpg"),
    349: ("Immortelle",                "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Helichrysum_italicum_%28immortelle%29.JPG/960px-Helichrysum_italicum_%28immortelle%29.JPG"),
    577: ("Blackhaw",                  "https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Viburnum_prunifolium_USDA1.jpg/960px-Viburnum_prunifolium_USDA1.jpg"),
    598: ("Yerba Mate",                "https://upload.wikimedia.org/wikipedia/commons/2/28/Ilex_paraguariensis_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-074.jpg"),
    637: ("Roseroot",                  "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Rhodiola_rosea_a2.jpg/960px-Rhodiola_rosea_a2.jpg"),
    639: ("Orpine",                    "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Sedum_telephium_240808e.jpg/960px-Sedum_telephium_240808e.jpg"),
    677: ("Galingale",                 "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Cyperus_longus_Ypey52.jpg/960px-Cyperus_longus_Ypey52.jpg"),
    679: ("Black Bog Rush",            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Schoenus_nigricans_kz2.jpg/960px-Schoenus_nigricans_kz2.jpg"),
    683: ("Winter Daphne",             "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Daphne_odora-ja01.jpg/960px-Daphne_odora-ja01.jpg"),
    685: ("False Hemp",                "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Datisca_cannabina_002.JPG/960px-Datisca_cannabina_002.JPG"),
    693: ("Mexican Yam",               "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Dioscorea_mexicana.jpg/960px-Dioscorea_mexicana.jpg"),
    715: ("Major Ephedra",             "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/20250704_Ephedra_major.jpg/500px-20250704_Ephedra_major.jpg"),
    717: ("Nevada Ephedra",            "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Ephedra-nevadensis-cones.jpg/960px-Ephedra-nevadensis-cones.jpg"),
    731: ("Coyote Brush",              "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Baccharis_pilularis_kz04.jpg/960px-Baccharis_pilularis_kz04.jpg"),
    739: ("Pale Indian Plantain",      "https://upload.wikimedia.org/wikipedia/commons/7/7e/Cacalia_atriplicifolia_flower.jpg"),
    757: ("Blessed Thistle",           "https://upload.wikimedia.org/wikipedia/commons/8/87/Cnicus_benedictus_flor.jpg"),
    769: ("Calamint",                  "https://upload.wikimedia.org/wikipedia/commons/2/23/Calamintha_nepeta_nepeta0.jpg"),
    773: ("Moldavian Balm",            "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Dracocephalum_moldavica_inflorescence.jpg/960px-Dracocephalum_moldavica_inflorescence.jpg"),
    787: ("Water Mint",                "https://upload.wikimedia.org/wikipedia/commons/f/f8/Mentha_aquatica_02.jpg"),
    801: ("Ammi",                      "https://upload.wikimedia.org/wikipedia/commons/4/4a/Ammi_visnaga_-_Toothpick-plant_-_Tandstikurt_%2851157555303%29.jpg"),
    813: ("Spreading Hedge Parsley",   "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Torilis_arvensis.jpg/960px-Torilis_arvensis.jpg"),
    843: ("Lesser Galangal",           "https://upload.wikimedia.org/wikipedia/commons/8/89/Alpinia_officinarum_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-156.jpg"),
    847: ("Spiked Ginger Lily",        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Curtis%27s_botanical_magazine_%288294309208%29.jpg/960px-Curtis%27s_botanical_magazine_%288294309208%29.jpg"),
    849: ("Zanthorhiza",               "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Xanthorhiza_simplicissima_kz13.jpg/500px-Xanthorhiza_simplicissima_kz13.jpg"),
    851: ("Kacip Fatimah",             "https://upload.wikimedia.org/wikipedia/en/5/53/Labisia_pumila_grown_in_a_nursery.jpg"),
    859: ("Fragrant Agrimony",         "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Agrimonia_procera_002.JPG/960px-Agrimonia_procera_002.JPG"),
    863: ("Common Lady's Mantle",      "https://upload.wikimedia.org/wikipedia/commons/8/84/Nordens_flora_Alchemilla_vulgaris.jpg"),
    865: ("Bastard Agrimony",          "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Illustration_Agrimonia_eupatoria0.jpg/960px-Illustration_Agrimonia_eupatoria0.jpg"),
    869: ("Musk Strawberry",           "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Fragaria_moschata_detail.JPG/960px-Fragaria_moschata_detail.JPG"),
    877: ("White Cinquefoil",          "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Potentilla_alba_close-up.jpg/960px-Potentilla_alba_close-up.jpg"),
    881: ("Tormentil",                 "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Potentilla_erecta_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-248.jpg/960px-Potentilla_erecta_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-248.jpg"),
    885: ("Cloudberry",                "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Rubus_chamaemorus%2C_from_Tromsø%2C_August_2020.jpeg/960px-Rubus_chamaemorus%2C_from_Tromsø%2C_August_2020.jpeg"),
    887: ("Blackberry",                "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Blackberry_%28Rubus_fruticosus%29.jpg/960px-Blackberry_%28Rubus_fruticosus%29.jpg"),
    895: ("Gum Acacia",                "https://upload.wikimedia.org/wikipedia/commons/e/ed/Acacia_senegal_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-004.jpg"),
    905: ("Guar",                      "https://upload.wikimedia.org/wikipedia/commons/9/9b/Cluster_bean-guar-Cyamopsis_psoralioides-Cyamopsis_tetragonolobus-TAMIL_NADU73.jpg"),
    917: ("Red Baneberry",             "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Actaea_rubra_kz03.jpg/960px-Actaea_rubra_kz03.jpg"),
    918: ("Amur Adonis",               "https://upload.wikimedia.org/wikipedia/commons/e/e3/W_hukujusou3021.jpg"),
    927: ("Upright Clematis",          "https://upload.wikimedia.org/wikipedia/commons/f/fd/Erect_Clematis.jpg"),
    934: ("Grapefruit",                "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Grapefruits_-_whole-halved-segments.jpg/960px-Grapefruits_-_whole-halved-segments.jpg"),
    935: ("Sweet Orange",              "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Oranges_-_whole-halved-segment.jpg/960px-Oranges_-_whole-halved-segment.jpg"),
    938: ("Evodia",                    "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Rutaceae_sp_SZ21_clean.png/960px-Rutaceae_sp_SZ21_clean.png"),
    957: ("Pituri",                    "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Duboisia_hopwoodii.jpg/960px-Duboisia_hopwoodii.jpg"),
    971: ("Jasmine Nightshade",        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Solanum_2.JPG/960px-Solanum_2.JPG"),
    980: ("Solid-rooted Corydalis",    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Corydalis_solida_240406.jpg/960px-Corydalis_solida_240406.jpg"),
    982: ("Dutchman's Breeches",       "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Dicentra_cucullaria_-_Dutchmans_Breeches_2.jpg/960px-Dicentra_cucullaria_-_Dutchmans_Breeches_2.jpg"),
    # Missing URI plants
    200: ("Frankincense",              "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Boswellia_sacra.jpg/960px-Boswellia_sacra.jpg"),
    308: ("Ajowan",                    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Ajwain_%28Trachyspermum_ammi%29.jpg/500px-Ajwain_%28Trachyspermum_ammi%29.jpg"),
    357: ("Tansy Ragwort",             "https://upload.wikimedia.org/wikipedia/commons/b/bd/Illustration_Senecio_jacobaea.jpg"),
    387: ("Annatto",                   "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Achiote_pj.JPG/960px-Achiote_pj.JPG"),
    400: ("Hound's Tongue",            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Cynoglossum_officinale_W.jpg/960px-Cynoglossum_officinale_W.jpg"),
    405: ("Viper's Bugloss",           "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Echium_vulgare_L.jpg/960px-Echium_vulgare_L.jpg"),
    410: ("Gromwell",                  "https://upload.wikimedia.org/wikipedia/commons/4/4c/Lithospermum_officinale.jpeg"),
    421: ("Lungwort",                  "https://upload.wikimedia.org/wikipedia/commons/7/71/Pulmonaria_officinalis_800.jpg"),
    438: ("Horseradish",               "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Armoracia_rusticana.jpg/960px-Armoracia_rusticana.jpg"),
    451: ("Woad",                      "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Isatis_tinctoria02.JPG/960px-Isatis_tinctoria02.JPG"),
    461: ("Radish",                    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Radish_3371103037_4ab07db0bf_o.jpg/960px-Radish_3371103037_4ab07db0bf_o.jpg"),
    470: ("Pinguin",                   "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Bromelia_pinguin_%28as_Bromelia_fastuosa%29_-_Collectanea_botanica_-_Lindley_pl._1_%281821%29.jpg/960px-Bromelia_pinguin_%28as_Bromelia_fastuosa%29_-_Collectanea_botanica_-_Lindley_pl._1_%281821%29.jpg"),
    482: ("Elemi",                     "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Canarium_indicum_-_Icica_icicariba_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-171.jpg/500px-Canarium_indicum_-_Icica_icicariba_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-171.jpg"),
    494: ("Night-blooming Cereus",     "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Johann_Jacob_Haid_Cereus.jpg/960px-Johann_Jacob_Haid_Cereus.jpg"),
    502: ("Prickly Pear",              "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Dikenli_%C4%B0ncir_%28Opuntia_ficus-indica%29_Gaziantep_Turkey.IMG_1104.jpg/960px-Dikenli_%C4%B0ncir_%28Opuntia_ficus-indica%29_Gaziantep_Turkey.IMG_1104.jpg"),
    512: ("Sweetshrub",                "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/%28MHNT%29_Calycanthus_floridus_-_Les_Martels%2C_Giroussens_Tarn.jpg/960px-%28MHNT%29_Calycanthus_floridus_-_Les_Martels%2C_Giroussens_Tarn.jpg"),
    521: ("Indian Tobacco",            "https://upload.wikimedia.org/wikipedia/commons/0/06/Lobelia_inflata_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-218.jpg"),
    530: ("Balloon Flower",            "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Platycodon_grandiflorus_in_Jardin_botanique_de_la_Charme.jpg/500px-Platycodon_grandiflorus_in_Jardin_botanique_de_la_Charme.jpg"),
    551: ("Japanese Honeysuckle",      "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Honeysuckle-2.jpg/960px-Honeysuckle-2.jpg"),
    699: ("Ebony",                     "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Ebonytreeforest.jpg/960px-Ebonytreeforest.jpg"),
    825: ("Grains Of Paradise",        "https://upload.wikimedia.org/wikipedia/commons/0/03/%C3%91amako_gi_%28Aframomum_melegueta%29.jpg"),
    829: ("Cluster Cardamom",          "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/BlackCardamom.jpg/960px-BlackCardamom.jpg"),
    833: ("Fingerroot",                "https://upload.wikimedia.org/wikipedia/commons/9/9c/Temu_kunci.png"),
    839: ("Zedoary",                   "https://upload.wikimedia.org/wikipedia/commons/0/0e/Curcuma_zedoaria_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-048.jpg"),
    855: ("Biddy-Biddy",               "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Acaena_novae-zelandiae_1.jpg/960px-Acaena_novae-zelandiae_1.jpg"),
    867: ("Garden Strawberry",         "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Garden_strawberry_%28Fragaria_%C3%97_ananassa%29_single2.jpg/960px-Garden_strawberry_%28Fragaria_%C3%97_ananassa%29_single2.jpg"),
    875: ("Indian Physic",             "https://upload.wikimedia.org/wikipedia/commons/b/be/Gillenia_trifoliata1.jpg"),
    943: ("Timut",                     "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Zanthoxylum_planispinum_-_Villa_Taranto_%28Verbania%29_-_DSC03807.JPG/960px-Zanthoxylum_planispinum_-_Villa_Taranto_%28Verbania%29_-_DSC03807.JPG"),
    984: ("Bleeding Heart",            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Lamprocapnos_spectabilis_%281%29.jpg/500px-Lamprocapnos_spectabilis_%281%29.jpg"),
}

def download(url, dest):
    thumb = to_thumb_320(url)
    for attempt, u in enumerate([thumb, url]):
        try:
            r = requests.get(u, headers=HEADERS, timeout=30)
            r.raise_for_status()
            if HAS_PIL:
                img = Image.open(BytesIO(r.content)).convert("RGB")
                img.save(dest, "JPEG", quality=85)
            else:
                dest.write_bytes(r.content)
            return True, u
        except Exception as e:
            if attempt == 0 and "429" in str(e):
                time.sleep(3)
                continue
            print(f"    ERR: {e}")
            return False, u
    return False, url

conn = sqlite3.connect(DB)
conn.text_factory = lambda b: b.decode("utf-8", errors="replace")

ok = 0
fail = []
for row_id, (name, url) in sorted(FIXES.items()):
    fname = sanitize(name) + ".jpg"
    dest = DRAWABLE / fname
    if dest.exists() and dest.stat().st_size > 5000:
        print(f"  {row_id:4d}  {name:<35}  SKIP (exists)")
        continue
    print(f"  {row_id:4d}  {name:<35}", end="  ", flush=True)
    success, used_url = download(url, dest)
    if success:
        conn.execute("UPDATE museum_item SET full_image_uri=? WHERE id=?", (used_url, row_id))
        conn.commit()
        print("OK")
        ok += 1
    else:
        fail.append((row_id, name))
    time.sleep(2)

conn.close()
print(f"\nDone: {ok} new OK. Failed: {len(fail)}")
if fail:
    print("Failed:", [f"{i} {n}" for i,n in fail])
