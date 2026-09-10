# CI/CD 与可观测性 - GitHub Actions 与 Actuator/Prometheus/Grafana

> **文档简介**: 打通从代码合入到线上监控的闭环：GitHub Actions 流水线（测试→镜像→部署），Actuator 指标接入 Prometheus，Grafana 看板与告警规则
>
> **目标读者**: 准备为 Spring Boot 服务搭建自动化交付与监控的开发者
>
> **前置知识**: 已完成 [K8s 部署](./02-kubernetes-deployment.md)；Actuator 端点见 [开发工具链](../frameworks/04-devtools.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#GitHubActions` `#Prometheus` `#Grafana` `#可观测性` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：
- 编写"测试 → 构建镜像 → 部署"的完整 GitHub Actions 流水线
- 暴露 Micrometer 指标给 Prometheus 抓取
- 在 Grafana 建立面向 SLO 的看板与告警

## 🛠️ 一、GitHub Actions 流水线

```yaml
# .github/workflows/ci.yml
name: build-and-deploy
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 21, cache: maven }
      - name: 单元 + 集成测试
        run: mvn -B verify                # 集成测试由 Testcontainers 驱动
      - uses: actions/upload-artifact@v4
        if: always()
        with: { name: test-reports, path: target/surefire-reports/ }

  image:
    needs: test
    runs-on: ubuntu-latest
    permissions: { contents: read, packages: write }
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:${{ github.sha }}
            ghcr.io/${{ github.repository }}:latest

  deploy:
    needs: image
    runs-on: ubuntu-latest
    environment: production                # 环境级审批门禁
    steps:
      - uses: actions/checkout@v4
      - name: 滚动更新
        run: |
          kubectl set image deployment/todo-api \
            app=ghcr.io/${{ github.repository }}:${{ github.sha }}
          kubectl rollout status deployment/todo-api --timeout=180s
```

**流水线纪律**：测试不过不构建；镜像 tag = commit SHA；部署前留人工审批（`environment` 门禁）。

## 🛠️ 二、指标暴露：Micrometer + Prometheus

### 应用侧

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,prometheus
  metrics:
    tags:
      application: ${spring.application.name}   # 全局标签：多服务区分
```

`/actuator/prometheus` 输出 OpenMetrics 文本：JVM 内存、GC、HTTP 请求直方图、Hikari 连接池全都在。

### Prometheus 侧

```yaml
# prometheus.yml 抓取配置
scrape_configs:
  - job_name: spring-boot
    metrics_path: /actuator/prometheus
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        target_label: application
```

## 🛠️ 三、Grafana 看板与告警

### 面向 SLO 的四象限看板

| 区域 | 指标（PromQL） | 回答的问题 |
|------|---------------|-----------|
| 流量 | `sum(rate(http_server_requests_seconds_count[5m]))` | 现在多忙 |
| 延迟 | `histogram_quantile(0.99, rate(http_server_requests_seconds_bucket[5m]))` | P99 多慢 |
| 错误 | `sum(rate(http_server_requests_seconds_count{status=~"5.."}[5m]))` | 挂了多少 |
| 饱和 | `jvm_memory_used_bytes{area="heap"}` / Hikari 活跃连接 | 还有多少余量 |

### 告警规则（Alertmanager）

```yaml
groups:
  - name: todo-api
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_server_requests_seconds_count{status=~"5..", application="todo-api"}[5m]))
            / sum(rate(http_server_requests_seconds_count{application="todo-api"}[5m])) > 0.01
        for: 5m
        labels: { severity: critical }
        annotations:
          summary: "todo-api 5xx 错误率超过 1%"
      - alert: GCPauseSpike
        expr: rate(jvm_gc_pause_seconds_sum[5m]) > 0.5
        for: 10m
        labels: { severity: warning }
        annotations:
          summary: "GC 时间占比异常，检查堆配置"
```

告警三原则：每条都可行动（收到知道干什么）、基于症状（5xx 率）而非原因（CPU）、带 runbook 链接。

## ❓ 常见问题

### Q1: 指标基数爆炸（cardinality explosion）？

自定义指标 tag 不要放 userId/orderId 这类高基数值——Prometheus 内存会爆。业务定位需求交给日志/追踪。

### Q2: CI 里集成测试跑不起来？

Runner 自带 Docker 即可用 Testcontainers；私服镜像需 `docker login`。构建缓存用 `setup-java` 的 `cache: maven`。

### Q3: 追踪（Tracing）接哪里？

Micrometer Tracing + OTLP 导出到 Jaeger/Tempo，traceId 自动进 MDC 日志（配置见 [生产级应用](../projects/04-production-spring-app.md)）。

## 🎨 最佳实践

### ✅ 推荐
- 流水线每个 job 单一职责：test / image / deploy 各自可重跑
- 指标带上 `application` 全局标签，看板一套模板多服务复用
- 核心接口必有 P99 延迟与错误率双指标

### ❌ 陷阱
- 告警只发不治：阈值一刀切导致狼来了效应
- 部署后无验证：加一步 `kubectl rollout status` + 健康检查冒烟
- 密钥写在 workflow YAML：一律走 `secrets.*`

## 🔗 相关文档

### 本模块
- 📖 [Spring Boot 核心速查](../reference/framework-essentials/01-spring-boot-essentials.md) — Actuator 完整端点
- 📖 [第三方库指南](../reference/library-guides/02-third-party-libs.md) — Micrometer 生态
- 📄 [开发工具链](../frameworks/04-devtools.md) — Actuator 基础
- 📄 [Docker 部署](./01-docker-deployment.md) — 流水线的构建输入
- 📄 [K8s 部署](./02-kubernetes-deployment.md) — 部署目标环境
- 📄 [生产级 Spring Boot 应用](../projects/04-production-spring-app.md) — 三支柱应用侧配置
