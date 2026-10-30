# Changelog

## 1.6.4

桌面端补正实测（图注对得上画面、打码、示意图不乱码、上传体积）：

- 图注只写截图上看得见的状态；打过码就不要写「未做任何加工」
- 窗口标题 / 关于页版本与申请表不一致时，正文写「安装包显示名 / 构建号」，不要把标题栏称作申请表全称
- 截图嵌入前压长边（约 1280）再进 PDF，避免十几张原图把上传稿撑到数十 MB
- 代码围栏示意图若导出后变成点：中文不能整行只用 Consolas；TTC 必须同时指定字体名
- 截图让用户在目标系统上手拍；不要在正在使用的桌面循环拉起 GUI

## 1.6.3

吸纳 `dev.eins1.cn` 侧 1.5.3 可复用口径（不另建第二份手册）：

- 新增 `assets/软件名称说明.template.md`；Phase 0 可出签章草稿
- `基础资料` 增加 `文档类型`、`名称需说明的品牌词`（与 `有人机界面` 必须一致）
- 截图：每图 3～5 句、平台一致、数量参考 15～30 / 3～5；ASCII 不能替代真机图
- **不采纳**：把全部截图只放 `document_identification-5.md` 文末（会让前 30 页没图）；截图目录仍为 `md素材/screenshots/`
- 合入本仓库时去掉 `rejection-hotspots.md` 重复标题

## 1.6.2

本轮补正实测（插图可见 + 只导文档）：

- `md2docx.py --only document|program`：补正只改点名项，避免覆盖未改的程序/文档稿
- Word 占用目标 docx 时另存 `*-重新生成.docx`，并打印插图张数与高度（<1cm 告警细黑线）
- 手册：细黑线成因、同一 PNG 勿三处全贴、界面名称/版本须对上申请表
- 回归：插图单倍行距与 `--only` 不改另一份；测试夹具对齐现行 `基础资料` 占位目录键
- `extract_codebase_data.py`：控制器目录不存在时跳过，不再 listdir 崩溃

## 1.6.1

- `md2docx.py` 插图段改为单倍行距：正文 Normal 固定 13 磅会把嵌入图压成一条线

## 1.6.0

补正实测固化（名称说明 + 运行截图分型）：

- 新增 `references/rejection-hotspots.md`：法规不强制「所有类型都截图」；有人机界面按操作手册必须真机连贯截图；无图形界面走设计说明书、禁止虚构 UI
- 硬约束 14（软件名称专有词 / 《软件名称说明》或商标证）、15（截图分型；不得以「上次没要」为由省略）
- `基础资料` 增加 `有人机界面`；Phase 3 / document_prompt / checklist / submission-rules 同步
- `md2docx.py` 支持 Markdown 图片（`![图注](screenshots/….png)`）

## 1.5.2

本仓库 FastAdmin+CMS 实战沉淀：

- 新增 `assets/demos/fastadmin-cms/`（config + 选码示意；UniApp 原生则 `前端文件: []`）
- **估页 vs 实测**：程序/文档页数以 `export_identification_pdf.py` 为准；脚本 50 行/页估页常偏高；说明书可扩 `-5`～`-7`
- `redact_materials.py`：著作权人替换兼容全角/半角括号变体
- SKILL / core-file-selection / document-generation / submission-rules / demos README 同步

## 1.5.1

- 新增 `assets/demos/`：多栈填表/选码**只读示意**（laravel-uniapp、spring-vue、php-mvc-shop、django-backend-only）
- SKILL / adapters / 选码手册增加「对照 demo、禁止照抄路径」指针

## 1.5.0

栈无关化（skill-authoring 审查）：

- **SKILL / adapters / 选码手册**：不以某一语言或框架为一等公民；强调配置覆盖 + Phase 2a 手选为真源
- **基础资料模板**：示例值改为占位「按实填写」，去掉固定 PHP/Laravel/`mcc_` 暗示
- **申请表 / checklist / workflow / fork 速查**：去掉「本仓库 Laravel」表述；电商 PHP 路径改为通用描述
- Phase 1 明确为辅助清单；提取偏空可继续；脚本注释同步

## 1.4.0

固化本轮登记实务（页数目标、程序段标题、产物清理）：

- **程序鉴别材料.pdf**：整本 **80～100 页**（≥50 行/页）；体量约 4000～6000+ 行
- **文档鉴别材料.pdf**：整本 **≥60 页**（可适当超出）；宜含流程图/时序图等图例
- **禁止**另存 `*-全文.pdf`；`export_identification_pdf.py` 整本导出并清理遗留全文 PDF
- 程序段标题强制 `分类：相对路径`；**禁止**标题写「(二开)」；fork 判定仍排除上游原生
- `core-file-selection` / `fork-detection` / `submission-rules` / `quality-checklist` / SKILL 同步

## 1.3.0

（中间小版本：多栈适配实践沉淀）

## 1.2.0

固化本轮登记实务修正（申请表字数/勾选、首页署名、双 PDF 提交）：

- 新增 `references/application-form-fields.md`（≤50 / 500～1300 / ≤100 / 编程语言列表 / 技术特点标签）
- 程序+文档首页强制 `权利人署名` / `软件名称` / `软件版本号`；脱敏保留署名行
- Phase 4：`export_identification_pdf.py` 导出程序与文档上传 PDF
- 程序宜 ≥50 行/页、文档宜 ≥30 行/页
- 无前端时程序开篇「由后端程序源代码组成」
- 模板 / checklist / submission-rules / workflow / SKILL 同步升版

## 1.1.0

- 说明书结构：背景→蓝图→流程→模块
- 内容脱敏：绝对路径、单位名默认不散落正文
- `redact_materials.py` Phase 4 前置
