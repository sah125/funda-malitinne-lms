"""Generate crisp favicons from the Malitinne logo.

The full logo is a wide wordmark, which becomes an unreadable smudge at
16-48px. Browsers need a *square* mark, so this script crops just the
golden key emblem (top part of the logo, above the word MALITINNE) and
places it on the brand navy tile so it stays readable at every size.

Run:  python make_favicons.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

PROJECT_ROOT = Path(__file__).resolve().parent
STATIC_DIR = PROJECT_ROOT / "static"
SOURCE_IMAGE = STATIC_DIR / "Malitinne-logo.png"
NAVY = (26, 26, 46, 255)        # --navy  #1a1a2e
GOLD = (201, 169, 110, 255)     # --gold-light #c9a96e


def emblem(logo):
    """Crop the key + hands emblem (everything above the wordmark)."""
    alpha = logo.split()[3]
    width, height = logo.size
    # find first fully empty row band between emblem and wordmark
    rows = [sum(1 for x in range(width) if alpha.getpixel((x, y)) > 20) for y in range(height)]
    top = next(y for y in range(height) if rows[y])
    gap = next(y for y in range(top + 20, height) if rows[y] == 0)
    band = logo.crop((0, top, width, gap))
    return band.crop(band.split()[3].getbbox())


def lighten(img):
    """Make the grey hands light so they read on navy; keep the gold key."""
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a and abs(r - g) < 18 and abs(g - b) < 18:   # greyish pixel
                px[x, y] = (235, 230, 220, a)
    return img


def tile(mark, size, radius_ratio=0.22, pad=0.14):
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=int(size * radius_ratio), fill=NAVY)
    inner = int(size * (1 - pad * 2))
    m = mark.copy()
    m.thumbnail((inner, inner), Image.Resampling.LANCZOS)
    canvas.paste(m, ((size - m.width) // 2, (size - m.height) // 2), m)
    # thin gold ring for definition on dark browser tabs
    if size >= 64:
        w = max(2, size // 64)
        draw.rounded_rectangle((w, w, size - 1 - w, size - 1 - w), radius=int(size * radius_ratio) - w, outline=GOLD, width=w)
    return canvas


def main():
    with Image.open(SOURCE_IMAGE) as source:
        logo = source.convert("RGBA")
    mark = lighten(emblem(logo))

    outputs = {
        "favicon-512.png": tile(mark, 512),
        "favicon-192.png": tile(mark, 192),
        "favicon-48.png": tile(mark, 48),
        "favicon-32.png": tile(mark, 32, pad=0.08),
        "favicon-16.png": tile(mark, 16, pad=0.04),
    }
    # Apple ignores transparency: full-bleed navy square
    apple = Image.new("RGBA", (180, 180), NAVY)
    m = mark.copy(); m.thumbnail((140, 140), Image.Resampling.LANCZOS)
    apple.paste(m, ((180 - m.width) // 2, (180 - m.height) // 2), m)
    outputs["apple-touch-icon.png"] = apple

    for filename, image in outputs.items():
        image.save(STATIC_DIR / filename, optimize=True)

    big = tile(mark, 256)
    big.save(STATIC_DIR / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    print("Created: " + ", ".join(outputs) + ", favicon.ico")


if __name__ == "__main__":
    main()
