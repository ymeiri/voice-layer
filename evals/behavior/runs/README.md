# Local Behavior Runs

This directory is for private, local real-agent captures. JSON files here are
ignored by Git because they may contain local context or user-specific text.

Use this workflow:

1. Print pilot prompts:

   ```sh
   python3 scripts/evaluate_behavior.py --print-pilot-prompts
   ```

2. Save local outputs as JSON in this directory.

3. Validate one capture:

   ```sh
   python3 scripts/evaluate_behavior.py --outputs evals/behavior/runs/<run>.json
   ```

4. Validate all local captures:

   ```sh
   python3 scripts/evaluate_behavior.py --outputs-dir evals/behavior/runs
   ```

5. When a capture is passing and sanitized, copy it into
   `tests/fixtures/behavior/` with a `*-real.json` filename so CI validates it.

Known failing local captures should be treated as defect evidence, not release
evidence. Replace them after the behavior is fixed or summarize the failure in
docs or an issue.
