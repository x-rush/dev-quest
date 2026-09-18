# JVM 调优与 GC 基础

> **文档简介**: 从内存模型出发理解 JVM 调优：堆/非堆区域的职责分界、G1/ZGC 的取舍、容器环境参数依据，以及一套"先测量后动手"的调优方法论
>
> **目标读者**: 服务已上线但延迟/内存表现不理想，需要定位与调优的开发者
>
> **前置知识**: 已完成 [Docker 部署](../../deployment/01-docker-deployment.md)；并发背景见 [并发 API 速查](../../reference/language-concepts/04-concurrency-api.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#JVM` `#GC` `#G1` `#ZGC` `#调优` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

- 画出 Java 21 运行时内存分界图，说清每块区域装什么
- 理解 G1 与 ZGC 的设计取舍与适用边界
- 掌握"指标 → 假设 → 单变量实验"的调优流程

## 🔍 一、运行时内存地图

```text
进程内存（容器 limit 必须覆盖全部）
├── 堆（-Xmx / MaxRAMPercentage）
│   ├── Young Gen: Eden + Survivor*2    短命对象，Minor GC 频繁
│   └── Old Gen:                        长命对象，Mixed/Full GC
├── 元空间（Metaspace）                 类元数据，随类加载数增长
├── 线程栈（-Xss，默认 1MB/线程）        虚拟线程不占此区（见虚拟线程专题）
├── 直接内存（NIO ByteBuffer 等）
└── JIT 代码缓存
```

**容器 OOM 的常见真相**：堆没满但进程总内存超过容器 limit → 内核 OOMKilled。这就是 [K8s 部署](../../deployment/02-kubernetes-deployment.md) 用 `MaxRAMPercentage=75` 而非 `-Xmx=limit` 的原因。

## 🔍 二、GC 演进到 G1

### G1（JDK 9+ 默认）：面向停顿目标

- 堆被切成约 2048 个 Region，收集收益最高的区域优先（Garbage First 之名由来）
- 软实时目标：`-XX:MaxGCPauseMillis=200`（默认 200ms）
- 混合回收逐步清理老年代，避免单次全堆停顿

### ZGC（JDK 15 转正；Java 21 引入分代模式）：停顿不随堆增长

- 着色指针 + 读屏障实现并发整理，停顿亚毫秒级且**与堆大小无关**
- 代价：吞吐略降（约 5-10%）、内存占用略高

### 选型决策

| 场景 | 推荐 |
|------|------|
| 通用 Web 服务（堆 < 8G） | G1（默认，最稳） |
| 超大堆（16G+）且延迟敏感 | ZGC |
| 批处理、吞吐优先、停顿无所谓 | Parallel GC |

```bash
java -XX:+UseZGC -XX:MaxRAMPercentage=75 -jar app.jar
```

## 🛠️ 三、调优方法论：先测量，后动手

### 1. 拿到 GC 日志

```bash
java -Xlog:gc*:file=/logs/gc.log:time,uptime:filecount=5,filesize=20m -jar app.jar
```

关键指标：

- **停顿时间**：单次与 P99，是否逼近 SLO
- **频率**：Minor GC 过频 → 新生代太小或对象分配过猛
- **晋升速率**：对象过早进老年代 → 长命对象太多（缓存？）
- **Full GC**：出现即优先排查，通常是内存泄漏或元空间不足

### 2. 常见症状 → 假设 → 实验

| 症状 | 可能假设 | 单变量实验 |
|------|---------|-----------|
| Minor GC 每秒多次 | Eden 太小 | `-XX:G1NewSizePercent=30` 观察 |
| 老年代稳定增长不回落 | 泄漏 | 堆转储对比（见下） |
| 停顿偶发 > 1s | 大对象/晋升风暴 | `-XX:G1HeapRegionSize=16m` |
| 元空间告警 | 动态类生成（Groovy/CGLIB） | `-XX:MaxMetaspaceSize` 设上限并排查 |

### 3. 堆转储分析

```bash
jmap -dump:live,format=b,file=heap.hprof <pid>
# 或 OOM 时自动：-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/logs
```

用 Eclipse MAT 打开，看 **Dominator Tree** 找大对象持有者；两份时间间隔的 dump 做 diff，增长最快的类即泄漏嫌疑。

## 🛠️ 四、与 Spring Boot 的联动

```yaml
# 把 JVM 状态变成可观测指标（配合 deployment/03 的监控栈）
management:
  endpoints:
    web:
      exposure:
        include: prometheus
```

Grafana 重点看板：

- `jvm_gc_pause_seconds` P99 —— GC 是否侵蚀延迟预算
- `jvm_memory_used_bytes{area="heap"}` 锯齿形态 —— 回落是否正常
- `process_runtime_available_processors` —— 容器 CPU 配额是否被 JVM 正确感知

**调优顺序**：应用代码（对象分配率、缓存边界）→ 依赖配置（连接池大小）→ JVM 参数。参数是最后手段，不是第一反应。

## 🎨 最佳实践

调 JVM 前先区分堆耗尽、原生内存、线程和容器配额问题；只增加堆可能挤压其他内存。GC 日志与必要的堆转储能帮助定位，但转储可能很大且含敏感数据，需限制保存位置、容量和访问。

在可比负载下每次改变一个参数，观察吞吐、延迟与暂停分布。System.gc 是请求，实际行为依 GC 与配置而异，不应靠它定时“修复泄漏”。完成分析后找到对象为何仍被引用，而不是只把故障推迟。

## 🔗 相关文档

### 本模块
- 📖 [并发 API 速查](../../reference/language-concepts/04-concurrency-api.md) — 线程栈与并发模型
- 📖 [第三方库指南](../../reference/library-guides/02-third-party-libs.md) — MAT 等分析工具
- 📄 [Docker 部署](../../deployment/01-docker-deployment.md) — 容器内存参数落地
- 📄 [K8s 部署](../../deployment/02-kubernetes-deployment.md) — limits 与 JVM 协同
- 📄 [虚拟线程并发模型](./02-virtual-threads.md) — 内存模型的并发侧延伸


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
