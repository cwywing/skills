# AI Dev Pipeline

[English](README.md)

Cursor Agent CLI 技能 + 可运行流水线：把计划拆成有序任务，通过 `agent -p --force`
循环交付（默认 Plan → Dev → Verify）。

## 安装到目标项目

```bash
# 从本 skills 仓（或 Remote Rule 导入后的 .cursor/skills/）
pip install -r skills/ai-dev-pipeline/requirements.txt
python skills/ai-dev-pipeline/scripts/install.py --target /path/to/your-project
```

安装后目标项目包含：

- `.cursor/skills/ai-dev-pipeline/` — Cursor Skill 文档
- `.pipeline/` — 配置、prompts、脚本、tasks、logs

## 使用

```bash
cd /path/to/your-project

# 1) 放入计划（Markdown 或 YAML 任务清单）
#    .pipeline/plans/your-plan.md

# 2) 鉴权
agent login
# 或: export CURSOR_API_KEY=...

# 3) 跑流水线
python .pipeline/scripts/run_pipeline.py --plan .pipeline/plans/your-plan.md

# 只导入/拆分，不调用 agent
python .pipeline/scripts/run_pipeline.py --plan .pipeline/plans/your-plan.md --dry-run
```

在 Cursor 对话中也可直接说：「按 `.pipeline/plans/xxx.md` 跑 AI 开发流水线」——会加载本 Skill。

## 默认阶段

Plan → Dev → Verify（可在 `.pipeline/config.yaml` 增删 Review / Deploy）

交付默认：`delivery.mode: commit`（独立分支 `pipeline/<task_id>`），可选 `pr` / `none`。

## 目录结构

```text
ai-dev-pipeline/
├── SKILL.md                 # Skill 入口（从这里开始）
├── reference.md
├── references/              # 运维手册、后端安全
├── scripts/                 # install / run_pipeline / ...
├── templates/               # config + prompts
├── examples/
└── requirements.txt
```
