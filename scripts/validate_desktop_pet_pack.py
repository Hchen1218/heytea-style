#!/usr/bin/env python3
"""Validate a schema-v2 or schema-v3 desktop-pet directory or ZIP."""

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

REQUIRED_ACTIONS = ("idle", "walk", "rest", "happy", "drag", "land", "wave", "signature", "curious", "stretch", "tiptoe", "play")
OPTIONAL_ACTIONS = ("fall", "touch")
ALLOWED_ACTIONS = REQUIRED_ACTIONS + OPTIONAL_ACTIONS
REQUIRED_BINDINGS = ("idle", "sleep", "click", "pointer", "drag", "release", "ambient")
COMPLETION_EVENTS = {"animation-finished", "motion-finished", "floor-impact", "pointer-released", "wake-requested", "timeout"}
MOTION_TYPES = {"walk", "fall", "cursor-approach", "cursor-return"}
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

    def __init__(self, message: str, *, path: str | None = None, frame: int | None = None, hint: str | None = None):
        self.message = message
        self.path = path
        self.frame = frame
        self.hint = hint if hint is not None else suggest_fix(message)
        parts = [message]
        if path:
            parts.append(f"file: {path}")
        if frame is not None:
            parts.append(f"frame: {frame}")
        if self.hint:
            parts.append(f"fix: {self.hint}")
        super().__init__("; ".join(parts))

    def to_dict(self) -> dict:
        return {
            "ok": False,
            "error": self.message,
            "path": self.path,
            "frame": self.frame,
            "hint": self.hint,
        }


def suggest_fix(message: str) -> str | None:
    rules = (
        ("non-transparent strip corners", "检查条带四角是否残留白底或棋盘格；运行资源必须真透明。"),
        ("fully opaque", "导出时去掉白底，保留 alpha 通道。"),
        ("no alpha channel", "另存为 PNG/WebP 并启用透明度。"),
        ("is empty", "该帧没有可见像素，重新导出这一帧。"),
        ("no visible body core", "主体偏离画布中心或被裁切，检查单元格边界。"),
        ("drifts more than 1 px", "固定脚锚点后重导出，idle/walk 不要左右或上下漂移。"),
        ("loop seam", "循环首尾帧应对齐同一姿势，或改为非 loop。"),
        ("changes more than 1.5%", "idle 高度抖动超过 1.5%，减小呼吸动画幅度。"),
        ("visible height", "调整 defaultScale 或角色高度，使默认桌面高度落在 120–140px。"),
        ("escapes the pack", "file 必须是包内相对路径，禁止 .. 与绝对路径。"),
        ("schemaVersion must be 2 or 3", "v1 包不能直接运行，请补画动作后升级为 v2。"),
        ("missing required actions", "补齐 12 个必选动作后再校验。"),
        ("must declare exactly one of fps or durationsMs", "每个 phase 只保留 fps 或 durationsMs 之一。"),
        ("ZIP must contain exactly one top-level", "压缩包必须只有一个与角色 id 同名的顶层目录。"),
        ("missing pet.json", "角色目录里需要 pet.json。"),
        ("missing regular preview.png", "补一张 preview.png 作为给人看的预览图。"),
    )
    for needle, hint in rules:
        if needle in message:
            return hint
    return "对照 references/desktop-pet-pack.md 修复后重新校验。"


def fail(message: str, *, path: str | None = None, frame: int | None = None, hint: str | None = None) -> None:
    raise PackValidationError(message, path=path, frame=frame, hint=hint)


def require_int(value: object, label: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        fail(f"{label} must be an integer")
    if value < minimum or value > maximum:
        fail(f"{label} must be between {minimum} and {maximum}")
    return value


def safe_relative_path(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        fail(f"{label} must be a non-empty relative path")
    pure = PurePosixPath(value.replace("\\", "/"))
    if pure.is_absolute() or any(part in {"", ".", ".."} or ":" in part for part in pure.parts):
        fail(f"{label} is unsafe: {value}")
    path = Path(*pure.parts)
    if path.suffix.lower() not in {".png", ".webp"}:
        fail(f"{label} must be PNG or WebP")
    return path


def load_manifest(root: Path) -> dict:
    try:
        data = json.loads((root / "pet.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail("missing pet.json")
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"pet.json is not valid UTF-8 JSON: {exc}")
    if not isinstance(data, dict):
        fail("pet.json root must be an object")
    return data


def validate_common(manifest: dict) -> tuple[int, int]:
    pack_id = manifest.get("id")
    if not isinstance(pack_id, str) or not ID_PATTERN.fullmatch(pack_id):
        fail("id must use lowercase ASCII letters, digits, and single hyphens")
    if not isinstance(manifest.get("displayName"), str) or not manifest["displayName"].strip():
        fail("displayName must be a non-empty string")
    canvas = manifest.get("canvas")
    if not isinstance(canvas, dict): fail("canvas must be an object")
    width = require_int(canvas.get("width"), "canvas.width", 32, 1024)
    height = require_int(canvas.get("height"), "canvas.height", 32, 1024)
    anchor = manifest.get("anchor")
    if not isinstance(anchor, dict): fail("anchor must be an object")
    require_int(anchor.get("x"), "anchor.x", 0, width - 1)
    require_int(anchor.get("y"), "anchor.y", 0, height - 1)
    scale = manifest.get("defaultScale")
    if isinstance(scale, bool) or not isinstance(scale, (int, float)) or not 0.5 <= scale <= 2: fail("defaultScale must be a number between 0.5 and 2")
    if "floorMode" in manifest and manifest["floorMode"] not in {"work-area", "display-edge"}: fail("floorMode must be work-area or display-edge")
    palette = manifest.get("palette")
    if not isinstance(palette, list) or not 1 <= len(palette) <= 3 or any(not isinstance(c, str) or not COLOR_PATTERN.fullmatch(c) for c in palette): fail("palette must contain one to three #RRGGBB colors")
    hitbox = manifest.get("hitbox")
    if not isinstance(hitbox, dict): fail("hitbox must be an object")
    require_int(hitbox.get("alphaThreshold"), "hitbox.alphaThreshold", 1, 254)
    bounds = hitbox.get("bounds")
    if not isinstance(bounds, dict): fail("hitbox.bounds must be an object")
    bx = require_int(bounds.get("x"), "hitbox.bounds.x", 0, width - 1)
    by = require_int(bounds.get("y"), "hitbox.bounds.y", 0, height - 1)
    bw = require_int(bounds.get("width"), "hitbox.bounds.width", 1, width)
    bh = require_int(bounds.get("height"), "hitbox.bounds.height", 1, height)
    if bx + bw > width or by + bh > height: fail("hitbox.bounds must stay inside the canvas")
    return width, height


def validate_v2(manifest: dict) -> None:
    actions = manifest.get("actions")
    if not isinstance(actions, dict): fail("actions must be an object")
    missing = [name for name in REQUIRED_ACTIONS if name not in actions]
    if missing: fail(f"missing required actions: {', '.join(missing)}")
    extras = sorted(set(actions) - set(ALLOWED_ACTIONS))
    if extras: fail(f"schema v2 does not accept unknown actions: {', '.join(extras)}")
    for name, action in actions.items():
        if not isinstance(action, dict): fail(f"actions.{name} must be an object")
        safe_relative_path(action.get("file"), f"actions.{name}.file")
        require_int(action.get("frames"), f"actions.{name}.frames", 1, 24)
        require_int(action.get("fps"), f"actions.{name}.fps", 1, 30)
        if not isinstance(action.get("loop"), bool) or not isinstance(action.get("mirrorable"), bool): fail(f"actions.{name} flags must be boolean")
    if actions["walk"].get("mirrorable") is not True: fail("actions.walk.mirrorable must be true")


def validate_phase(behavior: str, index: int, phase: object) -> None:
    label = f"behaviors.{behavior}.phases[{index}]"
    if not isinstance(phase, dict): fail(f"{label} must be an object")
    if not isinstance(phase.get("id"), str) or not ID_PATTERN.fullmatch(phase["id"]): fail(f"{label}.id is invalid")
    safe_relative_path(phase.get("file"), f"{label}.file")
    frames = require_int(phase.get("frames"), f"{label}.frames", 1, 24)
    has_fps, has_durations = "fps" in phase, "durationsMs" in phase
    if has_fps == has_durations: fail(f"{label} must declare exactly one of fps or durationsMs")
    if has_fps: require_int(phase["fps"], f"{label}.fps", 1, 30)
    if has_durations:
        values = phase["durationsMs"]
        if not isinstance(values, list) or len(values) != frames: fail(f"{label}.durationsMs must match frames")
        for duration in values: require_int(duration, f"{label}.durationsMs value", 34, 10000)
    if phase.get("playback") not in {"once", "loop"}: fail(f"{label}.playback must be once or loop")
    complete = phase.get("completeOn")
    if complete not in COMPLETION_EVENTS: fail(f"{label}.completeOn is unsupported")
    if not isinstance(phase.get("mirrorable"), bool): fail(f"{label}.mirrorable must be boolean")
    if "grounding" in phase and phase["grounding"] not in {"floor", "free"}: fail(f"{label}.grounding must be floor or free")
    if phase["playback"] == "loop" and complete == "animation-finished": fail(f"{label} loop must have an external exit event")
    motion = phase.get("motion")
    if motion is not None and motion not in MOTION_TYPES: fail(f"{label}.motion is unsupported")
    if complete == "timeout": require_int(phase.get("timeoutMs"), f"{label}.timeoutMs", 100, 24 * 60 * 60 * 1000)
    if complete == "motion-finished" and motion not in {"walk", "cursor-approach", "cursor-return"}: fail(f"{label} motion-finished requires horizontal motion")
    if complete == "floor-impact" and motion != "fall": fail(f"{label} floor-impact requires fall motion")


def validate_range(value: object, label: str, minimum: int = 1000, maximum: int = 24 * 60 * 60 * 1000) -> None:
    if not isinstance(value, list) or len(value) != 2:
        fail(f"{label} must have two values")
    low = require_int(value[0], f"{label}[0]", minimum, maximum)
    high = require_int(value[1], f"{label}[1]", minimum, maximum)
    if low > high: fail(f"{label} must be ascending")


def validate_cadence(cadence: object) -> None:
    if cadence is None: return
    if not isinstance(cadence, dict): fail("cadence must be an object")
    validate_range(cadence.get("idleIntervalMs"), "cadence.idleIntervalMs")
    validate_range(cadence.get("ambientIntervalMs"), "cadence.ambientIntervalMs")
    require_int(cadence.get("postEpisodeQuietMs"), "cadence.postEpisodeQuietMs", 0, 24 * 60 * 60 * 1000)
    require_int(cadence.get("pointerDwellMs"), "cadence.pointerDwellMs", 250, 60 * 1000)
    require_int(cadence.get("pointerCooldownMs"), "cadence.pointerCooldownMs", 0, 24 * 60 * 60 * 1000)
    require_int(cadence.get("dragThresholdPx"), "cadence.dragThresholdPx", 1, 64)
    if not isinstance(cadence.get("pointerResetsSleep"), bool): fail("cadence.pointerResetsSleep must be boolean")
    multipliers = cadence.get("profileMultipliers")
    if not isinstance(multipliers, dict): fail("cadence.profileMultipliers must be an object")
    for level in ("quiet", "balanced", "lively"):
        value = multipliers.get(level)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0.25 <= value <= 4:
            fail(f"cadence.profileMultipliers.{level} must be between 0.25 and 4")


def validate_v3(manifest: dict) -> None:
    if manifest.get("characterMode") != "flavor-monster": fail("schema v3 characterMode must be flavor-monster")
    validate_cadence(manifest.get("cadence"))
    behaviors = manifest.get("behaviors")
    if not isinstance(behaviors, dict) or not 6 <= len(behaviors) <= 10: fail("schema v3 requires 6-10 behaviors")
    for name, behavior in behaviors.items():
        if not ID_PATTERN.fullmatch(name) or not isinstance(behavior, dict): fail(f"invalid behavior: {name}")
        phases = behavior.get("phases")
        if not isinstance(phases, list) or not 1 <= len(phases) <= 12: fail(f"behaviors.{name}.phases must contain 1-12 phases")
        ids = [phase.get("id") if isinstance(phase, dict) else None for phase in phases]
        if len(ids) != len(set(ids)): fail(f"behaviors.{name} phase ids must be unique")
        for index, phase in enumerate(phases): validate_phase(name, index, phase)
    bindings = manifest.get("bindings")
    if not isinstance(bindings, dict) or any(name not in bindings for name in REQUIRED_BINDINGS): fail("all schema-v3 bindings are required")
    names = set(behaviors)
    direct = ("idle", "click", "pointer", "drag", "release")
    for name in direct:
        if bindings.get(name) not in names: fail(f"bindings.{name} must reference a behavior")
    sleep = bindings.get("sleep")
    if not isinstance(sleep, dict) or sleep.get("behavior") not in names: fail("bindings.sleep.behavior must reference a behavior")
    require_int(sleep.get("afterMs"), "bindings.sleep.afterMs", 1000, 24 * 60 * 60 * 1000)
    wake = sleep.get("wakeAfterMs")
    if not isinstance(wake, list) or len(wake) != 2: fail("bindings.sleep.wakeAfterMs must have two values")
    low = require_int(wake[0], "bindings.sleep.wakeAfterMs[0]", 1000, 24 * 60 * 60 * 1000)
    high = require_int(wake[1], "bindings.sleep.wakeAfterMs[1]", 1000, 24 * 60 * 60 * 1000)
    if low > high: fail("bindings.sleep.wakeAfterMs must be ascending")
    ambient = bindings.get("ambient")
    if not isinstance(ambient, list) or not ambient: fail("bindings.ambient must not be empty")
    for index, item in enumerate(ambient):
        if not isinstance(item, dict) or item.get("behavior") not in names: fail(f"bindings.ambient[{index}].behavior must reference a behavior")
        require_int(item.get("weight"), f"bindings.ambient[{index}].weight", 1, 100)
        require_int(item.get("cooldownMs"), f"bindings.ambient[{index}].cooldownMs", 0, 24 * 60 * 60 * 1000)
    reachable = {bindings[name] for name in direct} | {sleep["behavior"]} | {item["behavior"] for item in ambient}
    unbound = sorted(names - reachable)
    if unbound: fail(f"unbound behaviors: {', '.join(unbound)}")


def validate_manifest(manifest: dict) -> tuple[int, int]:
    width, height = validate_common(manifest)
    if manifest.get("schemaVersion") == 2: validate_v2(manifest)
    elif manifest.get("schemaVersion") == 3: validate_v3(manifest)
    else: fail("schemaVersion must be 2 or 3")
    return width, height


def iter_assets(manifest: dict):
    if manifest["schemaVersion"] == 2:
        for name, spec in manifest["actions"].items(): yield f"actions.{name}", spec, name
    else:
        for behavior, value in manifest["behaviors"].items():
            for phase in value["phases"]: yield f"behaviors.{behavior}.{phase['id']}", phase, None


def validate_strip(root: Path, label: str, spec: dict, width: int, height: int, default_scale: float, v2_action: str | None) -> None:
    relative = safe_relative_path(spec["file"], f"{label}.file")
    image_path = root / relative
    try:
        resolved = image_path.resolve(strict=True); resolved.relative_to(root.resolve(strict=True))
    except (OSError, ValueError): fail(f"{label}.file escapes the pack or does not exist", path=str(relative))
    if not resolved.is_file() or resolved.is_symlink(): fail(f"{label}.file must be a regular file", path=str(relative))
    if resolved.stat().st_size > MAX_FILE_BYTES: fail(f"{label}.file exceeds 24 MB", path=str(relative))
    try:
        with Image.open(resolved) as source:
            has_alpha = "A" in source.getbands() or "transparency" in source.info
            source.load(); image = source.convert("RGBA")
    except (OSError, ValueError) as exc: fail(f"{label}.file is not a readable image: {exc}", path=str(relative))
    frames = spec["frames"]
    if image.size != (width * frames, height): fail(f"{label} has size {image.size}; expected {(width * frames, height)}", path=str(relative), hint="条带宽度必须等于 canvas.width × frames，高度等于 canvas.height。")
    if not has_alpha: fail(f"{label} has no alpha channel", path=str(relative))
    alpha = image.getchannel("A")
    if alpha.getextrema() == (255, 255): fail(f"{label} is fully opaque; runtime assets need transparency", path=str(relative))
    corners = ((0, 0), (image.width - 1, 0), (0, image.height - 1), (image.width - 1, image.height - 1))
    if any(alpha.getpixel(point) != 0 for point in corners): fail(f"{label} has non-transparent strip corners", path=str(relative))
    boxes = []
    for index in range(frames):
        frame_alpha = alpha.crop((index * width, 0, (index + 1) * width, height)); box = frame_alpha.getbbox()
        if box is None: fail(f"{label} frame {index + 1} is empty", path=str(relative), frame=index + 1)
        if frame_alpha.crop((width // 4, 0, width * 3 // 4, height)).getbbox() is None: fail(f"{label} frame {index + 1} has no visible body core", path=str(relative), frame=index + 1)
        boxes.append(box)
    if v2_action in {"idle", "walk"}:
        centers = [(box[0] + box[2]) / 2 for box in boxes]; bottoms = [box[3] for box in boxes]
        if max(centers) - min(centers) > 1: fail(f"{label} body center drifts more than 1 px", path=str(relative))
        if max(bottoms) - min(bottoms) > 1: fail(f"{label} foot baseline drifts more than 1 px", path=str(relative))
    if v2_action == "idle":
        heights = [box[3] - box[1] for box in boxes]
        if max(heights) - min(heights) > max(1, round(sum(heights) / len(heights) * .015)): fail("actions.idle visible height changes more than 1.5%", path=str(relative))
        displayed = heights[0] * default_scale
        if height >= 200 and not 120 <= displayed <= 140: fail(f"default desktop visible height is {displayed:.1f}px; expected 120-140px", path=str(relative))
    is_loop = spec.get("loop") if v2_action else spec.get("playback") == "loop"
    if is_loop and frames > 1:
        first = alpha.crop((0, 0, width, height)); last = alpha.crop(((frames - 1) * width, 0, frames * width, height))
        changed = ImageChops.difference(first, last).point(lambda value: 255 if value > 24 else 0)
        changed_ratio = sum(changed.histogram()[1:]) / (width * height)
        limit = .18 if v2_action else .35
        if changed_ratio > limit: fail(f"{label} loop seam changes too much ({changed_ratio:.1%})", path=str(relative))


def validate_pack_directory(root: Path, *, require_root_name: bool = True) -> ValidationResult:
    root = root.resolve(strict=True)
    if not root.is_dir(): fail(f"not a directory: {root}")
    manifest = load_manifest(root); width, height = validate_manifest(manifest)
    if require_root_name and root.name != manifest["id"]: fail(f"pack directory must be named {manifest['id']}")
    preview = root / "preview.png"
    if not preview.is_file() or preview.is_symlink(): fail("missing regular preview.png")
    try:
        with Image.open(preview) as image: image.verify()
    except (OSError, ValueError) as exc: fail(f"preview.png is invalid: {exc}")
    for label, spec, action in iter_assets(manifest): validate_strip(root, label, spec, width, height, float(manifest["defaultScale"]), action)
    return ValidationResult(manifest["id"], root, manifest)


def validate_archive_members(archive: zipfile.ZipFile) -> str:
    infos = archive.infolist()
    if not infos: fail("ZIP is empty")
    total = 0; roots: set[str] = set()
    for info in infos:
        pure = PurePosixPath(info.filename.replace("\\", "/"))
        if pure.is_absolute() or any(part in {"", ".", ".."} or ":" in part for part in pure.parts): fail(f"ZIP contains unsafe path: {info.filename}")
        roots.add(pure.parts[0])
        if info.flag_bits & 1: fail(f"ZIP contains encrypted entry: {info.filename}")
        if stat.S_ISLNK(info.external_attr >> 16): fail(f"ZIP contains symlink: {info.filename}")
        if info.file_size > MAX_FILE_BYTES: fail(f"ZIP entry is too large: {info.filename}")
        total += info.file_size
        if total > MAX_ARCHIVE_BYTES: fail("ZIP expands beyond the 80 MB safety limit")
    if len(roots) != 1: fail("ZIP must contain exactly one top-level pet directory")
    return next(iter(roots))


def validate_pack(path: Path) -> ValidationResult:
    if path.is_dir(): return validate_pack_directory(path)
    if path.suffix.lower() != ".zip" or not path.is_file(): fail("input must be a pet directory or .zip file")
    try:
        with zipfile.ZipFile(path) as archive:
            root_name = validate_archive_members(archive)
            with tempfile.TemporaryDirectory(prefix="desktop-pet-validate-") as temp:
                archive.extractall(temp); result = validate_pack_directory(Path(temp) / root_name)
                return ValidationResult(result.pack_id, path.resolve(), result.manifest)
    except zipfile.BadZipFile as exc: fail(f"invalid ZIP: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", type=Path)
    parser.add_argument("--json", action="store_true", help="Print a machine-readable result")
    args = parser.parse_args()
    try:
        result = validate_pack(args.pack)
    except (OSError, PackValidationError) as exc:
        if args.json:
            payload = exc.to_dict() if isinstance(exc, PackValidationError) else {"ok": False, "error": str(exc), "path": None, "frame": None, "hint": None}
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"INVALID: {exc}")
        raise SystemExit(1) from exc
    payload = {
        "ok": True,
        "packId": result.pack_id,
        "schemaVersion": result.manifest["schemaVersion"],
        "root": str(result.root),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else f"VALID: {result.pack_id} (schema v{result.manifest['schemaVersion']})")


if __name__ == "__main__": main()
