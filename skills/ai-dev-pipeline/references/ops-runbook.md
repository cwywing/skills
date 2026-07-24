# Ops Runbook — 续跑、失败恢复、平台坑（Windows / Mac / Linux）

## 任务状态目录

`.pipeline/tasks/` 下四桶：

| 桶 | 含义 |
|----|------|
| `pending/` | 待处理；流水线从这里取下一条 |
| `active/` | 正在跑（Dev/Verify 中） |
| `done/` | Dev+Verify 通过且（如配置）交付成功 |
| `failed/` | Dev/Verify 耗尽重试，或交付失败且未单独标记 |

`run_pipeline` 启动时会先把 `active/` 清回 `pending/`，避免上次中断遗留。

## 首次跑 vs 续跑

| 场景 | 命令 | 说明 |
|------|------|------|
| 首次导入计划并循环 | `run_pipeline.py --plan <tasks>.yaml` | 解析计划写 `pending/`，再循环 |
| 续跑（不冲状态） | `run_loop.py --no-import` 或 `run_pipeline.py`（不带 `--plan`） | 已有任务则直接循环 |
| 只导入/解析不调 agent | `run_pipeline.py --plan <tasks>.yaml --dry-run` | 验证拆分结果 |
| 只跑一条 | `run_pipeline.py --once` | 冒烟用 |

**续跑不要重导入**：重导入会把已 `done` 的 stage 冲回 `pending`，重烧 agent 额度。
除非用户明确说「reset 任务 / 重头来」，否则一律 `--no-import`。

## 实现 OK 但交付失败

Dev+Verify 已 PASS，却因 `git add` / `checkout` 失败整单标 `failed`，是常见误判。

处理原则：
- 看 `result.delivery.ok`：`false` 但 `result.ok`（impl）为 `true` → 代码可用，仅交付失败。
- 汇报时区分：「实现完成，交付失败：<原因>」。
- 修复交付后可手动把任务从 `failed/` 移回 `pending/` 续跑（脚本会跳过已 done 的 stage），
  或直接在当前分支补 commit。

`run_pipeline` 已在交付前调用 `_cleanup_windows_junk`，并区分 `impl_ok` /
`delivery_ok` 写入任务 `delivery` 字段。

## 看哪些 log

- `.pipeline/logs/<task_id>/dev-attempt<N>.md` — 每次 Dev 的 prompt+stdout+stderr
- `.pipeline/logs/<task_id>/verify-attempt<N>.md` — Verify 同上
- `.pipeline/logs/<task_id>/<stage>-cmd.log` — `verify_command` 的 shell 输出
- `.pipeline/logs/delivery/<task_id>.log` — 交付（git/gh）输出
- `.pipeline/logs/loop-run.log` / `h5-loop-run.log` — 整轮 stdout

## 估时

- simple ~3–5 min/任务；medium ~4–7 min
- Verify 带 build/smoke 再 ×1.2–1.4
- N 任务全 loop ≈ N × 6 min 量级；9 个 medium ≈ 40 min 可接受
- 一次性 agent 啃整站：不可接受（难续跑、验收浅）

## 回合记忆与后续调整（memory / adapt）

每任务 Dev/Verify 结束后（无论成败）会：

1. 写 `.pipeline/memory/<task_id>.md` + `.yaml`，更新 `memory/index.md`
2. **仅 FAIL** 时从 verify/dev notes 抽 gap（PASS 不再扫模板里的 `authz:`/`defaults:` 字段名）
3. 若 `memory.use_agent: true`（且默认 `use_agent_only_on_fail: true`），可再调一轮短 agent 精炼 Gaps
4. 按 `adapt.mode`：
   - `off`：只记忆
   - `suggest`：写 `.pipeline/adaptations/*.yaml` 建议，不改任务（**模板默认**）
   - `apply`：在白名单字段内给匹配的 **pending** 追加 acceptance/description 注记（done/failed/active 不动；有 bak；匹配分 ≥2；DOC 收尾不打 AuthZ）

下一任务的 Dev/Verify prompt 注入截断后的 `{{prior_learnings}}`；`stage_notes` 单段/总量截断，避免 retry 爆 Windows 命令行。

激进可改：`use_agent: true` + `adapt.mode: apply`（慎用）。

## 失败恢复 checklist

1. `dir .pipeline/tasks/{pending,active,done,failed}` 看分布
2. 失败任务看 `logs/<id>/` 最新 attempt 的 `## STDERR` / `## META`
3. 判断是 impl（agent 返回错误/Verify FAIL）还是 delivery（git 失败）
4. impl 失败：修任务描述或代码后，把 `failed/<id>.yaml` 移回 `pending/`，`run_loop.py --no-import`
5. delivery 失败：清 Windows 垃圾 / 修分支后重跑交付，不必重做 Dev/Verify
6. 续跑前确认 `--no-import`，避免重置状态

## 失败归因 triage（重跑前先问：是 harness 还是 agent 的锅）

同一失败持续 2-3 次重试时，**先停下来归因，别盲目重跑烧额度**。按下表自上而下，第一行命中的就是最可能根因，修那一个再继续：

| 你看到的信号 | 可能根因 | 修这个，而不是改模型 |
|---|---|---|
| `command line is too long` / Verify STDOUT 空 | **Harness** — Windows argv 超限 | 确认 `agent_runner` spill；截断 notes/learnings |
| Verify 报 wrong task / smells: implemented other id | **Agent scope** — 跳号 | 加强任务描述；failed→pending 重跑；勿怪 AuthZ 条文 |
| 失败信息具体且每次相同（同错误同位置） | **Harness** — I/O 契约/schema/测试/工具返回错了 | 修契约/测试/工具，别重跑 agent |
| 失败每次漂移（不同错误不同步骤） | **Agent 方差** — 未收敛 | 重跑 1-2 次；仍漂移则收紧任务描述或拆小步骤 |
| Agent"成功"但 Checker 没拦住，或没有 Checker | **Harness** — 缺 ground truth | 先补 Checker 再跑 Maker |
| Agent 反复卡在没有确定性守卫的步骤 | **Harness** — 欠分解（Phase 1/2 债） | 回去拆步骤，别用 prompt 糊过去 |
| 只有这一个 case 失败，兄弟 case 都过 | 两者皆可 — 先重跑该 case 2 次 | 可复现→harness；抖动→agent 方差，加进 eval 当 flake case |

这是**诊断不是门禁**——它不阻塞进度，只为"当你停下来时，为对的原因停"。

## 指定模型

`agent` CLI 支持 `--model <id>`。本 skill 默认在 `config.yaml` 的 `agent.args` 里写死 `cursor-grok-4.5-high`：

```yaml
agent:
  args: ["-p", "--force", "--output-format", "json", "--model", "cursor-grok-4.5-high"]
```

常用可选模型（`agent --list-models` 查全量）：

| Model ID | 适用 |
|---|---|
| `cursor-grok-4.5-high` | **默认**，长上下文 + 强推理，适合 Dev/Plan |
| `composer-2.5` / `composer-2.5-fast` | 通用编码，fast 省额度 |
| `glm-5.2-high` / `glm-5.2-max` | GLM 系 |
| `kimi-k2.7-code` | Kimi 编码 |
| `auto` | 账号默认 |

换模型只改 `config.yaml`，**不要**在 prompt 里塞模型名（会被 agent 当成任务内容）。
参数化模型可带细粒度覆盖：`--model 'claude-opus-4-8[context=1m,effort=high,fast=false]'`。

## 跨平台通用性

本 skill 的所有平台特定逻辑都用 `os.name == "nt"` 守卫隔离，Mac/Linux 上自动走标准路径，**无需任何改动即可使用**。

| 逻辑 | Windows | Mac / Linux |
|------|---------|-------------|
| `agent` 可执行文件 | `agent.cmd`，需 `cmd.exe /c` 包装 | `agent`（无后缀），`shutil.which` 直接执行 |
| `verify_command`（npm 等） | 同上，`npm.cmd` 需包装 | `npm` 直接执行 |
| `_cleanup_windows_junk` | 清 `NUL/CON/PRN/AUX` 保留名 | `os.name != "nt"` 直接 return，跳过 |
| 路径 / 编码 | `pathlib.Path` + `encoding="utf-8"` | 同左，跨平台一致 |
| git / npm 命令 | 跨平台一致 | 跨平台一致 |

所有 `if os.name == "nt"` 分支在 Mac/Linux 上**不触发**，不影响运行。

## Mac / Linux 专属注意事项

### 1. `agent` CLI 安装与 PATH

Mac/Linux 上 `agent` 通常由 npm 全局安装，落在：

- Mac（Homebrew Node）：`/opt/homebrew/bin/agent` 或 `/usr/local/bin/agent`
- Linux（系统 Node）：`/usr/local/bin/agent` 或 `/usr/bin/agent`
- nvm 用户：`~/.nvm/versions/node/<ver>/bin/agent`
- 自定义前缀：`~/.npm-global/bin/agent`

`shutil.which("agent")` 依赖 `PATH`。若 `agent: command not found`，先确认：

```bash
which agent           # 应输出完整路径
npm config get prefix # 看全局安装前缀
echo $PATH            # 确认前缀/bin 在 PATH 里
```

nvm 用户尤其注意：非交互 shell（CI、cron）可能没加载 `nvm.sh`，需在脚本里显式 `source nvm.sh` 或用绝对路径。

### 2. 执行位

npm 全局安装时通常会带执行位，但若手动拷贝过 `agent` 二进制，需确保可执行：

```bash
chmod +x $(which agent)
```

### 3. 无保留设备名问题

Mac/Linux 没有 `NUL`/`CON`/`PRN`/`AUX` 这类保留设备名，`_cleanup_windows_junk` 会自动跳过，`git add -A` 不会因保留名失败。**无需任何手动清理**。

### 4. 端口占用的排查命令不同

```bash
# Mac / Linux
lsof -i :5173        # 找占用 PID
kill -9 <PID>        # 杀掉
# 或直接换端口
npm run dev -- --port 5174
```

### 5. 分支名与文件系统

Mac 默认文件系统（APFS）大小写不敏感，Linux 多数大小写敏感。分支名、任务 ID 一律用 `kebab-case` / 小写，避免跨平台 `git checkout` 时的大小写歧义。本 skill 生成的分支名（如 `pipeline/fix-theme-070`）已遵循此约定。

## Windows 专属坑

### 1. `agent.cmd` / `npm.cmd` 不能裸 subprocess

Windows 上 `agent` 实际是 `agent.cmd`，`subprocess.run(['agent', ...], shell=False)`
会 `FileNotFoundError`。`agent_runner.build_command` 已处理：

```python
if os.name == "nt" and resolved.lower().endswith((".cmd", ".bat")):
    return ["cmd.exe", "/c", resolved, *args, prompt]
```

`run_shell_command`（跑 `verify_command`）同样用 `shutil.which` + `cmd /c`。
**不要**在 Skill 或脚本里手写裸 `subprocess(['agent'/'npm', ...])`。

### 1b. Windows 命令行长度上限（~8191）

把整段 Dev/Verify prompt 挂在 argv 上，超限会直接报 `The command line is too long`
（agent 根本没跑，STDOUT 空）。`agent_runner.prepare_prompt_for_cli`：超安全阈值时
把全文写入 `logs/<task>/agent-prompt-*.md`，argv 只传短指针让 agent `Read` 该文件。

日志 `## META` 含 `prompt_spilled=True` 即走了文件 spill。若仍见 too long，查版本是否未同步脚本。

### 2. 禁止生成保留设备名

Agent 偶尔会写出 `NUL`、`NUL.map`（source map 占位）等 Windows 保留设备名，
`git add -A` 直接报 `exit 128`，整轮交付挂掉。

- `run_pipeline._cleanup_windows_junk` 会在交付前清理 `NUL/CON/PRN/AUX` 等
- `.gitignore` 应含 `NUL` / `NUL.map`
- Dev 提示词已禁伪代码，但若 agent 仍写出保留名，手动删 `\\?\C:\path\NUL`

### 3. 脏工作区 + 已有 `pipeline/*` 分支

每任务独立分支在脏工作区易 `git checkout` 失败（主题/组件类任务尤甚）。

- 多任务同产品优先一条 epic 分支连续 commit
- 或交付失败不回滚代码，仅补 commit
- `.gitignore` 覆盖 `dist/`、`node_modules/`、`*.pyc`、`__pycache__/`

### 4. 端口占用

`vite` 默认 5173 被占时直接报错退出。`npm run dev -- --port 5174` 换端口；
或先 `Get-NetTCPConnection -LocalPort 5173` 找 PID 杀掉。
