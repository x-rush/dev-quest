# 常见错误与故障排除

> **文档简介**: SwiftUI/Swift 开发高频故障的"现象 → 原因 → 解决"对照表：视图重算失控、并发编译警告、Preview 崩溃、布局塌陷与签名问题
>
> **目标读者**: 遇到具体报错/异常行为、需要快速定位的全体学习者
>
> **前置知识**: 无（字典条目，按现象跳入）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#故障排除` `#调试` `#并发警告` `#Preview` |
| **更新日期** | `2026年9月` |

---

## 1. 视图重算类

### 1.1 现象：输入一个字符整个页面闪烁/卡顿

**原因**: 大 state（长文本、大数组）直接 `@State`，任何变化触发整棵子树重算；或 body 内做重计算。

**解决**:

- 把输入草稿拆到独立小视图，父视图不读该 state
- 重计算挪进 `@Observable` store 的计算属性（属性级追踪只刷新读取者）
- 长列表确认用了 List / LazyVStack

### 1.2 现象：改了模型属性，界面没刷新

**排查链**:

1. 模型标了 `@Observable` 吗？（旧 `ObservableObject` 需 `@Published`）
2. 该视图的 body **真的读取了**该属性吗？（Observation 按读取注册）
3. 是 `.environment(obj)` 注入 + `@Environment(Model.self)` 读取吗？漏注入即失效
4. 是否在视图外绕过了属性直接改了底层存储？

### 1.3 现象：List 增删动画错乱/行内容错位

**原因**: `ForEach` 的 id 不稳定（用了数组下标、随机 UUID）。

**解决**: 元素遵循 `Identifiable`，id 用业务主键或创建时固定的 `UUID()`；不用 `.id(index)`。

### 1.4 现象：body 被调用了多次，逻辑重复执行

**解决**: body 只做纯描述。副作用放 `.task`/`.onAppear`/`.onChange`；一次性昂贵计算放 store 初始化。

---

## 2. 并发警告类（Swift 6 严格检查）

| 编译器消息 | 含义 | 解决 |
|-----------|------|------|
| `Mutation of captured var in concurrently-executing code` | 并发闭包捕获局部 var | 状态进 actor / 用 Task 返回值收集 |
| `Type does not conform to the 'Sendable' protocol` | 跨隔离域传非安全类型 | 模型改 struct；或显式 `@unchecked Sendable` 并注明同步策略 |
| `Expression is 'async' but is not marked with 'await'` | 漏 await | 按建议加 `await`/`try await` |
| `Main actor-isolated property can not be referenced from a nonisolated context` | 后台代码碰 UI 状态 | 函数标 `@MainActor` 或 `await MainActor.run { … }` |
| `Task-isolated value … never used` | 任务内捕获后未用且被推断转移 | 检查是否漏 `await`，或显式拷贝 |

### 2.1 现象：下拉刷新/页面退出后任务"看起来没取消"

**原因**: 协作式取消——代码没在检查点响应。

**解决**: 长循环加 `try Task.checkCancellation()`；网络用 `URLSession.data(for:)`（内建响应）；catch 里单独处理 `CancellationError`（静默）。

### 2.2 现象：Task 里改 @State 闪退或警告"Publishing changes from background threads"

**原因**: 任务跑在非 MainActor。

**解决**: 用 `.task`（自带 MainActor）；或 store 标 `@MainActor`；或 await 挂起点后自然回到主 actor。

---

## 3. Preview 崩溃类

### 3.1 现象：Canvas 显示 "Cannot preview in this file"

**排查**:

1. `⌘B` 全量编译，看真实编译错误（预览报错常滞后）
2. 确认文件里有 `#Preview { … }`
3. 重启 Xcode / `Product > Clean Build Folder`（`⇧⌘K`）
4. 关闭 "Use a Stale Build" 类实验选项，删 `~/Library/Developer/Xcode/DerivedData`

### 3.2 现象：预览运行时崩溃（模拟器却正常）

**高频原因与解决**:

| 原因 | 解决 |
|------|------|
| 环境缺失（modelContainer、environment 模型） | 在 `#Preview` 内补注入：`Editor().modelContainer(for: Note.self, isStoredInMemoryOnly: true)` 或 `.environment(Store())` |
| 真机能力（相机/推送）在预览触发 | 预览传入 mock 服务 |
| 初始化抛错（解包失败、解码失败） | 预览用合成数据工厂 `.sample` |

### 3.3 现象：预览一直 "Preparing…" 卡住

关闭其他模拟器实例；检查是否死循环 onAppear ↔ onChange 互相 setState；升级 Xcode 后首次预览需重建索引，耐心等或 Clean。

---

## 4. 布局类

### 4.1 现象：Text 被截成 "一行…" 不换行

加 `.lineLimit(nil)` 或 `.fixedSize(horizontal: false, vertical: true)`；被挤压的关键文本加 `.layoutPriority(1)`。

### 4.2 现象：视图高度为 0 / 完全消失

**排查**: 是否放在了 `GeometryReader`（默认占满但不给子视图约束）？是否被 `if` 条件隐藏？`.frame(maxHeight: .infinity)` 意外吃掉空间？用 Debug 里的 **View Hierarchy**（`⌘⇧O` 输入 Debug View Hierarchy）看真实坐标。

### 4.3 现象：键盘弹出击穿界面/遮挡输入框

表单内容放 `Form`/`ScrollView`（系统自动避让）；自定义布局加 `.safeAreaInset` 或 `.ignoresSafeArea(.keyboard, edges: .bottom)` 反向控制。

### 4.4 现象：ScrollView 嵌 List 滚动冲突

不要嵌套。需要行交互就用 List 从头到尾；需要混排就在 ScrollView 内全用 Lazy 容器 + 手写滑动操作。

---

## 5. 环境与构建类

### 5.1 现象：真机运行 "Signing for … requires a development team"

Xcode **Settings > Accounts** 登录 Apple ID → 项目 **Signing & Capabilities** 勾选 Automatically manage signing → Team 选 Personal Team。免费签名 7 天过期，重新 `⌘R` 续签。

### 5.2 现象：`@Query` 运行时崩溃 "could not find a model container"

`WindowGroup` 忘挂 `.modelContainer(for:)`；或 Preview 环境没补。

### 5.3 现象：升级 Xcode 后大量并发报错

Xcode 26 默认 Swift 6 语言模式。过渡方案：Target > Build Settings > **Strict Concurrency Checking** 调为 Minimal（Swift 5 模式），逐步修复后再切回。

### 5.4 现象：模拟器无法安装 App / 卡在 "Installing"

`xcrun simctl erase "iPhone 16 Pro"` 重置设备；或删除 DerivedData；磁盘不足也是常见根因（保留 40GB+）。

---

## 6. 调试工具箱

```swift
// 打印视图重算次数
let _ = Self._printChanges()          // 放 body 第一行，输出哪些属性触发重算

// 断言与诊断
#if DEBUG
assert(!items.isEmpty, "列表不应为空")
#endif

// 预览变体（iOS 17+ 预览宏多环境）
#Preview("深色") { Root().preferredColorScheme(.dark) }
```

| 工具 | 入口 | 用途 |
|------|------|------|
| Debug View Hierarchy | 调试栏 | 3D 检查视图坐标/约束 |
| Instruments > SwiftUI | Xcode > Product > Profile | 视图重算热点、body 耗时 |
| Main Thread Checker | 默认开启 | 抓后台线程碰 UI |
| LLDB | 断点后 | `p model`、`v`、`e expression` |

## 相关文档

- 📄 [01-swift-swiftui-cheatsheet.md](./01-swift-swiftui-cheatsheet.md) — 速查表
- 📄 [04-swiftui-state-api.md](../language-concepts/04-swiftui-state-api.md) — 数据流包装器语义
- 📄 [03-concurrency-api.md](../language-concepts/03-concurrency-api.md) — 并发 API 与取消语义
