# Prose & formatting discipline

Provenance: Fable 5 system prompt — `tone_and_formatting` and `lists_and_bullets`, plus the response rules in `search_usage_guidelines` (`../../../CLAUDE-FABLE-5/README.md`); official `skill-development` ("Writing Style Requirements"); `shb-*` skill suite (`.agents/skills/shb-*`) for the hide-implementation-mechanics extension of the meta-talk rule.

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

### Hide implementation mechanics, not just filler

The meta-talk rule has a deeper register for skills that wrap a tool, API, or internal system. There the filler isn't pleasantries — it's **leaked implementation detail.** Models narrate their own mechanics by default: which command they ran, which field they sorted by, the pagination they walked, the JSON shape they parsed. To the model this reads as transparency; to the user it reads as jargon about a system they did not ask to inspect.

Name the leak categories the skill should strip from user-facing output. The recurring ones:

- **Interface identifiers** — API field names, command names, flags, internal codes. Translate "totalElements is 189" into "189 tickets"; "state=processing" into "in progress."
- **Internal IDs and UUIDs** — entity identifiers the model uses to chain calls but that mean nothing to a user. Refer to an entity by its name and its business-facing number ("客户 林林科技 (CUS20260605001)"), never by "林林科技 (id: 0f384496-…)." The ID string itself is the leak, not just the label `id:`.
- **Opaque field keys** — custom-field maps whose keys are machine names (`field_x7k2`). Look up the metadata and show the human label, or omit the field; do not print the key.
- **Fetch mechanics** — pagination, truncation handling, envelope unwrapping, "I pulled all pages then merged." How the model got the data is not the user's concern; the result is.

The cleanest way to state this is one rule covering the whole spectrum: *anything the model does to obtain or format a result is backstage; the reply contains only the result, in the user's vocabulary.* This subsumes the pleasantries case ("Great question!" is backstage narration too) and extends naturally to implementation leaks. Phrase it firmly — this is a bright-line for any skill that acts on a user's behalf, because leaked mechanics read as either noise or, worse, as the model implying the user should have done the work themselves.

For skills that mutate state, the same principle applies to confirmation messages: restate scope in business terms (names, counts, what changes), not in command syntax. See `mutation-safety.md` → "Confirm scope in human terms."

## Length: calibrate, then state it

If output length matters, describe what good length looks like for the case rather than a blanket "be concise." How to phrase a calibrated rule lives in `instruction-design.md` → "Calibrate effort to the task."
