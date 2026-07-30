# admin-console-ux

[English](README.md)

可移植 Agent Skill：优化 **管理后台 / admin / backoffice** 的交互与显示，对齐主流中后台
**运维使用习惯** — 不是开发者闭门造车，也不是营销风 UI。

## 安装到项目

```bash
# Cursor
cp -r skills/admin-console-ux /path/to/project/.cursor/skills/admin-console-ux

# Claude Code
cp -r skills/admin-console-ux /path/to/project/.claude/skills/admin-console-ux
```

在说「优化管理后台」「后台样式/交互」「操作列歪了」「按运营习惯过一遍」
「修 AI 生成的后台」，或贴后台截图要求做成真正运维台时触发。

## 目录结构

- [SKILL.md](SKILL.md) — 工作流、硬线、交付清单（从这里开始）
- [references/](references/)
  - [ops-habits.md](references/ops-habits.md) — 走查脚本与运维习惯
  - [acceptance-checklist.md](references/acceptance-checklist.md) — 页面验收清单
  - [anti-patterns.md](references/anti-patterns.md) — 通病表与对比
- [README.md](README.md) / [README.zh-CN.md](README.zh-CN.md) — 本文件

## 配套技能

- **[skill-authoring](../skill-authoring/)** — 改本 SKILL.md 时的工艺层
- 优先对齐项目已有设计体系（Ant Design / Element / Naive / Arco）；
  本技能管 UX/流程，不另起组件库
