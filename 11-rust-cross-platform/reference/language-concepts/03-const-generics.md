# 常量泛型字典（const N / 数组与固定长度抽象 / 稳定版限制）

> **文档简介**: 常量泛型全量速查——`const N: usize` 语法、允许的参数类型、数组与固定长度抽象、与类型参数对比矩阵、稳定版限制清单（泛型类型位置中的 N + 1 等表达式受限；默认值是否可用取决于声明位置）。
>
> **目标读者**: 需要把"长度/容量/维度"编码进类型，或排查常量泛型编译错误的 Rust 使用者。
>
> **前置知识**: 可独立查阅（仍需准备下列前置知识）；泛型系统学习见[trait 与泛型教程](../../basics/04-traits-generics.md)。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 字典（全量参考，单一事实来源） |
| **难度** | ⭐⭐（可独立查阅，仍有前置知识，内容纵深） |
| **标签** | `#rust` `#reference` `#const-generics` `#type-system` |
| **更新日期** | `2026年9月` |

</details>

> 版本基线：Rust 1.98.1 / edition 2024（核实记录见模块 README）。限制依据 Rust Reference 按上下文核对；编译器能力可能随版本变化，本轮未运行 rustc。

## 📋 目录

- [一、定义与语法](#-一定义与语法)
- [二、允许的参数类型](#-二允许的参数类型)
- [三、数组与固定长度抽象](#-三数组与固定长度抽象)
- [四、常量参数在 trait / impl 中](#-四常量参数在-trait--impl-中)
- [五、与类型参数对比表](#-五与类型参数对比表)
- [六、类型级身份与实参推断](#-六类型级身份与实参推断)
- [七、稳定版限制清单](#-七稳定版限制清单)
- [八、运行期容量 vs 类型级容量](#-八运行期容量-vs-类型级容量)
- [示例与编译失败演示](#-可运行示例)
- [常见陷阱](#️-常见陷阱)
- [相关条目](#-相关条目)

---

## 📌 一、定义与语法

**定义**: 常量泛型把**编译期值**（如数组长度）作为类型的一部分参与单态化——`N` 不同的两个类型互不兼容，长度错误从运行期提前到编译期。

可携带常量参数的声明位置：`fn`、`struct`、`enum`、`trait`、`impl` 块。

```rust
// 声明位置示意（可运行完整示例见下文示例一/示例二/示例三）
struct FixedBuf<const N: usize> {
    data: [u8; N],
    len: usize,
} // struct
impl<const N: usize> FixedBuf<N> {} // impl 块：方法体内可用 N
trait Buf<const N: usize> {
    // trait 内允许无方法体的签名
    fn load(&self) -> [u8; N];
}
```

显式指定用 turbofish：`sum::<3>([1, 2, 3])`；多数场景靠实参推断。

---

## 📌 二、允许的参数类型

| 参数种类 | 稳定版 | 说明 |
|------|------|------|
| 所有整数类型（`usize` / `u8` / `i64` / …） | ✅ | 数组长度约定用 `usize` |
| `bool` | ✅ | 编译期开关标记 |
| `char` | ✅ | 少见但可用 |
| 浮点数 | ❌ | 禁止作为常量参数类型 |
| `&str` / `&T` 引用 | ❌ | 预期诊断："`&'static str` is forbidden as the type of a const generic parameter"（见演示二） |
| 自定义 struct 作为参数 | ❌ | 稳定版不支持 |

---

## 📌 三、数组与固定长度抽象

- `[T; N]` 中的 `N` 就是常量泛型的内置应用：**长度是类型的一部分**，`[i32; 2]` 与 `[i32; 3]` 是不同类型。
- 泛型函数天然接受任意长度：`fn sum<const N: usize>(values: [i32; N]) -> i32`。
- 数组到切片的 unsize 强转（`&[T; N]` → `&[T]`）自动发生——**多数 API 用切片即可，无需常量泛型**；只有"长度要进类型"时才用 `const N`。
- `[值; N]` 重复语法要求 `值` 为 `Copy` 类型或常量表达式。

---

## 📌 四、常量参数在 trait / impl 中

- `trait Buf<const N: usize>`：trait 级常量参数，实现时按值逐个实现；默认方法体可直接使用 `N`。
- `impl<const N: usize> FixedBuf<N>`：impl 块声明后，方法签名与体内可用 `N`（`[0; N]`、`self.len == N` 等）。
- 常量参数与类型参数可混用：`struct Grid<T, const W: usize, const H: usize>`。

---

## 📌 五、与类型参数对比表

| 维度 | 类型参数 `T` | 常量参数 `N` |
|------|------|------|
| 承载内容 | 类型 | 编译期值 |
| 允许种类 | 任意类型 | 稳定版仅整数 / `bool` / `char` |
| 约束表达 | `T: Trait` | 无法加 trait 约束；比较/算术受限（见第七节） |
| 典型用途 | 元素类型抽象 | 数组长度、容量、编译期维度 |
| 单态化 | 每类型一份 | 每**值**一份（`N` 取值多时注意膨胀） |
| 推断 | 按实参类型推断 | 按实参值推断，或 turbofish / 块表达式显式 |

---

## 📌 六、类型级身份与实参推断

- `N` 参与类型身份：`FixedBuf<4>` 与 `FixedBuf<8>` 是不同类型，互不能赋值。
- 字面量实参自动推断 `N`（`sum([1, 2, 3])` → `N = 3`）。
- 非 const 上下文的变量不能直接作实参；const 项或块表达式可以：

```rust
const N: usize = 3;
// sum::<{ N }>([0; N])        ✅ const 项 + 块表达式
// sum::<{ 2 + 2 }>([0; 4])    ✅ 块表达式内常量运算
// let n = 3; sum::<n>(..)     ❌ 非 const 值不可（已预期诊断）
```

---

## 📌 七、稳定版限制清单

以下按所标上下文解释限制；诊断文本可能随编译器版本变化：

| # | 限制 | 预期诊断 |
|---|------|------|
| 1 | 参数类型仅整数 / `bool` / `char`，浮点、`&str`、自定义类型不可 | "`&'static str` is forbidden as the type of a const generic parameter" |
| 2 | 不能对参数做算术——`[u8; N + 1]` 不可用 | "generic parameters may not be used in const operations" |
| 3 | 函数泛型参数不允许默认值；struct 等允许默认参数的位置支持 const N: usize = 3 | 不可把函数上的报错推广到所有声明 |
| 4 | 关联常量可以计算 N；把依赖泛型的计算结果用于受限的类型位置仍需分别判断 | 表达式所在位置决定是否允许 |

**受限时的替代**: 返回值把派生长度作为普通字段/元组携带；用宏在编译期展开固定尺寸；需要类型级数字运算时考虑 `typenum` 式类型级编码（第三库方案）。

---

## 📌 八、运行期容量 vs 类型级容量

| | `Vec::with_capacity(n)` | `FixedBuf<N>`（常量泛型） |
|------|------|------|
| 容量确定时机 | 运行期 | 编译期 |
| 长度是否在类型中 | 否 | 是 |
| 溢出行为 | 自动扩容 | `push` 返回 `Result`（或编译期拒绝） |
| 代码实例 | 一份 | 每个 `N` 一份 |
| 适用 | 大小运行期才知道 | 尺寸固定且需要编译期保证 |

---

## 💡 可运行示例

### 示例一：长度进函数签名

```rust
fn sum<const N: usize>(values: [i32; N]) -> i32 {
    values.iter().sum()
}

fn main() {
    let a = [1, 2, 3];
    let b = [1, 2, 3, 4];
    println!("{}", sum(a)); // N 由实参推断为 3
    println!("{}", sum(b)); // N = 4：另一次单态化
    println!("{}", sum::<2>([9, 9])); // turbofish 显式指定
}
```

预期结果（输出 `6` `10` `18`）。

### 示例二：容量进类型的固定缓冲区

```rust
/// 容量进类型的固定缓冲区
struct FixedBuf<const N: usize> {
    data: [u8; N],
    len: usize,
}

impl<const N: usize> FixedBuf<N> {
    fn new() -> Self {
        Self { data: [0; N], len: 0 }
    }
    fn push(&mut self, b: u8) -> Result<(), &'static str> {
        if self.len == N {
            return Err("缓冲区已满");
        }
        self.data[self.len] = b;
        self.len += 1;
        Ok(())
    }
    fn as_slice(&self) -> &[u8] {
        &self.data[..self.len]
    }
}

fn main() {
    let mut buf: FixedBuf<4> = FixedBuf::new();
    for b in [1, 2, 3] {
        buf.push(b).unwrap();
    }
    buf.push(4).unwrap();
    assert!(buf.push(5).is_err()); // 第 5 个放不下
    println!("{:?}", buf.as_slice());
}
```

预期结果（输出 `[1, 2, 3, 4]`，第 5 个 `push` 为 `Err`）。

### 示例三：维度进类型的矩阵

```rust
#[derive(Debug)]
struct Matrix<const R: usize, const C: usize> {
    cells: [[f64; C]; R],
}

impl<const R: usize, const C: usize> Matrix<R, C> {
    fn rows(&self) -> usize {
        R
    }
    fn cols(&self) -> usize {
        C
    }
}

fn main() {
    let m: Matrix<2, 3> = Matrix {
        cells: [[1.0; 3]; 2],
    };
    println!("{}x{}: {:?}", m.rows(), m.cols(), m);

    // 长度属于类型：[i32; 2] 与 [i32; 3] 是不同类型
    let two: [i32; 2] = [0; 2];
    let three: [i32; 3] = [0; 3];
    let _ = (two, three);
}
```

预期结果（输出 `2x3: Matrix { cells: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0]] }`）。

### 示例四：const 项与块表达式作实参

```rust
const N: usize = 3;

fn sum<const M: usize>(values: [i32; M]) -> i32 {
    values.iter().sum()
}

fn main() {
    // 块表达式形式：const 上下文可求值的表达式可作 const 实参
    println!("{}", sum::<{ N }>([0; N]));
    println!("{}", sum::<{ 2 + 2 }>([0; 4]));
}
```

预期结果（输出 `0` `0`）。

## ⚠️ 编译失败演示

**以下两块为编译失败演示，列出预期结果，本轮未运行编译器**（rustc，edition 2024）。

**演示一**：长度是类型——`N` 不匹配即类型不匹配（`E0308`）。

```rust
fn first<const N: usize>(arr: [i32; N]) -> i32 {
    arr[0]
}

fn main() {
    let a: [i32; 3] = [7, 8, 9];
    println!("{}", first::<2>(a)); // 期望 [i32; 2]，实为 [i32; 3]
}
```

预期诊断：`error[E0308]: mismatched types`（期望 `[i32; 2]`，实为 `[i32; 3]`）。

**演示二**：稳定版限制——对参数做算术（`N + 1`）。

```rust
fn extend<const N: usize>(a: [u8; N]) -> [u8; N + 1] {
    let mut out = [0u8; N + 1];
    out[..N].copy_from_slice(&a);
    out
}

fn main() {
    println!("{:?}", extend([1, 2]));
}
```

预期诊断：`generic parameters may not be used in const operations`（第七节限制 #2）。

---

## ⚠️ 常见陷阱

- ❌ **用 `const N` 替代切片 API**——绝大多数集合处理用 `&[T]` 即可，`const N` 会强迫调用方绑定具体长度。
  - ✅ 只有"长度必须进类型"（缓冲区容量、矩阵维度、编译期保证）才用常量泛型。
- ❌ **把 nightly 的 `N + 1` 写法带进稳定版**（第七节限制 #2，预期诊断）。
  - ✅ 派生长度改由返回结构体字段/元组携带，或用宏展开。
- ❌ **混淆 `[T; N]` 与 `Vec<T>` 的 API 面**——两者都有 `iter`/`len`，但 `push` 只有 `Vec`。
  - ✅ 增长式数据用 `Vec`，固定容量用 `FixedBuf<N>` 式封装或数组。
- ❌ **`N` 取值集合很大还硬用常量泛型**——每个 `N` 一份单态化实例，二进制膨胀。
  - ✅ 运行期大小用 `Vec::with_capacity(n)` / 切片。
- ❌ **以为参数可以加 trait 约束或比较**（`where N > 0` 类写法稳定版不可用）。
  - ✅ 约束在运行期断言（`assert!(N > 0)`）或用类型级方案表达。

---

<!-- full-library-explanation -->
## 让维度成为类型，还是作为运行时数据

前置是泛型、数组与切片。const N 适合协议固定长度或矩阵维度：接收 [u8;16] 的函数可在编译时拒绝 [u8;8]。若输入长度来自文件或 HTTP 请求，编译期无法预知，应先用 Vec 或切片，在边界检查长度，再转换成固定数组。常量泛型不能让外部数据免于运行时验证。

限制必须区分出现的位置。函数体中计算 N+1 是允许的，关联常量也能引用 N；稳定版在泛型数组类型位置使用 [T; N+1] 则受限。结构体等允许默认泛型参数的位置可写 const N:usize=3，函数泛型参数不允许这样设置默认值。单次编译失败只证明该上下文失败，不能推广为“整个语言不支持默认值”。

练习：定义 struct Buffer<const N:usize=3>([u8;N])，分别构造默认长度和显式长度 4，解释为什么它们是不同类型。再写一个接收 &[u8] 的校验函数，运行时拒绝长度不足的输入。若不需要在类型层证明长度关系，优先切片接口可减少实例化数量，也更容易接收不同来源的数据。依据见 [Rust Reference 泛型参数](https://doc.rust-lang.org/reference/items/generics.html)。

## 🔗 相关条目

- 📄 **[trait 与泛型（入门教程）](../../basics/04-traits-generics.md)** — 泛型系统与单态化
- 📄 **[集合与迭代器（入门教程）](../../basics/06-collections-iterators.md)** — 切片优先的日常集合处理
- 📄 **[trait 对象与动态分发](./02-trait-objects.md)** — DST 对照：`[T; N]` 定长 vs `[T]` / `dyn Trait` 不定长
- 📄 **[所有权细则](./01-ownership-dictionary.md)** — `[T; N]` 的 Copy 判定
- 🌐 **[The Rust Reference: Constant Generic Parameters](https://doc.rust-lang.org/reference/items/generics.html#const-generic-parameters)** — 官方语法与限制

---

## 📝 要点回顾

1. **`const N` 把编译期值编码进类型**：`N` 不同的类型互不兼容，长度错误提前到编译期。
2. **稳定版参数仅整数 / `bool` / `char`**；`&str`、浮点、自定义类型均不可（实测）。
3. **按上下文核对限制**：泛型类型位置中的算术表达式与函数默认参数受限；函数体内运算、关联常量计算和结构体常量参数默认值不能一概禁止。
4. **切片优先**：数组 `&[T; N] → &[T]` 自动强转，常量泛型留给"长度进类型"的场景。
5. **每值一份单态化**：`N` 值集合大时警惕二进制膨胀。

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
