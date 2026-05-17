#!/usr/bin/env python3
"""Run deterministic checks against synthetic voice-layer examples."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
EVALS = EXAMPLES / "evals"
TEXT_BLOCK_RE = re.compile(r"```text\n(?P<body>.*?)\n```", re.DOTALL)
COMMAND_WORD_RE = re.compile(
    r"\b(?:npm|pnpm|yarn|bun|python3?|pytest|uv|node|deno|go|cargo|git|make)\b"
)
COMMAND_ARGUMENT_RE = re.compile(r"[\w./:@=+-]+")


@dataclass
class Failure:
    case: str
    path: str
    message: str


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def phrase_count(text: str, phrases: list[str]) -> int:
    normalized = normalize(text)
    return sum(normalized.count(phrase.lower()) for phrase in phrases)


def decorative_dash_count(text: str) -> int:
    count = text.count("—") + text.count("–")
    for line in text.splitlines():
        start = 0
        while True:
            index = line.find(" -- ", start)
            if index == -1:
                break
            before = line[:index]
            after = line[index + 4 :].lstrip()
            if not (COMMAND_WORD_RE.search(before) and COMMAND_ARGUMENT_RE.match(after)):
                count += 1
            start = index + 4
        count += line.count(" - ")
    return count


def extract_draft(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = TEXT_BLOCK_RE.search(text)
    if not match:
        raise AssertionError(f"{path} has no fenced text draft")
    return match.group("body")


def check_required_any(case: str, path: str, draft: str, groups: list[list[str]]) -> list[Failure]:
    normalized = normalize(draft)
    failures: list[Failure] = []
    for group in groups:
        if not any(option.lower() in normalized for option in group):
            failures.append(Failure(case, path, f"missing one of: {', '.join(group)}"))
    return failures


def check_required_all(case: str, path: str, draft: str, phrases: list[str]) -> list[Failure]:
    normalized = normalize(draft)
    return [
        Failure(case, path, f"missing required phrase: {phrase}")
        for phrase in phrases
        if phrase.lower() not in normalized
    ]


def check_forbidden(case: str, path: str, draft: str, phrases: list[str]) -> list[Failure]:
    normalized = normalize(draft)
    return [
        Failure(case, path, f"contains forbidden phrase: {phrase}")
        for phrase in phrases
        if phrase.lower() in normalized
    ]


def run_case(path: Path) -> list[Failure]:
    data = json.loads(path.read_text(encoding="utf-8"))
    case = data["name"]
    source = (EXAMPLES / data["input"]).read_text(encoding="utf-8")
    source_tells = phrase_count(source, data.get("ai_tell_phrases", []))
    failures: list[Failure] = []

    for output in data["outputs"]:
        output_path = EXAMPLES / output["path"]
        draft = extract_draft(output_path)
        rel = str(output_path.relative_to(ROOT))
        draft_tells = phrase_count(draft, data.get("ai_tell_phrases", []))

        if draft_tells >= source_tells:
            failures.append(
                Failure(
                    case,
                    rel,
                    f"AI-tell count did not decrease ({draft_tells} >= {source_tells})",
                )
            )

        failures.extend(check_required_any(case, rel, draft, data.get("common_required_any", [])))
        failures.extend(check_forbidden(case, rel, draft, data.get("common_forbidden", [])))
        failures.extend(check_required_all(case, rel, draft, output.get("required_all", [])))
        failures.extend(check_forbidden(case, rel, draft, output.get("forbidden", [])))

        max_em_dash = output.get("max_em_dash")
        if max_em_dash is not None and draft.count("—") > max_em_dash:
            failures.append(
                Failure(case, rel, f"too many em dashes: {draft.count('—')} > {max_em_dash}")
            )

        max_decorative_dashes = output.get("max_decorative_dashes", max_em_dash)
        if max_decorative_dashes is not None:
            dash_count = decorative_dash_count(draft)
            if dash_count > max_decorative_dashes:
                failures.append(
                    Failure(
                        case,
                        rel,
                        f"too many decorative dashes: {dash_count} > {max_decorative_dashes}",
                    )
                )

    return failures


def main() -> int:
    failures: list[Failure] = []
    for case_path in sorted(EVALS.glob("*.json")):
        failures.extend(run_case(case_path))

    if failures:
        print("example evals failed", file=sys.stderr)
        for failure in failures:
            print(f"- {failure.case} {failure.path}: {failure.message}", file=sys.stderr)
        return 1

    print("example evals passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
