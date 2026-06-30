# skills

[English](README.md)

面向 Cursor 与 Claude Code 的可移植 Agent Skills 集合。每个技能是一个独立文件夹，可直接复制到项目的 skill 目录中使用。

## 技能一览

| 技能 | 适用场景 |
|------|----------|
| [harness-first](harness-first/) | **新项目**启动 — 在写功能代码或 prompt 之前，先搭建自验证执行 harness |
| [skill-authoring](skill-authoring/) | 撰写、审查或改进任意 SKILL.md，达到生产级质量 |
| [geo-article-generator](geo-article-generator/) | 把提供的素材资料落地成一篇可被生成式 AI 引擎识别、理解并引用的文章 |

两者可组合使用：先用 **harness-first** 启动项目，harness 跑稳后，用 **skill-authoring** 将重复工作流固化为技能。需要让内容对 AI 搜索也可读（而不只是对人）时，用 **geo-article-generator**。

## 安装

将技能文件夹复制到目标项目的 skill 目录：

```bash
# Cursor
cp -r harness-first          /path/to/project/.cursor/skills/harness-first
cp -r skill-authoring        /path/to/project/.cursor/skills/skill-authoring
cp -r geo-article-generator  /path/to/project/.cursor/skills/geo-article-generator

# Claude Code
cp -r harness-first          /path/to/project/.claude/skills/harness-first
cp -r skill-authoring        /path/to/project/.claude/skills/skill-authoring
cp -r geo-article-generator  /path/to/project/.claude/skills/geo-article-generator
```

两个工具均会自动发现技能，无需额外配置。

## 目录结构

- [README.md](README.md) / [README.zh-CN.md](README.zh-CN.md) — 本文件
- [harness-first/](harness-first/) — 五阶段门控式项目启动
  - [SKILL.md](harness-first/SKILL.md) — 主流程（从这里开始）
  - [README.md](harness-first/README.md) / [README.zh-CN.md](harness-first/README.zh-CN.md)
  - [references/](harness-first/references/) — 模板、门控、方法论
    - [templates.md](harness-first/references/templates.md)
    - [decision-gates.md](harness-first/references/decision-gates.md)
    - [methodology.md](harness-first/references/methodology.md)
- [skill-authoring/](skill-authoring/) — 技能写作工艺层
  - [SKILL.md](skill-authoring/SKILL.md) — 工作流与 checklist（从这里开始）
  - [README.md](skill-authoring/README.md) / [README.zh-CN.md](skill-authoring/README.zh-CN.md)
  - [references/](skill-authoring/references/) — 触发、文风、指令设计、示例
    - [descriptions-and-triggering.md](skill-authoring/references/descriptions-and-triggering.md)
    - [prose-and-formatting.md](skill-authoring/references/prose-and-formatting.md)
    - [instruction-design.md](skill-authoring/references/instruction-design.md)
    - [examples-and-output-formats.md](skill-authoring/references/examples-and-output-formats.md)
- [geo-article-generator/](geo-article-generator/) — 把素材落地成对生成式 AI 可读的文章
  - [SKILL.md](geo-article-generator/SKILL.md) — 主工作流（从这里开始）
  - [README.md](geo-article-generator/README.md) / [README.zh-CN.md](geo-article-generator/README.zh-CN.md)
  - [references/](geo-article-generator/references/) — GEO 原则、文章模板、自检闸门
    - [geo-principles.md](geo-article-generator/references/geo-principles.md)
    - [article-template.md](geo-article-generator/references/article-template.md)
    - [self-check.md](geo-article-generator/references/self-check.md)

按需创建 `scripts/`、`assets/` 子目录即可，并非每个技能都需要。

## 溯源

**skill-authoring** 中的模式提炼自 Claude Fable 5 系统提示词
（[`../CLAUDE-FABLE-5/README.md`](../CLAUDE-FABLE-5/README.md)），并与官方
skill-creator / skill-development 规范对齐。
