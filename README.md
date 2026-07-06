# skills

[中文](README.zh-CN.md)

A collection of portable Agent Skills for Cursor and Claude Code. Each skill is a
self-contained folder under `skills/` that you can copy into a project's skill directory,
or import via Cursor's **Remote Rule (GitHub)**.

## Skills

| Skill | When to use |
|-------|-------------|
| [harness-first](skills/harness-first/) | Starting a **new** project — build a self-verifying harness before writing feature code or prompts |
| [skill-authoring](skills/skill-authoring/) | Writing, reviewing, or improving any SKILL.md to production quality |
| [geo-article-generator](skills/geo-article-generator/) | Turning supplied source materials into a publishable article that generative AI engines can identify, understand, and cite |

They compose: kick off with **harness-first**, then capture stable workflows with
**skill-authoring** once the harness is running. Use **geo-article-generator**
whenever content needs to be legible to generative AI search, not just human readers.

## Install

### Option 1: Cursor Remote Rule (recommended)

1. Open **Customize** → **Rules** → **Add Rule** → **Remote Rule (GitHub)**
2. Enter: `https://github.com/cwywing/skills`
3. Select the skills you want to import

Cursor copies them into `.cursor/skills/` and auto-discovers them.

### Option 2: Manual copy

```bash
# Cursor
cp -r skills/harness-first          /path/to/project/.cursor/skills/harness-first
cp -r skills/skill-authoring        /path/to/project/.cursor/skills/skill-authoring
cp -r skills/geo-article-generator  /path/to/project/.cursor/skills/geo-article-generator

# Claude Code
cp -r skills/harness-first          /path/to/project/.claude/skills/harness-first
cp -r skills/skill-authoring        /path/to/project/.claude/skills/skill-authoring
cp -r skills/geo-article-generator  /path/to/project/.claude/skills/geo-article-generator
```

Both tools auto-discover skills. No extra configuration needed.

## Layout

```
skills/                          # repo root
├── README.md / README.zh-CN.md  # this file
└── skills/                      # skill collection (required for GitHub import)
    ├── harness-first/
    ├── skill-authoring/
    └── geo-article-generator/
```

- [harness-first/](skills/harness-first/) — 5-phase gated project bootstrap
  - [SKILL.md](skills/harness-first/SKILL.md) — main workflow (start here)
  - [references/](skills/harness-first/references/) — templates, gates, methodology
- [skill-authoring/](skills/skill-authoring/) — craft layer for writing skills
  - [SKILL.md](skills/skill-authoring/SKILL.md) — workflow + checklist (start here)
  - [references/](skills/skill-authoring/references/) — triggering, prose, instruction design, examples
- [geo-article-generator/](skills/geo-article-generator/) — generative-AI-legible articles
  - [SKILL.md](skills/geo-article-generator/SKILL.md) — main workflow (start here)
  - [references/](skills/geo-article-generator/references/) — GEO principles, article template, self-check gate

Optional subdirectories (`scripts/`, `assets/`) are created per-skill when needed —
not every skill requires them.

## Provenance

Patterns in **skill-authoring** are distilled from the Claude Fable 5 system prompt
([`../CLAUDE-FABLE-5/README.md`](../CLAUDE-FABLE-5/README.md)) and reconciled with
the official skill-creator / skill-development specs.
