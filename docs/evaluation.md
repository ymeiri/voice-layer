# Evaluation

The repo uses four evaluation tiers. The first three are deterministic and safe
to run in CI. The fourth is the human or LLM-judge layer needed for true voice
quality.

## Tier 1: deterministic checks

These are CI-friendly:

- valid skill frontmatter,
- plugin manifest shape,
- profile template shape,
- installer dry runs,
- no silent telemetry/network imports in executable repo code,
- eval files parse and contain expected fields.

Run:

```sh
python3 scripts/validate_repo.py
python3 scripts/check_no_silent_telemetry.py
python3 scripts/evaluate_examples.py
python3 scripts/evaluate_behavior.py
python3 -m unittest discover -s tests
```

## Tier 2: rule-based output checks

The current example harness checks the synthetic examples for:

- AI-tell phrase reduction from input to output,
- required context preservation,
- forbidden overclaims such as risk-free rollout language,
- profile/vibe-specific required phrases,
- forbidden profile/vibe misses,
- model-shaped punctuation limits such as repeated em dashes, double hyphen
  breaks, and spaced-hyphen asides.

Run:

```sh
python3 scripts/evaluate_examples.py
```

This is deliberately narrow. It verifies the demo fixtures; it does not prove
general voice quality.

## Tier 3: behavioral scenarios

Behavioral evals live in [../evals/behavior/scenarios.json](../evals/behavior/scenarios.json).
They define high-risk scenarios for the actual skills:

- consent negotiation before reading private sources,
- adapting the source menu to local tools,
- refusing third-party voice training,
- preserving technical identifiers,
- avoiding invented facts,
- cleaning AI tells,
- applying vibe without impersonation,
- adapting for an audience without cultural mimicry,
- documentation/RFC structure,
- agent-session calibration,
- raw sample retention boundaries.

Each scenario includes:

- a prompt,
- expected behavior,
- deterministic assertions,
- a reference output that must satisfy those assertions,
- a rubric for human or LLM-judge scoring.

Run:

```sh
python3 scripts/evaluate_behavior.py
```

This tier can also validate captured real-agent outputs. Start with the pilot
set before building automation:

```sh
python3 scripts/evaluate_behavior.py --print-pilot-prompts
```

Run each prompt in Claude Code or Codex, then store the outputs in a local file
under `evals/behavior/runs/`:

```json
{
  "schema_version": "1.0",
  "agent": "claude-code",
  "run_id": "manual-2026-05-11",
  "captured_at": "2026-05-11",
  "outputs": [
    {
      "scenario_id": "write.preserve-identifiers",
      "output": "The exact agent output goes here."
    }
  ]
}
```

Validate captured outputs:

```sh
python3 scripts/evaluate_behavior.py --outputs evals/behavior/runs/claude-code-manual-2026-05-11.json
python3 scripts/evaluate_behavior.py --outputs evals/behavior/runs/claude-code-manual-2026-05-11.json --require-pilot-coverage
python3 scripts/evaluate_behavior.py --outputs-dir evals/behavior/runs
```

`evals/behavior/runs/` is ignored by Git because real agent outputs may include
local context. Commit only sanitized fixtures or summarized findings.

Ignored local captures are diagnostic artifacts, not a CI signal. If a capture
is expected to stay green, sanitize it and copy it into
`tests/fixtures/behavior/` with a `*-real.json` filename. Every committed
behavior fixture is validated by the unit test matrix. If a local capture is
known to fail, either replace it after the behavior is fixed or document the
failure in the relevant issue/release note. Do not present a green CI run as
proof that all ignored captures pass.

## Tier 4: voice quality

Voice fit needs a human or an LLM judge with a rubric. A useful rubric asks:

- Does the output preserve the user's intent?
- Does it match the profile for this channel?
- Did it avoid overfitting private quirks into formal writing?
- Is the result something the user would plausibly send?

Do not claim full automation for this tier.
