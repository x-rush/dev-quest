# Serde - 序列化框架全量速查

> **文档简介**: Serde 1.0.229 的 derive 属性全表、枚举四种表示、JSON/TOML 后端用法与手写 Serialize/Deserialize 要点——数据进出边界的单一事实来源。
>
> **目标读者**: 需要精确控制结构化数据格式（API 载荷、配置文件、IPC 消息）的中级开发者。
>
> **前置知识**: [结构体、枚举与模式匹配](../../basics/03-structs-enums-patterns.md)、trait 基础

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 字典（全量参考，单一事实来源） |
| **难度** | ⭐⭐ 进阶 |
| **标签** | `#rust` `#serde` `#json` `#reference` |
| **更新日期** | `2026年9月` |

**版本基线**: Serde **1.0.229**（核实日期 2026-09-16，单一事实来源见[模块 README 技术基线](../../README.md)）。后端 crate（serde_json/toml 等）未列入基线，本文不标版本号。

## 🎯 学习目标

- ✅ 用 derive 宏 + 属性表精确控制任意字段名/缺省/跳过/拍平行为
- ✅ 为枚举选择正确的四种表示之一并预知 JSON 形态
- ✅ 按需手写 Serialize/Deserialize（含 `with` 模块契约）
- ✅ 掌握 serde_json 与 toml 两个后端的最小 API 面

## 📋 目录

- [核心概念：数据模型与两端](#核心概念数据模型与两端)
- [容器属性全表](#容器属性全表)
- [字段属性全表](#字段属性全表)
- [枚举的四种表示](#枚举的四种表示)
- [后端：json 与 toml](#后端json-与-toml)
- [自定义序列化](#自定义序列化)
- [最佳实践与陷阱](#最佳实践与陷阱)
- [常见问题](#常见问题)

---

## 🔍 核心概念：数据模型与两端

Serde 把"数据怎么变 Rust 值"拆成三层：**数据模型**（序列化原语操作的中间表示）居中；左侧 `#[derive(Serialize, Deserialize)]` 描述你的类型如何映射到模型；右侧各格式 crate（`serde_json`、`toml`…）实现 `Serializer`/`Deserializer` 把模型翻译为具体格式。**格式之间不互通代码**——换后端只换依赖，derive 层原样复用。

```toml
# Cargo.toml —— 版本标注策略：基线内技术写具体版本（见模块 README），
# 后端 crate 用 cargo add 取当前稳定版，避免文档出现第二处会过时的版本号
[dependencies]
serde = { version = "1.0.229", features = ["derive"] }
# cargo add serde_json   # JSON 后端
# cargo add toml         # TOML 后端
```

**derive 一次、处处可用**：

```rust
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
struct User {
    name: String,
    age: u8,
}
```

## 📦 容器属性全表（struct/enum 级）

| 属性 | 写法 | 作用 |
|------|------|------|
| `rename` | `#[serde(rename = "Name")]` | 整体重命名（可用 `serialize = "…"`/`deserialize = "…"` 分向） |
| `rename_all` | `#[serde(rename_all = "camelCase")]` | 字段名（struct）或变体名（enum）统一转大小写风格；也支持分向 |
| `rename_all_fields` | `#[serde(rename_all_fields = "camelCase")]` | 枚举内各**结构体变体的字段**统一转风格（变体名另用 `rename_all`） |
| `deny_unknown_fields` | `#[serde(deny_unknown_fields)]` | 反序列化遇到未知键即报错（默认忽略） |
| `default` | `#[serde(default)]` | 反序列化缺字段时取 `Default::default()`；`default = "path"` 用指定函数 |
| `transparent` | `#[serde(transparent)]` | 整个类型与唯一字段互相直通——序列化结果就是字段本身 |
| `tag` | `#[serde(tag = "type")]` | 枚举**内部标签**表示（见下节） |
| `tag` + `content` | `#[serde(tag = "t", content = "c")]` | 枚举**邻接标签**表示 |
| `untagged` | `#[serde(untagged)]` | 枚举**无标签**表示，按变体声明顺序逐个尝试 |
| `bound` | `#[serde(bound = "T: MyTrait")]` | 手动指定 derive 生成的 trait 约束 |
| `remote` | `#[serde(remote = "ForeignType")]` | 为不能改源码的外部类型做"远端 derive" |
| `from` / `try_from` / `into` | `#[serde(from = "Raw")]` | 先反序列化成中间类型再转换（`try_from` 带 fallible） |
| `crate` | `#[serde(crate = "other_serde")]` | 重新映射 derive 展开时用的 serde 路径 |
| `expecting` | `#[serde(expecting = "…")]` | 自定义错误描述语 |
| `variant_identifier` / `field_identifier` | — | 只做变体/字段名的派生（自写枚举名解析时用） |

`rename_all` 的 8 个合法值：`lowercase`、`UPPERCASE`、`PascalCase`、`camelCase`、`snake_case`、`SCREAMING_SNAKE_CASE`、`kebab-case`、`SCREAMING-KEBAB-CASE`。

## 🏷️ 字段属性全表

| 属性 | 写法 | 作用 |
|------|------|------|
| `rename` | `#[serde(rename = "userName")]` | 单字段重命名（Rust 关键字冲突必用，如 `"type"`） |
| `alias` | `#[serde(alias = "name")]` | 反序列化时的**备用**名（`rename` 仍生效；序列化只用主名） |
| `skip` | `#[serde(skip)]` | 双向都不参与；反序列化时该字段取 `Default` |
| `skip_serializing` / `skip_deserializing` | — | 单向跳过 |
| `skip_serializing_if` | `#[serde(skip_serializing_if = "Option::is_none")]` | 谓词 `fn(&T) -> bool` 为真则不序列化（常用 `Option::is_none`、`Vec::is_empty`） |
| `default` | `#[serde(default)]` / `default = "path"` | 字段级缺省（缺失时用 Default/指定函数） |
| `flatten` | `#[serde(flatten)]` | 该字段原地展开合并；反序列化时通常配 `Map` 收集剩余键 |
| `with` | `#[serde(with = "module")]` | 委托模块的 `serialize`/`deserialize` 函数（见自定义序列化） |
| `serialize_with` / `deserialize_with` | `#[serde(serialize_with = "path")]` | 单向委托函数 |
| `borrow` | `#[serde(borrow)]` | 反序列化借用 `&'a str` 等免分配（零拷贝） |
| `bound` | `#[serde(bound = "T: MyTrait")]` | 字段级约束覆盖 |
| `getter` | `#[serde(getter = "path")]` | 供 `remote` 模式取值 |

变体级属性（enum 变体上）：`rename`、`skip`（跳过该变体）、`untagged`、`other`（反序列化未匹配时的兜底 unit 变体）、`serialize_with`/`deserialize_with`。

### 实测：核心字段属性

```rust
#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
struct User {
    user_name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    nickname: Option<String>,
    #[serde(default)]
    age: u8,
    #[serde(skip)]
    internal: String,
}

// 序列化：skip 字段消失，None 字段消失
// {"userName":"ada","nickname":"a","age":30}
// {"userName":"b","age":0}

// 反序列化：缺 age 用 default(0)；skip 字段自动 Default
let u: User = serde_json::from_str(r#"{"userName":"c"}"#).unwrap();
assert_eq!(u.age, 0);
```

## 🧬 枚举的四种表示

| 表示 | 属性 | JSON 形态 | 适用 |
|------|------|-----------|------|
| **外部标签**（默认） | 无 | `{"Code":7}`、`{"Detail":{"x":1}}` | 通用默认；Rust 惯例 |
| **内部标签** | `#[serde(tag = "type")]` | `{"type":"user_created","name":"n"}` | API 载荷、日志事件（**不支持 tuple 变体**） |
| **邻接标签** | `#[serde(tag = "type", content = "data")]` | `{"type":"Code","data":7}` | 兼顾标签稳定与负载独立 |
| **无标签** | `#[serde(untagged)]` | `-3`、`"x"`、`2.5` | 多格式容错（按声明顺序逐变体尝试） |

```rust
#[derive(Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
enum Event {
    UserCreated { name: String },  // {"type":"user_created","name":"n"}
    Deleted,                       // {"type":"deleted"}
}

#[derive(Serialize, Deserialize)]
#[serde(tag = "type", content = "data")]
enum Adj {
    Code(u32),          // {"type":"Code","data":7}
    Detail { x: i32 },  // {"type":"Detail","data":{"x":1}}
}

#[derive(Serialize, Deserialize)]
#[serde(untagged)]
enum Num {
    I(i64),
    F(f64),
    S(String),
}  // "-3" → I；2.5 → F；"x" → S
```

`tag`/`content`/`untagged` 三者互斥；`deny_unknown_fields` 与 `flatten` 互斥（flatten 本质允许任意剩余键）。

## 🗄️ 后端：json 与 toml

### serde_json 最小 API 面

| API | 说明 |
|------|------|
| `serde_json::to_string(&v)` / `to_string_pretty` / `to_vec` / `to_writer` | 序列化 |
| `serde_json::from_str(s)` / `from_slice` / `from_reader` | 反序列化，类型由标注推断 |
| `serde_json::Value` | 动态 JSON 树：`Null/Bool/Number/String/Array/Object`，支持索引 `v["k"][0]` |
| `serde_json::from_value(v)` / `to_value(x)` | Value ↔ 强类型 |
| `serde_json::json!({...})` | 字面量宏构造 Value |
| `serde_json::Error` | 实现 `std::error::Error`，可直接进 anyhow/`?` |

```rust
// 输入: {"k": [1, 2, true], "s": "x"}
let v = serde_json::json!({ "k": [1, 2, true], "s": "x" });
assert_eq!(v["k"][2], serde_json::Value::Bool(true));
let s = serde_json::to_string_pretty(&v).unwrap(); // 带缩进输出
```

**数字注意**：JSON 整数默认按 `i64`/`u64` 解析，超范围或需保留任意精度时启用 serde_json 的 `arbitrary_precision` feature。

### toml 后端（配置文件）

```rust
#[derive(Serialize, Deserialize)]
struct Cfg { name: String, port: u16 }

let c = Cfg { name: "app".into(), port: 8080 };
let t = toml::to_string(&c).unwrap();
// t == "name = \"app\"\nport = 8080\n"
let c2: Cfg = toml::from_str(&t).unwrap();
```

TOML 无顶层"数组标量"概念，序列化目标需为表（struct/map）。YAML 后端 serde_yaml 原作者已停止维护，选型时自评估（不在基线，不展开）。

## ✍️ 自定义序列化

### 手写 Serialize（实测）

```rust
use serde::ser::SerializeStruct;      // serialize_field 方法在此 trait 上
use serde::{Serialize, Serializer};

struct Point { x: i32, y: i32 }

impl Serialize for Point {
    fn serialize<S: serde::Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
        let mut st = s.serialize_struct("Point", 2)?;
        st.serialize_field("x", &self.x)?;
        st.serialize_field("y", &self.y)?;
        st.end()
    }
}
// 输出: {"x":1,"y":2}
```

其他常用 Serializer 钩子：`serialize_str` / `serialize_i32` / `serialize_seq` / `serialize_map` / `serialize_newtype_struct`。

### 手写 Deserialize（Visitor 模式，实测）

```rust
use serde::de::{MapAccess, Visitor};
use serde::{Deserialize, Deserializer};

impl<'de> Deserialize<'de> for Point {
    fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        d.deserialize_struct("Point", &["x", "y"], PointVisitor)
    }
}

struct PointVisitor;

impl<'de> Visitor<'de> for PointVisitor {
    type Value = Point;

    fn expecting(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        f.write_str("struct Point with fields x and y")
    }

    fn visit_map<A: MapAccess<'de>>(self, mut map: A) -> Result<Point, A::Error> {
        let (mut x, mut y) = (None, None);
        while let Some(k) = map.next_key::<String>()? {
            match k.as_str() {
                "x" => x = Some(map.next_value()?),
                "y" => y = Some(map.next_value()?),
                _ => {}
            }
        }
        Ok(Point { x: x.unwrap_or_default(), y: y.unwrap_or_default() })
    }
}
// 输入 {"x":3,"y":4} → Point { x: 3, y: 4 }
```

Visitor 按"你愿意接受的数据形态"实现 `visit_str`/`visit_map`/`visit_seq`/`visit_u64` 等入口；没实现的形态得到默认的"类型不匹配"错误。

### `with` 模块契约

```rust
mod point_as_str {
    use serde::{Deserialize, Deserializer, Serialize, Serializer};

    pub fn serialize<S: Serializer>(v: &Point, s: S) -> Result<S::Ok, S::Error> {
        s.serialize_str(&format!("({},{})", v.x, v.y))
    }
    pub fn deserialize<'de, D: Deserializer<'de>>(d: D) -> Result<Point, D::Error> {
        let s = String::deserialize(d)?;
        // ...解析 s...
    }
}

#[derive(Serialize, Deserialize)]
struct Wrapper(#[serde(with = "point_as_str")] Point);
```

`with = "module"` 要求模块提供上述两个自由函数；只单向需要时用 `serialize_with`/`deserialize_with`。

## 🎨 最佳实践与陷阱

### ✅ 推荐做法
- **对外 API 用 `rename_all = "camelCase"`**：Rust 命名风格与 JSON 惯例解耦，一处声明全局生效。
- **可选字段统一 `skip_serializing_if = "Option::is_none"`**：保持载荷干净；`Option` 字段缺失时反序列化自动得 `None`，无需 `default`。
- **边界类型手写、内部类型 derive**：`remote` + `from` 组合为第三方类型做桥。

### ❌ 避免陷阱
- **`skip` 字段不是"必填校验"**：skip 字段反序列化时用 `Default::default()` 填充，不会报错。
- **`untagged` 挨个试变体**：变体多时解析慢且错误信息模糊，性能敏感路径慎用。
- **`flatten` 与 `deny_unknown_fields` 互斥**：拍平语义下"未知键"概念已不存在。
- **`deny_unknown_fields` 配 API 演进**：服务端加字段会直接打挂老客户端，宽松消费端慎用。
- **忘记 `SerializeStruct` 导入**：`serialize_field` 是 trait 方法，需 `use serde::ser::SerializeStruct;`。

## ❓ 常见问题

### Q1: 字段名撞 Rust 关键字（如 `type`、`ref`）怎么办？
**A**: 用 `#[serde(rename = "type")]` 显式指定线格式名字；Rust 侧声明可用原生标识符 `r#type`。推荐 rename 方案——线格式名与 Rust 命名解耦。

### Q2: 什么时候需要手写 Serialize/Deserialize？
**A**: 三种情况：① 线格式与内存结构有固定换算（如 `(u8,u8,u8)` ↔ `"#rrggbb"`）；② 需要校验/归一化（反序列化时 fallible 逻辑）；③ `remote` 桥接外部类型。能用属性表达的（rename/default/flatten）不要手写——属性可读性更高且 derive 保证双向一致。

## 📏 模式不变量

1. **数据模型是合约**：类型 ↔ 格式之间隔着一层中间表示，因此"换后端不换业务代码"——凡属性表能表达的映射都与具体格式无关。
2. **线格式名与内存名是两个命名空间**：`rename/rename_all` 的存在本身证明两侧命名各自演化，跨语言接口永远显式声明线名。
3. **缺省是反序列化单向概念**：`default`/`skip` 只 relax 读取端；序列化端的取舍由 `skip_serializing_if` 独立控制——读写策略不对称是常态。
4. **枚举表示是版本化承诺**：改 tag/untagged 形态等于改协议；选型时以"五年内最不容易改的表示"为准。
5. **derive 无法表达的就下沉到 Visitor**：校验、归一化、条件解析属于类型不变量，放在反序列化边界一次性完成。

## 🔗 相关资源

- 🌐 **[serde.rs](https://serde.rs/)** - 官方属性文档（本文属性表核对源）
- 🌐 **[docs.rs/serde](https://docs.rs/serde)** - trait 与 derive 参考手册
- 📄 **[Tauri IPC 命令](../framework-essentials/10-tauri-ipc-commands.md)** - Tauri 命令参数/返回值全走 Serde
- 📄 **[Axum 要点](../framework-essentials/11-axum-essentials.md)** - `Json<T>` 提取器即 Serde 边界
- 📄 **[错误处理库](./14-error-libraries.md)** - `serde_json::Error` 接入 anyhow 错误链
- 📄 **[枚举与模式匹配](../../basics/03-structs-enums-patterns.md)** - 被序列化的枚举本体

---

## 📝 总结

1. **三层架构**：derive（你的类型）→ 数据模型 → Serializer/Deserializer（格式 crate），属性表只作用于第一层。
2. **属性三张表**：容器/字段/变体，`rename` 族管名字、`skip` 族管取舍、`tag` 族管枚举形态。
3. **枚举先定表示**：外部标签默认，API 场景内部标签，容错场景 untagged。
4. **手写实现是逃生舱**：`serialize_struct` + Visitor + `with` 契约覆盖其余一切需求。

**文档版本**: v1.0.0 | **最后更新**: 2026年9月 | **维护团队**: Dev Quest Team
