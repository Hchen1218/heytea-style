#!/usr/bin/env python3
"""Install the bundled desktop-pet runner after explicit user confirmation."""

from __future__ import annotations

import json
import os
import plistlib
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from check_desktop_pet_environment import (
    MIN_NODE_VERSION,
    PRODUCT_NAME,
    EnvironmentReport,
    bundle_hash_path,
    detect_environment,
    select_mac_app,
    select_windows_unpacked,
    write_source_hash,
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
NPM_MIRROR_ENV = {
    "npm_config_registry": "https://registry.npmmirror.com",
    "ELECTRON_MIRROR": "https://npmmirror.com/mirrors/electron/",
    "ELECTRON_BUILDER_BINARIES_MIRROR": "https://npmmirror.com/mirrors/electron-builder-binaries/",
}
NETWORK_FAILURE_SIGNATURES = (
    "etimedout",
    "econnreset",
    "enotfound",
    "eai_again",
    "getaddrinfo",
    "socket hang up",
    "network is unreachable",
    "unable to resolve",
    "registry.npmjs.org",
    "fetch failed",
    "err_socket",
    "request to https://registry",
)


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
    reuseCachedBuild: bool
    sourceHash: str | None
    useMirror: bool


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


def runtime_is_current(report: EnvironmentReport) -> bool:
    return report.runtimeCompatible and report.installedSourceMatches


def should_reuse_cached_build(report: EnvironmentReport, *, allow_upgrade: bool = False) -> bool:
    if not report.sourceCompatible or not report.cachedBuildReady:
        return False
    if runtime_is_current(report):
        return False
    if report.runtimeCompatible and not allow_upgrade:
        return False
    return True


def mirror_environment(use_mirror: bool) -> dict[str, str] | None:
    if not use_mirror:
        return None
    env = os.environ.copy()
    env.update(NPM_MIRROR_ENV)
    return env


def is_network_failure(output: str) -> bool:
    lowered = output.lower()
    return any(signature in lowered for signature in NETWORK_FAILURE_SIGNATURES)


def diagnostic_advice(stage: str, output: str, *, fallback_used: bool, use_mirror: bool) -> tuple[str, list[str]]:
    summaries = {
        "dependencies": "安装运行器依赖失败（npm ci）。",
        "build": "打包桌宠运行器失败。",
        "validate": "打包产物自检未通过，没有写入用户目录。",
        "install": "将运行器复制到用户目录失败。",
    }
    steps: list[str] = []
    if is_network_failure(output):
        if use_mirror:
            steps.append("已使用 --mirror 仍失败：检查本机网络、代理，或稍后重试。")
        else:
            steps.append("网络或 npm registry 不可达：加上 --mirror 后重试（使用 npmmirror）。")
    if is_archive_build_failure(output) and not fallback_used:
        steps.append("这是 Electron 压缩包解压失败，安装器会自动用本地 electron/dist 重试一次。")
    if stage == "validate":
        steps.append("检查 assets/desktop-pet-runtime/dist 是否产出完整应用，以及 --self-test 输出。")
    if not steps:
        steps.append("查看 diagnostic.stderrTail 定位失败命令后重试。")
    return summaries.get(stage, "安装桌宠运行器失败。"), steps


def make_plan(
    report: EnvironmentReport,
    *,
    launch: bool = True,
    use_mirror: bool = False,
    allow_upgrade: bool = False,
) -> InstallPlan:
    npm = "npm.cmd" if report.platform == "windows" else "npm"
    build_script = "pack:win" if report.platform == "windows" else "pack:mac"
    root = Path(report.runtimeRoot)
    replacement_needed = report.runtimeInstalled and not report.runtimeCompatible
    source_refresh = report.runtimeCompatible and allow_upgrade and not report.installedSourceMatches
    refreshing = replacement_needed or source_refresh
    upgrade = refreshing and report.runtimeScope == "user"
    side_by_side = refreshing and report.runtimeScope == "system"
    if report.runtimeCompatible and not source_refresh:
        install_mode = "launch-existing"
    elif upgrade:
        install_mode = "in-place-upgrade"
    elif side_by_side:
        install_mode = "user-side-by-side"
    elif not report.runtimeInstalled:
        install_mode = "fresh-install"
    else:
        install_mode = "unavailable"
    reuse = should_reuse_cached_build(report, allow_upgrade=allow_upgrade)
    skip_build = (report.runtimeCompatible and not source_refresh) or reuse or not report.sourceCompatible
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
        stopExisting=refreshing,
        backupPath=backup,
        installToolchain=[] if reuse else toolchain_commands(report),
        installDependencies=None if skip_build or report.dependenciesInstalled else [npm, "ci"],
        buildRuntime=None if skip_build else [npm, "run", build_script],
        buildFallback=None if skip_build else [
            ["node", str(root / "node_modules" / "electron" / "install.js")],
            [npm, "run", build_script, "--", f"--config.electronDist={root / 'node_modules' / 'electron' / 'dist'}"],
        ],
        installDirectory=report.installDirectory,
        launchAfterInstall=launch,
        reuseCachedBuild=reuse,
        sourceHash=report.sourceHash,
        useMirror=use_mirror,
    )


def run(command: list[str], *, cwd: Path | None = None, dry_run: bool = False, env: dict[str, str] | None = None) -> None:
    print("+", " ".join(command))
    if not dry_run:
        subprocess.run(command, cwd=cwd, check=True, env=env)


def run_captured(command: list[str], *, cwd: Path, dry_run: bool = False, env: dict[str, str] | None = None) -> str:
    print("+", " ".join(command))
    if dry_run:
        return ""
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True, env=env)
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
    use_mirror: bool = False,
) -> dict:
    output = error.output if isinstance(error, CapturedCommandError) else str(error)
    summary, next_steps = diagnostic_advice(stage, output, fallback_used=fallback_used, use_mirror=use_mirror)
    return {
        "stage": stage,
        "attempt": attempt,
        "summary": summary,
        "nextSteps": next_steps,
        "networkFailure": is_network_failure(output),
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
    env: dict[str, str] | None = None,
) -> bool:
    build_script = "pack:win" if report.platform == "windows" else "pack:mac"
    try:
        run_captured([npm, "run", build_script], cwd=root, dry_run=dry_run, env=env)
        return False
    except CapturedCommandError as first_error:
        if not is_archive_build_failure(first_error.output):
            raise RuntimeBuildError(build_diagnostic(
                report, stage="build", attempt="standard", fallback_used=False, error=first_error,
                use_mirror=bool(env and env.get("npm_config_registry") == NPM_MIRROR_ENV["npm_config_registry"]),
            )) from first_error

        electron_installer = root / "node_modules" / "electron" / "install.js"
        electron_dist = root / "node_modules" / "electron" / "dist"
        try:
            run_captured([node, str(electron_installer)], cwd=root, dry_run=dry_run, env=env)
            run_captured(
                [npm, "run", build_script, "--", f"--config.electronDist={electron_dist}"],
                cwd=root,
                dry_run=dry_run,
                env=env,
            )
            return True
        except CapturedCommandError as fallback_error:
            raise RuntimeBuildError(build_diagnostic(
                report, stage="build", attempt="fallback", fallback_used=True, error=fallback_error,
                use_mirror=bool(env and env.get("npm_config_registry") == NPM_MIRROR_ENV["npm_config_registry"]),
            )) from fallback_error


def find_mac_app(dist: Path) -> Path:
    found = select_mac_app(dist)
    if found is None:
        raise InstallError(f"macOS build did not produce {PRODUCT_NAME}.app")
    return found


def find_windows_directory(dist: Path) -> Path:
    found = select_windows_unpacked(dist)
    if found is None:
        raise InstallError("Windows build did not produce a runnable unpacked directory")
    return found


def stamp_built_source_hash(report: EnvironmentReport, source_hash: str | None, *, dry_run: bool = False) -> None:
    if not source_hash:
        return
    root = Path(report.runtimeRoot)
    bundle = find_mac_app(root / "dist") if report.platform == "macos" else find_windows_directory(root / "dist")
    marker = bundle_hash_path(report.platform, bundle)
    print(f"+ stamp {marker}")
    if not dry_run:
        write_source_hash(marker, source_hash)


def macos_bundle_has_executable(application: Path) -> bool:
    macos_dir = application / "Contents" / "MacOS"
    if not macos_dir.is_dir():
        return False
    return any(path.is_file() for path in macos_dir.iterdir())


def prepare_macos_application(application: Path, *, dry_run: bool = False) -> None:
    if sys.platform != "darwin" or not macos_bundle_has_executable(application):
        return
    print(f"+ xattr -dr com.apple.quarantine {application}")
    print(f"+ codesign --force --deep --sign - {application}")
    if dry_run:
        return
    subprocess.run(["xattr", "-dr", "com.apple.quarantine", str(application)], check=False, capture_output=True)
    completed = subprocess.run(
        ["codesign", "--force", "--deep", "--sign", "-", str(application)],
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip() or f"exit {completed.returncode}"
        raise InstallError(f"ad-hoc codesign failed: {detail}")


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
            prepare_macos_application(destination, dry_run=dry_run)
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
    use_mirror: bool = False,
) -> Path | None:
    source_refresh = allow_upgrade and not report.installedSourceMatches
    if report.runtimeCompatible and not source_refresh:
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

    reuse = should_reuse_cached_build(report, allow_upgrade=allow_upgrade)
    if reuse:
        print("+ reuse cached runtime build")
    commands = toolchain_commands(report)
    if not reuse and (not report.nodeSupported or not report.npmAvailable):
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
    env = mirror_environment(use_mirror)
    fallback_used = False
    if not reuse:
        npm = shutil.which("npm.cmd" if report.platform == "windows" else "npm")
        node = shutil.which("node")
        if not npm:
            raise InstallError("npm is unavailable")
        if not node:
            raise InstallError("node is unavailable")
        if not report.dependenciesInstalled:
            try:
                run_captured([npm, "ci"], cwd=root, dry_run=dry_run, env=env)
            except CapturedCommandError as error:
                raise RuntimeBuildError(build_diagnostic(
                    report, stage="dependencies", attempt="npm-ci", fallback_used=False, error=error, use_mirror=use_mirror,
                )) from error
            if not dry_run:
                report = detect_environment(platform_name=report.platform, runtime_root=root)
                if not report.dependenciesInstalled:
                    error = InstallError(f"npm ci completed but runtime dependencies are {report.dependencyStatus}")
                    raise RuntimeBuildError(build_diagnostic(
                        report, stage="dependencies", attempt="post-install-check", fallback_used=False, error=error, use_mirror=use_mirror,
                    )) from error
        fallback_used = build_runtime(report, npm=npm, node=node, root=root, dry_run=dry_run, env=env)
    if not dry_run:
        validate_built_runtime(report, fallback_used=fallback_used)
        stamp_built_source_hash(report, report.sourceHash)
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


def main(argv: list[str] | None = None) -> int:
    from desktop_pet import main as cli_main

    return cli_main(["install", *(sys.argv[1:] if argv is None else argv)])


if __name__ == "__main__":
    sys.exit(main())
