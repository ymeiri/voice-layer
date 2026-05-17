#!/usr/bin/env python3
"""Sync canonical voice-layer core files into packaged skills."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE_SKILLS = ROOT / "core" / "skills"
CORE_REFERENCES = ROOT / "core" / "references"
CORE_PROFILE = ROOT / "core" / "profile"
CORE_SCRIPTS = ROOT / "core" / "scripts"
PACKAGE_ROOTS = (
    ROOT / "packages" / "claude-code",
    ROOT / "packages" / "codex",
)
SKILL_NAMES = ("write-in-my-voice", "calibrate-my-voice")

MAPPED_FILES = (
    (
        "profile contract",
        CORE_REFERENCES / "profile-contract.md",
        tuple((name, Path("references/profile-contract.md")) for name in SKILL_NAMES),
    ),
    (
        "profile template",
        CORE_PROFILE / "voice-profile.template.md",
        tuple((name, Path("assets/voice-profile.template.md")) for name in SKILL_NAMES),
    ),
    (
        "source menu",
        CORE_REFERENCES / "source-menu.md",
        (("calibrate-my-voice", Path("references/source-menu.md")),),
    ),
    (
        "source adapters",
        CORE_REFERENCES / "source-adapters.md",
        (("calibrate-my-voice", Path("references/source-adapters.md")),),
    ),
    (
        "AI tells",
        CORE_REFERENCES / "ai-tells.md",
        (("write-in-my-voice", Path("references/ai-tells.md")),),
    ),
    (
        "channel conventions",
        CORE_REFERENCES / "channel-conventions.md",
        (("write-in-my-voice", Path("references/channel-conventions.md")),),
    ),
    (
        "git collector",
        CORE_SCRIPTS / "collect_git_samples.py",
        (("calibrate-my-voice", Path("scripts/collect_git_samples.py")),),
    ),
)


def normalize_body(text: str) -> str:
    text = text.replace("\r\n", "\n")
    return text.rstrip("\n") + "\n"


def split_skill(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path} missing YAML frontmatter")
    try:
        _, raw_frontmatter, body = text.split("---\n", 2)
    except ValueError as exc:
        raise ValueError(f"{path} has malformed YAML frontmatter") from exc
    if body.startswith("\n"):
        body = body[1:]
    return f"---\n{raw_frontmatter}---\n", normalize_body(body)


def read_core_body(path: Path) -> str:
    body = path.read_text(encoding="utf-8")
    if body.startswith("---\n"):
        raise ValueError(f"{path} must contain the skill body only, not YAML frontmatter")
    return normalize_body(body)


def package_skill_path(package_root: Path, skill_name: str) -> Path:
    return package_root / "skills" / skill_name / "SKILL.md"


def package_resource_path(package_root: Path, skill_name: str, relative_path: Path) -> Path:
    return package_root / "skills" / skill_name / relative_path


def check_sync() -> list[str]:
    errors: list[str] = []
    for skill_name in SKILL_NAMES:
        core_path = CORE_SKILLS / f"{skill_name}.md"
        if not core_path.exists():
            errors.append(f"missing canonical skill body: {core_path}")
            continue
        for package_root in PACKAGE_ROOTS:
            package_path = package_skill_path(package_root, skill_name)
            if not package_path.exists():
                errors.append(f"missing packaged skill: {package_path}")
                continue
            try:
                core_body = read_core_body(core_path)
                _, package_body = split_skill(package_path)
            except ValueError as exc:
                errors.append(str(exc))
                continue
            if core_body != package_body:
                errors.append(f"{package_path.relative_to(ROOT)} body differs from {core_path.relative_to(ROOT)}")
    errors.extend(check_mapped_files())
    return errors


def check_mapped_files() -> list[str]:
    errors: list[str] = []
    for label, core_path, targets in MAPPED_FILES:
        if not core_path.exists():
            errors.append(f"missing canonical {label}: {core_path}")
            continue
        core_text = normalize_body(core_path.read_text(encoding="utf-8"))
        for package_root in PACKAGE_ROOTS:
            for skill_name, relative_path in targets:
                package_path = package_resource_path(package_root, skill_name, relative_path)
                if not package_path.exists():
                    errors.append(f"missing packaged {label}: {package_path}")
                    continue
                package_text = normalize_body(package_path.read_text(encoding="utf-8"))
                if core_text != package_text:
                    errors.append(f"{package_path.relative_to(ROOT)} differs from {core_path.relative_to(ROOT)}")
    return errors


def write_skill_bodies() -> list[str]:
    errors: list[str] = []
    for skill_name in SKILL_NAMES:
        core_path = CORE_SKILLS / f"{skill_name}.md"
        if not core_path.exists():
            errors.append(f"missing canonical skill body: {core_path}")
            continue
        for package_root in PACKAGE_ROOTS:
            package_path = package_skill_path(package_root, skill_name)
            if not package_path.exists():
                errors.append(f"missing packaged skill frontmatter source: {package_path}")
                continue
            try:
                core_body = read_core_body(core_path)
                frontmatter, _ = split_skill(package_path)
            except ValueError as exc:
                errors.append(str(exc))
                continue
            package_path.parent.mkdir(parents=True, exist_ok=True)
            package_path.write_text(f"{frontmatter}\n{core_body}", encoding="utf-8")
            print(f"updated: {package_path.relative_to(ROOT)}")
    return errors


def write_shared_files() -> list[str]:
    errors: list[str] = []
    for label, core_path, targets in MAPPED_FILES:
        if not core_path.exists():
            errors.append(f"missing canonical {label}: {core_path}")
            continue
        core_text = normalize_body(core_path.read_text(encoding="utf-8"))
        for package_root in PACKAGE_ROOTS:
            for skill_name, relative_path in targets:
                package_path = package_resource_path(package_root, skill_name, relative_path)
                package_path.parent.mkdir(parents=True, exist_ok=True)
                package_path.write_text(core_text, encoding="utf-8")
                print(f"updated: {package_path.relative_to(ROOT)}")
    return errors


def write_packages() -> list[str]:
    return write_skill_bodies() + write_shared_files()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="Check that packaged core files match core.")
    group.add_argument("--write", action="store_true", help="Rewrite packaged core files from core.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.write:
        errors = write_packages()
    else:
        errors = check_sync()

    if errors:
        print("core sync failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("core sync passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
