# Pre-publish self-check

Read at **Step 6**. This is a hard gate, not a polish pass: any failed item is
either fixed or the unsupported material is cut. Do not deliver a draft with a
failed `Entity clarity`, `Verifiability`, or `Extraction Check` gate — those
failure modes teach AI engines to mis-cite, ignore, or retrieve the wrong
chunk, which is worse than not being cited at all.

Run these as yes/no questions against the draft before handing it to the user.

## Entity clarity (non-negotiable)

- [ ] Does the first paragraph state the entity's full canonical name?
- [ ] Does the first sentence let a reader who has never heard of the entity
  correctly answer "who/what is this and what do they do"?
- [ ] Are aliases / English name / abbreviation expansion given once, early?
- [ ] If the name is generic or collides with another entity, is the
  disambiguating fact (location, year, full legal name) stated?
- [ ] Do product name, company name, and domain agree across the article? If
  they disagree, has the conflict been flagged to the user rather than
  papered over?

If any item fails, rewrite the lead before proceeding. Do not deliver with an
ambiguous entity.

## Verifiability (non-negotiable)

- [ ] Is every concrete factual claim (number, date, name, address,
  certification, customer, team size) tied to a source?
- [ ] Are all `UNVERIFIED` claims from Step 2 either sourced or cut?
- [ ] Does the sources block list every source relied on?
- [ ] Where a fact appears in both self-supplied and independent sources, is
  the independent corroboration noted?

If a claim cannot be sourced and cannot be cut (e.g. it is the article's
reason for existing), stop and ask the user for a source rather than shipping
an un-backed claim. Anti-hallucination outranks completeness.

## Semantic coverage

- [ ] Does every question in the Step 3 question set have a section that
  answers it?
- [ ] Does every section answer at least one real user question (not just
  exist for structure)?
- [ ] Are questions grouped under a primary Search Intent
  (Informational / Navigational / Commercial / Transactional)?
- [ ] Are comparison/boundary questions covered explicitly, with the other
  side of the comparison defined too?
- [ ] Is there any keyword-stuffed paragraph or long-tail keyword list? If so,
  cut it.

## Extraction Check (non-negotiable for chunk quality)

AI retrieval works on chunks. For **each** H2/H3 section (Retrieval Unit):

- [ ] Can this section **independently** answer one clear query if lifted alone?
- [ ] Is the target query nameable in one short phrase (e.g. "多少钱？",
  "优点？", "适合谁？", "X vs Y 哪个好？")?
- [ ] Does the section deliver **One Primary Answer** only (no packing pricing +
  pros + history into one chunk)?
- [ ] Does the section restate the entity where a cited sentence would otherwise
  lose the referent?
- [ ] Are mixed intents split into separate Retrieval Units?

Genre-specific (only if that genre was selected in Step 4):

- **Listicle:** TL;DR present? Quick Comparison Table present? Each #N item has
  Overview + Pros + Cons + Pricing as **separate** units (or explicit gap)?
  Ranking rule stated?
- **Comparison:** shared dimensions for both sides? Matrix/table extractable?
- **Review:** Pros and Cons both present when materials allow?

If a section fails Extraction Check, split or rewrite it before shipping.

## Coverage Check (non-negotiable for question→unit mapping)

Trace: **Search Intent / Information Need → Questions (Step 3) → Retrieval
Units in the draft.**

For every filtered question in Step 3:

- [ ] Is there ≥1 Retrieval Unit (heading / table / FAQ item) that answers it?
- [ ] Is the mapping explicit enough to name (e.g. What→Definition, How→Tutorial
  steps, Why→Evidence, Price→Pricing, Alternative→Comparison)?

Report **Question→Unit coverage %** in the delivery note (answered questions /
filtered question set). Target ≥95% for ship; anything below is a gap to fix or
an explicit deferral stated to the user.

Example trace:

```text
What is X?     → Definition     ✓
How to install → Timeline steps ✓
Why trust?     → Evidence       ✓
How much?      → Pricing        ✓
X vs Y?        → Comparison     ✓
```

Coverage Check is higher value than "does an FAQ section exist."

## Consistency

- [ ] Does each attribute (founding year, location, scope, product names) read
  identically everywhere it appears?
- [ ] Is any fact stated in two different wordings across the article? If so,
  pick one canonical phrasing.

## Anti-hallucination sweep

- [ ] Run a pass over every concrete fact and recheck it against the source
  materials. List any discrepancies; fix or cut.
- [ ] Are there adjective stacks with no referent ("leading", "innovative",
  "industry-first" without a source)? Cut them.
- [ ] Are there vague metrics ("thousands of", "widely used") with no number?
  Cut or quantify.
- [ ] If correcting a known-wrong public fact, is the correction stated as
  "误传为 A,实际为 B,依据 [来源]" with an authoritative source?

## Red flags — do not ship if any present

- The lead paragraph is all adjectives and vision statements with no
  verifiable subject+predicate.
- The same attribute reads two different ways in the article.
- A factual claim has no source and was not marked `UNVERIFIED`/cut.
- A "FAQ" section exists but its questions are invented keywords, not real
  user phrasings.
- The article promises or implies a guaranteed AI-citation outcome.
- The article claims "Listicle = GEO traffic" (or any single genre) as a
  guaranteed mechanism — frame format as Genre Router choice + extractable
  blocks, not a ranking promise.
- The audit emits an "AI citation probability" score (see below — this is not a
  valid metric).
- The article is one of a batch of thinly-differentiated pages generated off
  one shared fact set to "cover more keywords" — a content-farm pattern.
- A section fails Extraction Check (cannot answer one query as a standalone
  chunk, or packs multiple primary answers).
- Coverage Check fails: a Step 3 question has no mapped Retrieval Unit and was
  not explicitly deferred.

If a red flag is present, fix it or cut the offending section. Then re-run the
self-check from the top.

## Scored audit (report in the delivery note)

After the gate items pass, score the draft on five legibility dimensions. These
measure properties of *the article itself*, not predictions of what any AI
engine will do with it. Report as percentages or a level, computed against the
Step 2 entity/claim inventory and the Step 3 question set.

- **Entity coverage %** — share of the core entity's attributes (from the Fact
  Table / Step 2 inventory) that the article states, in canonical form.
- **Fact coverage %** — share of verifiable claims the article actually uses,
  vs. those available and relevant. Low coverage is not always bad (the article
  may be tightly scoped) — flag only when a question-set answer is missing a
  backing fact that exists.
- **Question coverage %** — share of the Step 3 filtered question set that the
  article answers (same denominator as Coverage Check / Question→Unit
  coverage). Target 100%; anything below is a gap to flag.
- **Question→Unit coverage %** — share of filtered questions that map to an
  explicit Retrieval Unit (report alongside Question coverage; usually equal
  when Extraction Check passes).
- **Source-traceability %** — share of factual claims that carry a source *
  and location* (document + page / section / anchor). Target 100%.
- **Hallucination-risk level** — Low / Medium / High. Low = every claim traced
  to a source location; Medium = some claims sourced but locations missing or
  some `UNVERIFIED` retained with disclosure; High = claims present without any
  source. High-risk drafts do not ship.

### Metrics that are NOT valid here

- **"AI citation probability"** is not a measurable property of the article.
  No one controls generative engine output, and any "probability of being
  cited" score is a fake-precise promise — the same kind of guarantee the
  source GEO thesis rejects. Do not emit it.
- Five-star or 0–10 "quality" scores with no defined denominator are theater.
  Every score above is a ratio against a concrete inventory (entities, claims,
  questions) or a defined level — keep it that way.
