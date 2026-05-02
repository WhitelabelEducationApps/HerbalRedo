import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

import io
from PIL import Image

TARGET_MAX_BYTES = 100 * 1024  # 100 KB

def try_compress(img, quality):
    buf = io.BytesIO()
    img.save(buf, format='WEBP', quality=quality, method=6)
    return buf.getvalue()


def compress_webp(path):
    original_size = os.path.getsize(path)
    if original_size <= TARGET_MAX_BYTES:
        return 0  # already small enough

    img = Image.open(path)
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGBA')

    # Try progressively smaller scales until we can hit 100KB
    for scale in [1.0, 0.75, 0.6, 0.5, 0.4, 0.33, 0.25]:
        if scale < 1.0:
            new_w = max(1, int(img.width * scale))
            new_h = max(1, int(img.height * scale))
            candidate = img.resize((new_w, new_h), Image.LANCZOS)
        else:
            candidate = img

        # Binary search quality for this scale
        lo, hi = 1, 90
        best_data = None
        while lo <= hi:
            mid = (lo + hi) // 2
            data = try_compress(candidate, mid)
            if len(data) <= TARGET_MAX_BYTES:
                best_data = data
                lo = mid + 1
            else:
                hi = mid - 1

        if best_data is not None:
            with open(path, 'wb') as f:
                f.write(best_data)
            return original_size - len(best_data)

    print(f"  SKIP (can't compress even at 25% size, q=1): {os.path.basename(path)}")
    return 0


def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    webp_files = [
        os.path.join(root, f)
        for root, _, files in os.walk(directory)
        for f in files if f.lower().endswith('.webp')
    ]

    over_limit = [p for p in webp_files if os.path.getsize(p) > TARGET_MAX_BYTES]
    print(f"Found {len(webp_files)} WebP files, {len(over_limit)} exceed 100KB")

    total_saved = 0
    compressed = 0
    for i, path in enumerate(over_limit, 1):
        orig = os.path.getsize(path)
        saved = compress_webp(path)
        if saved > 0:
            compressed += 1
            total_saved += saved
            new_size = os.path.getsize(path)
            print(f"[{i}/{len(over_limit)}] {os.path.basename(path)}: {orig//1024}KB → {new_size//1024}KB (saved {saved//1024}KB)")
        else:
            print(f"[{i}/{len(over_limit)}] {os.path.basename(path)}: kept ({orig//1024}KB)")

    print(f"\nDone: {compressed} files compressed, {total_saved//1024}KB total saved")


if __name__ == '__main__':
    main()
