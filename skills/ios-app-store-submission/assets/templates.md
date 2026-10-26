# Copy-ready templates

Fill every `<PLACEHOLDER>`. Keep the shapes stable across projects and versions
— the value of a template is that the next reader knows where to look.

## Project fact sheet (Phase 0 output — paste into the working chat)

```markdown
## 项目事实表 / Project facts
| 项 | 值 | 来源 |
|---|---|---|
| Repo / baseline commit | <repo> @ <sha> | git rev-parse HEAD |
| Bundle ID | <BUNDLE_ID> | project.yml / release map |
| ASC app id | <APP_ID> | asc apps list |
| Version string / versionId | <1.0> / <VERSION_ID> | asc versions list |
| Build number (current → next) | <N> → <N+1> | project.yml CURRENT_PROJECT_VERSION |
| Scheme / project | <SCHEME> / <PROJECT>.xcodeproj | ls *.xcodeproj |
| Team ID / distribution cert | <TEAM_ID> / Apple Distribution: <NAME> | keychain / release map |
| Signing keychain + pass file | <PATH> / <PATH> | build machine notes |
| Internal TestFlight group | <NAME> (<GROUP_ID>) | asc testflight groups list |
| Journal dir | docs/submissions/v<VER>/ | ls docs/submissions |
| Readiness file | <PATH>/review-readiness.json | ls metadata |
```

## timeline.md row (append on every ASC state change)

```markdown
| <YYYY-MM-DD HH:MM> | <event in one clause — what changed, build/version, for whom> | <evidence: asc output id / commit / file> |
```

## submission.md skeleton (new version)

```markdown
# <VERSION> 提审快照

> 状态截至 <DATE> (<ASC STATE>)。提交当天按文末清单重新核对并冻结。

## 1. 身份信息
<!-- app/bundle, app id, version + versionId, attached build + buildId,
     baseline commit, pricing/availability, age rating, release mode,
     TestFlight group -->

## 2. 审核联系方式 (blocker 状态)
<!-- name / phone (+country code) / email — or who owes it -->

## 3. 演示账号 (直接复制)
<!-- credentials block + what data the reviewer should see + no-charge note -->

## 4. 审核备注要点
<!-- six-section summary; 活文档 path is authoritative -->

## 5. 素材位置
<!-- table: video URL / screenshots / privacy draft / demo spec — path + status -->

## 6. 当前 blockers
<!-- table: blocker | 说明 | 解法 | owner -->

## 7. 提交当天动作
<!-- gates: validate 0 blocking, notes frozen copy, human eyeball,
     whatsNew via web, timeline + index rows -->
```

## rejections/<date>-<slug>.md skeleton

```markdown
# <GUIDELINE #> — <one-line summary>

## Apple 原文 (verbatim)
<paste — do not paraphrase, do not trim>

## 解读
<what Apple is actually asking for, in our words>

## 修复方案
<plan; each item lands as a commit — record hashes here as they merge>

## 回复草稿 (给 Apple)
<draf reply in the Resolution Center>
```

## notes.txt six-section skeleton (living document)

```text
1. Screen recording
   <URL or "MISSING — owner: <who>">

2. App purpose, problem, and value
   <one paragraph, plain words>

3. Access instructions and demo credentials
   Username: <demo account>
   Password: <demo password>
   <what data the reviewer will see; account-deletion path — must match the
   published privacy policy; note that no charge can occur>

4. External services
   <payments + guideline citation, analytics, device APIs, outward links>

5. Regional differences
   <e.g. same binary worldwide, no region-specific builds>

6. Regulated industry
   <license/authorization name + where it is attached>
```

## Manifest uploadRecord line (append, never rewrite)

```json
"uploadRecord": "<YYYY-MM-DD>: <what was uploaded/replaced, which sets, result (n/n COMPLETE)> via <exact command>."
```

## Status report (end of any submission task — the deliverable)

```markdown
## 状态报告
<lead: what stands done / what blocks, one sentence>

| Display type / 检查项 | 网页/人话名称 | 数量/状态 | 备注 |
|---|---|---|---|
| ... | ... | ... | ... |

**动过什么**: <mutations this run, or "什么都没动">
**剩余 blocking**: <validate items verbatim, decomposed to human blockers>
**下一步 / owner**: <who owes what, with the deadline if an expiry exists>
```
