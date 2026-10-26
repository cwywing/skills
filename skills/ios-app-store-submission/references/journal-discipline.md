# Journal discipline — docs/submissions/ and the machine gates

Read this file before the first journal write of a session. The journal exists
because submission work spans days and multiple operators: the ASC web UI holds
the state, but nothing in the web UI explains *why* a build was replaced or
what Apple was told. The journal is that missing memory, and it only works if
it is updated at the moment of change, not reconstructed later.

## Layout

```
docs/submissions/
  README.md                       ← index table (one row per version) + the discipline rules
  v<MAJOR.MINOR>/                 ← one directory per store version ("v1.0", "v1.1")
    submission.md                 ← submission snapshot: identity, copy-ready review
                                    material, submission-day checklist
    timeline.md                   ← append-only state history
    rejections/
      <date>-<slug>.md            ← one file per rejection
    submitted-notes-<date>.txt    ← frozen copy of the final review notes
```

Two sources of truth, deliberately separated: `metadata/` (or equivalent) is
the **live machine data** pushed to ASC — it changes with the current version.
`docs/submissions/` is the **historical ledger** — written once, sealed on
release. Never let the ledger restate live data by value; link instead
(duplicating a blocker list in two places guarantees one of them lies within a
week). A second separation keeps narratives honest: a project progress log
(what happened that day, append-only) is not the ledger (what state things are
in, materials, rejection handling) — conclusions change in place in the
ledger; the narrative log never gets rewritten. Do not copy one into the other.

The directory layout above suits apps with multiple versions and operators; a
small project may run a single-file form (index + app-info + one file per
version). Pick one and stay consistent — the discipline rules below apply to
both; don't migrate an existing working form for aesthetics.

## The three rules that keep the journal alive

1. **Every ASC state change appends one timeline row, immediately.** Submitted,
   Waiting for Review, In Review, rejected, approved, released, developer
   rejected — one row: date, event, evidence (command output id, commit, file
   path). The agent executing the change writes the row as part of finishing
   the change; humans only review. An append-only table with evidence beats a
   rewritten narrative: history stays honest because rows are never edited.
2. **Rejection → file first, fix second.** Before touching code or metadata,
   create `rejections/<date>-<slug>.md` with Apple's message verbatim (paste,
   do not paraphrase — the wording is the requirement), then the
   interpretation, then the fix plan. After the fix ships, append the commit
   and the draft reply to Apple in the same file. Fixing from a paraphrase
   fixes the wrong thing often enough that this order is not optional.
3. **Seal released versions; open a new directory for the next version.** A
   sealed directory is evidence; editing it later contaminates every conclusion
   drawn from it.

## Companion gates (link, don't duplicate)

- `metadata/review-readiness.json` (or equivalent machine file): the current
  blocker list and `readyForSubmission` — the boolean a pre-flight check reads.
  Update it when blockers resolve, with date + note, so the resolution history
  survives.
- Release map (e.g. `docs/release-map-<date>.md` §1/§4): the single authority
  for publish identity — repo, bundle id, signing team, ASC app id, review
  gates. The journal references it; it never restates it.
- `metadata/review_information/notes.txt`: the living review-notes document;
  the journal holds only its frozen submission-day snapshot.

## What the per-project archive should seal (so no session re-derives it)

- **Identity table**: app name / bundle / numeric ASC app id / versionId /
  buildId / pricing / availability / release mode (manual vs automatic). Name
  the two-ID trap explicitly in the table: the numeric app id (APIs) and the
  10-digit Apple ID (account views) are different numbers.
- **Signing chain**: distribution certificate, App Store profile,
  capabilities (PUSH/SIWA — a capability removed from the app id silently
  invalidates profiles → archive signing fails), and any
  Player License Agreement blocker (an unsigned PLA blocks signed archiving).
- **Problem-and-handling log**: one entry per incident with its conclusion and
  evidence (missing `UILaunchScreen` → upload error 90476; capability/PLA
  failures; demo-account data gaps). Seeded from the first rejection onward,
  it becomes the project's error map and the fastest read before any new
  release attempt.
- **Copy-ready material**: demo credentials, review-notes summary, privacy
  entry table — live in the version archive so "get it from here" has one
  answer.

## Commit style

One logical change per commit, conventional-commit prefixes matching the
project's history: `chore(release)` for version bumps and build uploads,
`docs(submissions)` for journal rows, `fix(metadata)` for ASC-content
corrections, `feat(metadata)` for new capture/upload automation. The timeline
row cites the commit — write the code change first, push, then the row naming
that hash (or one commit carrying both when the row *is* the change).
