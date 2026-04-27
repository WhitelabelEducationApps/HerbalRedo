#!/usr/bin/env python3
"""
Import medicinal plants from CSV file.

Allows you to add plants from external sources (Kaggle, Wikipedia lists, etc.)

CSV format required (header row):
    family,scientific_name,common_name

Usage:
    python import_plants_csv.py your_plants.csv
    python import_plants_csv.py --dry-run your_plants.csv
"""

import argparse
import csv
import sqlite3
from config import DB_PATH, LANGUAGES, DB_COLUMNS
from sources.gbif import validate_species
from sources.wikipedia import fetch_plant_descriptions
from sources.wikimedia import get_plant_image
from utils.colors import get_dominant_colors
from utils.categories import classify_plant
from db.populate import insert_plant, get_next_plant_id
from tqdm import tqdm
import os


def import_plants_from_csv(csv_path, dry_run=False):
    """Import plants from CSV file into database."""

    if not os.path.exists(csv_path):
        print(f"Error: File not found: {csv_path}")
        return

    # Read CSV
    plants_to_import = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                family = row.get('family', '').strip()
                latin = row.get('scientific_name', '').strip()
                common = row.get('common_name', '').strip()

                if latin and common:
                    plants_to_import.append((family or 'Unknown', latin, common))
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    print(f"Found {len(plants_to_import)} plants in CSV\n")

    if dry_run:
        print("(DRY RUN - preview only)\n")
        for family, latin, common in plants_to_import[:10]:
            print(f"  {common} ({latin})")
        if len(plants_to_import) > 10:
            print(f"  ... and {len(plants_to_import) - 10} more")
        return

    # Confirm
    response = input(f"\nImport {len(plants_to_import)} plants? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return

    # Import plants
    print("\nImporting plants...")

    successful = 0
    skipped = 0
    pbar = tqdm(total=len(plants_to_import), desc="Importing", unit=" plants")

    for family, latin_name, common_name in plants_to_import:
        try:
            # Validate with GBIF
            gbif_key, accepted_name = validate_species(latin_name)

            # Fetch descriptions
            descriptions = fetch_plant_descriptions(accepted_name, common_name)
            if not descriptions or not descriptions.get('en'):
                skipped += 1
                pbar.update(1)
                continue

            # Get image
            image_url = get_plant_image(accepted_name, common_name)

            # Extract colors
            colors = get_dominant_colors(image_url)

            # Classify
            category_id = classify_plant(descriptions.get('en', ''), '', common_name)

            # Prepare names
            names = {'en': common_name}
            for lang in LANGUAGES:
                if lang != 'en':
                    names[lang] = descriptions.get(lang, '')

            # Insert into database
            plant_id = get_next_plant_id()
            insert_plant({
                'id': plant_id,
                'author': category_id,
                'names': names,
                'descriptions': descriptions,
                'colors': colors,
                'image_url': image_url,
            })

            successful += 1

        except Exception as e:
            skipped += 1

        pbar.update(1)

    pbar.close()

    print(f"\nImport complete!")
    print(f"  Successful: {successful}")
    print(f"  Skipped: {skipped}")
    print(f"  Total in database: {successful + skipped}")


def main():
    parser = argparse.ArgumentParser(
        description="Import medicinal plants from CSV file"
    )
    parser.add_argument('csv_file', help='CSV file with plants (family, scientific_name, common_name)')
    parser.add_argument('--dry-run', action='store_true', help='Preview without importing')
    args = parser.parse_args()

    print("CSV Plant Importer")
    print("=" * 70)
    print(f"Database: {DB_PATH}\n")

    import_plants_from_csv(args.csv_file, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
