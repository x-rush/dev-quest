# Next.js 16 性能优化完整指南

## 先看框架承担哪部分职责

**性能优化**：用户等待时间可能来自请求、渲染、资源下载或主线程工作。先建立一个可重复基线，再改一个变量。

**最小练习与预期结果**：记录同一设备和网络条件下的加载与交互结果，优化后复测；不能把构建速度提升当作用户页面速度提升。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: Next.js 16 企业级性能优化实践指南，涵盖Core Web Vitals、构建优化、运行时优化、监控分析等现代Web性能优化技术

> **目标读者**: 具备Next.js基础的中高级开发者，需要掌握性能优化和用户体验提升的性能工程师

> **前置知识**: Next.js 16基础、React 19、Web性能指标、浏览器渲染原理、网络优化

> **预计时长**: 10-14小时

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `frameworks` |
| **难度** | ⭐⭐⭐ (精通)|
| **标签** | `#performance` `#optimization` `#core-web-vitals` `#bundle-analysis` `#monitoring` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 🎯 学习目标

### ⚡ 性能优化核心技能
- 掌握Core Web Vitals指标优化策略
- 学会构建时优化和运行时优化的最佳实践
- 理解Next.js 16的渲染性能优化机制
- 掌握性能监控和分析工具的使用

### 🚀 企业级优化能力
- 构建高性能的用户体验和交互响应
- 实现自动化性能监控和预警系统
- 学会性能预算和性能预算管理
- 掌握A/B测试和性能迭代优化

## 📖 概述

Next.js 16为性能优化提供了强大的工具和策略，从构建时优化到运行时优化，从Core Web Vitals到用户体验优化，为构建高性能的现代Web应用提供了完整的解决方案。本指南将深入探讨Next.js 16的性能优化最佳实践。

## 📊 Core Web Vitals 深度优化

### LCP (Largest Contentful Paint) 优化

```tsx
// src/components/performance/LCPOptimizer.tsx
import Image from 'next/image'
import { useState, useEffect, useMemo } from 'react'

interface LCPMetric {
  element: HTMLElement | null
  renderTime: number
  size: number
  url: string
}

export class LCPOptimizer {
  private static observer: PerformanceObserver | null = null
  private static metrics: LCPMetric | null = null

  // 监听LCP
  static observeLCP(): Promise<LCPMetric> {
    return new Promise((resolve) => {
      if (typeof window === 'undefined') {
        resolve({ element: null, renderTime: 0, size: 0, url: '' })
        return
      }

      const observer = new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries()
        const lastEntry = entries[entries.length - 1] as PerformanceNavigationTiming

        if (lastEntry) {
          const lcpEntry = entries
            .filter((entry): entry is PerformancePaintTiming =>
              entry.entryType === 'largest-contentful-paint'
            )
            .sort((a, b) => b.startTime - a.startTime)[0]

          if (lcpEntry) {
            const element = document.querySelector(lcpEntry.name) as HTMLElement
            this.metrics = {
              element,
              renderTime: lcpEntry.startTime,
              size: this.getElementSize(element),
              url:
                element instanceof HTMLImageElement
                  ? element.src
                  : element?.getAttribute('src') || ''
            }
            resolve(this.metrics)
          }
        }
      })

      observer.observe({ entryTypes: ['largest-contentful-paint'] })
      this.observer = observer
    })
  }

  // 获取元素大小
  private static getElementSize(element: HTMLElement | null): number {
    if (!element) return 0

    const rect = element.getBoundingClientRect()
    return rect.width * rect.height
  }

  // 优化建议
  static getOptimizationSuggestions(metrics: LCPMetric): string[] {
    const suggestions: string[] = []

    if (metrics.renderTime > 2500) {
      suggestions.push('LCP时间过长，建议优化')

      if (metrics.url && !metrics.url.startsWith('data:')) {
        suggestions.push('优化关键图片资源')
      }

      if (metrics.size > 100000) { // 大于100KB
        suggestions.push('压缩或分割大型内容')
      }
    }

    return suggestions
  }

  // 停止观察
  static disconnect(): void {
    if (this.observer) {
      this.observer.disconnect()
      this.observer = null
    }
  }
}

// LCP优化组件
interface OptimizedImageProps {
  src: string
  alt: string
  priority?: boolean
  placeholder?: 'blur' | 'empty'
  sizes?: string
  className?: string
  width?: number
  height?: number
  onLoad?: () => void
}

export function OptimizedImage({
  src,
  alt,
  priority = false,
  placeholder = 'blur',
  sizes = '(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw',
  className = '',
  width,
  height,
  onLoad
}: OptimizedImageProps) {
  const [imageLoaded, setImageLoaded] = useState(false)
  const [imageError, setImageError] = useState(false)

  // 生成模糊数据URL
  const blurDataURL = useMemo(() => {
    return `data:image/svg+xml;base64,${Buffer.from(
      `<svg width="${width || 400}" height="${height || 300}" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#e5e7eb"/>
        <filter id="blur">
          <feGaussianBlur in="SourceGraphic" stdDeviation="3" />
        </filter>
        <rect width="100%" height="100%" filter="url(#blur)" opacity="0.4"/>
      </svg>`
    ).toString('base64')}`
  }, [width, height])

  const handleLoad = () => {
    setImageLoaded(true)
    onLoad?.()
  }

  const handleError = () => {
    setImageError(true)
  }

  return (
    <div className={`relative ${className}`}>
      <Image
        src={src}
        alt={alt}
        width={width}
        height={height}
        priority={priority}
        placeholder={placeholder}
        blurDataURL={blurDataURL}
        sizes={sizes}
        quality={priority ? 85 : 75}
        onLoad={handleLoad}
        onError={handleError}
        className={`
          transition-opacity duration-300
          ${imageLoaded ? 'opacity-100' : 'opacity-0'}
          ${imageError ? 'hidden' : ''}
        `}
        style={{
          objectFit: 'cover'
        }}
      />

      {/* 加载状态指示器 */}
      {!imageLoaded && !imageError && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse" />
      )}

      {/* 错误状态 */}
      {imageError && (
        <div className="absolute inset-0 bg-gray-100 flex items-center justify-center">
          <div className="text-gray-500 text-sm">
            图片加载失败
          </div>
        </div>
      )}
    </div>
  )
}
```

### CLS (Cumulative Layout Shift) 优化

```tsx
// src/components/performance/CLSOptimizer.tsx
import { useEffect, useState, useRef } from 'react'

interface CLSMetric {
  cls: number
  layoutShiftElements: LayoutShift[]
}

interface LayoutShift extends PerformanceEntry {
  value: number
  sources: PerformanceEntry[]
  endTime: number
  hadRecentInput: boolean
}

export class CLSOptimizer {
  private static observer: PerformanceObserver | null = null
  private static clsValue: number = 0
  private static layoutShiftEntries: LayoutShift[] = []

  // 监听CLS
  static observeCLS(): Promise<CLSMetric> {
    return new Promise((resolve) => {
      if (typeof window === 'undefined') {
        resolve({ cls: 0, layoutShiftElements: [] })
        return
      }

      let clsValue = 0
      let sessionValue = 0
      const sessionEntries: LayoutShift[] = []

      const observer = new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
          if (!(entry as LayoutShift).hadRecentInput) {
            sessionValue += (entry as LayoutShift).value
            sessionEntries.push(entry as LayoutShift)
          }
        }

        clsValue = Math.max(sessionValue, clsValue)

        // 会话结束后重置
        if (sessionEntries.length > 0) {
          setTimeout(() => {
            this.layoutShiftEntries.push(...sessionEntries)
            sessionEntries.length = 0
            sessionValue = 0
          }, 5000)
        }
      })

      observer.observe({ type: 'layout-shift', buffered: true })
      this.observer = observer

      // 页面卸载时返回最终值
      setTimeout(() => {
        resolve({
          cls: clsValue,
          layoutShiftElements: this.layoutShiftEntries
        })
      }, 10000)
    })
  }

  // 预加载字体
  static preloadFonts(fonts: string[]): void {
    if (typeof window === 'undefined') return

    fonts.forEach(font => {
      const link = document.createElement('link')
      link.rel = 'preload'
      link.as = 'font'
      link.crossOrigin = 'anonymous'
      link.href = font
      document.head.appendChild(link)
    })
  }

  // 预计算布局
  static precomputeLayout(element: HTMLElement): void {
    if (element && typeof window !== 'undefined') {
      // 强制布局计算
      element.style.display = 'none'
      element.offsetHeight // 触发重排
      element.style.display = ''
    }
  }

  // 预留空间
  static reserveSpace(selector: string, dimensions: { width: number; height: number }): void {
    const element = document.querySelector(selector) as HTMLElement
    if (element) {
      element.style.width = `${dimensions.width}px`
      element.style.height = `${dimensions.height}px`
    }
  }

  // 停止观察
  static disconnect(): void {
    if (this.observer) {
      this.observer.disconnect()
      this.observer = null
    }
  }
}

// CLS优化Hook
export function useCLS() {
  const [cls, setCLS] = useState<number>(0)
  const [layoutShifts, setLayoutShifts] = useState<LayoutShift[]>([])

  useEffect(() => {
    let mounted = true

    CLSOptimizer.observeCLS().then(metrics => {
      if (mounted) {
        setCLS(metrics.cls)
        setLayoutShifts(metrics.layoutShiftElements)
      }
    })

    return () => {
      mounted = false
    }
  }, [])

  return { cls, layoutShifts }
}

// 稳定的文本组件
interface StableTextProps {
  children: React.ReactNode
  className?: string
  style?: React.CSSProperties
}

export function StableText({ children, className = '', style }: StableTextProps) {
  const [textHeight, setTextHeight] = useState<number>(0)
  const textRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (textRef.current) {
      const height = textRef.current.offsetHeight
      setTextHeight(height)
    }
  }, [children])

  return (
    <div
      ref={textRef}
      className={className}
      style={{
        ...style,
        // 预设高度防止布局偏移
        minHeight: textHeight || 'auto'
      }}
    >
      {children}
    </div>
  )
}

// 广告位组件（预留空间）
interface AdPlaceholderProps {
  className?: string
  width: number
  height: number
  onLoad?: () => void
}

export function AdPlaceholder({ className = '', width, height, onLoad }: AdPlaceholderProps) {
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    CLSOptimizer.reserveSpace('.ad-placeholder', { width, height })
  }, [width, height])

  return (
    <div
      className={`ad-placeholder ${className}`}
      style={{
        width: `${width}px`,
        height: `${height}px`,
        backgroundColor: loaded ? 'transparent' : '#f3f4f6',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'background-color 0.3s'
      }}
    >
      {!loaded && (
        <div className="text-gray-500 text-sm">
          广告位
        </div>
      )}
    </div>
  )
}
```

### FID (First Input Delay) 优化

```tsx
// src/components/performance/FIDOptimizer.tsx
import { useEffect, useState } from 'react'

interface FIDMetric {
  fid: number
  inputType: string
  inputTarget: string
  inputTime: number
}

export class FIDOptimizer {
  private static observer: PerformanceObserver | null = null

  // 监听FID
  static observeFID(): Promise<FIDMetric> {
    return new Promise((resolve) => {
      if (typeof window === 'undefined') {
        resolve({ fid: 0, inputType: '', inputTarget: '', inputTime: 0 })
        return
      }

      const observer = new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries()
        const fidEntry = entries.find(
          entry => entry.name === 'first-input'
        ) as any

        if (fidEntry) {
          resolve({
            fid: fidEntry.processingStart - fidEntry.startTime,
            inputType: fidEntry.name,
            inputTarget: (fidEntry.target as Element).tagName,
            inputTime: fidEntry.startTime
          })
        }
      })

      observer.observe({ entryTypes: ['first-input'] })
      this.observer = observer
    })
  }

  // 监听交互
  static observeInteractions(): Promise<FIDMetric[]> {
    return new Promise((resolve) => {
      if (typeof window === 'undefined') {
        resolve([])
        return
      }

      const events: FIDMetric[] = []
      let timeoutId: NodeJS.Timeout

      const observer = new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
          if (entry.entryType === 'event' && (entry as any).processingStart) {
            events.push({
              fid: (entry as any).processingStart - entry.startTime,
              inputType: entry.name,
              inputTarget: (entry.target as Element).tagName,
              inputTime: entry.startTime
            })
          }
        }

        clearTimeout(timeoutId)
        timeoutId = setTimeout(() => {
          resolve(events)
        }, 1000)
      })

      observer.observe({ entryTypes: ['event'] })
      this.observer = observer
    })
  }

  // 停止观察
  static disconnect(): void {
    if (this.observer) {
      this.observer.disconnect()
      this.observer = null
    }
  }
}

// 优化输入组件
interface OptimizedInputProps {
  type: string
  placeholder?: string
  className?: string
  autoFocus?: boolean
  onFocus?: () => void
  onBlur?: () => void
  onChange?: (value: string) => void
  disabled?: boolean
}

export function OptimizedInput({
  type,
  placeholder,
  className = '',
  autoFocus = false,
  onFocus,
  onBlur,
  onChange,
  disabled = false
}: OptimizedInputProps) {
  const [isFocused, setIsFocused] = useState(false)
  const [hasInteracted, setHasInteracted] = useState(false)

  const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    setIsFocused(true)
    setHasInteracted(true)
    onFocus?.(e)
  }

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    setIsFocused(false)
    onBlur?.(e)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange?.(e.target.value)
  }

  return (
    <input
      type={type}
      placeholder={placeholder}
      className={`
        px-4 py-2 border border-gray-300 rounded-lg
        focus:ring-2 focus:ring-blue-500 focus:border-transparent
        disabled:bg-gray-100 disabled:cursor-not-allowed
        transition-all duration-200
        ${isFocused ? 'border-blue-500 shadow-lg' : ''}
        ${hasInteracted ? '' : 'animate-pulse'}
        ${className}
      `}
      autoFocus={autoFocus}
      onFocus={handleFocus}
      onBlur={handleBlur}
      onChange={handleChange}
      disabled={disabled}
      // 优化：提前渲染输入框避免延迟
      inputMode={type === 'email' ? 'email' : undefined}
      spellCheck={type === 'text' ? 'false' : undefined}
      autoComplete="off"
    />
  )
}
```

## 🏗️ 构建时优化

### 高级Turbopack配置（Next.js 16 默认）

Next.js 16 起，**Turbopack 已是 `next dev` 与 `next build` 的默认打包器**，Turbopack 配置从 `experimental.turbopack` 移至顶层 `turbopack` 键。Webpack 仅作为迁移期回退，需通过 `next dev --webpack` / `next build --webpack` 显式启用。

```javascript
// next.config.ts
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Turbopack 配置（Next.js 16：顶层键，不再是 experimental.turbopack）
  turbopack: {
    rules: {
      // SVG 作为 React 组件加载
      '*.svg': {
        loaders: ['@svgr/turbopack'],
        as: '*.js',
      },
    },
    resolveAlias: {
      // 在 tsconfig paths 之外补充自定义别名
      underscore: 'lodash',
    },
  },

  // 包优化：按需引入，减小 bundle
  optimizePackageImports: [
    'lucide-react',
    '@radix-ui/react-icons',
    'date-fns',
    'clsx',
    'tailwind-merge',
    'recharts',
  ],

  // 图片优化配置
  images: {
    // 现代图片格式
    formats: ['image/avif', 'image/webp'],

    // 响应式图片尺寸（Next.js 16 默认值已移除 16）
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048],
    imageSizes: [32, 48, 64, 96, 128, 256, 384],

    // 缓存优化（Next.js 16 默认 minimumCacheTTL 已由 60s 提升至 4 小时）
    minimumCacheTTL: 14400,

    // 安全配置
    dangerouslyAllowSVG: true,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",

    // 远程图片域名（Next.js 16：使用 remotePatterns 替代已弃用的 images.domains）
    remotePatterns: [
      { protocol: 'https', hostname: 'example.com' },
      { protocol: 'https', hostname: 'cdn.example.com' },
      { protocol: 'https', hostname: 'images.unsplash.com' },
    ],

    // Next.js 16：quality 默认收敛为 [75]，其他值需在 qualities 中显式声明
    qualities: [75, 90],
  },

  // 压缩配置
  compress: true,

  // 重定向配置
  async redirects() {
    return [
      {
        source: '/home',
        destination: '/',
        permanent: true
      },
      {
        source: '/docs',
        destination: '/documentation',
        permanent: true
      }
    ]
  },

  // 头部配置
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY'
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block'
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin'
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(self), microphone=(), geolocation=()'
          }
        ]
      },
      {
        source: '/api/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'no-store, must-revalidate'
          },
          {
            key: 'Access-Control-Allow-Origin',
            value: '*'
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET, POST, PUT, DELETE, OPTIONS'
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'Content-Type, Authorization'
          }
        ]
      },
      {
        source: '/(.*\\.(png|jpg|jpeg|gif|webp|svg))',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable'
          }
        ]
      }
    ]
  }
}

module.exports = nextConfig
```

> ⚠️ **Next.js 16 注意**：`next build` 不再运行 lint（`next lint` 命令已移除，请直接使用 ESLint/Biome CLI）。若确有遗留 Webpack 自定义配置无法迁移，可在迁移期使用 `next dev --webpack` / `next build --webpack` 回退。

### Bundle分析和优化

```typescript
// scripts/analyze-bundle.js
const { execSync } = require('child_process')
const path = require('path')
const fs = require('fs')

// 分析bundle大小
function analyzeBundleSize() {
  console.log('📊 Analyzing bundle size...')

  // 生成webpack bundle analyzer报告
  execSync('ANALYZE=true npm run build', {
    stdio: 'inherit'
  })

  // 读取构建结果
  const buildDir = path.join(process.cwd(), '.next')
  const statsPath = path.join(buildDir, 'static/chunks')

  if (fs.existsSync(statsPath)) {
    const chunks = fs.readdirSync(statsPath)
    let totalSize = 0

    chunks.forEach(chunk => {
      const chunkPath = path.join(statsPath, chunk)
      const stats = fs.statSync(chunkPath)
      totalSize += stats.size
      console.log(`📦 ${chunk}: ${(stats.size / 1024).toFixed(2)}KB`)
    })

    console.log(`📦 Total bundle size: ${(totalSize / 1024).toFixed(2)}KB`)
  }
}

// 分析依赖大小
function analyzeDependencies() {
  console.log('📦 Analyzing dependencies...')

  try {
    const packageJson = require(path.join(process.cwd(), 'package.json'))
    const dependencies = {
      ...packageJson.dependencies,
      ...packageJson.devDependencies
    }

    Object.entries(dependencies).forEach(([name, version]) => {
      const pkgPath = path.join(process.cwd(), 'node_modules', name)

      if (fs.existsSync(pkgPath)) {
        try {
          const pkgInfo = require(path.join(pkgPath, 'package.json'))
          const size = calculatePackageSize(pkgPath)
          console.log(`📦 ${name}@${version}: ${size}`)
        } catch (error) {
          console.log(`❌ ${name}: 无法读取包信息`)
        }
      }
    })
  } catch (error) {
    console.error('Error analyzing dependencies:', error)
  }
}

// 计算包大小
function calculatePackageSize(packagePath: string) {
  let totalSize = 0

  function calculateDirectorySize(dirPath) {
    const files = fs.readdirSync(dirPath)

    files.forEach(file => {
      const filePath = path.join(dirPath, file)
      const stats = fs.statSync(filePath)

      if (stats.isDirectory()) {
        totalSize += calculateDirectorySize(filePath)
      } else {
        totalSize += stats.size
      }
    })

    return totalSize
  }

  try {
    return calculateDirectorySize(packagePath)
  } catch (error) {
    return '0B'
  }
}

// 性能预算检查
function checkPerformanceBudget() {
  console.log('🎯 Checking performance budget...')

  const budgets = {
    javascript: 244 * 1024, // 244KB
    css: 100 * 1024,      // 100KB
    images: 1024 * 1024,   // 1MB
    fonts: 250 * 1024,      // 250KB
    total: 3 * 1024 * 1024 // 3MB
  }

  // 这里应该从实际构建结果中获取数据
  const actualSize = {
    javascript: 180 * 1024,
    css: 80 * 1024,
    images: 800 * 1024,
    fonts: 180 * 1024,
    total: 1240 * 1024
  }

  let passed = true

  Object.entries(budgets).forEach(([resource, limit]) => {
    const actual = actualSize[resource as keyof typeof actualSize]
    const percentage = (actual / limit) * 100

    if (actual > limit) {
      console.log(`❌ ${resource}: ${(actual / 1024).toFixed(2)}KB (${percentage.toFixed(1)}% > ${limit / 1024}KB)`)
      passed = false
    } else {
      console.log(`✅ ${resource}: ${(actual / 1024).toFixed(2)}KB (${percentage.toFixed(1)}% < ${limit / 1024}KB)`)
    }
  })

  if (actualSize.total > budgets.total) {
    console.log(`❌ Total: ${(actualSize.total / 1024 / 1024).toFixed(2)}MB > ${budgets.total / 1024 / 1024}MB`)
    passed = false
  } else {
    console.log(`✅ Total: ${(actualSize.total / 1024 / 1024).toFixed(2)}MB < ${budgets.total / 1024 / 1024}MB`)
  }

  return passed
}

// 生成性能报告
async function generatePerformanceReport() {
  console.log('📊 Generating performance report...')

  const report = {
    timestamp: new Date().toISOString(),
    bundleSize: await getBundleSize(),
    dependencies: await getDependencyAnalysis(),
    buildTime: await getBuildTime(),
    performanceBudget: checkPerformanceBudget()
  }

  // 保存报告
  fs.writeFileSync(
    path.join(process.cwd(), 'performance-report.json'),
    JSON.stringify(report, null, 2)
  )

  console.log('📊 Performance report saved to performance-report.json')
}

// 获取bundle大小
async function getBundleSize() {
  // 实现bundle大小获取逻辑
  return {
    javascript: 180000,
    css: 80000,
    images: 800000,
    fonts: 180000,
    total: 1240000
  }
}

// 获取依赖分析
async function getDependencyAnalysis() {
  // 实现依赖分析逻辑
  return {
    totalDependencies: 50,
    vulnerablePackages: 0,
    outdatedPackages: 3,
    duplicateDependencies: 2
  }
}

// 获取构建时间
async function getBuildTime() {
  // 实现构建时间获取逻辑
  return 45000 // 45秒
}

// 主函数
async function main() {
  console.log('🚀 Next.js Performance Analysis')
  console.log('=====================================')

  analyzeBundleSize()
  analyzeDependencies()
  const budgetPassed = checkPerformanceBudget()
  await generatePerformanceReport()

  console.log('=====================================')
  console.log(`Performance budget check: ${budgetPassed ? '✅ PASSED' : '❌ FAILED'}`)

  if (!budgetPassed) {
    console.log('💡 Consider optimizing bundle size to meet performance budget')
    process.exit(1)
  }
}

if (require.main === module) {
  main()
}
```

## 🖥️ 运行时性能优化

### 智能预取和缓存

```typescript
// src/components/performance/PrefetchManager.tsx
'use client'

import { useEffect, useRef, useCallback } from 'react'
import { usePathname, useRouter } from 'next/navigation'

interface PrefetchConfig {
  strategy: 'hover' | 'mount' | 'idle' | 'viewport' | 'manual'
  delay?: number
  threshold?: number
  priority?: 'high' | 'low'
}

interface PrefetchEntry {
  url: string
  config: PrefetchConfig
  element?: HTMLElement
  timeoutId?: NodeJS.Timeout
  observer?: IntersectionObserver
}

export class PrefetchManager {
  private static instance: PrefetchManager
  private prefetchQueue = new Map<string, PrefetchEntry>()
  private isPrefetching = false
  private maxConcurrent = 3
  private currentPrefetches = 0

  private constructor() {
    this.setupIdleCallback()
    this.setupVisibilityObserver()
  }

  static getInstance(): PrefetchManager {
    if (!PrefetchManager.instance) {
      PrefetchManager.instance = new PrefetchManager()
    }
    return PrefetchManager.instance
  }

  // 预取URL
  prefetch(url: string, config: PrefetchConfig = { strategy: 'hover' }): void {
    if (this.prefetchQueue.has(url)) {
      return
    }

    const entry: PrefetchEntry = {
      url,
      config
    }

    this.prefetchQueue.set(url, entry)
    this.processQueue()
  }

  // 处理队列
  private async processQueue(): Promise<void> {
    if (this.isPrefetching || this.currentPrefetches >= this.maxConcurrent) {
      return
    }

    const entries = Array.from(this.prefetchQueue.entries())
      .filter(([_, entry]) =>
        entry.config.priority === 'high' ||
        entry.config.strategy === 'viewport'
      )
      .sort((a, b) => {
        // 优先级排序
        const priorityA = a[1].config.priority === 'high' ? 1 : 0
        const priorityB = b[1].config.priority === 'high' ? 1 : 0
        return priorityB - priorityA
      })

    if (entries.length === 0) return

    const [url, entry] = entries[0]
    this.isPrefetching = true
    this.currentPrefetches++

    try {
      await this.executePrefetch(url, entry)
      this.prefetchQueue.delete(url)
    } catch (error) {
      console.warn(`Failed to prefetch ${url}:`, error)
    } finally {
      this.isPrefetching = false
      this.currentPrefetches--

      // 继续处理队列
      setTimeout(() => this.processQueue(), 100)
    }
  }

  // 执行预取
  private async executePrefetch(url: string, entry: PrefetchEntry): Promise<void> {
    // 添加链接到head
    const link = document.createElement('link')
    link.rel = 'prefetch'
    link.href = url
    link.as = 'document'

    document.head.appendChild(link)

    // 预取完成标记
    return new Promise((resolve) => {
      link.onload = resolve
      setTimeout(() => {
        if (document.head.contains(link)) {
          document.head.removeChild(link)
        }
      }, 5000)
    })
  }

  // 空闲时预取
  private setupIdleCallback(): void {
    if ('requestIdleCallback' in window) {
      const idleCallback = (deadline: IdleDeadline) => {
        while (deadline.timeRemaining() > 0 && this.prefetchQueue.size > 0) {
          const entries = Array.from(this.prefetchQueue.entries())
          const [url, entry] = entries[0]

          if (entry.config.strategy === 'idle') {
            this.executePrefetch(url, entry)
            this.prefetchQueue.delete(url)
          }
        }
      }

      requestIdleCallback(idleCallback)
    }
  }

  // 可见区域预取
  private setupVisibilityObserver(): void {
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              const link = entry.target as HTMLLinkElement
              if (link.rel === 'prefetch' && link.dataset.url) {
                this.executePrefetch(link.dataset.url, {
                  url: link.dataset.url,
                  config: { strategy: 'viewport' }
                })
              }
            }
          })
        },
        {
          rootMargin: '50px'
        }
      )

      // 监听data-prefetch元素
      document.addEventListener('DOMContentLoaded', () => {
        const links = document.querySelectorAll('link[data-prefetch]')
        links.forEach(link => observer.observe(link))
      })
    }
  }

  // 预取多个URL
  prefetchMany(urls: string[], config: PrefetchConfig = {}): void {
    urls.forEach(url => {
      this.prefetch(url, config)
    })
  }

  // 清除预取队列
  clearQueue(): void {
    this.prefetchQueue.clear()
  }

  // 获取预取状态
  getStats() {
    return {
      queueSize: this.prefetchQueue.size,
      isPrefetching: this.isPrefetching,
      currentPrefetches: this.currentPrefetches,
      maxConcurrent: this.maxConcurrent
    }
  }
}

// React Hook
export function usePrefetch() {
  const manager = PrefetchManager.getInstance()
  const router = useRouter()
  const pathname = usePathname()

  // 预取相关页面
  const prefetchRoute = useCallback((url: string) => {
    manager.prefetch(url, {
      strategy: 'hover',
      delay: 100
    })
  }, [manager])

  // 预取页面资源
  const prefetchPageResources = useCallback(async (url: string) => {
    try {
      // 获取页面HTML
      const response = await fetch(url)
      const html = await response.text()

      // 解析HTML中的资源
      const parser = new DOMParser()
      const doc = parser.parseFromString(html, 'text/html')

      // 预取关键资源
      const criticalResources = [
        ...Array.from(doc.querySelectorAll('link[rel="stylesheet"]')).map(link => link.href),
        ...Array.from(doc.querySelectorAll('script[src]')).map(script => script.src),
        ...Array.from(doc.querySelectorAll('img[src]')).slice(0, 3).map(img => img.src)
      ]

      criticalResources.forEach(resource => {
        manager.prefetch(resource, {
          strategy: 'idle',
          priority: 'high'
        })
      })
    } catch (error) {
      console.warn('Failed to prefetch page resources:', error)
    }
  }, [manager])

  // 智能预取相关页面
  useEffect(() => {
    // 预取登录页面
    if (pathname !== '/login') {
      manager.prefetch('/login', {
        strategy: 'idle',
        priority: 'low'
      })
    }

    // 预取用户可能访问的页面
    if (pathname === '/') {
      manager.prefetchMany([
        '/dashboard',
        '/settings',
        '/help'
      ], {
        strategy: 'idle',
        priority: 'low'
      })
    }
  }, [pathname, manager])

  return {
    prefetchRoute,
    prefetchPageResources,
    getStats: () => manager.getStats()
  }
}
```

### 智能组件加载

```tsx
// src/components/performance/LazyComponentLoader.tsx
'use client'

import { Suspense, lazy, useState, useEffect, useRef, ComponentType } from 'react'
import { ErrorBoundary, FallbackProps } from 'react-error-boundary'

interface LazyComponentOptions {
  fallback?: React.ReactNode
  errorFallback?: ComponentType<FallbackProps>
  delay?: number
  rootMargin?: string
  threshold?: number
}

// 创建懒加载组件
export function createLazyComponent<T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>,
  options: LazyComponentOptions = {}
) {
  // React.lazy 只接受加载函数一个参数（loading 选项属于 next/dynamic），
  // 加载态由下方 Suspense 的 fallback 兜底
  const LazyComponent = lazy(importFunc)

  return function LazyComponentWrapper(props: React.ComponentProps<T>) {
    return (
      <ErrorBoundary
        FallbackComponent={options.errorFallback || DefaultErrorFallback}
      >
        <Suspense fallback={options.fallback || <ComponentSkeleton />}>
          {options.delay ? (
            <DelayedComponent
              delay={options.delay}
              component={<LazyComponent {...props} />}
            />
          ) : (
            <LazyComponent {...props} />
          )}
        </Suspense>
      </ErrorBoundary>
    )
  }
}

// 延迟加载组件
function DelayedComponent({
  delay,
  component
}: {
  delay: number
  component: React.ReactElement
}) {
  const [showComponent, setShowComponent] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setShowComponent(true), delay)
    return () => clearTimeout(timer)
  }, [delay])

  if (!showComponent) {
    return <div style={{ height: '100px' }} />
  }

  return component
}

// 可视区域懒加载组件
function createViewportLazyComponent<T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>,
  options: LazyComponentOptions = {}
) {
  const LazyComponent = lazy(importFunc)

  function ViewportLazyComponent(props: React.ComponentProps<T>) {
    const [isVisible, setIsVisible] = useState(false)
    const elementRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
      const observer = new IntersectionObserver(
        (entries) => {
          const [entry] = entries
          if (entry.isIntersecting) {
            setIsVisible(true)
            observer.disconnect()
          }
        },
        {
          rootMargin: options.rootMargin || '200px',
          threshold: options.threshold || 0.1
        }
      )

      if (elementRef.current) {
        observer.observe(elementRef.current)
      }

      return () => observer.disconnect()
    }, [options.rootMargin, options.threshold])

    return (
      <div ref={elementRef} style={{ minHeight: '200px' }}>
        {isVisible ? (
          <LazyComponent {...props} />
        ) : (
          options.fallback || <ComponentSkeleton />
        )}
      </div>
    )
  }

  return ViewportLazyComponent
}

// 默认错误边界（FallbackProps 为 react-error-boundary 注入的 props）
function DefaultErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
      <h3 className="text-red-800 font-medium">组件加载失败</h3>
      <p className="text-red-600 text-sm mt-1">{error.message}</p>
      <button
        onClick={() => resetErrorBoundary()}
        className="mt-2 px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
      >
        重试
      </button>
    </div>
  )
}

// 组件骨架屏
function ComponentSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
      <div className="h-3 bg-gray-200 rounded w-full"></div>
      <div className="h-3 bg-gray-200 rounded w-5/6 mt-2"></div>
    </div>
  )
}

// 使用示例
const HeavyDashboard = createLazyComponent(
  () => import('./HeavyDashboard'),
  {
    fallback: <ComponentSkeleton />,
    delay: 200,
    rootMargin: '100px',
    threshold: 0.1
  }
)

const ChartComponent = createViewportLazyComponent(
  () => import('./ChartComponent'),
  {
    fallback: <ComponentSkeleton />,
    rootMargin: '50px'
  }
)
```

## 📈 性能监控和分析

### 实时性能监控

```tsx
// src/lib/performance/PerformanceMonitor.ts
import { onCLS, onFID, onFCP, onINP, onLCP, onTTFB } from 'web-vitals'
import { useState, useEffect } from 'react'

// gtag 是 GA 全局注入的函数（未安装 @types/gtag.js 时需手动声明）
declare function gtag(command: string, ...args: unknown[]): void

interface PerformanceMetrics {
  lcp: number
  fid: number
  cls: number
  fcp: number
  ttfb: number
  inp: number
  tti: number
  clsr: number
  si: number
  timestamp: string
}

// 指标阈值类型（config 与 generateRecommendations 共用）
interface PerformanceThresholds {
  lcp: number
  fid: number
  cls: number
  fcp: number
  ttfb: number
  tti: number
}

export class PerformanceMonitor {
  private static instance: PerformanceMonitor
  private metrics: PerformanceMetrics | null = null
  private observers: PerformanceObserver[] = []
  private config = {
    reportInterval: 5000, // 5秒
    thresholds: {
      lcp: 2500,    // 2.5s
      fid: 100,     // 100ms
      cls: 0.1,     // 0.1
      fcp: 1800,    // 1.8s
      ttfb: 800,    // 800ms
      tti: 3800     // 3.8s
    }
  }

  private constructor() {
    this.startMonitoring()
  }

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor()
    }
    return PerformanceMonitor.instance
  }

  // 开始监控
  private startMonitoring(): void {
    // 监听Core Web Vitals：web-vitals 为每项指标提供独立的注册函数，
    // 不存在聚合式的 reportWebVitals 导出
    onCLS(this.handleCLS.bind(this))
    onFID(this.handleFID.bind(this))
    onLCP(this.handleLCP.bind(this))
    onTTFB(this.handleTTFB.bind(this))
    onFCP(this.handleFCP.bind(this))
    onINP(this.handleINP.bind(this))

    // 定期报告
    setInterval(() => {
      this.reportMetrics()
    }, this.config.reportInterval)
  }

  private handleCLS = (metric: any): void => {
    if (this.metrics) {
      this.metrics.cls = metric.value
    }
  }

  private handleFID = (metric: any): void => {
    if (this.metrics) {
      this.metrics.fid = metric.value
    }
  }

  private handleLCP = (metric: any): void => {
    if (this.metrics) {
      this.metrics.lcp = metric.renderTime || metric.startTime
    }
  }

  private handleFCP = (metric: any): void => {
    if (this.metrics) {
      this.metrics.fcp = metric.renderTime || metric.loadTime
    }
  }

  private handleTTFB = (metric: any): void => {
    if (this.metrics) {
      this.metrics.ttfb = metric.value
    }
  }

  private handleINP = (metric: any): void => {
    if (this.metrics) {
      this.metrics.inp = metric.value
    }
  }

  // 报告指标
  private reportMetrics(): void {
    if (!this.metrics) return

    const { metrics, config } = this
    const { thresholds } = config

    const report = {
      timestamp: new Date().toISOString(),
      metrics: {
        lcp: {
          value: metrics.lcp,
          threshold: thresholds.lcp,
          status: metrics.lcp <= thresholds.lcp ? 'good' : 'needs-improvement'
        },
        fid: {
          value: metrics.fid,
          threshold: thresholds.fid,
          status: metrics.fid <= thresholds.fid ? 'good' : 'needs-improvement'
        },
        cls: {
          value: metrics.cls,
          threshold: thresholds.cls,
          status: metrics.cls <= thresholds.cls ? 'good' : 'needs-improvement'
        },
        fcp: {
          value: metrics.fcp,
          threshold: thresholds.fcp,
          status: metrics.fcp <= thresholds.fcp ? 'good' : 'needs-improvement'
        },
        ttfb: {
          value: metrics.ttfb,
          threshold: thresholds.ttfb,
          status: metrics.ttfb <= thresholds.ttfb ? 'good' : 'needs-improvement'
        }
      },
      recommendations: this.generateRecommendations(metrics, thresholds)
    }

    // 发送到分析服务
    this.sendToAnalytics(report)

    // 显示性能警告
    this.showPerformanceWarnings(report)
  }

  // 生成优化建议
  private generateRecommendations(
    metrics: PerformanceMetrics,
    thresholds: PerformanceThresholds
  ): string[] {
    const recommendations: string[] = []

    if (metrics.lcp > thresholds.lcp) {
      recommendations.push('优化LCP：预加载关键资源、优化服务器响应时间、使用CDN')
    }

    if (metrics.fid > thresholds.fid) {
      recommendations.push('优化FID：减少JavaScript执行时间、拆分代码、使用Web Workers')
    }

    if (metrics.cls > thresholds.cls) {
      recommendations.push('优化CLS：预留图片尺寸、避免布局偏移、使用骨架屏')
    }

    if (metrics.fcp > thresholds.fcp) {
      recommendations.push('优化FCP：减少服务器渲染时间、预加载HTML、启用压缩')
    }

    if (metrics.ttfb > thresholds.ttfb) {
      recommendations.push('优化TTFB：减少阻塞渲染、内联关键CSS、优化字体加载')
    }

    return recommendations
  }

  // 发送到分析服务
  private sendToAnalytics(report: any): void {
    // 发送到分析服务
    if (typeof gtag !== 'undefined') {
      gtag('event', 'web_vitals', {
        event_category: 'Performance',
        event_label: 'Web Vitals Report',
        custom_page_location: window.location.href,
        value: report.metrics.lcp.value,
        fid: report.metrics.fid.value,
        cls: report.metrics.cls.value
      })
    }

    // 发送到自定义分析服务
    fetch('/api/analytics/performance', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(report)
    }).catch(error => {
      console.error('Failed to send analytics data:', error)
    })
  }

  // 显示性能警告
  private showPerformanceWarnings(report: any): void {
    const needsImprovement = Object.values(report.metrics)
      .filter((metric: any) => metric.status === 'needs-improvement')

    if (needsImprovement.length > 0) {
      console.group('🚨 Performance Issues Detected')
      needsImprovement.forEach((metric: any) => {
        console.warn(
          `${metric.name}: ${metric.value} (${metric.status})`
        )
        metric.recommendations?.forEach((rec: string) => {
          console.log(`  💡 ${rec}`)
        })
      })
      console.groupEnd()
    }
  }

  // 获取当前指标
  getMetrics(): PerformanceMetrics | null {
    return this.metrics
  }

  // 停止监控
  stop(): void {
    this.observers.forEach(observer => observer.disconnect())
    this.observers = []
  }
}

// React Hook
export function usePerformanceMonitor() {
  const monitor = PerformanceMonitor.getInstance()
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null)
  const [isMonitoring, setIsMonitoring] = useState(true)

  useEffect(() => {
    if (!metrics && isMonitoring) {
      const interval = setInterval(() => {
        setMetrics(monitor.getMetrics())
      }, 1000)

      return () => clearInterval(interval)
    }
  }, [metrics, isMonitoring, monitor])

  return {
    metrics,
    isMonitoring,
    stopMonitoring: () => {
      setIsMonitoring(false)
    }
  }
}

// 性能仪表板组件
export function PerformanceDashboard() {
  const { metrics } = usePerformanceMonitor()

  if (!metrics) {
    return <div>Loading performance data...</div>
  }

  const getScoreColor = (value: number, threshold: number) => {
    if (value <= threshold) return 'text-green-600'
    if (value <= threshold * 1.5) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreText = (value: number, threshold: number) => {
    if (value <= threshold) return 'Good'
    if (value <= threshold * 1.5) return 'Needs Improvement'
    return 'Poor'
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6">Performance Dashboard</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* LCP */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-semibold">LCP</h3>
            <span className={`text-sm font-medium ${getScoreColor(metrics.lcp, 2500)}`}>
              {getScoreText(metrics.lcp, 2500)}
            </span>
          </div>
          <div className="relative w-full h-2 bg-gray-200 rounded-full">
            <div
              className="absolute top-0 left-0 h-full bg-blue-600 rounded-full"
              style={{
                width: `${Math.min((metrics.lcp / 4000) * 100, 100)}%`
              }}
            />
          </div>
          <p className="text-sm text-gray-600 mt-2">
            {(metrics.lcp / 1000).toFixed(2)}s
          </p>
        </div>

        {/* FID */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-semibold">FID</h3>
            <span className={`text-sm font-medium ${getScoreColor(metrics.fid, 100)}`}>
              {getScoreText(metrics.fid, 100)}
            </span>
          </div>
          <div className="relative w-full h-2 bg-gray-200 rounded-full">
            <div
              className="absolute top-0 left-0 h-full bg-green-600 rounded-full"
              style={{
                width: `${Math.min((metrics.fid / 200) * 100, 100)}%`
              }}
            />
          </div>
          <p className="text-sm text-gray-600 mt-2">
            {metrics.fid ? `${metrics.fid}ms` : 'N/A'}
          </p>
        </div>

        {/* CLS */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-semibold">CLS</h3>
            <span className={`text-sm font-medium ${getScoreColor(metrics.cls, 0.1)}`}>
              {getScoreText(metrics.cls, 0.1)}
            </span>
          </div>
          <div className="relative w-full h-2 bg-gray-200 rounded-full">
            <div
              className="absolute top-0 left-0 h-full bg-purple-600 rounded-full"
              style={{
                width: `${Math.max((metrics.cls / 0.5) * 100, 100)}%`
              }}
            />
          </div>
          <p className="text-sm text-gray-600 mt-2">
            {(metrics.cls * 100).toFixed(3)}
          </p>
        </div>

        {/* FCP */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-semibold">FCP</h3>
            <span className={`text-sm font-medium ${getScoreColor(metrics.fcp, 1800)}`}>
              {getScoreText(metrics.fcp, 1800)}
            </span>
          </div>
          <div className="relative w-full h-2 bg-gray-200 rounded-full">
            <div
              className="absolute top-0 left-0 h-full bg-orange-600 rounded-full"
              style={{
                width: `${Math.min((metrics.fcp / 3000) * 100, 100)}%`
              }}
            />
          </div>
          <p className="text-sm text-gray-600 mt-2">
            {(metrics.fcp / 1000).toFixed(2)}s
          </p>
        </div>

        {/* TTFB */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-semibold">TTFB</h3>
            <span className={`text-sm font-medium ${getScoreColor(metrics.ttfb, 800)}`}>
              {getScoreText(metrics.ttfb, 800)}
            </span>
          </div>
          <div className="relative w-full h-2 bg-gray-200 rounded-full">
            <div
              className="absolute top-0 left-0 h-full bg-teal-600 rounded-full"
              style={{
                width: `${Math.min((metrics.ttfb / 1600) * 100, 100)}%`
              }}
            />
            </div>
          <p className="text-sm text-gray-600 mt-2">
            {(metrics.ttfb / 1000).toFixed(2)}s
          </p>
        </div>
      </div>

      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-4">Performance Score</h3>
        <div className="bg-gray-200 rounded-full h-4">
          <div
            className="bg-green-600 h-4 rounded-full"
            style={{
              width: `${Math.max(0, Object.values({
                lcp: Math.max(0, 100 - (metrics.lcp / 4000) * 100),
                fid: Math.max(0, 100 - (metrics.fid / 200) * 100),
                cls: Math.max(0, 100 - (metrics.cls / 0.5) * 100),
                fcp: Math.max(0, 100 - (metrics.fcp / 3000) * 100)
              }).reduce((sum, score) => sum + score, 0) / 4)}%`
            }}
          />
          </div>
        </div>
    </div>
  )
}
```

## ✅ 总结

通过本指南，你已经掌握了Next.js 16的企业级性能优化能力：

### 📊 Core Web Vitals优化
- LCP优化策略和图片预加载技术
- CLS防止和布局稳定性保证
- FID优化和交互响应性提升
- 完整的性能监控和分析体系

### 🏗️ 构建时优化
- Turbopack配置和Webpack优化
- Bundle分析和依赖优化
- 性能预算管理和自动化检查
- 现代构建工具和最佳实践

### 🖥️ 运行时优化
- 智能预取和缓存策略
- 组件懒加载和代码分割
- 实时性能监控和预警系统
- 用户体验优化和渐进式增强

### 📈 性能监控分析
- Core Web Vitals实时监控
- 性能数据收集和分析
- 自动化性能报告生成
- 性能问题诊断和优化建议

## 📚 下一步学习

- 深入学习Web性能API和浏览器优化
- 掌握高级性能测试和压力测试
- 学习A/B测试和性能迭代
- 探索微前端性能优化策略
- 了解边缘计算和CDN性能优化

## 🔗 相关资源链接

### 官方资源
- [Next.js 性能优化文档](https://nextjs.org/docs/advanced-features/measuring-performance)
- [Web.dev Core Web Vitals](https://web.dev/vitals/)
- [Lighthouse 性能审计](https://developer.chrome.com/docs/lighthouse/)
- [WebPageTest 性能测试](https://www.webpagetest.org/)

### 技术文章
- [Core Web Vitals 最佳实践](https://web.dev/learn-web-vitals/)
- [Next.js 图片优化指南](https://nextjs.org/docs/api-reference/next/image)
- [Turbopack 性能优化](https://turbo.build/repack)
- [Bundle 分析工具](https://webpack.js.org/guides/code-splitting/)

### 工具和资源
- [Chrome DevTools Performance](https://developer.chrome.com/docs/devtools/performance/)
- [Webpack Bundle Analyzer](https://www.npmjs.com/package/webpack-bundle-analyzer)
- [Web Vitals 库](https://www.npmjs.com/package/web-vitals)
- [PageSpeed Insights](https://pagespeed.web.dev/)

## 📚 模块内相关文档

### 同模块相关文档
- [Next.js 16 完整指南](./01-nextjs-16-complete.md) - 学习Next.js 16内置的性能优化特性
- [React 19 深度集成](./02-react-19-integration.md) - 掌握React 19并发渲染的性能优势
- [全栈开发模式](./03-full-stack-patterns.md) - 了解全栈应用的性能优化策略

### 相关知识模块
- [测试相关模块](../testing/01-unit-testing.md) - 性能测试和单元测试策略
- [部署相关模块](../deployment/01-vercel-deployment.md) - Vercel平台的性能优化配置
- [部署相关模块](../deployment/04-monitoring-analytics.md) - 应用性能监控和分析

### 基础前置知识
- [Web性能优化基础](../advanced-topics/performance/01-core-web-vitals.md) - Web性能优化的核心概念
- [浏览器渲染原理](../reference/performance-optimization/01-rendering-optimization.md) - 理解浏览器渲染和优化机制
- [HTTP/2 和网络优化](../reference/performance-optimization/02-bundle-optimization.md) - 网络层优化技术

---

## ✨ 总结

### 性能优化的交付边界

1. **先定义用户旅程和基线**：选择一个真实页面和关键操作，记录设备档位、网络、缓存状态、样本窗口与 LCP、INP、CLS、接口延迟或长任务等指标。不要把一次本机刷新速度当作总体性能结论。
2. **定位后只改变一个主要因素**：通过浏览器性能工具、服务端追踪或 bundle 报告判断瓶颈属于图片、JavaScript、服务端数据、渲染阻塞或交互，再做一个针对性改动；保存前后结果与可能的副作用。
3. **构建优化以产物为准**：动态导入、代码分割和依赖替换要检查实际构建输出与关键路由加载链。少一个源码 import 不保证首屏更小，也不保证请求瀑布没有变长。
4. **缓存与预取要有失效和预算**：说明哪些数据允许陈旧、如何失效、预取何时取消，以及它为低带宽、低内存用户增加了多少额外流量。缓存命中不应返回错误身份或过期权限数据。
5. **监控帮助持续发现回归**：为指标设置基线、告警或报告阈值，关联 release 和页面路径；回归发生后保留可定位证据并验证修复，而不是只长期收集图表。

### 学习成果验收

- [ ] 在固定设备、网络和缓存条件下为一个关键旅程记录优化前基线，包含样本数与指标来源。
- [ ] 使用性能工具定位一个可解释瓶颈，实施单一改动后比较前后指标，同时记录未改善或变差的指标。
- [ ] 分析生产构建，证明目标路由的初始资源或加载链确实改变，而非只观察开发服务器输出。
- [ ] 对缓存或预取场景演练失效、身份切换和网络受限，确认没有错误数据泄露或不可取消的额外请求。
- [ ] 为一次人为回归或已知慢路径确认监控能关联页面和 release，并记录诊断到修复验证的过程。

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
- **问题反馈**: [GitHub Issues](https://github.com/x-rush/dev-quest/issues)
- **内容建议**: [Discussion板块](https://github.com/x-rush/dev-quest/discussions)
- **技术交流**: 欢迎提交PR或Issue参与讨论

### 贡献者
- Dev Quest Team - 核心内容开发
- 社区贡献者 - 内容完善和纠错

---

**📜 文档版本**: v1.0.0
**📅 最后更新**: 2026年9月
**🏷️ 标签**: `#performance` `#optimization` `#core-web-vitals` `#bundle-analysis` `#monitoring`
**⭐ 推荐指数**: ⭐⭐⭐

**💡 提示**: 本模块为性能优化高级模块，建议先掌握Next.js 16基础和Web性能基础知识后再进行学习。

**🎯 学习建议**:
- 建议学习周期: 2-3周
- 理论与实践时间比例: 3:7
- 重点掌握Core Web Vitals优化和性能监控
- 结合真实项目进行性能测试和优化实践

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
