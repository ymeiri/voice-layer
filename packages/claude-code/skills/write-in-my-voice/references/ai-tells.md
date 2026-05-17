# AI writing tells

Use this catalog during the self-audit pass. The goal is not to make text "undetectable"; it is to remove patterns that make useful writing sound generic, inflated, or machine-shaped.

## High-signal patterns

| Pattern | Watch for | Rewrite move |
| --- | --- | --- |
| Throat-clearing | "Here is", "Let's dive in", "It is worth noting" | Start with the point |
| Sycophancy | "Great question", "You're absolutely right" | Answer directly |
| Inflated importance | "crucial", "pivotal", "transformative" | Name the concrete effect |
| Copula avoidance | "serves as", "functions as", "boasts" | Use "is", "has", or the active verb |
| Generic conclusions | "In conclusion", "moving forward", "exciting times" | Stop at the last concrete point |
| Rule of three | Padded triplets | List the actual items |
| Synonym cycling | service/system/platform/solution for one thing | Pick the right noun and repeat it |
| False ranges | "from X to Y" when no real scale exists | Name the real audience or scope |
| Vague authority | "experts say", "industry reports" | Cite a source or state the claim plainly |
| Over-hedging | "could potentially", "may perhaps" | Use one hedge or say what is unknown |
| Promotional language | "seamless", "robust", "vibrant" without proof | Replace with specific behavior |
| Decorative formatting | Excess bold, emojis, title-case headings | Remove unless the channel expects it |
| Dash dependency | Repeated em dash, double hyphen, or spaced-hyphen asides | Use a sentence, colon, comma, or remove the aside |
| Statistical repetition | Same connector, adjective, or sentence move repeating | Vary the structure or delete repeated scaffolding |
| Chatbot artifacts | "Hope this helps", "let me know" | Delete |

## Vocabulary to challenge

Challenge these words when they do not carry specific meaning:

```text
additionally, align, crucial, delve, enhance, foster, highlight, landscape,
leverage, paradigm, pivotal, robust, seamless, showcase, underscore, utilize
```

Do not run a blind find-and-replace. Some words are correct in context.

## Punctuation texture

AI drafts often overuse repeated em dashes, double hyphen clause breaks,
spaced-hyphen asides, colons before every explanation, and evenly balanced
fragments. Do not ban punctuation globally. Preserve real command syntax such
as `--agent` and `npm test -- path`. In prose, prefer a sentence, colon, comma,
or deletion over `--`, ` - `, or an em dash clause break.

## Repetition audit

Watch for repeated high-probability moves even when the exact words differ:

- "The key is..."
- "This helps X by doing Y"
- "By doing this, we can..."
- "This is not just X; it is Y"
- adjective pairs such as "clear and actionable"

Keep only the sentences that add a new idea, useful transition, or necessary
emphasis.

## Structure audit

Ask:

- Did the draft answer the real ask first?
- Did it add facts the user did not provide?
- Are the sentences all the same length?
- Is the punctuation pattern too regular for this user's voice?
- Are connectors, adjectives, or sentence openings repeating?
- Is a list replacing a paragraph that would read more naturally?
- Is any politeness covering uncertainty or disagreement?
- Did the draft preserve technical identifiers exactly?
