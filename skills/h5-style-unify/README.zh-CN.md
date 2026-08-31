# h5-style-unify

[English](README.md)

可移植 Agent Skill。针对**既有** H5 / 移动端网页项目做风格、配色、视觉设计的统一：
把散落的硬编码颜色收敛到唯一 token 真相源、用语义组件封装高频视觉件、再用机器门禁
锁住——不需要大爆炸重写。

**证据（如实声明）**：一个生产 H5 代码库（裸 Vue3 微信内嵌页）验证了 theme.css +
stylelint 以及 rgba / 内联样式 / customSyntax 等坑。共享该 H5 SoT 的姊妹 SwiftUI
应用验证了五环**顺序**和代码生成；Swift 细节在
[swiftui-style-unify](../swiftui-style-unify/)。不要理解成两个独立的 H5 落地。该 H5
案例当时没有 CI —— 工作流里的 CI 是它本该有的耐久层。

## 安装顺序（不是五环编号顺序）

```
P0 探测 → P1 审计 → P2 SoT → P3 门禁（自测）→ P4 迁移 → P5 组件 + 验收页 → P6 记录 + CI
```

可信门禁先于铺组件。规则能活比规则多更重要。文档是投影，不是第二份 SoT。

## 内含什么

- **工作流**（SKILL.md）：P0–P6，带变更安全分级。
- **`scripts/audit-styles.mjs`** — 零依赖、fail-closed。覆盖 stylelint 盲区：字面量
  `rgba()/hsl()`、内联 `style=`、Tailwind `bg-[#…]`、Vue SFC `<script>` 颜色字面量、
  uniapp `.wxss`/`.nvue`/`.uvue`。SoT 探测包含 Vue/uni 全局 `<style>`。`tests/` 锁住
  这些用例。
- **`references/`** — 分类法、技术栈适配、门禁配置（`<app-root>`，不是写死 `h5/`）、
  坑清单 + P0–P6 审计表、案例证据。
- **`assets/`** — `theme.css`（含暗色 `*-rgb`）、`.stylelintrc.json`、Vue3 验收页
  （只列 token 名）。

## 何时用 / 何时不用

对既有 H5 / 移动端代码库提出「统一风格 / 统一配色 / 样式统一 / design tokens / 门禁 /
换肤 / 多端视觉一致 / 风格一致性审计」时使用。不要用于从零发明全新视觉方向
（`frontend-design`），也不要用于管理后台运维 UX 走查（`admin-console-ux`）。
