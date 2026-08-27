from __future__ import annotations

import sys
import tempfile
import unittest
import plistlib
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_desktop_pet_environment import detect_environment
from install_desktop_pet_runtime import install_built_runtime, make_plan


def make_runtime(root: Path, *, dependencies: bool = False, windows: bool = False, version: str = "3.1.0") -> Path:
    (root / "src").mkdir(parents=True)
    (root / "package.json").write_text(f'{{"version":"{version}"}}', encoding="utf-8")
    (root / "src" / "main.js").write_text("'use strict';\n", encoding="utf-8")
    if dependencies:
        (root / "node_modules" / "electron").mkdir(parents=True)
        binary = ".cmd" if windows else ""
        bin_dir = root / "node_modules" / ".bin"
        bin_dir.mkdir(parents=True)
        (bin_dir / f"electron{binary}").touch()
        (bin_dir / f"electron-builder{binary}").touch()
    return root


def make_mac_app(path: Path, version: str) -> None:
    info = path / "Contents" / "Info.plist"
    info.parent.mkdir(parents=True)
    with info.open("wb") as handle:
        plistlib.dump({"CFBundleShortVersionString": version}, handle)


class DesktopPetEnvironmentTest(unittest.TestCase):
    def test_installed_macos_runtime_is_ready_without_node(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            home = base / "home"
            app = home / "Applications" / "Doodle Desktop Pet.app"
            make_mac_app(app, "3.1.0")
            runtime = make_runtime(base / "runtime")
            report = detect_environment(
                platform_name="macos",
                runtime_root=runtime,
                home=home,
                which=lambda _name: None,
            )
            self.assertEqual(report.status, "ready")
            self.assertTrue(report.runtimeInstalled)
            self.assertEqual(report.runtimeScope, "user")
            self.assertTrue(report.runtimeCompatible)
            self.assertEqual(report.runtimeVersion, "3.1.0")
            self.assertFalse(report.needsConfirmation)

    @patch("check_desktop_pet_environment.command_version", return_value="v22.11.0")
    def test_old_runtime_reports_upgradeable_instead_of_ready(self, _version) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); home = base / "home"; app = home / "Applications" / "Doodle Desktop Pet.app"
            make_mac_app(app, "2.0.0")
            runtime = make_runtime(base / "runtime", dependencies=True)
            available = {"node": "/bin/node", "npm": "/bin/npm"}
            report = detect_environment(platform_name="macos", runtime_root=runtime, home=home, which=available.get)
            self.assertEqual(report.status, "upgradeable")
            self.assertFalse(report.runtimeCompatible)
            self.assertTrue(report.needsConfirmation)
            self.assertEqual(report.nextAction, "ask-to-upgrade-runtime")
            plan = make_plan(report)
            self.assertTrue(plan.upgradeExisting)
            self.assertEqual(plan.installMode, "in-place-upgrade")
            self.assertTrue(plan.stopExisting)
            self.assertIsNotNone(plan.backupPath)
            self.assertEqual(plan.buildRuntime, ["npm", "run", "pack:mac"])

    @patch("check_desktop_pet_environment.command_version", return_value="v22.11.0")
    def test_system_macos_runtime_uses_user_side_by_side_plan(self, _version) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); home = base / "home"; system_app = base / "Applications" / "Doodle Desktop Pet.app"
            make_mac_app(system_app, "2.0.0")
            runtime = make_runtime(base / "runtime", dependencies=True)
            available = {"node": "/bin/node", "npm": "/bin/npm"}
            candidates = [home / "Applications" / "Doodle Desktop Pet.app", system_app]
            with patch("check_desktop_pet_environment.runtime_candidates", return_value=candidates):
                report = detect_environment(platform_name="macos", runtime_root=runtime, home=home, which=available.get)
            plan = make_plan(report)
            self.assertEqual(report.runtimeScope, "system")
            self.assertEqual(plan.installMode, "user-side-by-side")
            self.assertFalse(plan.upgradeExisting)
            self.assertTrue(plan.stopExisting)
            self.assertIsNone(plan.backupPath)
            self.assertEqual(plan.installDirectory, str(home / "Applications"))

    def test_v2_requirement_accepts_v2_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); home = base / "home"; app = home / "Applications" / "Doodle Desktop Pet.app"
            make_mac_app(app, "2.0.0")
            report = detect_environment(platform_name="macos", runtime_root=make_runtime(base / "runtime"), home=home, which=lambda _name: None, required_schema=2)
            self.assertEqual(report.status, "ready")
            self.assertTrue(report.runtimeCompatible)

    @patch("check_desktop_pet_environment.command_version", return_value="v22.11.0")
    def test_upgrade_rejects_a_source_that_cannot_build_required_schema(self, _version) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); home = base / "home"; app = home / "Applications" / "Doodle Desktop Pet.app"
            make_mac_app(app, "2.0.0")
            runtime = make_runtime(base / "runtime", dependencies=True, version="2.0.0")
            report = detect_environment(platform_name="macos", runtime_root=runtime, home=home, which={"node": "/bin/node", "npm": "/bin/npm"}.get)
            self.assertEqual(report.status, "upgrade-source-incompatible")
            self.assertFalse(report.sourceCompatible)
            self.assertIn("runtime-source>=3.1.0", report.missing)

    def test_upgrade_keeps_a_versioned_backup(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); runtime = base / "runtime"; install_dir = base / "Applications"
            built = runtime / "dist" / "mac-arm64" / "Doodle Desktop Pet.app"
            installed = install_dir / "Doodle Desktop Pet.app"
            make_mac_app(built, "3.0.0"); (built / "new.txt").write_text("v3", encoding="utf-8")
            make_mac_app(installed, "2.0.0"); (installed / "old.txt").write_text("v2", encoding="utf-8")
            report = SimpleNamespace(platform="macos", runtimeRoot=str(runtime), installDirectory=str(install_dir), runtimeVersion="2.0.0")
            result = install_built_runtime(report, upgrade=True)
            backup = install_dir / "Doodle Desktop Pet 2.0.0 Backup.app"
            self.assertEqual(result, installed)
            self.assertTrue((installed / "new.txt").is_file())
            self.assertTrue((backup / "old.txt").is_file())

    def test_repeated_refresh_never_overwrites_an_existing_backup(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); runtime = base / "runtime"; install_dir = base / "Applications"
            built = runtime / "dist" / "mac-arm64" / "Doodle Desktop Pet.app"
            installed = install_dir / "Doodle Desktop Pet.app"
            make_mac_app(built, "3.0.0"); (built / "new.txt").write_text("latest", encoding="utf-8")
            make_mac_app(installed, "3.0.0"); (installed / "old.txt").write_text("current", encoding="utf-8")
            existing = install_dir / "Doodle Desktop Pet 3.0.0 Backup.app"
            make_mac_app(existing, "3.0.0"); (existing / "kept.txt").write_text("keep", encoding="utf-8")
            report = SimpleNamespace(platform="macos", runtimeRoot=str(runtime), installDirectory=str(install_dir), runtimeVersion="3.0.0")
            install_built_runtime(report, upgrade=True)
            self.assertEqual((existing / "kept.txt").read_text(encoding="utf-8"), "keep")
            self.assertTrue((install_dir / "Doodle Desktop Pet 3.0.0 Backup 2.app" / "old.txt").is_file())

    def test_system_macos_runtime_stays_untouched_during_side_by_side_install(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); runtime = base / "runtime"; user_apps = base / "home" / "Applications"
            built = runtime / "dist" / "mac-arm64" / "Doodle Desktop Pet.app"
            system_app = base / "Applications" / "Doodle Desktop Pet.app"
            make_mac_app(built, "3.1.0"); (built / "new.txt").write_text("v3", encoding="utf-8")
            make_mac_app(system_app, "2.0.0"); (system_app / "old.txt").write_text("v2", encoding="utf-8")
            report = SimpleNamespace(platform="macos", runtimeRoot=str(runtime), installDirectory=str(user_apps), runtimeVersion="2.0.0")
            result = install_built_runtime(report, upgrade=False)
            self.assertEqual(result, user_apps / "Doodle Desktop Pet.app")
            self.assertTrue((result / "new.txt").is_file())
            self.assertEqual((system_app / "old.txt").read_text(encoding="utf-8"), "v2")
            self.assertFalse((system_app.parent / "Doodle Desktop Pet 2.0.0 Backup.app").exists())

    def test_windows_upgrade_plan_distinguishes_user_and_system_runtimes(self) -> None:
        common = dict(
            platform="windows", runtimeInstalled=True, runtimeCompatible=False,
            runtimeVersion="2.0.0", minimumRuntimeVersion="3.1.0",
            nodeSupported=True, npmAvailable=True, packageManager="winget",
            dependenciesInstalled=True, sourceCompatible=True,
            installDirectory="C:/Users/A/AppData/Local/Programs/Doodle Desktop Pet",
        )
        user = make_plan(SimpleNamespace(**common, runtimeScope="user", runtimePath="C:/Users/A/AppData/Local/Programs/Doodle Desktop Pet/Doodle Desktop Pet.exe"))
        system = make_plan(SimpleNamespace(**common, runtimeScope="system", runtimePath="C:/Program Files/Doodle Desktop Pet/Doodle Desktop Pet.exe"))
        self.assertEqual(user.installMode, "in-place-upgrade")
        self.assertTrue(user.upgradeExisting)
        self.assertIsNotNone(user.backupPath)
        self.assertEqual(system.installMode, "user-side-by-side")
        self.assertFalse(system.upgradeExisting)
        self.assertIsNone(system.backupPath)

    def test_windows_in_place_upgrade_numbers_existing_backup(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); runtime = base / "runtime"; install_dir = base / "Programs" / "Doodle Desktop Pet"
            built = runtime / "dist" / "win-unpacked"
            built.mkdir(parents=True); (built / "Doodle Desktop Pet.exe").write_text("v3", encoding="utf-8")
            install_dir.mkdir(parents=True); (install_dir / "Doodle Desktop Pet.exe").write_text("v2", encoding="utf-8")
            existing = install_dir.with_name("Doodle Desktop Pet 2.0.0 Backup")
            existing.mkdir(); (existing / "kept.txt").write_text("keep", encoding="utf-8")
            report = SimpleNamespace(platform="windows", runtimeRoot=str(runtime), installDirectory=str(install_dir), runtimeVersion="2.0.0")
            result = install_built_runtime(report, upgrade=True)
            self.assertEqual(result, install_dir / "Doodle Desktop Pet.exe")
            self.assertEqual(result.read_text(encoding="utf-8"), "v3")
            self.assertEqual((existing / "kept.txt").read_text(encoding="utf-8"), "keep")
            self.assertEqual((install_dir.with_name("Doodle Desktop Pet 2.0.0 Backup 2") / "Doodle Desktop Pet.exe").read_text(encoding="utf-8"), "v2")

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
            self.assertEqual(plan.installMode, "fresh-install")
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
