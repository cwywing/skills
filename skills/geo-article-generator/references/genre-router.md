# Genre Router — Intent → Information Need → Genre → Template

Read at **Step 4** before drafting. Listicle is **one genre among many**, not
the default and not a GEO principle.

## Pipeline

```text
Search Intent  →  Information Need  →  Genre  →  Template
```

- **Search Intent** may shift as engines rename buckets; keep it aligned with
  classic search + GEO practice.
- **Information Need** is the stable middle layer (Learn / Evaluate / Compare /
  Decide / Fix / Reach / Act). Prefer routing on Need when Intent labels drift.
- **Genre** selects the article skeleton.
- **Template** is a file under `templates/` that composes **Retrieval Units**
  (`retrieval-units.md`).

## 1. Classify Search Intent (from Step 1)

| Intent | User is trying to… | Typical query shape |
|--------|--------------------|---------------------|
| **Informational** | Understand / learn | What is X? How does X work? |
| **Navigational** | Reach a specific entity | X official site, X docs |
| **Commercial** | Evaluate / select before buying | Best X, X vs Y, alternatives, review |
| **Transactional** | Act / buy / sign up | Pricing, buy X, X plans |
| **Troubleshooting** | Fix a failure | Error / how to fix / not working |

A single article usually owns **one primary intent**. Secondary intents may
appear as sections, but do not force every genre into one article.

## 2. Map Intent → Information Need → Genre

| Intent | Information Need | Preferred Genre(s) |
|--------|------------------|--------------------|
| Informational | **Learn** | Explainer, Definition, Tutorial, News |
| Informational | **Understand why** | Explainer + Evidence units |
| Navigational | **Reach** | Brand, Company |
| Commercial | **Evaluate** | Listicle, Review |
| Commercial | **Compare** | Comparison, Benchmark |
| Commercial | **Select** | Listicle, Buying Guide, Decision Tree–heavy |
| Transactional | **Decide / Act** | Buying Guide, Review (pricing-forward) |
| Troubleshooting | **Fix** | FAQ / Guide / Tutorial |

Commercial Need refinements:

| Information Need | Genre |
|------------------|--------|
| Evaluate (Best / Top N) | **Listicle** |
| Compare (A vs B) | **Comparison** |
| Measure (numbers side-by-side) | **Benchmark** |
| Judge one product | **Review** |
| Pick under constraints | Buying Guide / Listicle + Decision Tree |

## 3. Genre → Template catalog

Templates live in `references/templates/`. Missing file → fall back to
`templates/explainer.md` and compose from Retrieval Units.

| Genre | When to use | Template |
|-------|-------------|----------|
| **Explainer** | Concept / category overview | `templates/explainer.md` |
| **Definition** | "What is X" as the whole piece | `templates/explainer.md` (Definition-heavy) |
| **Company / Brand** | Entity hub | `templates/explainer.md` |
| **Tutorial / Guide** | How-to, step sequence | `templates/tutorial.md` |
| **Listicle** | Top N / Best / ranked picks | `templates/listicle.md` |
| **Comparison** | X vs Y on shared dimensions | `templates/comparison.md` |
| **Review** | Single-product deep dive | `templates/review.md` |
| **Benchmark** | Metric-led side-by-side | `templates/benchmark.md` |
| **Case Study** | Named customer outcome | `templates/explainer.md` (Evidence-forward) |
| **News** | Time-bound announcement | `templates/news.md` |

New genres: add a row here + a file under `templates/` — **do not** change the
Workflow steps in `SKILL.md`.

## 4. Examples

```text
"What is LangChain"
  → Informational → Learn → Explainer → templates/explainer.md

"Best AI IDE 2026"
  → Commercial → Evaluate → Listicle → templates/listicle.md

"Cursor vs Claude Code"
  → Commercial → Compare → Comparison → templates/comparison.md

"X pricing plans"
  → Transactional → Decide/Act → Buying Guide / Review → templates/review.md

"X install fails with error Y"
  → Troubleshooting → Fix → FAQ/Guide → templates/tutorial.md
```

## 5. Hard rules

- **Do not** default every article to Listicle.
- **Do not** treat "Listicle gets more GEO traffic" as a principle.
- Route on **Information Need** first when Intent is ambiguous.
- Materials that "look like a list" do not override a Learn need.
- State `{intent, information_need, genre, template}` in the delivery note.
