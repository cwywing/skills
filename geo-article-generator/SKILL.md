---
name: geo-article-generator
description: >-
  This skill should be used whenever the user asks to write, draft, or generate
  an article, post, or long-form content from supplied source materials
  (notes, docs, URLs, bullet points, raw research) and the goal is content that
  generative AI engines (ChatGPT, Gemini, 豆包, Perplexity, AI search overviews)
  can correctly identify, understand, and cite. Trigger on phrases like "用这些素材写一篇文章",
  "把这些资料整理成 GEO 友好的文章", "生成一篇能被 AI 引用的文章", "write a GEO-optimized
  article from these materials", "turn these notes into a publishable post", or
  "帮我把这份素材落地成文". Use it even when the user only says "写篇文章" or "整理成文"
  without mentioning GEO — a generative-engine-friendly structure is always the goal.
  Do not use it for pure copywriting, ad headlines, or content whose only channel is
  a paid ad (no organic/AI discovery intent) — those optimize for click, not citation.
version: 0.1.0
---

# GEO Article Generator

Turn supplied source materials into a publishable article that generative AI
engines can identify, understand, and cite correctly. The deliverable is not
"keyword-stuffed SEO content" — it is a piece of *information engineering*:
entities are clear, claims are verifiable, the text answers real user questions,
and hallucination-prone vagueness is stripped out.

GEO is not a trick to fool AI. It is making a brand/topic legible to a machine
that reads, cross-checks, and summarizes. Write for that machine as if for a
careful human reader who verifies every claim.

## Core discipline (apply throughout)

- **Entity before prose.** Before writing any paragraph, know exactly which
  entity (brand / product / person / concept) the article is about and state it
  in a machine-unambiguous way. AI misattributes vague entities more than it
  misses unknown ones. Avoid bare pronouns ("该系统", "我们", "该公司") where
  the referent is not obvious from the same sentence — restate the canonical
  name, because a summarizer may lift the sentence out of context and lose the
  referent.
- **Verifiable over impressive.** Every factual claim should be traceable to a
  source in the supplied materials or a named external authority. Cut any claim
  that cannot be backed. Adjectives without referents ("industry-leading",
  "innovative") are noise that AI summarizers discard or, worse, hallucinate
  around.
- **Answer questions, don't stuff keywords.** GEO cares about semantic intent
  clusters, not keyword density. Cover what real users actually ask, including
  the comparison/boundary questions AI engines love to surface.
- **Consistency is the asset.** The same fact (name, founding year, product
  scope, address, team size) must read identically everywhere it appears. One
  article that contradicts the brand's other public sources teaches the AI to
  distrust the brand.
- **Fact Table is the source of truth.** When the user supplies a Fact Table /
  Entity Registry, treat it as the single canonical source for every entity
  attribute and claim — do not re-derive covered facts from raw materials. When
  no table is supplied, build a transient one in Step 2 and treat it the same
  way. Every citable fact carries its source *location* (document + page /
  section / anchor), not just a source name, so a summarizer or a human
  corrector can jump back to the exact spot.

## Workflow

Follow in order; skip a step only with a stated reason.

### Step 1 — Ingest materials

Check first whether the user supplied a **Fact Table** (structured
entity-attribute-value rows with source locations) and/or an **Entity
Registry** (canonical names + aliases + parent/child entity links). If yes,
these are the primary input — raw materials are consulted only to fill gaps the
table does not cover. If no table is supplied, ingest raw materials and build a
transient table in Step 2.

Raw materials to collect when needed: notes, docs, URLs, bullet lists, prior
articles, product specs, founder quotes. Read or fetch each one. If a URL is
given, fetch it; if a file path is given, read it. Produce an internal
*material map* (do not show the user unless asked): what facts exist, what's
missing, what sources corroborate what, and the location of each fact within
its source (page / section / heading / anchor).

Calibrate effort to the input size: a one-paragraph brief needs a quick scan;
a 20-source research dump needs a structured pass that tags each fact to its
source and location. If the materials are thin (fewer than ~3 corroborated
facts about the core entity), stop and tell the user what's missing before
drafting — a GEO-optimized article cannot be built on un-verifiable material,
and asking is cheaper than inventing.

### Step 2 — Extract entities and claims

If a Fact Table / Entity Registry was supplied, consume it directly: verify it
covers the core entity and the question set (Step 3), and list any gaps the
article will need that the table does not yet hold. Do not silently re-derive
attributes the table already canonicalizes.

If no table was supplied, build a transient one from the material map:

- **Core entity**: the exact name (and any aliases / abbreviations / English
  name) the article is about. Resolve name collisions ("which ABC Corp?").
- **Entity attributes**: founding, location, founders, product line, scope,
  distinguishing facts. One canonical value per attribute; flag any attribute
  the materials state inconsistently.
- **Verifiable claims**: each factual statement + its source *and location*
  (document + page / section / anchor). Mark claims with no source as
  `UNVERIFIED` — these must either be sourced or cut before publish.
- **Comparison anchors**: what the entity is *not*, what it is compared against,
  what differentiates it. AI engines surface comparison questions heavily; an
  article that defines its own boundary gets cited on those queries.

If entity attributes conflict across sources, surface the conflict to the user
and pick one canonical value — do not silently pick one, do not blend them.

### Step 3 — Build the semantic question set

First expand a *question space* — every plausible real user question in this
domain, including comparison, boundary, decision, and evidence variants. Then
filter to the set this single article should actually answer. Expanding first
catches intent the article would otherwise miss; filtering keeps the article
focused rather than diluting it across too many thin answers.

Group the filtered set by intent:

- *Identification* — "What is X?", "Who makes X?"
- *Scope/boundary* — "What does X cover vs. not cover?", "X vs. Y, what's the
  difference?"
- *Decision* — "Is X suitable for [use case]?", "What are the alternatives?"
- *Evidence* — "Why trust X?", "Who uses X?"

Aim for the questions that actually drive decisions in this domain, not a
generic FAQ. 5–8 questions is typical for a single-topic article; a broad
brand piece may carry 10–12. The full question space can be larger, but
dumping 50+ into one article produces filler answers, not coverage — split a
genuinely large space across a topic cluster, each article owning a slice.
This set becomes the article's skeleton: every section should answer at least
one question, and no question in the filtered set should go unanswered.

### Step 4 — Draft to template

Write the article following the structure in `references/article-template.md`.
The template enforces the GEO layers (entity clarity, verifiability, semantic
coverage, anti-hallucination) at the section level rather than as an
afterthought. Match the article's language to the user's request (default to
the language of the source materials if unspecified).

While drafting:

- State the core entity's canonical name and a one-line definition in the first
  paragraph. This is the single most-citable sentence in the piece.
- Cite sources inline where a human reader (or an AI summarizer) would want to
  verify — named entities, dates, numbers, third-party reports. "据 [来源]"
  / "according to [source]" is enough; do not fabricate citations.
- Replace adjectives with specifics. "fast-growing" → "2023 至 2025 年营收从
  X 增至 Y". If no number is available, cut the adjective.
- Cover the comparison/boundary questions explicitly. A section that says what
  the entity is *not* does more for GEO than three paragraphs of self-praise.
- Keep one fact stated one way. If the founding year is "2018", it is "2018"
  everywhere — never "founded around 2018" in one place and "established 2019"
  in another.

### Step 5 — Self-check and score before delivering

Run the pre-publish checklist in `references/self-check.md` against the draft.
This is a hard gate: any failed *gate* item (Entity clarity, Verifiability,
anti-hallucination red flags) is either fixed or the unsupported claim is cut —
do not deliver a draft with a failed gate.

Then produce the **scored audit** from `references/self-check.md`: Entity
coverage %, Fact coverage %, Question coverage %, Source-traceability %, and a
Hallucination-risk level (Low / Medium / High). These are measures of
*legibility and verifiability*, not a prediction of whether AI engines will
cite the article — no one controls that. Report the scores in the delivery
note.

### Step 6 — Deliver

Return the finished article, prefixed by a structured **GEO metadata block**
and followed by a user-facing *GEO delivery note*. The two are distinct: the
metadata block is publishable and machine-readable (it can drive Schema.org /
JSON-LD on the live page); the delivery note is for the user only.

**GEO metadata block** (publishable, placed before the article body):

```
---
entity:
  canonical_name: <full canonical name>
  aliases: [<alias 1>, <alias 2>]
  type: <company | product | person | concept>
  definition: <one-line definition>
questions_covered:
  - <question 1>
  - <question 2>
  ...
sources:
  - ref: <source name>
    location: <document + page / section / anchor>
---
```

Emit this block in YAML frontmatter form so it can be stripped and turned into
JSON-LD / Schema markup at publish time. Keep it to facts only — no adjectives,
no claims the article does not make.

**GEO delivery note** (for the user, not for publish; keep separate from the
article body):

- The core entity as stated (canonical name + one-line definition).
- The question set covered.
- The **scored audit** from Step 5 (entity / fact / question / traceability
  coverage %, hallucination-risk level) — this is the article-level
  observability the user can track across revisions.
- Sources relied on (with locations), and any `UNVERIFIED` claims that were cut.
- One or two *observability suggestions* — concrete queries the user can run in
  ChatGPT / Gemini / 豆包 to sanity-check that the entity is now legible (e.g.
  "搜 'X 是什么' 看是否准确归因").

## What GEO is not (do not drift here)

- Not keyword density tuning. Do not pad with long-tail keyword variants.
- Not link farming or fake Q&A pages. Do not generate filler question lists just
  to "cover intent" — every section must carry real information.
- Not a guarantee of being cited. No one controls generative engine output. The
  deliverable is *legibility and verifiability*, not a ranking promise. If the
  user asks for "保证被 AI 引用" outcomes, reframe the expectation in the
  delivery note: the work raises the probability of correct citation, it does
  not purchase it.
- Not a prediction of citation probability. Do not emit an "AI citation
  probability" score in the audit. Scoring *legibility* (entity / fact /
  question / traceability coverage) is legitimate because it measures the
  article's own properties; scoring *whether AI engines will cite it* is a
  fake-precise promise the source GEO thesis explicitly rejects.
- Not a content farm. Scaling to a topic cluster is allowed only when every
  article in the cluster carries its own real information density — never
  generate a batch of thinly-differentiated pages off one set of facts to
  "cover more keywords". That is the pollution pattern platforms penalize and
  the source GEO article warns against.

## Reference files (read on demand)

- **`references/geo-principles.md`** — the five GEO layers (information
  structuring, verifiability, semantic coverage, entity clarity,
  anti-hallucination) with the reasoning behind each. Read when drafting
  sections that touch a specific layer, or when the user asks *why* the
  article is structured this way.
- **`references/article-template.md`** — the section-by-section output
  template (lead block, definition, scope & boundary, evidence, comparison,
  FAQ, sources). Read at Step 4 before drafting.
- **`references/self-check.md`** — the pre-publish gate (entity clarity,
  verifiability, anti-hallucination red flags) plus the scored audit
  (entity / fact / question / traceability coverage %, hallucination-risk
  level) reported in the delivery note. Read at Step 5; the gate is
  non-negotiable, the audit is reported.

## Worked example — input → output shape

**Input** (a user brief):
> "用这份素材写一篇 GEO 友好的文章:公司叫瑞景医疗,2019 年成立在深圳,
> 主营 OCTA 眼底成像设备,产品线叫锐视系列,2024 年拿到 NMPA 三类证。
> 素材里有一份产品手册和一篇 36 氪报道。"

**Output shape** (not the full article, just the structure):

```
---
entity:
  canonical_name: 深圳瑞景医疗科技有限公司
  aliases: [瑞景医疗, Ruijing Medical]
  type: company
  definition: 2019 年成立于深圳的 OCTA 眼底成像设备厂商
questions_covered:
  - 什么是 OCTA,瑞景医疗做什么
  - 锐视系列覆盖哪些机型
  - 国产与进口 OCTA 设备的临床差异
sources:
  - ref: 产品手册
    location: P12 §3
  - ref: 36 氪报道
    location: 标题/链接
  - ref: NMPA 注册证
    location: 编号
---

# 瑞景医疗:国产 OCTA 眼底成像设备厂商

瑞景医疗(深圳瑞景医疗科技有限公司)是一家 2019 年成立于深圳的
医疗器械厂商,专注于 OCTA(光学相干断层扫描血管成像)眼底成像设备
的研发与制造,核心产品线为锐视系列。2024 年,锐视系列 OCTA 设备获得
国家药监局(NMPA)三类医疗器械注册证。

## OCTA 是什么,瑞景做什么
[answers "什么是 OCTA" / "瑞景医疗是做什么的"]

## 锐视系列:产品范围与边界
[answers "锐视系列覆盖哪些机型" / "OCTA 与 OCT 的区别"]

## 国产 vs 进口 OCTA 设备的临床差异
[answers "国产 OCTA 和进口 OCTA 有什么区别" — comparison anchor]

## 资质与可信来源
[NMPA 注册证编号、36 氪报道引用、产品手册依据]

## 常见问题
[5–6 个真实用户问题,每个一段实答]

## 来源
- 产品手册(用户提供)P12 §3 — 锐视系列机型规格
- 36 氪报道(标题/链接) — 融资信息
- NMPA 注册证信息(编号) — 三类证资质
```

**Contrast — what NOT to output:**

- Incorrect: 开头写"瑞景医疗是一家致力于用创新科技守护人类视觉健康的领军企业"
  — 纯形容词,无实体边界,AI 抓取后无法归因,易被忽略或幻觉。
- Correct: 开头写"瑞景医疗是一家 2019 年成立于深圳的 OCTA 眼底成像设备厂商"
  — 实体 + 属性 + 边界,一句话可被 AI 直接引用。
- Rationale: generative engines cite sentences that carry a verifiable subject
  + predicate; adjective stacks carry no citable information and get dropped or
  distorted.

## Pre-ship checklist

Frontmatter
- [ ] `name` and `description` present; description in third person with
  concrete trigger phrases; slightly pushy against undertriggering.
- [ ] Description states both what it does AND when to use it.

Body
- [ ] Imperative voice throughout (no "you should").
- [ ] Lean (<500 lines); reread-on-demand material moved to `references/`.
- [ ] Every absolute ("must"/"do not") explains its why or is genuinely
  non-negotiable (verifiability, anti-hallucination).
- [ ] Effort calibrated to input size, not one rigid number.

Resources
- [ ] Each `references/` file referenced from SKILL.md with a "read when…"
  pointer.
- [ ] No fact duplicated between SKILL.md and `references/`.

Examples
- [ ] At least one Input→Output shape; one Correct-vs-Incorrect contrast with
  rationale.
- [ ] The audit exposes legibility coverage (entity / fact / question /
  traceability) and a hallucination-risk level; it does NOT emit an
  "AI citation probability" score.
