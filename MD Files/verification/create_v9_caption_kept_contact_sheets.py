from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

render = Path(r"D:\Antigravity\Projects\SHM-Capstone\MD Files\verification\v9_render_20261030_caption_kept_final")
pages = sorted(render.glob("page-*.png"))
if len(pages) != 80:
    raise SystemExit(f"Expected 80 page images, got {len(pages)}")
columns, rows = 4, 5
thumb_w, thumb_h, label_h, gutter = 260, 337, 28, 18
cell_w, cell_h = thumb_w + gutter, thumb_h + label_h + gutter
font = ImageFont.truetype("arial.ttf", 16)
for start in range(0, 80, columns * rows):
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
    output = render / f"contact_{number:02d}.png"
    sheet.save(output)
    print(output)
