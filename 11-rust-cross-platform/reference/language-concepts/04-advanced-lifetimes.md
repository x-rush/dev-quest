# 高级生命周期字典（变型 / HRTB / 'static 两种含义）

## 阅读准备：先用一个反例确定本章的问题

前置：[生命周期基础](../../basics/07-lifetimes.md)、引用和泛型。此文可独立查词，但不是所有权第一课。看不懂变型时先退回“引用不能比被借数据用得更久”的约束。

设某容器承诺里面放的是 &'static str。如果允许把这个容器的可写引用当成存短生命周期字符串的容器，函数就可能塞进即将失效的引用，破坏原承诺。因此 `&mut T` 对 T 的不变性不是编译器刁难，而是在阻止通过写入口破坏调用方类型保证。

自测：将返回类型标成 &'static str，能否返回局部 String 的切片？不能；标注不会延长数据存活。需要返回新生成文本时应返回 String，或让调用者提供足够长寿的数据。等这个推理清楚后，再读 HRTB 对“任意调用生命周期”的量化。

> **文档简介**: 生命周期进阶规则速查——生命周期子类型与变型（协变/逆变/不变）、HRTB `for<'a>`、`&'static` 与 `T: 'static` 两种含义对照、struct 约束与省略规则、E0106/E0515/E0597/E0621/E0521 错误码速查。
>
> **目标读者**: 已会用基本标注、需要理解"为什么这个引用传不进去"的 Rust 使用者。
>
> **前置知识**: 可独立查阅（仍需准备下列前置知识）；标注基础见[生命周期标注教程](../../basics/07-lifetimes.md)。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 字典（全量参考，单一事实来源） |
| **难度** | ⭐⭐（可独立查阅，仍有前置知识，内容纵深） |
| **标签** | `#rust` `#reference` `#lifetimes` `#variance` `#hrtb` |
| **更新日期** | `2026年9月` |

</details>

> 版本基线：Rust 1.98.1 / edition 2024。文末命名的完整程序和编译失败反例由[Go/Rust 基础验证器](../../../shared-resources/tools/document-quality/verify_go_rust_basics.py)直接抽取；运行范围与结果见[验证报告](../../../shared-resources/tools/document-quality/reports/go-rust-basics.md)。签名片段不属于独立程序。

## 📋 目录

- [一、定位：生命周期约束引用，不改变值](#-一定位生命周期约束引用不改变值)
- [二、子类型：'static <: 'a](#-二子类型static--a)
- [三、变型表](#-三变型表)
- [四、HRTB：for<'a>](#-四hrtbfor)
- [五、&'static 与 T: 'static 两种含义](#-五static-与-t-static-两种含义)
- [六、struct / impl 中的生命周期与省略规则](#-六struct--impl-中的生命周期与省略规则)
- [七、dropck 约束简述](#-七dropck-约束简述)
- [八、错误码速查表](#-八错误码速查表)
- [示例与编译失败演示](#-可运行示例)
- [常见陷阱](#️-常见陷阱)
- [相关条目](#-相关条目)

---

## 📌 一、定位：生命周期约束引用，不改变值

**定义**: 生命周期是引用有效性的**静态描述**——它不延长任何值的存活时间，只约束"引用不得比被引数据活得更久"。运行期零开销。

- `'a` 是引用类型的组成部分：`&'a str` 与 `&'b str` 在 `'a ≠ 'b` 时是不同类型。
- 编译器为每个引用推导/检查 `'a`；程序员只在推断无法收敛时显式标注。
- 所有生命周期问题最终都能归约为：**被借数据活得 ≥ 引用所需**。

---

## 📌 二、子类型：'static <: 'a

生命周期之间存在**子类型关系**：若 `'long: 'short`，长生命周期的共享引用可以收窄为短生命周期的共享引用。`'static <: 'a` 表示这里的子类型方向；任意两个生命周期未必存在可证明的包含关系。表现在引用上：

| 事实 | 含义 |
|------|------|
| `&'static str` 可赋给 `&'a str` | 长命引用可**收窄**为短命引用（协变的直接推论） |
| `&'a str` 不可赋给 `&'static str` | 反向禁止，否则悬垂 |
| `Holder<'static>` 可当 `Holder<'a>` 用 | struct 对其生命周期参数协变时成立 |

---

## 📌 三、变型表

**变型（variance）** 决定"类型构造器随参数的子类型关系如何传播"——这是"为什么这个引用塞不进那个结构"的最终答案。

| 类型构造器 | 对 `'a` | 对 `T` | 说明 |
|------|------|------|------|
| `&'a T` | 协变 | 协变 | 长可当短用 |
| `&'a mut T` | 协变 | **不变** | T 不变：防短引用借道写入长插槽 |
| `Box<T>` / `Vec<T>` | — | 协变 | 值语义容器随元素协变 |
| `fn(T)`（参数位） | — | **逆变** | 参数位逆变：接受更广参数的函数可当更窄的用 |
| `fn() -> T`（返回位） | — | 协变 | 返回位协变 |
| `Cell<T>` 等内部可变性 | — | **不变** | 内部可写 ⇒ 等价 `&mut`，必须不变 |
| `struct S<'a, T>` 自定义 | 由字段逐个推出 | 由字段逐个推出 | 编译器按字段变型自动推导，不可手动标注 |

**不变性为何必要**: 若 `&'a mut &'static str` 对 `T` 协变，就能把 `&'b str`（`'b` 更短）写进 `'static` 插槽——短数据获得 `'static` 名义后被继续引用即悬垂。不变性堵死这条通路。反之，协变性是"长引用收窄"合法性的来源（第二节）。

---

## 📌 四、HRTB：for<'a>

**定义**: 高阶 trait 约束（HRTB）——约束"对**所有**可能的 `'a`"成立，而非某个具体 `'a`。

- 裸 fn 指针类型对输入引用即高阶：`fn(&str) -> &str` 的完整写法是 `for<'a> fn(&'a str) -> &'a str`。
- `Fn` 约束糖同理：`F: Fn(&str) -> &str` 隐含 `for<'a> Fn(&'a str) -> &'a str`——闭包对任意调用者给的引用都适用。
- 显式形式用于：fn 指针参数、trait bound（`F: for<'a> Fn(&'a str) -> &'a str`）、复杂返回签名。
- 常见动机：函数返回"借用自输入"的引用时，输出生命周期必须与调用处的实际输入绑定——HRTB 把"每次调用重新取 `'a`"写进类型。
- 闭包可以返回借用参数的引用，但类型推断需要足够的上下文；例如 `let identity: fn(&str) -> &str = |s| s;`。`move` 只改变捕获环境的方式，不会延长输入引用或自动建立返回值的生命周期关系。

完整形态见下文示例三。

---

## 📌 五、&'static 与 T: 'static 两种含义

**同名不同义，混淆是高频坑**：

| 写法 | 含义 | 满足者 |
|------|------|------|
| `&'static str`（引用类型中的 `'static`） | 引用所指数据从获得引用起可在程序剩余运行期使用 | 字符串字面量、静态存储、主动泄漏的 `Box`；从 `OnceLock` 借用的生命周期取决于 `OnceLock` 自身，局部实例不自动成为 `'static` |
| `T: 'static`（泛型约束） | 类型不携带短于 `'static` 的借用约束 | `String`、`Vec<i32>` 满足；拥有一个 `Vec<&'local str>` 并不使内部借用变成 `'static` |

- `T: 'static` 不要求这个值一直活到程序结束。示例四的 `String` 可在函数返回后立即释放；拥有值与其内部是否携带借用是两个问题。
- `&'local T` 不满足 `&'static` 形参要求（局部引用被拒，E0597 族）。
- `Box<dyn Trait>` 在类型签名中通常默认带 `'static` bound；表达式里可按上下文推断。也可明确写 `Box<dyn Trait + 'a>`，见[trait 对象篇](./02-trait-objects.md)。

---

## 📌 六、struct / impl 中的生命周期与省略规则

struct 持有引用必须声明参数并在字段中使用：

```rust
struct Excerpt<'a> {
    text: &'a str,
}
```

**省略规则**（推断收窄时按序套用）：

1. 每个作为输入的引用参数各获得一个独立的生命周期参数。
2. 若恰好只有一个输入生命周期，它赋给所有输出引用。
3. 方法带 `&self` / `&mut self` 时，`self` 的生命周期赋给所有输出引用。

普通自由函数 `fn pick(a: &str, b: &str) -> &str` 无法省略输出生命周期，因为编译器不知道返回值借自谁。方法的 `&self` 规则是例外：`fn pick(&self, other: &str) -> &str` 默认把输出绑定到 `self`。若函数总返回字面量，也可以明确返回 `&'static str`，无需把输出绑定到输入。

`impl` 块写法：`impl<'a> Excerpt<'a>`——方法内 `'a` 与 struct 的参数同一；方法签名内部再按省略规则 3 处理输出。

---

## 📌 七、dropck 约束简述

实现 `Drop` 且持有引用的类型有更严格的检查：其引用参数须**严格**长于自身存活期（保证析构函数运行时被引数据仍在）。编译器自动强制，违反时表现为 E0597；实践中避开方式是让 `Drop` 类型改持 owned 数据。此处仅作规则索引，完整 dropck 语义见官方 Reference。

---

## 📌 八、错误码速查表

| 错误码 | 含义 | 典型触发 | 修复方向 |
|------|------|------|------|
| `E0106` | 缺少生命周期标注 | 两个输入引用 + 输出引用，省略规则失效 | 显式 `<'a>` 把输入输出关联 |
| `E0515` | 返回局部值的引用 | `return &local` | 返回 owned / 把数据传参进来 |
| `E0597` | 被借值活得不够久 | 局部值借给更长命的结构 | 拉长被借值作用域 / 返回 owned |
| `E0621` | 函数签名与实际借用流不符 | 返回第二个输入的引用，但只给第一个输入标了输出所需生命周期 | 按实际数据来源关联参数，而非随意扩大到 `'static` |
| `E0521` | 借用数据逃逸出闭包等边界 | 把只在调用中有效的引用存入更长寿命的容器 | 缩短容器使用范围，或复制引用所指的数据；`move` 一个引用仍只是引用 |
| `E0373` | 闭包可能比当前函数活得久 | 闭包借环境值又被存入更长结构 | `move` 捕获 / 只捕获不可变副本 |
| `E0700` | 隐藏类型捕获了未允许捕获的生命周期 | 旧 edition 的返回位置 `impl Trait` 捕获输入借用 | 先核对 edition：2024 默认捕获所有作用域内泛型参数，可用 `use<...>` 精确捕获；不要把所有问题机械改成 `+ 'a` |

---

## 💡 可运行示例

### 示例一：显式关联与省略规则、NLL 的组合

<!-- verified-case: rust-lifetime-nll -->
```rust
// 两个输入引用时省略规则不适用，必须显式标注
fn longest<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() >= b.len() {
        a
    } else {
        b
    }
}

struct Excerpt<'a> {
    text: &'a str,
}

impl<'a> Excerpt<'a> {
    // 省略规则第 3 条：&self 的生命周期赋给输出引用
    fn shout(&self) -> &str {
        self.text
    }
}

fn main() {
    let s1 = String::from("long string first");
    let result;
    {
        let s2 = String::from("xyz");
        result = longest(s1.as_str(), s2.as_str());
        println!("{result}"); // result 的最后使用点在 s2 销毁前
    } // ✅ 借用已按 NLL 结束，合法
    let e = Excerpt { text: &s1 };
    println!("{} / {}", e.shout(), e.text);
}
```

预期输出是两行，第二行打印两个字段值：

```text
long string first
long string first / long string first
```

### 示例二：子类型与协变实证

<!-- verified-case: rust-lifetime-covariance -->
```rust
struct Holder<'a> {
    s: &'a str,
}

fn use_short<'a>(h: Holder<'a>) -> &'a str {
    h.s
}

fn main() {
    // 'static <: 'a：'static 是任何生命周期的子类型
    let owned: &'static str = "字面量天然 'static";
    let narrowed: &str = owned; // 长命引用收窄为短命引用
    println!("{narrowed} / {owned}");

    // 协变：Holder<'static> 可以当作 Holder<'a> 使用
    let h: Holder<'static> = Holder { s: "常驻文本" };
    println!("{}", use_short(h));
}
```

预期输出：

```text
字面量天然 'static / 字面量天然 'static
常驻文本
```

### 示例三：HRTB 的 fn 指针与 Fn 约束糖

<!-- verified-case: rust-lifetime-hrtb -->
```rust
// 裸 fn 指针类型对输入引用即高阶：for<'a> 是它的完整写法
fn apply(f: for<'a> fn(&'a str) -> &'a str, s: &str) -> String {
    f(s).to_uppercase()
}

fn shout(s: &str) -> &str {
    s
}

fn main() {
    // Fn(&str) -> &str 这类约束糖同样隐含 for<'a> 高阶量化
    fn sugar<G: Fn(&str) -> &str>(g: G) -> String {
        g("sugar").to_string()
    }
    println!("{}", apply(shout, "hrtb"));
    println!("{}", sugar(shout));
    let identity: fn(&str) -> &str = |s| s;
    let local = String::from("closure");
    println!("{}", identity(&local));
}
```

预期输出：

```text
HRTB
sugar
closure
```

### 示例四：`T: 'static` 接受 owned

<!-- verified-case: rust-lifetime-static -->
```rust
fn keep<T: 'static>(value: T) -> T {
    // 约束含义：T 不携带短于 'static 的借用；不能只看是否按值传入
    value
}

fn store(s: &'static str) -> &'static str {
    s
}

fn main() {
    // String 不借用外部数据，满足 T: 'static；值本身仍可提前释放
    println!("{}", keep(String::from("owned 也满足 'static 约束")));

    // store 形参是真正的 &'static str：只有常驻数据满足
    println!("{}", store("字面量"));

    let local = String::from("局部值");
    // store(&local); // ❌ 局部引用不满足 'static（E0597 族）
    println!("{}", local);
}
```

预期输出：

```text
owned 也满足 'static 约束
字面量
局部值
```

## ⚠️ 编译失败演示

以下是有意不能编译的反例。验证器要求 rustc 失败且包含声明的错误码，不能把这类代码当成成功程序。

E0597：被借值活得不够久——struct 持有已销毁局部值引用。

<!-- verified-case: rust-lifetime-dangling; error=E0597 -->
```rust
struct Reader<'a> {
    text: &'a str,
}

fn main() {
    let r;
    {
        let local = String::from("临时数据");
        r = Reader { text: &local };
    } // local 在此销毁
    println!("{}", r.text); // r 仍存活并使用 local 的数据 → 错误
}
```

预期错误码：`E0597`，局部 `local` 不够长寿。

E0106：省略规则失效——两个输入引用 + 输出引用。

<!-- verified-case: rust-lifetime-elision; error=E0106 -->
```rust
fn pick(a: &str, b: &str) -> &str {
    if a.len() > b.len() {
        a
    } else {
        b
    }
}

fn main() {
    println!("{}", pick("aa", "b"));
}
```

预期错误码：`E0106`，输出无法从两个独立的输入生命周期中选择。

拥有容器仍可能借用局部值。下面的 `Vec` 是按值传递，但其中的 `&str` 不满足 `'static`：

<!-- verified-case: rust-lifetime-owned-borrow; error=E0597 -->
```rust
fn keep<T: 'static>(value: T) -> T { value }

fn main() {
    let local = String::from("borrowed");
    let values = vec![local.as_str()];
    let _ = keep(values);
}
```

---

## ⚠️ 常见陷阱

- ❌ **给所有泛型无脑加 `T: 'static`**，然后困惑"为什么传引用不行"。
  - ✅ 先明确接收方是否必须独立于调用者借用而存活。按值传参也能携带借用，不必为了消除标注而一律要求 `'static`。
- ❌ **以为 `'static` 只能来自字面量**。
  - ✅ `Box::leak` 可造，但会放弃自动释放；静态存储的 `OnceLock` 与局部 `OnceLock` 的借用时长不同。
- ❌ **把 `move` 当成延长借用的指令**。
  - ✅ `move` 捕获 `&str` 仍然持有借用；返回输入引用需要正确类型关系，示例三展示了允许这种关系的函数指针上下文。
- ❌ **混淆参数位逆变与返回位协变**，导致"理应能传"的 fn 指针赋值失败。
  - ✅ 对照第三节变型表：`fn(T)` 的 T 是逆变位，`fn() -> T` 的 T 是协变位。
- ❌ **struct 持引用又实现 `Drop` 遇到严格 outlive 报错**（dropck，第七节）。
  - ✅ `Drop` 类型改持 owned 数据，或缩短 struct 自身生命期。

---

## 🔗 相关条目

- 📄 **[生命周期标注（入门教程）](../../basics/07-lifetimes.md)** — 标注语法与基础推断
- 📄 **[所有权细则](./01-ownership-dictionary.md)** — NLL 借用区间与 E0597 的所有权视角
- 📄 **[trait 对象与动态分发](./02-trait-objects.md)** — 对象默认 `'static` bound 的展开
- 📄 **[智能指针](../../basics/08-smart-pointers.md)** — owned 化摆脱生命周期纠缠
- 🌐 **[The Rust Reference: Subtyping and Variance](https://doc.rust-lang.org/reference/subtyping.html)** — 子类型与变型官方定义
- 🌐 **[The Rustonomicon: Subtyping and Variance](https://doc.rust-lang.org/nomicon/subtyping.html)** — 不变性必要性的完整论证
- 🌐 **[The Rust Reference: Lifetime elision](https://doc.rust-lang.org/reference/lifetime-elision.html)** — 接收者规则、函数指针与对象生命周期默认值
- 🌐 **[Rust By Example: Static](https://doc.rust-lang.org/rust-by-example/scope/lifetime/static_lifetime.html)** — 引用生命周期与类型约束

---

## 📝 要点回顾

1. **生命周期只约束引用**：不延长值，`'static <: 'a` 是一切收窄的基础。
2. **变型决定传播**：`&'a T` 双协变，`&'a mut T` 的 T 不变（防写入逃逸），参数位逆变。
3. **HRTB = 对所有 `'a` 成立**：`Fn(&str) -> &str` 糖已隐含；fn 指针显式写 `for<'a>`。
4. **`&'static` 与 `T: 'static` 是两回事**：后者约束类型携带的借用，不强迫值永远存活，拥有容器也可能包含短借用。
5. **多输入引用的自由函数可能需要显式标注**；方法还适用 `&self` 规则。struct 持引用并实现 `Drop` 时，还须满足析构阶段的借用检查。

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
