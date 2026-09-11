# 状态驱动视图（UI = f(state)）

> **文档简介**: SwiftUI 核心模型的条目式参考：视图是状态的纯函数、body 重新求值的触发与粒度、Observation 字段级追踪与调试手段
>
> **目标读者**: 想从"为什么界面会刷新"层面理解 SwiftUI 的学习者
>
> **前置知识**: 建议先学 [basics/02-first-swiftui-app.md](../../basics/02-first-swiftui-app.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#View协议` `#重新求值` `#Observation` `#渲染循环` |
| **更新日期** | `2026年9月` |

---

## 📌 定义

**状态驱动视图**是 SwiftUI 的核心契约：**UI 是状态的函数**。视图（View struct）只是对界面的一次轻量描述；状态变化时，框架重新调用 `body` 得到新描述，再与旧描述比对，把差异应用到真实界面上。

推论：

- 视图是**值类型**，每次求值都重建，永远不要在视图里保存"可变的工作数据"——那要用状态容器（@State 或 @Observable 模型）
- 你**不直接操作界面**（没有 label.setText），你只改状态，界面自然跟上

## 📖 语法 / 签名

### View 协议

```swift
public protocol View {
    associatedtype Body: View
    @ViewBuilder var body: Self.Body { get }
}
// body 的返回类型由编译器合成；@ViewBuilder 把多个子视图打包成一个
```

### 状态的三级来源

| 状态 | 生命周期 | 归属 |
|------|---------|------|
| `@State` | 视图生命周期，视图重建时保留 | 单个视图私有 |
| `@Observable` 模型 | 应用级（谁持有谁决定） | 跨视图共享 |
| `@Environment` | 视图树注入 | 依赖的隐式传递 |

### 重新求值的触发与粒度

```swift
// 触发：body 读取过的可观察属性发生变化
@Observable
final class Model {
    var title = ""            // 被 body 读取 → 变化触发重算
    var cachedCount = 0       // 未被 body 读取 → 变化不触发
}

// 粒度：Observation 是字段级追踪，只重算"读了这个字段的视图"
```

## 💡 示例

### 最小模型：状态 → 界面

```swift
struct CounterView: View {
    @State private var count = 0          // 状态
    var body: some View {                 // 函数
        Button("点了 \(count) 次") {       // 界面 = f(状态)
            count += 1                     // 改状态，不碰界面
        }
    }
}
```

### 字段级追踪的验证

```swift
struct ProfileView: View {
    @State private var model = ProfileModel()
    var body: some View {
        let _ = Self._printChanges()      // DEBUG：打印"谁触发了重算"
        Text(model.name)                  // 只读取 name → 只改 age 不会触发本视图
    }
}
```

### 状态放对层级：重算范围最小化

```swift
// 反例：输入草稿放在整个列表页 → 每敲一个字整页重算
struct Page: View {
    @State private var draft = ""
    var body: some View { List(100 rows) + Editor(text: $draft) }
}

// 正确：草稿收进编辑器子视图 → 只有它重算
struct Editor: View {
    @State private var draft = ""
    var body: some View { TextField("…", text: $draft) }
}
```

## ⚠️ 常见陷阱

| 陷阱 | 说明 | 解法 |
|------|------|------|
| body 中做副作用 | 网络请求、写文件会在每次重算时重复执行 | 副作用放 `.task` / `.onAppear` / 事件回调 |
| 用普通属性存可变状态 | 视图是值，重建即丢 | `@State` 或 @Observable 模型 |
| 状态层级过高 | 一处输入刷新整页 | 把状态下放到最小需要的子视图 |
| 期待 body 只执行一次 | 它会被频繁调用 | 保持 body 轻量，重活放模型层 |
| 手动调用"刷新方法" | 框架没有这种 API | 改状态，让数据流驱动 |

## 🔗 相关条目

- 📄 [04-swiftui-state-api.md](../language-concepts/04-swiftui-state-api.md) — 状态工具 API 全表
- 📄 [05-data-flow.md](./05-data-flow.md) — 状态在视图树中的流动
- 📄 [04-view-modifier.md](./04-view-modifier.md) — 修饰符与视图包装结构
- 📄 [advanced-topics/performance/01-rendering-performance.md](../../advanced-topics/performance/01-rendering-performance.md) — 重算优化的系统方法
