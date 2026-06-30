# geo-article-generator

[中文](README.zh-CN.md)

A portable Agent Skill. It turns supplied source materials (notes, docs, URLs,
raw research) into a publishable article that generative AI engines — ChatGPT,
Gemini, 豆包, Perplexity, AI search overviews — can correctly identify,
understand, and cite.

This is **not** SEO keyword-content generation. It is information engineering:
the article states a clear entity, backs every claim with a source, answers
real user questions (including comparison/boundary queries), and strips out
the adjective stacks and vague metrics that AI summarizers discard or
hallucinate around.

## What it gives you

- A six-step workflow: ingest materials → extract entities & claims → build a
  semantic question set (expand a question space, then filter) → draft to a
  GEO template → self-check & score → deliver with a scored audit + observability
  note.
- Accepts a supplied **Fact Table / Entity Registry** as the single source of
  truth (preferred), and falls back to building a transient one from raw
  materials. Every citable fact carries its source *location* (document + page
  / section / anchor), not just a source name.
- Three reference files loaded on demand: the five GEO layers, the
  section-by-section article template, and the pre-publish gate + scored audit.
- A worked Input→Output example and a Correct-vs-Incorrect contrast pair.
- Two explicit red lines: no "AI citation probability" score (fake-precise
  promise the source thesis rejects), no content-farm batch generation.
- Emits a publishable **GEO metadata block** (entity + questions + sources, in
  YAML) as the article prefix — strippable into JSON-LD / Schema markup at
  publish time — and avoids bare pronouns ("该系统", "我们") so lifted
  sentences stay correctly attributed.

## Install

Copy this folder into the project's skill directory:

```bash
# Cursor
cp -r geo-article-generator /path/to/project/.cursor/skills/geo-article-generator

# Claude Code
cp -r geo-article-generator /path/to/project/.claude/skills/geo-article-generator
```

Both tools auto-discover skills. No extra configuration needed.

## Layout

- [SKILL.md](SKILL.md) — main workflow (start here)
- [references/](references/)
  - [geo-principles.md](references/geo-principles.md) — the five GEO layers and the reasoning behind each
  - [article-template.md](references/article-template.md) — section-by-section output template
  - [self-check.md](references/self-check.md) — pre-publish gate and red flags

## What GEO is not

No keyword stuffing, no link farming, no fake Q&A pages, and no guarantee of
being cited — no one controls generative engine output. The deliverable is
*legibility and verifiability*, which raises the probability of correct
citation; it does not purchase it.

## Origin

Built from the GEO (Generative Engine Optimization) article discussing why GEO
is information engineering rather than a ranking trick, and why entity
clarity, verifiability, and anti-hallucination are the layers that actually
move the needle for AI discoverability.
