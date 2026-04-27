#!/usr/bin/env python3
"""
Audit medicinal plants DB for content errors.
Sends compact row summaries to local LLM (Ollama) in batches.
Flags rows where description doesn't match plant name, wrong categories, etc.
"""

import sqlite3
import json
import urllib.request
import urllib.error
import textwrap
import sys

DB_PATH = r"C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db"
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:8b-ctx16k"
BATCH_SIZE = 60
DESC_SNIPPET = 250  # chars of English description to include

SYSTEM_PROMPT = """\
You are auditing a medicinal plants database. Flag ONLY rows with clear, obvious content errors.

Flag a row ONLY if:
1. The description is clearly about something non-plant (a phone brand, a snake, a movie, a person, neurons, a company)
2. The description explicitly names a different plant species than the entry name suggests

Do NOT flag: minor category mismatches, broad descriptions, plants used as food, plants with multiple names, anything uncertain.

Be strict. Only output rows you are 100% certain have wrong content.

Output format — one line per flagged row:
ID <id> | <issue in under 12 words>

If no clear errors found: output exactly NONE
"""

def load_rows(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.execute("""
        SELECT id, paintingname, style, author,
               SUBSTR(description, 1, ?) as desc_en,
               paintingname_ro, paintingname_es, paintingname_de,
               full_image_uri
        FROM museum_item
        ORDER BY id
    """, (DESC_SNIPPET,))
    rows = cur.fetchall()
    conn.close()
    return rows

def format_batch(rows):
    lines = []
    for r in rows:
        # Compact: ID | Name | Category | Desc snippet
        desc = (r["desc_en"] or "").replace("\n", " ").strip()
        line = f'ID {r["id"]} | {r["paintingname"]} | cat:{r["style"]} | {desc}'
        lines.append(line)
    return "\n".join(lines)

def ask_llm(batch_text):
    payload = {
        "model": MODEL,
        "stream": False,
        "think": False,
        "options": {"temperature": 0.1, "num_predict": 512},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": batch_text},
        ],
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"].strip() if "choices" in result else result["message"]["content"].strip()
    except urllib.error.URLError as e:
        return f"ERROR: {e}"

CHECK_PROMPT = """\
You are auditing a single medicinal plant database record across all language fields.
Check every language description and name field for content errors.

Flag ONLY clear, obvious issues:
1. A description field is about something other than the named plant
2. A description field describes a different plant species than the entry name
3. A name field in one language refers to a completely different plant than the English name

For each issue found, output one line:
FIELD <field_name> | <issue in under 15 words>

If no issues found: output exactly NONE
"""

def check_single(row_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.execute("SELECT * FROM museum_item WHERE id=?", (row_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        print(f"ID {row_id} not found.")
        return
    keys = row.keys()
    # Build a compact representation of all language fields
    lines = [f"Plant: {row['paintingname']} (ID {row_id}, category: {row['style']})"]
    for k in keys:
        if k.startswith("description") or k.startswith("paintingname"):
            val = (row[k] or "").replace("\n", " ").strip()
            if val:
                lines.append(f"{k}: {val[:300]}")
    batch_text = "\n".join(lines)
    payload = {
        "model": MODEL,
        "stream": False,
        "think": False,
        "options": {"temperature": 0.1, "num_predict": 512},
        "messages": [
            {"role": "system", "content": CHECK_PROMPT},
            {"role": "user", "content": batch_text},
        ],
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        OLLAMA_URL, data=data,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            response = result["choices"][0]["message"]["content"].strip() if "choices" in result else result["message"]["content"].strip()
    except urllib.error.URLError as e:
        response = f"ERROR: {e}"
    print(f"\n=== Check result for ID {row_id} ({row['paintingname']}) ===")
    print(response)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Audit medicinal plants DB content via local LLM.")
    parser.add_argument("--check-id", type=int, help="Deep-check a single row ID across all language fields.")
    parser.add_argument("--random", action="store_true", help="Pick a random ID and deep-check it.")
    args = parser.parse_args()

    if args.random:
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute("SELECT id FROM museum_item ORDER BY RANDOM() LIMIT 1").fetchone()
        conn.close()
        check_single(row[0])
        return

    if args.check_id:
        check_single(args.check_id)
        return

    # Full audit
    print(f"Loading rows from {DB_PATH}...")
    rows = load_rows(DB_PATH)
    total = len(rows)
    print(f"Loaded {total} rows. Batch size: {BATCH_SIZE}. Batches: {(total + BATCH_SIZE - 1) // BATCH_SIZE}\n")

    real_ids = {r["id"] for r in rows}

    all_flags = []
    batches = [rows[i:i+BATCH_SIZE] for i in range(0, total, BATCH_SIZE)]

    for idx, batch in enumerate(batches):
        ids = f"{batch[0]['id']}–{batch[-1]['id']}"
        print(f"Batch {idx+1}/{len(batches)} (IDs {ids})...", end=" ", flush=True)
        batch_text = format_batch(batch)
        response = ask_llm(batch_text)
        if response.startswith("ERROR:"):
            print(f"FAILED: {response}")
            continue
        lines = []
        for l in response.splitlines():
            l = l.strip()
            if not l or l == "NONE":
                continue
            # Discard hallucinated IDs — must start with "ID <int>" and that int must exist
            import re
            m = re.match(r"ID\s+(\d+)", l)
            if m and int(m.group(1)) not in real_ids:
                continue
            lines.append(l)
        print(f"{len(lines)} flag(s)")
        all_flags.extend(lines)

    print("\n" + "="*60)
    print(f"AUDIT COMPLETE — {len(all_flags)} issue(s) found across {total} rows")
    print("="*60)
    if all_flags:
        for flag in all_flags:
            print(flag)
    else:
        print("No issues detected.")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
