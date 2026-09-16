# Tokio - 异步运行时全量速查

> **文档简介**: Tokio 1.53 异步运行时的 API 速查字典——runtime 构建、任务调度、四类同步原语、`select!`、定时器、异步 IO trait 与 stream 适配，一页查全。
>
> **目标读者**: 已掌握 Rust 所有权与 async/await 语法、需要写异步服务或 Tauri/Axum 应用的中级开发者。
>
> **前置知识**: [basics/09-concurrency-async](../../basics/09-concurrency-async.md)、[async 内核（Future/Pin/Waker）](../language-concepts/08-async-internals.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 字典（全量参考，单一事实来源） |
| **难度** | ⭐⭐ 进阶 |
| **标签** | `#rust` `#tokio` `#async` `#reference` |
| **更新日期** | `2026年9月` |

**版本基线**: Tokio **1.53**（核实日期 2026-09-16，单一事实来源见[模块 README 技术基线](../../README.md)）。Stream trait 属独立 crate `tokio-stream`（版本未列入基线，不在此标注）。

## 🎯 学习目标

- ✅ 用 Builder 与 `#[tokio::main]` 两种 flavor 正确搭建/进入 runtime
- ✅ 按"容量即背压"原则在 mpsc/oneshot/watch/broadcast 中选对通道
- ✅ 用 `select!` 组合多路异步事件，理解 biased/if 守卫/else 与取消安全
- ✅ 速查 AsyncRead/AsyncWrite 扩展 trait 与 tokio-stream 适配器

## 📋 目录

- [Runtime：创建与进入](#runtime-创建与进入)
- [任务 spawn 与 JoinHandle](#任务-spawn-与-joinhandle)
- [同步原语四兄弟](#同步原语四兄弟)
- [select! 宏](#select-宏)
- [time 定时器](#time-定时器)
- [IO trait](#io-trait-异步读写)
- [stream 适配](#stream-适配tokio-stream)
- [最佳实践与陷阱](#最佳实践与陷阱)

---

## 🔍 核心概念：Tokio 在异步栈中的位置

`async fn` 只是生成状态机（[Future](../language-concepts/08-async-internals.md)），**不执行**。Tokio 补齐执行层的三件事：**reactor**（注册 IO/定时器就绪事件）、**调度器**（多线程 work-stealing 执行任务）、**资源层**（`net`/`time`/`io`/`sync` 的异步版本 API）。本文所有 API 均要求"已在 runtime 上下文内"——要么在 `block_on` 的 future 里，要么在 `spawn` 出的任务里。

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
| `tokio::spawn` | `spawn<F: Future>(fut) -> JoinHandle<F::Output>` | 调度到 runtime；**必须**在 runtime 上下文内调用 |
| `JoinHandle::await` | `Result<T, JoinError>` | 任务 panic 或被 abort 时为 `Err` |
| `JoinHandle::abort()` | 取消任务 | 被 abort 的 `.await` 返回 `Err`，`JoinError::is_cancelled() == true` |
| `JoinHandle::is_finished()` | `-> bool` | 非阻塞查询是否已结束 |
| `task::spawn_blocking` | `spawn_blocking(\|\| T) -> JoinHandle<T>` | 同步闭包移入**阻塞线程池**，不占用 worker |
| `task::block_in_place` | `block_in_place(\|\| T) -> T` | 当前 worker 让出其他任务；**仅多线程 runtime 可用** |
| `task::yield_now()` | 让出一次调度权 | 防长循环饿死同 worker 任务 |
| `task::JoinSet` | 收集一批任务 | `spawn` 多个后按**完成序** `join_next()` |

### 示例（实测）

```rust
use std::time::Duration;

// abort → JoinError::is_cancelled
let h = tokio::spawn(async {
    tokio::time::sleep(Duration::from_millis(50)).await;
});
h.abort();
assert!(h.await.unwrap_err().is_cancelled());

// 正常完成取值
let v = tokio::spawn(async { 21 * 2 }).await.unwrap();
assert_eq!(v, 42);

// CPU/阻塞任务走阻塞线程池
let v = tokio::task::spawn_blocking(|| 7u32 * 6).await.unwrap();
```

**JoinHandle 是 fire-and-forget 的**：不 `.await` 任务也会继续执行；drop handle 不会取消任务（与 `Future` 未被 poll 即不动不同）。

## 🔀 同步原语四兄弟

### 对照表（选型核心）

| 原语 | 构造 → 产出 | 发送 | 接收 | 关闭语义 | 典型场景 |
|------|------------|------|------|---------|---------|
| **mpsc** | `mpsc::channel(n)` → `(Sender, Receiver)` | `send(v).await`（异步，满时背压等待） | `recv().await → Option<T>` | 所有 Sender drop 后 recv 得 `None` | 任务间数据管道，**容量 n 即背压** |
| **mpsc 无界** | `mpsc::unbounded_channel()` | `send(v)`（同步，不等待） | 同上 | 同上 | 无法限流时慎用（内存可无限涨） |
| **oneshot** | `oneshot::channel()` → `(Sender, Receiver)` | `send(v)`（同步，**消费 self**，只能发一次） | Receiver 本身实现 Future：`rx.await → Result<T, RecvError>` | 发送端 drop 未发送 → `Err(RecvError::Closed)` | 请求-响应、一次性回执 |
| **watch** | `watch::channel(init)` → `(Sender, Receiver)` | `send(v)`（同步，覆盖旧值） | `changed().await`；`borrow()` / `borrow_and_update()` | 发送端 drop 后 `changed()` 得 `Err` | 配置/状态最新值广播，只关心"现在" |
| **broadcast** | `broadcast::channel(n)` → `(Sender, Receiver)` | `send(v) -> Ok(读者数)`（同步） | `recv().await → Result<T, RecvError>`；多读者需各自 `subscribe()` | 全部 drop 前 `Closed`；读者落后超容量得 `Err(RecvError::Lagged(n))` | 事件扇出，读者各自独立游标 |

### 签名细节（易错点）

```rust
// mpsc：send 是 async；Receiver 关闭后返回 None 作为"流结束"
let (tx, mut rx) = tokio::sync::mpsc::channel::<i32>(4);
tx.send(1).await.unwrap();
drop(tx);
assert_eq!(rx.recv().await, None); // Some(1) 读完之后

// oneshot：send 同步且消费 self；发送失败原值退回 Err(v)
let (otx, orx) = tokio::sync::oneshot::channel::<&'static str>();
otx.send("done").unwrap();
assert_eq!(orx.await, Ok("done"));

// watch：send 同步可多次；changed() 与 borrow() 要配对
let (wtx, mut wrx) = tokio::sync::watch::channel(0u8);
wtx.send(2).unwrap();          // 连发两次只会看到最新值 2
wrx.changed().await.unwrap(); // 有"未读变更"才返回
assert_eq!(*wrx.borrow(), 2);

// broadcast：subscribe() 才产生新读者；send 返回当前读者数
let (btx, mut brx) = tokio::sync::broadcast::channel::<i32>(8);
let mut brx2 = btx.subscribe();
assert_eq!(btx.send(9).unwrap(), 2);
assert_eq!(brx.recv().await, Ok(9));
```

`watch::Receiver::borrow()` 返回读锁引用，持有期间会阻塞 sender；读取并标记已读用 `borrow_and_update()`。

## ⚡ select! 宏

### 语法要素

```rust
tokio::select! {
    biased;                                  // 可选：按声明顺序严格轮询（默认随机起点保公平）
    m = rx.recv(), if !rx.is_closed() => { /* m: Option<T> */ }   // 绑定 + if 守卫
    Some(v) = rx2.recv() => { /* 模式失配（None）→ 该分支禁用 */ }
    _ = tokio::time::sleep(d) => { /* 超时分支 */ }
    else => { /* 全部分支都禁用/失配时执行 */ }
}
```

- 每个分支：`<模式> = <future表达式> => <handler>`，逗号分隔。
- **模式可解构**：`Some(m) = rx.recv()` 在通道关闭时失配，分支自动禁用——全部禁用时需有 `else` 兜底。
- **默认公平**：随机轮询起点；`biased;` 省掉随机开销但要自己防低优先级分支饿死。
- **取消安全**：未被选中的分支 future 被**丢弃**。分支里的 future 必须能安全取消（`recv()`、`send()` 是取消安全的；`read_exact()` 半读到一半的数据会丢，需缓冲或拆分）。

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

```rust
// 实测：超时返回 Err(Elapsed)
let r = tokio::time::timeout(
    Duration::from_millis(5),
    tokio::time::sleep(Duration::from_millis(50)),
).await;
assert!(r.is_err());
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
| `&[u8]` / `&mut [u8]` | 读 | 内存源最常用 |
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

**Stream trait 不在 tokio 本体**：异步序列抽象在独立轻量 crate `tokio-stream`（`futures` crate 也可）。**默认 features 仅含 `time`**（实测 0.1 线）：`ReceiverStream`/`StreamMap` 无需额外 feature，`WatchStream`/`BroadcastStream` 需 `sync`（`cargo add tokio-stream --features sync`），`IntervalStream` 由默认的 `time` 覆盖。

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

### ✅ 推荐做法
- **容量即背压**：有界 mpsc 满了 `send().await` 自然等待，是流控的第一道闸。
- **阻塞移出 worker**：文件 IO、重 CPU、FFI 调用一律 `spawn_blocking`。
- **`select!` 分支保持取消安全**：非取消安全操作（如整段 `read_exact`）拆小或先落缓冲。

### ❌ 避免陷阱
- **在 async fn 里 `std::thread::sleep`**：卡死整个 worker 线程；用 `tokio::time::sleep`。
- **`current_thread` runtime 用 `block_in_place`**：会 panic，仅多线程 runtime 支持。
- **spawn 出的"孤儿任务"失控**：保存 `JoinHandle` 或用 `JoinSet` 管理，需要时可 `abort`。
- **broadcast 读者忽略 `Lagged`**：`Lagged(n)` 表示已丢 n 帧，必须显式决定重同步策略。
- **手动 Builder 忘了 `enable_all()`**：`net`/`time` API 运行时 panic。

## ❓ 常见问题

### Q1: `spawn` panic "must be called from the context of a Tokio 1.x runtime"？
**A**: 当前线程没有 runtime 上下文。要么整体进入（`#[tokio::main]` / `rt.block_on`），要么在库边界持有 `Handle`：`tokio::runtime::Handle::current()` / `Handle::try_current()`，用 `handle.spawn(...)` 从同步代码投递任务。

### Q2: `Stream` 为什么不在 tokio crate 里？
**A**: Tokio 0.2 曾内置 `tokio::stream`，随 Stream trait 设计迭代移出本体；稳定后的归属是 `tokio-stream`（re-export `futures_core::Stream`）。tokio 本体只保留产生"可转 Stream"资源的类型（Receiver、interval 等），适配器全部在 `tokio_stream::wrappers`。

## 📏 模式不变量

1. **Future 是惰性状态机**：不被 executor poll 就永不执行——"创建了但没 spawn/没 await"的代码是静默 no-op。
2. **阻塞与 reactor 互斥**：任何长阻塞必须移出 worker（`spawn_blocking`）或让出 worker（`block_in_place`），与具体 Tokio 版本无关。
3. **通道容量即背压策略**：有界=流控，无界=内存换吞吐，oneshot/watch/broadcast 是"单值/最新值/扇出"三种语义特化——换运行时这套判断依然成立。
4. **多路等待时落选分支被取消**：`select!` 每次循环丢弃未完成分支，"分支内状态"必须可安全丢弃或外置到分支外。
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

1. **进入方式两族**：宏（main 场景）与 Builder（库/多 runtime），手动 build 必须 `enable_all`。
2. **任务三出口**：`.await` 收值、`abort` 取消、`spawn_blocking` 隔离阻塞。
3. **通道按语义选**：多值管道 mpsc、单值回执 oneshot、最新状态 watch、扇出 broadcast。
4. **Stream 是独立 crate**：`tokio-stream` 负责 trait 与适配，tokio 本体提供资源。

**文档版本**: v1.0.0 | **最后更新**: 2026年9月 | **维护团队**: Dev Quest Team
