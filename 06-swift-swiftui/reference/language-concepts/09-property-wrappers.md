# 属性包装器（Property Wrapper）

> **文档简介**: @propertyWrapper 机制的条目式参考：wrappedValue/projectedValue 双通道、初始化规则，以及它与 SwiftUI 状态体系、宏（@Observable）的边界
>
> **目标读者**: 想弄清 @State/@Binding/@AppStorage 背后机制的学习者
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
| **标签** | `#propertyWrapper` `#wrappedValue` `#projectedValue` `#State` |
| **更新日期** | `2026年9月` |

</details>

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

var player = Player()
// wrappedValue：直接访问
player.stamina = 150                      // 实际存为 100

// projectedValue：$ 前缀访问包装器暴露的"另一个东西"
player.$stamina                           // 0...100（本例中是合法范围）
```

`$` 加在属性名之前：实例访问写 player.$stamina；它投影 stamina，而不是投影 player。

### projectedValue 的语义由包装器决定

| 包装器 | wrappedValue | projectedValue（$ 前缀） |
|--------|--------------|--------------------------|
| `@State` | 当前值 | `Binding<Value>` |
| `@Binding` | 当前值 | `Binding<Value>` 本身 |
| `@Bindable`（包装 @Observable 模型） | 当前值 | 绑定工厂 |
| `@AppStorage` | 持久化值 | `Binding<Value>` |
| `@Query`（SwiftData） | 结果集合 | 不应假设有可用的 $query；按具体 SDK 的公开 API 查询和初始化配置 |

### 初始化约定速记

以下是语法示意，Wrapper 与 x 未定义，不能直接拼入可运行文件。带参数的包装器必须实际声明匹配初始化器；`projectedValue` 只是普通参数标签，不是编译器自动提供的构造方法。

```swift
// 1. 直接赋初值 → 调 init(wrappedValue:)
@Wrapper var a = 1

// 2. 带附加参数 → 参数 + wrappedValue 标签
@Clamped(0...10) var b = 5

// 3. 全参数构造 → 不走 wrappedValue 标签
@Wrapper(projectedValue: x) var c
```

## 💡 示例

### 自定义 UserDefaults 包装器（局部片段）

放入已导入 Foundation 的应用文件。此例仅演示 getter/setter 转发，不能接受任意 Value；传入不受 UserDefaults 支持的值会失败。Settings 的共享可变静态属性在 Swift 严格并发下还需要隔离约定；若只由界面使用，可将 Settings 标记 `@MainActor` 并在主 actor 调用，不能靠包装器名称假定线程安全。

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

## 先验证语言机制，再连接界面

前置产物：会声明 struct、计算属性与 init，已有可用 Swift 编译器；SwiftUI 实验另需 Xcode 应用目标。先将前文 Clamped 定义和 Player 定义依序放进 `WrapperProbe.swift`，不要混入 UserDefaults/SwiftUI 的替代例子。用下面代码替换此前零散的 player 使用语句：

```swift
var player = Player()
for requested in [-1, 50, 150] {
    player.stamina = requested
    print("requested=\(requested), stored=\(player.stamina)")
}
print(player.$stamina.lowerBound, player.$stamina.upperBound)
```

执行 `swift --version` 记录工具链，再执行 `swift WrapperProbe.swift`。本文件由前文两段定义与这段入口组成，无外部包；预期三次 stored 依次为 0、50、100，最后输出 `0 100`。输入经过 wrappedValue setter 钳制，输出读取已存储值；`$stamina` 返回范围而不是 Binding。该预期尚未在本轮执行。

下一步把 Player 的初值改为 150。预期新实例初值仍为 100，因为初始化器也进行了钳制；只在 setter 钳制会漏掉这一入口。再删除 projectedValue，保持 stamina 访问应仍可编译，但 `$stamina` 应编译失败。这是有意反例，恢复声明后再继续。

最后在已导入 SwiftUI 的应用文件放入 ToggleRow，由已有屏幕渲染它。点击 Toggle，输入通过 `$isOn` 的 Binding 写回 State，界面显示新值。不要把自定义 Clamped 的范围投影传给 Toggle：参数要求 Binding<Bool>，与 ClosedRange<Int> 无关。此阶段需要 Apple UI 环境，命令行实验不能替代它。

| 失败现象 | 回查位置 | 应恢复的契约 |
|---|---|---|
| 初始 150 未钳制，后续写入正常 | init 是否和 setter 都约束值 | 所有进入存储的入口遵守同一范围 |
| `$stamina` 不存在 | 包装器是否声明 projectedValue | 投影是可选能力，不自动生成 Binding |
| 在 Player 外访问 `_stamina` 失败 | 编译器合成的后备存储访问范围 | 在类型内部解释或调试包装器，公开读取 stamina/投影 |
| Toggle 状态不刷新 | 是否误用普通包装器替代 State，或 Binding 指向其他实例 | 状态由视图身份保存，绑定读写同一来源 |
| Settings 静态可变属性并发诊断 | actor 隔离与调用位置 | 按访问者设计隔离，不关闭检查掩盖问题 |

**验证边界与来源：** 本轮核对 [Swift 语言手册：Properties / Property Wrappers](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/properties/)，未执行此 Swift 文件、Xcode 构建或 Toggle 交互。实验给出待验证输入输出，不代表 UserDefaults 持久化、SwiftUI 更新或并发安全已验证。

## ⚠️ 常见陷阱

| 陷阱 | 说明 | 解法 |
|------|------|------|
| 以为 `$` 对任何属性可用 | 仅当包装器声明了 `projectedValue` | 查包装器文档确认 |
| 包装器属性在 init 中错误赋值 | `self.x = …` 走的是 wrappedValue 通道 | 需要整体替换包装器时用 `_x = Wrapper(…)` |
| 宏与包装器混淆 | `@Observable` 模型上硬找 `$model` | `@Bindable` 才提供 projectedValue |
| 包装器内存储引用类型并全局共享 | 状态散落、难追踪 | 共享模型走 Environment 注入 |
| 忘记 wrappedValue 的 setter 逻辑 | 每次写入都经过包装器 | 副作用放 didSet 而非包装器（或反之），统一约定 |

<!-- full-library-explanation -->
## 包装器不自动提供观察与并发安全

Clamped 只钳制写入范围；它没有通知 SwiftUI，也不提供锁。UserDefault 示例只演示 getter/setter 转发，Value 并非任意类型都能直接写入 UserDefaults，且这不是凭证存储方案。生产包装器还要处理格式迁移与跨线程访问约定。

练习：创建 `var player = Player()`，依次写入 -1、50、150，预期读取 0、50、100，并检查 `$stamina` 返回范围。验收：能分别指出包装器本体 `_stamina`、被包装值 stamina 和投影 `$stamina` 的类型；不把所有 `$` 都当 Binding。

初始化 `State(initialValue:)` 只提供该视图身份的初值，父参数变化后若要同步，应重新考虑状态归属或 Binding，而不是重复在 init 中覆盖子视图私有状态。

## 🔗 相关条目

- 📄 [04-swiftui-state-api.md](./04-swiftui-state-api.md) — SwiftUI 状态包装器全表
- 📄 [02-swiftdata-observability.md](../framework-essentials/02-swiftdata-observability.md) — @Query 与 @Observable 的机制
- 📄 [05-data-flow.md](../framework-essentials/05-data-flow.md) — 包装器在数据流中的角色
- 📄 [basics/04-views-state.md](../../basics/04-views-state.md) — 状态管理教程


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
