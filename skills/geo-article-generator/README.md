# geo-article-generator

[中文](README.zh-CN.md)

A portable Agent Skill. It turns supplied source materials (notes, docs, URLs,
raw research) into a publishable article that generative AI engines — ChatGPT,
Gemini, 豆包, Perplexity, AI search overviews — can correctly identify,
understand, and cite.

**This skill optimizes for structured retrieval, not a specific article
format.** Articles are assemblies of verifiable **Retrieval Units** under a
Genre chosen by Search Intent → Information Need — not "always Listicle," not
keyword SEO.

## What it gives you

- Workflow: **Intent + Information Need** → Evidence → Question Coverage →
  **Genre Selection** → Generate (Retrieval Units) → Self-check & Deliver.
- **Genre Router** with a stable Information Need middle layer (Learn /
  Evaluate / Compare / Decide / Fix / Reach / Act).
- **Retrieval Units** + **One Question → One Chunk → One Primary Answer**.
- **Extraction Check** + **Coverage Check** (question → unit mapping %).
- Templates under `references/templates/` (explainer, listicle, comparison,
  tutorial, review, benchmark, news) — add genres without changing Workflow.
- Fact Table / Entity Registry as source of truth; publishable GEO metadata
  (entity + intent + information_need + genre + questions + sources).
- Red lines: no "AI citation probability"; no content-farm batches; no
  "Listicle = guaranteed GEO traffic."

## Install

```bash
# Cursor
cp -r skills/geo-article-generator /path/to/project/.cursor/skills/geo-article-generator

# Claude Code
cp -r skills/geo-article-generator /path/to/project/.claude/skills/geo-article-generator
```

## Layout

- [SKILL.md](SKILL.md) — main workflow
- [references/](references/)
  - [geo-principles.md](references/geo-principles.md)
  - [genre-router.md](references/genre-router.md)
  - [retrieval-units.md](references/retrieval-units.md)
  - [atomic-blocks.md](references/atomic-blocks.md) — legacy pointer
  - [self-check.md](references/self-check.md)
  - [templates/](references/templates/) — genre skeletons

## What GEO is not

No keyword stuffing, no Listicle-by-default, no citation guarantees. The
deliverable is legibility, verifiability, and extractable retrieval structure.
