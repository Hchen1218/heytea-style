from __future__ import annotations

import sys
import tempfile
import unittest
import plistlib
import json
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_desktop_pet_environment import detect_environment
from install_desktop_pet_runtime import (
    CapturedCommandError,
    InstallError,
    RuntimeBuildError,
    build_runtime,
    install,
    install_built_runtime,
    make_plan,
    parse_self_test_output,
)

RUNTIME_PACKAGE = json.loads((ROOT / "assets" / "desktop-pet-runtime" / "package.json").read_text(encoding="utf-8"))
RUNTIME_DEV_DEPENDENCIES = RUNTIME_PACKAGE["devDependencies"]
ELECTRON_VERSION = RUNTIME_DEV_DEPENDENCIES["electron"]
ELECTRON_BUILDER_VERSION = RUNTIME_DEV_DEPENDENCIES["electron-builder"]
ASAR_VERSION = RUNTIME_DEV_DEPENDENCIES["@electron/asar"]


def make_runtime(root: Path, *, dependencies: bool = False, windows: bool = False, version: str = "3.1.0") -> Path:
    (root / "src").mkdir(parents=True)
    metadata = {
        "version": version,
        "devDependencies": dict(RUNTIME_DEV_DEPENDENCIES),
    }
    (root / "package.json").write_text(json.dumps(metadata), encoding="utf-8")
    lockfile = {
        "lockfileVersion": 3,
        "packages": {
            "": {"devDependencies": metadata["devDependencies"]},
            "node_modules/electron": {"version": ELECTRON_VERSION},
            "node_modules/electron-builder": {"version": ELECTRON_BUILDER_VERSION},
            "node_modules/@electron/asar": {"version": ASAR_VERSION},
        },
    }
    (root / "package-lock.json").write_text(json.dumps(lockfile), encoding="utf-8")
    (root / "src" / "main.js").write_text("'use strict';\n", encoding="utf-8")
    if dependencies:
        (root / "node_modules" / "electron").mkdir(parents=True)
        (root / "node_modules" / "electron" / "package.json").write_text(
            json.dumps({"version": ELECTRON_VERSION}), encoding="utf-8"
        )
        (root / "node_modules" / "electron-builder").mkdir(parents=True)
        (root / "node_modules" / "electron-builder" / "package.json").write_text(
            json.dumps({"version": ELECTRON_BUILDER_VERSION}), encoding="utf-8"
        )
        (root / "node_modules" / "@electron" / "asar").mkdir(parents=True)
        (root / "node_modules" / "@electron" / "asar" / "package.json").write_text(
            json.dumps({"version": ASAR_VERSION}), encoding="utf-8"
        )
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

    @patch("check_desktop_pet_environment.command_version", return_value="v22.12.0")
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

    @patch("check_desktop_pet_environment.command_version", return_value="v22.12.0")
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

    @patch("check_desktop_pet_environment.command_version", return_value="v22.12.0")
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
            runtimeRoot="C:/runtime",
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

    @patch("check_desktop_pet_environment.command_version", return_value="v22.12.0")
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
            self.assertEqual(report.dependencyStatus, "ready")
            self.assertEqual(report.electronVersion, ELECTRON_VERSION)
            self.assertEqual(report.electronBuilderVersion, ELECTRON_BUILDER_VERSION)

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
            self.assertEqual(report.dependencyStatus, "missing")
            self.assertFalse(report.dependenciesInstalled)
            self.assertIn("node", report.missing)
            plan = make_plan(report)
            self.assertEqual(plan.installToolchain[0][:4], ["winget", "install", "--id", "OpenJS.NodeJS.LTS"])
            self.assertEqual(plan.buildRuntime, ["npm.cmd", "run", "pack:win"])

    def test_node_minimum_uses_full_semantic_version(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = make_runtime(Path(temp) / "runtime")
            available = {"node": "/bin/node", "npm": "/bin/npm"}
            with patch("check_desktop_pet_environment.command_version", return_value="v22.11.9"):
                old = detect_environment(platform_name="macos", runtime_root=root, home=Path(temp) / "home", which=available.get)
            with patch("check_desktop_pet_environment.command_version", return_value="v22.12.0"):
                minimum = detect_environment(platform_name="macos", runtime_root=root, home=Path(temp) / "home", which=available.get)
            self.assertFalse(old.nodeSupported)
            self.assertIn("node>=22.12.0", old.missing)
            self.assertTrue(minimum.nodeSupported)
            self.assertEqual(minimum.minimumNodeVersion, "22.12.0")

    @patch("check_desktop_pet_environment.command_version", return_value="v24.11.1")
    def test_dependency_drift_is_not_reported_as_installed(self, _version) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = make_runtime(Path(temp) / "runtime", dependencies=True)
            (root / "node_modules" / "electron-builder" / "package.json").write_text('{"version":"26.15.3"}', encoding="utf-8")
            report = detect_environment(
                platform_name="macos",
                runtime_root=root,
                home=Path(temp) / "home",
                which={"node": "/bin/node", "npm": "/bin/npm"}.get,
            )
            self.assertEqual(report.dependencyStatus, "drifted")
            self.assertFalse(report.dependenciesInstalled)
            self.assertEqual(report.electronBuilderVersion, "26.15.3")
            self.assertEqual(make_plan(report).installDependencies, ["npm", "ci"])

    def test_archive_build_failure_retries_exactly_once_with_unpacked_electron(self) -> None:
        report = SimpleNamespace(
            platform="macos", runtimeRoot="/runtime", nodeVersion="v24.11.1", npmAvailable=True,
            npmVersion="11.6.1",
            electronVersion=ELECTRON_VERSION, electronBuilderVersion=ELECTRON_BUILDER_VERSION,
        )
        failure = CapturedCommandError(["npm", "run", "pack:mac"], 1, "Invalid package during extractZipStreaming")
        with patch("install_desktop_pet_runtime.run_captured", side_effect=[failure, "", ""]) as runner:
            used = build_runtime(report, npm="npm", node="node", root=Path("/runtime"))
        self.assertTrue(used)
        self.assertEqual(runner.call_count, 3)
        self.assertIn("electron/install.js", runner.call_args_list[1].args[0][1])
        self.assertIn("--config.electronDist=/runtime/node_modules/electron/dist", runner.call_args_list[2].args[0])

    def test_failed_fallback_returns_structured_diagnostic_and_stops(self) -> None:
        report = SimpleNamespace(
            platform="macos", runtimeRoot="/runtime", nodeVersion="v24.11.1", npmAvailable=True,
            npmVersion="11.6.1",
            electronVersion=ELECTRON_VERSION, electronBuilderVersion=ELECTRON_BUILDER_VERSION,
        )
        first = CapturedCommandError(["npm"], 1, "unzipper premature close")
        second = CapturedCommandError(["npm"], 2, "fallback failed")
        with patch("install_desktop_pet_runtime.run_captured", side_effect=[first, "", second]) as runner:
            with self.assertRaises(RuntimeBuildError) as raised:
                build_runtime(report, npm="npm", node="node", root=Path("/runtime"))
        self.assertEqual(runner.call_count, 3)
        self.assertEqual(raised.exception.diagnostic["attempt"], "fallback")
        self.assertTrue(raised.exception.diagnostic["fallbackUsed"])
        self.assertEqual(raised.exception.diagnostic["exitCode"], 2)
        self.assertFalse(any("cache" in " ".join(call.args[0]).lower() for call in runner.call_args_list))

    def test_unrelated_build_failure_is_not_retried(self) -> None:
        report = SimpleNamespace(
            platform="macos", runtimeRoot="/runtime", nodeVersion="v24.11.1", npmAvailable=True,
            npmVersion="11.6.1", electronVersion=ELECTRON_VERSION, electronBuilderVersion=ELECTRON_BUILDER_VERSION,
        )
        failure = CapturedCommandError(["npm"], 1, "JavaScript syntax error")
        with patch("install_desktop_pet_runtime.run_captured", side_effect=failure) as runner:
            with self.assertRaises(RuntimeBuildError) as raised:
                build_runtime(report, npm="npm", node="node", root=Path("/runtime"))
        self.assertEqual(runner.call_count, 1)
        self.assertFalse(raised.exception.diagnostic["fallbackUsed"])
        self.assertEqual(raised.exception.diagnostic["attempt"], "standard")

    def test_validation_failure_happens_before_quit_or_install(self) -> None:
        report = SimpleNamespace(
            platform="macos", runtimeCompatible=False, runtimeInstalled=True, runtimeVersion="2.0.0",
            minimumRuntimeVersion="3.1.0", runtimePath="/Applications/Doodle Desktop Pet.app",
            runtimeScope="user", supported=True, sourceAvailable=True, sourceCompatible=True,
            sourceVersion="3.1.1", runtimeRoot="/runtime", nodeSupported=True, npmAvailable=True,
            dependenciesInstalled=True, dependencyStatus="ready", packageManager="brew",
            electronVersion=ELECTRON_VERSION, electronBuilderVersion=ELECTRON_BUILDER_VERSION, nodeVersion="v24.11.1",
            npmVersion="11.6.1",
            installDirectory="/Applications",
        )
        diagnostic = {"stage": "validate", "artifactChecks": {"selfTestPassed": False}}
        with (
            patch("install_desktop_pet_runtime.build_runtime", return_value=False),
            patch("install_desktop_pet_runtime.validate_built_runtime", side_effect=RuntimeBuildError(diagnostic)),
            patch("install_desktop_pet_runtime.request_runtime_quit") as quit_runtime,
            patch("install_desktop_pet_runtime.install_built_runtime") as copy_runtime,
        ):
            with self.assertRaises(RuntimeBuildError):
                install(report, allow_toolchain=False, allow_upgrade=True, launch=False, dry_run=False)
        quit_runtime.assert_not_called()
        copy_runtime.assert_not_called()

    def test_dependency_install_failure_returns_structured_diagnostic(self) -> None:
        report = SimpleNamespace(
            platform="macos", runtimeCompatible=False, runtimeInstalled=False, runtimeVersion=None,
            minimumRuntimeVersion="3.1.0", runtimePath=None, runtimeScope=None, supported=True,
            sourceAvailable=True, sourceCompatible=True, sourceVersion="3.1.1", runtimeRoot="/runtime",
            nodeSupported=True, npmAvailable=True, dependenciesInstalled=False, dependencyStatus="missing",
            packageManager="brew", electronVersion=None, electronBuilderVersion=None,
            nodeVersion="v24.11.1", npmVersion="11.6.1", installDirectory="/Applications",
        )
        failure = CapturedCommandError(["npm", "ci"], 7, "registry unavailable")
        with (
            patch("install_desktop_pet_runtime.shutil.which", side_effect=lambda name: f"/bin/{name}"),
            patch("install_desktop_pet_runtime.run_captured", side_effect=failure),
        ):
            with self.assertRaises(RuntimeBuildError) as raised:
                install(report, allow_toolchain=False, allow_upgrade=False, launch=False, dry_run=False)
        self.assertEqual(raised.exception.diagnostic["stage"], "dependencies")
        self.assertEqual(raised.exception.diagnostic["exitCode"], 7)
        self.assertIn("registry unavailable", raised.exception.diagnostic["stderrTail"])

    def test_self_test_parser_ignores_trailing_chromium_noise(self) -> None:
        stdout = (
            "gpu process started\n"
            'SELF_TEST_RESULT:{"ok":true,"product":"Doodle Desktop Pet","version":"3.1.1"}\n'
            "[1234:0904] Chromium leftover\n"
        )
        self.assertEqual(
            parse_self_test_output(stdout),
            {"ok": True, "product": "Doodle Desktop Pet", "version": "3.1.1"},
        )
        with self.assertRaises(InstallError):
            parse_self_test_output('{"ok":true}\n[gpu] leftover\n')

    def test_asar_validation_failure_is_not_retried(self) -> None:
        report = SimpleNamespace(
            platform="macos", runtimeRoot="/runtime", nodeVersion="v24.11.1", npmAvailable=True,
            npmVersion="11.6.1", electronVersion=ELECTRON_VERSION, electronBuilderVersion=ELECTRON_BUILDER_VERSION,
        )
        failure = CapturedCommandError(["npm"], 1, "RUNTIME_BUILD_VALIDATION_FAILED: application entry is missing")
        with patch("install_desktop_pet_runtime.run_captured", side_effect=failure) as runner:
            with self.assertRaises(RuntimeBuildError) as raised:
                build_runtime(report, npm="npm", node="node", root=Path("/runtime"))
        self.assertEqual(runner.call_count, 1)
        self.assertFalse(raised.exception.diagnostic["fallbackUsed"])
        self.assertEqual(raised.exception.diagnostic["attempt"], "standard")

    def test_dry_run_prints_quit_and_copy_without_validating(self) -> None:
        report = SimpleNamespace(
            platform="macos", runtimeCompatible=False, runtimeInstalled=True, runtimeVersion="2.0.0",
            minimumRuntimeVersion="3.1.0", runtimePath="/Applications/Doodle Desktop Pet.app",
            runtimeScope="user", supported=True, sourceAvailable=True, sourceCompatible=True,
            sourceVersion="3.1.1", runtimeRoot="/runtime", nodeSupported=True, npmAvailable=True,
            dependenciesInstalled=True, dependencyStatus="ready", packageManager="brew",
            electronVersion=ELECTRON_VERSION, electronBuilderVersion=ELECTRON_BUILDER_VERSION,
            nodeVersion="v24.11.1", npmVersion="11.6.1", installDirectory="/Applications",
        )
        with (
            patch("install_desktop_pet_runtime.shutil.which", side_effect=lambda name: f"/bin/{name}"),
            patch("install_desktop_pet_runtime.build_runtime", return_value=False) as build,
            patch("install_desktop_pet_runtime.validate_built_runtime") as validate,
            patch("install_desktop_pet_runtime.request_runtime_quit") as quit_runtime,
            patch(
                "install_desktop_pet_runtime.install_built_runtime",
                return_value=Path("/Applications/Doodle Desktop Pet.app"),
            ) as copy_runtime,
            patch("install_desktop_pet_runtime.launch_runtime") as launch,
        ):
            install(report, allow_toolchain=False, allow_upgrade=True, launch=True, dry_run=True)
        self.assertTrue(build.call_args.kwargs["dry_run"])
        validate.assert_not_called()
        quit_runtime.assert_called_once()
        self.assertTrue(quit_runtime.call_args.kwargs["dry_run"])
        copy_runtime.assert_called_once()
        self.assertTrue(copy_runtime.call_args.kwargs["dry_run"])
        launch.assert_called_once()
        self.assertTrue(launch.call_args.kwargs["dry_run"])

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
