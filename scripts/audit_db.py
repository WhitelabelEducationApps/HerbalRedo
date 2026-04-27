# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
"""
DB audit script - no external dependencies beyond stdlib + sqlite3.
Checks for:
  1. paintingname_* fields that look like sentences / non-names
  2. description_* fields that are stubs (too short)
  3. description_* fields containing known wrong-content phrases
  4. full_image_uri pointing to PDF/DJVU thumbnails
  5. Missing (empty) critical fields
  6. style_* fields that don't match any known category
"""

import re
import sqlite3
import sys
from pathlib import Path

DB = Path(r"C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db")

LANGUAGES = ["", "_ro", "_es", "_de", "_fr", "_it", "_ru", "_pt", "_ja", "_zh", "_ar", "_hi"]
LANG_LABELS = {
    "": "EN", "_ro": "RO", "_es": "ES", "_de": "DE", "_fr": "FR",
    "_it": "IT", "_ru": "RU", "_pt": "PT", "_ja": "JA", "_zh": "ZH",
    "_ar": "AR", "_hi": "HI",
}

KNOWN_CATEGORIES = {
    "adaptogen", "anti_inflammatory", "anti-inflammatory", "antifungal", "antiviral",
    "antibacterial", "digestive", "nervine", "respiratory", "cardiovascular",
    "immunostimulant", "analgesic", "detoxifying", "tonic", "toxic",
    # common translated variants
    "respirator", "respiratorio", "atemwege", "respiratoire", "дыхательное",
    "respiratório", "呼吸器", "呼吸", "تنفسي", "श्वसन",
    "tóxico", "giftig", "toxique", "tossico", "токсичное", "有毒", "سام", "विषैला",
    "analgezic", "analgésico", "schmerzmittel", "analgésique", "analgesico",
    "анальгетик", "止痛", "鎮痛", "مسكن", "दर्द निवारक",
    "tonic", "tónico", "tonikum", "tonique", "tonico", "тоник", "滋补", "トニック", "منشط", "टॉनिक",
}

PDF_RE = re.compile(r"(\.pdf\.jpg|\.djvu\.jpg|\.pdf/page|/page\d+-\d+px.*\.pdf|\.pdf\.png)", re.I)

# Phrases that indicate wrong plant content was pasted in
WRONG_CONTENT_PHRASES = [
    "nicotina", "nicotine", "nicotin",
    "resin is a solid or highly viscous",
    "brass instrument",
    "largest and most populous",   # Crete article
    "jasmine sandlas",             # celebrity biography
    "born 4 september",
    "heroin and cocaine",
    "Nicotiana tabacum",
    "pirolidinic",
    "chewing gum",                 # chicle description might be ok, but flag for review
]

# A paintingname looks like a sentence if it:
#  - contains a verb-like structure
#  - is suspiciously long
#  - starts with lowercase (should start uppercase or be a non-Latin script)
NAME_SENTENCE_RE = re.compile(
    r"(\bis\s+a\b|\bare\s+a\b|\bknown\s+as\b|\beste\s+o\b|\best\s+un\b|\bist\s+ein\b"
    r"|\bsunt\b.*\bspecii\b|\beste\s+un\b|\bplantele\b|\bherb\b|\bplant\b"
    r"|\bspecies\b|\bgenus\b|\bfamily\b|\bLIST\b|\bprincipii\b)",
    re.I,
)

def is_pdf_uri(url):
    return bool(url and PDF_RE.search(url))

def check_name_field(val):
    """Return issue string or None."""
    if not val:
        return "EMPTY"
    if len(val) > 80:
        return f"TOO_LONG({len(val)})"
    if NAME_SENTENCE_RE.search(val):
        return f"LOOKS_LIKE_SENTENCE"
    if val.strip().endswith(("-", ":", ";")):
        return "ENDS_WITH_PUNCTUATION"
    return None

def check_desc_field(val, lang, plant_name):
    """Return list of issue strings."""
    issues = []
    if not val:
        issues.append("EMPTY")
        return issues
    if len(val) < 80:
        issues.append(f"STUB({len(val)}chars)")
    val_lower = val.lower()
    for phrase in WRONG_CONTENT_PHRASES:
        if phrase.lower() in val_lower:
            issues.append(f"WRONG_CONTENT:'{phrase}'")
    return issues

def main():
    conn = sqlite3.connect(DB)
    conn.text_factory = lambda b: b.decode("utf-8", errors="replace")

    rows = conn.execute(
        "SELECT id, paintingname, full_image_uri, " +
        ", ".join(f"description{l}, paintingname{l}, style{l}" for l in LANGUAGES) +
        " FROM museum_item ORDER BY id"
    ).fetchall()
    conn.close()

    # Build column index
    cols = ["id", "paintingname", "full_image_uri"]
    for l in LANGUAGES:
        cols += [f"description{l}", f"paintingname{l}", f"style{l}"]
    idx = {c: i for i, c in enumerate(cols)}

    issues_by_type = {
        "name_field":    [],
        "desc_stub":     [],
        "desc_wrong":    [],
        "pdf_uri":       [],
        "missing_uri":   [],
        "unknown_style": [],
    }

    for row in rows:
        row_id   = row[idx["id"]]
        en_name  = row[idx["paintingname"]] or ""
        uri      = row[idx["full_image_uri"]] or ""

        # URI checks
        if not uri:
            issues_by_type["missing_uri"].append((row_id, en_name))
        elif is_pdf_uri(uri):
            issues_by_type["pdf_uri"].append((row_id, en_name, uri[:80]))

        for lang in LANGUAGES:
            label = LANG_LABELS[lang]

            # paintingname check (skip EN — already the primary key)
            if lang != "":
                name_val = row[idx[f"paintingname{lang}"]] or ""
                issue = check_name_field(name_val)
                if issue:
                    issues_by_type["name_field"].append(
                        (row_id, en_name, label, issue, name_val[:60])
                    )

            # description check
            desc_val = row[idx[f"description{lang}"]] or ""
            desc_issues = check_desc_field(desc_val, label, en_name)
            for di in desc_issues:
                if "WRONG_CONTENT" in di:
                    issues_by_type["desc_wrong"].append(
                        (row_id, en_name, label, di, desc_val[:80])
                    )
                else:
                    issues_by_type["desc_stub"].append(
                        (row_id, en_name, label, di)
                    )

            # style check (EN only, rest are translations)
            if lang == "":
                style_val = (row[idx["style"]] or "").strip().lower()
                if style_val and style_val not in KNOWN_CATEGORIES:
                    issues_by_type["unknown_style"].append(
                        (row_id, en_name, style_val)
                    )

    # ── Report ────────────────────────────────────────────────────────────────
    total = len(rows)
    print(f"Audited {total} rows\n")

    print(f"── PDF/DJVU thumbnail URIs ({len(issues_by_type['pdf_uri'])}) ─────────────────────")
    for row_id, name, uri in issues_by_type["pdf_uri"]:
        print(f"  {row_id:4d}  {name:<35}  {uri}")

    print(f"\n── Missing image URI ({len(issues_by_type['missing_uri'])}) ──────────────────────────")
    for row_id, name in issues_by_type["missing_uri"]:
        print(f"  {row_id:4d}  {name}")

    print(f"\n── Wrong content in descriptions ({len(issues_by_type['desc_wrong'])}) ───────────────")
    for row_id, name, lang, issue, snippet in issues_by_type["desc_wrong"]:
        print(f"  {row_id:4d}  [{lang}]  {name:<30}  {issue}")
        print(f"        snippet: {snippet}")

    print(f"\n── Name fields with bad values ({len(issues_by_type['name_field'])}) ───────────────────")
    for row_id, name, lang, issue, val in issues_by_type["name_field"]:
        print(f"  {row_id:4d}  [{lang}]  {name:<30}  {issue:<25}  '{val}'")

    print(f"\n── Stub descriptions <80 chars ({len(issues_by_type['desc_stub'])}) ─────────────────")
    # Group by language for readability
    by_lang = {}
    for row_id, name, lang, issue in issues_by_type["desc_stub"]:
        by_lang.setdefault(lang, []).append((row_id, name, issue))
    for lang in ["EN","RO","ES","DE","FR","IT","RU","PT","JA","ZH","AR","HI"]:
        entries = by_lang.get(lang, [])
        if entries:
            print(f"  [{lang}] {len(entries)} stubs")
            for row_id, name, issue in entries[:5]:
                print(f"    {row_id:4d}  {name:<35}  {issue}")
            if len(entries) > 5:
                print(f"    ... and {len(entries)-5} more")

    print(f"\n── Unknown style values ({len(issues_by_type['unknown_style'])}) ──────────────────────")
    for row_id, name, style in issues_by_type["unknown_style"]:
        print(f"  {row_id:4d}  {name:<35}  '{style}'")

    # Summary
    total_issues = sum(len(v) for v in issues_by_type.values())
    critical = len(issues_by_type["desc_wrong"]) + len(issues_by_type["pdf_uri"]) + len(issues_by_type["missing_uri"])
    print(f"\n── Summary ──────────────────────────────────────────────────────")
    print(f"  Total issues  : {total_issues}")
    print(f"  Critical      : {critical}  (wrong content + broken URIs)")
    print(f"  Fixable/minor : {total_issues - critical}  (stubs + name formatting)")

if __name__ == "__main__":
    main()
