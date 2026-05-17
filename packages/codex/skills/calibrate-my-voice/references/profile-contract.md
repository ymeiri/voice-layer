# Voice profile contract

The profile is Markdown with YAML frontmatter and structured sections. The
frontmatter gives future agents a stable schema. The body keeps the voice model
inspectable by humans.

The machine-readable schema lives at `core/profile/schema.json` in the repo.

## Required frontmatter

```yaml
schema_version: "1.0"
profile_subject: "self"
profile_name: "personal"
language: "en"
updated_at: "YYYY-MM-DD"
calibrated_by: "agent-or-human"
source_summary:
  - source: "git|github|slack|email|docs|confluence|agent_sessions|manual"
    scope: "repo, channel, query, folder, or pasted sample description"
    date_range: "YYYY-MM-DD..YYYY-MM-DD or unknown"
    sample_count: 0
    retention: "derived-patterns"
confidence: "low|medium|high"
privacy:
  raw_samples_retained: false
  approved_exact_examples: false
limitations:
  - "No email samples included."
```

Use `retention: "short-approved-examples"` only when the user approves exact
examples.

Optional:

```yaml
profile_subject_notes: "Only use for the owner of this profile."
```

## Validation-critical rules

- If `privacy.approved_exact_examples` is `false`, the `## Examples` section
  must contain only `No approved examples.`.
- If `privacy.approved_exact_examples` is `false`, do not store exact
  user-authored openings, closings, recurring phrases, typos, emoji phrases,
  private idioms, or sentence snippets anywhere else in the profile. Describe
  tendencies instead.
- Treat quoted openings, closings, recurring phrases, typos, emoji phrases,
  idioms, or sentence snippets outside `## Examples` as exact examples too.
- Put any explanation about example retention in `## Calibration notes`, not in
  `## Examples`.
- Wrap body prose with normal Markdown line breaks. Avoid very long unbroken
  paragraphs; no profile body line should approach 500 characters.
- Do not write raw pasted samples, transcript dumps, full exports, or large
  verbatim excerpts into the profile.
- Before claiming calibration is complete, look for `scripts/validate_profile.py`
  in the current working directory, the nearest parent repo root, and the skill
  package root. If found, run it against the generated profile and treat any
  failure as blocking.
- If no validator can be found, say where you looked and ask the user to run it
  from the repo checkout. Do not call the profile finalized.

## Interpretation rules

- Treat `profile_subject: self` as a permission boundary. Do not use the profile
  to imitate another person.
- Treat `confidence: low` as a reason to be conservative and ask follow-up
  questions for important drafts.
- Apply channel-specific sections only for their channel.
- Apply documentation style for design docs, RFCs, ADRs, runbooks, wiki pages,
  and public docs.
- Apply vibes as temporary overlays; do not treat them as identities or
  impersonation targets.
- Treat audience adaptation as clarity and context adjustment, not voice
  replacement.
- Treat cultural and language baseline as part of the user's voice. Do not mimic
  target cultures.
- Treat agent-session signals as preference evidence. Assistant-generated text
  is not the user's voice by default.
- Let explicit user preferences override observed habits. Mark those as
  "aspirational" in the profile.
- Hard safety rules in `SKILL.md` override profile preferences.

## Body headings

Use this order:

```markdown
## Summary
## Global voice
## Channel profiles
## Documentation style
## Openings and closings
## Sentence architecture
## Punctuation and formatting
## Punctuation texture
## Hedging and uncertainty
## Pushback and disagreement
## Recurring phrases
## Vocabulary fingerprint
## Vibes
## Audience adaptation
## Cultural and language baseline
## Agent-session signals
## Aversions
## Examples
## Calibration notes
```

## Voice-layer sections

- `Documentation style`: design docs, RFCs, ADRs, runbooks, wiki pages, public
  docs, section order, density, risks, alternatives, decisions, validation,
  tables, diagrams, and citations.
- `Vibes`: explicit user-approved tone overlays such as corporate-friendly or
  chill-rock-star. Do not infer a vibe from a living person.
- `Audience adaptation`: how the user adjusts for executives, peers, customers,
  public readers, or close teammates.
- `Cultural and language baseline`: regional English, spelling conventions,
  idioms, politeness, and directness. Culture is not a costume.
- `Agent-session signals`: prompts, corrections, accepted drafts,
  rejected-draft preferences, and explicit style instructions. Assistant output
  is not the user's voice by default.

## Confidence

- `high`: 50+ useful samples across 3+ channels, user confirmed the profile.
- `medium`: 15+ useful samples across 2+ channels, or one rich channel plus user
  corrections.
- `low`: fewer samples, one narrow channel, stale samples, or no user
  confirmation yet.

## Writing examples

Prefer paraphrases. With derived-pattern retention, `## Recurring phrases`
should describe phrase tendencies, not quote the user's exact wording. If the
user approves exact examples, keep them short and remove names, tokens, URLs,
customer details, and private identifiers.

## Layer priority

When profile sections conflict, preserve facts and safety first, then channel or
document shape, user voice, audience adaptation, requested vibe, and localization
preferences.
