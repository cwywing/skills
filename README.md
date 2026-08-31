# skills

[中文](README.zh-CN.md)

A collection of portable Agent Skills for Cursor and Claude Code. Each skill is a
self-contained folder under `skills/<name>/` (a `SKILL.md` plus optional
`scripts/`, `references/`, `assets/`, `tests/`). Copy that folder into a project's
skill directory, or install with `gh skill`.

The GitHub repo is named `skills`; the inner `skills/` directory is the
[Agent Skills](https://agentskills.io/specification) **collection** layout
(`skills/*/SKILL.md`) that `gh skill install` scans. They are not the same
thing as Cursor's install path (`.cursor/skills/<name>/`). Do not flatten
skill folders onto the repo root — installers will miss them.

## Skills

| Skill | When to use |
|-------|-------------|
| [harness-first](skills/harness-first/) | Starting a **new** project — build a self-verifying harness before writing feature code or prompts |
| [skill-authoring](skills/skill-authoring/) | Writing, reviewing, or improving any SKILL.md to production quality |
| [geo-article-generator](skills/geo-article-generator/) | Turning supplied source materials into a publishable article that generative AI engines can identify, understand, and cite |
| [ai-dev-pipeline](skills/ai-dev-pipeline/) | Splitting a plan into ordered tasks and continuously delivering via Cursor Agent CLI (`agent -p --force`) |
| [admin-console-ux](skills/admin-console-ux/) | Polishing admin / 管理后台 UX so display and interaction match mid-console **ops habits** |
| [h5-style-unify](skills/h5-style-unify/) | Unifying style/color/design for an **existing** H5 / mobile-web project — token SoT, machine gate, acceptance page |
| [swiftui-style-unify](skills/swiftui-style-unify/) | The same five-ring unification for an **existing** SwiftUI / iOS app — `DesignTokens` namespace, Dynamic Type typography, ripgrep gate, shared-SoT codegen |
| [ruanzhu-copyright](skills/ruanzhu-copyright/) | Preparing China **软件著作权** (软著) identification materials — 程序/文档鉴别材料, redaction, Word/PDF export |

They compose: kick off with **harness-first**, then capture stable workflows with
**skill-authoring** once the harness is running. Use **geo-article-generator**
whenever content needs to be legible to generative AI search, not just human readers.
Use **ai-dev-pipeline** when a PRD or plan should become a multi-task CLI delivery
loop instead of one giant agent run. Use **admin-console-ux** when an ops console
needs a full-page walkthrough against mainstream mid-console habits. Use
**h5-style-unify** when an existing H5/mobile-web codebase needs its colors and
styles converged into one token source with a lint gate. Use **swiftui-style-unify**
for the same unification on a SwiftUI app; when both ends of one product exist, the
two compose at a shared web SoT. Use **ruanzhu-copyright** when the deliverable is
软著登记材料 (not a code review or license/trademark filing).

## Install

After install, Cursor auto-discovers skills from `.cursor/skills/` and
`.agents/skills/` (also `.claude/skills/` for compatibility). Claude Code uses
`.claude/skills/`. User-level copies live under `~/.cursor/skills/` /
`~/.claude/skills/`.

### Option 1: GitHub CLI (recommended for a whole collection)

Requires [GitHub CLI](https://cli.github.com/) with `gh skill` (v2.90+):

```bash
# list skills in this repo
gh skill install cwywing/skills

# install one
gh skill install cwywing/skills h5-style-unify --agent cursor

# install all
gh skill install cwywing/skills --all --agent cursor
```

`--agent claude-code` writes to `.claude/skills/` instead. Add `--scope user`
for `~/.cursor/skills/` / `~/.claude/skills/`.

### Option 2: Manual copy

```bash
# Cursor (repeat for any skill name under skills/)
cp -r skills/harness-first          /path/to/project/.cursor/skills/harness-first
cp -r skills/skill-authoring        /path/to/project/.cursor/skills/skill-authoring
cp -r skills/geo-article-generator  /path/to/project/.cursor/skills/geo-article-generator
cp -r skills/ai-dev-pipeline        /path/to/project/.cursor/skills/ai-dev-pipeline
cp -r skills/admin-console-ux       /path/to/project/.cursor/skills/admin-console-ux
cp -r skills/h5-style-unify         /path/to/project/.cursor/skills/h5-style-unify
cp -r skills/swiftui-style-unify    /path/to/project/.cursor/skills/swiftui-style-unify
cp -r skills/ruanzhu-copyright      /path/to/project/.cursor/skills/ruanzhu-copyright

# Claude Code — same folders, destination .claude/skills/<name>
cp -r skills/<name> /path/to/project/.claude/skills/<name>
```

**ai-dev-pipeline:** copy alone installs the Skill docs; to also wire the
runnable `.pipeline/` runtime into a project:

```bash
pip install -r skills/ai-dev-pipeline/requirements.txt
python skills/ai-dev-pipeline/scripts/install.py --target /path/to/your-project
```

**ruanzhu-copyright:** copy the folder, then run its Python scripts from the
**target repo root** (see that skill's README). It does not install a `.pipeline/`
runtime.

Cursor **Remote Rule (GitHub)** imports `.mdc` project rules, not `SKILL.md`
skills. Do not use it for this repo.

## Layout

```
skills/                          # repo root (GitHub name; arbitrary)
├── README.md / README.zh-CN.md  # this file
└── skills/                      # collection root (skills/*/SKILL.md)
    ├── harness-first/
    ├── skill-authoring/
    ├── geo-article-generator/
    ├── ai-dev-pipeline/
    ├── admin-console-ux/
    ├── h5-style-unify/
    ├── swiftui-style-unify/
    └── ruanzhu-copyright/
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
- [ai-dev-pipeline/](skills/ai-dev-pipeline/) — Cursor Agent CLI multi-task delivery pipeline
  - [SKILL.md](skills/ai-dev-pipeline/SKILL.md) — main workflow (start here)
  - [scripts/](skills/ai-dev-pipeline/scripts/) — install + run_pipeline runtime
  - [templates/](skills/ai-dev-pipeline/templates/) — config + stage prompts
  - [references/](skills/ai-dev-pipeline/references/) — ops runbook, backend security
- [admin-console-ux/](skills/admin-console-ux/) — mid-console ops UX / walkthrough
  - [SKILL.md](skills/admin-console-ux/SKILL.md) — main workflow (start here)
  - [references/](skills/admin-console-ux/references/) — ops habits, acceptance, anti-patterns
- [h5-style-unify/](skills/h5-style-unify/) — H5/mobile-web style & color unification
  - [SKILL.md](skills/h5-style-unify/SKILL.md) — five-ring workflow (start here)
  - [scripts/](skills/h5-style-unify/scripts/) — fail-closed style audit (zero deps)
  - [assets/](skills/h5-style-unify/assets/) — theme.css / stylelint / acceptance-page templates
  - [references/](skills/h5-style-unify/references/) — token taxonomy, stack adapters, gate configs, pitfalls, case studies
  - [tests/](skills/h5-style-unify/tests/) — audit-script fixtures
- [swiftui-style-unify/](skills/swiftui-style-unify/) — SwiftUI/iOS style & color unification
  - [SKILL.md](skills/swiftui-style-unify/SKILL.md) — five-ring workflow, Swift-shaped (start here)
  - [scripts/](skills/swiftui-style-unify/scripts/) — ripgrep MUST-NOT gate (fail-closed; reports every rule) + `sync-design-tokens.mjs`
  - [assets/](skills/swiftui-style-unify/assets/) — DesignTokens / TextStyle / Theme / Preview Swift templates + `color-map.json.tmpl`
  - [references/](skills/swiftui-style-unify/references/) — token anatomy, theme & components, sync codegen, gate & pitfalls
  - [tests/](skills/swiftui-style-unify/tests/) — audit + sync fixtures
- [ruanzhu-copyright/](skills/ruanzhu-copyright/) — 软著鉴别材料 (program + document packs)
  - [SKILL.md](skills/ruanzhu-copyright/SKILL.md) — Phase 0–4 pipeline (start here)
  - [scripts/](skills/ruanzhu-copyright/scripts/) — extract, generate, redact, Word, upload PDF
  - [assets/](skills/ruanzhu-copyright/assets/) — 基础资料 templates, document prompt, multi-stack demos
  - [references/](skills/ruanzhu-copyright/references/) — phases, application-form fields, redaction, framework adapters
  - [tests/](skills/ruanzhu-copyright/tests/) — script-chain fixtures

Optional subdirectories (`scripts/`, `assets/`, `tests/`) are created per-skill
when needed — not every skill requires them.

## Provenance

Patterns in **skill-authoring** are distilled from the Claude Fable 5 system prompt
([`../CLAUDE-FABLE-5/README.md`](../CLAUDE-FABLE-5/README.md)) and reconciled with
the official skill-creator / skill-development specs.
