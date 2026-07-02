#!/usr/bin/env python3
"""Composite a black handwritten title layer onto a poster base."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageChops


def parse_measure(value: str, total: int) -> int:
    if value.endswith("%"):
        return round(float(value[:-1]) / 100 * total)
    return round(float(value))


def title_to_black_alpha(title: Image.Image, threshold: int) -> Image.Image:
    rgba = title.convert("RGBA")
    red, green, blue, source_alpha = rgba.split()
    gray = Image.merge("RGB", (red, green, blue)).convert("L")
    darkness = gray.point(lambda px: 255 if px < threshold else 0, mode="L")
    alpha = ImageChops.multiply(darkness, source_alpha)

    bbox = alpha.getbbox()
    if bbox:
        alpha = alpha.crop(bbox)
    else:
        raise ValueError("Title layer has no dark pixels to composite")

    black = Image.new("RGBA", alpha.size, (0, 0, 0, 255))
    black.putalpha(alpha)
    return black


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="Poster base image path")
    parser.add_argument("--title", required=True, help="Title layer image path")
    parser.add_argument("--out", required=True, help="Output image path")
    parser.add_argument("--x", default="8%", help="Left position, pixels or percent of base width")
    parser.add_argument("--y", default="7%", help="Top position, pixels or percent of base height")
    parser.add_argument("--width", default="42%", help="Title width, pixels or percent of base width")
    parser.add_argument("--threshold", type=int, default=210, help="Pixels darker than this become title ink")
    args = parser.parse_args()

    base_path = Path(args.base)
    title_path = Path(args.title)
    out_path = Path(args.out)

    base = Image.open(base_path).convert("RGBA")
    title = title_to_black_alpha(Image.open(title_path), args.threshold)

    target_width = parse_measure(args.width, base.width)
    target_height = round(title.height * target_width / title.width)
    title = title.resize((target_width, target_height), Image.Resampling.LANCZOS)

    x = parse_measure(args.x, base.width)
    y = parse_measure(args.y, base.height)
    base.alpha_composite(title, (x, y))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(out_path, quality=95)


if __name__ == "__main__":
    main()
