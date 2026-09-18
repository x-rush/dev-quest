# 数据流与 Environment

> **文档简介**: SwiftUI 单向数据流的条目式参考：状态单一事实来源、意图回写、Environment 隐式依赖注入与自定义环境键
>
> **目标读者**: 需要在多视图间组织数据流向、理清 Environment 用法的学习者
>
> **前置知识**: 建议先学 [03-state-driven-views.md](./03-state-driven-views.md) 与 [basics/04-views-state.md](../../basics/04-views-state.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#单向数据流` `#Environment` `#依赖注入` `#EnvironmentKey` |
| **更新日期** | `2026年9月` |

</details>

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
enum Theme: Sendable { case system, dark }

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
    struct Item: Identifiable { let id = UUID(); let name: String }
    private(set) var items: [Item] = []
    func add(_ item: String) { items.append(Item(name: item)) }   // 意图只进模型方法
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
        List(cart.items) { Text($0.name) }
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
| 把巨型模型塞进环境 | 依赖难追踪；Observation 本身仍按实际读取的属性追踪 | 模型保持字段级可观察；按域拆分小模型 |
| 环境值当配置库 | 万物皆环境导致依赖关系不可见 | 只放真正的"横切依赖"（主题、上下文、dismiss） |

<!-- full-library-explanation -->
## 依赖注入不是隐藏所有参数

向孩子传值适合只读展示，Binding 适合简单表单编辑，事件闭包适合表达删除、提交等意图，Environment 适合整个子树共享的服务。选择依据是依赖范围与写入权限，不是传参越少越好。

购物车练习：先在列表和徽章中显示同一 cart 的数量，添加两支同名笔时应出现两个有不同 id 的项目；再为其中一支增加删除按钮，确保徽章同步减一。不要把数量复制成第二个 @State，否则两处容易不同步。编辑订单涉及校验时通过模型方法修改，而不是让任意视图直接改全部字段。

预览应显式提供测试模型；生产请求服务可以替换成内存服务，以验证加载、空态与失败。dismiss 应从被呈现的视图环境读取，父视图取得的 dismiss 不一定对应想关闭的 sheet。

## 🔗 相关条目

- 📄 [04-swiftui-state-api.md](../language-concepts/04-swiftui-state-api.md) — @Environment 等 API 全表
- 📄 [03-state-driven-views.md](./03-state-driven-views.md) — 数据流的地基：状态驱动渲染
- 📄 [09-property-wrappers.md](../language-concepts/09-property-wrappers.md) — @Environment 的包装器机制
- 📄 [frameworks/02-swiftui-advanced.md](../../frameworks/02-swiftui-advanced.md) — Observation 与导航的进阶任务


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
