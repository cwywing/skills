# geo-article-generator

[English](README.md)

一个可移植的 Agent Skill。把用户提供的素材(笔记、文档、URL、原始调研)转成
一篇可发布的、能被生成式 AI 引擎(ChatGPT、Gemini、豆包、Perplexity、AI 搜索
概览)正确识别、理解并引用的文章。

这不是 SEO 关键词内容生成,而是信息工程:文章给出清晰的实体、每条主张都有来
源、覆盖真实用户问题(包括对比/边界类问题),并剔除那些会被 AI 摘要器丢弃或
引发幻觉的形容词堆砌与模糊指标。

## 它给你什么

- 六步工作流:摄入素材 → 抽取实体与事实 → 构建语义问题集(先扩出问题空间再筛选)
  → 按 GEO 模板起草 → 自检并打分 → 交付(附评分审计 + 可观测性建议)。
- 优先接受用户提供的 **Fact Table / Entity Registry** 作为唯一事实源,缺失时再
  退化到从原始素材新建。每条可引用事实都带*源位置*(文档 + 页码 / 章节 / 锚点),
  不只是源名称。
- 三份按需加载的参考文件:五层 GEO 原则、分节文章模板、发布前闸门 + 评分审计。
- 一组输入→输出示例和正反对照。
- 两条明确红线:不打"AI 引用概率"分(源论文反对的伪精确承诺),不做内容农场式
  批量灌水。
- 文章前缀输出**可发布的 GEO 元数据块**(实体 + 问题 + 来源,YAML 格式),发布时
  可剥离为 JSON-LD / Schema 标记;并回避"该系统""我们"等裸代词,确保被摘引的句子
  仍能正确归因。

## 安装

把整个文件夹复制到目标项目的 skill 目录:

```bash
# Cursor
cp -r geo-article-generator /path/to/project/.cursor/skills/geo-article-generator

# Claude Code
cp -r geo-article-generator /path/to/project/.claude/skills/geo-article-generator
```

两个工具都会自动发现 skill,无需额外配置。

## 目录

- [SKILL.md](SKILL.md) — 主工作流(从这里开始)
- [references/](references/)
  - [geo-principles.md](references/geo-principles.md) — 五层 GEO 原则及背后的原因
  - [article-template.md](references/article-template.md) — 分节输出模板
  - [self-check.md](references/self-check.md) — 发布前闸门与红线

## GEO 不是什么

不堆关键词、不养链接农场、不造假问答页、不承诺"保证被 AI 引用"——没有人能控
制生成式引擎的输出。交付物是*可识别性与可验证性*,它提高被正确引用的概率,但
不购买这个结果。

## 来源

基于讨论 GEO(生成式引擎优化)的文章构建。该文阐述为什么 GEO 是信息工程而非排
名技巧,为什么实体清晰度、可验证性、反幻觉才是真正影响 AI 可发现性的层次。
