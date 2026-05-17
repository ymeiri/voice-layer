# Support Matrix

`voice-layer` is meant to become a portable voice layer for many agents. That is
the product direction, not a blanket support claim for every agent today.

This page is the support boundary for the current repo.

## Support Levels

- **Supported:** package or installer exists, automated checks cover it, and the
  install path is documented.
- **Release candidate:** package metadata exists and validates, but still needs
  a fresh manual install test before public launch.
- **Experimental:** design direction exists, but the repo should not advertise
  support yet.
- **Not supported:** do not claim support.

## Current Matrix

| Surface | Level | Install path | Verified now | Remaining gap |
| --- | --- | --- | --- | --- |
| Claude Code direct skills | Supported | `./voice-layer install --agent claude` installs from `packages/claude-code` into `~/.claude/skills` | Temp-HOME install, doctor, uninstall, purge, RC-0 fresh calibration, and RC-0 write smoke test | Keep RC-0 fixtures passing as behavior evolves |
| Claude Code plugin | Release candidate | `/plugin marketplace add .` then `/plugin install voice-layer@voice-layer` from `packages/claude-code` | `claude plugin validate .` passes | Fresh Claude Code plugin install and invocation test |
| Codex direct skills | Supported | `./voice-layer install --agent codex` installs from `packages/codex` into `~/.agents/skills` | Temp-HOME install, doctor, uninstall, purge, and RC-0 write smoke test | Keep RC-0 fixtures passing as behavior evolves |
| Codex plugin | Release candidate | Codex plugin marketplace metadata points at `packages/codex` | Repo validator checks marketplace and plugin metadata | Fresh Codex plugin UI install test |
| ChatGPT Skills / API | Experimental | None yet | Profile model is portable in principle | Package/upload path and runtime behavior not verified |
| Cursor | Not supported | None | Cursor can be a calibration source if the user provides approved session exports | Cursor package format, invocation behavior, and validation are not verified |
| Windsurf / Continue / other agents | Not supported | None | They can be calibration sources if the user provides approved exports | No package, install, or invocation behavior verified |

## Current Claim

The repo may say:

```text
Bring your voice to any agent.
```

as the long-term direction.

The repo should also say:

```text
Current packaged support: Claude Code and Codex.
Cursor and other agents are not supported until verified.
```

Fresh direct-skill validation evidence is recorded in
[rc0-results.md](rc0-results.md).

## Adapter Split Status

The current repo has separate package roots for supported runtimes:

- `packages/claude-code`
- `packages/codex`

Shared behavior, reference files, the profile template, and the local git
collector are canonical under `core/` and synced into each package by
`scripts/sync_core.py`.

Runtime-specific package metadata can now diverge without forking the behavior
model. Do not add runtime-specific metadata until that runtime's validator or
fresh install flow accepts it.

## Source Collection Support

The calibration skill can negotiate sources from whatever tools the active agent
has available. That is not the same as this repo shipping tested collectors for
every vendor.

Current source-collection status:

- Pasted samples: supported by workflow.
- Local git commit messages: supported by bundled helper script, but treated as
  an optional lower-signal source rather than a substitute for PR descriptions
  or code review comments.
- GitHub, GitLab, Slack, email, Google Docs, Confluence, Linear, Asana,
  Monday.com, and similar tools: procedural guidance only unless the active
  agent already has a connector, the user connects/enables one during setup, or
  the user provides an export.

Do not claim native vendor integrations until collectors or connector-specific
workflows are implemented and tested.
