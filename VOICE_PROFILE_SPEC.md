# Voice Profile Spec

`voice-layer` is built around one idea:

```text
Bring your voice to any agent.
Adapt to any audience without losing yourself.
```

The voice profile is the portable artifact that makes this possible. It turns
writing preferences into an inspectable format that currently packaged Claude
Code and Codex integrations can apply consistently. Future agent integrations
should use the same profile model after their package and invocation behavior
are verified.

This document describes the target profile model. The current Agent Skills use
the required subset: Markdown with YAML frontmatter, source coverage,
confidence, privacy metadata, and human-readable voice sections.

The machine-readable schema lives at
[`core/profile/schema.json`](core/profile/schema.json).

## Design Goals

- **Portable:** one profile should work across agents.
- **Inspectable:** users can read and edit it.
- **Consent-first:** calibration sources must be approved before use.
- **Local-first:** profiles stay on the user's machine by default.
- **Measurable:** fields should map to observable writing behavior.
- **Respectful:** culture and language background are not costumes.

## Core Model

```text
voice = stable personal writing baseline
vibe = temporary tone/style overlay
channel = where the message will be sent
audience = who will read it
localization = clarity and convention adjustments
guardrails = facts, consent, privacy, and safety boundaries
```

The profile should not pretend to infer psychology. It should describe how text
is written: sentence rhythm, openings, hedging, disagreement style, formatting,
vocabulary, and channel-specific patterns.

## Subject Types

`profile_subject` defines what the profile is allowed to represent.

| Value | Meaning | Intended use |
| --- | --- | --- |
| `self` | A profile for the local user. | Personal writing assistance. |
| `synthetic_archetype` | A fictional style profile. | Demos, tests, examples. |
| `style_reference` | A documented public or licensed style reference. | Research and evaluation only. |

Living-person impersonation is out of scope for this repo. A style reference
must describe observable rhetorical patterns, not claims about inner traits,
beliefs, or psychology.

## Minimal Frontmatter

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
limitations: []
```

Use `retention: "short-approved-examples"` only when the user approves exact
examples.

When retention is `derived-patterns` and `privacy.approved_exact_examples` is
`false`, the profile must not contain exact user-authored phrase snippets in
any body section. This includes openings, closings, recurring phrases, typos,
emoji phrases, private idioms, relationship-specific jokes, and sentence-level
examples. Store paraphrased tendencies instead.

## Recommended Body Sections

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

The body stays in Markdown so users can understand and correct the profile.

## Voice

Voice is the stable baseline. It should be derived from approved user-authored
samples or explicit user preferences.

Useful fields:

```yaml
voice:
  sentence_length: "short|short-medium|medium|long|varied"
  paragraph_density: "sparse|moderate|dense"
  directness: "low|medium|high"
  warmth: "low|medium|high"
  formality: "low|medium|high"
  hedging: "low|medium|high"
  humor: "none|rare|occasional|frequent"
  opener_patterns: []
  closer_patterns: []
  disagreement_style: "soft|direct-but-respectful|direct|deferential"
  uncertainty_style: "avoid|brief|explicit|qualified"
  vocabulary:
    preferred: []
    avoid: []
    repetition_watchlist: []
  formatting:
    lists: "rare|when-useful|frequent"
    emoji: "never|rare|channel-dependent|frequent"
    dash_usage: "never|rare|occasional|frequent"
    colon_usage: "rare|when-introducing-specifics|frequent"
    repeated_punctuation_patterns: []
```

The profile should capture punctuation texture and repetition habits. Some users
use dashes naturally; others almost never do. The agent should compare drafts to
the calibrated baseline instead of applying a universal punctuation ban.

## Documentation Style

Long-form documents are not just another tone. Design docs, RFCs, ADRs, public
docs, and internal wikis have structure, density, and decision habits that can
be calibrated.

Useful fields:

```yaml
documentation:
  default_doc_types:
    - "design-doc"
    - "rfc"
    - "adr"
    - "runbook"
  structure:
    tldr: "always|over-500-words|rare"
    context_first: true
    decision_first: false
    alternatives_section: "always|when-real|rare"
    risks_section: "always|when-real|rare"
    open_questions_location: "top|near-end|end"
    validation_section: "always|when-technical|rare"
  density:
    detail_level: "brief|moderate|deep"
    background_level: "assume-context|some-context|self-contained"
    examples: "rare|when-useful|frequent"
  reasoning:
    separates_facts_from_recommendations: true
    names_tradeoffs: true
    records_decisions: true
    cites_sources: "inline|links|footnotes|rare"
  formatting:
    heading_style: "plain|question-based|numbered"
    tables: "for-comparisons|rare|frequent"
    diagrams: "when-system-shape-matters|rare|frequent"
```

Documentation calibration should look at user-authored docs and comments, not
generated docs the user did not accept. It should capture how the user scopes a
problem, explains alternatives, records decisions, names risks, and decides how
much context readers need.

## Vibe

A vibe is a temporary overlay. It adapts the draft to a situation without
replacing the user's voice.

Example:

```yaml
vibes:
  corporate-friendly:
    description: "Warm, polished, low-risk, and clear."
    adjustments:
      formality: "+0.25"
      warmth: "+0.15"
      slang: "-0.40"
      humor: "-0.30"
      certainty: "measured"
      closer: "clear-next-step"
  chill-rock-star:
    description: "Relaxed, confident, playful, and punchy."
    adjustments:
      formality: "-0.40"
      energy: "+0.35"
      humor: "+0.20"
      sentence_length: "short-punchy"
      metaphor: "occasional"
      opener: "hook-first"
```

Vibes should be named archetypes, not living-person impersonations.

## Audience Adaptation

Audience adaptation changes how much context, formality, and explanation the
draft needs. It should not erase the user's voice.

Example:

```yaml
audience_adaptation:
  executives:
    open_with_conclusion: true
    summarize_tradeoffs: true
    avoid_internal_jargon: true
  close_teammates:
    context_level: "low"
    formality: "low"
```

## Cultural And Language Baseline

Regional English and cultural communication norms can be part of the user's
voice. They are not interchangeable costumes.

Bad:

```text
Make this Indian English speaker sound like an LA surfer.
```

Better:

```text
Keep my voice, but make this easy for a US startup audience to read.
```

Model this as baseline plus adaptation:

```yaml
cultural_linguistic_baseline:
  language_variant: "en-IN"
  confidence: "observed|stated|unknown"
  notes:
    - "Formal email samples use polite openings."
    - "PR comments are direct and technical."

localization:
  preserve_user_voice: true
  do_not_mimic_target_culture: true
  clarify_nonportable_idioms: true
  spelling_mode: "keep-user-default|adapt-if-requested"
```

## Guardrails

Guardrails override style preferences.

```yaml
guardrails:
  preserve_facts: true
  preserve_identifiers: true
  do_not_impersonate: true
  do_not_infer_private_beliefs: true
  do_not_add_personal_experience: true
  do_not_store_raw_samples_by_default: true
```

## Conflict Resolution

When layers conflict, use this order:

1. Facts, safety, and consent.
2. Channel constraints.
3. User voice.
4. Audience adaptation.
5. Requested vibe.
6. Localization preferences.

This prevents a vibe or audience request from flattening the user's calibrated
voice into generic business English.

## Evaluation Targets

The spec should be testable without claiming perfect voice matching.

Useful checks:

- protected identifiers preserved,
- no new facts,
- AI-tell phrases reduced,
- model-shaped punctuation reduced when it conflicts with the profile,
- repeated vocabulary and sentence scaffolding reduced,
- profile aversions respected,
- selected vibe applied,
- audience adaptation applied,
- document structure follows the selected doc profile,
- user voice not erased,
- no raw private samples leaked.
- no exact user-authored phrase snippets leaked when exact examples were not approved.

Do not claim that generated text is indistinguishable from the user. Prefer
measurable claims such as "reduced AI-tell frequency" or "matched the selected
profile constraints better than baseline."
