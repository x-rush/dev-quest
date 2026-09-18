# 错误处理库 - std Error / thiserror / anyhow

## 错误的传播、描述与分类是三件事

前置：Result、?、trait 与 From。Result<T, E> 的 E 可以是普通类型；? 的传播不要求 E 本身实现 Debug、Display 或 std::error::Error。能否使用 ? 取决于当前返回类型及所需的转换规则。

当错误要对人展示时实现 Display，需要调试输出时实现 Debug，需要进入标准错误链生态时实现 Error。thiserror 帮助为具体错误类型生成实现；anyhow 方便应用入口汇集不同来源并追加上下文。它们减少样板，不取消“谁根据错误种类作决定”的设计责任。

自测：库调用者要区分“文件不存在”和“格式错误”，是否只返回一段文字就够？不够，稳定的具体错误变体更适合分支处理。应用最外层只需记录诊断时，可保留 cause 链并添加“读取配置失败”等上下文。

> **文档简介**: Rust 错误处理三件套速查——std 的 `Error` trait 与 source 链模型、thiserror 派生宏属性表、anyhow 的上下文与 downcast、附手写范式与"库层 vs 应用层"选型矩阵。
>
> **目标读者**: 已会用 `Result`/`?`、要为项目定型错误策略的中级开发者。
>
> **前置知识**: [错误处理基础（Result/panic）](../../basics/05-error-handling.md)、trait 对象

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 字典（全量参考，单一事实来源） |
| **难度** | ⭐⭐ 进阶 |
| **标签** | `#rust` `#error-handling` `#reference` |
| **更新日期** | `2026年9月` |

</details>

**版本基线**: Rust **1.98.1**（edition 2024）见[模块 README](../../README.md)；thiserror / anyhow 未列入基线表，本文不标版本号（依赖用 `cargo add` 取当前稳定版）。

## 🎯 学习目标

- ✅ 理解 `Error::source()` 链模型，能手写完整的自定义错误类型
- ✅ 用 thiserror 五个属性（`#[error]`/`#[source]`/`#[from]`/`transparent`/插值）消灭手写样板
- ✅ 用 anyhow 的 `Context`/`bail!`/`ensure!`/`chain`/`downcast_ref` 在应用层组装错误链
- ✅ 按选型矩阵确定每个 crate/模块的错误策略

## 📋 目录

- [std Error trait 与错误链](#-std-error-trait-与错误链)
- [手写范式](#️-手写范式纯-std实测)
- [thiserror：派生宏属性表](#️-thiserror派生宏属性表)
- [anyhow：应用层错误](#-anyhow应用层错误)
- [选型矩阵](#️-选型矩阵)
- [最佳实践与陷阱](#-最佳实践与陷阱)
- [常见问题](#-常见问题)

---

## 🔍 std Error trait 与错误链

```rust
pub trait Error: Debug + Display {
    fn source(&self) -> Option<&(dyn Error + 'static)> { None }
    // description() / cause() 已弃用
}
```

Rust 错误是**普通值**：`Result<T, E>` 的 `E` 不必实现 Debug/Display；能否使用 `?` 取决于返回类型与错误转换约束；实现 `Error` trait 才能进入"错误链"生态——`source()` 声明"谁导致了我"，让整条因果链可遍历、可 downcast。`?` 的自动 `From` 转换负责**换型**，`source()` 负责**保留根因**，两者互补。

- **`source()` 链**：从外到内逐层 `source()` 直到 `None` 即根因；Display 消息逐层叠加。
- **downcast**：对 `&dyn Error` 可 `downcast_ref::<T>()` 取回具体类型（需 `'static`）。
- **`Box<dyn Error>`**：trait 对象错误，`From<&str>`/`From<String>` 可直接构造；适合示例、main、快速原型。
- **`provide()`/`Request`**（携带 Backtrace 等附加数据）：截至本文仍属 nightly 特性 `error_generic_member_access`，稳定层只需掌握 `source()`。

### 依赖（未列入基线，不标版本）

```bash
cargo add thiserror   # 库层：derive 出标准 Error 实现
cargo add anyhow      # 应用层：动态错误类型 + 上下文
```

## ✍️ 手写范式（纯 std，实测）

```rust
use std::error::Error;
use std::fmt::{self, Display, Formatter};

// 底层错误：无 source（用默认实现，source() 返回 None）
#[derive(Debug)]
enum DataErr {
    NotFound { key: String },
    Parse { pos: usize, msg: String },
}

impl Display for DataErr {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        match self {
            DataErr::NotFound { key } => write!(f, "未找到: {key}"),
            DataErr::Parse { pos, msg } => write!(f, "解析失败 @ {pos}: {msg}"),
        }
    }
}

impl Error for DataErr {}

// 中间层：包装下层错误并补上下文
#[derive(Debug)]
struct LoadErr {
    path: String,
    source: DataErr,
}

impl Display for LoadErr {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "加载 {} 失败", self.path)
    }
}

impl Error for LoadErr {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        Some(&self.source)
    }
}

fn load(path: &str) -> Result<String, LoadErr> {
    let key = path.split('/').next_back().unwrap_or(path);
    Err(LoadErr {
        path: path.to_string(),
        source: DataErr::NotFound { key: key.to_string() },
    })
}

// 沿链下钻 + downcast 取回具体类型
let err = load("db/users.json").unwrap_err();
assert_eq!(err.to_string(), "加载 db/users.json 失败");
let mut cur: Option<&(dyn Error + 'static)> = Some(&err);
while let Some(e) = cur {
    println!("  - {e}");      // 加载 db/users.json 失败 / 未找到: users.json
    cur = e.source();
}
let root = err.source().unwrap();
assert!(root.downcast_ref::<DataErr>().is_some());
```

手写范式的信息密度：**Display 一行 + source 一个字段**——这正是 thiserror 帮你生成的全部内容。

## 🏷️ thiserror：派生宏属性表

定位：**库层**。`#[derive(Error)]` 只生成 `Error` trait 实现（含 source/from），`Display` 由 `#[error("…")]` 生成（或你自己实现）。

| 属性 | 写法 | 作用 |
|------|------|------|
| `#[error("…")]` | 变体或 struct 级 | 生成 `Display`；`{0}`/`{name}` 插值字段，`{source}` 引 source 字段，`{:?}` 可用，额外参数可写任意表达式 |
| `#[source]` | 字段级 | 标记 `source()` 返回的字段；**字段名叫 `source` 时可省略此属性** |
| `#[from]` | 字段/变体级 | 同时生成 `From<T> for 该错误`（使 `?` 直通）**并**把该字段当 source；两者**不可再重复标注**；该变体除 source 外不能再有其他字段 |
| `#[error(transparent)]` | 变体或 struct 级 | Display 与 `source()` 全部转发给内部错误——自身"隐身" |
| `#[backtrace]` | 字段级 | 标记 Backtrace 字段；依赖 nightly 特性（同 `provide()`），稳定层暂不依赖 |

```rust
use thiserror::Error;

#[derive(Debug, Error)]
enum DataErr {
    #[error("not found: {0}")]
    NotFound(String),

    #[error("io failed: {source}")]
    Io {
        #[from]
        source: std::io::Error,     // From<io::Error> + source() 一步到位
    },

    // 透传实现 Error 的类型：Display 与 source 均转发
    #[error(transparent)]
    TransparentIo(std::io::Error),

    // 透传 anyhow::Error：仅转发 Display
    //（anyhow::Error 未实现 std::error::Error，source 链不经此变体）
    #[error(transparent)]
    Other(#[from] anyhow::Error),
}
```

实测确认的语义细节：

- `#[error(transparent)]` 转发的是 `inner.source()`（内层的内层），不是 inner 本身——transparent 类型在链上"变成" inner。
- 手写 `Display` + `#[derive(Error)]` 合法：没有 `#[error]` 属性时自己补 Display 即可。
- 同一源类型的 `#[from]` 在一个枚举里只能出现一次（会生成冲突的 `From` 实现）。
- 字段名叫 `source` 时自动视为 source，无需 `#[source]` 标注。

## 🧰 anyhow：应用层错误

定位：**应用层**。`anyhow::Error` 是动态错误类型——"任何 `std::error::Error + Send + Sync + 'static`"都能 `?` 进来；上下文在边界处添加，最终统一 `main -> anyhow::Result<()>` 或在顶层打日志/映射退出码。

| API | 说明 |
|------|------|
| `anyhow::Result<T>` | `Result<T, anyhow::Error>` 别名 |
| `anyhow!("…{x}")` | 就地构造动态错误（format! 语法） |
| `bail!("…")` | `return Err(anyhow!(…))` 的糖 |
| `ensure!(cond, "…")` | 条件不成立即 bail（前置断言） |
| `.context("…")` / `.with_context(\|\| …)` | `Context` trait：给错误包一层可读上下文（可用于 `Result` 和 `Option`） |
| `.chain()` | 迭代整条错误链（外→内） |
| `.root_cause()` | 最内层根因 |
| `.downcast_ref::<T>()` / `downcast_mut` | 取回具体错误类型 |
| `{:#}` | Display 的 alternate 形式：行内打印全链 |

```rust
use anyhow::{bail, ensure, Context};

fn find(id: u32) -> Result<String, DataErr> { /* …库层错误… */ }

fn app() -> anyhow::Result<()> {
    find(1).context("加载用户失败")?;   // DataErr: std::error::Error → 直接 context
    Ok(())
}

fn bailing(n: i32) -> anyhow::Result<()> {
    ensure!(n > 0, "n 必须为正，实际 {n}");
    if n < 10 { bail!("太小: {n}"); }
    Ok(())
}

let e = app().unwrap_err();
e.to_string();                        // "加载用户失败"（只显示最外层！）
format!("{:#}", e);                   // "加载用户失败: not found: user #1"（行内全链）
format!("{e:?}");                     // 多行 "Caused by:" 列表
e.chain().count();                    // 链长度
e.downcast_ref::<DataErr>().unwrap(); // 取回库层具体类型
e.root_cause().to_string();           // "not found: user #1"
```

**三种打印形态（实测）**：`Display` = 最外层消息；`{:#}` = 全链冒号拼接；`{:?}` = 缩进多行含 Caused by。给用户看用 Display，排障看 `{:#}` 或 Debug。

## 🗺️ 选型矩阵

| 场景 | 推荐 | 理由 |
|------|------|------|
| **库 crate 的公开 API** | thiserror 枚举 | 调用方可 `match` 具体变体、可靠 `source()`；错误类型即 API 契约 |
| **应用/二进制的业务层** | anyhow | 不想为每层定义类型；`?` 全通吃，context 按需叠加 |
| **示例/原型/测试** | `Box<dyn Error>` / anyhow | 零设计成本 |
| **错误需要携带结构化字段供程序判断** | thiserror（或手写） | enum 变体字段可被 match；anyhow 只能 downcast 尝试 |
| **库需要同时服务 anyhow 用户** | thiserror + `#[error(transparent)] Other(#[from] anyhow::Error)` 变体 | 官方推荐的桥接写法（注意：该变体 source 链不转发） |
| **任何场景** | std `Error` + `source()` 是共同地基 | thiserror 生成的、anyhow 包装的都是它 |

**分层惯例**：底层 crate 用 thiserror 定义类型化错误 → 中间层 `?` 直通（`#[from]`）→ 应用边界 anyhow `context` 补充人类可读上下文 → main/处理器统一消费。错误消息全小写、结尾不带标点，让多层叠加读起来像句子。

## 🎨 最佳实践与陷阱

错误库按调用方需要选择：稳定公共 API 常提供可区分的错误，应用聚合多种失败可使用统一容器。anyhow 支持向下转换已知类型，但不是自动生成的稳定业务错误枚举。context 说明当时的操作，避免只是重复底层消息。

从同一种错误类型到多个变体不能自动生成互相冲突的 From，实现中需明确选择。io::Error 的载荷访问与 source 链不同，不能对所有载荷一概断言 source 永远为空；排查时按实际错误结构检查。panic、线程和 FFI 各有边界，不用统一“跨界即炸”替代契约。

## ❓ 常见问题

### Q1: `?` 到底做了什么，为什么有时不用写 `#[from]` 也能传播？
**A**: `?` 调用 `From::from` 把内层错误转成函数签名里的错误类型。std 已为常见组合提供 `From`（如 `io::Error → Box<dyn Error>`）；thiserror 的 `#[from]` 是为"你的枚举 ← 依赖的错误类型"补 `From`。没有对应 `From` 就必须 `map_err` 手动换型。

### Q2: 泛型错误 `E: Error` 和 trait 对象 `Box<dyn Error>` / `anyhow::Error` 怎么选？
**A**: 泛型是编译期单态化，零开销但会把错误类型传染到整个调用链签名；trait 对象在边界处统一类型、动态分发一次。惯例：**内部传递用具体类型或泛型，跨模块/跨 crate 边界用 trait 对象**（thiserror 枚举或 anyhow），把"错误类型爆炸"挡在边界上。

## 📏 模式不变量

1. **错误是值，不是控制流异常**：`?`/From/source 全部建立在普通类型系统上——没有隐藏栈展开，panic 才是异常路径。
2. **一条错误链 = 一次操作语义 + 一个根因**：外层补"在做什么"（context/Display），内层保留"为什么失败"（source）；两层信息永不合并职责。
3. **类型化错误是 API，动态错误是实现细节**：公开签名暴露可 match 的类型，私有传播允许动态——这条边界与用 thiserror 还是 anyhow 无关。
4. **可识别性必须显式声明**：`match` 变体、`downcast_ref` 类型或 sentinel 比较，三选一写在设计里；"字符串匹配错误消息"永远不是方案。

## 🔗 相关资源

- 🌐 **[docs.rs/std::error](https://doc.rust-lang.org/std/error/trait.Error.html)** - Error trait 官方参考
- 🌐 **[docs.rs/thiserror](https://docs.rs/thiserror)** / **[docs.rs/anyhow](https://docs.rs/anyhow)** - 两库官方文档（属性表核对源）
- 📄 **[错误处理教程](../../basics/05-error-handling.md)** - Result/`?`/panic 语言层基础
- 📄 **[Tokio 速查](./12-tokio-guide.md)** - `JoinError::is_cancelled` 与任务取消语义
- 📄 **[Serde 速查](./13-serde-guide.md)** - `serde_json::Error` 是标准 `Error`，可直接进 anyhow 链
- 📄 **[Axum 要点](../framework-essentials/11-axum-essentials.md)** - Handler 错误到 HTTP 状态码的映射

---

## 📝 总结

1. **地基只有一条**：`Debug + Display + source()`——手写范式是理解 thiserror/anyhow 的最小模型。
2. **thiserror = 库层**：五个属性消掉样板，错误类型本身是 API 契约。
3. **anyhow = 应用层**：动态类型 + context 组链，`{:#}` 看全链，downcast 取根因类型。
4. **选型看边界**：被依赖的层给类型，消费一切的层给动态；跨库桥接用 transparent 变体。

**文档版本**: v1.0.0 | **最后更新**: 2026年9月 | **维护团队**: Dev Quest Team


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
