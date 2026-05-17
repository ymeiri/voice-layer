# RC-0 Results

Date: 2026-05-12

RC-0 validates the current direct-skill flow for Claude Code and Codex:

- fresh calibration from approved sources,
- profile validation and validator-recovery behavior,
- `write-in-my-voice` behavior in Claude Code,
- `write-in-my-voice` behavior in Codex,
- captured real-agent output fixtures.

## Result

Status: passed for direct Claude Code and Codex skills.

## Evidence

Local raw transcript exports were used during validation, but they are ignored
by Git and are not release artifacts.

Sanitized captured fixtures:

- [`tests/fixtures/behavior/claude-code-rc0-real.json`](../tests/fixtures/behavior/claude-code-rc0-real.json)
- [`tests/fixtures/behavior/codex-rc0-real.json`](../tests/fixtures/behavior/codex-rc0-real.json)

## What Passed

- `calibrate-my-voice` asked before reading private sources.
- The source menu adapted to the local tool stack.
- Google Workspace was offered as a connectable source instead of silently
  skipped.
- PR descriptions and review comments were preferred over local git commits.
- Local git commits and AI agent sessions were skipped when the user chose to
  skip them.
- The profile validator failed once, blocked completion, was repaired, and then
  passed.
- Skill-created temporary raw files were deleted after analysis.
- The generated profile at `~/.config/voice-layer/voice-profile.md` passed
  validation.
- Claude Code and Codex both produced a PR description without profile leakage,
  `Insight` blocks, unsupported rollout/risk/impact/compatibility/validation
  sections, or feature-flag behavior inference.

## Verification Commands

```sh
python3 scripts/evaluate_behavior.py --outputs tests/fixtures/behavior/claude-code-rc0-real.json
python3 scripts/evaluate_behavior.py --outputs tests/fixtures/behavior/codex-rc0-real.json
python3 scripts/evaluate_behavior.py --outputs-dir tests/fixtures/behavior
python3 scripts/evaluate_behavior.py
python3 scripts/validate_repo.py
python3 scripts/evaluate_examples.py
python3 -m unittest discover -s tests
python3 scripts/validate_profile.py ~/.config/voice-layer/voice-profile.md
git diff --check
```

All commands passed during the RC-0 pass.

## Not Covered

RC-0 does not prove:

- Claude Code plugin installation from the plugin marketplace UI.
- Codex plugin installation from the plugin UI.
- Cursor, ChatGPT, Windsurf, Continue, or other agent support.
- Native vendor collectors for GitHub, Slack, Google Docs, Gmail, Linear, Jira,
  Asana, Monday.com, or Confluence.
- Full qualitative voice quality. The profile is useful, but the profile still
  records `confidence: "medium"` until the user reviews and confirms it.

## Follow-Up

The RC-0 fixture set should keep passing as the package layout changes. Phase 2
now keeps shared behavior in core and syncs it into agent-specific packages.
