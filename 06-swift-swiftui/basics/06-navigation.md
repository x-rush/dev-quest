# 导航 - NavigationStack、TabView 与模态呈现

## 先理解，再动手

NavigationStack 管理一条进入与返回路径，sheet 表达模态任务，TabView 表达并列主入口。用同一种容器模拟所有导航会模糊返回语义。

**本节自测**：从列表进详情，另用 sheet 编辑标题，取消编辑不保存。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

返回和取消行为明确；保存才修改拥有者的数据，草稿与正式记录分开。

</details>

> **文档简介**: 掌握 SwiftUI 现代导航三件套：NavigationStack 压栈导航与类型安全传值、TabView 标签切换、sheet/fullScreenCover 模态弹窗
>
> **目标读者**: 能搭建单页界面、需要组织多页面应用结构的学习者
>
> **前置知识**: [05-layouts.md](./05-layouts.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#NavigationStack` `#TabView` `#Sheet` `#导航传值` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 用 NavigationStack + NavigationLink 实现压栈导航与返回
- ✅ 通过 `navigationDestination(for:)` 实现类型安全的值驱动导航
- ✅ 用 TabView 组织底部标签页，并程序化切换
- ✅ 区分 sheet / fullScreenCover / alert 并正确使用

## 🔍 一、NavigationStack：压栈导航

`NavigationStack` 取代了已废弃的 `NavigationView`，是 iOS 16+ 的标准导航容器。

### 1.1 最小可用结构

```swift
struct HomeView: View {
    var body: some View {
        NavigationStack {
            List(friends) { friend in
                NavigationLink(value: friend) {
                    FriendRow(friend: friend)
                }
            }
            .navigationTitle("好友")
            .navigationDestination(for: Friend.self) { friend in
                FriendDetail(friend: friend)
            }
        }
    }
}
```

组成部分：

| 组件 | 作用 |
|------|------|
| `NavigationStack` | 导航容器，维护视图栈 |
| `NavigationLink(value:)` | 可点击的导航入口，携带一个 Hashable 值 |
| `navigationDestination(for:)` | 声明"哪种值 → 哪个目标视图"的映射规则 |
| `navigationTitle` | 导航栏标题（也参与大标题折叠动画） |

### 1.2 值驱动导航（推荐范式）

`NavigationLink(value:)` 携带的是**数据**而不是视图，目标视图由映射规则决定。好处：

- **类型安全**：`Friend` 类型的链接只会落到 `FriendDetail`
- **解耦**：列表不需要 import 或知道详情页
- **深链支持**：同一套规则可被程序化导航复用（见下）

### 1.3 程序化导航：绑定的栈路径

```swift
struct InboxView: View {
    @State private var path: [Friend] = []      // 栈本身就是个数组

    var body: some View {
        NavigationStack(path: $path) {
            List(friends) { friend in
                NavigationLink(value: friend) { Text(friend.name) }
            }
            .navigationDestination(for: Friend.self) {
                FriendDetail(friend: $0)
            }
            .toolbar {
                Button("跳到第一个") {
                    if let first = friends.first {
                        path = [first]         // 替换为仅含该目的地的路径
                    }
                }
            }
        }
    }
}
```

- `path` 数组里是**当前栈上每层的值**：追加即 push，删除即 pop，清空即回根
- 也可用 `NavigationPath`（类型擦除版）混合多种类型
- 深链推送通知、URL scheme 跳转都通过改 `path` 实现

## 🔍 二、TabView：平级切换

```swift
struct MainTabView: View {
    @State private var selection = 0

    var body: some View {
        TabView(selection: $selection) {
            HomeView()
                .tabItem { Label("首页", systemImage: "house") }
                .tag(0)

            SearchView()
                .tabItem { Label("发现", systemImage: "magnifyingglass") }
                .tag(1)

            ProfileView()
                .tabItem { Label("我的", systemImage: "person") }
                .tag(2)
        }
    }
}
```

要点：

- 每个 tab 通常**各自包一层 NavigationStack**，栈状态互不干扰
- iOS 18+ 可用新的 `Tab` 语法糖：`Tab("首页", systemImage: "house") { HomeView() }`
- `@State selection` 可程序化切 tab（如推送点击跳"消息"页）

## 🔍 三、模态呈现：sheet 与 fullScreenCover

### 3.1 基本用法

```swift
struct AddButton: View {
    @State private var showEditor = false

    var body: some View {
        Button("新建待办") {
            showEditor = true
        }
        .sheet(isPresented: $showEditor) {
            TaskEditor()
                .presentationDetents([.medium, .large])   // 可选：半屏样式
        }
    }
}

// 带值的弹窗：用 item 版本，nil ↔ 非 nil 切换控制出现与消失
struct TaskList: View {
    @State private var editing: TaskItem?

    var body: some View {
        List(tasks) { task in
            Button(task.title) { editing = task }
        }
        .sheet(item: $editing) { task in
            TaskEditor(task: task)
        }
    }
}
```

### 3.2 三种呈现方式对比

| API | 形态 | 典型场景 |
|------|------|----------|
| `.sheet` | 底部弹出的卡片，可下拉关闭 | 新建/编辑、详情预览 |
| `.fullScreenCover` | 覆盖全屏 | 相机、登录、引导页 |
| `.alert` | 系统警告框 | 简短的确认与错误提示；现代 actions 构建器并非固定两按钮限制 |

### 3.3 关闭与回调

sheet 内容里用 `@Environment(\.dismiss) private var dismiss` 获取关闭动作；先执行保存回调，再调用 `dismiss()` 即可程序化关闭并把结果交还父视图。

## ✅ 最佳实践

需要深链接或恢复导航时，把路径表达成可识别的数据，再为路径值定义目的界面；最简单的页面跳转也可以直接使用目的 View。只有路径元素具备合适的编码契约，才谈得上序列化恢复。

不同 tab 是否各自保留返回历史由交互决定，modal 则表示独立的临时任务，不由“超过两级”机械改成 push。测试直接打开详情、返回列表、切换 tab 再回来，确认路径所有者与界面显示一致。

## ❓ 常见问题

### Q1: NavigationLink 点击没反应？

最常见三个原因：目标值类型没实现 `Hashable`；`navigationDestination(for:)` 没挂在 Stack 视图树内；链接放在了 List 之外的普通容器但被手势拦截。逐一检查。

### Q2: sheet 里的环境（如 SwiftData context）丢失？

先检查 `.modelContainer(container)` 是否装在呈现者与 sheet 的共同祖先（通常为 App 的 WindowGroup）。SwiftData 的 `modelContext` 从环境读取，不能把 `ModelContainer` 当作 `ModelContext` 传入 `.modelContext(...)`。独立 Preview、另一窗口或手动创建的宿主也要配置容器；仅出现 sheet 不足以推断环境必然丢失。参见 [modelContainer](https://developer.apple.com/documentation/swiftui/view/modelcontainer(_:)) 与 [modelContext](https://developer.apple.com/documentation/swiftui/environmentvalues/modelcontext)。

## 🎯 练习与实践

### 先交付一个列表、详情与草稿编辑闭环

前置：macOS、Xcode 与 iOS 16+ SwiftUI App 工程，先让 ContentView 出现在模拟器。本文的 Friend、FriendRow、FriendDetail、TaskEditor 是示意类型，需自行定义；`NavigationLink(value:)` 的值必须 Hashable，`sheet(item:)` 的 item 必须 Identifiable。SwiftData 环境讨论额外要求 iOS 17+，本练习先用内存数组，不引入数据库。

产物：父视图保存一条 `id=1, title=第一条笔记`；导航路径保存 ID，详情按 ID 查父数据。sheet 打开时把标题复制到局部 draft，取消只 dismiss，保存才回调父视图修改标题并 dismiss。这样取消不会偷偷改动列表。为未知 ID 显示“笔记不存在”，不要对查找结果强制解包。

| 输入 | 预期输出 | 失败回查 |
|---|---|---|
| 列表点击 1 | 详情显示原题，出现返回入口 | destination 的值类型是否与 Link 相同，是否挂在 Stack 内 |
| 编辑为“改名”后取消 | 详情与列表仍为原题 | draft 是否直接绑定了正式记录 |
| 再编辑并保存 | 详情与列表都显示“改名” | 是否按稳定 ID 更新父状态，详情是否保存了过期副本 |
| 返回根，再打开未知 ID | 显示缺失状态，仍可返回 | 是否使用数组下标代替稳定 ID |
| 清空列表后点“跳到第一个” | 不跳转、不崩溃 | 是否仍用 friends[0] 越界取值 |

本轮未在 Xcode 编译，也未执行 iOS 模拟器或真机；这些是待执行预期，不能标为原生 UI 已验证。在工程选定实际 scheme 和模拟器后执行 Build、Run，逐项记录 Xcode/iOS 版本、输入及界面结果。单纯 Swift 语法检查不能证明 SwiftUI 的呈现与返回行为。

下一步接入 [异步并发](./07-concurrency-async-await.md)，用 ID 异步加载详情；覆盖等待、失败与记录已删除三种状态后，再增加独立标签页导航栈。参考 [Apple NavigationStack](https://developer.apple.com/documentation/swiftui/navigationstack) 与 [现代 alert API](https://developer.apple.com/documentation/swiftui/view/alert(_:isPresented:actions:))。

### 练习一：基础练习

- [ ] 搭建 MainTabView（3 个 tab），每个 tab 内独立 NavigationStack
- [ ] 实现"好友列表 → 详情"的值驱动导航，详情页标题为好友名
- [ ] 用 `sheet(item:)` 实现"点击任务 → 弹出编辑卡"

### 进阶挑战

- [ ] 绑定 `path: [Friend]`，加一个按钮一次 push 两层（列表 → 详情 → 设置）
- [ ] 在详情页放 `NavigationLink` 进入第三层，观察 toolbar 返回行为并自定义标题

---

## 相关文档

- 📄 [07-concurrency-async-await.md](./07-concurrency-async-await.md) — 下一篇：并发
- 📄 [01-swiftui-essentials.md](../reference/framework-essentials/01-swiftui-essentials.md) — 导航修饰符速查
- 📄 [02-troubleshooting.md](../reference/quick-references/02-troubleshooting.md) — 导航与环境丢失类故障排除


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
