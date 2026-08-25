#!/usr/bin/env python3
"""Normalize generated action boards into stable schema-v2 transparent sprite strips."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageFilter


REQUIRED_ACTION_FRAMES = {
    "idle": 4,
    "walk": 6,
    "rest": 4,
    "happy": 4,
    "drag": 2,
    "land": 4,
    "wave": 4,
    "signature": 6,
    "curious": 4,
    "stretch": 5,
    "tiptoe": 4,
    "play": 6,
}
OPTIONAL_ACTION_FRAMES = {
    "fall": 4,
    "touch": 5,
}
ACTION_FRAMES = {**REQUIRED_ACTION_FRAMES, **OPTIONAL_ACTION_FRAMES}


def matte_rgb(source: Image.Image) -> Image.Image:
    """Remove a baked white/checkerboard background without inventing opaque holes."""
    rgb = source.convert("RGB")
    pixels = rgb.load()
    alpha = Image.new("L", rgb.size, 0)
    alpha_pixels = alpha.load()
    for y in range(rgb.height):
        for x in range(rgb.width):
            red, green, blue = pixels[x, y]
            chroma = max(red, green, blue) - min(red, green, blue)
            darkest = min(red, green, blue)
            if darkest < 185:
                alpha_pixels[x, y] = 255
            elif chroma > 18 and darkest < 248:
                alpha_pixels[x, y] = min(255, 72 + chroma * 7)
    alpha = alpha.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.55))
    rgb.putalpha(alpha)
    return rgb


def clean_cross_frame_spill(frame: Image.Image, action: str) -> Image.Image:
    """Drop isolated marks that crossed a model-generated cell boundary."""
    rgba = frame.convert("RGBA")
    pixels = rgba.load()
    colored = Image.new("L", rgba.size, 0)
    colored_pixels = colored.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            red, green, blue, alpha = pixels[x, y]
            if alpha > 24 and max(red, green, blue) - min(red, green, blue) > 18:
                colored_pixels[x, y] = 255
    body = colored.getbbox()
    if body is None:
        return rgba
    body_width = body[2] - body[0]
    margin_ratio = 0.52 if action in {"happy", "wave", "signature", "touch", "fall"} else 0.24
    margin = max(12, round(body_width * margin_ratio))
    keep_left = max(0, body[0] - margin)
    keep_right = min(rgba.width, body[2] + margin)
    mask = rgba.getchannel("A")
    mask_pixels = mask.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            if x < keep_left or x >= keep_right:
                mask_pixels[x, y] = 0
    rgba.putalpha(mask)
    return rgba


def split_frames(source: Image.Image, count: int, action: str) -> list[Image.Image]:
    frames: list[Image.Image] = []
    for index in range(count):
        left = round(index * source.width / count)
        right = round((index + 1) * source.width / count)
        cell = source.crop((left, 0, right, source.height))
        prepared = cell.convert("RGBA") if "A" in cell.getbands() else matte_rgb(cell)
        frames.append(clean_cross_frame_spill(prepared, action))
    return frames


def normalize_frames(frames: list[Image.Image], action: str, canvas: int = 256) -> list[Image.Image]:
    boxes = [frame.getchannel("A").getbbox() for frame in frames]
    if any(box is None for box in boxes):
        raise ValueError("generated strip contains an empty frame")
    concrete = [box for box in boxes if box is not None]
    median_height = sorted(box[3] - box[1] for box in concrete)[len(concrete) // 2]
    median_width = sorted(box[2] - box[0] for box in concrete)[len(concrete) // 2]
    scale = min(210 / median_height, 220 / median_width)

    normalized: list[Image.Image] = []
    for frame, box in zip(frames, concrete, strict=True):
        resized = frame.resize(
            (max(1, round(frame.width * scale)), max(1, round(frame.height * scale))),
            Image.Resampling.LANCZOS,
        )
        frame_center = (box[0] + box[2]) / 2
        frame_bottom = box[3]
        x = round(128 - frame_center * scale)
        y = round(232 - frame_bottom * scale)
        target = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
        target.alpha_composite(resized, (x, y))
        normalized.append(target)
    if action == "idle":
        visible = [frame.getchannel("A").getbbox() for frame in normalized]
        target_width = sorted(box[2] - box[0] for box in visible)[len(visible) // 2]
        target_height = sorted(box[3] - box[1] for box in visible)[len(visible) // 2]
        stabilized = []
        for frame, box in zip(normalized, visible, strict=True):
            subject = frame.crop(box).resize((target_width, target_height), Image.Resampling.LANCZOS)
            target = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
            target.alpha_composite(subject, (round(128 - target_width / 2), 232 - target_height))
            stabilized.append(target)
        normalized = stabilized
    elif action == "walk":
        stabilized = []
        for frame in normalized:
            box = frame.getchannel("A").getbbox()
            dx = round(128 - (box[0] + box[2]) / 2)
            dy = 232 - box[3]
            target = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
            target.alpha_composite(frame, (dx, dy))
            stabilized.append(target)
        normalized = stabilized
    return normalized


def write_strip(frames: list[Image.Image], destination: Path) -> None:
    strip = Image.new("RGBA", (256 * len(frames), 256), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        strip.alpha_composite(frame, (index * 256, 0))
    destination.parent.mkdir(parents=True, exist_ok=True)
    strip.save(destination, lossless=True, method=6)


def prepare_directory(source_directory: Path, destination: Path) -> None:
    missing = [action for action in REQUIRED_ACTION_FRAMES if not (source_directory / f"{action}.png").is_file()]
    if missing:
        raise ValueError(f"missing required actions: {', '.join(missing)}")

    for action, count in ACTION_FRAMES.items():
        source = source_directory / f"{action}.png"
        if not source.is_file():
            print(f"skipped optional {action}: source not found")
            continue
        with Image.open(source) as image:
            frames = split_frames(image, count, action)
        normalized = normalize_frames(frames, action)
        write_strip(normalized, destination / f"{action}.webp")
        print(f"prepared {action}: {count} frames")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Directory containing raw action PNGs")
    parser.add_argument("destination", type=Path, help="Destination animations directory")
    args = parser.parse_args()

    try:
        prepare_directory(args.source, args.destination)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
