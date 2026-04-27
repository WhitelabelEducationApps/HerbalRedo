"""Medicinal category classification for plants."""

from config import MEDICINAL_CATEGORIES


def classify_plant(english_description, powo_uses=None, plant_name=None):
    """
    Classify plant into a medicinal category based on description keywords.
    Returns category id (key in MEDICINAL_CATEGORIES).
    """
    if not english_description:
        return 'tonic'  # Default fallback

    # Combine all searchable text
    searchable = (english_description + ' ' + (powo_uses or '') + ' ' + (plant_name or '')).lower()

    # Score each category
    best_category = 'tonic'
    best_score = 0

    for category_id, category_data in MEDICINAL_CATEGORIES.items():
        keywords = category_data['keywords']
        score = sum(1 for keyword in keywords if keyword.lower() in searchable)

        if score > best_score:
            best_score = score
            best_category = category_id

    return best_category


def get_category_names(category_id):
    """Get all language variants of a category name. Returns dict {lang: name}."""
    category = MEDICINAL_CATEGORIES.get(category_id)
    if not category:
        return {'en': 'Tonic'}

    result = {
        'en': category['name'],
        'ro': category['name_ro'],
        'es': category['name_es'],
        'de': category['name_de'],
        'fr': category['name_fr'],
        'it': category['name_it'],
        'ru': category['name_ru'],
        'pt': category['name_pt'],
        'zh': category['name_zh'],
        'ja': category['name_ja'],
        'ar': category['name_ar'],
        'hi': category['name_hi'],
    }
    return result
