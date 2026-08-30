# swiftui-style-unify

[中文](README.zh-CN.md)

A portable Agent Skill. It unifies style, color, and design for an **existing** SwiftUI /
iOS app — converging inline colors, fonts, and magic numbers into one token namespace with
Dynamic Type-aware typography, wrapping components around semantic props, and locking it
all with a fail-fast ripgrep gate. It is the SwiftUI sibling of
[h5-style-unify](../h5-style-unify/); the two compose at a shared web SoT.

**Evidence base, stated honestly:** ONE production case (EvairSIM — token layer, theme,
12 components, lint, codegen, docs, mined from source), cross-validated against community
best practice and open-source SwiftUI design systems. Where the community agrees with the
case, the skill says so; where it differs (runtime-theme engines, Style Dictionary,
SwiftLint), the skill presents the decision instead of silently inheriting one.

## The five rings, Swift-shaped

```
1 SoT          Asset-Catalog colorsets — generated from the shared web SoT when one exists
2 Tokens       ColorTokens (only home of Color("...")) · full TextStyle objects with
               Dynamic Type policy · Spacing/Radius/Shadow/Metrics/Motion — one
               `DesignTokens` namespace entry
3 Components   tone enums → token pairs; ButtonStyle owns interaction states
4 Gate         ripgrep MUST-NOT lint (fail-fast on missing rg — never fake-green) in CI
5 Acceptance   DEBUG-only Design Tab; every component registered, every token family
               ships a catalog
```

## What's inside

- **Workflow** (SKILL.md): detect → audit → token layer → components → Features
  migration → gate → honest audit table; mutation-safety tiers throughout.
- **`scripts/audit-swift-styles.sh`** — the generalized production gate: raw `Color(`,
  `.font(.system(size:))`, numeric `padding/cornerRadius/spacing/frame`, raw `.shadow`,
  bare `ProgressView/Toggle/ContentUnavailableView`, `Color("...")` outside the tokens
  file, and the multiline Image-sizing anti-pattern. Auto-detects the Features dir and
  tokens file; `--report` prints adoption counts. Tested: green on the case repo
  (713 `DesignTokens.` / 182 `.evairTextStyle` uses), correctly fails on a synthetic
  violation file.
- **`references/`** — token-layer anatomy (incl. Dynamic Type policy and the catalog
  pattern); theme injection & component contract; cross-end sync & codegen (with the
  Style-Dictionary decision table); gate rule set, false-green lessons (including the
  rg glob-precedence cousin bug found while generalizing), audit template, external
  cross-validation notes.
- **`assets/`** — drop-in Swift templates: `DesignTokens.swift` namespace + token
  families, `EvairTextStyle.swift` full typography object, `Theme.swift` Environment
  container + MotionTokens with the ported web curve.

## When to use / not use

Use for 统一 SwiftUI/iOS 项目风格配色、design tokens、主题注入/white-label、Dark Mode、
iOS↔H5 多端一致、SwiftUI 样式门禁 on an existing codebase. Not for H5/web (use
`h5-style-unify`), not for inventing a new visual aesthetic (`frontend-design`).

Provenance: EvairSIM session `sess_e1b1e90b` (2026-08-30) + direct source mining of the
repo at `~/wwwroot/EvairSIM/ios-swiftui`.
