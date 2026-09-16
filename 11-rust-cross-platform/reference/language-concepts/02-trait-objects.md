# trait 对象与动态分发字典（dyn Trait / 对象安全 / vtable）

> **文档简介**: `dyn Trait` 全量速查——dyn 兼容性（对象安全）规则表、胖指针与 vtable 机制、静态分发对比矩阵、Box/&/Rc/Arc 载体选择、默认生命周期与向上转型。
>
> **目标读者**: 需要在"泛型还是 dyn"之间做决策、或排查 E0038 的 Rust 使用者。
>
> **前置知识**: 无门槛（字典条目，支持任意跳入）；trait 与泛型系统学习见[trait 与泛型教程](../../basics/04-traits-generics.md)。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 字典（全量参考，单一事实来源） |
| **难度** | ⭐⭐（无阅读门槛，内容纵深） |
| **标签** | `#rust` `#reference` `#trait-object` `#dynamic-dispatch` |
| **更新日期** | `2026年9月` |

> 版本基线：Rust 1.98.1 / edition 2024（核实记录见模块 README）。本文用现行官方术语 **dyn 兼容**（dyn compatibility，旧称 object safe / 对象安全）；示例均经本机 rustc（edition 2024）编译运行实测。

## 📋 目录

- [一、定义与胖指针](#一定义与胖指针)
- [二、dyn 兼容性规则表](#二dyn-兼容性规则表)
- [三、vtable 机制](#三vtable-机制)
- [四、静态分发 vs 动态分发对比表](#四静态分发-vs-动态分发对比表)
- [五、载体选择：&dyn / Box<dyn> / Rc·Arc<dyn>](#五载体选择dyn--boxdyn--rcarcdyn)
- [六、trait 对象的默认生命周期](#六trait-对象的默认生命周期)
- [七、supertrait 与向上转型、自动 trait](#七supertrait-与向上转型自动-trait)
- [八、enum 封闭集合 vs dyn 开放集合](#八enum-封闭集合-vs-dyn-开放集合)
- [九、错误码：E0038](#九错误码e0038)
- [示例与编译失败演示](#-可运行示例)
- [常见陷阱](#-常见陷阱)
- [相关条目](#-相关条目)

---

## 📌 一、定义与胖指针

**定义**: `dyn Trait` 是一个**动态大小类型（DST）**，表示"某个实现了 Trait 的类型，但编译期不知道是哪个"。方法调用经虚表（vtable）在运行期间接分发——即动态分发。

- DST 不能直接存值（编译期大小未知），只能藏在指针后面：`&dyn Trait`、`Box<dyn Trait>`、`Rc<dyn Trait>`、`Arc<dyn Trait>`、`Pin<P>`、`*const dyn Trait`。
- 指向 trait 对象的指针是**胖指针**：一个字宽存数据地址 + 一个字宽存 vtable 地址（普通引用是瘦指针，一个字宽）。此宽度事实经本机 `size_of` 实测（见示例三）。

---

## 📌 二、dyn 兼容性规则表

trait 必须满足 dyn 兼容才能写成 `dyn Trait`。逐形态判定：

| 形态 | dyn 兼容？ | 说明 / 出路 |
|------|------|------|
| 方法带泛型类型参数（生命周期参数除外） | ❌ | vtable 无法为无限多实例化各备一份入口；泛型上移到 trait 级参数，或方法改收已擦除类型（如 `String`） |
| 方法返回 `Self` 或按值收 `Self` | ❌ | dyn 之下 `Self` 大小未知；加 `where Self: Sized` 让该方法退出对象，trait 仍兼容 |
| 无接收者的关联函数（静态方法） | ❌（该方法） | 同上加 `where Self: Sized` 收编 |
| trait 声明 `Self: Sized` | ❌（整个 trait） | 设计上只允许静态分发 |
| 有关联常量 | ❌ | 无法按类型静态入表 |
| GAT（泛型关联类型） | ❌ | 表无法承载按类型参数化的签名 |
| 接收者为 `&Self` / `&mut Self` / `Box<Self>` / `Rc<Self>` / `Arc<Self>` / `Pin<P>` | ✅ | 标准接收者集合 |
| 有关联类型 | ✅ | 对象类型中需指定：`Box<dyn Iterator<Item = u32>>` |

**典型非兼容 trait 的替代模式**: `Clone` 因 `clone(&self) -> Self` 不可直接 dyn；惯用出口是自定义 `fn clone_box(&self) -> Box<dyn Trait>`（返回 `Box<Self>` 是定长指针，dyn 兼容），为 `Box<dyn Trait>` 实现 `Clone` 委托之——完整可运行写法见示例五。

---

## 📌 三、vtable 机制

- 每个具体类型为实现的所有 dyn 兼容 trait 各生成一张 vtable；表内含析构/清理入口、`size`、`align` 与各方法指针（按声明序）。
- `w.draw()`（`w: &dyn Draw`）实际执行：读胖指针第二半 → 查表定位方法指针 → 以数据指针为 `self` 调用。
- 代价：一次指针间接跳转，且通常阻断内联。
- vtable 内存布局是编译器实现细节，跨版本不可依赖；可依赖的只有"胖指针两字宽"这类稳定事实。

---

## 📌 四、静态分发 vs 动态分发对比表

| 维度 | 泛型 / `impl Trait`（静态分发） | `dyn Trait`（动态分发） |
|------|------|------|
| 机制 | 单态化：每个用到的类型各生成一份代码 | vtable 间接调用：单份代码 |
| 内联 | 可以（热路径优化友好） | 通常不可 |
| 二进制体积 | 实例化类型多时膨胀 | 恒定一份 |
| 集合异构 | 需 `enum` 包装（封闭集合） | 直接混存（开放集合） |
| 返回多态 | `impl Trait`（单一具体类型，编译期定死） | `Box<dyn Trait>`（运行期任一实现） |
| 约束检查 | 全部在编译期（调用点） | 方法存在性在编译期，具体调用仍间接 |
| 性能 | 零成本抽象 | 一次指针跳转 + 阻碍内联 |

**选择口诀**: 类型集合封闭且追求热路径 → 泛型/enum；集合开放（插件、回调、UI 组件、异构容器）或要缩体积 → `dyn Trait`。

---

## 📌 五、载体选择：&dyn / Box<dyn> / Rc·Arc<dyn>

| 载体 | 所有权语义 | 典型场景 |
|------|------|------|
| `&dyn Trait` / `&mut dyn Trait` | 借用 | 传参、局部多态，零分配 |
| `Box<dyn Trait>` | 独占（堆） | 异构集合（`Vec<Box<dyn Trait>>`）、多态返回值、递归结构 |
| `Rc<dyn Trait>` / `Arc<dyn Trait>` | 共享计数 | 回调注册表；跨线程用 `Arc<dyn Trait + Send + Sync>` |
| 裸值 `dyn Trait` | ❌ | DST，不可直接存值 |

---

## 📌 六、trait 对象的默认生命周期

独立出现的位置默认补 `'static`；跟在引用后面默认取该引用的生命周期：

| 写法 | 默认补全为 |
|------|------|
| `Box<dyn Trait>` | `Box<dyn Trait + 'static>` |
| 类型参数位置等独立出现（如 `T = dyn Trait`） | `dyn Trait + 'static` |
| `&'a dyn Trait` | `&'a (dyn Trait + 'a)` |

含义：`Box<dyn Trait>` 默认只能装"常驻数据"（owned 类型或 `'static` 引用）；要装短命引用必须显式写 `Box<dyn Trait + 'a>`。生命周期含义的展开见[高级生命周期](./04-advanced-lifetimes.md)。

---

## 📌 七、supertrait 与向上转型、自动 trait

- **向上转型（upcasting）**：`&dyn Sub` 可直接转 `&dyn Super`（`trait Sub: Super` 时），无需任何 crate 辅助。已实测（示例四）。反向（`&dyn Super` → `&dyn Sub`）仍不可，需在 trait 上提供安全的 downcast 方法（如返回 `Option<&dyn Any>`）。
- **自动 trait 不随擦除传递**：具体类型是 `Send`/`Sync` 不代表 `dyn Trait` 是——跨线程必须显式写 `dyn Trait + Send`、`dyn Trait + Send + Sync`。
- 可为对象类型实现新 trait：`impl Trait for dyn Trait`（如为 `Box<dyn Greeter>` 实现 `Clone`，见示例五）。

---

## 📌 八、enum 封闭集合 vs dyn 开放集合

| | `enum` | `dyn Trait` |
|------|------|------|
| 类型集合 | 编译期固定 | 任何 crate 可新增实现 |
| 分发方式 | `match`（编译器可内联、可穷尽检查） | vtable 间接调用 |
| 新增变体成本 | 改 enum 定义 + 全部 match | 新增一个 `impl` 即可 |
| 适用 | 本模块内部的封闭变体 | 插件、回调、跨 crate 扩展点 |

---

## 📌 九、错误码：E0038

`E0038`：trait 不满足 dyn 兼容（现行提示语 "not dyn compatible"，旧提示语 "not object safe"）。触发于把不兼容 trait 用作对象类型；逐条对照第二节规则表定位是哪个成员破坏兼容，按"出路"列修复。编译失败演示见下文。

---

## 💡 可运行示例

### 示例一：异构集合与 `&dyn` 传参

```rust
trait Draw {
    fn draw(&self) -> String;
}
struct Button {
    label: String,
}
struct Slider {
    value: i32,
}

impl Draw for Button {
    fn draw(&self) -> String {
        format!("[按钮:{}]", self.label)
    }
}
impl Draw for Slider {
    fn draw(&self) -> String {
        format!("<滑杆:{}%>", self.value)
    }
}

fn preview(w: &dyn Draw) {
    // 形参也是胖指针：具体类型在编译期不可见
    println!("预览: {}", w.draw());
}

fn main() {
    // 同一集合容纳不同具体类型：动态分发的核心能力
    let ui: Vec<Box<dyn Draw>> = vec![
        Box::new(Button {
            label: String::from("提交"),
        }),
        Box::new(Slider { value: 72 }),
    ];
    for w in &ui {
        println!("{}", w.draw()); // 经 vtable 间接调用
    }
    let b = Button {
        label: String::from("取消"),
    };
    preview(&b); // &dyn：借用即多态，无需堆分配
}
```

已实测（输出三行：按钮、滑杆、预览）。

### 示例二：同一 trait 的两种分发

```rust
use std::f64::consts::PI;

trait Area {
    fn area(&self) -> f64;
}
struct Circle {
    r: f64,
}
struct Square {
    s: f64,
}
impl Area for Circle {
    fn area(&self) -> f64 { PI * self.r * self.r }
}
impl Area for Square {
    fn area(&self) -> f64 { self.s * self.s }
}

// 静态分发：编译期单态化出 area_of::<Circle> 与 area_of::<Square> 两份代码
fn area_of<S: Area>(shape: &S) -> f64 {
    shape.area()
}

fn main() {
    let c = Circle { r: 2.0 };
    let s = Square { s: 3.0 };
    println!("{:.2} {:.2}", area_of(&c), area_of(&s));

    // 同一数组混合两种类型：只能借助 dyn
    let shapes: [&dyn Area; 2] = [&c, &s];
    for sh in shapes {
        println!("{:.2}", sh.area());
    }
}
```

已实测（`12.57 9.00` 两轮）。

### 示例三：胖指针宽度实证

```rust
trait Speak {
    fn hi(&self) -> &'static str;
}

impl Speak for i32 {
    fn hi(&self) -> &'static str {
        "int"
    }
}
impl Speak for f64 {
    fn hi(&self) -> &'static str {
        "float"
    }
}

fn main() {
    let x: &dyn Speak = &7i32;
    println!("{}", x.hi());
    // 主流平台：&dyn Trait 是胖指针（数据地址 + vtable 地址）
    assert_eq!(
        std::mem::size_of::<&dyn Speak>(),
        2 * std::mem::size_of::<usize>()
    );
    // 普通引用是瘦指针
    assert_eq!(std::mem::size_of::<&i32>(), std::mem::size_of::<usize>());
    println!("胖指针布局确认");
}
```

已实测通过（主流平台两字宽断言成立）。

### 示例四：trait 向上转型

```rust
trait Animal {
    fn name(&self) -> &'static str;
}
trait Dog: Animal {
    fn bark(&self) -> &'static str;
}

struct Pup;
impl Animal for Pup {
    fn name(&self) -> &'static str {
        "pup"
    }
}
impl Dog for Pup {
    fn bark(&self) -> &'static str {
        "woof"
    }
}

fn main() {
    let d: &dyn Dog = &Pup;
    let a: &dyn Animal = d; // trait 对象向上转型：dyn Dog → dyn Animal
    println!("{} says {}", a.name(), d.bark());
}
```

已实测（输出 `pup says woof`）。

### 示例五：让 `Box<dyn Trait>` 可克隆（clone_box 模式）

```rust
trait Greeter {
    fn greet(&self) -> String;
    // 为 dyn 兼容提供克隆出口：返回 Box<Self> 是定长指针
    fn clone_box(&self) -> Box<dyn Greeter>;
}

// Box 是 #[fundamental]，可为本地 trait 的对象类型实现外部 trait Clone
impl Clone for Box<dyn Greeter> {
    fn clone(&self) -> Self {
        self.clone_box()
    }
}

struct En;
impl Greeter for En {
    fn greet(&self) -> String {
        String::from("hello")
    }
    fn clone_box(&self) -> Box<dyn Greeter> {
        Box::new(En)
    }
}

fn main() {
    let g: Box<dyn Greeter> = Box::new(En);
    let g2 = g.clone(); // Box<dyn Greeter> 可克隆
    println!("{} {}", g.greet(), g2.greet());
}
```

已实测（输出 `hello hello`）。

## ⚠️ 编译失败演示

**此块为编译失败演示，错误码已实测复核**（rustc，edition 2024）。

E0038：泛型方法破坏 dyn 兼容。

```rust
trait Collector {
    // 泛型方法：每个 T 都需要独立入口，vtable 无法静态列举 → 破坏 dyn 兼容
    fn collect_all<T: Into<String>>(&mut self, items: Vec<T>);
}
struct Log;

impl Collector for Log {
    fn collect_all<T: Into<String>>(&mut self, items: Vec<T>) {
        for i in items {
            let _: String = i.into();
        }
    }
}

fn main() {
    let _c: Box<dyn Collector> = Box::new(Log); // ❌ E0038
    let _ = _c;
}
```

实测报错：`error[E0038]: the trait 'Collector' is not dyn compatible`。

---

## ⚠️ 常见陷阱

- ❌ **写 `Vec<dyn Trait>` 直接存值** → DST 不可作为集合元素类型。
  - ✅ `Vec<Box<dyn Trait>>`（或 `Vec<&dyn Trait>` 借用已有值）。
- ❌ **以为 `dyn Trait` 自动继承具体类型的 `Send`/`Sync`**。
  - ✅ 自动 trait 必须显式写进对象类型：`dyn Trait + Send + Sync`。
- ❌ **用 dyn 一刀切"降低编译时间"**。
  - ✅ 热路径保留泛型（内联/常量传播）；dyn 用于边界与异构存储。
- ❌ **`Box<dyn Error>` 装不进短命引用**（默认 `'static`）。
  - ✅ 显式 `Box<dyn Error + 'a>`；错误处理库选型见[错误库字典](../library-guides/14-error-libraries.md)。
- ❌ **给已发布的 dyn 兼容 trait 随手加泛型方法** → 全部对象用法炸 E0038。
  - ✅ 泛型参数上移到 trait 级，或方法加 `where Self: Sized`。

---

## 🔗 相关条目

- 📄 **[trait 与泛型（入门教程）](../../basics/04-traits-generics.md)** — 静态分发的系统学习路径
- 📄 **[智能指针](../../basics/08-smart-pointers.md)** — Box / Rc / Arc 载体细节
- 📄 **[所有权细则](./01-ownership-dictionary.md)** — `Box<dyn Trait>` 转移/借用的所有权语义
- 📄 **[高级生命周期](./04-advanced-lifetimes.md)** — 对象默认 `'static` 的生命周期展开
- 📄 **[常量泛型](./03-const-generics.md)** — 编译期参数化的另一维度
- 🌐 **[The Rust Reference: Dynamically Sized Types](https://doc.rust-lang.org/reference/dynamically-sized-types.html)** — DST 与 trait 对象官方定义

---

## 📝 要点回顾

1. **`dyn Trait` 是 DST**：只能活在指针后，胖指针 = 数据地址 + vtable 地址。
2. **dyn 兼容性看成员**：无泛型方法、无 `Self` 按值、无关联常量/GAT；`where Self: Sized` 是成员级逃生口。
3. **静态 vs 动态一句话**：泛型换内联与体积，dyn 换开放集合与多态返回。
4. **默认 `'static`**：`Box<dyn Trait>` 只装常驻数据，短命引用要显式 `+ 'a`。
5. **`E0038` = dyn 兼容性被破坏**，对照规则表逐成员定位。

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
