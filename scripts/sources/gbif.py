"""GBIF (Global Biodiversity Information Facility) API client."""

import requests
import time
from config import GBIF_API_BASE, RATE_LIMITS

# GBIF requires a User-Agent header
HEADERS = {
    'User-Agent': 'HerbalRedo-App/1.0 (Educational medicinal plant database; contact: herbal@example.com)'
}


def validate_species(latin_name):
    """
    Validate species name via GBIF.
    Returns (gbif_key, accepted_name) or (None, latin_name) if not found.
    """
    try:
        time.sleep(RATE_LIMITS['gbif'])

        params = {
            'name': latin_name,
            'strict': True,
        }

        response = requests.get(GBIF_API_BASE, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Check if it's a valid, accepted species
        if data.get('matchType') == 'EXACT' and data.get('rank') == 'SPECIES':
            gbif_key = data.get('usageKey')
            accepted_name = data.get('scientificName', latin_name)
            return (gbif_key, accepted_name)

    except Exception as e:
        pass

    # Fallback: return original name if validation fails (don't skip)
    return (None, latin_name)
