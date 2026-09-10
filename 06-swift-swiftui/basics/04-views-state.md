# View 协议与状态管理 - @State、@Binding 与 @Observable

> **文档简介**: 系统讲解 SwiftUI 的视图身份与数据流：View 协议细节、@State/@Binding 本地状态、@Observable 现代数据模型与单向数据流架构
>
> **目标读者**: 已了解声明式 UI 基本概念、需要构建多视图数据驱动界面的学习者
>
> **前置知识**: [03-swift-syntax-essentials.md](./03-swift-syntax-essentials.md)（struct、闭包、可选值）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#View协议` `#State` `#Binding` `#Observable` `#数据流` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 说明 View 是值类型描述、SwiftUI 如何凭状态变化决定重算
- ✅ 用 `@State` 与 `@Binding` 管理视图本地状态与双向绑定
- ✅ 用 `@Observable` 宏编写可被视图观察的模型类
- ✅ 建立"自上而下的单向数据流"直觉

## 🔍 一、View 协议再深入

```swift
public protocol View {
    associatedtype Body: View
    @ViewBuilder @MainActor var body: Self.Body { get }
}
```

三个事实决定你写 SwiftUI 的方式：

1. **View 是 struct**：每次 `body` 求值都可能产生新的视图值，SwiftUI 靠视图在层级中的**位置身份**做 diff。
2. **`body` 必须是纯描述**：不应有副作用，不能假设它只被调用一次。
3. **视图 = 函数**：`VStack { Text("a"); Text("b") }` 本质是调用 `VStack.init(@ViewBuilder content:)` 闭包。`@ViewBuilder` 让多个子视图按顺序组装为元组视图。

### 视图身份（Identity）小知识

- 结构性身份：`if/else` 两个分支是不同视图；`ForEach` 用数据 `id` 维持身份
- 显式身份：`.id(someValue)` 强制重建；列表增删动画异常时常与身份有关，详见 [01-swiftui-essentials.md](../reference/framework-essentials/01-swiftui-essentials.md)

## 🔍 二、@State：视图私有状态

```swift
struct PlayPauseButton: View {
    @State private var isPlaying = false

    var body: some View {
        Button(isPlaying ? "暂停" : "播放") {
            isPlaying.toggle()
        }
    }
}
```

要点：

- `@State` 把属性升级为 **SwiftUI 托管的持久存储**：视图重建（`body` 重算）不会丢失它
- **必须 `private`**：状态属于这个视图，外部不该触碰
- 存值类型应为值类型（struct/String/Bool/Int）
- 只在当前视图及直接子视图内使用的 UI 状态（开关、选中的 tab、输入草稿）用它

## 🔍 三、@Binding：双向绑定

子视图需要"读 + 改"父视图的状态时，传入 `@Binding`：

```swift
struct FilterSwitch: View {
    @Binding var isOn: Bool          // 只持有引用，不拥有数据

    var body: some View {
        Toggle("仅看未完成", isOn: $isOn)
    }
}

struct TaskListView: View {
    @State private var onlyUndone = false    // 真正的数据在这里

    var body: some View {
        FilterSwitch(isOn: $onlyUndone)      // $ 前缀把 @State 投影为 Binding
    }
}
```

理解 `$`：对 `@State`/`@Binding` 属性加 `$` 前缀，取出其**投影包装**（ProjectedValue），即 `Binding<T>`。传入 Binding 的视图能读写源头，数据所有权仍在父视图。

| 场景 | 传什么 |
|------|--------|
| 子视图只读数据 | 直接传值 `TaskItem` |
| 子视图需要改数据 | 传 `$value`（Binding） |
| 子视图改完要通知（如删除） | 传闭包 `onDelete: (TaskItem) -> Void` |

## 🔍 四、@Observable：现代数据模型（Observation 框架）

`@State`/`@Binding` 适合视图私有的简单状态。**跨视图共享的领域模型**从 iOS 17 起用 Observation 框架：

```swift
import Observation

@Observable
final class NoteStore {
    var notes: [Note] = []
    var filterText = ""

    var filteredNotes: [Note] {
        filterText.isEmpty
            ? notes
            : notes.filter { $0.title.localizedCaseInsensitiveContains(filterText) }
    }

    func add(_ title: String) {
        notes.append(Note(title: title))
    }
}
```

```swift
struct NoteListView: View {
    @State private var store = NoteStore()   // 引用类型模型也用 @State 持有

    var body: some View {
        List(store.filteredNotes) { note in
            Text(note.title)
        }
        .safeAreaInset(edge: .bottom) {
            AddNoteBar { store.add($0) }
        }
    }
}
```

### Observation 为什么比旧方案好

- **属性级追踪**：视图只重算它实际读取的属性变化，粒度比旧 `ObservableObject`（整对象通知）更细
- **无需协议样板**：`@Observable` 宏自动生成追踪代码，不再需要 `@Published` 与 `objectWillChange`
- **普通 Swift**：在非 UI 层（测试、命令行）也能用，不绑定 Combine

### 模型跨层级传递

深层子视图需要同一份 store 时，用环境注入而不是逐层传递：

```swift
// 根部注入
ContentView()
    .environment(store)

// 任意深度子视图读取
struct BadgeView: View {
    @Environment(NoteStore.self) private var store

    var body: some View {
        Text("共 \(store.notes.count) 条")
    }
}
```

## 🔍 五、单向数据流

把上述组件串成架构图：

```
用户操作
   │（闭包 / Binding 写入）
   ▼
状态（@State 持有的 store）
   │（Observation 追踪变化）
   ▼
受影响视图重算 body → SwiftUI diff → 更新屏幕
```

原则：

1. **状态只有一份**，放在双方共同的最近父视图，或 `@Observable` store
2. **数据向下流**（props/环境），**事件向上流**（闭包/Binding）
3. 视图永不修改不属于自己的状态——想改，就发事件给拥有者

## ✅ 最佳实践

- ✅ **推荐**：UI 局部状态用 `@State`，领域模型用 `@Observable` class，两者不混用
- ✅ **推荐**：`@Observable` 模型是引用类型，**用 `@State` 在根部创建并持有**，保证生命周期与视图树一致
- ✅ **推荐**：把派生数据写成计算属性（如 `filteredNotes`），而不是手动维护两份变量
- ❌ **避免**：把 `@Observable` 模型再包一层 `@State` 之外的 `class` 持有器——多余且破坏追踪
- ❌ **避免**：在多个视图各自 `@State private var store = NoteStore()`，会创建两份互不相通的数据

## ❓ 常见问题

### Q1: 改了 `@Observable` 模型的属性，视图没刷新？

检查该视图是否真的**读取了那个属性**（Observation 按读取追踪）。若通过环境获取，确认用了 `@Environment(Model.self)` 且根部已 `.environment(model)` 注入。

### Q2: `@State` 的值在视图跳转回来后被重置了？

`@State` 生命周期与视图身份绑定：视图从层级移除（如被 NavigationStack 弹出）后状态销毁。需要存活的持久状态放 SwiftData 或外部 store。

### Q3: 旧的 `ObservableObject` / `@Published` 还能用吗？

能用，但新代码首选 `@Observable`。迁移对照与 API 全表见 [04-swiftui-state-api.md](../reference/language-concepts/04-swiftui-state-api.md)。

## 🎯 练习与实践

### 练习一：基础练习

- [ ] 实现 `CounterView`（@State）+ `StepperView`（@Binding 接收数值）组合
- [ ] 创建 `@Observable` 的 `ThemeStore`（深色开关），用 `.environment` 注入并在子视图读取切换背景色
- [ ] 给 TaskListView 加搜索框，验证 `filterText` 变化时列表即时过滤

---

## 相关文档

- 📄 [05-layouts.md](./05-layouts.md) — 下一篇：布局系统
- 📄 [04-swiftui-state-api.md](../reference/language-concepts/04-swiftui-state-api.md) — 全部属性包装器字典
- 📄 [02-swiftdata-observability.md](../reference/framework-essentials/02-swiftdata-observability.md) — SwiftData 与 Observation 深度速查
