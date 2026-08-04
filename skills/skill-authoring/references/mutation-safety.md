# Safety for skills that change real state

Provenance: `shb-*` skill suite (`.agents/skills/shb-task`, `shb-event`, `shb-customer`, `shb-warehouse-material` and siblings) — patterns hard-won from a production skill suite that creates, updates, and deletes live business records (tickets, customers, inventory) on behalf of real users. This file generalizes them for any skill whose actions have side effects.

This is the safety layer for **mutations** — create, update, delete, deploy, send, assign, approve. The rest of this skill set assumes content generation; a skill that writes to a system needs the extra discipline below.

## Why mutations deserve their own rules

A content-generation skill that drifts produces a bad paragraph; a mutation skill that drifts deletes the wrong record, overwrites a customer file, or sends a message to the wrong person. Three properties make mutations categorically harder:

- **Side effects are real.** Every call is a live write against a production system, not a sandbox. A retry is a second write, not a rewind.
- **Failures are often silent.** The system accepts the request, the record changes, and the mistake surfaces only later — by which point there is no undo.
- **The model is eager to "help."** Left to its defaults, a model will invent an ID it was never given, retry a failed write by varying fields at random, or call a destructive command because the user sounded impatient.

The rules below exist because each one names a failure mode that actually happened, more than once, before the rule was written.

## Rate the risk before acting — not all writes are equal

Split a skill's write operations into two tiers and gate each tier differently. State the split as a small table in the body, so the model checks it at the decision point:

| Tier | Examples | Gate |
| --- | --- | --- |
| Lower risk | Single-record create / update; status change; assignment | Confirm intent once, then act |
| Higher risk (all-or-nothing, bulk, or irreversible) | Delete; bulk update; deploy; anything with no rollback | Require an explicit confirmation of scope, or a `--dry-run` first |

The bright line is **can it be undone, and how wide is the blast radius?** A single update touches one record; a bulk update writes the same value across many; a delete is a soft-delete at best and often permanent. Bulk and irreversible operations earn a second confirmation gate — not as a formality, but because the model and the user genuinely lose track of how many records "all of them" means.

Do not add the gate automatically on the model's behalf. Have the model restate the scope to the user ("This will delete 14 records spanning three customers — proceed?") and wait. The confirmation is the safety device; auto-adding it disarms the device.

## Confirm scope in human terms before irreversible actions

Before a higher-risk write, the model restates what is about to happen using the names a user recognizes — not internal IDs, not field names, not query syntax. Compare:

- Wrong: "Deleting ids [102, 105, 108]. Confirm?"
- Right: "This will delete 3 materials: 螺丝 M6 (sn=MAT-001), 螺母 M6 (sn=MAT-014), 垫片 (sn=MAT-022). Proceed?"

The restated scope is also the model's last chance to notice it is about to act on the wrong things. If the user picks the target by name and the model is holding an ID, the model names it back; if the name and the ID disagree, that disagreement surfaces here instead of after the delete.

## fetch-then-merge when the backend replaces instead of patches

Many update APIs use **whole-object replacement** semantics: every field missing from the request body is cleared, not left alone. (Custom-field maps are sometimes the exception; system fields rarely are.) This is the single most common source of silent data loss in mutation skills.

Two defenses, in order of preference:

1. **Prefer a path that fetches before it writes.** If the CLI or wrapper offers a mode that loads the current record and merges the user's changes onto it, use it by default. Document it as the recommended path and warn that the raw-body path is dangerous.
2. **For the raw-body path, instruct the model to fetch the full current state, apply only the intended changes, and submit the merged object.** State this as a procedure ("first `get`, then overlay edits, then submit"), not a warning.

When you document this, name the exception precisely — which fields are safe incremental updates, which are wholesale replacement — because "be careful" does not generalize and the model cannot tell the difference from the field name alone.

## Failures are not a search space — do not explore by retrying

When a write fails, the error usually names the offending field or value (missing required field, uniqueness conflict, out-of-range, permission). The correct response is to read that signal, fix the one thing, and resubmit once.

What the model tends to do instead is treat the failure as a search problem: vary a few fields, resubmit, vary more, resubmit — "see which one works." Each iteration is a live write, and some of them land. By the time one "works," the record may have been written two or three times with partially-wrong data.

Instruct explicitly against this:

> On failure, locate the specific field or value the error names, change only that, and resubmit once. Do not vary unrelated fields to probe for a passing combination — every attempt is a real write, and partial writes accumulate. If the error does not name a cause, ask the user; do not keep guessing.

This converts a vague "be careful" into a concrete test applied at the exact moment the model is tempted to guess.

## IDs come only from results, never from the model's imagination

State-enforcing skills reference records by ID, and models hallucinate IDs readily — especially integer IDs, which look like something the user might have said, and especially when under pressure to "just do it." Two rules cover the failure modes:

- **Reuse, don't re-search.** Once an ID has appeared in any result this conversation, reuse it for every later reference to that entity. Re-running a search to "get the ID again" wastes a call and, worse, can return a *different* record if the data changed underneath.
- **Never fabricate.** The model must hold an ID that came from a result (a prior search, a detail fetch, a create's response) before it uses one. It must not pass a serial number, a user-spoken number, or an invented value where an ID is required. If no ID is in hand, run a query first; if the query finds nothing, stop and tell the user.

Integer IDs deserve an extra sentence, because the trap is specific: a user says "delete 102," and 102 is the *serial number*, not the *ID* — they diverge, and silently using one as the other acts on the wrong record or no record.

Name the legitimate exceptions explicitly. In one shipping skill, creating a ticket reuses *other* entity IDs from context but deliberately re-queries the customer ID fresh, because customer records churn. The rule is "reuse," not "never re-query" — re-query is allowed when staleness is the risk, not when laziness is.

## Make reference loading a gate, not a hint, for high-stakes operations

The skill spec's progressive disclosure says: put detail in `references/`, load on demand. For read operations "on demand" is fine — the model can muddle through. For writes, "on demand" is too soft: the model skips the reference and acts, and the detail it skipped was the fetch-then-merge rule it just violated.

When an operation carries real risk, escalate the loading instruction from a hint to a precondition. Two forms, by scale:

- **Per-operation loading table** (a single skill, several write commands): a table mapping each write command to the reference files that must be read first. The body says "before running X, read Y and Z" as a hard step, not a suggestion.
- **Extracted common-rules file** (a skill family sharing one backend): pull the cross-command safety rules — risk tiers, fetch-then-merge, the no-explore rule — into one `mutation-common.md` that every write path loads, so the rules live in one place rather than drifting across per-command docs.

The criterion is the same as for `MUST` vs. explain-the-why (see `instruction-design.md`): when skipping the reference causes an irreversible mistake, the loading instruction earns the harder register.

## A pre-action checklist for mutations

Combine the rules above into a short self-check the model runs before any write, adapted from the pre-action-checklist pattern in `instruction-design.md`:

- Is the target ID one I obtained from a result this conversation (not fabricated, not a serial number)?
- Is this a higher-risk operation (bulk, delete, deploy, irreversible)? If so, have I restated scope to the user and received confirmation?
- If updating against a replace-semantics backend, am I on the fetch-then-merge path — or, if not, have I loaded the full current record?
- Am I about to retry a failure? If so, do I know the specific cause, and am I changing only that?

Four yes/no questions at the decision point catch more than a long warning paragraph, because they convert vague caution into concrete tests applied at the exact moment the model is about to act.
