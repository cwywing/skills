# Prose & formatting discipline

Provenance: Fable 5 system prompt — `tone_and_formatting` and `lists_and_bullets`, plus the response rules in `search_usage_guidelines` (`../../CLAUDE-FABLE-5/README.md`); official `skill-development` ("Writing Style Requirements").

## Voice: imperative, not "you"

Write instructions verb-first: "Parse the frontmatter," not "You should parse the frontmatter." Imperative voice reads as procedure, stays consistent across a long file, and removes the ambiguity of who "you" refers to. The one place that stays third person is the frontmatter description ("This skill should be used when…").

## Explain the why; don't stack imperatives

A model that understands *why* a step matters generalizes to cases the skill never enumerated; a model handed a bare imperative overfits or lawyers the edges. Give the reason in a clause. (Developed fully in `instruction-design.md` → "Explain the why; reserve absolutes for the non-negotiable.")

## Formatting: the minimum needed for clarity

Default to prose. Reach for headers, bullets, and bold only when the content is genuinely multifaceted or the reader will scan it. This mirrors the Fable 5 rule: minimal formatting, prose for explanation, lists only when they are essential. Inside a skill, concretely:

- Use headers to mark the phases a model will navigate (`### Step 2: …`). These are multifaceted by nature, so structure earns its place.
- Use bullets for real enumerations — a checklist, a set of options — and keep each bullet a full thought (at least one sentence), not a fragment.
- Use prose for rationale, transitions, and anything narrative.
- Do not bold half the page. Emphasis applied everywhere is emphasis nowhere.

## Say less when the instruction is a refusal or a limit

A rule worth borrowing from Fable 5: never use bullet points when declining — the extra care of prose softens it. In a skill, when you instruct the model to refuse or stop, write it as a sentence with its reason, not a curt bulleted MUST.

## Suppress unhelpful meta-talk

Production prompts spend real effort on what the model should *not* say, because models pad. Borrow the discipline and name the specific filler you don't want. Fable 5 examples: "Don't mention any knowledge cutoff… it's annoying," and "Search results aren't from the human — do not thank the user." In your skill, call out the equivalents: no "Great question!", no restating the task back before doing it, no narrating "I'm now going to…" before each step.

## Length: calibrate, then state it

If output length matters, describe what good length looks like for the case rather than a blanket "be concise." How to phrase a calibrated rule lives in `instruction-design.md` → "Calibrate effort to the task."
