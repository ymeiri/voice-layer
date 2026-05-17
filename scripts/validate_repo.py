#!/usr/bin/env python3
"""Validate repository structure without third-party dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from validate_profile import (
    ALLOWED_RETENTION,
    REQUIRED_FRONTMATTER,
    REQUIRED_HEADINGS,
    SOURCE_REQUIRED_KEYS,
    SUPPORTED_SCHEMA_VERSIONS,
    VALID_CONFIDENCE,
    VALID_PROFILE_SUBJECTS,
    validate_profile,
)


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_PACKAGE = ROOT / "packages" / "claude-code"
CODEX_PACKAGE = ROOT / "packages" / "codex"
PACKAGE_ROOTS = (CLAUDE_PACKAGE, CODEX_PACKAGE)
SKILLS = CODEX_PACKAGE / "skills"
CORE_SKILLS = ROOT / "core" / "skills"
CORE_REFERENCES = ROOT / "core" / "references"
CORE_PROFILE = ROOT / "core" / "profile"
CORE_SCRIPTS = ROOT / "core" / "scripts"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

MAPPED_CORE_FILES = (
    (
        CORE_REFERENCES / "profile-contract.md",
        tuple((name, Path("references/profile-contract.md")) for name in ("write-in-my-voice", "calibrate-my-voice")),
    ),
    (
        CORE_PROFILE / "voice-profile.template.md",
        tuple((name, Path("assets/voice-profile.template.md")) for name in ("write-in-my-voice", "calibrate-my-voice")),
    ),
    (
        CORE_REFERENCES / "source-menu.md",
        (("calibrate-my-voice", Path("references/source-menu.md")),),
    ),
    (
        CORE_REFERENCES / "source-adapters.md",
        (("calibrate-my-voice", Path("references/source-adapters.md")),),
    ),
    (
        CORE_REFERENCES / "ai-tells.md",
        (("write-in-my-voice", Path("references/ai-tells.md")),),
    ),
    (
        CORE_REFERENCES / "channel-conventions.md",
        (("write-in-my-voice", Path("references/channel-conventions.md")),),
    ),
    (
        CORE_SCRIPTS / "collect_git_samples.py",
        (("calibrate-my-voice", Path("scripts/collect_git_samples.py")),),
    ),
)


def read_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"{path} missing YAML frontmatter")
    try:
        _, raw, body = text.split("---\n", 2)
    except ValueError as exc:
        raise AssertionError(f"{path} has malformed frontmatter") from exc
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.lstrip().startswith("- "):
            continue
        if ":" not in line:
            raise AssertionError(f"{path} has unsupported frontmatter line: {line}")
        key, value = line.split(":", 1)
        raw_value = value.strip()
        if raw_value and raw_value[0] not in ("'", '"') and ": " in raw_value:
            raise AssertionError(f"{path} has unquoted frontmatter value containing ': ': {line}")
        data[key.strip()] = raw_value.strip('"').strip("'")
    return data, body


def normalized_skill_body(body: str) -> str:
    body = body.replace("\r\n", "\n")
    if body.startswith("\n"):
        body = body[1:]
    return body.rstrip("\n") + "\n"


def first_yaml_block_keys(text: str, path: Path) -> set[str]:
    match = re.search(r"```yaml\n(.*?)```", text, re.DOTALL)
    if not match:
        raise AssertionError(f"{path} missing YAML schema block")
    return set(re.findall(r"(?m)^([A-Za-z_][A-Za-z0-9_]*)\s*:", match.group(1)))


def validate_skill(skill_dir: Path) -> None:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        raise AssertionError(f"missing {skill_file}")
    frontmatter, body = read_frontmatter(skill_file)
    name = frontmatter.get("name")
    description = frontmatter.get("description")
    if name != skill_dir.name:
        raise AssertionError(f"{skill_file}: name {name!r} must match directory {skill_dir.name!r}")
    if not name or not NAME_RE.match(name) or len(name) > 64:
        raise AssertionError(f"{skill_file}: invalid skill name")
    if not description or len(description) > 1024:
        raise AssertionError(f"{skill_file}: description missing or too long")
    if not body.strip():
        raise AssertionError(f"{skill_file}: body is empty")
    for required in ("agents/openai.yaml", "evals/evals.json"):
        if not (skill_dir / required).exists():
            raise AssertionError(f"{skill_dir}: missing {required}")


def validate_plugin_manifest() -> None:
    codex_manifest = CODEX_PACKAGE / ".codex-plugin" / "plugin.json"
    codex = json.loads(codex_manifest.read_text(encoding="utf-8"))
    if codex.get("name") != "voice-layer":
        raise AssertionError("Codex plugin name must be voice-layer")
    if codex.get("skills") != "./skills/":
        raise AssertionError("Codex plugin skills path must be ./skills/")
    if codex.get("license") != "MIT":
        raise AssertionError("Codex plugin license must be MIT")

    claude_manifest = CLAUDE_PACKAGE / ".claude-plugin" / "plugin.json"
    claude = json.loads(claude_manifest.read_text(encoding="utf-8"))
    if claude.get("name") != "voice-layer":
        raise AssertionError("Claude plugin name must be voice-layer")
    if claude.get("license") != "MIT":
        raise AssertionError("Claude plugin license must be MIT")

def validate_package_layout() -> None:
    for package_root in PACKAGE_ROOTS:
        if not (package_root / "assets" / "voice-layer.svg").exists():
            raise AssertionError(f"{package_root} missing assets/voice-layer.svg")
        if not (package_root / "skills").is_dir():
            raise AssertionError(f"{package_root} missing skills directory")
    if not (CLAUDE_PACKAGE / ".claude-plugin" / "plugin.json").exists():
        raise AssertionError("Claude package missing .claude-plugin/plugin.json")
    if (CLAUDE_PACKAGE / ".codex-plugin").exists():
        raise AssertionError("Claude package should not include .codex-plugin")
    if not (CODEX_PACKAGE / ".codex-plugin" / "plugin.json").exists():
        raise AssertionError("Codex package missing .codex-plugin/plugin.json")
    if (CODEX_PACKAGE / ".claude-plugin").exists():
        raise AssertionError("Codex package should not include .claude-plugin")


def validate_core_sync() -> None:
    sync_script = ROOT / "scripts" / "sync_core.py"
    if not sync_script.exists():
        raise AssertionError("missing scripts/sync_core.py")

    for package_root in PACKAGE_ROOTS:
        skills = package_root / "skills"
        if not skills.exists():
            raise AssertionError(f"missing package skills directory: {skills}")
        for skill_dir in sorted(skills.iterdir()):
            if not skill_dir.is_dir():
                continue
            core_path = CORE_SKILLS / f"{skill_dir.name}.md"
            package_path = skill_dir / "SKILL.md"
            if not core_path.exists():
                raise AssertionError(f"missing canonical skill body: {core_path}")
            core_body = core_path.read_text(encoding="utf-8")
            if core_body.startswith("---\n"):
                raise AssertionError(f"{core_path} must not contain YAML frontmatter")
            _, package_body = read_frontmatter(package_path)
            if normalized_skill_body(core_body) != normalized_skill_body(package_body):
                raise AssertionError(f"{package_path} body differs from {core_path}")

    for core_path, targets in MAPPED_CORE_FILES:
        if not core_path.exists():
            raise AssertionError(f"missing canonical core file: {core_path}")
        core_text = normalized_skill_body(core_path.read_text(encoding="utf-8"))
        for package_root in PACKAGE_ROOTS:
            for skill_name, relative_path in targets:
                package_path = package_root / "skills" / skill_name / relative_path
                if not package_path.exists():
                    raise AssertionError(f"missing packaged core file: {package_path}")
                package_text = normalized_skill_body(package_path.read_text(encoding="utf-8"))
                if package_text != core_text:
                    raise AssertionError(f"{package_path} differs from {core_path}")


def validate_marketplaces() -> None:
    codex_marketplace = ROOT / ".agents" / "plugins" / "marketplace.json"
    codex = json.loads(codex_marketplace.read_text(encoding="utf-8"))
    if codex.get("name") != "voice-layer":
        raise AssertionError("Codex marketplace name must be voice-layer")
    codex_plugins = codex.get("plugins", [])
    if not codex_plugins or codex_plugins[0].get("source", {}).get("path") != "./packages/codex":
        raise AssertionError("Codex marketplace must point at ./packages/codex")

    claude_marketplace = ROOT / ".claude-plugin" / "marketplace.json"
    claude = json.loads(claude_marketplace.read_text(encoding="utf-8"))
    if claude.get("name") != "voice-layer":
        raise AssertionError("Claude marketplace name must be voice-layer")
    claude_plugins = claude.get("plugins", [])
    if not claude_plugins or claude_plugins[0].get("source") != "./packages/claude-code":
        raise AssertionError("Claude marketplace must point at ./packages/claude-code")


def validate_cli_entrypoint() -> None:
    entrypoint = ROOT / "voice-layer"
    if not entrypoint.exists():
        raise AssertionError("missing voice-layer CLI entrypoint")
    text = entrypoint.read_text(encoding="utf-8")
    if "scripts/install.py" not in text:
        raise AssertionError("voice-layer CLI entrypoint must delegate to scripts/install.py")
    if not (entrypoint.stat().st_mode & 0o111):
        raise AssertionError("voice-layer CLI entrypoint must be executable")


def validate_profile_template() -> None:
    for template in (
        SKILLS / "calibrate-my-voice" / "assets" / "voice-profile.template.md",
        SKILLS / "write-in-my-voice" / "assets" / "voice-profile.template.md",
    ):
        result = validate_profile(template)
        if result.errors:
            raise AssertionError(f"{template} profile validation failed: {result.errors}")
        frontmatter, body = read_frontmatter(template)
        missing = REQUIRED_FRONTMATTER - set(frontmatter)
        if missing:
            raise AssertionError(f"profile template missing keys: {sorted(missing)}")
        for heading in REQUIRED_HEADINGS:
            if heading not in body:
                raise AssertionError(f"profile template missing heading: {heading}")


def validate_profile_schema() -> None:
    schema_path = CORE_PROFILE / "schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    checks = (
        ("supported_schema_versions", sorted(SUPPORTED_SCHEMA_VERSIONS)),
        ("required_frontmatter", sorted(REQUIRED_FRONTMATTER)),
        ("valid_profile_subjects", sorted(VALID_PROFILE_SUBJECTS)),
        ("valid_confidence", sorted(VALID_CONFIDENCE)),
        ("source_required_keys", list(SOURCE_REQUIRED_KEYS)),
        ("allowed_retention", sorted(ALLOWED_RETENTION)),
        ("required_headings", list(REQUIRED_HEADINGS)),
    )
    for key, expected in checks:
        actual = schema.get(key)
        if isinstance(expected, list) and key not in ("source_required_keys", "required_headings"):
            actual = sorted(actual)
        if actual != expected:
            raise AssertionError(f"profile schema {key} does not match validator")


def validate_profile_contracts() -> None:
    for contract in (
        SKILLS / "calibrate-my-voice" / "references" / "profile-contract.md",
        SKILLS / "write-in-my-voice" / "references" / "profile-contract.md",
    ):
        text = contract.read_text(encoding="utf-8")
        schema_keys = first_yaml_block_keys(text, contract)
        missing = sorted(REQUIRED_FRONTMATTER - schema_keys)
        if missing:
            raise AssertionError(f"{contract} missing required profile keys: {missing}")
        missing_headings = sorted(heading for heading in REQUIRED_HEADINGS if heading not in text)
        if missing_headings:
            raise AssertionError(f"{contract} missing required headings: {missing_headings}")
        if "No approved examples." not in text:
            raise AssertionError(f"{contract} missing Examples privacy invariant")
        if "Optional:" in text:
            optional_text = text.split("Optional:", 1)[1]
            if "```yaml" in optional_text:
                optional_text = optional_text.split("```yaml", 1)[1].split("```", 1)[0]
            optional_keys = set(re.findall(r"(?m)^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:", optional_text))
            misplaced = sorted(REQUIRED_FRONTMATTER & optional_keys)
            if misplaced:
                raise AssertionError(
                    f"{contract} lists validator-required keys as optional: {misplaced}"
                )


def validate_calibration_source_menu() -> None:
    skill_dir = SKILLS / "calibrate-my-voice"
    source_menu = skill_dir / "references" / "source-menu.md"
    if not source_menu.exists():
        raise AssertionError("calibrate-my-voice missing references/source-menu.md")
    text = source_menu.read_text(encoding="utf-8")
    for phrase in (
        "Step 1: Discover available sources",
        "Build the menu from artifact types",
        "I will not read a source until you approve it",
        "Do not combine consent",
        "connectable",
        "Do not substitute local git commits",
        "Linear, Jira, Asana, Monday.com",
        "AI agent session history",
        "Assistant output is not the user's voice by default",
    ):
        if phrase not in text:
            raise AssertionError(f"source menu missing phrase: {phrase}")

    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    if "Read `references/source-menu.md` before the first user-facing calibration question." not in skill_text:
        raise AssertionError("calibrate-my-voice must instruct agents to read source-menu.md before calibration questions")

    adapters = (skill_dir / "references" / "source-adapters.md").read_text(encoding="utf-8")
    for phrase in (
        "AI agent sessions",
        "documentation-style calibration",
        "Record agent-session findings separately",
        "connect or enable",
        "lower-signal source",
    ):
        if phrase not in adapters:
            raise AssertionError(f"source adapters missing phrase: {phrase}")


def validate_voice_layer_skill_behavior() -> None:
    rewrite = (SKILLS / "write-in-my-voice" / "SKILL.md").read_text(encoding="utf-8")
    for phrase in (
        "Voice-layer model",
        "Facts, safety, and consent",
        "requested vibe",
        "Culture is not a costume",
        "model-shaped punctuation",
    ):
        if phrase not in rewrite:
            raise AssertionError(f"write-in-my-voice skill missing phrase: {phrase}")

    calibrate = (SKILLS / "calibrate-my-voice" / "SKILL.md").read_text(encoding="utf-8")
    for phrase in (
        "agent sessions",
        "documentation style",
        "assistant output",
        "punctuation texture",
        "agent-session signals",
        "validate_profile.py",
    ):
        if phrase not in calibrate:
            raise AssertionError(f"calibrate-my-voice skill missing phrase: {phrase}")


def validate_public_support_docs() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for phrase in (
        "docs/support-matrix.md",
        "docs/implementation-roadmap.md",
        "Current packaged support is Claude Code and Codex",
        "Cursor and other agents are not claimed",
        "supported until their package and invocation behavior are verified",
    ):
        if phrase not in readme:
            raise AssertionError(f"README missing support boundary phrase: {phrase}")

    support = (ROOT / "docs" / "support-matrix.md").read_text(encoding="utf-8")
    for phrase in (
        "Claude Code direct skills",
        "Codex direct skills",
        "Cursor | Not supported",
        "Do not claim native vendor integrations",
    ):
        if phrase not in support:
            raise AssertionError(f"support matrix missing phrase: {phrase}")

    roadmap = (ROOT / "docs" / "implementation-roadmap.md").read_text(encoding="utf-8")
    for phrase in (
        "Definition Of Complete",
        "Phase 2: Core And Adapter Split",
        "scripts/sync_core.py",
        "packages/",
        "Profile Validation And Activation",
        "Behavioral Evals",
    ):
        if phrase not in roadmap:
            raise AssertionError(f"implementation roadmap missing phrase: {phrase}")


def validate_public_profile_spec() -> None:
    path = ROOT / "VOICE_PROFILE_SPEC.md"
    spec = path.read_text(encoding="utf-8")
    missing = sorted(REQUIRED_FRONTMATTER - first_yaml_block_keys(spec, path))
    if missing:
        raise AssertionError(f"VOICE_PROFILE_SPEC.md missing required profile keys: {missing}")
    missing_headings = sorted(heading for heading in REQUIRED_HEADINGS if heading not in spec)
    if missing_headings:
        raise AssertionError(f"VOICE_PROFILE_SPEC.md missing required headings: {missing_headings}")


def validate_evals(skill_dir: Path) -> None:
    path = skill_dir / "evals" / "evals.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("skill_name") != skill_dir.name:
        raise AssertionError(f"{path}: skill_name mismatch")
    evals = data.get("evals")
    if not isinstance(evals, list) or not evals:
        raise AssertionError(f"{path}: evals must be a non-empty list")
    for item in evals:
        if not item.get("prompt") or not item.get("expected_output"):
            raise AssertionError(f"{path}: each eval needs prompt and expected_output")


def main() -> int:
    for package_root in PACKAGE_ROOTS:
        for skill_dir in sorted((package_root / "skills").iterdir()):
            if skill_dir.is_dir():
                validate_skill(skill_dir)
                validate_evals(skill_dir)
    validate_core_sync()
    validate_package_layout()
    validate_plugin_manifest()
    validate_marketplaces()
    validate_cli_entrypoint()
    validate_profile_schema()
    validate_profile_template()
    validate_profile_contracts()
    validate_calibration_source_menu()
    validate_voice_layer_skill_behavior()
    validate_public_support_docs()
    validate_public_profile_spec()
    print("validation passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
