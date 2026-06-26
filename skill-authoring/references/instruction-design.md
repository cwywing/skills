# Designing instructions a model will actually follow

Provenance: Fable 5 system prompt — `core_search_behaviors` item 2 (scale to complexity), `artifact_usage_criteria` (USE / DO NOT USE lists), and the copyright "Self-check before responding" block (`../../CLAUDE-FABLE-5/README.md`); official `skill-creator` ("Improving the skill") and `skill-development` (progressive disclosure).

## Knowledge goes in references/, not the body

The body loads every time the skill fires; `references/` load only when the model reaches for them. So keep procedure and pointers in SKILL.md, and move everything the model rereads — schemas, API docs, domain facts, long policies, worked walkthroughs — into `references/`. This is the knowledge-base pattern: the body says *how*, the references hold *what*. Keep each fact in one place only; duplication drifts out of sync and burns context. For a large reference file, add a table of contents or grep hints at the top so the model can jump to the relevant part.

## Explain the why; reserve absolutes for the non-negotiable

This is the central tension between a raw system prompt and a good skill, and it is worth getting right.

A production prompt like Fable 5 leans on ALL-CAPS absolutes — "NEVER," "SEVERE VIOLATION," "NON-NEGOTIABLE" — but it spends that register almost entirely on a short list of bright-line constraints: copyright limits, child safety, weapons. The official skill-creator guidance is blunt that for ordinary content, all-caps MUST/NEVER is a *yellow flag*, and "if possible, reframe and explain the reasoning so that the model understands why."

Reconcile the two with one rule:

> Use an absolute imperative only when the constraint is genuinely bright-line — a safety, legal, or correctness rule that must never be reasoned away. For the other ~95% of a skill (workflow, craft, formatting, preferences), explain the why and let the model apply judgment.

Why it works: a model given reasons has good theory of mind and adapts the intent to cases you did not foresee. A model given a wall of MUSTs either overfits to your examples or spends effort lawyering the edges. Reasons generalize; decrees don't.

## Calibrate effort to the task — don't hard-code one number

Avoid "always do X searches" or "always write N paragraphs." State tiers keyed to difficulty, the way Fable 5 scales tool calls:

> 1 call for a single fact; 3–5 for a medium task; 5–10 for deeper research; if it would take 20+, suggest a different tool.

The pattern is to give the model a cheap-vs-thorough spectrum plus the cue for choosing a point on it. This beats both a rigid rule (wrong half the time) and silence (the model guesses, inconsistently).

## Decision criteria as parallel USE / DON'T lists

When the skill must choose between two paths, give two short concrete lists rather than a paragraph. The Fable 5 artifact rule is the model:

> Use artifacts for: code over 20 lines; content used outside the chat; a document over 1500 characters.
> Do NOT use artifacts for: snippets of 20 lines or fewer; lists and tables; short conversational replies.

Concrete thresholds (20 lines, 1500 characters) and concrete cases make the boundary checkable instead of a matter of vibes.

## Give the model a pre-action self-check

For the failure modes that matter, embed a short checklist the model runs *before* acting. Fable 5 does this for copyright: "Is this quote 15+ words? Have I already quoted this source?" A handful of yes/no questions at the decision point catches more than a long warning paragraph, because it converts a vague rule into a concrete test applied at the right moment.

## Write for reuse, not for your three test cases

(From skill-creator's "Improving the skill.") You draft and test against a few cases, but the skill will run across thousands. When a stubborn issue tempts you toward a fiddly example-specific patch or an oppressive MUST, step back and change the metaphor, explain the principle, or restructure — those transfer; overfit rules don't. Read the *transcripts* of test runs, not just the outputs: if every run independently wrote the same helper script, bundle it in `scripts/` instead of describing it each time.
