#!/usr/bin/env python3
"""Validate a desktop-pet pack directory or ZIP against schema v2."""

from __future__ import annotations

import argparse
import json
import re
import stat
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from PIL import Image, ImageChops


REQUIRED_ACTIONS = (
    "idle",
    "walk",
    "rest",
    "happy",
    "drag",
    "land",
    "wave",
    "signature",
    "curious",
    "stretch",
    "tiptoe",
    "play",
)
OPTIONAL_ACTIONS = ("fall", "touch")
ALLOWED_ACTIONS = REQUIRED_ACTIONS + OPTIONAL_ACTIONS
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")
MAX_ARCHIVE_BYTES = 80 * 1024 * 1024
MAX_FILE_BYTES = 24 * 1024 * 1024


@dataclass(frozen=True)
class ValidationResult:
    pack_id: str
    root: Path
    manifest: dict


class PackValidationError(ValueError):
    """Raised when a pack violates the public contract."""


def fail(message: str) -> None:
    raise PackValidationError(message)


def require_int(value: object, label: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        fail(f"{label} must be an integer")
    if value < minimum or value > maximum:
        fail(f"{label} must be between {minimum} and {maximum}")
    return value


def safe_relative_path(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        fail(f"{label} must be a non-empty relative path")
    normalized = value.replace("\\", "/")
    pure = PurePosixPath(normalized)
    if pure.is_absolute() or any(part in {"", ".", ".."} or ":" in part for part in pure.parts):
        fail(f"{label} is unsafe: {value}")
    return Path(*pure.parts)


def load_manifest(root: Path) -> dict:
    manifest_path = root / "pet.json"
    if not manifest_path.is_file():
        fail("missing pet.json")
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"pet.json is not valid UTF-8 JSON: {exc}")
    if not isinstance(data, dict):
        fail("pet.json root must be an object")
    return data


def validate_manifest(manifest: dict) -> tuple[int, int]:
    if manifest.get("schemaVersion") != 2:
        fail("schemaVersion must be exactly 2")

    pack_id = manifest.get("id")
    if not isinstance(pack_id, str) or not ID_PATTERN.fullmatch(pack_id):
        fail("id must use lowercase ASCII letters, digits, and single hyphens")
    if not isinstance(manifest.get("displayName"), str) or not manifest["displayName"].strip():
        fail("displayName must be a non-empty string")

    canvas = manifest.get("canvas")
    if not isinstance(canvas, dict):
        fail("canvas must be an object")
    width = require_int(canvas.get("width"), "canvas.width", 32, 1024)
    height = require_int(canvas.get("height"), "canvas.height", 32, 1024)

    anchor = manifest.get("anchor")
    if not isinstance(anchor, dict):
        fail("anchor must be an object")
    anchor_x = require_int(anchor.get("x"), "anchor.x", 0, width)
    anchor_y = require_int(anchor.get("y"), "anchor.y", 0, height)
    if anchor_x == width or anchor_y == height:
        fail("anchor must lie inside the canvas, not on its outer edge")

    scale = manifest.get("defaultScale")
    if isinstance(scale, bool) or not isinstance(scale, (int, float)) or not 0.5 <= scale <= 2:
        fail("defaultScale must be a number between 0.5 and 2")

    palette = manifest.get("palette")
    if not isinstance(palette, list) or not 1 <= len(palette) <= 3:
        fail("palette must contain one to three colors")
    if any(not isinstance(color, str) or not COLOR_PATTERN.fullmatch(color) for color in palette):
        fail("palette colors must use #RRGGBB")

    hitbox = manifest.get("hitbox")
    if not isinstance(hitbox, dict):
        fail("hitbox must be an object")
    require_int(hitbox.get("alphaThreshold"), "hitbox.alphaThreshold", 1, 254)
    bounds = hitbox.get("bounds")
    if not isinstance(bounds, dict):
        fail("hitbox.bounds must be an object")
    bx = require_int(bounds.get("x"), "hitbox.bounds.x", 0, width - 1)
    by = require_int(bounds.get("y"), "hitbox.bounds.y", 0, height - 1)
    bw = require_int(bounds.get("width"), "hitbox.bounds.width", 1, width)
    bh = require_int(bounds.get("height"), "hitbox.bounds.height", 1, height)
    if bx + bw > width or by + bh > height:
        fail("hitbox.bounds must stay inside the canvas")

    actions = manifest.get("actions")
    if not isinstance(actions, dict):
        fail("actions must be an object")
    missing = [name for name in REQUIRED_ACTIONS if name not in actions]
    if missing:
        fail(f"missing required actions: {', '.join(missing)}")
    extras = sorted(set(actions) - set(ALLOWED_ACTIONS))
    if extras:
        fail(f"schema v2 does not accept unknown actions: {', '.join(extras)}")

    for name in actions:
        action = actions[name]
        if not isinstance(action, dict):
            fail(f"actions.{name} must be an object")
        path = safe_relative_path(action.get("file"), f"actions.{name}.file")
        if path.suffix.lower() not in {".png", ".webp"}:
            fail(f"actions.{name}.file must be PNG or WebP")
        require_int(action.get("frames"), f"actions.{name}.frames", 1, 24)
        require_int(action.get("fps"), f"actions.{name}.fps", 1, 30)
        if not isinstance(action.get("loop"), bool):
            fail(f"actions.{name}.loop must be boolean")
        if not isinstance(action.get("mirrorable"), bool):
            fail(f"actions.{name}.mirrorable must be boolean")
    if actions["walk"].get("mirrorable") is not True:
        fail("actions.walk.mirrorable must be true")

    return width, height


def validate_strip(root: Path, action_name: str, action: dict, width: int, height: int, default_scale: float) -> None:
    relative = safe_relative_path(action["file"], f"actions.{action_name}.file")
    image_path = root / relative
    try:
        resolved = image_path.resolve(strict=True)
        resolved.relative_to(root.resolve(strict=True))
    except (OSError, ValueError):
        fail(f"actions.{action_name}.file escapes the pack or does not exist")
    if not resolved.is_file() or resolved.is_symlink():
        fail(f"actions.{action_name}.file must be a regular file")
    if resolved.stat().st_size > MAX_FILE_BYTES:
        fail(f"actions.{action_name}.file exceeds {MAX_FILE_BYTES // (1024 * 1024)} MB")

    try:
        with Image.open(resolved) as source:
            has_alpha = "A" in source.getbands() or "transparency" in source.info
            source.load()
            image = source.convert("RGBA")
    except (OSError, ValueError) as exc:
        fail(f"actions.{action_name}.file is not a readable image: {exc}")

    frames = action["frames"]
    expected = (width * frames, height)
    if image.size != expected:
        fail(f"actions.{action_name} has size {image.size}; expected {expected}")
    if not has_alpha:
        fail(f"actions.{action_name} has no alpha channel")

    alpha = image.getchannel("A")
    if alpha.getextrema() == (255, 255):
        fail(f"actions.{action_name} is fully opaque; runtime assets need transparency")
    corners = ((0, 0), (image.width - 1, 0), (0, image.height - 1), (image.width - 1, image.height - 1))
    if any(alpha.getpixel(point) != 0 for point in corners):
        fail(f"actions.{action_name} has non-transparent strip corners")

    boxes = []
    for index in range(frames):
        frame_alpha = alpha.crop((index * width, 0, (index + 1) * width, height))
        box = frame_alpha.getbbox()
        if box is None:
            fail(f"actions.{action_name} frame {index + 1} is empty")
        boxes.append(box)

    core_boxes = []
    for index in range(frames):
        frame_alpha = alpha.crop((index * width, 0, (index + 1) * width, height))
        core = frame_alpha.crop((width // 4, 0, width * 3 // 4, height)).getbbox()
        if core is None:
            fail(f"actions.{action_name} frame {index + 1} has no visible body core")
        core_boxes.append(core)
    stable_x = {"idle", "walk"}
    grounded = {"idle", "walk"}
    if action_name in stable_x:
        centers = [(box[0] + box[2]) / 2 for box in boxes]
        if max(centers) - min(centers) > 1:
            fail(f"actions.{action_name} body center drifts more than 1 px")
    if action_name in grounded:
        bottoms = [box[3] for box in boxes]
        if max(bottoms) - min(bottoms) > 1:
            fail(f"actions.{action_name} foot baseline drifts more than 1 px")
    if action_name == "idle":
        heights = [box[3] - box[1] for box in boxes]
        if max(heights) - min(heights) > max(1, round(sum(heights) / len(heights) * 0.015)):
            fail("actions.idle visible height changes more than 1.5%")
        if height >= 200:
            displayed_height = heights[0] * default_scale
            if not 120 <= displayed_height <= 140:
                fail(f"default desktop visible height is {displayed_height:.1f}px; expected 120-140px")
    if action.get("loop") and frames > 1:
        first = alpha.crop((0, 0, width, height))
        last = alpha.crop(((frames - 1) * width, 0, frames * width, height))
        changed = ImageChops.difference(first, last).point(lambda value: 255 if value > 24 else 0)
        changed_ratio = sum(changed.histogram()[1:]) / (width * height)
        if changed_ratio > 0.18:
            fail(f"actions.{action_name} loop seam changes too much ({changed_ratio:.1%})")


def validate_pack_directory(root: Path, *, require_root_name: bool = True) -> ValidationResult:
    root = root.resolve(strict=True)
    if not root.is_dir():
        fail(f"not a directory: {root}")
    manifest = load_manifest(root)
    width, height = validate_manifest(manifest)
    if require_root_name and root.name != manifest["id"]:
        fail(f"pack directory must be named {manifest['id']}")

    preview = root / "preview.png"
    if not preview.is_file() or preview.is_symlink():
        fail("missing regular preview.png")
    try:
        with Image.open(preview) as image:
            image.verify()
    except (OSError, ValueError) as exc:
        fail(f"preview.png is invalid: {exc}")

    for name in manifest["actions"]:
        validate_strip(root, name, manifest["actions"][name], width, height, float(manifest["defaultScale"]))
    return ValidationResult(manifest["id"], root, manifest)


def validate_archive_members(archive: zipfile.ZipFile) -> str:
    infos = archive.infolist()
    if not infos:
        fail("ZIP is empty")
    total = 0
    roots: set[str] = set()
    for info in infos:
        name = info.filename.replace("\\", "/")
        pure = PurePosixPath(name)
        if pure.is_absolute() or any(part in {"", ".", ".."} or ":" in part for part in pure.parts):
            fail(f"ZIP contains unsafe path: {info.filename}")
        roots.add(pure.parts[0])
        if info.flag_bits & 0x1:
            fail(f"ZIP contains encrypted entry: {info.filename}")
        mode = info.external_attr >> 16
        if stat.S_ISLNK(mode):
            fail(f"ZIP contains symlink: {info.filename}")
        if info.file_size > MAX_FILE_BYTES:
            fail(f"ZIP entry is too large: {info.filename}")
        total += info.file_size
        if total > MAX_ARCHIVE_BYTES:
            fail("ZIP expands beyond the 80 MB safety limit")
    if len(roots) != 1:
        fail("ZIP must contain exactly one top-level pet directory")
    return next(iter(roots))


def validate_pack(path: Path) -> ValidationResult:
    if path.is_dir():
        return validate_pack_directory(path)
    if path.suffix.lower() != ".zip" or not path.is_file():
        fail("input must be a pet directory or .zip file")
    try:
        with zipfile.ZipFile(path) as archive:
            root_name = validate_archive_members(archive)
            with tempfile.TemporaryDirectory(prefix="desktop-pet-validate-") as temp:
                archive.extractall(temp)
                result = validate_pack_directory(Path(temp) / root_name)
                return ValidationResult(result.pack_id, path.resolve(), result.manifest)
    except zipfile.BadZipFile as exc:
        fail(f"invalid ZIP: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", type=Path, help="Pet directory or ZIP to validate")
    args = parser.parse_args()
    try:
        result = validate_pack(args.pack)
    except (OSError, PackValidationError) as exc:
        raise SystemExit(f"INVALID: {exc}") from exc
    print(f"VALID: {result.pack_id} (schema v2)")


if __name__ == "__main__":
    main()
