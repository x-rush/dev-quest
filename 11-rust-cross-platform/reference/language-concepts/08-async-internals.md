# Future·Pin·Waker

## 概述

`async/.await` 是语法糖，底层只有三个概念：**Future**（惰性的状态机）、**Pin**（"不再移动"的承诺）、**Waker**（类型擦除的唤醒句柄）。std 只定义接口，执行器（Tokio 等）负责调度——理解这三件套，`Box::pin`、`!Send` 报错、"为什么我的 Future 没跑"都有了答案。概念与 API 均属稳定层（基线 Rust 1.98.1 / edition 2024，见[模块 README](../../README.md)）。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#rust` `#reference` `#async` `#Future` `#Pin` `#Waker` |
| **更新日期** | `2026年9月` |

</details>

## 条目 1：Future trait 与 Poll 状态机

📌 **定义**: Future 是"**尚未完成的计算**"：`poll` 被执行器调用时推进到下一个挂起点——要么就绪（`Ready`），要么"稍后再问"（`Pending`）。签名（std 定义，示意）：

```rust
// std::future::Future（签名摘录，不能单独编译）
trait Future {
    type Output;
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}
enum Poll<T> { Ready(T), Pending }
```

**poll 契约**:
- 一次 poll 可以经过多个立即就绪的 await；返回 Pending 时要安排后续就绪通知（见条目 3）
- 返回 `Ready` 后**不得再 poll**——属逻辑错误，实现可以 panic，但不是 UB
- Future **惰性**：不 poll 就一行代码都不执行（`async fn f()` 调用后什么都不发生）

💡 **示例**（手写 Future + 手写执行器 + 手工 noop Waker，edition 2024 示例，本轮未运行）:

```rust
use std::future::Future;
use std::pin::Pin;
use std::ptr;
use std::task::{Context, Poll, RawWaker, RawWakerVTable, Waker};

// 手工构造 noop Waker（真实执行器会提供能唤醒调度器的 Waker）
fn noop_waker() -> Waker {
    unsafe fn noop_clone(p: *const ()) -> RawWaker {
        RawWaker::new(p, &VTABLE)
    }
    unsafe fn noop(_p: *const ()) {}
    static VTABLE: RawWakerVTable = RawWakerVTable::new(noop_clone, noop, noop, noop);
    unsafe { Waker::from_raw(RawWaker::new(ptr::null(), &VTABLE)) }
}

// 手写 Future：被 poll 三次后才就绪
struct PollCounter {
    remaining: u32,
}

impl Future for PollCounter {
    type Output = u32;
    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        if self.remaining == 0 {
            return Poll::Ready(self.remaining);
        }
        self.remaining -= 1; // Self: Unpin → Pin<&mut> 可直接解引拿 &mut
        cx.waker().wake_by_ref(); // 本例立即可继续推进，安排下一次 poll
        Poll::Pending
    }
}

// 极简执行器：真实运行时（如 Tokio）的核心就是这个循环 + 真正的 Waker/调度
fn block_on<F: Future>(fut: F) -> F::Output {
    let mut fut = Box::pin(fut); // Future 默认 !Unpin，poll 签名要求 Pin<&mut Self>
    let waker = noop_waker();
    let mut cx = Context::from_waker(&waker);
    loop {
        match fut.as_mut().poll(&mut cx) {
            Poll::Ready(v) => return v,
            Poll::Pending => std::thread::yield_now(), // 忙等示意
        }
    }
}

fn main() {
    let out = block_on(PollCounter { remaining: 3 });
    println!("输出 = {out}（期间 Pending 3 次）");
}
```

**关键点解析**:
- `block_on` 暴露了执行器的本质：**循环 poll + Pending 时挂起/让出 + wake 后重新入队**。
- `Pin<&mut Self>` 的 receiver 形态正是 `Pin` 存在的原因（条目 2）。

⚠️ **常见陷阱**: 手动 poll 忘记登记 waker 就返回 `Pending`——真实执行器下该 Future 可能**永远不被唤醒**（本例忙等循环侥幸掩盖了这一点）。

🔗 **相关条目**: [条目 2：Pin 与 !Unpin](#条目-2pin-与-unpin)、[条目 3：Waker 唤醒机制](#条目-3waker-唤醒机制)

## 条目 2：Pin 与 !Unpin

📌 **定义**: `Pin<P>` 是指针的包装，承诺**被指向的数据在 drop 之前不会移动**。需要它是因为编译器为 async 函数生成的状态机可能**自引用**（跨 `.await` 存活的局部变量，其借用被存进状态机字段）——移动即悬垂，且编译器无法在类型层面证明"没移动"，只能靠 `Pin` 类型化承诺。

📖 **Unpin 语义**: `Unpin` 是 auto trait，含义是"**被移动也无妨**"。常规类型（`i32`、`Vec`、`&T`……）几乎全部 `Unpin`——给它们套 `Pin` 毫无约束；`!Unpin` 的主体就是编译器生成的 async Future 与自引用结构。

**API 速查**:

| API | 作用 | 前提 |
|-----|------|------|
| `Box::pin(x)` | 堆上固定 → `Pin<Box<T>>` | 无（任意 T） |
| `pin!(x)` 宏 | 栈上固定 → `Pin<&mut T>` | 无 |
| `Pin::new(&mut x)` | 包一层 Pin | `x: Unpin` |
| `Pin::into_inner(p)` | 取回内部指针 P | `T: Unpin` |
| `Pin::get_ref()` | 得 `&T` | 无 |
| `Pin::get_unchecked_mut()` | 得 `&mut T` | unsafe（对 `!Unpin` 不得外泄此引用） |
| `Pin::set(new_value)` | 整体替换被固定值 | `P: DerefMut` |

**纪律**:
- 结构体含 `!Unpin` 字段时，`poll` 内访问字段要做**投影**（把 `Pin<&mut Self>` 拆成字段的 Pin）——手写繁琐，工程上用第三方 `pin-project` 宏
- 违反 Pin 契约（移动已固定数据）= UB（见 [unsafe Rust](./06-unsafe.md) 的 UB 清单）

⚠️ **常见陷阱**: `Unpin` 是"可以安全地从 Pin 里拿出来"，不是"可以移动"；`!Unpin` 类型也能正常 `let x = ...;` 绑定和移动——一旦进入需要固定的状态，就要在整个固定生命周期维持承诺，不只在 poll 调用期间。

🔗 **相关条目**: [条目 4：async fn 脱糖概览](#条目-4async-fn-脱糖概览)、[条目 5：为什么 Box::pin](#条目-5为什么-boxpin)

## 条目 3：Waker 唤醒机制

📌 **定义**: `Waker` 是**类型擦除的唤醒句柄**：Future 返回 `Pending` 前把执行器给的 waker 登记给事件源；事件就绪方调用 `wake()`，执行器把任务重新入队再 poll。轮询 + 唤醒的握手是异步运行时的全部接线。

📖 **方法表**:

| 方法 | 语义 |
|------|------|
| `wake()` | 消耗句柄，通知执行器"可以再 poll 了" |
| `wake_by_ref()` | 通知执行器但保留句柄，不要求内部必须克隆 |
| `will_wake(&other)` | true 保证唤醒同一任务，false 不保证不同；可用于优化 |
| `Waker::noop()` | 标准库占位 waker（测试/手工驱动用） |

底层是 `RawWaker` + `RawWakerVTable`（clone/wake/wake_by_ref/drop 四个函数指针）——示例块中的 `noop_waker` 即手工构造全过程。

**握手协议**（牢记三条）:
1. 每次 `Pending` 前都要登记当前 `cx.waker()`（新 poll 可能带来新 waker，覆盖旧值）
2. `wake` 后执行器可能 poll 若干次——Future 逻辑须对"多余 poll"幂等
3. waker 可以被克隆送到任意线程（`Send` 语义），事件源不需要知道执行器是谁

💡 **示例**（后台线程经 waker 唤醒主执行器，edition 2024 示例，本轮未运行）:

```rust
use std::future::Future;
use std::pin::Pin;
use std::sync::{Arc, Mutex};
use std::task::{Context, Poll, Wake, Waker};
use std::thread;
use std::time::Duration;

struct ThreadWake(thread::Thread);
impl Wake for ThreadWake {
    fn wake(self: Arc<Self>) { self.0.unpark(); }
    fn wake_by_ref(self: &Arc<Self>) { self.0.unpark(); }
}
fn block_on<F: Future>(future: F) -> F::Output {
    let waker = Waker::from(Arc::new(ThreadWake(thread::current())));
    let mut cx = Context::from_waker(&waker);
    let mut future = Box::pin(future);
    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return value,
            Poll::Pending => thread::park(),
        }
    }
}
struct State { done: bool, waker: Option<Waker> }
struct WaitFlag(Arc<Mutex<State>>);
impl Future for WaitFlag {
    type Output = ();
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        let mut state = self.0.lock().unwrap();
        if state.done { Poll::Ready(()) }
        else {
            state.waker = Some(cx.waker().clone());
            Poll::Pending
        }
    }
}
fn main() {
    let state = Arc::new(Mutex::new(State { done: false, waker: None }));
    let producer = Arc::clone(&state);
    let handle = thread::spawn(move || {
        thread::sleep(Duration::from_millis(30));
        let waker = {
            let mut state = producer.lock().unwrap();
            state.done = true;
            state.waker.take()
        };
        if let Some(waker) = waker { waker.wake(); }
    });
    block_on(WaitFlag(state));
    handle.join().unwrap();
    println!("被后台线程 wake 后完成");
}
```

**关键点解析**: 这是所有异步 IO 库的原型——"查状态；未就绪则登记 waker 并退出；事件源置状态 + `wake()`"。

⚠️ **常见陷阱**: 只在第一次 poll 登记 waker、之后忘了更新——执行器换 waker 后唤醒丢失，任务永久卡死；`wake()` 在事件方线程调用，不存在"必须回原线程"的假设。

🔗 **相关条目**: [条目 1：Future trait 与 Poll 状态机](#条目-1future-trait-与-poll-状态机)

## 条目 4：async fn 脱糖概览

📌 **定义**: `async fn`/`async` 块被编译器改写为**匿名状态机类型**，`.await` 是状态转移点。理解脱糖，就能解释惰性、`!Unpin`、`!Send` 与递归报错。

📖 **脱糖示意**（text 块，不可编译，仅示意）:

```text
async fn fetch(id: u64) -> Data          // 签名脱糖 →
fn fetch(id: u64) -> impl Future<Output = Data>

async {                                  // 体脱糖 → 匿名状态机枚举（示意）
    let a = step1(id).await;             //   enum FetchFut { Start, AtS1 { ... }, Done { ... } }
    let b = step2(a).await;              //   poll() 匹配当前变体：
    b                                    //     Start → poll step1，把 a 存入 AtS1 变体
}                                        //     AtS1  → poll step2，把 b 存入 Done
                                         // 跨 await 存活的局部变量 = 状态机的字段
                                         // → 若字段是对另一字段的借用，即自引用（Pin 存在的原因）
```

**推论速查**:

| 现象 | 脱糖解释 |
|------|---------|
| `async fn` 不调用不执行 | 返回的 Future 惰性，poll 才驱动 |
| async Future 默认 `!Unpin` | 状态机可能自引用，需要 Pin 承诺 |
| 非Send 局部变量（如 `std::sync::MutexGuard`）跨 await → Future `!Send` | 该变量成了状态机字段，随状态机一起"跨线程" |
| 状态机大小取决于需要跨挂起点保存的数据、判别信息和布局优化 | `.await` 两边的变量生命周期都算进字段 |
| 构造 async 状态机本身不必堆分配 | 状态机是普通值，`Box::pin` 后才上堆 |

⚠️ **常见陷阱**: 在 `.await` 之后还要用的值，其生命周期横跨挂起点——把"不需要跨 await 的值"放进更小的 `{}` 块，状态机更小、`Send` 判定更容易通过。

🔗 **相关条目**: [条目 2：Pin 与 !Unpin](#条目-2pin-与-unpin)、[条目 5：为什么 Box::pin](#条目-5为什么-boxpin)

## 条目 5：为什么 Box::pin

📌 **定义**: `Box::pin(x)` 把任意 Future 固定到堆上（Pin<Box<T>>；可移动指针包装本身，但不会自动延长 T 中借用的生命周期），一次解决执行器与类型系统的三个约束。

📖 **三个理由**:

1. **执行器需要 `Pin<&mut Self>` 才能 poll**：`!Unpin` 的 Future 必须先固定——栈固定用 `pin!` 宏（作用域内），跨作用域/跨线程用 `Box::pin` 更通用
2. **递归 async fn 无限大小**：递归调用点不 Box 会报 E0733（"recursion in an `async fn` requires boxing"）——`Box::pin(递归调用)` 用堆间接层打断类型自包含（下例）
3. **spawn 需要 `'static`**：运行时的 `spawn(fut)` 要求 Future 拥有其全部数据（任务活得比调用栈久），装箱不会获得 static；需让 Future 的数据本身满足要求，例如移入拥有的值，或使用允许较短生命周期的执行方式

💡 **示例**（递归 async fn，edition 2024 示例，本轮未运行）:

```rust
use std::future::Future;
use std::pin::Pin;
use std::ptr;
use std::task::{Context, Poll, RawWaker, RawWakerVTable, Waker};

fn noop_waker() -> Waker {
    unsafe fn noop_clone(p: *const ()) -> RawWaker {
        RawWaker::new(p, &VTABLE)
    }
    unsafe fn noop(_p: *const ()) {}
    static VTABLE: RawWakerVTable = RawWakerVTable::new(noop_clone, noop, noop, noop);
    unsafe { Waker::from_raw(RawWaker::new(ptr::null(), &VTABLE)) }
}

fn block_on<F: Future>(fut: F) -> F::Output {
    let mut fut = Box::pin(fut);
    let waker = noop_waker();
    let mut cx = Context::from_waker(&waker);
    loop {
        match fut.as_mut().poll(&mut cx) {
            Poll::Ready(v) => return v,
            Poll::Pending => std::thread::yield_now(),
        }
    }
}

// 递归 async fn：递归点必须 Box::pin 打断无限大小的类型（否则 E0733）
async fn countdown(n: u32) -> u32 {
    if n == 0 {
        0
    } else {
        let inner = Box::pin(countdown(n - 1));
        1 + inner.await
    }
}

fn main() {
    let depth = block_on(countdown(100));
    println!("递归深度 = {depth}");
}
```

**关键点解析**: 只需在**递归点** `Box::pin`——外层是否再装箱由执行器决定（示例的 `block_on` 内部已 Box）。每个 `Box::pin` 是一次堆分配：递归深度 = 分配次数。

⚠️ **常见陷阱**: `Pin<Box<T>>` 自动 `Unpin`，于是可以对它 `&mut`——但被指的 T 仍不得移动，"Box 了就随便动"是误读；能 `pin!` 栈固定的就不必 `Box::pin`（省一次分配）。

🔗 **相关条目**: [条目 4：async fn 脱糖概览](#条目-4async-fn-脱糖概览)、[智能指针全表](./07-smart-pointers.md)（Box 的异步延伸）

## 相关文档

- 📄 **[并发与异步教程](../../basics/09-concurrency-async.md)** — Tokio 使用层面的按序入门
- 📄 **[智能指针全表](./07-smart-pointers.md)** — `Box::pin`、`Arc<Mutex<T>>` 与异步共享状态
- 📄 **[unsafe Rust](./06-unsafe.md)** — 违反 Pin 契约为何是 UB
- 📄 **[所有权字典](./01-ownership-dictionary.md)** — 自引用与所有权的根源规则

---

**文档版本**: v2.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team


<!-- full-library-explanation -->
## 把“等待发生”与“任务被安排再次运行”连起来

前置是 Future、线程同步与所有权。Pending 不是让执行器不断来问的指令；Future 需要安排就绪通知，让任务有理由再次进入运行队列。检查状态与登记 waker 必须避免竞争窗口：若事件在“检查未就绪”之后、“登记 waker”之前完成，通知可能丢失。本页 WaitFlag 用同一把锁保护状态和 waker，生产方更新后取出 waker，再在锁外唤醒。

pinning 与生命周期是两条约束。Box::pin 让被指对象具有稳定位置，不会把它借用的局部字符串变成 static。async move 可以把拥有的数据移入 Future，但若移动的是一个短期引用，引用的寿命仍没有增长。Tokio spawn 等 API 对 Send/static 的要求应分别检查，不能通过多包一层 Box 自动满足。

练习：让事件在首次 poll 前完成，Future 应立即 Ready；让事件在 Pending 后完成，线程应被 unpark 唤醒；多次无关唤醒只会重新检查条件，不应导致提前成功。再将拥有的 String 与 &String 分别移入异步块，比较能否满足需要 static 的函数签名。这里的单任务执行器用于说明通知机制，不提供生产运行时的 IO 驱动、任务公平性和关闭管理。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
