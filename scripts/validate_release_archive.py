#!/usr/bin/env python3
"""Build and validate a release archive from a git tree."""

from __future__ import annotations

import argparse
import io
import subprocess
import sys
import tarfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREFIX = "voice-layer-0.1.0/"

REQUIRED_PATHS = {
    ".agents/plugins/marketplace.json",
    ".claude-plugin/marketplace.json",
    ".github/workflows/ci.yml",
    "AI_TELLS.md",
    "CHANGELOG.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "NOTICE",
    "PRIVACY.md",
    "README.md",
    "SECURITY.md",
    "VOICE_PROFILE_SPEC.md",
    "assets/brand/demo-thumbnail.png",
    "assets/brand/logo.svg",
    "assets/brand/prompts.md",
    "assets/brand/readme-hero.svg",
    "assets/brand/social-preview.png",
    "assets/demo/voice-layer-demo.gif",
    "core/README.md",
    "core/profile/schema.json",
    "docs/install.md",
    "docs/release-audit.md",
    "docs/release-checklist.md",
    "docs/support-matrix.md",
    "evals/behavior/scenarios.json",
    "examples/README.md",
    "install.sh",
    "packages/claude-code/.claude-plugin/plugin.json",
    "packages/codex/.codex-plugin/plugin.json",
    "packaging/homebrew/README.md",
    "packaging/homebrew/voice-layer.rb",
    "packaging/homebrew/voice-layer.public.rb",
    "pyproject.toml",
    "scripts/check_no_silent_telemetry.py",
    "scripts/evaluate_behavior.py",
    "scripts/evaluate_examples.py",
    "scripts/install.py",
    "scripts/sync_core.py",
    "scripts/validate_profile.py",
    "scripts/validate_release_archive.py",
    "scripts/validate_repo.py",
    "tests/test_repo.py",
    "tests/fixtures/profiles/valid-profile.md",
    "voice-layer",
}

FORBIDDEN_EXACT_NAMES = {
    ".DS_Store",
    "voice-profile.md",
}

FORBIDDEN_PATH_PARTS = {
    ".claude",
    "__pycache__",
}

FORBIDDEN_SUFFIXES = {
    ".mov",
    ".mp4",
    ".pyc",
}

FORBIDDEN_TEXT = {
    "/" + "Users" + "/",
    "yuval" + ".meiri",
    "Datadog" + " Inc",
}


@dataclass(frozen=True)
class Finding:
    detail: str


def run_git_archive(tree: str, prefix: str) -> bytes:
    try:
        proc = subprocess.run(
            ["git", "archive", "--format=tar", f"--prefix={prefix}", tree],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"git archive failed for {tree!r}: {stderr}") from exc
    return proc.stdout


def strip_prefix(name: str, prefix: str) -> str:
    if not name.startswith(prefix):
        return name
    return name[len(prefix) :]


def is_binary(data: bytes) -> bool:
    return b"\0" in data


def check_path(path: str) -> list[Finding]:
    findings: list[Finding] = []
    parts = [part for part in path.split("/") if part]
    name = parts[-1] if parts else path
    if name in FORBIDDEN_EXACT_NAMES:
        findings.append(Finding(f"forbidden release file name: {path}"))
    if any(part in FORBIDDEN_PATH_PARTS for part in parts):
        findings.append(Finding(f"forbidden release path component: {path}"))
    if any(name.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES):
        findings.append(Finding(f"forbidden release file suffix: {path}"))
    if "command-message" in name:
        findings.append(Finding(f"private session export included: {path}"))
    if path.startswith("evals/behavior/runs/") and path != "evals/behavior/runs/README.md":
        findings.append(Finding(f"private behavior run artifact included: {path}"))
    return findings


def check_text(path: str, data: bytes) -> list[Finding]:
    if is_binary(data):
        return []
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return []
    return [
        Finding(f"{path}: forbidden private/local text marker: {marker}")
        for marker in sorted(FORBIDDEN_TEXT)
        if marker in text
    ]


def validate_archive(data: bytes, prefix: str) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[str] = set()
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            path = strip_prefix(member.name, prefix)
            seen.add(path)
            findings.extend(check_path(path))
            file_obj = archive.extractfile(member)
            if file_obj is None:
                continue
            findings.extend(check_text(path, file_obj.read()))

    missing = sorted(REQUIRED_PATHS - seen)
    findings.extend(Finding(f"required release file missing: {path}") for path in missing)
    return findings


def write_archive(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tree", default="HEAD", help="Git tree-ish to archive. Default: HEAD.")
    parser.add_argument("--prefix", default=DEFAULT_PREFIX, help="Archive path prefix.")
    parser.add_argument("--output", type=Path, help="Optional path to write the validated tar archive.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        data = run_git_archive(args.tree, args.prefix)
    except RuntimeError as exc:
        print(f"release archive validation failed: {exc}", file=sys.stderr)
        return 1

    findings = validate_archive(data, args.prefix)
    if findings:
        print("release archive validation failed", file=sys.stderr)
        for finding in findings:
            print(f"- {finding.detail}", file=sys.stderr)
        return 1

    if args.output:
        write_archive(args.output, data)
        print(f"release archive validation passed: wrote {args.output}")
    else:
        print("release archive validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
