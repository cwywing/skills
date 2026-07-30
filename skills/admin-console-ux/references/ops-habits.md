# Ops habits (universal)

Read when doing a full-console walkthrough, or when deciding whether a display/interaction matches **operator** habits vs developer convenience.

Design for **ops scanning and clearing work**, not for how the API or ORM looks. Prefer mainstream mid-console patterns (Ant Design Pro / Element Admin–class list+filter+table+pager) over bespoke layouts.

## Walkthrough-derived rules (adopt as universal)

These came from real admin QA (screenshot → fix → browser pass). Keep the rule; drop product-specific nouns when applying elsewhere.

| Ops failure | Universal rule |
|-------------|----------------|
| Status shows `pending` / `waitlist` | Locale label + colored Tag (待审核 / 候补 / 已通过 / 已驳回 …) |
| Screen mixes done + todo | Default filter = actionable queue (待处理); 全部 is explicit |
| Endless scroll of rows | Paginate (~20/page default); hide pager if one page; show total count |
| Reject always "资料不完整" | Modal; operator types reason; then submit |
| Approve with one click, no pause | Secondary `confirm` before submit |
| Global role cannot see which region/tenant | Add scope column + scope filter on cross-scope lists |
| Datetime shows `2026-11-15 00:00:00` | Render at business precision (`Y-m-d` when time unused) |
| Some pages lack nav highlight or logout | One shared chrome; selected state obvious; logout on every page |
| Create form sits above and buries the list | List first; form below or separate route; header CTA to create |
| Stats / column headers in English | Human locale headers everywhere (including aggregate tables) |

## Page walkthrough script

For **each** in-scope admin page after login:

1. **Where am I?** Nav selected state matches route; brand shows operator · scope.
2. **Can I find work?** Default filter, search, reset, empty state, total count.
3. **Can I read the grid?** Locale headers/tags; date precision; title/sub cells; no raw enums.
4. **Can I act safely?** Action column aligned; confirm / reject-reason modal; buttons only when actionable.
5. **Does chrome hold?** No console errors; no accidental horizontal overflow; CSS change visible (cache bust).

Record `页面 | 结果 | 问题` (OK or concrete fail). Do not mark the job done without this table.

## B-end table norms (portable)

Synthesized from common mid-console guidance ([CSDN · B端表格](https://blog.csdn.net/2401_82943878/article/details/137002129), [极客大学 · 表格/列表索引](https://geekdaxue.co/read/yoyo24777@eowzxg/Mu6aK5TI6DCJRsJj), and typical Ant/Element admin practice):

- Treat a list page as **toolbar (filter/search/actions) + table + pager**, not a naked `<table>`.
- Column headers name the business meaning; format cells by type (text / date / id mono / status tag).
- Keep density readable: fewer columns with primary+secondary lines beat many sparse columns.
- Put row actions in a stable trailing column; keep paired actions same shape/metrics.
- Filters that change results reset to page 1; pagination must keep the active query string.
- Offer 重置 when there are multiple filters; show active filter chips/context when deep-linked (e.g. from a stats drill-down).
- Export (CSV/Excel) when ops need offline analysis — place with other list tools, not buried in a random row.

Zhihu mid-console essays (e.g. [zhuanlan.zhihu.com/p/716135232](https://zhuanlan.zhihu.com/p/716135232)) reinforce the same stance: efficiency and scanability for daily operators over decorative UI.

## Contrast — developer convenience vs ops habit

| Developer-shipped | Ops habit |
|-------------------|-----------|
| Enum / status code in the cell | Chinese Tag |
| Default `status=all` | Default todo / actionable set |
| No pager "until we need it" | Pager + total when growth is plausible |
| Hard-coded reject reason | Operator-written reason in modal |
| Form above list (easier for the author) | List first, form second |
| Scope omitted for "simpler markup" | Scope column/filter when role is cross-scope |
| English th: `pending` / `approved` | 待审核 / 已通过 |
