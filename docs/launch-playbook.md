# Launch Playbook

This playbook keeps launch copy sharp without overstating what `voice-layer`
does today.

## Positioning

Primary frame:

```text
A local-first personal voice layer for AI agents.
```

Use this when the audience is technical:

```text
Not a prompt library. A local voice profile for Claude Code and Codex.
```

Use this when the audience is broader:

```text
Humanize AI-generated drafts without uploading your writing samples to a hosted humanizer.
```

Do not claim:

- automatic interception of all agent output,
- MCP Registry support,
- Cursor, Windsurf, ChatGPT Skills/API, or native SaaS collector support,
- AI detector bypass,
- `v1.0.0` maturity.

Current accurate claim:

```text
voice-layer supports direct Claude Code and Codex skill installs, Homebrew,
and a validated Claude Code plugin path. The Codex plugin path is still a
release candidate until the desktop plugin UI install is manually verified.
```

## High-ROI Sequence

1. Confirm README first viewport, Homebrew install, CI badge, release badge,
   demo GIF, privacy language, and support matrix are current.
2. Upload `assets/brand/social-preview.png` in GitHub Settings.
3. Post Hacker News `Show HN`.
4. Submit manual PRs to relevant Claude/agent awesome lists.
5. Publish one technical blog post.
6. Use Reddit, Product Hunt, X, and LinkedIn after the first feedback loop.

## Hacker News

Title:

```text
Show HN: voice-layer, a local-first voice profile for Claude Code and Codex
```

First comment:

```text
Hi HN, I built voice-layer because I kept using CLI agents to draft PR
comments, Slack replies, and docs, then rewriting the result so it sounded
less like generic AI prose and more like me.

The project is a local-first personal voice layer for Claude Code and Codex.
It stores an inspectable voice profile at ~/.config/voice-layer/voice-profile.md
and uses that profile when you explicitly ask the agent to write or rewrite
text with the skill.

Install:

  brew tap ymeiri/voice-layer
  brew install voice-layer
  voice-layer install --agent both
  voice-layer doctor --agent both

A few design choices:

- no hosted service and no repo telemetry;
- calibration is consent-first, so the agent asks before reading private
  sources;
- the profile is local Markdown with schema validation;
- the skill checks for common AI writing tells, but this is not an AI detector
  bypass tool;
- current packaged support is Claude Code and Codex. Other agents are not
  claimed until their package and invocation behavior are verified.

I would especially value feedback on the profile contract, install lifecycle,
and whether the local-first boundary is clear enough.
```

Avoid:

- saying it intercepts output automatically,
- saying it runs offline if the active agent still calls its normal model API,
- asking for stars directly.

## Awesome Lists

Candidate targets:

- `hesreallyhim/awesome-claude-code`
- `travisvn/awesome-claude-skills`
- relevant agent-skills directories as they appear

Submission note template:

```text
Hi, I would like to add voice-layer to the list.

voice-layer is an MIT-licensed, local-first personal voice layer for Claude Code
and Codex. It ships Agent Skills for calibrating a local voice profile and using
that profile to rewrite PR comments, Slack replies, docs, RFCs, and emails.

Why it fits this list:

- Claude Code plugin and direct skill install paths are documented.
- Homebrew install is available.
- The README includes a demo GIF, privacy model, support matrix, and release
  checklist.
- The project avoids hosted telemetry and stores the generated profile locally.

Repo: https://github.com/ymeiri/voice-layer
```

Before opening any PR:

- read the target repo's contribution rules,
- match the list's exact ordering and formatting,
- avoid AI-generated-looking PR prose,
- open one PR at a time and respond manually.

## Technical Blog Post

Working title:

```text
Building a local-first voice profile for AI agents
```

Outline:

1. The problem: AI agents are useful, but their drafts flatten personal voice.
2. Why a prompt is not enough: profiles, channel shape, audience, and guardrails
   need to be reusable.
3. The local-first contract: profile location, permissions, no hosted service,
   and consent-first calibration.
4. How `write-in-my-voice` works: profile lookup, channel detection, AI-tell
   cleanup, and output-only responses.
5. Why this is not an AI detector bypass tool.
6. What is supported now: Claude Code, Codex, Homebrew, Claude plugin.
7. What comes next: more agents, better evals, optional MCP only if it becomes
   real.

## Reddit

Use only after participating organically. Suggested title:

```text
I built a local-first voice layer for Claude Code/Codex because AI drafts kept sounding the same
```

Short body:

```text
I use CLI agents heavily for PR comments, Slack replies, and docs, but kept
rewriting the output to remove generic AI phrasing.

I built voice-layer as a local-first solution: it creates an inspectable
voice-profile.md and lets Claude Code/Codex rewrite drafts in that profile when
I explicitly ask it to.

It is not an AI detector bypass tool, and it is not a hosted humanizer. The
point is professional authenticity and local control.

I would value technical feedback on the profile format and privacy boundary.
```

## Product Hunt

Use after HN/awesome-list feedback has settled.

Tagline:

```text
Bring your voice to Claude Code and Codex, locally.
```

Maker comment:

```text
I built voice-layer because AI agents are useful, but their drafts often flatten
personal voice. voice-layer stores a local Markdown voice profile and lets
Claude Code or Codex rewrite drafts in that profile for PR comments, Slack
replies, docs, RFCs, and emails.

It has no hosted service, no repo telemetry, Homebrew install, and explicit
calibration consent. It is not an AI detector bypass tool. It is for developers
who want AI-assisted writing to still sound like them.
```

## X And LinkedIn

Short launch post:

```text
I open-sourced voice-layer.

It is a local-first personal voice layer for Claude Code and Codex: calibrate a
local voice-profile.md, then use it to rewrite PR comments, Slack replies, docs,
RFCs, and emails so AI drafts still sound like you.

No hosted service. No repo telemetry. Homebrew install.

https://github.com/ymeiri/voice-layer
```

Thread idea:

1. AI agents help with writing, but their drafts often collapse into the same
   voice.
2. A prompt is not enough; personal voice needs a reusable local profile.
3. `voice-layer` stores that profile locally and keeps calibration explicit.
4. Demo GIF.
5. Install commands.
6. Ask for feedback on agent support and profile contract.
