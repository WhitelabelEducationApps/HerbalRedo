# -*- coding: utf-8 -*-
"""
Batch image fixer for plants with PDF/DJVU thumbnails or missing URIs.
Queries Wikipedia pageimages API, then Wikimedia Commons search.
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import re
import sqlite3
import time
import requests
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

HEADERS = {
    "User-Agent": "HerbalRedo/1.0 (medicinal plant app; educational use)"
}

PDF_RE = re.compile(
    r"(\.pdf\.jpg|\.djvu\.jpg|\.pdf/page|/page\d+-\d+px-.*\.pdf|\.pdf\.png|\.pdf\.jpeg)",
    re.IGNORECASE,
)

WIKI_API = "https://en.wikipedia.org/w/api.php"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"

# Map plant common names to their Wikipedia article titles (for tricky ones)
WIKI_TITLE_MAP = {
    "Licorice": "Liquorice",
    "Cat's Claw": "Cat's claw (Uncaria tomentosa)",
    "Asian Ginseng": "Panax ginseng",
    "Scaevola": "Scaevola (plant)",
    "Saw Palmetto": "Serenoa repens",
    "Bistort": "Persicaria bistorta",
    "Protea": "Protea (plant)",
    "Resurrection Plant": "Selaginella lepidophylla",
    "Quassia": "Quassia amara",
    "Bladdernut": "Staphylea",
    "Benzoin": "Styrax benzoin",
    "Damiana": "Turnera diffusa",
    "Slippery Elm": "Ulmus rubra",
    "Stinging Nettle": "Urtica dioica",
    "Spikenard": "Nardostachys jatamansi",
    "Lemon Verbena": "Aloysia citrodora",
    "Narrow-leaved Coneflower": "Echinacea angustifolia",
    "Immortelle": "Helichrysum italicum",
    "Blackhaw": "Viburnum prunifolium",
    "Yerba Mate": "Ilex paraguariensis",
    "Roseroot": "Rhodiola rosea",
    "Orpine": "Hylotelephium telephium",
    "Galingale": "Cyperus longus",
    "Black Bog Rush": "Schoenus nigricans",
    "Winter Daphne": "Daphne odora",
    "False Hemp": "Datisca cannabina",
    "Mexican Yam": "Dioscorea mexicana",
    "Major Ephedra": "Ephedra major",
    "Nevada Ephedra": "Ephedra nevadensis",
    "Coyote Brush": "Baccharis pilularis",
    "Pale Indian Plantain": "Arnoglossum atriplicifolium",
    "Blessed Thistle": "Cnicus benedictus",
    "Calamint": "Calamintha",
    "Moldavian Balm": "Dracocephalum moldavica",
    "Water Mint": "Mentha aquatica",
    "Ammi": "Ammi visnaga",
    "Spreading Hedge Parsley": "Torilis arvensis",
    "Lesser Galangal": "Alpinia officinarum",
    "Spiked Ginger Lily": "Hedychium spicatum",
    "Zanthorhiza": "Xanthorhiza simplicissima",
    "Kacip Fatimah": "Labisia pumila",
    "Fragrant Agrimony": "Agrimonia procera",
    "Common Lady's Mantle": "Alchemilla vulgaris",
    "Bastard Agrimony": "Agrimonia eupatoria",
    "Musk Strawberry": "Fragaria moschata",
    "White Cinquefoil": "Potentilla alba",
    "Tormentil": "Potentilla erecta",
    "Cloudberry": "Rubus chamaemorus",
    "Blackberry": "Rubus fruticosus",
    "Gum Acacia": "Acacia senegal",
    "Guar": "Cyamopsis tetragonoloba",
    "Red Baneberry": "Actaea rubra",
    "Amur Adonis": "Adonis amurensis",
    "Upright Clematis": "Clematis recta",
    "Grapefruit": "Citrus paradisi",
    "Sweet Orange": "Citrus sinensis",
    "Evodia": "Tetradium ruticarpum",
    "Pituri": "Duboisia hopwoodii",
    "Jasmine Nightshade": "Solanum jasminoides",
    "Solid-rooted Corydalis": "Corydalis solida",
    "Dutchman's Breeches": "Dicentra cucullaria",
    # Missing URI plants
    "Frankincense": "Boswellia sacra",
    "Ajowan": "Trachyspermum ammi",
    "Tansy Ragwort": "Jacobaea vulgaris",
    "Annatto": "Bixa orellana",
    "Hound's Tongue": "Cynoglossum officinale",
    "Viper's Bugloss": "Echium vulgare",
    "Gromwell": "Lithospermum officinale",
    "Lungwort": "Pulmonaria officinalis",
    "Horseradish": "Armoracia rusticana",
    "Woad": "Isatis tinctoria",
    "Radish": "Raphanus sativus",
    "Pinguin": "Bromelia pinguin",
    "Elemi": "Canarium luzonicum",
    "Night-blooming Cereus": "Selenicereus grandiflorus",
    "Prickly Pear": "Opuntia ficus-indica",
    "Sweetshrub": "Calycanthus floridus",
    "Indian Tobacco": "Lobelia inflata",
    "Balloon Flower": "Platycodon grandiflorus",
    "Japanese Honeysuckle": "Lonicera japonica",
    "Ebony": "Diospyros ebenum",
    "Cnidium": "Cnidium monnieri",
    "Grains Of Paradise": "Aframomum melegueta",
    "Cluster Cardamom": "Amomum subulatum",
    "Fingerroot": "Boesenbergia rotunda",
    "Zedoary": "Curcuma zedoaria",
    "Biddy-Biddy": "Acaena novae-zelandiae",
    "Garden Strawberry": "Fragaria ananassa",
    "Indian Physic": "Porteranthus trifoliatus",
    "Timut": "Zanthoxylum armatum",
    "Bleeding Heart": "Lamprocapnos spectabilis",
}


def sanitize(name: str) -> str:
    s = re.sub(r"[^a-z0-9]", "", name.lower())
    return ("a" + s) if s and s[0].isdigit() else s


def is_pdf_thumbnail(url: str) -> bool:
    return bool(url and PDF_RE.search(url))


def get_wikipedia_image(title: str) -> str | None:
    """Query Wikipedia pageimages API for a thumbnail URL."""
    try:
        r = requests.get(WIKI_API, params={
            "action": "query",
            "titles": title,
            "prop": "pageimages",
            "pithumbsize": 600,
            "format": "json",
        }, headers=HEADERS, timeout=15)
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        for page in pages.values():
            thumb = page.get("thumbnail", {})
            if thumb:
                return thumb.get("source")
    except Exception as e:
        pass
    return None


def get_commons_image(query: str) -> str | None:
    """Search Wikimedia Commons for an image."""
    try:
        time.sleep(0.5)
        r = requests.get(COMMONS_API, params={
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srnamespace": 6,
            "srlimit": 5,
            "format": "json",
        }, headers=HEADERS, timeout=15)
        r.raise_for_status()
        results = r.json().get("query", {}).get("search", [])
        for result in results:
            title = result.get("title", "")
            if not title:
                continue
            time.sleep(0.3)
            info_r = requests.get(COMMONS_API, params={
                "action": "query",
                "titles": title,
                "prop": "imageinfo",
                "iiprop": "url",
                "iiurlwidth": 500,
                "format": "json",
            }, headers=HEADERS, timeout=15)
            info_r.raise_for_status()
            pages2 = info_r.json().get("query", {}).get("pages", {})
            for pg in pages2.values():
                imageinfo = pg.get("imageinfo", [])
                if imageinfo:
                    url = imageinfo[0].get("thumburl") or imageinfo[0].get("url")
                    if url and not is_pdf_thumbnail(url):
                        return url
    except Exception:
        pass
    return None


def find_image(plant_name: str) -> tuple[str | None, str]:
    """Returns (url, source_label) or (None, 'not found')."""
    wiki_title = WIKI_TITLE_MAP.get(plant_name, plant_name)

    # 1. Wikipedia pageimages API with mapped title
    url = get_wikipedia_image(wiki_title)
    if url and not is_pdf_thumbnail(url):
        return url, f"wiki:{wiki_title}"
    time.sleep(0.3)

    # 2. Wikipedia pageimages API with common name (if different)
    if wiki_title != plant_name:
        url = get_wikipedia_image(plant_name)
        if url and not is_pdf_thumbnail(url):
            return url, f"wiki:{plant_name}"
        time.sleep(0.3)

    # 3. Commons search with wiki title
    url = get_commons_image(f"{wiki_title} plant")
    if url and not is_pdf_thumbnail(url):
        return url, f"commons:{wiki_title}"

    return None, "not found"


def download_image(url: str, dest: Path) -> bool:
    """Download URL to dest as JPEG. Returns True on success."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        if HAS_PIL:
            img = Image.open(BytesIO(r.content)).convert("RGB")
            img.save(dest, "JPEG", quality=85)
        else:
            dest.write_bytes(r.content)
        return True
    except Exception as e:
        print(f"    ERROR downloading: {e}")
        return False


def main():
    conn = sqlite3.connect(DB)
    conn.text_factory = lambda b: b.decode("utf-8", errors="replace")

    pdf_ids = [144, 154, 186, 193, 216, 242, 243, 256, 257, 259, 267, 271, 274, 275, 277, 279, 286, 288, 290, 291, 292, 304, 344, 349, 577, 598, 637, 639, 677, 679, 683, 685, 693, 715, 717, 731, 739, 757, 769, 773, 787, 801, 813, 843, 847, 849, 851, 859, 863, 865, 869, 877, 881, 885, 887, 895, 905, 917, 918, 927, 934, 935, 938, 957, 971, 980, 982]
    missing_ids = [200, 308, 357, 387, 400, 405, 410, 421, 438, 451, 461, 470, 482, 494, 502, 512, 521, 530, 551, 699, 823, 825, 829, 833, 839, 855, 867, 875, 943, 984]
    all_ids = sorted(set(pdf_ids + missing_ids))

    placeholders = ",".join("?" * len(all_ids))
    rows = conn.execute(
        f"SELECT id, paintingname, full_image_uri FROM museum_item WHERE id IN ({placeholders}) ORDER BY id",
        all_ids
    ).fetchall()

    fixed = 0
    failed = []

    for row_id, name, current_uri in rows:
        fname = sanitize(name) + ".jpg"
        dest = DRAWABLE / fname
        already_exists = dest.exists()

        # Check if we even need to fix this
        if current_uri and not is_pdf_thumbnail(current_uri) and already_exists:
            print(f"  SKIP {row_id:4d}  {name}  (already ok)")
            continue

        print(f"  {row_id:4d}  {name:<40}", end="", flush=True)

        url, source = find_image(name)
        if url:
            if download_image(url, dest):
                conn.execute(
                    "UPDATE museum_item SET full_image_uri=? WHERE id=?",
                    (url, row_id)
                )
                conn.commit()
                print(f"  OK  [{source}]")
                fixed += 1
            else:
                print(f"  DOWNLOAD_FAIL  [{url[:60]}]")
                failed.append((row_id, name, "download_fail"))
        else:
            print(f"  NOT_FOUND")
            failed.append((row_id, name, "not_found"))

        time.sleep(0.5)

    conn.close()
    print(f"\nDone. Fixed: {fixed}/{len(rows)}. Failed: {len(failed)}")
    if failed:
        print("Failed plants:")
        for row_id, name, reason in failed:
            print(f"  {row_id:4d}  {name:<40}  {reason}")


if __name__ == "__main__":
    main()
