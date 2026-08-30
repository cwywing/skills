# Pitfalls, Audit Table & Acceptance Checklist

Every item below was observed in a production codebase, not theorized. Read before Phase 6; check
against during Phases 2–5.

## Pitfall list (cross-validated)

| # | Pitfall | How it manifested | Countermeasure |
| --- | --- | --- | --- |
| 1 | **Gate false-green** | design lint silently passed every rule when ripgrep was absent (CI + local Macs) | deps checked up front, fail fast; gate self-test observes an actual failure |
| 2 | **customSyntax top-level** | plain `.css` violations stopped matching while `.vue` still caught — gate looked alive | `postcss-html` only inside `overrides` scoped to `**/*.vue` |
| 3 | **rgba blind spot** | `color-no-hex` green, yet `drop-shadow(… rgba(0,0,0,0.12))` shipped in business code | audit script / CI grep for literal rgba·hsl outside SoT |
| 4 | **Semantic dual-caliber** | "warning text" used `--color-warning` in one file, `--color-warning-text` in another — tokenized but still two colors | one intent → one token; converge during component migration |
| 5 | **Channel/status aliasing** | "approved" badge colored WeChat green `#07c160` (channel) instead of business `success`; fix changed visible pixels | channel colors are their own semantic family, never aliased to status |
| 6 | **Second SoT drift** | a parallel `tokens.js` drifted from `theme.css`; docs tempted to copy color tables | one SoT file; docs are indexes; duplicates get deleted, not synced |
| 7 | **Order violation** | components merged while the gate was untrusted — enforcement came later and retrofitted poorly | gate credible FIRST, then scale the component library |
| 8 | **Day-one strictness** | enabling many lint rules at once drowns history; the gate gets disabled | exactly one rule to start; tighten on a schedule, not on ambition |
| 9 | **Hex museum** | precise variants (`-softer`, `-vivid`, …) accumulated beyond need | each variant carries a "used by" comment; periodic merge audit |
| 10 | **Skeleton components mistaken for adoption** | `AppButton` existed + passed review, zero business usage | acceptance page matrix + per-component adoption counts in the audit table |
| 11 | **Acceptance page in prod** | — (avoided by contract) | dev-only route registration (`import.meta.env.DEV` / DEBUG flag); verify absent from the prod build |
| 12 | **Inline-style escape hatch** | `style="color:#…"` in templates bypasses `<style>`-scoped lint | audit script scans template attributes; custom-property bindings (`:style="{'--i':i}"`) are fine |
| 13 | **Cross-end drift** | native colors edited directly; H5 retheme invisible to iOS | SoT + codegen + CI diff on regenerated artifacts (Mode D) |
| 14 | **Hooks mistaken for enforcement** | pre-commit is local and bypassable | CI is the durable layer; hooks are convenience |

## Migration discipline (Tier-2 batches)

- Migrate per-file, `#hex → var(--*)`, zero intended pixel change; screenshots before/after where
  feasible (page-level, not component-level).
- A batch that intentionally changes visuals (semantic fixes like pitfall 4/5) is its OWN change
  with its own commit message saying the color visibly moves. Never smuggle a visual change inside
  "mechanical refactor".
- Unmigratable leftovers (deadline pressure, third-party CSS) go to the leftovers section with file
  paths — recorded debt, not silent debt.

## Audit table template (drop into the design doc)

```markdown
## 改造审计（诚实记录）

| 阶段 | 内容 | 状态 |
| --- | --- | --- |
| P0 | SoT 收敛（theme.css 重写；删除平行 token 源/死代码） | ✅/⬜ |
| P1 | 语义 token 补全（状态四件套/字号/间距/圆角/动效） | ✅/⬜ |
| P2 | 业务层 hex/rgba 硬编码清零 | ✅/⬜ |
| P3 | 语义组件抽取 + 业务迁移（列出组件 × 已迁页面） | ✅ 主路径 / ⬜ |
| P4 | stylelint 门禁（color-no-hex，error，白名单仅 SoT） | ✅/⬜ |
| P4b | pre-commit 挂钩 + CI（写明是否 fail-closed） | ✅/⬜ |
| P5 | 验收页 + 本文档 | ✅/⬜ |

### 已知遗留（诚实记录）
- <file:line> <what> <why not done> <proposed owner/timeline>
```

Adoption counts make the table honest at a glance (case-study numbers: iOS — 182 `evairTextStyle`
uses, 699 `DesignTokens.` uses, 156 `Evair*` component uses; H5 — 13/13 files consuming `var(--*)`).
Re-count after each migration batch; a component with zero business usage is a skeleton, and the
table must say so.

## Acceptance checklist (final pass)

- [ ] `node scripts/audit-styles.mjs <app-root>` exits 0; before/after counts captured.
- [ ] Gate self-test executed and OBSERVED failing on injected `#abcdef`, then passing.
- [ ] `npm run build` (or platform equivalent) — acceptance route absent from the artifact;
      dev server — acceptance page renders with runtime `var()` values.
- [ ] Every wrapped component appears in the acceptance matrix.
- [ ] Design doc: projection only (no copied color tables), audit table filled, leftovers listed
      with file paths.
- [ ] Visible color changes (if any) listed as a separate deliverable, distinct from the mechanical
      refactor.
- [ ] Dark mode (if in scope): semantic tokens re-assigned in one block; lib bridge verified in
      both themes; no scale-layer fork.
