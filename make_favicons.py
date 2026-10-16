from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parent
STATIC_DIR = PROJECT_ROOT / "static"
SOURCE_IMAGE = STATIC_DIR / "Malitinne-logo.png"
BACKGROUND = (255, 255, 255, 255)


def square(image, size, pad=0.1):
    canvas = Image.new("RGBA", (size, size), BACKGROUND)
    inner_size = int(size * (1 - pad * 2))
    resized = image.copy()
    resized.thumbnail((inner_size, inner_size), Image.Resampling.LANCZOS)
    canvas.paste(
        resized,
        ((size - resized.width) // 2, (size - resized.height) // 2),
        resized,
    )
    return canvas


def main():
    with Image.open(SOURCE_IMAGE) as source:
        logo = source.convert("RGBA")

    outputs = {
        "favicon-512.png": square(logo, 512),
        "favicon-192.png": square(logo, 192),
        "apple-touch-icon.png": square(logo, 180),
        "favicon-48.png": square(logo, 48),
    }
    for filename, image in outputs.items():
        image.save(STATIC_DIR / filename)

    square(logo, 256).save(
        STATIC_DIR / "favicon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64)],
    )
    print("Created: " + ", ".join(outputs) + ", favicon.ico")


if __name__ == "__main__":
    main()
