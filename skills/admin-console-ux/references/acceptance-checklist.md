# Acceptance checklist

Read when executing step 3 of the workflow or when verifying a page before marking it done. Keep facts here only (not duplicated in SKILL.md). For the "why" and walkthrough script, see [ops-habits.md](ops-habits.md).

## A. Copy & data display

- [ ] Status/enums as locale + colored Tag — never raw English codes
- [ ] Table / stats headers in human language (not API field names)
- [ ] Dates at business precision (`Y-m-d` when time is meaningless; drop `00:00:00`)
- [ ] ID / userid / code in monospace; human name first, technical id on sub-line
- [ ] Cell hierarchy: primary line dark, secondary muted smaller text
- [ ] Empty values show `—` (not blank / `null` / `undefined`)

## B. List infrastructure

- [ ] Page header: title + **total count** + primary CTA
- [ ] Filter bar: status/scope/keyword as needed; 查询 + 重置; each control has a label
- [ ] Default filter favors the ops queue (e.g. 待处理), not 全部 drowning the todo list
- [ ] Changing filters resets to page 1; pagination preserves query params
- [ ] Pagination when growth is plausible (~20/page default unless product defines size); hide pager on single page
- [ ] Empty state with next-step guidance
- [ ] Active filter context visible when deep-linked (e.g. 当前筛选：xxx · 清除)
- [ ] Cross-scope roles: scope column + scope filter; single-scope roles omit redundant scope UI

## C. Actions & feedback

- [ ] Action-column siblings same structure; forms do not participate in visible layout; `topDiff===0` and equal height
- [ ] Paired buttons same shape (both solid or both outline) + identical box model; actions in a stable trailing column
- [ ] Approve/enable: secondary confirm
- [ ] Reject/delete/disable: modal with **operator-written** reason or explicit consequence — no hard-coded reason, no unconfirmed submit
- [ ] Shared success/error alerts; no silent fail
- [ ] Buttons only when actionable; otherwise `—`

## D. Forms & master data

- [ ] List first, then create/edit (or separate edit route); form does not bury the table
- [ ] Header CTA anchors to form or opens create route
- [ ] Required `*`; full-width controls; label above; related fields show preview/linkage
- [ ] Master data is its own module; business docs use selects — no complex entry widgets stuffed into the doc form
- [ ] When prerequisites missing, point to the menu that creates them

## E. Shell & nav

- [ ] One shared nav; current item solid high-contrast + bold white
- [ ] Logout available on every page; brand shows 操作者 · 范围
- [ ] Narrow viewports: wrap or horizontal scroll — do not crush the bar
- [ ] Content max-width ~1200–1280, centered
- [ ] CSS cache bust (`filemtime` / version query)

## F. Walkthrough gate

- [ ] Logged in and opened **every** in-scope nav page (not only the page just edited)
- [ ] Deliverables include `页面 | 结果 | 问题` table
