# Implementation Roadmap

This roadmap defines what "complete implementation" means for `voice-layer`.
It keeps the current repo honest while preserving the path toward "bring your
voice to any agent."

## Definition Of Complete

A complete implementation has:

- one canonical voice profile model,
- agent-specific packages for each supported runtime,
- profile validation and activation,
- behavioral evals for writing and calibration,
- tested source collection workflows,
- clear privacy and impersonation boundaries,
- fresh install verification for each claimed surface.

## Principles

- Keep voice behavior canonical. Do not let Claude, Codex, Cursor, or another
  adapter drift into different safety or calibration rules.
- Let packages be native. Each agent should get the metadata, install path, and
  invocation shape that fits that agent.
- Do not claim support for a platform until its install and invocation flow has
  been verified.
- Keep raw samples out of the repo and out of generated packages.

## Phase 0: Current State

Status: RC-0 passed for direct Claude Code and Codex skills. See
[rc0-results.md](rc0-results.md).

The repo currently contains canonical core behavior plus agent-specific package
roots for Claude Code and Codex:

- `core/`
- `packages/claude-code`
- `packages/codex`

Current validation covers:

- repository structure,
- marketplace metadata,
- core/package sync,
- skill frontmatter portability,
- example fixtures,
- direct install lifecycle,
- Claude marketplace validation,
- fresh calibration in Claude Code,
- real Claude Code and Codex write smoke tests,
- sanitized real-agent behavior fixtures for the feature-flag/no-rollout
  regression.

## Phase 1: Support Boundaries

Status: complete for current claims. Continue maintaining this as support
changes.

Tasks:

- Maintain [support-matrix.md](support-matrix.md) as the public support source
  of truth.
- Keep README claims aligned with the support matrix.
- Avoid advertising Cursor, Windsurf, Continue, ChatGPT, or API support until
  each surface has a package and verified install path.

Acceptance:

- README links to the support matrix.
- Release checklist includes support-claim review.
- Stale unsupported-platform claims are absent.

## Phase 2: Core And Adapter Split

Status: complete for current supported runtimes. Shared skill bodies, shared
references, the profile template, and the local git collector have canonical
`core/` sources. `scripts/sync_core.py` syncs those files into Claude Code and
Codex packages while package frontmatter and plugin metadata remain
adapter-specific.

Target structure:

```text
core/
  skills/
    write-in-my-voice.md
    calibrate-my-voice.md
  references/
  profile/
    voice-profile.template.md
  scripts/
    collect_git_samples.py

packages/
  claude-code/
    .claude-plugin/
    skills/
  codex/
    .codex-plugin/
    skills/
```

Tasks:

- Move shared behavioral instructions into `core/`. Done for skill bodies,
  profile contract, source negotiation references, writing references, profile
  template, and local git collector.
- Generate or sync package-specific `SKILL.md` files from core. Done with
  `scripts/sync_core.py`, which syncs body text while preserving package
  frontmatter.
- Allow Claude Code package metadata to use Claude-valid fields where useful.
  Done structurally by creating `packages/claude-code`.
- Keep Codex package metadata Codex-valid. Done structurally by creating
  `packages/codex`.
- Add a packaging validator that checks generated packages are in sync with
  core. Done in `scripts/validate_repo.py`.

Acceptance:

- Claude package passes `claude plugin validate .`.
- Codex package passes repo Codex package validation.
- Shared behavior changes are made once in core and reflected in all supported
  packages by `scripts/sync_core.py --check`.

## Phase 3: Profile Validation And Activation

Status: in progress. The `1.0` schema baseline is explicit and validated, and
deterministic behavior checks now cover profile activation and fake
personalization boundaries. The remaining work is live activation quality:
making calibration produce a useful profile and capturing real-agent proof that
writing skills apply it reliably across channels.

Tasks:

- Maintain `scripts/validate_profile.py`. Done.
- Keep the machine-readable schema in `core/profile/schema.json`. Done.
- Validate required frontmatter keys, schema version, source coverage,
  confidence, privacy markers, and required body sections. Done.
- Detect likely raw corpus leakage, long private quotes, and missing source
  limitations. Done with blocking errors for leakage and warnings for empty
  limitations.
- Add profile activation checks for writing tasks so valid profiles are loaded
  and missing or invalid profiles do not produce fake personalization. Done for
  deterministic behavior evals; real-agent captures still pending.
- Add calibration quality checks for first-run setup: consent, source coverage,
  confidence, user correction, and validator pass before completion. Pending.

Acceptance:

- Placeholder and calibrated sample profiles can be validated.
- Invalid profiles fail with actionable messages.
- Install doctor can report profile schema health.
- Writing flows prove whether a valid profile was available and applied without
  leaking profile internals.
- First-run calibration produces a validated profile with clear source coverage,
  limitations, and confidence.

## Phase 4: Behavioral Evals

Status: deterministic and real-capture validation are active. RC-0 added
passing Claude Code and Codex captured fixtures. Qualitative judging is still
pending.

Tasks:

- Maintain behavioral eval fixtures for:
  - consent negotiation,
  - refusing third-party voice training,
  - preserving identifiers,
  - avoiding invented facts,
  - AI-tell cleanup,
  - audience adaptation without cultural mimicry,
  - documentation/RFC structure,
  - agent-session calibration.
- Keep RC-0 captured outputs from Claude Code and Codex passing, and add more
  real captures when new behavior contracts are hardened.
- Add qualitative or rubric-based checks for real generated outputs.

Acceptance:

- Evals catch regressions in consent, safety, fact preservation, and voice
  application.
- Evals can run locally without private data.
- Scenario rubrics are reusable by human reviewers or LLM judges.

## Phase 5: Source Collection Workflows

Tasks:

- Keep pasted samples as the baseline path.
- Harden local git collection.
- Add connector-specific workflows only when they can be scoped, tested, and
  consent-gated.
- Start with high-value engineering artifacts:
  - PR descriptions,
  - PR review comments,
  - issue comments,
  - design docs/RFCs,
  - agent session transcripts.

Acceptance:

- Every collector requires explicit scope before reading.
- Collectors retain derived patterns, not raw corpora.
- Each collector has tests or reproducible fixtures.

## Phase 6: Additional Agent Adapters

Order:

1. Claude Code package.
2. Codex package.
3. Cursor experimental package after verifying current Cursor skill behavior.
4. Other agents only after package and invocation behavior are verified.

Cursor-specific open questions:

- Where should user-level and project-level skills live?
- Which frontmatter keys are accepted?
- Does disabled auto-invocation work for custom skills?
- How should install/update work for an open-source repo?
- How do Cursor rules interact with skills when both are present?

Acceptance:

- The support matrix is updated only after a fresh install and invocation test.
- Experimental packages are clearly labeled.

## Phase 7: Public Launch Readiness

Tasks:

- Fresh install tests on real Claude Code and Codex environments.
- Final privacy review.
- Final README pass.
- Demo assets based on synthetic profiles only.
- Marketplace submission checklist.

Acceptance:

- No unsupported support claims.
- No private samples or local settings in git status.
- Release checklist is complete.
