# 工作流分阶段手册（Phase 0～4）

在目标项目中，默认工作目录为 `docs/软著登记申请/`（可通过用户要求改名，但结构不变）。

Skill 根目录记为 `SKILL_ROOT`（通常 `.cursor/skills/ruanzhu-copyright`）。

脚本统一调用方式（**在仓库根目录执行**）：

```bash
python SKILL_ROOT/scripts/<script>.py --workdir docs/软著登记申请
```

---

## Phase 0 — 脚手架与基础资料

1. 创建目录：`docs/软著登记申请/`、`docs/软著登记申请/md素材/`
2. 复制 `assets/基础资料.template.md` → `docs/软著登记申请/基础资料.md`
3. 填写 `# config`：
   - **后端/前端项目根目录优先用相对路径**（仓库根填 `.`）；禁止把本机绝对路径当作说明书素材（见 `content-redaction.md`）
   - 框架类型、表前缀；仅后端则前端根目录留空、`前端框架类型: none`
   - 可选覆盖：`后端模型目录` 等
4. 填写申请表字段：软件全称、版本、**著作权人**、开发完成日期、功能描述、技术特点
   - **必读** `references/application-form-fields.md`（字数、编程语言列表、技术特点标签）
   - **字符限制**：短字段（含开发目的、面向领域）常 **≤50**；主要功能 **500～1300**；技术特点自填 **≤100**（标签可选）
   - **编程语言**：支撑环境下方固定列表勾选；勿填框架名
   - **鉴别材料首页**：程序/文档说明须含权利人署名、软件名称、软件版本号（与申请表一致）
5. **开发完成日期**推荐：若用户未指定，可用 `git log --format=%aI --all` 全部作者日期取**中位数**对应日历日，并在「已确认」表注明依据；用户指定则用用户值
6. 缺字段时**逐项向用户确认**，禁止用「（必填）」占位进入后续阶段
7. `软件的主要功能` 按**业务链路**概括，不要只列无关联的模块名

自检：无「（必填）」；config 非盘符绝对路径；短字段 ≤50；主要功能 500～1300；技术特点 ≤100；编程语言在列表内；首页三行署名已规划。

---

## Phase 0.5 — Python 依赖

需要：`python-docx`、`markdown`、`beautifulsoup4`。

```bash
pip install -r SKILL_ROOT/scripts/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

若 Windows 系统代理（Clash 等）导致 pip 超时，用下方绕过方式：

```python
python -c "
import urllib.request
urllib.request.getproxies = lambda: {}
import pip._internal.network.session as s
orig = s.PipSession.__init__
def patched(self, *a, **kw):
    orig(self, *a, **kw)
    self.trust_env = False
s.PipSession.__init__ = patched
from pip._internal.cli.main import main
import sys
sys.argv = ['pip', 'install', 'python-docx', 'markdown', 'beautifulsoup4',
            '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple',
            '--trusted-host', 'pypi.tuna.tsinghua.edu.cn']
main()
"
```

---

## Phase 1 — 提取 codebase_data.json

```bash
python SKILL_ROOT/scripts/extract_codebase_data.py --workdir docs/软著登记申请
```

输出：`md素材/codebase_data.json`

成功标志：打印模型/控制器/服务/路由/前端统计，且 JSON 文件非空。

任意栈：先按真实仓库改 `基础资料.md` 目录覆盖项；布局与默认回退不符时读 `framework-adapters.md`。Phase 1 摘要偏空时**继续 Phase 2a**，勿因提取失败中止。

注意：提取结果中的注释可能含人名/URL；写入说明书与程序导出前仍须走脱敏。

---

## Phase 2a — 核心文件清单

读 `references/core-file-selection.md`，分析前后端，写出：

`md素材/core_business_files.json`

硬约束见该文件：相对路径、行数区间、后端占比 ≥40%（仅后端时前端可为 `[]`）。

---

## Phase 2b — 程序鉴别材料 MD

```bash
python SKILL_ROOT/scripts/generate_program_identification.py --workdir docs/软著登记申请
```

输出：

- `program_identification-1.md`（前端；无前端时可几乎只有说明头）
- `program_identification-2.md`（后端）

若脚本警告后端占比或总行数异常，回到 2a 调整 JSON 后重跑。

---

## Phase 3 — 文档鉴别材料 MD

1. **必须先读** `references/document-generation.md` 与 `assets/document_prompt.md`
2. 按 **背景 → 蓝图 → 流程 → 模块** 顺序写 `document_identification-*.md`
3. **禁止**模块优先、无总览链路的说明书
4. 遵守 `content-redaction.md`（首页说明含权利人署名三行；其余正文默认无单位全称、无绝对路径）

---

## Phase 4 — 脱敏后合并为 Word / 提交 PDF

**顺序不可颠倒：**

```bash
python SKILL_ROOT/scripts/redact_materials.py --workdir docs/软著登记申请
python SKILL_ROOT/scripts/md2docx.py --workdir docs/软著登记申请
python SKILL_ROOT/scripts/export_identification_pdf.py --workdir docs/软著登记申请
```

输出：

- `md素材/程序鉴别材料.docx` / `文档鉴别材料.docx`
- `md素材/程序鉴别材料.pdf` / `文档鉴别材料.pdf`（**上传用整本**：程序 80～100 页；文档 ≥60 页）
- **勿**生成 `*-全文.pdf`（校对用 Word）

依赖：本机 Microsoft Word（win32com）、PyMuPDF（`fitz`）。兼容旧命令 `export_program_pdf.py`（默认同样导出全部）。

然后执行 `references/quality-checklist.md` 与 `references/submission-rules.md`。

---

## 从旧目录迁移

若项目已有 `docs/07-R11软件著作权登记申请/`，可将 `--workdir` 直接指向该目录（须含 `基础资料.md` + `md素材/`），无需强制改名。

---

## 回归测试

```bash
python SKILL_ROOT/tests/run_tests.py
```

全部 OK 再对外交付/复制。测试使用 `tests/fixtures/mini_*`，不依赖业务仓库。
