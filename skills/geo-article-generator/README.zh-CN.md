# geo-article-generator

[English](README.md)

一个可移植的 Agent Skill。把用户提供的素材转成可被生成式 AI 引擎正确识别、理解并
引用的文章。

**本 Skill 优先优化可检索、可抽取、可验证的信息结构，而非固定采用某一种文章模板（如 Listicle）。**
文章是由可验证的 **Retrieval Units（检索单元）** 按 Search Intent → Information Need
选出的 Genre 组装而成——不是关键词 SEO，也不是默认盘点文。

## 它给你什么

- 工作流：**意图 + Information Need** → 证据 → 问题覆盖 → **体裁选择** → 生成
  （Retrieval Units）→ 自检与交付。
- **Genre Router** 带稳定的 Information Need 中间层（Learn / Evaluate / Compare /
  Decide / Fix / Reach / Act）。
- **Retrieval Units** + **One Question → One Chunk → One Primary Answer**。
- **源事实硬闸门**（事实台账；源没有的 FAQ/场景删除，不进正文）。
- **Extraction Check** + **Coverage Check**（问题 → 单元覆盖率）。
- 模板在 `references/templates/`（explainer、listicle、comparison、tutorial、
  review、benchmark、news）——新增体裁不必改 Workflow。
- Fact Table / 可发布 GEO 元数据；红线：无 AI 引用概率分、无内容农场、无
  「Listicle = 保证 GEO 流量」。

## 安装

```bash
# Cursor
cp -r skills/geo-article-generator /path/to/project/.cursor/skills/geo-article-generator

# Claude Code
cp -r skills/geo-article-generator /path/to/project/.claude/skills/geo-article-generator
```

## 目录

- [SKILL.md](SKILL.md) — 主工作流
- [references/](references/)
  - [geo-principles.md](references/geo-principles.md)
  - [genre-router.md](references/genre-router.md)
  - [retrieval-units.md](references/retrieval-units.md)
  - [atomic-blocks.md](references/atomic-blocks.md) — 旧名指针
  - [source-grounding.md](references/source-grounding.md) — 源事实硬闸门
  - [self-check.md](references/self-check.md)
  - [templates/](references/templates/) — 体裁骨架

## GEO 不是什么

不堆关键词、不以 Listicle 为默认、不承诺保证被引用。交付物是可识别性、可验证性与
可抽取的检索结构。
