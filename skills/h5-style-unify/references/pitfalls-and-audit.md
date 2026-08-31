# Pitfalls, Audit Table & Acceptance Checklist

Every item below was observed in a production codebase, not theorized. Read before P6; check
against during P2–P5.

## Pitfall list

| # | Pitfall | How it manifested | Countermeasure |
| --- | --- | --- | --- |
| 1 | **Gate false-green** | lint passed every rule when the tool (ripgrep / misconfigured stylelint) was absent or parsing the wrong syntax | deps checked up front; gate self-test observes an actual failure |
| 2 | **customSyntax top-level** | plain `.css` violations stopped matching while `.vue` still caught | `postcss-html` only inside `overrides` scoped to `**/*.vue` |
| 3 | **rgba blind spot** | `color-no-hex` green, yet `drop-shadow(… rgba(0,0,0,0.12))` shipped | audit script flags literal rgba·hsl outside SoT |
| 4 | **Semantic dual-caliber** | "warning text" used two different tokens in different files | one intent → one token |
| 5 | **Channel/status aliasing** | "approved" badge used a channel green instead of business `success`; fix changed pixels | channel colors are their own family, never aliased to status |
| 6 | **Second SoT drift** | a parallel `tokens.js` drifted from `theme.css` | one SoT file; docs are indexes; duplicates get deleted |
| 7 | **Order violation** | components merged while the gate was untrusted | P3 gate self-test BEFORE P5 components |
| 8 | **Day-one strictness** | many lint rules at once; the gate gets disabled | exactly one rule to start |
| 9 | **Hex museum** | precise variants (`-softer`, `-vivid`) accumulated | each variant carries a "used by" comment |
| 10 | **Skeleton components mistaken for adoption** | `AppButton` existed, zero business usage | acceptance matrix + adoption counts |
| 11 | **Acceptance page in prod** | — (avoided by contract) | `import.meta.env.DEV` / DEBUG; verify absent from prod build |
| 12 | **Inline-style escape hatch** | `style="color:#…"` in templates | audit script scans template attributes |
| 13 | **Tailwind / SFC script escape** | `bg-[#fff]` and `<script> primary: '#fff'` (including multiline object literals) passed stylelint and same-line keyword filters | audit script; SFC script hex is error-level even without a color-ish key on the same line. `querySelector('#fade')` / `getElementById('…')` id strings are exempt (not colors). Other hex-like quoted ids still flag — record as leftover or rename, do not weaken the rule |
| 14 | **SoT-in-Vue missed** | uniapp tokens lived in App.vue; auditor only looked at `.css` | SoT detection includes SFC `<style>` |
| 15 | **Cross-end drift** | native colors edited directly | SoT + codegen + CI diff (Mode D / swiftui skill) |
| 16 | **Hooks mistaken for enforcement** | pre-commit is local and bypassable | CI is the durable layer |
| 17 | **Copied px on the acceptance page** | labels said `12px` while SoT moved | page lists token names only |

## Migration discipline (Tier-2 batches)

- Migrate per-file, `#hex → var(--*)`, zero intended pixel change.
- A batch that intentionally changes visuals is its OWN commit.
- Unmigratable leftovers go to the leftovers section with file paths.

## Audit table template (drop into the design doc)

Rows match SKILL.md phases. Do not invent a second numbering.

```markdown
## 改造审计（诚实记录）

| 阶段 | 内容 | 状态 |
| --- | --- | --- |
| P0 | 技术栈探测；确认 app root | ✅/⬜ |
| P1 | 基线审计（记录 error/warn 计数） | ✅/⬜ |
| P2 | SoT 收敛（theme.css；删除平行 token 源） | ✅/⬜ |
| P3 | 门禁（color-no-hex + 自测曾失败）+ 暂用 staged-only hooks | ✅/⬜ |
| P4 | 消费层 + 业务 hex/rgba 机械替换 | ✅/⬜ |
| P5 | 语义组件 + 验收页（dev-only） | ✅/⬜ |
| P6 | 诚实遗留 + 全量 CI fail-closed | ✅/⬜ |

### 已知遗留
- <file:line> <what> <why not done> <proposed owner/timeline>
```

Re-count after each migration batch. A component with zero business usage is a skeleton; the table
must say so. Do not copy iOS adoption numbers into this H5 table — they live in
`swiftui-style-unify/references/gate-and-pitfalls.md`.

## Acceptance checklist (final pass)

- [ ] `node scripts/audit-styles.mjs <app-root>` exits 0 (or leftovers listed); before/after captured.
- [ ] Gate self-test executed and OBSERVED failing on injected `#abcdef`, then passing.
- [ ] Prod build: acceptance route absent. Dev: page renders with runtime `var()` values, no copied px/hex.
- [ ] Every wrapped component appears in the acceptance matrix.
- [ ] Visible color changes listed as a separate deliverable.
- [ ] Dark mode (if in scope): semantic tokens **and** `*-rgb` re-assigned in one block.
