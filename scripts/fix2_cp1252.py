#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix 2: Recode CP1252-stored bytes in Latin-script name columns to proper UTF-8."""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'

COLS = [
    'paintingname_ro','paintingname_es','paintingname_de',
    'paintingname_fr','paintingname_it','paintingname_pt',
]

def try_recode(raw_bytes):
    try:
        raw_bytes.decode('utf-8')
        return None  # already valid UTF-8, no change needed
    except UnicodeDecodeError:
        try:
            return raw_bytes.decode('cp1252')
        except Exception:
            return raw_bytes.decode('utf-8', errors='replace')

# Single connection: read raw bytes, write corrected strings
conn = sqlite3.connect(DB_PATH)
conn.text_factory = bytes
cur = conn.cursor()

cur.execute(f'SELECT id, {", ".join(COLS)} FROM museum_item ORDER BY id')
rows = cur.fetchall()
conn.close()

# Build updates
updates = []  # list of (id, {col: new_value})
for row in rows:
    pid = row[0]
    changes = {}
    for i, col in enumerate(COLS):
        raw = row[i + 1]
        if raw is None:
            continue
        recoded = try_recode(raw)
        if recoded is not None:
            changes[col] = recoded
    if changes:
        updates.append((pid, changes))

print(f'Rows needing recode: {len(updates)}')

# Write back with UTF-8 connection
conn_w = sqlite3.connect(DB_PATH)
conn_w.execute('PRAGMA encoding = "UTF-8"')
cur_w = conn_w.cursor()

for pid, changes in updates:
    sets = [f'{c}=?' for c in changes]
    vals = list(changes.values()) + [pid]
    cur_w.execute(f'UPDATE museum_item SET {",".join(sets)} WHERE id=?', vals)

conn_w.commit()
conn_w.close()
print('Committed.')

# Verify
conn2 = sqlite3.connect(DB_PATH)
conn2.text_factory = lambda b: b.decode('utf-8', errors='replace')
cur2 = conn2.cursor()
print('\nRemaining replacement-char counts:')
for col in COLS:
    cur2.execute(f"SELECT COUNT(*) FROM museum_item WHERE {col} LIKE ?", ('%\ufffd%',))
    c = cur2.fetchone()[0]
    print(f'  {col}: {c}')
conn2.close()
