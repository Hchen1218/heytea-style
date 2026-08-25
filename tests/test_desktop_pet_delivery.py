from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from test_pet_pack import PetPackTest

from build_desktop_pet_pack import write_deterministic_zip
from build_desktop_pet_delivery import build_delivery


class DesktopPetDeliveryTest(unittest.TestCase):
    def make_zip(self, base: Path) -> Path:
        root = PetPackTest().make_pack(base)
        out = base / "tea-cup-source.zip"
        write_deterministic_zip(root, out, "tea-cup")
        return out

    def test_macos_delivery_contains_executable_launchers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            result = build_delivery(self.make_zip(base), base / "delivery", "macos")
            delivery = Path(result["delivery"])
            start = delivery / "启动桌宠.command"
            stop = delivery / "关闭桌宠.command"
            self.assertTrue(start.stat().st_mode & 0o111)
            self.assertIn("--open-pet", start.read_text(encoding="utf-8"))
            self.assertIn("--quit", stop.read_text(encoding="utf-8"))
            self.assertTrue((delivery / "tea-cup-v2.zip").is_file())
            self.assertTrue((delivery / "preview.png").is_file())

    def test_windows_delivery_uses_shared_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            result = build_delivery(self.make_zip(base), base / "delivery", "windows")
            start = Path(result["delivery"]) / "启动桌宠.cmd"
            content = start.read_text(encoding="utf-8")
            self.assertIn("%LOCALAPPDATA%", content)
            self.assertIn("--open-pet", content)
            self.assertNotIn("electron.exe", content.lower())

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
