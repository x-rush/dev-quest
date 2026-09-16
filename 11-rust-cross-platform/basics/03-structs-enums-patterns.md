# 结构体、枚举与模式匹配

> **文档简介**: 用 struct 组织数据、用 enum 建模"有限的可能性"、用 match 穷尽处理每一种情况——Rust 数据建模三件套，也是理解 Option/Result 的前置。
>
> **目标读者**: 已理解所有权与借用基本规则的 Rust 初学者
>
> **前置知识**: [01 环境搭建](./01-environment-setup.md)、[02 所有权与借用](./02-ownership-borrowing.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#rust` `#struct` `#enum` `#pattern-matching` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

- ✅ **掌握核心概念**: 结构体三种形态与 impl 方法、枚举作为"和类型"的建模能力、match 的穷尽性检查
- ✅ **实践能力**: 用枚举给业务状态建模，写出编译器保证不漏分支的处理逻辑
- ✅ **解决问题**: 告别 null 判断混乱与 switch 漏分支——`Option<T>` 与 match 是系统化解法
- ✅ **进阶方向**: 为 [04 trait 与泛型](./04-traits-generics.md) 和 [05 错误处理](./05-error-handling.md)（Result 就是枚举）打底

## 📋 目录

- [核心概念](#核心概念)
- [实践指南](#实践指南)
- [代码示例](#代码示例)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)
- [交叉引用](#交叉引用)
- [总结](#总结)

---

## 🔍 核心概念

### 概念一：结构体 —— 数据的组织单元

**定义**: struct 把若干相关字段组织成一个自定义类型，`impl` 块为其附加关联函数与方法，角色类似其他语言的 class（但没有继承）。

**三种形态**:
- **具名字段结构体**: `struct App { name: String, stars: u32 }`——绝大多数场景用这个
- **元组结构体**: `struct Point(f64, f64)`——字段少且不需要名字时
- **单元结构体**: `struct Marker;`——只作为类型标记，不存数据

**关键特性**:
- 方法第一参数是所有权视角：`&self` 只读、`&mut self` 可写、`self` 消费自身（正是 02 篇的借用规则）
- 无 `new` 关键字：惯例用一个无 `self` 的**关联函数**充当构造器
- 字段默认私有，跨模块暴露需要 `pub`（工程化内容后续篇目展开）

**使用场景**:
- 场景一：领域实体（用户、订单、配置项）的数据载体
- 场景二：为第三方数据源（JSON/API）定义映射结构

### 概念二：枚举 —— 有限可能性的建模

**定义**: enum 表示"值只能是若干变体之一"，且**每个变体可以携带不同类型的数据**。类型系统中称这类结构为"和类型"（sum type）。

**关键特性**:
- 变体携带数据的能力远强于 C 风格 enum：`Mobile { os: String }`、`Web(String)` 都合法
- 标准库两大核心类型 `Option<T>` 与 `Result<T, E>` 就是普通枚举——学会 enum 即学会错误处理的骨架
- 枚举同样可以实现方法、参与泛型

**使用场景**:
- 场景一：状态机（连接状态、订单状态）——每个状态携带各自的数据
- 场景二：消息协议（如本模块 Tauri IPC 的事件类型）——一个枚举穷举所有事件

### 概念三：Option —— "没有值"的一等公民

**定义**: `Option<T>` 是标准库枚举，只有 `Some(T)` 与 `None` 两个变体，显式表达"可能有值也可能没有"。

**关键特性**:
- Rust 没有 null：空缺被建模为类型，编译器强制你在用值之前处理 `None`
- 取值四件套：`match`（全覆盖）、`if let`（只关心有值）、`unwrap_or`（兜底默认值）、`let else`（无值提前退出）
- 彻底消除"空引用调用"这类运行时崩溃（即所谓"十亿美元错误"）

### 概念四：match —— 穷尽性检查的表达力

**定义**: match 将一个值与一系列模式比较并执行首个命中的分支，编译器**强制所有可能情况都被覆盖**。

**关键特性**:
- **穷尽性**: 枚举每新增一个变体，所有未覆盖它的 match 都会编译报错——重构免费的完整性保障
- **解构**: 模式可以直接拆开变体携带的数据（`Move { x, y }`）
- **匹配守卫**: 分支后追加 `if` 条件做进一步过滤
- 必须返回同一类型——match 本身是表达式，有值

---

## 🛠️ 实践指南

### 步骤一：建模一个跨平台应用的目标平台

**目标**: 用枚举完成一次真实的领域建模（呼应本模块 Tauri 2 跨端方向）。

**操作指南**:
1. `cargo new platform-model && cd platform-model`
2. 定义 `Platform` 枚举（可直接采用下方示例二的定义）
3. 实现 `name(&self) -> &str` 方法，用 match 覆盖全部变体
4. 新增一个变体（比如 `Watch`），先不更新 match——观察编译器如何指出**每一个**遗漏的位置
5. 补全分支直到编译通过

**验证方法**: `cargo run` 输出所有目标平台名；故意漏分支时能读到编译器的穷尽性报错

### 步骤二：用 Option 重构一次"返回 -1 表示找不到"

**目标**: 把哨兵值风格（返回 -1/null）改成 `Option` 风格。

**操作指南**:
1. 写一个在数组中查找目标的函数，初版返回 `i32`，找不到返回 `-1`
2. 改签名为 `fn find(numbers: &[i32], target: i32) -> Option<i32>`
3. 在调用侧分别用 `match`、`unwrap_or` 处理，感受"空值是类型而非魔法数"

**验证方法**: 调用侧不存在任何与 -1 比较的代码

---

## 💻 代码示例

> 以下四段示例均已在本机以 `rustc --edition 2024` 实测编译并运行通过。

### 示例一：结构体与 impl

```rust
// 结构体：把相关数据组织在一起
struct App {
    name: String,
    version: String,
    stars: u32,
}

// impl 块为结构体实现关联函数与方法（类似其他语言的类方法）
impl App {
    // 关联函数（没有 self），通常作为构造器
    fn new(name: &str, version: &str) -> Self {
        Self {
            name: name.to_string(),
            version: version.to_string(),
            stars: 0,
        }
    }

    // 方法：&self 只读借用
    fn describe(&self) -> String {
        format!("{} v{} ({} stars)", self.name, self.version, self.stars)
    }

    // 方法：&mut self 可变借用
    fn add_star(&mut self) {
        self.stars += 1;
    }
}

fn main() {
    let mut app = App::new("dev-quest", "0.1.0");
    app.add_star();
    app.add_star();
    println!("{}", app.describe());
}
```

**关键点解析**:
- `new` 是关联函数：通过 `App::new(...)` 调用，无 `self` 参数
- 三个方法的 `self` 形态分别演示了"构造返回 Self / 只读 / 可写"三种所有权视角
- 字段接 `String`（拥有数据）而构造器接 `&str`（借用传入），是 02 篇"参数优先借用"惯例的直接应用

### 示例二：枚举与穷尽 match

```rust
// 枚举：值只能是有限变体之一，每个变体可携带不同数据
enum Platform {
    Windows,
    MacOS,
    Linux,
    Mobile { os: String }, // 类结构体变体
    Web(String),           // 类元组变体
}

// 枚举上同样可以实现方法
impl Platform {
    fn name(&self) -> &str {
        match self {
            Platform::Windows => "Windows",
            Platform::MacOS => "macOS",
            Platform::Linux => "Linux",
            Platform::Mobile { os } => os,
            Platform::Web(framework) => framework,
        }
    }
}

fn main() {
    let targets = [
        Platform::Windows,
        Platform::MacOS,
        Platform::Linux,
        Platform::Mobile { os: String::from("iOS") },
        Platform::Web(String::from("wasm")),
    ];

    for p in &targets {
        println!("目标平台: {}", p.name());
    }
}
```

**关键点解析**:
- 三种变体形态同框：无数据、类结构体（命名字段）、类元组（带一个值）
- match 直接解构变体数据：`os`、`framework` 都是新绑定
- 删掉任何一个分支试试——编译器会报"非穷尽匹配"，这就是枚举建模的安全性来源

### 示例三：Option 的四种处理方式

```rust
// 在列表中查找：Rust 用 Option 表达"可能有值也可能没有"
fn find_even(numbers: &[i32]) -> Option<i32> {
    for &n in numbers {
        if n % 2 == 0 {
            return Some(n);
        }
    }
    None
}

fn main() {
    // 方式一：match 全覆盖处理两种情况
    match find_even(&[1, 3, 5]) {
        Some(n) => println!("找到偶数: {n}"),
        None => println!("列表中没有偶数"),
    }

    // 方式二：if let 只关心"有值"的情况
    if let Some(n) = find_even(&[2, 4]) {
        println!("第一个偶数: {n}");
    }

    // 方式三：unwrap_or 提供默认值兜底
    let n = find_even(&[1, 3]).unwrap_or(-1);
    println!("默认值兜底: {n}");

    // 方式四：let else —— 没有值就提前退出当前函数
    let Some(n) = find_even(&[8]) else {
        println!("没有偶数，直接结束");
        return;
    };
    println!("let else 拿到: {n}");
}
```

**关键点解析**:
- 返回 `Option<i32>` 把"可能找不到"写进类型签名，调用方无法假装没看见
- 四种取值方式按场景选用：全覆盖用 match、单分支用 if let / let else、有默认值用 unwrap_or
- `find_even(&[1, 3, 5])` 直接传数组字面量：参数是 `&[i32]`（切片），比 `&Vec<i32>` 更通用

### 示例四：match 的高级模式

```rust
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(u8, u8, u8),
}

fn process(msg: &Message) -> String {
    match msg {
        // 单元变体
        Message::Quit => String::from("退出程序"),
        // 解构命名字段 + 匹配守卫
        Message::Move { x, y } if *x == 0 && *y == 0 => String::from("原地不动"),
        Message::Move { x, y } => format!("移动到 ({x}, {y})"),
        // 解构类元组变体
        Message::Write(text) => format!("写入: {text}"),
        Message::ChangeColor(r, g, b) => format!("调色 rgb({r},{g},{b})"),
    }
}

fn main() {
    let msgs = [
        Message::Quit,
        Message::Move { x: 0, y: 0 },
        Message::Move { x: 10, y: -3 },
        Message::Write(String::from("你好")),
        Message::ChangeColor(255, 128, 0),
    ];

    for m in &msgs {
        println!("{}", process(m));
    }
}
```

**关键点解析**:
- 同一变体可以出现多个分支：先匹配更特殊的（守卫 `if *x == 0 && *y == 0`），再匹配一般的
- `msg` 是 `&Message`，模式中的绑定自动成为引用（`*x` 解引用）——匹配借用值不需要额外动作
- 顺序敏感：守卫分支必须在通配的 `Move` 分支之前

---

## 🎨 最佳实践

### ✅ 推荐做法
- **derive(Debug) 作为默认起点**: 结构体与枚举第一行都加 `#[derive(Debug)]`，随时可用 `{var:?}` 打印
- **信任穷尽性检查**: 新增枚举变体后按编译器提示逐处补分支，而不是加 `_ =>` 通配逃逸
- **按场景选 Option 取值方式**: 需要两种情况都处理用 match；单分支用 if let / let else；有兜底值用 unwrap_or 系列方法

### ❌ 避免陷阱
- **生产代码裸 `unwrap()`**: 在 `Option`/`Result` 上直接 unwrap，None/Err 时立刻 panic——原型可以，工程不行
- **用 bool/魔法数模拟状态**: `is_done + is_failed + is_archived` 三个 bool 的组合爆炸，不如一个三变体枚举
- **match 分支返回不同类型**: match 是表达式，所有分支必须同类型；需要不同行为时把差异装进枚举或字符串里

---

## ❓ 常见问题

### Q1: match 与 if/else 的本质区别？
**A**: ① match 有穷尽性检查，漏情况编译不过，if/else 没有；② match 能解构数据（把变体里的字段直接绑定为新变量）；③ match 是表达式有返回值。凡是"按值的形态分发"的场景，match 都是更安全的选择。

### Q2: 枚举变体各自携带不同类型的数据，会不会很乱？
**A**: 恰恰相反——这正是 Rust 枚举强于传统 enum 的地方。每个变体是独立的"小结构体"，match 解构后各自拿到正确类型的绑定，编译器全程把关。消息协议、状态机、AST 节点都是典型受益场景。

### Q3: match 匹配 `&Message` 时为什么模式里不用写 `&`？
**A**: 匹配引用时模式会自动"穿透"引用进行绑定（绑定成为引用本身），因此示例中 `*x` 需要解引用后比较。这种默认行为让多数 match 代码保持简洁；需要所有权转移的复杂场景会在后续篇目中展开。

---

## 🔗 交叉引用

### 本模块
- 📄 **[02 所有权与借用](./02-ownership-borrowing.md)** — 方法接收器 `&self / &mut self / self` 的规则来源
- 📄 **[04 trait 与泛型](./04-traits-generics.md)** — 给自定义类型附加共享行为
- 📄 **[05 错误处理](./05-error-handling.md)** — `Result<T, E>` 就是一个带两个变体的枚举
- 📖 **[模块 README](../README.md)** — 本篇在入门路径 01→05 中的位置

---

## 📝 总结

### 核心要点回顾
1. **struct + impl**: 具名字段结构体是默认选择，构造器是惯例而非关键字
2. **enum 是和类型**: 变体可携带数据，`Option`/`Result` 都由它构成
3. **match 的穷尽性**: 漏分支编译不过，新增变体的重构成本被编译器兜底
4. **没有 null**: "没有值"是 `Option<T>`，四种取值方式按场景选用

### 学习成果检查
- [ ] 能说出三种结构体形态及适用场景
- [ ] 能用枚举为一个业务状态建模并穷尽处理
- [ ] 四种 Option 取值方式信手拈来且知道各自适用场景
- [ ] 理解"穷尽性检查是免费的完整性保障"这句话的含义

---

**最后更新**: 2026年9月

> 🎯 **下一步**: 类型会定义了，接着学习 [04 trait 与泛型](./04-traits-generics.md)——让不同的类型共享同一套行为契约。
