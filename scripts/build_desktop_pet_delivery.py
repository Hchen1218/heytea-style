#!/usr/bin/env python3
"""Build a user-facing pet folder with launch/quit entrypoints and one validated pack."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path

from validate_desktop_pet_pack import PackValidationError, validate_pack


PRODUCT_NAME = "Doodle Desktop Pet"
MIN_RUNTIME_BY_SCHEMA = {2: "2.0.0", 3: "3.1.0"}


def minimum_runtime_version(schema_version: int) -> str:
    return MIN_RUNTIME_BY_SCHEMA[3 if schema_version >= 3 else 2]


def current_platform() -> str:
    if sys.platform == "darwin":
        return "macos"
    if sys.platform == "win32":
        return "windows"
    return sys.platform


def mac_launchers(pack_name: str, schema_version: int) -> dict[str, str]:
    common = f'''#!/bin/zsh
set -u
HERE=${{0:A:h}}
RUNNER="$HOME/Applications/{PRODUCT_NAME}.app"
[[ -d "$RUNNER" ]] || RUNNER="/Applications/{PRODUCT_NAME}.app"
if [[ ! -d "$RUNNER" ]]; then
  echo "尚未安装 {PRODUCT_NAME}。请先通过桌宠 Skill 安装一次通用运行器。"
  read "?按回车键关闭…"
  exit 1
fi
'''
    required_version = minimum_runtime_version(schema_version)
    compatibility = f'''RUNTIME_VERSION=$(/usr/libexec/PlistBuddy -c "Print :CFBundleShortVersionString" "$RUNNER/Contents/Info.plist" 2>/dev/null || true)
REQUIRED_VERSION="{required_version}"
version_at_least() {{
  local installed="$1" required="$2"
  local -a installed_parts required_parts
  installed_parts=("${{(@s:.:)installed}}")
  required_parts=("${{(@s:.:)required}}")
  local index have need
  for index in 1 2 3; do
    have=${{installed_parts[$index]:-0}}
    need=${{required_parts[$index]:-0}}
    [[ "$have" == <-> && "$need" == <-> ]] || return 1
    (( have > need )) && return 0
    (( have < need )) && return 1
  done
  return 0
}}
if ! version_at_least "$RUNTIME_VERSION" "$REQUIRED_VERSION"; then
  echo "此角色包需要 {PRODUCT_NAME} $REQUIRED_VERSION 或更高版本；当前版本：${{RUNTIME_VERSION:-未知}}。"
  echo "请先通过桌宠 Skill 升级通用运行器。"
  read "?按回车键关闭…"
  exit 2
fi
'''
    return {
        "启动桌宠.command": common + compatibility + f'open -n "$RUNNER" --args --open-pet "$HERE/{pack_name}"\n',
        "关闭桌宠.command": common + 'open -n "$RUNNER" --args --quit\n',
    }


def windows_launchers(pack_name: str, schema_version: int) -> dict[str, str]:
    common = f'''@echo off\r
setlocal\r
set "RUNNER=%LOCALAPPDATA%\\Programs\\{PRODUCT_NAME}\\{PRODUCT_NAME}.exe"\r
if not exist "%RUNNER%" set "RUNNER=%ProgramFiles%\\{PRODUCT_NAME}\\{PRODUCT_NAME}.exe"\r
if not exist "%RUNNER%" (\r
  echo {PRODUCT_NAME} is not installed. Install the shared runtime once with the desktop-pet Skill.\r
  pause\r
  exit /b 1\r
)\r
'''
    required_version = minimum_runtime_version(schema_version)
    required_major = int(required_version.split('.')[0])
    compatibility = f'''set "RUNTIME_VERSION="\r
for /f "usebackq delims=" %%V in (`powershell -NoProfile -Command "(Get-Item $args[0]).VersionInfo.ProductVersion" "%RUNNER%"`) do set "RUNTIME_VERSION=%%V"\r
for /f "tokens=1 delims=." %%M in ("%RUNTIME_VERSION%") do set "RUNTIME_MAJOR=%%M"\r
if not defined RUNTIME_MAJOR (\r
  echo Cannot determine the installed {PRODUCT_NAME} version. Version {required_major}.0.0 or later is required.\r
  pause\r
  exit /b 2\r
)\r
if %RUNTIME_MAJOR% LSS {required_major} (\r
  echo This pet requires {PRODUCT_NAME} {required_major}.0.0 or later. Installed: %RUNTIME_VERSION%\r
  pause\r
  exit /b 2\r
)\r
'''
    compatibility += f'''powershell -NoProfile -Command "try {{ if ([version]$args[0] -lt [version]$args[1]) {{ exit 1 }} }} catch {{ exit 2 }}" "%RUNTIME_VERSION%" "{required_version}"
if errorlevel 1 (
  echo This pet requires {PRODUCT_NAME} {required_version} or later. Installed: %RUNTIME_VERSION%
  pause
  exit /b 2
)
'''
    return {
        "启动桌宠.cmd": common + compatibility + f'start "" "%RUNNER%" --open-pet "%~dp0{pack_name}"\r\n',
        "关闭桌宠.cmd": common + 'start "" "%RUNNER%" --quit\r\n',
    }


def extract_preview(pack: Path, pack_id: str, destination: Path) -> None:
    member = f"{pack_id}/preview.png"
    with zipfile.ZipFile(pack) as archive:
        try:
            data = archive.read(member)
        except KeyError as exc:
            raise PackValidationError("validated pack is missing preview.png") from exc
    destination.write_bytes(data)


def build_delivery(pack: Path, out: Path, platform_name: str, *, force: bool = False) -> dict:
    result = validate_pack(pack)
    if platform_name not in {"macos", "windows", "all"}:
        raise ValueError(f"unsupported delivery platform: {platform_name}")
    if out.exists():
        if not force:
            raise FileExistsError(f"delivery directory already exists: {out}")
        shutil.rmtree(out)
    out.mkdir(parents=True)

    pack_name = f"{result.pack_id}-v{result.manifest['schemaVersion']}.zip"
    shutil.copy2(pack, out / pack_name)
    (out / pack_name).chmod(0o644)
    extract_preview(pack, result.pack_id, out / "preview.png")

    launchers: dict[str, str] = {}
    if platform_name in {"macos", "all"}:
        launchers.update(mac_launchers(pack_name, result.manifest["schemaVersion"]))
    if platform_name in {"windows", "all"}:
        launchers.update(windows_launchers(pack_name, result.manifest["schemaVersion"]))
    for name, content in launchers.items():
        target = out / name
        target.write_text(content, encoding="utf-8", newline="")
        if target.suffix == ".command":
            target.chmod(target.stat().st_mode | 0o111)

    instructions = (
        "桌宠使用说明\n\n"
        "1. 通用运行器只需要安装一次，本文件夹不会重复携带 Electron 程序。\n"
        "2. 双击“启动桌宠”会导入或切换到本角色；已经运行时不会创建第二只桌宠。\n"
        "3. 右键桌宠可暂停、调整活跃度和尺寸、切换角色、隐藏或退出。\n"
        "4. 双击“关闭桌宠”会保存设置并正常退出，不会强制杀进程。\n"
        "5. 桌宠隐藏后仍可通过系统托盘菜单重新显示。\n"
        f"6. 本角色包需要 Doodle Desktop Pet {minimum_runtime_version(result.manifest['schemaVersion'])} 或更高版本。\n"
    )
    (out / "使用说明.txt").write_text(instructions, encoding="utf-8")
    return {
        "delivery": str(out.resolve()),
        "packId": result.pack_id,
        "platform": platform_name,
        "pack": pack_name,
        "launchers": sorted(launchers),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", type=Path, help="Validated schema-v2 or schema-v3 pet ZIP")
    parser.add_argument("--out", required=True, type=Path, help="New delivery directory")
    parser.add_argument("--platform", choices=("macos", "windows", "all"), default=current_platform())
    parser.add_argument("--force", action="store_true", help="Replace an existing delivery directory")
    args = parser.parse_args()
    try:
        summary = build_delivery(args.pack, args.out, args.platform, force=args.force)
    except (OSError, PackValidationError, ValueError) as exc:
        raise SystemExit(f"DELIVERY FAILED: {exc}") from exc
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
