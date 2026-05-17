# Channel conventions

Apply the user's profile inside the shape expected by the channel.

## Slack, Teams, and chat

- Keep one point or one ask per message.
- Prefer a link plus a short note over a long summary.
- Use threads for follow-ups when the channel supports them.
- Do not add greetings or sign-offs unless the user's profile or the conversation clearly calls for them.
- For longer updates, use short paragraphs or a compact list.

## PR descriptions

Default structure:

```markdown
[One-line impact statement]

## Why
[Problem or motivation.]

## What changed
[Reviewer-level summary.]

## Validation
[Tests, checks, screenshots, rollout notes, or why none apply.]
```

Keep background after the impact. Do not include AI attribution or tool footers.

## Code review comments

- One claim per comment.
- State the concern first.
- Explain why it matters if the consequence is not obvious.
- Give a concrete fix or question.
- Use "nit:" only for optional polish.

## Issues and project trackers

- Lead with status, decision, or blocker.
- Link the PR, doc, log, or thread.
- Tag the next owner only when action is needed.
- Keep each comment self-contained because readers see it chronologically.

## Google Docs, Confluence, design docs, RFCs, and ADRs

- Use a short TL;DR for pages over roughly 500 words.
- Use prose for reasoning and tables for comparisons.
- Put open questions at the end with owners when known.
- Separate observed facts from recommendations.
- Preserve the user's documentation shape when a profile exists: context-first,
  decision-first, alternatives-heavy, risk-heavy, terse ADR, or long-form RFC.
- For design docs and RFCs, make alternatives and risks explicit when they are
  real. Do not invent alternatives just to fill a template.
- For ADRs, keep the decision, status, context, consequences, and date easy to
  scan.
- For runbooks, optimize for repeatable action over narrative polish.

## Email

- Subject names the ask or answer.
- First body sentence carries the point.
- Use a sign-off when the relationship or organization expects one.
- External email should define acronyms on first use.

## Release notes and public docs

- Do not imitate private chat quirks.
- Prefer crisp, factual phrasing.
- Keep claims measurable and supported.
- Avoid insider shorthand unless the audience knows it.
