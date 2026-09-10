# 第一个 SwiftUI App - 声明式 UI 入门

> **文档简介**: 解剖 SwiftUI App 的生命周期与默认模板代码，建立"状态驱动界面"的声明式 UI 思维，并掌握 Xcode Preview 工作流
>
> **目标读者**: 已完成环境搭建、希望理解 SwiftUI 程序骨架的初学者
>
> **前置知识**: [01-environment-setup.md](./01-environment-setup.md)；任意一门语言的基础编程经验

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#SwiftUI` `#App生命周期` `#声明式UI` `#Preview` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 解释 `@main` App 结构与 Scene 的关系
- ✅ 读懂默认模板 `ContentView.swift` 的每一行
- ✅ 理解"UI = f(state)"的声明式思维，并说出它与命令式 UI 的区别
- ✅ 使用 Xcode Preview 实时预览与交互调试界面

## 🔍 一、App 生命周期

每个 SwiftUI 应用的入口是一个遵循 `App` 协议的结构体：

```swift
import SwiftUI

@main
struct SwiftNotesApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

逐层拆解：

| 元素 | 角色 |
|------|------|
| `@main` | 告诉编译器：程序的入口在这里（SwiftUI 项目不再需要 `main.swift`） |
| `App` 协议 | 要求提供 `body`，且 `body` 是 `some Scene` 类型 |
| `WindowGroup` | 一种 Scene：为每个窗口/每个场景创建内容实例（iPhone 上是单窗口，iPad 多窗口、macOS 可多开） |
| `ContentView` | 应用实际显示的根视图 |

### Scene 家族

除 `WindowGroup` 外还有其他常用 Scene，按需追加在 `body` 中：

```swift
@main
struct SwiftNotesApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: Note.self)          // SwiftData 容器（详见第 08 课）
        
        Settings {
            SettingsView()                        // macOS/iOS 设置场景
        }
    }
}
```

## 🔍 二、解剖 ContentView

```swift
import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack {
            Image(systemName: "globe")
                .imageScale(.large)
                .foregroundStyle(.tint)
            Text("Hello, world!")
        }
        .padding()
    }
}
```

三个关键点：

1. **`View` 协议**：SwiftUI 中"一切皆视图"。遵循 `View` 协议只需实现一个 `body` 计算属性，返回 `some View`。
2. **`some View`**：`some` 表示"某个确定的、遵循 View 的类型"但隐藏具体类型名——SwiftUI 用修饰符组合出极其复杂的类型，手写类型名不现实。详见 [05-protocols-generics.md](../reference/language-concepts/05-protocols-generics.md)。
3. **`body` 是计算属性**：每次状态变化 SwiftUI 可能重新调用 `body` 重新求值 UI——这正是声明式的核心（下节展开）。

## 🔍 三、声明式 UI 思维

### 命令式 vs 声明式

以"点击按钮改变标签文字"为例对比两种范式：

**命令式（UIKit 思路）**：描述"怎么改"

```swift
// UIKit：手动拿到控件、手动修改
@objc func buttonTapped() {
    label.text = "你点击了 \(count) 次"
}
```

**声明式（SwiftUI 思路）**：描述"界面是什么样"，变化交给框架

```swift
// SwiftUI：只声明 UI 与状态的关系
struct CounterView: View {
    @State private var count = 0

    var body: some View {
        VStack {
            Text("你点击了 \(count) 次")
            Button("点我") {
                count += 1          // 只改状态，UI 自动更新
            }
        }
    }
}
```

心智模型一句话：**UI = f(state)**。你永远不直接操作控件；改状态，SwiftUI 重新计算并渲染界面。

### 重渲染 ≠ 性能问题

`body` 每次都会重新求值，但 SwiftUI 内部做了 diff（差异比较），只更新真正变化的真实视图。所以"视图很轻、值类型、随时重建"是正常且被鼓励的写法。相关陷阱见 [02-troubleshooting.md](../reference/quick-references/02-troubleshooting.md)。

## 🛠️ 四、Preview 工作流

### 4.1 基本用法

在 `ContentView.swift` 底部：

```swift
#Preview {
    ContentView()
}
```

按下 `⌥⌘↩` 切换到 Canvas，即可实时预览；直接在预览中点击、滚动，交互与真机一致。改代码，预览增量刷新，无需 `⌘R`。

### 4.2 让预览更接近真实

```swift
#Preview("浅色") {
    ContentView()
        .preferredColorScheme(.light)
}

#Preview("深色 + 大字体") {
    ContentView()
        .preferredColorScheme(.dark)
        .environment(\.dynamicTypeSize, .xxxLarge)
}

// 带假数据的预览（依赖 @Observable 模型时）
#Preview {
    let model = NoteViewModel()
    model.notes = [.previewSample]
    return NoteListView(model: model)
}
```

### 4.3 Preview 崩溃排查

预览器是独立进程，崩溃不会影响模拟器运行。常见原因：模型初始化抛错、缺少 `modelContainer` 环境、预览代码本身编译失败。系统性排查表见 [02-troubleshooting.md](../reference/quick-references/02-troubleshooting.md)。

## ✅ 最佳实践

- ✅ **推荐**：把"改 UI"的冲动转成"改状态"——先想清楚哪个状态变化了，再写界面描述
- ✅ **推荐**：小视图拆分。`body` 太长就抽子 View，SwiftUI 重建小视图的开销极低
- ✅ **推荐**：为每个视图文件保留一个 `#Preview`，复杂界面提供深色/大字体变体
- ❌ **避免**：在 `body` 里做副作用（网络请求、写数据库）——`body` 可能被调用多次
- ❌ **避免**：试图缓存或持有 View 实例。视图是廉价的值描述，不是长期对象

## ❓ 常见问题

### Q1: `body` 里的代码会执行多次，变量声明会不会重复初始化？

会，所以 `body` 中只做"描述"。需要跨重渲染保留的值放 `@State`（见 [04-views-state.md](./04-views-state.md)）。

### Q2: Preview 显示 "Cannot preview in this file"？

通常是编译错误或该文件没有 `#Preview` 宏。先 `⌘B` 全量编译看报错面板，再确认预览宏存在。

### Q3: Scene 和 View 有什么区别？

Scene 是系统级"场景容器"（窗口、菜单栏、设置面板），管理窗口生命周期；View 是场景内部的 UI 树。App `body` 放 Scene，Scene 里放 View。

## 🎯 练习与实践

### 练习一：基础练习

- [ ] 新建 SwiftUI 项目，运行后在模拟器上看到 "Hello, world!"
- [ ] 实现 `CounterView`：按钮 + 点击计数文本，并解释状态变化后发生了什么
- [ ] 为 CounterView 添加两个 `#Preview`（浅色/深色）

### 进阶挑战

- [ ] 把 `WindowGroup` 内容替换为一个三行的自我介绍卡片（姓名/职业/一句话），使用 VStack + 三个 Text
- [ ] 尝试在 iPad 模拟器（iPad Pro 13"）运行同一项目，观察窗口与布局差异

---

## 相关文档

- 📄 [03-swift-syntax-essentials.md](./03-swift-syntax-essentials.md) — 补齐阅读模板代码所需的 Swift 语法
- 📄 [04-views-state.md](./04-views-state.md) — 深入 View 协议与状态管理
- 📄 [参考：SwiftUI 核心速查](../reference/framework-essentials/01-swiftui-essentials.md) — 视图与修饰符字典
