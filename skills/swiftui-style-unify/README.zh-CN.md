# swiftui-style-unify

[English](README.md)

针对**既有** SwiftUI / iOS 应用做风格、配色、设计统一：把散落在视图里的颜色、
字体、魔法数字收进一个 token 命名空间（排版带 Dynamic Type 策略），用语义 props
封装组件，再用 fail-closed 的 ripgrep 门禁拦住回退。和
[h5-style-unify](../h5-style-unify/) 是同一套五环方法的两端，在共享 web SoT 处
组合使用。

这套做法有真实项目背书：一个生产 SwiftUI 案例（token 层、主题、组件、lint、
代码生成、文档），并与社区的 SwiftUI 设计系统实践交叉核对过。社区与案例一致的
地方直接写结论，有分歧的地方（运行时主题引擎、Style Dictionary、SwiftLint）把
取舍写明白。各方案的采纳计数只放在 `references/gate-and-pitfalls.md`。

命名固定用 `DesignTokens`、`TextStyle` / `.textStyle(_:)`、`AppTheme`、
`AppBadge`，不带客户品牌前缀。

## 安装顺序（不是五环编号顺序）

```
P0 探测 → P1 审计（全量计数）→ P2 token 层 → P3 门禁（自测）
        → P4 迁移视图 → P5 App* 组件 + DEBUG 验收页 → P6 记录
```

## 内含什么

- **工作流**（SKILL.md）：P0–P6；变更安全分级；views 目录要跟用户确认，不默认
  就叫 `Features/`。
- **`scripts/audit-swift-styles.sh`** — 在 macOS 上能直接跑（不依赖 GNU
  `xargs -r`）。先汇总全部规则再退出；缺 `rg` 直接失败。禁
  `.font(.system(size:))`，允许 `.font(.system(.body))`。组件包装规则在
  `--components` 之前只警告。这些用例在 `tests/` 里锁住。
- **`scripts/sync-design-tokens.mjs`** — web CSS SoT → Asset Catalog colorset。
  MAP 模板在 `assets/color-map.json.tmpl`。
- **`references/`** — token 解剖、主题/组件契约、同步 + Style Dictionary 决策表、
  门禁规则 + P0–P6 审计表。
- **`assets/`** — `DesignTokens.swift`、`TextStyle.swift`、`Theme.swift`、
  `DesignSystemPreviewView.swift`。

## 何时用 / 何时不用

对既有代码库提出「统一 SwiftUI/iOS 项目风格配色、design tokens、主题注入 /
white-label、Dark Mode、iOS↔H5 多端一致、SwiftUI 样式门禁」时使用。H5/网页项目
用 `h5-style-unify`；从零发明视觉方向用 `frontend-design`。
