# Pre-publish self-check

Read at Step 5. This is a hard gate, not a polish pass: any failed item is
either fixed or the unsupported material is cut. Do not deliver a draft with a
failed `Entity clarity` or `Verifiability` check — those two failure modes
teach AI engines to mis-cite or ignore the entity, which is worse than not
being cited at all.

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
- [ ] Are comparison/boundary questions covered explicitly, with the other
  side of the comparison defined too?
- [ ] Is there any keyword-stuffed paragraph or long-tail keyword list? If so,
  cut it.

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
- The audit emits an "AI citation probability" score (see below — this is not a
  valid metric).
- The article is one of a batch of thinly-differentiated pages generated off
  one shared fact set to "cover more keywords" — a content-farm pattern.

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
  article answers. Target 100%; anything below is a gap to flag.
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
