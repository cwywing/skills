# skill-authoring

[中文](README.zh-CN.md)

A portable Agent Skill — the **craft layer** for writing production-grade skills.
It sits between the official structural spec (skill-development) and the eval/package
loop (skill-creator).

## Install into a project

```bash
# Cursor
cp -r skill-authoring /path/to/project/.cursor/skills/skill-authoring

# Claude Code
cp -r skill-authoring /path/to/project/.claude/skills/skill-authoring
```

Trigger it by saying "write a skill", "improve my SKILL.md", "why isn't my skill
triggering", or any time you are about to hand a draft to skill-creator.

## Layout

- [SKILL.md](SKILL.md) — workflow + checklist (start here)
- [references/](references/)
  - [descriptions-and-triggering.md](references/descriptions-and-triggering.md) — frontmatter / when to fire
  - [prose-and-formatting.md](references/prose-and-formatting.md) — voice, tone, formatting
  - [instruction-design.md](references/instruction-design.md) — why-over-MUST, effort calibration
  - [examples-and-output-formats.md](references/examples-and-output-formats.md) — few-shot, contrast pairs
- [README.md](README.md) / [README.zh-CN.md](README.zh-CN.md) — this file

Add `scripts/` or `assets/` only when a skill needs deterministic code or output
templates — this meta-skill does not require them.

## Companion skills

- **skill-creator** (official) — test, eval, optimize description, package.
- **skill-development** (official) — frontmatter, anatomy, validation checklist.
- **[harness-first](../harness-first/)** — a complete skill that follows every
  pattern documented here; use it as a reference while drafting.

## Provenance

Patterns trace to the Claude Fable 5 system prompt
([`../CLAUDE-FABLE-5/README.md`](../CLAUDE-FABLE-5/README.md)) and official
skill-creator / skill-development guidance.
