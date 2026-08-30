# Case Studies — two production proofs of the pipeline

These two projects are the skill's evidence base. Numbers and paths below were verified against the
codebases (2026-08-30); the pitfalls in `pitfalls-and-audit.md` carry their scars.

## Side-by-side

| Ring | star-training H5 | EvairSIM iOS |
| --- | --- | --- |
| Stack | bare Vue3 + vue-router + Vite, WeChat-embedded H5 | SwiftUI (iOS 17+, `@Observable`), eSIM store |
| SoT | `h5/src/theme/theme.css` (143 lines, hex, two-layer names) | shared `../h5/src/styles.css` (`:root` + `.dark`, OKLCH vars) |
| Sync | none needed (single end) | `scripts/sync-design-tokens.mjs` → 35 `.colorset` (Any+Dark), OKLCH→sRGB; intermediate JSON gitignored |
| Consumption | `h5/src/styles/base.css` global classes; business `var(--*)` | `DesignTokens.swift` typed entry (`typealias`s) + `EvairTheme` Environment injection (white-label ready) |
| Components | `AppStatusTag` (tone×variant), `AppButton` (variant×size, skeleton) | 12 `Evair*` components (Button/Card/Badge/Chip/EmptyState/Skeleton/Progress/Toggle/TextField/ListRow/SymbolStyle) |
| Gate | stylelint `color-no-hex` (error, CN message) + pre-commit lint-staged | `scripts/lint-design-system.sh` (ripgrep MUST-NOTs) + CI; CI re-syncs tokens and diffs — stale = red |
| Acceptance | `views/_DesignSystem.vue`, route only when `import.meta.env.DEV` | `DesignSystemPreviewView.swift`, DEBUG → Design tab; new components must register |
| Adoption (measured) | 13/13 style-bearing files on `var(--*)`; zero raw hex outside SoT | 182 `evairTextStyle`, 699 `DesignTokens.`, 156 `Evair*` uses in Features |
| Recorded leftovers | rgba leak (fixed list), warning dual-caliber, AppButton unmigrated, no CI, admin-side outside the system | audit doc `design-system-audit-2026-08-09.md`; Motion aligned to H5 curves in P2 |

## Convergent decisions (both projects, independently)

These are the transferable invariants — treat them as defaults, not options:

1. One SoT file; everything else consumes or is generated.
2. Docs are indexes/projections; copying color tables into docs is banned on both sides.
3. Semantic two-layer naming (scale ↔ intent).
4. Components take semantic props (`tone`, `variant`, `size`) and own ALL color mapping; layout and
   sizing stay with the caller (`class="badge"` shrinks to size/position only).
5. Machine gate with error-level failure and explicit remediation messages.
6. Acceptance page that renders runtime values and doubles as the component registry.
7. Progressive tightening — one rule first, "a rule that survives beats many rules".
8. Honest audit tables with unpaid debt listed by file path.

## Divergences (why they differ — pick deliberately)

- **Gate order.** H5 built SoT→components→gate sequentially; iOS retro ("gate on sand") made
  gate-credibility P0. The skill's operating principles adopt the iOS ordering.
- **SoT scope.** Single-end project keeps a local SoT (simpler); multi-end product points every
  platform at the web SoT + codegen (drift-proof, costs CI discipline). See `stack-adapters.md`.
- **Gate tool.** CSS platform → stylelint (rule ecosystem); non-CSS / extra MUSTs → ripgrep
  `assert_no_match` script. Both are fail-closed.
- **Token depth.** iOS adds full font objects (size/weight/lineHeight/tracking + Dynamic Type),
  Motion tokens, Metrics; a first-pass H5 consolidation can defer these — add when a second
  consumer exists.

## Source records

- star-training session transcript (full Q&A + review round, incl. the three review findings):
  `docs/sess_135a0e98-6416-4cd1-94b4-ac8f1e82c243-style-unification-transcript.md` in that repo.
- EvairSIM session `sess_e1b1e90b-8cb3-4875-b693-826cffd26a99` (WSL-side ZCode session library);
  repo docs: `docs/design-system.md`, `docs/design-tokens.md`, `docs/components-reference.md`,
  `.cursor/rules/design-system.mdc`.

When applying this skill to a new project, mirror the closest column, then read
`pitfalls-and-audit.md` once before writing any file.
