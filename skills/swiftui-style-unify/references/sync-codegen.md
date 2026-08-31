# Cross-End Sync & Codegen — shared web SoT → iOS colorsets

This file owns the Swift side; the web side and the sync *contract* belong to `h5-style-unify`
Mode D. The runnable generator ships as `scripts/sync-design-tokens.mjs`.

## The pipeline

```
<web-app>/src/theme/theme.css  (:root + .dark / [data-theme=dark])
        │  node scripts/sync-design-tokens.mjs --css … --assets … --map …
        ▼
Assets.xcassets/*.colorset  (Any + Dark appearances, sRGB)   ← generated, committed
        ▼
ColorTokens.swift semantic names → DesignTokens → views
```

Three rules make codegen trustworthy:

1. **The MAP is the only hand-written bridge.** `assets/color-map.json.tmpl`:
   `{ "AppWarning": ["--color-warning", "--color-warning"] }` — asset name → [lightVar, darkVar].
   Adding a color: CSS var → MAP entry → ColorTokens name → run sync → eyeball DEBUG tab.
2. **Committed-but-regenerated.** Colorsets are committed (Xcode needs them); CI re-runs the
   sync and fails on any diff.
3. **No second SoT.** Do not check in a generated JSON token dump as something humans edit.

## Running the shipped script

```bash
node scripts/sync-design-tokens.mjs \
  --css ../h5/src/theme/theme.css \
  --assets App/Assets.xcassets \
  --map scripts/color-map.json
```

`--dry-run` prints conversions without writing. Values supported: `#hex`, `oklch(L C h)`,
`rgb()` / `rgba()` numbers, `var(--other)`. Unresolvable values fail the run.

Copy `assets/color-map.json.tmpl` into the iOS repo and grow it. Dark values come from the SoT's
`.dark` or `[data-theme="dark"]` block; missing dark vars fall back to light (still fail if the
light var is missing).

## Dark mode falls out for free

Each colorset carries two appearances (Any + Dark). Views never know dark mode exists. If a
surface needs different dark handling, fix it in the SoT, not in Swift.

## CI posture

The job re-runs the sync; any colorset diff fails the build. When the H5 path is unreachable,
the job goes RED — not "best effort skip".

## When to prefer Style Dictionary instead

| Situation | Better fit | Why |
| --- | --- | --- |
| Product already has a live web frontend that IS the visual reference | shared web CSS SoT + this script | no third artifact; color truth tracks the shipping web app |
| iOS-only, or tokens owned by a design tool (Tokens Studio/Figma) | Style Dictionary | token JSON is the natural SoT |
| Many platforms with no canonical one | Style Dictionary (or Specify) | one SoT feeding N generators |

If you start custom and later add a third platform, migrating the MAP into a Style Dictionary
config is mechanical — semantic names survive; only the SoT file format changes.
