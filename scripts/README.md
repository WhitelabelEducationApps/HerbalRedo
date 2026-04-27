# Medicinal Plant Database Enrichment Pipeline

Automated Python pipeline to scrape POWO (Plants of the World Online), Wikipedia, and GBIF to populate the HerbalRedo medicinal plant database with 1,000+ quality plants in 11 languages with medicinal categories.

## Setup

```bash
cd scripts
pip install -r requirements.txt
```

**Note:** The pipeline uses the official `pykew` library for POWO access (as recommended by Kew Gardens). `pykew` is installed automatically with the requirements above.

## Usage

### Full pipeline run (recommended first time)
```bash
python main.py
```

This will:
1. Fetch medicinal plant candidates from POWO
2. Validate each species with GBIF
3. Fetch descriptions from Wikipedia in 11 languages
4. Download plant images from Wikimedia Commons
5. Extract dominant colors from images
6. Classify plants into medicinal categories
7. Insert all data into `plants.db`
8. Populate the `authors` table with medicinal categories

### Dry run (no database writes)
```bash
python main.py --dry-run
```

Fetches all data but doesn't modify the database. Good for testing.

### Update existing plants only
```bash
python main.py --update-existing-only
```

Re-fetch and update the 120 existing plants (improve descriptions, add translations, etc.)

### Add new plants only
```bash
python main.py --new-only
```

Only add new medicinal plants, skip existing ones.

### Limit number of plants
```bash
python main.py --limit 100
```

Process at most 100 plants (useful for testing).

## Progress

Progress is saved to `progress.json` after each plant. If the script is interrupted, it will resume from where it left off on the next run.

To reset progress:
```bash
rm progress.json
```

## Features

### Data sources
- **POWO** — authoritative curated list of medicinal plants with use information
- **Wikipedia** — plant descriptions in 11 languages (en, ro, es, de, fr, it, ru, pt, zh, ja, ar, hi)
- **GBIF** — species name validation and taxonomy
- **Wikimedia Commons** — plant images

### Languages
- English, Romanian, Spanish, German, French, Italian, Russian, Portuguese, Chinese, Japanese, Arabic, Hindi

### Medicinal Categories
13 categories based on traditional medicinal uses:
- Adaptogen
- Anti-inflammatory
- Antifungal
- Antiviral
- Antibacterial
- Digestive
- Nervine
- Respiratory
- Cardiovascular
- Immunostimulant
- Analgesic
- Detoxifying
- Tonic (fallback)

### Quality measures
- Wikipedia articles must be >= 200 characters to avoid stubs
- Scientific names are embedded in English descriptions
- Automatic color extraction from plant images (4 dominant colors → ARGB integers)
- Rate limiting to respect API quotas
- Caching of downloaded images to avoid re-fetching
- Progress tracking with resumable runs

## Database schema

The pipeline populates `androidApp/src/main/assets/plants.db` with:

**museum_item table** — one row per plant
- `id` (INTEGER) — unique plant ID
- `paintingname` / `paintingname_ro` / etc. — plant common name in each language
- `description` / `description_ro` / etc. — plant description/uses in each language
- `author` (TEXT) — medicinal category ID (links to `authors` table)
- `style` / `style_ro` / etc. — localized category name
- `full_image_uri` (TEXT) — Wikimedia Commons image URL
- `prim_color`, `sec_color`, `detail_color`, `background_color` (INTEGER) — ARGB colors
- `isFavourite`, `viewed`, `visited` (TEXT) — user state flags

**authors table** — medicinal categories
- `id` (TEXT) — category key (adaptogen, digestive, etc.)
- `name` / `name_ro` / etc. — category name in each language
- `description` / `description_ro` / etc. — category description in each language

## Configuration

Edit `config.py` to adjust:
- `LANGUAGES` — which languages to fetch
- `MEDICINAL_CATEGORIES` — category definitions and keywords
- `RATE_LIMITS` — API request delays
- `MIN_WIKIPEDIA_ARTICLE_LENGTH` — minimum description quality

## Troubleshooting

### "Database file not found"
Ensure you've built the Android app at least once. The `plants.db` file should exist at:
```
androidApp/src/main/assets/plants.db
```

### Pipeline is slow
- Reduce `--limit` for faster testing
- Check your internet connection
- Adjust `RATE_LIMITS` in `config.py` if APIs are responding quickly

### Wikipedia articles not found
Some plants may not have Wikipedia articles. The pipeline skips these (reasonable for stubs or niche species).

### Image extraction fails
Some Wikimedia URLs may be inaccessible. The pipeline continues with a default color if image download fails.

## Next steps

1. Run `python main.py --dry-run` to preview without writes
2. Run `python main.py` to populate the database
3. Verify `plants.db` with a SQLite browser to check data quality
4. Build and test the Android app
