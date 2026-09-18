# Swift 正则（Regex 与 RegexBuilder）

> **文档简介**: Swift 原生正则全量速查：Regex 字面量、运行时构造与 RegexBuilder、命名捕获与 TryCapture、String 匹配/替换方法、与 NSRegularExpression 的关系及 Swift 6 并发语义
>
> **目标读者**: 需要在 Swift 中做文本提取/校验/替换的全体学习者（字典条目，可任意跳入）
>
> **前置知识**: String 基础见 [../library-guides/01-foundation-and-stdlib.md](../library-guides/01-foundation-and-stdlib.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Regex` `#正则` `#RegexBuilder` `#字符串` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

`Regex` 是 Swift 5.7（iOS 16+）引入的原生正则类型：既支持**编译期校验**的正则字面量，也支持 `RegexBuilder` 的可组合 DSL，捕获结果带类型（可直接转 `Int`/`Date`），不需要 Foundation 的字符串范围桥接。

---

## 1. 两种写法：字面量与 RegexBuilder

| 写法 | 形式 | 校验时机 | 适用 |
|------|------|----------|------|
| 正则字面量 | `let re = /[a-z]+/` | **编译期**（写错即编译错误） | 短模式、模式固定 |
| 运行时构造 | `try Regex("[a-z]+")` | 运行时 throwing | 模式来自用户/配置 |
| RegexBuilder | `Regex { "v"; OneOrMore(.digit) }` | 编译期 + 类型化捕获 | 复杂模式、需要转换捕获 |

```swift
let version = /\d+\.\d+/                    // 字面量：斜杠包裹
let runtime = try Regex(#"\d+\.\d+"#)       // 运行时：构造器 throws

// RegexBuilder 等价形式
import RegexBuilder

let builder = Regex {
    OneOrMore(.digit)
    "."
    OneOrMore(.digit)
}
```

字面量里的语法错误在**编译期**报错——这是原生 Regex 相对旧方案的最大体验提升。

## 2. 匹配方法（String 上的 Regex API）

| 方法 | 返回 | 用途 |
|------|------|------|
| `str.firstMatch(of: re)` | `Regex.Match?` | 第一个匹配 |
| `str.wholeMatch(of: re)` | `Regex.Match?` | 整串必须完全匹配（校验场景） |
| `str.prefixMatch(of: re)` | `Regex.Match?` | 从头匹配前缀 |
| `str.matches(of: re)` | `[Regex.Match]` 序列 | 全部匹配 |
| `str.contains(re)` | `Bool` | 是否存在匹配 |
| `str.split(separator: re)` | `[Substring]` | 按正则切分 |
| `str.replacing(re) { m in ... }` | `String` | 闭包替换全部匹配（替换语法见下方专项说明） |

```swift
let log = "req=42ms cost=108ms"
if let m = log.firstMatch(of: /cost=(\d+)/) {
    m.0              // "cost=108"（.0 恒为整段匹配；\d+ 在 "ms" 前停止）
    m.1              // "108"（第一个捕获组）
}
log.wholeMatch(of: /\d+/)      // nil：整串不是纯数字
log.split(separator: /\s+/)    // 按空白切分
```

**替换**：`replacing(_:with:)` 的 `with:` **不是模板字符串**（签名见 SE-0357），有两个重载——**闭包**（拿到 Match 自行拼串）与**字符集合替换值**（例如 String）；匹配参数才是 RegexComponent：

```swift
// ① 闭包形式：捕获直接取用，类型安全
let masked = "13812345678".replacing(/(\d{3})\d{4}(\d{4})/) { m in
    "\(m.1)****\(m.2)"          // "138****5678"
}

// ② 字符串替换值：直接插入 +
let cleaned = "a-b-c".replacing(/-/, with: "+")   // "a+b+c"

// ③ 需要 "$1" 模板语法 → 走 Foundation ICU 路径（见 §5）
let masked2 = "13812345678".replacingOccurrences(
    of: "(\\d{3})\\d{4}(\\d{4})",
    with: "$1****$2",
    options: .regularExpression)  // "138****5678"
```

原生 Regex API **不支持** `$1`/`${name}` 替换模板——这是与 PCRE 系语言（JS/Go/Java/PHP）的常见差异点。

## 3. 捕获：无名 / 命名 / 类型转换

```swift
// ① 无名捕获：按元组顺序取（.0 整段，.1 起为捕获组）
let date = "2026-09-18"
if let m = date.firstMatch(of: /(\d{4})-(\d{2})-(\d{2})/) {
    m.1   // 年
}

// ② 命名捕获：(?<name>...)，Match 上直接按名访问
if let m = date.firstMatch(of: /(?<year>\d{4})-(?<month>\d{2})/) {
    "\(m.year) 年 \(m.month) 月"      // m.year 直接可用
}
```

RegexBuilder 的核心构件（均自 Swift 5.7）：

| 构件 | 职责 |
|------|------|
| `Capture { ... }` | 捕获，`transform:` 闭包做类型转换（如 `Int.init`） |
| `TryCapture { ... }` | 转换可能失败的捕获：transform 返回 nil 表示该捕获转换失败；抛错与回溯不是同一概念，应按所用匹配 API 的错误规则处理 |
| `One(...)` / `ChoiceOf { ... }` | 精确一次 / 多选一分支 |
| `Optionally(...)` / `ZeroOrMore(...)` / `OneOrMore(...)` | 可选 / 任意次 / 一次以上 |
| `Repeat(count:)` / `Repeat(count:...limit:)` | 指定次数区间 |
| `Anchor.startOfLine` / `.endOfLine` | 行首/行尾锚点 |

```swift
let quantity = Regex {
    TryCapture { OneOrMore(.digit) } transform: { Int($0) }   // 数字超出 Int 范围时转换也可能失败
    "x"
    ChoiceOf {
        "small"; "large"
    }
}
if let m = "3xlarge".firstMatch(of: quantity) {
    m.1    // 3（Int 类型，非 String）
}
```

**贪婪语义**: 量词默认贪婪（eager），可改惰性。注意 `repetitionBehavior(_:)` 是**整体 `Regex`** 上的方法（`extension Regex`），不能挂在单个构件上；组件侧改惰性用量词的构造参数：

```swift
import RegexBuilder

// ✅ ① 链式：挂在整体 Regex 上
let lazy1 = Regex {
    OneOrMore(.digit)
    "ms"
}.repetitionBehavior(.reluctant)

// ✅ ② 组件侧等价写法：量词构造参数
let lazy2 = Regex {
    OneOrMore(.digit, .reluctant)
    "ms"
}

// ❌ OneOrMore(.digit).repetitionBehavior(.reluctant)
//    组件对象没有 repetitionBehavior 成员，编译错误
```

## 4. Swift 6 语义与并发

- 不要假设任意 Regex、捕获输出和变换闭包都能跨隔离域传递；以实际 SDK 的 Sendable 约束及编译器诊断为准，必要时在工作域构造模式，只返回可发送的解析结果。
- 字面量可以在编译期检查模式；不要据此承诺整个匹配过程没有运行时开销。动态模式应避免在热循环中重复构造。
- `Regex` 输出类型默认 `AnyRegexOutput`；字面量与 RegexBuilder 构造的 Regex 捕获是强类型的。

## 5. 与 NSRegularExpression 的关系

| 维度 | Regex（Swift 5.7+） | NSRegularExpression（Foundation/ICU） |
|------|---------------------|---------------------------------------|
| 语法校验 | 字面量编译期 | 运行时 throwing 构造 |
| 捕获结果 | 类型化元组/属性 | `NSTextCheckingResult`（range 手动切） |
| 引擎 | Swift 原生实现 | ICU |
| 定位 | `firstMatch(of:)` 等 String 方法 | `firstMatch(in:options:range:)`（NSRange） |

**结论**: 支持部署目标且类型化捕获有价值时优先考虑原生 Regex；兼容旧系统或需要 ICU 语义时可选择 `NSRegularExpression`。Foundation 的 `range(of:options: .regularExpression)` / `replacingOccurrences(of:options:)` 走的是 ICU 旧路径，别与原生 Regex API 混用。

## ⚠️ 常见陷阱

- ❌ **把字面量正则当字符串再转义**：`/\d+/` 不是 `"\\d+"`——字面量内不需要双反斜杠
  ✅ 字面量写 `\d`；只有 `try Regex("...")` 字符串路径才需要转义。
- ❌ **把 `"$1"` 字符串当替换模板**：`replacing(re, with: "$1")` 会插入字面文本 `$1`，不是捕获组引用
  ✅ 闭包形式 `replacing(re) { m in ... }` 引用捕获，或 Foundation `replacingOccurrences(of:with:options: .regularExpression)` 的 ICU 模板。
- ❌ **用 `firstMatch` 做整串校验**：不带整串边界的 `/\d+/` 会在包含其他文本的字符串里找到一段数字
  ✅ 校验场景用 `wholeMatch(of:)`（此时也不需要手写 `^$`）。
- ❌ **捕获下标越界当 Optional 用**：`m.3` 超出捕获数是编译错误，不是 nil
  ✅ 捕获数量由模式决定，命名捕获比裸数字可读得多。
- ❌ **混淆两套引擎的索引与替换语法**：NSRegularExpression 使用 UTF-16 的 NSRange
  ✅ 按部署目标选引擎；NSRange 转换使用 Range(nsRange, in: text)，不要拿整数直接下标 Swift String。

<!-- full-library-explanation -->
## 一次练习串起匹配、捕获与替换

先定义输入，再分别问“有没有编号”“整串是不是编号”“如何隐藏编号”，避免把提取规则误当验证规则。

```swift
let text = "order=42; other=7"
let rule = /order=(\d+)/
print(text.firstMatch(of: rule) != nil) // true
print(text.wholeMatch(of: rule) != nil) // false
print(text.replacing(rule) { "order=[\($0.1)]" })
// order=[42]; other=7
print("42".replacing(/\d+/, with: "$1")) // 字面文本 $1
```

若输入是用户提供的模式，构造失败应向用户报告格式问题；若输入是用户提供的待匹配文本，则还要限制长度与复杂模式，避免在 UI 线程处理不可控工作。格式正确不等于业务值有效，例如日期数字匹配后仍需检查月份和实际历法。

验收：测试空串、`order=abc`、`order=42`、`x order=42 y` 四种输入，分别记录 firstMatch 与 wholeMatch 的结果；最后解释为什么 `$1` 不会自动取第一组。API 签名核对依据：[SE-0357](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0357-regex-string-processing-algorithms.md)。本轮没有 Swift 工具链运行记录。

## 🔗 相关条目

- 📄 **[01-foundation-and-stdlib.md](../library-guides/01-foundation-and-stdlib.md)** - String/Date 基础速查（§1 文本）
- 📄 **[16-stdlib-foundation-map.md](./16-stdlib-foundation-map.md)** - 系统框架低频地图
- 🌐 **[官方文档：Regex](https://developer.apple.com/documentation/swift/regex)** - Apple 开发者文档
- 🌐 **[swift.org：Embracing Swift Regex](https://swift.org/blog/regex/)** - Swift 官方博客 Regex 综述

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
