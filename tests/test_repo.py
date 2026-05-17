from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepoTests(unittest.TestCase):
    def test_repo_validator_passes(self) -> None:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_repo.py")],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def test_core_sync_check_passes(self) -> None:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "sync_core.py"), "--check"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def test_example_evals_pass(self) -> None:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "evaluate_examples.py")],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def test_behavior_evals_pass(self) -> None:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "evaluate_behavior.py")],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def test_behavior_evals_accept_captured_outputs(self) -> None:
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_behavior.py"),
                "--outputs-dir",
                str(ROOT / "tests" / "fixtures" / "behavior"),
            ],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def test_behavior_fixtures_include_real_capture(self) -> None:
        real_fixtures = sorted((ROOT / "tests" / "fixtures" / "behavior").glob("*-real.json"))
        self.assertTrue(real_fixtures, "expected at least one sanitized real-agent behavior capture")

    def test_behavior_evals_reject_missing_coverage(self) -> None:
        suite = {
            "schema_version": "1.0",
            "coverage_requirements": ["write.missing"],
            "scenarios": [
                {
                    "id": "test.valid-scenario",
                    "skill": "write-in-my-voice",
                    "coverage": ["write.ai_tell_cleanup"],
                    "prompt": "Use $write-in-my-voice to rewrite FOO-1.",
                    "expected_behavior": ["Preserve FOO-1.", "Return a draft.", "Do not invent facts."],
                    "reference_output": "FOO-1 is ready for review.",
                    "assertions": {
                        "required_all": ["FOO-1"],
                        "preserve_exact": ["FOO-1"],
                        "forbidden": ["deployed"],
                    },
                    "rubric": [
                        {"criterion": "facts", "weight": 1, "pass": "Preserves facts."},
                        {"criterion": "voice", "weight": 1, "pass": "Uses plain voice."},
                        {"criterion": "safety", "weight": 1, "pass": "Avoids inventions."},
                    ],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "scenarios.json"
            path.write_text(json.dumps(suite), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "evaluate_behavior.py"), "--scenarios", str(path)],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("missing required coverage tag: write.missing", proc.stderr)

    def test_behavior_evals_reject_bad_captured_output(self) -> None:
        capture = {
            "schema_version": "1.0",
            "agent": "codex",
            "outputs": [
                {
                    "scenario_id": "write.preserve-identifiers",
                    "output": "This was tested and validated.",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "outputs.json"
            path.write_text(json.dumps(capture), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "evaluate_behavior.py"), "--outputs", str(path)],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("codex output missing exact token: FOO-123", proc.stderr)
        self.assertIn("codex output contains forbidden phrase: validated", proc.stderr)

    def test_behavior_evals_reject_decorative_dash_breaks(self) -> None:
        suite = {
            "schema_version": "1.0",
            "coverage_requirements": ["write.ai_tell_cleanup"],
            "scenarios": [
                {
                    "id": "test.decorative-dash",
                    "skill": "write-in-my-voice",
                    "coverage": ["write.ai_tell_cleanup"],
                    "prompt": "Use $write-in-my-voice to rewrite FOO-1.",
                    "expected_behavior": ["Preserve FOO-1.", "Return a draft.", "Avoid AI punctuation."],
                    "reference_output": "FOO-1 is ready -- but needs review.",
                    "assertions": {
                        "required_all": ["FOO-1"],
                        "preserve_exact": ["FOO-1"],
                        "forbidden": ["deployed"],
                        "max_em_dash": 0,
                    },
                    "rubric": [
                        {"criterion": "facts", "weight": 1, "pass": "Preserves facts."},
                        {"criterion": "voice", "weight": 1, "pass": "Uses plain voice."},
                        {"criterion": "punctuation", "weight": 1, "pass": "Avoids AI dash breaks."},
                    ],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "scenarios.json"
            path.write_text(json.dumps(suite), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "evaluate_behavior.py"), "--scenarios", str(path)],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("too many decorative dashes", proc.stderr)

    def test_behavior_evals_allow_command_separators(self) -> None:
        suite = {
            "schema_version": "1.0",
            "coverage_requirements": ["write.preserve_identifiers"],
            "scenarios": [
                {
                    "id": "test.command-separator",
                    "skill": "write-in-my-voice",
                    "coverage": ["write.preserve_identifiers"],
                    "prompt": "Use $write-in-my-voice to rewrite this: Tests: npm test -- widgets/config.test.ts.",
                    "expected_behavior": [
                        "Preserve the command.",
                        "Return a draft.",
                        "Do not treat command syntax as prose punctuation.",
                    ],
                    "reference_output": "Testing\n\n- npm test -- widgets/config.test.ts",
                    "assertions": {
                        "required_all": ["npm test -- widgets/config.test.ts"],
                        "preserve_exact": ["npm test -- widgets/config.test.ts"],
                        "forbidden": ["deployed"],
                        "max_em_dash": 0,
                    },
                    "rubric": [
                        {"criterion": "facts", "weight": 1, "pass": "Preserves facts."},
                        {"criterion": "command", "weight": 1, "pass": "Preserves command syntax."},
                        {"criterion": "punctuation", "weight": 1, "pass": "Allows command separators."},
                    ],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "scenarios.json"
            path.write_text(json.dumps(suite), encoding="utf-8")
            subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "evaluate_behavior.py"), "--scenarios", str(path)],
                cwd=ROOT,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

    def test_profile_validator_accepts_valid_profile_and_template(self) -> None:
        validator = ROOT / "scripts" / "validate_profile.py"
        profiles = [
            ROOT / "tests" / "fixtures" / "profiles" / "valid-profile.md",
            ROOT
            / "core"
            / "profile"
            / "voice-profile.template.md",
        ]
        for profile in profiles:
            with self.subTest(profile=profile):
                subprocess.run(
                    [sys.executable, str(validator), "--quiet", str(profile)],
                    cwd=ROOT,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

    def test_profile_validator_rejects_invalid_profiles(self) -> None:
        validator = ROOT / "scripts" / "validate_profile.py"
        profiles = [
            ROOT / "tests" / "fixtures" / "profiles" / "invalid-profile-missing-section.md",
            ROOT / "tests" / "fixtures" / "profiles" / "invalid-profile-raw-sample-risk.md",
        ]
        for profile in profiles:
            with self.subTest(profile=profile):
                proc = subprocess.run(
                    [sys.executable, str(validator), str(profile)],
                    cwd=ROOT,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                self.assertNotEqual(proc.returncode, 0)
                self.assertIn("profile validation failed", proc.stderr)

    def test_profile_validator_rejects_unsupported_inline_lists(self) -> None:
        validator = ROOT / "scripts" / "validate_profile.py"
        source = ROOT / "tests" / "fixtures" / "profiles" / "valid-profile.md"
        text = source.read_text(encoding="utf-8").replace(
            'limitations:\n  - "Mostly engineering communication samples."\n',
            'limitations: ["Mostly engineering communication samples."]\n',
        )
        with tempfile.TemporaryDirectory() as tempdir:
            profile = Path(tempdir) / "voice-profile.md"
            profile.write_text(text, encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(validator), str(profile)],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("unsupported inline list syntax", proc.stderr)

    def test_profile_validator_rejects_exact_phrase_leakage_without_approval(self) -> None:
        validator = ROOT / "scripts" / "validate_profile.py"
        source = ROOT / "tests" / "fixtures" / "profiles" / "valid-profile.md"
        text = source.read_text(encoding="utf-8").replace(
            "Uses brief agreement, risk-checking language, and concrete next-step phrasing.",
            '- "exact private phrase from a message"',
        )
        with tempfile.TemporaryDirectory() as tempdir:
            profile = Path(tempdir) / "voice-profile.md"
            profile.write_text(text, encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(validator), str(profile)],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("exact phrase-like text outside Examples", proc.stderr)

    def test_profile_validator_rejects_extra_examples_text_without_approval(self) -> None:
        validator = ROOT / "scripts" / "validate_profile.py"
        source = ROOT / "tests" / "fixtures" / "profiles" / "valid-profile.md"
        text = source.read_text(encoding="utf-8").replace(
            "No approved examples.",
            "No approved examples.\n\nAdditional example text.",
        )
        with tempfile.TemporaryDirectory() as tempdir:
            profile = Path(tempdir) / "voice-profile.md"
            profile.write_text(text, encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(validator), str(profile)],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("Examples section contains content", proc.stderr)

    def test_installer_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            env = os.environ.copy()
            env["HOME"] = tempdir
            env["XDG_CONFIG_HOME"] = str(Path(tempdir) / ".config")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "install.py"),
                    "install",
                    "--dry-run",
                    "--agent",
                    "both",
                ],
                cwd=ROOT,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            )
        self.assertIn("write-in-my-voice", proc.stdout)
        self.assertIn("calibrate-my-voice", proc.stdout)
        self.assertIn("create profile template", proc.stdout)
        self.assertIn("voice-layer doctor", proc.stdout)

    def test_installer_doctor(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            env = os.environ.copy()
            env["HOME"] = tempdir
            env["XDG_CONFIG_HOME"] = str(Path(tempdir) / ".config")
            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "install.py"), "doctor", "--agent", "both"],
                cwd=ROOT,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            )
        self.assertIn("voice-layer doctor", proc.stdout)
        self.assertIn("missing", proc.stdout)

    def test_installer_full_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            env = os.environ.copy()
            env["HOME"] = tempdir
            env["XDG_CONFIG_HOME"] = str(Path(tempdir) / ".config")

            subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "install.py"), "install", "--agent", "both"],
                cwd=ROOT,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            )
            doctor = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "install.py"), "doctor", "--agent", "both"],
                cwd=ROOT,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            )
            self.assertIn("installed (managed copy)", doctor.stdout)
            profile = Path(tempdir) / ".config" / "voice-layer" / "voice-profile.md"
            self.assertTrue(profile.exists())
            self.assertEqual(profile.stat().st_mode & 0o777, 0o600)

            subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "install.py"), "uninstall", "--agent", "both"],
                cwd=ROOT,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            )
            self.assertTrue(profile.exists())
            self.assertFalse((Path(tempdir) / ".claude" / "skills" / "write-in-my-voice").exists())
            self.assertFalse((Path(tempdir) / ".agents" / "skills" / "write-in-my-voice").exists())

    def test_cli_purge_requires_confirmation_and_removes_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            env = os.environ.copy()
            env["HOME"] = tempdir
            env["XDG_CONFIG_HOME"] = str(Path(tempdir) / ".config")

            subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "install.py"), "install", "--agent", "codex"],
                cwd=ROOT,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            )
            profile_dir = Path(tempdir) / ".config" / "voice-layer"
            self.assertTrue(profile_dir.exists())

            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "install.py"), "purge", "--agent", "codex"],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("purge requires --yes", proc.stderr)
            self.assertTrue(profile_dir.exists())

            subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "install.py"), "purge", "--agent", "codex", "--yes"],
                cwd=ROOT,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            )
            self.assertFalse(profile_dir.exists())

    def test_cli_validate_profile(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "install.py"),
                "validate-profile",
                "--quiet",
                str(ROOT / "tests" / "fixtures" / "profiles" / "valid-profile.md"),
            ],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertEqual(proc.stdout, "")

    def test_installer_version(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "install.py"), "--version"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertIn("voice-layer", proc.stdout)

    def test_git_collector_handles_empty_repo(self) -> None:
        collector = (
            ROOT
            / "packages"
            / "codex"
            / "skills"
            / "calibrate-my-voice"
            / "scripts"
            / "collect_git_samples.py"
        )
        with tempfile.TemporaryDirectory() as tempdir:
            subprocess.run(["git", "init"], cwd=tempdir, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc = subprocess.run(
                [sys.executable, str(collector), "--repo", tempdir, "--author", "nobody@example.com"],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        self.assertNotEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
