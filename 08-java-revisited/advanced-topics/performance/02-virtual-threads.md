# Java 21 虚拟线程并发模型

> **文档简介**: 深入解释虚拟线程如何重构 Java 并发经济学：载体线程与挂载机制、为什么"阻塞"不再是罪恶、Spring Boot 4 下的启用与适用边界、以及 Pinning 等现实陷阱
>
> **目标读者**: 理解传统线程池模型、想评估虚拟线程收益的开发者
>
> **前置知识**: [并发 API 速查](../../reference/language-concepts/04-concurrency-api.md)、[现代 Java 特性](../../basics/07-modern-features.md)、[JVM 调优与 GC 基础](./01-jvm-tuning.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#虚拟线程` `#并发` `#Java21` `#Loom` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

- 说清虚拟线程、载体线程、调度器三者的关系
- 理解"一请求一线程"为何重新变得可行
- 在 Spring Boot 4 中正确启用，并识别 Pinning 场景

## 🔍 一、旧模型的经济学危机

平台线程（`Thread`）是 1:1 映射到 OS 线程的：栈大小与提交内存取决于平台和 JVM 参数，另有内核调度成本。

```java
// 经典解法：线程池限制并发
ExecutorService pool = Executors.newFixedThreadPool(200);
// 200 并发以上，请求排队——线程是稀缺资源，于是"池化 + 异步化"
```

为了用少量线程扛高并发，业界发展出整套复杂度：`CompletableFuture` 回调、Reactor 响应式栈、`WebFlux`。**代价是可读性与调试性**：堆栈断裂、上下文丢失。

## 🔍 二、虚拟线程的模型

### 关键角色

```text
虚拟线程（百万级，栈在堆上）        载体线程（ForkJoinPool，数量≈CPU核数）
        │                                    ▲
        │        挂载 mount / 卸载 unmount    │
        └────────────────────────────────────┘
             虚拟线程阻塞时主动让出载体线程
```

- **虚拟线程**：JVM 管理的轻量执行单元，栈帧可保存在堆中，内存随实际栈深度和所持对象变化
- **载体线程（Carrier）**：真正跑在 CPU 上的平台线程，由内部 `ForkJoinPool`（FIFO 模式）调度
- **挂载/卸载**：虚拟线程调用阻塞 API（如 Socket 读）时，JVM 把它的栈从载体上"卸下"保存到堆，载体立即执行其他虚拟线程——许多受支持的阻塞操作可以释放载体；并非所有阻塞都如此

### 为什么这是范式转变

```java
// 一请求一线程：同步写法，异步级别的扩展性
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 100_000).forEach(i ->
        executor.submit(() -> {
            Thread.sleep(Duration.ofSeconds(1));   // "阻塞"但几乎零成本
            return fetchUserData(i);               // 网络调用同理
        }));
}
// 仅作调度示意；下游容量与内存仍需限额，submit 返回的 Future 需要收集失败
```

写同步代码，获得异步扩展性——**这是 Loom 项目的全部野心**。

## 🛠️ 三、Spring Boot 4 中的启用

```yaml
# 一行配置：Tomcat/Jetty 改用虚拟线程处理请求
spring:
  threads:
    virtual:
      enabled: true
```

在支持的嵌入式服务器与自动配置执行器中生效；自定义 Executor、Scheduler 及不同应用模型可能改变结果。固定延迟调度等还有专门语义，需检查实际执行器。**前提**：Java 21+（推荐 25）+ Boot 3.2+（Boot 4 沿用同一属性）。

### 收益最大的场景

| 场景 | 原因 |
|------|------|
| IO 密集 REST 服务（调 DB/第三方 API） | 阻塞等待大量时间，卸载收益高 |
| 并发出站调用编排 | `Executors.newVirtualThreadPerTaskExecutor()` 替代线程池调参 |
| 高并发 SSE/WebSocket 推送 | 连接数 ≫ CPU 核数 |

```java
// 并行聚合多个下游：平铺直叙，无回调嵌套
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    var userF  = executor.submit(userClient::fetch);
    var orderF = executor.submit(orderClient::fetch);
    var pointsF = executor.submit(pointsClient::fetch);
    return new Dashboard(userF.get(), orderF.get(), pointsF.get());
}
```

## ⚠️ 四、Pinning 与现实陷阱

### 什么导致 Pinning（钉死载体线程）

```java
synchronized (lock) {          // ❌ 块内阻塞时虚拟线程无法卸载
    socket.read();             //    载体线程被钉住 → 吞吐退化为平台线程模型
}
```

- `synchronized` 块/方法内发生阻塞（JDK 24 已修复，Java 21 仍存在）
- **本地方法（JNI）内阻塞**：无法避免，需避开此类 API

```java
// 解法：改用 ReentrantLock（java.util.concurrent 全系虚拟线程友好）
private final ReentrantLock lock = new ReentrantLock();

lock.lock();
try {
    socket.read();             // ✅ 阻塞时正常卸载
} finally {
    lock.unlock();
}
```

**检测**：Java 21 可用 -Djdk.tracePinnedThreads=full 辅助定位；更高版本应查对应 JDK 的 JFR 事件与诊断选项，不能假设旧属性持续有效。

### 其他纪律

1. **不要池化虚拟线程**——它们廉价到"用完即弃"，池化反而引入排队瓶颈
2. **ThreadLocal 谨慎用**——百万线程 × 大对象 = 堆膨胀；传递词法作用域内的只读上下文可评估 ScopedValue；它不会自动传播到任意新建线程（Java 25 已转正，JEP 506）
3. **CPU 密集任务无收益**——瓶颈在核数，虚拟线程只解放"等待"
4. **信号量做并发闸门**——限流下游用 `Semaphore.acquire()`（会卸载），而非限制线程数

## 🔍 五、与响应式的关系

| 维度 | 虚拟线程 | Reactor/WebFlux |
|------|---------|-----------------|
| 编程模型 | 同步直白 | 回调/操作符链 |
| 容量限制 | 取决于内存、载体与下游资源 | 取决于事件循环、背压与下游资源 |
| 迁移成本 | 检查线程局部变量、阻塞与并发限制 | 检查操作符、上下文与阻塞混用 |
| 适用 | 绝大多数 IO 服务 | 极端连接密度、流处理 |

实践建议：默认虚拟线程 + 传统栈；确有极端吞吐需求再局部引入响应式——两者可共存。

<!-- full-library-explanation -->
## 虚拟线程降低等待成本，不增加下游容量

假设数据库池只有 20 个连接，同时进入 2 万个请求。换成虚拟线程可以减少平台线程占用，但仍只有约 20 个请求同时持有连接，其余请求需要排队。必须同时约束入口并发、等待超时和每个请求持有的数据，不能把“线程便宜”理解成“排队免费”。

ExecutorService.close 会等待任务结束；前面聚合示例中，某个 Future.get 失败并不会自动取消其他任务。需要明确总截止时间、取消传播以及下游是否响应中断。未保存 Future 的 submit 任务，其异常还可能停留在 Future 中，不能只凭主线程正常退出判定工作全部成功。

**练习**：用固定延迟的假下游，比较固定线程池与虚拟线程执行同一批任务；记录吞吐、p95、排队长度和内存。然后用 Semaphore 把下游并发限定为 20，观察线程更多并不突破该限制。CPU 计算应另做对照，不能从 sleep 实验推导 CPU 吞吐提升。

版本边界需要单独记忆：Java 21 的 synchronized 阻塞可能钉住载体；JDK 24 的 JEP 491 改善了这一情况。升级后仍应分析真实 JFR 数据，而非机械地替换所有 synchronized。参考 [JEP 444](https://openjdk.org/jeps/444) 与 [JEP 491](https://openjdk.org/jeps/491)。

## 🔗 相关文档

### 本模块
- 📖 [并发 API 速查](../../reference/language-concepts/04-concurrency-api.md) — 全量并发 API 条目
- 📖 [现代 Java 特性](../../basics/07-modern-features.md) — 虚拟线程入门章节
- 📄 [JVM 调优与 GC 基础](./01-jvm-tuning.md) — 线程栈内存模型的另一面
- 📄 [K8s 部署](../../deployment/02-kubernetes-deployment.md) — 虚拟线程时代的容器内存评估
- 📄 [生产级 Spring Boot 应用](../../projects/04-production-spring-app.md) — 并发闸门与容量保护


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
