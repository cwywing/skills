# GEO principles — the five layers

Provenance: distilled from the GEO article this skill was built from
(Generative Engine Optimization, 2026). Each layer is a *failure mode* an AI
engine hits when summarizing a brand/topic, paired with the editorial fix.

Read this when drafting a section that touches a specific layer, or when the
user asks *why* the article is structured the way it is.

## 1. Information structuring (基础信息结构化)

**Failure mode:** the same fact reads differently across the brand's public
surface (website says one thing, press release another, founder interview a
third). A human reader reconciles via context; an AI engine *amplifies* the
inconsistency into a wrong answer.

**Fix:** pick one canonical value per attribute (founding year, location,
scope, team size, product names) and use it verbatim everywhere. If the
materials disagree, surface the conflict and choose one before drafting —
never blend ("约 2018–2019 年成立") and never silently pick.

**Why it matters for citation:** AI engines weight *stable* information higher.
A fact that reads the same across multiple sources is treated as more
trustworthy than one that fluctuates. Internal consistency is free authority.

## 2. Verifiability (内容可验证性)

**Failure mode:** a claim floats with no anchor. The AI cannot tell whether to
trust it, so it either drops it or repeats it as a hedged "据称".

**Fix:** tie every factual claim to a source — supplied material, named
report, public database, regulatory filing. Inline attribution ("据 [来源]")
is enough; the goal is a chain a summarizer can follow. Claims with no source
are cut, not polished. Carry the source *location* (document + page / section
/ anchor) alongside the source name, so a corrector can jump to the exact
spot — a source name alone is hard to verify after the fact.

**Fact Table as the single source of truth:** when the user supplies a
structured Fact Table / Entity Registry, it is the canonical source for every
attribute and claim — the article does not re-derive covered facts from raw
materials. When no table is supplied, the skill builds a transient one in
Step 2 and treats it the same way. This is what makes consistency enforceable
across many articles instead of case-by-case.

**Cross-corroboration bonus:** if the same fact appears in the brand's own
material *and* an independent third party, say so. AI engines treat
independently-corroborated facts as more authoritative than self-claims.

## 3. Semantic coverage, not keyword coverage (语义覆盖)

**Failure mode:** SEO-era habit of building pages around keyword variants.
GEO queries are full questions ("中国市场有哪些 GLP-1 类药物已获批用于减重"),
not keyword strings. Keyword-stuffed content answers no real question and gets
skipped.

**Fix:** build the article from a *question set* (Step 3), not a keyword list.
Each section answers at least one real user question. Cover the
comparison/boundary questions explicitly — "X vs Y 有什么区别", "X 适用于哪些
场景" — because those are exactly the queries AI engines surface as
generated answers.

**Why boundary sections outperform self-praise:** a section that defines what
the entity is *not* gives the summarizer a clean edge to draw; three
paragraphs of adjectives give it nothing.

## 4. Entity clarity (品牌实体清晰度)

**Failure mode:** the entity is ambiguous — generic name, abbreviation
collision with another company, product/company/domain/social handles all
different, founder info missing. Humans resolve this by context; AI engines
misattribute or fail to recognize the entity at all.

**Fix:** in the first paragraph, state the full canonical name (and aliases,
English name, abbreviation expansion) plus a one-line definition that
distinguishes it from namesakes. Ensure product name, company name, and domain
agree; if they don't, that's a brand problem to flag to the user, not a
writing problem to paper over.

**The one-sentence test:** can a reader (or AI) who has never heard of the
entity correctly answer "who/what is this and what do they do" after the first
sentence? If not, rewrite the lead.

## 5. Anti-hallucination and correction (反幻觉与纠错)

**Failure mode:** the article contains a wrong number, a wrong address, an
outdated team size, a mis-stated certification. AI engines present generated
answers in a confident tone, so errors propagate *as if verified*. A wrong
citation is worse than no citation.

**Fix:** in Step 5, run every concrete fact (numbers, dates, addresses, names,
credentials, customer lists) against the source materials. Anything not backed
gets cut. If the user supplied a known-wrong public fact to correct, state the
correction explicitly and cite the authoritative source — this is one of the
few cases where repeating the wrong fact (to correct it) is useful, but frame
it as "X 误传为 A,实际为 B,依据 [来源]".

**Why this layer is non-negotiable:** the other four layers raise the chance
of being cited; this layer prevents being cited *wrongly*. A brand misquoted
in a generated answer loses more trust than a brand absent from it.
