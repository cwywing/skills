# Theme Injection & Semantic Components

Provenance: one production SwiftUI `AppTheme` (Environment, ~30 lines) + a dozen components.
Community cross-check: Environment-based theme propagation is the consensus pattern for runtime
theming; the production variant is deliberately minimal.

Portable names: `AppTheme`, `appTheme`, `AppBadge`, `AppButton`, `AppEmptyState`, `AppToggle`,
`AppProgress`. Do not copy a client brand prefix into a new repo.

## AppTheme — injectable, but token-first

The lightest container that still unlocks white-label:

```swift
struct AppTheme: Sendable {
    static let shared = AppTheme()
    var colors: ColorTokens.Type { ColorTokens.self }
    var typography: TypographyTokens.Type { TypographyTokens.self }
}

private struct AppThemeKey: EnvironmentKey {
    static let defaultValue = AppTheme.shared
}
extension EnvironmentValues {
    var appTheme: AppTheme { get { self[AppThemeKey.self] } set { self[AppThemeKey.self] = newValue } }
}
```

Design decisions worth copying:

- **Views still read `DesignTokens.*` directly**; the theme container is plumbing for a FUTURE
  white-label/high-contrast swap. Heavy "every view resolves tokens through the Environment"
  architectures belong to products that actually switch themes at runtime.
- **Screen-root modifier** instead of per-view backgrounds (`appScreenBackground()`).
- `Sendable` from day one — Swift 6 strict concurrency will not negotiate later.

## Component contract

1. **Props are semantic, never chromatic.** A tone enum maps to token PAIRS:

   ```swift
   enum AppBadgeTone: CaseIterable, Sendable {
       case neutral, muted, primary, success, warning, danger, info
       var foreground: Color {
           switch self {
           case .success: DesignTokens.Colors.success
           case .warning: DesignTokens.Colors.warning
           default: DesignTokens.Colors.appText
           }
       }
       var background: Color {
           switch self {
           case .success: DesignTokens.Colors.successBackground
           default: DesignTokens.Colors.appCard
           }
       }
   }
   ```

   The view passes `.success`; the component decides what success means chromatically. This is
   the SwiftUI twin of H5 `AppStatusTag`.

2. **The component consumes only tokens.** If it needs a value the token layer lacks, that value
   becomes a token first.

3. **Interactive state belongs in ButtonStyle.** Pressed / disabled / loading written once.

4. **Layout stays with the caller.** Components own color/typography/interaction.

5. **Accessibility identifiers are a first-class optional param.**

## Component inventory (right-size yours)

Start with the high-frequency four (Button, Card, Badge/Chip, EmptyState), gate adoption, then
grow (Progress, Toggle, TextField, ListRow, Skeleton) on demand. An unused component is invisible
debt. Turn on `audit-swift-styles.sh --components` only after the wrappers exist — otherwise the
gate drowns the repo in ProgressView/Toggle hits and tempts rule deletion.

## Registration contract

Every new component lands in the same change as its acceptance-view section. The DEBUG preview
(`assets/DesignSystemPreviewView.swift.tmpl`) doubles as the registry: if it is not rendered
there, review cannot see it.
