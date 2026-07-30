# admin-console-ux

[中文](README.zh-CN.md)

A portable Agent Skill for polishing **admin / backoffice / 管理后台** consoles so
display and interaction match mainstream mid-console **ops habits** — not
developer-invented chrome or marketing aesthetics.

## Install into a project

```bash
# Cursor
cp -r skills/admin-console-ux /path/to/project/.cursor/skills/admin-console-ux

# Claude Code
cp -r skills/admin-console-ux /path/to/project/.claude/skills/admin-console-ux
```

Trigger it by saying "优化管理后台", "后台样式/交互", "操作列歪了",
"按运营习惯过一遍", "修 AI 生成的后台", or when pasting an admin screenshot
and asking to make it feel like a real ops console.

## Layout

- [SKILL.md](SKILL.md) — workflow, non-negotiables, deliverables (start here)
- [references/](references/)
  - [ops-habits.md](references/ops-habits.md) — walkthrough script + ops rules
  - [acceptance-checklist.md](references/acceptance-checklist.md) — page acceptance
  - [anti-patterns.md](references/anti-patterns.md) — failure table + contrasts
- [README.md](README.md) / [README.zh-CN.md](README.zh-CN.md) — this file

## Companion skills

- **[skill-authoring](../skill-authoring/)** — craft layer when editing this SKILL.md
- Prefer the project's existing design system (Ant Design / Element / Naive / Arco);
  this skill is UX/process, not a new component library
