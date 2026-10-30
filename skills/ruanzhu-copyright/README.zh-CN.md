# ruanzhu-copyright

[English](README.md)

面向中国大陆**计算机软件著作权登记**的鉴别材料生成 skill（项目级），当前版本 1.6.4。

- 栈无关：任意语言/框架。目录结构写进 `基础资料.md` 配置，Phase 2a 以手选源码为准。
- `assets/demos/` 是多栈参考示例（只读，别照抄里面的路径）。

## 安装

将整个目录复制到目标项目：

```bash
# Cursor
cp -r ruanzhu-copyright /path/to/project/.cursor/skills/ruanzhu-copyright

# Claude Code
cp -r ruanzhu-copyright /path/to/project/.claude/skills/ruanzhu-copyright
```

触发说法：「做软著」「生成程序/文档鉴别材料」「软著登记材料」「导出软著 PDF」「软著补正」。

## 目录

- `SKILL.md` — Agent 编排入口（含硬约束）
- `scripts/` — 提取 / 程序 MD / 脱敏 / Word / PDF 导出
- `assets/` — 基础资料模板、文件清单模板、文档 prompt
- `references/` — 分阶段手册、申请表字段、content-redaction、框架适配、提交规则、质量清单、易驳回补正点

## 快速跑（在目标仓库根目录执行）

```bash
python .cursor/skills/ruanzhu-copyright/scripts/extract_codebase_data.py --workdir docs/软著登记申请
python .cursor/skills/ruanzhu-copyright/scripts/generate_program_identification.py --workdir docs/软著登记申请
# 写完 document_identification-*.md 之后：
python .cursor/skills/ruanzhu-copyright/scripts/redact_materials.py --workdir docs/软著登记申请
python .cursor/skills/ruanzhu-copyright/scripts/md2docx.py --workdir docs/软著登记申请
python .cursor/skills/ruanzhu-copyright/scripts/export_identification_pdf.py --workdir docs/软著登记申请
```

补正只改文档时：

```bash
python .cursor/skills/ruanzhu-copyright/scripts/md2docx.py --workdir docs/软著登记申请 --only document
python .cursor/skills/ruanzhu-copyright/scripts/export_identification_pdf.py --workdir docs/软著登记申请 --only document
```

`基础资料.md` 的后端根目录建议填 `.`；模板里的语言/框架示例必须改成当前项目的真实值。说明书按**背景 → 蓝图 → 流程 → 模块**组织，首页要有权利人署名三行。

上传用（整本，无全文 PDF）：

- `程序鉴别材料.pdf` — 80～100 页
- `文档鉴别材料.pdf` — ≥60 页

## 1.6.x 要点

- 有人机界面必须真机截图；无 UI 走设计说明书，禁止虚构界面（`rejection-hotspots.md`）
- 软件名称专有词：`assets/软件名称说明.template.md` 或商标证
- `文档类型` 与 `有人机界面` 必须一致
- Markdown 图片写成 `![图注](screenshots/….png)`；插图段单倍行距（否则 Word 里会变成细黑线）
- `md2docx` / `export` 支持 `--only document|program`；docx 被占用就另存 `*-重新生成.docx`
- 图注只写这张截图上看得见的内容；打过码就别再写「未做任何加工」
- 窗口标题或关于页版本与申请表不一致时，写「安装包显示名 / 构建号」，别把标题栏称作申请表全称
- 截图先把长边压到 1280 左右再嵌入，免得上传 PDF 膨胀到几十 MB
- 代码围栏里的流程图导出后抽一页检查：汉字别整行只用 Consolas；TTC 字体要同时指定字体名
- 截图在目标系统上手拍；不要在正在使用的桌面上循环拉起窗口自动化

## 1.5.x 要点

- 栈无关：配置驱动 + Phase 2a 手选；Phase 1 提取失败可以继续
- `assets/demos/`：多栈 config / 选码示意（只读）
- 程序 PDF 整本 80～100 页；文档 PDF 整本 ≥60 页
- 程序段标题格式：`功能名：相对路径`；禁止在标题里写「(二开)」
- 禁止另存 `*-全文.pdf`
- 申请表：短字段 ≤50 字；主要功能 500～1300 字；技术特点 ≤100 字；编程语言只认官方列表

## 回归测试

```bash
python .cursor/skills/ruanzhu-copyright/tests/run_tests.py
```

测试夹具仍是一个迷你前后端样例，只用来验证脚本链路，不代表 skill 只支持这个栈。
