# 错误处理：Result / panic / anyhow / thiserror

## 先理解，再动手

Result 把可能失败写进返回类型，? 把错误传播给调用者。panic 不适合表达正常可预期的无效输入。

**本节自测**：解析合法与非法数字，用 match 输出两种结果，再把传播放进返回 Result 的函数。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

非法输入走 Err，调用方能决定反馈；unwrap 会把可处理失败变成 panic。

</details>

> **文档简介**: Rust 把"失败"建模成类型——Result 显式返回、? 优雅传播、panic 只留给真正的 bug，再引入 anyhow 与 thiserror 的工程分工。basics 核心五篇的收官。
>
> **目标读者**: 已掌握枚举与 trait、准备写"像样的" Rust 应用的学习者
>
> **前置知识**: [03 结构体、枚举与模式匹配](./03-structs-enums-patterns.md)（Result 是枚举）、[04 trait 与泛型](./04-traits-generics.md)（From / Display / Error 都是 trait）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 教程 |
| **难度** | ⭐⭐ |
| **标签** | `#rust` `#error-handling` `#result` `#anyhow` `#thiserror` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

- ✅ **掌握核心概念**: panic 与 Result 的分工、`?` 运算符的传播与转换机制、自定义错误类型的完整要素
- ✅ **实践能力**: 写出返回 `Result` 的函数、用 `From`/`map_err` 统一错误类型、让 `main` 返回 `Result` 获得非零退出码
- ✅ **解决问题**: 选型困难——什么时候手写错误类型、什么时候上 anyhow / thiserror
- ✅ **进阶方向**: 为本模块后续的 SQLx / Axum / Tauri 开发（它们的 API 大量以 Result 收尾）建立心智模型

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

### 概念一：panic 与 Result —— 两种失败的分工

**定义**: Rust 把失败分成两类：**不可恢复**的 panic（程序有 bug、不变量被破坏）与**可恢复**的错误（外部输入、网络、文件——预期内可能失败）。

**关键特性**:
- `panic!` 立刻终止当前线程（默认展开栈），适合断言不变量，不适合处理外部输入
- `Result<T, E>` 是普通枚举：`Ok(T)` 成功、`Err(E)` 失败，编译器强制两种情况都被面对
- 一句话分工：**panic = bug；Err = 预期内的失败**。外部数据永远走 Result

**与异常语言的对比**:

| 方面 | Java / Python 异常 | Rust Result |
|------|-------------------|-------------|
| 失败入口 | 隐藏在调用链，类型签名不体现 | 函数签名 `-> Result<T, E>` 一目了然 |
| 是否必须处理 | 可不捕获，运行时炸 | 编译器检查，`?`/match 必选其一 |
| 传播成本 | try/catch 样板 | 一个 `?` 字符 |

### 概念二：? 运算符 —— 错误传播的一等公民

**定义**: `?` 作用在 `Result` 值上：`Ok` 则取出内部值继续执行，`Err` 则立即把错误 `return` 出当前函数。

**关键特性**:
- 语义上等价于一段 match 提前返回的样板，但路径干净得多
- `?` 在返回 `Err` 前会调用 `From::from` 做**自动转换**：函数错误类型只要能从底层错误"From"过来，就能直接用 `?`
- 显式转换用 `map_err`：顺路包装上下文信息（"在做什么时失败了"）

### 概念三：自定义错误类型的完整要素

**定义**: 一个"合格"的错误类型 = 枚举列举失败原因 + `Display`（人类可读信息）+ `std::error::Error`（接入生态，如 `?` 自动转换与错误源链）。

**关键特性**:
- 用枚举建模：每种失败原因一个变体，携带定位所需的上下文数据
- `impl Display for ...` 决定 `println!("{e}")` 看到什么
- `impl std::error::Error for ...` 后，其他错误可以 `From` 进来，`?` 跨错误类型畅通
- 手写一遍是为了理解结构——工程上由 thiserror 的 derive 代劳（见示例五）

### 概念四：anyhow 与 thiserror 的生态分工

**定义**: 两个事实标准库各管一头：**thiserror** 用 derive 为你的错误类型生成 Display/From（库、公共 API 边界用）；**anyhow** 提供一个万能动态错误类型与链式上下文（应用、二进制入口用）。

**关键特性**:
- 库作者关心"调用方能精确 match 我的错误变体" → thiserror，保留类型信息
- 应用作者关心"快速传播 + 附上下文 + 统一打印" → `anyhow::Result` + `.context(...)`
- 两者不冲突：同一项目常同时使用——错误类型用 thiserror 定义，应用内传播用 anyhow

---

## 🛠️ 实践指南

### 步骤一：把 match 错误处理升级为 ? 风格

**目标**: 亲手完成从"样板 match"到"`?` 传播"的重构。

**操作指南**:
1. `cargo new error-lab && cd error-lab`
2. 写一个解析 CSV 行求和的函数，初版在循环里用 match 处理 `parse` 的 Err
3. 把签名改为 `-> Result<i64, ParseIntError>`，循环内改用 `?`
4. 对比两版行数与可读性

**验证方法**: 两版对 `"1, 2, 3"` 返回 `Ok(6)`、对含非数字输入返回 `Err`

### 步骤二：定义你自己的错误类型

**目标**: 走完"枚举 + Display + Error"三件套。

**操作指南**:
1. 参照示例三定义 `ConfigError` 枚举（至少两个变体）
2. 实现 `Display` 与 `std::error::Error`
3. 写一个返回 `Result<u16, ConfigError>` 的端口解析函数，用 `map_err` 把 `ParseIntError` 包进来
4. 在 `main` 里 match 打印每个失败分支

**验证方法**: 合法/越界/非数字三种输入各自命中正确的错误变体

---

## 💻 代码示例

> 示例一至示例四（纯标准库）均已在本机以 `rustc --edition 2024` 实测编译并运行通过；示例五、六依赖 crates.io 第三方库，说明见各节标注。

### 示例一：Result 与 match 基础

```rust
use std::num::ParseIntError;

// Result<T, E>：Ok 表示成功、Err 表示失败，编译器逼你处理两种情况
fn parse_age(input: &str) -> Result<u32, ParseIntError> {
    input.trim().parse::<u32>()
}

fn main() {
    match parse_age(" 28 ") {
        Ok(age) => println!("年龄: {age}"),
        Err(e) => println!("解析失败: {e}"),
    }

    match parse_age("abc") {
        Ok(age) => println!("年龄: {age}"),
        Err(e) => println!("解析失败: {e}"),
    }
}
```

**关键点解析**:
- 错误类型出现在签名里——调用方"会不会失败、失败是什么"无需看实现
- `parse_age(" 28 ")` 成功返回 28：`parse` 对接 `FromStr` 生态，先 `trim` 清理空白是常见前置
- 03 篇的 match 解构在这里原样适用——`Ok`/`Err` 就是枚举变体

### 示例二：? 运算符传播

```rust
use std::num::ParseIntError;

// ? 运算符：成功取值继续执行，失败立刻把错误 return 出去
fn sum_csv(line: &str) -> Result<i64, ParseIntError> {
    let mut total = 0;
    for part in line.split(',') {
        let n: i64 = part.trim().parse()?;
        total += n;
    }
    Ok(total)
}

fn main() {
    // 与手写 match 等价，但错误传播路径干净得多
    println!("{:?}", sum_csv("1, 2, 3"));
    println!("{:?}", sum_csv("1, x, 3"));
}
```

**关键点解析**:
- `parse()?` 一行替代"match + 提前 return"四行，失败点直接跳出到函数边界
- `?` 隐含 `From::from` 转换：本例错误类型一致看不出来，跨类型时（见示例三）才显威力
- 输出中 `Err(ParseIntError { kind: InvalidDigit })` 是 Debug 打印——错误类型通常 derive Debug 供诊断

### 示例三：手写自定义错误类型

```rust
use std::fmt;

// 手写自定义错误类型（先理解这一层，再用 thiserror 减少样板）
#[derive(Debug)]
enum ConfigError {
    MissingKey(String),
    BadPort(String),
}

impl fmt::Display for ConfigError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ConfigError::MissingKey(k) => write!(f, "缺少配置项: {k}"),
            ConfigError::BadPort(v) => write!(f, "端口号无效: {v}"),
        }
    }
}

// 实现 std::error::Error 才能接入错误处理生态（? 跨错误类型转换等）
impl std::error::Error for ConfigError {}

fn require(config: &[(String, String)], key: &str) -> Result<String, ConfigError> {
    config
        .iter()
        .find(|(k, _)| k == key)
        .map(|(_, v)| v.clone())
        .ok_or_else(|| ConfigError::MissingKey(key.to_string()))
}

fn parse_port(raw: &str) -> Result<u16, ConfigError> {
    // 解析失败时转换成自己的错误类型
    let n: u32 = raw
        .parse()
        .map_err(|_| ConfigError::BadPort(raw.to_string()))?;
    if n > 65535 {
        return Err(ConfigError::BadPort(raw.to_string()));
    }
    Ok(n as u16)
}

fn main() {
    let config = vec![
        (String::from("host"), String::from("localhost")),
        (String::from("port"), String::from("8080")),
    ];

    for input in ["8080", "99999", "abc"] {
        match parse_port(input) {
            Ok(p) => println!("{input} -> 端口 {p}"),
            Err(e) => println!("{input} -> 错误: {e}"),
        }
    }

    match require(&config, "token") {
        Ok(v) => println!("token = {v}"),
        Err(e) => println!("错误: {e}"),
    }
}
```

**关键点解析**:
- 三件套齐活：枚举变体 = 失败原因清单，Display = 可读信息，`impl Error` = 生态接口
- `ok_or_else` 把 `None` 变成具体 `Err`——Option 到 Result 的标准桥
- `map_err` 是显式转换点：借机把"原始错误"包装成带上下文的业务错误（这里保留了原始输入）

### 示例四：main 返回 Result

```rust
use std::num::ParseIntError;

fn run() -> Result<(), ParseIntError> {
    // 没有命令行参数时用默认端口
    let port: u16 = std::env::args()
        .nth(1)
        .unwrap_or_else(|| "8080".to_string())
        .parse()?;
    println!("服务将监听端口 {port}");
    Ok(())
}

// main 也可以返回 Result：Err 时进程以非零退出码结束并打印错误
fn main() -> Result<(), ParseIntError> {
    run()
}
```

```bash
cargo run 3000      # 输出: 服务将监听端口 3000
cargo run -- --bad  # Err 路径：非零退出码，stderr 打印错误 Debug 信息
```

**关键点解析**:
- `main() -> Result<(), E>` 让顶层错误自动转成进程退出码——CLI 工具与 CI 友好
- `unwrap_or_else` 提供默认值而不是 unwrap：默认值逻辑属于代码，崩溃不该由缺参数触发
- 顶层只剩一层 `?` 时，错误信息集中在一处打印，调试入口单一

### 示例五：thiserror —— 库边界的错误类型（依赖第三方）

```rust
use thiserror::Error;

// thiserror：derive 生成 Display 与 From 转换，等价于示例三的全部手写内容
#[derive(Debug, Error)]
pub enum ConfigError {
    #[error("配置项缺失: {0}")]
    MissingKey(String),
    #[error("底层 IO 错误: {0}")]
    Io(#[from] std::io::Error),
}
```

> ⚠️ 本段依赖 crates.io 的 thiserror，不在自包含实测范围内；用法以官方文档为准。`#[error("...")]` 生成 Display，`#[from]` 生成 `From<io::Error>` 使 `?` 自动转换生效——与示例三逐项对应。

### 示例六：anyhow —— 应用边界的快速传播（依赖第三方）

```rust
use anyhow::{Context, Result};

// anyhow：应用代码用 ? + context 快速传播并附加上下文
fn load_port() -> Result<u32> {
    let raw = std::env::var("APP_PORT").context("缺少 APP_PORT 环境变量")?;
    raw.parse::<u32>().context("APP_PORT 不是合法数字")
}

fn main() -> Result<()> {
    let port = load_port()?;
    println!("端口: {port}");
    Ok(())
}
```

> ⚠️ 本段依赖 crates.io 的 anyhow，不在自包含实测范围内；用法以官方文档为准。`Result` 是 `anyhow::Result`（错误类型为动态的 `anyhow::Error`），`.context(...)` 给错误链挂上"当时在做什么"的描述。

依赖引入方式（版本号以 `cargo add` 自动写入的当前稳定版为准，本模块技术基线未收录这两库，随用随查 crates.io）:

```bash
cargo add anyhow thiserror
```

---

## 🎨 最佳实践

错误类型应让调用者能够决定如何处理：没有权限、格式错误和暂时不可用可能需要不同动作。结构化错误适合公共契约，应用边界可使用统一包装并添加操作上下文；anyhow 也能向下转换已知类型，只是不会自动提供稳定的枚举契约。

外部失败通常通过 Result 表达；确有默认值语义时可以转换，但应明确丢失了哪些信息。expect 给 panic 补说明，并没有让失败更安全。测试错误传播后资源释放、数据未部分写入，以及用户消息不暴露内部路径或秘密。

---

## ❓ 常见问题

### Q1: unwrap / expect 什么时候可以用？
**A**: 三类场景：① 原型与示例代码；② 单元测试（失败就该快速崩溃）；③ 编译期能证明不会 Err 的地方（如对常量字符串 parse 后立刻 expect）。工程代码的运行时路径上不要裸 unwrap。

### Q2: anyhow 和 thiserror 是二选一吗？
**A**: 不是二选一，而是各管一段。thiserror 负责"定义"——你的错误类型长什么样、怎么显示、从哪些底层错误转换而来；anyhow 负责"传播"——应用代码里用 `?` 一路向上、途中 `.context()` 挂上下文。中大型应用常两者并存，以"是否是库边界"划线。

### Q3: `?` 到底做了什么？
**A**: 三步：① 若值是 `Ok`，取出内部值，表达式结果就是它；② 若是 `Err`，先对其调用 `From::from` 转换成本函数的错误类型；③ 立即 `return Err(...)`。所以"函数错误类型一致"时 `?` 无感，"不一致但存在 From 转换"时自动转换，"两者皆无"时编译报错提示你补 `map_err` 或 `#[from]`。

---

## 🔗 交叉引用

### 本模块
- 📄 **[03 结构体、枚举与模式匹配](./03-structs-enums-patterns.md)** — `Result`/`Option` 的 match 处理基础
- 📄 **[04 trait 与泛型](./04-traits-generics.md)** — `From`、`Display`、`std::error::Error` 都是 trait，本文是它们最密集的应用场景
- 📄 **[01 环境搭建](./01-environment-setup.md)** — `cargo add` 添加 anyhow / thiserror 依赖
- 📖 **[所有权细则字典](../reference/language-concepts/01-ownership-dictionary.md)** — 错误类型所有权设计的深层细则

### 跨模块
- 📄 **[09 Node.js 后端](../../09-nodejs-backend/README.md)** — 回调/异常风格错误传播的对照参考（Axum 后端线在本模块 frameworks/ 展开）

---

## 📝 总结

### 核心要点回顾
1. **分工**: panic 留给 bug，外部输入一律 `Result`——签名即文档
2. **`?` 是主力**: Ok 取值 / Err 转换并提前返回，`From` 与 `map_err` 是它的两个转换阀门
3. **错误类型三件套**: 枚举变体 + Display + `std::error::Error`，手写一遍是理解生态的前提
4. **生态分工**: thiserror 管定义（库边界），anyhow 管传播（应用边界）

### 学习成果检查
- [ ] 能说清 panic 与 Err 的适用边界
- [ ] 能把一段 match 错误处理重构为 `?` 风格并解释转换路径
- [ ] 独立完成过"枚举 + Display + Error"的自定义错误类型
- [ ] 面对新项目能立即选对 anyhow / thiserror / 手写的取舍

---

**最后更新**: 2026年9月

> 🎯 **下一步**: basics 核心五篇完成。继续按模块 README 入门路径推进后续篇目（集合与迭代器、生命周期），或回翻 [02 所有权与借用](./02-ownership-borrowing.md) 与字典象限巩固基础。


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
