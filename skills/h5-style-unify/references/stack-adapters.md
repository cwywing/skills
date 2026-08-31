# Stack Adapters — Modes A–D

Route here from P0. All modes share the same five rings; what differs is the consumption layer
(P4) and where theming hooks attach.

## Mode A — Bare Vue / React, no UI library

The reference H5 implementation. Full anatomy:

```
src/theme/theme.css     SoT — only file with hex (stylelint-whitelisted)
src/styles/base.css     @import theme.css; global classes + resets
main.js                 imports base.css ONLY — single global entry
components/ui/          AppStatusTag (tone × variant), AppButton (variant × size)
views/_DesignSystem.vue acceptance page, dev-only route
```

Entry discipline: the app imports exactly one global stylesheet. Views/components may only add
scoped styles, all consuming `var(--*)`. React equivalents: same files, `.css` imports in root,
components in `components/ui/` with the same prop shape.

## Mode B — Component library (Vant / antd-mobile / Varlet)

Theme the lib by **bridging its CSS variables onto your SoT** — never by editing lib internals.

```css
/* src/theme/bridge-vant.css — Vant 4 */
:root {
  --van-button-primary-background: var(--color-primary);
  --van-button-primary-border-color: var(--color-primary);
  --van-cell-background: var(--color-bg-card);
  --van-text-color: var(--color-text);
  --van-danger-color: var(--color-danger);
}
.van-theme-dark {
  --van-cell-background: var(--color-bg-card);
}
```

- **Vant 4**: `--van-*`; dark via `<van-config-provider theme="dark">` (`van-theme-dark`).
- **antd-mobile**: `--adm-*`. Drive dark via your own block re-assigning `--adm-*`.
- **Varlet**: built-in dark + global/local override. Bridge palette props onto SoT tokens.

Lib CSS in `node_modules` is out of stylelint scope. The bridge file IS in scope and must consume
only `var(--*)`.

## Mode C — uniapp

Two variable systems coexist:

- `uni.scss` — SCSS variables, **compile-time**. Cannot switch at runtime.
- CSS custom properties in App.vue `<style>` (not scoped) or a global css/wxss file — runtime-capable
  on H5 and WeChat MP. **nvue does not support CSS variables.**

Practical shape: SoT stays a plain-CSS file of custom properties imported by App.vue global style
**or** lives in App.vue global `<style>` with `:root` / `page`. The audit script detects SoT in
`.css` / `.scss` / `.wxss` **and** Vue/uni SFC style blocks. `uni.scss` may mirror a few
compile-time constants with a comment that the SoT is authoritative.

Scan coverage: `.vue` / `.nvue` / `.uvue` / `.wxss`. If a platform file type is not scanned, list
it in leftovers rather than pretending the gate covers it.

## Mode D — Cross-end shared SoT + codegen

When H5 and native apps must not drift, ONE web file is the SoT. **This file owns the web side
and the sync contract. The Swift/Asset-Catalog side lives in `swiftui-style-unify`**
(`scripts/sync-design-tokens.mjs`, MAP, ColorTokens, CI diff).

```
<app-root>/src/theme/theme.css   SoT: :root + .dark
swiftui-style-unify/scripts/sync-design-tokens.mjs
    → iOS Assets.xcassets/*.colorset (Any + Dark)
ColorTokens.swift                generated colorsets as typed tokens
CI                               re-runs sync; a stale colorset diff fails the build
```

Rules:

1. Generated colorsets are **committed** (Xcode needs them) but CI regenerates and diffs.
2. No hand-edited intermediate JSON SoT.
3. Motion curves port verbatim.
4. Adopt Mode D only when a second platform actually exists.

## Legacy Blade / CDN-Antd backends (adjacent, lower priority)

Server-rendered admin with Antd via CDN cannot join a build-time system. Proven lightweight move:
extract a `status-tag` partial with a semantic map so status semantics are single-sourced. Full
unification needs a build chain — treat as a separate project; do not block H5 work on it.
