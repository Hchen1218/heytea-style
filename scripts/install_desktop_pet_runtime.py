#!/usr/bin/env python3
"""Install the bundled desktop-pet runner after explicit user confirmation."""

from __future__ import annotations

import argparse
import json
import os
import plistlib
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from check_desktop_pet_environment import (
    MIN_NODE_VERSION,
    PRODUCT_NAME,
    EnvironmentReport,
    detect_environment,
    normalize_platform,
)


class InstallError(RuntimeError):
    pass


class CapturedCommandError(RuntimeError):
    def __init__(self, command: list[str], returncode: int, output: str):
        super().__init__(f"command exited {returncode}: {' '.join(command)}")
        self.command = command
        self.returncode = returncode
        self.output = output


class RuntimeBuildError(InstallError):
    def __init__(self, diagnostic: dict):
        super().__init__(json.dumps(diagnostic, ensure_ascii=False))
        self.diagnostic = diagnostic


SELF_TEST_PREFIX = "SELF_TEST_RESULT:"


@dataclass(frozen=True)
class InstallPlan:
    platform: str
    installMode: str
    alreadyInstalled: bool
    installedVersion: str | None
    minimumVersion: str
    upgradeExisting: bool
    stopExisting: bool
    backupPath: str | None
    installToolchain: list[list[str]]
    installDependencies: list[str] | None
    buildRuntime: list[str] | None
    buildFallback: list[list[str]] | None
    installDirectory: str | None
    launchAfterInstall: bool


def toolchain_commands(report: EnvironmentReport) -> list[list[str]]:
    if report.nodeSupported and report.npmAvailable:
        return []
    if report.platform == "macos" and report.packageManager == "brew":
        return [["brew", "install", "node"]]
    if report.platform == "windows" and report.packageManager == "winget":
        return [[
            "winget",
            "install",
            "--id",
            "OpenJS.NodeJS.LTS",
            "--exact",
            "--accept-package-agreements",
            "--accept-source-agreements",
        ]]
    return []


def make_plan(report: EnvironmentReport, *, launch: bool = True) -> InstallPlan:
    npm = "npm.cmd" if report.platform == "windows" else "npm"
    build_script = "pack:win" if report.platform == "windows" else "pack:mac"
    root = Path(report.runtimeRoot)
    replacement_needed = report.runtimeInstalled and not report.runtimeCompatible
    upgrade = replacement_needed and report.runtimeScope == "user"
    side_by_side = replacement_needed and report.runtimeScope == "system"
    if report.runtimeCompatible:
        install_mode = "launch-existing"
    elif upgrade:
        install_mode = "in-place-upgrade"
    elif side_by_side:
        install_mode = "user-side-by-side"
    elif not report.runtimeInstalled:
        install_mode = "fresh-install"
    else:
        install_mode = "unavailable"
    backup = None
    if upgrade and report.runtimePath:
        installed = Path(report.runtimePath)
        if report.platform == "macos":
            backup = str(installed.with_name(f"{PRODUCT_NAME} {report.runtimeVersion or 'Unknown'} Backup.app"))
        else:
            backup = str(installed.parent.with_name(f"{PRODUCT_NAME} {report.runtimeVersion or 'Unknown'} Backup"))
    return InstallPlan(
        platform=report.platform,
        installMode=install_mode,
        alreadyInstalled=report.runtimeInstalled,
        installedVersion=report.runtimeVersion,
        minimumVersion=report.minimumRuntimeVersion,
        upgradeExisting=upgrade,
        stopExisting=replacement_needed,
        backupPath=backup,
        installToolchain=toolchain_commands(report),
        installDependencies=None if report.dependenciesInstalled or not report.sourceCompatible else [npm, "ci"],
        buildRuntime=None if report.runtimeCompatible or not report.sourceCompatible else [npm, "run", build_script],
        buildFallback=None if report.runtimeCompatible or not report.sourceCompatible else [
            ["node", str(root / "node_modules" / "electron" / "install.js")],
            [npm, "run", build_script, "--", f"--config.electronDist={root / 'node_modules' / 'electron' / 'dist'}"],
        ],
        installDirectory=report.installDirectory,
        launchAfterInstall=launch,
    )


def run(command: list[str], *, cwd: Path | None = None, dry_run: bool = False) -> None:
    print("+", " ".join(command))
    if not dry_run:
        subprocess.run(command, cwd=cwd, check=True)


def run_captured(command: list[str], *, cwd: Path, dry_run: bool = False) -> str:
    print("+", " ".join(command))
    if dry_run:
        return ""
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    output = "\n".join(part.strip() for part in (completed.stdout, completed.stderr) if part.strip())
    if output:
        print(output)
    if completed.returncode != 0:
        raise CapturedCommandError(command, completed.returncode, output)
    return output


def is_archive_build_failure(output: str) -> bool:
    lowered = output.lower()
    signatures = (
        "invalid package",
        "extractzipstreaming",
        "unzipper",
        "err_stream",
        "premature close",
        "archive extraction",
    )
    return any(signature in lowered for signature in signatures)


def parse_self_test_output(stdout: str) -> dict:
    for line in reversed([part.strip() for part in (stdout or "").splitlines() if part.strip()]):
        if line.startswith(SELF_TEST_PREFIX):
            return json.loads(line[len(SELF_TEST_PREFIX):] or "{}")
    raise InstallError(f"packaged runtime self-test response was not found: {stdout}")


def build_diagnostic(
    report: EnvironmentReport,
    *,
    stage: str,
    attempt: str,
    fallback_used: bool,
    error: CapturedCommandError | Exception,
    artifact_checks: dict | None = None,
) -> dict:
    output = error.output if isinstance(error, CapturedCommandError) else str(error)
    return {
        "stage": stage,
        "attempt": attempt,
        "versions": {
            "node": report.nodeVersion,
            "npm": report.npmVersion,
            "electron": report.electronVersion,
            "electronBuilder": report.electronBuilderVersion,
        },
        "exitCode": error.returncode if isinstance(error, CapturedCommandError) else None,
        "stderrTail": output[-4000:],
        "fallbackUsed": fallback_used,
        "artifactChecks": artifact_checks or {
            "bundleFound": False,
            "appAsarPresent": False,
            "defaultAppAbsent": False,
            "selfTestPassed": False,
        },
    }


def build_runtime(
    report: EnvironmentReport,
    *,
    npm: str,
    node: str,
    root: Path,
    dry_run: bool = False,
) -> bool:
    build_script = "pack:win" if report.platform == "windows" else "pack:mac"
    try:
        run_captured([npm, "run", build_script], cwd=root, dry_run=dry_run)
        return False
    except CapturedCommandError as first_error:
        if not is_archive_build_failure(first_error.output):
            raise RuntimeBuildError(build_diagnostic(
                report, stage="build", attempt="standard", fallback_used=False, error=first_error,
            )) from first_error

        electron_installer = root / "node_modules" / "electron" / "install.js"
        electron_dist = root / "node_modules" / "electron" / "dist"
        try:
            run_captured([node, str(electron_installer)], cwd=root, dry_run=dry_run)
            run_captured(
                [npm, "run", build_script, "--", f"--config.electronDist={electron_dist}"],
                cwd=root,
                dry_run=dry_run,
            )
            return True
        except CapturedCommandError as fallback_error:
            raise RuntimeBuildError(build_diagnostic(
                report, stage="build", attempt="fallback", fallback_used=True, error=fallback_error,
            )) from fallback_error


def find_mac_app(dist: Path) -> Path:
    matches = sorted(dist.glob(f"mac*/{PRODUCT_NAME}.app"))
    if not matches:
        raise InstallError(f"macOS build did not produce {PRODUCT_NAME}.app")
    return matches[0]


def find_windows_directory(dist: Path) -> Path:
    candidates = [dist / "win-unpacked", dist / "win-ia32-unpacked", dist / "win-arm64-unpacked"]
    for candidate in candidates:
        if (candidate / f"{PRODUCT_NAME}.exe").is_file():
            return candidate
    raise InstallError("Windows build did not produce a runnable unpacked directory")


def validate_built_runtime(report: EnvironmentReport, *, fallback_used: bool = False) -> dict:
    root = Path(report.runtimeRoot)
    checks = {
        "bundleFound": False,
        "appAsarPresent": False,
        "defaultAppAbsent": False,
        "selfTestPassed": False,
    }
    try:
        if report.platform == "macos":
            application = find_mac_app(root / "dist")
            resources = application / "Contents" / "Resources"
            with (application / "Contents" / "Info.plist").open("rb") as handle:
                executable_name = plistlib.load(handle).get("CFBundleExecutable")
            if not executable_name:
                raise InstallError("packaged macOS application has no CFBundleExecutable")
            executable = application / "Contents" / "MacOS" / str(executable_name)
        else:
            application = find_windows_directory(root / "dist")
            resources = application / "resources"
            executable = application / f"{PRODUCT_NAME}.exe"
        checks["bundleFound"] = executable.is_file()
        if not checks["bundleFound"]:
            raise InstallError(f"packaged runtime executable is missing: {executable}")
        app_asar = resources / "app.asar"
        checks["appAsarPresent"] = app_asar.is_file() and app_asar.stat().st_size > 0
        checks["defaultAppAbsent"] = not (resources / "default_app.asar").exists()
        if not checks["appAsarPresent"]:
            raise InstallError(f"validated app.asar is missing: {app_asar}")
        if not checks["defaultAppAbsent"]:
            raise InstallError(f"default_app.asar remained in the packaged runtime: {resources}")

        completed = subprocess.run(
            [str(executable), "--self-test"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if completed.returncode != 0:
            raise InstallError(f"packaged runtime self-test exited {completed.returncode}: {(completed.stderr or completed.stdout).strip()}")
        payload = parse_self_test_output(completed.stdout)
        if payload.get("ok") is not True or payload.get("product") != PRODUCT_NAME:
            raise InstallError(f"packaged runtime returned an invalid self-test response: {payload}")
        if report.sourceVersion and payload.get("version") != report.sourceVersion:
            raise InstallError(f"packaged runtime version {payload.get('version')} does not match source {report.sourceVersion}")
        checks["selfTestPassed"] = True
        return checks
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError, plistlib.InvalidFileException, InstallError) as error:
        raise RuntimeBuildError(build_diagnostic(
            report,
            stage="validate",
            attempt="post-build",
            fallback_used=fallback_used,
            error=error,
            artifact_checks=checks,
        )) from error


def available_backup_path(preferred: Path, *, suffix: str | None = None) -> Path:
    if not preferred.exists():
        return preferred
    effective_suffix = preferred.suffix if suffix is None else suffix
    stem = preferred.name[: -len(effective_suffix)] if effective_suffix else preferred.name
    for index in range(2, 1000):
        candidate = preferred.with_name(f"{stem} {index}{effective_suffix}")
        if not candidate.exists():
            return candidate
    raise InstallError(f"could not allocate a backup path beside: {preferred}")


def install_built_runtime(report: EnvironmentReport, *, upgrade: bool = False, dry_run: bool = False) -> Path:
    root = Path(report.runtimeRoot)
    dist = root / "dist"
    destination_root = Path(report.installDirectory or "")
    if report.platform == "macos":
        source = find_mac_app(dist)
        destination = destination_root / source.name
        backup = None
        if destination.exists():
            if not upgrade:
                raise InstallError(f"refusing to replace existing application: {destination}")
            backup = available_backup_path(destination.with_name(f"{PRODUCT_NAME} {report.runtimeVersion or 'Unknown'} Backup.app"))
            print(f"+ backup {destination} -> {backup}")
        print(f"+ copy {source} -> {destination}")
        if not dry_run:
            destination_root.mkdir(parents=True, exist_ok=True)
            if backup:
                destination.rename(backup)
                try:
                    shutil.copytree(source, destination, symlinks=True)
                except BaseException:
                    if destination.exists():
                        shutil.rmtree(destination)
                    if backup.exists():
                        backup.rename(destination)
                    raise
            else:
                shutil.copytree(source, destination, symlinks=True)
        return destination

    source = find_windows_directory(dist)
    destination = destination_root
    backup = None
    if destination.exists():
        if not upgrade:
            raise InstallError(f"refusing to replace existing application: {destination}")
        backup = available_backup_path(
            destination.with_name(f"{PRODUCT_NAME} {report.runtimeVersion or 'Unknown'} Backup"),
            suffix="",
        )
        print(f"+ backup {destination} -> {backup}")
    print(f"+ copy {source} -> {destination}")
    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if backup:
            destination.rename(backup)
            try:
                shutil.copytree(source, destination)
            except BaseException:
                if destination.exists():
                    shutil.rmtree(destination)
                if backup.exists():
                    backup.rename(destination)
                raise
        else:
            shutil.copytree(source, destination)
    return destination / f"{PRODUCT_NAME}.exe"


def launch_runtime(platform_name: str, application: Path, *, dry_run: bool = False) -> None:
    command = ["open", str(application)] if platform_name == "macos" else [str(application)]
    print("+", " ".join(command))
    if dry_run:
        return
    if platform_name == "macos":
        subprocess.run(command, check=True)
    else:
        subprocess.Popen(command, close_fds=True)


def request_runtime_quit(platform_name: str, application: Path, *, dry_run: bool = False) -> None:
    command = ["open", "-n", str(application), "--args", "--quit"] if platform_name == "macos" else [str(application), "--quit"]
    print("+", " ".join(command))
    if dry_run:
        return
    subprocess.run(command, check=True, timeout=15)
    time.sleep(2)


def install(
    report: EnvironmentReport,
    *,
    allow_toolchain: bool,
    allow_upgrade: bool,
    launch: bool,
    dry_run: bool,
) -> Path | None:
    if report.runtimeCompatible and not allow_upgrade:
        application = Path(report.runtimePath or "")
        if launch:
            launch_runtime(report.platform, application, dry_run=dry_run)
        return application
    if report.runtimeInstalled and not allow_upgrade:
        raise InstallError(
            f"installed runtime {report.runtimeVersion or 'unknown'} is older than required {report.minimumRuntimeVersion}; rerun with --upgrade after confirmation"
        )
    if not report.supported:
        raise InstallError(f"unsupported platform: {report.platform}")
    if not report.sourceAvailable:
        raise InstallError("bundled runtime source is missing")
    if not report.sourceCompatible:
        raise InstallError(f"bundled runtime source {report.sourceVersion or 'unknown'} is older than required {report.minimumRuntimeVersion}")

    commands = toolchain_commands(report)
    if not report.nodeSupported or not report.npmAvailable:
        if not allow_toolchain:
            raise InstallError(
                f"Node.js {MIN_NODE_VERSION}+ and npm are required; rerun with --install-toolchain after confirmation"
            )
        if not commands:
            manager = "Homebrew" if report.platform == "macos" else "winget"
            raise InstallError(f"cannot install Node.js automatically because {manager} is unavailable")
        for command in commands:
            run(command, dry_run=dry_run)
        if dry_run:
            return None
        report = detect_environment(platform_name=report.platform, runtime_root=Path(report.runtimeRoot))
        if not report.nodeSupported or not report.npmAvailable:
            raise InstallError("Node.js installation finished but the current process cannot find node/npm; reopen the terminal and retry")

    root = Path(report.runtimeRoot)
    npm = shutil.which("npm.cmd" if report.platform == "windows" else "npm")
    node = shutil.which("node")
    if not npm:
        raise InstallError("npm is unavailable")
    if not node:
        raise InstallError("node is unavailable")
    if not report.dependenciesInstalled:
        try:
            run_captured([npm, "ci"], cwd=root, dry_run=dry_run)
        except CapturedCommandError as error:
            raise RuntimeBuildError(build_diagnostic(
                report, stage="dependencies", attempt="npm-ci", fallback_used=False, error=error,
            )) from error
        if not dry_run:
            report = detect_environment(platform_name=report.platform, runtime_root=root)
            if not report.dependenciesInstalled:
                error = InstallError(f"npm ci completed but runtime dependencies are {report.dependencyStatus}")
                raise RuntimeBuildError(build_diagnostic(
                    report, stage="dependencies", attempt="post-install-check", fallback_used=False, error=error,
                )) from error
    fallback_used = build_runtime(report, npm=npm, node=node, root=root, dry_run=dry_run)
    if not dry_run:
        validate_built_runtime(report, fallback_used=fallback_used)
    if report.runtimeInstalled:
        request_runtime_quit(report.platform, Path(report.runtimePath or ""), dry_run=dry_run)
    application = install_built_runtime(
        report,
        upgrade=report.runtimeInstalled and report.runtimeScope == "user",
        dry_run=dry_run,
    )
    if launch:
        launch_runtime(report.platform, application, dry_run=dry_run)
    return application


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--yes", action="store_true", help="Confirm installation was explicitly approved by the user")
    parser.add_argument("--install-toolchain", action="store_true", help="Allow installing Node.js through brew or winget")
    parser.add_argument("--upgrade", action="store_true", help="Allow replacing or refreshing an installed runtime while preserving a versioned backup")
    parser.add_argument("--no-launch", action="store_true", help="Do not launch after installation")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without changing the system")
    parser.add_argument("--json-plan", action="store_true", help="Print the planned actions and exit")
    parser.add_argument("--platform", choices=("macos", "windows"), help="Override platform for diagnostics/tests")
    parser.add_argument("--runtime-root", type=Path, help="Override the bundled runtime source directory")
    args = parser.parse_args()

    current_platform = normalize_platform(args.platform)
    report = detect_environment(platform_name=current_platform, runtime_root=args.runtime_root)
    plan = make_plan(report, launch=not args.no_launch)
    if args.json_plan:
        print(json.dumps(asdict(plan), ensure_ascii=False, indent=2))
        return
    if not args.yes:
        raise SystemExit("INSTALLATION NOT STARTED: explicit confirmation is required; rerun with --yes")
    try:
        application = install(
            report,
            allow_toolchain=args.install_toolchain,
            allow_upgrade=args.upgrade,
            launch=not args.no_launch,
            dry_run=args.dry_run,
        )
    except RuntimeBuildError as exc:
        raise SystemExit(f"INSTALL FAILED: {json.dumps(exc.diagnostic, ensure_ascii=False)}") from exc
    except (InstallError, OSError, subprocess.SubprocessError) as exc:
        diagnostic = build_diagnostic(
            report,
            stage="install",
            attempt="installer",
            fallback_used=False,
            error=exc,
        )
        raise SystemExit(f"INSTALL FAILED: {json.dumps(diagnostic, ensure_ascii=False)}") from exc
    print(json.dumps({"installed": str(application) if application else None, "platform": current_platform}, ensure_ascii=False))


if __name__ == "__main__":
    main()
