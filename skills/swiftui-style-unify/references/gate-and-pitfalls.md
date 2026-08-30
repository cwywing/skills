# Gate, Pitfalls, Audit & External Validation

Provenance: EvairSIM `scripts/lint-design-system.sh` (122 lines, production CI) + the
2026-08-09 audit retro + community cross-checks. The generalized, ready-to-install copy
ships as `scripts/audit-swift-styles.sh` in this skill.

## The MUST-NOT rule set (Features layer)

| Rule (ripgrep pattern) | Remediation message |
| --- | --- |
| `Color\(` | use `DesignTokens.Colors.*` |
| `\.font\(\.system\(` | use `.evairTextStyle(DesignTokens.Typography.*)` |
| `cornerRadius\(\s*[0-9]` | use `DesignTokens.Radius.*` |
| `padding\(\s*[0-9]` / `padding\(\.[a-zA-Z]+,\s*[0-9]` | use `DesignTokens.Spacing.*` |
| `spacing:\s*[0-9]` (incl. `spacing: 0` → `Spacing.none`) | use `DesignTokens.Spacing.*` |
| `\.shadow\(` | use Theme components / `.evairShadow` |
| `frame\((width\|height):\s*[0-9]` / `lineWidth:\s*[0-9]` | use `DesignTokens.Metrics.*` |
| `MetricsTokens` | Features must go through `DesignTokens.Metrics` |
| `ProgressView\(` | use `EvairProgress.page/.circular/.linear` |
| `ContentUnavailableView` | use `EvairEmptyState` |
| `\bToggle\(` | use `EvairToggle` |
| `Color\("` repo-wide, excluding the tokens file | asset names live only in ColorTokens.swift |
| multiline `Image(systemName:…)` + `\.evairTextStyle` (`rg -U`) | size symbols with `.evairSymbolSize(DesignTokens.Metrics.*)` — typography tokens smuggle lineHeight/tracking into images |

Note the last two shapes: repo-wide scoping with per-file exemptions, and MULTILINE
pattern matching (`rg -U`) for an anti-pattern that spans two lines. Both are cheap in
ripgrep and impossible in most linters — that is why this gate is a script, not a
SwiftLint config (though progressive SwiftLint/SwiftFormat in CI is the complementary
half; the case ran both, design rules here, formatting there).

Every rule carries a fix in its message, not just the crime. When you add rules, keep
that bar.

## The false-green lesson (paid for twice)

The original lint ran `rg` without checking it existed. On CI runners and contributor
Macs without ripgrep, every pattern silently matched nothing → the script printed PASS →
the gate was green while enforcing nothing. It shipped that way until the audit retro.

A cousin bug surfaced while generalizing the script for this skill: **ripgrep globs apply
in order with LATER globs taking precedence** — writing `-g '!Tokens.swift' -g '*.swift'`
(exclusion, then include) lets the include silently re-admit the excluded file, and the
rule fires on the very tokens file it was meant to exempt. Always order globs
whitelist-first, exclusion-last, and re-run the gate on a known-clean repo after touching
any glob.

Countermeasures now baked into the shipped script and worth never removing:

```bash
set -euo pipefail
command -v rg >/dev/null 2>&1 || { echo "❌ ripgrep required" >&2; exit 1; }   # fail FAST
```

1. **Dependency check before any rule runs** — missing tooling is an error, never a pass.
2. **`set -euo pipefail`** — a failing subcommand cannot be mistaken for "no matches".
3. **Gate self-test observed**: inject `Color(red: 1, green: 0, blue: 0)` into Features,
   watch the exit code go non-zero, remove it, watch it pass. Perform this on install and
   after ANY gate config change.

The deeper principle: a gate that reports success while doing nothing is worse than no
gate — it launders violations as "checked".

## Acceptance view (DEBUG Design Tab)

Contract from the case: DEBUG-only tab rendering every token family via its `catalog`
array — color swatches (each labeled with its name AND its H5 variable), type specimens
at real Dynamic Type settings, spacing/radius scales, motion presets, and the component
matrix (every component × every tone/variant × interaction state). Production builds
exclude it via `#if DEBUG`-gated registration. New components land with their section in
the same change.

## Audit table template (drop into the design doc)

```markdown
## 改造审计（诚实记录）

| 阶段 | 内容 | 状态 |
| --- | --- | --- |
| P0 | 修 lint 假绿（缺 rg 静默放行）+ 清 Features 违规 | ✅/⬜ |
| P1 | Token 层补全（ColorTokens 语义化 / EvairTextStyle+DynamicType / Metrics/Motion） | ✅/⬜ |
| P2 | 高频组件（Button/Card/Badge/Empty/Skeleton/Progress/Toggle/TextField） | ✅/⬜ |
| P3 | Features 批量替换 + 采纳计数 | ✅/⬜ |
| P4 | 设计 lint 进 CI（fail-closed）+ colorset diff | ✅/⬜ |
| P5 | 验收页 + 文档 + 本审计 | ✅/⬜ |

### 已知遗留
- <file:line> <what> <why not done>
```

Adoption counts that made the case's table honest: 182 `.evairTextStyle` uses, 699
`DesignTokens.` uses, 156 `Evair*` component uses across Features. Re-count per batch and
put the numbers IN the table — a component with zero business usage is a skeleton, and
the table must say so.

## External cross-validation notes (what the wider community agrees with, where it differs)

Agreements (high confidence — independent sources converge with the case):

- Design tokens as single SoT with semantic naming; primitives separated from semantic
  tokens (production-scale token guides; `swift-design-system`'s 3-layer hierarchy).
- ONE namespace type as the entry point (Design Systems Collective's SwiftUI color
  guide prescribes exactly the `DesignTokens` shape).
- Environment-based theme propagation for runtime theming (multiple Swift-6-safe
  articles); Asset-Catalog colorsets for light/dark.
- OKLCH for perceptually-uniform ramps (ColorTokensKit-Swift generates OKLCH/LCH ramps
  for exactly the soft/text/border-family reasons the case's SoT chose them).
- Codegen for multi-platform color delivery (Style Dictionary's iOS formats).

Differences / open choices (state the decision, don't silently inherit):

- Community libraries (SwiftUI-Design-System-Pro, SwiftThemeKit, DesignFoundation) ship
  full component suites and runtime-theme engines. The case deliberately did NOT: minimal
  Environment container, token-first access, components grown on demand. Prefer the
  minimal core unless runtime theme switching is a product requirement.
- Style Dictionary (token JSON SoT) vs live web CSS SoT — see `sync-codegen.md` for the
  decision table.
- SwiftLint vs script gate: community default leans SwiftLint rules; the case uses
  ripgrep scripts because multiline and repo-wide-with-exemption rules don't fit rule
  configs cleanly. Both are defensible; the discipline (fail-closed, self-test,
  fix-in-message) transfers either way.
