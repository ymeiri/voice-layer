# Install

There are four install paths. Homebrew and direct CLI are the primary supported
paths for v0.1.0. Plugin-manager paths remain release candidates until fresh UI
install tests pass.

## Prerequisites

- Claude Code with plugin support for Claude plugin installs.
- Codex with plugin support for Codex plugin installs.
- Python 3 for the direct CLI.
- A restart of the target agent after plugin installation.

## Homebrew install

Use this after the first public release when you want the cleanest install and
update path:

```sh
brew tap ymeiri/voice-layer
brew install voice-layer
voice-layer install --agent both
voice-layer doctor --agent both
```

The Homebrew formula installs the CLI and packaged skill resources only. It does
not modify `~/.claude`, `~/.agents`, or `~/.config`; that remains an explicit
`voice-layer install` step.

Uninstall while preserving your profile:

```sh
voice-layer uninstall --agent both
brew uninstall voice-layer
brew untap ymeiri/voice-layer
```

Delete profile data only when you explicitly mean it:

```sh
voice-layer purge --yes
```

## Direct CLI install

Use this for source checkouts, personal experiments, or when Homebrew is
unavailable.

```sh
./voice-layer install --agent both
```

This copies Claude skills from `packages/claude-code` to `~/.claude/skills` and
Codex skills from `packages/codex` to `~/.agents/skills`. It also creates a
placeholder voice profile at `~/.config/voice-layer/voice-profile.md`, and
refuses to overwrite existing skills unless you pass `--force` or
`--backup-existing`.

Preview the exact file operations first:

```sh
./voice-layer install --agent both --dry-run
```

Run a health check:

```sh
./voice-layer doctor --agent both
```

`doctor` checks only direct skill installs in `~/.claude/skills` and
`~/.agents/skills`. It also reports whether the local voice profile passes the
profile schema checks. Use each agent's plugin UI to verify marketplace installs.

Use a symlink install when you want direct installs to track this checkout:

```sh
./voice-layer install --agent both --mode symlink
```

Uninstall copied skills or symlinks while preserving your profile:

```sh
./voice-layer uninstall --agent both
```

Delete local profile data only with an explicit purge:

```sh
./voice-layer purge --yes
```

## Codex plugin install

Use this when you want the native Codex plugin browser and update path.

Codex reads repo marketplaces from `.agents/plugins/marketplace.json`. The
public marketplace can be added from `ymeiri/voice-layer` and points at
`packages/codex`. Open Codex, run `/plugins`, add the `ymeiri/voice-layer`
marketplace if needed, select `Voice Layer`, and install `voice-layer`.

If Codex does not show the marketplace, use the direct CLI below and run
`voice-layer doctor --agent codex`.

Start a new thread after installing, then test:

```text
Use $write-in-my-voice to rewrite this Slack reply: Great question! It is important to note that we could potentially leverage this.
```

## Claude Code plugin install

Use this when you want Claude Code's native plugin manager and namespaced skills.

From Claude Code, add this repo as a marketplace and install the plugin:

```text
/plugin marketplace add ymeiri/voice-layer
/plugin install voice-layer@voice-layer
```

The Claude marketplace points at `packages/claude-code`.

Restart Claude Code after installing. Plugin skills are namespaced, so test with:

```text
/voice-layer:write-in-my-voice rewrite this Slack reply: Great question! It is important to note that we could potentially leverage this.
```

The `voice-layer:write-in-my-voice` shape is `plugin-name:skill-name`.

## Source install shortcut

`./install.sh --agent both` remains as a small convenience wrapper for
`./voice-layer install --agent both`.

## Homebrew packaging test

The repo includes a local Homebrew formula at
`packaging/homebrew/voice-layer.rb`. It is a packaging proof for the public tap
formula in `packaging/homebrew/voice-layer.public.rb`.

See [packaging/homebrew/README.md](../packaging/homebrew/README.md) for the
local tap setup required by current Homebrew.

## First calibration

Read [../PRIVACY.md](../PRIVACY.md) before calibrating from Slack, email, docs, Confluence, or any private workspace.

After install, ask your agent:

```text
Use $calibrate-my-voice to build my local voice profile from pasted samples.
```

For Claude plugin installs, use:

```text
/voice-layer:calibrate-my-voice build my local voice profile from pasted samples.
```

Start with pasted samples if you want the lowest-friction path. Use connectors or exports only after deciding exactly which sources and date ranges are in scope.

Calibration is the step that makes `write-in-my-voice` personal. The calibrating agent should start by discovering which source tools are available in the current session, then build a source menu from artifact types rather than a fixed vendor list. It may offer pasted samples, PR/MR descriptions authored by you, code review comments written by you, project-management comments or updates, chat messages, docs/comments you authored, sent email, agent-session exports, and optional local git commit messages when the current agent has the tools to collect them. If an important source such as Google Docs is not connected, the agent should ask whether you want to connect or enable it, provide an export/paste, use another source, or skip it. It must wait for your approval for each source and scope before fetching. Before calibration, `write-in-my-voice` still removes common AI writing tells, but it uses a generic direct-writing fallback instead of your voice.
