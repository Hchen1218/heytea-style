from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_desktop_pet_pack import build_behavior_timelines, build_contact_sheet
from validate_desktop_pet_pack import PackValidationError, validate_pack_directory


EXAMPLE = ROOT / "examples" / "desktop-pet" / "pink-green-flavor-monster-v3"


class PetPackV3Test(unittest.TestCase):
    def copy_pack(self, base: Path) -> Path:
        target = base / EXAMPLE.name
        shutil.copytree(EXAMPLE, target)
        return target

    def load(self, root: Path) -> dict:
        return json.loads((root / "pet.json").read_text(encoding="utf-8"))

    def save(self, root: Path, manifest: dict) -> None:
        (root / "pet.json").write_text(json.dumps(manifest), encoding="utf-8")

    def test_valid_eight_behavior_pack_and_reviews(self) -> None:
        result = validate_pack_directory(EXAMPLE)
        self.assertEqual(result.manifest["schemaVersion"], 3)
        with tempfile.TemporaryDirectory() as temp:
            timeline, overview = Path(temp) / "timeline.png", Path(temp) / "overview.png"
            build_behavior_timelines(result.root, result.manifest, timeline)
            build_contact_sheet(result.root, result.manifest, overview)
            self.assertTrue(timeline.is_file() and overview.is_file())

    def test_six_behavior_pack_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self.copy_pack(Path(temp)); manifest = self.load(root)
            del manifest["behaviors"]["explore-walk"]
            del manifest["behaviors"]["fruit-hiccup"]
            manifest["bindings"]["ambient"] = [{"behavior": "awake-story", "weight": 1, "cooldownMs": 25000}]
            self.save(root, manifest)
            validate_pack_directory(root)

    def test_cadence_policy_is_validated(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self.copy_pack(Path(temp)); manifest = self.load(root)
            manifest["cadence"]["idleIntervalMs"] = [36000, 24000]
            self.save(root, manifest)
            with self.assertRaisesRegex(PackValidationError, "cadence.idleIntervalMs"):
                validate_pack_directory(root)

    def test_grounding_policy_is_validated(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self.copy_pack(Path(temp)); manifest = self.load(root)
            manifest["behaviors"]["awake-story"]["phases"][0]["grounding"] = "floating"
            self.save(root, manifest)
            with self.assertRaisesRegex(PackValidationError, "grounding must be floor or free"):
                validate_pack_directory(root)

    def test_floor_mode_is_validated(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self.copy_pack(Path(temp)); manifest = self.load(root)
            manifest["floorMode"] = "floating"
            self.save(root, manifest)
            with self.assertRaisesRegex(PackValidationError, "floorMode must be work-area or display-edge"):
                validate_pack_directory(root)

    def test_missing_binding_dead_loop_and_illegal_event_fail(self) -> None:
        mutations = (
            lambda manifest: manifest["bindings"].pop("pointer"),
            lambda manifest: manifest["behaviors"]["held"]["phases"][1].update(completeOn="animation-finished"),
            lambda manifest: manifest["behaviors"]["awake-story"]["phases"][0].update(completeOn="banana"),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temp:
                root = self.copy_pack(Path(temp)); manifest = self.load(root); mutation(manifest); self.save(root, manifest)
                with self.assertRaises(PackValidationError): validate_pack_directory(root)

    def test_path_escape_and_opaque_phase_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self.copy_pack(Path(temp)); manifest = self.load(root)
            manifest["behaviors"]["awake-story"]["phases"][0]["file"] = "../escape.webp"; self.save(root, manifest)
            with self.assertRaisesRegex(PackValidationError, "unsafe"): validate_pack_directory(root)
        with tempfile.TemporaryDirectory() as temp:
            root = self.copy_pack(Path(temp)); manifest = self.load(root); phase = manifest["behaviors"]["awake-story"]["phases"][0]
            Image.new("RGBA", (384 * phase["frames"], 384), (255, 255, 255, 255)).save(root / phase["file"])
            with self.assertRaisesRegex(PackValidationError, "no alpha channel|fully opaque"): validate_pack_directory(root)


if __name__ == "__main__": unittest.main()
