# Retrieval Units — composable answer chunks

Read at **Step 5** while drafting (any genre). GEO / LLM retrieval works on
**chunks**, not whole essays. An article is an assembly of **Retrieval Units**
under a Genre skeleton — not free-form prose that happens to have headings.

`atomic-blocks.md` is an alias pointer to this file (legacy name).

## Core rule

```text
One Question  →  One Chunk  →  One Primary Answer
```

- **One Question:** the chunk targets a single query.
- **One Chunk:** one H2/H3 (or table / FAQ item) is the retrieval boundary.
- **One Primary Answer:** that chunk answers **only** that query. Do not pack
  pricing + pros + history + review into a "Pricing" section — embeddings and
  extractors degrade when one chunk serves five intents.

**Test:** cut the section out of the article. Can it still answer its target
query without prior-paragraph pronouns or setup? If it also answers a second
unrelated query, split it.

## Unit catalog

| Retrieval Unit | Answers (examples) | Typical shape |
|----------------|--------------------|---------------|
| **Definition** | What is X? | Short paragraph; entity restated |
| **Summary / TL;DR** | What's the short answer? | 3–6 sentences or bullets |
| **Comparison** | X vs Y? | Table or paired dimensions |
| **Feature Matrix** | How do they differ? | Rows = features, cols = products |
| **Pricing** | What does it cost? | Plans, currency, as-of date — **only cost** |
| **Pros** | Advantages? | Bullets; verifiable |
| **Cons** | Limitations? | Bullets; real tradeoffs |
| **Best For** | Who is it for? | Personas; optional Not For |
| **Overview** | What is this item? | One short entity hub paragraph |
| **Evidence** | Why trust this? | Named sources, certs, cases |
| **Timeline / Checklist** | Steps / order? | Numbered or `- [ ]` |
| **FAQ item** | Long-tail / dialogue Q | One Q + 2–4 sentence A |
| **Decision Tree** | Conditional "which should I choose?" | If/then paths |
| **Recommendation** | Which should I choose? (summary) | Short pick + criterion |

Use a unit only when Step 3 has a matching question. Empty decorative units
hurt GEO.

## Composition

1. Genre template (`templates/*.md`) orders units; this file defines each unit.
2. Restate the entity inside the chunk when a sentence might be cited alone.
3. Prefer structure (table / list) over adjective paragraphs for Evaluate /
   Compare / Decide needs.
4. **Coverage:** every filtered question should map to ≥1 Retrieval Unit
   (see Coverage Check in `self-check.md`).
5. Cross-genre: Explainer may be Definition + Scope + Evidence + FAQ;
   Listicle stacks Summary + Comparison table + per-item Overview/Pros/Cons/
   Pricing + Decision Tree + FAQ.

## Anti-patterns

- One mega-section mixing Pricing + Pros + story + CTA.
- A "Pricing" unit that also sells features and history.
- Pros without Cons in Review/Listicle items when materials allow Cons.
- FAQ of keyword variants instead of real questions.
- Treating Listicle itself as a Retrieval Unit — Listicle is a **Genre** that
  *composes* units.
