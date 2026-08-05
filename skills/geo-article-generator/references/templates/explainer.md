# Template — Explainer / Definition / Brand

Read at Step 5 when Genre Router selected **Explainer**, **Definition**,
**Company/Brand**, or as fallback. Compose sections from
`../retrieval-units.md`. For Listicle / Comparison / Review / etc., use the
matching file in this folder.

Genre chooses the skeleton; Retrieval Units carve each section
(One Question → One Chunk → One Primary Answer).

Drop a section only when Step 3 has no matching question. Never keep an empty
section.

## Skeleton (Retrieval Units)

```text
Lead (= Summary + Definition seeds)
├── Definition          → What is X?
├── Scope & boundary    → What is / is not in scope?
├── Evidence            → Why trust this?
├── Comparison (opt.)   → X vs Y?
├── FAQ items (opt.)
└── Sources
```

## Lead block (always present)

First paragraph, 2–4 sentences. Must contain:

1. The core entity's full canonical name (+ alias / English / abbreviation if
   relevant).
2. A one-line definition that distinguishes it from namesakes.
3. The single most distinguishing verifiable fact (founding year + location,
   or core product + certification, or category + scope).

Write as a complete, self-contained, citable statement — no bare pronouns
("该系统", "我们", "该公司"). Restate the canonical name.

## Definition

**Unit:** Definition. Answers identification questions. Category + scope in
plain language; lay version first, then technical if needed.

## Scope & boundary

**Unit:** Best For / boundary prose. Concrete in-scope and out-of-scope items.
High GEO value for summarizers drawing edges.

## Evidence

**Unit:** Evidence. Credentials, filings, third-party coverage, named cases.
Each item sourced.

## Comparison (optional)

**Unit:** Comparison (+ Feature Matrix if useful). Both sides defined; concrete
dimensions, not vibes.

## FAQ (optional)

**Unit:** FAQ item per question. Real user phrasings; 2–4 sentence answers;
no duplicate of a full earlier section.

## Sources

**Two layers — do not mix in the publishable body:**

1. **Reader-facing「来源」** — title + public URL only. Blank line between major
   blocks for CPA HTML (`<p><br></p>`).
2. **Internal audit** — located sources in `geo-metadata.json` / `sources.md` /
   delivery note.

## What to omit

Adjective stacks, vague metrics, vision quotes with no fact, filler
transitions, duplicate restatements of the same fact.
