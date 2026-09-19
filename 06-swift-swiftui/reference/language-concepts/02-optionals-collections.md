# 可选值与集合 API 速查

> **文档简介**: Optional 解包全手段（可选链、guard let、map/flatMap）与 Array/Dictionary/Set 核心 API 的条目式参考
>
> **目标读者**: 查阅某个解包写法或集合方法的全体学习者
>
> **前置知识**: 无；配套教程见 [basics/03-swift-syntax-essentials.md](../../basics/03-swift-syntax-essentials.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#Optional` `#Array` `#Dictionary` `#Set` `#集合API` |
| **更新日期** | `2026年9月` |

</details>

---

## 1. Optional 类型

**定义**: `enum Optional<Wrapped> { case none, case some(Wrapped) }`——`String?` 只是 `Optional<String>` 的语法糖。

### 1.1 解包手段对照表

| 手段 | 语法 | 场景 | nil 时行为 |
|------|------|------|-----------|
| if let | `if let name { … }` | 有值才执行的分支 | 跳过分支 |
| guard let | `guard let name else { return }` | 早退出 + 绑定提升 | 执行 else 并退出 |
| nil 合并 | `name ?? "默认"` | 提供默认值 | 取右侧 |
| 可选链 | `user?.profile?.name` | 连续访问 | 整体为 nil |
| map | `name.map { $0.count }` | 有值才转换 | nil |
| 强制解包 | `name!` | 100% 确定有值 | **崩溃** |
| as? / try? | `value as? T` / `try? fetch()` | 条件转换失败 / 抛错分别转 nil | nil |

### 1.2 可选链与整体 nil

```swift
struct User { var name: String = "匿名"; var address: Address? }
struct Address { var city: String? }

let user = User(address: nil)
let city = user.address?.city ?? "未知"     // Optional 链短路，合并后 city 为 String
let upper = user.address?.city?.uppercased() // 链可以任意长
```

**关键**: 可选链结果的类型是 `T?` 而不是 `T`，哪怕最后一个属性非可选——因为链条中途可能断。

### 1.3 guard let 的绑定提升

```swift
func render(user: User?) {
    guard let user, let city = user.address?.city else {
        return                     // 必须退出：return/throw/continue/fatalError
    }
    // 此后 user 与 city 都是普通非可选值，作用域直达函数尾
    print("\(user.name) 住在 \(city)")
}
```

---

## 2. Array

### 2.1 创建与访问

```swift
var nums = [3, 1, 2]
nums[0]                       // 下标越界会崩溃
nums.first                    // 3（Optional）
nums.last                     // 2（Optional）
nums.first(where: { $0 > 1 }) // Optional(3) —— 第一个满足条件的元素
nums.count; nums.isEmpty
```

### 2.2 变换与过滤（最常用五件套）

```swift
nums.map { $0 * 2 }                    // [6,2,4] —— 一一映射
nums.filter { $0 > 1 }                 // [3,2] —— 筛选
nums.reduce(0, +)                      // 6 —— 折叠求和
nums.compactMap { $0 > 1 ? $0 : nil }  // [3,2] —— 映射并剔除 nil
nums.flatMap { [$0, $0] }              // 展平一层
```

### 2.3 排序与查找

```swift
nums.sorted()                        // 升序新数组
nums.sorted { $0 > $1 }              // 自定义降序
nums.sort()                          // 原地排序（var 需要）
nums.contains(1); nums.contains { $0 > 5 }
nums.firstIndex(of: 2)               // 前面 sort 后数组为 [1,2,3]，得到 Optional(1)
nums.min(); nums.max()
```

### 2.4 增删

```swift
nums.append(4); nums += [5]
nums.insert(0, at: 0)
nums.remove(at: 0); nums.removeAll()
nums.dropFirst(); nums.prefix(2); nums.suffix(2)   // 非破坏性切片
```

### 2.5 与 SwiftUI 配合

```swift
import SwiftUI

struct ListItem: Identifiable {
    let id: UUID
    var title: String
    var isPinned: Bool
}

struct PinnedItemsView: View {
    let items: [ListItem]
    var body: some View {
        List {
            Section("全部") {
                ForEach(items) { item in Text(item.title) }
            }
            Section("已置顶") {
                ForEach(items.filter(\.isPinned)) { item in Text(item.title) }
            }
        }
    }
}
```

**陷阱**: `ForEach` 依赖 `id` 稳定性。用 `indices` 或随机 id 做 id 会导致增删动画错乱，见 [02-troubleshooting.md](../quick-references/02-troubleshooting.md)。

---

## 3. Dictionary

### 3.1 增查改删

```swift
var scores = ["alice": 90, "bob": 75]
scores["carol"] = 88                 // 增/改
scores["alice"]                      // Optional(90) —— 下标永远返回可选
scores["dave", default: 0]           // 0 —— 带默认值查询
scores.removeValue(forKey: "bob")    // Optional(75)
```

### 3.2 高频变换

```swift
scores.mapValues { $0 + 5 }          // 全部 +5
scores.filter { $0.value > 80 }      // 过滤（得到 Dictionary）
Dictionary(grouping: users, by: \.city)   // 按键分组 → [City: [User]]
scores.merge(["carol": 80]) { max($0, $1) } // 合并并解决键冲突
```

### 3.3 典型模式：计数器

```swift
var counts: [String: Int] = [:]
for word in words {
    counts[word, default: 0] += 1    // 一行完成词频统计
}
```

**陷阱**: 下标赋 `nil` 是**删除**键值对；判断"键不存在"用 `scores[key] == nil`，判断"值可能为 nil"需区分双重可选。

---

## 4. Set

```swift
let a: Set = [1, 2, 3]
let b: Set = [3, 4]

a.union(b)           // {1,2,3,4}  并
a.intersection(b)    // {3}        交
a.subtracting(b)     // {1,2}      差
a.symmetricDifference(b)  // {1,2,4}
a.contains(2)        // true —— 哈希查找，O(1)
```

**选型**: 只判断"存在性/去重"用 Set；需要顺序用 Array + `Set` 辅助判重。

---

## ⚠️ 高频陷阱速查

- **数组下标越界崩溃**：优先 `first`/`last`/`firstIndex(of:)` 等返回 Optional 的 API
- **Dictionary 下标的 Optional**：读值永远是 `T?`；`for (k, v) in dict` 中 v 才是普通值
- **`sorted()` 与 `sort()` 混淆**：前者返回新数组，后者原地修改且要求 var

## 相关文档

- 📄 [01-swift-keywords.md](./01-swift-keywords.md) — guard/if 等关键字语义
- 📄 [05-protocols-generics.md](./05-protocols-generics.md) — Sequence/Collection 协议体系
- 📄 [01-foundation-and-stdlib.md](../library-guides/01-foundation-and-stdlib.md) — Foundation 类型补充


<!-- full-library-explanation -->
## Optional 表达哪一种缺失

`Int("abc")` 返回 nil 可以表示解析失败；字典找不到键也返回 nil，但原因不同。不要一律用 `?? 0` 抹掉差别。若加载可能失败且错误需要展示，使用 throws 或枚举，而不是把所有失败都压成 nil。

```swift
let texts = ["1", "bad", "3"]
let parsed = texts.map(Int.init)       // [Int?]，保留输入位置
let valid = texts.compactMap(Int.init) // [Int]，丢弃失败项
print(parsed.count, valid.count)       // 3 2
```

以下完整 Swift 标准库程序把 Optional、`map`、`compactMap` 和 Dictionary 缺键语义放在一个可复跑的契约中。它只覆盖语言与标准库；不覆盖 SwiftUI 的视图更新。

<!-- p1-runtime-case: swift-optionals-collections -->
```swift
let texts = ["1", "bad", "3"]
let parsed = texts.map(Int.init)
let valid = texts.compactMap(Int.init)
var scores = ["alice": 90]

precondition(parsed.count == 3)
precondition(parsed[1] == nil)
precondition(valid == [1, 3])
precondition(scores["nobody"] == nil)
scores["alice"] = nil
precondition(scores["alice"] == nil)
print("Swift optional and collection contracts passed")
```

练习：为导入清单保留每个失败项的行号和原因。验收：不能用 compactMap 静默删除坏数据后宣布“全部导入成功”。另测字典值本身为 Optional 时的缺键与存储 nil，必要时用 updateValue 或显式枚举表达。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
