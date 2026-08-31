# Gate, Pitfalls, Audit & External Validation

Provenance: one production ripgrep design lint + an audit retro (false-green when `rg` was
missing) + a glob-precedence bug found while generalizing the script. The installable copy is
`scripts/audit-swift-styles.sh`.

This file is the **only** place in this skill that stores adoption counts from the production
case (measured 2026-08 while generalizing the gate): 713 `DesignTokens.` uses and 182
`.textStyle` / equivalent typography-modifier uses in the views layer. Do not copy these into
README or SKILL.md.

## The MUST-NOT rule set (views layer)

| Rule (ripgrep pattern) | Remediation |
| --- | --- |
| `Color\(` | `DesignTokens.Colors.*` |
| `\.font\(\.system\(size:` | `.textStyle(DesignTokens.Typography.*)` — `.font(.system(.body))` is allowed |
| `cornerRadius\(\s*[0-9]` | `DesignTokens.Radius.*` |
| `padding\(\s*[0-9]` / `padding\(\.[a-zA-Z]+,\s*[0-9]` | `DesignTokens.Spacing.*` |
| `spacing:\s*[0-9]` | `DesignTokens.Spacing.*` (`spacing: 0` → `Spacing.none`) |
| `\.shadow\(` | Theme components / token shadow modifiers |
| `frame\((width\|height):\s*[0-9]` / `lineWidth:\s*[0-9]` | `DesignTokens.Metrics.*` |
| `MetricsTokens` | go through `DesignTokens.Metrics` |
| `ProgressView\(` / `ContentUnavailableView` / `\bToggle\(` | Theme wrappers — **warn** until `--components` |
| `Color\("` repo-wide, excluding the tokens file | asset names live only in ColorTokens.swift |
| multiline `Image(systemName:…)` + `\.<style-mod>` (`rg -U`) | `.symbolSize(DesignTokens.Metrics.*)` |

The script **aggregates** all hits, then exits 1 if any error-level violation exists. Phase 1
baseline counts depend on that. It does not stop at the first match.

Views directory auto-detect: `Features/` if present, else `App/`, else repo root. `Theme/` and
`*Tokens.swift` are excluded from view-layer rules. Confirm with `--features` when the layout
differs. Missing `Features/` is not a hard failure.

The script is POSIX/macOS-safe (no GNU `xargs -r`). Token-file discovery uses `rg` + `find` in a
`while read` loop.

## The false-green lesson (paid for twice)

The original lint ran `rg` without checking it existed. On CI runners and contributor Macs
without ripgrep, every pattern silently matched nothing → PASS → the gate enforced nothing.

A cousin bug: **ripgrep globs apply in order with LATER globs taking precedence** — writing
`-g '!Tokens.swift' -g '*.swift'` (exclusion, then include) lets the include re-admit the
excluded file. Always include first, exclusion last.

Countermeasures baked into the shipped script:

1. Dependency check before any rule runs — missing tooling is an error, never a pass.
2. `set -euo pipefail`.
3. Gate self-test observed: inject `Color(red: 1, green: 0, blue: 0)`, watch non-zero + printed
   hit, remove, watch pass.

A gate that reports success while doing nothing is worse than no gate.

## Acceptance view (DEBUG)

DEBUG-only tab rendering every token family via its `catalog` — color swatches (name + optional
H5 variable), type specimens, and the component matrix. Production builds exclude it via
`#if DEBUG`. Template: `assets/DesignSystemPreviewView.swift.tmpl`.

## Audit table template

Rows match SKILL.md phases.

```markdown
## 改造审计（诚实记录）

| 阶段 | 内容 | 状态 |
| --- | --- | --- |
| P0 | 探测 views 目录 / Theme / 是否共享 web SoT / rg 是否存在 | ✅/⬜ |
| P1 | 基线审计（全规则计数，非 first-hit） | ✅/⬜ |
| P2 | Token 层（DesignTokens / TextStyle+Dynamic Type / Metrics/Motion） | ✅/⬜ |
| P3 | 门禁进 CI + 自测曾失败 | ✅/⬜ |
| P4 | 视图层机械替换 + 采纳计数 | ✅/⬜ |
| P5 | 高频组件 + DEBUG 验收页；然后 `--components` | ✅/⬜ |
| P6 | 诚实遗留 + colorset diff（若 Mode D） | ✅/⬜ |

### 已知遗留
- <file:line> <what> <why not done>
```

## External cross-validation notes

Agreements (independent sources converge with the case):

- Design tokens as single SoT with semantic naming; primitives separated from semantic tokens.
- ONE namespace type as the entry point.
- Environment-based theme propagation for runtime theming; Asset-Catalog colorsets for light/dark.
- OKLCH for perceptually-uniform ramps when generating palettes.
- Codegen for multi-platform color delivery.

Differences / open choices (state the decision, don't silently inherit):

- Community libraries ship full component suites and runtime-theme engines. Prefer the minimal
  core unless runtime theme switching is a product requirement.
- Style Dictionary (token JSON SoT) vs live web CSS SoT — see `sync-codegen.md`.
- SwiftLint vs script gate: multiline and repo-wide-with-exemption rules fit a script; formatting
  can stay in SwiftLint. Both are defensible; fail-closed + self-test + fix-in-message transfers.
