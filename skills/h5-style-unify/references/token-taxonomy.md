# Token Taxonomy — the SoT's internal structure

Provenance: `h5/src/theme/theme.css` of the star-training case (143 lines, bare Vue3), cross-checked
against EvairSIM's token layer (`ColorTokens/Typography/Spacing/Radius/Motion`). The template to
start from is `assets/theme.css.tmpl`.

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
| Channel colors | `--color-wecom*` (WeChat green), `--color-alipay-*`, … | semantically SEPARATE from `success` — never alias them |
| Text | `--fs-*` for sizes; text colors: `--color-text`, `-secondary`, `-secondary-strong`, `-muted`, `-on-primary` | — |
| Backgrounds | — | `--color-bg-page/-card/-muted/-subtle/-footer`, `--color-border` |
| Alpha/overlay | `--color-*-rgb` triplets | business writes `rgba(var(--*-rgb), 0.12)` |
| Type scale | `--fs-caption(12) … --fs-hero(28)`, ~9 steps | `--fs-body`, `--fs-hint`, `--fs-title-nav`, `--fs-title-hero` |
| Spacing | 4pt grid: `--space-1/2/3/4/5/6/8/12` | `--space-page-x`, `--space-card-gap`, `--space-card-padding`, `--space-section` |
| Radius | `--radius-sm/md/lg/pill` | `--radius-input/card/panel` |
| Motion | `--duration-fast(0.12s)/base(0.15s)`, `--ease-out: cubic-bezier(0.22,1,0.36,1)` | cross-end projects keep the curve identical to the web SoT |
| Shadows | `--shadow-card/-float/-pop` (+decorative) | shadows may hold raw rgba INSIDE the SoT — acceptable, documented |
| Font & layout | `--font-family` (CJK stack), `--app-max-width: 430px`, `--nav-height: 48px` | — |

Mobile specifics that belong in the SoT, not scattered: safe-area paddings consume
`env(safe-area-inset-*)`; focus-visible ring uses `--color-primary`; tap highlight suppressed in
base reset. Functional px (component-local sizes/offsets) are explicitly NOT token-gated — the gate
covers color only (progressive principle).

## Rules of engagement

1. **Register first, consume second.** A new color enters only via a semantic token in the SoT; PRs
   that consume an unregistered value are wrong even when they pass the lint (raw rgba is the known
   bypass — see `pitfalls-and-audit.md`).
2. **One intent, one token.** "Warning text" must resolve to exactly one token. The case study had
   `--color-warning` and `--color-warning-text` both used as warning text in different files —
   tokenized yet still dual-caliber; convergence happens only when every consumer names the same token.
3. **RGB triplets are registered, not improvised.** If a color needs alpha, its `*-rgb` triplet is
   declared next to it in the SoT (`--color-primary-rgb: 22, 119, 255`). Ad-hoc `rgba(r,g,b,…)`
   with literal numbers is a violation even without hex.
4. **Precise variants are debt.** `-softer`, `-vivid` style variants accumulate ("history hex
   museum"). Adding one requires a comment stating which surface uses it; audit periodically and
   merge near-duplicates.

## Dark mode strategy

- Single-end project: keep `:root` light; add `[data-theme="dark"] { … }` (or `.dark` class on
  `html`) overriding ONLY semantic tokens. Scale layers and semantic names stay identical — dark
  mode is a re-assignment, not a second taxonomy.
- Component-lib projects: Vant — `<van-config-provider theme="dark">`; Varlet — built-in dark theme
  vars; antd-mobile — override its `--adm-*` set inside your dark block.
- Cross-end (EvairSIM pattern): the shared SoT file holds `:root` + `.dark` blocks; native ends
  generate Any + Dark appearances from both (see `stack-adapters.md` Mode D).

EvairSIM's SoT uses OKLCH variables (`oklch(0.62 0.19 255)`) — perceptually uniform ramps make
soft/text/border sets mathematically related. Plain hex is fine for a first consolidation; if you
generate palettes or need WCAG-checked steps, OKLCH + a contrast check is the upgrade path.
