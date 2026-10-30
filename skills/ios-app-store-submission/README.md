# ios-app-store-submission

[中文](README.zh-CN.md)

Headless iOS App Store submission skill: take an app from ready code to
submitted-for-review via `xcodebuild` + the `asc` (App Store Connect CLI), and
keep a per-version journal so multi-day, multi-operator work stays
reconstructable. Covers build/upload, TestFlight access, review materials,
readiness gates, and rejection handling.

Authoring follows [skill-authoring](../skill-authoring/) house style; the
content is distilled from real v1.0 submission runs across two apps
(2026-10) — every rule in `references/` names a failure that
actually happened.

## Canonical copy — downstream installs, never forks

**Published home: [cwywing/skills](https://github.com/cwywing/skills) →
`skills/ios-app-store-submission/`** — the single source of truth for this
skill across the org's iOS repos. Sync rule: if you find a defect or learn
something new while using an installed copy, land the change in the published
home (stage it in a working repo if mid-run, promote immediately after), then
re-install downstream — do not edit an installed copy in place, or the forks
drift apart. A project's differences belong in its fact sheet and journal (see
the checklist below), never in the skill body.

## Install

Copy the whole folder into a project skill directory (do not flatten — the
folder *is* the skill). If the project previously ran a fork of this skill,
remove the fork in the same change so only one copy triggers:

```bash
# from a repo that has this folder committed (canonical)
git archive HEAD .agents/skills/ios-app-store-submission | tar -x -C /path/to/project
# or plain cp -r; destination .agents/skills/ (or .cursor/skills/ / .claude/skills/)
```

Requires on the build machine: Xcode, an authenticated `asc` CLI
([Rork asc](https://github.com/rorkai/App-Store-Connect-CLI)), and the Apple
Distribution certificate in a known keychain.

## Project customization checklist (do this once per project)

- Fill the fact-sheet template's "source" column with *your* authoritative
  locations (release-map doc path, `project.yml` vs `Info.plist`, keychain
  path, readiness JSON path).
- Create the journal root the skill expects: `docs/submissions/` with the
  layout in `references/journal-discipline.md` (or point the skill at your
  existing journal location in Phase 0).
- Replace the demo/no-charge wording in `assets/templates.md` §notes-3 with
  your app's account-deletion and payment story.
- Raw-API fallback needs `python3` + the `cryptography` package (and
  `ASC_KEY_ID`/`ASC_ISSUER_ID`/`ASC_KEY_PATH` or a `~/.appstoreconnect/*.env`);
  the retouch script runs via `swift scripts/retouch_status_bar.swift`.
- Keep everything else: the phases, gates, and bright lines are project-neutral
  on purpose — they encode App Store mechanics, not one app's choices.

## Folder map

```
SKILL.md                              ← workflow, gates, bright lines
references/build-and-upload.md        ← archive → export → upload → attach + error map
references/review-readiness.md        ← validate/doctor, review details, privacy/age/pricing
references/screenshots-capture.md     ← XCUITest capture line, retouch, slot/size table
references/testflight-and-access.md   ← invite chain, internal groups, spam traps
references/raw-api-fallback.md        ← raw REST API traps when the CLI can't reach
references/journal-discipline.md      ← docs/submissions/ rules
scripts/asc_api.py                    ← signed raw-API executor (ES256 JWT)
scripts/retouch_status_bar.swift      ← screenshot status-bar retouch (iOS 26+)
assets/templates.md                   ← fact sheet, journal, notes, report skeletons
assets/export-options.plist           ← manual export template
```
