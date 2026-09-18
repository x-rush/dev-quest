# SwiftUI 状态属性包装器全表

> **文档简介**: @State、@Binding、@Observable、@Bindable、@Environment 等 SwiftUI 数据流工具的完整对照：定义、投影值、适用边界与新旧迁移
>
> **目标读者**: 需要确定"这个状态该用哪个包装器"的全体学习者
>
> **前置知识**: 建议先学 [basics/04-views-state.md](../../basics/04-views-state.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#State` `#Binding` `#Observable` `#Environment` `#属性包装器` |
| **更新日期** | `2026年9月` |

</details>

---

## 0. 选型速查（先看这张表）

| 状态归属 | 值类型简单状态 | 引用类型模型 |
|----------|----------------|--------------|
| 本视图私有 | `@State` | `@State`（根部创建） |
| 子视图读写父视图数据 | `@Binding` | `@Bindable` / 直接传引用 |
| 只读传入 | 普通属性 | 普通属性（引用） |
| 跨层级共享 | `@Environment(\.key)` | `.environment(obj)` + `@Environment(Type.self)` |
| SwiftData 查询 | — | `@Query` |

---

## 1. @State

**定义**: SwiftUI 托管的视图私有可变存储；属性在视图结构体重建后依然存活。

```swift
struct Counter: View {
    @State private var count = 0

    var body: some View {
        Button("\(count)") { count += 1 }
    }
}
```

| 维度 | 说明 |
|------|------|
| 存什么 | 值类型 UI 状态；或根视图创建的 `@Observable` 引用 |
| 投影值 `$count` | `Binding<Int>` |
| 访问控制 | 通常声明 private 以封装所有权；不是由 iOS 17 统一强制的语法规则 |
| 生命周期 | 与视图身份绑定，视图移除即销毁 |

**陷阱**: `@State private var list: [Item] = loadExpensive()` 的初始化表达式会在每次重建视图结构时重新求值（尽管 SwiftUI 通常只取首次）——昂贵初始化放 `.task` 或 store。

---

## 2. @Binding

**定义**: 对外部状态的**读写引用**，不拥有数据。

```swift
struct StepperRow: View {
    @Binding var value: Int

    var body: some View {
        Stepper("\(value)", value: $value)
    }
}
// 父视图：StepperRow(value: $count)
```

| 维度 | 说明 |
|------|------|
| 创建方式 | `$state`、`@Bindable` 的 `$model.x`、`Binding(get:set:)` 自定义 |
| 常量绑定 | 显式 `Binding.constant(value)`，常用于只读预览；let 不自动变成 Binding |

---

## 3. @Observable 与 @Bindable（Observation 框架，iOS 17+）

**定义**: `@Observable` 宏把 class 变成"属性级可观察"；视图读取哪些属性，就追踪哪些属性。

```swift
@Observable
final class NoteStore {
    var notes: [Note] = []
    var filter = ""
    func add(_ t: String) { notes.append(Note(title: t)) }
}
```

**视图侧持有方式**：

| 包装器 | 用途 | 示例 |
|--------|------|------|
| `@State` | 本视图**创建并拥有**该引用 | `@State private var store = NoteStore()` |
| 普通属性 | 父视图传入，无需 Binding；引用的 var 成员仍可修改 | `let store: NoteStore` |
| `@Bindable` | 父视图传入，需要 **Binding**（表单/双向） | `@Bindable var store: NoteStore` |

```swift
struct Editor: View {
    @Bindable var store: NoteStore        // 引用来自父视图/环境
    var body: some View { TextField("搜索", text: $store.filter) }
}
```

**与旧方案对照**：

| 旧（Combine 系，仍可用） | 新（Observation） |
|--------------------------|-------------------|
| `class Model: ObservableObject` | `@Observable final class Model` |
| `@Published var x` | 普通 `var x`（宏自动追踪） |
| `@StateObject` | `@State` |
| `@ObservedObject` | 普通属性 或 `@Bindable` |
| `@EnvironmentObject` | `@Environment(Model.self)` |

---

## 4. @Environment

**定义**: 读取 SwiftUI 环境值（系统注入或上层 `.environment()` 注入）。

### 4.1 系统环境键（常用）

| 键 | 类型 | 用途 |
|----|------|------|
| `\.dismiss` | DismissAction | 关闭当前呈现 |
| `\.colorScheme` | ColorScheme | 当前深/浅色 |
| `\.scenePhase` | ScenePhase | active/inactive/background |
| `\.modelContext` | ModelContext | SwiftData 数据库上下文 |

```swift
struct Editor: View {
    @Environment(\.dismiss) private var dismiss
    @Environment(\.scenePhase) private var phase

    var body: some View {
        Button("完成") { dismiss() }
            .onChange(of: phase) { _, new in if new == .background { autosave() } }
    }
}
```

### 4.2 环境注入 Observable 模型

```swift
// 注入（App 根部）
WindowGroup { Root() }.environment(store)

// 读取（任意深度）
@Environment(NoteStore.self) private var store
```

**陷阱**: 环境模型未注入就读取会**运行时崩溃**；有默认值的 EnvironmentKey 与可选模型读取是不同 API，开发期用 `@Environment(NoteStore.self)` 后立刻访问验证。

---

## 5. 其他数据流工具

| 工具 | 定义 | 典型场景 |
|------|------|----------|
| `@Query` | SwiftData 查询，响应数据库变化 | `@Query(filter: #Predicate<TaskItem> { !$0.isDone })` |
| `@AppStorage` | UserDefaults 绑定 | `@AppStorage("theme") var theme = "system"` |
| `@SceneStorage` | 状态恢复（每场景独立） | 文本草稿、选中 tab |
| `@FocusState` | 键盘焦点 | `@FocusState var focused: Field?` |
| `@GestureState` | 手势进行中的临时值，**手势结束自动复位** | `@GestureState var s: CGFloat = 1` + `.gesture(g.updating($s) { v, s, _ in s = v.magnification })` — 详见 [08-gestures.md](../framework-essentials/08-gestures.md) |

---

## ⚠️ 高频陷阱速查

- **@State 引用类型去重**：两个视图各自 `@State var store = Store()` 会得到两份实例；共享模型必须根部创建 + 环境传递
- **$ 前缀对不上**：只有包装属性有投影；对 `let store`（普通属性）写 `$store.x` 前需 `@Bindable`
- **onChange 旧签名**：iOS 17+ 是双参数 `{ old, new in }`，单参数旧版已废弃

## 相关文档

- 📄 [02-swiftdata-observability.md](../framework-essentials/02-swiftdata-observability.md) — SwiftData 与 Observation 原理速查
- 📄 [03-concurrency-api.md](./03-concurrency-api.md) — 与 @MainActor 的配合


<!-- full-library-explanation -->
## 先回答谁创建、谁修改、需要活多久

一个页面创建草稿用 State；子编辑器修改该草稿用 Binding；多个页面共享可观察模型时由共同祖先持有，再传引用或注入环境。Bindable 只为已有 Observable 对象产生 Binding，不替你创建应用级单例，也不提供线程安全。

练习：父视图保存整数 count，两个 StepperRow 同时绑定 `$count`。操作任一控件，另一处应立即更新。再让两个子视图各自创建 State count，观察它们变为独立计数，解释差异。最后用 `.constant(3)` 预览一个子视图，控件不会把 3 改成永久的新值。

可观察对象使用 `let` 只限制引用重新赋值，不禁止修改其可变成员。若只想开放读取，应通过 private(set)、只读协议或值快照表达权限；普通属性不是只读对象保证。迁移旧 ObservableObject 时要连同所有权包装器一起调整，不能仅删除 @Published。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
