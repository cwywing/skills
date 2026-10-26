# Screenshot capture pipeline — XCUITest → retouch → validate → upload

Read this file before capturing, retouching, or uploading screenshots (Phase 4
capture work; Phase 5 verification only needs `asc screenshots list`). Every
trap below cost a simulator or device round on a real project — check the list
before changing the test, not after failures.

## Capture via XCUITest (the only reliable simulator automation)

idb is often uninstalled and `simctl` cannot tap; XCUITest is the dependable
path. Write a dedicated screenshot test class (one test method per language,
file names prefixed per language) with these properties:

- **Real data**: no stub/`-uiTesting` launch arguments — stubs route the
  network layer to sample data and the shots then misrepresent the shipped app
  (Guideline 2.3: screenshots must faithfully reflect the submitted binary's
  real UI; staged data and DEBUG entries are risk). Point the app at production.
- **Page order = slot order**: walk the app's main path (browse → purchase →
  payment → account), wait for each page's defining element before shooting,
  and give `sleep(1)` for images/text to settle.
- **In-app language switch**: `launchEnvironment["AppleLanguages"]` no longer
  reaches apps with an internal LocaleManager on iOS 26 — switch in the app's
  language page, then `terminate()` + relaunch (large-title navigation only
  updates after relaunch).
- **Clear residue**: Keychain survives app uninstall — log out (confirm dialog
  included) before reaching the login gate so signed-out shots are reproducible.
- **System alerts**: pages that trigger clipboard checks pop the "Allow Paste"
  dialog; dismiss via SpringBoard, and match the button with CONTAINS ("Don't
  Allow **Paste**" / "不允许粘贴" — exact "Don't Allow" misses on iOS 26).
- **iPad**: tab structure differs (floating top bar); when
  `app.tabBars.buttons` misses, fall back to `app.buttons` by label. Prefix
  filenames by `UIDevice.current.userInterfaceIdiom`, or the iPad run
  overwrites the iPhone run. DEBUG-only entries (design-system previews) must
  be off-screen — scroll if not.

```
xcodebuild test -project <PROJECT>.xcodeproj -scheme <SCHEME> \
  -destination 'platform=iOS Simulator,name=<SIM>' \
  -only-testing:<XCUITests>/StoreScreenshotUITests/testCapture_<lang>
```

## Status-bar retouch

`simctl status_bar override` succeeds but has no effect on iOS 26+ simulators
(known system issue), so charging indicators and odd signal stay in the shot.
Post-process with `scripts/retouch_status_bar.swift`: locate the old battery by
green pixels, sample nearby background, erase tight to it, redraw a full
battery at original size; auto-adapts to iPhone (1320w) and iPad (2064w).
Before modifying the script, read its header notes (AppKit y-down vs
CoreGraphics y-up mixing paints at the image bottom; `NSImage lockFocus`
second-pass produces bit-shifted output — pure CG is reliable). Verify the
result by cropping a battery close-up for human review; do not crop with
`sips --cropOffset` (unreliable semantics).

## Sizes, slots, and the echo trap

**`asc screenshots sizes --all` output is the only truth for slot/type
mapping** — trust it over memory and over error messages.

| Web-UI slot | --device-type | Pixels |
|---|---|---|
| iPhone 6.9" (大显示屏) | `IPHONE_69` (API lands as `APP_IPHONE_67`) | 1290×2796 or 1320×2868* |
| iPhone 6.7" | `IPHONE_67` | 1290×2796 |
| iPad 13" | `IPAD_PRO_3GEN_129` | 2064×2752 |
| iPad 12.9" (legacy) | `IPAD_PRO_129` | 2048×2732 |

\* 1320×2868 is the 6.9" device native resolution; asc accepts and maps it.
The web UI's "6.9 英寸" slot is API type `APP_IPHONE_67`. Feeding
`APP_IPHONE_69` to the raw API returns invalid value **while listing it as
valid** — error lists include echoes of accepted names; when a value is
rejected despite being "valid", re-run `asc screenshots sizes`. iPad 2064×2752
belongs to 3GEN_129; uploading into legacy `IPAD_PRO_129` yields a
dimension-mismatch blocker. Smaller iPhone slots (6.3" 中等显示屏) stay empty —
they auto-scale from the 6.9" set; never upload there.

Pipeline: native 1320×2868 → (only if a 6.7" slot is wanted) resample
`sips --resampleWidth 1290` then center-crop → strip alpha (asc rejects
transparent PNGs; flatten or export JPEG) → `asc screenshots validate --path
DIR --device-type TYPE` locally → upload (`--replace` is the higher-risk tier,
SKILL.md table) → read back with `asc screenshots list`, count and order per
set.

Human acceptance per set: language correct, no DEBUG entry in frame, no alert
covering the shot, data real, status bar clean.
