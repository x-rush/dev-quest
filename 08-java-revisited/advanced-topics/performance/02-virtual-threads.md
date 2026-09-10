# Java 21 虚拟线程并发模型

> **文档简介**: 深入解释虚拟线程如何重构 Java 并发经济学：载体线程与挂载机制、为什么"阻塞"不再是罪恶、Spring Boot 3 下的启用与适用边界、以及 Pinning 等现实陷阱
>
> **目标读者**: 理解传统线程池模型、想评估虚拟线程收益的开发者
>
> **前置知识**: [并发 API 速查](../../reference/language-concepts/04-concurrency-api.md)、[现代 Java 特性](../../basics/07-modern-features.md)、[JVM 调优与 GC 基础](./01-jvm-tuning.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#虚拟线程` `#并发` `#Java21` `#Loom` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

- 说清虚拟线程、载体线程、调度器三者的关系
- 理解"一请求一线程"为何重新变得可行
- 在 Spring Boot 3 中正确启用，并识别 Pinning 场景

## 🔍 一、旧模型的经济学危机

平台线程（`Thread`）是 1:1 映射到 OS 线程的：每个线程约 1MB 栈内存 + 内核调度成本。

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

- **虚拟线程**：JVM 管理的轻量执行单元，栈帧存于堆，创建成本约几百字节
- **载体线程（Carrier）**：真正跑在 CPU 上的平台线程，由内部 `ForkJoinPool`（FIFO 模式）调度
- **挂载/卸载**：虚拟线程调用阻塞 API（如 Socket 读）时，JVM 把它的栈从载体上"卸下"保存到堆，载体立即执行其他虚拟线程——**阻塞不再占用 OS 线程**

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
// 10 万并发任务轻松创建；同代码在平台线程模型下需要 10 万 OS 线程
```

写同步代码，获得异步扩展性——**这是 Loom 项目的全部野心**。

## 🛠️ 三、Spring Boot 3 中的启用

```yaml
# 一行配置：Tomcat/Jetty 改用虚拟线程处理请求
spring:
  threads:
    virtual:
      enabled: true
```

生效后：每个 HTTP 请求由一个虚拟线程处理；`@Async`、`@Scheduled` 也自动切换。**前提**：Java 21 + Boot 3.2+。

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

**检测**：`-Djdk.tracePinnedThreads=full` 打印钉死现场；或监控 `jdk.VirtualThreadPinned` 事件。

### 其他纪律

1. **不要池化虚拟线程**——它们廉价到"用完即弃"，池化反而引入排队瓶颈
2. **ThreadLocal 谨慎用**——百万线程 × 大对象 = 堆膨胀；跨线程共享数据用 `ScopedValue`（预览演进中）
3. **CPU 密集任务无收益**——瓶颈在核数，虚拟线程只解放"等待"
4. **信号量做并发闸门**——限流下游用 `Semaphore.acquire()`（会卸载），而非限制线程数

## 🔍 五、与响应式的关系

| 维度 | 虚拟线程 | Reactor/WebFlux |
|------|---------|-----------------|
| 编程模型 | 同步直白 | 回调/操作符链 |
| 扩展上限 | 很高（百万级阻塞 IO） | 更高（单线程处理海量连接） |
| 生态成本 | 零（现有代码直接跑） | 全链路响应式库 |
| 适用 | 绝大多数 IO 服务 | 极端连接密度、流处理 |

实践建议：默认虚拟线程 + 传统栈；确有极端吞吐需求再局部引入响应式——两者可共存。

## 🔗 相关文档

### 本模块
- 📖 [并发 API 速查](../../reference/language-concepts/04-concurrency-api.md) — 全量并发 API 条目
- 📖 [现代 Java 特性](../../basics/07-modern-features.md) — 虚拟线程入门章节
- 📄 [JVM 调优与 GC 基础](./01-jvm-tuning.md) — 线程栈内存模型的另一面
- 📄 [K8s 部署](../../deployment/02-kubernetes-deployment.md) — 虚拟线程时代的容器内存评估
- 📄 [生产级 Spring Boot 应用](../../projects/04-production-spring-app.md) — 并发闸门与容量保护
