# Requiere Pillow: pip install Pillow
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT_DIR = Path(__file__).parent
MAIN = OUT_DIR / "placeholder.png"
THUMB = OUT_DIR / "placeholder_thumb.png"

def make_placeholder(path: Path, size=(800,800), text="No Image"):
    img = Image.new("RGB", size, (240,240,240))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", int(size[1]*0.08))
    except Exception:
        font = ImageFont.load_default()

    # Compatibilidad con distintas versiones de Pillow
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
    except AttributeError:
        try:
            w, h = font.getsize(text)
        except Exception:
            w, h = (len(text) * 10, int(size[1] * 0.08))

    draw.text(((size[0]-w)/2, (size[1]-h)/2), text, fill=(120,120,120), font=font)
    img.save(path, optimize=True)

if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    make_placeholder(MAIN, size=(800,800), text="No Image")
    make_placeholder(THUMB, size=(240,240), text="No Image")
    print(f"Generado: {MAIN} y {THUMB}")