---
name: skill-authoring
description: This skill should be used whenever authoring, drafting, structuring, reviewing, or improving a Claude skill (a SKILL.md and its bundled resources) and the goal is production-grade quality. Trigger it when the user says things like "write a skill", "create a skill for X", "make a SKILL.md", "turn this workflow into a skill", "improve/review my skill", or "why isn't my skill triggering", or when about to hand a skill to skill-creator. It supplies distilled house-style patterns — description/triggering, prose, instruction design, and examples — drawn from a production system prompt and layered on top of the official skill spec. Use it even when the user only says "make a skill for X" without mentioning quality, since a well-crafted skill is always the goal.
version: 0.1.0
---

# Skill Authoring

This skill captures *how to write a skill well* — the craft layer, distilled from a production-grade system prompt (the Claude Fable 5 prompt in `../CLAUDE-FABLE-5/README.md`) and reconciled with the official skill spec. Apply it while drafting any SKILL.md so the result reads like a production system prompt rather than a rough draft.

## What this adds, and how it relates to skill-creator

Most setups already have two official skills:

- **skill-creator** — the process engine: draft → test → eval → iterate → optimize description → package.
- **skill-development** (plugin-dev) — the structural spec: frontmatter, anatomy, progressive disclosure, validation checklist.

This skill is the **craft layer** between them: the prose, triggering, and instruction-design patterns that decide whether a structurally-correct skill is actually followed well by the next model. Compose them — apply these patterns while drafting, then hand the draft to skill-creator for the eval/iterate/package loop. Do not re-implement that loop here.

## The authoring workflow

Follow this in order; skip a step only with a clear reason.

1. **Capture intent.** Establish what the skill enables, when it should trigger, and the expected output. Pull answers from the conversation history first (tools used, steps taken, corrections made) before asking the user to fill gaps.
2. **Research the domain, then bank the knowledge.** Before writing instructions, gather the durable knowledge the skill needs — search the web, read official docs, query internal tools or MCP. Put what a future model will need to reread into `references/` (schemas, APIs, policies, domain facts); put deterministic repeated code into `scripts/`; put output templates into `assets/`. This *is* the "knowledge base": progressive disclosure loads it only when the skill reaches for it. See `references/instruction-design.md` → "Knowledge goes in references, not the body."
3. **Draft to spec, in house style.** Write SKILL.md per the official spec — lean body, imperative voice, third-person pushy description — applying the four pattern files below as you go.
4. **Self-review** against the checklist at the bottom of this file.
5. **Hand off to skill-creator** for test cases, evals, description optimization, and packaging.

## House-style essentials (the 20% to always apply)

- **The description is the only trigger.** The model picks a skill from name + description alone, before it ever sees the body. Spend disproportionate effort here: third person, concrete trigger phrases, lean slightly pushy. → `references/descriptions-and-triggering.md`
- **Lean body, knowledge in references/.** Keep SKILL.md under ~500 lines / ~1.5–2k words; move anything reread-on-demand to `references/`. → `references/instruction-design.md`
- **Imperative voice, explain the why.** Write verb-first instructions and give the reason, rather than stacking ALL-CAPS MUSTs. Reserve absolute imperatives for the few genuinely non-negotiable constraints. → `references/prose-and-formatting.md`, `references/instruction-design.md`
- **Calibrate, don't fix.** Tell the model how to scale effort to the task, not one rigid number. → `references/instruction-design.md`
- **Show, with contrast.** Include Input→Output examples and Correct-vs-Incorrect pairs with a one-line rationale. → `references/examples-and-output-formats.md`

## Reference files (read on demand)

Read the relevant file when you reach that part of drafting:

- **`references/descriptions-and-triggering.md`** — writing the frontmatter description so the skill fires at the right times and not the wrong ones.
- **`references/prose-and-formatting.md`** — voice, tone, formatting discipline, and what *not* to say.
- **`references/instruction-design.md`** — making instructions a model actually follows: why-over-MUST, effort calibration, decision tables, self-checks, and knowledge placement.
- **`references/examples-and-output-formats.md`** — few-shot examples, contrast pairs, and pinning exact output formats.

Each file records its provenance in the Fable 5 system prompt (`../CLAUDE-FABLE-5/README.md`) and the official skill skills, so any pattern traces back to a source.

For a complete skill that follows every pattern here, see `../harness-first/SKILL.md` in this repo.

## Worked example — description rewriting

The highest-leverage edit in any skill is the frontmatter description. Study this contrast before drafting:

**Input** (a one-line user request):
> "make a skill for formatting git commit messages"

**Output** (the description that should result):

```
This skill should be used whenever the user asks to write, format, or improve a
git commit message, or when committing changes and the message needs to follow
team conventions. Trigger on phrases like "write a commit message", "format this
commit", "conventional commits for this diff", or "what should the commit say".
Use it even when the user only says "commit this" without mentioning message
style — a well-formed message is always the goal.
```

**Contrast — description quality:**
- Correct: third person, names concrete trigger phrases, nudges the near-miss ("commit this" without asking for style).
- Incorrect: "Helps with git commit messages."
- Rationale: the model selects skills from description alone; a label with no triggers almost never fires. See `references/descriptions-and-triggering.md`.

## Pre-ship checklist

Frontmatter
- [ ] `name` and `description` present; description in third person with concrete trigger phrases; slightly pushy against undertriggering.
- [ ] Description states both what it does AND when to use it; no "when to use" information hidden in the body.

Body
- [ ] Imperative/infinitive voice throughout (no "you should").
- [ ] Lean (<500 lines / ~1.5–2k words); reread-on-demand material moved to `references/`.
- [ ] Every ALL-CAPS absolute is genuinely non-negotiable; everything else explains its why.
- [ ] Effort, length, and tool-use guidance are calibrated to task difficulty, not a single rigid rule.

Resources
- [ ] Domain knowledge in `references/`; repeated deterministic code in `scripts/`; output templates in `assets/`.
- [ ] Every bundled file is referenced from SKILL.md with a "read when…" pointer.
- [ ] No fact duplicated between SKILL.md and `references/`.

Examples
- [ ] At least one concrete Input→Output example; a Correct-vs-Incorrect contrast wherever a subtle pitfall is likely.

Then hand the draft to **skill-creator** for evals, description optimization, and packaging.
