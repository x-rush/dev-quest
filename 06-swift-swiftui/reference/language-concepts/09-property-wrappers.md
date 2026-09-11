# 属性包装器（Property Wrapper）

> **文档简介**: @propertyWrapper 机制的条目式参考：wrappedValue/projectedValue 双通道、初始化规则，以及它与 SwiftUI 状态体系、宏（@Observable）的边界
>
> **目标读者**: 想弄清 @State/@Binding/@AppStorage 背后机制的学习者
>
> **前置知识**: 建议先学 [basics/04-views-state.md](../../basics/04-views-state.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#propertyWrapper` `#wrappedValue` `#projectedValue` `#State` |
| **更新日期** | `2026年9月` |

---

## 📌 定义

**属性包装器**是把"某个属性的读写逻辑"封装成独立类型的语言机制：被标注的属性实际存储在包装器实例里，代码中对该属性的读写被转发到包装器的 `wrappedValue`。

SwiftUI 的状态体系（`@State`、`@Binding`、`@Environment`、`@AppStorage`…）与 SwiftData 的 `@Query` 都建立在这一机制上。理解它，`$` 前缀与初始化规则就不再是魔法。

> 注意区分：`@Observable`、`@Model` 是**宏（macro）**，展开为成员与方法，不是属性包装器；`@State`、`@Query` 才是。

## 📖 语法 / 签名

### 定义一个包装器

```swift
@propertyWrapper
struct Clamped<Value: Comparable> {
    private var value: Value
    let range: ClosedRange<Value>

    var wrappedValue: Value {            // 主体通道：读写被包装的属性
        get { value }
        set { value = min(max(newValue, range.lowerBound), range.upperBound) }
    }

    var projectedValue: ClosedRange<Value> { range }   // 辅助通道：$ 前缀访问

    init(wrappedValue: Value, _ range: ClosedRange<Value>) {
        self.range = range
        self.value = min(max(wrappedValue, range.lowerBound), range.upperBound)
    }
}
```

### 使用与两个通道

```swift
struct Player {
    @Clamped(0...100) var stamina = 100   // 初值经 init(wrappedValue:) 进入包装器
}

// wrappedValue：直接访问
player.stamina = 150                      // 实际存为 100

// projectedValue：$ 前缀访问包装器暴露的"另一个东西"
$player.stamina                           // 0...100（本例中是合法范围）
```

### projectedValue 的语义由包装器决定

| 包装器 | wrappedValue | projectedValue（$ 前缀） |
|--------|--------------|--------------------------|
| `@State` | 当前值 | `Binding<Value>` |
| `@Binding` | 当前值 | `Binding<Value>` 本身 |
| `@Bindable`（包装 @Observable 模型） | 当前值 | 绑定工厂 |
| `@AppStorage` | 持久化值 | `Binding<Value>` |
| `@Query`（SwiftData） | 结果集合 | 查询配置 |

### 初始化约定速记

```swift
// 1. 直接赋初值 → 调 init(wrappedValue:)
@Wrapper var a = 1

// 2. 带附加参数 → 参数 + wrappedValue 标签
@Clamped(0...10) var b = 5

// 3. 全参数构造 → 不走 wrappedValue 标签
@Wrapper(projectedValue: x) var c
```

## 💡 示例

### 自定义 UserDefaults 包装器（项目高频）

```swift
@propertyWrapper
struct UserDefault<Value> {
    let key: String
    let defaultValue: Value

    var wrappedValue: Value {
        get { UserDefaults.standard.object(forKey: key) as? Value ?? defaultValue }
        set { UserDefaults.standard.set(newValue, forKey: key) }
    }
}

enum Settings {
    @UserDefault(key: "haptics.on", defaultValue: true)
    static var hapticsEnabled: Bool
}
```

### 在 SwiftUI 里对照理解 @State

```swift
struct ToggleRow: View {
    @State private var isOn = false      // wrappedValue: Bool
                                         // $isOn: Binding<Bool>
    var body: some View {
        Toggle("提醒", isOn: $isOn)      // 参数要 Binding → 用 $isOn
    }
}
```

## ⚠️ 常见陷阱

| 陷阱 | 说明 | 解法 |
|------|------|------|
| 以为 `$` 对任何属性可用 | 仅当包装器声明了 `projectedValue` | 查包装器文档确认 |
| 包装器属性在 init 中错误赋值 | `self.x = …` 走的是 wrappedValue 通道 | 需要整体替换包装器时用 `_x = Wrapper(…)` |
| 宏与包装器混淆 | `@Observable` 模型上硬找 `$model` | `@Bindable` 才提供 projectedValue |
| 包装器内存储引用类型并全局共享 | 状态散落、难追踪 | 共享模型走 Environment 注入 |
| 忘记 wrappedValue 的 setter 逻辑 | 每次写入都经过包装器 | 副作用放 didSet 而非包装器（或反之），统一约定 |

## 🔗 相关条目

- 📄 [04-swiftui-state-api.md](./04-swiftui-state-api.md) — SwiftUI 状态包装器全表
- 📄 [02-swiftdata-observability.md](../framework-essentials/02-swiftdata-observability.md) — @Query 与 @Observable 的机制
- 📄 [05-data-flow.md](../framework-essentials/05-data-flow.md) — 包装器在数据流中的角色
- 📄 [basics/04-views-state.md](../../basics/04-views-state.md) — 状态管理教程
