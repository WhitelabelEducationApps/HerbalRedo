"""
extract_book1.py — Extract plant entries from:
  "A Guide to Medicinal Plants - An Illustrated, Scientific and Medicinal Approach"

Output: extracted_book1.jsonl — one JSON object per plant, with fields:
  scientific_name, common_names, description, origin, traditional_uses, full_text, page_start

Usage:
  python extract_book1.py
  python extract_book1.py --pdf "path/to/book.pdf" --out extracted_book1.jsonl
"""

import re
import json
import argparse
import sys
import fitz  # pymupdf

BOOK_PATH = r"H:\Downloads\A Guide to Medicinal Plants - An Illustrated, Scientific and Medicinal Approach\A Guide to Medicinal Plants - An Illustrated, Scientific and Medicinal Approach.pdf"
DEFAULT_OUT = "extracted_book1.jsonl"

# Matches lines like: "1.  Abrus precatorius L. (Leguminosae)"
# Handles hyphenated species (capillus-veneris), var., subsp., author chains
PLANT_HEADING_RE = re.compile(
    r"^\s*(\d{1,2})\.\s+"                          # number (1 or 2 digits)
    r"([A-Z][a-z]+(?:\s+[a-z×][a-z×-]*)+)"        # genus + species (allows hyphens in species)
    r"(?:\s+[A-Za-z()&.,]+)*"                       # optional author(s)
    r"\s*\(([A-Za-z]+)\)"                           # (Family)
    r"\s*$"
)

SECTION_MARKERS = [
    "Description:",
    "Origin:",
    "Phytoconstituents:",
    "Traditional Medicinal Uses:",
    "Pharmacological Activities:",
    "Adverse Reactions:",
    "Drug-Herb Interactions:",
    "Drug-herb Interactions:",
    "Dosage:",
    "References:",
]


def extract_section(text, marker):
    """Pull text between a section marker and the next known marker."""
    idx = text.find(marker)
    if idx == -1:
        return ""
    start = idx + len(marker)
    # Find the earliest next section marker
    end = len(text)
    for other in SECTION_MARKERS:
        if other == marker:
            continue
        j = text.find(other, start)
        if j != -1 and j < end:
            end = j
    return text[start:end].strip()


def clean_text(t):
    # Remove hyphenated line-break artifacts, collapse whitespace
    t = re.sub(r"-\n", "", t)
    t = re.sub(r"\n+", " ", t)
    t = re.sub(r"\s{2,}", " ", t)
    return t.strip()


def extract_common_names(text_after_heading):
    """Lines between the heading and 'Description:' are common names.
    The heading itself (genus + species) is always the first line — skip it."""
    idx = text_after_heading.find("Description:")
    if idx == -1:
        idx = 300
    chunk = text_after_heading[:idx]
    lines = [l.strip() for l in chunk.splitlines() if l.strip()]
    # Skip: page numbers, lines that look like the scientific heading (contain parenthesized family)
    names = [
        l for l in lines
        if not re.match(r"^\d+$", l)
        and not re.search(r"\([A-Z][a-z]+aceae\)", l)
        and not re.search(r"\(Leguminosae\)|\(Gramineae\)|\(Palmae\)|\(Compositae\)|\(Guttiferae\)", l)
        and not re.match(r"^[A-Z][a-z]+ [a-z]", l)  # skip "Genus species ..." lines
    ]
    return ", ".join(names)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", default=BOOK_PATH)
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args()

    print(f"Opening: {args.pdf}")
    doc = fitz.open(args.pdf)
    total_pages = len(doc)
    print(f"Total pages: {total_pages}")

    # --- Pass 1: extract all text per page ---
    pages_text = []
    for i in range(total_pages):
        pages_text.append(doc[i].get_text())

    # --- Pass 2: find plant heading locations ---
    plant_locations = []  # list of (page_idx, line_idx, number, scientific_name, family)

    for page_idx, text in enumerate(pages_text):
        lines = text.splitlines()
        for line_idx, line in enumerate(lines):
            m = PLANT_HEADING_RE.match(line)
            if m:
                plant_locations.append({
                    "page": page_idx,
                    "number": int(m.group(1)),
                    "scientific_name": m.group(2).strip(),
                    "family": m.group(3).strip(),
                })

    print(f"Found {len(plant_locations)} plant headings")
    if not plant_locations:
        print("ERROR: No plant headings found. Check the regex or book format.")
        sys.exit(1)

    # --- Pass 3: collect text blocks per plant ---
    # Each plant's text runs from its heading page to the next plant's heading page
    plants = []
    for i, loc in enumerate(plant_locations):
        start_page = loc["page"]
        end_page = plant_locations[i + 1]["page"] if i + 1 < len(plant_locations) else total_pages

        # Gather all text from start_page to end_page (exclusive)
        chunks = []
        for p in range(start_page, end_page):
            chunks.append(pages_text[p])
        full_text = "\n".join(chunks)

        # Trim to start at the heading itself
        heading_pattern = re.escape(loc["scientific_name"])
        m = re.search(heading_pattern, full_text)
        if m:
            full_text = full_text[m.start():]

        common_names = extract_common_names(full_text)
        description = clean_text(extract_section(full_text, "Description:"))
        origin = clean_text(extract_section(full_text, "Origin:"))
        traditional_uses = clean_text(extract_section(full_text, "Traditional Medicinal Uses:"))

        plants.append({
            "number": loc["number"],
            "scientific_name": loc["scientific_name"],
            "family": loc["family"],
            "common_names": common_names,
            "description": description,
            "origin": origin,
            "traditional_uses": traditional_uses,
            "full_text": clean_text(full_text),
            "page_start": start_page + 1,  # 1-indexed
            "source": "A Guide to Medicinal Plants (Illustrated, Scientific and Medicinal Approach)",
        })

    # --- Write output ---
    with open(args.out, "w", encoding="utf-8") as f:
        for plant in plants:
            f.write(json.dumps(plant, ensure_ascii=False) + "\n")

    print(f"Wrote {len(plants)} plants to {args.out}")

    # Print a quick preview of the first 3
    print("\n--- Preview (first 3 plants) ---")
    for plant in plants[:3]:
        print(f"\n[{plant['number']}] {plant['scientific_name']} ({plant['family']})")
        print(f"  Common names: {plant['common_names'][:80]}")
        print(f"  Description:  {plant['description'][:120]}...")
        print(f"  Origin:       {plant['origin'][:80]}...")
        print(f"  Trad. uses:   {plant['traditional_uses'][:120]}...")


if __name__ == "__main__":
    main()
