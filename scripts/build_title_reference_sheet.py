#!/usr/bin/env python3
"""Build a private title construction reference sheet from extracted cutouts.

The default sheet is model-facing: it avoids English labels and does not render
the target title with a system font. The exact target text belongs in the prompt;
this sheet is only for layout pressure, malformed glyph rhythm, and stroke style.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = SKILL_DIR / "private-assets" / "reference-cutouts" / "asset-index.json"
DEFAULT_OUT = SKILL_DIR / "private-assets" / "reference-cutouts" / "title_reference_sheet.png"


FONT_CANDIDATES = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in FONT_CANDIDATES:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def load_records(index_path: Path) -> list[dict]:
    if not index_path.exists():
        raise SystemExit(
            f"Missing private asset index: {index_path}\n"
            "This helper needs reference cutouts. If this package does not include them, "
            "pass --index to a local asset index or use the text prompt workflow."
        )
    with index_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def by_name(records: list[dict]) -> dict[str, dict]:
    return {record["name"]: record for record in records}


def choose_records(records: list[dict], names: list[str], categories: tuple[str, ...], limit: int) -> list[dict]:
    lookup = by_name(records)
    selected = [lookup[name] for name in names if name in lookup]
    if selected:
        return selected[:limit]

    filtered = [
        record
        for record in records
        if record["category"] in categories
        and record.get("quality") in {"primary", "secondary"}
        and record.get("quality") != "avoid-default"
    ]
    return filtered[:limit]


def paste_fit(
    sheet: Image.Image,
    image: Image.Image,
    box: tuple[int, int, int, int],
    max_scale: float = 1.0,
) -> None:
    left, top, right, bottom = box
    target_w = right - left
    target_h = bottom - top
    working = image.copy().convert("RGBA")
    scale = min(target_w / working.width, target_h / working.height, max_scale)
    new_size = (max(1, int(working.width * scale)), max(1, int(working.height * scale)))
    working = working.resize(new_size, Image.Resampling.LANCZOS)
    x = left + (target_w - working.width) // 2
    y = top + (target_h - working.height) // 2
    sheet.paste(working, (x, y), working)


def draw_target_layout(
    draw: ImageDraw.ImageDraw,
    title: str,
    box: tuple[int, int, int, int],
    human_labels: bool,
) -> None:
    left, top, right, bottom = box
    draw.rectangle(box, outline=(215, 215, 215), width=2)
    if human_labels:
        draw.text((left + 18, top + 14), "Target layout only - exact text stays in prompt", fill=(0, 0, 0), font=load_font(28))

    chars = [char for char in title if not char.isspace()]
    guide_pen = (210, 210, 210)

    if len(chars) == 4:
        positions = [
            (left + 95, top + 95, 190, 185),
            (left + 92, top + 305, 205, 190),
            (left + 335, top + 135, 185, 180),
            (left + 318, top + 340, 215, 185),
        ]
    else:
        positions = []
        col_count = 2 if len(chars) > 3 else 1
        row_count = (len(chars) + col_count - 1) // col_count
        cell_w = 230
        cell_h = 165
        start_x = left + 90
        start_y = top + 105
        for idx, _char in enumerate(chars):
            col = idx // row_count
            row = idx % row_count
            positions.append((
                start_x + col * cell_w + (12 if row % 2 else 0),
                start_y + row * cell_h + (18 if col % 2 else 0),
                185,
                145,
            ))

    for idx, (x, y, w, h) in enumerate(positions[: len(chars)]):
        draw.rectangle((x, y, x + w, y + h), outline=guide_pen, width=2)
        # Small non-text guide marks push the model toward broken construction
        # without contaminating the target title with a standard system glyph.
        mark_x = x + 22 + (idx % 2) * 16
        mark_y = y + 24 + (idx % 3) * 10
        draw.line((mark_x, mark_y, mark_x + w * 0.35, mark_y + 7), fill=(225, 225, 225), width=2)
        draw.line((mark_x + 18, mark_y + 40, mark_x + 12, mark_y + h * 0.72), fill=(225, 225, 225), width=2)


def draw_record_grid(
    sheet: Image.Image,
    draw: ImageDraw.ImageDraw,
    records: list[dict],
    title: str,
    top: int,
    cell_size: tuple[int, int],
    cols: int,
    human_labels: bool,
) -> int:
    if human_labels:
        draw.text((60, top), title, fill=(0, 0, 0), font=load_font(38))
        y = top + 58
    else:
        y = top
    cell_w, cell_h = cell_size
    label_font = load_font(20)
    for idx, record in enumerate(records):
        col = idx % cols
        row = idx // cols
        left = 60 + col * cell_w
        top_cell = y + row * cell_h
        draw.rectangle((left, top_cell, left + cell_w - 18, top_cell + cell_h - 16), outline=(220, 220, 220), width=1)
        image = Image.open(SKILL_DIR / record["path"]).convert("RGBA")
        bottom_pad = 62 if human_labels else 18
        paste_fit(sheet, image, (left + 12, top_cell + 12, left + cell_w - 30, top_cell + cell_h - bottom_pad))
        if human_labels:
            draw.text((left + 12, top_cell + cell_h - 52), record["name"], fill=(0, 0, 0), font=label_font)
            draw.text((left + 12, top_cell + cell_h - 29), record["category"], fill=(90, 90, 90), font=label_font)

    rows = max(1, (len(records) + cols - 1) // cols)
    return y + rows * cell_h + 34


def build_sheet(args: argparse.Namespace) -> Path:
    records = load_records(args.index)
    title_blocks = choose_records(
        records,
        args.title_refs,
        ("lettering/title-blocks",),
        limit=3,
    )
    glyphs = choose_records(
        records,
        args.glyph_refs,
        ("lettering/glyphs",),
        limit=8,
    )
    strokes = choose_records(
        records,
        args.stroke_refs,
        ("lettering/strokes",),
        limit=8,
    )

    sheet = Image.new("RGB", (1600, 2200), "white")
    draw = ImageDraw.Draw(sheet)
    top = 60
    if args.human_labels:
        draw.text((60, 42), "Crooked title construction sheet", fill=(0, 0, 0), font=load_font(48))
        draw.text((60, 98), "Private local reference only. Model-facing sheets should omit labels.", fill=(70, 70, 70), font=load_font(26))
        top = 155
    draw_target_layout(draw, args.title, (60, top, 1540, top + 495), args.human_labels)

    next_y = draw_record_grid(sheet, draw, title_blocks, "1. Title block rhythm", top + 555, (480, 250), 3, args.human_labels)
    next_y = draw_record_grid(sheet, draw, glyphs, "2. Glyph skeleton specimens", next_y, (360, 230), 4, args.human_labels)
    draw_record_grid(sheet, draw, strokes, "3. Stroke and radical anatomy", next_y, (360, 220), 4, args.human_labels)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out)
    return args.out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True, help="Exact target title text.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output PNG path.")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX, help="asset-index.json path.")
    parser.add_argument("--title-ref", dest="title_refs", action="append", default=[], help="Asset name to use as title block reference.")
    parser.add_argument("--glyph-ref", dest="glyph_refs", action="append", default=[], help="Asset name to use as glyph reference.")
    parser.add_argument("--stroke-ref", dest="stroke_refs", action="append", default=[], help="Asset name to use as stroke reference.")
    parser.add_argument("--human-labels", action="store_true", help="Include section labels and asset names for human inspection. Default is model-facing with no extra text labels.")
    return parser.parse_args()


def main() -> None:
    out_path = build_sheet(parse_args())
    print(out_path)


if __name__ == "__main__":
    main()
