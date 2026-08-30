# h5-style-unify

[中文](README.zh-CN.md)

A portable Agent Skill. It unifies style, color, and visual design for an **existing**
H5 / mobile-web project — converging scattered hard-coded colors into one token source of
truth, wrapping components around semantics, and enforcing it all with a machine gate —
without a big-bang rewrite.

The pipeline is not theory: it was **cross-validated on two production codebases** — a bare
Vue3 WeChat-embedded H5 app (star-training) and a SwiftUI iOS client sharing an H5 SoT
(EvairSIM) — including every pitfall they paid for (gate false-green, the rgba blind spot,
semantic dual-caliber colors, SoT drift).

## The five rings

```
1 SoT          theme.css — the ONLY file allowed to hold raw hex
2 Consumption  base.css global classes / component-lib var bridging; business uses var(--*)
3 Components   tone × variant semantic wrappers; business passes semantics, never colors
4 Gate         stylelint color-no-hex (error) + pre-commit + CI — fail-closed
5 Acceptance   dev-only design-system page rendering every token at runtime values
```

Governing principles (both case studies converge on them): a credible **gate before broad
component work**; **one rule that survives beats many rules**; **docs are projections,
never a second SoT**; **fail-closed, never fake-green**; and an **honest audit table**
that lists unpaid debt by file path.

## What's inside

- **Workflow** (SKILL.md): Phase 0 stack detection → Phase 1 audit → SoT → consumption →
  gate → acceptance page → honest audit table, with mutation-safety tiers for every phase
  (this skill edits real code).
- **`scripts/audit-styles.mjs`** — zero-dependency, fail-closed audit. Covers what
  stylelint cannot see: literal `rgba()/hsl()`, inline `style="…#fff…"`, JS-side color
  literals; auto-detects the SoT, the gate, and the stack. Tested against both case-study
  repos (where it re-found the recorded JS-side blind spots) and a synthetic violation
  project.
- **`references/`** — token taxonomy & two-layer naming; stack adapters (bare Vue/React,
  Vant, antd-mobile, Varlet, uniapp, cross-end SoT + codegen); gate configs verbatim
  (stylelint trap included); the cross-validated pitfall list + audit-table template; the
  two case studies side by side.
- **`assets/`** — drop-in templates: annotated `theme.css` (light + optional dark),
  `.stylelintrc.json` with the Chinese remediation message, and a Vue3 dev-only
  design-system acceptance page.

## When to use / not use

Use it when the ask is **统一风格 / 统一配色 / 样式统一 / design tokens / 门禁 / 换肤 /
多端视觉一致 / 风格一致性审计** on an existing H5 or mobile-web codebase. Don't use it to
invent a brand-new visual aesthetic from zero (that's `frontend-design`), and not for
admin-console ops-UX walkthroughs (that's `admin-console-ux`).

Provenance: sessions `sess_135a0e98` (star-training H5, transcript kept in that repo's
`docs/`) and `sess_e1b1e90b` (EvairSIM iOS), both 2026-08-30.
