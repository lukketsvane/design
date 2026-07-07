#!/usr/bin/env python3
"""Gjer eit render-PNG om til ein liten SVG (JPEG-data-URI inni) som kan
lastast opp INLINE til Notion via notion-create-attachment (`content`).
Slik hamnar alle render i Galleri-databasen som faktiske bilete, utan at me
treng ein offentleg URL (repoet er privat) eller å sende store binaerfiler
gjennom verktoykall.

Bruk (i loopen, steg 5/persistence):
  python3 verkstad/tools/png_to_notion_svg.py <render.png> [width] [maxkib]
Skriv ein .svg ved sida av PNG-en (same namn, .notion.svg) og prentar stien.
Les den vesle SVG-en og send innhaldet som `content` til
notion-create-attachment; bruk markdown_source i ei ny Galleri-rad.

Galleri-database: collection 82c18616-62e5-4d02-aee9-564ca1b2c27f
(sjaa notion/manifest.json -> databases.galleri).
"""
import base64
import io
import sys

from PIL import Image


def png_to_notion_svg(png_path, out_svg=None, width=460, max_kib=170, quality=72):
    """Skriv ein SVG som pakkar eit nedskalert JPEG av PNG-en som data-URI.
    Held seg under Notion sin 200 KiB inline-grense (default mål 170 KiB)."""
    if out_svg is None:
        out_svg = png_path.rsplit(".", 1)[0] + ".notion.svg"
    im = Image.open(png_path).convert("RGB")
    w, h = im.size
    for cand_w in (width, 420, 380, 340, 300):
        for q in (quality, 62, 52, 44):
            im2 = im.resize((cand_w, max(1, int(h * cand_w / w))), Image.LANCZOS)
            buf = io.BytesIO()
            im2.save(buf, format="JPEG", quality=q, optimize=True)
            data = buf.getvalue()
            b64 = base64.b64encode(data).decode()
            W, H = im2.size
            svg = (
                '<svg xmlns="http://www.w3.org/2000/svg" '
                'xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
                f'<image width="{W}" height="{H}" '
                f'xlink:href="data:image/jpeg;base64,{b64}"/></svg>'
            )
            if len(svg.encode("utf-8")) <= max_kib * 1024:
                with open(out_svg, "w") as f:
                    f.write(svg)
                return out_svg, len(svg), W, H
    raise SystemExit(f"Fekk ikkje {png_path} under {max_kib} KiB")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    png = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 460
    maxkib = int(sys.argv[3]) if len(sys.argv) > 3 else 170
    out, n, W, H = png_to_notion_svg(png, width=width, max_kib=maxkib)
    print(f"{out}  ({n} bytes, {W}x{H})")
