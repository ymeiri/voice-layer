# Examples

These examples are synthetic. They are not based on a real person's writing and
they do not imitate a living public figure.

The goal is to make `voice-layer` visible:

```text
same facts + different voice/vibe/audience -> different usable draft
```

## Demo Input

The shared input is intentionally generic and AI-shaped:

- [rollout-update.md](inputs/rollout-update.md)

## Synthetic Archetypes

- [staff-engineer.yaml](archetypes/staff-engineer.yaml): terse, specific,
  tradeoff-first.
- [diplomatic-manager.yaml](archetypes/diplomatic-manager.yaml): warm,
  careful, alignment-oriented.
- [product-launcher.yaml](archetypes/product-launcher.yaml): energetic,
  concrete, launch-focused.

## Vibe Overlays

- [corporate-friendly.yaml](vibes/corporate-friendly.yaml): polished,
  low-risk, executive-readable.
- [chill-rock-star.yaml](vibes/chill-rock-star.yaml): relaxed, punchy,
  confident, but still grounded.

## Worked Outputs

| Output | Profile | Vibe | What to notice |
| --- | --- | --- | --- |
| [rollout-update.staff-engineer.md](outputs/rollout-update.staff-engineer.md) | staff engineer | none | direct risk framing and concrete rollout guardrail |
| [rollout-update.diplomatic-manager.md](outputs/rollout-update.diplomatic-manager.md) | diplomatic manager | corporate-friendly | softer alignment language without hiding the risk |
| [rollout-update.product-launcher-chill-rock-star.md](outputs/rollout-update.product-launcher-chill-rock-star.md) | product launcher | chill-rock-star | higher energy while preserving facts and constraints |

These are not benchmark claims. They are launch/demo fixtures with deterministic
checks for fact preservation, AI-tell reduction, and profile/vibe guardrails.

Run:

```sh
python3 scripts/evaluate_examples.py
```
