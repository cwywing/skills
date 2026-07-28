# Changelog

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
