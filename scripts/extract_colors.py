#!/usr/bin/env python3
"""
extract_colors.py — Pre-compute Palette-like colors for all plant drawables.

Processes base images (no _N suffix) from drawable-nodpi and writes
extracted_colors.json to the assets directory. The app loads this file
at startup so no Palette extraction is needed at runtime for known plants.

Usage:
    python scripts/extract_colors.py \
        --drawable-dir androidApp/src/main/res/drawable-nodpi \
        --output androidApp/src/main/assets/extracted_colors.json

Requirements:
    pip install Pillow
"""

import argparse
import colorsys
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Image extensions we handle
# ---------------------------------------------------------------------------
IMAGE_EXTS = {".webp", ".jpg", ".jpeg", ".png"}

# Base-image pattern: filename that does NOT end with _<digits> before extension
# e.g.  acaipalm.webp   → base image  ✓
#       acaipalm_2.webp → gallery     ✗
_NUMBERED_RE = re.compile(r"_\d+$")


def is_base_image(stem: str) -> bool:
    return not _NUMBERED_RE.search(stem)


# ---------------------------------------------------------------------------
# Color math
# ---------------------------------------------------------------------------

def rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    """Return (H 0-1, S 0-1, L 0-1)."""
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    return h, s, l


def to_argb_int(r: int, g: int, b: int, a: int = 255) -> int:
    """Signed 32-bit ARGB integer matching Java's Color.argb()."""
    unsigned = (a << 24) | (r << 16) | (g << 8) | b
    if unsigned >= (1 << 31):
        unsigned -= (1 << 32)
    return unsigned


# ---------------------------------------------------------------------------
# Palette-like swatch extraction
#
# Android Palette (androidx.palette) does:
#   1. Median-cut quantization to ~16 representative colors
#   2. Score each color for 6 named targets using HSL thresholds + population
#   3. Best-scoring color per target wins
#
# We replicate the same target definitions and scoring weights here.
# ---------------------------------------------------------------------------

TARGETS = {
    # name          min_s  max_s  tgt_s  min_l  max_l  tgt_l
    "vibrant":      (0.35, 1.00,  1.0,   0.30,  0.70,  0.50),
    "vibrantDark":  (0.35, 1.00,  1.0,   0.00,  0.45,  0.26),
    "vibrantLight": (0.35, 1.00,  1.0,   0.55,  1.00,  0.74),
    "muted":        (0.00, 0.40,  0.3,   0.30,  0.70,  0.50),
    "mutedDark":    (0.00, 0.40,  0.3,   0.00,  0.45,  0.26),
    "mutedLight":   (0.00, 0.40,  0.3,   0.55,  1.00,  0.74),
}

# Scoring weights from Android Palette source
_W_SAT  = 3.0
_W_LUM  = 6.5
_W_POP  = 0.5


def _score(s: float, l: float, pop: float,
           min_s, max_s, tgt_s, min_l, max_l, tgt_l) -> float:
    if not (min_s <= s <= max_s and min_l <= l <= max_l):
        return 0.0
    sat_score = 1.0 - abs(s - tgt_s)
    lum_score = 1.0 - abs(l - tgt_l)
    return (_W_SAT * sat_score + _W_LUM * lum_score + _W_POP * pop) / (
        _W_SAT + _W_LUM + _W_POP
    )


def extract_colors(image_path: Path) -> dict:
    """
    Return a dict with keys: vibrant, vibrantDark, vibrantLight,
    muted, mutedDark, mutedLight, dominant.
    Values are signed 32-bit ARGB ints, or None when no qualifying swatch found.
    """
    from PIL import Image  # imported here so the error is clear if Pillow missing

    img = Image.open(image_path).convert("RGB")
    img.thumbnail((100, 100), Image.Resampling.LANCZOS)

    # Median-cut quantization — same algorithm as Android Palette
    quantized = img.quantize(colors=16, method=Image.Quantize.MEDIANCUT, dither=0)
    palette_flat = quantized.getpalette()   # [R, G, B, R, G, B, ...]

    # Count pixels per palette entry
    get_pixels = getattr(quantized, "get_flattened_data", quantized.getdata)
    counts: dict[int, int] = {}
    for idx in get_pixels():
        counts[idx] = counts.get(idx, 0) + 1

    total = sum(counts.values())

    # Build list of (r, g, b, population_fraction)
    swatches: list[tuple[int, int, int, float]] = []
    for idx, cnt in counts.items():
        base = idx * 3
        swatches.append((palette_flat[base], palette_flat[base + 1],
                         palette_flat[base + 2], cnt / total))

    result: dict[str, int | None] = {}

    for name, params in TARGETS.items():
        best_score = 0.0
        best_rgb: tuple[int, int, int] | None = None
        for r, g, b, pop in swatches:
            h, s, l = rgb_to_hsl(r, g, b)
            sc = _score(s, l, pop, *params)
            if sc > best_score:
                best_score = sc
                best_rgb = (r, g, b)
        result[name] = to_argb_int(*best_rgb) if best_rgb else None

    # Dominant = highest pixel count
    if swatches:
        dom = max(swatches, key=lambda x: x[3])
        result["dominant"] = to_argb_int(dom[0], dom[1], dom[2])
    else:
        result["dominant"] = None

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--drawable-dir", required=True,
                        help="Path to drawable-nodpi directory")
    parser.add_argument("--output", required=True,
                        help="Output JSON file path")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        print("ERROR: Pillow is not installed. Run: pip install Pillow", file=sys.stderr)
        return 1

    drawable_dir = Path(args.drawable_dir)
    if not drawable_dir.is_dir():
        print(f"ERROR: drawable dir not found: {drawable_dir}", file=sys.stderr)
        return 1

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Collect base images
    candidates = [
        p for p in sorted(drawable_dir.iterdir())
        if p.suffix.lower() in IMAGE_EXTS and is_base_image(p.stem)
    ]

    print(f"Found {len(candidates)} base images in {drawable_dir}")

    colors_map: dict[str, dict] = {}
    errors = 0

    for i, img_path in enumerate(candidates, 1):
        key = img_path.stem  # resource entry name, e.g. "acaipalm"
        try:
            colors_map[key] = extract_colors(img_path)
            if args.verbose:
                print(f"  [{i}/{len(candidates)}] {key}")
        except Exception as exc:
            print(f"  WARN: skipping {img_path.name}: {exc}", file=sys.stderr)
            errors += 1

    output_path.write_text(json.dumps(colors_map, separators=(",", ":")), encoding="utf-8")

    print(f"Wrote {len(colors_map)} entries -> {output_path}")
    if errors:
        print(f"WARNING: {errors} images failed (see above)", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
