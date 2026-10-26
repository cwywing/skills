# Review readiness — validate, review details, screenshots, privacy

Read this file before Phase 4 (review materials) and Phase 5 (validate &
report). The theme: **the API's validate output is the only source of truth for
"can we submit"** — not the repo's historical claims, not last week's memory of
the checklist, not what the web UI appears to show.

## The two gates

```bash
asc validate --app <APP_ID> --version-id <VERSION_ID>
asc review doctor --app <APP_ID>
```

`validate` returns a machine-readable summary: `errors` are blocking, `warnings`
and `infos` are not (but infos can still block at submission time in practice —
App Privacy publish state is the known case the public API cannot see).
`review doctor` adds the review-detail configuration state and coverage
warnings (declarations only checkable on the web). Re-run both after every
mutation in this phase; a green from yesterday is not a green today.

Map API checks to human blockers honestly — the API consolidates. Several human
gaps (contact phone, demo credentials, screen-recording URL) all surface as the
single check `review_details.missing`, because they all live inside the review
detail resource. Reporting "1 blocking item" when the human list is 3 items is
under-reporting; decompose in the status report (see SKILL.md report format).

## Review details — the resource that gates submission

Created once per version; submission is impossible without it:

```bash
asc review details-create --version-id <VERSION_ID> \
  --contact-first-name "<F>" --contact-last-name "<L>" \
  --contact-email "<EMAIL>" --contact-phone "<+COUNTRY CODE NUMBER>"
```

The contact phone is the piece teams are never ready with — collect it from the
human early, not at submit time. The email can be a team shared mailbox
(service@…); the name and phone are personal data: ask the human, never invent,
never commit them outside the review notes and its frozen snapshot. Everything
else rides as review notes (`asc review details-update --notes ...` or the web
UI). A production-grade notes document has six sections (portable pattern —
keep the order, reviewers scan for them):

1. **Screen recording** — hosted URL of a device walkthrough.
2. **App purpose** — one paragraph, plain words.
3. **Access instructions / demo credentials** — a dedicated review account
   seeded with representative data, plus the account-deletion path (Apple
   requires apps with account creation to offer deletion; name the in-app path
   and, if any, the support-email fallback — it must match the published
   privacy policy).
4. **External services** — payments (if using Stripe/external checkout, cite
   Guideline 3.1.3(e) rather than hoping the reviewer infers it), analytics,
   device APIs (camera purpose), any outward browser links.
5. **Regional differences** — "same binary worldwide" if true.
6. **Regulated industry** — telecom, health, finance: name the license or
   authorization and where it is attached; never invent one in the notes.

Demo-account discipline: seed the account on production with data that lets a
reviewer reach every gated flow in ~5 minutes (orders across states including
one delivered and one refunded, in-use assets, one support conversation), then
verify it three ways (raw API, simulator, real device) before writing it into
the notes. Two spec traps: if registration requires email verification, the
reviewer cannot self-register — either lift it for review or hand the demo
credentials; and before submission, run a regression pass through the app with
this exact account on device and simulator, injecting credentials via a
test-runner seam rather than hardcoding. Credentials live in the review notes
and the version's submission snapshot — keep them out of logs, commit messages,
and agent memory.

## Screen recording

Apple's reviewers ask for a device recording when a flow needs hardware,
hardware-dependent state, or accounts/region the reviewer cannot reach. The
recording must visibly be the physical device (a screen capture of a mirroring
window reads as a Mac video and gets rejected by the team — the safest path is
Control-Center recording on the device, driven by a scripted UI test, then
AirDrop to the build machine). Host it on a stable HTTPS URL you control, then
backfill the URL into notes section 1. A recorded-but-unhosted video is not
done; track it as a blocker until the URL is in the notes.

## Screenshots

State lives per version-localization and per display type:

```bash
asc screenshots list --version-id <VERSION_ID> --locale <LOCALE>   # sets + per-shot COMPLETE state
```

- Required sets: one iPhone set (the largest display type the build supports —
  `APP_IPHONE_67` for 6.9"-class) and an iPad set whenever
  `TARGETED_DEVICE_FAMILY` includes 2. Missing iPad screenshots are a hard
  validation error; missing iPhone-small sets are not (smaller sizes scale from
  the large set). Slot/type mapping, sizes, and the capture pipeline live in
  `references/screenshots-capture.md` — read it before capturing or uploading.
- Order is content: capture and upload shop/browse → purchase → payment →
  account, and keep that order after any re-upload. Signed-out placeholder
  shots fail review for apps with login — retake signed in with the demo
  account once it exists.
- `--replace` deletes the set and re-creates it: tier it as a higher-risk
  write (SKILL.md table). Keep the source PNGs in-repo with a manifest whose
  `uploadRecord` line is updated whenever a upload mutation happens, so the
  next session can diff repo-truth against ASC-truth.

## Privacy, age rating, encryption, pricing, listing metadata

- **App Privacy**: the declaration can be approved via API but "published"
  state is web-only — the App Privacy nutrition label has no public API. Two
  routes: `asc web auth status` to check, then `asc web auth login --apple-id
  <EMAIL>` once (password + 2FA cached in the keychain, then `asc web privacy
  pull` / `plan --file privacy.json` / `apply` / `publish`), or hand the human
  a row-by-row entry table (category →
  data type → use → linked to identity, plus the explicit "not collected"
  list) to copy in the web UI. Either way the declared data must match the
  app's `PrivacyInfo.xcprivacy` (`NSPrivacyCollectedDataTypes`) — a mismatch is
  a privacy-evidence-mismatch rejection. The info-level validate check
  `privacy.publish_state.unverified` is exactly this gap.
- **Age rating**: submit the questionnaire once per app (`asc age-rating`, or
  the raw API path in raw-api-fallback.md — all required fields in one PATCH);
  ASC computes the badge (4+ for a shopping/utility app with messaging flagged).
- **Listing metadata**: content rights (`DOES_NOT_USE_THIRD_PARTY_CONTENT`
  unless licensed), categories (primary + secondary, ids are the uppercase
  enums), and `usesIdfa=false` wherever the app has no ads/trackers — a stale
  IDFA flag invites 4.8/rejection friction.
- **Export compliance**: handled at build level (see build-and-upload.md).
- **Pricing & availability**: free or paid schedule plus territory list;
  `asc validate` reports `pricingScheduleMissing` / `appAvailabilityMissing`
  when absent; `asc pricing current --app <APP_ID>` shows what is live right
  now. Set both before first submission; they are cheap and often forgotten.
  `--start-date` must be **today in US Pacific time** — a UTC-date
  in the late UTC night reads as "in the future" and errors. Schedule create
  is whole-timeline replacement: view first, merge intent, then write.

## Submission-day gates (all must hold)

1. `review-readiness` blockers list empty AND `asc validate` blocking count 0.
2. Notes document final; freeze a timestamped copy next to the version journal.
3. Human eyeballed the notes (the release gate is a person, not the CLI).
4. `whatsNew` filled — note the API rejects whatsNew while a first version sits
   in PREPARE_FOR_SUBMISSION, so enter it in the web UI at submission time.
5. Confirm the attached build is the intended one (newest VALID, correct
   version), release mode is what was agreed (manual vs automatic), then —
   only on the human's explicit go — submit.
