# React应用性能测试指南 (Performance Testing Guide)

> **文档简介**: 从PHP开发者视角全面掌握Next.js 15应用的性能测试，涵盖Core Web Vitals、Bundle分析、负载测试等现代性能测试技术。

> **目标读者**: 具备React基础，希望系统学习应用性能测试的中高级开发者

> **前置知识**: React组件开发、性能优化基础、CI/CD概念

> **预计时长**: 4-5小时（理论学习）+ 3-4小时（实践练习）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `testing` |
| **难度** | ⭐⭐⭐⭐ (4/5星) |
| **标签** | `#performance-testing` `#lighthouse` `#core-web-vitals` `#bundle-analysis` `#nextjs15` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标

完成本模块后，你将能够：

- ✅ **掌握性能指标**: 理解Core Web Vitals和其他关键性能指标
- ✅ **使用Lighthouse CI**: 配置和集成自动化性能测试
- ✅ **Bundle分析**: 分析和优化应用打包大小
- ✅ **负载测试**: 实施应用的负载和压力测试
- ✅ **性能监控**: 建立持续的性能监控体系
- ✅ **优化验证**: 验证性能优化的效果

## 📖 概述

性能测试是现代Web应用开发中不可或缺的一环，它直接影响用户体验、转化率和SEO排名。对于Next.js应用来说，性能测试不仅包括传统的前端性能指标，还需要考虑SSR/SSG性能、路由切换性能、以及不同渲染模式的性能特征。

### 性能测试的重要性

1. **用户体验**: 快速的加载和交互提升用户满意度
2. **商业影响**: 性能提升直接影响转化率和收入
3. **SEO优化**: Core Web Vitals是Google搜索排名的重要因素
4. **资源利用**: 优化性能减少服务器和带宽成本
5. **竞争优势**: 更好的性能成为产品差异化因素

## 🛠️ 工具栈介绍

### 1. Lighthouse CI
**自动化性能测试**: 在CI/CD中集成Lighthouse性能审计

```bash
# 安装Lighthouse CI
npm install -D @lhci/cli@0.12.x

# 初始化配置
npx lhci autorun
```

**核心功能**:
- 自动化性能审计
- 性能回归检测
- 历史数据追踪
- 性能报告生成

### 2. Webpack Bundle Analyzer
**Bundle分析工具**: 可视化分析打包结果

```bash
# 安装Bundle Analyzer
npm install -D @next/bundle-analyzer
```

**分析能力**:
- 模块大小分析
- 依赖关系可视化
- 重复代码检测
- Tree-shaking效果验证

### 3. Core Web Vitals
**Google性能指标**: 量化用户体验的关键指标

**核心指标**:
- LCP (Largest Contentful Paint): 加载性能
- FID (First Input Delay): 交互性
- CLS (Cumulative Layout Shift): 视觉稳定性

### 4. WebPageTest
**在线性能测试**: 详细的性能分析和瀑布图

**测试功能**:
- 多地理位置测试
- 不同网络条件模拟
- 详细的瀑布图分析
- 性能优化建议

### 5. K6 Load Testing
**负载测试工具**: 现代化的负载和压力测试

```bash
# 安装K6
npm install -D k6

# 或全局安装
brew install k6  # macOS
```

## 🔧 环境配置

### 1. Lighthouse CI配置

```yaml
# .lighthouserc.js
module.exports = {
  ci: {
    collect: {
      url: [
        "http://localhost:3000",
        "http://localhost:3000/about",
        "http://localhost:3000/products",
      ],
      numberOfRuns: 3,
      settings: {
        chromeFlags: "--no-sandbox --headless",
        preset: "desktop",
        throttling: {
          rttMs: 40,
          throughputKbps: 10240,
          cpuSlowdownMultiplier: 1,
          requestLatencyMs: 0,
          downloadThroughputKbps: 0,
          uploadThroughputKbps: 0,
        },
      },
    },
    assert: {
      assertions: {
        "categories:performance": ["warn", { minScore: 0.8 }],
        "categories:accessibility": ["error", { minScore: 0.9 }],
        "categories:best-practices": ["warn", { minScore: 0.8 }],
        "categories:seo": ["warn", { minScore: 0.8 }],
        "categories:pwa": "off",
      },
    },
    upload: {
      target: "temporary-public-storage",
    },
  },
}
```

### 2. Next.js性能配置

```typescript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  // 启用Bundle Analyzer
  webpack: (config, { isServer }) => {
    if (process.env.ANALYZE === 'true') {
      const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer')
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'server',
          analyzerPort: 8888,
          openAnalyzer: true,
        })
      )
    }
    return config
  },

  // 性能优化配置
  experimental: {
    // 启用App Router (Next.js 13+)
    appDir: true,
    // 优化字体加载
    fontLoaders: [
      { loader: '@next/font/google', options: { subsets: ['latin'] } },
    ],
  },

  // 图片优化
  images: {
    formats: ['image/webp', 'image/avif'],
    domains: ['example.com'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // 压缩配置
  compress: true,

  // 实验性功能
  swcMinify: true,

  // 构建优化
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
}

module.exports = nextConfig
```

### 3. 性能测试脚本

```bash
#!/bin/bash
# scripts/performance-test.sh

set -e

echo "🚀 Starting performance tests..."

# 启动应用
npm run dev &
APP_PID=$!

# 等待应用启动
sleep 10

# 运行Lighthouse CI
echo "📊 Running Lighthouse CI..."
npx lhci autorun

# 生成Bundle分析
echo "📦 Analyzing bundle size..."
ANALYZE=true npm run build

# 运行Core Web Vitals测试
echo "🎯 Testing Core Web Vitals..."
npm run test:vitals

# 清理
kill $APP_PID

echo "✅ Performance tests completed!"
```

## 📋 测试策略

### Core Web Vitals测试策略

**LCP优化验证**:
- 测量主要内容的加载时间
- 验证图片优化效果
- 检查字体加载策略
- 评估SSR/SSG性能

**FID优化验证**:
- 测量首次交互延迟
- 验证JavaScript执行时间
- 检查主线程阻塞情况
- 评估代码分割效果

**CLS优化验证**:
- 检查布局稳定性
- 验证图片尺寸设置
- 评估字体加载策略
- 检查动态内容插入

### Bundle分析策略

**大小分析**:
- 初始Bundle大小
- 路由级Bundle大小
- 第三方库大小
- 代码分割效果

**依赖分析**:
- 重复依赖检测
- Tree-shaking效果
- 按需加载验证
- Polyfill优化

### 负载测试策略

**并发用户测试**:
- 模拟真实用户访问
- 测试服务器响应能力
- 验证缓存效果
- 检查错误率

**压力测试**:
- 极限负载测试
- 系统稳定性验证
- 性能瓶颈识别
- 降级策略验证

## 💻 实战示例

### 基础性能测试示例

#### 1. Lighthouse CI集成

```typescript
// scripts/lighthouse.js
const { spawn } = require('child_process')
const path = require('path')

const runLighthouse = async (url, outputPath) => {
  return new Promise((resolve, reject) => {
    const lighthouse = spawn('npx', [
      'lighthouse',
      url,
      '--output=json',
      '--output-path=' + outputPath,
      '--chrome-flags="--headless"',
      '--quiet'
    ])

    lighthouse.stdout.on('data', (data) => {
      console.log(`Lighthouse: ${data}`)
    })

    lighthouse.stderr.on('data', (data) => {
      console.error(`Lighthouse Error: ${data}`)
    })

    lighthouse.on('close', (code) => {
      if (code === 0) {
        resolve()
      } else {
        reject(new Error(`Lighthouse exited with code ${code}`))
      }
    })
  })
}

const main = async () => {
  const urls = [
    'http://localhost:3000',
    'http://localhost:3000/about',
    'http://localhost:3000/products'
  ]

  for (const url of urls) {
    const filename = path.basename(url) || 'home'
    const outputPath = `./lighthouse-results/${filename}.json`

    console.log(`Running Lighthouse for ${url}...`)
    await runLighthouse(url, outputPath)
    console.log(`✅ Results saved to ${outputPath}`)
  }
}

main().catch(console.error)
```

#### 2. Core Web Vitals监控

```typescript
// lib/vitals.ts
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'

function sendToAnalytics(metric: any) {
  // 发送到分析服务
  if (process.env.NEXT_PUBLIC_ANALYTICS_ENDPOINT) {
    fetch(process.env.NEXT_PUBLIC_ANALYTICS_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(metric),
    })
  }

  // 本地开发时输出到控制台
  if (process.env.NODE_ENV === 'development') {
    console.log('[Web Vitals]', metric)
  }
}

export function reportWebVitals() {
  getCLS(sendToAnalytics)
  getFID(sendToAnalytics)
  getFCP(sendToAnalytics)
  getLCP(sendToAnalytics)
  getTTFB(sendToAnalytics)
}

// 自定义性能指标
export function measurePageLoad() {
  if (typeof window !== 'undefined') {
    window.addEventListener('load', () => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
      const loadTime = navigation.loadEventEnd - navigation.fetchStart

      console.log(`Page load time: ${loadTime}ms`)

      // 发送到分析服务
      sendToAnalytics({
        name: 'page-load-time',
        value: loadTime,
        timestamp: Date.now(),
      })
    })
  }
}
```

```typescript
// pages/_app.tsx
import { reportWebVitals, measurePageLoad } from '@/lib/vitals'

function MyApp({ Component, pageProps }: AppProps) {
  useEffect(() => {
    reportWebVitals()
    measurePageLoad()
  }, [])

  return <Component {...pageProps} />
}

export default MyApp
```

#### 3. Bundle分析工具

```typescript
// scripts/analyze-bundle.js
const { execSync } = require('child_process')
const fs = require('fs')
const path = require('path')

const analyzeBundle = () => {
  console.log('📦 Analyzing bundle size...')

  // 构建应用并生成分析报告
  execSync('ANALYZE=true npm run build', { stdio: 'inherit' })

  // 读取构建统计信息
  const buildStats = JSON.parse(
    fs.readFileSync('./.next/build-manifest.json', 'utf8')
  )

  // 分析各页面Bundle大小
  const bundleAnalysis = {}

  Object.keys(buildStats.pages).forEach(page => {
    const pageBundles = buildStats.pages[page]
    const totalSize = pageBundles.reduce((sum, bundle) => {
      const bundlePath = path.join('.next', bundle)
      if (fs.existsSync(bundlePath)) {
        const stats = fs.statSync(bundlePath)
        return sum + stats.size
      }
      return sum
    }, 0)

    bundleAnalysis[page] = {
      bundles: pageBundles,
      totalSize: (totalSize / 1024).toFixed(2) + ' KB'
    }
  })

  // 生成分析报告
  const report = {
    timestamp: new Date().toISOString(),
    bundleAnalysis,
    recommendations: generateRecommendations(bundleAnalysis)
  }

  fs.writeFileSync(
    './bundle-analysis.json',
    JSON.stringify(report, null, 2)
  )

  console.log('✅ Bundle analysis completed!')
  console.log('📄 Report saved to bundle-analysis.json')
}

function generateRecommendations(analysis) {
  const recommendations = []

  Object.entries(analysis).forEach(([page, data]) => {
    const sizeInKB = parseFloat(data.totalSize)

    if (sizeInKB > 500) {
      recommendations.push({
        page,
        issue: 'Large bundle size',
        suggestion: 'Consider code splitting or lazy loading',
        size: data.totalSize
      })
    }

    if (data.bundles.length > 3) {
      recommendations.push({
        page,
        issue: 'Too many bundles',
        suggestion: 'Optimize bundle splitting strategy',
        bundles: data.bundles.length
      })
    }
  })

  return recommendations
}

if (require.main === module) {
  analyzeBundle()
}

module.exports = { analyzeBundle, generateRecommendations }
```

### 高级性能测试场景

#### 1. 自定义性能指标测试

```typescript
// __tests__/performance/custom-metrics.test.ts
import { test, expect } from '@playwright/test'

test.describe('Custom Performance Metrics', () => {
  test('should meet custom performance thresholds', async ({ page }) => {
    // 导航到页面
    await page.goto('/')

    // 等待页面完全加载
    await page.waitForLoadState('networkidle')

    // 获取性能指标
    const metrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming

      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.fetchStart,
        loadComplete: navigation.loadEventEnd - navigation.fetchStart,
        firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
        firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0,
      }
    })

    // 验证自定义指标
    expect(metrics.domContentLoaded).toBeLessThan(1500)
    expect(metrics.loadComplete).toBeLessThan(3000)
    expect(metrics.firstContentfulPaint).toBeLessThan(1000)

    console.log('Performance metrics:', metrics)
  })

  test('should measure component render performance', async ({ page }) => {
    await page.goto('/')

    // 测量复杂组件的渲染时间
    const renderTime = await page.evaluate(async () => {
      const startTime = performance.now()

      // 触发复杂组件渲染
      const button = document.querySelector('[data-testid="load-complex-component"]')
      if (button) {
        button.click()

        // 等待组件渲染完成
        await new Promise(resolve => {
          const observer = new MutationObserver((mutations) => {
            const complexComponent = document.querySelector('[data-testid="complex-component"]')
            if (complexComponent) {
              observer.disconnect()
              resolve()
            }
          })
          observer.observe(document.body, { childList: true, subtree: true })
        })
      }

      return performance.now() - startTime
    })

    expect(renderTime).toBeLessThan(500)
    console.log(`Complex component render time: ${renderTime}ms`)
  })
})
```

#### 2. 内存泄漏检测

```typescript
// __tests__/performance/memory-leaks.test.ts
import { test, expect } from '@playwright/test'

test.describe('Memory Leak Detection', () => {
  test('should not have memory leaks during navigation', async ({ page }) => {
    await page.goto('/')

    // 启用内存监控
    await page.goto('chrome://memory-internals')

    const initialMemory = await page.evaluate(() => {
      return (performance as any).memory?.usedJSHeapSize || 0
    })

    // 执行多次导航
    for (let i = 0; i < 10; i++) {
      await page.goto('/')
      await page.waitForLoadState('networkidle')
      await page.goto('/about')
      await page.waitForLoadState('networkidle')
    }

    // 强制垃圾回收
    await page.evaluate(() => {
      if (window.gc) {
        window.gc()
      }
    })

    const finalMemory = await page.evaluate(() => {
      return (performance as any).memory?.usedJSHeapSize || 0
    })

    const memoryIncrease = finalMemory - initialMemory
    const memoryIncreasePercent = (memoryIncrease / initialMemory) * 100

    // 内存增长不应超过50%
    expect(memoryIncreasePercent).toBeLessThan(50)

    console.log(`Memory increase: ${memoryIncreasePercent.toFixed(2)}%`)
  })
})
```

#### 3. 负载测试脚本

```javascript
// tests/load/k6-test.js
import http from 'k6/http'
import { check, sleep } from 'k6'
import { Rate } from 'k6/metrics'

// 自定义指标
const errorRate = new Rate('errors')

// 测试配置
export const options = {
  stages: [
    { duration: '2m', target: 100 }, // 2分钟内增加到100用户
    { duration: '5m', target: 100 }, // 保持100用户5分钟
    { duration: '2m', target: 200 }, // 2分钟内增加到200用户
    { duration: '5m', target: 200 }, // 保持200用户5分钟
    { duration: '2m', target: 0 },   // 2分钟内减少到0用户
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95%的请求响应时间小于500ms
    http_req_failed: ['rate<0.1'],    // 错误率小于10%
    errors: ['rate<0.1'],             // 自定义错误率小于10%
  },
}

const BASE_URL = 'http://localhost:3000'

export default function () {
  // 测试首页
  const homeResponse = http.get(`${BASE_URL}/`)
  const homeSuccess = check(homeResponse, {
    'home page status is 200': (r) => r.status === 200,
    'home page response time < 500ms': (r) => r.timings.duration < 500,
  })
  errorRate.add(!homeSuccess)

  sleep(1)

  // 测试产品页面
  const productResponse = http.get(`${BASE_URL}/products`)
  const productSuccess = check(productResponse, {
    'products page status is 200': (r) => r.status === 200,
    'products page response time < 800ms': (r) => r.timings.duration < 800,
  })
  errorRate.add(!productSuccess)

  sleep(1)

  // 测试API端点
  const apiResponse = http.get(`${BASE_URL}/api/products`)
  const apiSuccess = check(apiResponse, {
    'API status is 200': (r) => r.status === 200,
    'API response time < 300ms': (r) => r.timings.duration < 300,
    'API returns products': (r) => JSON.parse(r.body).length > 0,
  })
  errorRate.add(!apiSuccess)

  sleep(2)
}

export function handleSummary(data) {
  return {
    'load-test-summary.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  }
}
```

#### 4. 性能回归检测

```typescript
// __tests__/performance/performance-regression.test.ts
import { test, expect } from '@playwright/test'
import fs from 'fs'
import path from 'path'

interface PerformanceBaseline {
  url: string
  metrics: {
    firstContentfulPaint: number
    largestContentfulPaint: number
    cumulativeLayoutShift: number
    firstInputDelay: number
  }
  timestamp: string
}

test.describe('Performance Regression Detection', () => {
  const BASELINE_FILE = './performance-baseline.json'

  test('should not regress from baseline performance', async ({ page }) => {
    const url = '/'

    // 测量当前性能
    await page.goto(url)
    await page.waitForLoadState('networkidle')

    const currentMetrics = await page.evaluate(() => {
      return new Promise((resolve) => {
        const metrics = {
          firstContentfulPaint: 0,
          largestContentfulPaint: 0,
          cumulativeLayoutShift: 0,
          firstInputDelay: 0,
        }

        // 监听LCP
        new PerformanceObserver((list) => {
          const entries = list.getEntries()
          const lastEntry = entries[entries.length - 1]
          metrics.largestContentShift = lastEntry.startTime
        }).observe({ entryTypes: ['largest-contentful-paint'] })

        // 监听CLS
        new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (!entry.hadRecentInput) {
              metrics.cumulativeLayoutShift += entry.value
            }
          }
        }).observe({ entryTypes: ['layout-shift'] })

        // 监听FID
        new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            metrics.firstInputDelay = entry.processingStart - entry.startTime
          }
        }).observe({ entryTypes: ['first-input'] })

        // 获取FCP
        const fcpEntry = performance.getEntriesByName('first-contentful-paint')[0]
        if (fcpEntry) {
          metrics.firstContentfulPaint = fcpEntry.startTime
        }

        // 等待一段时间收集所有指标
        setTimeout(() => resolve(metrics), 3000)
      })
    })

    // 读取基准数据
    let baseline: PerformanceBaseline | null = null
    if (fs.existsSync(BASELINE_FILE)) {
      baseline = JSON.parse(fs.readFileSync(BASELINE_FILE, 'utf8'))
    }

    if (baseline) {
      // 比较性能指标
      const regressionThreshold = 0.1 // 10%的回归阈值

      expect(currentMetrics.firstContentfulPaint).toBeLessThan(
        baseline.metrics.firstContentfulPaint * (1 + regressionThreshold)
      )

      expect(currentMetrics.largestContentfulPaint).toBeLessThan(
        baseline.metrics.largestContentfulPaint * (1 + regressionThreshold)
      )

      expect(currentMetrics.cumulativeLayoutShift).toBeLessThan(
        baseline.metrics.cumulativeLayoutShift * (1 + regressionThreshold)
      )

      console.log('Performance comparison with baseline:')
      console.log('Current:', currentMetrics)
      console.log('Baseline:', baseline.metrics)
    } else {
      // 创建基准数据
      const newBaseline: PerformanceBaseline = {
        url,
        metrics: currentMetrics,
        timestamp: new Date().toISOString(),
      }

      fs.writeFileSync(BASELINE_FILE, JSON.stringify(newBaseline, null, 2))
      console.log('Created new performance baseline:', newBaseline)
    }
  })
})
```

### 复杂性能测试场景

#### 1. 多页面性能对比

```typescript
// __tests__/performance/cross-page-performance.test.ts
import { test, expect } from '@playwright/test'

const pages = [
  { name: 'Home', url: '/' },
  { name: 'Products', url: '/products' },
  { name: 'About', url: '/about' },
  { name: 'Contact', url: '/contact' },
]

test.describe('Cross-page Performance Comparison', () => {
  const performanceResults: Array<{
    page: string
    url: string
    metrics: any
    bundleSize?: number
  }> = []

  pages.forEach(({ name, url }) => {
    test(`should measure performance for ${name} page`, async ({ page }) => {
      // 清除缓存
      await page.context().clearCookies()
      await page.goto(url)
      await page.waitForLoadState('networkidle')

      // 测量性能指标
      const metrics = await page.evaluate(() => {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming

        return {
          // 基础指标
          domContentLoaded: navigation.domContentLoadedEventEnd - navigation.fetchStart,
          loadComplete: navigation.loadEventEnd - navigation.fetchStart,

          // 资源加载
          resourceCount: performance.getEntriesByType('resource').length,
          totalResourceSize: performance.getEntriesByType('resource')
            .reduce((sum, entry) => sum + (entry.transferSize || 0), 0),

          // 用户交互指标
          firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
          firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0,
        }
      })

      // 测量Bundle大小（通过API）
      const bundleSize = await page.evaluate(() => {
        const scripts = Array.from(document.querySelectorAll('script[src]'))
        let totalSize = 0

        scripts.forEach(script => {
          if (script.src.includes('/_next/static/')) {
            // 这里可以通过fetch API获取文件大小
            // 简化示例，使用固定值
            totalSize += 50000 // 50KB估算
          }
        })

        return totalSize
      })

      performanceResults.push({
        page: name,
        url,
        metrics,
        bundleSize,
      })

      // 基本性能断言
      expect(metrics.domContentLoaded).toBeLessThan(2000)
      expect(metrics.firstContentfulPaint).toBeLessThan(1500)

      console.log(`${name} page performance:`, metrics)
    })
  })

  test('should compare performance across pages', () => {
    // 分析性能数据
    const avgDomContentLoaded = performanceResults.reduce(
      (sum, result) => sum + result.metrics.domContentLoaded, 0
    ) / performanceResults.length

    const avgBundleSize = performanceResults.reduce(
      (sum, result) => sum + (result.bundleSize || 0), 0
    ) / performanceResults.length

    console.log('Performance Summary:')
    console.log(`Average DOM Content Loaded: ${avgDomContentLoaded.toFixed(2)}ms`)
    console.log(`Average Bundle Size: ${(avgBundleSize / 1024).toFixed(2)}KB`)

    // 识别性能最差的页面
    const worstPage = performanceResults.reduce((prev, current) =>
      prev.metrics.domContentLoaded > current.metrics.domContentLoaded ? prev : current
    )

    console.log(`Worst performing page: ${worstPage.page} (${worstPage.metrics.domContentLoaded}ms)`)

    // 确保没有页面性能过差
    performanceResults.forEach(result => {
      expect(result.metrics.domContentLoaded).toBeLessThan(avgDomContentLoaded * 2)
    })
  })
})
```

#### 2. 移动端性能测试

```typescript
// __tests__/performance/mobile-performance.test.ts
import { test, devices, expect } from '@playwright/test'

const mobileDevices = [
  devices['iPhone 13'],
  devices['Pixel 5'],
  devices['iPad Pro'],
]

mobileDevices.forEach(device => {
  test.describe(`Mobile Performance: ${device.name}`, () => {
    test.use({ ...device, locale: 'en-US' })

    test('should perform well on mobile device', async ({ page }) => {
      // 模拟慢速网络
      await page.context().route('**/*', async route => {
        // 添加网络延迟
        await new Promise(resolve => setTimeout(resolve, Math.random() * 100))
        await route.continue()
      })

      const startTime = Date.now()
      await page.goto('/')
      await page.waitForLoadState('networkidle')
      const loadTime = Date.now() - startTime

      // 测量Core Web Vitals
      const vitals = await page.evaluate(() => {
        return new Promise((resolve) => {
          const metrics = {
            LCP: 0,
            FID: 0,
            CLS: 0,
          }

          // LCP
          new PerformanceObserver((list) => {
            const entries = list.getEntries()
            const lastEntry = entries[entries.length - 1]
            metrics.LCP = lastEntry.startTime
          }).observe({ entryTypes: ['largest-contentful-paint'] })

          // CLS
          new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
              if (!entry.hadRecentInput) {
                metrics.CLS += entry.value
              }
            }
          }).observe({ entryTypes: ['layout-shift'] })

          // FID
          new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
              metrics.FID = entry.processingStart - entry.startTime
            }
          }).observe({ entryTypes: ['first-input'] })

          // 模拟用户交互触发FID
          setTimeout(() => {
            document.body.click()
          }, 1000)

          setTimeout(() => resolve(metrics), 3000)
        })
      })

      // 移动端性能阈值（比桌面端宽松）
      expect(loadTime).toBeLessThan(5000) // 5秒内加载完成
      expect(vitals.LCP).toBeLessThan(4000) // LCP < 4s
      expect(vitals.CLS).toBeLessThan(0.25) // CLS < 0.25

      console.log(`${device.name} performance:`)
      console.log(`Load time: ${loadTime}ms`)
      console.log(`LCP: ${vitals.LCP}ms`)
      console.log(`CLS: ${vitals.CLS}`)
      console.log(`FID: ${vitals.FID}ms`)
    })

    test('should handle touch interactions properly', async ({ page }) => {
      await page.goto('/')

      // 测试触摸交互响应时间
      const touchResponseTime = await page.evaluate(async () => {
        const button = document.querySelector('[data-testid="mobile-menu-button"]')
        if (!button) return 0

        return new Promise((resolve) => {
          const startTime = performance.now()

          button.addEventListener('click', () => {
            const endTime = performance.now()
            resolve(endTime - startTime)
          })

          // 模拟触摸事件
          const touchEvent = new TouchEvent('touchstart', {
            bubbles: true,
            cancelable: true,
          })
          button.dispatchEvent(touchEvent)

          const clickEvent = new MouseEvent('click', {
            bubbles: true,
            cancelable: true,
          })
          button.dispatchEvent(clickEvent)
        })
      })

      expect(touchResponseTime).toBeLessThan(100) // 触摸响应时间 < 100ms
      console.log(`${device.name} touch response: ${touchResponseTime}ms`)
    })
  })
})
```

#### 3. 缓存性能测试

```typescript
// __tests__/performance/caching-performance.test.ts
import { test, expect } from '@playwright/test'

test.describe('Caching Performance', () => {
  test('should benefit from browser caching', async ({ page }) => {
    const urls = ['/products/1', '/products/2', '/products/3']
    const loadTimes: number[] = []

    // 首次访问（冷缓存）
    for (const url of urls) {
      const startTime = Date.now()
      await page.goto(url)
      await page.waitForLoadState('networkidle')
      const loadTime = Date.now() - startTime
      loadTimes.push(loadTime)
    }

    // 第二次访问（热缓存）
    const cachedLoadTimes: number[] = []
    for (const url of urls) {
      const startTime = Date.now()
      await page.goto(url)
      await page.waitForLoadState('networkidle')
      const loadTime = Date.now() - startTime
      cachedLoadTimes.push(loadTime)
    }

    // 分析缓存效果
    const avgColdLoadTime = loadTimes.reduce((a, b) => a + b, 0) / loadTimes.length
    const avgCachedLoadTime = cachedLoadTimes.reduce((a, b) => a + b, 0) / cachedLoadTimes.length
    const cacheImprovement = ((avgColdLoadTime - avgCachedLoadTime) / avgColdLoadTime) * 100

    console.log(`Average cold load time: ${avgColdLoadTime.toFixed(2)}ms`)
    console.log(`Average cached load time: ${avgCachedLoadTime.toFixed(2)}ms`)
    console.log(`Cache improvement: ${cacheImprovement.toFixed(2)}%`)

    // 缓存应该显著提升性能
    expect(cacheImprovement).toBeGreaterThan(30) // 至少30%的性能提升
  })

  test('should implement proper Service Worker caching', async ({ page }) => {
    // 检查Service Worker注册
    const swRegistered = await page.evaluate(() => {
      return !!navigator.serviceWorker?.controller
    })

    if (swRegistered) {
      console.log('Service Worker is active')

      // 测试离线功能
      await page.context().setOffline(true)

      const offlineLoadTime = await page.evaluate(async () => {
        const startTime = performance.now()
        try {
          await fetch('/')
          return performance.now() - startTime
        } catch {
          return -1
        }
      })

      if (offlineLoadTime > 0) {
        console.log(`Offline load time: ${offlineLoadTime.toFixed(2)}ms`)
        expect(offlineLoadTime).toBeLessThan(1000) // 离线加载应该很快
      } else {
        console.log('Offline functionality not available')
      }

      await page.context().setOffline(false)
    } else {
      console.log('Service Worker not implemented')
    }
  })
})
```

## 🎨 测试最佳实践

### 测试组织结构

**性能测试文件组织**:
```
__tests__/
├── performance/               # 性能测试
│   ├── core-vitals.test.ts    # Core Web Vitals测试
│   ├── bundle-analysis.test.ts # Bundle分析测试
│   ├── load-testing/          # 负载测试
│   │   ├── k6-test.js
│   │   └── artillery-config.yml
│   ├── mobile-performance.test.ts # 移动端性能测试
│   └── regression.test.ts     # 性能回归测试
├── lighthouse-results/        # Lighthouse测试结果
├── bundle-analysis/           # Bundle分析结果
└── performance-baseline.json  # 性能基准数据
```

### 性能阈值设定

**基于设备类型的阈值**:
```typescript
// config/performance-thresholds.ts
export const PERFORMANCE_THRESHOLDS = {
  desktop: {
    firstContentfulPaint: 1500,
    largestContentfulPaint: 2500,
    firstInputDelay: 100,
    cumulativeLayoutShift: 0.1,
    domContentLoaded: 1500,
    loadComplete: 3000,
  },
  mobile: {
    firstContentfulPaint: 2000,
    largestContentfulPaint: 4000,
    firstInputDelay: 200,
    cumulativeLayoutShift: 0.25,
    domContentLoaded: 2500,
    loadComplete: 5000,
  },
  slow3G: {
    firstContentfulPaint: 4000,
    largestContentfulPaint: 8000,
    firstInputDelay: 300,
    cumulativeLayoutShift: 0.3,
    domContentLoaded: 5000,
    loadComplete: 10000,
  },
}
```

### 测试环境管理

**网络条件模拟**:
```typescript
// utils/network-simulation.ts
export const NETWORK_PROFILES = {
  'offline': {
    offline: true,
  },
  'slow-3g': {
    downloadThroughput: 500 * 1024 / 8,  // 500 Kbps
    uploadThroughput: 500 * 1024 / 8,    // 500 Kbps
    latency: 400 * 5,                    // 400ms RTT
  },
  'fast-3g': {
    downloadThroughput: 1.6 * 1024 * 1024 / 8,  // 1.6 Mbps
    uploadThroughput: 750 * 1024 / 8,           // 750 Kbps
    latency: 300 * 5,                           // 300ms RTT
  },
  '4g': {
    downloadThroughput: 9 * 1024 * 1024 / 8,  // 9 Mbps
    uploadThroughput: 1.5 * 1024 * 1024 / 8,  // 1.5 Mbps
    latency: 100 * 5,                          // 100ms RTT
  },
}
```

### 数据管理策略

**性能数据存储**:
```typescript
// utils/performance-storage.ts
interface PerformanceDataPoint {
  timestamp: string
  url: string
  device: string
  network: string
  metrics: Record<string, number>
  buildVersion: string
}

export class PerformanceStorage {
  private storagePath: string

  constructor(storagePath: string = './performance-data') {
    this.storagePath = storagePath
    this.ensureStorageDirectory()
  }

  async saveDataPoint(data: PerformanceDataPoint): Promise<void> {
    const filename = `${this.storagePath}/${data.timestamp.split('T')[0]}.json`
    let existingData: PerformanceDataPoint[] = []

    if (fs.existsSync(filename)) {
      existingData = JSON.parse(fs.readFileSync(filename, 'utf8'))
    }

    existingData.push(data)
    fs.writeFileSync(filename, JSON.stringify(existingData, null, 2))
  }

  async getHistoricalData(
    url: string,
    days: number = 30
  ): Promise<PerformanceDataPoint[]> {
    const startDate = new Date()
    startDate.setDate(startDate.getDate() - days)

    const allData: PerformanceDataPoint[] = []

    for (let i = 0; i < days; i++) {
      const date = new Date(startDate)
      date.setDate(date.getDate() + i)
      const filename = `${this.storagePath}/${date.toISOString().split('T')[0]}.json`

      if (fs.existsSync(filename)) {
        const dayData = JSON.parse(fs.readFileSync(filename, 'utf8'))
        allData.push(...dayData.filter(d => d.url === url))
      }
    }

    return allData.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
  }

  private ensureStorageDirectory(): void {
    if (!fs.existsSync(this.storagePath)) {
      fs.mkdirSync(this.storagePath, { recursive: true })
    }
  }
}
```

## 🔍 高级测试技术

### 测试覆盖率

**性能测试覆盖率矩阵**:
```typescript
// utils/performance-coverage.ts
export interface PerformanceCoverageMatrix {
  pages: string[]
  devices: string[]
  networks: string[]
  metrics: string[]
  results: Record<string, Record<string, Record<string, Record<string, number>>>>
}

export class PerformanceCoverage {
  private matrix: PerformanceCoverageMatrix

  constructor() {
    this.matrix = {
      pages: ['/', '/about', '/products', '/contact'],
      devices: ['desktop', 'mobile', 'tablet'],
      networks: ['4g', 'fast-3g', 'slow-3g'],
      metrics: ['FCP', 'LCP', 'FID', 'CLS', 'TTI'],
      results: {},
    }
  }

  async runFullCoverageTest(): Promise<void> {
    for (const page of this.matrix.pages) {
      this.matrix.results[page] = {}

      for (const device of this.matrix.devices) {
        this.matrix.results[page][device] = {}

        for (const network of this.matrix.networks) {
          this.matrix.results[page][device][network] = {}

          const metrics = await this.runPerformanceTest(page, device, network)
          for (const metric of this.matrix.metrics) {
            this.matrix.results[page][device][network][metric] = metrics[metric] || 0
          }
        }
      }
    }

    this.generateCoverageReport()
  }

  private async runPerformanceTest(
    page: string,
    device: string,
    network: string
  ): Promise<Record<string, number>> {
    // 实现具体的性能测试逻辑
    return {
      FCP: Math.random() * 2000,
      LCP: Math.random() * 3000,
      FID: Math.random() * 100,
      CLS: Math.random() * 0.1,
      TTI: Math.random() * 4000,
    }
  }

  private generateCoverageReport(): void {
    const report = {
      timestamp: new Date().toISOString(),
      coverage: this.matrix,
      summary: this.generateSummary(),
    }

    fs.writeFileSync(
      './performance-coverage-report.json',
      JSON.stringify(report, null, 2)
    )
  }
}
```

### 测试性能优化

**并行测试执行**:
```typescript
// utils/parallel-performance-testing.ts
export class ParallelPerformanceTester {
  private concurrency: number

  constructor(concurrency: number = 3) {
    this.concurrency = concurrency
  }

  async runTestsParallel(tests: Array<() => Promise<any>>): Promise<any[]> {
    const results: any[] = []
    const executing: Promise<void>[] = []

    for (const test of tests) {
      const promise = test().then(result => {
        results.push(result)
      })

      executing.push(promise)

      if (executing.length >= this.concurrency) {
        await Promise.race(executing)
        executing.splice(executing.findIndex(p => p === promise), 1)
      }
    }

    await Promise.all(executing)
    return results
  }
}
```

### 智能测试调度

**基于变更的测试选择**:
```typescript
// utils/smart-test-scheduler.ts
export class SmartTestScheduler {
  async selectRelevantPerformanceTests(
    changedFiles: string[],
    allTests: PerformanceTest[]
  ): Promise<PerformanceTest[]> {
    const relevantTests: PerformanceTest[] = []

    for (const test of allTests) {
      if (this.isTestRelevant(changedFiles, test)) {
        relevantTests.push(test)
      }
    }

    // 确保至少运行核心性能测试
    if (relevantTests.length === 0) {
      relevantTests.push(...allTests.filter(test => test.core))
    }

    return relevantTests
  }

  private isTestRelevant(changedFiles: string[], test: PerformanceTest): boolean {
    // 检查测试是否与变更文件相关
    for (const file of changedFiles) {
      if (test.affectedPaths.some(path => file.includes(path))) {
        return true
      }
    }
    return false
  }
}

interface PerformanceTest {
  name: string
  affectedPaths: string[]
  core: boolean
  execute: () => Promise<any>
}
```

### 可视化回归测试

**性能趋势可视化**:
```typescript
// utils/performance-visualization.ts
export class PerformanceVisualization {
  generateTrendChart(data: PerformanceDataPoint[]): string {
    // 生成性能趋势图表
    const chartData = data.map(point => ({
      x: new Date(point.timestamp),
      y: point.metrics.LCP,
    }))

    return `
      <html>
        <head>
          <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
          <canvas id="trendChart"></canvas>
          <script>
            const ctx = document.getElementById('trendChart').getContext('2d');
            new Chart(ctx, {
              type: 'line',
              data: {
                datasets: [{
                  label: 'LCP Trend',
                  data: ${JSON.stringify(chartData)},
                  borderColor: 'rgb(75, 192, 192)',
                  tension: 0.1
                }]
              },
              options: {
                responsive: true,
                scales: {
                  x: {
                    type: 'time',
                    time: {
                      unit: 'day'
                    }
                  },
                  y: {
                    beginAtZero: true,
                    title: {
                      display: true,
                      text: 'LCP (ms)'
                    }
                  }
                }
              }
            });
          </script>
        </body>
      </html>
    `
  }
}
```

## 🚀 CI/CD集成

### 自动化性能测试流程

**GitHub Actions完整配置**:
```yaml
# .github/workflows/performance.yml
name: Performance Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    # 每天凌晨2点运行性能测试
    - cron: '0 2 * * *'

jobs:
  performance-tests:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build application
        run: npm run build

      - name: Start application
        run: |
          npm start &
          sleep 10

      - name: Run Lighthouse CI
        run: |
          npm install -g @lhci/cli@0.12.x
          lhci autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}

      - name: Run Core Web Vitals tests
        run: npm run test:vitals

      - name: Run bundle analysis
        run: |
          ANALYZE=true npm run build
          node scripts/analyze-bundle.js

      - name: Run load tests
        run: |
          npm install -g k6
          k6 run tests/load/k6-test.js

      - name: Upload performance reports
        uses: actions/upload-artifact@v3
        with:
          name: performance-reports
          path: |
            lighthouse-results/
            bundle-analysis.json
            load-test-summary.json

      - name: Comment PR with performance results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs')

            // 读取Lighthouse结果
            const lighthouseResults = JSON.parse(
              fs.readFileSync('./lighthouse-results/manifest.json', 'utf8')
            )

            // 生成性能报告
            const report = generatePerformanceReport(lighthouseResults)

            // 添加PR评论
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            })

  performance-regression:
    runs-on: ubuntu-latest
    needs: performance-tests

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Download performance reports
        uses: actions/download-artifact@v3
        with:
          name: performance-reports

      - name: Check for performance regression
        run: node scripts/check-regression.js

      - name: Notify team of regression
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: failure
          text: 'Performance regression detected! Please check the test results.'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 性能报告生成

**自动化报告生成器**:
```typescript
// scripts/generate-performance-report.ts
import fs from 'fs'
import path from 'path'

interface PerformanceReport {
  timestamp: string
  buildVersion: string
  lighthouse: {
    overall: number
    performance: number
    accessibility: number
    bestPractices: number
    seo: number
  }
  coreWebVitals: {
    lcp: number
    fid: number
    cls: number
  }
  bundleAnalysis: {
    totalSize: number
    mainBundle: number
    vendorBundle: number
  }
  loadTesting: {
    avgResponseTime: number
    maxResponseTime: number
    errorRate: number
  }
  recommendations: string[]
}

export class PerformanceReportGenerator {
  generateReport(): PerformanceReport {
    const lighthouseData = this.loadLighthouseData()
    const vitalsData = this.loadVitalsData()
    const bundleData = this.loadBundleData()
    const loadData = this.loadLoadTestData()

    const report: PerformanceReport = {
      timestamp: new Date().toISOString(),
      buildVersion: process.env.GITHUB_SHA || 'local',
      lighthouse: this.processLighthouseData(lighthouseData),
      coreWebVitals: vitalsData,
      bundleAnalysis: bundleData,
      loadTesting: loadData,
      recommendations: this.generateRecommendations({
        lighthouse: lighthouseData,
        vitals: vitalsData,
        bundle: bundleData,
        load: loadData,
      }),
    }

    this.saveReport(report)
    this.generateMarkdownReport(report)

    return report
  }

  private loadLighthouseData() {
    // 加载Lighthouse测试结果
    const manifestPath = './lighthouse-results/manifest.json'
    if (fs.existsSync(manifestPath)) {
      return JSON.parse(fs.readFileSync(manifestPath, 'utf8'))
    }
    return null
  }

  private loadVitalsData() {
    // 加载Core Web Vitals数据
    const vitalsPath = './vitals-results.json'
    if (fs.existsSync(vitalsPath)) {
      return JSON.parse(fs.readFileSync(vitalsPath, 'utf8'))
    }
    return { lcp: 0, fid: 0, cls: 0 }
  }

  private loadBundleData() {
    // 加载Bundle分析数据
    const bundlePath = './bundle-analysis.json'
    if (fs.existsSync(bundlePath)) {
      const analysis = JSON.parse(fs.readFileSync(bundlePath, 'utf8'))
      return this.processBundleAnalysis(analysis)
    }
    return { totalSize: 0, mainBundle: 0, vendorBundle: 0 }
  }

  private loadLoadTestData() {
    // 加载负载测试数据
    const loadPath = './load-test-summary.json'
    if (fs.existsSync(loadPath)) {
      return JSON.parse(fs.readFileSync(loadPath, 'utf8'))
    }
    return { avgResponseTime: 0, maxResponseTime: 0, errorRate: 0 }
  }

  private processLighthouseData(data: any) {
    if (!data) return { overall: 0, performance: 0, accessibility: 0, bestPractices: 0, seo: 0 }

    // 处理Lighthouse数据
    return {
      overall: data[0]?.average || 0,
      performance: data[0]?.averages?.performance || 0,
      accessibility: data[0]?.averages?.accessibility || 0,
      bestPractices: data[0]?.averages?.['best-practices'] || 0,
      seo: data[0]?.averages?.seo || 0,
    }
  }

  private processBundleAnalysis(analysis: any) {
    // 处理Bundle分析数据
    return {
      totalSize: analysis.totalSize || 0,
      mainBundle: analysis.mainBundleSize || 0,
      vendorBundle: analysis.vendorBundleSize || 0,
    }
  }

  private generateRecommendations(data: any): string[] {
    const recommendations: string[] = []

    // Lighthouse建议
    if (data.lighthouse?.performance < 80) {
      recommendations.push('Performance score is below 80. Consider optimizing images, reducing bundle size, or improving server response time.')
    }

    // Core Web Vitals建议
    if (data.vitals.lcp > 2500) {
      recommendations.push('LCP is above 2.5s. Optimize largest content elements and server response time.')
    }

    if (data.vitals.fid > 100) {
      recommendations.push('FID is above 100ms. Reduce JavaScript execution time and main thread work.')
    }

    if (data.vitals.cls > 0.1) {
      recommendations.push('CLS is above 0.1. Ensure images have dimensions and avoid inserting content above existing content.')
    }

    // Bundle大小建议
    if (data.bundle.totalSize > 1024 * 1024) { // 1MB
      recommendations.push('Total bundle size exceeds 1MB. Consider code splitting and tree shaking.')
    }

    // 负载测试建议
    if (data.load.errorRate > 0.05) {
      recommendations.push('Error rate is above 5%. Investigate server issues and improve error handling.')
    }

    return recommendations
  }

  private saveReport(report: PerformanceReport): void {
    const reportsPath = './performance-reports'
    if (!fs.existsSync(reportsPath)) {
      fs.mkdirSync(reportsPath, { recursive: true })
    }

    const filename = `${reportsPath}/performance-report-${Date.now()}.json`
    fs.writeFileSync(filename, JSON.stringify(report, null, 2))

    // 保存最新报告
    fs.writeFileSync(`${reportsPath}/latest.json`, JSON.stringify(report, null, 2))
  }

  private generateMarkdownReport(report: PerformanceReport): void {
    const markdown = `
# Performance Report

**Generated**: ${new Date(report.timestamp).toLocaleString()}
**Build**: ${report.buildVersion}

## 🎯 Performance Scores

| Metric | Score | Status |
|--------|-------|--------|
| Performance | ${report.lighthouse.performance} | ${report.lighthouse.performance >= 80 ? '✅ Good' : report.lighthouse.performance >= 50 ? '⚠️ Needs Improvement' : '❌ Poor'} |
| Accessibility | ${report.lighthouse.accessibility} | ${report.lighthouse.accessibility >= 90 ? '✅ Good' : '⚠️ Needs Improvement'} |
| Best Practices | ${report.lighthouse.bestPractices} | ${report.lighthouse.bestPractices >= 80 ? '✅ Good' : '⚠️ Needs Improvement'} |
| SEO | ${report.lighthouse.seo} | ${report.lighthouse.seo >= 80 ? '✅ Good' : '⚠️ Needs Improvement'} |

## 📊 Core Web Vitals

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| LCP | ${report.coreWebVitals.lcp}ms | < 2500ms | ${report.coreWebVitals.lcp < 2500 ? '✅' : '❌'} |
| FID | ${report.coreWebVitals.fid}ms | < 100ms | ${report.coreWebVitals.fid < 100 ? '✅' : '❌'} |
| CLS | ${report.coreWebVitals.cls} | < 0.1 | ${report.coreWebVitals.cls < 0.1 ? '✅' : '❌'} |

## 📦 Bundle Analysis

- **Total Size**: ${(report.bundleAnalysis.totalSize / 1024).toFixed(2)} KB
- **Main Bundle**: ${(report.bundleAnalysis.mainBundle / 1024).toFixed(2)} KB
- **Vendor Bundle**: ${(report.bundleAnalysis.vendorBundle / 1024).toFixed(2)} KB

## 🚀 Load Testing

- **Average Response Time**: ${report.loadTesting.avgResponseTime}ms
- **Maximum Response Time**: ${report.loadTesting.maxResponseTime}ms
- **Error Rate**: ${(report.loadTesting.errorRate * 100).toFixed(2)}%

## 💡 Recommendations

${report.recommendations.map(rec => `- ${rec}`).join('\n')}

---

*Report generated by Performance Test Suite*
    `

    const reportsPath = './performance-reports'
    fs.writeFileSync(`${reportsPath}/latest.md`, markdown)
  }
}
```

### 质量门禁

**性能质量检查**:
```typescript
// scripts/performance-quality-gate.ts
interface QualityGateThresholds {
  minPerformanceScore: number
  maxBundleSize: number
  maxLCP: number
  maxFID: number
  maxCLS: number
  maxErrorRate: number
}

export class PerformanceQualityGate {
  private thresholds: QualityGateThresholds = {
    minPerformanceScore: 80,
    maxBundleSize: 1024 * 1024, // 1MB
    maxLCP: 2500,
    maxFID: 100,
    maxCLS: 0.1,
    maxErrorRate: 0.05, // 5%
  }

  async checkQualityGate(report: PerformanceReport): Promise<{
    passed: boolean
    failures: string[]
    warnings: string[]
  }> {
    const failures: string[] = []
    const warnings: string[] = []

    // 检查Lighthouse性能分数
    if (report.lighthouse.performance < this.thresholds.minPerformanceScore) {
      failures.push(
        `Performance score ${report.lighthouse.performance} is below threshold ${this.thresholds.minPerformanceScore}`
      )
    }

    // 检查Bundle大小
    if (report.bundleAnalysis.totalSize > this.thresholds.maxBundleSize) {
      failures.push(
        `Bundle size ${report.bundleAnalysis.totalSize} bytes exceeds threshold ${this.thresholds.maxBundleSize} bytes`
      )
    }

    // 检查Core Web Vitals
    if (report.coreWebVitals.lcp > this.thresholds.maxLCP) {
      failures.push(
        `LCP ${report.coreWebVitals.lcp}ms exceeds threshold ${this.thresholds.maxLCP}ms`
      )
    }

    if (report.coreWebVitals.fid > this.thresholds.maxFID) {
      failures.push(
        `FID ${report.coreWebVitals.fid}ms exceeds threshold ${this.thresholds.maxFID}ms`
      )
    }

    if (report.coreWebVitals.cls > this.thresholds.maxCLS) {
      failures.push(
        `CLS ${report.coreWebVitals.cls} exceeds threshold ${this.thresholds.maxCLS}`
      )
    }

    // 检查负载测试结果
    if (report.loadTesting.errorRate > this.thresholds.maxErrorRate) {
      failures.push(
        `Error rate ${(report.loadTesting.errorRate * 100).toFixed(2)}% exceeds threshold ${(this.thresholds.maxErrorRate * 100).toFixed(2)}%`
      )
    }

    // 警告（不阻止构建但需要关注）
    if (report.lighthouse.accessibility < 90) {
      warnings.push('Accessibility score is below 90')
    }

    if (report.lighthouse.seo < 90) {
      warnings.push('SEO score is below 90')
    }

    const passed = failures.length === 0

    // 生成质量门禁报告
    this.generateQualityGateReport({
      passed,
      failures,
      warnings,
      timestamp: new Date().toISOString(),
    })

    return { passed, failures, warnings }
  }

  private generateQualityGateReport(result: {
    passed: boolean
    failures: string[]
    warnings: string[]
    timestamp: string
  }): void {
    const report = {
      ...result,
      thresholds: this.thresholds,
    }

    fs.writeFileSync(
      './quality-gate-result.json',
      JSON.stringify(report, null, 2)
    )

    if (!result.passed) {
      console.error('❌ Performance quality gate failed!')
      result.failures.forEach(failure => console.error(`  - ${failure}`))
      process.exit(1)
    } else {
      console.log('✅ Performance quality gate passed!')
      if (result.warnings.length > 0) {
        console.log('⚠️ Warnings:')
        result.warnings.forEach(warning => console.log(`  - ${warning}`))
      }
    }
  }
}
```

## 📊 测试监控和分析

### 测试结果分析

**性能趋势分析**:
```typescript
// utils/performance-trend-analysis.ts
export class PerformanceTrendAnalyzer {
  analyzeTrends(data: PerformanceDataPoint[]): {
    trends: Record<string, 'improving' | 'stable' | 'degrading'>
    insights: string[]
    recommendations: string[]
  } {
    const trends: Record<string, 'improving' | 'stable' | 'degrading'> = {}
    const insights: string[] = []
    const recommendations: string[] = []

    // 分析LCP趋势
    const lcpTrend = this.analyzeMetricTrend(data, 'LCP')
    trends.LCP = lcpTrend.direction

    if (lcpTrend.direction === 'degrading') {
      insights.push(`LCP is degrading by ${lcpTrend.changePercent.toFixed(2)}% over the last ${lcpTrend.days} days`)
      recommendations.push('Investigate LCP regression: check server response time, render-blocking resources, and image optimization')
    }

    // 分析Bundle大小趋势
    const bundleTrend = this.analyzeMetricTrend(data, 'bundleSize')
    trends.bundleSize = bundleTrend.direction

    if (bundleTrend.direction === 'degrading') {
      insights.push(`Bundle size increased by ${bundleTrend.changePercent.toFixed(2)}% over the last ${bundleTrend.days} days`)
      recommendations.push('Review recent dependencies and implement code splitting')
    }

    return { trends, insights, recommendations }
  }

  private analyzeMetricTrend(
    data: PerformanceDataPoint[],
    metric: string
  ): {
    direction: 'improving' | 'stable' | 'degrading'
    changePercent: number
    days: number
  } {
    // 简化的趋势分析逻辑
    const recentData = data.slice(-7) // 最近7天
    const olderData = data.slice(-14, -7) // 之前7天

    if (recentData.length === 0 || olderData.length === 0) {
      return { direction: 'stable', changePercent: 0, days: 0 }
    }

    const recentAvg = recentData.reduce((sum, d) => sum + (d.metrics[metric] || 0), 0) / recentData.length
    const olderAvg = olderData.reduce((sum, d) => sum + (d.metrics[metric] || 0), 0) / olderData.length

    const changePercent = ((recentAvg - olderAvg) / olderAvg) * 100

    let direction: 'improving' | 'stable' | 'degrading'
    if (Math.abs(changePercent) < 5) {
      direction = 'stable'
    } else if ((metric === 'LCP' || metric === 'bundleSize') && changePercent < 0) {
      direction = 'improving'
    } else if (metric !== 'LCP' && metric !== 'bundleSize' && changePercent > 0) {
      direction = 'improving'
    } else {
      direction = 'degrading'
    }

    return { direction, changePercent, days: 7 }
  }
}
```

### 质量指标追踪

**性能仪表板数据**:
```typescript
// utils/performance-dashboard.ts
export class PerformanceDashboard {
  generateDashboardData(): {
    overview: any
    trends: any
    alerts: any
    recommendations: any
  } {
    const recentData = this.getRecentPerformanceData()
    const historicalData = this.getHistoricalPerformanceData()

    return {
      overview: this.generateOverview(recentData),
      trends: this.generateTrends(historicalData),
      alerts: this.generateAlerts(recentData),
      recommendations: this.generateRecommendations(recentData, historicalData),
    }
  }

  private generateOverview(data: PerformanceDataPoint[]) {
    if (data.length === 0) return null

    const latest = data[data.length - 1]
    const avgLCP = data.reduce((sum, d) => sum + d.metrics.LCP, 0) / data.length
    const avgFID = data.reduce((sum, d) => sum + d.metrics.FID, 0) / data.length
    const avgCLS = data.reduce((sum, d) => sum + d.metrics.CLS, 0) / data.length

    return {
      latest: latest.metrics,
      averages: {
        LCP: avgLCP,
        FID: avgFID,
        CLS: avgCLS,
      },
      performanceScore: latest.metrics.performanceScore,
      status: this.getOverallStatus(latest.metrics),
    }
  }

  private getOverallStatus(metrics: Record<string, number>): 'good' | 'needs-improvement' | 'poor' {
    const lcpStatus = metrics.LCP < 2500 ? 'good' : metrics.LCP < 4000 ? 'needs-improvement' : 'poor'
    const fidStatus = metrics.FID < 100 ? 'good' : metrics.FID < 300 ? 'needs-improvement' : 'poor'
    const clsStatus = metrics.CLS < 0.1 ? 'good' : metrics.CLS < 0.25 ? 'needs-improvement' : 'poor'

    if (lcpStatus === 'good' && fidStatus === 'good' && clsStatus === 'good') {
      return 'good'
    } else if (lcpStatus === 'poor' || fidStatus === 'poor' || clsStatus === 'poor') {
      return 'poor'
    } else {
      return 'needs-improvement'
    }
  }
}
```

### 性能基准测试

**自动化基准测试**:
```typescript
// utils/performance-benchmark.ts
export class PerformanceBenchmark {
  private benchmarks: Record<string, number> = {}

  async runBenchmarkSuite(): Promise<void> {
    console.log('🚀 Starting performance benchmark suite...')

    // 组件渲染性能基准
    await this.benchmarkComponentRendering()

    // 路由切换性能基准
    await this.benchmarkRouteTransitions()

    // API调用性能基准
    await this.benchmarkAPICalls()

    // 内存使用基准
    await this.benchmarkMemoryUsage()

    this.generateBenchmarkReport()
  }

  private async benchmarkComponentRendering(): Promise<void> {
    const testCases = [
      { name: 'SimpleButton', component: 'Button', props: {} },
      { name: 'ComplexForm', component: 'ContactForm', props: { fields: 10 } },
      { name: 'DataTable', component: 'DataTable', props: { rows: 1000 } },
    ]

    for (const testCase of testCases) {
      const renderTime = await this.measureComponentRender(testCase)
      this.benchmarks[`component-${testCase.name}`] = renderTime

      console.log(`⏱️ ${testCase.name} render time: ${renderTime}ms`)
    }
  }

  private async benchmarkRouteTransitions(): Promise<void> {
    const routes = ['/', '/about', '/products', '/contact']

    for (const route of routes) {
      const transitionTime = await this.measureRouteTransition(route)
      this.benchmarks[`route-${route.replace('/', 'home')}`] = transitionTime

      console.log(`🔄 Route ${route} transition: ${transitionTime}ms`)
    }
  }

  private async measureComponentRender(testCase: any): Promise<number> {
    // 实现组件渲染时间测量
    return Math.random() * 100 // 模拟数据
  }

  private async measureRouteTransition(route: string): Promise<number> {
    // 实现路由切换时间测量
    return Math.random() * 200 // 模拟数据
  }

  private generateBenchmarkReport(): void {
    const report = {
      timestamp: new Date().toISOString(),
      benchmarks: this.benchmarks,
      summary: this.generateBenchmarkSummary(),
    }

    fs.writeFileSync(
      './performance-benchmark.json',
      JSON.stringify(report, null, 2)
    )

    console.log('📊 Benchmark report generated')
  }

  private generateBenchmarkSummary() {
    const entries = Object.entries(this.benchmarks)
    const avgRenderTime = entries
      .filter(([key]) => key.startsWith('component-'))
      .reduce((sum, [, value]) => sum + value, 0) /
      entries.filter(([key]) => key.startsWith('component-')).length

    const avgRouteTime = entries
      .filter(([key]) => key.startsWith('route-'))
      .reduce((sum, [, value]) => sum + value, 0) /
      entries.filter(([key]) => key.startsWith('route-')).length

    return {
      averageComponentRenderTime: avgRenderTime,
      averageRouteTransitionTime: avgRouteTime,
      totalBenchmarks: entries.length,
    }
  }
}
```

## 🔄 文档交叉引用

### 相关文档
- 📄 **[单元测试指南](./01-unit-testing.md)**: 单元测试基础知识和最佳实践
- 📄 **[组件测试指南](./02-component-testing.md)**: React组件测试详细指南
- 📄 **[E2E测试指南](./03-e2e-testing.md)**: 端到端测试策略和实施
- 📄 **[测试工具详解](../knowledge-points/development-tools/01-testing-tools.md)**: 测试生态系统和工具对比

### 参考章节
- 📖 **[性能优化知识](../knowledge-points/performance-optimization/01-core-web-vitals.md)**: Core Web Vitals详细解释
- 📖 **[Next.js性能配置](../knowledge-points/nextjs-advanced/01-performance-optimization.md)**: Next.js性能优化技术
- 📖 **[企业落地项目](../projects/01-corporate-landing.md)**: 企业级项目性能测试实践
- 📖 **[电商平台项目](../projects/02-ecommerce-store.md)**: 大型应用性能测试策略

## 📝 总结

### 核心要点回顾

1. **性能指标体系**: 掌握Core Web Vitals和自定义性能指标的意义和测量方法
2. **工具栈应用**: 熟练使用Lighthouse CI、Bundle Analyzer、K6等性能测试工具
3. **测试策略设计**: 根据应用特点设计合理的性能测试策略和阈值
4. **自动化集成**: 将性能测试集成到CI/CD流程中，实现持续性能监控
5. **数据分析**: 通过趋势分析和基准测试持续优化应用性能
6. **质量门禁**: 建立性能质量标准，防止性能回归

### 学习成果检查

- [ ] 是否理解了Core Web Vitals的意义和测量方法？
- [ ] 是否能够配置和使用Lighthouse CI？
- [ ] 是否掌握了Bundle分析和优化技巧？
- [ ] 是否能够设计和实施负载测试？
- [ ] 是否了解性能监控和趋势分析？
- [ ] 是否能够建立性能质量门禁？

## 🤝 贡献与反馈

### 内容改进
如果你发现本文档有改进空间，欢迎：
- 🐛 **报告问题**: 在Issues中提出具体问题
- 💡 **建议改进**: 提出修改建议和补充内容
- 📝 **参与贡献**: 提交PR完善文档内容

### 学习反馈
分享你的学习体验：
- ✅ **有用内容**: 哪些部分对你最有帮助
- ❓ **疑问点**: 哪些内容需要进一步澄清
- 🎯 **建议**: 希望增加什么内容

## 🔗 外部资源

### 官方文档
- **Web.dev**: [Core Web Vitals](https://web.dev/vitals/) - Google官方性能指标指南
- **Lighthouse**: [官方文档](https://developer.chrome.com/docs/lighthouse/) - 性能审计工具详细说明
- **Lighthouse CI**: [官方文档](https://github.com/GoogleChrome/lighthouse-ci) - CI集成指南

### 性能测试工具
- **WebPageTest**: [在线测试工具](https://www.webpagetest.org/) - 详细性能分析
- **K6**: [负载测试工具](https://k6.io/) - 现代化负载测试平台
- **Bundle Analyzer**: [Webpack插件](https://github.com/webpack-contrib/webpack-bundle-analyzer) - Bundle可视化分析

### 学习资源
- **性能优化课程**: [web.dev性能课程](https://web.dev/learn/performance/) - Google官方性能优化课程
- **Performance Calendar**: [博客系列](https://perf- calendar.com/) - 性能优化专家分享
- **Smashing Magazine**: [性能文章](https://www.smashingmagazine.com/category/performance/) - 前端性能最佳实践

### 监控和分析
- **Google PageSpeed Insights**: [在线工具](https://pagespeed.web.dev/) - 性能评分和优化建议
- **Chrome DevTools**: [性能面板](https://developer.chrome.com/docs/devtools/performance/) - 浏览器性能分析工具
- **Firebase Performance**: [监控服务](https://firebase.google.com/docs/perf-mon) - 实时性能监控

---

**文档状态**: ✅ 已完成
**最后更新**: 2025年10月
**版本**: v1.0.0