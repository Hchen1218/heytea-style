#!/usr/bin/env python3
"""Build version-aware review artifacts and a validated desktop-pet ZIP."""

from __future__ import annotations

import argparse
import json
import tempfile
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from validate_desktop_pet_pack import OPTIONAL_ACTIONS, REQUIRED_ACTIONS, PackValidationError, validate_pack, validate_pack_directory
from build_desktop_pet_delivery import build_delivery, current_platform


def load_font(size: int):
    for candidate in ("/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/SFNS.ttf", "C:/Windows/Fonts/arial.ttf"):
        try: return ImageFont.truetype(candidate, size=size)
        except OSError: pass
    return ImageFont.load_default()


def review_behaviors(manifest: dict) -> list[str]:
    if manifest["schemaVersion"] == 2: return [*REQUIRED_ACTIONS, *(name for name in OPTIONAL_ACTIONS if name in manifest["actions"])]
    return list(manifest["behaviors"])


def behavior_phases(manifest: dict, behavior: str) -> list[tuple[str, dict]]:
    if manifest["schemaVersion"] == 2: return [("play", manifest["actions"][behavior])]
    return [(phase["id"], phase) for phase in manifest["behaviors"][behavior]["phases"]]


def read_spec_frames(root: Path, manifest: dict, spec: dict) -> list[Image.Image]:
    width, height = manifest["canvas"]["width"], manifest["canvas"]["height"]
    with Image.open(root / spec["file"]) as source: strip = source.convert("RGBA")
    return [strip.crop((index * width, 0, (index + 1) * width, height)) for index in range(spec["frames"])]


def read_frames(root: Path, manifest: dict, behavior: str) -> list[Image.Image]:
    return [frame for _, spec in behavior_phases(manifest, behavior) for frame in read_spec_frames(root, manifest, spec)]


def build_contact_sheet(root: Path, manifest: dict, out_path: Path) -> None:
    cell, header, columns = 300, 50, 4 if manifest["schemaVersion"] == 3 else 3
    behaviors = review_behaviors(manifest); rows = (len(behaviors) + columns - 1) // columns
    sheet = Image.new("RGB", (cell * columns, (cell + header) * rows), "#F7F4EC"); draw = ImageDraw.Draw(sheet); font = load_font(25)
    for index, behavior in enumerate(behaviors):
        frames = read_frames(root, manifest, behavior); frame = frames[len(frames) // 2]; frame.thumbnail((cell - 36, cell - 36), Image.Resampling.LANCZOS)
        column, row = index % columns, index // columns; x = column * cell + (cell - frame.width) // 2; y = row * (cell + header) + (cell - frame.height) // 2
        sheet.paste(frame, (x, y), frame); draw.text((column * cell + 14, row * (cell + header) + cell + 7), behavior, fill="#111111", font=font)
    out_path.parent.mkdir(parents=True, exist_ok=True); sheet.save(out_path)


def build_behavior_timelines(root: Path, manifest: dict, out_path: Path) -> None:
    behaviors = review_behaviors(manifest); width, row_height = 1200, 118
    sheet = Image.new("RGB", (width, row_height * len(behaviors)), "#F7F4EC"); draw = ImageDraw.Draw(sheet); title = load_font(21); small = load_font(16)
    for row, behavior in enumerate(behaviors):
        y = row * row_height; draw.text((18, y + 10), behavior, fill="#111111", font=title)
        phases = behavior_phases(manifest, behavior); total = sum(spec["frames"] for _, spec in phases); x = 250
        for phase_name, spec in phases:
            segment = max(80, round((width - 280) * spec["frames"] / total)); color = "#D7EBC3" if spec.get("playback") == "loop" or spec.get("loop") else "#F4C3CD"
            draw.rounded_rectangle((x, y + 14, min(width - 18, x + segment - 5), y + 72), 10, fill=color, outline="#111111", width=2)
            draw.text((x + 9, y + 25), phase_name, fill="#111111", font=small); x += segment
        events = " → ".join(spec.get("completeOn", "animation-finished") for _, spec in phases)
        draw.text((250, y + 82), events, fill="#555555", font=small)
    out_path.parent.mkdir(parents=True, exist_ok=True); sheet.save(out_path)


def spec_durations(spec: dict) -> list[int]:
    if "durationsMs" in spec: return spec["durationsMs"]
    return [max(34, round(1000 / spec["fps"]))] * spec["frames"]


def build_motion_preview(root: Path, manifest: dict, out_path: Path) -> None:
    canvas = manifest["canvas"]; size = max(canvas["width"], canvas["height"], 256); label_height = 44
    output, durations, font = [], [], load_font(20)
    for behavior in review_behaviors(manifest):
        for phase_name, spec in behavior_phases(manifest, behavior):
            for frame, duration in zip(read_spec_frames(root, manifest, spec), spec_durations(spec), strict=True):
                preview = Image.new("RGB", (size, size + label_height), "#F7F4EC"); preview.paste(frame, ((size - frame.width) // 2, (size - frame.height) // 2), frame)
                ImageDraw.Draw(preview).text((12, size + 8), f"{behavior} / {phase_name}", fill="#111111", font=font); output.append(preview); durations.append(duration)
    out_path.parent.mkdir(parents=True, exist_ok=True); output[0].save(out_path, save_all=True, append_images=output[1:], duration=durations, loop=0, optimize=False)


def build_frame_audit(root: Path, manifest: dict, out_path: Path) -> None:
    columns, cell, label_height = 6, 160, 28; rows = []
    for behavior in review_behaviors(manifest):
        for phase_name, spec in behavior_phases(manifest, behavior):
            frames = read_spec_frames(root, manifest, spec)
            for start in range(0, len(frames), columns): rows.append((f"{behavior} / {phase_name}", start, frames[start:start + columns]))
    sheet = Image.new("RGB", (columns * cell, len(rows) * (cell + label_height)), "#394052"); draw = ImageDraw.Draw(sheet); font = load_font(16)
    for row, (label, start, frames) in enumerate(rows):
        for column, frame in enumerate(frames):
            preview = frame.copy(); preview.thumbnail((cell - 12, cell - 12), Image.Resampling.LANCZOS); x = column * cell + (cell - preview.width) // 2; y = row * (cell + label_height) + (cell - preview.height) // 2
            sheet.paste(preview, (x, y), preview); draw.text((column * cell + 8, row * (cell + label_height) + 6), f"#{start + column + 1}", fill="#FFFFFF", font=font)
        draw.text((8, row * (cell + label_height) + cell + 5), f"{label} · {start + 1}-{start + len(frames)}", fill="#FFFFFF", font=font)
    out_path.parent.mkdir(parents=True, exist_ok=True); sheet.save(out_path)


def write_deterministic_zip(root: Path, out_path: Path, pack_id: str) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix="desktop-pet-pack-", suffix=".zip", delete=False, dir=out_path.parent) as handle: temp_path = Path(handle.name)
    try:
        with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for source in sorted(path for path in root.rglob("*") if path.is_file() and not path.is_symlink()):
                relative = source.relative_to(root); info = zipfile.ZipInfo((Path(pack_id) / relative).as_posix(), date_time=(2024, 1, 1, 0, 0, 0)); info.compress_type = zipfile.ZIP_DEFLATED; info.external_attr = 0o100644 << 16; archive.writestr(info, source.read_bytes())
        validate_pack(temp_path); temp_path.replace(out_path); out_path.chmod(0o644)
    finally: temp_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("source", type=Path); parser.add_argument("--out", type=Path); parser.add_argument("--review-dir", type=Path); parser.add_argument("--review-only", action="store_true"); parser.add_argument("--delivery-dir", type=Path); parser.add_argument("--delivery-platform", choices=("macos", "windows", "all"), default=current_platform()); args = parser.parse_args()
    try:
        result = validate_pack_directory(args.source)
        if not args.out and not args.review_only: parser.error("--out is required unless --review-only is used")
        if args.review_only and not args.review_dir: parser.error("--review-dir is required with --review-only")
        review_dir = args.review_dir or args.out.with_suffix("").with_name(f"{args.out.stem}-review")
        build_contact_sheet(result.root, result.manifest, review_dir / "contact-sheet.png"); build_behavior_timelines(result.root, result.manifest, review_dir / "behavior-timelines.png"); build_motion_preview(result.root, result.manifest, review_dir / "motion-preview.gif"); build_frame_audit(result.root, result.manifest, review_dir / "frame-audit.png")
        delivery = None
        if not args.review_only:
            write_deterministic_zip(result.root, args.out, result.pack_id)
            if args.delivery_dir: delivery = build_delivery(args.out, args.delivery_dir, args.delivery_platform)
    except (OSError, PackValidationError, ValueError) as exc: raise SystemExit(f"BUILD FAILED: {exc}") from exc
    print(json.dumps({"pack": None if args.review_only else str(args.out.resolve()), "packId": result.pack_id, "review": str(review_dir.resolve()), "schemaVersion": result.manifest["schemaVersion"], "delivery": None if delivery is None else delivery["delivery"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__": main()
