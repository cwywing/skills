# Reference — Cursor Agent CLI Pipeline

## Cursor CLI Agent：能力与使用场景

### 是什么

终端里的 Cursor Agent（命令一般是 `agent`）。和 IDE 里的 Agent 同类：能读代码、改文件、跑命令、搜索、按提示完成开发任务。  
支持交互模式，也支持脚本/CI 的无头（非交互）模式。

---

### 核心能力

| 能力 | 说明 |
|------|------|
| 代码理解 | 检索、阅读仓库，回答架构/实现问题 |
| 自动改代码 | 创建、编辑、删除文件 |
| 跑命令 | 构建、测试、脚本等（受本机权限与配置约束） |
| 非交互执行 | `-p` 跑完退出，适合脚本/CI |
| 无人确认写盘 | `-p --force` 直接落盘改文件 |
| 结构化输出 | `--output-format text\|json\|stream-json`，方便脚本解析 |
| 鉴权 | `agent login`，或环境变量 `CURSOR_API_KEY` |
| 可编程调用 | Shell/`subprocess` 调 CLI；也可用官方 Python SDK `cursor-sdk` |

常用命令形态：

```bash
# 交互
agent "实现用户登录接口"

# 只分析、默认不强制写文件
agent -p "这个模块做什么？"

# 脚本自动开发并改文件
agent -p --force "按下列需求实现：..."

# 给脚本吃的 JSON 输出
agent -p --force --output-format json "..."
```

Windows 安装示例：

```powershell
irm 'https://cursor.com/install?win32=true' | iex
agent login
```

---

### 举例使用场景

**1. 夜间批量开发，白天人工验收**  
把多条开发任务写成清单，脚本逐条调用 `agent -p --force "..."`；次日看 diff / 测一遍再合并。

**2. Python / Shell 编排流水线**  
外部系统或脚本传入任务描述 → 调 Agent → 收集 stdout/json 日志 → 进入下一阶段（测试、通知、建分支等）。

**3. CI 自动审查或小修**  
PR 上跑 `agent -p` 做代码审查；或对明确小范围用 `--force` 自动补 JSDoc、修 lint、生成变更说明。

**4. 批量机械性改造**  
对一批文件统一加注释、改 API 风格、补类型注解等重复劳动。

**5. 只问不改（安全预审）**  
先 `agent -p` 要方案/风险分析，确认后再 `--force` 真正改代码。

**6. 本地与云端 Agent（SDK）**  
用 `cursor-sdk`：本地对着工作区跑，或云端隔离环境跑长任务/并行任务。

---

### 最小可跑示例（脚本）

```python
import subprocess

prompt = "实现 GET /health，返回 {\"ok\": true}，并写最短说明"

r = subprocess.run(
    ["agent", "-p", "--force", "--output-format", "text", prompt],
    capture_output=True,
    text=True,
)
print(r.stdout)
```

```bash
export CURSOR_API_KEY=your_key   # CI/无登录环境常用
agent -p --force "Refactor utils to ES modules"
```

---

### 使用时注意

- 无头改文件务必带 `--force`，否则往往只建议不落盘  
- 工作目录决定 Agent 主要改哪里  
- 无人值守建议：独立分支、有日志、人工再验，不要直接合主干  
- 任务写清目标、约束、验收标准，效果明显更好  
- 会消耗 Cursor 用量/额度

---

## Pipeline layout (after install)

```text
.cursor/skills/ai-dev-pipeline/
.pipeline/
  config.yaml
  plans/
  tasks/{pending,active,done,failed}/
  prompts/
  scripts/
  logs/
  examples/
```

## Task YAML

```yaml
id: FE_001
description: "Implement feature X"
acceptance:
  - "file or behavior criterion"
category: feature
complexity: medium
source: plans/sample-plan.md
stages:
  plan: { status: skipped }
  dev: { status: pending }
  verify: { status: pending }
```

## Scripts

| Script | Role |
|--------|------|
| `install.py` | Copy skill + `.pipeline` into target project |
| `run_pipeline.py` | Main loop |
| `parse_plan.py` | MD/YAML → tasks |
| `task_store.py` | Task file IO |
| `agent_runner.py` | `subprocess` wrapper for `agent` |

## Exit codes (`run_pipeline.py`)

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Auth/agent missing or task failures |
| 2 | Missing config / no plans |
| 124 | Agent timeout (recorded in stage log) |
