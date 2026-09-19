# CI/CD 流水线 - Go应用自动化部署

> **文档简介**: Go应用CI/CD流水线完整指南，涵盖GitHub Actions、自动化测试、部署策略等现代DevOps实践

> **目标读者**: Go开发者，需要建立完整CI/CD流程的开发者

> **前置知识**: Go基础开发、Docker基础、Git基础

> **预计时长**: 6-8小时完整学习

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `deployment/devops` |
| **难度** | ⭐⭐⭐ (精通)|
| **标签** | `#CI/CD` `#GitHub Actions` `#自动化部署` `#DevOps` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 🎯 学习目标

### 核心技能
- **CI/CD概念**: 理解持续集成、持续部署的核心原理
- **GitHub Actions**: 能说明工作流由什么事件触发、各作业在哪里运行、失败如何阻止后续步骤；修改一项断言使测试失败，确认失败状态确实反映在提交检查中。
- **自动化测试**: 集成测试、性能测试的自动化执行
- **部署策略**: 多环境部署、蓝绿部署、金丝雀发布

### 实践能力
- **流水线设计**: 根据项目需求设计CI/CD流水线
- **质量门禁**: 建立代码质量检查和安全扫描
- **监控集成**: 部署后监控和告警配置
- **回滚机制**: 建立快速回滚和故障恢复机制

## 📖 CI/CD基础概念

### 持续集成 (Continuous Integration)
```yaml
# 自动触发条件
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

# 并行执行任务
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        go-version: ['1.25', '1.26']
```

### 持续部署 (Continuous Deployment)
```yaml
# 部署到不同环境
deploy:
  needs: test
  runs-on: ubuntu-latest
  strategy:
    matrix:
      environment: [staging, production]
```

## 🛠️ GitHub Actions 工作流

### 基础Go CI工作流
```yaml
# .github/workflows/ci.yml
name: Go CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Setup Go
      uses: actions/setup-go@v4
      with:
        go-version: '1.25'

    - name: Cache Go modules
      uses: actions/cache@v3
      with:
        path: ~/go/pkg/mod
        key: ${{ runner.os }}-go-${{ hashFiles('**/go.sum') }}
        restore-keys: |
          ${{ runner.os }}-go-

    - name: Download dependencies
      run: go mod download

    - name: Run tests
      run: go test -v -race -coverprofile=coverage.out ./...

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.out
```

### 完整的CI/CD流水线
```yaml
# .github/workflows/complete-ci-cd.yml
name: Complete CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
    tags: [ 'v*.*.*' ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # 代码质量检查
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Setup Go
      uses: actions/setup-go@v4
      with:
        go-version: '1.25'
    - name: Run golangci-lint
      uses: golangci/golangci-lint-action@v3
      with:
        version: latest
        args: --timeout=5m

  # 安全扫描
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run Gosec Security Scanner
      uses: securecodewarrior/github-action-gosec@master
      with:
        args: '-fmt sarif -out gosec.sarif ./...'
    - name: Upload SARIF file
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: gosec.sarif

  # 测试
  test:
    name: Test
    runs-on: ubuntu-latest
    needs: [lint]

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v4
    - name: Setup Go
      uses: actions/setup-go@v4
      with:
        go-version: '1.25'

    - name: Cache Go modules
      uses: actions/cache@v3
      with:
        path: |
          ~/.cache/go-build
          ~/go/pkg/mod
        key: ${{ runner.os }}-go-${{ hashFiles('**/go.sum') }}
        restore-keys: |
          ${{ runner.os }}-go-

    - name: Download dependencies
      run: go mod download

    - name: Run unit tests
      run: go test -v -race -coverprofile=coverage.out ./...
      env:
        DB_HOST: localhost
        DB_PORT: 5432
        DB_NAME: testdb
        DB_USER: postgres
        DB_PASSWORD: postgres
        REDIS_HOST: localhost
        REDIS_PORT: 6379

    - name: Run integration tests
      run: go test -v -tags=integration ./...

    - name: Run benchmark tests
      run: go test -bench=. -benchmem ./...

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3

  # 构建Docker镜像
  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.event_name == 'push'

    steps:
    - uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}

    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  # 部署到Staging
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [build]
    if: github.ref == 'refs/heads/develop'
    environment: staging

    steps:
    - uses: actions/checkout@v4

    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment..."
        # 这里添加实际的部署脚本
        # 例如: kubectl apply -f k8s/staging/

    - name: Run smoke tests
      run: |
        echo "Running smoke tests..."
        # 运行冒烟测试

  # 部署到Production
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [build]
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
    - uses: actions/checkout@v4

    - name: Deploy to production
      run: |
        echo "Deploying to production environment..."
        # 这里添加实际的部署脚本

    - name: Health check
      run: |
        echo "Performing health check..."
        # 健康检查

    - name: Notify team
      if: always()
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        channel: '#deployments'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## 🚀 部署策略

### 蓝绿部署
```yaml
# 蓝绿部署脚本示例
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: go-app-rollout
spec:
  replicas: 3
  strategy:
    blueGreen:
      activeService: go-app-active
      previewService: go-app-preview
      autoPromotionEnabled: false
      scaleDownDelaySeconds: 30
      prePromotionAnalysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: go-app-preview
      postPromotionAnalysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: go-app-active
  selector:
    matchLabels:
      app: go-app
  template:
    metadata:
      labels:
        app: go-app
    spec:
      containers:
      - name: go-app
        image: go-app:latest
        ports:
        - containerPort: 8080
```

### 金丝雀发布
```yaml
# 金丝雀发布配置
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: go-app-canary
spec:
  replicas: 5
  strategy:
    canary:
      steps:
      - setWeight: 20
      - pause: {duration: 10m}
      - setWeight: 40
      - pause: {duration: 10m}
      - setWeight: 60
      - pause: {duration: 10m}
      - setWeight: 80
      - pause: {duration: 10m}
      canaryService: go-app-canary
      stableService: go-app-stable
      trafficRouting:
        istio:
          virtualService:
            name: go-app-vsvc
            routes:
            - primary
```

## 📊 监控和告警

### Prometheus监控配置
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'go-app'
    static_configs:
      - targets: ['app:8080']
    metrics_path: /metrics
    scrape_interval: 5s

rule_files:
  - "go-app-alerts.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### 告警规则
```yaml
# go-app-alerts.yml
groups:
- name: go-app-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second"

  - alert: HighMemoryUsage
    expr: (go_memstats_heap_inuse_bytes / go_memstats_heap_sys_bytes) > 0.9
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage"
      description: "Memory usage is {{ $value | humanizePercentage }}"

  - alert: ApplicationDown
    expr: up{job="go-app"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Application is down"
      description: "Go app has been down for more than 1 minute"
```

## 🔧 环境配置

### 多环境配置
```yaml
# docker-compose.override.yml (development)
version: '3.8'
services:
  app:
    build:
      context: .
      target: development
    volumes:
      - .:/app
      - /app/vendor
    environment:
      - GIN_MODE=debug
      - LOG_LEVEL=debug
    command: air -c .air.toml

  db:
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=devdb

# docker-compose.staging.yml (staging)
version: '3.8'
services:
  app:
    image: go-app:staging
    environment:
      - GIN_MODE=release
      - LOG_LEVEL=info
    deploy:
      replicas: 2

# docker-compose.prod.yml (production)
version: '3.8'
services:
  app:
    image: go-app:latest
    environment:
      - GIN_MODE=release
      - LOG_LEVEL=warn
    deploy:
      replicas: 5
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

### Kubernetes配置
```yaml
# k8s/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: go-app
  labels:
    app: go-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: go-app
  template:
    metadata:
      labels:
        app: go-app
    spec:
      containers:
      - name: go-app
        image: go-app:latest
        ports:
        - containerPort: 8080
        env:
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: db-host
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: db-password
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: go-app-service
spec:
  selector:
    app: go-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: ClusterIP
```

## 🎯 最佳实践

### 1. 流水线设计原则

先把任务按“是否需要前一步产物”画出依赖：格式/静态检查与单元测试可独立执行，发布必须等待必需检查和构建通过。5 分钟可以是团队的反馈目标，不是所有项目的正确性标准；先测实际耗时，再把慢的外部服务测试拆到合适阶段。

最小故障演练是提交一个确定失败的断言，确认测试 job 变红、发布 job 不执行、失败日志仍可下载。独立文档检查不应因为代码编译失败而被跳过；收集日志的步骤可使用 `if: always()`，但不能用 `continue-on-error` 把必需测试失败变成通过。命令经过 `tee` 时启用 `pipefail`，避免只保留最后一个命令的退出状态。

### 2. 安全实践

当流水线开始接触镜像仓库、部署密钥或云账号时，先列出每个 job 需要读取/写入什么，再配置最小权限。来自外部贡献的代码只运行不含部署凭证的检查；部署放到受保护环境，并采用短时凭证或明确的密钥管理流程。

依赖和镜像扫描的意义是给出受影响版本、利用条件、修复版本及处置优先级。选择维护中的扫描工具，把 Actions 固定到经过审查的版本或提交，不要复制 `@master` 作为长期基线。报告上传失败和“扫描发现漏洞”是两种问题，都要可追踪；报告可下载并不表示发布已经安全。

**验收：** 用无生产权限的演练环境确认普通检查拿不到部署密钥；选一条扫描结果复查依赖来源与修复版本。例外必须注明原因、责任人和复核日期，不能整类永久忽略。

### 3. 性能优化

优先缓存可重建的依赖下载和编译结果，缓存键覆盖操作系统、工具链和依赖锁文件；有 go.sum 的 Go 模块可由 setup-go 管理缓存，仅标准库的小工具没有 go.sum 时不要强行启用模块缓存。冷缓存仍必须能成功构建，缓存是加速器，不是缺失依赖的补丁。

先比较一次冷构建与一次热构建的耗时。不要把 `go build -a` 当作加速选项，它会强制重建已有包；`-ldflags='-s -w'` 主要影响符号/调试信息与产物大小，不能承诺运行更快。只有依赖确实不需要 cgo 时才设置 `CGO_ENABLED=0`，跨平台和静态链接另行验证。

**验收：** 清空缓存后流水线仍通过；恢复缓存后的二进制运行同一组测试；记录时间和产物大小的变化。并行化时检查 CPU/内存是否被争抢，避免每个 job 更慢却误以为总吞吐提高。

### 4. 监控和日志

下面是已有 Gin/Prometheus 项目中的中间件片段，计数器与直方图需要先定义和注册。标签使用路由模板（如 `/users/:id`），不使用每个用户的原始 URL，以免产生无限增长的时间序列。未匹配路由统一为固定标签。验收时请求两个不同用户 ID，确认它们落在同一路由指标，并用一次失败请求核对状态码计数。

```go
// 应用监控中间件
func MonitoringMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()

        c.Next()

        duration := time.Since(start)
        status := c.Writer.Status()

        route := c.FullPath()
        if route == "" {
            route = "unmatched"
        }

        // Prometheus metrics
        httpRequestsTotal.WithLabelValues(
            c.Request.Method,
            route,
            fmt.Sprintf("%d", status),
        ).Inc()

        httpRequestDuration.WithLabelValues(
            c.Request.Method,
            route,
        ).Observe(duration.Seconds())
    }
}
```

## 🔄 文档交叉引用

### 相关文档
- 📄 **[Docker容器化]**: [deployment/01-containerization.md](01-containerization.md) - Docker容器化部署
- 📄 **[Kubernetes部署]**: [deployment/03-kubernetes-deployment.md](03-kubernetes-deployment.md) - K8s部署配置
- 📄 **[监控可观测性]**: [deployment/04-observability.md](04-observability.md) - 应用监控配置

### 参考章节
- 📖 **[单元测试]**: [testing/01-unit-testing.md](../testing/01-unit-testing.md) - 测试驱动开发
- 📖 **[微服务架构]**: [advanced-topics/architecture/01-microservices-design.md](../advanced-topics/architecture/01-microservices-design.md) - 微服务设计模式

## 📝 总结

### 核心要点回顾
1. **CI/CD基础**: 理解持续集成和持续部署的核心概念
2. **GitHub Actions**: 掌握工作流配置和自动化流程
3. **部署策略**: 了解蓝绿部署、金丝雀发布等策略
4. **监控告警**: 建立完整的监控和告警体系

### 学习成果检查
- [ ] 是否理解CI/CD的核心原理？
- [ ] 是否能够配置GitHub Actions工作流？
- [ ] 是否掌握不同的部署策略？
- [ ] 是否能够建立监控告警体系？

---

**文档状态**: ✅ 已完成
**最后更新**: 2026年9月
**版本**: v1.0.0

---

> 💡 **实践建议**:
> - 建立完善的测试体系，确保代码质量
> - 使用基础设施即代码管理部署配置
> - 建立监控告警体系，及时发现问题
> - 定期演练故障恢复流程，确保系统可靠性

<!-- acceptance-exercise -->
## 练习与验收：用失败提交检验发布门禁

在练习分支给已有业务测试改一个错误预期，提交后检查 test job 失败，镜像发布和部署步骤没有启动。恢复断言后重跑，记录 commit SHA、镜像 digest 与部署使用的 digest。再从已知好版本做一次测试环境回退。验收：坏提交确实被拦截、好提交的产物可追溯，回退后健康检查与一条真实业务请求都成功；仅 workflow 显示绿色不够。

以上是在个人或隔离测试环境中的练习，不是本轮已执行记录；实际运行范围见仓库文档质量报告。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
