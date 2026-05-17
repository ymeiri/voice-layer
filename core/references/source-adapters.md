# Source adapters

Use only sources the user approved for this calibration session.

Before using any adapter, run the source menu in `source-menu.md` and record the user's approved scope.

## Local git

Use `scripts/collect_git_samples.py` when the user approves the current repo or a specific repo path.

Local git commit messages are a distinct, lower-signal source for technical writing style. Do not use them as the default substitute for PR descriptions, PR review comments, or issue comments. If the user asks for PR history and no code-hosting connector is visible, ask whether they want to connect/enable a code-hosting source, provide an export/paste, or explicitly fall back to commits.

Good signal:

- non-merge commit messages,
- commit bodies with rationale,
- reviewable branch descriptions if available.

Filter out:

- merge commits,
- reverts unless the user writes detailed rationale,
- generated commit messages,
- dependency bumps with boilerplate.

## Pull requests and code reviews

Use the available code-hosting or forge connector if the user approves the host, org, and repo scope. Examples include GitHub, GitLab, Bitbucket, Gerrit, Azure DevOps, or an internal forge.

If no code-hosting connector is visible but PR/MR voice is important, offer setup or fallback before collecting anything:

- connect or enable the relevant forge connector,
- authenticate a local CLI such as `gh`, `glab`, or an internal forge CLI when available,
- use a user-provided export or pasted samples,
- skip PR/MR sources for this pass,
- explicitly fall back to local git commit messages as a separate lower-signal source.

Ask separately for:

- PR descriptions authored by the user,
- PR review comments written by the user,
- issue comments written by the user.

Do not treat approval for one PR source as approval for the others.

Good signal:

- PR titles and descriptions authored by the user,
- review comments authored by the user,
- issue comments authored by the user.

Do not train on other reviewers' text. Use surrounding thread context only to understand what the user was responding to.

## Issues and project-management tools

Use the available issue/project connector only if the user approves the product, workspace/org, project/board/query, and date range. Examples include Linear, Jira, Asana, Monday.com, Shortcut, Trello, Azure Boards, Notion, GitHub Issues, or an internal tracker.

Ask separately for:

- issue descriptions authored by the user,
- comments written by the user,
- status updates written by the user,
- project docs or specs authored by the user.

Good signal:

- comments where the user explains a decision,
- status updates written in the user's normal work register,
- issue descriptions authored from scratch by the user.

Filter out:

- template text,
- copied specs,
- automation/bot comments,
- comments authored by teammates,
- customer/user text pasted into tickets.

## Slack, Teams, and messengers

Ask for workspace, channels or DMs, date range, and whether exact examples may be retained.

Good signal:

- recent user messages,
- threads where the user explains technical reasoning,
- DMs for casual register if the user approves.

Filter out:

- other people's messages,
- bot messages,
- copied logs,
- incident templates,
- emoji-only acknowledgements unless the user's emoji habits matter.

## Google Docs and Confluence

Ask for exact docs, folders, pages, or search scope. Do not crawl a whole workspace by default.

If docs are relevant and a Google Workspace, Google Drive, or Google Docs connector is not visible, ask whether the user wants to connect or enable it, provide exports or pasted docs, use another docs/wiki source that is available, or skip docs. Do not just mark Google Docs unavailable and continue without offering the connection/setup choice.

Good signal:

- docs the user authored or substantially edited,
- decision docs,
- design docs, RFCs, ADRs, runbooks, and long-form project docs,
- project updates,
- comments written by the user.

Filter out:

- copied specifications,
- meeting transcripts,
- generated summaries,
- shared templates.

For documentation-style calibration, capture:

- document shape: TL;DR use, section order, heading style, and length,
- reasoning habits: context, alternatives, risks, open questions, validation, and decision records,
- density: how much background, examples, diagrams, tables, and citations the user includes,
- audience assumptions: how much context the user expects readers to have.

Do not force all docs into one template. Record how the user actually structures each doc type.

## Email

Ask for mailbox, query, date range, and whether external recipients are in scope.

Good signal:

- sent mail written by the user,
- replies where the user answers a specific ask,
- longer internal explanations.

Filter out:

- quoted prior messages,
- legal footers,
- calendars and auto-replies,
- forwarded content.

## AI agent sessions

Ask for the agent app or export path, project/workspace scope, date range, and approved signal types before reading. Examples include Claude Code, Codex, ChatGPT, Cursor, Windsurf, Continue, and local transcript exports.

Good signal:

- user-authored prompts and follow-up instructions,
- user corrections such as "too fluffy", "less corporate", or "keep my wording",
- explicit style preferences,
- user-edited or explicitly accepted final drafts,
- repeated negative preferences from rejected drafts.

Filter out:

- assistant output unless the user explicitly accepted or edited it,
- rejected assistant drafts as positive style examples,
- tool logs,
- code blocks,
- stack traces,
- pasted third-party messages,
- private content outside the approved scope.

Record agent-session findings separately from final-message voice samples. They are preference signals, not polished writing by default.

## Manual samples

When connectors are unavailable, ask the user to paste 5 to 10 representative samples and label each with channel and audience. This is often enough for a first low-confidence profile.
