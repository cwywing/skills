---
name: h5-style-unify
description: Unify style, color, and visual design for an EXISTING H5 / mobile-web project (H5、移动端网页、uniapp、微信内嵌页、管理后台之外的 C 端页面). Use when the user wants to 统一风格 / 统一配色 / 样式统一 / 建立设计系统或 design tokens（theme.css、CSS 变量）、收敛散落的硬编码颜色、加 stylelint 门禁 / pre-commit / CI 校验、做换肤或暗黑模式、保持 H5 与 iOS / 小程序多端视觉一致、或审计项目风格一致性. Encodes a five-ring pipeline (SoT → gate → migrate → components → acceptance) from one production H5 codebase, with a sibling iOS case for the shared-SoT pattern. NOT for inventing a brand-new visual aesthetic from scratch (that is frontend-design), and NOT for admin-console ops UX walkthroughs (that is admin-console-ux).
metadata:
  version: "0.2.1"
---

# H5 / Mobile Style Unification

Bring an existing H5 / mobile-web codebase from "colors scattered everywhere, consistency by memory" to "one token source, machine-enforced" — without a big-bang rewrite.

Evidence (state it this way when reporting): **one production H5 case** (bare Vue3 WeChat-embedded app) proved theme.css + stylelint + rgba/inline-style pitfalls; a **sibling SwiftUI app** sharing that H5 SoT proved the five-ring order and codegen. Details in `references/case-studies.md`. Do not claim two independent H5 production rollouts.

## Scope

**In scope:** existing H5 / mobile-web frontends — bare Vue / React (no UI lib), Vant, antd-mobile, Varlet, uniapp, or multi-end projects that must stay visually in sync with native apps. Deliverables: a design-token source of truth, consumption layer, UI-component wrapping, a lint gate, and a dev-only acceptance page.

**Out of scope:** inventing a new visual direction from zero (use `frontend-design`), choosing a component library, and native iOS/Android implementation (use `swiftui-style-unify`; only the web side of the shared-SoT contract lives here).

## Architecture vs install order

When the job is done, five rings exist:

```
1 SoT          theme.css — the ONLY file allowed to hold raw hex
2 Consumption  base.css / component-lib var bridging; business uses var(--*) only
3 Components   tone × variant semantic wrappers; business passes semantics
4 Gate         stylelint color-no-hex (error) + pre-commit + CI — fail-closed
5 Acceptance   dev-only page rendering every token and component matrix
```

**Install them in the Phase order below, not in ring-number order.** A credible gate (Phase 3, self-test observed failing) comes before broad component work (Phase 5). Building components on an untrusted gate is how the iOS sibling paid: every component merged afterwards sat on sand.

Other principles: **one rule that survives beats many rules** (start with `color-no-hex` only); **the doc is a projection** (index names, never copy color tables).

## Effort calibration

| Ask | Do |
| --- | --- |
| One file / one leaked color | Confirm SoT exists; fix that file; run the audit. Install the gate only if none exists. Skip the component library. |
| 「统一风格」 / whole app | Full P0–P6 on **one** app root. |
| H5 + iOS must match | This skill owns the web SoT + Mode D contract; `swiftui-style-unify` owns Swift + `scripts/sync-design-tokens.mjs`. |

## Workflow

Phase numbers below **are** the audit-table rows. Do not invent a second P0–P5.

### P0 — Detect the stack (read-only)

Read `package.json` deps + the src tree. Route by this table; details live in `references/stack-adapters.md`:

| Detection | Mode | Adapter |
| --- | --- | --- |
| No UI lib (bare Vue/React) | Pure CSS variables, own SoT | Mode A |
| `vant` in deps | SoT + `--van-*` bridge | Mode B |
| `antd-mobile` | SoT + `--adm-*` bridge | Mode B |
| `varlet` | SoT + global/local var override | Mode B |
| uniapp (`@dcloudio` / `manifest.json`) | CSS vars with platform caveats | Mode C |
| Must match a native app | Shared SoT; Swift skill does codegen | Mode D |

Confirm with the user which directory is the app root (one app per run; never sweep a monorepo in one pass). Configs use `<app-root>`, not a hardcoded `h5/` prefix.

### P1 — Audit the baseline (read-only)

Run this skill's `scripts/audit-styles.mjs <app-root>` (zero deps, Node ≥ 18). It reports raw hex (including Tailwind `bg-[#…]`), raw rgba/hsl, inline-style leaks, Vue SFC `<script>` color literals, and uniapp `.wxss`/`.nvue`/`.uvue`. SoT detection covers css/scss/wxss **and** Vue/uni global `<style>` (`:root` / `page`). Record the error/warning counts — before/after is the deliverable's proof.

### P2 — Build / converge the SoT

Start from `assets/theme.css.tmpl`. Taxonomy is in `references/token-taxonomy.md`. Key rules:

- Register the semantic token in the SoT FIRST, then consume it. Never the reverse.
- Channel colors (WeChat green, Alipay blue, …) stay a **separate family** from `success` — aliasing them caused a visible regression. Do not put a specific channel into the default SoT unless the product has that channel.
- For alpha, use `rgba(var(--*-rgb), α)`. If a color changes in dark mode, reassign its `*-rgb` triplet too.

### P3 — Gate (before components, before a full-repo CI hammer)

Copy `assets/stylelintrc.json.tmpl` → `<app-root>/.stylelintrc.json`. Whitelist ONLY the SoT in `.stylelintignore`. Full configs, the `customSyntax` trap, and the self-test are in `references/gate-configs.md`.

Self-test: inject `color: #abcdef` into a non-whitelisted file → lint MUST exit non-zero; remove it → exit 0. A gate never seen failing is unverified.

If historical hex would drown CI on day one: wire **pre-commit / lint-staged on staged files only** now, and turn on full-repo CI in P6 after migration. Do not skip the self-test. Do not start Phase 5 component wrapping until this self-test has been observed.

### P4 — Consumption layer + mechanical migration

Mode A: `src/styles/base.css` that `@import`s the theme and hosts global classes. Mode B: a bridge file mapping lib vars onto SoT tokens.

Tier-2 mutation: batch per-file `#hex → var(--*)`, one visual intent per commit. A pure refactor must not change any rendered pixel. A badge recolored from a channel green to business `success` is a **separate** visual decision.

### P5 — Components + acceptance page

Wrap high-frequency visuals (`AppStatusTag` tone×variant, `AppButton`, …) so business passes semantics. Drop in `assets/DesignSystemPage.vue.tmpl` (Vue3; adapt for React), route **dev-only**. Swatches render via `var(--token)` — token names only, no copied px/hex. Every new wrapped component registers in the same change.

### P6 — Record honestly + durable CI

Fill the audit table (same P0–P6). List leftovers by file path. Re-run the audit script and report before/after counts. If CI is not yet fail-closed, add it now (`lint:css` + `audit-styles.mjs`).

## Mutation safety

This skill edits real code.

- **Read-only:** P0–P1.
- **Tier 1 — additive files (confirm scope once):** theme.css, base.css, bridge, stylelint configs, acceptance page. List files before creating.
- **Tier 2 — editing business styles (per-batch):** hex→var. Show the plan and ONE sample diff first.
- **Tier 3 — hooks / CI (explicit confirmation each time).**
- **No explore-on-failure:** if the self-test or audit errors, report the exact output. Do not weaken the rule, delete the whitelist entry, or rerun until green.

## Correct / Incorrect (consumption contract)

**Incorrect** — business code owning color values:

```css
/* views/Order.vue */
.badge-warning { background: #fff7e6; color: #ff7d00; }
.overlay { background: rgba(15, 23, 42, 0.5); }
```

**Correct** — values live once in the SoT; business speaks semantics:

```css
/* src/theme/theme.css (the ONLY hex allowed) */
--color-warning-soft: #fff7e6;
--color-warning-text: #d48806;
--color-overlay-rgb: 15, 23, 42;

/* views/Order.vue */
.badge-warning { background: var(--color-warning-soft); color: var(--color-warning-text); }
.overlay { background: rgba(var(--color-overlay-rgb), 0.5); }
```

Rationale: identical pixels, one owner, re-theming is a one-file change.

## Reference files (read on demand)

- `references/token-taxonomy.md` — taxonomy, two-layer naming, dark-mode (including `*-rgb`).
- `references/stack-adapters.md` — Modes A–D.
- `references/gate-configs.md` — verbatim configs, customSyntax trap, self-test (`<app-root>`, not `h5/`).
- `references/pitfalls-and-audit.md` — pitfall list, audit-table template (P0–P6), checklist.
- `references/case-studies.md` — H5 production case + iOS sibling; numbers live only there.

## Self-check before done

- [ ] Audit script before/after counts reported; final run exits 0 (or leftovers listed by path).
- [ ] Gate self-test OBSERVED to fail on injected `#abcdef`, then pass.
- [ ] Acceptance page reachable in dev, absent from the prod build; no copied color/px tables.
- [ ] Visible color changes listed separately from mechanical refactors.
- [ ] Evidence phrased as one H5 case + optional iOS sibling, not "two H5 productions".
