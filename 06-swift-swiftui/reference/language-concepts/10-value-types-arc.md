# 值类型、引用类型与 ARC

> **文档简介**: struct/enum（值语义）与 class/actor（引用语义）的条目式参考：赋值与传递行为、ARC 引用计数、weak/unowned 与循环引用
>
> **目标读者**: 从 GC 语言（Go/Java/Kotlin）转来、需要重建内存心智模型的学习者
>
> **前置知识**: 建议先学 [basics/03-swift-syntax-essentials.md](../../basics/03-swift-syntax-essentials.md) §二

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#struct` `#class` `#ARC` `#weak` `#值语义` |
| **更新日期** | `2026年9月` |

</details>

---

## 📌 定义

**值类型**（struct、enum、元组等）：赋值与传参时**整体拷贝**，每个持有者各有一份独立数据——修改互不影响。

**引用类型**（class、actor、闭包）：赋值与传参时**共享同一个实例**，多变量指向同一块内存；生命周期由 **ARC（自动引用计数）**管理——引用计数归零时实例立即释放。

Swift 标准库的设计哲学是**优先 struct**：模型、坐标、配置等数据用值语义减少意外共享；并发安全仍取决于内部成员与访问方式；`class` 只留给需要共享可变状态或身份的场景（ViewModel、controller）。

> 与 Go 对照：Go 的 map/slice 是"引用语义的值类型"混合体；Swift 中 struct 明确是值语义，class 才是引用。

## 📖 语法 / 签名

### 两种类型的关键差异

| 能力 | struct / enum | class |
|------|---------------|-------|
| 赋值行为 | 拷贝 | 共享引用 |
| 可变性控制 | `var` 实例整体可变 | 属性逐个 `var` |
| 修改自身的方法 | 需 `mutating` | 直接修改 |
| 继承 | 不支持 | 支持 |
| deinit | 无 | 有 |
| 身份比较 | 无（用 `==` 比值） | `===` 比实例 |

### 引用计数与弱引用

```swift
final class Cache {
    deinit { print("Cache 释放") }        // 计数归零时调用
}

// weak：不增加计数，实例释放后自动变 nil（必须 var + Optional）
weak var parent: Parent?

// unowned：不增加计数，且假定实例始终存活（释放后访问即崩溃）
unowned let owner: Owner
```

### 循环引用的经典现场与解法

```swift
final class Screen {
    var onClose: (() -> Void)?            // 强引用闭包
    func dismiss() {}                     // 示例占位方法（真实 dismiss 通常由导航层提供）
    deinit { print("释放") }
}

func demo() {
    let screen = Screen()
    screen.onClose = { screen.dismiss() } // 闭包捕获 screen → 互相强引用
    // 解法：screen.onClose = { [weak screen] in screen?.dismiss() }
}
```

## 💡 示例

### SwiftUI 中的标准分工

```swift
import Foundation
import Observation

// 值类型：复制本例结构后，修改副本的字段不会修改原值
struct Note: Identifiable, Codable {
    let id: UUID
    var title: String
    var done: Bool
}

// 引用类型：共享可变状态，全 App 唯一实例
@MainActor @Observable
final class NotesModel {
    var notes: [Note] = []          // 数组元素是值类型
    func toggle(_ id: UUID) {
        guard let index = notes.firstIndex(where: { $0.id == id }) else { return }
        notes[index].done.toggle()
    }
}
```

### 值语义的隔离效果

```swift
var a = Note(id: UUID(), title: "草稿", done: false)
var b = a
b.title = "已发布"
print(a.title)   // "草稿" —— b 的修改不影响 a
```

### 标准库集合的写时复制（Copy-on-Write）

```swift
let big = Array(0..<1_000_000)
var copy = big        // Array 通常共享底层存储，保持值语义
copy[0] = -1          // 首次写入才发生实际拷贝
```

## ⚠️ 常见陷阱

| 陷阱 | 说明 | 解法 |
|------|------|------|
| struct 含 class 字段当"深拷贝" | 拷贝的只是引用，两份数据共享同一对象 | 嵌套结构保持全值类型，或显式复制 |
| 循环引用导致泄漏 | 对象互相强引用永不释放 | `weak` 打破环；Instruments Leaks 验证 |
| unowned 悬垂崩溃 | 实例已释放仍访问 | 生命周期不明时一律用 `weak` |
| 把普通 class 放 @State 就期待属性被观察 | 普通字段变化不自动触发观察 | 现代 Observation 模型可由 @State 持有；按实际对象与系统版本选择 |
| 滥用 class 图"省拷贝" | 标准集合可采用 COW，但并非所有值类型都 O(1) | 先测量再优化，默认 struct |

<!-- full-library-explanation -->
## 值语义与物理复制分开理解

struct 复制的是其值；若字段含 class，字段值是同一对象引用。Array 的 COW 也不把元素引用自动深复制。因此“用 struct 就线程安全”不成立，仍要检查内部共享可变对象与跨隔离域访问。

练习：定义 Box 类和包含 Box 的 Holder 结构体，复制 Holder 后修改 box.value。反馈：两份 Holder 可观察到同一 Box 改变；把 Box 改为值类型后再比较。不要用 O(1) 概括所有值类型复制成本，集合第一次独立写入可能复制缓冲区。

ARC 管理强引用关系，作用域结束不总能作为精确释放时钟；任务、闭包和缓存可能延长寿命。排查泄漏时重复进出页面并查看保留路径，缓存稳定增长与永久引用环需要分别判断。

## 🔗 相关条目

- 📄 [09-property-wrappers.md](./09-property-wrappers.md) — @State 值语义与包装器
- 📄 [11-actors-sendability.md](./11-actors-sendability.md) — actor 是引用类型中的并发安全特例
- 📄 [03-state-driven-views.md](../framework-essentials/03-state-driven-views.md) — 视图本身是值类型
- 📄 [02-troubleshooting.md](../quick-references/02-troubleshooting.md) — 内存类问题排查


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
