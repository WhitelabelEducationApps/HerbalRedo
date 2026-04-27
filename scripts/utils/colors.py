"""Color extraction from plant images using Pillow."""

import os
import hashlib
from io import BytesIO
from PIL import Image
import requests
from config import IMAGE_CACHE_DIR, RATE_LIMITS
import time

def download_and_cache_image(url, timeout=10):
    """Download image from URL and cache it. Returns PIL Image or None."""
    if not url:
        return None

    try:
        # Cache key based on URL hash
        cache_key = hashlib.md5(url.encode()).hexdigest()
        cache_path = os.path.join(IMAGE_CACHE_DIR, f"{cache_key}.png")

        # Return cached image if exists
        if os.path.exists(cache_path):
            return Image.open(cache_path).copy()

        # Download image
        time.sleep(RATE_LIMITS['wikimedia'])
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

        img = Image.open(BytesIO(response.content))

        # Resize if too large to save space
        if img.width > 500:
            ratio = 500 / img.width
            new_size = (500, int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        # Cache the image
        img.save(cache_path, 'PNG')
        return img.copy()

    except Exception as e:
        print(f"Failed to download image from {url}: {e}")
        return None


def get_dominant_colors(image_url, num_colors=4):
    """Extract dominant colors from image. Returns list of ARGB integers."""
    if not image_url:
        return [0xFF808080] * num_colors  # Default gray if no image

    try:
        img = download_and_cache_image(image_url)
        if not img:
            return [0xFF808080] * num_colors

        # Convert to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = rgb_img
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize for faster processing
        small_img = img.copy()
        small_img.thumbnail((100, 100))

        # Reduce colors to palette
        paletted = small_img.quantize(colors=num_colors)
        palette = paletted.getpalette()

        # Extract RGB tuples from palette
        colors = []
        for i in range(num_colors):
            r = palette[i * 3]
            g = palette[i * 3 + 1]
            b = palette[i * 3 + 2]
            # Convert to ARGB integer (alpha=255)
            argb = 0xFF000000 | (r << 16) | (g << 8) | b
            colors.append(argb)

        return colors

    except Exception as e:
        print(f"Failed to extract colors from {image_url}: {e}")
        return [0xFF808080] * num_colors
