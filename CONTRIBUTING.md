# Contributing

Contributions should keep the skill portable across Agent Skills clients.

## Standards

- Keep `SKILL.md` concise and move detailed material into `references/`.
- Do not add product-specific requirements to the core skill unless there is a fallback.
- Do not commit real voice profiles, private exports, or user-authored corpora.
- Prefer deterministic scripts for repeatable checks and source collection.
- Add eval prompts when behavior changes.
- Keep support claims aligned with `docs/support-matrix.md`.
- Keep the direct install lifecycle explicit: package installation must not mutate
  `~/.claude`, `~/.agents`, or `~/.config` without a `voice-layer install` call.

## Contribution Terms

By submitting a contribution, you agree that your contribution is provided under
the MIT license used by this repository. This project does not use a CLA or DCO
for v0.1.0.

## Privacy Rules

Do not include:

- real `voice-profile.md` files,
- private Slack, email, docs, PR, issue, or agent-session exports,
- credentials, tokens, or local machine paths,
- company names or internal repository names from private workspaces,
- screenshots or recordings with unredacted private data.

Use synthetic examples in tests and docs. If a bug requires private context,
summarize the behavior and keep the raw material out of GitHub.

## Local checks

```sh
python3 scripts/validate_repo.py
python3 scripts/sync_core.py --check
python3 scripts/check_no_silent_telemetry.py
python3 scripts/validate_profile.py tests/fixtures/profiles/valid-profile.md
python3 scripts/evaluate_examples.py
python3 scripts/evaluate_behavior.py
python3 scripts/evaluate_behavior.py --outputs-dir tests/fixtures/behavior
python3 -m unittest discover -s tests
git diff --check
```

Before a release tag, also run:

```sh
python3 scripts/validate_release_archive.py
```
