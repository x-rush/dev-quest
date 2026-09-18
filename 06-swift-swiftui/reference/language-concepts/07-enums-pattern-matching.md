# 枚举与模式匹配

> **文档简介**: enum（含关联值）与模式匹配的条目式参考：代数数据类型思想、switch 穷尽性、if/guard/for case 与 SwiftUI 状态建模
>
> **目标读者**: 需要查阅枚举与模式匹配细节的学习者
>
> **前置知识**: 建议先学 [basics/03-swift-syntax-essentials.md](../../basics/03-swift-syntax-essentials.md) §四

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#enum` `#关联值` `#模式匹配` `#switch` `#穷尽性` |
| **更新日期** | `2026年9月` |

</details>

---

## 📌 定义

**枚举（enum）**定义一组互斥取值中的一个，每个 `case` 可以携带**关联值（associated value）**——这让 Swift 枚举成为"和类型"（sum type）：一个值要么是 A，要么是 B，要么是带数据的 C。

**模式匹配**是从值结构中"解构并提取"的机制，`switch` 是主战场，`if case` / `guard case` / `for case` 是单场景快捷方式。

> `Optional` 本质就是标准库中的枚举（`Optional.some(Wrapped)` / `.none`），掌握枚举就掌握了可选值的底层模型。

## 📖 语法 / 签名

### 枚举定义的三种形态

```swift
// 1. 纯标签
enum Alignment { case left, center, right }

// 2. 关联值：每个 case 携带不同类型的数据
enum LoadState {
    case idle
    case loading
    case loaded(Note)
    case failed(Error)
}

// 3. 原始值：case 绑定一个固定字面量
enum Planet: Int { case mercury = 1, venus, earth }
```

### 模式种类速查

| 模式 | 写法 | 场景 |
|------|------|------|
| 通配符 | `_` | 明确忽略 |
| 值绑定 | `case .loaded(let note)` | 提取关联值 |
| 可选解构 | `case .some(let v)` / `case let v?` | 解包 Optional |
| 类型转换 | `case is UIError` / `case let e as URLError` | do-catch 分类 |
| 区间表达式 | `case 0..<60` | 数值分段 |
| 元组解构 | `case (0, let y)` | 坐标匹配 |

### switch 之外的匹配入口

```swift
// if case：只关心一个 case
if case .loaded(let note) = state { render(note) }

// guard case：提前退出
guard case .loading = state else { return }

// for case：过滤集合
for case .failed(let e) in history { log(e) }
```

### @unknown default

```swift
switch alignment {
case .left: …
case .center: …
case .right: …
@unknown default: …   // 只用于他人库中可能新增 case 的枚举
}
```

## 💡 示例

### 用枚举建模 SwiftUI 的界面状态（最常用模式）

```swift
enum ContentState: Equatable {
    case idle
    case loading
    case loaded([Note])
    case failed(String)
}

struct NoteListView: View {
    @State private var state: ContentState = .idle

    var body: some View {
        switch state {                       // ViewBuilder 中 switch 天然可用
        case .idle:
            Text("开始吧")
        case .loading:
            ProgressView()
        case .loaded(let notes):
            List(notes) { Text($0.title) }
        case .failed(let message):
            ContentUnavailableView("出错了", systemImage: "exclamationmark.triangle", description: Text(message))
        }
    }
}
```

> 枚举互斥性带来保证：界面上"加载中"和"错误"不可能同时出现——这正是多个 `Bool` 标志位组合做不到的。

### 关联值相等的自动合成

```swift
// 所有关联值都遵循 Equatable 时，== 自动可用
enum Direction: Equatable { case north, turn(Int) }
Direction.turn(3) == Direction.turn(3)   // true
```

## ⚠️ 常见陷阱

| 陷阱 | 说明 | 解法 |
|------|------|------|
| switch 不穷尽 | 少一个 case 编译报错（这是特性不是缺陷） | 新增 case 时让编译器找出所有遗漏点 |
| 关联值提取写错 | `case let .loaded(note)` 与 `case .loaded(let note)` 混淆 | 两种皆合法，团队内统一一种 |
| 原始值与关联值混用 | 同一枚举不能同时有 rawValue 和关联值 | 需要时用计算属性生成 rawValue |
| 递归枚举漏 indirect | case 引用自身会编译错 | 在 case 或整个 enum 前加 `indirect` |
| @unknown default 用在自己枚举上 | 编译警告 | 它只用于非 frozen 的外部枚举 |

<!-- full-library-explanation -->
## 状态枚举还需要合法转换

枚举保证一个值属于一个 case，却不阻止程序从 idle 直接跳到 loaded，也不保证过期请求不会把新 loaded 改成 failed。把“当前有哪些状态”和“事件允许怎样转换”分开设计。

练习：增加 refreshing(previous: [Note])，让刷新失败时保留旧列表并显示错误，而不是清空可用数据。验收：首次加载和后台刷新可区分；switch 为新增 case 给出明确 UI；旧请求完成前核对资源身份。

rawValue 是每个 case 固定的编码，关联值是每个实例携带的数据。`Planet(rawValue: 99)` 可能为 nil，外部协议新加取值时需要兼容策略，不能强制解包。若 NoteList 示例声明 ContentState: Equatable，Note 的全部相关属性也须满足合成相等性的条件。

## 🔗 相关条目

- 📄 [02-optionals-collections.md](./02-optionals-collections.md) — Optional 是枚举的实例
- 📄 [08-error-handling.md](./08-error-handling.md) — do-catch 中的模式匹配
- 📄 [03-state-driven-views.md](../framework-essentials/03-state-driven-views.md) — 枚举驱动界面状态的思想
- 📄 [basics/03-swift-syntax-essentials.md](../../basics/03-swift-syntax-essentials.md) §四 — 枚举入门教程


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
