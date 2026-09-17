"""
Randomise the look of Windows Terminal: picks a random image from the
photos folder as the background and derives matching colours from it.

Examples:
    python terminal_randomizer.py
    python terminal_randomizer.py --opacity 85              # transparent window
    python terminal_randomizer.py --acrylic                 # blurred, 75% opaque
    python terminal_randomizer.py --acrylic --opacity 60    # blurred, 60% opaque
    python terminal_randomizer.py --acrylic --opacity auto  # opacity from image brightness
    python terminal_randomizer.py --profile "PowerShell" --profile "Ubuntu"
    python terminal_randomizer.py --settings "D:\\dotfiles\\wt\\settings.json"
    python terminal_randomizer.py --restore
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import random
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

import pre_load_images as images

# Checked in this order; override with --settings or WT_SETTINGS_PATH.
SETTINGS_CANDIDATES = [
    # Microsoft Store / winget (stable, preview, canary)
    r"%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json",
    r"%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe\LocalState\settings.json",
    r"%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminalCanary_8wekyb3d8bbwe\LocalState\settings.json",
    # Unpackaged (Scoop, Chocolatey, portable zip)
    r"%LOCALAPPDATA%\Microsoft\Windows Terminal\settings.json",
]

BACKUP_FILE = images.INPUT_DIR / "settings_backup.json"
SHADER_FILE = images.INPUT_DIR / "Retro.hlsl"
FONT_COLORS_FILE = images.INPUT_DIR / "font_colors.txt"

SHADER_KEY = "experimental.pixelShaderPath"
MANAGED_KEYS = ("backgroundImage", "backgroundImageOpacity", "background", "foreground",
                "cursorColor", "selectionBackground", "tabColor", "useAcrylic", "opacity")

IMAGE_OPACITY_RANGE = (0.15, 0.30)  # how strongly the background image shows
DEFAULT_ACRYLIC_OPACITY = 75        # window opacity for --acrylic without --opacity


# --------------------------------------------------------------------------
# settings.json handling
# --------------------------------------------------------------------------
def find_settings(explicit: str | None) -> Path:
    if explicit:
        candidates = [explicit]
    elif os.environ.get("WT_SETTINGS_PATH"):
        candidates = [os.environ["WT_SETTINGS_PATH"]]
    else:
        candidates = SETTINGS_CANDIDATES

    for candidate in candidates:
        path = Path(os.path.expandvars(os.path.expanduser(candidate)))
        if path.is_file():
            return path

    tried = "\n  ".join(os.path.expandvars(c) for c in candidates)
    sys.exit("Could not find Windows Terminal's settings.json. Tried:\n  " + tried +
             "\nOpen Terminal > Settings > 'Open JSON file' to see where yours is, "
             "then pass it with --settings.")


def _strip_jsonc(text: str) -> str:
    """Remove // and /* */ comments and trailing commas, leaving strings intact.

    Windows Terminal allows these in settings.json, but Python's json does not.
    """
    def scan(src, handle):
        out, i, in_string = [], 0, False
        while i < len(src):
            ch = src[i]
            if in_string:
                out.append(ch)
                if ch == "\\" and i + 1 < len(src):
                    out.append(src[i + 1])
                    i += 1
                elif ch == '"':
                    in_string = False
                i += 1
            elif ch == '"':
                in_string = True
                out.append(ch)
                i += 1
            else:
                i = handle(src, i, out)
        return "".join(out)

    def comments(src, i, out):
        if src.startswith("//", i):
            end = src.find("\n", i)
            return len(src) if end == -1 else end
        if src.startswith("/*", i):
            end = src.find("*/", i + 2)
            out.append(" ")
            return len(src) if end == -1 else end + 2
        out.append(src[i])
        return i + 1

    def trailing_commas(src, i, out):
        if src[i] == ",":
            rest = src[i + 1:].lstrip()
            if rest[:1] in ("}", "]"):
                return i + 1
        out.append(src[i])
        return i + 1

    return scan(scan(text, comments), trailing_commas)


def load_settings(path: Path) -> dict:
    # utf-8-sig: settings.json is UTF-8 (often with emoji); Windows' default
    # cp1252 would garble or crash on it.
    text = path.read_text(encoding="utf-8-sig")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            return json.loads(_strip_jsonc(text))
        except json.JSONDecodeError as exc:
            sys.exit(f"{path} is not valid JSON ({exc}). Fix it in Terminal first.")


def write_settings(path: Path, data: dict) -> None:
    """Write via a temp file + rename, so a crash never leaves a half-written
    settings.json (which would reset Terminal to defaults)."""
    target = Path(os.path.realpath(path))  # keep symlinked dotfiles intact
    text = json.dumps(data, indent=4, ensure_ascii=False) + "\n"
    fd, tmp = tempfile.mkstemp(prefix="settings.", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        for attempt in range(5):  # Terminal may briefly hold the file while reloading
            try:
                os.replace(tmp, target)
                return
            except PermissionError:
                if attempt == 4:
                    raise
                time.sleep(0.2)
    finally:
        with contextlib.suppress(OSError):
            os.unlink(tmp)


def backup_settings(path: Path) -> None:
    """Keep a copy of the settings as they were before the first run."""
    if not BACKUP_FILE.exists():
        shutil.copy2(path, BACKUP_FILE)  # raw copy keeps any comments
        print(f"Backed up your original settings to {BACKUP_FILE}")


def target_profiles(settings: dict, names: list[str]) -> list[dict]:
    """Profiles to modify: 'defaults' (all profiles) or the named ones."""
    profiles = settings.get("profiles")
    if isinstance(profiles, list):  # very old settings format
        profiles = settings["profiles"] = {"list": profiles}
    elif not isinstance(profiles, dict):
        profiles = settings["profiles"] = {}

    if not names:
        defaults = profiles.get("defaults")
        if not isinstance(defaults, dict):
            defaults = profiles["defaults"] = {}
        return [defaults]

    wanted = {n.casefold(): n for n in names}
    found = [p for p in profiles.get("list", [])
             if str(p.get("name", "")).casefold() in wanted]
    missing = set(wanted) - {str(p.get("name", "")).casefold() for p in found}
    if missing:
        available = ", ".join(repr(p.get("name")) for p in profiles.get("list", []))
        sys.exit(f"Profile(s) not found: {', '.join(wanted[m] for m in missing)}\n"
                 f"Available: {available}")
    return found


def warn_about_overrides(settings: dict) -> None:
    """Values set on a single profile beat 'defaults', so point those out."""
    for profile in settings["profiles"].get("list", []):
        keys = [k for k in MANAGED_KEYS if k in profile]
        if keys:
            print(f"Note: profile {profile.get('name')!r} sets {', '.join(keys)} itself, "
                  "so it won't follow the random theme. Remove those keys from it, "
                  "or use --clean-overrides.")


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def _is_our_shader(value) -> bool:
    if not isinstance(value, str) or not value:
        return False

    def norm(path):
        return os.path.normcase(os.path.abspath(os.path.expandvars(path)))
    return norm(value) == norm(str(SHADER_FILE))


def pick_photo(photos: list[Path], current: str | None) -> Path:
    """Random photo, avoiding the one already shown when possible."""
    current_norm = os.path.normcase(current or "")
    choices = [p for p in photos if os.path.normcase(str(p)) != current_norm]
    return random.choice(choices or photos)


def load_font_colors() -> list[str]:
    try:
        text = FONT_COLORS_FILE.read_text(encoding="utf-8")
    except OSError:
        return []
    return re.findall(r"#[0-9a-fA-F]{6}\b", text)


def window_settings(acrylic: bool, opacity, palette) -> dict:
    """useAcrylic/opacity for the chosen transparency mode.

    acrylic  opacity   result
    no       -         solid window (opacity 100)
    no       N/auto    plain transparency
    yes      -         blurred, DEFAULT_ACRYLIC_OPACITY
    yes      N/auto    blurred at that opacity
    """
    if opacity == "auto":
        opacity = images.adaptive_opacity(palette)
    elif opacity is None:
        opacity = DEFAULT_ACRYLIC_OPACITY if acrylic else 100
    return {"useAcrylic": acrylic, "opacity": opacity}


def describe_window(window: dict) -> str:
    if window["useAcrylic"]:
        return f"acrylic, {window['opacity']}% opaque"
    if window["opacity"] < 100:
        return f"transparent, {window['opacity']}% opaque"
    return "solid"


# --------------------------------------------------------------------------
# Command-line arguments
# --------------------------------------------------------------------------
def opacity_arg(value: str):
    """argparse type for --opacity: 'auto' or a whole number 0-100."""
    if value.lower() == "auto":
        return "auto"
    try:
        number = int(value.rstrip("%"))
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected a number 0-100 or 'auto', got {value!r}")
    if not 0 <= number <= 100:
        raise argparse.ArgumentTypeError(f"must be between 0 and 100, got {number}")
    return number


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--settings", help="path to settings.json (auto-detected by default)")
    parser.add_argument("--photos", type=Path, default=images.PHOTOS_DIR,
                        help="folder with background images (default: %(default)s)")
    parser.add_argument("--profile", action="append", default=[], metavar="NAME",
                        help="only change this profile (repeatable). Default: all profiles")

    look = parser.add_argument_group("appearance")
    look.add_argument("--shader", action="store_true",
                      help="turn on the retro CRT shader (off by default)")
    look.add_argument("--acrylic", action="store_true",
                      help="blur what's behind the window (Acrylic). "
                           f"Uses {DEFAULT_ACRYLIC_OPACITY}%% opacity unless --opacity is given")
    look.add_argument("--opacity", type=opacity_arg, metavar="PERCENT|auto",
                      help="window opacity 0-100. Without --acrylic this is plain "
                           "transparency. 'auto' picks it from the image's brightness")
    look.add_argument("--font-colors", action="store_true",
                      help="pick text colour from input_files/font_colors.txt instead")
    look.add_argument("--complementary", action="store_true",
                      help="use the complementary hue for text (the old look)")

    maint = parser.add_argument_group("maintenance")
    maint.add_argument("--clean-overrides", action="store_true",
                       help="remove theme keys set on individual profiles")
    maint.add_argument("--rebuild-cache", action="store_true", help="re-analyse all images")
    maint.add_argument("--dry-run", action="store_true",
                       help="show the changes without writing them")
    maint.add_argument("--restore", action="store_true",
                       help="put back the settings backed up on the first run")
    return parser.parse_args(argv)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    settings_path = find_settings(args.settings)

    if args.restore:
        if not BACKUP_FILE.exists():
            sys.exit(f"No backup found at {BACKUP_FILE}")
        shutil.copyfile(BACKUP_FILE, os.path.realpath(settings_path))
        print(f"Restored {settings_path} from {BACKUP_FILE}")
        return

    photos = images.list_photos(args.photos)
    if not photos:
        sys.exit(f"No images ({', '.join(sorted(images.IMAGE_EXTENSIONS))}) "
                 f"found in {args.photos}")

    palettes = images.update_cache(photos, force=args.rebuild_cache)
    photos = [p for p in photos if p.name in palettes]  # skip unreadable ones
    if not photos:
        sys.exit("None of the images could be read.")

    settings = load_settings(settings_path)
    targets = target_profiles(settings, args.profile)

    photo = pick_photo(photos, targets[0].get("backgroundImage"))
    palette = palettes[photo.name]
    scheme = images.build_scheme(palette, complementary=args.complementary)
    if args.font_colors:
        font_colors = load_font_colors()
        if font_colors:
            scheme["foreground"] = random.choice(font_colors)
        else:
            print(f"No colours found in {FONT_COLORS_FILE}; using image colours.")

    # backgroundImageOpacity = how visible the image is inside the window;
    # opacity = how much of the desktop shows through the window itself.
    window = window_settings(args.acrylic, args.opacity, palette)
    changes = {
        **scheme,
        "backgroundImage": str(photo),
        "backgroundImageOpacity": round(random.uniform(*IMAGE_OPACITY_RANGE), 2),
        **window,
    }

    for profile in targets:
        profile.update(changes)
        profile.setdefault("padding", "15")
        if not args.shader:
            # Only remove our own shader; leave any shader you set up yourself.
            if _is_our_shader(profile.get(SHADER_KEY)):
                del profile[SHADER_KEY]
        elif SHADER_FILE.is_file():
            profile[SHADER_KEY] = str(SHADER_FILE)
        else:
            print(f"Shader enabled but {SHADER_FILE} is missing; skipping it.")

    if args.clean_overrides and not args.profile:
        for profile in settings["profiles"].get("list", []):
            for key in MANAGED_KEYS:
                profile.pop(key, None)
    elif not args.profile:
        warn_about_overrides(settings)

    print(f"Background: {photo.name}")
    print(f"  {'shader':22} {'on' if args.shader else 'off'}")
    print(f"  {'window':22} {describe_window(window)}")
    for key, value in changes.items():
        if key not in ("backgroundImage", *window):
            print(f"  {key:22} {value}")

    if args.dry_run:
        print("(dry run - settings.json not changed)")
        return

    backup_settings(settings_path)
    write_settings(settings_path, settings)


if __name__ == "__main__":
    main()
