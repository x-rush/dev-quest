# 智能指针全表

## 概述

智能指针是**实现 `Deref`（透明访问内部值）与 `Drop`（确定性释放）的封装结构体**，在栈指针之外携带元数据（引用计数、锁、能力标记）。Rust 的选择逻辑：先问**所有权独占还是共享**，再问**要不要内部可变性**，最后问**单线程还是多线程**。本篇给出 std 全量对比与各类型速查。基线 Rust 1.98.1 / edition 2024（见[模块 README](../../README.md)）。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#rust` `#reference` `#智能指针` `#Rc-Arc` `#内部可变性` |
| **更新日期** | `2026年9月` |

## 条目 1：全量对比总表

📌 **定义**: 九个核心智能指针按"所有权 × 线程安全 × 内部可变性 × 开销"定位。

📖 **总表**:

| 类型 | 所有权语义 | 线程安全 | 内部可变性 | 开销 | 典型场景 |
|------|-----------|---------|-----------|------|---------|
| `Box<T>` | 独占，堆上单值 | 随 `T` | 无 | 一次指针解引，无计数 | 递归类型、大值、`dyn Trait` |
| `Rc<T>` | 共享（克隆只加计数） | ✗ 非原子计数 | 无 | 非原子计数增减 | 单线程共享只读数据 |
| `Arc<T>` | 共享 | ✓ 原子计数 | 无 | 原子计数（跨核同步成本） | 多线程共享只读数据 |
| `Cell<T>` | 独占 | `!Sync` | ✓ 仅 `Copy` 类型（get/set 整值替换） | 无锁，极低 | `Copy` 类型内部可变 |
| `RefCell<T>` | 独占 | `!Sync` | ✓ 任意 `T`（运行时借用规则） | 运行时借用计数 | 单线程共享可变 |
| `Mutex<T>` | 独占 | ✓（`T: Send`） | ✓ 阻塞式互斥 | 系统锁（futex 级） | 多线程互斥写 |
| `RwLock<T>` | 独占 | ✓（`T: Send`） | ✓ 多读单写 | 读写锁，常态高于 Mutex | 读多写少 |
| `Cow<'a, B>` | 借用**或**拥有（枚举） | 随 `B` | 无（写时整体克隆） | 一个枚举判别 + 分支 | 读多写少、免拷贝 API |
| `Weak<T>` | 不拥有（观察者） | 随 Rc/Arc | 无 | 计数的 weak 侧 | 破环、缓存 |

**组合速查**（单指针不够用时的惯用组合）:

| 组合 | 一句话定位 |
|------|-----------|
| `Rc<RefCell<T>>` | 单线程"共享 + 可变" |
| `Arc<Mutex<T>>` | 多线程"共享 + 可变"（互斥） |
| `Arc<RwLock<T>>` | 多线程读多写少 |
| `Box<dyn Trait>` | 异质集合 / 运行时分发 |
| `Arc<AtomicU64>` | 无锁共享计数器 |
| `Weak<Node>` | 树/图的父指针等回边 |

⚠️ **常见陷阱**: `Rc`/`Arc` 共享的是**只读访问**——"共享 + 改"必须叠内部可变性（RefCell/Mutex）；两层 `Deref` 解引（`&**rc`）源于先解 `Rc` 再解内部值。

🔗 **相关条目**: [条目 2：Box](#条目-2box)、[条目 3：Rc 与 Weak](#条目-3rc-与-weak-循环引用-breaking)

## 条目 2：Box

📌 **定义**: 最朴素的智能指针：把值放到堆上，栈上留一个指针。独占所有权，无计数、无锁，`*b` 一次解引。

📖 **语法/签名**: `Box::new(value)`；递归类型用 `Box<Next>` 提供间接层；`Box<dyn Trait>` 是 trait 对象载体（动态分发）。

💡 **示例**（本块经 rustc edition 2024 实测通过）:

```rust
// Box 突破递归类型的无限大小：直接内嵌 List 会报 E0072
enum List {
    Cons(i32, Box<List>),
    Nil,
}

use List::{Cons, Nil};

fn main() {
    let list = Cons(1, Box::new(Cons(2, Box::new(Cons(3, Box::new(Nil))))));

    let mut sum = 0;
    let mut cur: &List = &list;
    while let Cons(v, next) = cur {
        sum += v;
        cur = &**next; // &Box<List> 两层解引得到 &List
    }
    println!("sum = {sum}");

    // Box 的另一主场景：trait 对象（动态分发）
    let shapes: Vec<Box<dyn std::fmt::Debug>> = vec![Box::new(1), Box::new("a")];
    println!("{:?}", shapes);
}
```

**关键点解析**:
- 递归类型必须经 `Box`（或引用/`Rc`）打断"类型大小含自身"的无限递归，否则 E0072。
- `Box::leak` 可把 `Box<T>` 转成 `&'static mut T`（进程级泄漏换取静态生命周期，慎用）。

⚠️ **常见陷阱**: "值太大所以 Box"多数是过早优化——大数组直接放 `Box<[u8; 10000]>` 有意义，几十字节的 struct 没有；`Box<dyn Trait>` 有虚表分发成本，热路径泛型（静态分发）优先。

🔗 **相关条目**: [条目 1：全量对比总表](#条目-1全量对比总表)

## 条目 3：Rc 与 Weak（循环引用 breaking）

📌 **定义**: `Rc<T>`（引用计数）实现单线程共享所有权：`Rc::clone` 只把计数 +1（O(1)，不拷贝数据），最后一个所有者离开时释放。`Weak<T>` 是**不拥有所有权**的伴生指针（`Rc::downgrade` 产生，`upgrade()` 取回 `Option<Rc<T>>`），用于打破 `Rc` 环——环上的强引用互相持有即内存泄漏（编译器不报错），把"回边"（父指针/反向引用）换成 `Weak` 即断环。

📖 **计数规则**: `strong_count` = 拥有者数量（归零才释放）；`weak_count` = 观察者数量（不影响释放，仅保活控制块）。

💡 **示例**（本块经 rustc edition 2024 实测通过）:

```rust
use std::cell::RefCell;
use std::rc::{Rc, Weak};

#[derive(Debug)]
struct Node {
    value: i32,
    parent: RefCell<Weak<Node>>,      // 父用 Weak：不拥有，破环
    children: RefCell<Vec<Rc<Node>>>, // 子用 Rc：拥有
}

fn main() {
    let leaf = Rc::new(Node {
        value: 3,
        parent: RefCell::new(Weak::new()),
        children: RefCell::new(vec![]),
    });
    let branch = Rc::new(Node {
        value: 5,
        parent: RefCell::new(Weak::new()),
        children: RefCell::new(vec![Rc::clone(&leaf)]),
    });
    *leaf.parent.borrow_mut() = Rc::downgrade(&branch);

    println!(
        "leaf strong={} weak={}",
        Rc::strong_count(&leaf),
        Rc::weak_count(&leaf)
    );
    println!(
        "branch strong={} weak={}",
        Rc::strong_count(&branch),
        Rc::weak_count(&branch)
    );

    // Weak 不能直接解引，须 upgrade 成 Option<Rc<T>>
    if let Some(p) = leaf.parent.borrow().upgrade() {
        println!("leaf 的父节点 value = {}", p.value);
    }

    drop(branch);
    println!("drop 后 upgrade 为 None: {}", leaf.parent.borrow().upgrade().is_none());
}
```

**关键点解析**:
- 输出 `leaf strong=2`（`main` 绑定 + `branch.children` 各 1）、`branch weak=1`（`leaf.parent`）——父引用不产生强计数，环不成。
- `drop(branch)` 后强计数归零，节点释放，`upgrade()` 返回 `None`——Weak 恰好暴露"目标可能已死"。
- 若 `parent` 用 `Rc<Node>`，`leaf ↔ branch` 强计数互锁，两者永不释放。

⚠️ **常见陷阱**: `Weak::upgrade` 每次调用都要判 `None`（目标可能随时消失）；`Arc` 同样会成环，破环手法相同（`Arc::downgrade`）；`Rc` 绝不能跨线程（`!Send !Sync`，编译器会拦）。

🔗 **相关条目**: [条目 4：RefCell 与内部可变性](#条目-4refcell-与内部可变性)、[条目 6：Arc + Mutex/RwLock](#条目-6arc--mutexrwlock)

## 条目 4：RefCell 与内部可变性

📌 **定义**: **内部可变性** = 通过共享引用（`&T`）修改内部值。`RefCell<T>` 把"独占 vs 共享"的借用检查从编译期**搬到运行时**：维持借用计数器，违反规则立即 panic。是 `Rc<RefCell<T>>` 组合的另一半。

📖 **运行时借用规则**:

| 已有借用 | 再请求 | 结果 |
|---------|--------|------|
| 共享 | 共享 | ✓ 多个共存 |
| 共享 | 可变 | ✗ panic（`BorrowMutError`："already borrowed"） |
| 可变 | 共享 / 可变 | ✗ panic（`BorrowError`："already mutably borrowed"） |

`try_borrow()` / `try_borrow_mut()` 返回 `Result`，不 panic；守卫 `Ref`/`RefMut` drop 时释放借用（RAII）。

💡 **示例**（与条目 5 共用一块，经 rustc edition 2024 实测通过）:

```rust
use std::borrow::Cow;
use std::cell::RefCell;

fn main() {
    // RefCell：把"独占 vs 共享"检查从编译期搬到运行时
    let cell = RefCell::new(vec![1, 2, 3]);

    {
        let mut w = cell.borrow_mut(); // 运行时申请可变借用
        w.push(4);
    } // RefMut drop → 借用释放

    let r1 = cell.borrow();
    let r2 = cell.borrow(); // 多个共享借用共存 OK
    println!("r1[0]={} r2[2]={} len={}", r1[0], r2[2], cell.borrow().len());

    // Cow：读多写少场景，"需要修改才克隆"
    fn normalize(s: &str) -> Cow<'_, str> {
        if s.contains(' ') {
            Cow::Owned(s.replace(' ', "_")) // 有修改需求 → 拷贝
        } else {
            Cow::Borrowed(s) // 无修改 → 零拷贝借用
        }
    }
    println!("{} / {}", normalize("hello world"), normalize("hello"));
}
```

**关键点解析**:
- 借用守卫的作用域就是锁的作用域：把 `borrow_mut()` 压进最小块，共享借用随 `Ref` 存活。
- `Cell<T>` 是 `RefCell` 的 `Copy` 特化版：`get()` 拷出、`set()` 整值替换，无 panic 可能。

⚠️ **常见陷阱**: 借用守卫存活期间再 `borrow_mut()` 是运行时 panic——尤其中间夹着一个看似无害的 `borrow()`（守卫还活着）；`RefCell` 让"编译期发现"退化为"运行期发现"，仅在没有更好的类型方案时使用。

🔗 **相关条目**: [条目 3：Rc 与 Weak](#条目-3rc-与-weak-循环引用-breaking)、[条目 6：Arc + Mutex/RwLock](#条目-6arc--mutexrwlock)

## 条目 5：Cow（写时克隆）

📌 **定义**: `Cow<'a, B>`（Clone on Write）是枚举：`Borrowed(&'a B)` 或 `Owned(B::Owned)`。读路径零拷贝透传借用；只有真正要修改时（`to_mut()` 或构造 `Owned`）才克隆。Deref 到 `B::Owned`，调用方几乎无感。

📖 **语法/签名**: `enum Cow<'a, B: ToOwned + ?Sized>`；关键方法 `to_mut()`（Borrowed 分支触发克隆并转 Owned）、`into_owned()`（取得拥有值，按需克隆）；常见 `B`：`str`、`[T]`、`Path`。

💡 **示例**: 见条目 4 代码块的 `normalize`——含空格走 `Owned`（拷贝改写），不含走 `Borrowed`（纯借用）。

**适用判定**:
- 函数多数输入**不改**、少数要改 → 返回 `Cow`，把克隆决定权留给数据本身
- 配置/词法分析等"模式匹配后偶尔改写"的管线是高发区

⚠️ **常见陷阱**: `Cow` 不是延迟拷贝缓存——每次 `to_mut()` 都可能克隆；对 `Borrowed` 调 `to_mut()` 会**复制整个值**（意外大拷贝）；不需要"有时不改"就别上 `Cow`，直接 `String`/`&str` 更直白。

🔗 **相关条目**: [条目 1：全量对比总表](#条目-1全量对比总表)

## 条目 6：Arc + Mutex/RwLock

📌 **定义**: 多线程共享可变 = **共享（Arc）× 互斥（Mutex/RwLock）** 的乘法。`Arc` 解决"所有权"，锁解决"可变性"；锁守卫（`MutexGuard`/`RwLockReadGuard`/`RwLockWriteGuard`）是 RAII：离开作用域自动解锁。`lock()`/`read()`/`write()` 返回 `Result`——锁被**毒化**（持锁线程 panic）后返回 `Err`，`.unwrap()` 是常见处理，也可 `into_inner()` 带病取值。

📖 **语法/签名**: `Arc::clone(&arc)`（别 `.clone()` 顺手拷错对象）、`lock().unwrap()` 得 `MutexGuard`、`read().unwrap()` 可并发多份、`write().unwrap()` 独占。

💡 **示例**（本块经 rustc edition 2024 实测通过）:

```rust
use std::sync::{Arc, Mutex, RwLock};
use std::thread;

fn main() {
    // Arc<Mutex<T>>：多线程共享可变的标准组合
    let counter = Arc::new(Mutex::new(0u64));
    let handles: Vec<_> = (0..4)
        .map(|_| {
            let c = Arc::clone(&counter);
            thread::spawn(move || {
                for _ in 0..1000 {
                    *c.lock().unwrap() += 1; // lock 返回 Result：处理锁毒化
                }
            })
        })
        .collect();
    for h in handles {
        h.join().unwrap();
    }
    println!("counter = {}", *counter.lock().unwrap()); // 4000

    // RwLock：多读单写
    let state = Arc::new(RwLock::new(vec![1, 2, 3]));
    let r1 = state.read().unwrap();
    let r2 = state.read().unwrap(); // 并发读 OK
    println!("{} {}", r1.len(), r2[2]);
    drop((r1, r2)); // 显式释放读锁后再取写锁
    state.write().unwrap().push(4);
    println!("{:?}", *state.read().unwrap());
}
```

**关键点解析**:
- `Mutex` 只保证互斥，不保证"不会忘记加锁"——但漏加锁时 `&T` 访问会编译失败，安全网仍在类型系统。
- `RwLock` 读锁可并发多份；同一作用域先读后写须先 `drop` 读守卫（示例的 `drop((r1, r2))`）。
- 共享计数这类原子量直接 `Arc<AtomicU64>`，免锁（见组合速查表）。

⚠️ **常见陷阱**: `std::sync::MutexGuard` 是 `!Send`——**跨 `.await` 持锁**会让整个 Future 变 `!Send`，在 Tokio 多线程调度下编译失败（异步场景换 `tokio::sync::Mutex`，见 [Future·Pin·Waker](./08-async-internals.md)）；嵌套锁两把 `Mutex` 顺序不一致即死锁，全工程固定加锁顺序。

🔗 **相关条目**: [条目 3：Rc 与 Weak](#条目-3rc-与-weak-循环引用-breaking)、[并发与异步教程](../../basics/09-concurrency-async.md)

## 条目 7：陷阱速查

📌 **定义**: 智能指针高频事故一览（自上而下按出现频率）。

📖 **清单**:

| 事故 | 症状 | 对策 |
|------|------|------|
| `Rc`/`Arc` 循环引用 | 内存泄漏，无任何报错 | 回边一律 `Weak`，析构路径画图核对 |
| RefCell 双重可变借用 | 运行时 panic "already mutably borrowed" | 借用守卫压最小作用域；能编译期解决就别运行时 |
| RwLock 先读后写 | 死锁 | `drop` 读守卫再取写锁 |
| 锁毒化连锁 | `unwrap` 层层炸 | 锁内不 panic / `into_inner` 恢复策略 |
| 跨 `.await` 持 std 锁 | Future `!Send`，spawn 编译失败 | 换异步运行时的锁或缩小临界区到 await 之前 |
| `Arc::clone` 写成 `T::clone` | 拷贝了内部值 | 显式 `Arc::clone(&a)`，cargo clippy 可提示 |
| `Weak` 忘判 `None` | panic on unwrap | `upgrade()` 后必须处理已释放情形 |

⚠️ **常见陷阱**: 泄漏（循环引用）**不是 UB**、也不会崩——内存曲线缓慢上涨，只能靠代码评审与弱引用纪律预防。

## 相关文档

- 📄 **[所有权字典](./01-ownership-dictionary.md)** — 所有权/借用规则的单一事实来源
- 📄 **[unsafe Rust](./06-unsafe.md)** — Box/Vec 等封装背后的 unsafe 机制
- 📄 **[Future·Pin·Waker](./08-async-internals.md)** — `Box::pin` 与异步共享状态
- 📄 **[智能指针教程](../../basics/08-smart-pointers.md)** — 按序学习的入门讲解

---

**文档版本**: v2.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team
