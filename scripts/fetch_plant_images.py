#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch additional plant images and convert all drawables to WebP.

Steps:
  1. Convert every .jpg in drawable-nodpi/ to .webp (≤100 KB), delete original.
  2. For each plant, fetch up to 5 extra images from Wikimedia Commons + iNaturalist.
     - Skip candidates that are visually similar to existing images (pHash, threshold=10).
     - Save as <baseName>_2.webp, _3.webp … up to _6.webp.

Usage:
  pip install requests Pillow imagehash
  python scripts/fetch_plant_images.py [--dry-run] [--plant "Aloe Vera"] [--convert-only]
"""

import argparse
import io
import json
import re
import sqlite3
import sys
import time
from io import BytesIO
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

try:
    from PIL import Image
except ImportError:
    sys.exit("Missing: pip install Pillow")

try:
    import imagehash
except ImportError:
    sys.exit("Missing: pip install imagehash")

try:
    import requests
except ImportError:
    sys.exit("Missing: pip install requests")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
ROOT       = Path(__file__).resolve().parent.parent
DB_PATH    = ROOT / "androidApp/src/main/assets/plants.db"
NODPI_DIR  = ROOT / "androidApp/src/main/res/drawable-nodpi"
CHECKPOINT = Path(__file__).parent / ".image_fetch_progress.json"

MAX_EXTRA_IMAGES = 5   # up to _2 … _6
MAX_KB           = 100
HASH_THRESHOLD   = 10  # 0=identical, 64=totally different; 10 catches crops/resizes of same photo
REQUEST_TIMEOUT  = 10
INTER_REQUEST_DELAY = 1.5  # seconds between HTTP calls

HEADERS = {"User-Agent": "HerbalRedo/1.0 (educational medicinal-plant app; contact: dev@herbal)"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def sanitize(name: str) -> str:
    s = re.sub(r"[^a-z0-9]", "", name.lower())
    return ("a" + s) if s and s[0].isdigit() else s


def save_webp(img: Image.Image, path: Path, max_kb: int = MAX_KB) -> bool:
    """Save PIL image as WebP, binary-searching quality to stay under max_kb."""
    lo, hi = 30, 90
    best_bytes = None
    while lo <= hi:
        mid = (lo + hi) // 2
        buf = BytesIO()
        img.save(buf, "WEBP", quality=mid, method=4)
        data = buf.getvalue()
        if len(data) <= max_kb * 1024:
            best_bytes = data
            lo = mid + 1
        else:
            hi = mid - 1
    if best_bytes is None:
        # Even quality=30 is too big — save at 30 anyway (edge case: huge image)
        buf = BytesIO()
        img.save(buf, "WEBP", quality=30, method=4)
        best_bytes = buf.getvalue()
    path.write_bytes(best_bytes)
    return True


def phash(img: Image.Image):
    return imagehash.phash(img)


def is_too_similar(candidate_hash, existing_hashes: list, threshold: int = HASH_THRESHOLD) -> bool:
    return any(abs(candidate_hash - h) < threshold for h in existing_hashes)


def fetch_image(url: str) -> Image.Image | None:
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            img = Image.open(BytesIO(r.content)).convert("RGB")
            # Reject tiny images
            if img.width < 300 or img.height < 300:
                return None
            return img
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                return None
    return None


# ---------------------------------------------------------------------------
# Phase 0: Convert existing JPGs to WebP
# ---------------------------------------------------------------------------
def convert_existing_jpgs(dry_run: bool) -> int:
    jpgs = list(NODPI_DIR.glob("*.jpg")) + list(NODPI_DIR.glob("*.jpeg"))
    print(f"\n[Phase 0] Converting {len(jpgs)} JPG(s) to WebP (≤{MAX_KB} KB)...")
    converted = 0
    for jpg in jpgs:
        webp_path = jpg.with_suffix(".webp")
        if dry_run:
            print(f"  DRY-RUN  {jpg.name}  →  {webp_path.name}")
            converted += 1
            continue
        try:
            img = Image.open(jpg).convert("RGB")
            save_webp(img, webp_path)
            size_kb = webp_path.stat().st_size // 1024
            print(f"  OK  {jpg.name}  →  {webp_path.name}  ({size_kb} KB)")
            jpg.unlink()
            converted += 1
        except Exception as e:
            print(f"  FAIL  {jpg.name}  →  {e}")
    print(f"  Converted: {converted}/{len(jpgs)}")
    return converted


# ---------------------------------------------------------------------------
# Image sources
# ---------------------------------------------------------------------------
def wikimedia_candidates(plant_name: str) -> list[str]:
    """Return up to 8 image URLs from Wikimedia Commons for the plant."""
    urls = []
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": f"{plant_name} plant",
                "gsrnamespace": "6",
                "gsrlimit": "12",
                "prop": "imageinfo",
                "iiprop": "url|size|mediatype|mime",
                "iiurlwidth": "600",
                "format": "json",
            },
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        for page in pages.values():
            info = (page.get("imageinfo") or [{}])[0]
            mime = info.get("mime", "")
            url  = info.get("thumburl") or info.get("url", "")
            w    = info.get("thumbwidth") or info.get("width", 0)
            # Accept jpeg/webp, reject SVG/PNG diagrams and tiny images
            if mime in ("image/jpeg", "image/webp") and w >= 300 and url:
                urls.append(url)
    except Exception as e:
        print(f"    [Wikimedia] error: {e}")
    time.sleep(INTER_REQUEST_DELAY)
    return urls[:8]


def inat_candidates(plant_name: str) -> list[str]:
    """Return up to 8 observation photo URLs from iNaturalist for the plant."""
    urls = []
    try:
        # 1. Find taxon ID
        r = requests.get(
            "https://api.inaturalist.org/v1/taxa",
            params={"q": plant_name, "rank": "species", "per_page": "1"},
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results:
            return []
        taxon_id = results[0]["id"]
        time.sleep(INTER_REQUEST_DELAY)

        # 2. Get research-grade observations with photos
        r2 = requests.get(
            "https://api.inaturalist.org/v1/observations",
            params={
                "taxon_id": taxon_id,
                "quality_grade": "research",
                "photos": "true",
                "per_page": "10",
                "order_by": "votes",
            },
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        r2.raise_for_status()
        for obs in r2.json().get("results", []):
            for photo in obs.get("photos", []):
                url = photo.get("url", "")
                # iNat URLs contain "square" (75px) — replace with "medium" (500px)
                url = url.replace("/square.", "/medium.")
                if url and url not in urls:
                    urls.append(url)
                if len(urls) >= 8:
                    break
            if len(urls) >= 8:
                break
    except Exception as e:
        print(f"    [iNaturalist] error: {e}")
    time.sleep(INTER_REQUEST_DELAY)
    return urls


# ---------------------------------------------------------------------------
# Phase 1: Fetch extra images per plant
# ---------------------------------------------------------------------------
def load_checkpoint() -> set:
    if CHECKPOINT.exists():
        return set(json.loads(CHECKPOINT.read_text()))
    return set()


def save_checkpoint(done: set):
    CHECKPOINT.write_text(json.dumps(sorted(done)))


def existing_images_for(base_name: str) -> list[Path]:
    """Return all existing images for this plant (primary + numbered variants)."""
    results = []
    primary = next(
        (NODPI_DIR / f"{base_name}{ext}" for ext in (".webp", ".jpg", ".jpeg", ".png")
         if (NODPI_DIR / f"{base_name}{ext}").exists()),
        None
    )
    if primary:
        results.append(primary)
    for i in range(2, 7):
        for ext in (".webp", ".jpg", ".jpeg"):
            p = NODPI_DIR / f"{base_name}_{i}{ext}"
            if p.exists():
                results.append(p)
                break
    return results


def next_slot(base_name: str) -> int | None:
    """Return next available numeric slot (2–6), or None if full."""
    for i in range(2, 7):
        taken = any(
            (NODPI_DIR / f"{base_name}_{i}{ext}").exists()
            for ext in (".webp", ".jpg", ".jpeg")
        )
        if not taken:
            return i
    return None


def fetch_extras_for_plant(plant_name: str, dry_run: bool) -> tuple[int, int]:
    """Download extra images for one plant. Returns (accepted, rejected)."""
    base_name = sanitize(plant_name)
    existing = existing_images_for(base_name)

    if not existing:
        print(f"  SKIP  {plant_name!r}  (no primary image found)")
        return 0, 0

    # Load existing hashes
    existing_hashes = []
    for p in existing:
        try:
            existing_hashes.append(phash(Image.open(p).convert("RGB")))
        except Exception:
            pass

    # How many more slots?
    slots_left = sum(
        1 for i in range(2, 7)
        if not any((NODPI_DIR / f"{base_name}_{i}{ext}").exists() for ext in (".webp", ".jpg"))
    )
    if slots_left == 0:
        print(f"  FULL  {plant_name!r}  (already has max images)")
        return 0, 0

    # Gather candidates from both sources
    print(f"  Fetching candidates for {plant_name!r}...")
    wiki_urls = wikimedia_candidates(plant_name)
    inat_urls = inat_candidates(plant_name)
    all_urls  = wiki_urls + inat_urls
    print(f"    sources: wikimedia={len(wiki_urls)}, inat={len(inat_urls)}")

    accepted = rejected = 0
    for url in all_urls:
        slot = next_slot(base_name)
        if slot is None:
            break

        img = fetch_image(url)
        if img is None:
            continue

        candidate_hash = phash(img)
        if is_too_similar(candidate_hash, existing_hashes):
            rejected += 1
            continue

        dest = NODPI_DIR / f"{base_name}_{slot}.webp"
        if dry_run:
            print(f"    DRY-RUN  slot={slot}  url={url[:80]}")
            accepted += 1
            existing_hashes.append(candidate_hash)
        else:
            try:
                save_webp(img, dest)
                size_kb = dest.stat().st_size // 1024
                print(f"    OK  _{slot}.webp  ({size_kb} KB)  {url[:70]}")
                existing_hashes.append(candidate_hash)
                accepted += 1
            except Exception as e:
                print(f"    FAIL  slot={slot}  {e}")

        time.sleep(INTER_REQUEST_DELAY)

    print(f"    → accepted={accepted}, too_similar={rejected}")
    return accepted, rejected


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Fetch + convert plant images")
    parser.add_argument("--dry-run",      action="store_true", help="Print actions, no writes")
    parser.add_argument("--plant",        type=str,            help="Process only this plant name")
    parser.add_argument("--convert-only", action="store_true", help="Only convert JPGs, skip fetching")
    args = parser.parse_args()

    if args.dry_run:
        print("*** DRY RUN — no files will be written ***\n")

    # Phase 0: Convert existing JPGs
    convert_existing_jpgs(args.dry_run)

    if args.convert_only:
        print("Done (convert-only mode).")
        return

    # Load plant list from DB
    conn = sqlite3.connect(DB_PATH)
    conn.text_factory = lambda b: b.decode("utf-8", errors="replace")
    plants = conn.execute("SELECT id, paintingname FROM museum_item ORDER BY id").fetchall()
    conn.close()

    if args.plant:
        plants = [(pid, name) for pid, name in plants
                  if name.lower() == args.plant.lower()]
        if not plants:
            sys.exit(f"Plant not found: {args.plant!r}")

    done = load_checkpoint()
    total_accepted = total_rejected = 0

    print(f"\n[Phase 1] Fetching extra images for {len(plants)} plants...\n")
    for pid, name in plants:
        key = f"{pid}:{name}"
        if key in done:
            print(f"  SKIP (checkpoint)  {name}")
            continue

        accepted, rejected = fetch_extras_for_plant(name, args.dry_run)
        total_accepted += accepted
        total_rejected += rejected

        if not args.dry_run:
            done.add(key)
            save_checkpoint(done)

    print(f"\n=== Done ===")
    print(f"Total accepted: {total_accepted}")
    print(f"Total rejected (too similar): {total_rejected}")


if __name__ == "__main__":
    main()
