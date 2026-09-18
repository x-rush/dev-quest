# Kubernetes 部署 - Java 应用编排概览

> **文档简介**: 把容器化的 Spring Boot 应用放上 Kubernetes：Deployment/Service 三件套、健康探针与优雅停机、资源配置与 HPA 扩缩容
>
> **目标读者**: 已能构建镜像、需要理解 Java 应用在 K8s 上正确姿势的开发者
>
> **前置知识**: 已完成 [Docker 部署](./01-docker-deployment.md)；Actuator 探针见 [开发工具链](../frameworks/04-devtools.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#Kubernetes` `#探针` `#HPA` `#滚动更新` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：
- 编写 Java 应用标准的 Deployment + Service 清单
- 配置 liveness/readiness/startup 探针，理解三者差异
- 设置 requests/limits 与 HPA，让 JVM 与 K8s 协同扩缩

## 🛠️ 一、最小可用编排清单

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-api
spec:
  replicas: 3
  selector:
    matchLabels: { app: todo-api }
  strategy:
    rollingUpdate: { maxUnavailable: 0, maxSurge: 1 }  # 先起新再停旧，零中断
  template:
    metadata:
      labels: { app: todo-api }
    spec:
      containers:
        - name: app
          image: registry.example.com/todo-api:1.0.0   # 固定版本 tag
          ports: [{ containerPort: 8080 }]
          env:
            - name: DB_PASSWORD                        # 敏感项来自 Secret
              valueFrom:
                secretKeyRef: { name: todo-db, key: password }
          resources:
            requests: { cpu: 500m, memory: 512Mi }     # 调度依据 + 堆比例基准
            limits:   { cpu: "2",  memory: 1Gi }
          startupProbe:                                # Java 慢启动专用
            httpGet: { path: /actuator/health/liveness, port: 8080 }
            failureThreshold: 30
            periodSeconds: 2
          livenessProbe:
            httpGet: { path: /actuator/health/liveness, port: 8080 }
            periodSeconds: 10
          readinessProbe:
            httpGet: { path: /actuator/health/readiness, port: 8080 }
            periodSeconds: 5
          lifecycle:
            preStop:
              exec: { command: ["sh", "-c", "sleep 5"] }  # 等负载均衡摘流
---
apiVersion: v1
kind: Service
metadata:
  name: todo-api
spec:
  selector: { app: todo-api }
  ports: [{ port: 80, targetPort: 8080 }]
```

## 🛠️ 二、三种探针：Java 场景的正确用法

| 探针 | 失败动作 | Java 应用要点 |
|------|---------|--------------|
| **startupProbe** | 杀容器重启前允许长启动 | Spring Boot 冷启动可达数十秒，必须配置，否则 liveness 误杀 |
| **livenessProbe** | 重启容器 | 只检查"进程死锁/死循环"，**不要**检查下游依赖 |
| **readinessProbe** | 摘出 Service 负载均衡 | 检查"能否服务流量"，数据库断连时可置 not-ready |

```yaml
# Actuator 已内置 K8s 探针端点（需启用）
management:
  endpoint:
    health:
      probes:
        enabled: true
```

## 🛠️ 三、优雅停机：滚动更新零 5xx 的配方

1. **应用侧**：`server.shutdown: graceful` + `spring.lifecycle.timeout-per-shutdown-phase: 30s`
2. **K8s 侧**：`preStop` 睡 5 秒——新配置尚未传播完的请求落在已摘流的 Pod 上
3. **terminationGracePeriodSeconds**：默认 30s，若优雅停机需 40s 必须调大

验证方法：滚动更新期间压测，断言 5xx 为零（见 [生产级应用](../projects/04-production-spring-app.md)）。

## 🛠️ 四、资源与扩缩容

### requests/limits 与 JVM 的关系

```text
容器 memory limit 1Gi
└── -XX:MaxRAMPercentage=75 → 堆上限约 768Mi
    └── 留 256Mi 给元空间、线程栈、直接内存、G1 开销
```

CPU limit 过低会引发 GC 停顿拉长（GC 线程被限流），Java 服务建议 **CPU limit ≥ requests 的 2 倍或直接不设 limit**。

### HPA 自动扩缩

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: todo-api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: todo-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: memory
        target: { type: Utilization, averageUtilization: 70 }
```

> 生产建议叠加业务指标（如 HTTP RPS，经 Prometheus Adapter 暴露）而非只用资源指标。

## ❓ 常见问题

### Q1: Pod 反复重启（CrashLoopBackOff）？

先看 `kubectl logs --previous`：常见原因是探针路径 404（未启用 probes 端点）、数据库密码未注入、内存 OOMKilled（limits 太小）。

### Q2: OOMKilled 但堆没满？

容器里不止堆：元空间、线程栈、直接内存、JIT 代码缓存都计入 limit。虚拟线程大开时线程栈增长更快，详见 [虚拟线程并发模型](../advanced-topics/performance/02-virtual-threads.md)。

### Q3: 本地怎么调试 K8s 清单？

`kubectl apply --dry-run=client -f k8s/` 校验语法；`kustomize`/`Helm` 管理环境差异不在本文展开。

## 🎨 最佳实践

readiness 决定是否接收流量，liveness 用于判断是否需要重启，startup 给慢启动留出初始化窗口。若 liveness 直接依赖数据库，数据库故障可能触发全体应用反复重启；应先定义故障应由哪一层恢复。

发布固定产物并验证就绪与核心接口，回滚镜像不自动回滚数据库或外部状态。资源配额从实际负载测量，过紧的 CPU/内存限制可能增加延迟。练习让下游暂时不可用，观察系统是否停止接流量而非无休止重启。

## 🚀 下一步

- 流水线与监控 → [CI/CD 与可观测性](./03-ci-cd-observability.md)

## 🔗 相关文档

### 本模块
- 📖 [Spring Boot 核心速查](../reference/framework-essentials/01-spring-boot-essentials.md) — Actuator 端点清单
- 📖 [JVM 调优与 GC 基础](../advanced-topics/performance/01-jvm-tuning.md) — 容器内存参数依据
- 📄 [Docker 部署](./01-docker-deployment.md) — 本文的镜像来源
- 📄 [CI/CD 与可观测性](./03-ci-cd-observability.md) — 部署自动化
- 📄 [生产级 Spring Boot 应用](../projects/04-production-spring-app.md) — 综合演练


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
