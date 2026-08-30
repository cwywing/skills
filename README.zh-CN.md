# skills

[English](README.md)

面向 Cursor 与 Claude Code 的可移植 Agent Skills 集合。每个技能是 `skills/` 下的独立文件夹，可复制到项目的 skill 目录，或通过 Cursor 的 **Remote Rule (GitHub)** 导入。

## 技能一览

| 技能 | 适用场景 |
|------|----------|
| [harness-first](skills/harness-first/) | **新项目**启动 — 在写功能代码或 prompt 之前，先搭建自验证执行 harness |
| [skill-authoring](skills/skill-authoring/) | 撰写、审查或改进任意 SKILL.md，达到生产级质量 |
| [geo-article-generator](skills/geo-article-generator/) | 把提供的素材资料落地成一篇可被生成式 AI 引擎识别、理解并引用的文章 |
| [ai-dev-pipeline](skills/ai-dev-pipeline/) | 把计划拆成有序任务，用 Cursor Agent CLI（`agent -p --force`）持续交付 |
| [admin-console-ux](skills/admin-console-ux/) | 优化管理后台交互与显示，对齐主流中后台**运维使用习惯** |
| [h5-style-unify](skills/h5-style-unify/) | 统一**既有** H5 / 移动端项目的风格配色设计 — token 真相源、机器门禁、验收页，双案例交叉验证 |

两者可组合使用：先用 **harness-first** 启动项目，harness 跑稳后，用 **skill-authoring** 将重复工作流固化为技能。需要让内容对 AI 搜索也可读（而不只是对人）时，用 **geo-article-generator**。需要把 PRD/计划变成多任务 CLI 流水线（而不是一次 agent 啃完）时，用 **ai-dev-pipeline**。需要按运维习惯整站走查并统一后台 UX 时，用 **admin-console-ux**。需要把既有 H5/移动端代码库的配色样式收敛到单一 token 源并加 lint 门禁时，用 **h5-style-unify**。


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
cp -r skills/ai-dev-pipeline        /path/to/project/.cursor/skills/ai-dev-pipeline
cp -r skills/admin-console-ux       /path/to/project/.cursor/skills/admin-console-ux
cp -r skills/h5-style-unify         /path/to/project/.cursor/skills/h5-style-unify

# Claude Code
cp -r skills/harness-first          /path/to/project/.claude/skills/harness-first
cp -r skills/skill-authoring        /path/to/project/.claude/skills/skill-authoring
cp -r skills/geo-article-generator  /path/to/project/.claude/skills/geo-article-generator
cp -r skills/ai-dev-pipeline        /path/to/project/.claude/skills/ai-dev-pipeline
cp -r skills/admin-console-ux       /path/to/project/.claude/skills/admin-console-ux
cp -r skills/h5-style-unify         /path/to/project/.claude/skills/h5-style-unify
```


**ai-dev-pipeline** 仅复制会装上 Skill 文档；若还要把可运行的 `.pipeline/` 装进项目：

```bash
pip install -r skills/ai-dev-pipeline/requirements.txt
python skills/ai-dev-pipeline/scripts/install.py --target /path/to/your-project
```

两个工具均会自动发现技能，无需额外配置。

## 目录结构

```
skills/                          # 仓库根目录
├── README.md / README.zh-CN.md  # 本文件
└── skills/                      # 技能集合（GitHub 导入所需）
    ├── harness-first/
    ├── skill-authoring/
    ├── geo-article-generator/
    ├── ai-dev-pipeline/
    ├── admin-console-ux/
    └── h5-style-unify/
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
- [ai-dev-pipeline/](skills/ai-dev-pipeline/) — Cursor Agent CLI 多任务持续交付流水线
  - [SKILL.md](skills/ai-dev-pipeline/SKILL.md) — 主工作流（从这里开始）
  - [scripts/](skills/ai-dev-pipeline/scripts/) — install + run_pipeline 运行时
  - [templates/](skills/ai-dev-pipeline/templates/) — 配置与阶段 prompts
  - [references/](skills/ai-dev-pipeline/references/) — 运维手册、后端安全
- [admin-console-ux/](skills/admin-console-ux/) — 中后台运维 UX / 整站走查
  - [SKILL.md](skills/admin-console-ux/SKILL.md) — 主工作流（从这里开始）
  - [references/](skills/admin-console-ux/references/) — 运维习惯、验收清单、通病对比
- [h5-style-unify/](skills/h5-style-unify/) — H5/移动端风格配色统一
  - [SKILL.md](skills/h5-style-unify/SKILL.md) — 五环工作流（从这里开始）
  - [scripts/](skills/h5-style-unify/scripts/) — fail-closed 样式审计脚本（零依赖）
  - [assets/](skills/h5-style-unify/assets/) — theme.css / stylelint / 验收页模板
  - [references/](skills/h5-style-unify/references/) — token 分类法、技术栈适配、门禁配置、坑清单、案例对照


按需创建 `scripts/`、`assets/` 子目录即可，并非每个技能都需要。

## 溯源

**skill-authoring** 中的模式提炼自 Claude Fable 5 系统提示词
（[`../CLAUDE-FABLE-5/README.md`](../CLAUDE-FABLE-5/README.md)），并与官方
skill-creator / skill-development 规范对齐。
