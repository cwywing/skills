---
name: h5-style-unify
description: Unify style, color, and visual design for an EXISTING H5 / mobile-web project (H5、移动端网页、uniapp、微信内嵌页、管理后台之外的 C 端页面). Use when the user wants to 统一风格 / 统一配色 / 样式统一 / 建立设计系统或 design tokens（theme.css、CSS 变量）、收敛散落的硬编码颜色、加 stylelint 门禁 / pre-commit / CI 校验、做换肤或暗黑模式、保持 H5 与 iOS / 小程序多端视觉一致、或审计项目风格一致性. Encodes a five-ring pipeline (SoT → semantic two-layer tokens → component wrapping → machine gate → acceptance page) cross-validated on two production codebases, including their paid-for pitfalls (gate false-green, rgba blind spot, semantic dual-caliber). NOT for inventing a brand-new visual aesthetic from scratch (that is frontend-design), and NOT for admin-console ops UX walkthroughs (that is admin-console-ux).
metadata:
  version: "0.1.0"
---

# H5 / Mobile Style Unification

Bring an existing H5 / mobile-web codebase from "colors scattered everywhere, consistency by memory" to "one token source, machine-enforced" — without a big-bang rewrite. The pipeline and every pitfall below were cross-validated on two production projects (a bare Vue3 H5 app and a SwiftUI iOS client sharing an H5 SoT); see `references/case-studies.md`.

## Scope

**In scope:** existing H5 / mobile-web frontends — bare Vue / React (no UI lib), Vant, antd-mobile, Varlet, uniapp, or multi-end projects that must stay visually in sync with native apps. Deliverables: a design-token source of truth, consumption layer, UI-component wrapping, a lint gate, and a dev-only acceptance page.

**Out of scope:** inventing a new visual direction from zero (use `frontend-design`), choosing a component library, and native iOS/Android implementation (only the cross-end SoT sync pattern is covered).

## Core pipeline (five rings, in order)

```
1 SoT          theme.css — the ONLY file allowed to hold raw hex
2 Consumption  base.css global classes / component-lib var bridging; business code uses var(--*) only
3 Components   tone × variant semantic wrappers; business passes semantics, never colors
4 Gate         stylelint color-no-hex (error) + pre-commit + CI — fail-closed
5 Acceptance   dev-only design-system page rendering every token and component matrix
```

Three principles govern the order — all three were learned the hard way in the case studies:

1. **A credible gate comes before broad component work.** EvairSIM's retro: "when the gate cannot be trusted, every component merged afterwards is built on sand." Fix/establish the gate first (or in the same pass), then scale components.
2. **A rule that survives beats many rules.** Start with exactly ONE stylelint rule (`color-no-hex`). Adding `--strict` ruleship on day one drowns the codebase in historical debt and the gate gets switched off. Tighten later.
3. **The doc is a projection, never a second SoT.** The design doc indexes token *categories and naming*, never copies color values. Duplicate value tables drift; one was deleted as dead code in the case study (`tokens.js`).

## Workflow

### Phase 0 — Detect the stack (read-only)

Read `package.json` deps + the src tree. Route by this table; details live in `references/stack-adapters.md`:

| Detection | Mode | Adapter |
| --- | --- | --- |
| No UI lib (bare Vue/React) | Pure CSS variables, own SoT | Mode A in `stack-adapters.md` |
| `vant` in deps | SoT + `--van-*` bridge (+ ConfigProvider dark) | Mode B |
| `antd-mobile` | SoT + `--adm-*` bridge | Mode B |
| `varlet` | SoT + global/local var override + dark | Mode B |
| uniapp (`@dcloudio` / `manifest.json`) | CSS vars with platform caveats | Mode C |
| Must match a native app / sibling H5 | Shared SoT + codegen sync | Mode D |

Confirm with the user which directory is the app root (one app per run; never sweep a monorepo in one pass).

### Phase 1 — Audit the baseline (read-only)

Run `node scripts/audit-styles.mjs <app-root>` (zero deps, Node ≥ 18). It reports raw hex / raw rgba / inline-style leaks outside the SoT whitelist, whether an SoT and a gate exist, and exits non-zero on violations — fail-closed. Record the baseline counts in the final report; before/after numbers are the deliverable's proof, not decoration.

### Phase 2 — Build / converge the SoT

Start from `assets/theme.css.tmpl` (annotated, light + optional dark block). Taxonomy and two-layer naming rules — scale layer (`--radius-md`) vs semantic layer (`--radius-card`), status-color four-piece sets, `*-rgb` triplets for alpha — are in `references/token-taxonomy.md`. Key rules:

- Register the semantic token in the SoT FIRST, then consume it in business code. Never the reverse.
- Channel colors (e.g. WeChat green `--color-wecom*`) stay semantically separate from status colors (`--color-success*`) — merging them caused a visible-color regression in the case study.
- For alpha, use `rgba(var(--*-rgb), α)`, not raw rgba.

### Phase 3 — Consumption layer + migration

Mode A: create `src/styles/base.css` that `@import`s the theme and hosts global classes for high-frequency primitives (nav bar, hero, buttons, cards, focus ring). Mode B: add a bridge file mapping component-lib vars onto SoT tokens (`--van-button-primary-background: var(--color-primary)`), so theming the lib never touches lib internals.

Migrating existing hardcodes is Tier-2 mutation (see below): batch per-file `#hex → var(--*)`, one visual intent per commit. A pure refactor must not change any rendered pixel; if a swap DOES change what users see (e.g. a badge recolored from WeChat green to business `success`), call it out separately — that is a visual decision, not cleanup.

### Phase 4 — The gate (machine enforcement)

Copy `assets/stylelintrc.json.tmpl` → `h5/.stylelintrc.json`, whitelist ONLY the SoT in `.stylelintignore`, wire pre-commit (`simple-git-hooks` + `lint-staged`, staged files only), and add CI when possible. Full configs, the `customSyntax` trap (postcss-html MUST live inside `overrides`, or the rule silently dies for plain `.css` — a real false-green), and the gate self-test are in `references/gate-configs.md`.

Self-test before declaring victory: inject `color: #abcdef` into a non-whitelisted file → lint MUST exit non-zero; remove it → exit 0. A gate that was never seen to fail is unverified.

### Phase 5 — Acceptance page

Drop in `assets/DesignSystemPage.vue.tmpl` (Vue3; adapt for React), register the route dev-only (`import.meta.env.DEV` for Vite; excluded from prod build). Swatches must render via `var(--token)` so the page shows runtime-truth, not copied values. Every new wrapped component MUST be registered in its matrix — an unregistered component is invisible to review.

### Phase 6 — Record honestly

Write the audit table (phases P0–P5 with real status) and a "known leftovers" section into the design doc — unpaid debt, un-migrated pages, gate blind spots. The case-study docs' credibility comes entirely from this honesty; mirror it. Then re-run the audit script and report before/after counts.

## Mutation safety

This skill edits real state. Tiering and discipline (see
`../skill-authoring/references/mutation-safety.md`):

- **Read-only (no confirmation):** Phases 0–1 — stack detection, audit, reporting.
- **Tier 1 — additive files (confirm scope once, up front):** theme.css, base.css, bridge file, stylelint configs, acceptance page. State the file list before creating.
- **Tier 2 — editing business styles (per-batch confirmation):** hex→var migration. Show the plan and ONE sample file's diff first; on approval, batch the rest per-file. Never mix a pure token swap with a visible color change in one commit.
- **Tier 3 — shared workflow config (explicit confirmation each time):** git hooks, lint-staged, CI files. These affect every contributor's commit flow.
- **No explore-on-failure:** if the gate self-test fails or the audit script errors, stop and report the exact output — do not "fix" by weakening the rule, deleting the whitelist entry, or re-running with flags until it goes green. Weakening a gate to pass it is the exact failure mode this skill exists to prevent.

## Correct / Incorrect (consumption contract)

**Incorrect** — business code owning color values, the drift this skill eliminates:

```css
/* views/Order.vue */
.badge-warning { background: #fff7e6; color: #ff7d00; }  /* raw hex, third copy of "warning" */
.overlay { background: rgba(15, 23, 42, 0.5); }           /* raw rgba — gate blind spot */
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

One-line rationale: identical pixels, but the color now has exactly one owner and re-theming is a one-file change.

## Reference files (read on demand)

- `references/token-taxonomy.md` — full token taxonomy, two-layer naming, when to add a variant vs reuse, dark-mode strategy.
- `references/stack-adapters.md` — Modes A–D: bare CSS vars / Vant / antd-mobile / Varlet / uniapp / cross-end SoT + codegen sync.
- `references/gate-configs.md` — every gate config verbatim (stylelint, ignore, hooks, CI), the false-green lessons, gate self-test.
- `references/pitfalls-and-audit.md` — the cross-validated pitfall list (rgba blind spot, semantic dual-caliber, SoT drift, …), audit-table template, acceptance checklist.
- `references/case-studies.md` — the two production projects side by side, with adoption counts and file paths.

## Self-check before done

- [ ] Audit script exits 0; before/after violation counts reported.
- [ ] Gate self-test performed and OBSERVED to fail on injected `#abcdef`.
- [ ] Acceptance page reachable in dev, absent from the prod build.
- [ ] Design doc written as projection (no copied color tables) + honest leftovers section.
- [ ] Any visible color changes listed separately from pure refactors.
