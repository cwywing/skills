# h5-style-unify

[English](README.md)

可移植 Agent Skill。针对**既有** H5 / 移动端网页项目做风格、配色、视觉设计的统一：
把散落的硬编码颜色收敛到唯一 token 真相源、用语义组件封装高频视觉件、再用机器门禁
锁住成果——不需要大爆炸重写。

方案不是理论推演，而是在**两个生产项目上交叉验证**过的：裸 Vue3 微信内嵌 H5
（star-training）和与 H5 共享 SoT 的 SwiftUI iOS 客户端（EvairSIM），连同它们踩过的
每一个坑（门禁假绿、rgba 盲区、语义色双口径、SoT 漂移）。

## 五环流水线

```
1 SoT          theme.css — 全项目唯一允许写裸 hex 的文件
2 消费层        base.css 全局基建类 / 组件库变量桥接；业务只用 var(--*)
3 组件封装      tone × variant 语义组件；业务传语义，不碰色值
4 机器门禁      stylelint color-no-hex（error 级）+ pre-commit + CI — fail-closed
5 验收页        dev-only 设计系统页，用运行时真实值渲染全部 token
```

贯穿原则（两个案例独立收敛出同样结论）：**门禁可信先于铺组件**；**规则能活比规则多
更重要**；**文档是投影，不是第二份 SoT**；**fail-closed，绝不假绿**；**审计表诚实
记录未还的债（精确到文件路径）**。

## 内含什么

- **工作流**（SKILL.md）：Phase 0 技术栈探测 → Phase 1 审计 → SoT → 消费层 → 门禁 →
  验收页 → 诚实审计表；每个阶段带变更安全分级（本技能会改真实代码）。
- **`scripts/audit-styles.mjs`** — 零依赖、fail-closed 的审计脚本。覆盖 stylelint
  看不见的盲区：字面量 `rgba()/hsl()`、模板内联 `style="…#fff…"`、JS 侧颜色字面量；
  自动探测 SoT、门禁与技前端栈。已在两个案例仓库实测（重新发现了记录在案的 JS 侧
  盲区）并用合成违规项目验证过全部检测器。
- **`references/`** — token 分类法与双层命名；技术栈适配（裸 Vue/React、Vant、
  antd-mobile、Varlet、uniapp、跨端 SoT + 代码生成）；门禁配置实录（含 customSyntax
  踩坑）；交叉验证的坑清单 + 审计表模板；两个案例的并排对照。
- **`assets/`** — 即取即用模板：带注释的 `theme.css`（亮色 + 可选暗色）、带中文整改
  提示的 `.stylelintrc.json`、Vue3 dev-only 设计系统验收页。

## 何时用 / 何时不用

对既有 H5 / 移动端代码库提出「统一风格 / 统一配色 / 样式统一 / design tokens / 门禁 /
换肤 / 多端视觉一致 / 风格一致性审计」时使用。不要用于从零发明全新视觉方向（那是
`frontend-design`），也不要用于管理后台运维 UX 走查（那是 `admin-console-ux`）。

溯源：会话 `sess_135a0e98`（star-training H5，完整整理已存该项目 `docs/`）与
`sess_e1b1e90b`（EvairSIM iOS），均为 2026-08-30。
