#!/usr/bin/env python3
"""Remove duplicate plants from the database, keeping one record per unique name."""

import sqlite3
from pathlib import Path

DB_PATH = Path("androidApp/src/main/assets/plants.db")

def deduplicate():
    """Remove duplicate plants, keeping the first occurrence (lowest ID)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get count before
    cursor.execute("SELECT COUNT(*) FROM museum_item")
    before = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM museum_item
        WHERE paintingname IN (
            SELECT paintingname FROM museum_item
            GROUP BY paintingname HAVING COUNT(*) > 1
        )
    """)
    duplicates = cursor.fetchone()[0]

    print(f"Before: {before} total records")
    print(f"Duplicates to remove: {duplicates} records\n")

    # Delete duplicates, keeping the record with the lowest ID for each plant name
    cursor.execute("""
        DELETE FROM museum_item
        WHERE id NOT IN (
            SELECT MIN(id) FROM museum_item
            GROUP BY paintingname
        )
    """)

    conn.commit()

    # Get count after
    cursor.execute("SELECT COUNT(*) FROM museum_item")
    after = cursor.fetchone()[0]

    print(f"After: {after} total records")
    print(f"Removed: {before - after} duplicate records")

    # Verify no more duplicates
    cursor.execute("""
        SELECT COUNT(*) FROM museum_item
        GROUP BY paintingname HAVING COUNT(*) > 1
    """)
    remaining_dups = len(cursor.fetchall())

    if remaining_dups == 0:
        print("\n✓ All duplicates successfully removed!")
    else:
        print(f"\n✗ Warning: {remaining_dups} plants still have duplicates")

    conn.close()

if __name__ == '__main__':
    import os
    os.chdir(Path(__file__).parent.parent)
    deduplicate()
