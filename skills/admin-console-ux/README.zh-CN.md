# admin-console-ux

[English](README.md)

优化管理后台（admin / backoffice）交互与显示的可移植 Agent Skill，对齐主流中后台
的运维使用习惯，既不闭门造车，也不做成营销风 UI。

## 安装到项目

```bash
# Cursor
cp -r skills/admin-console-ux /path/to/project/.cursor/skills/admin-console-ux

# Claude Code
cp -r skills/admin-console-ux /path/to/project/.claude/skills/admin-console-ux
```

说「优化管理后台」「后台样式/交互」「操作列歪了」「按运营习惯过一遍」
「修 AI 生成的后台」，或者贴一张后台截图要求做成真正能用的运维台，就会触发。

## 目录结构

- [SKILL.md](SKILL.md) — 工作流、硬线、交付清单（从这里开始）
- [references/](references/)
  - [ops-habits.md](references/ops-habits.md) — 走查脚本与运维习惯
  - [acceptance-checklist.md](references/acceptance-checklist.md) — 页面验收清单
  - [anti-patterns.md](references/anti-patterns.md) — 通病表与对比
- [README.md](README.md) / [README.zh-CN.md](README.zh-CN.md) — 本文件

## 配套技能

- **[skill-authoring](../skill-authoring/)** — 改本 SKILL.md 时的工艺层
- 优先对齐项目已有的设计体系（Ant Design / Element / Naive / Arco）；
  本技能只管 UX 和流程，不另起组件库
