#!/usr/bin/env python3
"""Single entrypoint for desktop-pet environment, packing, and delivery."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

from build_desktop_pet_delivery import build_delivery, current_platform
from build_desktop_pet_pack import write_deterministic_zip, write_review_artifacts
from check_desktop_pet_environment import detect_environment, human_summary
from install_desktop_pet_runtime import InstallError, RuntimeBuildError, build_diagnostic, install, make_plan
from prepare_generated_animation_strips import prepare_directory, prepare_phase_recipe
from validate_desktop_pet_pack import PackValidationError, validate_pack_directory


REPO_ROOT = Path(__file__).resolve().parents[1]


def fail(message: str, *, as_json: bool, extra: dict | None = None, code: int = 1) -> int:
    if as_json:
        payload = {"ok": False, "error": message}
        if extra:
            payload.update(extra)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(message)
    return code


def resolve_pet_dir(source: Path) -> Path:
    path = source.expanduser().resolve()
    if path.is_file() and path.name == "pet.json":
        return path.parent
    return path


def default_outputs(pack_id: str, schema_version: int, platform_name: str) -> dict[str, Path]:
    generated = REPO_ROOT / "generated-pets"
    stem = pack_id if pack_id.endswith(f"-v{schema_version}") else f"{pack_id}-v{schema_version}"
    return {
        "zip": generated / f"{stem}.zip",
        "review": generated / f"{stem}-review",
        "delivery": generated / f"{pack_id}-{platform_name}",
    }


def cmd_doctor(args: argparse.Namespace) -> int:
    report = detect_environment(
        platform_name=args.platform,
        runtime_root=args.runtime_root,
        required_schema=args.required_schema,
        probe_registry=args.probe_registry,
    )
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(human_summary(report))
    return 0 if report.supported else 2


def cmd_install(args: argparse.Namespace) -> int:
    report = detect_environment(platform_name=args.platform, runtime_root=args.runtime_root, probe_registry=False)
    plan = make_plan(
        report,
        launch=not args.no_launch,
        use_mirror=args.mirror,
        allow_upgrade=args.upgrade,
    )
    if args.json_plan:
        print(json.dumps(asdict(plan), ensure_ascii=False, indent=2))
        return 0
    if not args.yes:
        return fail("INSTALLATION NOT STARTED: explicit confirmation is required; rerun with --yes", as_json=args.json)
    try:
        application = install(
            report,
            allow_toolchain=args.install_toolchain,
            allow_upgrade=args.upgrade,
            launch=not args.no_launch,
            dry_run=args.dry_run,
            use_mirror=args.mirror,
        )
    except RuntimeBuildError as exc:
        return fail(
            f"INSTALL FAILED: {json.dumps(exc.diagnostic, ensure_ascii=False)}",
            as_json=args.json,
            extra={"diagnostic": exc.diagnostic},
        )
    except (InstallError, OSError, subprocess.SubprocessError) as exc:
        diagnostic = build_diagnostic(
            report,
            stage="install",
            attempt="installer",
            fallback_used=False,
            error=exc,
            use_mirror=args.mirror,
        )
        return fail(
            f"INSTALL FAILED: {json.dumps(diagnostic, ensure_ascii=False)}",
            as_json=args.json,
            extra={"diagnostic": diagnostic},
        )
    print(json.dumps(
        {
            "ok": True,
            "installed": str(application) if application else None,
            "platform": report.platform,
            "reusedCachedBuild": plan.reuseCachedBuild,
        },
        ensure_ascii=False,
    ))
    return 0


def cmd_prepare(args: argparse.Namespace) -> int:
    try:
        if args.recipe:
            prepare_phase_recipe(args.recipe, args.source, args.destination)
        else:
            prepare_directory(args.source, args.destination)
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        return fail(str(exc), as_json=args.json)
    print(json.dumps(
        {
            "ok": True,
            "source": str(args.source),
            "destination": str(args.destination),
            "recipe": str(args.recipe) if args.recipe else None,
        },
        ensure_ascii=False,
    ) if args.json else f"prepared {args.destination}")
    return 0


def cmd_review(args: argparse.Namespace) -> int:
    source = resolve_pet_dir(args.source)
    try:
        result = validate_pack_directory(source)
        defaults = default_outputs(result.pack_id, result.manifest["schemaVersion"], current_platform())
        review_dir = args.review_dir or defaults["review"]
        artifacts = write_review_artifacts(result.root, result.manifest, review_dir)
    except (OSError, PackValidationError, ValueError) as exc:
        extra = exc.to_dict() if isinstance(exc, PackValidationError) else None
        return fail(str(exc), as_json=args.json, extra=extra)
    print(json.dumps(
        {
            "ok": True,
            "packId": result.pack_id,
            "schemaVersion": result.manifest["schemaVersion"],
            "review": str(review_dir.resolve()),
            "artifacts": artifacts,
        },
        ensure_ascii=False,
    ))
    return 0


def cmd_pack(args: argparse.Namespace) -> int:
    source = resolve_pet_dir(args.source)
    try:
        result = validate_pack_directory(source)
        platform_name = args.delivery_platform or current_platform()
        defaults = default_outputs(result.pack_id, result.manifest["schemaVersion"], platform_name)
        review_dir = args.review_dir or defaults["review"]
        zip_path = args.out or defaults["zip"]
        delivery_dir = args.delivery_dir or defaults["delivery"]
        artifacts = write_review_artifacts(result.root, result.manifest, review_dir)
        write_deterministic_zip(result.root, zip_path, result.pack_id)
        delivery = build_delivery(zip_path, delivery_dir, platform_name, force=args.force)
    except (OSError, PackValidationError, ValueError) as exc:
        extra = exc.to_dict() if isinstance(exc, PackValidationError) else None
        return fail(str(exc), as_json=args.json, extra=extra)
    print(json.dumps(
        {
            "ok": True,
            "packId": result.pack_id,
            "schemaVersion": result.manifest["schemaVersion"],
            "pack": str(zip_path.resolve()),
            "review": str(review_dir.resolve()),
            "delivery": delivery["delivery"],
            "artifacts": artifacts,
        },
        ensure_ascii=False,
    ))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor", help="Read-only environment preflight")
    doctor.add_argument("--json", action="store_true")
    doctor.add_argument("--platform", choices=("macos", "windows"))
    doctor.add_argument("--runtime-root", type=Path)
    doctor.add_argument("--required-schema", type=int, choices=(2, 3), default=3)
    doctor.add_argument("--probe-registry", action="store_true")
    doctor.set_defaults(func=cmd_doctor)

    install_cmd = sub.add_parser("install", help="Install or upgrade the shared runner after explicit confirmation")
    install_cmd.add_argument("--yes", action="store_true")
    install_cmd.add_argument("--install-toolchain", action="store_true")
    install_cmd.add_argument("--upgrade", action="store_true")
    install_cmd.add_argument("--mirror", action="store_true")
    install_cmd.add_argument("--no-launch", action="store_true")
    install_cmd.add_argument("--dry-run", action="store_true")
    install_cmd.add_argument("--json-plan", action="store_true")
    install_cmd.add_argument("--json", action="store_true")
    install_cmd.add_argument("--platform", choices=("macos", "windows"))
    install_cmd.add_argument("--runtime-root", type=Path)
    install_cmd.set_defaults(func=cmd_install)

    prepare = sub.add_parser("prepare", help="Normalize animation strips or split a phase recipe")
    prepare.add_argument("source", type=Path)
    prepare.add_argument("destination", type=Path)
    prepare.add_argument("--recipe", type=Path)
    prepare.add_argument("--json", action="store_true")
    prepare.set_defaults(func=cmd_prepare)

    review = sub.add_parser("review", help="Build contact-sheet, timelines, preview GIF, and frame audit")
    review.add_argument("source", type=Path)
    review.add_argument("--review-dir", type=Path)
    review.add_argument("--json", action="store_true")
    review.set_defaults(func=cmd_review)

    pack = sub.add_parser("pack", help="Build, validate, and write a delivery folder in one step")
    pack.add_argument("source", type=Path)
    pack.add_argument("--out", type=Path)
    pack.add_argument("--review-dir", type=Path)
    pack.add_argument("--delivery-dir", type=Path)
    pack.add_argument("--delivery-platform", choices=("macos", "windows", "all"))
    pack.add_argument("--force", action="store_true")
    pack.add_argument("--json", action="store_true")
    pack.set_defaults(func=cmd_pack)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
