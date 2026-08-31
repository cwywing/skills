---
name: swiftui-style-unify
description: Unify style, color, and design for an EXISTING SwiftUI / iOS app project. Use when the user wants to 统一 iOS/SwiftUI 项目的风格配色、建立 SwiftUI design tokens（DesignTokens / ColorTokens / Typography）、做主题注入或 white-label 换肤、Dark Mode、保持 iOS 与 H5/网页多端视觉一致、给 SwiftUI 代码加样式门禁或审计. Encodes the five-ring pipeline in Swift shapes — a `DesignTokens` namespace, full text-style objects with Dynamic Type, Environment theme injection, optional Asset-Catalog codegen from a shared web SoT, and a ripgrep MUST-NOT gate that is fail-closed (missing rg fails; every rule is reported before exit). One production SwiftUI case, cross-checked against community design-system practice. NOT for H5/web projects (that is h5-style-unify) or inventing a new visual aesthetic from scratch (that is frontend-design).
metadata:
  version: "0.2.1"
---

# SwiftUI Style Unification

Bring an existing SwiftUI app from "colors and fonts inline in every view" to "one token namespace, semantic components, and a machine gate" — the same five-ring pipeline as `h5-style-unify`, in the shapes Swift actually wants.

Evidence (state it this way when reporting): **one production SwiftUI case**, mined from source (token layer, theme, components, lint, codegen, docs), cross-checked against community SwiftUI design-system practice. See `references/gate-and-pitfalls.md` for where they agree and differ. Do not claim two production iOS rollouts.

Portable names in this skill: `DesignTokens`, `TextStyle` / `.textStyle(_:)`, `AppTheme`, `AppBadge` / `AppButton` / … — never a client brand prefix.

## Scope

**In scope:** existing SwiftUI codebases — token layer, theme injection, semantic component wrapping, a ripgrep gate, a DEBUG acceptance view, and (when a web sibling exists) shared-SoT colorset codegen.

**Out of scope:** H5/web unification (use `h5-style-unify`; the two compose at the shared SoT), new visual direction from zero (`frontend-design`), UIKit (Asset-Catalog ideas port; the Swift API surface does not).

## Architecture vs install order

When the job is done:

```
1 SoT          Asset-Catalog colorsets (generated from a web SoT when one exists;
               otherwise hand-maintained colorsets)
2 Tokens       ColorTokens (only home of Color("...")) · TextStyle + Dynamic Type
               · Spacing/Radius/Shadow/Metrics/Motion — one DesignTokens entry
3 Components   App*-style wrappers (tone enums → token pairs; ButtonStyle for states)
4 Gate         ripgrep MUST-NOT lint — missing rg fails; all rules reported, then exit
5 Acceptance   DEBUG-only DesignSystemPreviewView; every component registered there
```

**Install in the Phase order below.** A credible gate (P3, self-test observed failing) comes before broad component work (P5). The production retro: every component merged while the gate was untrusted was built on sand.

Also: **one rule that survives beats many rules**; **docs are projections** (index and map, never copy values).

## Effort calibration

| Ask | Do |
| --- | --- |
| One screen / one leaked `Color(red:)` | Confirm token layer exists; fix that file; run the audit. Install the gate only if none exists. |
| 「统一风格」 / whole app | Full P0–P6. Confirm the **views directory** (not every repo has `Features/`). |
| iOS + H5 must match | `h5-style-unify` Mode D owns the web SoT; this skill owns MAP + ColorTokens + `scripts/sync-design-tokens.mjs` + CI diff. |

## Workflow

Phase numbers below **are** the audit-table rows.

### P0 — Detect the project shape (read-only)

Establish: app source root, the **views directory** the gate will police (a folder named `Features` if present, otherwise `App`, otherwise repo root with `Theme/` excluded — confirm with the user), any existing Theme/, whether a sibling web project exists, and whether `rg` is installed. The gate must fail, not fake-green, without ripgrep. Confirm repo root and views dir before anything writes.

### P1 — Audit the baseline (read-only)

Run this skill's `scripts/audit-swift-styles.sh <repo-root>`. It prints **every** failing rule and a total count (it does not stop at the first hit). Default `--style-mod textStyle`. Component-wrapper rules (`ProgressView` / `Toggle` / `ContentUnavailableView`) are **warnings** until `--components` after wrappers exist. Record the error/warning counts.

`.font(.system(.body))` (Apple Dynamic Type, no explicit size) is allowed. `.font(.system(size:))` is not.

### P2 — Build the token layer

Start from `assets/DesignTokens.swift.tmpl` + `assets/TextStyle.swift.tmpl` + `assets/Theme.swift.tmpl`. Anatomy in `references/swift-tokens.md`. Non-negotiables:

- ONE namespace entry (`enum DesignTokens { typealias … }`). Views reference `DesignTokens.Colors.*`, never a `*Tokens` type directly.
- `Color("...")` appears in exactly one file (ColorTokens).
- Text styles are complete objects (size, weight, design, lineHeight, tracking, Dynamic Type policy). Apply with `.textStyle(_:)`. `relative` is the default; `fixed` is an explicit display/hero exception.
- Motion: if a web SoT exists, port its curve verbatim; document exceptions (shimmer stays linear).
- Every token family ships a `catalog` for the acceptance view.

### P3 — Gate (before components)

Copy `scripts/audit-swift-styles.sh` into the repo. Wire a required CI step that runs it. Self-test: inject `Color(red: 1, green: 0, blue: 0)` into a views file, OBSERVE non-zero exit and a printed hit, remove, observe pass.

If historical literals would drown CI: run the script in CI as `continue-on-error` only while recording a shrinking count is **not** allowed — instead, keep it required but scoped to new files via review, or migrate hot paths first. Prefer: gate is required, P4 drives the count to zero. Do not start P5 wrappers until the self-test has been observed.

When a shared SoT exists, also add the colorset-diff check (CI re-runs `sync-design-tokens.mjs`; a diff fails the build).

### P4 — Migrate views (per-batch, Tier-2)

Replace raw values with tokens file-by-file. Mechanical swap and visible recolor are separate commits. New tokens: register first (P2), then consume.

### P5 — Components + acceptance view

Wrap high-frequency visuals as `App*` components: tone enums map to token **pairs** (see AppBadge in `references/theme-and-components.md`). Buttons via `ButtonStyle`. Layout stays with the caller. Drop in `assets/DesignSystemPreviewView.swift.tmpl`, `#if DEBUG` only. Re-run the audit with `--components` once wrappers exist so ProgressView/Toggle/empty-state become errors.

### P6 — Record honestly

Audit table (P0–P6) + leftovers by file path. Report before/after counts and `--report` adoption numbers (`DesignTokens.` uses, `.textStyle(` uses).

## Cross-end composition (with h5-style-unify)

Web CSS is the color SoT; iOS consumes generated colorsets. Adding a color: add the CSS var → register in `assets/color-map.json.tmpl` (the MAP) → add the semantic name in ColorTokens → run `scripts/sync-design-tokens.mjs` → eyeball the DEBUG tab. Procedure in `references/sync-codegen.md` (includes when Style Dictionary is the better SoT).

## Mutation safety

- **Read-only:** P0–P1.
- **Tier 1 — additive files:** token layer, theme, components, lint script, preview view. List files before creating.
- **Tier 2 — editing views:** per-batch, sample diff first; never mix mechanical swaps with visible changes.
- **Tier 3 — CI / shared scripts:** explicit confirmation; a step that would be skipped on failure goes red instead.
- **No weakening to pass:** if the self-test or audit errors, report the output. Do not delete rules, exclude files, or rerun until green.

## Correct / Incorrect (the consumption contract)

**Incorrect** — view owning visual decisions:

```swift
Text(status)
    .font(.system(size: 13, weight: .medium))
    .foregroundColor(Color(red: 0.95, green: 0.3, blue: 0.2))
RoundedRectangle(cornerRadius: 12).padding(14)
```

**Correct** — view speaks semantics; the token layer owns values:

```swift
// ColorTokens.swift (the ONLY Color("...") in the app)
static let warning = Color("AppWarning")

Text(status)
    .textStyle(DesignTokens.Typography.labelMedium)
    .foregroundStyle(DesignTokens.Colors.warning)
    .padding(DesignTokens.Spacing.md)
```

Rationale: identical pixels today, one owner, Dynamic Type by default, re-theming never touches feature files.

## Reference files (read on demand)

- `references/swift-tokens.md` — token-layer anatomy, Dynamic Type, catalog, naming.
- `references/theme-and-components.md` — Environment injection, tone-enum components, ButtonStyle.
- `references/sync-codegen.md` — web SoT → colorset codegen + Style Dictionary decision table.
- `references/gate-and-pitfalls.md` — MUST-NOT rules, false-green lessons, audit-table template, community notes. Adoption numbers live only here.

## Self-check before done

- [ ] Audit script before/after counts reported (full rule list, not first-hit).
- [ ] Gate self-test observed failing on an injected raw `Color`, then passing.
- [ ] `Color("...")` exists in exactly one file; views use `DesignTokens` only.
- [ ] Acceptance view DEBUG-reachable; every wrapped component registered.
- [ ] Evidence stated as one production case + external validation.
- [ ] No client brand prefix (`Evair*` or similar) in types, modifiers, or file names.
