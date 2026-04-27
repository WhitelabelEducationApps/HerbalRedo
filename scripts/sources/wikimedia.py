"""Plant image sources with fallback chain."""

import requests
import time
from config import COMMONS_API_BASE, RATE_LIMITS, MIN_IMAGE_WIDTH


# Wikimedia requires a User-Agent header
HEADERS = {
    'User-Agent': 'HerbalRedo-App/1.0 (Educational medicinal plant database; contact: herbal@example.com)'
}

# Pixabay API key (free tier, no key needed for basic search)
PIXABAY_BASE = "https://pixabay.com/api/"


def get_commons_image(latin_name):
    """
    Get image URL from Wikimedia Commons for a plant.
    Returns image URL or None on failure/rate-limit.
    """
    try:
        time.sleep(RATE_LIMITS['wikimedia'])

        # Search for images matching the plant name
        search_params = {
            'action': 'query',
            'list': 'search',
            'srsearch': f'{latin_name} plant',
            'srlimit': 10,
            'srnamespace': 6,  # File namespace
            'format': 'json',
        }

        response = requests.get(COMMONS_API_BASE, params=search_params, headers=HEADERS, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = data.get('query', {}).get('search', [])

        # Try to fetch image info for top results
        for result in results:
            title = result.get('title', '')
            if not title:
                continue

            try:
                time.sleep(RATE_LIMITS['wikimedia'] * 0.5)

                # Fetch image info
                info_params = {
                    'action': 'query',
                    'titles': title,
                    'prop': 'imageinfo',
                    'iiprop': 'url',
                    'iiurlwidth': 400,
                    'format': 'json',
                }

                info_response = requests.get(COMMONS_API_BASE, params=info_params, headers=HEADERS, timeout=10)
                info_response.raise_for_status()

                info_data = info_response.json()
                pages = info_data.get('query', {}).get('pages', {})

                for page in pages.values():
                    imageinfo = page.get('imageinfo', [])
                    if imageinfo:
                        url = imageinfo[0].get('thumburl') or imageinfo[0].get('url')
                        if url:
                            return url

            except Exception:
                continue

    except Exception as e:
        pass

    return None


def get_pixabay_image(plant_name):
    """
    Get image from Pixabay (free alternative when Wikimedia is rate-limited).
    Pixabay is more reliable for high-volume requests.
    Returns image URL or None.
    """
    try:
        time.sleep(RATE_LIMITS['wikimedia'] * 0.5)

        params = {
            'q': f'{plant_name} plant',
            'min_width': 200,
            'min_height': 200,
            'image_type': 'photo',
            'order': 'popular',
            'per_page': 3,
            'safesearch': 'true',
        }

        # Pixabay free API doesn't require key for limited requests
        response = requests.get(PIXABAY_BASE, params=params, headers=HEADERS, timeout=10)

        if response.status_code == 200:
            data = response.json()
            hits = data.get('hits', [])

            if hits:
                # Return first result's thumbnail
                img = hits[0]
                return img.get('previewURL') or img.get('webformatURL')

    except Exception as e:
        pass

    return None


def get_plant_image(latin_name, common_name=None):
    """
    Get plant image with fallback chain:
    1. Try Wikimedia Commons (best quality, but rate-limited)
    2. Fall back to Pixabay (reliable, free, no rate limit issues)
    3. Return None if both fail (color extraction will use default)
    """
    # Try Wikimedia first
    url = get_commons_image(latin_name)
    if url:
        return url

    # Fall back to Pixabay
    search_name = common_name or latin_name
    url = get_pixabay_image(search_name)
    if url:
        return url

    # No image found
    return None
