# Go 应用 Kubernetes 部署指南

## 📚 概述

Kubernetes是现代云原生应用的事实标准，为Go应用提供了强大的编排和扩展能力。Go应用的二进制分发特性与Kubernetes的容器化理念完美契合，使Go成为Kubernetes环境下的理想选择。

### 🎯 学习目标
- 掌握Go应用在Kubernetes中的部署策略
- 学会配置资源管理和自动扩展
- 理解服务发现和负载均衡
- 掌握配置管理和密钥管理
- 学会监控和日志收集
- 理解Go在Kubernetes中的性能优化

## 🔄 Go vs PHP 在 Kubernetes 中的差异

### PHP Kubernetes 部署挑战
```yaml
# PHP应用Deployment (传统方式)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: php-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: php-app
  template:
    metadata:
      labels:
        app: php-app
    spec:
      containers:
      - name: php-app
        image: php:8.2-fpm
        resources:
          requests:
            memory: "256Mi"
            cpu: "500m"
          limits:
            memory: "512Mi"
            cpu: "1000m"
        # 需要共享文件卷
        volumeMounts:
        - name: app-code
          mountPath: /var/www/html
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
        volumeMounts:
        - name: app-code
          mountPath: /var/www/html
      volumes:
      - name: app-code
        persistentVolumeClaim:
          claimName: app-code-pvc
```

### Go Kubernetes 部署优势
```yaml
# Go应用Deployment (现代方式)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: go-app
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
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "500m"
        # 无需共享文件卷
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
```

## 📝 Kubernetes 基础部署

### 1. 基础 Deployment 配置

#### 简单 Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: go-web-app
  labels:
    app: go-web-app
    version: v1.0.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: go-web-app
  template:
    metadata:
      labels:
        app: go-web-app
        version: v1.0.0
    spec:
      containers:
      - name: go-web-app
        image: your-registry/go-web-app:v1.0.0
        ports:
        - containerPort: 8080
          name: http
        env:
        - name: APP_ENV
          value: "production"
        - name: APP_PORT
          value: "8080"
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 1
```

#### 带有数据库的 Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: go-api-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: go-api-app
  template:
    metadata:
      labels:
        app: go-api-app
    spec:
      containers:
      - name: go-api-app
        image: your-registry/go-api-app:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: redis-url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: jwt-secret
              key: secret
        resources:
          requests:
            memory: "128Mi"
            cpu: "200m"
          limits:
            memory: "256Mi"
            cpu: "1000m"
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
        - name: logs-volume
          mountPath: /app/logs
      volumes:
      - name: config-volume
        configMap:
          name: app-config
      - name: logs-volume
        emptyDir: {}
```

### 2. Service 配置

#### ClusterIP Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: go-app-service
  labels:
    app: go-app
spec:
  type: ClusterIP
  selector:
    app: go-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
    name: http
```

#### LoadBalancer Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: go-app-service
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: nlb
    service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
spec:
  type: LoadBalancer
  selector:
    app: go-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
    name: http
  - protocol: TCP
    port: 443
    targetPort: 8080
    name: https
```

#### NodePort Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: go-app-service
spec:
  type: NodePort
  selector:
    app: go-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
    nodePort: 30080
```

### 3. Ingress 配置

#### 基础 Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: go-app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: api-tls-secret
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: go-app-service
            port:
              number: 80
```

#### 带有路由的 Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: go-app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    nginx.ingress.kubernetes.io/use-regex: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: api-tls-secret
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /api/v1(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: go-app-service-v1
            port:
              number: 80
      - path: /api/v2(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: go-app-service-v2
            port:
              number: 80
```

## 📝 配置管理

### 1. ConfigMap

#### 配置文件 ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  config.yaml: |
    server:
      host: "0.0.0.0"
      port: 8080
      read_timeout: "30s"
      write_timeout: "30s"
      idle_timeout: "60s"

    database:
      host: "postgres-service"
      port: 5432
      name: "myapp"
      max_open_conns: 25
      max_idle_conns: 25
      conn_max_lifetime: "5m"

    redis:
      host: "redis-service"
      port: 6379
      password: ""
      db: 0

    logging:
      level: "info"
      format: "json"
      output: "stdout"

    monitoring:
      enabled: true
      port: 9090
      path: "/metrics"
```

#### 环境变量 ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-env-config
data:
  APP_ENV: "production"
  APP_PORT: "8080"
  LOG_LEVEL: "info"
  DB_HOST: "postgres-service"
  DB_PORT: "5432"
  DB_NAME: "myapp"
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
  METRICS_ENABLED: "true"
  METRICS_PORT: "9090"
```

### 2. Secret

#### 数据库 Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: cG9zdGdyZXM=  # base64: postgres
  password: eW91cl9zZWN1cmVfcGFzc3dvcmQ=  # base64: your_secure_password
  url: cG9zdGdyZXMvcG9zdGdyZXNAcG9zdGdyZXMtc2VydmljZTo1NDMyL215YXBw  # base64 encoded URL
```

#### JWT Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: jwt-secret
type: Opaque
data:
  secret: eW91cl9zdXBlcl9zZWNyZXRfanN0X2tleQ==  # base64: your_super_secret_jwt_key
  refresh_secret: eW91cl9zdXBlcl9zZWNyZXRfcmVmcmVzaF9rZXk=  # base64: refresh key
```

#### TLS Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: tls-secret
type: kubernetes.io/tls
data:
  tls.crt: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0t...
  tls.key: LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0t...
```

### 3. 配置注入方式

#### 环境变量注入
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: go-app
spec:
  template:
    spec:
      containers:
      - name: go-app
        env:
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: DB_HOST
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: jwt-secret
              key: secret
```

#### 文件挂载注入
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: go-app
spec:
  template:
    spec:
      containers:
      - name: go-app
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
          readOnly: true
        - name: secret-volume
          mountPath: /app/secrets
          readOnly: true
      volumes:
      - name: config-volume
        configMap:
          name: app-config
      - name: secret-volume
        secret:
          secretName: app-secrets
```

## 📝 自动扩展和负载均衡

### 1. Horizontal Pod Autoscaler (HPA)

#### CPU 和内存扩展
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: go-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: go-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Max
```

#### 自定义指标扩展
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: go-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: go-app
  minReplicas: 1
  maxReplicas: 20
  metrics:
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: 1000
  - type: External
    external:
      metric:
        name: queue_messages_ready
        selector:
          matchLabels:
            queue: "task_queue"
      target:
        type: AverageValue
        averageValue: 100
```

### 2. Vertical Pod Autoscaler (VPA)

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: go-app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: go-app
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: go-app
      minAllowed:
        cpu: "100m"
        memory: "64Mi"
      maxAllowed:
        cpu: "1000m"
        memory: "512Mi"
```

### 3. Pod Disruption Budget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: go-app-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: go-app
```

## 📝 网络和安全

### 1. Network Policy

#### 基础网络策略
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: go-app-network-policy
spec:
  podSelector:
    matchLabels:
      app: go-app
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    - podSelector:
        matchLabels:
          app: nginx-ingress
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 5432  # PostgreSQL
    - protocol: TCP
      port: 6379  # Redis
    - protocol: TCP
      port: 53   # DNS
```

#### 严格网络策略
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: go-app-strict-network-policy
spec:
  podSelector:
    matchLabels:
      app: go-app
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress
    - podSelector:
        matchLabels:
          app: nginx-ingress-controller
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
  - to: []
    ports:
    - protocol: UDP
      port: 53
```

### 2. Pod Security Context

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: go-app
spec:
  template:
    spec:
      securityContext:
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
      containers:
      - name: go-app
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          capabilities:
            drop:
            - ALL
          seccompProfile:
            type: RuntimeDefault
```

### 3. Service Account

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: go-app-sa
  annotations:
    iam.gke.io/gcp-service-account: go-app@your-project.iam.gserviceaccount.com
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: go-app-role
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: go-app-rolebinding
subjects:
- kind: ServiceAccount
  name: go-app-sa
roleRef:
  kind: Role
  name: go-app-role
  apiGroup: rbac.authorization.k8s.io
```

## 📝 监控和日志

### 1. Prometheus 监控配置

#### ServiceMonitor
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: go-app-monitor
  labels:
    app: go-app
spec:
  selector:
    matchLabels:
      app: go-app
  endpoints:
  - port: http
    interval: 30s
    path: /metrics
    scheme: http
    metricRelabelings:
    - sourceLabels: [__name__]
      regex: 'go_.*'
      action: keep
```

#### PrometheusRule
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: go-app-alerts
  labels:
    app: go-app
spec:
  groups:
  - name: go-app
    rules:
    - alert: GoAppHighErrorRate
      expr: rate(http_requests_total{status=~"5..", app="go-app"}[5m]) > 0.1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Go app high error rate"
        description: "Go app has high error rate: {{ $value }}"

    - alert: GoAppHighLatency
      expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{app="go-app"}[5m])) > 1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Go app high latency"
        description: "Go app has high latency: {{ $value }}s"
```

### 2. 日志收集配置

#### Fluentd ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*go-app*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
      format json
      time_format %Y-%m-%dT%H:%M:%S.%NZ
    </source>

    <filter kubernetes.**>
      @type kubernetes_metadata
    </filter>

    <match kubernetes.**>
      @type elasticsearch
      host elasticsearch-service
      port 9200
      index_name go-app-logs
      type_name _doc
    </match>
```

### 3. 分布式追踪

#### Jaeger Agent 配置
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: jaeger-agent
  labels:
    app: jaeger-agent
spec:
  selector:
    matchLabels:
      app: jaeger-agent
  template:
    metadata:
      labels:
        app: jaeger-agent
    spec:
      containers:
      - name: jaeger-agent
        image: jaegertracing/jaeger-agent:latest
        ports:
        - containerPort: 5775
          name: udp-zipkin
        - containerPort: 5778
          name: config-rest
        - containerPort: 6831
          name: udp-compact
        - containerPort: 6832
          name: udp-binary
        args:
        - --reporter.grpc.host-port=jaeger-collector:14250
        - --reporter.type=grpc
```

## 🧪 实践练习

### 练习1: 完整的微服务部署
```yaml
# api-gateway.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: api-gateway:latest
        ports:
        - containerPort: 8080
        env:
        - name: USER_SERVICE_URL
          value: "http://user-service:8080"
        - name: ORDER_SERVICE_URL
          value: "http://order-service:8080"
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway-service
spec:
  selector:
    app: api-gateway
  ports:
  - port: 80
    targetPort: 8080
```

### 练习2: 带有监控的完整配置
```yaml
# monitoring-config.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'go-app'
      static_configs:
      - targets: ['go-app-service:80']
      metrics_path: '/metrics'
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config-volume
          mountPath: /etc/prometheus
      volumes:
      - name: config-volume
        configMap:
          name: prometheus-config
```

## 📋 生产环境最佳实践

### 1. 资源优化
- 合理设置资源请求和限制
- 使用HPA进行自动扩展
- 优化镜像大小和启动时间
- 配置合适的探针

### 2. 安全配置
- 使用非root用户运行
- 配置网络策略
- 定期更新基础镜像
- 使用密钥管理敏感信息

### 3. 高可用配置
- 多副本部署
- 跨区域部署
- 健康检查和自愈
- 备份和恢复策略

### 4. 监控和日志
- 完整的监控体系
- 集中日志收集
- 告警和通知
- 性能指标收集

## 📋 检查清单

- [ ] 掌握Kubernetes基础概念
- [ ] 学会配置Deployment和Service
- [ ] 理解配置管理(ConfigMap/Secret)
- [ ] 掌握自动扩展策略
- [ ] 学会网络和安全配置
- [ ] 理解监控和日志收集
- [ ] 掌握生产环境最佳实践
- [ ] 学会故障排除

## 🚀 下一步

掌握Kubernetes部署后，你可以继续学习：
- **服务网格**: Istio, Linkerd
- **云原生工具**: Helm, Operator
- **CI/CD流水线**: GitLab CI, GitHub Actions
- **多云部署**: 跨云平台策略

---

**学习提示**: Go应用的二进制特性使其在Kubernetes中表现出色。合理的资源管理和监控配置可以让你的Go应用在Kubernetes环境中高效运行。

*最后更新: 2025年9月*