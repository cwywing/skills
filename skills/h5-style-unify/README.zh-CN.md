# h5-style-unify

[English](README.md)

针对**既有** H5 / 移动端网页项目做风格、配色、视觉设计的统一：把散落的硬编码颜色
收敛到唯一的 token 真相源，用语义组件封装高频视觉件，再加机器门禁拦住回退，
全程不需要推倒重来。

这套做法有真实项目背书：一个生产 H5 代码库（裸 Vue3 的微信内嵌页）验证了
theme.css + stylelint，也踩出了 rgba、内联样式、customSyntax 这些坑；共享同一
H5 SoT 的 SwiftUI 应用验证了五环顺序和代码生成，Swift 侧的细节见
[swiftui-style-unify](../swiftui-style-unify/)。两者是同一次落地的两端，不是
两次独立的 H5 实践。另外这个 H5 项目当时没有 CI，工作流里的 CI 相当于把它欠的
那一层补上。

## 安装顺序（不是五环编号顺序）

```
P0 探测 → P1 审计 → P2 SoT → P3 门禁（自测）→ P4 迁移 → P5 组件 + 验收页 → P6 记录 + CI
```

先把门禁做可信，再铺组件；规则能留下比规则多更重要；文档只是投影，不是第二份 SoT。

## 内含什么

- **工作流**（SKILL.md）：P0–P6，带变更安全分级。
- **`scripts/audit-styles.mjs`** — 零依赖、fail-closed。覆盖 stylelint 的盲区：
  字面量 `rgba()/hsl()`、内联 `style=`、Tailwind `bg-[#…]`、Vue SFC `<script>`
  颜色字面量、uniapp `.wxss`/`.nvue`/`.uvue`。SoT 探测包含 Vue/uni 全局
  `<style>`。这些用例在 `tests/` 里锁住。
- **`references/`** — 分类法、技术栈适配、门禁配置（`<app-root>`，不写死 `h5/`）、
  坑清单 + P0–P6 审计表、案例证据。
- **`assets/`** — `theme.css`（含暗色 `*-rgb`）、`.stylelintrc.json`、Vue3 验收页
  （只列 token 名）。

## 何时用 / 何时不用

对既有 H5 / 移动端代码库提出「统一风格 / 统一配色 / 样式统一 / design tokens /
门禁 / 换肤 / 多端视觉一致 / 风格一致性审计」时使用。从零发明全新视觉方向不归它管
（用 `frontend-design`），管理后台的运维 UX 走查也不归它管（用 `admin-console-ux`）。
