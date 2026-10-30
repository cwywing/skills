# harness-first

[English](README.md)

可移植、与项目无关的 Agent Skill。在任何新项目里，第一步都不是写代码或写 prompt，
而是先通过五个门控阶段搭一套自验证 harness（现实模型 → 边界划分 → 最小可运行链路 →
评测优先 → Maker-Checker 循环）。

## 安装到新项目

将整个文件夹复制到新项目的 skill 目录：

```bash
# Cursor
cp -r skills/harness-first /path/to/new-project/.cursor/skills/harness-first

# Claude Code
cp -r skills/harness-first /path/to/new-project/.claude/skills/harness-first
```

两个工具都会自动发现。greenfield 项目里直接开工即可触发，也可以说
「bootstrap this project」「let's build X」「help me architect this」。

## 目录结构

- [SKILL.md](SKILL.md) — 五阶段门控工作流（从这里开始）
- [references/](references/)
  - [templates.md](references/templates.md) — 各阶段交付物模板
  - [decision-gates.md](references/decision-gates.md) — 各门控详细通过/失败标准
  - [methodology.md](references/methodology.md) — 方法论与原理（按需阅读）
- [README.md](README.md) / [README.zh-CN.md](README.zh-CN.md) — 本文件

不含任何项目特定内容，可直接用于后端、前端、CMS、自动化、流水线或 LLM/Agent 应用。

工作流稳定后，用 [skill-authoring](../skill-authoring/) 将其固化为技能，再交给 skill-creator 做评测与打包。
