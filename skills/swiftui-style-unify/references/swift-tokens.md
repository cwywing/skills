# Swift Tokens — the token layer's anatomy

Provenance: EvairSIM `EvairSIM/App/Theme/Tokens/` (9 files, 499 lines total), read from
source. Community cross-check: the "single namespace type" advice (Design Systems
Collective's *Building a SwiftUI Design System*) matches EvairSIM's `DesignTokens` exactly;
the 3-layer token hierarchy in open-source `swift-design-system` maps to the same
primitive → semantic split used by `h5-style-unify`.

## File layout (one concern per file)

```
App/Theme/Tokens/
├── DesignTokens.swift      17-line namespace: enum DesignTokens { typealias … }
├── ColorTokens.swift       the ONLY file where Color("AssetName") appears
├── EvairTextStyle.swift    full font object + Dynamic Type policy + catalog
├── TypographyTokens.swift  thin alias so DesignTokens.Typography.* returns style objects
├── SpacingTokens.swift     4pt grid, named steps
├── RadiusTokens.swift      named steps (semantic: card/input/pill)
├── ShadowTokens.swift      shadow presets + .evairShadow() modifier
├── MetricsTokens.swift     icon/control sizes (NOT spacing — sizing intent)
└── MotionTokens.swift      durations + canned Animations, curves ported from web SoT
```

The namespace entry is deliberately trivial — typealiases only, so refactors never touch
Feature code:

```swift
enum DesignTokens {
    typealias Colors = ColorTokens
    typealias Typography = TypographyTokens
    typealias Spacing = SpacingTokens
    typealias Radius = RadiusTokens
    typealias Shadow = ShadowTokens
    typealias Metrics = MetricsTokens
    typealias Motion = MotionTokens
}
```

Feature code references `DesignTokens.Metrics.*` — the gate even forbids direct
`MetricsTokens` references in Features, so the alias layer is load-bearing, not cosmetic.

## ColorTokens — semantics, never asset names

Values live in Asset Catalog colorsets (Any + Dark appearances); the Swift file is a pure
semantic index. Group by intent, mirroring the web SoT's families:

- **Brand**: `brandPrimary`, `brandPrimaryForeground`, `brandPrimaryGlow`, `ring`
- **App shell** (authenticated/catalog surfaces): `appBackground`, `appSurface`, `appCard`,
  `appCardHover`, `appBorder`, `appMuted`, `appText`, `appTextMuted`
- **Global surfaces**: `background`, `foreground`, `surface`, `surfaceForeground`,
  `border`, `input`
- **Secondary/accent**: `secondary(-Foreground)`, `muted(-Foreground)`, `accent(-Foreground)`
- **Feedback**: `destructive(-Foreground)`, `success(+Background)`, `warning(+Background)`,
  `danger(+Background)`, `info(+Background)` — note the paired `*Background` soft colors,
  the Swift analogue of the H5 "status four-piece set".

Ship the **swatch catalog with cross-end references** — each entry carries the H5 variable
name it was generated from. Drift becomes greppable in both directions:

```swift
static let catalog: [EvairColorSwatch] = [
    .init(id: "brandPrimary", name: "Brand Primary", color: brandPrimary, h5Variable: "--primary"),
    .init(id: "success",      name: "Success",       color: success,      h5Variable: "--app-success"),
    // …
]
```

## EvairTextStyle — typography as a complete object

A font token that carries only a size is half a decision. The production shape:

```swift
enum EvairDynamicTypePolicy: Sendable {
    case fixed                            // display/hero only; does not scale — use sparingly
    case relative(Font.TextStyle)         // scales with the system curve — preferred default
}

struct EvairTextStyle: Sendable {
    let name: String
    let policy: EvairDynamicTypePolicy
    let size: CGFloat                     // design spec size
    let weight: Font.Weight
    let design: Font.Design
    let lineHeight: CGFloat               // target line height in points
    let tracking: CGFloat                 // web em × size, e.g. -0.025 × 22

    var font: Font { /* fixed → .system(size:weight:design:); relative → .system(textStyle:).weight() */ }
    var lineSpacing: CGFloat { max(0, lineHeight - size) }   // SwiftUI's unit is spacing, not height
}

extension View {
    func evairTextStyle(_ style: EvairTextStyle) -> some View {
        font(style.font).tracking(style.tracking).lineSpacing(style.lineSpacing)
    }
}
```

Why each field earns its place:

- **policy** — the moment typography is tokenized, Dynamic Type becomes a per-token
  decision instead of per-view chaos. `relative` is the default; `fixed` is an explicit,
  documented exception (display sizes).
- **lineHeight → lineSpacing** — the web spec speaks line-height; SwiftUI wants extra
  spacing. The token converts at the boundary so Feature code never does this math.
- **tracking from em** — headings port the web `letter-spacing: -0.025em` as
  `size * -0.025`; keep the em constant beside the catalog, not scattered.
- **catalog** — an array of every style, consumed by the acceptance view; a style not in
  the catalog is not reviewable.

Naming (17 styles in the case): `display/headline/body/label` × `Large/Medium/Small`,
plus purpose names (`caption`, `price`, `button`, `tabLabel`). Purpose names are the
semantic layer — prefer them in Feature code; size-grid names are for the token layer.

## Motion — port the curve, document the exceptions

```swift
Animation.timingCurve(0.22, 1, 0.36, 1, duration: 0.2)   // the web cubic-bezier, verbatim
```

Durations: `fast 0.2` (slightly above the web 0.15 — the curve is imperceptible under
~0.2s on press), `normal 0.25`, `shimmer 1.2`. The shimmer is documented as linear ON
PURPOSE (it is a loading loop, not a UI transition) — exceptions written down stop
"why is this one different" archaeology later.

## Metrics vs Spacing — keep them separate

Spacing answers "gap between things" (4pt grid). Metrics answers "how big is this thing"
(`leadingIconSize`, `thumbnailSize`, control heights). The gate's icon-size rule exists
because of this split: sizing an SF Symbol with a TYPOGRAPHY token smuggles line-height
and tracking into an image — hence `.evairSymbolSize(DesignTokens.Metrics.*)` and the
multiline lint against `Image(...)` + `.evairTextStyle`.
