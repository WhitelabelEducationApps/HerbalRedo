"""
Fill missing drawable images for museum_item entries.

Fallback chain per plant (stops at first success):
  1. Stored full_image_uri
  2. Wikipedia article thumbnail  (no key)
  3. iNaturalist                  (no key)
  4. GBIF media                   (no key)
  5. Wikimedia Commons search     (no key)
  6. Encyclopedia of Life (EOL)   (no key)
  7. Google Custom Search         (optional: GOOGLE_API_KEY + GOOGLE_CX env vars)
  8. Unsplash                     (optional: UNSPLASH_KEY env var)

Usage:
    python scripts/fill_missing_drawables.py [--dry-run] [--check-only] [--workers N]

Optional env vars for paid/keyed sources:
    GOOGLE_API_KEY   Google Custom Search API key
    GOOGLE_CX        Google Custom Search engine CX id
    UNSPLASH_KEY     Unsplash Access Key
"""

import os
import re
import sys
import time
import sqlite3
import argparse
import threading
import requests
from io import BytesIO
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "androidApp" / "src" / "main" / "assets" / "plants.db"
DRAWABLE_DIR = ROOT / "androidApp" / "src" / "main" / "res" / "drawable-nodpi"

HEADERS = {
    "User-Agent": (
        "HerbalRedo-App/1.0 (Educational medicinal plant database; "
        "contact: rsavutiu@gmail.com)"
    )
}
TIMEOUT = 15

# ── Optional API keys from environment ────────────────────────────────────────
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GOOGLE_CX      = os.environ.get("GOOGLE_CX", "")
UNSPLASH_KEY   = os.environ.get("UNSPLASH_KEY", "")

# ── Per-source rate limiters (token bucket style via lock + sleep) ─────────────
_rate_locks: dict[str, threading.Lock] = {}
_rate_last:  dict[str, float] = {}

def _rate_wait(source: str, interval: float) -> None:
    lock = _rate_locks.setdefault(source, threading.Lock())
    with lock:
        now = time.monotonic()
        wait = interval - (now - _rate_last.get(source, 0.0))
        if wait > 0:
            time.sleep(wait)
        _rate_last[source] = time.monotonic()


# ── Naming convention (mirrors StringUtils.kt) ────────────────────────────────
def sanitize(name: str) -> str:
    s = re.sub(r"[^a-z0-9]", "", name.lower())
    return ("a" + s) if s and s[0].isdigit() else s


# Wikimedia URLs that are PDF/DJVU page thumbnails, not actual plant photos
_PDF_PATTERNS = re.compile(
    r"(\.pdf\.jpg|\.djvu\.jpg|\.pdf/page|/page\d+-\d+px-.*\.pdf|\.pdf\.png)",
    re.IGNORECASE,
)

def is_pdf_thumbnail(url: str) -> bool:
    """Return True if the URL is a scanned book/PDF page, not a plant photo."""
    return bool(_PDF_PATTERNS.search(url))


# Binomial name patterns to try in order
_BINOMIAL_FROM_PARENS = re.compile(r"\(([A-Z][a-z]+(?:\s+[a-z]+){1,2})\)")
_BINOMIAL_ITALIC      = re.compile(r"\*([A-Z][a-z]+ [a-z]+)")   # *Genus species*
_BINOMIAL_PLAIN       = re.compile(r"\b([A-Z][a-z]+ [a-z]{3,})\b")  # first occurrence

def extract_scientific(name: str, description: str = "") -> list[str]:
    """
    Return candidate scientific names, best-first:
      1. Binomial in parentheses in paintingname  e.g. "Alfalfa (Medicago sativa)"
      2. Italic markdown in description            e.g. "*Ajuga reptans L.*"
      3. Parenthesised binomial in description
      4. First plain binomial in description
    Deduped, capped at 3 candidates.
    """
    candidates: list[str] = []

    def _add(m: re.Match) -> None:
        val = m.group(1).split()[0:2]  # keep only Genus species (drop author)
        if len(val) == 2:
            candidates.append(" ".join(val))

    for m in _BINOMIAL_FROM_PARENS.finditer(name):
        _add(m)
    for m in _BINOMIAL_ITALIC.finditer(description):
        _add(m)
    for m in _BINOMIAL_FROM_PARENS.finditer(description):
        _add(m)
    for m in _BINOMIAL_PLAIN.finditer(description):
        _add(m)
        break  # only first plain occurrence

    seen: set[str] = set()
    unique = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique[:3]


# ── HTTP helpers ──────────────────────────────────────────────────────────────
def check_uri(url: str) -> bool:
    """Return True only if the URL is reachable AND is not a PDF/DJVU page thumbnail."""
    if not url or is_pdf_thumbnail(url):
        return False
    try:
        r = requests.head(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        if r.status_code == 200:
            return True
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True)
        return r.status_code == 200
    except Exception:
        return False


def download_image(url: str) -> bytes | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        return r.content
    except Exception:
        return None


def to_jpeg(data: bytes) -> bytes | None:
    if not HAS_PIL:
        return data
    try:
        img = Image.open(BytesIO(data)).convert("RGB")
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return buf.getvalue()
    except Exception:
        return None


# ── Source 1: Stored URI (handled in process_row) ────────────────────────────

# ── Source 2: Wikipedia article thumbnail ────────────────────────────────────
def search_wikipedia_thumb(query: str) -> str | None:
    _rate_wait("wikipedia", 0.25)
    try:
        r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "titles": query,
                "prop": "pageimages",
                "pithumbsize": 500,
                "format": "json",
            },
            headers=HEADERS, timeout=TIMEOUT,
        )
        r.raise_for_status()
        for page in r.json().get("query", {}).get("pages", {}).values():
            thumb = page.get("thumbnail", {}).get("source")
            if thumb:
                return thumb
    except Exception:
        pass
    return None


# ── Source 3: iNaturalist ─────────────────────────────────────────────────────
def search_inaturalist(query: str) -> str | None:
    _rate_wait("inaturalist", 0.5)
    try:
        r = requests.get(
            "https://api.inaturalist.org/v1/taxa",
            params={"q": query, "rank": "species,genus", "per_page": 3, "locale": "en"},
            headers=HEADERS, timeout=TIMEOUT,
        )
        r.raise_for_status()
        for taxon in r.json().get("results", []):
            photo = taxon.get("default_photo") or {}
            url = photo.get("medium_url") or photo.get("square_url")
            if url:
                return url
    except Exception:
        pass
    return None


# ── Source 4: GBIF media ──────────────────────────────────────────────────────
def search_gbif(query: str) -> str | None:
    _rate_wait("gbif", 0.3)
    try:
        # Step 1: species match
        r = requests.get(
            "https://api.gbif.org/v1/species/match",
            params={"name": query, "verbose": False},
            headers=HEADERS, timeout=TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        usage_key = data.get("usageKey") or data.get("speciesKey")
        if not usage_key:
            return None

        _rate_wait("gbif", 0.3)
        # Step 2: fetch media
        r2 = requests.get(
            f"https://api.gbif.org/v1/species/{usage_key}/media",
            params={"limit": 5},
            headers=HEADERS, timeout=TIMEOUT,
        )
        r2.raise_for_status()
        for item in r2.json().get("results", []):
            url = item.get("identifier")
            if url and item.get("type") == "StillImage":
                return url
    except Exception:
        pass
    return None


# ── Source 5: Wikimedia Commons search ────────────────────────────────────────
def search_wikimedia(query: str) -> str | None:
    _rate_wait("wikimedia", 0.5)
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": f"{query} plant",
                "srlimit": 5,
                "srnamespace": 6,
                "format": "json",
            },
            headers=HEADERS, timeout=TIMEOUT,
        )
        r.raise_for_status()
        for result in r.json().get("query", {}).get("search", []):
            title = result.get("title", "")
            if not title:
                continue
            _rate_wait("wikimedia", 0.3)
            info = requests.get(
                "https://commons.wikimedia.org/w/api.php",
                params={
                    "action": "query",
                    "titles": title,
                    "prop": "imageinfo",
                    "iiprop": "url",
                    "iiurlwidth": 500,
                    "format": "json",
                },
                headers=HEADERS, timeout=TIMEOUT,
            )
            info.raise_for_status()
            for page in info.json().get("query", {}).get("pages", {}).values():
                for ii in page.get("imageinfo", []):
                    url = ii.get("thumburl") or ii.get("url")
                    if url:
                        return url
    except Exception:
        pass
    return None


# ── Source 6: Encyclopedia of Life (EOL) ─────────────────────────────────────
def search_eol(query: str) -> str | None:
    _rate_wait("eol", 0.5)
    try:
        r = requests.get(
            "https://eol.org/api/search/1.0.json",
            params={"q": query, "page": 1, "exact": False},
            headers=HEADERS, timeout=TIMEOUT,
        )
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results:
            return None

        eol_id = results[0].get("id")
        if not eol_id:
            return None

        _rate_wait("eol", 0.5)
        r2 = requests.get(
            f"https://eol.org/api/pages/1.0/{eol_id}.json",
            params={"images": 1, "videos": 0, "sounds": 0, "maps": 0, "text": 0,
                    "details": True, "common_names": False},
            headers=HEADERS, timeout=TIMEOUT,
        )
        r2.raise_for_status()
        for obj in r2.json().get("dataObjects", []):
            if obj.get("dataType") == "http://purl.org/dc/dcmitype/StillImage":
                url = obj.get("eolMediaURL") or obj.get("mediaURL")
                if url:
                    return url
    except Exception:
        pass
    return None


# ── Source 7: Google Custom Search (optional) ─────────────────────────────────
def search_google(query: str) -> str | None:
    if not GOOGLE_API_KEY or not GOOGLE_CX:
        return None
    _rate_wait("google", 0.2)
    try:
        r = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "key": GOOGLE_API_KEY,
                "cx": GOOGLE_CX,
                "q": f"{query} plant",
                "searchType": "image",
                "num": 3,
                "imgType": "photo",
                "safe": "active",
            },
            headers=HEADERS, timeout=TIMEOUT,
        )
        r.raise_for_status()
        for item in r.json().get("items", []):
            url = item.get("link")
            if url:
                return url
    except Exception:
        pass
    return None


# ── Source 8: Unsplash (optional) ────────────────────────────────────────────
def search_unsplash(query: str) -> str | None:
    if not UNSPLASH_KEY:
        return None
    _rate_wait("unsplash", 0.1)
    try:
        r = requests.get(
            "https://api.unsplash.com/search/photos",
            params={"query": f"{query} plant", "per_page": 3, "orientation": "squarish"},
            headers={**HEADERS, "Authorization": f"Client-ID {UNSPLASH_KEY}"},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        results = r.json().get("results", [])
        if results:
            urls = results[0].get("urls", {})
            return urls.get("regular") or urls.get("small")
    except Exception:
        pass
    return None


# ── Fallback chain ────────────────────────────────────────────────────────────
SOURCES = [
    ("wikipedia",   search_wikipedia_thumb),
    ("inaturalist", search_inaturalist),
    ("gbif",        search_gbif),
    ("wikimedia",   search_wikimedia),
    ("eol",         search_eol),
    ("google",      search_google),
    ("unsplash",    search_unsplash),
]


def find_image(paintingname: str, description: str = "") -> tuple[str | None, str]:
    """Try all sources, returning (url, source_name) or (None, '')."""
    # Common name stripped of parenthetical, e.g. "Alfalfa"
    common = re.sub(r"\s*\(.*\)", "", paintingname).strip()
    # Scientific names extracted from name + description, best-first
    scientific_names = extract_scientific(paintingname, description)

    # Query order: scientific names first (more precise), then common name
    queries: list[str] = []
    queries.extend(scientific_names)
    if common not in queries:
        queries.append(common)

    for source_name, fn in SOURCES:
        for q in queries:
            url = fn(q)
            if url:
                return url, source_name

    return None, ""


# ── Per-row processing ────────────────────────────────────────────────────────
def process_row(row, drawable_dir: Path, dry_run: bool, check_only: bool) -> dict:
    row_id, paintingname, full_image_uri, description = row
    filename = sanitize(paintingname) + ".jpg"
    dest = drawable_dir / filename

    result = {
        "id": row_id,
        "name": paintingname,
        "filename": filename,
        "status": None,
        "uri_ok": None,
        "source": "",
        "note": "",
    }

    uri_ok = check_uri(full_image_uri) if full_image_uri else False
    if full_image_uri and is_pdf_thumbnail(full_image_uri):
        result["note"] = "pdf-thumbnail"
    result["uri_ok"] = uri_ok

    if dest.exists():
        result["status"] = "exists"
        return result

    if check_only:
        result["status"] = "missing"
        return result

    if dry_run:
        result["status"] = "skipped"
        return result

    # Try stored URI first
    image_data = None
    if uri_ok and full_image_uri:
        image_data = download_image(full_image_uri)
        if image_data:
            result["source"] = "stored_uri"

    # Work through fallback chain
    if image_data is None:
        url, source = find_image(paintingname, description or "")
        if url:
            image_data = download_image(url)
            result["source"] = source
            result["note"] = url[:80]

    if image_data:
        jpeg = to_jpeg(image_data)
        if jpeg:
            dest.write_bytes(jpeg)
            result["status"] = "downloaded"
        else:
            result["status"] = "failed"
            result["note"] = "image conversion error"
    else:
        result["status"] = "failed"
        result["note"] = "all sources exhausted"

    return result


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run",    action="store_true",
                        help="Report what would happen without saving any files")
    parser.add_argument("--check-only", action="store_true",
                        help="Only audit missing files and URI health, no downloads")
    parser.add_argument("--workers",   type=int, default=4,
                        help="Parallel download threads (default: 4)")
    args = parser.parse_args()

    if not HAS_PIL:
        print("WARNING: Pillow not installed — images saved as-is (format not guaranteed).")
        print("         pip install Pillow\n")

    if not DB_PATH.exists():
        sys.exit(f"DB not found: {DB_PATH}")
    if not DRAWABLE_DIR.exists():
        sys.exit(f"Drawable dir not found: {DRAWABLE_DIR}")

    enabled_keys = []
    if GOOGLE_API_KEY and GOOGLE_CX:
        enabled_keys.append("Google CSE")
    if UNSPLASH_KEY:
        enabled_keys.append("Unsplash")
    if enabled_keys:
        print(f"Keyed sources active: {', '.join(enabled_keys)}")
    else:
        print("Keyed sources: none (set GOOGLE_API_KEY+GOOGLE_CX or UNSPLASH_KEY to enable)")

    conn = sqlite3.connect(DB_PATH)
    conn.text_factory = lambda b: b.decode("utf-8", errors="replace")
    rows = conn.execute(
        "SELECT id, paintingname, full_image_uri, description FROM museum_item ORDER BY id"
    ).fetchall()
    conn.close()

    total = len(rows)
    existing = sum(1 for _, n, *_ in rows if (DRAWABLE_DIR / (sanitize(n) + ".jpg")).exists())
    print(f"\nDB rows: {total}  |  Already have: {existing}  |  Missing: {total - existing}")

    if args.check_only:
        print("Mode: CHECK-ONLY\n")
    elif args.dry_run:
        print("Mode: DRY-RUN\n")

    counters: dict[str, int] = {"exists": 0, "downloaded": 0, "failed": 0,
                                 "skipped": 0, "missing": 0}
    source_counts: dict[str, int] = {}
    failures: list[tuple] = []
    uri_broken: list[tuple] = []

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(process_row, row, DRAWABLE_DIR, args.dry_run, args.check_only): row
            for row in rows
        }
        done = 0
        for future in as_completed(futures):
            done += 1
            res = future.result()
            counters[res["status"]] += 1

            if res["status"] == "downloaded" and res["source"]:
                source_counts[res["source"]] = source_counts.get(res["source"], 0) + 1

            if not res["uri_ok"] and res["status"] != "exists":
                uri_broken.append((res["id"], res["name"]))

            if res["status"] == "failed":
                failures.append((res["id"], res["name"], res["note"]))

            if done % 25 == 0 or done == total:
                pct = done * 100 // total
                print(
                    f"  [{pct:3d}%] {done}/{total}  "
                    f"ok={counters['downloaded']}  "
                    f"failed={counters['failed']}  "
                    f"uri_broken={len(uri_broken)}",
                    end="\r",
                )

    print()
    print("\n── Summary ──────────────────────────────────────────────────────")
    print(f"  Total rows    : {total}")
    print(f"  Already exist : {counters['exists']}")
    print(f"  Downloaded    : {counters['downloaded']}")
    print(f"  Failed        : {counters['failed']}")
    print(f"  URI broken    : {len(uri_broken)}")

    if source_counts:
        print("\n── Downloads by source ──────────────────────────────────────────")
        for src, count in sorted(source_counts.items(), key=lambda x: -x[1]):
            print(f"  {src:<20} {count}")

    if uri_broken:
        print("\n── Broken stored URIs ───────────────────────────────────────────")
        for row_id, name in uri_broken[:30]:
            print(f"  id={row_id:4d}  {name[:55]}")
        if len(uri_broken) > 30:
            print(f"  ... and {len(uri_broken) - 30} more")

    if failures:
        print("\n── All-sources failures ─────────────────────────────────────────")
        for row_id, name, note in failures[:20]:
            print(f"  id={row_id:4d}  {name[:50]}  [{note[:50]}]")
        if len(failures) > 20:
            print(f"  ... and {len(failures) - 20} more")

    print()


if __name__ == "__main__":
    main()
