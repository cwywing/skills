# swiftui-style-unify

[English](README.md)

可移植 Agent Skill。针对**既有** SwiftUI / iOS 应用做风格、配色、设计统一：把散落在
视图里的颜色、字体、魔法数字收敛进单一 token 命名空间（排版带 Dynamic Type 策略），
用语义 props 封装组件，再用 fail-fast 的 ripgrep 门禁锁住。它是
[h5-style-unify](../h5-style-unify/) 的 SwiftUI 姊妹篇，两者在共享 web SoT 处组合。

**证据基础（如实声明）**：一个生产案例（EvairSIM——token 层、主题、12 个组件、lint、
代码生成链、文档，全部从源码取证），并与社区最佳实践及开源 SwiftUI 设计系统交叉验
证。社区与案例一致处，skill 明说；分歧处（运行时主题引擎、Style Dictionary、
SwiftLint），skill 给出决策表而不是默默继承某一方。

## 五环的 Swift 形态

```
1 SoT          Asset Catalog colorset — 存在共享 web SoT 时由其生成
2 Token 层     ColorTokens（Color("...") 唯一家）· 带 Dynamic Type 策略的完整 TextStyle
               对象 · Spacing/Radius/Shadow/Metrics/Motion — 统一 DesignTokens 入口
3 组件封装     tone 枚举 → token 成对映射；ButtonStyle 承载交互态
4 机器门禁     ripgrep MUST-NOT 清单（缺 rg 即 fail-fast，绝不假绿）进 CI
5 验收页       DEBUG-only Design Tab；每个组件登记，每个 token 族带 catalog
```

## 内含什么

- **工作流**（SKILL.md）：探测 → 审计 → token 层 → 组件 → Features 迁移 → 门禁 →
  诚实审计表；全程带变更安全分级。
- **`scripts/audit-swift-styles.sh`** — 泛化自生产门禁：裸 `Color(`、
  `.font(.system(size:))`、数字 `padding/cornerRadius/spacing/frame`、裸 `.shadow`、
  裸 `ProgressView/Toggle/ContentUnavailableView`、tokens 文件之外的 `Color("...")`、
  多行 Image 尺寸反模式。自动探测 Features 目录与 tokens 文件；`--report` 输出采纳
  计数。实测：案例仓库全绿（713 处 `DesignTokens.` / 182 处 `.evairTextStyle`），
  合成违规文件正确拦截。
- **`references/`** — token 层解剖（含 Dynamic Type 策略与 catalog 模式）；主题注入
  与组件契约；跨端同步与代码生成（含 Style Dictionary 决策表）；门禁规则全集、假绿
  教训（含泛化脚本时新发现的 rg glob 优先级表亲 bug）、审计模板、外部交叉验证注记。
- **`assets/`** — 即取即用 Swift 模板：`DesignTokens.swift` 命名空间 + token 族、
  `EvairTextStyle.swift` 完整排版对象、`Theme.swift` Environment 容器 + 移植了 web
  曲线的 MotionTokens。

## 何时用 / 何时不用

对既有代码库提出「统一 SwiftUI/iOS 项目风格配色、design tokens、主题注入 /
white-label、Dark Mode、iOS↔H5 多端一致、SwiftUI 样式门禁」时使用。H5/网页项目用
`h5-style-unify`；从零发明视觉方向用 `frontend-design`。

溯源：EvairSIM 会话 `sess_e1b1e90b`（2026-08-30）+ 对 `~/wwwroot/EvairSIM/ios-swiftui`
仓库的直接源码取证。
