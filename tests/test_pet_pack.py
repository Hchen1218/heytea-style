from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_desktop_pet_pack import build_contact_sheet, build_frame_audit, build_motion_preview, write_deterministic_zip
from validate_desktop_pet_pack import PackValidationError, REQUIRED_ACTIONS, suggest_fix, validate_pack


class PetPackTest(unittest.TestCase):
    def make_pack(self, parent: Path, pack_id: str = "tea-cup") -> Path:
        root = parent / pack_id
        animations = root / "animations"
        animations.mkdir(parents=True)
        width = height = 64
        actions = {}
        for index, name in enumerate(REQUIRED_ACTIONS):
            frames = 2 if name != "walk" else 3
            strip = Image.new("RGBA", (width * frames, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(strip)
            for frame in range(frames):
                left = frame * width + 18 + (0 if name in {"idle", "walk"} else frame)
                draw.ellipse((left, 15, left + 28, 48), fill=(220, 190 - index * 5, 70, 255), outline=(15, 15, 15, 255), width=2)
            path = animations / f"{name}.png"
            strip.save(path)
            actions[name] = {
                "file": f"animations/{name}.png",
                "frames": frames,
                "fps": 6,
                "loop": name in {"idle", "walk", "rest", "drag"},
                "mirrorable": name == "walk",
            }
        Image.new("RGB", (256, 256), "#F7F4EC").save(root / "preview.png")
        manifest = {
            "schemaVersion": 2,
            "id": pack_id,
            "displayName": "Tea Cup",
            "canvas": {"width": width, "height": height},
            "anchor": {"x": 32, "y": 52},
            "defaultScale": 0.6,
            "palette": ["#DDBE46", "#111111"],
            "hitbox": {
                "alphaThreshold": 24,
                "bounds": {"x": 8, "y": 8, "width": 48, "height": 48},
            },
            "actions": actions,
        }
        (root / "pet.json").write_text(json.dumps(manifest), encoding="utf-8")
        return root

    def test_valid_directory_and_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = self.make_pack(base)
            result = validate_pack(root)
            self.assertEqual(result.pack_id, "tea-cup")

            out = base / "tea-cup.zip"
            write_deterministic_zip(root, out, result.pack_id)
            archived = validate_pack(out)
            self.assertEqual(archived.pack_id, "tea-cup")

    def test_review_artifacts_are_created(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = self.make_pack(base)
            result = validate_pack(root)
            sheet = base / "review" / "contact-sheet.png"
            gif = base / "review" / "motion-preview.gif"
            audit = base / "review" / "frame-audit.png"
            build_contact_sheet(root, result.manifest, sheet)
            build_motion_preview(root, result.manifest, gif)
            build_frame_audit(root, result.manifest, audit)
            self.assertTrue(sheet.is_file())
            self.assertTrue(gif.is_file())
            self.assertTrue(audit.is_file())

    def test_frame_audit_wraps_and_keeps_every_frame_visible(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = self.make_pack(base)
            manifest_path = root / "pet.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for frame_count in (7, 24):
                with self.subTest(frame_count=frame_count):
                    strip = Image.new("RGBA", (64 * frame_count, 64), (0, 0, 0, 0))
                    draw = ImageDraw.Draw(strip)
                    for frame in range(frame_count):
                        left = frame * 64 + 18
                        draw.ellipse((left, 15, left + 28, 48), fill=(220, 180, 70, 255))
                    strip.save(root / manifest["actions"]["curious"]["file"])
                    manifest["actions"]["curious"]["frames"] = frame_count

                    audit = base / f"frame-audit-{frame_count}.png"
                    build_frame_audit(root, manifest, audit)
                    with Image.open(audit) as image:
                        expected_rows = 11 + (frame_count + 5) // 6
                        self.assertEqual(image.size, (960, expected_rows * 188))
                        last_row = 8 + (frame_count - 1) // 6
                        last_column = (frame_count - 1) % 6
                        cell = image.crop((
                            last_column * 160,
                            last_row * 188 + 20,
                            (last_column + 1) * 160,
                            last_row * 188 + 160,
                        ))
                        background = Image.new("RGB", cell.size, "#394052")
                        self.assertIsNotNone(ImageChops.difference(cell, background).getbbox())

    def test_rejects_opaque_strip(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self.make_pack(Path(temp))
            manifest = json.loads((root / "pet.json").read_text(encoding="utf-8"))
            idle = manifest["actions"]["idle"]
            Image.new("RGBA", (64 * idle["frames"], 64), (255, 255, 255, 255)).save(root / idle["file"])
            with self.assertRaises(PackValidationError) as raised:
                validate_pack(root)
            self.assertEqual(raised.exception.path, "animations/idle.png")
            self.assertIn("白底", raised.exception.hint or "")

    def test_empty_frame_includes_frame_number(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self.make_pack(Path(temp))
            manifest = json.loads((root / "pet.json").read_text(encoding="utf-8"))
            idle = manifest["actions"]["idle"]
            Image.new("RGBA", (64 * idle["frames"], 64), (0, 0, 0, 0)).save(root / idle["file"])
            with self.assertRaises(PackValidationError) as raised:
                validate_pack(root)
            self.assertEqual(raised.exception.frame, 1)
            self.assertEqual(raised.exception.path, "animations/idle.png")
            self.assertIn("可见像素", raised.exception.hint or "")

    def test_idle_height_jitter_hint_does_not_talk_about_default_scale(self) -> None:
        jitter = suggest_fix("actions.idle visible height changes more than 1.5%")
        scale = suggest_fix("default desktop visible height is 90.0px; expected 120-140px")
        self.assertIsNotNone(jitter)
        self.assertNotIn("defaultScale", jitter or "")
        self.assertIn("defaultScale", scale or "")

    def test_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self.make_pack(Path(temp))
            manifest_path = root / "pet.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["actions"]["idle"]["file"] = "../idle.png"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(PackValidationError):
                validate_pack(root)

    def test_rejects_legacy_v1_without_deleting_it(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self.make_pack(Path(temp))
            manifest_path = root / "pet.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["schemaVersion"] = 1
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(PackValidationError):
                validate_pack(root)
            self.assertTrue(manifest_path.is_file())

    def test_accepts_recognized_optional_runtime_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self.make_pack(Path(temp))
            manifest_path = root / "pet.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for name in ("fall", "touch"):
                frames = 2
                strip = Image.new("RGBA", (64 * frames, 64), (0, 0, 0, 0))
                draw = ImageDraw.Draw(strip)
                for frame in range(frames):
                    left = frame * 64 + 18 + frame
                    draw.ellipse((left, 15, left + 28, 48), fill=(220, 180, 70, 255))
                strip.save(root / "animations" / f"{name}.png")
                manifest["actions"][name] = {"file": f"animations/{name}.png", "frames": frames, "fps": 3, "loop": name == "fall", "mirrorable": name == "touch"}
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            self.assertEqual(validate_pack(root).pack_id, "tea-cup")


if __name__ == "__main__":
    unittest.main()
