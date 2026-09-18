# Foundation 与标准库核心速查

> **文档简介**: Swift 标准库与 Foundation 框架中 iOS 开发高频类型的条目式参考：字符串、日期、格式化、JSON 编解码与系统工具
>
> **目标读者**: 需要查阅基础类型 API 的全体学习者
>
> **前置知识**: 无；集合类型详见 [02-optionals-collections.md](../language-concepts/02-optionals-collections.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#Foundation` `#标准库` `#String` `#Date` `#Codable` |
| **更新日期** | `2026年9月` |

</details>

---

## 1. String 与文本

### 1.1 基础操作

```swift
let s = "  Hello, Swift  "
s.trimmingCharacters(in: .whitespacesAndNewlines)   // "Hello, Swift"
s.isEmpty; s.count                                   // 字符数（非字节数）
s.lowercased(); s.uppercased()
s.hasPrefix("  He"); s.hasSuffix("ft  ")
s.replacingOccurrences(of: "Swift", with: "World")
```

### 1.2 插值与拼接

```swift
let name = "路"; let score = 92.456
"\(name) 得分 \(Int(score))"                          // 基础插值
String(format: "%.2f 分", score)                      // C 风格格式化
score.formatted(.number.precision(.fractionLength(2))) // "92.46"
```

### 1.3 本地化数字/单位（iOS 16+ FormatStyle）

```swift
12345.formatted()                                   // 按区域格式化
12345.formatted(.number.grouping(.never))
let price = Decimal(string: "49.9")! // 固定合法示例；用户输入应 guard let
price.formatted(.currency(code: "CNY"))             // ¥49.90
Duration.seconds(1200).formatted(.units(allowed: [.minutes]))                              // "20 分钟"
```

---

## 2. Date 与日历

### 2.1 创建与比较

```swift
let now = Date.now
let later = now.addingTimeInterval(3600)            // +1 小时
later > now                                          // true
now.timeIntervalSince(later)                         // -3600
```

### 2.2 Calendar 组件运算

```swift
let cal = Calendar.current
cal.component(.hour, from: now)                      // 取小时
cal.isDateInToday(now); cal.isDateInWeekend(now)
cal.startOfDay(for: now)                             // 当天零点
cal.date(byAdding: .day, value: 7, to: now)!         // 加 7 天
```

### 2.3 格式化

```swift
now.formatted(date: .abbreviated, time: .shortened)  // "2026年9月10日 14:30"
now.formatted(.dateTime.year().month().day())        // 链式选择组件
now.formatted(.relative(presentation: .named))       // "今天"
```

**陷阱**: `DateFormatter` 创建开销大——缓存复用，不要在 ForEach 循环里新建；能换 FormatStyle 就换。

---

## 3. Codable：JSON 编解码

### 3.1 基本编解码

```swift
struct User: Codable {
    let id: Int
    let name: String
    let avatarURL: URL?          // URL 类型自动解析字符串
}

let original = User(id: 1, name: "小林", avatarURL: nil)
let data = try JSONEncoder().encode(original)
let user = try JSONDecoder().decode(User.self, from: data)
```

### 3.2 键名策略与自定义

```swift
struct Repo: Codable {
    let starCount: Int
    let fullName: String

    enum CodingKeys: String, CodingKey {
        case starCount = "stargazers_count"   // 服务端蛇形命名
        case fullName = "full_name"
    }
}

// 或全局策略
let decoder = JSONDecoder()
decoder.keyDecodingStrategy = .convertFromSnakeCase
```

### 3.3 嵌套与默认值

```swift
struct Payload: Codable {
    let users: [User]
}
// 解码失败排查：匹配 DecodingError 并检查 context.codingPath；localizedDescription 不保证给出完整路径
```

**陷阱**: Swift 的 Codable 无"缺失键给默认值"——服务器可能省略的字段要声明为 Optional，或手写 `init(from:)`。

---

## 4. 常用 Foundation 工具

### 4.1 UUID、UserDefaults、FileManager

```swift
UUID().uuidString                       // 唯一标识（ForEach id、模型主键）

UserDefaults.standard.set("dark", forKey: "theme")
let theme = UserDefaults.standard.string(forKey: "theme")   // Optional
@AppStorage("theme") var theme = "system"                   // SwiftUI 侧

let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
try? "日志".write(to: docs.appending(path: "log.txt"), atomically: true, encoding: .utf8)
```

### 4.2 Bundle 与资源

```swift
Bundle.main.url(forResource: "config", withExtension: "json")
let text = try String(contentsOf: fileURL, encoding: .utf8)
```

---

## 5. 标准库与 Foundation 补充

| 类型/函数 | 用途 | 示例 |
|-----------|------|------|
| `Measurement` | 带单位量值 | `Measurement(value: 5, unit: UnitLength.kilometers)` |
| `Decimal` | 精确小数（金额） | 避免 Double 误差 |
| `Duration` | 时长 | `.seconds(2)`；配合 Task.sleep |
| `RandomNumberGenerator` | 随机 | `Int.random(in: 1...100)` |
| `assert / precondition / fatalError` | 断言 | debug/release 差异 |

## ⚠️ 高频陷阱速查

- **String.count ≠ 字节数**：含 emoji 时 UTF-8 长度远大于 count；网络传输量看 `utf8.count`
- **DateFormatter 线程与开销**：实例缓存复用；接口约定 ISO 8601 时使用相应解析器；用户本地化日期应按实际 Locale 与格式解析
- **Double 存金额**：用 Decimal 或以"分"为单位的 Int
- **URL(string:) 返回 Optional**：合法输入也用 `guard let` 解包，硬解包 `!` 是崩溃源
- **UserDefaults 存大对象**：只存配置小值；结构化数据进 SwiftData/文件

## 相关文档

- 📄 [02-optionals-collections.md](../language-concepts/02-optionals-collections.md) — Array/Dictionary/Set 全表
- 📄 [02-third-party-libs.md](./02-third-party-libs.md) — 三方库生态
- 📄 [03-concurrency-api.md](../language-concepts/03-concurrency-api.md) — 异步 IO 与 Foundation 的配合


<!-- full-library-explanation -->
## 把文本与 JSON 当不可信输入处理

```swift
import Foundation

struct Profile: Decodable {
    let name: String
    let visits: Int
    enum CodingKeys: String, CodingKey { case name, visits }
    init(from decoder: Decoder) throws {
        let values = try decoder.container(keyedBy: CodingKeys.self)
        name = try values.decode(String.self, forKey: .name)
        visits = try values.decodeIfPresent(Int.self, forKey: .visits) ?? 0
    }
}
let input = Data(#"{"name":"小林"}"#.utf8)
let profile = try JSONDecoder().decode(Profile.self, from: input)
print(profile.name, profile.visits) // 小林 0
```

把 visits 改为字符串 `"many"` 时应解码失败，不能用缺省值掩盖类型错误。捕获 DecodingError 后查看其 context.codingPath、debugDescription；不要把包含用户原文的整个 payload 打进日志。默认属性值不等于合成 Decodable 会在缺键时自动采用该值。

String 的索引使用 String.Index，字符、UTF-16 单元和 UTF-8 字节长度并不相等。日期存储与传输约定应固定，显示则按 Locale/Calendar/时区格式化；“明天同一当地时刻”使用日历运算，不一定等于加 86400 秒。金额从十进制字符串或整数最小单位进入，避免先经过 Double 再期待 Decimal 消除已经发生的误差。

验收：包含 emoji 的姓名不被截断、缺省访问数为 0、错误类型报告失败、跨夏令时日期仍符合产品约定。本轮没有 Swift 运行记录。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
