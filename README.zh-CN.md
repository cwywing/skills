# skills

[English](README.md)

面向 Cursor 与 Claude Code 的可移植 Agent Skills 集合。每个技能是 `skills/<name>/`
下的独立文件夹（一份 `SKILL.md`，按需带 `scripts/`、`references/`、`assets/`、
`tests/`）。把该文件夹复制到项目的 skill 目录，或用 `gh skill` 安装。

GitHub 仓库名叫 `skills`；内层 `skills/` 是
[Agent Skills](https://agentskills.io/specification) 的**集合仓**约定
（`skills/*/SKILL.md`），供 `gh skill install` 扫描。它和 Cursor 安装后的路径
（`.cursor/skills/<name>/`）不是同一层，也不重复。不要把各个 skill 摊到仓库根目录
——安装器会扫不到。

## 技能一览

| 技能 | 适用场景 |
|------|----------|
| [harness-first](skills/harness-first/) | **新项目**启动 — 在写功能代码或 prompt 之前，先搭建自验证执行 harness |
| [skill-authoring](skills/skill-authoring/) | 撰写、审查或改进任意 SKILL.md，达到生产级质量 |
| [geo-article-generator](skills/geo-article-generator/) | 把提供的素材资料落地成一篇可被生成式 AI 引擎识别、理解并引用的文章 |
| [ai-dev-pipeline](skills/ai-dev-pipeline/) | 把计划拆成有序任务，用 Cursor Agent CLI（`agent -p --force`）持续交付 |
| [admin-console-ux](skills/admin-console-ux/) | 优化管理后台交互与显示，对齐主流中后台**运维使用习惯** |
| [h5-style-unify](skills/h5-style-unify/) | 统一**既有** H5 / 移动端项目的风格配色设计 — token 真相源、机器门禁、验收页 |
| [swiftui-style-unify](skills/swiftui-style-unify/) | 同一套五环统一法用于**既有** SwiftUI / iOS 应用 — `DesignTokens` 命名空间、Dynamic Type 排版、ripgrep 门禁、共享 SoT 代码生成 |
| [ruanzhu-copyright](skills/ruanzhu-copyright/) | 准备中国大陆 **软件著作权（软著）** 鉴别材料 — 程序/文档鉴别材料、脱敏、Word/PDF 导出 |

它们可以组合：先用 **harness-first** 启动项目，harness 跑稳后，用 **skill-authoring**
把重复工作流固化为技能。需要让内容对 AI 搜索也可读（而不只是对人）时，用
**geo-article-generator**。需要把 PRD/计划变成多任务 CLI 流水线（而不是一次 agent
啃完）时，用 **ai-dev-pipeline**。需要按运维习惯整站走查并统一后台 UX 时，用
**admin-console-ux**。需要把既有 H5/移动端代码库的配色样式收敛到单一 token 源并加
lint 门禁时，用 **h5-style-unify**。SwiftUI 应用做同样的统一时用
**swiftui-style-unify**；同一产品两端并存时，两个技能在共享 web SoT 处组合。交付物
是软著登记材料（不是 code review、许可证或商标）时，用 **ruanzhu-copyright**。

## 安装

安装后，Cursor 会从 `.cursor/skills/`、`.agents/skills/` 自动发现技能（兼容
`.claude/skills/`）。Claude Code 使用 `.claude/skills/`。用户级副本在
`~/.cursor/skills/` / `~/.claude/skills/`。

### 方式一：GitHub CLI（装整仓时推荐）

需要带 `gh skill` 的 [GitHub CLI](https://cli.github.com/)（v2.90+）：

```bash
# 列出本仓技能
gh skill install cwywing/skills

# 安装单个
gh skill install cwywing/skills h5-style-unify --agent cursor

# 全部安装
gh skill install cwywing/skills --all --agent cursor
```

`--agent claude-code` 会写到 `.claude/skills/`。加 `--scope user` 则装到
`~/.cursor/skills/` / `~/.claude/skills/`。

### 方式二：手动复制

```bash
# Cursor（skills/ 下任意技能名同理）
cp -r skills/harness-first          /path/to/project/.cursor/skills/harness-first
cp -r skills/skill-authoring        /path/to/project/.cursor/skills/skill-authoring
cp -r skills/geo-article-generator  /path/to/project/.cursor/skills/geo-article-generator
cp -r skills/ai-dev-pipeline        /path/to/project/.cursor/skills/ai-dev-pipeline
cp -r skills/admin-console-ux       /path/to/project/.cursor/skills/admin-console-ux
cp -r skills/h5-style-unify         /path/to/project/.cursor/skills/h5-style-unify
cp -r skills/swiftui-style-unify    /path/to/project/.cursor/skills/swiftui-style-unify
cp -r skills/ruanzhu-copyright      /path/to/project/.cursor/skills/ruanzhu-copyright

# Claude Code — 同一文件夹，目标改为 .claude/skills/<name>
cp -r skills/<name> /path/to/project/.claude/skills/<name>
```

**ai-dev-pipeline** 仅复制会装上 Skill 文档；若还要把可运行的 `.pipeline/` 装进项目：

```bash
pip install -r skills/ai-dev-pipeline/requirements.txt
python skills/ai-dev-pipeline/scripts/install.py --target /path/to/your-project
```

**ruanzhu-copyright** 复制文件夹即可；Python 脚本在**目标仓库根目录**执行（见该技能
README）。它不会安装 `.pipeline/` 运行时。

Cursor 的 **Remote Rule (GitHub)** 导入的是 `.mdc` 项目规则，不是 `SKILL.md` 技能。
不要用它来装本仓。

## 目录结构

```
skills/                          # 仓库根目录（GitHub 名，可改）
├── README.md / README.zh-CN.md  # 本文件
└── skills/                      # 集合入口（skills/*/SKILL.md）
    ├── harness-first/
    ├── skill-authoring/
    ├── geo-article-generator/
    ├── ai-dev-pipeline/
    ├── admin-console-ux/
    ├── h5-style-unify/
    ├── swiftui-style-unify/
    └── ruanzhu-copyright/
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
  - [tests/](skills/h5-style-unify/tests/) — 审计脚本夹具
- [swiftui-style-unify/](skills/swiftui-style-unify/) — SwiftUI/iOS 风格配色统一
  - [SKILL.md](skills/swiftui-style-unify/SKILL.md) — 五环工作流的 Swift 形态（从这里开始）
  - [scripts/](skills/swiftui-style-unify/scripts/) — ripgrep MUST-NOT 门禁（fail-closed，汇总全部规则）+ `sync-design-tokens.mjs`
  - [assets/](skills/swiftui-style-unify/assets/) — DesignTokens / TextStyle / Theme / Preview Swift 模板 + `color-map.json.tmpl`
  - [references/](skills/swiftui-style-unify/references/) — token 解剖、主题与组件、同步代码生成、门禁与坑
  - [tests/](skills/swiftui-style-unify/tests/) — 审计与 sync 夹具
- [ruanzhu-copyright/](skills/ruanzhu-copyright/) — 软著鉴别材料（程序包 + 文档包）
  - [SKILL.md](skills/ruanzhu-copyright/SKILL.md) — Phase 0–4 流水线（从这里开始）
  - [scripts/](skills/ruanzhu-copyright/scripts/) — 提取、生成、脱敏、Word、上传用 PDF
  - [assets/](skills/ruanzhu-copyright/assets/) — 基础资料模板、文档 prompt、多栈 demo
  - [references/](skills/ruanzhu-copyright/references/) — 分阶段手册、申请表字段、脱敏、框架适配
  - [tests/](skills/ruanzhu-copyright/tests/) — 脚本链路夹具

按需创建 `scripts/`、`assets/`、`tests/` 子目录即可，并非每个技能都需要。

## 溯源

**skill-authoring** 中的模式提炼自 Claude Fable 5 系统提示词
（[`../CLAUDE-FABLE-5/README.md`](../CLAUDE-FABLE-5/README.md)），并与官方
skill-creator / skill-development 规范对齐。
