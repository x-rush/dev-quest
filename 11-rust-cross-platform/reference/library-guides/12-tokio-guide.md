# Tokio - 异步运行时全量速查

> **文档简介**: Tokio 1.53 异步运行时的 API 速查字典——runtime 构建、任务调度、四类同步原语、`select!`、定时器、异步 IO trait 与 stream 适配，一页查全。
>
> **目标读者**: 已掌握 Rust 所有权与 async/await 语法、需要写异步服务或 Tauri/Axum 应用的中级开发者。
>
> **前置知识**: [basics/09-concurrency-async](../../basics/09-concurrency-async.md)、[async 内核（Future/Pin/Waker）](../language-concepts/08-async-internals.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 字典（全量参考，单一事实来源） |
| **难度** | ⭐⭐ 进阶 |
| **标签** | `#rust` `#tokio` `#async` `#reference` |
| **更新日期** | `2026年9月` |

</details>

**版本基线**: Tokio **1.53**（核实日期 2026-09-16，单一事实来源见[模块 README 技术基线](../../README.md)）。Stream trait 属独立 crate `tokio-stream`（版本未列入基线，不在此标注）。

## 🎯 学习目标

- ✅ 用 Builder 与 `#[tokio::main]` 两种 flavor 正确搭建/进入 runtime
- ✅ 按"容量即背压"原则在 mpsc/oneshot/watch/broadcast 中选对通道
- ✅ 用 `select!` 组合多路异步事件，理解 biased/if 守卫/else 与取消安全
- ✅ 速查 AsyncRead/AsyncWrite 扩展 trait 与 tokio-stream 适配器

## 📋 目录

- [Runtime：创建与进入](#️-runtime创建与进入)
- [任务 spawn 与 JoinHandle](#-任务-spawn-与-joinhandle)
- [同步原语四兄弟](#-同步原语四兄弟)
- [select! 宏](#-select-宏)
- [time 定时器](#️-time-定时器)
- [IO trait](#-io-trait异步读写)
- [stream 适配](#-stream-适配tokio-stream)
- [最佳实践与陷阱](#-最佳实践与陷阱)

---

## 🔍 核心概念：Tokio 在异步栈中的位置

调用 `async fn` 得到状态机（[Future](../language-concepts/08-async-internals.md)），函数体由后续 poll 驱动。Tokio 提供 I/O 与时间驱动、任务调度和异步资源 API。`tokio::spawn`、计时器等需要运行时上下文；创建通道、oneshot 同步发送等操作不要求运行时。current-thread 调度器和多线程调度器也不是同一种执行方式。

下文标记为“完整程序”的围栏可分别存为 `src/main.rs`，其余围栏是有上下文前提的 API 片段。验证使用 Rust edition 2024，精确依赖与锁文件见[本批验证报告](../../../shared-resources/tools/document-quality/reports/rust-ecosystem-validation.md)。学习时先创建 `cargo new tokio-reference`，再配置：

```toml
[dependencies]
tokio = { version = "=1.53.0", features = ["rt-multi-thread", "macros", "sync", "time", "io-util", "test-util"] }
tokio-stream = { version = "=0.1.17", features = ["sync"] }
```

`test-util` 只为下面的虚拟时间验收；服务应用应按自己实际使用的能力配置 features。

## 🛠️ Runtime：创建与进入

### 三种进入方式

| 方式 | 写法 | 适用场景 |
|------|------|---------|
| 宏（默认多线程） | `#[tokio::main]` | 应用 main 函数 |
| 宏（单线程） | `#[tokio::main(flavor = "current_thread")]` | 轻量工具、嵌入、测试 |
| 宏（多线程+调参） | `#[tokio::main(flavor = "multi_thread", worker_threads = 2)]` | 需控制 worker 数 |
| 手动 Builder | `Builder::new_multi_thread()...build()?.block_on(fut)` | 库内嵌 runtime、多 runtime、非 main 入口 |

### Builder 速查

```rust
let rt = tokio::runtime::Builder::new_multi_thread()
    .worker_threads(4)          // worker 线程数（默认 = CPU 核数）
    .max_blocking_threads(512)  // spawn_blocking 阻塞线程池上限
    .thread_name("worker")      // 线程名前缀
    .thread_stack_size(2 * 1024 * 1024)
    .enable_all()               // 启用 IO + time（手动 build 必须，否则对应 API panic）
    .build()?;
rt.block_on(async { /* ... */ });
```

- `new_current_thread()`：单线程调度器；所有任务跑在 `block_on` 调用线程上。
- `enable_io()` / `enable_time()` / `enable_all()`：手动 build 时**必须**开启对应资源，否则 `tokio::time::sleep` 等会 panic（宏入口已默认全开）。
- `Runtime::new()`：等价 `new_multi_thread().enable_all().build()` 的捷径。

### 陷阱：不能嵌套进入 runtime

```
// panic: Cannot start a runtime from within a runtime.
// This happens because a function (like `block_on`) attempted to
// block the current thread while the thread is being used to drive asynchronous tasks.
```

`#[tokio::main]` 已在 runtime 内，main 里再 `Builder::build().block_on()` 会 panic。已进入 runtime 后想跑异步代码用 `.await` 或 `tokio::spawn`。

## 🧵 任务 spawn 与 JoinHandle

### API 速查

| API | 签名要点 | 说明 |
|------|---------|------|
| `tokio::spawn` | 输入 `Future + Send + 'static`，输出也需 `Send + 'static` | 调度到 runtime；必须在 runtime 上下文内调用。`'static` 表示不借用短命外部数据，不表示任务永久运行 |
| `JoinHandle::await` | `Result<T, JoinError>` | 任务 panic 或被 abort 时为 `Err` |
| `JoinHandle::abort()` | 请求取消任务 | 已完成的任务可能仍返回 `Ok`；已启动的 `spawn_blocking` 无法借此停止。等待 handle 才能观察最终结果 |
| `JoinHandle::is_finished()` | `-> bool` | 非阻塞查询是否已结束 |
| `task::spawn_blocking` | `spawn_blocking(\|\| T) -> JoinHandle<T>` | 同步闭包移入**阻塞线程池**，不占用 worker |
| `task::block_in_place` | `block_in_place(\|\| T) -> T` | 当前 worker 让出其他任务；**仅多线程 runtime 可用** |
| `task::yield_now()` | 让出一次调度权 | 防长循环饿死同 worker 任务 |
| `task::JoinSet` | 收集一批任务 | `spawn` 多个后按**完成序** `join_next()` |

### 完整程序：任务结果与取消

<!-- rust-ecosystem: tokio-tasks -->
```rust
#[tokio::main(flavor = "current_thread")]
async fn main() {
    // pending 永远不自行完成，因此这个案例没有“先完成后 abort”的竞态。
    let h = tokio::spawn(std::future::pending::<()>());
    h.abort();
    assert!(h.await.unwrap_err().is_cancelled());
    assert_eq!(tokio::spawn(async { 21 * 2 }).await.unwrap(), 42);
    assert_eq!(tokio::task::spawn_blocking(|| 7u32 * 6).await.unwrap(), 42);
    println!("tokio-tasks: ok");
}
```

**JoinHandle 是 fire-and-forget 的**：不 `.await` 任务也会继续执行；drop handle 不会取消任务（与 `Future` 未被 poll 即不动不同）。

## 🔀 同步原语四兄弟

### 对照表（选型核心）

| 原语 | 构造 → 产出 | 发送 | 接收 | 关闭语义 | 典型场景 |
|------|------------|------|------|---------|---------|
| **mpsc** | `mpsc::channel(n)` → `(Sender, Receiver)` | `send(v).await`（异步，满时背压等待） | `recv().await → Option<T>` | 所有 Sender drop 后 recv 得 `None` | 任务间数据管道，**容量 n 即背压** |
| **mpsc 无界** | `mpsc::unbounded_channel()` | `send(v)`（同步，不等待） | 同上 | 同上 | 无法限流时慎用（内存可无限涨） |
| **oneshot** | `oneshot::channel()` → `(Sender, Receiver)` | `send(v)`（同步，**消费 self**，只能发一次） | Receiver 本身实现 Future：`rx.await → Result<T, RecvError>` | 发送端 drop 未发送 → `Err(RecvError)`；它不是带 `Closed` 变体的枚举 | 请求-响应、一次性回执 |
| **watch** | `watch::channel(init)` → `(Sender, Receiver)` | `send(v)`（同步，覆盖旧值） | `changed().await`；`borrow()` / `borrow_and_update()` | 所有发送端 drop 且当前值已读后，`changed()` 得 `Err` | 配置/状态最新值广播，只关心"现在" |
| **broadcast** | `broadcast::channel(n)` → `(Sender, Receiver)` | `send(v) -> Ok(读者数)`（同步） | `recv().await → Result<T, RecvError>`；多读者需各自 `subscribe()` | 所有发送端 drop 且已保留消息读尽后 `Closed`；读者落后得 `Lagged(n)` | 事件扇出，读者各自独立游标 |

### 完整程序：先排空消息，再观察关闭

<!-- rust-ecosystem: tokio-channels -->
```rust
#[tokio::main(flavor = "current_thread")]
async fn main() {
// mpsc：send 是 async；Receiver 关闭后返回 None 作为"流结束"
let (tx, mut rx) = tokio::sync::mpsc::channel::<i32>(4);
tx.send(1).await.unwrap();
drop(tx);
assert_eq!(rx.recv().await, Some(1));
assert_eq!(rx.recv().await, None);

// oneshot：send 同步且消费 self；发送失败原值退回 Err(v)
let (otx, orx) = tokio::sync::oneshot::channel::<&'static str>();
otx.send("done").unwrap();
assert_eq!(orx.await, Ok("done"));
let (otx, orx) = tokio::sync::oneshot::channel::<()>();
drop(otx);
assert!(orx.await.is_err());

// watch：send 同步可多次；changed() 与 borrow() 要配对
let (wtx, mut wrx) = tokio::sync::watch::channel(0u8);
wtx.send(1).unwrap();
wtx.send(2).unwrap();          // 当前接收者两次发送之间未读取，只看到最新值 2
wrx.changed().await.unwrap(); // 有"未读变更"才返回
assert_eq!(*wrx.borrow_and_update(), 2);
drop(wtx);
assert!(wrx.changed().await.is_err());

// broadcast：subscribe() 才产生新读者；send 返回当前读者数
let (btx, mut brx) = tokio::sync::broadcast::channel::<i32>(8);
let mut brx2 = btx.subscribe();
assert_eq!(btx.send(9).unwrap(), 2);
assert_eq!(brx.recv().await, Ok(9));
assert_eq!(brx2.recv().await, Ok(9));
drop(btx);
assert!(matches!(brx.recv().await, Err(tokio::sync::broadcast::error::RecvError::Closed)));
println!("tokio-channels: ok");
}
```

`watch::Receiver::borrow()` 返回读锁引用，持有期间会阻塞 sender；读取并标记已读用 `borrow_and_update()`。

## ⚡ select! 宏

### 语法要素

```rust
tokio::select! {
    biased;                                  // 可选：按声明顺序严格轮询（默认随机起点保公平）
    m = rx.recv(), if receiving => { /* m: Option<T>；None 后把 receiving 设为 false */ }
    Some(v) = rx2.recv() => { /* 模式失配（None）→ 该分支禁用 */ }
    _ = tokio::time::sleep(d) => { /* 超时分支 */ }
    else => { /* 全部分支都禁用/失配时执行 */ }
}
```

- 每个分支：`<模式> = <future表达式> => <handler>`，逗号分隔。
- **模式可解构**：`Some(m) = rx.recv()` 在通道关闭时失配，分支自动禁用——全部禁用时需有 `else` 兜底。
- **默认公平**：随机轮询起点；`biased;` 省掉随机开销但要自己防低优先级分支饿死。
- **取消安全**：临时创建且未获选的 future 会被丢弃；借用到外部保存的 future 不因此销毁原对象。mpsc `recv()` 落选不会消费消息；`send(value)` 落选保证没发出，但已移入 future 的 value 会被丢弃。需要保留消息时先 `reserve()` 等待容量，再用 Permit 发送。`read_exact()` 可能已消费部分输入，重试前必须处理这一进度。[发送与取消契约](https://docs.rs/tokio/1.53.0/tokio/sync/mpsc/struct.Sender.html#cancel-safety)

关闭不代表缓冲区已空，不要用 `!rx.is_closed()` 作为排空通道的守卫。

<!-- rust-ecosystem: tokio-reserve -->
```rust
#[tokio::main(flavor = "current_thread")]
async fn main() {
    let (tx, mut rx) = tokio::sync::mpsc::channel(1);
    tx.send(String::from("first")).await.unwrap();
    let mut pending = Some(String::from("second"));
    tokio::select! {
        biased;
        _ = std::future::ready(()) => {}, // 模拟取消，消息仍由外部变量持有
        permit = tx.reserve() => { permit.unwrap().send(pending.take().unwrap()); }
    }
    assert_eq!(pending.as_deref(), Some("second"));
    assert_eq!(rx.recv().await.as_deref(), Some("first"));
    tx.reserve().await.unwrap().send(pending.take().unwrap());
    drop(tx);
    assert_eq!(rx.recv().await.as_deref(), Some("second"));
    assert_eq!(rx.recv().await, None);
    println!("tokio-reserve: ok");
}
```

## ⏱️ time 定时器

| API | 说明 |
|------|------|
| `tokio::time::sleep(d).await` | 睡指定时长；返回 `Sleep` future |
| `sleep_until(instant)` | 睡到绝对时刻（`tokio::time::Instant`） |
| `timeout(d, fut)` | 包一层超时 → `Result<T, Elapsed>`；`Elapsed` 仅表示超时，无更多信息 |
| `timeout_at(instant, fut)` | 绝对时刻版 |
| `interval(d)` → `tick().await` | 周期 tick；首次 tick 立即完成 |
| `interval_at(start, period)` | 指定首个 tick 时刻 |

**测试加速**：feature `test-util` 下 `#[tokio::test(start_paused = true)]` 冻结时钟，用 `tokio::time::advance(d).await` 瞬时推进——单元测试不必真实等待。

<!-- rust-ecosystem: tokio-time -->
```rust
use std::time::Duration;
#[tokio::main(flavor = "current_thread")]
async fn main() {
tokio::time::pause(); // 这个程序使用虚拟时间，无需等待真实的 50 毫秒
let r = tokio::time::timeout(
    Duration::from_millis(5),
    tokio::time::sleep(Duration::from_millis(50)),
).await;
assert!(r.is_err());
println!("tokio-time: ok");
}
```

## 📡 IO trait（异步读写）

### Ext trait 方法速查（`use tokio::io::...Ext`）

| Ext trait | 常用方法 | 备注 |
|-----------|---------|------|
| `AsyncReadExt` | `read` / `read_exact` / `read_to_end` / `read_to_string` / `read_u8`…`read_u32`… | `read_u32` **大端**；`read_u32_le` 小端；整数读法填入自带缓冲 |
| `AsyncWriteExt` | `write` / `write_all` / `write_fmt` / `flush` / `shutdown` / `write_u8`… | `shutdown` 等价刷完并关闭写端 |
| `AsyncBufReadExt` | `fill_buf` / `consume` / `read_line` / `lines()` / `split(b'\n')` | 需 `BufReader` 包一层 |
| `AsyncSeekExt` | `seek(SeekFrom::…)` | 语义同 std |

### 谁实现了这些 trait

| 类型 | 读/写 | 说明 |
|------|-------|------|
| `&[u8]` | 读 | 可将切片引用变量作为内存读取游标 |
| `&mut [u8]` | 写 | 固定长度内存目标，空间耗尽后不能继续写入 |
| `Vec<u8>` | 写 | 内存 sink |
| `tokio::fs::File` | 读写 | feature `fs` |
| `tokio::net::TcpStream` | 读写 | feature `net`；`into_split()` 拆读写半 |
| `tokio::io::duplex(n)` / `simplex()` | 双工/单工 | 内存管道，测试友好 |
| `tokio::io::stdin()/stdout()` | 读写 | feature `io-std` |
| `tokio::io::copy(&mut r, &mut w)` | — | `Result<u64>` 拷贝字节数；`copy_bidirectional` 双向（代理场景） |

```rust
use tokio::io::{AsyncReadExt, AsyncWriteExt, AsyncBufReadExt};

// &[u8] 实现 AsyncRead：read_u32 按大端读 4 字节
let mut rd: &[u8] = &[1, 0, 0, 0, 2];
assert_eq!(rd.read_u32().await.unwrap(), 0x0100_0000);

// Vec<u8> 实现 AsyncWrite
let mut out: Vec<u8> = Vec::new();
out.write_all(b"hi").await.unwrap();
out.flush().await.unwrap();
out.shutdown().await.unwrap();

// 按行读
let mut brd = tokio::io::BufReader::new(&b"line1\nline2\n"[..]);
let mut line = String::new();
brd.read_line(&mut line).await.unwrap();
assert_eq!(line, "line1\n");
```

## 🌊 stream 适配（tokio-stream）

**Stream trait 不在 tokio 本体**：`tokio-stream` 重导出 `futures_core::Stream`，并提供适配器。本文固定版本 0.1.17 的默认 feature 是 `time`；`ReceiverStream`/`StreamMap` 无需额外 feature，`WatchStream`/`BroadcastStream` 需 `sync`，`IntervalStream` 需 `time`。其它 wrappers 还可能要求 `io-util` 或 `net`，不要从下面的名称表推断全部默认可用。[feature 表](https://docs.rs/crate/tokio-stream/0.1.17/features)

```rust
use tokio_stream::{Stream, StreamExt, wrappers::ReceiverStream, StreamMap};
```

### StreamExt 方法（注明者需 feature `time`）

`next` / `try_next` / `map` / `then` / `merge` / `filter` / `filter_map` / `fuse` / `take` / `take_while` / `skip` / `skip_while` / `all` / `any` / `chain` / `fold` / `collect` / `peekable` / `map_while`，以及 `timeout` / `timeout_repeating` / `throttle` / `chunks_timeout`（需 `time`）。

### 构造与适配

| 来源 | 用法 |
|------|------|
| `tokio_stream::iter(0..5)` / `once(v)` / `pending()` / `empty()` | 同步序列转异步流 |
| `wrappers::ReceiverStream` / `UnboundedReceiverStream` | mpsc 接收端 → Stream（无需 feature） |
| `wrappers::WatchStream`（需 `sync`） | watch 接收端 → Stream（含当前值） |
| `wrappers::BroadcastStream`（需 `sync`） | broadcast 接收端 → `Result<T, BroadcastStreamRecvError>`（`Lagged(n)` 表读者落后丢帧） |
| `wrappers::{IntervalStream, SplitStream, LinesStream, TcpListenerStream, JoinSetStream}` | 定时器 / 拆半 IO / 行流 / 监听器 / JoinSet → Stream |
| `StreamMap` | 多条流按 key 合并；`insert`/`remove` 运行时增删，产出 `(key, item)` |

```rust
use tokio_stream::{wrappers::ReceiverStream, StreamExt, StreamMap};

// mpsc → Stream → next
let (tx, rx) = tokio::sync::mpsc::channel::<i32>(4);
tx.send(5).await.unwrap();
drop(tx);
let mut st = ReceiverStream::new(rx);
assert_eq!(st.next().await, Some(5));
assert_eq!(st.next().await, None); // 通道关闭 → 流结束

// 异构流合并
let mut map = StreamMap::new();
map.insert("a", ReceiverStream::new(rx_a));
while let Some((key, item)) = map.next().await { /* ... */ }
```

## 🎨 最佳实践与陷阱

有界通道让生产者在容量耗尽时等待，但总任务数量和生产速度也需限制，否则排队可能只是转移到任务堆积。阻塞调用可放合适执行器，已有异步 API 无需再全部包 spawn_blocking；CPU 密集工作同样要限并发。

select 丢弃未获选 Future 的语义要求检查取消安全，部分读写可能已经推进，不能简单重来。任务需要明确关闭与等待责任，abort 不会停止所有已经开始的阻塞工作。Runtime Builder 按需启用时间或 I/O 驱动，也可 enable_all；验收取消和关闭时资源确实释放。

## ❓ 常见问题

### 练习：优雅停止一个有界工作队列

从通道完整程序开始，将输入改成三个任务：收到停止信号后停止接收新工作，消费缓冲中的工作，再等待工作任务退出。验收正常停止、生产者提前 drop、工作任务返回错误三条路径。说明为什么“关闭后立刻丢弃 receiver”会丢任务，以及为什么仅 drop JoinHandle 不足以证明资源已清理。

### Q1: `spawn` panic "must be called from the context of a Tokio 1.x runtime"？
**A**: 当前线程没有 runtime 上下文。要么整体进入（`#[tokio::main]` / `rt.block_on`），要么在库边界持有 `Handle`：`tokio::runtime::Handle::current()` / `Handle::try_current()`，用 `handle.spawn(...)` 从同步代码投递任务。

### Q2: `Stream` 为什么不在 tokio crate 里？
**A**: Tokio 0.2 曾内置 `tokio::stream`，随 Stream trait 设计迭代移出本体；稳定后的归属是 `tokio-stream`（re-export `futures_core::Stream`）。tokio 本体只保留产生"可转 Stream"资源的类型（Receiver、interval 等），适配器全部在 `tokio_stream::wrappers`。

## 📏 模式不变量

1. **async 函数体由 poll 驱动**：仅创建 future 不执行函数体；但普通函数返回 future 前可以已做工作，spawn 返回的 handle 背后任务也已提交。
2. **阻塞与 reactor 互斥**：任何长阻塞必须移出 worker（`spawn_blocking`）或让出 worker（`block_in_place`），与具体 Tokio 版本无关。
3. **通道容量即背压策略**：有界=流控，无界=内存换吞吐，oneshot/watch/broadcast 是"单值/最新值/扇出"三种语义特化——换运行时这套判断依然成立。
4. **多路等待时检查所有权**：`select!` 丢弃落选的临时 future；外部保存并借用的 future 可以继续使用，消息与部分 I/O 进度需要明确保存位置。
5. **事件扇出必有滞后边界**：容量有限的广播通道本质是"最新 n 条事件"的滑动窗口，消费者必须处理丢帧。

## 🔗 相关资源

- 🌐 **[docs.rs/tokio/1.53.0](https://docs.rs/tokio/1.53.0/tokio/)** - 本篇基线版本官方 API
- 🌐 **[Tokio Tutorial](https://tokio.rs/tokio/tutorial)** - 官方教程（含 mini-redis 实战）
- 🌐 **[docs.rs/tokio-stream](https://docs.rs/tokio-stream)** - Stream trait 与适配器
- 📄 **[并发与 async 教程](../../basics/09-concurrency-async.md)** - 语言层 async/await 入门
- 📄 **[async 内核](../language-concepts/08-async-internals.md)** - Future/Pin/Waker 机制
- 📄 **[Axum 要点](../framework-essentials/11-axum-essentials.md)** - Tokio 生态 Web 框架
- 📄 **[Tauri 2 要点](../framework-essentials/09-tauri-2-essentials.md)** - Tauri 命令层背后的 Tokio runtime
- 📄 **[错误处理库](./14-error-libraries.md)** - JoinError 与 anyhow 桥接

---

## 📝 总结

1. **进入方式两族**：宏与 Builder；手动 build 按 API 所需启用 I/O 或时间驱动，也可用 `enable_all`。
2. **任务三出口**：`.await` 收值、`abort` 取消、`spawn_blocking` 隔离阻塞。
3. **通道按语义选**：多值管道 mpsc、单值回执 oneshot、最新状态 watch、扇出 broadcast。
4. **Stream 是独立 crate**：`tokio-stream` 负责 trait 与适配，tokio 本体提供资源。

**文档版本**: v1.0.0 | **最后更新**: 2026年9月 | **维护团队**: Dev Quest Team


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
