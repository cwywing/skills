---
name: admin-console-ux
description: >-
  This skill should be used whenever polishing, unifying, or fixing the UX and
  styling of an admin / backoffice / 管理后台 console (list pages, forms, review
  queues, nav chrome) so display and interaction match mainstream mid-console
  ops habits — not developer-invented chrome. It enforces shared layout,
  geometrically aligned action columns, high-contrast nav selected state,
  todo-first filters, locale status tags, confirms/modals, design-system glue
  CSS only, and a mandatory every-page browser walkthrough table. Trigger on
  phrases like "优化管理后台", "后台样式/交互", "admin UI 统一", "操作列歪了",
  "导航选中看不清", "按钮对不齐", "修 AI 生成的后台", "按运营习惯过一遍",
  "按 Ant Design / Element 改后台", or when the user pastes an admin screenshot
  and asks to make it look like a real ops console. Use it even when the user
  only says "把后台弄好看点" or "对齐一下后台" without naming Ant Design —
  operational consistency is the goal. Do not use for consumer H5, marketing
  landings, or brand-differentiated consumer UI.
metadata:
  version: "1.3.0"
---

# Admin Console UX（中后台交互与样式）

Goal: **interaction and display match mid-console ops habits**, verified page-by-page in a real browser — not "looks vaguely like Ant Design," and not developer-invented chrome.

Audience is **operators / reviewers / dispatchers**. Ship what they scan and clear work with (Chinese labels, todo-first queues, confirm danger, obvious where-am-I). Do not ship API field names, English enums, or engineer-convenient defaults.

## When to use / when not

| Use | Do not use |
|-----|------------|
| Admin list / form / review / nav polish | Consumer H5 or marketing landing |
| "按钮歪了 / 选中态看不见 / 后台不统一" | Brand-differentiated consumer visual experiments |
| Unifying Blade/Vue admin onto Ant / Element / Naive / Arco | Inventing a second parallel CSS system for "好看" |
| Full ops walkthrough to match mainstream mid-console habits | Pixel-perfect brand marketing polish |

## Before coding — scope gate

1. Restate the scope in one sentence.
2. If unclear whether this is **master-data split** vs **style/structure-only**, ask once, then proceed.
3. List **admin pages in scope** + **UI stack to align to** (prefer the project's existing design system).
4. Note **role scopes** (e.g. regional vs global admin) — global views need scope columns/filters; regional views usually hide them.

### Effort calibration

| Scope | Do |
|-------|----|
| One page / one screenshot bug | Fix that page's structure + CSS; still check nav selected state on that route; short walkthrough of touched pages only |
| "后台整体优化" / multi-page / "按运营习惯过一遍" | Shared layout first, then **every** list/form page, then full walkthrough table (login → each nav item) |
| Mentions 地点/分类/仓库 + 表单很重 | Treat as possible master-data split; confirm before extracting modules |

## Non-negotiables (bright lines)

These fail the job if skipped — each has a short why.

1. **Structure before paint on action columns.**  
   Same-level clickable nodes (`button`/`a`) inside one flex row. A visible button wrapped in `<form>` next to a naked `<button>` is the #1 cause of "歪斜." Hide the form and `submit()` from the visible button, or keep forms out of layout. Verify with `getBoundingClientRect()`: sibling `topDiff === 0` and equal `height`. Eyes alone lie.

2. **Nav selected state must read in one glance.**  
   On dark headers use a solid high-contrast fill (e.g. `#1890ff`) + bold white text. Kill weak framework hints (barely-visible `::after` underlines). After each page load, selected label matches the route and background is not transparent.

3. **Paired actions share box model and shape.**  
   Same height / font-size / padding / border-width / `box-sizing` / radius. Prefer both solid or both outline for 通过/驳回、编辑/删除 — mixing solid+outline creates a false "crooked" look even when metrics match. Color carries semantics; metrics stay identical.

4. **Browser walkthrough is mandatory — every in-scope page.**  
   Code review does not catch alignment, overflow, dead selected states, or ops-hostile copy. Login once, then open **each** nav destination (lists and forms). Check display + interaction against [references/ops-habits.md](references/ops-habits.md). Output the walkthrough table in Deliverables.

5. **No secrets in front-end or repo.**  
   Third-party keys (maps, etc.) only via server-side proxy.

## Workflow

```
Admin Console UX:
- [ ] 0. Scope gate (restate; master-data vs style-only)
- [ ] 1. Inventory admin routes/pages in scope
- [ ] 2. Align UI stack; extract shared layout + high-contrast nav
- [ ] 3. Fix pages: structure (action columns) → glue CSS → list/form patterns
- [ ] 4. Browser walkthrough (+ rect check on action columns)
- [ ] 5. Emit deliverables template below
```

Read on demand:

- Ops habits (walkthrough-derived + B-end table norms) → [references/ops-habits.md](references/ops-habits.md)
- Full acceptance checklist → [references/acceptance-checklist.md](references/acceptance-checklist.md)
- Anti-pattern table + Correct/Incorrect → [references/anti-patterns.md](references/anti-patterns.md)

## Working rules (with why)

- Prefer the project's design system class names; glue CSS only for layout gaps. A second visual system drifts page-by-page. Align to mainstream mid-console patterns (Ant Design Pro / Element Admin–class), not a one-off invention.
- Share one layout (header, content width ~1200–1280, table density, form spacing). Per-page copied chrome is how "one page fixed, others still crooked" happens.
- Bust CSS cache in dev (`filemtime` or query version) so "改了看不见" does not waste a cycle.
- Tool aesthetic: neutral gray canvas (e.g. `#f0f2f5`), default primary. Marketing cards, purple gradients, heavy shadows, pill stacks fight ops scanning.
- Master data (venues, categories, warehouses) as its own enabled/disabled module; business forms use selects + server snapshot. Stuffing map-suggest / complex address entry into the document form couples the wrong lifecycle.
- Prefer select over free text; prefer auto-generated links over paste-the-URL fields.
- **List page anatomy (ops default):** page header (title + **total count** + primary CTA) → filter/search toolbar (查询 + 重置) → table (human column headers; title/sub cells; Chinese status Tags; actions on the right) → pagination. Keep columns lean — primary line + muted sub-line beats stuffing extra columns.
- **Todo-first defaults:** review/work queues default to the actionable set (e.g. 待处理 = pending+waitlist), not 全部. Changing filters resets to page 1 and preserves other query params across pagination.
- **Pagination:** when rows can grow, paginate (default ~20/page unless the product already defines a size). Hide pager when only one page. Prefer showing **total row count** near the title or pager — ops care about volume more than "page 3 of N" alone.
- **Role-aware columns:** if the signed-in role can see multiple scopes (region / tenant / org), add that dimension as a column **and** a filter on cross-scope lists. Single-scope roles omit the redundant column.
- **Human language everywhere:** status values, table headers, filter labels, empty states — Chinese (or the product locale). Never leave English enum codes or raw API keys as the only label.
- **Dates/times at business precision:** date-only fields render `Y-m-d`; drop meaningless `00:00:00`.
- Destructive flows: confirm for approve/enable; modal + **operator-written reason** for reject/delete/disable. Hard-coded reject copy and silent fails burn trust.
- List before create/edit form on the same page (or separate edit route) so the form does not bury the queue; primary CTA can anchor to `#form` or open a dedicated route.
- Buttons use verbs: 查询 / 重置 / 通过 / 驳回 / 新建 / 保存.

## Contrast — action column structure

**Incorrect** (looks crooked; form participates in layout):

```html
<td>
  <form method="post">...<button>通过</button></form>
  <button type="button">驳回</button>
</td>
```

**Correct** (siblings in one flex row; form hidden):

```html
<td class="admin-actions">
  <div class="admin-action-btns">
    <form id="approve-1" method="post" hidden>...</form>
    <button type="button" data-approve-id="1">通过</button>
    <button type="button" data-reject-open>驳回</button>
  </div>
</td>
```

Rationale: mismatched ancestors change baseline/height; CSS cannot reliably paper over that.

## Contrast — nav selected state

- Correct: selected item solid `#1890ff`, white bold label, no reliance on `::after` underline.
- Incorrect: only opacity change or 2px bottom border on dark header.
- Rationale: ops users glance at chrome; weak hints read as "not selected."

## Deliverables (exact shape)

Emit this structure when done:

```markdown
## Deliverables
### Pages / files touched
- path/…

### Action-column structure (1–2 sentences)
…

### Nav selected-state CSS (key rules)
…

### Browser walkthrough
| 页面 | 结果 | 问题 |
|------|------|------|
| … | OK / FAIL | … or OK |

### Not done / risks
- migration / env / out-of-scope …
```

If walkthrough was skipped, say so explicitly under the table — do not imply OK.
