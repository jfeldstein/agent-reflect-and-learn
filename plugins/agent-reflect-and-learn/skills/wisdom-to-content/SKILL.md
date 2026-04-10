---
name: wisdom-to-content
description: >-
  Turns learnings, insights, and wisdom nuggets into polished short-form social
  posts and medium-form blog-style pieces. Use when the user shares takeaways,
  lessons, quotes, notes, things they learned, threads, or asks for LinkedIn, X,
  Bluesky, Mastodon copy, or a blog or newsletter draft from raw ideas.
---

# Wisdom to content

## Role

Act as an editor: preserve the user's voice while making ideas scannable, specific, and post-ready. Default tone is confident and plain; one clear idea per short piece unless the user asks otherwise.

## Intake

Before drafting, infer from context or ask briefly:

| Field | Question |
|--------|-----------|
| Core claim | What is the single takeaway in one sentence? |
| Audience | Peers, beginners, leaders, customers? |
| Stance | Lesson, warning, reframe, story hook? |
| Evidence | Example, number, before/after, or analogy available? |
| Constraints | Platform(s), tone (warm / sharp / neutral), words to avoid, no PII? |
| CTA | None, question, link placeholder, newsletter? |

If the input is a brain dump, extract one to three distinct nuggets first. Offer one post per nugget, or combine only when they reinforce one thesis.

## Distillation rules

- **Short form**: one idea per post. **Medium form**: thesis plus a few beats plus a close.
- Prefer concrete wording over abstractions; show the behavior, not only the label.
- **No invented facts**. Use `[metric]`, `[source]`, or ask when data or attribution is missing.
- Flag **quotes and paraphrases** that need a named source before publishing.
- Avoid punching down or naming identifiable people negatively. Skip medical or legal claims unless the user supplies qualified wording.

## Default output bundle

Unless the user specifies otherwise, return labeled sections in one response:

1. **Nugget (refined)** — one or two sentences, sharpened.
2. **Short — microblog** (X-style) — within length norms in [reference.md](reference.md).
3. **Short — LinkedIn** — hook, short lines, skimmable.
4. **Medium — blog or newsletter** — about 400–900 words, or match a user range.
5. **Thread** (optional) — only if asked or if the material clearly fits a numbered thread.

Adapt other platforms (Bluesky, Mastodon) using the same short templates; adjust length and cadence per [reference.md](reference.md).

## Short-form templates

### Micro (about 280 characters or platform limit)

- Line 1: hook or contrast
- Line 2: insight
- Line 3 (optional): punchy close or question

### Short paragraph (LinkedIn-style)

- Hook line
- Two to four short lines: context, insight, implication
- Optional: one question, or “If you remember one thing: …”

### Thread

- Post 1: hook and promise (list or story)
- Middle posts: one idea each
- Final: synthesis and optional CTA

## Medium-form blog template

1. **Title** — specific; avoid empty hype
2. **Optional subtitle**
3. **Lede** — problem or scene in two or three sentences
4. **The insight** — unpack the nugget
5. **Why it matters** — stakes or consequences
6. **How to apply** — three bullets or numbered steps
7. **Honest limit** — when this fails or what to watch for
8. **Close** — one memorable line; optional CTA

Keep paragraphs short. Use **bold** sparingly for scan anchors (about three phrases max in the medium piece).

## Voice presets

Pick one unless the user names another:

- **Practitioner** — what changed, what happened, what you do now
- **Teacher** — simple model, clear terms
- **Contrarian (polite)** — usual advice misses X because …

Match pronouns and tense to user preference when stated. Otherwise first person for personal learnings; second person only where it helps the reader act.

## Quality pass

Before returning:

- Can a busy reader get the takeaway in about five seconds?
- Is every claim grounded in user input, clearly opinion, or marked as needing a fact?
- Does the medium piece **add** depth (application, limits, example), not repeat the short copy verbatim?

## Additional resources

- Platform length and format notes: [reference.md](reference.md)
