# trait 与泛型

## 先理解，再动手

trait 描述类型必须提供的能力，泛型把实现留到使用具体类型时组合。先有两个实现，再理解抽象解决了哪份重复。

**本节自测**：给两种类型实现同一描述能力，写只依赖 trait 的打印函数。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

调用者不需要识别具体类型；无法实现的方法要求说明抽象边界不合适。

</details>

> **文档简介**: 用 trait 定义类型的行为契约，用泛型写出编译期零成本的抽象，理解静态分发（泛型单态化）与动态分发（trait 对象）的取舍。
>
> **目标读者**: 已掌握结构体与枚举、想写出可复用抽象的 Rust 学习者
>
> **前置知识**: [03 结构体、枚举与模式匹配](./03-structs-enums-patterns.md)；[02 所有权与借用](./02-ownership-borrowing.md) 中的借用参数习惯

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 教程 |
| **难度** | ⭐⭐ |
| **标签** | `#rust` `#trait` `#generics` `#abstraction` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

- ✅ **掌握核心概念**: trait 契约、默认方法、泛型与 trait bound、`impl Trait`、trait 对象 `dyn Trait`
- ✅ **实践能力**: 定义自己的 trait 并为多个类型实现；按"同构/异构"选型泛型或 trait 对象
- ✅ **解决问题**: 理解 derive 自动实现的来龙去脉，不再把 `#[derive(Debug)]` 当魔法
- ✅ **进阶方向**: [05 错误处理](./05-error-handling.md) 的 `From` 转换与本篇直接相关；动态分发细则见字典篇目

## 📋 目录

- [核心概念](#-核心概念)
- [实践指南](#️-实践指南)
- [代码示例](#-代码示例)
- [最佳实践](#-最佳实践)
- [常见问题](#-常见问题)
- [交叉引用](#-交叉引用)
- [总结](#-总结)

---

## 🔍 核心概念

### 概念一：trait —— 行为契约

**定义**: trait 声明一组类型必须（或可以选择）提供的方法。某个类型用 `impl Trait for Type` 声明"我实现了这套契约"。

**关键特性**:
- 角色对标 TypeScript/Java 的 interface、Go 的 interface，但 trait 可带**默认方法**，实现者只补差异
- 实现位置受**孤儿规则**约束：trait 或类型的定义 crate 之一必须是你自己的，防止生态冲突
- trait 方法天然与所有权系统协作：接收器的 `&self / &mut self / self` 遵循 02 篇的借用规则

**使用场景**:
- 场景一：为不同存储后端（本地/云）定义统一的 `save` 契约
- 场景二：库的扩展点——用户实现你的 trait 即可接入你的框架流程

### 概念二：泛型与 trait bound —— 编译期抽象

**定义**: 泛型函数/类型对"满足某 trait 的任意类型"工作；trait bound（如 `T: PartialOrd`）约束了泛型参数必须具备的能力。

**关键特性**:
- 编译器对每个具体类型**单态化**（monomorphization）：生成专用代码，运行时无间接跳转——"零成本抽象"
- bound 写在尖括号里（短）或 `where` 子句里（长而清晰），表达力相同
- 没有 bound 的泛型（如 `fn id<T>(x: T)`）几乎什么都做不了——能力全部来自 bound

### 概念三：impl Trait —— bound 的语法糖

**定义**: 参数位置的 `impl Trait`（如 `fn f(x: impl Display)`）是泛型 bound 的简写；返回位置的 `impl Trait` 表示"返回某个实现了该 trait 的具体类型，但调用方不需要知道是哪个"。

**关键特性**:
- 参数位置：与显式泛型等价，写起来更顺
- 返回位置：隐藏具体类型，API 更稳定；代价是调用方只能依赖声明的 trait 能力

### 概念四：trait 对象 dyn Trait —— 运行时分发

**定义**: `&dyn Trait` / `Box<dyn Trait>` 存放"任意实现了 Trait 的值"，通过虚表在**运行时**分发方法调用。

**关键特性**:
- 集合里可以混放不同类型（`Vec<Box<dyn Storage>>`）——泛型做不到这一点
- 代价：每次调用经过一次间接跳转，编译器失去单态化优化机会
- 与泛型的选择标准：**同构集合/追求极致性能 → 泛型；异构集合/插件式扩展 → dyn Trait**

### 概念五：derive —— 自动实现标准 trait

**定义**: `#[derive(Debug, Clone, ...)]` 让编译器为类型自动生成常用标准 trait 的实现，消除样板代码。

**关键特性**:
- 高频成员：`Debug`（{:?} 打印）、`Clone`（显式深拷贝）、`PartialEq`（== 比较）、`Default`、`Hash`、`Copy` 等
- derive 只对"全部字段都实现了该 trait"的类型生效——字段能力决定整体能力
- 第三方库也大量提供 derive 宏（如 05 篇的 thiserror），机制相同

---

## 🛠️ 实践指南

### 步骤一：为一个 trait 实现两个类型

**目标**: 体验"契约 + 多实现"的扩展方式。

**操作指南**:
1. `cargo new trait-lab && cd trait-lab`
2. 定义 `trait Storage { fn save(&self, key: &str); }`
3. 为 `LocalDisk` 和 `CloudBucket` 分别实现（可直接采用下方示例四）
4. 新增第三个实现（如 `MemoryCache`），加入 `Vec<Box<dyn Storage>>`——观察扩展过程不需要修改既有代码

**验证方法**: `cargo run` 依次输出每个后端的保存日志

### 步骤二：把具体函数泛型化

**目标**: 体会"先具体、后抽象"的重构路径。

**操作指南**:
1. 写 `fn max_i32(a: i32, b: i32) -> i32` 与 `fn max_str(a: &str, b: &str) -> &str`
2. 合并为 `fn max_of<T: PartialOrd>(a: T, b: T) -> T`
3. 对比三者的调用处，确认泛型版本无功能损失

**验证方法**: 同一个泛型函数分别传整数与字符串都能编译运行

---

## 💻 代码示例

> 以下四段是可用 `rustc --edition 2024` 复核的完整示例。请在自己的工具链中编译、运行，并记录实际版本和输出。

### 示例一：trait 定义、默认方法与覆写

```rust
// trait 定义一组行为契约
trait Describe {
    // 必须实现的方法
    fn name(&self) -> String;

    // 默认方法：实现者可以不覆写、直接使用
    fn summary(&self) -> String {
        format!("【{}】类型: {}", self.name(), std::any::type_name::<Self>())
    }
}

struct CliTool {
    name: String,
}

struct GuiApp {
    name: String,
    framework: String,
}

impl Describe for CliTool {
    fn name(&self) -> String {
        self.name.clone()
    }
    // summary 沿用默认实现
}

impl Describe for GuiApp {
    fn name(&self) -> String {
        format!("{}（{}）", self.name, self.framework)
    }

    // 也可以覆写默认实现
    fn summary(&self) -> String {
        format!("GUI 应用: {}", self.name())
    }
}

fn main() {
    let cli = CliTool { name: String::from("quest") };
    let gui = GuiApp {
        name: String::from("笔记"),
        framework: String::from("Tauri"),
    };

    println!("{}", cli.summary());
    println!("{}", gui.summary());
}
```

**关键点解析**:
- 契约最小化：必填的只有 `name`，`summary` 作为默认方法复用 `name` 组合出更大能力
- 默认方法能调用本 trait 的其他方法——这是设计"可扩展契约"的常用手法
- 覆写与否由实现者决定，调用方代码完全不变

### 示例二：derive 自动实现

```rust
// derive 自动实现常用 std trait，免去手写样板代码
#[derive(Debug, Clone, PartialEq)]
struct Task {
    title: String,
    done: bool,
}

fn main() {
    let t1 = Task { title: String::from("学完所有权"), done: false };

    // Debug：可以用 {:?} 打印（内插简写 {t1:?}）
    println!("{t1:?}");

    // Clone：显式深拷贝
    let t2 = t1.clone();

    // PartialEq：可以用 == 比较
    println!("t1 == t2? {}", t1 == t2);
}
```

**关键点解析**:
- 一行 derive 换来三个 trait 的完整实现——`Debug` 输出全部字段，`Clone` 递归拷贝，`PartialEq` 逐字段比较
- 02 篇的 `clone()` 能力正来自 `Clone` trait：标准库类型与你的自定义类型遵循同一套契约体系
- 若某字段不支持对应 trait（如含 f64 时不能用 `Eq`），derive 会直接编译报错说明原因

### 示例三：泛型、trait bound 与 where 子句

```rust
// 泛型函数 + trait bound：只接受支持比较的类型
fn max_of<T: PartialOrd>(a: T, b: T) -> T {
    if a >= b { a } else { b }
}

// where 子句：bound 较多时更可读
fn print_pair<T, U>(a: T, b: U)
where
    T: std::fmt::Debug,
    U: std::fmt::Debug,
{
    println!("a = {a:?}, b = {b:?}");
}

// 参数位置的 impl Trait：与泛型 bound 等价的语法糖（本例聚焦切片参数的常见形态）
fn count_long(words: &[String]) -> usize {
    words.iter().filter(|w| w.len() > 5).count()
}

fn main() {
    println!("{}", max_of(3, 7));
    println!("{}", max_of("apple", "banana"));

    print_pair("分数", 98);

    let words = vec![
        String::from("rust"),
        String::from("ownership"),
        String::from("borrow"),
    ];
    println!("超过 5 个字符的单词数: {}", count_long(&words));
}
```

**关键点解析**:
- `T: PartialOrd` 不写这个 bound，`>=` 直接编译失败——泛型的全部能力来自 bound
- 同一个 `max_of` 编译期被单态化成整数版与字符串版两份专用代码，运行时零分发开销
- `count_long` 接 `&[String]` 切片：借用参数 + 最宽接收类型，是 02 篇惯例与 03 篇切片知识的合流

### 示例四：trait 对象与异构集合

```rust
// trait 对象：运行期动态分发，同一集合容纳不同实现
trait Storage {
    fn save(&self, key: &str);
}

struct LocalDisk;
struct CloudBucket;

impl Storage for LocalDisk {
    fn save(&self, key: &str) {
        println!("[本地磁盘] 保存 {key}");
    }
}

impl Storage for CloudBucket {
    fn save(&self, key: &str) {
        println!("[云端对象存储] 上传 {key}");
    }
}

// Box<dyn Trait>：统一容纳不同类型
fn sync_all(storages: &[Box<dyn Storage>], key: &str) {
    for s in storages {
        s.save(key);
    }
}

fn main() {
    let storages: Vec<Box<dyn Storage>> =
        vec![Box::new(LocalDisk), Box::new(CloudBucket)];
    sync_all(&storages, "config.toml");
}
```

**关键点解析**:
- `Vec<Box<dyn Storage>>` 里可以同时放任意实现者——泛型集合只能装同一种类型
- `Box` 把不同大小的实现者统一到堆上的固定尺寸指针（trait 对象是胖指针：数据指针 + 虚表指针）
- 循环里的 `s.save(key)` 在运行时经虚表分发到各自实现

---

## 🎨 最佳实践

泛型用约束声明操作所需能力，dyn trait 对象允许运行时通过共同接口处理不同具体类型；选择还涉及代码体积、分发与所有权成本，不只是“性能好/坏”。先实现具体需求，再抽取确有复用价值的能力。

derive 遵循字段组成的默认语义，若 Debug 需脱敏或 PartialEq 要表达领域身份，手写实现可能必要。方法接收 self、&self 或 &mut self 分别表达消费、读取和修改责任，用调用者视角检查是否过度限制。

---

## ❓ 常见问题

### Q1: 泛型与 dyn Trait 到底怎么选？
**A**: 两个维度交叉判断：① 集合是否需要混放不同实现（需要 → dyn）；② 调用是否在热路径（是 → 泛型，避免虚表跳转）。两者都宽松时优先泛型——静态分发是 Rust 性能惯例；需要把实现者当参数跨 API 边界传递且类型不重要时，`impl Trait` / `dyn Trait` 更简洁。

### Q2: derive 都能派生哪些 trait？
**A**: 标准派生包括 `Debug`、`Clone`、`Copy`、`PartialEq`、`Eq`、`PartialOrd`、`Ord`、`Hash`、`Default` 等。前提是所有字段都实现了对应 trait；不满足时编译器会指出具体哪个字段缺失。第三方库可以提供自己的 derive 宏（如错误处理篇的 thiserror）。

### Q3: 什么是孤儿规则（E0117）？
**A**: `impl Trait for Type` 只能写在"trait 定义者"或"类型定义者"的 crate 里。它保证全世界的 impl 不会互相冲突，是 Rust 生态无全局注册表却能安全组合的基石。需要为外部类型补能力时，标准解法是**新类型模式**：包一层你自己的元组结构体再实现。

---

## 🔗 交叉引用

### 本模块
- 📄 **[03 结构体、枚举与模式匹配](./03-structs-enums-patterns.md)** — 本文为其类型补充"行为"维度
- 📄 **[05 错误处理](./05-error-handling.md)** — `From` / `Display` / `Error` 都是本篇定义的标准 trait
- 📄 **[02 所有权与借用](./02-ownership-borrowing.md)** — trait 方法接收器 `&self / &mut self / self` 的规则基础
- 📖 **[模块 README](../README.md)** — 进阶路径（reference 全量字典）在整体学习图中的位置

---

## 📝 总结

### 核心要点回顾
1. **trait 是行为契约**: 必填方法 + 可选默认方法，`impl Trait for Type` 参与契约
2. **泛型 = 编译期单态化**: 能力来自 trait bound，运行时零间接开销
3. **dyn Trait = 运行时分发**: 为异构集合与插件式扩展而生，代价是虚表跳转
4. **derive 消样板**: 标准派生一行搞定，机制与第三方 derive 宏一致

### 学习成果检查
- [ ] 能为一个 trait 完成两个以上实现并说明默认方法的作用
- [ ] 能解释 `T: PartialOrd` 不写会发生什么
- [ ] 面对需求能说出泛型与 dyn Trait 的选择理由
- [ ] 理解 derive 输出的实现与自己手写等价

---

**最后更新**: 2026年9月

> 🎯 **下一步**: 进入 [05 错误处理](./05-error-handling.md)——`Result`、`?` 与错误生态库（anyhow / thiserror），basics 核心五篇的收官。


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
