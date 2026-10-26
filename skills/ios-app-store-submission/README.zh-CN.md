# ios-app-store-submission

无头（headless）iOS 提审 skill：用 `xcodebuild` + `asc`（App Store Connect CLI）
把「代码就绪」推进到「已提交审核」，并用按版本归档的提审台账保证跨天、多人
协作随时可复盘。覆盖 build 上传、TestFlight 访问、审核材料、就绪度门禁、
驳回处理全流程。

编写遵循 [skill-authoring](../skill-authoring/) 的 house style；内容提炼自
两个 App 的真实 v1.0 提审实战（2026-10）——`references/`
里每条规则背后都有一次真实踩过的坑。

## 权威源 —— 下游只安装，不 forks

**发布主页：[cwywing/skills](https://github.com/cwywing/skills) →
`skills/ios-app-store-submission/`** —— 全组织 iOS 仓库共用这份 skill 的唯一
事实源。同步规则：在已安装的副本里发现缺陷或学到新东西，改动**落到发布主页**
（提审进行中可先暂存在工作仓库，结束后立即晋升），然后下游重新安装——不要
就地改副本，否则分叉必然漂移。项目差异属于各项目的事实表与台账（见下方定制
清单），永远不进 skill 正文。

## 安装

整个目录拷进项目的 skill 目录（不要拍平——目录本身就是 skill）：

```bash
# 从已提交本目录的仓库（权威源）导出到目标项目
git archive HEAD .agents/skills/ios-app-store-submission | tar -x -C /path/to/project
# 或直接 cp -r；目标 .agents/skills/（或 .cursor/skills/ / .claude/skills/）
# 若项目里装过本 skill 的分叉副本，同一次改动里删掉旧副本，保证只触发一份
```

构建机依赖：Xcode、已认证的 `asc` CLI（Rork asc）、Apple Distribution 证书
所在的已知钥匙串。

## 每个项目一次的定制清单

- 把事实表模板里「来源」列填成*你的*权威位置（release-map 文档路径、
  `project.yml` 还是 `Info.plist`、钥匙串路径、readiness JSON 路径）。
- 建 skill 期望的台账根目录：`docs/submissions/`（布局见
  `references/journal-discipline.md`），或在 Phase 0 把 skill 指向已有的
  台账位置。
- 把 `assets/templates.md` §notes-3 的演示账号/不扣款话术换成你 app 的
  账号删除路径与支付说明。
- 裸 API 兜底需要 `python3` + `cryptography` 包（凭据来自
  `ASC_KEY_ID`/`ASC_ISSUER_ID`/`ASC_KEY_PATH` 或 `~/.appstoreconnect/*.env`）；
  修图脚本用 `swift scripts/retouch_status_bar.swift` 直接跑。
- 其余保持原样：阶段、门禁、bright lines 是刻意做成项目无关的——它们沉淀
  的是 App Store 机制，不是某个 app 的选择。

## 目录结构

```
SKILL.md                              ← 工作流、门禁、bright lines
references/build-and-upload.md        ← 归档 → 导出 → 上传 → 挂载 + 错误对照表
references/review-readiness.md        ← validate/doctor、审核信息、隐私/分级/定价
references/screenshots-capture.md     ← XCUITest 截图产线、状态栏修图、槽位尺寸表
references/testflight-and-access.md   ← 邀请链、内测组、垃圾邮件陷阱
references/raw-api-fallback.md        ← CLI 覆盖不到时的裸 API 端点陷阱
references/journal-discipline.md      ← docs/submissions/ 纪律
scripts/asc_api.py                    ← 裸 API 执行器（ES256 JWT 签名）
scripts/retouch_status_bar.swift      ← 截图状态栏修图（iOS 26+）
assets/templates.md                   ← 事实表、台账、备注、报告骨架
assets/export-options.plist           ← 手动导出模板
```
