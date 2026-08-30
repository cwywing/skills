---
name: swiftui-style-unify
description: Unify style, color, and design for an EXISTING SwiftUI / iOS app project. Use when the user wants to 统一 iOS/SwiftUI 项目的风格配色、建立 SwiftUI design tokens（DesignTokens / ColorTokens / Typography）、做主题注入或 white-label 换肤、Dark Mode、保持 iOS 与 H5/网页多端视觉一致、给 SwiftUI 代码加样式门禁或审计. Encodes the five-ring pipeline (SoT → semantic tokens → component wrapping → machine gate → acceptance page) in production Swift shapes — a `DesignTokens` namespace, full text-style objects with Dynamic Type policy, Environment theme injection, Asset-Catalog colorset codegen from a shared web SoT, and a ripgrep MUST-NOT gate that fails fast instead of faking green. Single production case (EvairSIM, mined from source) cross-validated against community best practice and open-source SwiftUI design systems. NOT for H5/web projects (that is h5-style-unify) or inventing a new visual aesthetic from scratch (that is frontend-design).
metadata:
  version: "0.1.0"
---

# SwiftUI Style Unification

Bring an existing SwiftUI app from "colors and fonts inline in every view" to "one token
namespace, semantic components, and a machine gate" — the same five-ring pipeline as
`h5-style-unify`, in the shapes Swift actually wants. Evidence base (state it honestly when
reporting): ONE production case, EvairSIM, mined from source (tokens, theme, lint, codegen,
docs); every pattern cross-checked against community best practice and open-source SwiftUI
design systems — see `references/gate-and-pitfalls.md` for where they agree and differ.

## Scope

**In scope:** existing SwiftUI codebases — token layer, theme injection, semantic component
wrapping, a ripgrep gate, a DEBUG acceptance view, and (when a web sibling exists) shared-SoT
colorset codegen. **Out of scope:** H5/web unification (use `h5-style-unify`; the two skills
compose at the shared SoT), new visual direction from zero (`frontend-design`), UIKit
(Asset-Catalog ideas port, the Swift API surface does not).

## The five rings, Swift-shaped

```
1 SoT          colors: Asset Catalog colorsets generated from the shared web SoT
               (single-app project: hand-maintained colorsets are the SoT)
2 Tokens       ColorTokens (only place Color("...") lives) · EvairTextStyle (full font
               object + Dynamic Type policy) · Spacing/Radius/Shadow/Metrics/Motion,
               all behind one `DesignTokens` namespace
3 Components   Evair*-style wrappers (tone enums → token pairs; ButtonStyle for states)
4 Gate         ripgrep MUST-NOT lint, error-level, fail-fast on missing rg — CI runs it
5 Acceptance   DEBUG-only DesignSystemPreviewView; every new component registered there
```

The same three ordering principles as `h5-style-unify` apply, and the iOS case is the one
that paid for them: **a credible gate before broad component work** (the retro line is
"every component merged while the gate was untrusted was built on sand"), **one rule that
survives beats many rules**, **docs are projections** — the token doc indexes and maps, it
never copies values.

## Workflow

### Phase 0 — Detect the project shape (read-only)

Establish: app source root (`<App>/`), the Features directory (layer the gate polices), any
existing Theme/ dir, whether a sibling web project exists (shared-SoT mode), and whether
`rg` (ripgrep) is installed — the gate depends on it and must fail, not fake-green, without
it. Confirm the repo root and Features dir with the user before anything writes.

### Phase 1 — Audit the baseline (read-only)

Run `./scripts/audit-swift-styles.sh <repo-root>`. It reports MUST-NOT violations (raw
`Color(`, `.font(.system(size:))`, numeric `padding/cornerRadius/spacing/frame`, raw
`.shadow`, bare `ProgressView/Toggle/ContentUnavailableView`, `Color("...")` outside the
tokens file) plus structural facts (tokens namespace present?). Record baseline counts —
the before/after delta is the deliverable's proof.

### Phase 2 — Build the token layer

Start from `assets/DesignTokens.swift.tmpl` + `assets/EvairTextStyle.swift.tmpl` +
`assets/Theme.swift.tmpl`. Full anatomy in `references/swift-tokens.md`. Non-negotiables:

- ONE namespace entry (`enum DesignTokens { typealias … }`) — Feature code references
  `DesignTokens.Colors.*`, never a `*Tokens` type directly.
- `Color("...")` appears in exactly one file (ColorTokens). Feature views never see asset
  names.
- Text styles are complete objects — size, weight, design, lineHeight, tracking, AND a
  Dynamic Type policy (`.fixed` for display sizes only; `.relative(textStyle)` for
  everything users read). Applying is one modifier: `.evairTextStyle(_:)`.
- Motion: if a web SoT exists, port its curve verbatim
  (`Animation.timingCurve(0.22, 1, 0.36, 1, duration:)`), with documented exceptions
  (shimmer stays linear — it is not a UI transition).
- Every token family ships a `catalog` (array of itself) so the acceptance view renders
  from one source and drift is visible.

### Phase 3 — Components (semantic props, zero raw values)

Wrap high-frequency visuals as `Evair*`-style components: tone enums map to token PAIRS
(foreground + background) — see EvairBadge in `references/theme-and-components.md`. Buttons
via `ButtonStyle` so pressed/disabled/loading states live in one place. Components own
color/typography; layout and sizing stay with the caller. Each new component must register
in the acceptance view the same PR it lands in — unregistered = invisible to review.

### Phase 4 — Migrate Features (per-batch, Tier-2)

Replace raw values with tokens file-by-file; screenshots before/after per screen. Pure
mechanical swap and visible change (semantic recolor) are separate commits. Features that
genuinely need a new token: register the token FIRST (Phase 2 flow), then consume.

### Phase 5 — The gate

Install `scripts/audit-swift-styles.sh` into the repo (it is the generalized production
lint), wire it into CI as a required check, and add the colorset-diff check when a shared
SoT exists (CI re-runs the sync; a diff fails the build — hand-edits to generated
colorsets are caught, not trusted). Gate self-test: inject `Color(red: 1, green: 0, blue:
0)` into a Features file, OBSERVE the lint fail, remove, observe pass. A gate never seen
failing is unverified.

### Phase 6 — Record honestly

Audit table (rings × status) + leftovers by file path, mirroring
`references/gate-and-pitfalls.md`. Report before/after violation counts and component
adoption counts (`DesignTokens.` uses, component uses in Features).

## Cross-end composition (with h5-style-unify)

When the product has both an H5 app and an iOS app, the web `styles.css` is the single
color SoT and iOS consumes generated colorsets — `h5-style-unify` Mode D owns the web side
and the sync contract; this skill owns the Swift side (MAP registration, ColorTokens,
CI diff). Adding a color is a four-step procedure that touches both — see
`references/sync-codegen.md`, which also covers the Style-Dictionary alternative (token
JSON as SoT) and when it is the better choice.

## Mutation safety

Same tiering as `h5-style-unify` (see `../skill-authoring/references/mutation-safety.md`):

- **Read-only:** Phases 0–1.
- **Tier 1 — additive files:** token layer, theme, components, lint script, preview view.
  List the files before creating.
- **Tier 2 — editing Features views:** per-batch, sample diff first, never mix mechanical
  token swaps with visible changes.
- **Tier 3 — CI / shared scripts:** explicit confirmation; CI must be fail-closed (a step
  that would be skipped on failure goes red instead).
- **No weakening to pass:** if the gate self-test fails or the audit errors, report the
  output — do not delete rules, exclude files, or rerun until green. That failure mode is
  exactly what the fail-fast rg check exists to prevent.

## Correct / Incorrect (the consumption contract)

**Incorrect** — Feature view owning visual decisions:

```swift
// Features/OrderView.swift
Text(status)
    .font(.system(size: 13, weight: .medium))   // no Dynamic Type, drifts from every other caption
    .foregroundColor(Color(red: 0.95, green: 0.3, blue: 0.2))  // raw color, second SoT
RoundedRectangle(cornerRadius: 12).padding(14)  // magic numbers
```

**Correct** — Feature speaks semantics; the token layer owns values:

```swift
// App/Theme/Tokens/ColorTokens.swift (the ONLY Color("...") in the app)
static let warning = Color("AppWarning")

// Features/OrderView.swift
Text(status)
    .evairTextStyle(DesignTokens.Typography.labelMedium)  // Dynamic Type-aware, one source
    .foregroundStyle(DesignTokens.Colors.warning)
    .padding(DesignTokens.Spacing.md)
```

One-line rationale: identical pixels today, but the values have one owner, the text scales
with user settings, and re-theming never touches Feature files.

## Reference files (read on demand)

- `references/swift-tokens.md` — the token layer's Swift anatomy, Dynamic Type policy,
  catalog pattern, naming rules.
- `references/theme-and-components.md` — Environment theme injection, white-label swap,
  tone-enum components, ButtonStyle state handling.
- `references/sync-codegen.md` — shared web SoT → colorset codegen (MAP, OKLCH→sRGB, CI
  diff) and the Style-Dictionary alternative; when each wins.
- `references/gate-and-pitfalls.md` — the full MUST-NOT rule set, false-green lessons,
  acceptance-view contract, audit-table template, external cross-validation notes.

## Self-check before done

- [ ] Audit script exits 0 on the repo; before/after counts reported.
- [ ] Gate self-test observed failing on an injected raw `Color`, then passing.
- [ ] `Color("...")` exists in exactly one file; `DesignTokens` is the only namespace
      Features import for visuals.
- [ ] Acceptance view DEBUG-reachable, every wrapped component registered.
- [ ] Audit table + honest leftovers written; evidence base stated as one-case +
      external validation (do not claim two production cases).
