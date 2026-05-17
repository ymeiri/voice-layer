---
schema_version: "1.0"
profile_subject: "self"
profile_name: "personal"
language: "en"
updated_at: "2026-05-11"
calibrated_by: "calibrate-my-voice"
source_summary:
  - source: "manual"
    scope: "pasted PR review comments and Slack replies"
    date_range: "2026-04-01..2026-05-01"
    sample_count: 12
    retention: "derived-patterns"
confidence: "medium"
privacy:
  raw_samples_retained: false
  approved_exact_examples: false
limitations:
  - "Mostly engineering communication samples."
---

# Voice profile

## Summary

Direct, technical, and low-ceremony. Usually starts with the point and adds
context only when it changes the decision.

## Global voice

Uses concise technical English, plain verbs, and specific constraints.

## Channel profiles

Slack replies are short. PR comments name the exact concern and proposed next
step.

## Documentation style

Design docs start with context, tradeoffs, and an explicit recommendation.

## Openings and closings

Usually skips greetings in technical channels and closes with a concrete next
step.

## Sentence architecture

Mixes short claims with medium explanatory sentences.

## Punctuation and formatting

Uses bullets when items are parallel and avoids decorative punctuation.

## Punctuation texture

Dashes are rare. Colons are used to introduce specifics.

## Hedging and uncertainty

Hedges only when uncertainty is real.

## Pushback and disagreement

Direct but respectful. Names the technical risk rather than softening it away.

## Recurring phrases

Uses brief agreement, risk-checking language, and concrete next-step phrasing.

## Vocabulary fingerprint

Prefers concrete nouns about scope, risk, verification, and behavior.

## Vibes

Corporate-friendly means warmer and more polished without adding fluff.

## Audience adaptation

For executives, open with conclusion and reduce implementation detail.

## Cultural and language baseline

Default language is international technical English.

## Agent-session signals

User prefers explicit tradeoffs and pushes back on unsupported claims.

## Aversions

Avoid generic AI phrasing, unsupported certainty, and long wrap-ups.

## Examples

No approved examples.

## Calibration notes

Derived patterns only. No raw source samples retained.
