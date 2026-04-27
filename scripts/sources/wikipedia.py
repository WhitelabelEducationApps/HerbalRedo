"""Wikipedia API client for plant descriptions in multiple languages."""

import requests
import time
from config import WIKIPEDIA_API_BASE, RATE_LIMITS, MIN_WIKIPEDIA_ARTICLE_LENGTH, LANGUAGES

# Wikipedia requires a User-Agent header
HEADERS = {
    'User-Agent': 'HerbalRedo-App/1.0 (Educational medicinal plant database; contact: herbal@example.com)'
}


def search_wikipedia(query, lang='en'):
    """Search for a plant article on Wikipedia in a given language."""
    try:
        base_url = f"https://{lang}.wikipedia.org/w/api.php"
        time.sleep(RATE_LIMITS['wikipedia'])

        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': query,
            'srlimit': 1,
            'format': 'json',
        }

        response = requests.get(base_url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = data.get('query', {}).get('search', [])

        if results:
            return results[0]['title']

    except Exception as e:
        pass

    return None


def get_wikipedia_content(title, lang='en'):
    """Get introduction/extract from Wikipedia article."""
    try:
        base_url = f"https://{lang}.wikipedia.org/w/api.php"
        time.sleep(RATE_LIMITS['wikipedia'])

        params = {
            'action': 'query',
            'titles': title,
            'prop': 'extracts',
            'exintro': True,
            'explaintext': True,
            'format': 'json',
        }

        response = requests.get(base_url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()

        data = response.json()
        pages = data.get('query', {}).get('pages', {})

        for page in pages.values():
            extract = page.get('extract', '').strip()
            if extract:
                return extract

    except Exception as e:
        pass

    return None


def get_interlanguage_links(title, source_lang='en'):
    """Get links to the same article in other languages."""
    try:
        base_url = f"https://{source_lang}.wikipedia.org/w/api.php"
        time.sleep(RATE_LIMITS['wikipedia'])

        params = {
            'action': 'query',
            'titles': title,
            'prop': 'langlinks',
            'lllimit': 500,
            'format': 'json',
        }

        response = requests.get(base_url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()

        data = response.json()
        pages = data.get('query', {}).get('pages', {})

        links = {}
        for page in pages.values():
            for link in page.get('langlinks', []):
                lang = link.get('lang')
                page_title = link.get('*')
                if lang and page_title:
                    links[lang] = page_title

        return links

    except Exception as e:
        pass

    return {}


def fetch_plant_descriptions(latin_name, common_name=None):
    """
    Fetch plant descriptions in all languages.
    Returns dict {lang: description}.

    Falls back to placeholder if APIs are unavailable.
    """
    descriptions = {}

    # Try to find English Wikipedia article first
    search_query = f"{latin_name} plant" if common_name is None else common_name
    english_title = search_wikipedia(search_query, 'en')

    if not english_title:
        # Fallback: create minimal placeholder description
        # In production, this ensures the plant still gets added even if APIs are slow
        descriptions['en'] = f"{common_name or latin_name} is a medicinal plant with traditional uses. " \
                             f"Scientific name: {latin_name}. Further information available on botanical databases."
        return descriptions

    # Get English content and validate quality
    english_content = get_wikipedia_content(english_title, 'en')
    if not english_content or len(english_content) < MIN_WIKIPEDIA_ARTICLE_LENGTH:
        # Use placeholder instead of skipping
        descriptions['en'] = f"{common_name or latin_name} is a medicinal plant with traditional uses. " \
                             f"Scientific name: {latin_name}. Further information available on botanical databases."
        return descriptions

    descriptions['en'] = english_content

    # Get interlanguage links
    lang_links = get_interlanguage_links(english_title, 'en')

    # Fetch content in other languages
    for lang in LANGUAGES:
        if lang == 'en':
            continue

        if lang in lang_links:
            # Use existing article title in that language
            title = lang_links[lang]
        else:
            # Try searching
            title = search_wikipedia(latin_name, lang)

        if title:
            content = get_wikipedia_content(title, lang)
            if content:
                descriptions[lang] = content

    return descriptions


def is_latin_name_in_text(text, latin_name):
    """Check if Latin name (scientific name) is mentioned in text."""
    if not text or not latin_name:
        return False

    # Extract genus and species from latin name
    parts = latin_name.strip().split()
    if len(parts) >= 2:
        genus = parts[0]
        species = parts[1]
        text_lower = text.lower()
        return (genus.lower() in text_lower) or (species.lower() in text_lower)

    return False
