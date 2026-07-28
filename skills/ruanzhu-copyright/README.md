# ruanzhu-copyright

中国大陆 **计算机软件著作权登记** 鉴别材料生成 skill（项目级）。版本 **1.5.2**。  
**栈无关**：任意语言/框架；用 `基础资料.md` 配置目录，Phase 2a 手选源码为准。  
**Demo 参考**：`assets/demos/`（只读示意，勿照抄路径）。

## 安装

将整个目录复制到目标项目：

```bash
# Cursor
cp -r ruanzhu-copyright /path/to/project/.cursor/skills/ruanzhu-copyright
```

触发示例：「做软著」「生成程序/文档鉴别材料」「软著登记材料」「导出软著 PDF」。

## 目录

- `SKILL.md` — Agent 编排入口（含硬约束）
- `scripts/` — 提取 / 程序 MD / 脱敏 / Word / **PDF 导出**
- `assets/` — 基础资料模板、文件清单模板、文档 prompt
- `references/` — 分阶段手册、申请表字段、content-redaction、框架适配、提交规则、质量清单

## 快速跑（在仓库根执行）

```bash
python .cursor/skills/ruanzhu-copyright/scripts/extract_codebase_data.py --workdir docs/软著登记申请
python .cursor/skills/ruanzhu-copyright/scripts/generate_program_identification.py --workdir docs/软著登记申请
# 写完 document_identification-*.md 之后：
python .cursor/skills/ruanzhu-copyright/scripts/redact_materials.py --workdir docs/软著登记申请
python .cursor/skills/ruanzhu-copyright/scripts/md2docx.py --workdir docs/软著登记申请
python .cursor/skills/ruanzhu-copyright/scripts/export_identification_pdf.py --workdir docs/软著登记申请
```

`基础资料.md` 后端根目录推荐 `.`；**模板里的语言/框架示例必须改成当前项目真实值**。说明书 **背景→蓝图→流程→模块**；首页须权利人署名三行。

上传用（整本，无全文 PDF）：
- `程序鉴别材料.pdf` — **80～100 页**
- `文档鉴别材料.pdf` — **≥60 页**

## 1.5.x 要点

- 栈无关：配置驱动 + 2a 手选；Phase 1 提取失败可继续
- `assets/demos/`：多栈 config / 选码示意（只读）
- 程序 PDF 整本 80～100 页；文档 PDF 整本 ≥60 页
- 程序段标题：`功能名：相对路径`；禁止标题写「(二开)」
- 禁止另存 `*-全文.pdf`
- 申请表：短字段 ≤50；主要功能 500～1300；技术特点 ≤100；编程语言仅官方列表

## 回归测试

```bash
python .cursor/skills/ruanzhu-copyright/tests/run_tests.py
```

测试夹具仍为迷你前后端样例，仅验证脚本链路，不表示 skill 仅支持该栈。
