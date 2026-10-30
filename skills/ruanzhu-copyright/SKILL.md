---
name: ruanzhu-copyright
description: This skill should be used whenever the user asks to prepare, generate, or improve China software copyright (软著) registration materials — including 程序鉴别材料, 文档鉴别材料, 基础资料, codebase extraction, or Word/PDF export for 软件著作权. Trigger on phrases like "做软著", "生成程序鉴别材料", "文档鉴别材料", "软著登记", "软件著作权", "鉴别材料.docx", "导出软著PDF", "软著补正", "软件名称说明", "缺少软件运行截图", or "帮我出软著源码和说明书". Use it even when the user only says "按软著要求导出代码/说明书" without naming phases — the full Phase 0–4 pipeline (含申请表字数校验与上传 PDF) is the goal. When rewriting the 说明书, always follow background→blueprint→flows→modules (never module-first) and content-redaction rules. For UI software (小程序/APP/Web) embed real running screenshots; for no-UI backends use design-spec diagrams and never invent screens. Works for any language or framework (read framework-adapters when the default extract layout does not match). Do not use for general code review, license compliance (SPDX), or trademark filing.
metadata:
  version: "1.6.4"
---

# 软著鉴别材料生成（ruanzhu-copyright）

把**任意技术栈**的项目变成可提交的软著鉴别材料：配置 →（可选）结构扫描 → 筛选核心源码 → 生成程序/文档 MD → **脱敏** → 合并 Word → **导出上传用 PDF**。本 skill **自带脚本与模板**；复制本目录到目标项目的 `.cursor/skills/ruanzhu-copyright/` 即可复用。

**栈无关原则：** 不把任何语言/框架当作「唯一正确形态」。`基础资料.md` 的目录与框架字段由当前仓库填写；Phase 1 提取脚本仅为辅助清单（默认目录布局可覆盖，解析失败也可继续）；**真正决定材料内容的是 Phase 2a 选出的源码文件**与 Phase 3 说明书。异栈项目先读 `framework-adapters.md`。需要对照「填好的示意」时打开 `assets/demos/`（只读参考，禁止整份照抄路径）。

## When to use / When not

| 使用 | 不使用 |
|------|--------|
| 生成或重跑软著程序/文档鉴别材料（含 PDF） | 普通 Code Review、重构 |
| 填写/校验软著基础资料与申请表字段（字数/勾选） | 开源许可证选型、商标/专利 |
| 从任意前后端栈导出登记用材料 | 仅问「软著要多久/多少钱」的政策闲聊 |

## 产物约定

在目标仓库创建工作目录（默认 `docs/软著登记申请/`；若仓库已有同类目录可直接沿用）：

```
<workdir>/
  基础资料.md
  软件名称说明.md              # 可选：名称含品牌/专名时，用户签章后上传
  md素材/
    codebase_data.json
    core_business_files.json
    program_identification-1.md   # 前端（可仅说明头或空数组）
    program_identification-2.md   # 后端（或主业务侧）
    document_identification-1.md … -4.md（不足 60 页可加 -5～-7）
    screenshots/                  # 有 UI 时真机 PNG
    程序鉴别材料.docx / 文档鉴别材料.docx
    程序鉴别材料.pdf / 文档鉴别材料.pdf   # 上传用（整本；勿另存 *-全文.pdf）
```

`SKILL_ROOT` = 本 skill 安装路径。脚本一律在**仓库根**执行：

```bash
python SKILL_ROOT/scripts/<name>.py --workdir docs/软著登记申请
```

## 执行流程（按序，跳过须有理由）

1. **读手册**：`references/workflow-phases.md`；申请表填字段时读 `application-form-fields.md`。
2. **Phase 0**：复制 `assets/基础资料.template.md`；填 **`文档类型`** 与 **`有人机界面`**（须一致）；名称含品牌/专名时复制 `assets/软件名称说明.template.md`；按**当前项目真实栈**填目录/语言/环境；拿不准字段时可对照 `assets/demos/<相近栈>/config.snippet.md`（只借鉴结构，路径与著作权信息必须改写）；**路径用相对路径**；按字数表填申请表；开发完成日期可用 git 中位数（见 workflow）。禁止「（必填）」残留。
3. **依赖**：`scripts/requirements.txt`（Word PDF 另需本机 Word + `pywin32`；见 workflow）。
4. **Phase 1**：`extract_codebase_data.py`（辅助）。目录或语言与默认布局不符时，先改 `# config` 覆盖项并读 `framework-adapters.md`。扫描结果偏空时**不要卡住**——进入 2a 手选源码。
5. **Phase 2a**：先读 `fork-detection.md`（基于开源框架/插件时强制排除上游原生），再 `core-file-selection.md` → `core_business_files.json`。`分类` 写功能名，**勿**写「(二开)」；程序段标题由脚本输出为 `分类：相对路径`。
6. **Phase 2b**：`generate_program_identification.py`（首页署名三行；段标题含相对路径；按扩展名推断围栏）。初选约 4000～6500 行；**页数以 Phase 4 实测为准**（脚本按 50 行/页估页常偏高）。
7. **Phase 3**：先读 `document-generation.md` + `document_prompt.md` + **`rejection-hotspots.md`**（名称说明、有无 UI 是否强制截图）。按 **背景→蓝图→流程→模块** 写说明书；首页署名三行；遵守 `content-redaction.md`。有人机界面则嵌入真机截图（前 30 页也要有图）；无图形界面则走设计说明书、禁止虚构界面。文档目标 **≥60 页**；MD 估页不准，不足则加 `-5`～`-7` 后重导。
8. **Phase 4**：**先** `redact_materials.py`，**再** `md2docx.py`，**再** `export_identification_pdf.py`。补正只改文档（或只改程序）时两步都加 `--only document` / `--only program`，勿覆盖未点名稿。docx 被占用则用脚本另存的 `*-重新生成.docx`。导完打开抽查插图高度（不能是细黑线）。整本上传 PDF，**不另存** `*-全文.pdf`。程序超 100 / 文档不足 60 时回 2a 或 3 调整后重跑本步。
9. **收尾**：`quality-checklist.md` + `submission-rules.md`。

## 捆绑资源（按需读取）

| 路径 | 何时读 |
|------|--------|
| `references/workflow-phases.md` | 开始全流程 |
| `references/application-form-fields.md` | Phase 0 — **申请表字数/勾选（强制）** |
| `references/content-redaction.md` | Phase 0/3/4 — **路径与单位名（强制）** |
| `references/document-generation.md` | Phase 3 — **说明书结构（强制）** |
| `references/rejection-hotspots.md` | Phase 0/3 / 补正通知 — **文档类型 + 名称说明 + 运行截图（强制）** |
| `assets/软件名称说明.template.md` | 名称含品牌/专名或收到名称补正时 |
| `references/fork-detection.md` | Phase 2a 前 — **基于开源框架/插件时强制** |
| `references/core-file-selection.md` | Phase 2a |
| `references/framework-adapters.md` | 任意栈；默认提取布局不匹配时必读 |
| `references/quality-checklist.md` | 交付前 |
| `references/submission-rules.md` | 程序/文档 PDF 页数与行数 |
| `assets/document_prompt.md` | 写说明书章节清单 |
| `assets/基础资料.template.md` | 初始化配置（空白可写；示例值须按项目改写） |
| `assets/demos/README.md` | 需要栈示意时 — **只读 demo**（含 fastadmin-cms / laravel-uniapp / spring-vue / php-mvc-shop / django-backend-only） |
| `scripts/redact_materials.py` | Phase 4 前强制运行 |
| `scripts/export_identification_pdf.py` | Phase 4 导出上传 PDF |
| `tests/run_tests.py` | 改脚本或新环境回归 |

## 努力程度

- **只改基础资料或重跑成品**：相关 Phase + **必须再跑 redact → md2docx → export PDF**。
- **全新项目全套材料**：完整 0→4；程序 **80～100** / 文档 **≥60**（均以 export 实测为准）。
- **已有 md、只需刷新源码**：2a（如需）→ 2b → redact → 4。
- **异栈 / 提取为空**：缩短 Phase 1；加码 Phase 2a 选码与 Phase 3 基于选中源码撰写。
- **FastAdmin/CMS 类二开**：对照 `assets/demos/fastadmin-cms/` 与 `fork-detection.md`；UniApp 为上游原生时 `前端文件` 置为 `[]`。
- **改说明书结构/去路径**：按 document-generation + content-redaction 重写后重导。
- **页数未达标**：回 2a/3 调整后重跑 Phase 4，不要改脚本硬截页。
- **补正通知（名称 / 缺运行截图）**：只改被点名项；读 `rejection-hotspots.md`；有 UI 缺图则等真机 PNG 再导出，禁止用【缺图】稿或 AI 假界面提交。重导用 `--only document`（或 `--only program`）。

## 示例

**Input：**「给当前仓库生成软著材料（可能无独立前端工程）」

**Output（行为）：** 脚手架 → 基础资料（相对路径、字数校验、著作权人、**按真实栈填环境/语言**）→ 可选提取 → 核心文件（独创业务优先、三次审查）→ 程序 MD（首页署名；段标题=`分类：相对路径`）→ 说明书（背景/蓝图/流程/模块 + 图例 + 首页署名）→ redact → docx → 双 PDF（整本，无全文 PDF）→ 清单。

**Contrast — 说明书结构：**

- Correct：背景痛点 → 端到端蓝图 → 流程（触发/步骤/规则/结果）→ 模块对照表
- Incorrect：按目录/类名堆模块、无总览链路
- Rationale：先连起来才能验收业务；模块只做索引

**Contrast — 程序段标题：**

- Correct：`/* ======= 订单计价服务：src/services/order_pricing.py ======= */`
- Incorrect：`/* ======= 订单计价(二开新增)：order_pricing ======= */`
- Rationale：审查只需相对路径定位；「二开」标签写进正文无必要且易干扰

**Contrast — 单位名：**

- Correct：首页 `权利人署名: 某某有限公司`；正文写「本系统」
- Incorrect：正文各章反复宣传单位全称；或首页署名与申请表不一致
- Rationale：见 `content-redaction.md`

**Contrast — 申请表字数：**

- Correct：开发目的 ≤50；主要功能 500～1300；技术特点自填 ≤100；编程语言仅官方列表项
- Incorrect：开发目的两段长文；把框架名填进「编程语言」
- Rationale：见 `application-form-fields.md`

**Contrast — 技术栈表述：**

- Correct：`基础资料` / 说明书写「本项目实际使用的语言与运行时」；选码按业务特征跨目录
- Incorrect：默认照抄模板里的示例框架/语言，或因提取脚本扫不到就放弃异栈项目
- Rationale：材料应对齐真实仓库；2a 手选不依赖某一框架约定

**Contrast — PDF 产物：**

- Correct：仅 `程序鉴别材料.pdf`（80～100 页整本）+ `文档鉴别材料.pdf`（≥60 页整本）
- Incorrect：另存 `*-全文.pdf`；或程序 PDF 截成前 30+后 30=60 页却把全文另存
- Rationale：本流程约定整本按目标页数交付；校对用 Word 即可

**Contrast — 运行截图：**

- Correct：小程序/APP 交真机连贯截图（登录→主界面→各功能）；纯 API 无界面则设计说明书 + 流程图，不编 UI
- Incorrect：有界面的说明书只写文字布局；或纯后端去截无关网页/Postman 冒充本软件
- Rationale：法规不强制「所有类型都截图」；有人机界面按操作手册审，缺图就会补正。详见 `rejection-hotspots.md`

**Contrast — Word 插图被压扁：**

- Correct：插图段单倍行距；导完抽查图高约 7～17cm；脚本打印 `[插图] N 张，高度 … cm`
- Incorrect：继承正文固定 13 磅行距，图变成细黑线还当缺图重截
- Rationale：图已经嵌进 Word，是排版把高度锁成一行字

**Contrast — 补正重导范围：**

- Correct：`md2docx.py --only document` 再 `export --only document`
- Incorrect：默认全量转换，把未点名的程序.docx 一并覆盖
- Rationale：程序未被点名则不要引入无关 diff；Word 占用时用 `*-重新生成.docx`

**Contrast — 软件名称专有词：**

- Correct：品牌/音译词交盖章《软件名称说明》，或已注册则交商标证
- Incorrect：只在说明书里改一句话；或有商标证却写「尚未注册」
- Rationale：审查要的是「其他相关证明文件」

**Contrast — 估页 vs 实测：**

- Correct：选码约 6000 行 → export 得 92 页 → 定稿；文档 MD 写厚后仍 40 页 → 再加 `-5`～`-7` 重导至 ≥60
- Incorrect：generate 提示「估 122 页」就立刻猛砍到估 80；或只数 MD 行数宣称「已够 60 页」却不跑 export
- Rationale：Word 实际约 55～70 行/页，脚本 50 行/页估页偏高；说明书表格密度也使行数不可靠

## 硬约束（不可推理掉）

1. **说明书结构**：必须「背景 → 蓝图串联 → 流程详解 → 模块后置」；禁止模块优先。
2. **路径**：对外材料禁止本机绝对路径；config 优先相对路径；程序段标题必须含**相对路径**。
3. **单位名**：著作权人在 `基础资料.md`；程序/文档**首页说明**须署权利人全称（与申请表一致）；其余正文默认不重复。
4. **申请表字数**：短字段 ≤50；主要功能 500～1300；技术特点自填 ≤100；编程语言仅官方列表（勿填框架名）。
5. **Phase 4**：必须先 `redact_materials.py` 再 `md2docx.py` 再导出 PDF。补正只改其中一份时必须 `--only`，禁止覆盖未点名稿。
6. **PDF 页数与产物**：程序 **80～100** 页整本；文档 **≥60** 页整本；**禁止**另存 `*-全文.pdf`。
7. **代码质量优先**：独创业务算法/状态机/领域规则优先；同构列表 CRUD、空壳转发、纯路由拼接**靠后少选**。详见 `core-file-selection.md`。
8. **三次审查**：写出 `core_business_files.json` 后，须完成「样板占比 → 业务特征 → 体量比例」至少三轮，**通过后**才跑 generate → redact → Word → PDF。
9. **开源二开筛选**：基于开源框架/插件时必须排除上游原生；**程序正文标题勿标注「(二开)」**。
10. **栈无关**：不以某一语言/框架为前置条件；模板中的示例栈必须按项目改写。
11. **密钥**：不把密钥、生产密码写入任何鉴别材料。
12. **真实性**：不编造代码里不存在的业务模块。
13. **免责**：不声称本 skill 保证审查通过或替代法律意见。
14. **软件名称专有词**：全称含自创品牌、音译或外文标识时，从 `assets/软件名称说明.template.md` 出草稿（含义、取名、不涉及他人名称/商标、申请人签章）或交中国大陆商标注册证。本 skill 不代签章。简称/全称不得混用。详见 `rejection-hotspots.md`。
15. **运行截图分型**：`文档类型` 与 `有人机界面` 必须一致。有人机界面按操作手册，**必须**嵌入真实运行截图；总览图放概述后（前 30 页可见），禁止只堆在 `-5.md` 文末，禁止 ASCII 线框替代真机图，禁止【缺图】稿。无图形界面走设计说明书，禁止虚构操作界面。详见 `rejection-hotspots.md`。
16. **截图说明与平台**：每张图配 3～5 句操作说明；截图平台与申请表运行平台一致；复杂系统约 15～30 张、简单工具至少 3～5 张。
