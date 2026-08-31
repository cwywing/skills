# h5-style-unify

[中文](README.zh-CN.md)

A portable Agent Skill. It unifies style, color, and visual design for an **existing**
H5 / mobile-web project — converging scattered hard-coded colors into one token source of
truth, wrapping components around semantics, and enforcing it with a machine gate —
without a big-bang rewrite.

**Evidence, stated honestly:** one production H5 codebase (bare Vue3 WeChat-embedded app)
proved theme.css + stylelint + the rgba/inline-style/customSyntax pitfalls. A sibling
SwiftUI app sharing that H5 SoT proved the five-ring **order** and codegen; Swift details
live in [swiftui-style-unify](../swiftui-style-unify/). Do not read this as two independent
H5 rollouts. The H5 case did not ship CI — CI in the workflow is the layer it should have had.

## Install order (not ring-number order)

```
P0 detect → P1 audit → P2 SoT → P3 gate (self-test) → P4 migrate → P5 components + acceptance → P6 record + CI
```

A credible gate comes **before** broad component work. One rule that survives beats many
rules. Docs are projections, never a second SoT.

## What's inside

- **Workflow** (SKILL.md): P0–P6 with mutation-safety tiers.
- **`scripts/audit-styles.mjs`** — zero-dependency, fail-closed. Covers stylelint blind
  spots: literal `rgba()/hsl()`, inline `style=`, Tailwind `bg-[#…]`, Vue SFC `<script>`
  color literals, uniapp `.wxss`/`.nvue`/`.uvue`. SoT detection includes Vue/uni global
  `<style>`. `tests/` locks these cases.
- **`references/`** — taxonomy, stack adapters (A–D), gate configs (`<app-root>`, not
  `h5/`), pitfalls + P0–P6 audit table, case-study evidence.
- **`assets/`** — `theme.css` (light + optional dark, including `*-rgb` in dark),
  `.stylelintrc.json`, Vue3 dev-only acceptance page (token names only).

## When to use / not use

Use when the ask is **统一风格 / 统一配色 / 样式统一 / design tokens / 门禁 / 换肤 /
多端视觉一致 / 风格一致性审计** on an existing H5 or mobile-web codebase. Don't use it to
invent a brand-new visual aesthetic (`frontend-design`), and not for admin-console ops-UX
walkthroughs (`admin-console-ux`).
