#!/usr/bin/env python3
"""Manage voice-layer skills for Claude Code and Codex."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from validate_profile import validate_profile


SKILL_NAMES = ("write-in-my-voice", "calibrate-my-voice")
PROJECT = "voice-layer"
MARKER = ".voice-layer-install.json"
VERSION = "0.1.0"
CLAUDE_PACKAGE = "packages/claude-code"
CODEX_PACKAGE = "packages/codex"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def source_root(agent_kind: str) -> Path:
    root = repo_root()
    if agent_kind == "claude":
        return root / CLAUDE_PACKAGE / "skills"
    if agent_kind == "codex":
        return root / CODEX_PACKAGE / "skills"
    raise ValueError(f"unsupported agent kind: {agent_kind}")


def default_config_home() -> Path:
    configured = os.environ.get("XDG_CONFIG_HOME")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".config"


def target_specs(agent: str) -> list[tuple[str, Path, Path]]:
    targets: list[tuple[str, Path, Path]] = []
    if agent in ("claude", "both"):
        targets.append(("claude", Path.home() / ".claude" / "skills", source_root("claude")))
    if agent in ("codex", "both"):
        targets.append(("codex", Path.home() / ".agents" / "skills", source_root("codex")))
    return targets


def profile_path(value: str | None) -> Path:
    if value:
        return Path(value).expanduser()
    configured = os.environ.get("VOICE_LAYER_PROFILE")
    if configured:
        return Path(configured).expanduser()
    return default_profile_path()


def default_profile_path() -> Path:
    return default_config_home() / "voice-layer" / "voice-profile.md"


def same_symlink(target: Path, source: Path) -> bool:
    return target.is_symlink() and target.resolve() == source.resolve()


def remove_target(target: Path) -> None:
    if target.is_dir() and not target.is_symlink():
        shutil.rmtree(target)
    else:
        target.unlink()


def marker_payload(source: Path, agent_target: Path) -> dict[str, str]:
    return {
        "project": PROJECT,
        "version": VERSION,
        "source": str(source),
        "installed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "target": str(agent_target),
    }


def has_marker(target: Path) -> bool:
    marker = target / MARKER
    if not marker.exists():
        return False
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return data.get("project") == PROJECT


def backup_target(target: Path, dry_run: bool) -> Path:
    suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    backup = target.with_name(f"{target.name}.backup.{suffix}")
    action = "would backup" if dry_run else "backup"
    print(f"{action}: {target} -> {backup}")
    if not dry_run:
        target.rename(backup)
    return backup


def install_one(
    source: Path,
    target: Path,
    mode: str,
    force: bool,
    backup_existing: bool,
    dry_run: bool,
) -> None:
    if target.exists() or target.is_symlink():
        if same_symlink(target, source):
            print(f"already installed: {target}")
            return
        if backup_existing:
            backup_target(target, dry_run)
        elif has_marker(target):
            print(f"replace managed install: {target}")
            if not dry_run:
                remove_target(target)
        elif force:
            print(f"replace unmanaged path: {target}")
            if not dry_run:
                remove_target(target)
        else:
            message = (
                f"refusing to replace existing unmanaged path: {target}\n"
                "Use --backup-existing to preserve it, or --force if replacement is intentional."
            )
            if dry_run:
                print(f"would skip existing unmanaged path: {target}")
                return
            raise SystemExit(message)

    action = f"would {mode}" if dry_run else mode
    print(f"{action}: {source} -> {target}")
    if dry_run:
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    if mode == "symlink":
        target.symlink_to(source, target_is_directory=True)
    else:
        shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        (target / MARKER).write_text(
            json.dumps(marker_payload(source, target), indent=2) + "\n",
            encoding="utf-8",
        )


def ensure_profile(path: Path, dry_run: bool) -> None:
    root = repo_root()
    template = (
        root
        / "core"
        / "profile"
        / "voice-profile.template.md"
    )
    if path.exists():
        print(f"profile exists: {path}")
        secure_profile_permissions(path, dry_run)
        return
    action = "would create profile template" if dry_run else "create profile template"
    print(f"{action}: {path}")
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template, path)
    secure_profile_permissions(path, dry_run=False)


def secure_profile_permissions(path: Path, dry_run: bool) -> None:
    mode = path.stat().st_mode & 0o777
    if mode == 0o600:
        return
    action = "would secure profile permissions" if dry_run else "secure profile permissions"
    print(f"{action}: {path} {oct(mode)} -> 0o600")
    if not dry_run:
        path.chmod(0o600)


def uninstall_one(source: Path, target: Path, force: bool, dry_run: bool) -> None:
    if not target.exists() and not target.is_symlink():
        print(f"not installed: {target}")
        return
    if not (
        same_symlink(target, source)
        or has_marker(target)
        or force
    ):
        message = (
            f"refusing to uninstall unmanaged path: {target}\n"
            "Use --force only if this is the voice-layer install you want to remove."
        )
        if dry_run:
            print(f"would skip unmanaged path: {target}")
            return
        raise SystemExit(message)
    action = "would remove" if dry_run else "remove"
    print(f"{action}: {target}")
    if dry_run:
        return
    remove_target(target)


def profile_state(path: Path) -> str:
    if not path.exists():
        return "missing"
    text = path.read_text(encoding="utf-8", errors="replace")
    if "Not calibrated yet." in text:
        return "placeholder"
    return "present"


def profile_health(path: Path) -> str:
    if not path.exists():
        return "missing"
    result = validate_profile(path)
    if result.errors:
        return f"invalid ({len(result.errors)} error{'s' if len(result.errors) != 1 else ''})"
    if result.warnings:
        return f"valid with warnings ({len(result.warnings)})"
    return "valid"


def profile_permissions(path: Path) -> str:
    if not path.exists():
        return "missing"
    mode = path.stat().st_mode & 0o777
    if mode != 0o600:
        return f"{oct(mode)} (expected 0o600)"
    return oct(mode)


def doctor(agent: str, profile: Path) -> int:
    root = repo_root()
    print(f"voice-layer doctor v{VERSION}")
    print(f"repo: {root}")
    print(f"codex marketplace file: {root / '.agents' / 'plugins' / 'marketplace.json'}")
    print(f"claude marketplace file: {root / '.claude-plugin' / 'marketplace.json'}")
    print("scope: direct skill installs only; plugin-manager installs are checked by the agent plugin UI.")
    print(f"profile: {profile} ({profile_state(profile)})")
    print(f"profile schema: {profile_health(profile)}")
    print(f"profile permissions: {profile_permissions(profile)}")
    missing_targets = 0
    for skill_name in SKILL_NAMES:
        for agent_kind, base_target, skills in target_specs(agent):
            source = skills / skill_name
            print(f"source {agent_kind} {skill_name}: {'ok' if source.exists() else 'missing'}")
            target = base_target / skill_name
            if same_symlink(target, source):
                status = "installed (symlink)"
            elif has_marker(target):
                status = "installed (managed copy)"
            elif target.exists() or target.is_symlink():
                status = "present but unmanaged"
            else:
                status = "missing"
                missing_targets += 1
            print(f"target {target}: {status}")
    print("next:")
    if missing_targets:
        print("  Install skills: voice-layer install --agent both")
    state = profile_state(profile)
    if state in ("missing", "placeholder"):
        print("  First calibration: Use $calibrate-my-voice to build my local voice profile from pasted samples.")
    else:
        print("  Codex direct skill: Use $write-in-my-voice to rewrite this Slack reply: ...")
        print("  Claude direct skill: /write-in-my-voice rewrite this Slack reply: ...")
    return 0


def validate_profile_command(profile: Path, quiet: bool) -> int:
    result = validate_profile(profile)
    if result.errors:
        print(f"profile validation failed: {profile}", file=sys.stderr)
        for error in result.errors:
            print(f"- {error}", file=sys.stderr)
        for warning in result.warnings:
            print(f"warning: {warning}", file=sys.stderr)
        return 1
    if not quiet:
        for warning in result.warnings:
            print(f"warning: {warning}", file=sys.stderr)
        print(f"profile validation passed: {profile}")
    return 0


def confirm_purge(profile: Path, yes: bool) -> None:
    if yes:
        return
    if not sys.stdin.isatty():
        raise SystemExit("purge requires --yes when running non-interactively")
    answer = input(f"Permanently delete voice-layer profile data at {profile.parent}? [y/N] ")
    if answer.strip().lower() not in ("y", "yes"):
        raise SystemExit("purge cancelled")


def purge_profile(profile: Path, dry_run: bool) -> None:
    config_dir = default_config_home() / PROJECT
    if profile == config_dir / "voice-profile.md":
        action = "would remove config directory" if dry_run else "remove config directory"
        print(f"{action}: {config_dir}")
        if not dry_run and config_dir.exists():
            shutil.rmtree(config_dir)
        return
    action = "would remove profile" if dry_run else "remove profile"
    print(f"{action}: {profile}")
    if not dry_run and profile.exists():
        profile.unlink()


def add_common_agent_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--agent",
        choices=("claude", "codex", "both"),
        default="both",
        help="Which agent skill location to install into.",
    )


def add_common_profile_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--profile-path",
        help="Voice profile path. Defaults to $VOICE_LAYER_PROFILE or ~/.config/voice-layer/voice-profile.md.",
    )


def add_common_mutation_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--force", action="store_true", help="Replace or remove an unmanaged existing skill directory instead of preserving it.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without changing files.")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, prog="voice-layer")
    parser.add_argument("--version", action="version", version=f"voice-layer {VERSION}")
    subcommands = parser.add_subparsers(dest="command", required=True)

    install = subcommands.add_parser("install", help="Install voice-layer skills for Claude Code and/or Codex.")
    add_common_agent_arg(install)
    install.add_argument(
        "--mode",
        choices=("copy", "symlink"),
        default="copy",
        help="Copy skills or symlink them to this checkout.",
    )
    add_common_profile_arg(install)
    install.add_argument("--skip-profile", action="store_true", help="Do not create a profile template.")
    install.add_argument("--backup-existing", action="store_true", help="Move existing unmanaged skill directories aside before installing.")
    add_common_mutation_args(install)

    uninstall = subcommands.add_parser("uninstall", help="Remove installed voice-layer skill links or managed copies.")
    add_common_agent_arg(uninstall)
    add_common_profile_arg(uninstall)
    add_common_mutation_args(uninstall)

    purge = subcommands.add_parser("purge", help="Remove skill installs and delete local voice-layer profile data.")
    add_common_agent_arg(purge)
    add_common_profile_arg(purge)
    purge.add_argument("--yes", action="store_true", help="Confirm destructive profile deletion.")
    add_common_mutation_args(purge)

    doctor_parser = subcommands.add_parser("doctor", help="Show install status and next steps.")
    add_common_agent_arg(doctor_parser)
    add_common_profile_arg(doctor_parser)

    validate = subcommands.add_parser("validate-profile", help="Validate a voice-layer profile.")
    add_common_profile_arg(validate)
    validate.add_argument("profile", nargs="?", help="Optional profile path. Defaults to the configured voice-layer profile.")
    validate.add_argument("--quiet", action="store_true", help="Only print validation failures.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    explicit_profile = getattr(args, "profile", None)
    profile = Path(explicit_profile).expanduser() if explicit_profile else profile_path(args.profile_path)

    if args.command == "doctor":
        return doctor(args.agent, profile)

    if args.command == "validate-profile":
        return validate_profile_command(profile, args.quiet)

    if args.command == "uninstall":
        for skill_name in SKILL_NAMES:
            for _agent_kind, base_target, skills in target_specs(args.agent):
                source = skills / skill_name
                uninstall_one(source, base_target / skill_name, args.force, args.dry_run)
        print(f"keep profile: {profile}")
        print("done")
        return 0

    if args.command == "purge":
        confirm_purge(profile, args.yes or args.dry_run)
        for skill_name in SKILL_NAMES:
            for _agent_kind, base_target, skills in target_specs(args.agent):
                source = skills / skill_name
                uninstall_one(source, base_target / skill_name, args.force, args.dry_run)
        purge_profile(profile, args.dry_run)
        print("done")
        return 0

    for skill_name in SKILL_NAMES:
        for _agent_kind, base_target, skills in target_specs(args.agent):
            source = skills / skill_name
            if not source.exists():
                raise SystemExit(f"missing skill source: {source}")
            install_one(
                source,
                base_target / skill_name,
                args.mode,
                args.force,
                args.backup_existing,
                args.dry_run,
            )
    if not args.skip_profile:
        ensure_profile(profile, args.dry_run)
    print("next:")
    print("  Run 'voice-layer doctor --agent both' to verify skill installation.")
    print("  Ask your agent: Use $calibrate-my-voice to build my local voice profile from pasted samples.")
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
