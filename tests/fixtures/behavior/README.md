# Behavior Fixtures

This directory contains sanitized captured outputs that are safe to commit and
expected to pass `scripts/evaluate_behavior.py`.

Every `*.json` file in this directory is validated by the unit test suite. If a
real-agent run is private, stale, or failing, keep it under
`evals/behavior/runs/` instead and summarize the finding in docs or an issue.

Filename convention:

- `*-real.json`: sanitized output from a real agent run.
- other names: synthetic fixtures used to exercise the evaluator.
