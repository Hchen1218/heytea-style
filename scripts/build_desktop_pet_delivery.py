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


def current_platform() -> str:
    if sys.platform == "darwin":
        return "macos"
    if sys.platform == "win32":
        return "windows"
    return sys.platform


def mac_launchers(pack_name: str) -> dict[str, str]:
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
    return {
        "启动桌宠.command": common + f'open -n "$RUNNER" --args --open-pet "$HERE/{pack_name}"\n',
        "关闭桌宠.command": common + 'open -n "$RUNNER" --args --quit\n',
    }


def windows_launchers(pack_name: str) -> dict[str, str]:
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
    return {
        "启动桌宠.cmd": common + f'start "" "%RUNNER%" --open-pet "%~dp0{pack_name}"\r\n',
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

    pack_name = f"{result.pack_id}-v2.zip"
    shutil.copy2(pack, out / pack_name)
    (out / pack_name).chmod(0o644)
    extract_preview(pack, result.pack_id, out / "preview.png")

    launchers: dict[str, str] = {}
    if platform_name in {"macos", "all"}:
        launchers.update(mac_launchers(pack_name))
    if platform_name in {"windows", "all"}:
        launchers.update(windows_launchers(pack_name))
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
    parser.add_argument("pack", type=Path, help="Validated schema-v2 pet ZIP")
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
