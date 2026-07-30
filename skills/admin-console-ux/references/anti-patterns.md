# Anti-patterns & contrasts

Read when diagnosing a screenshot, reviewing a diff, or teaching why a fix is structural.

## Quick table

| Failure | Symptom | Fix |
|---------|---------|-----|
| Crooked actions | One control inside `<form>`, sibling naked | Same-level nodes + hidden form + JS submit |
| Invisible selected | Opacity / thin underline only | Solid high-contrast fill; remove weak `::after` |
| Looks crooked | Solid + outline mixed in one pair | Same shape; identical box-model metrics |
| Raw DB dump | `pending`, full datetime | Chinese Tag; precision formatting |
| No ops default | Screen flooded with completed rows | Default todo queue + filters |
| Missing list basics | No pagination / filter / empty | Toolbar + empty + pagination |
| Careless danger | Hard-coded reject reason; no confirm | Modal + confirm |
| One-page fix | Other admin pages still crooked | Shared layout + full walkthrough |
| Master data in doc form | Map suggest stuffed into session form | Own module + select |
| CSS cache | "改了看不见" | `filemtime` / version query |
| Wrong aesthetic | Purple gradients / pill stacks | Neutral ops chrome |

## Correct vs Incorrect — more cases

### Default filter

- Incorrect: list defaults to 全部 so approved/rejected bury 待审核.
- Correct: default 待处理 (pending+waitlist or equivalent); 全部 is explicit.
- Rationale: review queues exist to clear work, not to archive-browse.

### Status display

- Incorrect: cell text `waitlist`.
- Correct: blue/orange Tag `候补`.
- Rationale: ops language is Chinese; color encodes triage speed.

### Scope of change

- Incorrect: polish only `reservations` and ship.
- Correct: shared nav/layout + every in-scope list/form, then walkthrough table.
- Rationale: inconsistency across pages is the user-visible failure mode.

### Master data

- Incorrect: embed Amap tips + address fields on every session create form as the only place to manage venues.
- Correct: 培训地点 (or equivalent) CRUD with enable/disable; session form selects `venue_id` and shows a read-only preview.
- Rationale: venue lifecycle ≠ session lifecycle; duplication drifts.

### Cross-scope admin

- Incorrect: global admin sees the same columns as a single-region admin; cannot tell which region a row belongs to.
- Correct: add 区域/租户/组织 column + matching filter on cross-scope lists; hide for single-scope roles.
- Rationale: ops triage needs the dimension they are accountable for.

### List vs form order

- Incorrect: large create form at the top; table of existing rows below the fold.
- Correct: table first; 「新建」CTA scrolls to form or opens edit route.
- Rationale: daily work is mostly review/edit of existing rows, not blank-form entry.

### Hard-coded reject

- Incorrect: `reject_reason = '资料不完整'` with one click.
- Correct: modal textarea; operator writes reason; then confirm submit.
- Rationale: reasons are operational communication to the applicant, not a constant.
