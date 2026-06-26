# skill-authoring

[English](README.md)

可移植的 Agent Skill — 撰写生产级技能的**工艺层**。它位于官方结构规范（skill-development）与评测/打包流程（skill-creator）之间。

## 安装到项目

```bash
# Cursor
cp -r skill-authoring /path/to/project/.cursor/skills/skill-authoring

# Claude Code
cp -r skill-authoring /path/to/project/.claude/skills/skill-authoring
```

在说「write a skill」「improve my SKILL.md」「why isn't my skill triggering」，或即将把草稿交给 skill-creator 时触发。

## 目录结构

- [SKILL.md](SKILL.md) — 工作流与 checklist（从这里开始）
- [references/](references/)
  - [descriptions-and-triggering.md](references/descriptions-and-triggering.md) — frontmatter 与触发时机
  - [prose-and-formatting.md](references/prose-and-formatting.md) — 语气、文风、格式
  - [instruction-design.md](references/instruction-design.md) — why 优于 MUST、力度校准
  - [examples-and-output-formats.md](references/examples-and-output-formats.md) — 少样本示例与对比对
- [README.md](README.md) / [README.zh-CN.md](README.zh-CN.md) — 本文件

仅在技能需要确定性代码或输出模板时，再添加 `scripts/` 或 `assets/` — 本元技能本身不需要。

## 配套技能

- **skill-creator**（官方）— 测试、评测、优化 description、打包。
- **skill-development**（官方）— frontmatter、结构、验证 checklist。
- **[harness-first](../harness-first/)** — 完整践行本文档所有模式的技能，可作为起草时的参考范本。

## 溯源

模式溯源至 Claude Fable 5 系统提示词
（[`../CLAUDE-FABLE-5/README.md`](../CLAUDE-FABLE-5/README.md)）及官方
skill-creator / skill-development 指南。
