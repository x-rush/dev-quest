# Next.js 15 CI/CD 流水线完全指南

> **文档简介**: Next.js 15 + 现代CI/CD流水线完整指南，涵盖GitHub Actions、自动化测试、多环境部署、代码质量检查、安全扫描等企业级CI/CD实践

> **目标读者**: 具备Next.js基础的开发者，需要掌握企业级CI/CD流水线设计和DevOps实践的工程师

> **前置知识**: Next.js 15基础、Git版本控制、Docker基础、CI/CD概念、Linux基础

> **预计时长**: 6-8小时

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `deployment` |
| **难度** | ⭐⭐⭐⭐ (4/5星) |
| **标签** | `#ci-cd` `#github-actions` `#automation` `#testing` `#deployment` `#devops` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标

### 🔄 企业级CI/CD流水线
- 掌握GitHub Actions企业级工作流设计和优化
- 实现完整的自动化测试和质量检查流水线
- 构建多环境部署和自动化发布策略
- 实现代码安全扫描和漏洞检测集成
- 掌握容器化构建和镜像管理最佳实践
- 建立完整的监控和告警机制

### 🚀 自动化质量保证
- 实现代码质量检查和格式化自动化
- 构建单元测试、集成测试、E2E测试流水线
- 实现性能测试和回归检测自动化
- 掌握依赖安全扫描和许可证合规检查
- 构建代码覆盖率统计和质量报告
- 建立质量门禁和发布策略

### 🛠️ DevOps最佳实践
- 实施基础设施即代码和配置管理
- 掌握蓝绿部署和金丝雀发布策略
- 构建故障回滚和应急响应机制
- 实现日志聚合和分析自动化
- 掌握团队协作和权限管理最佳实践
- 建立可观测性和性能监控体系

## 📖 概述

Next.js 15 应用的CI/CD流水线是现代软件工程的核心组成部分，直接影响开发效率、代码质量和系统稳定性。本指南深入探讨企业级CI/CD实践，从基础的工作流配置到复杂的部署策略，涵盖质量保证、安全扫描、监控告警等全方位内容，帮助你构建世界级的自动化交付体系。

## 🏗️ CI/CD 架构概览

### 流水线架构设计

```
┌─────────────────────────────────────────────────────────┐
│                     代码提交阶段                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │  Git Push   │ │  PR Created │ │  Tag Push   │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                     构建和测试阶段                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │ Code Quality │ │  Unit Tests  │ │ Build Images │         │
│  │   Checks    │ │  E2E Tests   │ │ Security Scan│         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                     部署阶段                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │   Staging    │ │ Production  │ │  Monitoring  │         │
│  │ Deployment  │ │ Deployment  │ │    Alert     │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
└─────────────────────────────────────────────────────────┘
```

## 🔄 GitHub Actions 工作流

### 基础工作流配置

#### 📋 .github/workflows/ci.yml
```yaml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  NODE_VERSION: '20'
  CACHE_VERSION: 'v1'

jobs:
  # 代码质量检查
  quality:
    name: Code Quality
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Type check
        run: npm run type-check

      - name: ESLint
        run: npm run lint

      - name: Prettier check
        run: npm run format:check

      - name: Check formatting
        run: npm run format:verify

  # 单元测试
  test:
    name: Unit Tests
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm run test:coverage

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info
          flags: unittests
          name: codecov-umbrella

  # 安全扫描
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run npm audit
        run: npm audit --audit-level high

      - name: Run Snyk security scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  # 构建应用
  build:
    name: Build Application
    runs-on: ubuntu-latest
    needs: [quality, test]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build application
        run: npm run build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-artifacts
          path: |
            .next/
            public/
            package.json
          retention-days: 1

  # E2E测试
  e2e:
    name: End-to-End Tests
    runs-on: ubuntu-latest
    needs: [build]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: build-artifacts

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright
        run: npx playwright install --with-deps

      - name: Run E2E tests
        run: npm run test:e2e

      - name: Upload E2E test results
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

#### 🚀 .github/workflows/deploy.yml
```yaml
name: Deploy Application

on:
  push:
    branches: [main]
    tags: ['v*']
  workflow_dispatch:

env:
  NODE_VERSION: '20'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # 构建和推送Docker镜像
  build-and-push:
    name: Build and Push Docker Image
    runs-on: ubuntu-latest
    outputs:
      image-digest: ${{ steps.build.outputs.digest }}
      image-tag: ${{ steps.meta.outputs.tags }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

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
            type=raw,value=latest,enable={{is_default_branch}}
          flavor: latest=true

      - name: Build and push Docker image
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            NEXT_PUBLIC_BUILD_DATE=${{ github.sha }}
            NEXT_PUBLIC_BUILD_VERSION=${{ github.ref_name }}

  # 部署到Staging环境
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [build-and-push]
    if: github.ref == 'refs/heads/develop'
    environment:
      name: staging
      url: https://staging.example.com
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to staging
        run: |
          echo "Deploying to staging environment..."
          echo "Image: ${{ needs.build-and-push.outputs.image-tag }}"
          # 这里添加实际的部署脚本

      - name: Run health check
        run: |
          sleep 30
          curl -f https://staging.example.com/api/health

  # 部署到生产环境
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [build-and-push]
    if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')
    environment:
      name: production
      url: https://example.com
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to production
        run: |
          echo "Deploying to production environment..."
          echo "Image: ${{ needs.build-and-push.outputs.image-tag }}"
          # 这里添加实际的部署脚本

      - name: Run health check
        run: |
          sleep 60
          curl -f https://example.com/api/health

      - name: Notify deployment
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: "🚀 Production deployment completed successfully!"
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}

  # 性能测试
  performance-test:
    name: Performance Test
    runs-on: ubuntu-latest
    needs: [deploy-production]
    if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Install Lighthouse CI
        run: npm install -g @lhci/cli@0.12.x

      - name: Run Lighthouse CI
        run: lhci autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}
          LHCI_SERVER_URL: ${{ secrets.LHCI_SERVER_URL }}

  # 发布通知
  notify:
    name: Notify Release
    runs-on: ubuntu-latest
    needs: [deploy-production, performance-test]
    if: always() && github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')
    steps:
      - name: Create GitHub Release
        if: needs.deploy-production.result == 'success'
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref_name }}
          release_name: Release ${{ github.ref_name }}
          draft: false
          prerelease: false

      - name: Notify team
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: |
            🎉 New version released!
            Version: ${{ github.ref_name }}
            Deploy status: ${{ needs.deploy-production.result }}
            Performance status: ${{ needs.performance-test.result }}
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 高级工作流配置

#### 🏗️ .github/workflows/advanced-ci.yml
```yaml
name: Advanced CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  schedule:
    - cron: '0 2 * * *' # 每天凌晨2点运行

env:
  NODE_VERSION: '20'
  TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}

jobs:
  # 并行矩阵测试
  test-matrix:
    name: Test Matrix
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        node-version: [18, 20]
        os: [ubuntu-latest, windows-latest]
        browser: [chromium, firefox, webkit]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}

      - name: Get npm cache directory
        id: npm-cache-dir
        run: echo "dir=$(npm config get cache)" >> $GITHUB_OUTPUT

      - name: Cache npm dependencies
        uses: actions/cache@v3
        with:
          path: ${{ steps.npm-cache-dir.outputs.dir }}
          key: ${{ runner.os }}-node-${{ matrix.node-version }}-${{ hashFiles('**/package-lock.json') }}
          restore-keys: |
            ${{ runner.os }}-node-${{ matrix.node-version }}-

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm run test

  # 依赖缓存和优化
  optimized-build:
    name: Optimized Build
    runs-on: ubuntu-latest
    outputs:
      build-time: ${{ steps.build.outputs.time }}
      build-size: ${{ steps.size.outputs.size }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Cache Turbopack
        uses: actions/cache@v3
        with:
          path: |
            .turbo
            node_modules/.cache
          key: ${{ runner.os }}-turbo-${{ hashFiles('**/package-lock.json') }}
          restore-keys: |
            ${{ runner.os }}-turbo-

      - name: Install dependencies
        run: npm ci

      - name: Build with Turbopack
        id: build
        run: |
          start_time=$(date +%s)
          npm run build
          end_time=$(date +%s)
          build_time=$((end_time - start_time))
          echo "time=$build_time" >> $GITHUB_OUTPUT

      - name: Calculate build size
        id: size
        run: |
          size=$(du -sh .next | cut -f1)
          echo "size=$size" >> $GITHUB_OUTPUT

      - name: Build optimization report
        run: |
          echo "## Build Optimization Report" >> $GITHUB_STEP_SUMMARY
          echo "| Metric | Value |" >> $GITHUB_STEP_SUMMARY
          echo "|--------|-------|" >> $GITHUB_STEP_SUMMARY
          echo "| Build Time | ${{ steps.build.outputs.time }}s |" >> $GITHUB_STEP_SUMMARY
          echo "| Build Size | ${{ steps.size.outputs.size }} |" >> $GITHUB_STEP_SUMMARY

  # 代码安全深度扫描
  deep-security-scan:
    name: Deep Security Scan
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Run CodeQL Analysis
        uses: github/codeql-action/init@v2
        with:
          languages: javascript

      - name: Autobuild
        uses: github/codeql-action/autobuild@v2

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2

  # 依赖许可证检查
  license-check:
    name: License Check
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Install dependencies
        run: npm ci

      - name: Check licenses
        run: |
          npx license-checker --onlyAllow 'MIT;Apache-2.0;BSD-2-Clause;BSD-3-Clause;0BSD' || exit 1

      - name: Generate license report
        run: npm run licenses:report

      - name: Upload license report
        uses: actions/upload-artifact@v3
        with:
          name: license-report
          path: license-report.json
```

## 🧪 测试配置

### 测试套件设置

#### 📋 vitest.config.ts
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/coverage/**',
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80,
        },
      },
    },
    include: [
      'tests/**/*.{test,spec}.{js,ts,jsx,tsx}',
      'src/**/*.{test,spec}.{js,ts,jsx,tsx}',
    ],
    exclude: [
      'node_modules/',
      'dist/',
      '.next/',
      '**/*.config.*',
    ],
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@/components': resolve(__dirname, './src/components'),
      '@/lib': resolve(__dirname, './src/lib'),
      '@/app': resolve(__dirname, './src/app'),
    },
  },
})
```

#### 🎭 playwright.config.ts
```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'playwright-report/results.json' }],
    ['junit', { outputFile: 'playwright-report/results.xml' }],
  ],
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  webServer: {
    command: 'npm run build && npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
})
```

## 📊 质量门禁配置

### 代码质量标准

#### 📋 .github/workflows/quality-gate.yml
```yaml
name: Quality Gate

on:
  pull_request:
    branches: [main]

jobs:
  quality-check:
    name: Quality Gate Check
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Run ESLint
        id: eslint
        run: |
          npm run lint --format=json > eslint-report.json || echo "ESLint issues found"
          eslint_count=$(cat eslint-report.json | jq '.[].messages | length' || echo "0")
          echo "count=$eslint_count" >> $GITHUB_OUTPUT

      - name: Check test coverage
        id: coverage
        run: |
          npm run test:coverage
          coverage=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
          echo "coverage=$coverage" >> $GITHUB_OUTPUT

      - name: Run bundle analysis
        id: bundle
        run: |
          npm run build
          size=$(du -sh .next | cut -f1)
          echo "size=$size" >> $GITHUB_OUTPUT

      - name: Quality Gate Validation
        run: |
          # 质量门禁标准
          MIN_COVERAGE=80
          MAX_ESLINT_ERRORS=10
          MAX_BUNDLE_SIZE="50M"

          # 检查代码覆盖率
          COVERAGE=${{ steps.coverage.outputs.coverage }}
          if (( $(echo "$COVERAGE < $MIN_COVERAGE" | bc -l) )); then
            echo "❌ Coverage check failed: $COVERAGE% < $MIN_COVERAGE%"
            exit 1
          fi

          # 检查ESLint错误
          ESLINT_COUNT=${{ steps.eslint.outputs.count }}
          if [[ $ESLINT_COUNT -gt $MAX_ESLINT_ERRORS ]]; then
            echo "❌ ESLint check failed: $ESLINT_COUNT errors > $MAX_ESLINT_ERRORS"
            exit 1
          fi

          # 检查Bundle大小
          # 简化的大小比较，实际项目中需要更复杂的逻辑
          BUNDLE_SIZE=${{ steps.bundle.outputs.size }}
          echo "✅ All quality checks passed!"

      - name: Comment PR with quality metrics
        uses: actions/github-script@v6
        with:
          script: |
            const eslintCount = ${{ steps.eslint.outputs.count }};
            const coverage = ${{ steps.coverage.outputs.coverage }};
            const bundleSize = '${{ steps.bundle.outputs.size }}';

            const comment = `
            ## 📊 Quality Metrics

            | Metric | Value | Status |
            |--------|-------|--------|
            | ESLint Errors | ${eslintCount} | ${eslintCount <= 10 ? '✅' : '❌'} |
            | Test Coverage | ${coverage}% | ${coverage >= 80 ? '✅' : '❌'} |
            | Bundle Size | ${bundleSize} | ${bundleSize <= '50M' ? '✅' : '❌'} |

            ${eslintCount <= 10 && coverage >= 80 && bundleSize <= '50M' ? '✅ Quality gate passed!' : '❌ Quality gate failed!'}
            `;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

## 🚀 多环境部署策略

### 环境配置管理

#### 📄 .github/workflows/multi-deploy.yml
```yaml
name: Multi-Environment Deployment

on:
  push:
    branches: [main, develop]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production
      force_deploy:
        description: 'Force deployment (skip quality checks)'
        required: false
        default: false
        type: boolean

env:
  NODE_VERSION: '20'

jobs:
  # 环境变量验证
  validate-env:
    name: Validate Environment
    runs-on: ubuntu-latest
    outputs:
      deploy-to-prod: ${{ steps.decision.outputs.deploy-to-prod }}
    steps:
      - name: Determine deployment target
        id: decision
        run: |
          if [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
            if [[ "${{ github.event_name }}" == "workflow_dispatch" ]]; then
              echo "deploy-to-prod=${{ github.event.inputs.environment == 'production' }}" >> $GITHUB_OUTPUT
            else
              echo "deploy-to-prod=false" >> $GITHUB_OUTPUT
            fi
          else
            echo "deploy-to-prod=false" >> $GITHUB_OUTPUT
          fi

  # Staging环境部署
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [validate-env]
    if: needs.validate-env.outputs.deploy-to-prod == 'false'
    environment:
      name: staging
      url: https://staging.example.com
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: false
          load: true
          tags: nextjs-app:staging
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Deploy to staging
        run: |
          echo "Deploying to staging..."
          docker-compose -f docker-compose.staging.yml up -d

      - name: Health check
        run: |
          timeout 300 bash -c 'until curl -f https://staging.example.com/api/health; do sleep 5; done'

      - name: Run smoke tests
        run: |
          npm run test:smoke -- --base-url=https://staging.example.com

  # 生产环境部署
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [validate-env]
    if: needs.validate-env.outputs.deploy-to-prod == 'true'
    environment:
      name: production
      url: https://example.com
    steps:
      - name: Create deployment issue
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `🚀 Production Deployment - ${new Date().toISOString()}`,
              body: `Starting production deployment for commit: ${context.sha}`,
              labels: ['deployment', 'production']
            });

      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ secrets.REGISTRY_URL }}
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ secrets.REGISTRY_URL }}/nextjs-app:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Blue-green deployment
        run: |
          echo "Starting blue-green deployment..."

          # 创建新环境
          docker-compose -f docker-compose.prod.yml -p blue up -d

          # 等待新环境就绪
          timeout 600 bash -c 'until curl -f http://blue.example.com/api/health; do sleep 10; done'

          # 运行健康检查
          npm run test:health -- --base-url=http://blue.example.com

          # 切换流量
          # 这里添加实际的流量切换逻辑

          # 清理旧环境
          docker-compose -f docker-compose.prod.yml -p green down

      - name: Post-deployment verification
        run: |
          echo "Running post-deployment verification..."

          # 基础健康检查
          curl -f https://example.com/api/health

          # 关键功能测试
          npm run test:smoke -- --base-url=https://example.com

          # 性能检查
          npm run test:performance -- --base-url=https://example.com

      - name: Update deployment issue
        if: always()
        uses: actions/github-script@v6
        with:
          script: |
            const status = '${{ job.status }}';
            const title = status === 'success'
              ? '✅ Production Deployment Completed'
              : '❌ Production Deployment Failed';

            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: title,
              body: `Deployment status: ${status}\nCommit: ${context.sha}`,
              labels: ['deployment', 'production']
            });

  # 回滚机制
  rollback:
    name: Emergency Rollback
    runs-on: ubuntu-latest
    needs: [deploy-production]
    if: failure() && needs.deploy-production.result == 'failure'
    environment:
      name: production
    steps:
      - name: Execute rollback
        run: |
          echo "🚨 Executing emergency rollback..."

          # 停止新版本
          docker-compose -f docker-compose.prod.yml -p blue down

          # 恢复上一版本
          docker-compose -f docker-compose.prod.yml -p green up -d

          # 等待服务恢复
          timeout 300 bash -c 'until curl -f https://example.com/api/health; do sleep 10; done'

          echo "✅ Rollback completed"

      - name: Notify rollback
        uses: 8398a7/action-slack@v3
        with:
          status: custom
          text: "🚨 Production deployment failed and was rolled back!"
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## 📈 监控和告警

### 集成监控系统

#### 📊 .github/workflows/monitoring.yml
```yaml
name: Monitoring Integration

on:
  schedule:
    - cron: '*/15 * * * *' # 每15分钟运行
  workflow_dispatch:

jobs:
  # 性能监控
  performance-monitoring:
    name: Performance Monitoring
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run Lighthouse CI
        uses: treosh/lighthouse-ci-action@v9
        with:
          urls: |
            https://example.com
            https://example.com/dashboard
            https://example.com/api/health
          configPath: './.lighthouserc.json'
          uploadArtifacts: true
          temporaryPublicStorage: true

      - name: Analyze performance trends
        run: |
          echo "Analyzing performance trends..."
          # 这里添加性能趋势分析逻辑

  # 可用性检查
  availability-check:
    name: Availability Check
    runs-on: ubuntu-latest
    steps:
      - name: Check service availability
        run: |
          services=("https://example.com" "https://api.example.com/health" "https://staging.example.com")

          for service in "${services[@]}"; do
            if ! curl -f -s "$service" > /dev/null; then
              echo "❌ Service unavailable: $service"

              # 发送告警
              curl -X POST -H 'Content-type: application/json' \
                --data "{\"text\":\"🚨 Service Down: $service\"}" \
                "${{ secrets.SLACK_WEBHOOK_URL }}"

              exit 1
            else
              echo "✅ Service available: $service"
            fi
          done

  # 资源使用监控
  resource-monitoring:
    name: Resource Monitoring
    runs-on: ubuntu-latest
    steps:
      - name: Monitor resource usage
        run: |
          echo "Checking resource usage..."

          # 检查磁盘使用
          disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
          if [[ $disk_usage -gt 85 ]]; then
            echo "⚠️ High disk usage: ${disk_usage}%"
          fi

          # 检查内存使用
          mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
          if [[ $mem_usage -gt 90 ]]; then
            echo "⚠️ High memory usage: ${mem_usage}%"
          fi

      - name: Generate monitoring report
        run: |
          echo "## 📊 Monitoring Report" >> $GITHUB_STEP_SUMMARY
          echo "| Metric | Status |" >> $GITHUB_STEP_SUMMARY
          echo "|--------|--------|" >> $GITHUB_STEP_SUMMARY
          echo "| Service Availability | ✅ All services operational |" >> $GITHUB_STEP_SUMMARY
          echo "| Resource Usage | ✅ Within normal limits |" >> $GITHUB_STEP_SUMMARY
          echo "| Performance | ✅ Meeting SLA requirements |" >> $GITHUB_STEP_SUMMARY
```

## 📋 最佳实践清单

### ✅ CI/CD流水线设计
- [ ] 实现多阶段构建和并行执行
- [ ] 配置智能缓存策略
- [ ] 设置质量门禁和自动化检查
- [ ] 实现失败重试和错误处理
- [ ] 建立完整的测试覆盖

### ✅ 测试策略
- [ ] 单元测试、集成测试、E2E测试
- [ ] 代码覆盖率统计和质量报告
- [ ] 性能测试和回归检测
- [ ] 安全测试和漏洞扫描
- [ ] 自动化烟雾测试

### ✅ 部署策略
- [ ] 多环境部署配置管理
- [ ] 蓝绿部署和金丝雀发布
- [ ] 自动化回滚和故障恢复
- [ ] 健康检查和监控集成
- [ ] 零停机部署策略

### ✅ 安全和合规
- [ ] 代码安全扫描和漏洞检测
- [ ] 依赖安全审计和许可证检查
- [ ] 密钥管理和环境变量保护
- [ ] 访问控制和权限管理
- [ ] 安全告警和事件响应

## 🎯 总结

Next.js 15 CI/CD流水线是现代软件工程的核心实践，直接影响开发效率、代码质量和交付速度。通过合理设计工作流、配置自动化测试、实施质量门禁，可以构建可靠的自动化交付体系。

## 🔗 相关资源链接

### 官方资源
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Next.js 部署文档](https://nextjs.org/docs/deployment)
- [Docker Hub](https://hub.docker.com/)
- [Kubernetes 文档](https://kubernetes.io/docs/)

### 技术文章
- [CI/CD 最佳实践](https://docs.github.com/en/actions/guides)
- [GitHub Actions 高级用法](https://docs.github.com/en/actions/learn-github-actions)
- [容器化部署策略](https://docs.docker.com/build/ci-cd/)
- [GitOps 工作流](https://www.weave.works/technologies/gitops/)

### 工具和资源
- [GitHub Marketplace](https://github.com/marketplace)
- [Docker Buildx](https://docs.docker.com/buildx/)
- [Helm 包管理](https://helm.sh/)
- [ArgoCD GitOps](https://argoproj.github.io/cd/)

## 📚 模块内相关文档

### 同模块相关文档
- [Vercel部署指南](./01-vercel-deployment.md) - Vercel平台的自动化部署集成
- [Docker容器化部署](./02-docker-containerization.md) - 容器化应用的CI/CD流水线
- [监控与分析](./04-monitoring-analytics.md) - CI/CD流水线的监控和报告

### 相关知识模块
- [框架相关模块](../frameworks/01-nextjs-15-complete.md) - Next.js 15的构建和部署集成
- [测试相关模块](../testing/01-unit-testing.md) - 单元测试在CI流水线中的集成
- [测试相关模块](../testing/03-e2e-testing.md) - E2E测试在CI/CD中的自动化执行

### 基础前置知识
- [Git版本控制](../../../00-javascript-foundation/basics/04-git-version-control.md) - Git工作流和分支策略
- [CI/CD基础概念](../../../01-react-foundation/advanced/12-cicd-fundamentals.md) - CI/CD的基本概念和工作原理
- [DevOps实践](../../../01-react-foundation/advanced/11-devops-practices.md) - DevOps文化和实践方法

---

## ✨ 总结

### 核心技术要点
1. **GitHub Actions工作流**: 现代化的CI/CD流水线设计和配置
2. **多环境部署**: 开发、测试、预生产、生产环境的自动化管理
3. **质量保证门禁**: 自动化测试、代码检查、安全扫描的集成
4. **容器化集成**: Docker构建、推送和部署的自动化流程
5. **高级流水线特性**: 矩阵构建、缓存优化、并行执行和GitOps

### 学习成果自检
- [ ] 理解CI/CD的核心概念和价值
- [ ] 掌握GitHub Actions的配置和工作流设计
- [ ] 能够构建多环境的自动化部署流水线
- [ ] 熟练集成质量保证和安全扫描工具
- [ ] 能够实施现代化的GitOps和容器化部署策略

---

## 🤝 贡献与反馈

### 贡献指南
欢迎提交Issue和Pull Request来改进本模块内容！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交变更 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

### 反馈渠道
- **问题反馈**: [GitHub Issues](https://github.com/your-username/dev-quest/issues)
- **内容建议**: [Discussion板块](https://github.com/your-username/dev-quest/discussions)
- **技术交流**: 欢迎提交PR或Issue参与讨论

### 贡献者
- Dev Quest Team - 核心内容开发
- 社区贡献者 - 内容完善和纠错

---

**📜 文档版本**: v1.0.0
**📅 最后更新**: 2025年10月
**🏷️ 标签**: `#ci-cd` `#github-actions` `#automation` `#devops` `#gitops`
**⭐ 推荐指数**: ⭐⭐⭐⭐⭐

**💡 提示**: 本模块专注于现代CI/CD实践，适合需要构建自动化部署流程的团队。

**🎯 学习建议**:
- 建议学习周期: 2-3周
- 理论与实践时间比例: 4:6
- 重点掌握GitHub Actions和多环境部署
- 结合实际项目构建完整的CI/CD流水线