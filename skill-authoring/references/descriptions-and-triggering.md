# Writing the description (the trigger)

Provenance: Fable 5 system prompt — the `ask_user_input_v0` tool description under "Tool Definitions" (`../../CLAUDE-FABLE-5/README.md`); official `skill-creator` ("Write the SKILL.md" and "Description Optimization"); official `skill-development` ("Metadata Quality").

## Why this is the highest-leverage text in the skill

The model never sees a skill's body until the skill is selected, and it selects from name + description alone. A perfect body behind a vague description is dead weight. Spend disproportionate effort here — more than on any single section of the body.

## The shape: what + when, in third person

Write the description in third person and make it carry two things at once: what the skill does, and the concrete situations that should trigger it. Put *all* "when to use" information here — never in the body.

```
This skill should be used when <situations>, e.g. when the user says
"<phrase 1>", "<phrase 2>", or "<phrase 3>". It <what it does>.
Use it even when <near-miss the model would otherwise skip>.
```

## Lean pushy — to combat undertriggering

Current models *under*-trigger skills: they skip them when they would help. Counter it by naming explicit phrases and adding a nudge for the case the model would otherwise handle bareheaded. The skill-creator guidance gives the canonical move: instead of "How to build a dashboard for internal data," write "…Make sure to use this skill whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of company data, even if they don't explicitly ask for a 'dashboard.'"

Push *precisely*, not broadly. An overbroad description causes mis-triggering, which trains the user to ignore the skill. Aim the nudge at genuine near-misses, not at everything adjacent.

## The WHEN-TO / WHEN-NOT pattern

The strongest tool and skill descriptions in production prompts pair "when to use" with "when NOT to use," each with concrete cases. The Fable 5 `ask_user_input_v0` description is the exemplar: positive cases ("Help me plan a workout" → ask about goals, time, equipment) sit next to negative cases ("Should I learn Python or JavaScript?" → the user wants analysis, not the options echoed back; the user is venting → just listen).

Do the same. When mis-triggering is a real risk, add a short "When to use / When not to use" block in the body with two or three concrete cases each. The negatives carry the most signal — the valuable ones are *near-misses* that share keywords with the skill but actually need a different tool.

## Concrete over abstract — always

Trigger examples must look like real user messages: file paths, names, casual phrasing, typos, a little backstory. Abstract stubs neither test nor teach triggering. (Source: skill-creator, Description Optimization, Step 1.)

- Weak: `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`
- Strong: `"ok my boss just sent me this xlsx (its in downloads, called something like 'Q4 sales final FINAL v2.xlsx') and wants a profit-margin % column — revenue's in column C, costs in D i think"`

## Quick test before shipping a description

- Would it fire on the three phrasings a real user would actually type?
- Would it *not* fire on the nearest adjacent task that needs a different tool?
- Does it state *when* to use the skill, not only *what* it is?
