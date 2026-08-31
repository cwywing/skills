# Token Taxonomy — the SoT's internal structure

Provenance: the production H5 case `src/theme/theme.css` (hex, two-layer names), cross-checked
against the sibling SwiftUI token layer. Start from `assets/theme.css.tmpl`.

## Two-layer naming (the core discipline)

Every dimension has a **scale layer** (abstract steps) and a **semantic layer** (usage intent).
Semantic tokens reference scale tokens; business code uses the semantic layer; the SoT itself and
generic UI components may use the scale layer.

```
--radius-md: 12px;            /* scale */
--radius-card: var(--radius-md);   /* semantic — the only one business pages touch */
```

Why: re-theming becomes a scale-layer edit in one file; business pages never churn. When a new usage
appears, first look for an existing semantic token; only add a new one when the intent is genuinely
new — otherwise you rebuild the "hex museum" the consolidation just removed.

## Dimension checklist

| Dimension | Scale layer | Semantic layer (examples) |
| --- | --- | --- |
| Brand color | `--color-primary/-dark/-soft/-softer` | — |
| Status colors | success / warning / danger **four-piece set**: main + `-text` + `-soft` + `-border` | danger may add `-vivid` (borders/icons) / `-softer` (error input bg) |
| Channel colors | `--color-wecom*`, `--color-alipay-*`, … **only if the product has that channel** | semantically SEPARATE from `success` — never alias them |
| Text | `--fs-*` for sizes; text colors: `--color-text`, `-secondary`, `-secondary-strong`, `-muted`, `-on-primary` | — |
| Backgrounds | — | `--color-bg-page/-card/-muted/-subtle/-footer`, `--color-border` |
| Alpha/overlay | `--color-*-rgb` triplets | business writes `rgba(var(--*-rgb), 0.12)` |
| Type scale | `--fs-caption` … `--fs-hero`, ~9 steps | `--fs-body`, `--fs-hint`, `--fs-title-nav`, `--fs-title-hero` |
| Spacing | 4pt grid: `--space-1/2/3/4/5/6/8/12` | `--space-page-x`, `--space-card-gap`, `--space-card-padding`, `--space-section` |
| Radius | `--radius-sm/md/lg/pill` | `--radius-input/card/panel` |
| Motion | `--duration-fast/--duration-base`, `--ease-out: cubic-bezier(0.22,1,0.36,1)` | cross-end projects keep the curve identical to the web SoT |
| Shadows | `--shadow-card/-float/-pop` | shadows may hold rgba **via triplets** INSIDE the SoT |
| Font & layout | `--font-family` (CJK stack), `--app-max-width`, `--nav-height` | — |

Mobile specifics that belong in the SoT, not scattered: safe-area paddings consume
`env(safe-area-inset-*)`; focus-visible ring uses `--color-primary`; tap highlight suppressed in
base reset. Functional px (component-local sizes/offsets) are explicitly NOT token-gated — the gate
covers color first (progressive principle).

## Rules of engagement

1. **Register first, consume second.** A new color enters only via a semantic token in the SoT; PRs
   that consume an unregistered value are wrong even when they pass stylelint (raw rgba and
   Tailwind `bg-[#…]` are known bypasses — see `pitfalls-and-audit.md`).
2. **One intent, one token.** "Warning text" must resolve to exactly one token.
3. **RGB triplets are registered, not improvised.** If a color needs alpha, its `*-rgb` triplet is
   declared next to it. When dark mode reassigns `--color-text`, it MUST also reassign
   `--color-text-rgb`.
4. **Precise variants are debt.** `-softer`, `-vivid` accumulate. Adding one requires a comment
   stating which surface uses it.

## Dark mode strategy

- Single-end: keep `:root` light; add `[data-theme="dark"]` (or `.dark` on `html`) overriding ONLY
  semantic tokens **and their `*-rgb` triplets**. Scale layers and semantic names stay identical.
- Component-lib: Vant — `<van-config-provider theme="dark">`; Varlet — built-in dark vars;
  antd-mobile — override `--adm-*` inside the dark block.
- Cross-end: the shared SoT holds `:root` + `.dark`; native ends generate Any + Dark appearances
  (see `stack-adapters.md` Mode D and `swiftui-style-unify`).

OKLCH (`oklch(0.62 0.19 255)`) is an upgrade path for perceptually uniform ramps. Plain hex is
fine for a first consolidation.
