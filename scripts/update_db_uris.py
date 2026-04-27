# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import re, sqlite3
from pathlib import Path

DB = Path(r"C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db")

def to_thumb_320(url):
    m = re.match(r'(https://upload\.wikimedia\.org/wikipedia/[^/]+/thumb/[a-f0-9]/[a-f0-9]+/(.+?))/\d+px-', url)
    if m:
        return f"{m.group(1)}/320px-{m.group(2)}"
    m2 = re.match(r'(https://upload\.wikimedia\.org/wikipedia/([^/]+))/([a-f0-9]/[a-f0-9]+)/(.+)', url)
    if m2:
        base, wiki, hashes, fname = m2.group(1), m2.group(2), m2.group(3), m2.group(4)
        return f"{base}/thumb/{hashes}/{fname}/320px-{fname}"
    return url

FIXES = {
    186: "https://upload.wikimedia.org/wikipedia/commons/c/c4/Uncaria_tomentosa.png",
    216: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Starr_010209-0286_Scaevola_taccada.jpg/960px-Starr_010209-0286_Scaevola_taccada.jpg",
    242: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Oxalis_acetosella_LC0190.jpg/960px-Oxalis_acetosella_LC0190.jpg",
    243: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Serenoa_repens_USDA1.jpg/500px-Serenoa_repens_USDA1.jpg",
    257: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Apothekergarten_Seligenstadt_Rheum_Palmatum_Medizinalrhabarber2.jpg/960px-Apothekergarten_Seligenstadt_Rheum_Palmatum_Medizinalrhabarber2.jpg",
    259: "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Peninsula_Sandstone_Fynbos_-_KingProtea_-_Table_Mountain.JPG/960px-Peninsula_Sandstone_Fynbos_-_KingProtea_-_Table_Mountain.JPG",
    271: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Bergenia_crassifolia_a1.jpg/960px-Bergenia_crassifolia_a1.jpg",
    274: "https://upload.wikimedia.org/wikipedia/commons/0/05/Selaginella_lepidophylla_gruen.jpeg",
    275: "https://upload.wikimedia.org/wikipedia/commons/4/44/Quassia_amara_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-117.jpg",
    290: "https://upload.wikimedia.org/wikipedia/commons/6/6f/Fen_nettle_%28Urtica_dioica_ssp._galeopsifolia%29_-_geograph.org.uk_-_5423125.jpg",
    291: "https://upload.wikimedia.org/wikipedia/commons/6/6b/Nardostachys_jatamansi_rhizome_with_a_scale_to_asses_its_size_Photo_N_C_SHAH.jpg",
    292: "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Aloysia_citriodora_002.jpg/960px-Aloysia_citriodora_002.jpg",
    304: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Sommacco.jpg/960px-Sommacco.jpg",
    308: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Ajwain_%28Trachyspermum_ammi%29.jpg/500px-Ajwain_%28Trachyspermum_ammi%29.jpg",
    349: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Helichrysum_italicum_%28immortelle%29.JPG/960px-Helichrysum_italicum_%28immortelle%29.JPG",
    357: "https://upload.wikimedia.org/wikipedia/commons/b/bd/Illustration_Senecio_jacobaea.jpg",
    387: "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Achiote_pj.JPG/960px-Achiote_pj.JPG",
    400: "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Cynoglossum_officinale_W.jpg/960px-Cynoglossum_officinale_W.jpg",
    405: "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Echium_vulgare_L.jpg/960px-Echium_vulgare_L.jpg",
    421: "https://upload.wikimedia.org/wikipedia/commons/7/71/Pulmonaria_officinalis_800.jpg",
    438: "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Armoracia_rusticana.jpg/960px-Armoracia_rusticana.jpg",
    451: "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Isatis_tinctoria02.JPG/960px-Isatis_tinctoria02.JPG",
    470: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Bromelia_pinguin_%28as_Bromelia_fastuosa%29_-_Collectanea_botanica_-_Lindley_pl._1_%281821%29.jpg/960px-Bromelia_pinguin_%28as_Bromelia_fastuosa%29_-_Collectanea_botanica_-_Lindley_pl._1_%281821%29.jpg",
    482: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Canarium_indicum_-_Icica_icicariba_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-171.jpg/500px-Canarium_indicum_-_Icica_icicariba_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-171.jpg",
    494: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Johann_Jacob_Haid_Cereus.jpg/960px-Johann_Jacob_Haid_Cereus.jpg",
    502: "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Dikenli_%C4%B0ncir_%28Opuntia_ficus-indica%29_Gaziantep_Turkey.IMG_1104.jpg/960px-Dikenli_%C4%B0ncir_%28Opuntia_ficus-indica%29_Gaziantep_Turkey.IMG_1104.jpg",
    512: "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/%28MHNT%29_Calycanthus_floridus_-_Les_Martels%2C_Giroussens_Tarn.jpg/960px-%28MHNT%29_Calycanthus_floridus_-_Les_Martels%2C_Giroussens_Tarn.jpg",
    530: "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Platycodon_grandiflorus_in_Jardin_botanique_de_la_Charme.jpg/500px-Platycodon_grandiflorus_in_Jardin_botanique_de_la_Charme.jpg",
    551: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Honeysuckle-2.jpg/960px-Honeysuckle-2.jpg",
    577: "https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Viburnum_prunifolium_USDA1.jpg/960px-Viburnum_prunifolium_USDA1.jpg",
    637: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Rhodiola_rosea_a2.jpg/960px-Rhodiola_rosea_a2.jpg",
    639: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Sedum_telephium_240808e.jpg/960px-Sedum_telephium_240808e.jpg",
    677: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Cyperus_longus_Ypey52.jpg/960px-Cyperus_longus_Ypey52.jpg",
    679: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Schoenus_nigricans_kz2.jpg/960px-Schoenus_nigricans_kz2.jpg",
    683: "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Daphne_odora-ja01.jpg/960px-Daphne_odora-ja01.jpg",
    685: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Datisca_cannabina_002.JPG/960px-Datisca_cannabina_002.JPG",
    693: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Dioscorea_mexicana.jpg/960px-Dioscorea_mexicana.jpg",
    699: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Ebonytreeforest.jpg/960px-Ebonytreeforest.jpg",
    715: "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/20250704_Ephedra_major.jpg/500px-20250704_Ephedra_major.jpg",
    717: "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Ephedra-nevadensis-cones.jpg/960px-Ephedra-nevadensis-cones.jpg",
    731: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Baccharis_pilularis_kz04.jpg/960px-Baccharis_pilularis_kz04.jpg",
    739: "https://upload.wikimedia.org/wikipedia/commons/7/7e/Cacalia_atriplicifolia_flower.jpg",
    757: "https://upload.wikimedia.org/wikipedia/commons/8/87/Cnicus_benedictus_flor.jpg",
    769: "https://upload.wikimedia.org/wikipedia/commons/2/23/Calamintha_nepeta_nepeta0.jpg",
    773: "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Dracocephalum_moldavica_inflorescence.jpg/960px-Dracocephalum_moldavica_inflorescence.jpg",
    801: "https://upload.wikimedia.org/wikipedia/commons/4/4a/Ammi_visnaga_-_Toothpick-plant_-_Tandstikurt_%2851157555303%29.jpg",
    813: "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Torilis_arvensis.jpg/960px-Torilis_arvensis.jpg",
    829: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/BlackCardamom.jpg/960px-BlackCardamom.jpg",
    833: "https://upload.wikimedia.org/wikipedia/commons/9/9c/Temu_kunci.png",
    847: "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Curtis%27s_botanical_magazine_%288294309208%29.jpg/960px-Curtis%27s_botanical_magazine_%288294309208%29.jpg",
    849: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Xanthorhiza_simplicissima_kz13.jpg/500px-Xanthorhiza_simplicissima_kz13.jpg",
    851: "https://upload.wikimedia.org/wikipedia/en/5/53/Labisia_pumila_grown_in_a_nursery.jpg",
    855: "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Acaena_novae-zelandiae_1.jpg/960px-Acaena_novae-zelandiae_1.jpg",
    859: "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Agrimonia_procera_002.JPG/960px-Agrimonia_procera_002.JPG",
    865: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Illustration_Agrimonia_eupatoria0.jpg/960px-Illustration_Agrimonia_eupatoria0.jpg",
    867: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Garden_strawberry_%28Fragaria_%C3%97_ananassa%29_single2.jpg/960px-Garden_strawberry_%28Fragaria_%C3%97_ananassa%29_single2.jpg",
    869: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Fragaria_moschata_detail.JPG/960px-Fragaria_moschata_detail.JPG",
    875: "https://upload.wikimedia.org/wikipedia/commons/b/be/Gillenia_trifoliata1.jpg",
    877: "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Potentilla_alba_close-up.jpg/960px-Potentilla_alba_close-up.jpg",
    881: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Potentilla_erecta_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-248.jpg/960px-Potentilla_erecta_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-248.jpg",
    885: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Rubus_chamaemorus%2C_from_Troms%C3%B8%2C_August_2020.jpeg/960px-Rubus_chamaemorus%2C_from_Troms%C3%B8%2C_August_2020.jpeg",
    905: "https://upload.wikimedia.org/wikipedia/commons/9/9b/Cluster_bean-guar-Cyamopsis_psoralioides-Cyamopsis_tetragonolobus-TAMIL_NADU73.jpg",
    917: "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Actaea_rubra_kz03.jpg/960px-Actaea_rubra_kz03.jpg",
    918: "https://upload.wikimedia.org/wikipedia/commons/e/e3/W_hukujusou3021.jpg",
    927: "https://upload.wikimedia.org/wikipedia/commons/f/fd/Erect_Clematis.jpg",
    935: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Oranges_-_whole-halved-segment.jpg/960px-Oranges_-_whole-halved-segment.jpg",
    938: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Rutaceae_sp_SZ21_clean.png/960px-Rutaceae_sp_SZ21_clean.png",
    943: "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Zanthoxylum_planispinum_-_Villa_Taranto_%28Verbania%29_-_DSC03807.JPG/960px-Zanthoxylum_planispinum_-_Villa_Taranto_%28Verbania%29_-_DSC03807.JPG",
    957: "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Duboisia_hopwoodii.jpg/960px-Duboisia_hopwoodii.jpg",
    971: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Solanum_2.JPG/960px-Solanum_2.JPG",
    980: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Corydalis_solida_240406.jpg/960px-Corydalis_solida_240406.jpg",
    982: "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Dicentra_cucullaria_-_Dutchmans_Breeches_2.jpg/960px-Dicentra_cucullaria_-_Dutchmans_Breeches_2.jpg",
    984: "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Lamprocapnos_spectabilis_%281%29.jpg/500px-Lamprocapnos_spectabilis_%281%29.jpg",
}

conn = sqlite3.connect(DB)
conn.text_factory = lambda b: b.decode("utf-8", errors="replace")
updated = 0
for row_id, url in FIXES.items():
    thumb = to_thumb_320(url)
    conn.execute("UPDATE museum_item SET full_image_uri=? WHERE id=?", (thumb, row_id))
    updated += 1
conn.commit()
conn.close()
print(f"Updated {updated} DB rows with 320px thumb URLs")
