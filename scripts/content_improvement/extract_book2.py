"""
extract_book2.py — Extract plant entries from:
  "36 Healing Herbs - The World's Best Medicinal Plants" (National Geographic, 2012)

Structure per plant:
  Common Name (e.g. "Aloe")
  Scientific Name (e.g. "Aloe vera")
  Narrative intro paragraphs
  Therapeutic Uses
  [list of conditions]
  How to Use
  [dosage/form details]
  Precautions (optional)

Output: extracted_book2.jsonl

Usage:
  python extract_book2.py
  python extract_book2.py --pdf "path/to/book.pdf" --out extracted_book2.jsonl
"""

import re
import json
import argparse
import sys
import fitz  # pymupdf

BOOK_PATH = (
    r"H:\Downloads\36 Healing Herbs - The World's Best Medicinal Plants"
    r"\36 Healing Herbs - The World's Best Medicinal Plants.pdf"
)
DEFAULT_OUT = "extracted_book2.jsonl"

# Scientific name: first Genus species from a line (may have multiple species, comma-sep)
# Also handles hybrids like "Mentha x piperita" (x = 1 char)
SCIENTIFIC_NAME_RE = re.compile(
    r"^([A-Z][a-z]+(?:\s+[a-z×x][a-z-]*){1,3})(?:,.*)?$"
)

# Common name: 1-5 title-case words, allows periods (St.) and apostrophes (straight + curly)
COMMON_NAME_RE = re.compile(
    r"^([A-Z][a-zA-Z'\u2019.-]+(?:\s+[A-Za-z'\u2019.-]+){0,4})\s*$"
)

SECTION_MARKERS = [
    "Therapeutic Uses",
    "How to Use",
    "Precautions",
    "Cautions",
    "Safety",
    "Dosage",
]

# Words/phrases that look like plant names but aren't
NOT_PLANT_NAMES = {
    "Therapeutic Uses", "How to Use", "Precautions", "Cautions", "Safety",
    "Dosage", "Cover", "Title Page", "Copyright", "Contents", "Foreword",
    "About the Author", "A Note to Readers", "The World of Medicinal Herbs",
    "Infusion", "Decoction", "Syrup", "Powder", "Tincture", "Capsule",
    "Cream", "Tablet", "Extract", "References", "Index", "Introduction",
    "Fresh", "Dried", "Standardized", "Warning", "Note", "Research",
    "Studies", "Clinical", "Traditional", "Modern", "History",
}

# Lines to skip (TOC entries, page artifacts)
SKIP_LINE_RE = re.compile(
    r"^(Cover|Title Page|Copyright|Contents|Foreword|About the Author|"
    r"A Note to Readers|The World of Medicinal Herbs)\s*$"
)


def clean(t):
    t = re.sub(r"-\n", "", t)
    t = re.sub(r"\n+", " ", t)
    t = re.sub(r"\s{2,}", " ", t)
    return t.strip()


def extract_section(text, marker):
    idx = text.find(marker)
    if idx == -1:
        return ""
    start = idx + len(marker)
    end = len(text)
    for other in SECTION_MARKERS:
        if other == marker:
            continue
        j = text.find(other, start)
        if j != -1 and j < end:
            end = j
    return text[start:end].strip()


def find_plant_boundaries(pages_text):
    """
    Scan all pages for the (common_name, scientific_name) pair pattern.
    Returns list of dicts: {page, common_name, scientific_name}
    """
    plants = []
    total = len(pages_text)

    for page_idx in range(total):
        lines = [l.rstrip() for l in pages_text[page_idx].splitlines() if l.strip()]
        # Only check the first 6 non-empty lines of each page — plant headings are at page tops
        for i, line in enumerate(lines[:6]):
            if SKIP_LINE_RE.match(line):
                continue
            cm = COMMON_NAME_RE.match(line)
            if not cm:
                continue
            common = cm.group(1).strip()
            if common in NOT_PLANT_NAMES:
                continue
            # Scientific name should be within next 3 lines
            for j in range(i + 1, min(i + 5, len(lines))):
                sm = SCIENTIFIC_NAME_RE.match(lines[j])
                if sm:
                    # Take only first species if multiple (e.g. "Echinacea purpurea, E. angustifolia")
                    sci = sm.group(1).strip().split(",")[0].strip()
                    parts = sci.split()
                    if len(parts) >= 2 and parts[1][0].islower():
                        plants.append({
                            "page": page_idx,
                            "common_name": common,
                            "scientific_name": sci,
                        })
                    break

    # Deduplicate: keep first occurrence of each scientific name
    seen = set()
    unique = []
    for p in plants:
        key = p["scientific_name"]
        if key not in seen:
            seen.add(key)
            unique.append(p)

    return unique


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", default=BOOK_PATH)
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args()

    print(f"Opening: {args.pdf}")
    doc = fitz.open(args.pdf)
    total_pages = len(doc)
    print(f"Total pages: {total_pages}")

    pages_text = [doc[i].get_text() for i in range(total_pages)]

    boundaries = find_plant_boundaries(pages_text)
    print(f"Found {len(boundaries)} plant entries")

    if not boundaries:
        print("ERROR: No plants found. Check PDF or adjust regex.")
        sys.exit(1)

    plants = []
    for i, loc in enumerate(boundaries):
        start_page = loc["page"]
        end_page = boundaries[i + 1]["page"] if i + 1 < len(boundaries) else total_pages

        chunks = [pages_text[p] for p in range(start_page, end_page)]
        full_text = "\n".join(chunks)

        # Trim to start at the common name
        idx = full_text.find(loc["common_name"])
        if idx != -1:
            full_text = full_text[idx:]

        # Intro = text after scientific name line, before first section marker
        sci_idx = full_text.find(loc["scientific_name"])
        if sci_idx != -1:
            intro_start = sci_idx + len(loc["scientific_name"])
        else:
            intro_start = len(loc["common_name"])
        intro_end = len(full_text)
        for m in SECTION_MARKERS:
            j = full_text.find(m, intro_start)
            if j != -1 and j < intro_end:
                intro_end = j
        intro = full_text[intro_start:intro_end]

        therapeutic_uses = extract_section(full_text, "Therapeutic Uses")
        how_to_use = extract_section(full_text, "How to Use")
        precautions = extract_section(full_text, "Precautions") or extract_section(full_text, "Cautions")

        # Parse therapeutic uses into a list (each non-empty line is a condition)
        uses_list = [
            l.strip() for l in therapeutic_uses.splitlines()
            if l.strip() and len(l.strip()) > 2
        ]

        plants.append({
            "number": i + 1,
            "common_name": loc["common_name"],
            "scientific_name": loc["scientific_name"],
            "intro": clean(intro),
            "therapeutic_uses": uses_list,
            "how_to_use": clean(how_to_use),
            "precautions": clean(precautions),
            "full_text": clean(full_text),
            "page_start": start_page + 1,
            "source": "36 Healing Herbs - The World's Best Medicinal Plants (National Geographic, 2012)",
        })

    with open(args.out, "w", encoding="utf-8") as f:
        for p in plants:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    print(f"Wrote {len(plants)} plants to {args.out}")

    print("\n--- Preview (first 4 plants) ---")
    for p in plants[:4]:
        print(f"\n[{p['number']}] {p['common_name']} ({p['scientific_name']})")
        print(f"  Intro:     {p['intro'][:120]}...")
        print(f"  Uses:      {p['therapeutic_uses'][:5]}")
        print(f"  How to use:{p['how_to_use'][:80]}...")


if __name__ == "__main__":
    main()
