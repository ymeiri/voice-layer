# Patterns that make AI writing sound fake

AI writing often fails in recognizable ways. It sounds polished but generic,
warm but weightless, structured but not actually useful.

`voice-layer` uses this catalog as a cleanup pass. The goal is not to make text
"undetectable" or to hide AI use. The goal is to remove patterns that make real
communication sound inflated, evasive, or machine-shaped.

## Core Principle

Good human writing usually has a job:

- answer a question,
- make a request,
- explain a tradeoff,
- push back,
- record a decision,
- move work forward.

AI-shaped writing often performs helpfulness instead of doing the job. When in
doubt, preserve facts and make the useful part easier to read.

## High-Signal Patterns

| Pattern | Watch for | Rewrite move |
| --- | --- | --- |
| Throat-clearing | "Here is", "Let's dive in", "It is worth noting" | Start with the point. |
| Sycophancy | "Great question", "You're absolutely right" | Answer directly unless the praise matters. |
| Inflated importance | "crucial", "pivotal", "transformative" | Name the concrete effect. |
| Copula avoidance | "serves as", "functions as", "boasts" | Use "is", "has", or the active verb. |
| Generic conclusions | "In conclusion", "moving forward", "exciting times" | Stop at the last concrete point. |
| Rule of three padding | "clear, concise, and actionable" | Keep only real distinctions. |
| Synonym cycling | service/system/platform/solution for one thing | Pick the right noun and repeat it. |
| False ranges | "from X to Y" when no real scale exists | Name the real audience or scope. |
| Vague authority | "experts say", "industry reports" | Cite a source or state the claim plainly. |
| Over-hedging | "could potentially", "may perhaps" | Use one hedge or say what is unknown. |
| Promotional filler | "seamless", "robust", "vibrant" without proof | Replace with specific behavior. |
| Decorative formatting | Excess bold, emoji, title-case headings | Remove unless the channel expects it. |
| Dash dependency | Repeated em dash, double hyphen, or spaced-hyphen asides | Use a sentence, colon, comma, or remove the aside. |
| Statistical repetition | Same connector, adjective, or sentence move repeating | Vary the structure or delete repeated scaffolding. |
| Chatbot artifacts | "Hope this helps", "Let me know if..." | Delete unless it is a real next step. |
| False empathy | "I understand how frustrating..." without context | Name the issue or omit the emotion. |
| Fake precision | "significantly improves" without a measure | Use a real number or a modest claim. |
| Empty contrast | "not only X but also Y" with weak Y | State the actual relationship. |

## Vocabulary To Challenge

Challenge these words when they do not carry specific meaning:

```text
additionally, align, crucial, delve, elevate, empower, enhance, foster,
highlight, landscape, leverage, paradigm, pivotal, robust, seamless,
showcase, streamline, transform, underscore, unlock, utilize
```

Do not run a blind find-and-replace. Some words are correct in context. The
problem is not the word itself; the problem is using a fancy word to avoid a
specific claim.

## Punctuation Texture

AI drafts often have a punctuation fingerprint:

- repeated em dashes,
- double hyphen clause breaks,
- spaced-hyphen asides in consecutive paragraphs,
- balanced fragments that all resolve the same way,
- colons before every list or explanation,
- commas used to stack vague qualifiers.

Do not ban punctuation globally. Preserve real command syntax such as `--agent`
and `npm test -- path`. In prose, double hyphens and spaced hyphens as clause
breaks are usually model-shaped. Prefer a sentence, colon, comma, or deletion.

## Repetition Audit

AI text often repeats high-probability moves:

- "This helps X by doing Y",
- "The key is...",
- "This is not just X; it is Y",
- "By doing this, we can...",
- adjective pairs such as "clear and actionable" or "simple and effective".

Watch for repeated scaffolding even when the exact words differ. The fix is not
to search for one banned phrase. The fix is to ask whether each sentence adds a
new idea, a useful transition, or just a statistically likely shape.

## Structure Audit

Ask these questions before returning a draft:

- Did the draft answer the real ask first?
- Did it add facts the user did not provide?
- Did it preserve technical identifiers exactly?
- Are all sentences the same length?
- Is the punctuation pattern too regular for this user's voice?
- Are connectors, adjectives, or sentence openings repeating?
- Is a list replacing a paragraph that would read more naturally?
- Is politeness covering uncertainty, disagreement, or lack of evidence?
- Is the ending useful, or is it a generic wrap-up?
- Would the same text work for any company, any team, or any person?

## Voice-Layer Rule

Removing AI tells is not enough.

`voice-layer` should first preserve the user's calibrated voice, then adapt to
channel, audience, and requested vibe. The cleanup pass should never flatten the
user into generic business English.

```text
voice + vibe + channel + audience + guardrails -> usable draft
```

When these conflict, preserve facts and safety first, then preserve the user's
voice, then apply the requested adaptation as lightly as possible.

## Example

Before:

```text
Great question! It is important to note that we can leverage this robust
approach to streamline the workflow and unlock significant value moving
forward.
```

After:

```text
Yes. This should simplify the workflow. The main tradeoff is that we need to
own the migration path instead of leaving it to each team.
```

The rewrite does not just remove banned words. It replaces generic optimism
with a concrete claim and a real tradeoff.
