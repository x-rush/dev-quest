# Serde - 序列化框架全量速查

> **文档简介**: Serde 1.0.229 的 derive 属性全表、枚举四种表示、JSON/TOML 后端用法与手写 Serialize/Deserialize 要点——数据进出边界的单一事实来源。
>
> **目标读者**: 需要精确控制结构化数据格式（API 载荷、配置文件、IPC 消息）的中级开发者。
>
> **前置知识**: [结构体、枚举与模式匹配](../../basics/03-structs-enums-patterns.md)、trait 基础

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 字典（全量参考，单一事实来源） |
| **难度** | ⭐⭐ 进阶 |
| **标签** | `#rust` `#serde` `#json` `#reference` |
| **更新日期** | `2026年9月` |

</details>

**版本基线**: Serde **1.0.229**，模块学习基线见[模块 README](../../README.md)。示例依赖固定在下方清单，便于重建同一环境；升级时重新生成锁文件并执行边界验收。

下文完整 JSON 程序的精确依赖、锁文件与运行结果见[验证报告](../../../shared-resources/tools/document-quality/reports/rust-ecosystem-validation.md)。TOML 示例在本批仅提供 API 用法，不计入 JSON 程序验证范围。

## 🎯 学习目标

- ✅ 用 derive 宏 + 属性表精确控制任意字段名/缺省/跳过/拍平行为
- ✅ 为枚举选择正确的四种表示之一并预知 JSON 形态
- ✅ 按需手写 Serialize/Deserialize（含 `with` 模块契约）
- ✅ 掌握 serde_json 与 toml 两个后端的最小 API 面

## 📋 目录

- [核心概念：数据模型与两端](#-核心概念数据模型与两端)
- [容器属性全表](#-容器属性全表structenum-级)
- [字段属性全表](#️-字段属性全表)
- [枚举的四种表示](#-枚举的四种表示)
- [后端：json 与 toml](#️-后端json-与-toml)
- [自定义序列化](#️-自定义序列化)
- [最佳实践与陷阱](#-最佳实践与陷阱)
- [常见问题](#-常见问题)

---

## 🔍 核心概念：数据模型与两端

Serde 把类型与数据格式分开：derive 描述 Rust 类型怎样映射到 Serde 数据模型，格式 crate 实现编码和解码。很多类型可以复用 derive，但换格式仍需检查限制：JSON 对象键必须能表示成字符串，TOML 顶层是表，某些格式不支持 `deserialize_any`。类型能 derive 不等于任意格式都支持往返转换。

```toml
# 下文命名完整程序分别保存为 src/main.rs；使用同一组依赖。
[dependencies]
serde = { version = "=1.0.229", features = ["derive"] }
serde_json = "=1.0.145"
toml = "=0.8.23"
```

下面为类型定义片段；是否适用于某个后端仍需检查该格式限制：

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
| `rename` | `#[serde(rename = "userName")]` | 单字段重命名；关键字也可用原始标识符 `r#type`，不必总加 rename |
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

### 完整程序：缺失、null、别名与跳过字段

<!-- rust-ecosystem: serde-fields -->
```rust
use serde::{Serialize, Deserialize};
#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
struct User {
    #[serde(alias = "name")]
    user_name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    nickname: Option<String>,
    #[serde(default)]
    age: u8,
    #[serde(skip)]
    internal: String,
}

fn main() {
let u: User = serde_json::from_str(r#"{"userName":"c"}"#).unwrap();
assert_eq!(u.age, 0);
assert_eq!(u.nickname, None);
assert_eq!(u.internal, "");
assert_eq!(serde_json::to_value(&u).unwrap(), serde_json::json!({"userName":"c", "age":0}));
assert_eq!(serde_json::from_str::<User>(r#"{"name":"ada"}"#).unwrap().user_name, "ada");
// default 处理缺失，不把 null 自动变成 u8 的 0。
assert!(serde_json::from_str::<User>(r#"{"userName":"c","age":null}"#).is_err());
assert!(serde_json::from_str::<User>(r#"{"name":"a","userName":"b"}"#).is_err());
println!("serde-fields: ok");
}
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
}  // JSON 数值 -3 → I；2.5 → F；JSON 字符串 "-3" 与 "x" → S
```

`tag` 单独使用选择内部标签，`tag` 与 `content` 联用选择邻接标签，`untagged` 选择无标签，不能与前两种表示组合。Serde 不支持将 `deny_unknown_fields` 与 `flatten` 联用；这不代表字段拍平在概念上必然允许任意键。[枚举表示](https://serde.rs/enum-representations.html)、[字段属性](https://serde.rs/field-attrs.html)

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

### 完整程序：手写 Serialize

<!-- rust-ecosystem: serde-serialize -->
```rust
use serde::ser::SerializeStruct;      // serialize_field 方法在此 trait 上
use serde::Serialize;

struct Point { x: i32, y: i32 }

impl Serialize for Point {
    fn serialize<S: serde::Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
        let mut st = s.serialize_struct("Point", 2)?;
        st.serialize_field("x", &self.x)?;
        st.serialize_field("y", &self.y)?;
        st.end()
    }
}
fn main() {
    assert_eq!(serde_json::to_string(&Point { x: 1, y: 2 }).unwrap(), r#"{"x":1,"y":2}"#);
    println!("serde-serialize: ok");
}
```

其他常用 Serializer 钩子：`serialize_str` / `serialize_i32` / `serialize_seq` / `serialize_map` / `serialize_newtype_struct`。

### 完整程序：Visitor 必须消费每个值

当决定忽略未知字段时，也必须调用 `next_value::<IgnoredAny>()` 消费其值，否则解析器仍停留在该字段的值上。下面独立程序还拒绝重复字段和缺失字段，避免损坏坐标悄悄变成 `(0, 0)`。

<!-- rust-ecosystem: serde-visitor -->
```rust
use serde::de::{MapAccess, Visitor, IgnoredAny, Error};
use serde::{Deserialize, Deserializer};

#[derive(Debug, PartialEq)]
struct Point { x: i32, y: i32 }
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
                "x" => {
                    if x.is_some() { return Err(A::Error::duplicate_field("x")); }
                    x = Some(map.next_value()?);
                }
                "y" => {
                    if y.is_some() { return Err(A::Error::duplicate_field("y")); }
                    y = Some(map.next_value()?);
                }
                _ => { let _: IgnoredAny = map.next_value()?; }
            }
        }
        Ok(Point {
            x: x.ok_or_else(|| A::Error::missing_field("x"))?,
            y: y.ok_or_else(|| A::Error::missing_field("y"))?,
        })
    }
}
fn main() {
    assert_eq!(serde_json::from_str::<Point>(r#"{"extra":{"a":[1,2]},"x":3,"y":4}"#).unwrap(), Point { x: 3, y: 4 });
    assert!(serde_json::from_str::<Point>(r#"{"x":3}"#).unwrap_err().to_string().contains("missing field"));
    assert!(serde_json::from_str::<Point>(r#"{"x":3,"x":4,"y":5}"#).unwrap_err().to_string().contains("duplicate field"));
    assert!(serde_json::from_str::<Point>(r#"{"x":"bad","y":4}"#).is_err());
    println!("serde-visitor: ok");
}
```

Visitor 按"你愿意接受的数据形态"实现 `visit_str`/`visit_map`/`visit_seq`/`visit_u64` 等入口；没实现的形态得到默认的"类型不匹配"错误。

### `with` 模块契约

下面是独立完整程序；定义了 `Point`、模块导入、解析与失败路径，不依赖前面示例中的类型。

<!-- rust-ecosystem: serde-with -->
```rust
use serde::{Serialize, Deserialize};
#[derive(Debug, PartialEq)]
struct Point { x: i32, y: i32 }
mod point_as_str {
    use super::Point;
    use serde::{Deserialize, Deserializer, Serializer};
    use serde::de::Error;

    pub fn serialize<S: Serializer>(v: &Point, s: S) -> Result<S::Ok, S::Error> {
        s.serialize_str(&format!("({},{})", v.x, v.y))
    }
    pub fn deserialize<'de, D: Deserializer<'de>>(d: D) -> Result<Point, D::Error> {
        let s = String::deserialize(d)?;
        let body = s.strip_prefix('(').and_then(|s| s.strip_suffix(')'))
            .ok_or_else(|| D::Error::custom("expected (x,y)"))?;
        let (x, y) = body.split_once(',').ok_or_else(|| D::Error::custom("missing comma"))?;
        Ok(Point { x: x.parse().map_err(D::Error::custom)?, y: y.parse().map_err(D::Error::custom)? })
    }
}

#[derive(Debug, PartialEq, Serialize, Deserialize)]
struct Wrapper(#[serde(with = "point_as_str")] Point);
fn main() {
    let value = Wrapper(Point { x: -3, y: 4 });
    let encoded = serde_json::to_string(&value).unwrap();
    assert_eq!(encoded, r#""(-3,4)""#);
    assert_eq!(serde_json::from_str::<Wrapper>(&encoded).unwrap(), value);
    for bad in [r#""3,4""#, r#""(3,4,5)""#, r#""(x,4)""#] {
        assert!(serde_json::from_str::<Wrapper>(bad).is_err());
    }
    println!("serde-with: ok");
}
```

`with = "module"` 要求模块提供上述两个自由函数；只单向需要时用 `serialize_with`/`deserialize_with`。

## 🎨 最佳实践与陷阱

序列化字段名、null 与缺失是接口契约，camelCase 和省略 None 都不是普遍规定。例如 PATCH 中“未提供”与“主动清空”可能不同，需要显式建模，不能只靠一个 Option 草率合并。

derive 适合类型结构与格式一致的场景，特殊边界可使用转换或自定义实现。untagged 的匹配顺序与错误反馈需测试，flatten 与 deny_unknown_fields 按 Serde 支持限制使用；未知字段仍有概念，不能把配置不兼容解释成未知键不存在。

## ❓ 常见问题

### 练习：把外部 JSON 当作不可信输入

先执行四个完整程序，再把 `Point` 的未知字段策略从“消费并忽略”改成“返回错误”。验收时保留正常、缺失、重复、类型不匹配四类输入，并增加未知嵌套对象。解释为什么 `age: null` 与缺少 `age` 不等价；如果接口要支持主动清空昵称，应如何区别字段缺失与显式 null？答案应写成输入/输出表，不能只写“使用 Option”。

### Q1: 字段名撞 Rust 关键字（如 `type`、`ref`）怎么办？
**A**: 用 `#[serde(rename = "type")]` 显式指定线格式名字；Rust 侧声明可用原生标识符 `r#type`。推荐 rename 方案——线格式名与 Rust 命名解耦。

### Q2: 什么时候需要手写 Serialize/Deserialize？
**A**: 当默认映射不足以表达格式时，可考虑自定义实现，例如颜色三元组与十六进制字符串互转。校验可以先用 `try_from`，外部类型可先用 remote derive，并非都必须写 Visitor。属性能表达的映射通常优先使用属性，但单向 skip、default、alias 本来就可能使读写不对称，derive 不保证任意数据往返后保持原样。

## 📏 模式不变量

1. **数据模型是合约**：类型与格式之间有一层抽象，但每种格式只支持其中一部分形态；更换后端必须重新验证数据契约。
2. **线格式名与内存名是两个命名空间**：`rename/rename_all` 的存在本身证明两侧命名各自演化，跨语言接口永远显式声明线名。
3. **读取与写出分别设计**：`default` 决定缺字段时的读取行为；`skip` 同时影响两个方向；`skip_serializing_if` 只影响写出。不要把单向策略当成往返保证。
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


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
