# SwiftUI 基础任务指南 — 视图、状态与布局

> **文档简介**: 面向任务的 SwiftUI 快速上手指南：从第一个视图出发，掌握 `@State`/`@Binding` 状态管理与三大布局容器的组合套路
>
> **目标读者**: 已有其他平台 UI 开发经验（如 React/Compose）、要在 Xcode 中实际搭建界面的学习者
>
> **前置知识**: [basics/03-swift-syntax-essentials.md](../basics/03-swift-syntax-essentials.md)（struct、闭包）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#SwiftUI` `#View` `#State` `#Binding` `#布局` |
| **更新日期** | `2026年9月` |

## 🎯 本指南解决什么问题

你不是来"学完 SwiftUI"的，而是要**在 30 分钟内搭出一个可交互的界面**。按下面三步走：写视图 → 接状态 → 排布局。概念细节随时跳到字典查。

## 🛠️ 任务一：写出第一个视图

SwiftUI 中一切界面都是遵循 `View` 协议的 struct：

```swift
import SwiftUI

struct GreetingCard: View {
    let name: String                      // 外部传入的不可变数据

    var body: some View {                 // body 是"界面描述"，不是"渲染函数"
        VStack(spacing: 8) {
            Text("你好, \(name)")          // 字符串插值进 Text
                .font(.title.bold())
            Image(systemName: "hand.wave") // SF Symbols 图标
                .foregroundStyle(.orange)
        }
        .padding()
    }
}

#Preview {                                // Xcode 15+ 宏，替代 PreviewProvider
    GreetingCard(name: "Dev Quest")
}
```

要点：

- `body` 是纯描述，可被多次求值；副作用放事件回调里
- 修饰符链从内向外包视图（`.font` 包住 `Text`，`.padding` 包住 `VStack`）
- 改代码后立即看效果：Xcode Preview，操作细节见 [04-devtools.md](./04-devtools.md)

## 🛠️ 任务二：接上状态

### 2.1 视图私有状态：`@State`

```swift
struct CounterView: View {
    @State private var count = 0          // private 是硬约定：状态不出视图

    var body: some View {
        VStack {
            Text("点击了 \(count) 次")
            Button("加一") { count += 1 }  // 修改 State 触发界面更新
        }
    }
}
```

### 2.2 父子共享：`@Binding`

子视图要**读写**父视图的状态时，父传 `Binding`，子当普通可写值用：

```swift
struct ThemeToggle: View {
    @Binding var isDark: Bool             // 只声明，不赋初值

    var body: some View {
        Toggle("深色模式", isOn: $isDark)  // $ 前缀取出 Binding
    }
}

struct SettingsView: View {
    @State private var isDark = false     // 状态的"所有者"在这里

    var body: some View {
        ThemeToggle(isDark: $isDark)      // 传 $isDark 下去
    }
}
```

数据流向一句话：**数据向下（传值），事件向上（Binding 回写）**。

### 2.3 什么时候用哪个

| 需求 | 用什么 | 例子 |
|------|--------|------|
| 视图内部临时状态 | `@State` | 输入框草稿、开关 |
| 子视图改父状态 | `@Binding` | 表单项回传 |
| 跨视图共享的领域模型 | `@Observable`（见进阶篇） | 用户会话、购物车 |

全部属性包装器的完整对照表见字典：[04-swiftui-state-api.md](../reference/language-concepts/04-swiftui-state-api.md)。

## 🛠️ 任务三：排布局

三个堆叠容器 + 一个滚动容器能覆盖 90% 界面：

```swift
struct ProfileCard: View {
    var body: some View {
        ScrollView {                       // 内容超出屏幕时的外壳
            VStack(alignment: .leading, spacing: 12) {
                HStack(spacing: 12) {      // 横向：头像 + 名字
                    Image(systemName: "person.circle.fill")
                        .font(.system(size: 48))
                    VStack(alignment: .leading) {
                        Text("x_rush").font(.headline)
                        Text("iOS 学习者")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                    }
                }
                Divider()
                Grid {                     // iOS 16+：表格式两列布局
                    GridRow {
                        Text("模块").gridColumnAlignment(.leading)
                        Text("进度")
                    }
                    GridRow { Text("SwiftUI"); ProgressView(value: 0.6) }
                }
            }
            .padding()
        }
    }
}
```

选择口诀：

- 内容少用 `VStack/HStack`，**长列表必须 `LazyVStack` 或 `List`**（惰性加载）
- 两列对齐用 `Grid`，自适应瀑布用 `LazyVGrid`
- 布局容器的完整清单见字典：[01-swiftui-essentials.md](../reference/framework-essentials/01-swiftui-essentials.md)

## ✅ 最佳实践

- ✅ `@State` 一律 `private`，编译器会阻止外部误改
- ✅ 界面能拆就拆成小 View，SwiftUI 按 struct 做增量求值，拆分反而更快
- ✅ 常量数据用 `let` 传入，不要为了"方便"全塞进状态

## ❌ 避免陷阱

- ❌ 把 `@State` 声明成非 private 或在 `init` 里直接赋值——状态属于视图身份，外部不该碰
- ❌ 用 `@State` 持有引用类型模型——应改用 `@Observable`，见进阶篇
- ❌ 无限嵌套修饰符不看顺序——`.padding().background()` 和 `.background().padding()` 结果不同

## ❓ 常见问题

**Q1: 改了 `@State`，Preview 不刷新？** 确认修改发生在事件回调中而非 `body` 里；Preview 需要 iOS 17+ 目标运行时支持 Observable。

**Q2: `$isDark` 的 `$` 是什么语法？** 属性包装器的 projected value，`@State` 的投影就是 `Binding`。

**Q3: `List` 和 `LazyVStack` 选谁？** 需要滑动删除/编辑/分隔线选 `List`，纯展示且要自由样式选 `LazyVStack`。

## 🎯 练习

- [ ] 实现「点餐卡」：`@State` 记录份数，Stepper 增减，总价随份数变化
- [ ] 把份数改为 `@Binding`，由父视图持有，验证子视图改动能传回去
- [ ] 用 `Grid` 把三个菜名 + 价格排成两列表格

## 相关文档

- 📄 [02-swiftui-advanced.md](./02-swiftui-advanced.md) — 下一篇：Observation、NavigationStack 与动画
- 📄 [04-swiftui-state-api.md](../reference/language-concepts/04-swiftui-state-api.md) — 属性包装器全表
- 📄 [01-swiftui-essentials.md](../reference/framework-essentials/01-swiftui-essentials.md) — 视图与修饰符字典
- 📄 [04-views-state.md](../basics/04-views-state.md) — 教程侧的状态管理讲解
