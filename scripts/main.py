#!/usr/bin/env python3
"""
Medicinal plant database enrichment pipeline.
Scrapes POWO, Wikipedia, and GBIF to build a comprehensive medicinal plant database.
"""

import argparse
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from sources.powo import fetch_medicinal_plants
from sources.gbif import validate_species
from sources.wikipedia import fetch_plant_descriptions, is_latin_name_in_text
from sources.wikimedia import get_plant_image
from utils.colors import get_dominant_colors
from utils.categories import classify_plant, get_category_names
from db.populate import init_db, insert_plant, populate_categories, get_next_plant_id, get_existing_plant_ids
from config import PROGRESS_FILE


def load_progress():
    """Load progress from file."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'processed': {}, 'counts': {'success': 0, 'skipped': 0, 'failed': 0}}


def save_progress(progress):
    """Save progress to file."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


def run_pipeline(dry_run=False, update_existing_only=False, new_only=False, limit=None):
    """Run the full enrichment pipeline."""
    print(f"Starting medicinal plant enrichment pipeline...")
    print(f"  Dry run: {dry_run}")
    print(f"  Update existing only: {update_existing_only}")
    print(f"  New only: {new_only}")
    print()

    # Initialize database
    if not dry_run:
        init_db()
        populate_categories()

    # Load progress
    progress = load_progress()
    processed = progress.get('processed', {})
    counts = progress.get('counts', {'success': 0, 'skipped': 0, 'failed': 0})

    # Get existing plant IDs
    if not dry_run:
        existing_ids = get_existing_plant_ids()
    else:
        existing_ids = set()

    next_id = len(existing_ids) if existing_ids else 0

    try:
        # Fetch POWO medicinal plants
        plant_count = 0
        for powo_id, latin_name, common_name, family, uses in fetch_medicinal_plants(limit=limit):
            plant_count += 1

            # Check if already processed
            if powo_id in processed:
                print(f"Skipping {latin_name} (already processed)")
                continue

            # Skip existing plants if new_only
            if new_only and powo_id in existing_ids:
                processed[powo_id] = {'status': 'skipped', 'reason': 'existing plant'}
                counts['skipped'] += 1
                save_progress({'processed': processed, 'counts': counts})
                continue

            # Skip new plants if update_existing_only
            if update_existing_only and powo_id not in existing_ids:
                processed[powo_id] = {'status': 'skipped', 'reason': 'new plant (update_existing_only)'}
                counts['skipped'] += 1
                save_progress({'processed': processed, 'counts': counts})
                continue

            print(f"\nProcessing: {common_name} ({latin_name})")

            try:
                # Validate with GBIF
                gbif_key, accepted_name = validate_species(latin_name)
                print(f"  [OK] GBIF validated: {accepted_name}")

                # Fetch descriptions from Wikipedia
                descriptions = fetch_plant_descriptions(accepted_name, common_name)
                if not descriptions:
                    print(f"  [SKIP] No Wikipedia article found")
                    processed[powo_id] = {'status': 'failed', 'reason': 'no wikipedia'}
                    counts['failed'] += 1
                    save_progress({'processed': processed, 'counts': counts})
                    continue

                # Add Latin name to description if missing
                if 'en' in descriptions:
                    if not is_latin_name_in_text(descriptions['en'], accepted_name):
                        descriptions['en'] = f"Also known scientifically as *{accepted_name}* ({family}), {descriptions['en']}"
                        print(f"  [OK] Added Latin name to description")

                # Get image (Wikimedia → Pixabay fallback)
                image_url = get_plant_image(accepted_name, common_name)
                if image_url:
                    print(f"  [OK] Found image")
                else:
                    print(f"  [WARN] No image found")

                # Extract colors
                colors = get_dominant_colors(image_url)
                print(f"  [OK] Extracted {len(colors)} colors")

                # Classify plant
                category_id = classify_plant(descriptions.get('en', ''), uses, common_name)
                print(f"  [OK] Classified as: {category_id}")

                # Prepare names
                names = {
                    'en': common_name,
                }
                for lang in ['ro', 'es', 'de', 'fr', 'it', 'ru', 'pt', 'zh', 'ja', 'ar', 'hi']:
                    names[lang] = descriptions.get(lang, '')

                # Store in database
                if not dry_run:
                    plant_id = get_next_plant_id()
                    insert_plant({
                        'id': plant_id,
                        'author': category_id,
                        'names': names,
                        'descriptions': descriptions,
                        'colors': colors,
                        'image_url': image_url,
                    })
                    print(f"  [OK] Inserted into database (ID: {plant_id})")

                processed[powo_id] = {'status': 'success', 'id': plant_id if not dry_run else -1}
                counts['success'] += 1

            except Exception as e:
                print(f"  ✗ Error: {e}")
                processed[powo_id] = {'status': 'failed', 'reason': str(e)}
                counts['failed'] += 1

            # Save progress after each plant
            save_progress({'processed': processed, 'counts': counts})

        print(f"\n{'='*60}")
        print(f"Pipeline completed!")
        print(f"  Total plants processed: {plant_count}")
        print(f"  Successful: {counts['success']}")
        print(f"  Skipped: {counts['skipped']}")
        print(f"  Failed: {counts['failed']}")
        print(f"{'='*60}")

    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user. Progress saved.")
        save_progress({'processed': processed, 'counts': counts})
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Medicinal plant database enrichment pipeline")
    parser.add_argument('--dry-run', action='store_true', help="Fetch data only, don't write to database")
    parser.add_argument('--update-existing-only', action='store_true', help="Only re-process existing plants")
    parser.add_argument('--new-only', action='store_true', help="Only add new plants")
    parser.add_argument('--limit', type=int, help="Limit number of plants to process")

    args = parser.parse_args()

    # Validate flags
    if args.update_existing_only and args.new_only:
        print("Error: Cannot use both --update-existing-only and --new-only")
        sys.exit(1)

    run_pipeline(
        dry_run=args.dry_run,
        update_existing_only=args.update_existing_only,
        new_only=args.new_only,
        limit=args.limit,
    )


if __name__ == '__main__':
    main()
