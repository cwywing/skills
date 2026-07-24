# AI Dev Pipeline

[中文](README.zh-CN.md)

Cursor Agent CLI skill + runnable pipeline: split a plan into ordered tasks and
continuously deliver via `agent -p --force` (Plan → Dev → Verify by default).

## Install into a project

```bash
# From this skills repo (or after Remote Rule import under .cursor/skills/)
pip install -r skills/ai-dev-pipeline/requirements.txt
python skills/ai-dev-pipeline/scripts/install.py --target /path/to/your-project
```

After install the target project has:

- `.cursor/skills/ai-dev-pipeline/` — Cursor Skill docs
- `.pipeline/` — config, prompts, scripts, tasks, logs

## Usage

```bash
cd /path/to/your-project

# 1) Add a plan (Markdown or YAML task list)
#    .pipeline/plans/your-plan.md

# 2) Auth
agent login
# or: export CURSOR_API_KEY=...

# 3) Run the pipeline
python .pipeline/scripts/run_pipeline.py --plan .pipeline/plans/your-plan.md

# Import/split only — no agent calls
python .pipeline/scripts/run_pipeline.py --plan .pipeline/plans/your-plan.md --dry-run
```

In Cursor chat you can also say: “按 `.pipeline/plans/xxx.md` 跑 AI 开发流水线”
— this skill will load.

## Default stages

Plan → Dev → Verify (add Review / Deploy in `.pipeline/config.yaml` as needed).

Delivery default: `delivery.mode: commit` (feature branch `pipeline/<task_id>`),
optional `pr` / `none`.

## Layout

```text
ai-dev-pipeline/
├── SKILL.md                 # Skill entry (start here)
├── reference.md
├── references/              # Ops runbook, backend security
├── scripts/                 # install / run_pipeline / ...
├── templates/               # config + prompts
├── examples/
└── requirements.txt
```
