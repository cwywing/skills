# swiftui-style-unify

[中文](README.zh-CN.md)

A portable Agent Skill. It unifies style, color, and design for an **existing** SwiftUI /
iOS app — converging inline colors, fonts, and magic numbers into one token namespace with
Dynamic Type-aware typography, wrapping components around semantic props, and locking it
with a fail-closed ripgrep gate. It is the SwiftUI sibling of
[h5-style-unify](../h5-style-unify/); the two compose at a shared web SoT.

**Evidence, stated honestly:** one production SwiftUI case (token layer, theme, components,
lint, codegen, docs), cross-checked against community SwiftUI design-system practice.
Where the community agrees, the skill says so; where it differs (runtime-theme engines,
Style Dictionary, SwiftLint), it presents the decision. Adoption counts live only in
`references/gate-and-pitfalls.md`.

Portable names: `DesignTokens`, `TextStyle` / `.textStyle(_:)`, `AppTheme`, `AppBadge` —
no client brand prefix.

## Install order (not ring-number order)

```
P0 detect → P1 audit (full counts) → P2 tokens → P3 gate (self-test)
         → P4 migrate views → P5 App* components + DEBUG preview → P6 record
```

## What's inside

- **Workflow** (SKILL.md): P0–P6; mutation-safety tiers; views dir is confirmed, not
  assumed to be named `Features/`.
- **`scripts/audit-swift-styles.sh`** — macOS-safe (no GNU `xargs -r`). Reports **every**
  rule, then exits. Missing `rg` fails. `.font(.system(size:))` banned;
  `.font(.system(.body))` allowed. Component wrappers are warnings until `--components`.
  `tests/` locks these cases.
- **`scripts/sync-design-tokens.mjs`** — web CSS SoT → Asset Catalog colorsets (hex / OKLCH
  / rgb). MAP template in `assets/color-map.json.tmpl`.
- **`references/`** — token anatomy, theme/component contract, sync + Style Dictionary
  decision table, gate rules + P0–P6 audit table.
- **`assets/`** — `DesignTokens.swift`, `TextStyle.swift`, `Theme.swift`,
  `DesignSystemPreviewView.swift`.

## When to use / not use

Use for 统一 SwiftUI/iOS 项目风格配色、design tokens、主题注入/white-label、Dark Mode、
iOS↔H5 多端一致、SwiftUI 样式门禁 on an existing codebase. Not for H5/web (use
`h5-style-unify`), not for inventing a new visual aesthetic (`frontend-design`).
