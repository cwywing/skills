# swiftui-style-unify

[English](README.md)

可移植 Agent Skill。针对**既有** SwiftUI / iOS 应用做风格、配色、设计统一：把散落在
视图里的颜色、字体、魔法数字收敛进单一 token 命名空间（排版带 Dynamic Type 策略），
用语义 props 封装组件，再用 fail-closed 的 ripgrep 门禁锁住。它是
[h5-style-unify](../h5-style-unify/) 的 SwiftUI 姊妹篇，两者在共享 web SoT 处组合。

**证据（如实声明）**：一个生产 SwiftUI 案例（token 层、主题、组件、lint、代码生成、
文档），并与社区 SwiftUI 设计系统实践交叉验证。社区与案例一致处明说；分歧处
（运行时主题引擎、Style Dictionary、SwiftLint）给出决策。采纳计数只放在
`references/gate-and-pitfalls.md`。

可移植命名：`DesignTokens`、`TextStyle` / `.textStyle(_:)`、`AppTheme`、`AppBadge` ——
不要带客户品牌前缀。

## 安装顺序（不是五环编号顺序）

```
P0 探测 → P1 审计（全量计数）→ P2 token 层 → P3 门禁（自测）
        → P4 迁移视图 → P5 App* 组件 + DEBUG 验收页 → P6 记录
```

## 内含什么

- **工作流**（SKILL.md）：P0–P6；变更安全分级；views 目录需确认，不默认一定叫
  `Features/`。
- **`scripts/audit-swift-styles.sh`** — 可在 macOS 跑（不用 GNU `xargs -r`）。先汇总
  全部规则再退出。缺 `rg` 即失败。禁 `.font(.system(size:))`，允许
  `.font(.system(.body))`。组件包装规则在 `--components` 之前只警告。`tests/` 锁住
  这些用例。
- **`scripts/sync-design-tokens.mjs`** — web CSS SoT → Asset Catalog colorset。MAP
  模板在 `assets/color-map.json.tmpl`。
- **`references/`** — token 解剖、主题/组件契约、同步 + Style Dictionary 决策表、
  门禁规则 + P0–P6 审计表。
- **`assets/`** — `DesignTokens.swift`、`TextStyle.swift`、`Theme.swift`、
  `DesignSystemPreviewView.swift`。

## 何时用 / 何时不用

对既有代码库提出「统一 SwiftUI/iOS 项目风格配色、design tokens、主题注入 /
white-label、Dark Mode、iOS↔H5 多端一致、SwiftUI 样式门禁」时使用。H5/网页项目用
`h5-style-unify`；从零发明视觉方向用 `frontend-design`。
