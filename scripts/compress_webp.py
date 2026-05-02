import sys
import os
import re
import argparse
sys.stdout.reconfigure(encoding='utf-8')

import io
from PIL import Image

_GALLERY_RE = re.compile(r'_[2-9]\.(webp|jpg|jpeg|png)$', re.IGNORECASE)

def is_gallery(path):
    return bool(_GALLERY_RE.search(os.path.basename(path)))

def try_compress(img, quality):
    buf = io.BytesIO()
    img.save(buf, format='WEBP', quality=quality, method=6)
    return buf.getvalue()


def compress_webp(path, max_bytes):
    original_size = os.path.getsize(path)
    if original_size <= max_bytes:
        return 0  # already small enough

    img = Image.open(path)
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGBA')

    for scale in [1.0, 0.75, 0.6, 0.5, 0.4, 0.33, 0.25]:
        if scale < 1.0:
            new_w = max(1, int(img.width * scale))
            new_h = max(1, int(img.height * scale))
            candidate = img.resize((new_w, new_h), Image.LANCZOS)
        else:
            candidate = img

        lo, hi = 1, 90
        best_data = None
        while lo <= hi:
            mid = (lo + hi) // 2
            data = try_compress(candidate, mid)
            if len(data) <= max_bytes:
                best_data = data
                lo = mid + 1
            else:
                hi = mid - 1

        if best_data is not None:
            with open(path, 'wb') as f:
                f.write(best_data)
            return original_size - len(best_data)

    print(f"  SKIP (can't hit target even at 25% scale, q=1): {os.path.basename(path)}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Compress WebP images in a directory.")
    parser.add_argument("directory", nargs="?", default=".",
                        help="Directory to scan (default: current dir)")
    parser.add_argument("--max-kb", type=int, default=100,
                        help="Target max file size in KB (default: 100)")
    parser.add_argument("--gallery-only", action="store_true",
                        help="Only process gallery images (_2, _3, … suffixes)")
    args = parser.parse_args()

    max_bytes = args.max_kb * 1024

    all_files = [
        os.path.join(root, f)
        for root, _, files in os.walk(args.directory)
        for f in files if f.lower().endswith('.webp')
    ]

    if args.gallery_only:
        candidates = [p for p in all_files if is_gallery(p)]
        print(f"Gallery-only mode: {len(candidates)} gallery images (of {len(all_files)} total)")
    else:
        candidates = all_files
        print(f"Found {len(all_files)} WebP files")

    over_limit = [p for p in candidates if os.path.getsize(p) > max_bytes]
    print(f"{len(over_limit)} exceed {args.max_kb} KB — compressing...\n")

    total_saved = 0
    compressed = 0
    for i, path in enumerate(over_limit, 1):
        orig = os.path.getsize(path)
        saved = compress_webp(path, max_bytes)
        if saved > 0:
            compressed += 1
            total_saved += saved
            new_size = os.path.getsize(path)
            print(f"[{i}/{len(over_limit)}] {os.path.basename(path)}: "
                  f"{orig//1024}KB -> {new_size//1024}KB (saved {saved//1024}KB)")
        else:
            print(f"[{i}/{len(over_limit)}] {os.path.basename(path)}: already ok ({orig//1024}KB)")

    print(f"\nDone: {compressed} files compressed, {total_saved//1024} KB ({total_saved//1024//1024} MB) saved")


if __name__ == '__main__':
    main()
