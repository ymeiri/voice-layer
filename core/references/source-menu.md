# Source menu

Use this before collecting samples. The goal is to make source choice explicit and interactive without assuming a specific company tool stack.

## Step 1: Discover available sources

Do a metadata-only capability inventory before asking the user what to collect. Do not query private content during this step.

Look for:

- connected apps or MCP tools visible to the current agent,
- local CLIs that are already available and authenticated,
- local repositories,
- export files or paths the user mentioned,
- source types the user explicitly named.

Classify each possible source as:

- `available directly`: the agent has a connector/tool/CLI it can use after consent,
- `connectable`: the source is not visible now, but the user may be able to enable a connector, plugin, CLI auth, or workspace connection in the current agent,
- `available by export/paste`: the user can provide data, but the agent cannot fetch it directly,
- `unavailable`: no connector, CLI, export, or paste path is available yet.

If the environment has tool discovery, use it to identify connector names. If not, ask the user which tools they use instead of guessing.

If an important category is not directly available but is commonly connector-backed, ask whether the user wants to connect or enable it, provide an export or paste, use a different tool, or skip it. Do not silently downgrade it to paste/export only.

If a question UI or picker cannot show every relevant source category, do not
use it as the source menu. Switch to plain text and preserve every discovered
or connectable category. A UI limit is not a reason to drop Google Docs,
email, agent sessions, docs/wiki sources, or any other available category.

## Step 2: Build the menu from artifact types

Use artifact categories, then name the local tool examples in parentheses. Do not make Jira, Linear, Asana, Monday, GitHub, Slack, Google Docs, or any other product mandatory.

Common categories:

- pasted samples or exports,
- pull request or merge request descriptions,
- code review comments,
- issue/project-management comments or updates,
- chat messages,
- docs/wiki/pages, RFCs, design docs, ADRs, runbooks, and comments,
- sent email,
- AI agent session transcripts and exports,
- local git commit messages,
- support/customer replies,
- other user-authored workplace writing.

Examples of tools that may fit those categories:

- code review: GitHub, GitLab, Bitbucket, Gerrit, Azure DevOps,
- issues/project work: Linear, Jira, Asana, Monday.com, Shortcut, Trello, Azure Boards, Notion, GitHub Issues, internal trackers,
- chat: Slack, Teams, Discord, Mattermost, Matrix, internal chat,
- docs: Google Docs, Confluence, Notion, SharePoint, Dropbox Paper, internal wiki,
- email: Gmail, Outlook, local mail exports.
- agent sessions: Claude Code, Codex, ChatGPT, Cursor, Windsurf, Continue, local transcript exports.

## First question template

Ask a concise question like this, adapted to the actual capability inventory:

```text
Which sources should I use for calibration?

I can use pasted samples. I can also collect user-authored samples from tools that are available in this session, but only after you approve the source and scope.

Options:
1. Pasted samples or exports
2. PR/MR descriptions I authored ([available tool names, connect/setup, or paste/export])
3. Code review comments I wrote ([available tool names, connect/setup, or paste/export])
4. Issue/project-management comments or updates I wrote ([available tool names, connect/setup, or paste/export])
5. Chat messages I wrote ([available tool names, connect/setup, or paste/export])
6. Docs/wiki pages, RFCs, design docs, ADRs, runbooks, or comments I authored ([available tool names, connect/setup, or paste/export])
7. Sent email ([available tool names, connect/setup, or paste/export])
8. AI agent session history: my prompts, corrections, accepted drafts, and explicit style preferences ([available tool names, connect/setup, or paste/export])
9. Local git commit messages (available locally, lower signal than PR descriptions/review comments)
10. Other workplace writing you want included

For each source you choose, tell me the scope and date range. I will not read a source until you approve it.

Retention note: derived patterns only means I will not store raw samples in the
voice profile or in skill-created temp files after analysis. The active agent or
connector host may still keep session/tool logs outside the profile.
```

If the agent cannot access a category, label it as unavailable and offer paste/export fallback:

Example: "I can access Linear and Slack in this session, but I do not see a GitHub connector. I can collect Linear comments and Slack messages if you approve scope, and you can paste/export PR comments if you want that signal."

If a docs source is relevant but no docs connector is visible, ask a setup question:

Example: "I do not see a Google Drive/Docs connector in this session. Do you want to connect or enable Google Workspace now, provide exported/pasted docs, use a different docs source such as Confluence or Notion, or skip docs for this pass?"

If Google Docs/Gmail or another connector-backed category appears as
`connectable`, include it in the menu with explicit choices: connect/enable,
export/paste, use another source, or skip. Do not list it only in the inventory
and omit it from the choices.

## Required fields per approved source

Before fetching, collect:

- source type,
- tool/product name when relevant,
- exact scope (repo, org, workspace, channel, mailbox query, doc/folder/page, export path),
- date range or sample limit,
- author identity to filter on,
- retention preference: derived patterns only, or short approved examples after review.

Also disclose that retention mode controls the profile and skill-created working
files, not every transcript or tool artifact the active agent host may keep.

For connectable sources, also ask whether the user wants to connect or enable the source now, provide export/paste samples, choose another source, or skip it.

For agent sessions, also collect:

- agent app or transcript format,
- project/workspace scope,
- which signal types are approved: user turns, corrections, accepted drafts, rejected drafts as negative preference signals,
- whether tool logs, code blocks, pasted third-party messages, and assistant outputs must be excluded.

## Collection rules

- Treat no answer as no permission.
- Do not combine consent. Approval for Slack does not imply approval for email, PRs, docs, or issues.
- Do not fetch "everything". Ask for a narrower repo, workspace, channel, query, page, folder, or date range.
- Do not treat "I use Linear" as approval to read Linear. It only makes Linear eligible for the menu.
- Do not substitute local git commits for PR/MR descriptions or code review comments unless the user explicitly accepts that fallback.
- If an approved source returns only metadata, zero usable user-authored samples,
  or a connector/auth/tool failure, do not count it as collected evidence. Ask
  whether to retry, connect/authenticate, provide export or pasted samples,
  skip the source, or proceed with the remaining sources.
- Use only user-authored text as voice signal.
- Use surrounding context only to understand the user's message, not as voice examples.
- Treat accepted user-authored docs as documentation-style signal: structure,
  section order, length, risk framing, alternatives, decision records, examples,
  and citation/link habits.
- Do not treat generated docs as the user's documentation style unless the user
  explicitly accepted or edited them.
- Treat agent sessions as high-noise, high-sensitivity data. User turns and user
  corrections are evidence. Assistant output is not the user's voice by default.
  Accepted drafts can be used only when acceptance or user edits are explicit.
  Rejected drafts are negative preference signals, not style samples.
- If the user says "whatever you think is best", propose a concrete source plan and wait for approval.

## Recommended first calibration plan

When the user has no preference and tools are available, recommend:

- 20 to 50 PR descriptions or review comments for technical written voice,
- 30 to 80 chat messages for casual register,
- 10 to 20 pasted samples for fast setup,
- local git commits only when the user wants commit-message style or accepts commits as a lower-signal fallback,
- optional docs/RFCs/design docs/email only if the user wants formal or
  long-form writing coverage.

Explain that more sources improve coverage but increase privacy review surface.
