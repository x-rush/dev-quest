# 并发 API 速查 - Executor、虚拟线程、并发集合与 CompletableFuture

> **文档简介**: Java 并发工具条目式速查：线程创建、Executor 体系、虚拟线程、并发集合、同步器、原子类、CompletableFuture 与 ScopedValue
>
> **目标读者**: 需要查阅并发 API 细节与选型边界的开发者
>
> **前置知识**: 线程基础概念；教程见 [现代 Java 特性](../../basics/07-modern-features.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#并发` `#虚拟线程` `#CompletableFuture` `#并发集合` |
| **更新日期** | `2026年9月` |

</details>

## 🧵 线程创建方式

```java
// 平台线程
Thread.ofPlatform().name("worker-", 0).start(() -> work());   // Builder 风格（Java 21）
new Thread(() -> work()).start();                             // 传统写法

// 虚拟线程（Java 21+）
Thread.startVirtualThread(() -> work());                      // 快捷创建
var vt = Thread.ofVirtual().name("v-", 0).start(() -> work());
```

**陷阱**: 虚拟线程适合 IO 密集；CPU 密集任务应保持平台线程 + 线程池（数量 ≈ 核数）。

## 🏊 Executor 体系

| 工厂方法 | 语义 | 适用 |
|---------|------|------|
| `newFixedThreadPool(n)` | 固定 n 个平台线程 | CPU 型任务 |
| `newCachedThreadPool()` | 按需创建、空闲回收 | 突发短任务（注意无限扩张） |
| `newSingleThreadExecutor()` | 单线程顺序执行 | 串行化任务 |
| `newVirtualThreadPerTaskExecutor()` | 每任务一个虚拟线程 | **IO 密集首选**（Java 21+） |
| `newWorkStealingPool()` | ForkJoin 池 | 分治/并行流默认池 |

```java
// 提交与取结果
Future<Integer> f = executor.submit(() -> compute());
Integer r = f.get(5, TimeUnit.SECONDS);          // 务必设置超时

// 生命周期：提交后 shutdown 等待收尾
executor.shutdown();
if (!executor.awaitTermination(30, TimeUnit.SECONDS)) executor.shutdownNow();
```

**陷阱**: `Executors.newFixedThreadPool` 的无界队列可能堆积任务致 OOM；生产建议手动 `new ThreadPoolExecutor(...)` 明确队列容量与拒绝策略。

## 🌱 虚拟线程要点

```java
// 标准姿势：try-with-resources 作为"结构化"边界
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    tasks.forEach(t -> executor.submit(() -> callRemote(t)));
}   // 阻塞直到全部完成
```

- **不要池化**虚拟线程，也不要用它跑 CPU 任务
- `synchronized` 内阻塞在 Java 21 会钉住载体线程（Java 24 修复）；21 上热点路径改用 `ReentrantLock`
- 需要限制并发度时用 `Semaphore` 而非线程池
- `ThreadLocal` 在百万级虚拟线程下内存放大——改用 `ScopedValue`（Java 25 正式）：

```java
private static final ScopedValue<User> CURRENT_USER = ScopedValue.newInstance();

ScopedValue.where(CURRENT_USER, user).run(() -> handle());
CURRENT_USER.get();   // 绑定范围内可读，不可写
```

- 结构化并发仍处预览（`StructuredTaskScope`，JDK 25 为第 5 次预览），生产暂用 try-with-resources + Executor

## 🗄️ 并发集合

| 类 | 特点 | 用法要点 |
|----|------|---------|
| `ConcurrentHashMap` | 高并发哈希表 | `computeIfAbsent`/`merge` 原子；**key/value 不允许 null** |
| `CopyOnWriteArrayList` | 写时复制 | 迭代无锁快照；写多场景禁用 |
| `ConcurrentLinkedQueue` | 无锁队列 | 无界，CAS 实现 |
| `ArrayBlockingQueue` | 有界阻塞队列 | 生产者-消费者限流首选 |
| `LinkedBlockingQueue` | 阻塞队列 | 默认无界，建议显式容量 |
| `BlockingDeque` | 双端阻塞 | 工作窃取模式 |

```java
// 生产者-消费者
var queue = new ArrayBlockingQueue<String>(1000);
queue.put("task");          // 满则阻塞
String task = queue.take(); // 空则阻塞
```

## 🔄 同步器与原子类

| 工具 | 用途 | 关键方法 |
|------|------|---------|
| `CountDownLatch` | 等待 N 个事件完成 | `countDown()` / `await()`（一次性） |
| `CyclicBarrier` | N 方互相等待、可复用 | `await()` / `reset()` |
| `Semaphore` | 限流/资源许可 | `acquire()` / `release()` |
| `ReentrantLock` | 可中断、可超时、公平锁 | `tryLock(1, SECONDS)`；必须 try-finally unlock |
| `ReadWriteLock` | 读共享写互斥 | `readLock()` / `writeLock()` |
| `AtomicInteger` 等 | 无锁原子单值 | `incrementAndGet()` / `compareAndSet()` |
| `LongAdder` | 高并发计数 | `increment()`，`sum()` 读取（写竞争远优于 AtomicLong） |

**陷阱**: 忘记 unlock → 死锁；`wait/notify` 遗留用法 → 优先 `BlockingQueue`、`CountDownLatch` 等高级工具。

## 🔮 CompletableFuture

```java
var f1 = CompletableFuture.supplyAsync(() -> fetchUser(id));        // 默认 ForkJoinPool
var f2 = CompletableFuture.supplyAsync(() -> fetchOrders(id), ioPool); // 指定池（IO 任务建议虚拟线程池）

f1.thenCombine(f2, (user, orders) -> render(user, orders))          // 两路合并
  .thenApply(this::enrich)                                          // 同步转换
  .thenCompose(this::saveAsync)                                     // 接另一个异步（防嵌套 Future）
  .exceptionally(ex -> fallback(ex))                                // 兜底
  .thenAccept(System.out::println);

CompletableFuture.allOf(f1, f2, f3).join();                         // 等待全部
CompletableFuture.anyOf(f1, f2).join();                             // 任一完成
```

**陷阱**:
- 默认池是 `ForkJoinPool.commonPool`——IO 任务务必传自定义 Executor（推荐虚拟线程池）
- `get()`/`join()` 不带超时会永久阻塞
- 异常只在触发终端操作的线程可见，`exceptionally`/`handle` 必须接上

## ✅ 最佳实践 / ❌ 陷阱清单

大量阻塞等待可评估虚拟线程，CPU 任务则受可用核数约束；两者都需要限制访问稀缺资源的并发。并发集合保证其声明的操作安全，不自动保证“先检查再修改”等多个步骤的业务原子性。

等待应有取消或超时策略，但超时不自动停止后台任务，需要传递中断并释放资源。用两个并发调用测试同一库存不被超卖，再观察负载增加时的排队；不要依赖危险的强制停线程操作恢复状态。

## 🔗 相关文档

- 📄 **[Stream/Optional API 速查](./03-streams-optional.md)** - 并行流的边界
- 📄 **[集合框架与泛型](./02-collections-generics.md)** - 非并发集合选型
- 📄 **[常见错误排查](../quick-references/02-troubleshooting.md)** - 死锁与竞态排查
- 📄 **[现代 Java 特性](../../basics/07-modern-features.md)** - 虚拟线程教程


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
