---
name: ios-app-store-submission
description: >-
  This skill should be used whenever an iOS app needs to move from ready code to
  submitted-for-review on App Store Connect, or anything on that path: building
  and uploading a new App Store build, attaching a build to a version, bumping
  the build number, TestFlight setup and tester access ("收不到 TestFlight
  邀请", "add him to the internal group"), review readiness checks (asc
  validate / review doctor), review notes and demo accounts (审核备注/演示账号),
  store screenshot verification, capture, or re-upload (商店截图产线/重拍),
  App Privacy / age rating / encryption compliance, pre-submission audits
  ("能不能提交审核了", "查一下截图挂在哪个槽位"), and rejection handling. It
  runs the whole flow headlessly via the asc CLI plus xcodebuild (raw App Store
  Connect API as fallback when the CLI can't reach), and keeps a per-version
  submission journal so multi-day, multi-operator work stays reconstructable. Use it even when the
  user asks for only one slice ("just re-upload the build", "看看截图还在不在")
  — every slice shares the same fact sheet, safety gates, and journal rules. Do
  not use it for Android/Play Store releases, local debug builds or simulator
  work, feature development, or writing store copy with no ASC access.
version: 0.2.2
---

# iOS App Store Submission

Drive an iOS app from "code is done" to "submitted for App Review" and through
rejections, entirely from the CLI, without losing state between sessions. The
work is mostly *state verification* — ASC's truth diverges from every human's
memory of it — so the skill's core discipline is: **query, then mutate, then
re-query, then write the journal row.** Optimism is the one unrecoverable
mistake here; a claim of "done" that the API does not back costs a review slot.

## When to use / when not to use

Use it for: "build and upload the new version, I'll submit"; "TestFlight invite
never arrived"; "is the app ready to submit?"; "verify the screenshots are
still attached"; "we got rejected, handle it"; "write/fill the review notes and
demo account".

Do **not** use it for: Play Store or Android work; running the app on a
simulator or device for development (that is iOS-dev tooling, not ASC state);
implementing features; producing marketing copy when no ASC session is
involved. If the user only wants a local build, no ASC mutation is warranted —
stop after archiving.

## Bright lines (non-negotiable — each names a real accident)

1. **Never submit for review without the human's explicit, current go.**
   Submission is irreversible from the API and starts a clock with Apple. Every
   earlier step is reversible; this one is not. "我直接提交" (the user will
   submit) means *they* submit — prepare everything, submit nothing.
2. **IDs and states come only from command output in this conversation.** An
   app id, version id, build id, or group id from memory of another session, a
   doc, or the web UI may be stale or another app's. Re-query when not in hand;
   if a query returns nothing, stop and report instead of improvising.
3. **`asc validate` is the only "ready" verdict.** Docs, READMEs, readiness
   JSONs, and previous sessions describe the past; blocking = 0 in *today's*
   validate output is the gate. Decompose consolidated API errors into the real
   human blockers when reporting (review_details.missing hides up to three
   separate human gaps).
4. **On a failed write, fix the named cause and retry once — never probe.**
   Every retry is a live write on production. If the error names no cause, ask.
   Two legitimate wait-then-retry cases exist (ASC eventual consistency, ~60s:
   re-invite right after revoke; build VALID polling after "Upload committed").
5. **Secrets stay in the review notes and the sealed snapshot; personal data
   is never invented.** Demo credentials and contact phone never go into
   commit messages, agent memory, logs, or the chat record's permanent
   artifacts — and when a form needs a human's name, phone, or password, ask;
   fabricating a plausible value is worse than an empty field.

Everything else below explains its why and tolerates judgment.

## Risk tiers — gate before acting

| Tier | Examples | Gate |
|---|---|---|
| Read-only | `validate`, `review doctor`, `builds list`, `screenshots list`, `users/invites/testers list` | Run freely; this is the "query" half of the core discipline |
| Lower-risk write | metadata/keyword push, timeline row, add accepted tester to group, re-invite after revoke, attach build | Confirm intent once in human terms, act, re-verify |
| Higher-risk write | `screenshots upload --replace` (deletes the set), revoke invitation / delete user, profile recreation, review-details create (locks in contact info) | Restate scope — names, counts, what expires or is deleted — and wait for confirmation |
| Irreversible | **Submit for Review**; release to store | Bright line 1: the human confirms, in the current conversation, after seeing the final validate report |

The pattern for every mutation: re-verify after acting (`screenshots list`
after upload, `testers list` after add). A mutation is not done when the
command exits 0; it is done when a read-back shows the intended state.

## Phases

Run the phases the task needs (see Entry points). Each write-phase gate is a
precondition, not a suggestion: skipping the reference causes exactly the
mistake it documents.

**Phase 0 — Fact sheet.** Fill `assets/templates.md` → Project fact sheet from
live sources (`asc apps list`, `asc versions list`, project file, release-map
doc) — never from memory. Every later command consumes it. A wrong app id here
poisons everything downstream, which is why it cites its source per row.

**Phase 1 — Preflight.** `git pull` / confirm baseline; `asc status --app
<APP_ID>` for the one-screen overview (state / attached build / TestFlight /
next step), then `asc validate` and `asc review doctor` for the baseline
truth; read the journal index (`docs/submissions/README.md` or the project's
equivalent) and the readiness JSON. This produces the before-picture every
later claim is measured against.

**Phase 2 — Build & upload.** **Read `references/build-and-upload.md` first.**
Bump build number → archive Release → verify versions in the archive → export
(manual signing) → upload → poll to VALID → attach to version. Commit the bump
(`chore(release)`).

**Phase 3 — TestFlight & access.** **Read `references/testflight-and-access.md`
first.** Diagnose the invite chain hop by hop; add accepted members to the
internal group; end by telling the human which email to look for in which
inbox, including the spam-folder instruction.

**Phase 4 — Review materials.** **Read `references/review-readiness.md` first.**
Review details (contact + notes with demo account), screen recording (hosted
URL or it is not done), screenshots (verify from API; `--replace` is
higher-risk), privacy/age/encryption/pricing. Gate additions: capturing or
re-uploading screenshots requires `references/screenshots-capture.md`; any
operation the asc CLI cannot reach (or whose error misleads) requires
`references/raw-api-fallback.md`.

**Phase 5 — Validate & report.** Re-run both gates; emit the status report
(`assets/templates.md`): lead sentence, state table, mutations this run,
remaining blocking decomposed to human blockers, next steps with owners and
any expiry dates. This report is the deliverable for single-slice tasks.

**Phase 6 — Submit day.** All gates hold (readiness blockers empty, validate
blocking 0, notes frozen to a timestamped copy, human eyeballed the notes,
whatsNew filled via web). Then, and only then, ask for the explicit go and
submit on confirmation. After any ASC state change anywhere in the pipeline:
append the journal row (read `references/journal-discipline.md` before the
first journal write of a session).

## Entry points — calibrate depth to the ask

- "重新 build 上传，然后我提交" → Phases 0, 1, 2, 5 (+6 prep, no submit).
- "TestFlight 收不到邀请 / 加进内测组" → Phases 0, 3, 5.
- "查一下截图/validate/能不能提交" → Phases 0, 1 (+4 read-only), 5.
- "重拍/上传商店截图" → Phases 0, 4 (capture gate), 5.
- "被拒了" → journal rejection file first (reasons are API-invisible: verbatim
  text comes from Resolution Center / Apple's email; no fix before it lands),
  then fix, then Phases 1, 2, 5.
- "提交后查审核状态" → Phases 0, 1, 5; a REJECTED state with clean validate
  means review-content rejection, not metadata.
- Full prep from scratch → all phases.

## Worked example

Input: "重新build 然后上传最新的版本 我直接提交审核。另外 wing@example.com 没收到
TestFlight 邀请。"

Output (shape): fact sheet filled from live queries; build N+1 archived,
exported, uploaded, polled to VALID, attached; validate re-run showing the one
blocking item reported as its three human causes (contact phone owed by X,
video URL unhosted pending Y, privacy publish unverifiable via API); TestFlight
diagnosis = team invite pending/unaccepted (the real cause — no TestFlight
invite can exist yet), old invite revoked, fresh invite sent with new expiry;
timeline rows appended for the build and the invite; final report states
plainly: submission remains in the user's hands, and "tell me when he accepts
and I will add him to the group" — because pre-acceptance group-add fails.

## Contrast pairs

Correct: "这会删除 6.9" 现有 4 张截图并重新上传同序的 4 张 — 继续？"
Incorrect: "Running screenshots upload --replace on APP_IPHONE_67."
Rationale: scope confirmation uses the names and counts a human recognizes;
command syntax is backstage and confirms nothing.

Correct: build VALID 8 minutes after upload on the second poll.
Incorrect: "上传成功了" after "Upload committed" with no VALID poll.
Rationale: committed ≠ processed; only a read-back of VALID supports "done".

Correct: invitee absent from `users list`, present in `invites list` with
expiry tomorrow → diagnose step 2 of the chain, re-invite, tell them to check
spam.
Incorrect: "重新加一下 TestFlight 就好了" — adding to the group someone who has
not accepted the team invite.
Rationale: the chain has a strict order; acting on the wrong hop fails or
silently does nothing.

## Pre-action self-check (run before any write)

- Is every ID in the command from this conversation's query results?
- Which risk tier is this? Higher-risk → scope restated and confirmed?
- Am I on the fetch-then-verify path (read state → mutate → read back)?
- If this failed before: do I know the *named* cause, and am I changing only
  that?
- After this succeeds, which journal row and which re-verify does it owe?

## References (read when the phase gate says so)

- `references/build-and-upload.md` — archive/export/upload pipeline, signing
  keychain, profile management, error map. Phase 2.
- `references/review-readiness.md` — validate/doctor interpretation, review
  details and notes, screen recording, screenshots readiness, privacy/age/
  encryption/pricing/listing metadata. Phases 4–6.
- `references/screenshots-capture.md` — XCUITest capture line, status-bar
  retouch, slot/size table, alpha/validate/upload loop. Phase 4 capture.
- `references/testflight-and-access.md` — invite chain, internal groups, spam
  traps, failure table. Phase 3.
- `references/raw-api-fallback.md` — raw REST API via `scripts/asc_api.py`:
  endpoint traps (localizations, age rating, build attach, direct upload).
  When the CLI can't reach.
- `references/journal-discipline.md` — docs/submissions/ layout, the rules,
  archive-worthy entries, commit style. Before any journal write.
- `scripts/asc_api.py` — zero-config signed API executor (the raw fallback).
- `scripts/retouch_status_bar.swift` — screenshot battery/signal retouch.
- `assets/templates.md` — fact sheet, timeline row, submission/rejection/
  notes/report skeletons.
- `assets/export-options.plist` — manual export options template.
