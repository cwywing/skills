---
name: ai-dev-pipeline
description: >-
  This skill should be used whenever the user wants to install, run, resume, or
  debug a Cursor Agent CLI AI development pipeline that splits a plan into
  ordered tasks and continuously delivers via `agent -p --force` (Plan → Dev →
  Verify by default). Trigger on phrases like "跑 pipeline", "按计划持续交付",
  "用 agent cli 编排任务", "install ai-dev-pipeline", "续跑流水线",
  "用流水线自动开发", or "不要一次 agent 做完全部". Use it even when the
  user only pastes a PRD and says "帮我自动开发" without naming the pipeline —
  multi-task orchestration is still the goal. Do not use for one-shot IDE chat
  edits with no task queue, or for Cursor SDK cloud agents unless they ask to
  wire the CLI pipeline.
metadata:
  version: "0.2.0"
---

# AI Dev Pipeline（Cursor Agent CLI）

把一份计划拆成**多条小任务**，通过可安装的 `.pipeline/` 脚本与 Cursor CLI
循环交付——而不是一次 `agent` 啃整站 PRD。

## 何时用 / 何时不用

**用：**
- 把流水线安装进目标仓库
- 把 Markdown/YAML 计划变成有序任务并循环 Dev→Verify→交付
- 失败后续跑、或汇报 done/failed/日志供人工验收

**不用：**
- 用户只想在对话里改一处代码、没有任务队列
- 只问 Cursor SDK / 云端 agent（除非要接本 CLI 流水线）
- 要求合并 main / force-push（拒绝；只走 feature 分支）

## 前置条件

- `agent` 在 PATH；`agent login` 或 `CURSOR_API_KEY`
- Python 3.8+ 与 PyYAML
- 源包：本仓 `skills/ai-dev-pipeline/` 或既有安装

## 工作流

复制并跟踪：

```text
Pipeline Progress:
- [ ] 1. 未安装则安装
- [ ] 2. 写/定位计划（优先带 order 的 YAML 任务）
- [ ] 3. 开跑前自检
- [ ] 4. 运行或续跑循环
- [ ] 5. 汇报 + 人工验收点
```

### 1. 安装

```bash
python <ai-dev-pipeline>/scripts/install.py --target <project-root>
```

生成 `.cursor/skills/ai-dev-pipeline/` 与 `.pipeline/`。

### 2. 计划 → 任务

优先结构化 YAML；Markdown 仅作输入，Plan 阶段必须产出带 `order` 的任务。

默认依赖分档（`order` 越小越先）：

| order | 层 |
|------:|---|
| 10–19 | 数据 / Store / 工具函数 |
| 20–29 | 主题 / 设计系统 |
| 30–39 | 共享组件 |
| 40–49 | 页面 |
| 50–59 | 路由 / 种子 / 联调 |
| 60+   | QA 脚本 / 还债 |

每条任务需：唯一 `id`、`order`、可检查的 `acceptance`、可选 `platform`、可选
`verify_command`。

### 3. 开跑前自检（逐条 yes/no）

1. 每个 pending 任务都有 `order`？
2. 是首次跑（导入计划）还是续跑（`--no-import` / 不再传 `--plan`）？
3. 行为类任务有 `verify_command`，或写明为什么没有？
4. `.gitignore` 覆盖 `dist/`、`node_modules/`，且不会提交 Windows 保留名垃圾？
5. 交付模式清楚（默认 `commit` → feature 分支，绝不 main）？
6. **覆盖度三必做**：读写闭环 / 异常流程 / DOC 收尾任务都齐了？缺则先补再跑。

(1)(2) 不满足则先修，再调 agent。

### 4. 运行 / 续跑

**首次导入并循环：**

```bash
python .pipeline/scripts/run_pipeline.py --plan .pipeline/plans/<tasks>.yaml
```

**续跑（不要重导入，否则会冲掉 stage 状态、白烧额度）：**

```bash
python .pipeline/run_loop.py --no-import
# 或任务已存在时：run_pipeline.py 不带 --plan
```

Flags：`--once`（单任务）、`--dry-run`（仅导入/解析）。

按难度校准：1 个冒烟任务 → `--once`；整份 PRD → 全 loop；估时
约 3–7 分钟/任务 × 阶段数（Verify 带 build 约 ×1.2–1.4）。

### 5. 汇报

告诉用户：done/failed 数量、失败是**实现**还是**交付**、分支与 commit、
`.pipeline/logs/<task_id>/`、剩余人工验收项。

## 硬约束（不可协商）

- 通过 `install.py` / `run_pipeline.py`（或项目 `run_loop.py`）驱动；不要另起编排。
- 无头写盘用 `agent -p --force`，经 `agent_runner`（Windows：`cmd /c` +
  `agent.cmd`，绝不裸 `subprocess(['agent', ...])`）。
- 默认模型 `cursor-grok-4.5-high`（已写入 `config.yaml` 的 `agent.args`）；
  改模型改 config，不要在 prompt 里塞模型名。
- 不合并 main/master；不 force-push。
- 续跑不要重导入计划 YAML，除非用户明确要求 reset 任务。
- 汇报时把「交付 git 失败」与「Dev/Verify 成功」分开判断。
- **编排覆盖度三必做**（缺一不开跑）：
  1. **读写闭环**：每个 PRD 资源必须有写 + 读（list/show）任务或验收项，禁止只写不读的模块。
  2. **异常流程**：每个生命周期（订单/支付/提现等）必须有取消/失败/重试/边界任务或验收项，禁止只做 happy path。
  3. **DOC 收尾**：最后一条任务（order 90+）必须是文档收尾（README + `docs/api.md` 全接口清单）。
  开跑前自检若缺任一类，先补任务再跑，不要带着缺口开跑。
- **任务 scope 强约束**：Dev/Verify 只做当前 active 任务，禁止跳号做其他 pending
  任务（prompt 已注入 `other_pending_ids` 提醒 + 脚本侧实时传入）。
- **Reality-first 编排**：编排任务前先建 reality 模型（真实工作流 + 确定性/模糊分离 +
  失败点命名）+ 边界表（每步 owner）；必须守的约束进 acceptance 的可检查项（机制），
  不靠 prompt 文字希望。详见 plan.md 的 Reality-first 段。
- **回合记忆 + 后续调整**：每任务结束后写 `.pipeline/memory/`，下一轮注入
  `prior_learnings`（截断、且仅相关 gap）。默认 `adapt.mode=suggest`（只写建议）；
  `apply` 才自动给相关 pending 追加 acceptance（不改 done、不重跑 Plan；
  DOC 收尾与弱匹配不 patch）。详见 ops-runbook「回合记忆」。
- **Windows 长 prompt**：agent argv 超限时脚本把全文写入临时文件，仅传短指针；
  若日志出现 `command line is too long`，先当 harness 问题修，勿当业务 FAIL。
- **AuthN ≠ AuthZ（资金/特权写）**：admin 结算、打款、改价等特权写必须「登录 + 授权」
  （role/policy/gate）；仅挂 `auth:sanctum` 不算完成。Verify 须有「非特权用户 → 403」
  测试。写操作默认需认证；收款账号以服务端绑定/快照为准。细则：
  [references/backend-security.md](references/backend-security.md)
- **危险默认值关死**：Auth/支付/快递 Mock 与第三方回调跳签 **默认关闭**；仅显式 env
  且非 production 可开。Verify 查 `.env.example`/config 默认或 production 强制关测试。
  细则同上。

## 软规则（带 why）

- 复用唯一主题/组件体系；并行 `style-*` + `theme-*` 会漂移，视觉门禁容易失败。
- Verify 是门禁：行为验收不能只看「文件存在」；尽量配 `verify_command`
  （build、node smoke 等）。
- 多任务同产品时优先一条 epic 分支连续 commit；每任务独立分支在脏工作区易
  checkout 失败。

## 正误对照

**正确 — 部分失败后续跑**
- 输入：「上次挂了，继续跑剩余任务」
- 动作：列 pending/done/failed → `run_loop.py --no-import`
- 错误：再跑 `run_pipeline.py --plan ...`
- 原因：重导入覆盖 stage 状态并重烧 agent 额度

**正确 — 任务粒度**
- 输入：完整产品 PRD
- 动作：6–10 条有序 YAML（store→theme→components→pages→seed→qa）
- 错误：一条任务「实现整个应用」
- 原因：一次性 agent 跳过验收深度且难续跑

**正确 — 特权写 AuthZ**
- 输入：管理端结算 `POST /api/admin/orders/{id}/settle`
- 动作：`auth` + admin/policy + Feature 测试「普通用户 → 403」
- 错误：仅挂登录中间件 + 注释「管理后台鉴权前暂开放」
- 原因：登录 ≠ 管理/财务权限；资金写无 AuthZ 可被任意客户端调用

## 按需阅读

- CLI 参数、任务 schema、prompt 模板：[reference.md](reference.md)
- 续跑 / 失败恢复 / Windows 坑：[references/ops-runbook.md](references/ops-runbook.md)
- 后端 AuthZ / Mock 默认值（资金类任务时读）：[references/backend-security.md](references/backend-security.md)

## Review 阶段（可选，整份 PRD 跑完建议开一轮）

Dev/Verify 是单任务门禁；Review 是**整份 PRD 的覆盖度审计**。整份 PRD 全 loop
跑完后，建议在 `config.yaml` 把 review 阶段 `enabled: true` 再跑一轮，产出
PRD 覆盖度矩阵 + 缺口清单（读闭环 / 异常流程 / AuthZ / 危险默认值 / 文档 / 测试），
据此决定补哪些任务再续跑。Review 不替代 Verify；特权写无 AuthZ 或 Mock 默认开
视为 critical，不得 APPROVE。
