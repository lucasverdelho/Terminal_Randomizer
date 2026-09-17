"""
Extract a colour palette from every image in the photos folder and cache it,
then turn a palette into a readable Windows Terminal colour scheme.

Run directly to (re)build the cache:
    python pre_load_images.py            # only new / changed images
    python pre_load_images.py --force    # everything
"""
from __future__ import annotations

import argparse
import colorsys
import json
import os
import sys
from pathlib import Path

from PIL import Image

# All paths are relative to this file, so the scripts work from any folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PHOTOS_DIR = PROJECT_ROOT / "photos"
INPUT_DIR = PROJECT_ROOT / "input_files"
CACHE_DIR = PROJECT_ROOT / "cache"
CACHE_FILE = CACHE_DIR / "palettes.json"

# Formats Windows Terminal can show as a background image.
IMAGE_EXTENSIONS = {".gif", ".png", ".jpg", ".jpeg", ".bmp"}

CACHE_VERSION = 2
PALETTE_SIZE = 6      # colours extracted per image
SAMPLE_FRAMES = 8     # GIF frames sampled (the background animates)
SAMPLE_SIZE = 128     # frames are shrunk to this before sampling

_MEDIANCUT = getattr(getattr(Image, "Quantize", Image), "MEDIANCUT", 0)


# --------------------------------------------------------------------------
# Palette extraction + cache
# --------------------------------------------------------------------------
def list_photos(photos_dir: Path = PHOTOS_DIR) -> list[Path]:
    """Image files in photos_dir (ignores desktop.ini, Thumbs.db, folders...)."""
    if not photos_dir.is_dir():
        return []
    return sorted(
        p for p in photos_dir.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )


def extract_palette(path: Path, size: int = PALETTE_SIZE) -> list[list[int]]:
    """Return [[r, g, b, pixel_count], ...], most common colour first.

    Samples several frames of animated GIFs, not just the first one.
    Transparent areas count as black, since that is what shows through
    on a dark terminal.
    """
    pixels: list[tuple[int, int, int]] = []
    with Image.open(path) as img:
        n_frames = getattr(img, "n_frames", 1)
        step = max(1, n_frames // SAMPLE_FRAMES)
        for index in range(0, n_frames, step)[:SAMPLE_FRAMES]:
            img.seek(index)
            frame = img.convert("RGBA")
            frame.thumbnail((SAMPLE_SIZE, SAMPLE_SIZE))
            backdrop = Image.new("RGBA", frame.size, (0, 0, 0, 255))
            pixels.extend(Image.alpha_composite(backdrop, frame).convert("RGB").getdata())

    sample = Image.new("RGB", (len(pixels), 1))
    sample.putdata(pixels)
    quantized = sample.quantize(colors=size, method=_MEDIANCUT)
    flat = quantized.getpalette()
    counts = sorted(quantized.getcolors(), reverse=True)
    return [[*flat[i * 3:i * 3 + 3], count] for count, i in counts]


def _fingerprint(path: Path) -> list[int]:
    stat = path.stat()
    return [stat.st_size, int(stat.st_mtime)]


def load_cache() -> dict:
    try:
        data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict) or data.get("version") != CACHE_VERSION:
        return {}
    return data.get("photos", {})


def save_cache(entries: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CACHE_FILE.with_suffix(".tmp")
    tmp.write_text(
        json.dumps({"version": CACHE_VERSION, "photos": entries}, indent=2),
        encoding="utf-8",
    )
    os.replace(tmp, CACHE_FILE)


def update_cache(photos: list[Path], force: bool = False, verbose: bool = True) -> dict:
    """Make sure every photo has an up-to-date palette; return {name: palette}.

    Only new or modified images are processed, so this is fast after the
    first run. Images that fail to load are reported and skipped.
    """
    cache = {} if force else load_cache()
    result: dict = {}
    changed = False

    for photo in photos:
        entry = cache.get(photo.name)
        fingerprint = _fingerprint(photo)
        if entry and entry.get("fingerprint") == fingerprint and entry.get("palette"):
            result[photo.name] = entry
            continue
        if verbose:
            print(f"Analysing colours of {photo.name} ...")
        try:
            palette = extract_palette(photo)
        except Exception as exc:  # corrupt / unsupported file
            print(f"  skipped {photo.name}: {exc}", file=sys.stderr)
            continue
        result[photo.name] = {"fingerprint": fingerprint, "palette": palette}
        changed = True

    # Drop entries for photos that were deleted.
    if changed or set(cache) != set(result):
        save_cache(result)
    return {name: entry["palette"] for name, entry in result.items()}


# --------------------------------------------------------------------------
# Colour helpers
# --------------------------------------------------------------------------
def rgb_to_hex(rgb) -> str:
    """(r, g, b) -> '#rrggbb', always 6 zero-padded digits."""
    r, g, b = (max(0, min(255, round(c))) for c in rgb)
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    if len(value) != 6:
        raise ValueError(f"{hex_color!r} is not in #rrggbb format")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _hls(rgb) -> tuple[float, float, float]:
    return colorsys.rgb_to_hls(*(c / 255 for c in rgb[:3]))


def _hls_to_hex(h: float, l: float, s: float) -> str:
    return rgb_to_hex(c * 255 for c in colorsys.hls_to_rgb(h % 1.0, l, s))


def _chroma(rgb) -> float:
    """How colourful a colour is, 0 (grey) .. 1 (pure hue)."""
    return (max(rgb[:3]) - min(rgb[:3])) / 255


def _luminance(hex_color: str) -> float:
    def channel(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in hex_to_rgb(hex_color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a: str, b: str) -> float:
    la, lb = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


# --------------------------------------------------------------------------
# Palette -> terminal colours
# --------------------------------------------------------------------------
MONO_THRESHOLD = 0.08   # below this chroma an image is treated as greyscale
MIN_TEXT_CONTRAST = 7.0  # WCAG AAA for body text


def build_scheme(palette: list[list[int]], complementary: bool = False) -> dict[str, str]:
    """Derive readable terminal colours from an image palette.

    The old approach inverted the dominant colour, which often gave muddy
    or low-contrast text. Here we keep the image's hues but choose the
    lightness ourselves, so text is always bright on a very dark background.
    """
    if not palette:
        raise ValueError("empty palette")
    total = sum(p[3] for p in palette) or 1
    dominant = palette[0]

    # "Accent" = colourful AND reasonably common, so a few neon pixels
    # don't win over the actual mood of the image.
    def accent_score(p):
        return _chroma(p) * (p[3] / total) ** 0.5 + 0.01 * (p[3] / total)

    accents = sorted(palette, key=accent_score, reverse=True)
    primary = accents[0]
    ph, _, ps = _hls(primary)

    # Secondary accent: prefer a noticeably different hue for cursor/tab.
    secondary = primary
    for candidate in accents[1:]:
        ch, _, _ = _hls(candidate)
        hue_gap = min(abs(ch - ph), 1 - abs(ch - ph))
        if _chroma(candidate) >= MONO_THRESHOLD and hue_gap > 0.08:
            secondary = candidate
            break
    sh, _, ss = _hls(secondary)

    mono = _chroma(primary) < MONO_THRESHOLD

    def tone(h, s, lightness, s_min, s_max):
        return _hls_to_hex(h, lightness, 0.0 if mono else _clamp(s, s_min, s_max))

    text_hue = ph + 0.5 if complementary else ph
    bg_hue = _hls(dominant)[0] if _chroma(dominant) >= MONO_THRESHOLD else ph

    background = tone(bg_hue, _hls(dominant)[2], 0.06, 0.20, 0.45)

    # Brighten the text until it is comfortably readable.
    lightness = 0.78
    foreground = tone(text_hue, ps, lightness, 0.45, 0.75)
    while contrast_ratio(foreground, background) < MIN_TEXT_CONTRAST and lightness < 0.95:
        lightness += 0.03
        foreground = tone(text_hue, ps, lightness, 0.45, 0.75)

    return {
        "background": background,
        "foreground": foreground,
        "cursorColor": tone(sh, ss, 0.68, 0.60, 0.90),
        "selectionBackground": tone(ph, ps, 0.32, 0.35, 0.60),
        "tabColor": tone(sh, ss, 0.42, 0.45, 0.75),
    }


def adaptive_opacity(palette: list[list[int]], low: int = 60, high: int = 90) -> int:
    """Window opacity (percent) from how bright the image is.

    Bright, busy images stay more opaque so the desktop behind the window
    doesn't make text harder to read; dark images can be more see-through.
    """
    total = sum(p[3] for p in palette) or 1
    brightness = sum((0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) / 255 * p[3]
                     for p in palette) / total
    # Most wallpapers sit between ~10% and ~60% brightness; spread that
    # range over low..high so the difference is actually visible.
    t = _clamp((brightness - 0.10) / 0.50, 0.0, 1.0)
    return round(low + (high - low) * t)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--photos", type=Path, default=PHOTOS_DIR,
                        help="folder with background images (default: %(default)s)")
    parser.add_argument("--force", action="store_true", help="re-analyse every image")
    args = parser.parse_args(argv)

    photos = list_photos(args.photos)
    if not photos:
        sys.exit(f"No images found in {args.photos}")
    palettes = update_cache(photos, force=args.force)
    for name, palette in palettes.items():
        print(f"{name:30} {build_scheme(palette)}")


if __name__ == "__main__":
    main()
