#!/usr/bin/env python3
"""Guard executable voice-layer code against silent network or telemetry paths."""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

NETWORK_IMPORT_ROOTS = {
    "aiohttp",
    "ftplib",
    "grpc",
    "http",
    "httpx",
    "imaplib",
    "nntplib",
    "poplib",
    "requests",
    "smtplib",
    "socket",
    "ssl",
    "telnetlib",
    "urllib",
    "urllib3",
    "websocket",
    "websockets",
}

TELEMETRY_IMPORT_ROOTS = {
    "amplitude",
    "analytics",
    "datadog",
    "ddtrace",
    "mixpanel",
    "opentelemetry",
    "posthog",
    "segment",
    "sentry_sdk",
}

SHELL_NETWORK_COMMANDS = {
    "curl",
    "ftp",
    "nc",
    "ncat",
    "netcat",
    "rsync",
    "scp",
    "sftp",
    "socat",
    "ssh",
    "telnet",
    "wget",
}

FORBIDDEN_IMPORT_ROOTS = NETWORK_IMPORT_ROOTS | TELEMETRY_IMPORT_ROOTS
FORBIDDEN_DEPENDENCIES = FORBIDDEN_IMPORT_ROOTS | {
    "analytics-python",
    "sentry-sdk",
}
SHELL_COMMAND_RE = re.compile(
    r"(?<![-\w])(" + "|".join(sorted(re.escape(command) for command in SHELL_NETWORK_COMMANDS)) + r")(?![-\w])"
)


@dataclass(frozen=True)
class Finding:
    path: Path
    detail: str


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def python_files() -> list[Path]:
    files = [
        *sorted((ROOT / "scripts").glob("*.py")),
        *sorted((ROOT / "core" / "scripts").glob("*.py")),
        *sorted((ROOT / "packages").glob("*/skills/*/scripts/*.py")),
    ]
    return [path for path in files if path.resolve() != Path(__file__).resolve()]


def shell_files() -> list[Path]:
    return [path for path in (ROOT / "voice-layer", ROOT / "install.sh") if path.exists()]


def import_root(name: str) -> str:
    return name.split(".", 1)[0]


def check_imports(path: Path, tree: ast.AST) -> list[Finding]:
    findings: list[Finding] = []
    for node in ast.walk(tree):
        imported: list[str] = []
        if isinstance(node, ast.Import):
            imported = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported = [node.module]
        for module in imported:
            root = import_root(module)
            if root in FORBIDDEN_IMPORT_ROOTS:
                findings.append(Finding(path, f"forbidden import: {module}"))
    return findings


def check_shell_literals(path: Path, tree: ast.AST) -> list[Finding]:
    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        match = SHELL_COMMAND_RE.search(node.value)
        if match:
            findings.append(Finding(path, f"network-capable shell command literal: {match.group(1)}"))
    return findings


def check_python_file(path: Path) -> list[Finding]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [Finding(path, f"cannot parse Python file: {exc}")]
    return [*check_imports(path, tree), *check_shell_literals(path, tree)]


def check_shell_file(path: Path) -> list[Finding]:
    text = path.read_text(encoding="utf-8")
    findings = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = SHELL_COMMAND_RE.search(stripped)
        if match:
            findings.append(Finding(path, f"line {line_number}: network-capable command: {match.group(1)}"))
    return findings


def normalized_dependency_name(raw: str) -> str:
    name = raw.split(";", 1)[0].split("[", 1)[0]
    return re.split(r"\s*(?:==|~=|!=|<=|>=|<|>)\s*", name, maxsplit=1)[0].strip().lower().replace("_", "-")


def check_pyproject() -> list[Finding]:
    path = ROOT / "pyproject.toml"
    findings: list[Finding] = []
    text = path.read_text(encoding="utf-8")
    for match in re.finditer(r"""["']([^"']+)["']""", text):
        dependency = match.group(1)
        name = normalized_dependency_name(dependency)
        if name in FORBIDDEN_DEPENDENCIES:
            findings.append(Finding(path, f"forbidden dependency: {dependency}"))
    return findings


def main() -> int:
    findings: list[Finding] = []
    scanned = 0
    for path in python_files():
        scanned += 1
        findings.extend(check_python_file(path))
    for path in shell_files():
        scanned += 1
        findings.extend(check_shell_file(path))
    findings.extend(check_pyproject())

    if findings:
        print("silent telemetry guard failed", file=sys.stderr)
        for finding in findings:
            print(f"- {rel(finding.path)}: {finding.detail}", file=sys.stderr)
        print(
            "\nIf a future feature needs network access, make it explicit, opt-in, "
            "documented, and update this guard in the same change.",
            file=sys.stderr,
        )
        return 1

    print(f"silent telemetry guard passed ({scanned} executable files checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
