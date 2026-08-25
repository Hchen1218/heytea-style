from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_desktop_pet_environment import detect_environment
from install_desktop_pet_runtime import make_plan


def make_runtime(root: Path, *, dependencies: bool = False, windows: bool = False) -> Path:
    (root / "src").mkdir(parents=True)
    (root / "package.json").write_text("{}", encoding="utf-8")
    (root / "src" / "main.js").write_text("'use strict';\n", encoding="utf-8")
    if dependencies:
        (root / "node_modules" / "electron").mkdir(parents=True)
        binary = ".cmd" if windows else ""
        bin_dir = root / "node_modules" / ".bin"
        bin_dir.mkdir(parents=True)
        (bin_dir / f"electron{binary}").touch()
        (bin_dir / f"electron-builder{binary}").touch()
    return root


class DesktopPetEnvironmentTest(unittest.TestCase):
    def test_installed_macos_runtime_is_ready_without_node(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            home = base / "home"
            app = home / "Applications" / "Doodle Desktop Pet.app"
            app.mkdir(parents=True)
            runtime = make_runtime(base / "runtime")
            report = detect_environment(
                platform_name="macos",
                runtime_root=runtime,
                home=home,
                which=lambda _name: None,
            )
            self.assertEqual(report.status, "ready")
            self.assertTrue(report.runtimeInstalled)
            self.assertFalse(report.needsConfirmation)

    @patch("check_desktop_pet_environment.command_version", return_value="v22.11.0")
    def test_macos_source_is_installable(self, _version) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            runtime = make_runtime(base / "runtime", dependencies=True)
            available = {"node": "/bin/node", "npm": "/bin/npm", "brew": "/opt/homebrew/bin/brew"}
            report = detect_environment(
                platform_name="macos",
                runtime_root=runtime,
                home=base / "home",
                which=available.get,
            )
            self.assertEqual(report.status, "installable")
            self.assertTrue(report.dependenciesInstalled)
            self.assertEqual(report.packageManager, "brew")
            plan = make_plan(report)
            self.assertIsNone(plan.installDependencies)
            self.assertEqual(plan.buildRuntime, ["npm", "run", "pack:mac"])

    @patch("check_desktop_pet_environment.command_version", return_value=None)
    def test_windows_missing_node_uses_winget_plan(self, _version) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            runtime = make_runtime(base / "runtime", windows=True)
            available = {"winget": "C:/Windows/winget.exe"}
            report = detect_environment(
                platform_name="windows",
                runtime_root=runtime,
                home=base / "home",
                environ={"LOCALAPPDATA": str(base / "LocalAppData")},
                which=available.get,
            )
            self.assertEqual(report.status, "needs-toolchain")
            self.assertEqual(report.packageManager, "winget")
            self.assertIn("node", report.missing)
            plan = make_plan(report)
            self.assertEqual(plan.installToolchain[0][:4], ["winget", "install", "--id", "OpenJS.NodeJS.LTS"])
            self.assertEqual(plan.buildRuntime, ["npm.cmd", "run", "pack:win"])

    def test_linux_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            runtime = make_runtime(Path(temp) / "runtime")
            report = detect_environment(
                platform_name="linux",
                runtime_root=runtime,
                home=Path(temp) / "home",
                which=lambda _name: None,
            )
            self.assertFalse(report.supported)
            self.assertEqual(report.status, "unsupported")
            self.assertEqual(report.nextAction, "stop")


if __name__ == "__main__":
    unittest.main()
