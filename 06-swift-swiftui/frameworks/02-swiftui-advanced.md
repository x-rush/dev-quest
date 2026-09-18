# SwiftUI 进阶任务指南 — Observation、NavigationStack 与动画

## 先看框架承担哪部分职责

**SwiftUI 进阶**：Observation 跟踪属性读取，导航维护位置，动画描述状态变化如何呈现。它们协作但不能互相替代。

**最小练习与预期结果**：同一个模型注入两个视图，修改属性后相关内容更新；另建一个模型应是独立状态，能解释差异。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 面向任务的 SwiftUI 进阶指南：用 `@Observable` 建领域模型、用 `NavigationStack` 组织多页导航、用动画 API 让状态变化"动起来"
>
> **目标读者**: 已能搭建单页 SwiftUI 界面、要构建多视图数据驱动应用的中级学习者
>
> **前置知识**: [01-swiftui-basics.md](./01-swiftui-basics.md)（@State/@Binding、布局容器）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#Observable` `#NavigationStack` `#动画` `#过渡` `#数据流` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 本指南解决什么问题

单页 Demo 到真实应用的三个跨越：**共享模型跨视图联动**、**页面间跳转与传参**、**状态变化的动画呈现**。每个任务给可直接照做的模式。

## 🛠️ 任务一：用 @Observable 建跨视图模型

`@Observable` 宏（Observation 框架，iOS 17+）替代旧的 `ObservableObject`：

```swift
import SwiftUI
import Observation

@Observable                              // 宏：属性读取/写入自动被视图追踪
final class CartModel {
    var items: [String] = []             // 视图"读了"哪个属性，就追踪哪个

    var total: Int { items.count }       // 派生数据写成计算属性

    func add(_ item: String) {
        items.append(item)
    }

    func remove(_ item: String) {
        items.removeAll { $0 == item }
    }
}
```

在视图根部创建并用环境注入：

```swift
struct ShopApp: App {
    @State private var cart = CartModel()   // @State 持有引用类型模型是推荐写法

    var body: some Scene {
        WindowGroup {
            ShopHomeView()
                .environment(cart)          // 注入环境
        }
    }
}

struct CartBadge: View {
    @Environment(CartModel.self) private var cart   // 环境中取回

    var body: some View {
        Image(systemName: "cart")
            .overlayBadge(count: cart.total)    // cart.total 变化自动刷新
    }
}
```

**为什么不传 Binding 而用环境**：模型被 5 个以上视图读写时，逐层传参会形成"props 钻井"；环境让任意深度的子视图直接取用。二者对比与迁移对照见 [04-swiftui-state-api.md](../reference/language-concepts/04-swiftui-state-api.md)。

## 🛠️ 任务二：NavigationStack 多页导航

### 2.1 声明式路由

```swift
struct NoteListView: View {
    let titles = ["Swift 6", "Observation", "SwiftData"]

    var body: some View {
        NavigationStack {                          // 1. 导航容器
            List(titles, id: \.self) { title in
                NavigationLink(value: title) {     // 2. 压入一个"路由值"
                    Text(title)
                }
            }
            .navigationTitle("笔记")
            .navigationDestination(for: String.self) { title in
                NoteDetailView(title: title)       // 3. 值 → 目标视图
            }
        }
    }
}

struct NoteDetailView: View {
    let title: String
    var body: some View {
        Text("详情：\(title)")
            .navigationTitle(title)
            .navigationBarTitleDisplayMode(.inline)
    }
}
```

### 2.2 程序化跳转（绑定路径）

```swift
struct LoginView: View {
    @State private var path: [String] = []         // 路径数组 = 导航栈状态

    var body: some View {
        NavigationStack(path: $path) {
            Button("跳过引导") { path.append("home") }
                .navigationDestination(for: String.self) { dest in
                    if dest == "home" { HomeView() }
                }
        }
        // path.removeLast() 可编程返回；清空数组 = 回到根
    }
}
```

**模式选择**：纯用户点击用 `NavigationLink(value:)`；登录后自动跳转、深链还原用绑定路径。传参用路由值携带，不要依赖单例。

## 🛠️ 任务三：动画与过渡

### 3.1 隐式动画：`animation(_:value:)`

```swift
struct LikeButton: View {
    @State private var isLiked = false

    var body: some View {
        Button {
            withAnimation(.spring(duration: 0.4)) {  // 显式：闭包内所有变化带动画
                isLiked.toggle()
            }
        } label: {
            Image(systemName: isLiked ? "heart.fill" : "heart")
                .foregroundStyle(isLiked ? .red : .gray)
                .scaleEffect(isLiked ? 1.3 : 1.0)
                .animation(.bouncy, value: isLiked)  // 隐式：该值变化时动起来
        }
    }
}
```

### 3.2 出入过渡：`transition` + `if`

```swift
struct Banner: View {
    @State private var showBanner = false

    var body: some View {
        VStack {
            Button(showBanner ? "收起" : "显示提示") { showBanner.toggle() }

            if showBanner {
                Text("已保存到草稿箱")
                    .padding()
                    .background(.ultraThinMaterial, in: .rect(cornerRadius: 8))
                    .transition(.move(edge: .top).combined(with: .opacity))
            }
        }
        .animation(.easeInOut(duration: 0.25), value: showBanner)  // 必须挂动画
    }
}
```

**两个必踩的坑**：

- `transition` 不生效 → 忘了在**包含分支的容器**上挂 `.animation(_:value:)`
- 匹配动画跳变 → `if/else` 两侧是不同视图身份，用 `contentTransition(.numericText())` 或统一视图结构

动效 API 全表（`spring`/`keyframe`/`phaseAnimator` 等）见字典 [01-swiftui-essentials.md](../reference/framework-essentials/01-swiftui-essentials.md)。

## ✅ 最佳实践

派生属性尽量由已有状态计算，避免保存一份 filteredItems 后每次又手动同步。若计算昂贵，应明确缓存输入和失效时机，而不是默认计算属性没有成本。

数据驱动导航便于测试和恢复，但路径值还需可编码且能处理已删除资源。动画绑定到实际变化的状态并验证中断、快速操作和减少动态效果设置，避免整棵界面的无关变化一起动。

## ❌ 避免陷阱

- ❌ 在多个视图各自创建 `@Observable` 实例——环境注入的必须是同一份（根部 `@State` 创建）
- ❌ `NavigationStack` 嵌套 `ScrollView` 外层再包一层导致手势冲突——滚动交给页面根视图
- ❌ 对长列表元素加 spring 动画导致逐项延迟错位——列表增删用 `withAnimation` 包数据变更即可

## ❓ 常见问题

**Q1: `@Observable` 和旧 `ObservableObject` 混用？** 可以共存，但新代码统一 `@Observable`；旧代码迁移步骤见 [02-swiftdata-observability.md](../reference/framework-essentials/02-swiftdata-observability.md)。

**Q2: 如何在细节页回传数据？** 让详情页写回同一份 `@Observable` 模型，或用闭包回调；不要用通知中心传业务数据。

**Q3: `TabView` 里每个 tab 要独立 NavigationStack 吗？** 是，每个 tab 包一个 `NavigationStack`，否则切 tab 会丢失各自导航状态。

## 🎯 练习

- [ ] 把购物车改为 `@Observable` + 环境注入，在两个不同 tab 的页面同时显示总数
- [ ] 实现"详情页修改标题 → 返回后列表即时更新"
- [ ] 给列表项添加滑动删除动画，验证 `ForEach` 的 `id` 稳定性

## 相关文档

- 📄 [03-ecosystem-integration.md](./03-ecosystem-integration.md) — 下一篇：SwiftData + URLSession 集成
- 📄 [02-swiftdata-observability.md](../reference/framework-essentials/02-swiftdata-observability.md) — Observation 追踪机制字典
- 📄 [06-navigation.md](../basics/06-navigation.md) — 教程侧导航讲解
- 📄 [04-views-state.md](../basics/04-views-state.md) — 数据流基础教程


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
