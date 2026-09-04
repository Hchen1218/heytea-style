from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from desktop_pet import main
from install_desktop_pet_runtime import InstallPlan
from test_pet_pack import PetPackTest


class DesktopPetCliTest(unittest.TestCase):
    def test_pack_builds_zip_review_and_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = PetPackTest().make_pack(base)
            out = base / "tea-cup-v2.zip"
            review = base / "review"
            delivery = base / "delivery"
            code = main([
                "pack",
                str(source),
                "--out", str(out),
                "--review-dir", str(review),
                "--delivery-dir", str(delivery),
                "--delivery-platform", "macos",
            ])
            self.assertEqual(code, 0)
            self.assertTrue(out.is_file())
            self.assertTrue((review / "contact-sheet.png").is_file())
            self.assertTrue((review / "frame-audit.png").is_file())
            self.assertTrue((delivery / "启动桌宠.command").is_file())
            self.assertTrue((delivery / "tea-cup-v2.zip").is_file())

    def test_review_infers_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = PetPackTest().make_pack(Path(temp))
            with patch("desktop_pet.default_outputs", return_value={"review": Path(temp) / "inferred-review"}):
                code = main(["review", str(source)])
            self.assertEqual(code, 0)
            self.assertTrue((Path(temp) / "inferred-review" / "motion-preview.gif").is_file())

    def test_invalid_source_does_not_write_a_zip(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "empty"
            source.mkdir()
            out = Path(temp) / "broken.zip"
            code = main(["pack", str(source), "--out", str(out), "--delivery-dir", str(Path(temp) / "delivery")])
            self.assertEqual(code, 1)
            self.assertFalse(out.exists())

    def test_force_replaces_an_existing_delivery_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = PetPackTest().make_pack(base)
            out = base / "tea-cup-v2.zip"
            delivery = base / "delivery"
            args = [
                "pack", str(source), "--out", str(out),
                "--review-dir", str(base / "review"),
                "--delivery-dir", str(delivery),
                "--delivery-platform", "macos",
            ]
            self.assertEqual(main(args), 0)
            self.assertEqual(main(args + ["--force"]), 0)
            self.assertTrue((delivery / "启动桌宠.command").is_file())

    def test_doctor_registry_probe_is_opt_in(self) -> None:
        report = SimpleNamespace(supported=True)
        with (
            patch("desktop_pet.detect_environment", return_value=report) as detect,
            patch("desktop_pet.human_summary", return_value="ok"),
        ):
            self.assertEqual(main(["doctor"]), 0)
            self.assertFalse(detect.call_args.kwargs["probe_registry"])
            self.assertEqual(main(["doctor", "--probe-registry"]), 0)
            self.assertTrue(detect.call_args.kwargs["probe_registry"])

    def test_install_json_plan_forwards_upgrade(self) -> None:
        report = SimpleNamespace(platform="macos")
        plan = InstallPlan(
            platform="macos",
            installMode="in-place-upgrade",
            alreadyInstalled=True,
            installedVersion="3.1.0",
            minimumVersion="3.1.0",
            upgradeExisting=True,
            stopExisting=True,
            backupPath=None,
            installToolchain=[],
            installDependencies=None,
            buildRuntime=None,
            buildFallback=None,
            installDirectory="/Applications",
            launchAfterInstall=True,
            reuseCachedBuild=True,
            sourceHash="abc",
            useMirror=False,
        )
        with (
            patch("desktop_pet.detect_environment", return_value=report),
            patch("desktop_pet.make_plan", return_value=plan) as planner,
        ):
            buffer = io.StringIO()
            with patch("sys.stdout", buffer):
                code = main(["install", "--json-plan", "--upgrade"])
        self.assertEqual(code, 0)
        self.assertTrue(planner.call_args.kwargs["allow_upgrade"])
        self.assertIn("in-place-upgrade", buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
