# Source grounding — hard gate (源事实硬闸门)

Read at **Step 2** (build the fact ledger) and **Step 6** (re-check the draft).
This gate outranks completeness, GEO structure, FAQ coverage, and “entity
definition polish.” A thin, sourced article ships; a fluent article with
invented specs does **not**.

CPA / 官网 / 商城发文尤其适用：读者会把正文当官方口径。

## Allowed sources (only these)

For a given article, facts may come **only** from:

1. User-supplied brief text (verbatim claims they typed)
2. Fetched source files in the material folder: `transcript.md`, WeChat
   `#js_content`, `sources.md` quotes, on-screen captions recorded from frames
3. Platform metadata: Douyin `metadata.json` `published_at` / `create_time`;
   WeChat `create_time`
4. A named **independent** authority the user attached (report, filing) with a
   location

**Not allowed** (do not “helpfully” fill gaps):

- Official mall / website product pages (e.g. eins1.cn) unless that URL is in
  `sources.md` as a fetched source
- Search snippets, other news, “brand common knowledge”
- Invented FAQ answers, typical use-cases, SKU lists, prices, dates, headcount
- CTA extras: 在线客服、批量报价、集成商/渠道 — unless the source said so

If GEO needs an entity one-liner and the source never defines the product
beyond its name + tags, **restate only those words**. Do not upgrade tags into
a product taxonomy the source did not state.

## Fact ledger (required)

In `geo-metadata.json` (CPA sidecar) or the delivery note, list every concrete
claim in the **publishable body**:

```json
"fact_ledger": [
  {
    "claim": "最高降幅约 49%",
    "source": "transcript.md 口播",
    "status": "sourced"
  },
  {
    "claim": "适用于钢管框架",
    "status": "cut",
    "reason": "源未出现"
  }
]
```

`status` is only `sourced` | `cut` | `UNVERIFIED`.

- **sourced** — location is specific enough to jump back (file + heading / line
  / 口播句 / 画面字幕).
- **UNVERIFIED** — user insisted it stay; it must **not** appear in
  `article-geo.md`. Put it only in the delivery note.
- **cut** — removed from the body.

**High hallucination risk** = any body sentence with a number, name, scope,
price, date, or capability that is not `sourced`. **Do not ship.**

## Body vs audit

- `article-geo.md`: only `sourced` claims (+ allowed restatement of canonical
  names already in the source).
- `sources.md` / `geo-metadata.json`: IDs, paths, UNVERIFIED, press_id.

Do not put `UNVERIFIED` / Whisper / 抽帧路径 in the reader-facing body.

## FAQ / scenes / comparisons

Each FAQ answer and each “typical scene” bullet is a claim. If the source does
not support the answer, **drop the FAQ item** — do not invent a plausible
answer to look complete.

## Publish archive fields (CPA)

After a successful publish, append to `sources.md` (do not invent IDs):

```text
## 发布留档
- 渠道：opencart | tpadmin
- 站点：eins1.cn | starseiki.cn
- remote_id / press_id / archives.id：…
- 前台 URL：…
- 发布任务：data/tasks.json publishLog id=…
```

Copy `transcript.md` (or WeChat `source.html` + 正文摘录) **into**
`materials/<slug>/`, not only `storage/<task-id>/`.
