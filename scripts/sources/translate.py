"""Translation via LibreTranslate for missing plant descriptions."""

import requests
import time
from config import LANGUAGES, DB_COLUMNS, RATE_LIMITS
from tqdm import tqdm

# LibreTranslate API (free, no API key needed)
TRANSLATE_API = "https://libretranslate.de/translate"

# Language code mappings for LibreTranslate
LIBRETRANSLATE_CODES = {
    'en': 'en',
    'ro': 'ro',
    'es': 'es',
    'de': 'de',
    'fr': 'fr',
    'it': 'it',
    'ru': 'ru',
    'pt': 'pt',
    'zh': 'zh',
    'ja': 'ja',
    'ar': 'ar',
    'hi': 'hi',
}

# User agent for API requests
HEADERS = {
    'User-Agent': 'HerbalRedo-App/1.0 (Educational medicinal plant database)'
}


def translate_text(text, source_lang='en', target_lang='es', max_retries=3):
    """
    Translate text using LibreTranslate API.

    Args:
        text: Text to translate
        source_lang: Source language code (en, es, etc.)
        target_lang: Target language code
        max_retries: Number of retries on failure

    Returns:
        Translated text or original text if translation fails
    """
    if not text or len(text.strip()) < 10:
        return text

    source_code = LIBRETRANSLATE_CODES.get(source_lang, 'en')
    target_code = LIBRETRANSLATE_CODES.get(target_lang, 'es')

    if source_code == target_code:
        return text

    for attempt in range(max_retries):
        try:
            time.sleep(RATE_LIMITS['powo'] * 0.5)

            payload = {
                'q': text,
                'source': source_code,
                'target': target_code,
            }

            response = requests.post(
                TRANSLATE_API,
                json=payload,
                headers=HEADERS,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                translated = data.get('translatedText', text)
                return translated
            elif response.status_code == 429:
                # Rate limited, wait and retry
                time.sleep(5)
                continue
            else:
                # Other error, return original
                return text

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return text

    return text


def fill_missing_translations(db_path):
    """
    Fill missing translations in the database using LibreTranslate.

    For each plant, for each language:
    - If name is missing, translate from English
    - If description is missing, translate from English
    - If category is missing, translate from English

    Updates the database in-place.
    """
    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Scanning for missing translations...")

    # Get all plants
    cursor.execute("SELECT id, paintingname, description FROM museum_item ORDER BY id")
    plants = cursor.fetchall()

    total_plants = len(plants)
    total_filled = 0

    pbar = tqdm(total=total_plants, desc="Filling translations", unit=" plants")

    for plant_id, english_name, english_desc in plants:
        plant_filled = 0

        # For each language (skip English)
        for lang in LANGUAGES:
            if lang == 'en':
                continue

            name_col, desc_col, style_col = DB_COLUMNS.get(lang, (None, None, None))
            if not name_col:
                continue

            # Check if name is missing
            cursor.execute(f"SELECT {name_col} FROM museum_item WHERE id = ?", (plant_id,))
            result = cursor.fetchone()
            current_name = result[0] if result else None

            if not current_name and english_name:
                translated_name = translate_text(english_name, 'en', lang)
                if translated_name and translated_name != english_name:
                    cursor.execute(
                        f"UPDATE museum_item SET {name_col} = ? WHERE id = ?",
                        (translated_name, plant_id)
                    )
                    plant_filled += 1

            # Check if description is missing
            cursor.execute(f"SELECT {desc_col} FROM museum_item WHERE id = ?", (plant_id,))
            result = cursor.fetchone()
            current_desc = result[0] if result else None

            if not current_desc and english_desc:
                translated_desc = translate_text(english_desc, 'en', lang)
                if translated_desc and translated_desc != english_desc:
                    cursor.execute(
                        f"UPDATE museum_item SET {desc_col} = ? WHERE id = ?",
                        (translated_desc, plant_id)
                    )
                    plant_filled += 1

        if plant_filled > 0:
            total_filled += plant_filled
            conn.commit()

        pbar.update(1)

    pbar.close()
    conn.close()

    print(f"\nTranslation complete!")
    print(f"  Plants processed: {total_plants}")
    print(f"  Fields filled: {total_filled}")


if __name__ == '__main__':
    from config import DB_PATH

    print("LibreTranslate Missing Translation Filler")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    print()

    confirm = input("Fill missing translations with LibreTranslate? (y/n): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        exit(0)

    fill_missing_translations(DB_PATH)
    print("\nDone!")
