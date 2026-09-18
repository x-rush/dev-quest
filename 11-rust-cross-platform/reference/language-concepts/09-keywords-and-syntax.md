# Rust 关键词与语法入口

前置知识：能理解变量、函数、条件和循环。本页以 edition 2024 的常用稳定语法为学习口径；关键词分类核对 [Rust Reference](https://doc.rust-lang.org/reference/keywords.html)。保留词不等于已经可以使用的功能。

## 一个完整的语言层实验

执行 `cargo new keyword-lab`，把以下代码保存到 `keyword-lab/src/main.rs`，进入目录执行 `cargo run`。无需第三方依赖。预期输出 `2` 和 `true`，各占一行；本轮未在本机 Rust 工具链执行。

```rust
#[derive(Debug)]
struct Task {
    done: bool,
}

fn count_done(tasks: &[Task]) -> usize {
    let mut count = 0;
    for task in tasks {
        if task.done {
            count += 1;
        }
    }
    count
}

fn main() {
    let mut tasks = vec![Task { done: false }, Task { done: true }];
    tasks[0].done = true;
    let count = count_done(&tasks);
    println!("{count}");
    match tasks.first() {
        Some(task) => println!("{}", task.done),
        None => println!("empty"),
    }
}
```

`struct` 定义一种数据，`fn` 定义操作，`let mut` 允许更新，`&tasks` 借出访问权。`Some/None` 是 Option 的变体，`usize/bool` 是类型，`vec!/println!` 是宏；它们都不该被混称为“关键词”。删掉 tasks 的 mut 会使写入编译失败；删掉 count 的 mut 会使累加编译失败。`#[derive(Debug)]` 是属性形式，它让编译器生成指定 trait 的实现，不是函数调用。

## 绑定、类型与抽象

| 名称 | 读法与用途 | 容易混淆的边界 |
|---|---|---|
| `let` / `mut` | 创建绑定；允许绑定或借用可变 | 新的同名 let 是遮蔽，不等于修改旧绑定 |
| `const` | 编译期可求值的常量项；也用于 const fn/泛型 | const 与运行时可变绑定不同 |
| `static` | 具有静态存储期的项 | 与 `'static` 生命周期语境不同；可变全局数据另有安全要求 |
| `fn` / `return` | 定义函数；提前返回 | 函数末尾无分号的表达式也可产生返回值 |
| `struct` / `enum` | 定义结构体 / 互斥变体数据 | enum 可为各变体携带不同数据，不只是整数标签 |
| `type` | 类型别名或关联类型 | 别名不会自动创建一个语义独立的新类型 |
| `trait` / `impl` | 声明能力约定 / 实现类型方法或 trait | trait 约束描述能力，不意味着继承数据字段 |
| `Self` / `self` | 当前实现的类型 / 方法接收者或当前模块路径 | `&self` 借用，`self` 通常取得所有权 |
| `where` | 写泛型约束 | 让复杂约束移出泛型参数列表，不改变其含义 |
| `dyn` | trait 对象的动态分发 | 只有满足相应兼容要求的 trait 可这样使用 |
| `as` | 类型转换或导入重命名 | 整数转换可能截断，不能默认等价于有检查的 TryFrom |

先通过[变量与可变性](https://doc.rust-lang.org/book/ch03-01-variables-and-mutability.html)理解绑定，再看[所有权参考](01-ownership-dictionary.md)。不要从“值在栈还是堆上”猜测 Copy/Clone 的所有语义。

## 控制流、模式与所有权

| 名称 | 作用 | 对照 |
|---|---|---|
| `if` / `else` | 条件表达式 | 两个分支产生的值要有兼容类型；条件须是 bool |
| `match` | 按模式穷尽分支 | 漏掉可能情况会被检查；可用 `_` 接住未关心的模式 |
| `for` / `in` | 从可迭代值依次取项 | `for x in values` 和 `for x in &values` 对所有权不同 |
| `loop` | 无条件循环 | 可用 `break value` 产生结果 |
| `while` | 条件循环 | 条件在每次迭代前检查 |
| `break` / `continue` | 结束循环 / 开始下一次迭代 | 可配合循环标签，避免把内外层混淆 |
| `ref` | 在模式里绑定引用 | 与表达式中的 `&value` 所处位置不同 |
| `move` | 闭包等按值捕获 | 不自动让捕获类型变成 Send，也不自动创建线程 |
| `true` / `false` | 布尔值 | 数字 0 不能隐式当 false |
| `_` | 忽略模式或类型推断占位等 | `_` 与命名为 `_value` 的绑定不同，后者仍可保留值 |

## 模块、异步与不安全边界

`mod` 声明模块；`use` 把路径引入作用域；`pub` 控制可见性；`crate` 指本 crate 或可见性范围；`super` 指上级模块。把代码放进另一个文件不意味着自动公开 API。

`async` 产生异步计算，`.await` 等待可等待值；标准库定义 Future，但异步 I/O 应用通常还需要运行时。`unsafe` 表示必须额外证明特定操作的安全条件，不会关闭所有类型或借用检查；`extern` 用于外部 ABI/链接等语境，须结合 [unsafe 参考](06-unsafe.md)学习。

## 保留词和语境词完整入口

edition 2024 需要识别的保留词有 `abstract`、`become`、`box`、`do`、`final`、`gen`、`macro`、`override`、`priv`、`try`、`typeof`、`unsized`、`virtual`、`yield`。不要把未来预留的 `gen` 当成已经可用于稳定生成器教程的语法。

语境相关的名称包括 `'static`、`macro_rules`、`raw`、`safe`、`union`。例如 `macro_rules!` 定义声明式宏；`raw` 出现在原始借用语法；`safe` 在外部块的特定声明中有意义。旧 edition 对 async/await/dyn、try、gen 的规则不同，迁移应核对 Cargo.toml 的 edition。使用 raw identifier 如 `r#type` 可以处理部分名称冲突，但不是所有特殊路径关键词都可这样转义。

## 自测

1. 把开头数组改为空，为什么 count_done 返回 0，而 first 返回 None？
2. 若函数改为接收 `Vec<Task>`，调用之后是否还能继续用原 tasks？解释移动与借用的差别。
3. 把末尾 `count` 改为 `count;`，观察返回类型错误，解释分号如何改变表达式结果。

先完成这些边界，再查[标准类型与常用方法](10-standard-types-and-methods.md)。返回[模块导读](../../LEARNING_GUIDE.md)。
