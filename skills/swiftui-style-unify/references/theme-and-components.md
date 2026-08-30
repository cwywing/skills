# Theme Injection & Semantic Components

Provenance: EvairSIM `EvairTheme.swift` (36 lines) + `App/Theme/Components/` (12
components). Community cross-check: Environment-based theme propagation is the consensus
pattern for runtime theming in SwiftUI (production-scale token guides, Swift 6-safe
runtime-theming articles); EvairSIM's variant is deliberately minimal.

## EvairTheme — injectable, but token-first

The case chose the lightest container that still unlocks white-label:

```swift
struct EvairTheme: Sendable {
    static let shared = EvairTheme()
    var colors: ColorTokens.Type { ColorTokens.self }
    var typography: TypographyTokens.Type { TypographyTokens.self }
    // …one line per token family
}

private struct EvairThemeKey: EnvironmentKey {
    static let defaultValue = EvairTheme.shared
}
extension EnvironmentValues {
    var evairTheme: EvairTheme { get { self[EvairThemeKey.self] } set { self[EvairThemeKey.self] = newValue } }
}
```

Design decisions worth copying:

- **Feature code still reads `DesignTokens.*` directly**; the theme container is
  plumbing for a FUTURE white-label/high-contrast swap, not an extra indirection every
  view pays for today. Heavy "every view resolves tokens through the Environment"
  architectures are what the community articles describe for runtime-theme-switching
  products — adopt that only when runtime switching is a real requirement.
- **Screen-root modifier** instead of per-view backgrounds:

  ```swift
  extension View {
      func evairScreenBackground() -> some View {
          background(DesignTokens.Colors.appBackground.ignoresSafeArea())
              .foregroundStyle(DesignTokens.Colors.appText)
      }
  }
  ```

  One modifier encodes "a screen root looks like THIS" — background + default foreground
  in one call, impossible to half-apply.

- `Sendable` from day one — Swift 6 strict concurrency will not negotiate later.

## Component contract (all 12 follow it)

1. **Props are semantic, never chromatic.** A tone enum maps to token PAIRS:

   ```swift
   enum EvairBadgeTone: CaseIterable, Sendable {
       case neutral, muted, primary, success, warning, danger, info
       var foreground: Color {
           switch self {
           case .success: DesignTokens.Colors.success
           case .warning: DesignTokens.Colors.warning   // …
           }
       }
       var background: Color {
           switch self {
           case .success: DesignTokens.Colors.successBackground   // the paired soft color
           // …
           }
       }
   }
   ```

   Feature passes `.success`; the component decides what success means chromatically.
   This is the SwiftUI twin of the H5 `AppStatusTag` tone × variant table.

2. **The component consumes only tokens.** Inside `EvairBadge`: `.evairTextStyle(
   Typography.labelSmall)`, `.padding(.horizontal, Spacing.xs)`, `Capsule()` — zero raw
   values. If a component needs a value the token layer lacks, that value becomes a token
   first.

3. **Interactive state belongs in ButtonStyle.** `EvairButtonStyle` (normal / pressed /
   disabled / loading) so state visuals are written once; Feature buttons choose a style,
   never re-implement pressed effects. Same for `EvairTextField`'s focus ring.

4. **Layout stays with the caller.** Components own color/typography/interaction; sizing
   and positioning come from the call site (or Metrics tokens) — mirrors the H5 contract
   "component owns color, caller owns layout".

5. **Accessibility identifiers are a first-class optional param**, not an afterthought
   bolted on by callers reaching into internals.

## Component inventory (right-size yours)

The case shipped 12: Button/ButtonStyle, Card, Badge, Chip, EmptyState, Skeleton,
Progress, Toggle, TextField, ListRow, SymbolStyle (+ helpers). The audit retro is
explicit that the count was NOT the goal — mechanism gaps (gate credibility, reuse,
adoption measurement) were. Start with the high-frequency four (Button, Card,
Badge/Chip, EmptyState), gate adoption, then grow on demand; an unused component is
invisible debt.

## Registration contract

Every new component lands in the same change as its acceptance-view section (swatches,
style list, component matrix with all variants × states). The acceptance view doubles as
the component registry: if it is not rendered there, review cannot see it — and the
per-family `catalog` arrays are what the view iterates, so registration is usually one
line.
