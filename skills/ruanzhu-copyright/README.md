# ruanzhu-copyright

[中文](README.zh-CN.md)

Generates identification materials for 计算机软件著作权登记 (software copyright
registration in mainland China) as a project-level skill. Version **1.6.4**.

- Stack-agnostic: works with any language/framework. Directory layout is
  configured through `基础资料.md`, and Phase 2a relies on hand-picked source
  files.
- `assets/demos/` holds multi-stack reference examples (read-only; do not copy
  their paths).

## Install

Copy the whole folder into the target project:

```bash
# Cursor
cp -r ruanzhu-copyright /path/to/project/.cursor/skills/ruanzhu-copyright

# Claude Code
cp -r ruanzhu-copyright /path/to/project/.claude/skills/ruanzhu-copyright
```

Trigger phrases: 「做软著」, 「生成程序/文档鉴别材料」, 「软著登记材料」,
「导出软著 PDF」, 「软著补正」.

## Layout

- `SKILL.md` — agent orchestration entry (hard constraints included)
- `scripts/` — extract / program MD / redact / Word / PDF export
- `assets/` — 基础资料 template, file-manifest template, document prompt
- `references/` — phase manuals, application-form fields, content-redaction,
  framework adapters, submission rules, quality checklist, rejection hotspots

## Quick run (from the target repo root)

```bash
python .cursor/skills/ruanzhu-copyright/scripts/extract_codebase_data.py --workdir docs/软著登记申请
python .cursor/skills/ruanzhu-copyright/scripts/generate_program_identification.py --workdir docs/软著登记申请
# after writing document_identification-*.md:
python .cursor/skills/ruanzhu-copyright/scripts/redact_materials.py --workdir docs/软著登记申请
python .cursor/skills/ruanzhu-copyright/scripts/md2docx.py --workdir docs/软著登记申请
python .cursor/skills/ruanzhu-copyright/scripts/export_identification_pdf.py --workdir docs/软著登记申请
```

When a correction (补正) touches only the document pack:

```bash
python .cursor/skills/ruanzhu-copyright/scripts/md2docx.py --workdir docs/软著登记申请 --only document
python .cursor/skills/ruanzhu-copyright/scripts/export_identification_pdf.py --workdir docs/软著登记申请 --only document
```

In `基础资料.md`, set the backend root to `.` unless you have a reason not to.
The language/framework examples in the templates must be replaced with the
project's real values. The manual follows 背景 → 蓝图 → 流程 → 模块 (background
→ blueprint → flow → modules); the first page carries the three-line 权利人
(copyright holder) signature.

Upload volumes (whole PDFs, no full-text appendix):

- `程序鉴别材料.pdf` — 80–100 pages
- `文档鉴别材料.pdf` — ≥60 pages

## 1.6.x notes

- Apps with a UI must use real-device screenshots; UI-less apps go through the
  design manual, and invented interfaces are forbidden (`rejection-hotspots.md`)
- Distinctive terms in the software name: `assets/软件名称说明.template.md` or a
  trademark certificate
- `文档类型` and `有人机界面` must agree with each other
- Markdown images as `![图注](screenshots/….png)`; single line spacing on image
  paragraphs (otherwise Word renders a thin black line)
- `md2docx` / `export` accept `--only document|program`; if the docx is locked,
  save as `*-重新生成.docx`
- Captions describe only what is visible in that screenshot; once redacted,
  never claim 「未做任何加工」 (no processing)
- If the window title or About-page version differs from the application form,
  write the installer display name / build number — don't call the title bar by
  the form's full name
- Compress screenshots to ~1280 on the long edge before embedding, or the
  upload PDF balloons to tens of MB
- For flowcharts inside code fences, spot-check one exported page: don't set
  whole Chinese lines in Consolas alone; with TTC fonts, specify the font name
  as well
- Capture screenshots by hand on the target system; don't loop window
  automation on a desktop you are actively using

## 1.5.x notes

- Stack-agnostic: config-driven + Phase 2a hand-picking; a Phase 1 extraction
  failure does not block the run
- `assets/demos/`: multi-stack config / code-selection examples (read-only)
- Program PDF 80–100 pages as a whole volume; document PDF ≥60 pages
- Program section titles follow `功能名：相对路径`; never write 「(二开)」 in a title
- Never save `*-全文.pdf`
- Application form: short fields ≤50 chars; 主要功能 500–1300; 技术特点 ≤100;
  programming languages from the official list only

## Regression tests

```bash
python .cursor/skills/ruanzhu-copyright/tests/run_tests.py
```

The fixtures are still a miniature front/back-end sample; they verify the
script chain only, not a claim that the skill supports only that stack.
