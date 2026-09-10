# Swift + SwiftUI 一行式速查表

> **文档简介**: 最高频 Swift 语句与 SwiftUI 片段的一行式速查：复制即用，按场景分组，不展开原理
>
> **目标读者**: 需要快速找到"那行代码怎么写"的全体学习者
>
> **前置知识**: 各条目的讲解见 reference 其他分册与 basics

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#速查` `#Swift` `#SwiftUI` `#代码片段` |
| **更新日期** | `2026年9月` |

---

## 1. Swift 一行式

```swift
// 常量与变量
let max = 10; var count = 0

// 字符串插值
let msg = "共 \(items.count) 条，完成 \(doneRate * 100, specifier: "%.0f")%"

// 可选解包三连
if let name { print(name) }                            // 影子绑定
let display = nickname ?? "游客"                        // 默认值
guard let url = URL(string: input) else { return }     // 早退出

// 集合五件套
let doubled = nums.map { $0 * 2 }
let filtered = nums.filter { $0 > 0 }
let total = nums.reduce(0, +)
let valid = urls.compactMap { URL(string: $0) }
let grouped = Dictionary(grouping: users, by: \.city)

// 排序
let top = users.sorted { $0.score > $1.score }.prefix(10)

// 去重
let unique = Array(Set(ids))

// 枚举 switch 穷尽
var label: String { switch state { case .idle: "待机"; case .loading: "加载中"; case .loaded(let n): "已载 \(n)"; case .failed(let m): m } }

// 错误处理
let result = try? decode()                              // 错误转 nil
try await Task.checkCancellation()                      // 取消检查
defer { file.close() }                                  // 退出前清理

// 类型判断与转换
if let task = value as? TaskItem { use(task) }

// 计时
let cost = { measure(); return CFAbsoluteTimeGetCurrent() - start }()
```

---

## 2. SwiftUI 界面骨架

```swift
// App 入口
@main struct App_: App { var body: some Scene { WindowGroup { Root() } } }

// 视图模板
struct Row: View { let item: Item; var body: some View { Text(item.title) } }

// 预览
#Preview { Row(item: .sample) }

// 状态三件
@State private var on = false                          // 私有状态
@Binding var value: Int                                // 双向引用
@Observable final class Model { var x = 0 }            // 可观察模型
```

---

## 3. 布局一行式

```swift
VStack(alignment: .leading, spacing: 12) { … }         // 垂直排列
HStack { Text("左"); Spacer(); Text("右") }             // 两端对齐
ZStack(alignment: .bottom) { Img(); Caption() }        // 叠加贴底
LazyVGrid(columns: [GridItem(.adaptive(minimum: 120))]) { … }  // 自适应网格
.frame(maxWidth: .infinity)                            // 占满宽
.frame(maxWidth: 480)                                  // iPad 限宽
.padding(16)                                           // 内边距
.background(.background.secondary, in: RoundedRectangle(cornerRadius: 12))  // 圆角卡片
.safeAreaInset(edge: .bottom) { Bar() }                // 底部悬浮条
.overlay(alignment: .topTrailing) { Badge() }          // 角标
```

---

## 4. 列表与导航一行式

```swift
List(items) { item in Text(item.title) }               // Identifiable 列表
List { Section("A") { … }; Section("B") { … } }        // 分组
ForEach(items) { item in NavigationLink(value: item) { Row(item: item) } }
.navigationDestination(for: Item.self) { Detail($0) }  // 值驱动目标
.navigationTitle("标题").navigationBarTitleDisplayMode(.inline)
.toolbar { Button("加", systemImage: "plus") { add() } }   // iOS 17 快捷构造
.sheet(item: $selected) { EditView($0) }               // 带值弹窗
TabView { A().tabItem { Label("一", systemImage: "1.circle") } }
.searchable(text: $query, prompt: "搜索")               // 搜索栏
.swipeActions { Button("删", role: .destructive) { del() } }  // 滑动操作
```

---

## 5. 数据流一行式

```swift
.environment(store)                                    // 根部注入模型
@Environment(Model.self) private var store             // 读取模型
@Environment(\.dismiss) private var dismiss            // 关闭当前页
@Query(filter: #Predicate<Task> { !$0.isDone }) var todo: [Task]  // SwiftData 查询
context.insert(Item()); try context.save()             // 增 + 存
@AppStorage("theme") var theme = "system"              // 持久偏好
.onChange(of: value) { old, new in react(new) }        // iOS 17 签名
```

---

## 6. 并发一行式

```swift
.task { items = try await api.load() }                 // 视图生命周期任务
.task(id: userID) { await load(userID) }               // 参数变化重启
try await URLSession.shared.data(from: url)            // GET 请求
async let a = f(); async let b = g(); use(try await a, try await b)  // 并行
await MainActor.run { label = "ok" }                   // 桥接回主线程
try await Task.sleep(for: .seconds(2))                 // 非阻塞休眠
for await update in stream { apply(update) }           // 消费异步流
```

---

## 7. 外观与动画一行式

```swift
.foregroundStyle(.secondary)                           // 语义色
.tint(.orange)                                         // 控件主色
.font(.headline.bold())                                // 字体链式
.animation(.snappy, value: isOn)                       // 限定动画
withAnimation(.spring(duration: 0.3)) { open.toggle() }
.transition(.scale.combined(with: .opacity))           // 进出场
.contentTransition(.numericText())                     // 数字滚动（iOS 17）
.matchedGeometryEffect(id: "hero", in: ns)             // 共享元素
.preferredColorScheme(isDark ? .dark : .light)         // 强制主题
```

## ⚠️ 使用提示

- 所有 `item`/`items`/`store` 均为占位名，替换为你的模型与属性
- 需要原理与陷阱解释时，跳转各分册：语法 → [02-optionals-collections.md](../language-concepts/02-optionals-collections.md)；数据流 → [04-swiftui-state-api.md](../language-concepts/04-swiftui-state-api.md)；视图 → [01-swiftui-essentials.md](../framework-essentials/01-swiftui-essentials.md)

## 相关文档

- 📄 [02-troubleshooting.md](./02-troubleshooting.md) — 报错对照与排查
- 📄 [01-swift-keywords.md](../language-concepts/01-swift-keywords.md) — 关键字详解
- 📄 [basics/01-environment-setup.md](../../basics/01-environment-setup.md) — 常用命令行（simctl）
