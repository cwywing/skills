# skills

[中文](README.zh-CN.md)

A collection of portable Agent Skills for Cursor and Claude Code. Each skill is a
self-contained folder you can copy into a project's skill directory.

## Skills

| Skill | When to use |
|-------|-------------|
| [harness-first](harness-first/) | Starting a **new** project — build a self-verifying harness before writing feature code or prompts |
| [skill-authoring](skill-authoring/) | Writing, reviewing, or improving any SKILL.md to production quality |

They compose: kick off with **harness-first**, then capture stable workflows with
**skill-authoring** once the harness is running.

## Install

Copy the skill folder into your project's skill directory:

```bash
# Cursor
cp -r harness-first   /path/to/project/.cursor/skills/harness-first
cp -r skill-authoring /path/to/project/.cursor/skills/skill-authoring

# Claude Code
cp -r harness-first   /path/to/project/.claude/skills/harness-first
cp -r skill-authoring /path/to/project/.claude/skills/skill-authoring
```

Both tools auto-discover skills. No extra configuration needed.

## Layout

- [README.md](README.md) / [README.zh-CN.md](README.zh-CN.md) — this file
- [harness-first/](harness-first/) — 5-phase gated project bootstrap
  - [SKILL.md](harness-first/SKILL.md) — main workflow (start here)
  - [README.md](harness-first/README.md) / [README.zh-CN.md](harness-first/README.zh-CN.md)
  - [references/](harness-first/references/) — templates, gates, methodology
    - [templates.md](harness-first/references/templates.md)
    - [decision-gates.md](harness-first/references/decision-gates.md)
    - [methodology.md](harness-first/references/methodology.md)
- [skill-authoring/](skill-authoring/) — craft layer for writing skills
  - [SKILL.md](skill-authoring/SKILL.md) — workflow + checklist (start here)
  - [README.md](skill-authoring/README.md) / [README.zh-CN.md](skill-authoring/README.zh-CN.md)
  - [references/](skill-authoring/references/) — triggering, prose, instruction design, examples
    - [descriptions-and-triggering.md](skill-authoring/references/descriptions-and-triggering.md)
    - [prose-and-formatting.md](skill-authoring/references/prose-and-formatting.md)
    - [instruction-design.md](skill-authoring/references/instruction-design.md)
    - [examples-and-output-formats.md](skill-authoring/references/examples-and-output-formats.md)

Optional subdirectories (`scripts/`, `assets/`) are created per-skill when needed —
not every skill requires them.

## Provenance

Patterns in **skill-authoring** are distilled from the Claude Fable 5 system prompt
([`../CLAUDE-FABLE-5/README.md`](../CLAUDE-FABLE-5/README.md)) and reconciled with
the official skill-creator / skill-development specs.
