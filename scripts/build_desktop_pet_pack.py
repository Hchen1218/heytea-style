#!/usr/bin/env python3
"""Build review artifacts and a validated desktop-pet ZIP from a pack directory."""

from __future__ import annotations

import argparse
import json
import tempfile
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from validate_desktop_pet_pack import OPTIONAL_ACTIONS, REQUIRED_ACTIONS, PackValidationError, validate_pack, validate_pack_directory
from build_desktop_pet_delivery import build_delivery, current_platform


def review_actions(manifest: dict) -> list[str]:
    return [*REQUIRED_ACTIONS, *(name for name in OPTIONAL_ACTIONS if name in manifest["actions"])]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/SFNS.ttf",
        "C:/Windows/Fonts/arial.ttf",
    )
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except OSError:
                pass
    return ImageFont.load_default()


def read_frames(root: Path, manifest: dict, action_name: str) -> list[Image.Image]:
    canvas = manifest["canvas"]
    action = manifest["actions"][action_name]
    with Image.open(root / action["file"]) as source:
        strip = source.convert("RGBA")
    width, height = canvas["width"], canvas["height"]
    return [strip.crop((index * width, 0, (index + 1) * width, height)) for index in range(action["frames"])]


def build_contact_sheet(root: Path, manifest: dict, out_path: Path) -> None:
    cell = 320
    header = 56
    actions = review_actions(manifest)
    rows = (len(actions) + 2) // 3
    sheet = Image.new("RGB", (cell * 3, (cell + header) * rows), "#F7F4EC")
    draw = ImageDraw.Draw(sheet)
    label_font = load_font(28)
    for index, action_name in enumerate(actions):
        action_frames = read_frames(root, manifest, action_name)
        frame = action_frames[len(action_frames) // 2]
        frame.thumbnail((cell - 40, cell - 40), Image.Resampling.LANCZOS)
        column, row = index % 3, index // 3
        x = column * cell + (cell - frame.width) // 2
        y = row * (cell + header) + (cell - frame.height) // 2
        sheet.paste(frame, (x, y), frame)
        draw.text((column * cell + 18, row * (cell + header) + cell + 8), action_name, fill="#111111", font=label_font)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)


def build_motion_preview(root: Path, manifest: dict, out_path: Path) -> None:
    canvas = manifest["canvas"]
    size = max(canvas["width"], canvas["height"], 256)
    label_height = 44
    output_frames: list[Image.Image] = []
    durations: list[int] = []
    font = load_font(24)
    for action_name in review_actions(manifest):
        action = manifest["actions"][action_name]
        duration = max(34, round(1000 / action["fps"]))
        for frame in read_frames(root, manifest, action_name):
            preview = Image.new("RGB", (size, size + label_height), "#F7F4EC")
            x = (size - frame.width) // 2
            y = (size - frame.height) // 2
            preview.paste(frame, (x, y), frame)
            draw = ImageDraw.Draw(preview)
            draw.text((16, size + 8), action_name, fill="#111111", font=font)
            output_frames.append(preview)
            durations.append(duration)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    output_frames[0].save(
        out_path,
        save_all=True,
        append_images=output_frames[1:],
        duration=durations,
        loop=0,
        optimize=False,
    )


def build_frame_audit(root: Path, manifest: dict, out_path: Path) -> None:
    columns, cell, label_height = 6, 160, 28
    actions = review_actions(manifest)
    rows: list[tuple[str, int, list[Image.Image]]] = []
    for action_name in actions:
        frames = read_frames(root, manifest, action_name)
        for start in range(0, len(frames), columns):
            rows.append((action_name, start, frames[start : start + columns]))
    sheet = Image.new("RGB", (columns * cell, len(rows) * (cell + label_height)), "#394052")
    draw = ImageDraw.Draw(sheet)
    font = load_font(18)
    for row, (action_name, start, frames) in enumerate(rows):
        for column, frame in enumerate(frames):
            preview = frame.copy()
            preview.thumbnail((cell - 12, cell - 12), Image.Resampling.LANCZOS)
            x = column * cell + (cell - preview.width) // 2
            y = row * (cell + label_height) + (cell - preview.height) // 2
            sheet.paste(preview, (x, y), preview)
            draw.text((column * cell + 8, row * (cell + label_height) + 6), f"#{start + column + 1}", fill="#FFFFFF", font=font)
        frame_range = f"{start + 1}-{start + len(frames)}"
        draw.text((8, row * (cell + label_height) + cell + 4), f"{action_name} · frames {frame_range}", fill="#FFFFFF", font=font)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)


def write_deterministic_zip(root: Path, out_path: Path, pack_id: str) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix="desktop-pet-pack-", suffix=".zip", delete=False, dir=out_path.parent) as handle:
        temp_path = Path(handle.name)
    try:
        with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for source in sorted(path for path in root.rglob("*") if path.is_file() and not path.is_symlink()):
                relative = source.relative_to(root)
                info = zipfile.ZipInfo((Path(pack_id) / relative).as_posix(), date_time=(2024, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, source.read_bytes())
        validate_pack(temp_path)
        temp_path.replace(out_path)
        out_path.chmod(0o644)
    finally:
        temp_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Validated pet directory")
    parser.add_argument("--out", type=Path, help="Output ZIP (omit with --review-only)")
    parser.add_argument("--review-dir", type=Path, help="Directory for contact sheet and GIF")
    parser.add_argument("--review-only", action="store_true", help="Build review artifacts without packaging")
    parser.add_argument("--delivery-dir", type=Path, help="Also build a launcher folder around the validated ZIP")
    parser.add_argument("--delivery-platform", choices=("macos", "windows", "all"), default=current_platform())
    args = parser.parse_args()

    try:
        result = validate_pack_directory(args.source)
        if not args.out and not args.review_only:
            parser.error("--out is required unless --review-only is used")
        if args.review_only and not args.review_dir:
            parser.error("--review-dir is required with --review-only")
        review_dir = args.review_dir or args.out.with_suffix("").with_name(f"{args.out.stem}-review")
        build_contact_sheet(result.root, result.manifest, review_dir / "contact-sheet.png")
        build_motion_preview(result.root, result.manifest, review_dir / "motion-preview.gif")
        build_frame_audit(result.root, result.manifest, review_dir / "frame-audit.png")
        if not args.review_only:
            write_deterministic_zip(result.root, args.out, result.pack_id)
            delivery = build_delivery(args.out, args.delivery_dir, args.delivery_platform) if args.delivery_dir else None
        else:
            delivery = None
    except (OSError, PackValidationError, ValueError) as exc:
        raise SystemExit(f"BUILD FAILED: {exc}") from exc

    summary = {
        "pack": None if args.review_only else str(args.out.resolve()),
        "packId": result.pack_id,
        "review": str(review_dir.resolve()),
        "schemaVersion": 2,
        "delivery": None if delivery is None else delivery["delivery"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
