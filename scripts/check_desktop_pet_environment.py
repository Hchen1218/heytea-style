#!/usr/bin/env python3
"""Inspect whether the desktop-pet runner can be used or installed locally."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Mapping


PRODUCT_NAME = "Doodle Desktop Pet"
MIN_NODE_MAJOR = 20


@dataclass(frozen=True)
class EnvironmentReport:
    platform: str
    supported: bool
    status: str
    runtimeInstalled: bool
    runtimePath: str | None
    sourceAvailable: bool
    runtimeRoot: str
    nodeAvailable: bool
    nodeVersion: str | None
    nodeSupported: bool
    npmAvailable: bool
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


def node_major(version: str | None) -> int | None:
    if not version:
        return None
    match = re.search(r"v?(\d+)", version)
    return int(match.group(1)) if match else None


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
) -> EnvironmentReport:
    current_platform = normalize_platform(platform_name)
    current_home = (home or Path.home()).expanduser()
    current_environ = environ or os.environ
    root = (runtime_root or Path(__file__).resolve().parents[1] / "assets" / "desktop-pet-runtime").resolve()
    supported = current_platform in {"macos", "windows"}

    installed = next((candidate for candidate in runtime_candidates(current_platform, current_home, current_environ) if candidate.exists()), None)
    source_available = (root / "package.json").is_file() and (root / "src" / "main.js").is_file()
    node_path = which("node")
    npm_path = which("npm") or which("npm.cmd")
    version = command_version(node_path)
    major = node_major(version)
    node_supported = major is not None and major >= MIN_NODE_MAJOR
    dependencies_installed = (
        (root / "node_modules" / "electron").exists()
        and (root / "node_modules" / ".bin" / ("electron.cmd" if current_platform == "windows" else "electron")).exists()
        and (root / "node_modules" / ".bin" / ("electron-builder.cmd" if current_platform == "windows" else "electron-builder")).exists()
    )
    package_manager = "brew" if current_platform == "macos" and which("brew") else None
    if current_platform == "windows" and (which("winget") or which("winget.exe")):
        package_manager = "winget"

    missing: list[str] = []
    if not supported:
        missing.append("supported-platform")
    if not installed:
        missing.append("desktop-pet-runtime")
    if not source_available:
        missing.append("runtime-source")
    if not node_path:
        missing.append("node")
    elif not node_supported:
        missing.append(f"node>={MIN_NODE_MAJOR}")
    if not npm_path:
        missing.append("npm")
    if source_available and node_supported and npm_path and not dependencies_installed:
        missing.append("runtime-dependencies")

    if installed:
        status = "ready"
        next_action = "launch-runtime"
    elif not supported:
        status = "unsupported"
        next_action = "stop"
    elif not source_available:
        status = "missing-source"
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
        sourceAvailable=source_available,
        runtimeRoot=str(root),
        nodeAvailable=node_path is not None,
        nodeVersion=version,
        nodeSupported=node_supported,
        npmAvailable=npm_path is not None,
        dependenciesInstalled=dependencies_installed,
        packageManager=package_manager,
        installDirectory=str(destination) if destination else None,
        missing=missing,
        needsConfirmation=not bool(installed) and supported,
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
    lines.extend(
        [
            f"runtime source: {'yes' if report.sourceAvailable else 'no'}",
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
    args = parser.parse_args()

    report = detect_environment(platform_name=args.platform, runtime_root=args.runtime_root)
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2) if args.json else human_summary(report))
    if not report.supported:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
