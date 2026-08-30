# Stack Adapters — Modes A–D

Route here from Phase 0. All modes share the same five rings; what differs is the consumption layer
(Phase 3) and where theming hooks attach.

## Mode A — Bare Vue / React, no UI library (star-training pattern)

The reference implementation. Full anatomy:

```
src/theme/theme.css     SoT — only file with hex (stylelint-whitelisted)
src/styles/base.css     @import theme.css; global classes: .nav-bar .hero-block
                        .btn-pill(.lg/.ghost) .btn-text .card .panel .footer-hint
                        + resets (safe-area, tap-highlight, focus-visible ring)
main.js                 imports base.css ONLY — single global entry
components/ui/          AppStatusTag (tone × variant), AppButton (variant × size)
views/_DesignSystem.vue acceptance page, dev-only route
```

Entry discipline: the app imports exactly one global stylesheet. Views/components may only add
scoped styles, all consuming `var(--*)`. React equivalents: same files, `.css` imports in root,
components in `components/ui/` with the same prop shape.

## Mode B — Component library (Vant / antd-mobile / Varlet)

The lib is themed by **bridging its CSS variables onto your SoT** — never by editing lib internals
or restyling per component. All three libs are CSS-variable native, so a single bridge file holds
the entire mapping:

```css
/* src/theme/bridge-vant.css — Vant 4 */
:root {
  --van-button-primary-background: var(--color-primary);
  --van-button-primary-border-color: var(--color-primary);
  --van-cell-background: var(--color-bg-card);
  --van-text-color: var(--color-text);
  --van-danger-color: var(--color-danger);
  /* …map the tokens you actually use; grow on demand */
}
.van-theme-dark {  /* only if dark mode: Vant toggles this class via ConfigProvider */
  --van-cell-background: var(--color-bg-card);  /* your dark block already re-assigned it */
}
```

- **Vant 4**: vars are `--van-*`; dark mode via `<van-config-provider theme="dark">` which adds
  `van-theme-dark` and swaps the lib's own variable set. Your bridge keeps working because it maps
  to YOUR tokens, whose dark values your `[data-theme="dark"]` block re-assigns.
- **antd-mobile**: vars are `--adm-*` (`--adm-color-primary`, `--adm-color-background`,
  `--adm-color-text`, …). Same bridge pattern; no dark-theme class — drive dark via your own block
  re-assigning `--adm-*`.
- **Varlet**: built-in dark theme + global/local override (`:root { --color-primary: … }` style).
  Bridge `varlet`'s palette props onto SoT tokens; dark toggling is provided by the lib.

Gate scope note: lib CSS ships inside `node_modules` — stylelint never sees it. The bridge file IS
in scope and must consume only `var(--*)`.

## Mode C — uniapp

Two variable systems coexist; know which one you are touching:

- `uni.scss` — SCSS variables, **compile-time**, injected into every file. Fine for build-time
  constants; CANNOT switch at runtime (no dark toggle / no white-label via uni.scss).
- CSS custom properties in App.vue `<style>` (not scoped) or a global css file — runtime-capable;
  supported on H5 and WeChat MP (vars resolve per-page on MP; prefer declaring on `page`/`:root` in
  App.vue global style). **nvue does not support CSS variables** — keep nvue pages on uni.scss
  constants or inline themes.

Practical shape: SoT stays a plain-CSS file of custom properties imported by App.vue global style;
`uni.scss` may mirror a few compile-time constants with a comment that the SoT is authoritative
(mirroring is a documented exception — it is a compile artifact, not a second source you edit).

## Mode D — Cross-end shared SoT + codegen (EvairSIM pattern)

When H5 and native apps must not drift, ONE web file is the SoT for every platform:

```
../h5/src/styles.css          SoT: :root + .dark, OKLCH custom properties
scripts/sync-design-tokens.mjs  parse SoT → OKLCH→sRGB conversion → write:
                               iOS Assets.xcassets/*.colorset (Any + Dark)
                               + design-tokens-colors.json (intermediate, gitignored)
ColorTokens/…/DesignTokens.swift  generated colorsets surfaced as typed tokens
CI                            re-runs sync; a stale colorset diff fails the build
                               (and an unreachable H5 repo fails the job — fail-closed)
```

Rules that make codegen safe:

1. The generated artifacts are **committed** (colorsets) so Xcode sees them, but CI re-generates and
   diffs — hand-edits to generated files are caught, not trusted.
2. The intermediate JSON is gitignored — never a hand-edited middle layer.
3. Native consumption mirrors Mode A's contract: Features layer MUST NOT use `Color(...)`,
   `.font(.system(size:))`, raw `padding(N)`; a ripgrep lint enforces it (see `gate-configs.md`).
4. Motion curves are ported verbatim (`cubic-bezier(0.22,1,0.36,1)` → the iOS spring/curve token) —
   cross-end consistency includes feel, not just color.

Adopt Mode D only when a second platform actually exists; its cost is a sync script + CI discipline.

## Legacy Blade / CDN-Antd backends (adjacent, lower priority)

Server-rendered admin with Antd via CDN can't join a build-time system. Proven lightweight moves:
extract a `status-tag` partial with a semantic map (`pending→orange, approved→green`) so at least
status semantics are single-sourced, and align the CDN theme's primary with the H5 primary
(`#1890ff` vs `#1677ff` mismatch is a recorded leftover in the case study). Full unification needs
a build chain — treat as a separate project, don't block H5 work on it.
