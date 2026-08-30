# Cross-End Sync & Codegen — shared web SoT → iOS colorsets

Provenance: EvairSIM `scripts/sync-design-tokens.mjs` (174 lines) + CI + docs, read from
source. This file owns the Swift side; the web side and the sync *contract* belong to
`h5-style-unify` Mode D — the two skills meet here.

## The pipeline

```
h5/src/styles.css (:root + .dark, OKLCH variables)     ← ONLY hand-maintained color SoT
        │  node scripts/sync-design-tokens.mjs
        ▼
Assets.xcassets/*.colorset  (Any + Dark appearances, sRGB)   ← generated, committed
docs/design-tokens-colors.json                              ← generated, GITIGNORED
        ▼
ColorTokens.swift semantic names → DesignTokens → Features
```

Three rules make codegen trustworthy:

1. **The MAP is the only hand-written bridge.** `const MAP = { AppWarning:
   ['--app-warning', '--app-warning'], … }` — asset name → [lightVar, darkVar]. A new
   color is a four-step procedure (documented in the cursor rule, enforced by habit):
   add the CSS var → register in MAP → add the semantic name in ColorTokens → run sync
   and eyeball the DEBUG acceptance tab. No step may be skipped silently.
2. **Committed-but-regenerated.** Colorsets are committed (Xcode needs them in the
   catalog), but CI re-runs the sync and fails on any diff — hand-edits to generated
   files are caught, not trusted.
3. **The intermediate JSON is gitignored.** It is a local debugging list, explicitly
   labeled "not a second SoT". Two sources of truth = drift; the case deleted one before
   it hurt.

## OKLCH → sRGB

The web SoT stores colors as `oklch(L C h)` (perceptually uniform — soft/text/border
families are mathematically related ramps; the open-source ColorTokensKit-Swift validates
the same choice independently). The sync script converts OKLCH → (linear sRGB → gamma)
and writes plain sRGB components into the colorset JSON, because Asset Catalogs want
sRGB/display-P3 numbers, not modern CSS color functions. Conversion code lives in ONE
place (the script); neither platform ever re-implements it.

## Dark mode falls out for free

Each colorset carries two appearances (Any + Dark) generated from the SoT's `:root` and
`.dark` blocks. iOS switches automatically; Feature code never knows dark mode exists.
The mistake to avoid: a THIRD appearance or conditional color logic in views — if a
surface needs different dark handling, fix it in the SoT, not in Swift.

## CI posture (fail-closed, literally)

The production CI job clones/pulls the sibling H5 repo and re-runs the sync; any colorset
diff fails the build. When the H5 fetch itself fails, the job goes RED — the opposite of
"best effort skip". Any step that would be skipped on failure must instead fail; that
single posture is what makes the whole pipeline honest.

## When to prefer Style Dictionary instead

The generic industry tool ([Style Dictionary](https://styledictionary.com/), Amazon-born)
generates iOS Swift classes AND colorsets from a token JSON SoT, with first-class
light/dark support (see its creator's dark-mode guide). Choose per situation:

| Situation | Better fit | Why |
| --- | --- | --- |
| Product already has a live web frontend that IS the visual reference | shared web CSS SoT + custom sync (this pattern) | no third artifact to maintain; designers/devs already edit styles.css; color truth tracks the shipping web app |
| iOS-only product, or tokens owned by a design tool (Tokens Studio/Figma) | Style Dictionary | token JSON is the natural SoT; battle-tested generators for every platform you will add |
| Many platforms (web + iOS + Android) with no canonical one | Style Dictionary (or Specify) | one SoT feeding N generators beats N pairwise sync scripts |

If you start custom and later add a third platform, migrating the MAP into a Style
Dictionary config is mechanical — the semantic names survive; only the SoT file format
changes. Decide once, record the decision in the design doc.
