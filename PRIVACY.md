# Privacy

`voice-layer` is designed to personalize writing without turning private messages into a dataset.

## What stays local

- The generated voice profile is stored locally at `~/.config/voice-layer/voice-profile.md` by default.
- Raw source exports and temporary calibration notes should be deleted after the profile is written.
- The repo ignores `voice-profile.md`, sample exports, and local calibration work directories.

## No silent telemetry guard

The repo includes a CI-backed guard:

```sh
python3 scripts/check_no_silent_telemetry.py
```

It scans the executable repo surface for known network and telemetry imports,
network-capable shell commands, and telemetry/network dependencies. This is a
static guardrail against accidentally adding hidden data paths to the CLI,
installer, validators, and bundled skill scripts.

This guard is not a sandbox and does not claim to audit Claude Code, Codex,
model providers, MCP servers, or third-party connectors. If a future source
adapter needs network access, it must be explicit, opt-in, documented, and
updated in the guard in the same change.

`derived-patterns` retention means raw samples are not stored in the generated
profile and skill-created temporary files should be deleted after analysis. It
does not guarantee that the active AI agent, connector, MCP server, or host
application deletes its own session transcripts or tool-result artifacts.

## What may leave the machine

Calibration is performed by the active AI agent. If that agent sends read context to a hosted model provider, snippets or summaries of private source material may be sent to that provider during the session.

Some agent hosts also persist local session logs or tool outputs. When using
connectors for Slack, email, docs, PRs, or similar private sources, assume raw
source material may appear in those session artifacts even when the final
profile keeps only derived patterns.

The calibration skill therefore requires the agent to:

- ask before reading each source,
- gather only user-authored text,
- avoid other people's messages except as minimal reply context,
- summarize patterns instead of storing raw messages,
- ask before keeping any exact user-authored phrase or example,
- disclose that connector reads may create host-managed session or tool logs,
- delete skill-created temporary raw files after analysis,
- show the generated profile for user correction.

## Source rules

| Source | Consent | Retention default |
| --- | --- | --- |
| Git commits | Ask once per repository | Derived patterns unless exact examples are approved |
| PR descriptions/reviews | Ask once per host/org/repo scope | Derived patterns unless exact examples are approved |
| Slack or chat exports | Ask per workspace/channel/export | No raw quotes by default |
| Google Docs or Confluence | Ask per folder/page/doc scope | Derived patterns only unless approved |
| Email | Ask per mailbox/query scope | No raw quotes by default |

## Do not use for impersonation

Use these skills for your own writing or for an explicitly authorized style guide. Do not use them to impersonate another person, forge approval, or hide authorship where disclosure is required.
