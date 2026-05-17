#!/usr/bin/env python3
"""Validate a voice-layer voice profile."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "core" / "profile" / "schema.json"


def load_schema(path: Path = SCHEMA_PATH) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


PROFILE_SCHEMA = load_schema()
CURRENT_SCHEMA_VERSION = str(PROFILE_SCHEMA["current_schema_version"])
SUPPORTED_SCHEMA_VERSIONS = set(PROFILE_SCHEMA["supported_schema_versions"])
REQUIRED_FRONTMATTER = set(PROFILE_SCHEMA["required_frontmatter"])
VALID_PROFILE_SUBJECTS = set(PROFILE_SCHEMA["valid_profile_subjects"])
VALID_CONFIDENCE = set(PROFILE_SCHEMA["valid_confidence"])
REQUIRED_HEADINGS = tuple(PROFILE_SCHEMA["required_headings"])
SOURCE_REQUIRED_KEYS = tuple(PROFILE_SCHEMA["source_required_keys"])
ALLOWED_RETENTION = set(PROFILE_SCHEMA["allowed_retention"])
PRIVACY_REQUIRED_KEYS = tuple(PROFILE_SCHEMA["privacy_required_keys"])
BLOCK_LIST_FRONTMATTER_KEYS = {"source_summary", "limitations"}
RAW_SAMPLE_RISK_PATTERNS = (
    re.compile(r"(?im)^raw samples?\s*:"),
    re.compile(r"(?im)^transcript\s*:"),
    re.compile(r"(?im)^verbatim\s+messages?\s*:"),
    re.compile(r"(?im)^message dump\s*:"),
    re.compile(r"(?i)BEGIN RAW"),
    re.compile(r"(?i)FULL EXPORT"),
)
EXACT_PHRASE_RE = re.compile(r'["“]([^"“”\n]{4,140})["”]')
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
EXACT_PHRASE_ALLOWED_HEADINGS = {
    "## Aversions",
    "## Examples",
    "## Calibration notes",
}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class ValidationResult:
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def parse_scalar(raw: str) -> str | bool | int:
    value = raw.strip()
    if value in ("true", "false"):
        return value == "true"
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def split_key_value(text: str, context: str) -> tuple[str, str]:
    if ":" not in text:
        raise ValueError(f"unsupported {context}: {text}")
    key, value = text.split(":", 1)
    return key.strip(), value.strip()


def require_list(data: dict[str, object], key: str) -> list[object]:
    value = data.setdefault(key, [])
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    return value


def require_map(data: dict[str, object], key: str) -> dict[str, object]:
    value = data.setdefault(key, {})
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be a map")
    return value


def parse_top_level_value(key: str, raw_value: str) -> tuple[object, str | None]:
    if raw_value == "":
        if key in BLOCK_LIST_FRONTMATTER_KEYS:
            return [], "list"
        return {}, "map"
    if raw_value == "[]":
        return [], "list"
    if raw_value.startswith("[") and raw_value.endswith("]"):
        raise ValueError(f"{key} uses unsupported inline list syntax; use [] or block list")
    return parse_scalar(raw_value), None


def parse_frontmatter(raw: str) -> dict[str, object]:
    """Parse the small YAML subset used by generated voice profiles."""

    data: dict[str, object] = {}
    current_list_key: str | None = None
    current_list_item: dict[str, object] | None = None
    current_map_key: str | None = None

    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - "):
            if current_list_key is None:
                raise ValueError(f"list item without list key: {line}")
            item_text = line[4:]
            if ":" not in item_text:
                require_list(data, current_list_key).append(parse_scalar(item_text))
                current_list_item = None
                current_map_key = None
                continue
            key, value = split_key_value(item_text, "list item")
            current_list_item = {key: parse_scalar(value)}
            require_list(data, current_list_key).append(current_list_item)
            current_map_key = None
            continue
        if line.startswith("    "):
            if current_list_item is None or ":" not in line:
                raise ValueError(f"unsupported nested line: {line}")
            key, value = split_key_value(line.strip(), "nested list item")
            current_list_item[key] = parse_scalar(value)
            continue
        if line.startswith("  "):
            if current_map_key is None or ":" not in line:
                raise ValueError(f"unsupported map line: {line}")
            key, value = split_key_value(line.strip(), "map line")
            require_map(data, current_map_key)[key] = parse_scalar(value)
            continue

        current_list_key = None
        current_list_item = None
        current_map_key = None
        key, raw_value = split_key_value(line, "frontmatter line")
        parsed_value, container = parse_top_level_value(key, raw_value)
        data[key] = parsed_value
        if container == "list":
            current_list_key = key
        elif container == "map":
            current_map_key = key

    return data


def read_profile(path: Path) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("profile must start with YAML frontmatter")
    try:
        _, raw_frontmatter, body = text.split("---\n", 2)
    except ValueError as exc:
        raise ValueError("profile has malformed frontmatter delimiters") from exc
    return parse_frontmatter(raw_frontmatter), body


def is_placeholder(data: dict[str, object], body: str) -> bool:
    limitations = data.get("limitations")
    if isinstance(limitations, list) and "Not calibrated yet." in limitations:
        return True
    return "Not calibrated yet." in body


def section_text(body: str, heading: str) -> str:
    start = body.find(heading)
    if start < 0:
        return ""
    rest = body[start + len(heading) :]
    match = re.search(r"\n## ", rest)
    if not match:
        return rest.strip()
    return rest[: match.start()].strip()


def iter_sections(body: str) -> list[tuple[str, list[tuple[int, str]]]]:
    sections: list[tuple[str, list[tuple[int, str]]]] = []
    heading: str | None = None
    lines: list[tuple[int, str]] = []
    for line_number, line in enumerate(body.splitlines(), start=1):
        if line.startswith("## "):
            if heading is not None:
                sections.append((heading, lines))
            heading = line.strip()
            lines = []
            continue
        if heading is not None:
            lines.append((line_number, line))
    if heading is not None:
        sections.append((heading, lines))
    return sections


def looks_like_exact_phrase(text: str) -> bool:
    phrase = text.strip()
    if len(phrase) < 8:
        return False
    if re.fullmatch(r"[A-Za-z0-9_.:/#-]+", phrase):
        return False
    return " " in phrase or bool(re.search(r"[.!?,;:]", phrase))


def exact_phrase_line_numbers(body: str) -> list[tuple[str, int]]:
    findings: list[tuple[str, int]] = []
    for heading, lines in iter_sections(body):
        if heading in EXACT_PHRASE_ALLOWED_HEADINGS:
            continue
        for line_number, line in lines:
            searchable = INLINE_CODE_RE.sub("", line)
            if any(looks_like_exact_phrase(match.group(1)) for match in EXACT_PHRASE_RE.finditer(searchable)):
                findings.append((heading, line_number))
    return findings


def validate_sources(data: dict[str, object], placeholder: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    source_summary = data.get("source_summary")
    if not isinstance(source_summary, list):
        errors.append("source_summary must be a list")
        return errors, warnings
    if not source_summary and not placeholder:
        errors.append("calibrated profiles must include at least one source_summary entry")
    for index, entry in enumerate(source_summary, start=1):
        if not isinstance(entry, dict):
            errors.append(f"source_summary[{index}] must be a map")
            continue
        for key in SOURCE_REQUIRED_KEYS:
            if key not in entry:
                errors.append(f"source_summary[{index}] missing {key}")
        retention = entry.get("retention")
        if retention not in ALLOWED_RETENTION:
            errors.append(
                f"source_summary[{index}] retention must be one of {sorted(ALLOWED_RETENTION)}"
            )
        sample_count = entry.get("sample_count")
        if not isinstance(sample_count, int) or sample_count < 0:
            errors.append(f"source_summary[{index}] sample_count must be a non-negative integer")
        elif sample_count == 0 and not placeholder:
            warnings.append(f"source_summary[{index}] sample_count is 0")
        for text_key in ("source", "scope", "date_range"):
            value = entry.get(text_key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"source_summary[{index}] {text_key} must be a non-empty string")
        if entry.get("date_range") in ("unknown", "", None):
            warnings.append(f"source_summary[{index}] date_range is unknown")
    return errors, warnings


def validate_privacy(data: dict[str, object], body: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    privacy = data.get("privacy")
    if not isinstance(privacy, dict):
        errors.append("privacy must be a map")
        return errors, warnings
    for key in PRIVACY_REQUIRED_KEYS:
        if key not in privacy:
            errors.append(f"privacy missing {key}")
        elif not isinstance(privacy[key], bool):
            errors.append(f"privacy.{key} must be true or false")
    if privacy.get("raw_samples_retained") is True:
        warnings.append("raw_samples_retained is true; verify this is explicitly approved")

    examples = section_text(body, "## Examples")
    if "## Examples" in body and privacy.get("approved_exact_examples") is not True:
        if examples.strip() != "No approved examples.":
            errors.append("Examples section contains content but approved_exact_examples is not true")
        phrase_findings = exact_phrase_line_numbers(body)
        if phrase_findings:
            locations = ", ".join(
                f"{heading} line {line_number}" for heading, line_number in phrase_findings[:3]
            )
            errors.append(
                "profile contains exact phrase-like text outside Examples "
                f"but approved_exact_examples is not true: {locations}"
            )

    for pattern in RAW_SAMPLE_RISK_PATTERNS:
        if pattern.search(body):
            errors.append(f"profile appears to contain raw sample material: {pattern.pattern}")
    for line_number, line in enumerate(body.splitlines(), start=1):
        stripped = line.strip()
        if len(stripped) > 500 and not stripped.startswith("|"):
            errors.append(f"line {line_number} is unusually long and may contain raw pasted text")
            break
    return errors, warnings


def validate_profile(path: Path) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        data, body = read_profile(path)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        return ValidationResult([str(exc)], [])

    missing = REQUIRED_FRONTMATTER - set(data)
    if missing:
        errors.append(f"missing frontmatter keys: {', '.join(sorted(missing))}")

    schema_version = data.get("schema_version")
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        errors.append(f"unsupported schema_version: {schema_version!r}")

    if data.get("profile_subject") not in VALID_PROFILE_SUBJECTS:
        errors.append(f"profile_subject must be one of {sorted(VALID_PROFILE_SUBJECTS)}")

    if data.get("confidence") not in VALID_CONFIDENCE:
        errors.append(f"confidence must be one of {sorted(VALID_CONFIDENCE)}")

    for key in ("profile_name", "language", "updated_at", "calibrated_by"):
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{key} must be a non-empty string")

    updated_at = data.get("updated_at")
    if isinstance(updated_at, str) and updated_at != "YYYY-MM-DD" and not DATE_RE.fullmatch(updated_at):
        errors.append("updated_at must use YYYY-MM-DD format")

    limitations = data.get("limitations")
    if not isinstance(limitations, list):
        errors.append("limitations must be a list")
    elif not limitations and not is_placeholder(data, body):
        warnings.append("limitations is empty; record source coverage gaps or write 'No known limitations.'")

    for heading in REQUIRED_HEADINGS:
        if heading not in body:
            errors.append(f"missing required heading: {heading}")

    placeholder = is_placeholder(data, body)
    source_errors, source_warnings = validate_sources(data, placeholder)
    errors.extend(source_errors)
    warnings.extend(source_warnings)

    privacy_errors, privacy_warnings = validate_privacy(data, body)
    errors.extend(privacy_errors)
    warnings.extend(privacy_warnings)

    if not placeholder:
        if data.get("calibrated_by") == "unset":
            errors.append("calibrated profiles must set calibrated_by")
        if data.get("updated_at") == "YYYY-MM-DD":
            errors.append("calibrated profiles must set updated_at")
        for heading in ("## Summary", "## Global voice", "## Calibration notes"):
            text = section_text(body, heading)
            if not text or "Not calibrated yet." in text:
                errors.append(f"calibrated profiles must populate {heading}")

    return ValidationResult(errors, warnings)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path, help="Path to voice-profile.md")
    parser.add_argument("--quiet", action="store_true", help="Only print errors and warnings.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    result = validate_profile(args.profile)
    for warning in result.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    if result.errors:
        print(f"profile validation failed: {args.profile}", file=sys.stderr)
        for error in result.errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if not args.quiet:
        print(f"profile validation passed: {args.profile}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
