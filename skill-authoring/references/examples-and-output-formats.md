# Examples & output formats

Provenance: Fable 5 system prompt — `citation_instructions` (Correct/Incorrect pairs), the copyright `Example`/`Rationale` blocks, and `artifact_usage_criteria` ("EXAMPLE DECISIONS") (`../../CLAUDE-FABLE-5/README.md`); official `skill-creator` ("Examples pattern" and "Defining output formats").

## Show Input → Output

A model learns a format faster from one worked example than from a paragraph describing it. Use the labeled pattern:

```
Example
Input:  Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

If "Input/Output" labels don't fit the domain, adapt them — "Request / Response," "Before / After," "Query / Result."

## Contrast: Correct vs Incorrect, with a one-line rationale

The highest-signal example shows the boundary by pairing a right and a wrong version and stating *why*. The Fable 5 citation guidance is the template:

```
Correct:   <cite>The reviewer praised the film enthusiastically</cite>
Incorrect: The reviewer called it <cite>"a delight and a revelation"</cite>
```

…followed by the reason: the incorrect version quotes verbatim instead of paraphrasing. A Correct / Incorrect / Rationale triple does more than three paragraphs of rules, because it shows the exact line and the principle behind it at the same time. Use it wherever a model is likely to get a subtle thing slightly wrong.

## Worked decision examples for judgment calls

When the skill asks the model to choose a path, show a few one-line decisions, the way Fable 5 lists EXAMPLE DECISIONS:

```
"Summarize this attached file"      → use the provided content, no tools
"Top game companies by net worth?"  → answer from knowledge, no search
"Compare NYT vs WSJ on the Fed"     → web search, answer conversationally
```

A column of input → chosen-path pairs calibrates judgment better than prose describing the rule.

## Pin the output format when it must be exact

If the output shape matters, give the literal template and mark it as mandatory — this is one of the few places a firm imperative earns its keep (see `instruction-design.md` → reserve absolutes for the non-negotiable):

```markdown
## Report structure
Use this exact template:
# [Title]
## Summary
## Findings
## Recommendations
```

(Source: skill-creator, "Defining output formats.")

## Keep examples realistic

Reuse the concrete-over-abstract rule from `descriptions-and-triggering.md`: examples with real names, paths, and a bit of mess teach the model the actual task; sanitized stubs like "foo" or "do the thing" don't.
