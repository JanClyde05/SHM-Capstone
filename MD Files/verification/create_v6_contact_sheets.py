from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
RENDER_DIR = ROOT / "MD Files/verification/v6_render"
pages = sorted(RENDER_DIR.glob("page-*.png"))
if len(pages) != 80:
    raise RuntimeError(f"Expected 80 rendered page images, found {len(pages)}")

columns, rows = 4, 5
thumb_w, thumb_h = 260, 337
label_h, gutter = 28, 18
cell_w, cell_h = thumb_w + gutter, thumb_h + label_h + gutter
font = ImageFont.truetype("arial.ttf", 16)

for start in range(0, len(pages), columns * rows):
    subset = pages[start:start + columns * rows]
    sheet = Image.new("RGB", (columns * cell_w + gutter, rows * cell_h + gutter), "white")
    draw = ImageDraw.Draw(sheet)
    for offset, path in enumerate(subset):
        page = Image.open(path).convert("RGB")
        page.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        col, row = offset % columns, offset // columns
        x, y = gutter + col * cell_w, gutter + row * cell_h
        draw.text((x, y), f"Physical page {start + offset + 1}", fill="black", font=font)
        sheet.paste(page, (x, y + label_h))
    number = start // (columns * rows) + 1
    output = RENDER_DIR / f"contact_{number:02d}.png"
    sheet.save(output)
    print(output)
