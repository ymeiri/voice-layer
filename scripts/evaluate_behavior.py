#!/usr/bin/env python3
"""Validate behavioral eval scenarios and reference outputs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "evals" / "behavior" / "scenarios.json"
SUPPORTED_SCHEMA_VERSIONS = {"1.0"}
SUPPORTED_SKILLS = {"write-in-my-voice", "calibrate-my-voice"}
SUPPORTED_CAPTURE_AGENTS = {"claude-code", "codex"}
AI_TELL_PHRASES = (
    "great question",
    "important to note",
    "could potentially",
    "leverage",
    "robust",
    "seamless",
    "enhance",
    "crucial",
    "pivotal",
    "delve",
    "underscore",
    "hope this helps",
)
CAPTURED_OUTPUT_FORBIDDEN = (
    "no voice profile found",
    "applying default voice",
    "ai-tell cleanup",
    "removing copula avoidance",
    "your calibrated profile",
    "voice-profile.md",
    "skill's hard rule",
    "skill's hard rules",
    "hard rules block",
    "profile shows",
    "per profile",
    "i leaned into",
    "i followed that shape",
    "identifiers are preserved",
    "i kept all identifiers",
    "the description is intentionally short",
    "the draft is thin",
    "if you want a fuller",
    "★ insight",
)
COMMAND_WORD_RE = re.compile(
    r"\b(?:npm|pnpm|yarn|bun|python3?|pytest|uv|node|deno|go|cargo|git|make)\b"
)
COMMAND_ARGUMENT_RE = re.compile(r"[\w./:@=+-]+")


@dataclass
class Failure:
    scenario: str
    message: str


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def require(condition: bool, scenario: str, message: str) -> list[Failure]:
    if condition:
        return []
    return [Failure(scenario, message)]


def require_string(data: dict[str, Any], key: str, scenario: str) -> tuple[str, list[Failure]]:
    value = data.get(key)
    failures = require(
        isinstance(value, str) and bool(value.strip()),
        scenario,
        f"{key} must be a non-empty string",
    )
    if failures:
        return "", failures
    return value, []


def require_string_list(data: dict[str, Any], key: str, scenario: str) -> tuple[list[str], list[Failure]]:
    value = data.get(key)
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item.strip() for item in value)
    ):
        return [], [Failure(scenario, f"{key} must be a non-empty list of strings")]
    return value, []


def require_nested_string_list(
    data: dict[str, Any],
    key: str,
    scenario: str,
) -> tuple[list[list[str]], list[Failure]]:
    value = data.get(key, [])
    if not isinstance(value, list):
        return [], [Failure(scenario, f"{key} must be a list")]
    for group in value:
        if (
            not isinstance(group, list)
            or not group
            or not all(isinstance(item, str) and item.strip() for item in group)
        ):
            return [], [Failure(scenario, f"{key} must contain non-empty string groups")]
    return value, []


def phrase_count(text: str, phrases: tuple[str, ...]) -> int:
    normalized = normalize(text)
    return sum(normalized.count(phrase) for phrase in phrases)


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


def validate_rubric(scenario_id: str, rubric: object) -> list[Failure]:
    if not isinstance(rubric, list) or len(rubric) < 3:
        return [Failure(scenario_id, "rubric must contain at least three criteria")]
    failures: list[Failure] = []
    total_weight = 0
    for index, item in enumerate(rubric, start=1):
        if not isinstance(item, dict):
            failures.append(Failure(scenario_id, f"rubric[{index}] must be a map"))
            continue
        criterion = item.get("criterion")
        weight = item.get("weight")
        pass_text = item.get("pass")
        if not isinstance(criterion, str) or not criterion.strip():
            failures.append(Failure(scenario_id, f"rubric[{index}] missing criterion"))
        if not isinstance(weight, int) or weight <= 0:
            failures.append(Failure(scenario_id, f"rubric[{index}] weight must be a positive integer"))
        else:
            total_weight += weight
        if not isinstance(pass_text, str) or not pass_text.strip():
            failures.append(Failure(scenario_id, f"rubric[{index}] missing pass text"))
    if total_weight <= 0:
        failures.append(Failure(scenario_id, "rubric total weight must be positive"))
    return failures


def validate_assertions_shape(scenario_id: str, assertions: object) -> tuple[dict[str, Any], list[Failure]]:
    if not isinstance(assertions, dict) or not assertions:
        return {}, [Failure(scenario_id, "assertions must be a non-empty map")]
    failures: list[Failure] = []
    for key in ("required_all", "forbidden", "preserve_exact"):
        value = assertions.get(key, [])
        if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
            failures.append(Failure(scenario_id, f"assertions.{key} must be a list of strings"))
    _, nested_failures = require_nested_string_list(assertions, "required_any", scenario_id)
    failures.extend(nested_failures)
    if "max_em_dash" in assertions and not isinstance(assertions["max_em_dash"], int):
        failures.append(Failure(scenario_id, "assertions.max_em_dash must be an integer"))
    if "max_decorative_dashes" in assertions and not isinstance(assertions["max_decorative_dashes"], int):
        failures.append(Failure(scenario_id, "assertions.max_decorative_dashes must be an integer"))
    if "max_ai_tell_phrases" in assertions and not isinstance(assertions["max_ai_tell_phrases"], int):
        failures.append(Failure(scenario_id, "assertions.max_ai_tell_phrases must be an integer"))
    if "must_ask_question" in assertions and not isinstance(assertions["must_ask_question"], bool):
        failures.append(Failure(scenario_id, "assertions.must_ask_question must be true or false"))
    return assertions, failures


def validate_output_assertions(
    scenario_id: str,
    prompt: str,
    output: str,
    assertions: dict[str, Any],
    label: str = "reference output",
) -> list[Failure]:
    failures: list[Failure] = []
    normalized = normalize(output)

    for phrase in assertions.get("required_all", []):
        if phrase.lower() not in normalized:
            failures.append(Failure(scenario_id, f"{label} missing required phrase: {phrase}"))

    required_any, nested_failures = require_nested_string_list(assertions, "required_any", scenario_id)
    failures.extend(nested_failures)
    for group in required_any:
        if not any(option.lower() in normalized for option in group):
            failures.append(Failure(scenario_id, f"{label} missing one of: {', '.join(group)}"))

    for phrase in assertions.get("forbidden", []):
        if phrase.lower() in normalized:
            failures.append(Failure(scenario_id, f"{label} contains forbidden phrase: {phrase}"))

    for token in assertions.get("preserve_exact", []):
        if token not in prompt:
            failures.append(Failure(scenario_id, f"preserve_exact token is not present in prompt: {token}"))
        if token not in output:
            failures.append(Failure(scenario_id, f"{label} missing exact token: {token}"))

    max_em_dash = assertions.get("max_em_dash")
    if isinstance(max_em_dash, int) and output.count("—") > max_em_dash:
        failures.append(Failure(scenario_id, f"too many em dashes: {output.count('—')} > {max_em_dash}"))

    max_decorative_dashes = assertions.get("max_decorative_dashes", max_em_dash)
    if isinstance(max_decorative_dashes, int):
        dash_count = decorative_dash_count(output)
        if dash_count > max_decorative_dashes:
            failures.append(
                Failure(
                    scenario_id,
                    f"too many decorative dashes: {dash_count} > {max_decorative_dashes}",
                )
            )

    max_ai_tells = assertions.get("max_ai_tell_phrases")
    if isinstance(max_ai_tells, int):
        ai_tell_count = phrase_count(output, AI_TELL_PHRASES)
        if ai_tell_count > max_ai_tells:
            failures.append(Failure(scenario_id, f"too many AI-tell phrases: {ai_tell_count} > {max_ai_tells}"))

    if assertions.get("must_ask_question") is True and "?" not in output:
        failures.append(Failure(scenario_id, f"{label} must ask a question"))
    return failures


def validate_scenario(item: object) -> tuple[str, list[str], list[Failure]]:
    if not isinstance(item, dict):
        return "<unknown>", [], [Failure("<unknown>", "scenario must be a map")]

    scenario_id, failures = require_string(item, "id", "<unknown>")
    if failures:
        return "<unknown>", [], failures

    skill, skill_failures = require_string(item, "skill", scenario_id)
    prompt, prompt_failures = require_string(item, "prompt", scenario_id)
    output, output_failures = require_string(item, "reference_output", scenario_id)
    coverage, coverage_failures = require_string_list(item, "coverage", scenario_id)
    expected, expected_failures = require_string_list(item, "expected_behavior", scenario_id)
    failures = skill_failures + prompt_failures + output_failures + coverage_failures + expected_failures

    if skill and skill not in SUPPORTED_SKILLS:
        failures.append(Failure(scenario_id, f"unsupported skill: {skill}"))
    if expected and len(expected) < 3:
        failures.append(Failure(scenario_id, "expected_behavior must contain at least three checks"))

    assertions, assertion_failures = validate_assertions_shape(scenario_id, item.get("assertions"))
    failures.extend(assertion_failures)
    failures.extend(validate_rubric(scenario_id, item.get("rubric")))
    if prompt and output and assertions:
        failures.extend(validate_output_assertions(scenario_id, prompt, output, assertions))
    return scenario_id, coverage, failures


def scenario_map(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    scenarios = data.get("scenarios", [])
    if not isinstance(scenarios, list):
        return {}
    return {
        item["id"]: item
        for item in scenarios
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def validate_suite(data: object) -> list[Failure]:
    if not isinstance(data, dict):
        return [Failure("<suite>", "scenario suite must be a map")]
    failures: list[Failure] = []
    if data.get("schema_version") not in SUPPORTED_SCHEMA_VERSIONS:
        failures.append(Failure("<suite>", f"unsupported schema_version: {data.get('schema_version')!r}"))

    coverage_requirements = data.get("coverage_requirements")
    if not isinstance(coverage_requirements, list) or not coverage_requirements:
        failures.append(Failure("<suite>", "coverage_requirements must be a non-empty list"))
        coverage_requirements = []
    elif not all(isinstance(item, str) and item.strip() for item in coverage_requirements):
        failures.append(Failure("<suite>", "coverage_requirements must contain strings"))
        coverage_requirements = []

    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        failures.append(Failure("<suite>", "scenarios must be a non-empty list"))
        return failures

    seen_ids: set[str] = set()
    covered: set[str] = set()
    for item in scenarios:
        scenario_id, coverage, scenario_failures = validate_scenario(item)
        if scenario_id in seen_ids:
            failures.append(Failure(scenario_id, "duplicate scenario id"))
        seen_ids.add(scenario_id)
        covered.update(coverage)
        failures.extend(scenario_failures)

    for tag in sorted(set(coverage_requirements) - covered):
        failures.append(Failure("<suite>", f"missing required coverage tag: {tag}"))
    return failures


def validate_captured_outputs(data: object, suite: dict[str, Any], require_pilot: bool) -> list[Failure]:
    if not isinstance(data, dict):
        return [Failure("<outputs>", "captured output file must be a map")]
    failures: list[Failure] = []
    if data.get("schema_version") not in SUPPORTED_SCHEMA_VERSIONS:
        failures.append(Failure("<outputs>", f"unsupported schema_version: {data.get('schema_version')!r}"))
    agent = data.get("agent")
    if agent not in SUPPORTED_CAPTURE_AGENTS:
        failures.append(Failure("<outputs>", f"agent must be one of {sorted(SUPPORTED_CAPTURE_AGENTS)}"))

    outputs = data.get("outputs")
    if not isinstance(outputs, list) or not outputs:
        return failures + [Failure("<outputs>", "outputs must be a non-empty list")]

    scenarios = scenario_map(suite)
    seen: set[str] = set()
    for index, item in enumerate(outputs, start=1):
        if not isinstance(item, dict):
            failures.append(Failure("<outputs>", f"outputs[{index}] must be a map"))
            continue
        scenario_id = item.get("scenario_id")
        output = item.get("output")
        if not isinstance(scenario_id, str) or not scenario_id.strip():
            failures.append(Failure("<outputs>", f"outputs[{index}] missing scenario_id"))
            continue
        if scenario_id in seen:
            failures.append(Failure(scenario_id, "duplicate captured output"))
        seen.add(scenario_id)
        if scenario_id not in scenarios:
            failures.append(Failure(scenario_id, "captured output references unknown scenario"))
            continue
        if not isinstance(output, str) or not output.strip():
            failures.append(Failure(scenario_id, "captured output must be a non-empty string"))
            continue
        scenario = scenarios[scenario_id]
        failures.extend(
            validate_output_assertions(
                scenario_id,
                scenario["prompt"],
                output,
                scenario["assertions"],
                label=f"{agent} output",
            )
        )
        normalized = normalize(output)
        for phrase in CAPTURED_OUTPUT_FORBIDDEN:
            if phrase in normalized:
                failures.append(Failure(scenario_id, f"{agent} output exposes internal note: {phrase}"))

    if require_pilot:
        required = {
            item["id"]
            for item in scenarios.values()
            if item.get("pilot") is True
        }
        for missing in sorted(required - seen):
            failures.append(Failure(missing, "missing captured output for pilot scenario"))
    return failures


def print_pilot_prompts(data: dict[str, Any]) -> None:
    for item in data.get("scenarios", []):
        if isinstance(item, dict) and item.get("pilot") is True:
            print(f"## {item['id']} [{item['skill']}]")
            print(item["prompt"])
            print()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenarios", type=Path, default=SCENARIOS, help="Path to scenarios JSON.")
    parser.add_argument("--outputs", type=Path, help="Path to captured real-agent outputs JSON.")
    parser.add_argument(
        "--outputs-dir",
        type=Path,
        help="Directory of captured real-agent output JSON files to validate.",
    )
    parser.add_argument(
        "--require-pilot-coverage",
        action="store_true",
        help="Require captured outputs for every scenario marked pilot=true.",
    )
    parser.add_argument("--print-pilot-prompts", action="store_true", help="Print pilot prompts for manual capture.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    data = json.loads(args.scenarios.read_text(encoding="utf-8"))
    if args.print_pilot_prompts:
        print_pilot_prompts(data)
        return 0
    failures = validate_suite(data)
    if args.outputs:
        failures.extend(
            validate_captured_outputs(
                json.loads(args.outputs.read_text(encoding="utf-8")),
                data,
                require_pilot=args.require_pilot_coverage,
            )
        )
    if args.outputs_dir:
        output_paths = sorted(args.outputs_dir.glob("*.json"))
        if not output_paths:
            failures.append(Failure("<outputs-dir>", f"no JSON files found in {args.outputs_dir}"))
        for output_path in output_paths:
            capture_failures = validate_captured_outputs(
                json.loads(output_path.read_text(encoding="utf-8")),
                data,
                require_pilot=args.require_pilot_coverage,
            )
            failures.extend(
                Failure(f"{output_path.name}:{failure.scenario}", failure.message)
                for failure in capture_failures
            )
    if failures:
        print("behavior evals failed", file=sys.stderr)
        for failure in failures:
            print(f"- {failure.scenario}: {failure.message}", file=sys.stderr)
        return 1
    print("behavior evals passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
