# 项目实战 04 - 生产级 Spring Boot 应用

> **文档简介**: 毕业项目：把一个 Spring Boot 应用推向生产——配置管理与密钥安全、结构化日志与三支柱可观测性、优雅停机与容量保护、CI/CD 与灰度发布，形成完整的生产交付清单
>
> **目标读者**: 已完成前三个项目、准备负责真实线上服务的开发者
>
> **前置知识**: 已完成 [订单系统](./03-order-system.md)、[Docker 部署](../deployment/01-docker-deployment.md)、[CI/CD 与可观测性](../deployment/03-ci-cd-observability.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#生产化` `#可观测性` `#配置管理` `#容量保护` |
| **更新日期** | `2026年9月` |

## 🎯 项目目标

把 [订单系统](./03-order-system.md) 升级为生产可运营的服务：

- 配置：多环境 profile + 环境变量注入密钥，零硬编码
- 可观测：结构化日志、指标、链路追踪三支柱齐全
- 稳定性：优雅停机、超时重试、限流降级
- 交付：流水线自动化 + 滚动发布 + 回滚预案

## 🛠️ 一、配置管理与密钥安全

### 分层配置

```yaml
# application.yml —— 公共默认
spring:
  application:
    name: order-service

---
# application-prod.yml —— 生产差异项，密钥不落盘
spring:
  datasource:
    url: ${DB_URL}            # 环境变量注入
    username: ${DB_USER}
    password: ${DB_PASSWORD}  # 由 K8s Secret / Vault 提供
```

```bash
# 本地开发：.env 文件 + 启动脚本导出（.env 必须进 .gitignore）
export DB_PASSWORD=$(cat ./secrets/db_password)
```

**原则**：配置分三类——代码内置默认值（低风险）、配置文件（环境差异）、环境变量/密钥系统（敏感项）。生产任何凭据都不进 Git。

## 🛠️ 二、可观测性三支柱

### 1. 结构化日志

```xml
<!-- logback-spring.xml 关键片段：JSON 格式便于采集解析 -->
<appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
    <encoder class="net.logstash.logback.encoder.LogstashEncoder">
        <customFields>{"service":"order-service"}</customFields>
    </encoder>
</appender>
```

```java
// 面向问题域打日志：带业务键，够定位、不打全量对象
log.info("order placed, orderId={}, userId={}, amount={}",
        order.getId(), order.getUserId(), order.getAmount());
```

### 2. 指标（Micrometer + Prometheus）

```java
@Service
public class OrderMetrics {

    private final Counter placedCounter;
    private final Timer placeTimer;

    public OrderMetrics(MeterRegistry registry) {
        placedCounter = Counter.builder("order.placed.total")
                .tag("channel", "web").register(registry);
        placeTimer = registry.timer("order.place.duration");
    }

    public Order place(Long userId, Long productId, int qty) {
        return placeTimer.record(() -> {
            placedCounter.increment();
            return doPlace(userId, productId, qty);
        });
    }
}
```

### 3. 链路追踪

```xml
<!-- Micrometer Tracing + OTLP 导出：依赖引入即生效 -->
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-bridge-otel</artifactId>
</dependency>
<dependency>
    <groupId>io.opentelemetry</groupId>
    <artifactId>opentelemetry-exporter-otlp</artifactId>
</dependency>
```

traceId 自动注入 MDC，日志与追踪一键互查。完整管线见 [CI/CD 与可观测性](../deployment/03-ci-cd-observability.md)。

## 🛠️ 三、稳定性工程

### 优雅停机

```yaml
server:
  shutdown: graceful          # 接到 SIGTERM 先停止接收新请求
spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```

K8s 侧配合 `preStop` 睡眠数秒，等负载均衡摘流（见 [K8s 部署](../deployment/02-kubernetes-deployment.md)）。

### 客户端防护：超时 + 重试 + 熔断

```java
// Resilience4j：第三方调用必须有边界
@CircuitBreaker(name = "payment", fallbackMethod = "payFallback")
@Retry(name = "payment")
@TimeLimiter(name = "payment")
public CompletableFuture<PaymentResult> pay(PaymentRequest req) {
    return CompletableFuture.supplyAsync(() -> paymentClient.call(req));
}

// 降级：记录并进入补偿队列，而非让用户看到 500
CompletableFuture<PaymentResult> payFallback(PaymentRequest req, Throwable t) {
    compensationQueue.enqueue(req);
    return CompletableFuture.completedFuture(PaymentResult.pending(req.orderId()));
}
```

### 自我保护：容量三件套

| 手段 | 配置点 | 目的 |
|------|--------|------|
| 连接池上限 | `hikari.maximum-pool-size` | 数据库不被打爆 |
| 线程池隔离 | 自定义 `ThreadPoolTaskExecutor` | 慢调用不占满主线程 |
| 接口限流 | Bucket4j / Resilience4j RateLimiter | 削峰、防刷 |

## 🛠️ 四、交付：流水线与发布

```yaml
# GitHub Actions 生产发布（节选）
jobs:
  deploy:
    needs: build   # build：测试 + 镜像推送（见 deployment/03）
    runs-on: ubuntu-latest
    steps:
      - uses: azure/k8s-deploy@v5
        with:
          strategy: rolling       # 滚动发布，保留上一版本快速回滚
          images: registry.example.com/order-service:${{ github.sha }}
          manifests: k8s/
```

**发布纪律**：
- 镜像 tag 用 commit SHA，禁止 `latest`
- 数据库变更向后兼容（先加列后删列，双写过渡）
- 每次发布前确认回滚命令一条可执行

## ✅ 生产就绪检查清单

- [ ] 敏感配置全部走环境变量/Secret，`git grep` 无明文密钥
- [ ] `/actuator/health` 分 liveness/readiness，并接入自定义依赖检查
- [ ] 日志 JSON 化且带 traceId，能按 orderId 串起全链路
- [ ] 核心业务有指标与告警（错误率、P99 延迟）
- [ ] 所有出站调用有超时，关键路径有熔断降级
- [ ] 优雅停机验证过：滚动更新期间零 5xx
- [ ] 压测过目标容量，连接池/线程池有依据
- [ ] 回滚演练至少一次

## 🎨 最佳实践

### ✅ 推荐
- 可观测性从第一天就有，而不是"上线后补"
- 降级路径必须真实演练（拔掉下游再压测）
- 配置变更走流水线，禁止生产机器手改

### ❌ 陷阱
- 重试没有退避与上限 → 故障放大（雪崩）
- 只监控 JVM 指标不看业务指标：JVM 全绿但订单都在失败
- 日志打敏感字段（手机号、token）违反合规

## 🔗 相关文档

### 本模块
- 📖 [Spring Boot 核心速查](../reference/framework-essentials/01-spring-boot-essentials.md) — Actuator 与配置绑定
- 📖 [JVM 调优与 GC 基础](../advanced-topics/performance/01-jvm-tuning.md) — 容器内存参数依据
- 📄 [Docker 部署](../deployment/01-docker-deployment.md) — 镜像构建
- 📄 [K8s 部署](../deployment/02-kubernetes-deployment.md) — 编排与探针
- 📄 [CI/CD 与可观测性](../deployment/03-ci-cd-observability.md) — 流水线与监控栈
- 📄 [分层与六边形架构](../advanced-topics/architecture/01-layered-architecture.md) — 演进式架构治理
