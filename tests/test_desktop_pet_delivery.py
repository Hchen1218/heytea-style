from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from test_pet_pack import PetPackTest

from build_desktop_pet_pack import write_deterministic_zip
from build_desktop_pet_delivery import build_delivery

ROOT = Path(__file__).resolve().parents[1]


class DesktopPetDeliveryTest(unittest.TestCase):
    def make_zip(self, base: Path) -> Path:
        root = PetPackTest().make_pack(base)
        out = base / "tea-cup-source.zip"
        write_deterministic_zip(root, out, "tea-cup")
        return out

    def make_v3_zip(self, base: Path) -> Path:
        root = ROOT / "examples" / "desktop-pet" / "pink-green-flavor-monster-v3"
        out = base / "monster-source.zip"
        write_deterministic_zip(root, out, root.name)
        return out

    def test_macos_delivery_contains_executable_launchers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            result = build_delivery(self.make_zip(base), base / "delivery", "macos")
            delivery = Path(result["delivery"])
            start = delivery / "启动桌宠.command"
            stop = delivery / "关闭桌宠.command"
            self.assertTrue(start.is_file())
            self.assertTrue(stop.is_file())
            if os.name == "posix":
                self.assertTrue(start.stat().st_mode & 0o111)
                self.assertTrue(stop.stat().st_mode & 0o111)
            self.assertIn("--open-pet", start.read_text(encoding="utf-8"))
            self.assertIn('REQUIRED_VERSION="2.0.0"', start.read_text(encoding="utf-8"))
            self.assertIn("version_at_least", start.read_text(encoding="utf-8"))
            self.assertIn("--quit", stop.read_text(encoding="utf-8"))
            self.assertTrue((delivery / "tea-cup-v2.zip").is_file())
            self.assertTrue((delivery / "preview.png").is_file())
            notes = (delivery / "使用说明.txt").read_text(encoding="utf-8")
            self.assertIn("xattr -dr com.apple.quarantine", notes)
            self.assertIn("Gatekeeper", notes)

    def test_windows_delivery_uses_shared_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            result = build_delivery(self.make_zip(base), base / "delivery", "windows")
            start = Path(result["delivery"]) / "启动桌宠.cmd"
            content = start.read_text(encoding="utf-8")
            self.assertIn("%LOCALAPPDATA%", content)
            self.assertIn("--open-pet", content)
            self.assertNotIn("electron.exe", content.lower())
            self.assertIn("LSS 2", content)

    def test_v3_delivery_refuses_legacy_runner_before_launch(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            mac = Path(build_delivery(self.make_v3_zip(base), base / "mac", "macos")["delivery"]) / "启动桌宠.command"
            self.assertIn('REQUIRED_VERSION="3.1.0"', mac.read_text(encoding="utf-8"))
            windows = Path(build_delivery(self.make_v3_zip(base), base / "win", "windows")["delivery"]) / "启动桌宠.cmd"
            self.assertIn("LSS 3", windows.read_text(encoding="utf-8"))
            self.assertIn("3.1.0", windows.read_text(encoding="utf-8"))

    def test_refuses_to_overwrite_delivery_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            pack = self.make_zip(base)
            out = base / "delivery"
            build_delivery(pack, out, "macos")
            with self.assertRaises(FileExistsError):
                build_delivery(pack, out, "macos")


if __name__ == "__main__":
    unittest.main()
