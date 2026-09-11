# 数据流与 Environment

> **文档简介**: SwiftUI 单向数据流的条目式参考：状态单一事实来源、意图回写、Environment 隐式依赖注入与自定义环境键
>
> **目标读者**: 需要在多视图间组织数据流向、理清 Environment 用法的学习者
>
> **前置知识**: 建议先学 [03-state-driven-views.md](./03-state-driven-views.md) 与 [basics/04-views-state.md](../../basics/04-views-state.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#单向数据流` `#Environment` `#依赖注入` `#EnvironmentKey` |
| **更新日期** | `2026年9月` |

---

## 📌 定义

**单向数据流**是 SwiftUI 推荐的数据组织方式：

```text
状态（单一事实来源） ──渲染──▶ 视图
   ▲                            │
   └──────意图（事件回调）◀── 用户交互
```

- 状态只放在一个地方（@State 或共享模型），视图是它的投影
- 视图永远不"拥有"别人的数据，只通过回调/Binding 请求数据变更
- **Environment** 是沿视图树**向下**的隐式传递通道：祖先注入，任意后代读取，免去逐层传参

## 📖 语法 / 签名

### 读取环境

```swift
// 系统环境值
@Environment(\.colorScheme) private var colorScheme
@Environment(\.dismiss) private var dismiss

// Observable 模型（键即类型）
@Environment(AppModel.self) private var appModel
```

### 注入环境

```swift
// 模型注入：键是类型本身
@State private var appModel = AppModel()
WindowGroup { RootView() }.environment(appModel)

// 值注入：自定义键
.environment(\.theme, .dark)
```

### 自定义环境键

```swift
private struct ThemeKey: EnvironmentKey {
    static let defaultValue: Theme = .system   // 必须提供默认值
}

extension EnvironmentValues {
    var theme: Theme {
        get { self[ThemeKey.self] }
        set { self[ThemeKey.self] = newValue }
    }
}
```

### 常用系统环境键

| 键 | 类型 | 用途 |
|----|------|------|
| `\.dismiss` | `DismissAction` | 关闭当前 sheet/导航 |
| `\.openURL` | `OpenURLAction` | 打开链接 |
| `\.scenePhase` | `ScenePhase` | 前后台切换 |
| `\.colorScheme` | `ColorScheme` | 深/浅色模式 |
| `\.modelContext`（SwiftData） | `ModelContext` | 数据库上下文 |

## 💡 示例

### 完整的单向数据流闭环

```swift
@MainActor @Observable
final class CartModel {
    var items: [String] = []
    func add(_ item: String) { items.append(item) }   // 意图只进模型方法
}

struct CartRoot: View {
    @State private var cart = CartModel()
    var body: some View {
        CartList().environment(cart)        // 注入：向下传递
    }
}

struct CartList: View {
    @Environment(CartModel.self) private var cart   // 读取：免层层传参
    var body: some View {
        List(cart.items, id: \.self) { Text($0) }
        Button("加一件") { cart.add("笔") }   // 意图回写：只调模型方法
    }
}
```

### 深层视图用 dismiss 关闭 sheet

```swift
struct DetailSheet: View {
    @Environment(\.dismiss) private var dismiss
    var body: some View {
        Button("完成") { dismiss() }
    }
}
```

## ⚠️ 常见陷阱

| 陷阱 | 说明 | 解法 |
|------|------|------|
| 忘记注入就读取 | 运行时崩溃（模型类环境） | Preview 与根视图都要注入；开发期立刻暴露 |
| @Environment 直接改值 | 环境读取通道只读 | 改共享模型请调用其方法 |
| 注入位置在消费者下层 | 读取不到或读到默认值 | 注入必须在消费视图的祖先（如 NavigationStack 外层） |
| 把巨型模型塞进环境 | 任何字段变化大面积重算 | 模型保持字段级可观察；按域拆分小模型 |
| 环境值当配置库 | 万物皆环境导致依赖关系不可见 | 只放真正的"横切依赖"（主题、上下文、dismiss） |

## 🔗 相关条目

- 📄 [04-swiftui-state-api.md](../language-concepts/04-swiftui-state-api.md) — @Environment 等 API 全表
- 📄 [03-state-driven-views.md](./03-state-driven-views.md) — 数据流的地基：状态驱动渲染
- 📄 [09-property-wrappers.md](../language-concepts/09-property-wrappers.md) — @Environment 的包装器机制
- 📄 [frameworks/02-swiftui-advanced.md](../../frameworks/02-swiftui-advanced.md) — Observation 与导航的进阶任务
