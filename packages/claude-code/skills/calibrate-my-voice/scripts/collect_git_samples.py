#!/usr/bin/env python3
"""Collect user-authored git commit messages for voice calibration."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def git(repo: Path, args: list[str]) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.stdout


def default_author(repo: Path) -> str | None:
    try:
        email = git(repo, ["config", "--get", "user.email"]).strip()
    except subprocess.CalledProcessError:
        return None
    return email or None


def collect(repo: Path, limit: int, author: str | None) -> str:
    cmd = [
        "log",
        "--no-merges",
        f"-{limit}",
        "--format=---COMMIT %H | %ad---%n%s%n%n%b",
        "--date=short",
    ]
    if author:
        cmd.insert(1, f"--author={author}")
    output = git(repo, cmd)
    blocks = []
    for block in output.split("---COMMIT "):
        block = block.strip()
        if not block:
            continue
        lowered = block.lower()
        if lowered.startswith("revert ") or "\nrevert " in lowered[:120]:
            continue
        blocks.append("---COMMIT " + block)
    return "\n\n".join(blocks).strip() + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Git repository path.")
    parser.add_argument("--limit", type=int, default=100, help="Maximum commits to inspect.")
    parser.add_argument("--author", help="Author filter. Defaults to git config user.email.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    repo = Path(args.repo).expanduser().resolve()
    author = args.author if args.author is not None else default_author(repo)
    try:
        print(collect(repo, args.limit, author), end="")
    except subprocess.CalledProcessError as exc:
        print(exc.stderr.strip() or str(exc), file=sys.stderr)
        return exc.returncode or 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
