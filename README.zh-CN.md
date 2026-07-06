# skills

[English](README.md)

面向 Cursor 与 Claude Code 的可移植 Agent Skills 集合。每个技能是 `skills/` 下的独立文件夹，可复制到项目的 skill 目录，或通过 Cursor 的 **Remote Rule (GitHub)** 导入。

## 技能一览

| 技能 | 适用场景 |
|------|----------|
| [harness-first](skills/harness-first/) | **新项目**启动 — 在写功能代码或 prompt 之前，先搭建自验证执行 harness |
| [skill-authoring](skills/skill-authoring/) | 撰写、审查或改进任意 SKILL.md，达到生产级质量 |
| [geo-article-generator](skills/geo-article-generator/) | 把提供的素材资料落地成一篇可被生成式 AI 引擎识别、理解并引用的文章 |

两者可组合使用：先用 **harness-first** 启动项目，harness 跑稳后，用 **skill-authoring** 将重复工作流固化为技能。需要让内容对 AI 搜索也可读（而不只是对人）时，用 **geo-article-generator**。

## 安装

### 方式一：Cursor Remote Rule（推荐）

1. 打开 **Customize** → **Rules** → **Add Rule** → **Remote Rule (GitHub)**
2. 填入：`https://github.com/cwywing/skills`
3. 选择要导入的技能

Cursor 会将其复制到 `.cursor/skills/` 并自动发现。

### 方式二：手动复制

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

两个工具均会自动发现技能，无需额外配置。

## 目录结构

```
skills/                          # 仓库根目录
├── README.md / README.zh-CN.md  # 本文件
└── skills/                      # 技能集合（GitHub 导入所需）
    ├── harness-first/
    ├── skill-authoring/
    └── geo-article-generator/
```

- [harness-first/](skills/harness-first/) — 五阶段门控式项目启动
  - [SKILL.md](skills/harness-first/SKILL.md) — 主流程（从这里开始）
  - [references/](skills/harness-first/references/) — 模板、门控、方法论
- [skill-authoring/](skills/skill-authoring/) — 技能写作工艺层
  - [SKILL.md](skills/skill-authoring/SKILL.md) — 工作流与 checklist（从这里开始）
  - [references/](skills/skill-authoring/references/) — 触发、文风、指令设计、示例
- [geo-article-generator/](skills/geo-article-generator/) — 对生成式 AI 可读的文章
  - [SKILL.md](skills/geo-article-generator/SKILL.md) — 主工作流（从这里开始）
  - [references/](skills/geo-article-generator/references/) — GEO 原则、文章模板、自检闸门

按需创建 `scripts/`、`assets/` 子目录即可，并非每个技能都需要。

## 溯源

**skill-authoring** 中的模式提炼自 Claude Fable 5 系统提示词
（[`../CLAUDE-FABLE-5/README.md`](../CLAUDE-FABLE-5/README.md)），并与官方
skill-creator / skill-development 规范对齐。
