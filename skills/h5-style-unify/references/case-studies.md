# Case Studies — evidence base

Numbers and paths below were verified against the codebases (2026-08). This is the **only** file
in this skill that stores adoption counts. Do not duplicate them in README or SKILL.md.

## What was actually proven

| | H5 production case | iOS sibling (shared SoT) |
| --- | --- | --- |
| Role in this skill | The H5 pipeline (theme.css, stylelint, rgba/inline pitfalls, Vue consumption) | Proves the five-ring **order** and Mode D codegen; Swift details belong to `swiftui-style-unify` |
| Stack | bare Vue3 + vue-router + Vite, WeChat-embedded H5 | SwiftUI (iOS 17+), store app sharing the H5 SoT |
| SoT | `src/theme/theme.css` (hex, two-layer names) | shared web CSS (`:root` + `.dark`) |
| Gate | stylelint `color-no-hex` (error) + pre-commit lint-staged | ripgrep MUST-NOT + CI; CI re-syncs tokens |
| Acceptance | `views/_DesignSystem.vue`, `import.meta.env.DEV` | DEBUG Design tab |
| Adoption (measured) | 13/13 style-bearing files on `var(--*)`; zero raw hex outside SoT | recorded in the Swift skill — do not copy here |
| Recorded leftovers | rgba leak (later listed), warning dual-caliber, AppButton unmigrated, **no CI at the time of the H5 case**, admin-side outside the system | see sibling skill |

The H5 case did **not** ship CI. Treat CI in this skill as the durable layer the case *should* have
had, not as something that case already ran.

## Convergent decisions (transferable defaults)

1. One SoT file; everything else consumes or is generated.
2. Docs are indexes/projections; copying color tables into docs is banned.
3. Semantic two-layer naming (scale ↔ intent).
4. Components take semantic props and own color mapping; layout stays with the caller.
5. Machine gate with error-level failure and explicit remediation messages.
6. Acceptance page that renders runtime values and doubles as the component registry.
7. Progressive tightening — one rule first.
8. Honest audit tables with unpaid debt listed by file path.

## Divergences (pick deliberately)

- **Gate order.** The H5 case built SoT → components → gate sequentially; the iOS retro made
  gate-credibility P3 (before components). This skill's **workflow** adopts the iOS ordering.
- **SoT scope.** Single-end keeps a local SoT; multi-end points at the web SoT + codegen.
- **Gate tool.** CSS → stylelint; extra MUSTs / Swift → ripgrep script.
- **Token depth.** iOS adds full font objects + Motion + Metrics; a first-pass H5 consolidation
  can defer those until a second consumer exists.

When applying this skill, mirror the H5 column for Vue/CSS work; read `pitfalls-and-audit.md`
once before writing any file. For native implementation, switch to `swiftui-style-unify`.
