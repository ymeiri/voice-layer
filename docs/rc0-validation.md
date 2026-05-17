# RC-0 Validation

RC-0 is the first release-candidate pass for `voice-layer`. Its goal is to prove
the current skills behave correctly in real Claude Code and Codex sessions
before new feature work continues.

Do not treat deterministic tests alone as release evidence. RC-0 requires live
agent outputs plus local validation.

## Preconditions

From the repo root:

```sh
./voice-layer install --agent both --mode symlink
./voice-layer doctor --agent both
python3 scripts/validate_repo.py
python3 scripts/evaluate_behavior.py
python3 -m unittest discover -s tests
```

If you want a fresh calibration cycle, move the current profile aside before the
live run:

```sh
mv ~/.config/voice-layer/voice-profile.md ~/.config/voice-layer/voice-profile.md.rc0-backup
```

Do not delete the backup until the new profile passes validation.

## Claude Code Write Test

Run this in Claude Code from the repo root:

```text
/write-in-my-voice draft a PR description from this:
Change parseWidgetConfig() in src/widgets/config.ts. The goal is to fix FOO-123. The behavior is behind ENABLE_WIDGET_V2=true. Tests: npm test -- widgets/config.test.ts.
```

Pass criteria:

- Output contains only the PR description.
- It preserves `FOO-123`, `parseWidgetConfig()`, `src/widgets/config.ts`,
  `ENABLE_WIDGET_V2=true`, and `npm test -- widgets/config.test.ts`.
- It does not include `★ Insight`, profile paths, rationale, self-audit notes,
  or follow-up commentary.
- It does not create `Rollout`, `Risk`, `Impact`, `Compatibility`, or
  `Validation` sections from the feature flag alone.
- It does not infer flag-off behavior, rollout safety, customer impact, or
  validation beyond the supplied test command.

## Codex Write Test

Run the equivalent prompt in Codex:

```text
Use $write-in-my-voice to draft a PR description from this:
Change parseWidgetConfig() in src/widgets/config.ts. The goal is to fix FOO-123. The behavior is behind ENABLE_WIDGET_V2=true. Tests: npm test -- widgets/config.test.ts.
```

Use the same pass criteria as the Claude Code write test.

## Calibration Test

Run this in Claude Code after moving the profile aside if you want a clean
cycle:

```text
/calibrate-my-voice build my local voice profile.
```

Pass criteria:

- The agent asks which sources it may use before reading private data.
- The source menu adapts to available tools and explicitly allows connect,
  export, paste, skip, or alternate-source choices.
- It explains that derived-pattern retention applies to the generated profile
  and skill-created temp files, while the active agent or connector host may
  still keep session/tool artifacts outside the profile.
- Google Docs and Gmail/Workspace are offered as connectable or exportable
  sources when long-form docs or email are relevant; they are not silently
  dropped just because a connector is not already authenticated.
- PR descriptions and PR review comments are treated as higher-signal
  engineering sources than local git commit messages.
- For every approved source, the agent asks for scope, identity filter, date
  range, and retention mode.
- If an approved source yields only metadata, zero usable samples, auth failure,
  or tool failure, the agent asks whether to retry, export/paste, skip, or
  proceed with lower confidence before writing the final profile.
- The generated profile validates before the agent claims completion:

  ```sh
  python3 scripts/validate_profile.py ~/.config/voice-layer/voice-profile.md
  ```
- Skill-created temporary raw-sample files are deleted or explicitly accounted
  for; host-managed session/tool artifacts are disclosed if detected.

## Capture Format

Keep raw captures under `evals/behavior/runs/`. Files there are ignored by Git.
Do not edit the agent output before capture.

Example:

```json
{
  "schema_version": "1.0",
  "agent": "claude-code",
  "run_id": "rc0-2026-05-12",
  "captured_at": "2026-05-12",
  "outputs": [
    {
      "scenario_id": "write.no-feature-flag-inference",
      "output": "Summary\n\nFixes FOO-123 by updating parseWidgetConfig() in src/widgets/config.ts. The changed behavior is gated by ENABLE_WIDGET_V2=true.\n\nTesting\n\n- npm test -- widgets/config.test.ts"
    }
  ]
}
```

Validate captures:

```sh
python3 scripts/evaluate_behavior.py --outputs evals/behavior/runs/<file>.json
python3 scripts/evaluate_behavior.py --outputs-dir evals/behavior/runs
```

When a capture is passing and sanitized, copy it into
`tests/fixtures/behavior/` with a `*-real.json` filename so the unit tests keep
checking it.

## RC-0 Pass Condition

RC-0 passes only when:

- Claude Code write test passes.
- Codex write test passes.
- Fresh calibration flow passes and the generated profile validates.
- Captured write outputs pass `scripts/evaluate_behavior.py`.
- Local deterministic checks pass:

  ```sh
  python3 scripts/validate_repo.py
  python3 scripts/validate_profile.py ~/.config/voice-layer/voice-profile.md
  python3 scripts/evaluate_examples.py
  python3 scripts/evaluate_behavior.py
  python3 scripts/evaluate_behavior.py --outputs-dir tests/fixtures/behavior
  python3 -m unittest discover -s tests
  git diff --check
  ```

If any live run fails, patch the skill contract or evaluator first, then rerun
the same prompt. Do not broaden the project scope until RC-0 is green.
