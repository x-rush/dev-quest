# 导航 - NavigationStack、TabView 与模态呈现

> **文档简介**: 掌握 SwiftUI 现代导航三件套：NavigationStack 压栈导航与类型安全传值、TabView 标签切换、sheet/fullScreenCover 模态弹窗
>
> **目标读者**: 能搭建单页界面、需要组织多页面应用结构的学习者
>
> **前置知识**: [05-layouts.md](./05-layouts.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#NavigationStack` `#TabView` `#Sheet` `#导航传值` |
| **更新日期** | `2026年9月` |

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
                    path = [friends[0]]         // 压栈到指定位置
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
| `.alert` | 系统警告框 | 不可超过两个操作的确认 |

### 3.3 关闭与回调

sheet 内容里用 `@Environment(\.dismiss) private var dismiss` 获取关闭动作；先执行保存回调，再调用 `dismiss()` 即可程序化关闭并把结果交还父视图。

## ✅ 最佳实践

- ✅ **推荐**：导航用"值驱动"（value + destination 规则），仅在简单原型里用 `NavigationLink(destination:)` 直塞视图
- ✅ **推荐**：每个 tab 独立 NavigationStack；需要跨 tab 保持的返回栈，把 path 存到 `@Observable` store
- ❌ **避免**：在 NavigationStack 内再嵌 NavigationStack（双重导航栏）
- ❌ **避免**：用 sheet 一层叠一层地"模拟导航"——超过两级跳转就该用 push

## ❓ 常见问题

### Q1: NavigationLink 点击没反应？

最常见三个原因：目标值类型没实现 `Hashable`；`navigationDestination(for:)` 没挂在 Stack 视图树内；链接放在了 List 之外的普通容器但被手势拦截。逐一检查。

### Q2: sheet 里的环境（如 SwiftData context）丢失？

sheet 呈现的是**新的呈现层级**，部分环境不会自动继承。在 sheet 内容上重新注入：`.sheet(...) { Editor().modelContext(container) }`。

## 🎯 练习与实践

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
