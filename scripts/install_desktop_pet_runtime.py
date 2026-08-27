#!/usr/bin/env python3
"""Install the bundled desktop-pet runner after explicit user confirmation."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from check_desktop_pet_environment import (
    MIN_NODE_MAJOR,
    PRODUCT_NAME,
    EnvironmentReport,
    detect_environment,
    normalize_platform,
)


class InstallError(RuntimeError):
    pass


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
        installDependencies=None if report.dependenciesInstalled or not report.sourceCompatible else [npm, "install"],
        buildRuntime=None if report.runtimeCompatible or not report.sourceCompatible else [npm, "run", build_script],
        installDirectory=report.installDirectory,
        launchAfterInstall=launch,
    )


def run(command: list[str], *, cwd: Path | None = None, dry_run: bool = False) -> None:
    print("+", " ".join(command))
    if not dry_run:
        subprocess.run(command, cwd=cwd, check=True)


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
                f"Node.js {MIN_NODE_MAJOR}+ and npm are required; rerun with --install-toolchain after confirmation"
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
    if not npm:
        raise InstallError("npm is unavailable")
    if not report.dependenciesInstalled:
        run([npm, "install"], cwd=root, dry_run=dry_run)
    run([npm, "run", "pack:win" if report.platform == "windows" else "pack:mac"], cwd=root, dry_run=dry_run)
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
    except (InstallError, OSError, subprocess.SubprocessError) as exc:
        raise SystemExit(f"INSTALL FAILED: {exc}") from exc
    print(json.dumps({"installed": str(application) if application else None, "platform": current_platform}, ensure_ascii=False))


if __name__ == "__main__":
    main()
