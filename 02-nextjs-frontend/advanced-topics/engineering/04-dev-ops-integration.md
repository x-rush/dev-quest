# Next.js DevOps集成与CI/CD实践

## 概述

DevOps集成是现代前端工程化的核心组成部分，通过自动化和标准化流程提高交付速度和质量。本文深入探讨Next.js应用的DevOps最佳实践。

## CI/CD管道设计

### 基础管道架构

```typescript
// .github/workflows/ci-cd.yml
name: Next.js CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  NODE_VERSION: '18'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: ${{ env.NODE_VERSION }}
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run type checking
      run: npm run type-check

    - name: Run linting
      run: npm run lint

    - name: Run unit tests
      run: npm run test:unit

    - name: Run integration tests
      run: npm run test:integration

    - name: Build application
      run: npm run build

    - name: Run e2e tests
      run: npm run test:e2e

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    needs: test

    steps:
    - uses: actions/checkout@v4

    - name: Run npm audit
      run: npm audit --audit-level=high

    - name: Run Snyk security scan
      uses: snyk/actions/node@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

    - name: Run dependency check
      run: npx audit-ci --config .audit-ci.json

  build-and-push:
    name: Build and Push Docker Image
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.ref == 'refs/heads/main'

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
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}

    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        platforms: linux/amd64,linux/arm64
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: build-and-push
    if: github.ref == 'refs/heads/main'
    environment: staging

    steps:
    - uses: actions/checkout@v4

    - name: Deploy to Kubernetes
      uses: kodermax/kubectl-aws-eks@master
      env:
        KUBE_CONFIG_DATA: ${{ secrets.KUBE_CONFIG_DATA_STAGING }}
      with:
        args: apply -f k8s/staging

    - name: Run smoke tests
      run: |
        npm run test:smoke \
          --baseUrl=https://staging.example.com

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
    - uses: actions/checkout@v4

    - name: Deploy to Kubernetes
      uses: kodermax/kubectl-aws-eks@master
      env:
        KUBE_CONFIG_DATA: ${{ secrets.KUBE_CONFIG_DATA_PRODUCTION }}
      with:
        args: apply -f k8s/production

    - name: Run production tests
      run: |
        npm run test:production \
          --baseUrl=https://example.com

    - name: Notify deployment
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        channel: '#deployments'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### 多环境部署策略

```typescript
// scripts/deploy.ts
import { execSync } from 'child_process';
import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

interface DeployConfig {
  environment: 'development' | 'staging' | 'production';
  region: string;
  cluster: string;
  namespace: string;
  domain: string;
  resources: {
    cpu: string;
    memory: string;
    replicas: number;
  };
}

const deployConfigs: Record<string, DeployConfig> = {
  development: {
    environment: 'development',
    region: 'us-west-2',
    cluster: 'dev-cluster',
    namespace: 'dev',
    domain: 'dev.example.com',
    resources: {
      cpu: '500m',
      memory: '1Gi',
      replicas: 1,
    },
  },
  staging: {
    environment: 'staging',
    region: 'us-west-2',
    cluster: 'staging-cluster',
    namespace: 'staging',
    domain: 'staging.example.com',
    resources: {
      cpu: '1000m',
      memory: '2Gi',
      replicas: 2,
    },
  },
  production: {
    environment: 'production',
    region: 'us-east-1',
    cluster: 'prod-cluster',
    namespace: 'prod',
    domain: 'example.com',
    resources: {
      cpu: '2000m',
      memory: '4Gi',
      replicas: 3,
    },
  },
};

function generateKubernetesManifest(config: DeployConfig): string {
  const template = readFileSync(
    join(__dirname, '../k8s/template.yaml'),
    'utf-8'
  );

  const manifest = template
    .replace(/{{ENVIRONMENT}}/g, config.environment)
    .replace(/{{NAMESPACE}}/g, config.namespace)
    .replace(/{{DOMAIN}}/g, config.domain)
    .replace(/{{CPU_LIMITS}}/g, config.resources.cpu)
    .replace(/{{MEMORY_LIMITS}}/g, config.resources.memory)
    .replace(/{{REPLICAS}}/g, config.resources.replicas.toString());

  return manifest;
}

function deployEnvironment(environment: string): void {
  const config = deployConfigs[environment];
  if (!config) {
    throw new Error(`Unknown environment: ${environment}`);
  }

  console.log(`Deploying to ${environment}...`);

  // Generate Kubernetes manifests
  const manifest = generateKubernetesManifest(config);
  const manifestPath = join(__dirname, `../k8s/${environment}.yaml`);
  writeFileSync(manifestPath, manifest);

  // Deploy to Kubernetes
  try {
    execSync(
      `kubectl apply -f ${manifestPath} --namespace=${config.namespace}`,
      { stdio: 'inherit' }
    );

    // Wait for deployment
    execSync(
      `kubectl rollout status deployment/nextjs-app --namespace=${config.namespace} --timeout=300s`,
      { stdio: 'inherit' }
    );

    console.log(`Successfully deployed to ${environment}`);
  } catch (error) {
    console.error(`Deployment to ${environment} failed:`, error);
    process.exit(1);
  }
}

function runSmokeTests(environment: string): void {
  const config = deployConfigs[environment];
  console.log(`Running smoke tests for ${environment}...`);

  try {
    execSync(
      `npm run test:smoke -- --baseUrl=https://${config.domain}`,
      { stdio: 'inherit' }
    );
    console.log(`Smoke tests passed for ${environment}`);
  } catch (error) {
    console.error(`Smoke tests failed for ${environment}:`, error);
    process.exit(1);
  }
}

// CLI usage
if (require.main === module) {
  const environment = process.argv[2];
  if (!environment) {
    console.error('Please specify an environment: development, staging, production');
    process.exit(1);
  }

  deployEnvironment(environment);
  runSmokeTests(environment);
}

export { deployEnvironment, runSmokeTests, DeployConfig };
```

## 基础设施即代码 (IaC)

### Terraform配置

```hcl
# main.tf
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  token                  = data.aws_eks_cluster_auth.this.token
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    token                  = data.aws_eks_cluster_auth.this.token
  }
}

# EKS Cluster
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.15"

  cluster_name    = var.cluster_name
  cluster_version = "1.27"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  cluster_endpoint_public_access = true

  eks_managed_node_groups = {
    nextjs_nodes = {
      min_size     = 2
      max_size     = 10
      desired_size = 3

      instance_types = ["t3.medium", "t3.large"]
      capacity_type  = "ON_DEMAND"

      labels = {
        "app.kubernetes.io/component" = "frontend"
        "app.kubernetes.io/name"      = "nextjs"
      }

      taints = {
        dedicated = {
          key    = "dedicated"
          value  = "nextjs"
          effect = "NO_SCHEDULE"
        }
      }
    }
  }

  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
  }
}

# VPC Configuration
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.cluster_name}-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-west-2a", "us-west-2b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true

  public_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                      = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"             = "1"
  }
}

# Kubernetes Namespaces
resource "kubernetes_namespace" "nextjs" {
  metadata {
    name = var.namespace
    labels = {
      "app.kubernetes.io/name"     = "nextjs"
      "app.kubernetes.io/part-of"  = "nextjs-platform"
    }
  }
}

# Kubernetes Service Account
resource "kubernetes_service_account" "nextjs" {
  metadata {
    name      = "nextjs-service-account"
    namespace = kubernetes_namespace.nextjs.metadata[0].name
    labels = {
      "app.kubernetes.io/name" = "nextjs"
    }
  }

  automount_service_account_token = true
}

# Kubernetes Cluster Role
resource "kubernetes_cluster_role" "nextjs" {
  metadata {
    name = "nextjs-role"
    labels = {
      "app.kubernetes.io/name" = "nextjs"
    }
  }

  rule {
    api_groups = [""]
    resources  = ["pods", "services", "configmaps", "secrets"]
    verbs      = ["get", "list", "watch"]
  }

  rule {
    api_groups = ["apps"]
    resources  = ["deployments", "replicasets"]
    verbs      = ["get", "list", "watch", "create", "update", "patch", "delete"]
  }

  rule {
    api_groups = ["autoscaling"]
    resources  = ["horizontalpodautoscalers"]
    verbs      = ["get", "list", "watch", "create", "update", "patch", "delete"]
  }
}

# Kubernetes Cluster Role Binding
resource "kubernetes_cluster_role_binding" "nextjs" {
  metadata {
    name = "nextjs-role-binding"
    labels = {
      "app.kubernetes.io/name" = "nextjs"
    }
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.nextjs.metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.nextjs.metadata[0].name
    namespace = kubernetes_namespace.nextjs.metadata[0].name
  }
}

# Helm Release for Ingress Controller
resource "helm_release" "nginx_ingress" {
  name       = "nginx-ingress"
  repository = "https://kubernetes.github.io/ingress-nginx"
  chart      = "ingress-nginx"
  namespace  = "ingress-nginx"
  version    = "4.8.0"

  set {
    name  = "controller.service.type"
    value = "LoadBalancer"
  }

  set {
    name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/aws-load-balancer-type"
    value = "nlb"
  }

  depends_on = [module.eks]
}

# Helm Release for Monitoring
resource "helm_release" "prometheus" {
  name       = "prometheus"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  namespace  = "monitoring"
  version    = "48.0.0"

  set {
    name  = "prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues"
    value = "false"
  }

  set {
    name  = "grafana.adminPassword"
    value = var.grafana_password
  }

  depends_on = [module.eks]
}
```

### Kubernetes配置

```yaml
# k8s/template.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nextjs-app
  namespace: {{NAMESPACE}}
  labels:
    app.kubernetes.io/name: nextjs-app
    app.kubernetes.io/component: frontend
    app.kubernetes.io/part-of: nextjs-platform
spec:
  replicas: {{REPLICAS}}
  selector:
    matchLabels:
      app.kubernetes.io/name: nextjs-app
  template:
    metadata:
      labels:
        app.kubernetes.io/name: nextjs-app
        app.kubernetes.io/component: frontend
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "3001"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: nextjs-service-account
      containers:
      - name: nextjs-app
        image: ghcr.io/your-username/nextjs-app:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 3000
          name: http
        - containerPort: 3001
          name: metrics
        env:
        - name: NODE_ENV
          value: "{{ENVIRONMENT}}"
        - name: NEXT_PUBLIC_API_URL
          value: "https://api.{{DOMAIN}}"
        - name: NEXT_PUBLIC_ANALYTICS_ID
          valueFrom:
            secretKeyRef:
              name: nextjs-secrets
              key: analytics-id
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: nextjs-secrets
              key: database-url
        resources:
          requests:
            cpu: "250m"
            memory: "512Mi"
          limits:
            cpu: "{{CPU_LIMITS}}"
            memory: "{{MEMORY_LIMITS}}"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: nextjs-cache
          mountPath: /app/.next/cache
        - name: nextjs-build
          mountPath: /app/.next
      volumes:
      - name: nextjs-cache
        emptyDir: {}
      - name: nextjs-build
        persistentVolumeClaim:
          claimName: nextjs-build-pvc
      imagePullSecrets:
      - name: github-registry-secret

---
apiVersion: v1
kind: Service
metadata:
  name: nextjs-service
  namespace: {{NAMESPACE}}
  labels:
    app.kubernetes.io/name: nextjs-app
    app.kubernetes.io/component: frontend
spec:
  selector:
    app.kubernetes.io/name: nextjs-app
  ports:
  - port: 80
    targetPort: 3000
    name: http
  - port: 3001
    targetPort: 3001
    name: metrics
  type: ClusterIP

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: nextjs-build-pvc
  namespace: {{NAMESPACE}}
  labels:
    app.kubernetes.io/name: nextjs-app
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: gp2

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nextjs-ingress
  namespace: {{NAMESPACE}}
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/configuration-snippet: |
      more_set_headers "X-Content-Type-Options: nosniff";
      more_set_headers "X-Frame-Options: DENY";
      more_set_headers "X-XSS-Protection: 1; mode=block";
spec:
  tls:
  - hosts:
    - {{DOMAIN}}
    secretName: nextjs-tls-secret
  rules:
  - host: {{DOMAIN}}
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nextjs-service
            port:
              number: 80

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nextjs-hpa
  namespace: {{NAMESPACE}}
  labels:
    app.kubernetes.io/name: nextjs-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nextjs-app
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
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: 100

---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: nextjs-pdb
  namespace: {{NAMESPACE}}
  labels:
    app.kubernetes.io/name: nextjs-app
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: nextjs-app
```

## 监控与可观测性

### 监控配置

```typescript
// lib/monitoring.ts
import { NextRequest, NextResponse } from 'next/server';
import { createHash } from 'crypto';
import { performance } from 'perf_hooks';

interface MetricData {
  name: string;
  value: number;
  labels: Record<string, string>;
  timestamp: number;
}

interface HealthCheck {
  status: 'healthy' | 'degraded' | 'unhealthy';
  checks: HealthCheckResult[];
  timestamp: number;
}

interface HealthCheckResult {
  name: string;
  status: 'pass' | 'fail' | 'warn';
  duration: number;
  message?: string;
}

class MonitoringService {
  private metrics: MetricData[] = [];
  private healthChecks: HealthCheckResult[] = [];

  constructor() {
    // Start collecting metrics periodically
    setInterval(() => this.collectSystemMetrics(), 30000);
  }

  // Custom metrics collection
  recordMetric(name: string, value: number, labels: Record<string, string> = {}): void {
    const metric: MetricData = {
      name,
      value,
      labels,
      timestamp: Date.now(),
    };

    this.metrics.push(metric);

    // Keep only last 1000 metrics in memory
    if (this.metrics.length > 1000) {
      this.metrics = this.metrics.slice(-1000);
    }

    // Send to external monitoring service
    this.sendToPrometheus(metric);
  }

  // HTTP request monitoring middleware
  async withMonitoring(
    request: NextRequest,
    handler: (req: NextRequest) => Promise<NextResponse>
  ): Promise<NextResponse> {
    const startTime = performance.now();
    const requestId = createHash('sha256')
      .update(`${Date.now()}-${Math.random()}`)
      .digest('hex')
      .substring(0, 8);

    try {
      const response = await handler(request);
      const duration = performance.now() - startTime;

      // Record metrics
      this.recordMetric('http_requests_total', 1, {
        method: request.method,
        path: request.nextUrl.pathname,
        status: response.status.toString(),
      });

      this.recordMetric('http_request_duration_ms', duration, {
        method: request.method,
        path: request.nextUrl.pathname,
      });

      // Add headers
      response.headers.set('X-Request-ID', requestId);
      response.headers.set('X-Response-Time', duration.toFixed(2));

      return response;
    } catch (error) {
      const duration = performance.now() - startTime;

      this.recordMetric('http_requests_total', 1, {
        method: request.method,
        path: request.nextUrl.pathname,
        status: '500',
      });

      this.recordMetric('http_errors_total', 1, {
        method: request.method,
        path: request.nextUrl.pathname,
        error: error instanceof Error ? error.name : 'unknown',
      });

      throw error;
    }
  }

  // Health checks
  async performHealthChecks(): Promise<HealthCheck> {
    const checks: HealthCheckResult[] = [];

    // Database health check
    checks.push(await this.checkDatabase());

    // External API health check
    checks.push(await this.checkExternalAPIs());

    // Cache health check
    checks.push(await this.checkCache());

    // Storage health check
    checks.push(await this.checkStorage());

    // Determine overall status
    const failedChecks = checks.filter(c => c.status === 'fail');
    const warningChecks = checks.filter(c => c.status === 'warn');

    let status: HealthCheck['status'] = 'healthy';
    if (failedChecks.length > 0) {
      status = 'unhealthy';
    } else if (warningChecks.length > 0) {
      status = 'degraded';
    }

    const health: HealthCheck = {
      status,
      checks,
      timestamp: Date.now(),
    };

    this.healthChecks = checks;
    return health;
  }

  private async checkDatabase(): Promise<HealthCheckResult> {
    const startTime = performance.now();

    try {
      // Implement your database health check logic
      // Example: await prisma.$queryRaw`SELECT 1`;

      return {
        name: 'database',
        status: 'pass',
        duration: performance.now() - startTime,
      };
    } catch (error) {
      return {
        name: 'database',
        status: 'fail',
        duration: performance.now() - startTime,
        message: error instanceof Error ? error.message : 'Database connection failed',
      };
    }
  }

  private async checkExternalAPIs(): Promise<HealthCheckResult> {
    const startTime = performance.now();

    try {
      // Implement your external API health check logic
      const response = await fetch('https://api.example.com/health', {
        timeout: 5000,
      });

      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }

      return {
        name: 'external_apis',
        status: 'pass',
        duration: performance.now() - startTime,
      };
    } catch (error) {
      return {
        name: 'external_apis',
        status: 'warn',
        duration: performance.now() - startTime,
        message: error instanceof Error ? error.message : 'External APIs unavailable',
      };
    }
  }

  private async checkCache(): Promise<HealthCheckResult> {
    const startTime = performance.now();

    try {
      // Implement your cache health check logic
      // Example: await redis.ping();

      return {
        name: 'cache',
        status: 'pass',
        duration: performance.now() - startTime,
      };
    } catch (error) {
      return {
        name: 'cache',
        status: 'warn',
        duration: performance.now() - startTime,
        message: error instanceof Error ? error.message : 'Cache unavailable',
      };
    }
  }

  private async checkStorage(): Promise<HealthCheckResult> {
    const startTime = performance.now();

    try {
      // Implement your storage health check logic
      // Example: await s3.listBuckets().promise();

      return {
        name: 'storage',
        status: 'pass',
        duration: performance.now() - startTime,
      };
    } catch (error) {
      return {
        name: 'storage',
        status: 'fail',
        duration: performance.now() - startTime,
        message: error instanceof Error ? error.message : 'Storage unavailable',
      };
    }
  }

  private async collectSystemMetrics(): Promise<void> {
    const memUsage = process.memoryUsage();
    const cpuUsage = process.cpuUsage();

    this.recordMetric('nodejs_memory_usage_bytes', memUsage.heapUsed, {
      type: 'heap_used',
    });

    this.recordMetric('nodejs_memory_usage_bytes', memUsage.heapTotal, {
      type: 'heap_total',
    });

    this.recordMetric('nodejs_memory_usage_bytes', memUsage.rss, {
      type: 'rss',
    });

    this.recordMetric('nodejs_cpu_usage_total', cpuUsage.user + cpuUsage.system, {
      type: 'total',
    });
  }

  private sendToPrometheus(metric: MetricData): void {
    // Implement Prometheus metrics endpoint
    // This would typically expose metrics on a /metrics endpoint
  }

  // Generate Prometheus metrics format
  generatePrometheusMetrics(): string {
    const lines: string[] = [];

    for (const metric of this.metrics) {
      const labels = Object.entries(metric.labels)
        .map(([key, value]) => `${key}="${value}"`)
        .join(',');

      const labelString = labels ? `{${labels}}` : '';
      lines.push(`${metric.name}${labelString} ${metric.value} ${metric.timestamp}`);
    }

    return lines.join('\n');
  }

  // Generate health check report
  generateHealthReport(): HealthCheck {
    const overallStatus = this.healthChecks.every(c => c.status === 'pass')
      ? 'healthy'
      : this.healthChecks.some(c => c.status === 'fail')
      ? 'unhealthy'
      : 'degraded';

    return {
      status: overallStatus,
      checks: this.healthChecks,
      timestamp: Date.now(),
    };
  }
}

export const monitoring = new MonitoringService();

// Export middleware for API routes
export function withMonitoring() {
  return async (
    request: NextRequest,
    context: any,
    handler: (req: NextRequest, context: any) => Promise<NextResponse>
  ): Promise<NextResponse> => {
    return await monitoring.withMonitoring(request, handler);
  };
}
```

### 日志管理

```typescript
// lib/logging.ts
import winston from 'winston';
import { NextRequest } from 'next/server';

interface LogContext {
  requestId?: string;
  userId?: string;
  path?: string;
  method?: string;
  userAgent?: string;
  ip?: string;
  duration?: number;
  [key: string]: any;
}

class Logger {
  private logger: winston.Logger;

  constructor() {
    this.logger = winston.createLogger({
      level: process.env.LOG_LEVEL || 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
      ),
      defaultMeta: {
        service: 'nextjs-app',
        environment: process.env.NODE_ENV,
      },
      transports: [
        // Console logging
        new winston.transports.Console({
          format: winston.format.combine(
            winston.format.colorize(),
            winston.format.simple()
          ),
        }),

        // File logging for errors
        new winston.transports.File({
          filename: 'logs/error.log',
          level: 'error',
          maxsize: 5242880, // 5MB
          maxFiles: 5,
        }),

        // File logging for all logs
        new winston.transports.File({
          filename: 'logs/combined.log',
          maxsize: 5242880, // 5MB
          maxFiles: 5,
        }),
      ],
    });

    // Add Datadog transport in production
    if (process.env.NODE_ENV === 'production' && process.env.DATADOG_API_KEY) {
      this.logger.add(new winston.transports.Http({
        host: 'http-intake.logs.datadoghq.com',
        path: `/api/v2/logs?dd-api-key=${process.env.DATADOG_API_KEY}&ddsource=nodejs`,
        ssl: true,
      }));
    }
  }

  info(message: string, context: LogContext = {}): void {
    this.logger.info(message, context);
  }

  warn(message: string, context: LogContext = {}): void {
    this.logger.warn(message, context);
  }

  error(message: string, error?: Error, context: LogContext = {}): void {
    this.logger.error(message, {
      ...context,
      error: error ? {
        message: error.message,
        stack: error.stack,
        name: error.name,
      } : undefined,
    });
  }

  debug(message: string, context: LogContext = {}): void {
    this.logger.debug(message, context);
  }

  // HTTP request logging middleware
  async logHttpRequest(
    request: NextRequest,
    handler: (req: NextRequest) => Promise<Response>
  ): Promise<Response> {
    const startTime = Date.now();
    const requestId = this.generateRequestId();

    const context: LogContext = {
      requestId,
      path: request.nextUrl.pathname,
      method: request.method,
      userAgent: request.headers.get('user-agent') || '',
      ip: this.getClientIP(request),
    };

    this.info('HTTP request started', context);

    try {
      const response = await handler(request);
      const duration = Date.now() - startTime;

      this.info('HTTP request completed', {
        ...context,
        duration,
        statusCode: response.status,
      });

      return response;
    } catch (error) {
      const duration = Date.now() - startTime;

      this.error('HTTP request failed', error instanceof Error ? error : new Error('Unknown error'), {
        ...context,
        duration,
      });

      throw error;
    }
  }

  // Business event logging
  logBusinessEvent(event: string, data: any, userId?: string): void {
    this.info(`Business event: ${event}`, {
      event,
      data,
      userId,
      timestamp: Date.now(),
    });
  }

  // Performance event logging
  logPerformanceEvent(operation: string, duration: number, metadata: any = {}): void {
    this.info(`Performance: ${operation}`, {
      operation,
      duration,
      metadata,
      timestamp: Date.now(),
    });
  }

  // Security event logging
  logSecurityEvent(event: string, details: any): void {
    this.warn(`Security event: ${event}`, {
      event,
      details,
      timestamp: Date.now(),
      severity: 'security',
    });
  }

  private generateRequestId(): string {
    return Math.random().toString(36).substring(2, 15);
  }

  private getClientIP(request: NextRequest): string {
    return (
      request.headers.get('x-forwarded-for') ||
      request.headers.get('x-real-ip') ||
      request.headers.get('cf-connecting-ip') ||
      'unknown'
    );
  }
}

export const logger = new Logger();

// Export logging middleware
export function withLogging() {
  return async (
    request: NextRequest,
    context: any,
    handler: (req: NextRequest, context: any) => Promise<Response>
  ): Promise<Response> => {
    return await logger.logHttpRequest(request, handler);
  };
}
```

## 灾难恢复与备份

### 备份策略

```typescript
// scripts/backup.ts
import { execSync } from 'child_process';
import { createReadStream, createWriteStream } from 'fs';
import { createGzip } from 'zlib';
import { pipeline } from 'stream/promises';
import { upload } from '@aws-sdk/lib-storage';
import { S3Client } from '@aws-sdk/client-s3';
import { CronJob } from 'cron';

interface BackupConfig {
  database: {
    host: string;
    port: number;
    username: string;
    password: string;
    database: string;
  };
  s3: {
    bucket: string;
    region: string;
    accessKeyId: string;
    secretAccessKey: string;
  };
  retention: {
    daily: number;
    weekly: number;
    monthly: number;
  };
}

class BackupService {
  private s3Client: S3Client;
  private config: BackupConfig;

  constructor(config: BackupConfig) {
    this.config = config;
    this.s3Client = new S3Client({
      region: config.s3.region,
      credentials: {
        accessKeyId: config.s3.accessKeyId,
        secretAccessKey: config.s3.secretAccessKey,
      },
    });

    // Schedule regular backups
    this.scheduleBackups();
  }

  // Perform database backup
  async backupDatabase(): Promise<string> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `database-backup-${timestamp}.sql.gz`;
    const filepath = `/tmp/${filename}`;

    try {
      // Create database dump
      const dumpCommand = `pg_dump -h ${this.config.database.host} \
        -p ${this.config.database.port} \
        -U ${this.config.database.username} \
        -d ${this.config.database.database} \
        --no-owner \
        --no-privileges`;

      const gzip = createGzip();
      const output = createWriteStream(filepath);
      const dump = execSync(dumpCommand, { env: { ...process.env, PGPASSWORD: this.config.database.password } });

      await pipeline(
        createReadStream(dump),
        gzip,
        output
      );

      // Upload to S3
      await this.uploadToS3(filepath, `backups/database/${filename}`);

      logger.info('Database backup completed', { filename, size: dump.length });

      return filename;
    } catch (error) {
      logger.error('Database backup failed', error instanceof Error ? error : new Error('Unknown error'));
      throw error;
    }
  }

  // Backup static assets
  async backupAssets(): Promise<string> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `assets-backup-${timestamp}.tar.gz`;
    const filepath = `/tmp/${filename}`;

    try {
      // Create assets archive
      execSync(`tar -czf ${filepath} public/ static/`);

      // Upload to S3
      await this.uploadToS3(filepath, `backups/assets/${filename}`);

      logger.info('Assets backup completed', { filename });

      return filename;
    } catch (error) {
      logger.error('Assets backup failed', error instanceof Error ? error : new Error('Unknown error'));
      throw error;
    }
  }

  // Upload file to S3
  private async uploadToS3(filepath: string, key: string): Promise<void> {
    const fileStream = createReadStream(filepath);

    const uploadParams = {
      Bucket: this.config.s3.bucket,
      Key: key,
      Body: fileStream,
      ContentType: 'application/gzip',
    };

    const upload = new Upload({
      client: this.s3Client,
      params: uploadParams,
    });

    await upload.done();
  }

  // Clean old backups
  async cleanOldBackups(): Promise<void> {
    try {
      const { Contents } = await this.s3Client.send({
        ...new ListObjectsV2Command({
          Bucket: this.config.s3.bucket,
          Prefix: 'backups/',
        }),
      });

      if (!Contents) return;

      const now = new Date();
      const filesToDelete: string[] = [];

      for (const object of Contents) {
        if (!object.Key || !object.LastModified) continue;

        const ageInDays = (now.getTime() - object.LastModified.getTime()) / (1000 * 60 * 60 * 24);

        // Determine retention period based on backup type
        let retentionDays = this.config.retention.daily;

        if (object.Key.includes('weekly')) {
          retentionDays = this.config.retention.weekly;
        } else if (object.Key.includes('monthly')) {
          retentionDays = this.config.retention.monthly;
        }

        if (ageInDays > retentionDays) {
          filesToDelete.push(object.Key);
        }
      }

      // Delete old backups
      if (filesToDelete.length > 0) {
        await this.s3Client.send({
          ...new DeleteObjectsCommand({
            Bucket: this.config.s3.bucket,
            Delete: {
              Objects: filesToDelete.map(Key => ({ Key })),
            },
          }),
        });

        logger.info('Cleaned old backups', { count: filesToDelete.length });
      }
    } catch (error) {
      logger.error('Failed to clean old backups', error instanceof Error ? error : new Error('Unknown error'));
    }
  }

  // Restore database from backup
  async restoreDatabase(backupKey: string): Promise<void> {
    try {
      const filepath = `/tmp/${backupKey.split('/').pop()}`;

      // Download backup from S3
      const { Body } = await this.s3Client.send({
        ...new GetObjectCommand({
          Bucket: this.config.s3.bucket,
          Key: backupKey,
        }),
      });

      if (!Body) throw new Error('Backup file not found');

      const gunzip = createGunzip();
      const output = createWriteStream(filepath);

      await pipeline(Body as Readable, gunzip, output);

      // Restore database
      const restoreCommand = `psql -h ${this.config.database.host} \
        -p ${this.config.database.port} \
        -U ${this.config.database.username} \
        -d ${this.config.database.database} \
        -f ${filepath}`;

      execSync(restoreCommand, {
        env: { ...process.env, PGPASSWORD: this.config.database.password },
        stdio: 'inherit'
      });

      logger.info('Database restore completed', { backupKey });
    } catch (error) {
      logger.error('Database restore failed', error instanceof Error ? error : new Error('Unknown error'));
      throw error;
    }
  }

  // Schedule regular backups
  private scheduleBackups(): void {
    // Daily backup at 2 AM
    new CronJob('0 2 * * *', async () => {
      try {
        await this.backupDatabase();
        await this.backupAssets();
        await this.cleanOldBackups();
      } catch (error) {
        logger.error('Scheduled backup failed', error instanceof Error ? error : new Error('Unknown error'));
      }
    }, null, true, 'UTC');

    // Weekly backup on Sunday at 3 AM
    new CronJob('0 3 * * 0', async () => {
      try {
        const filename = await this.backupDatabase();
        // Copy to weekly folder
        await this.s3Client.send({
          ...new CopyObjectCommand({
            Bucket: this.config.s3.bucket,
            CopySource: `${this.config.s3.bucket}/backups/database/${filename}`,
            Key: `backups/database/weekly/${filename}`,
          }),
        });
      } catch (error) {
        logger.error('Weekly backup failed', error instanceof Error ? error : new Error('Unknown error'));
      }
    }, null, true, 'UTC');

    // Monthly backup on 1st at 4 AM
    new CronJob('0 4 1 * *', async () => {
      try {
        const filename = await this.backupDatabase();
        // Copy to monthly folder
        await this.s3Client.send({
          ...new CopyObjectCommand({
            Bucket: this.config.s3.bucket,
            CopySource: `${this.config.s3.bucket}/backups/database/${filename}`,
            Key: `backups/database/monthly/${filename}`,
          }),
        });
      } catch (error) {
        logger.error('Monthly backup failed', error instanceof Error ? error : new Error('Unknown error'));
      }
    }, null, true, 'UTC');
  }

  // Get backup status
  async getBackupStatus(): Promise<{
    lastBackup?: string;
    totalBackups: number;
    backupSize: number;
  }> {
    try {
      const { Contents } = await this.s3Client.send({
        ...new ListObjectsV2Command({
          Bucket: this.config.s3.bucket,
          Prefix: 'backups/',
        }),
      });

      if (!Contents) {
        return { totalBackups: 0, backupSize: 0 };
      }

      const databaseBackups = Contents.filter(obj => obj.Key?.includes('database-backup'));
      const sortedBackups = databaseBackups.sort((a, b) =>
        (b.LastModified?.getTime() || 0) - (a.LastModified?.getTime() || 0)
      );

      return {
        lastBackup: sortedBackups[0]?.LastModified?.toISOString(),
        totalBackups: Contents.length,
        backupSize: Contents.reduce((sum, obj) => sum + (obj.Size || 0), 0),
      };
    } catch (error) {
      logger.error('Failed to get backup status', error instanceof Error ? error : new Error('Unknown error'));
      throw error;
    }
  }
}

// Export backup service
export { BackupService, BackupConfig };
```

## 最佳实践与建议

### 1. CI/CD最佳实践

```yaml
# .github/workflows/security.yml
name: Security Scanning

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run npm audit
      run: npm audit --audit-level=moderate

    - name: Run Snyk
      uses: snyk/actions/node@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

    - name: Run OWASP Dependency Check
      run: |
        curl -L -o dependency-check.tar.gz https://github.com/jeremylong/DependencyCheck/releases/download/v8.2.1/dependency-check-8.2.1-release.tar.gz
        tar -xzf dependency-check.tar.gz
        ./dependency-check/bin/dependency-check --project "Next.js App" --format HTML --out dependency-check-report.html

    - name: Upload security reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: |
          dependency-check-report.html
          snyk-report.json
```

### 2. 监控最佳实践

```typescript
// lib/monitoring/alerts.ts
interface AlertRule {
  name: string;
  condition: (metrics: any) => boolean;
  severity: 'info' | 'warning' | 'critical';
  message: string;
  actions: AlertAction[];
}

interface AlertAction {
  type: 'email' | 'slack' | 'pagerduty';
  config: any;
}

class AlertManager {
  private rules: AlertRule[] = [];

  constructor() {
    this.setupDefaultRules();
  }

  addRule(rule: AlertRule): void {
    this.rules.push(rule);
  }

  async evaluateRules(metrics: any): Promise<void> {
    for (const rule of this.rules) {
      if (rule.condition(metrics)) {
        await this.triggerAlert(rule, metrics);
      }
    }
  }

  private setupDefaultRules(): void {
    // High error rate alert
    this.addRule({
      name: 'high_error_rate',
      condition: (metrics) => {
        const errorRate = metrics.http_requests_total.filter(
          (req: any) => req.labels.status >= '500'
        ).length / metrics.http_requests_total.length;
        return errorRate > 0.05; // 5% error rate
      },
      severity: 'critical',
      message: 'High error rate detected',
      actions: [
        {
          type: 'slack',
          config: { channel: '#alerts' },
        },
        {
          type: 'pagerduty',
          config: { service_key: process.env.PAGERDUTY_SERVICE_KEY },
        },
      ],
    });

    // High response time alert
    this.addRule({
      name: 'high_response_time',
      condition: (metrics) => {
        const avgResponseTime = metrics.http_request_duration_ms.reduce(
          (sum: number, req: any) => sum + req.value, 0
        ) / metrics.http_request_duration_ms.length;
        return avgResponseTime > 2000; // 2 seconds
      },
      severity: 'warning',
      message: 'High response time detected',
      actions: [
        {
          type: 'slack',
          config: { channel: '#performance' },
        },
      ],
    });

    // Memory usage alert
    this.addRule({
      name: 'high_memory_usage',
      condition: (metrics) => {
        const memoryUsage = metrics.nodejs_memory_usage_bytes.find(
          (m: any) => m.labels.type === 'heap_used'
        )?.value || 0;
        return memoryUsage > 500 * 1024 * 1024; // 500MB
      },
      severity: 'warning',
      message: 'High memory usage detected',
      actions: [
        {
          type: 'email',
          config: { to: 'devops@example.com' },
        },
      ],
    });
  }

  private async triggerAlert(rule: AlertRule, metrics: any): Promise<void> {
    const alert = {
      name: rule.name,
      severity: rule.severity,
      message: rule.message,
      timestamp: new Date().toISOString(),
      metrics,
    };

    logger.warn('Alert triggered', alert);

    // Execute actions
    for (const action of rule.actions) {
      try {
        await this.executeAction(action, alert);
      } catch (error) {
        logger.error('Failed to execute alert action', error);
      }
    }
  }

  private async executeAction(action: AlertAction, alert: any): Promise<void> {
    switch (action.type) {
      case 'slack':
        await this.sendSlackAlert(action.config, alert);
        break;
      case 'email':
        await this.sendEmailAlert(action.config, alert);
        break;
      case 'pagerduty':
        await this.sendPagerDutyAlert(action.config, alert);
        break;
    }
  }

  private async sendSlackAlert(config: any, alert: any): Promise<void> {
    // Implement Slack webhook integration
    const webhookUrl = process.env.SLACK_WEBHOOK_URL;
    if (!webhookUrl) return;

    const payload = {
      channel: config.channel,
      text: `[${alert.severity.toUpperCase()}] ${alert.message}`,
      attachments: [
        {
          color: this.getSeverityColor(alert.severity),
          fields: [
            { title: 'Alert', value: alert.name, short: true },
            { title: 'Time', value: alert.timestamp, short: true },
          ],
        },
      ],
    };

    await fetch(webhookUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  }

  private async sendEmailAlert(config: any, alert: any): Promise<void> {
    // Implement email alert integration
    // This would typically use a service like SendGrid or AWS SES
  }

  private async sendPagerDutyAlert(config: any, alert: any): Promise<void> {
    // Implement PagerDuty integration
    const pagerDutyUrl = 'https://events.pagerduty.com/v2/enqueue';

    await fetch(pagerDutyUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        routing_key: config.service_key,
        event_action: 'trigger',
        payload: {
          summary: alert.message,
          severity: alert.severity === 'critical' ? 'critical' : 'warning',
          source: 'nextjs-app',
          component: 'frontend',
        },
      }),
    });
  }

  private getSeverityColor(severity: string): string {
    switch (severity) {
      case 'critical': return 'danger';
      case 'warning': return 'warning';
      default: return 'good';
    }
  }
}

export const alertManager = new AlertManager();
```

### 3. 灾难恢复最佳实践

```typescript
// scripts/disaster-recovery.ts
import { BackupService } from './backup';

class DisasterRecoveryService {
  private backupService: BackupService;

  constructor(backupService: BackupService) {
    this.backupService = backupService;
  }

  // Perform failover to backup region
  async failoverToBackupRegion(): Promise<void> {
    try {
      logger.info('Initiating failover to backup region');

      // Update DNS to point to backup region
      await this.updateDNS('backup');

      // Restore database from latest backup
      const latestBackup = await this.getLatestBackup();
      if (latestBackup) {
        await this.backupService.restoreDatabase(latestBackup);
      }

      // Scale up backup infrastructure
      await this.scaleInfrastructure('backup', 3);

      logger.info('Failover completed successfully');
    } catch (error) {
      logger.error('Failover failed', error instanceof Error ? error : new Error('Unknown error'));
      throw error;
    }
  }

  // Perform failback to primary region
  async failbackToPrimaryRegion(): Promise<void> {
    try {
      logger.info('Initiating failback to primary region');

      // Sync data from backup to primary
      await this.syncDataToPrimary();

      // Update DNS to point to primary region
      await this.updateDNS('primary');

      // Scale down backup infrastructure
      await this.scaleInfrastructure('backup', 1);

      logger.info('Failback completed successfully');
    } catch (error) {
      logger.error('Failback failed', error instanceof Error ? error : new Error('Unknown error'));
      throw error;
    }
  }

  // Test disaster recovery procedures
  async testDisasterRecovery(): Promise<void> {
    try {
      logger.info('Starting disaster recovery test');

      // Create test environment
      await this.createTestEnvironment();

      // Simulate failover
      await this.simulateFailover();

      // Validate data integrity
      await this.validateDataIntegrity();

      // Cleanup test environment
      await this.cleanupTestEnvironment();

      logger.info('Disaster recovery test completed successfully');
    } catch (error) {
      logger.error('Disaster recovery test failed', error instanceof Error ? error : new Error('Unknown error'));
      throw error;
    }
  }

  private async updateDNS(region: 'primary' | 'backup'): Promise<void> {
    // Implement DNS update logic
    // This would typically use Route 53 or similar DNS service
  }

  private async scaleInfrastructure(region: 'primary' | 'backup', replicas: number): Promise<void> {
    // Implement infrastructure scaling logic
    // This would typically use Kubernetes or similar orchestration platform
  }

  private async getLatestBackup(): Promise<string | null> {
    // Implement logic to get latest backup
    return 'backups/database/latest-backup.sql.gz';
  }

  private async syncDataToPrimary(): Promise<void> {
    // Implement data synchronization logic
  }

  private async createTestEnvironment(): Promise<void> {
    // Implement test environment creation
  }

  private async simulateFailover(): Promise<void> {
    // Implement failover simulation
  }

  private async validateDataIntegrity(): Promise<void> {
    // Implement data validation logic
  }

  private async cleanupTestEnvironment(): Promise<void> {
    // Implement test environment cleanup
  }
}

export { DisasterRecoveryService };
```

## 总结

DevOps集成是Next.js应用成功部署和运维的关键。通过实施本文介绍的最佳实践，你可以：

1. **建立完善的CI/CD管道**：自动化测试、构建和部署流程
2. **实现基础设施即代码**：使用Terraform和Kubernetes管理基础设施
3. **加强监控与可观测性**：实时监控应用性能和健康状态
4. **实施灾难恢复策略**：确保业务连续性和数据安全
5. **遵循最佳实践**：提高运维效率和系统可靠性

这些实践将帮助你构建一个高效、可靠、安全的Next.js应用部署和运维体系。