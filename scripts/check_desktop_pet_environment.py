#!/usr/bin/env python3
"""Inspect whether the desktop-pet runner can be used or installed locally."""

from __future__ import annotations

import argparse
import json
import os
import platform
import plistlib
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Mapping


PRODUCT_NAME = "Doodle Desktop Pet"
MIN_NODE_VERSION = "22.12.0"
MIN_RUNTIME_BY_SCHEMA = {2: "2.0.0", 3: "3.1.0"}


@dataclass(frozen=True)
class EnvironmentReport:
    platform: str
    supported: bool
    status: str
    runtimeInstalled: bool
    runtimePath: str | None
    runtimeScope: str | None
    runtimeVersion: str | None
    runtimeCompatible: bool
    requiredSchema: int
    minimumRuntimeVersion: str
    sourceAvailable: bool
    sourceVersion: str | None
    sourceCompatible: bool
    runtimeRoot: str
    nodeAvailable: bool
    nodeVersion: str | None
    minimumNodeVersion: str
    nodeSupported: bool
    npmAvailable: bool
    npmVersion: str | None
    dependencyStatus: str
    electronVersion: str | None
    electronBuilderVersion: str | None
    dependenciesInstalled: bool
    packageManager: str | None
    installDirectory: str | None
    missing: list[str]
    needsConfirmation: bool
    nextAction: str


def normalize_platform(value: str | None = None) -> str:
    raw = (value or sys.platform).lower()
    if raw in {"darwin", "mac", "macos"}:
        return "macos"
    if raw in {"win32", "windows", "win"}:
        return "windows"
    return raw


def command_version(executable: str | None) -> str | None:
    if not executable:
        return None
    try:
        completed = subprocess.run(
            [executable, "--version"],
            check=True,
            capture_output=True,
            text=True,
            timeout=8,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return (completed.stdout or completed.stderr).strip() or None


def version_tuple(value: str | None) -> tuple[int, int, int] | None:
    if not value:
        return None
    match = re.match(r"^\s*v?(\d+)(?:\.(\d+))?(?:\.(\d+))?", value)
    if not match:
        return None
    return tuple(int(part or 0) for part in match.groups())


def package_version(path: Path) -> str | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8")).get("version")
        return str(value) if value else None
    except (OSError, json.JSONDecodeError):
        return None


def expected_dependency_versions(root: Path) -> tuple[str | None, str | None, str | None]:
    try:
        metadata = json.loads((root / "package.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None, None, None
    development = metadata.get("devDependencies") or {}
    return development.get("electron"), development.get("electron-builder"), development.get("@electron/asar")


def lockfile_matches_dependencies(
    root: Path,
    electron: str | None,
    builder: str | None,
    asar: str | None,
) -> bool:
    try:
        packages = json.loads((root / "package-lock.json").read_text(encoding="utf-8")).get("packages") or {}
        root_development = (packages.get("") or {}).get("devDependencies") or {}
        return bool(
            electron
            and builder
            and asar
            and root_development.get("electron") == electron
            and root_development.get("electron-builder") == builder
            and root_development.get("@electron/asar") == asar
            and (packages.get("node_modules/electron") or {}).get("version") == electron
            and (packages.get("node_modules/electron-builder") or {}).get("version") == builder
            and (packages.get("node_modules/@electron/asar") or {}).get("version") == asar
        )
    except (OSError, json.JSONDecodeError):
        return False


def runtime_version(platform_name: str, application: Path) -> str | None:
    if platform_name == "macos":
        try:
            with (application / "Contents" / "Info.plist").open("rb") as handle:
                value = plistlib.load(handle).get("CFBundleShortVersionString")
            return str(value) if value else None
        except (OSError, plistlib.InvalidFileException):
            return None
    if platform_name == "windows":
        powershell = shutil.which("powershell") or shutil.which("powershell.exe")
        if not powershell:
            return None
        try:
            completed = subprocess.run(
                [powershell, "-NoProfile", "-Command", "(Get-Item $args[0]).VersionInfo.ProductVersion", str(application)],
                check=True, capture_output=True, text=True, timeout=8,
            )
            return completed.stdout.strip() or None
        except (OSError, subprocess.SubprocessError):
            return None
    return None


def runtime_candidates(platform_name: str, home: Path, environ: Mapping[str, str]) -> list[Path]:
    if platform_name == "macos":
        return [
            home / "Applications" / f"{PRODUCT_NAME}.app",
            Path("/Applications") / f"{PRODUCT_NAME}.app",
        ]
    if platform_name == "windows":
        local = Path(environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
        program_files = Path(environ.get("ProgramFiles", "C:/Program Files"))
        return [
            local / "Programs" / PRODUCT_NAME / f"{PRODUCT_NAME}.exe",
            program_files / PRODUCT_NAME / f"{PRODUCT_NAME}.exe",
        ]
    return []


def default_install_directory(platform_name: str, home: Path, environ: Mapping[str, str]) -> Path | None:
    if platform_name == "macos":
        return home / "Applications"
    if platform_name == "windows":
        local = Path(environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
        return local / "Programs" / PRODUCT_NAME
    return None


def detect_environment(
    *,
    platform_name: str | None = None,
    runtime_root: Path | None = None,
    home: Path | None = None,
    environ: Mapping[str, str] | None = None,
    which: Callable[[str], str | None] = shutil.which,
    required_schema: int = 3,
) -> EnvironmentReport:
    current_platform = normalize_platform(platform_name)
    current_home = (home or Path.home()).expanduser()
    current_environ = environ or os.environ
    root = (runtime_root or Path(__file__).resolve().parents[1] / "assets" / "desktop-pet-runtime").resolve()
    supported = current_platform in {"macos", "windows"}
    if required_schema not in MIN_RUNTIME_BY_SCHEMA:
        raise ValueError(f"unsupported required schema: {required_schema}")

    candidates = runtime_candidates(current_platform, current_home, current_environ)
    installed = next((candidate for candidate in candidates if candidate.exists()), None)
    installed_scope = None
    if installed:
        installed_scope = "user" if candidates and installed == candidates[0] else "system"
    installed_version = runtime_version(current_platform, installed) if installed else None
    minimum_version = MIN_RUNTIME_BY_SCHEMA[required_schema]
    installed_tuple = version_tuple(installed_version)
    minimum_tuple = version_tuple(minimum_version)
    runtime_compatible = bool(installed and installed_tuple and minimum_tuple and installed_tuple >= minimum_tuple)
    source_available = (root / "package.json").is_file() and (root / "src" / "main.js").is_file()
    source_version = None
    if source_available:
        try:
            source_version = str(json.loads((root / "package.json").read_text(encoding="utf-8")).get("version") or "") or None
        except (OSError, json.JSONDecodeError):
            source_version = None
    source_tuple = version_tuple(source_version)
    source_compatible = bool(source_available and source_tuple and minimum_tuple and source_tuple >= minimum_tuple)
    node_path = which("node")
    npm_path = which("npm") or which("npm.cmd")
    version = command_version(node_path)
    npm_version = command_version(npm_path)
    node_supported = bool(version_tuple(version) and version_tuple(version) >= version_tuple(MIN_NODE_VERSION))
    node_modules = root / "node_modules"
    electron_version = package_version(node_modules / "electron" / "package.json")
    electron_builder_version = package_version(node_modules / "electron-builder" / "package.json")
    asar_version = package_version(node_modules / "@electron" / "asar" / "package.json")
    expected_electron, expected_builder, expected_asar = expected_dependency_versions(root)
    lockfile_ready = lockfile_matches_dependencies(root, expected_electron, expected_builder, expected_asar)
    electron_binary = node_modules / ".bin" / ("electron.cmd" if current_platform == "windows" else "electron")
    builder_binary = node_modules / ".bin" / ("electron-builder.cmd" if current_platform == "windows" else "electron-builder")
    dependency_artifacts_exist = node_modules.exists() or electron_version is not None or electron_builder_version is not None
    dependencies_installed = bool(
        expected_electron
        and expected_builder
        and expected_asar
        and lockfile_ready
        and electron_version == expected_electron
        and electron_builder_version == expected_builder
        and asar_version == expected_asar
        and electron_binary.exists()
        and builder_binary.exists()
    )
    dependency_status = "ready" if dependencies_installed else "drifted" if dependency_artifacts_exist else "missing"
    package_manager = "brew" if current_platform == "macos" and which("brew") else None
    if current_platform == "windows" and (which("winget") or which("winget.exe")):
        package_manager = "winget"

    missing: list[str] = []
    if not supported:
        missing.append("supported-platform")
    if not installed:
        missing.append("desktop-pet-runtime")
    elif not runtime_compatible:
        missing.append(f"desktop-pet-runtime>={minimum_version}")
    if not source_available:
        missing.append("runtime-source")
    elif not source_compatible:
        missing.append(f"runtime-source>={minimum_version}")
    if not node_path:
        missing.append("node")
    elif not node_supported:
        missing.append(f"node>={MIN_NODE_VERSION}")
    if not npm_path:
        missing.append("npm")
    if source_available and node_supported and npm_path and not dependencies_installed:
        missing.append("runtime-dependencies")

    if runtime_compatible:
        status = "ready"
        next_action = "launch-runtime"
    elif not supported:
        status = "unsupported"
        next_action = "stop"
    elif installed and not source_compatible:
        status = "upgrade-source-missing" if not source_available else "upgrade-source-incompatible"
        next_action = "provide-runtime-package"
    elif installed and (not node_supported or not npm_path):
        status = "needs-toolchain"
        next_action = "ask-to-install-toolchain-for-upgrade"
    elif installed:
        status = "upgradeable"
        next_action = "ask-to-upgrade-runtime"
    elif not source_compatible:
        status = "missing-source" if not source_available else "incompatible-source"
        next_action = "provide-runtime-package"
    elif not node_supported or not npm_path:
        status = "needs-toolchain"
        next_action = "ask-to-install-toolchain"
    else:
        status = "installable"
        next_action = "ask-to-install-runtime"

    destination = default_install_directory(current_platform, current_home, current_environ)
    return EnvironmentReport(
        platform=current_platform,
        supported=supported,
        status=status,
        runtimeInstalled=installed is not None,
        runtimePath=str(installed) if installed else None,
        runtimeScope=installed_scope,
        runtimeVersion=installed_version,
        runtimeCompatible=runtime_compatible,
        requiredSchema=required_schema,
        minimumRuntimeVersion=minimum_version,
        sourceAvailable=source_available,
        sourceVersion=source_version,
        sourceCompatible=source_compatible,
        runtimeRoot=str(root),
        nodeAvailable=node_path is not None,
        nodeVersion=version,
        minimumNodeVersion=MIN_NODE_VERSION,
        nodeSupported=node_supported,
        npmAvailable=npm_path is not None,
        npmVersion=npm_version,
        dependencyStatus=dependency_status,
        electronVersion=electron_version,
        electronBuilderVersion=electron_builder_version,
        dependenciesInstalled=dependencies_installed,
        packageManager=package_manager,
        installDirectory=str(destination) if destination else None,
        missing=missing,
        needsConfirmation=supported and not runtime_compatible and source_compatible,
        nextAction=next_action,
    )


def human_summary(report: EnvironmentReport) -> str:
    lines = [
        f"platform: {report.platform}",
        f"status: {report.status}",
        f"runtime installed: {'yes' if report.runtimeInstalled else 'no'}",
    ]
    if report.runtimePath:
        lines.append(f"runtime path: {report.runtimePath}")
        lines.append(f"runtime scope: {report.runtimeScope}")
    lines.append(f"runtime version: {report.runtimeVersion or 'unknown'} (required >= {report.minimumRuntimeVersion})")
    lines.extend(
        [
            f"runtime source: {'yes' if report.sourceAvailable else 'no'}",
            f"runtime source version: {report.sourceVersion or 'unknown'}",
            f"node: {report.nodeVersion or 'missing'}",
            f"npm: {'yes' if report.npmAvailable else 'no'}",
            f"dependencies: {'yes' if report.dependenciesInstalled else 'no'}",
            f"next action: {report.nextAction}",
        ]
    )
    if report.missing:
        lines.append(f"missing: {', '.join(report.missing)}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print a machine-readable report")
    parser.add_argument("--platform", choices=("macos", "windows"), help="Override platform for diagnostics/tests")
    parser.add_argument("--runtime-root", type=Path, help="Override the bundled runtime source directory")
    parser.add_argument("--required-schema", type=int, choices=(2, 3), default=3, help="Pack schema that the installed runner must support")
    args = parser.parse_args()

    report = detect_environment(platform_name=args.platform, runtime_root=args.runtime_root, required_schema=args.required_schema)
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2) if args.json else human_summary(report))
    if not report.supported:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
