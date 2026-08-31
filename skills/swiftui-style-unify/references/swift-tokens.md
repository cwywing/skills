# Swift Tokens — the token layer's anatomy

Provenance: one production SwiftUI token layer (9 files, namespace + Color/Typography/Spacing/
Radius/Shadow/Metrics/Motion). Community cross-check: a single namespace type as the entry point
matches common SwiftUI design-system guidance; the primitive → semantic split matches
`h5-style-unify`.

Portable names: `DesignTokens`, `TextStyle`, `.textStyle(_:)`, `TypographyTokens`. Do not copy a
client brand prefix into a new repo.

## File layout (one concern per file)

```
App/Theme/Tokens/
├── DesignTokens.swift      namespace: enum DesignTokens { typealias … }
├── ColorTokens.swift       the ONLY file where Color("AssetName") appears
├── TextStyle.swift         full font object + Dynamic Type policy + catalog
├── TypographyTokens.swift  thin alias so DesignTokens.Typography.* returns style objects
│                           (the shipped template inlines this at the bottom of TextStyle.swift)
├── SpacingTokens.swift     4pt grid, named steps
├── RadiusTokens.swift      named steps (semantic: card/input/pill)
├── ShadowTokens.swift      shadow presets
├── MetricsTokens.swift     icon/control sizes (NOT spacing)
└── MotionTokens.swift      durations + canned Animations (in Theme.swift.tmpl)
```

The namespace entry is deliberately trivial — typealiases only:

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

Views reference `DesignTokens.Metrics.*` — the gate forbids direct `MetricsTokens` references in
the views layer, so the alias is load-bearing.

## ColorTokens — semantics, never asset names

Values live in Asset Catalog colorsets (Any + Dark); the Swift file is a pure semantic index.
Group by intent, mirroring the web SoT's families: brand, app shell, global surfaces, feedback
(paired `*Background` soft colors = H5 status four-piece set).

Ship the **swatch catalog with cross-end references** — each entry may carry the H5 variable name
it was generated from:

```swift
static let catalog: [ColorSwatch] = [
    .init(id: "brandPrimary", name: "Brand Primary", color: brandPrimary, sotVariable: "--color-primary"),
    .init(id: "success",      name: "Success",       color: success,      sotVariable: "--color-success"),
]
```

## TextStyle — typography as a complete object

A font token that carries only a size is half a decision:

```swift
enum DynamicTypePolicy: Sendable {
    case fixed                            // display/hero only
    case relative(Font.TextStyle)         // preferred default
}

struct TextStyle: Sendable {
    let name: String
    let policy: DynamicTypePolicy
    let size: CGFloat
    let weight: Font.Weight
    let design: Font.Design
    let lineHeight: CGFloat
    let tracking: CGFloat
}

extension View {
    func textStyle(_ style: TextStyle) -> some View {
        font(style.font).tracking(style.tracking).lineSpacing(style.lineSpacing)
    }
}
```

- **policy** — Dynamic Type is a per-token decision. `relative` default; `fixed` is documented.
- **lineHeight → lineSpacing** — convert at the token boundary.
- **tracking from em** — `size * -0.025` for headings; keep the em constant beside the catalog.
- **catalog** — a style not in the catalog is not reviewable.

`.font(.system(.body))` (no explicit size) is Apple Dynamic Type and is **allowed** by the gate.
`.font(.system(size:))` is not.

Naming: size-grid names (`display/headline/body/label` × L/M/S) plus purpose names (`caption`,
`price`, `button`). Prefer purpose names in views.

## Motion — port the curve, document the exceptions

```swift
Animation.timingCurve(0.22, 1, 0.36, 1, duration: 0.2)
```

Durations: `fast 0.2` (slightly above typical web 0.15 — the curve is imperceptible under ~0.2s
on press), `normal 0.25`, `shimmer 1.2` linear on purpose (loading loop, not a UI transition).

## Metrics vs Spacing

Spacing = gap between things (4pt grid). Metrics = how big a thing is (`leadingIconSize`,
`thumbnailSize`). Sizing an SF Symbol with a typography token smuggles line-height and tracking
into an image — hence `.symbolSize(DesignTokens.Metrics.*)` and the multiline lint against
`Image(...)` + `.textStyle`.
