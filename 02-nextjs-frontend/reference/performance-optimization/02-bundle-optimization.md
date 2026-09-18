# Next.js 16 打包优化完全指南

> **文档简介**: Next.js 16 现代打包优化完整指南，涵盖代码分割、Tree Shaking、Bundle分析、Turbopack优化等现代打包技术

> **目标读者**: 具备Next.js基础的中高级开发者，需要优化应用性能和打包体积的前端工程师

> **前置知识**: Next.js 16基础、Webpack/Turbopack概念、HTTP协议、性能优化基础、JavaScript模块化

> **预计时长**: 6-10小时

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `reference` |
| **难度** | ⭐⭐⭐ (精通)|
| **标签** | `#bundle-optimization` `#code-splitting` `#tree-shaking` `#performance` `#webpack` `#turbopack` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 🎯 学习目标

### 📦 企业级打包优化
- 掌握Next.js 16现代化打包工具链和优化策略
- 实现智能代码分割和动态导入，优化初始加载性能
- 运用Tree Shaking消除无用代码，减少打包体积
- 掌握Bundle分析和监控工具，持续优化性能
- 实现现代化的缓存策略和长期缓存机制
- 配置Turbopack获得极致的构建性能

### 🚀 高级优化技术
- 实现微前端和模块联邦架构的打包优化
- 掌握服务端组件和客户端组件的打包策略
- 实现现代化的依赖管理和vendor优化
- 掌握字体、图片、静态资源的优化策略
- 实现CDN和边缘计算的资源分发优化
- 构建自动化性能监控和告警系统

### 🏗️ 企业级最佳实践
为关键页面记录初始下载量、执行成本和交互延迟，性能预算从目标设备和用户网络推导。包大小增加时查看新增了哪个依赖、进入了哪些路由，不只看整个仓库压缩后的总数。

把分析和比较接入构建流程，超过预算时输出可定位的差异与例外说明。多环境构建要确认公开配置与秘密边界，团队规范围绕可重复测量和回归判断，而不是要求每次都采用更多优化工具。

## 📖 概述

Next.js 16 提供了业界领先的打包优化生态系统，结合 Webpack 5 和革命性的 Turbopack，为现代Web应用提供了极致的构建性能和运行时优化。本指南深入探讨企业级打包优化技术，从基础的代码分割到高级的微前端架构，帮助你构建高性能、可维护的现代化应用。

## 🏗️ Next.js 16 打包架构概览

### 打包工具生态

#### 🚀 Turbopack (Next.js 16 默认打包器)
```typescript
// next.config.ts
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Next.js 16：Turbopack 是 next dev 与 next build 的默认打包器，
  // 配置位于顶层 turbopack 键（不再是 experimental.turbo）
  turbopack: {
    rules: {
      '*.svg': {
        loaders: ['@svgr/turbopack'],
        as: '*.js',
      },
    },
  },
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
}

module.exports = nextConfig
```

**Turbopack 核心优势**:
- **增量构建**: 99%的更新时间 < 100ms，Fast Refresh 最快可达 5-10 倍提升
- **内存缓存**: 智能依赖图缓存，支持文件系统缓存进一步加速启动
- **并行处理**: 多核CPU充分利用，生产构建相比 Webpack 快 2-5 倍
- **TypeScript集成**: 原生TS支持，无需额外配置

#### 📦 Webpack (迁移期回退)
```typescript
// next.config.ts - Webpack 自定义配置
// ⚠️ Next.js 16 中 Webpack 不再是默认打包器：检测到 webpack 配置时
// 必须以 next dev --webpack / next build --webpack 显式启用，否则构建失败
/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // 生产环境优化
    if (!dev && !isServer) {
      config.optimization = {
        ...config.optimization,
        usedExports: true,
        sideEffects: false,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            default: {
              minChunks: 2,
              priority: -20,
              reuseExistingChunk: true,
            },
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendors',
              priority: -10,
              chunks: 'all',
            },
            react: {
              test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
              name: 'react',
              priority: 20,
              chunks: 'all',
            },
          },
        },
      }
    }

    // 自定义解析规则
    config.resolve.extensions = ['.tsx', '.ts', '.jsx', '.js', '.json']

    return config
  },
}

module.exports = nextConfig
```

## 🔄 代码分割策略

### 自动代码分割

#### 📄 基于路由的分割
```tsx
// app/dashboard/page.tsx - 自动分割
import { Suspense } from 'react'
import DashboardLayout from '@/components/dashboard/DashboardLayout'
import DashboardOverview from '@/components/dashboard/DashboardOverview'
import RecentActivity from '@/components/dashboard/RecentActivity'

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <Suspense fallback={<div>Loading overview...</div>}>
        <DashboardOverview />
      </Suspense>
      <Suspense fallback={<div>Loading activity...</div>}>
        <RecentActivity />
      </Suspense>
    </DashboardLayout>
  )
}
```

#### 🧩 基于组件的分割
```tsx
// components/lazy/HeavyComponent.tsx
'use client'

import { useState, useEffect } from 'react'

export default function HeavyComponent() {
  const [data, setData] = useState(null)

  useEffect(() => {
    // 模拟重型数据加载
    import('@/lib/heavy-computation').then(module => {
      const result = module.computeComplexData()
      setData(result)
    })
  }, [])

  return (
    <div>
      <h2>Heavy Component</h2>
      {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
    </div>
  )
}

// pages/heavy-page.tsx
import dynamic from 'next/dynamic'
import { Suspense } from 'react'

// 动态导入重型组件
const HeavyComponent = dynamic(() => import('@/components/lazy/HeavyComponent'), {
  loading: () => <div>Loading heavy component...</div>,
  ssr: false, // 客户端渲染
})

export default function HeavyPage() {
  return (
    <div>
      <h1>Heavy Page</h1>
      <Suspense fallback={<div>Loading...</div>}>
        <HeavyComponent />
      </Suspense>
    </div>
  )
}
```

### 动态导入模式

#### 🎯 按需加载
```tsx
// lib/dynamic-imports.ts
export const loadChartLibrary = () => import('chart.js')
export const loadEditor = () => import('@/components/editor/AdvancedEditor')
export const loadAdminPanel = () => import('@/components/admin/AdminPanel')

// components/charts/DynamicChart.tsx
'use client'

import { useState, useEffect, useRef } from 'react'

interface ChartProps {
  type: 'line' | 'bar' | 'pie'
  data: any[]
}

export default function DynamicChart({ type, data }: ChartProps) {
  const [ChartComponent, setChartComponent] = useState<any>(null)

  useEffect(() => {
    const loadChart = async () => {
      try {
        const chartModule = await import('chart.js/auto')
        const Chart = chartModule.default

        setChartComponent(() => {
          return (props: any) => {
            const canvasRef = useRef<HTMLCanvasElement>(null)

            useEffect(() => {
              if (canvasRef.current) {
                const ctx = canvasRef.current.getContext('2d')
                new Chart(ctx, {
                  type,
                  data: props.data,
                  options: props.options,
                })
              }
            }, [])

            return <canvas ref={canvasRef} />
          }
        })
      } catch (error) {
        console.error('Failed to load chart library:', error)
      }
    }

    // 只在需要时加载
    if (data.length > 0) {
      loadChart()
    }
  }, [type, data])

  if (!ChartComponent) {
    return <div className="chart-placeholder">Loading chart...</div>
  }

  return <ChartComponent data={data} />
}
```

#### 📱 基于设备条件的加载
```tsx
// components/device/DetectDevice.tsx
'use client'

import { useEffect, useState } from 'react'

export default function DetectDevice({ children }: { children: React.ReactNode }) {
  const [isMobile, setIsMobile] = useState(false)
  const [isTablet, setIsTablet] = useState(false)

  useEffect(() => {
    const checkDevice = () => {
      setIsMobile(window.innerWidth < 768)
      setIsTablet(window.innerWidth >= 768 && window.innerWidth < 1024)
    }

    checkDevice()
    window.addEventListener('resize', checkDevice)
    return () => window.removeEventListener('resize', checkDevice)
  }, [])

  // 基于设备类型动态加载组件
  if (isMobile) {
    return <>{children}</>
  }

  if (isTablet) {
    return <>{children}</>
  }

  // 桌面端加载更多功能
  return <>{children}</>
}

// pages/adaptive-page.tsx
import dynamic from 'next/dynamic'
import DetectDevice from '@/components/device/DetectDevice'

// 桌面端专用组件
const DesktopFeatures = dynamic(
  () => import('@/components/desktop/DesktopFeatures'),
  {
    loading: () => null,
    ssr: false
  }
)

// 移动端专用组件
const MobileFeatures = dynamic(
  () => import('@/components/mobile/MobileFeatures'),
  {
    loading: () => null,
    ssr: false
  }
)

export default function AdaptivePage() {
  return (
    <DetectDevice>
      <div>
        <h1>Adaptive Content</h1>
        <DesktopFeatures />
        <MobileFeatures />
      </div>
    </DetectDevice>
  )
}
```

## 🌳 Tree Shaking 优化

### 配置优化

#### 📦 package.json 优化
```json
{
  "name": "my-nextjs-app",
  "sideEffects": [
    "**/*.css",
    "**/*.scss",
    "**/*.module.css",
    "**/*.module.scss",
    "./src/components/**/*.tsx",
    "./src/styles/**/*"
  ],
  "exports": {
    ".": {
      "import": "./dist/index.esm.js",
      "require": "./dist/index.cjs.js",
      "types": "./dist/index.d.ts"
    },
    "./components": {
      "import": "./dist/components/index.esm.js",
      "require": "./dist/components/index.cjs.js"
    }
  }
}
```

#### 🔧 ES模块优化
```typescript
// lib/utils.ts - ES模块写法
// ✅ 正确：具名导出，支持Tree Shaking
export const formatDate = (date: Date): string => {
  return date.toLocaleDateString()
}

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

// ❌ 错误：默认导出整个库，无法Tree Shaking
export default {
  formatDate,
  debounce,
  throttle
}

// 使用方式 - 支持Tree Shaking
import { formatDate, debounce } from '@/lib/utils'
```

#### 📚 依赖库优化
```typescript
// lib/optimized-imports.ts
// ✅ 正确：按需导入大型库
import { getAuth, signInWithPopup, GoogleAuthProvider } from 'firebase/auth'
import { collection, query, where, getDocs } from 'firebase/firestore'
import { Button } from '@/components/ui/button' // 按需导入UI组件
import { format } from 'date-fns' // 只导入需要的函数

// ❌ 错误：导入整个库
import firebase from 'firebase'
import * as firebase from 'firebase'
import { DatePicker, TimePicker, Calendar } from 'antd' // 导入未使用的组件

// Lodash 按需导入示例
import { debounce, throttle, cloneDeep } from 'lodash-es'

// 或者使用更小的替代库
import { debounce } from 'just-debounce-it'
import { throttle } from 'just-throttle'

// 图标库按需导入
import {
  HomeIcon,
  UserIcon,
  SettingsIcon
} from '@heroicons/react/24/outline'

// 或者使用更小的图标库
import {
  home,
  user,
  settings
} from 'lucide-react'
```

### Bundle分析和监控

#### 📊 Webpack Bundle Analyzer
```typescript
// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

/** @type {import('next').NextConfig} */
const nextConfig = {
  // ... 其他配置
}

module.exports = withBundleAnalyzer(nextConfig)
```

```json
// package.json scripts
{
  "scripts": {
    "analyze": "ANALYZE=true next build",
    "build:analyze": "npm run analyze"
  }
}
```

#### 📈 自定义Bundle分析
```typescript
// scripts/analyze-bundle.js
const fs = require('fs')
const path = require('path')

function analyzeBundle(buildDir = '.next') {
  const manifestPath = path.join(buildDir, 'build-manifest.json')

  if (!fs.existsSync(manifestPath)) {
    console.error('Build manifest not found. Run `next build` first.')
    return
  }

  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'))
  const stats = {
    totalFiles: 0,
    totalSize: 0,
    files: [],
    largestFiles: [],
    dependencies: new Set(),
  }

  // 分析页面文件
  Object.entries(manifest.pages).forEach(([page, files]) => {
    files.forEach(file => {
      const filePath = path.join(buildDir, file)
      if (fs.existsSync(filePath)) {
        const fileStats = fs.statSync(filePath)
        const size = fileStats.size

        stats.totalFiles++
        stats.totalSize += size

        stats.files.push({
          page,
          file,
          size: formatBytes(size),
          sizeBytes: size,
        })
      }
    })
  })

  // 找出最大的文件
  stats.largestFiles = stats.files
    .sort((a, b) => b.sizeBytes - a.sizeBytes)
    .slice(0, 10)

  // 输出分析结果
  console.log('📊 Bundle Analysis Report')
  console.log('========================')
  console.log(`Total Files: ${stats.totalFiles}`)
  console.log(`Total Size: ${formatBytes(stats.totalSize)}`)
  console.log('')

  console.log('🔍 Largest Files:')
  stats.largestFiles.forEach((file, index) => {
    console.log(`${index + 1}. ${file.file} (${file.size}) - ${file.page}`)
  })

  return stats
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 运行分析
analyzeBundle()
```

#### 🚨 Bundle大小监控
```typescript
// scripts/bundle-size-monitor.js
const fs = require('fs')
const path = require('path')

const BUDGET_LIMITS = {
  'pages/_app.js': 100 * 1024, // 100KB
  'pages/_document.js': 50 * 1024, // 50KB
  'pages/index.js': 150 * 1024, // 150KB
  'framework.js': 200 * 1024, // 200KB
  'main.js': 100 * 1024, // 100KB
}

function checkBundleSize(buildDir = '.next') {
  const manifestPath = path.join(buildDir, 'build-manifest.json')

  if (!fs.existsSync(manifestPath)) {
    console.error('Build manifest not found')
    process.exit(1)
  }

  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'))
  let warnings = 0
  let errors = 0

  console.log('🔍 Bundle Size Check')
  console.log('===================')

  // 检查每个页面的大小
  Object.entries(manifest.pages).forEach(([page, files]) => {
    files.forEach(file => {
      const filePath = path.join(buildDir, file)
      if (fs.existsSync(filePath)) {
        const fileStats = fs.statSync(filePath)
        const size = fileStats.size

        // 检查预算限制
        const budgetLimit = BUDGET_LIMITS[file] || BUDGET_LIMITS[path.basename(file)]

        if (budgetLimit) {
          const percentage = (size / budgetLimit * 100).toFixed(1)
          const status = percentage > 100 ? '🚨' : percentage > 80 ? '⚠️' : '✅'

          console.log(`${status} ${file}: ${formatBytes(size)} (${percentage}% of limit)`)

          if (percentage > 100) {
            errors++
            console.error(`   ❌ Exceeds budget limit of ${formatBytes(budgetLimit)}`)
          } else if (percentage > 80) {
            warnings++
            console.warn(`   ⚠️ Approaching budget limit`)
          }
        } else {
          console.log(`ℹ️  ${file}: ${formatBytes(size)}`)
        }
      }
    })
  })

  console.log('')
  console.log(`Summary: ${errors} errors, ${warnings} warnings`)

  if (errors > 0) {
    console.error('❌ Bundle size check failed')
    process.exit(1)
  } else {
    console.log('✅ Bundle size check passed')
  }
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

checkBundleSize()
```

## ⚡ 缓存优化策略

### 长期缓存

#### 🏷️ 文件名哈希
```typescript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  // 启用内容哈希
  generateEtags: true,

  // 静态文件优化
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['@heroicons/react', 'lucide-react']
  },

  // 输出配置
  distDir: '.next',

  // 启用压缩
  compress: true,

  // 图片优化
  images: {
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
}

module.exports = nextConfig
```

#### 🗂️ 资源缓存策略
```typescript
// lib/cache-strategies.ts
export const cacheConfig = {
  // 静态资源长期缓存
  staticAssets: {
    maxAge: 365 * 24 * 60 * 60, // 1年
    immutable: true,
  },

  // HTML文件短期缓存
  pages: {
    maxAge: 24 * 60 * 60, // 1天
    mustRevalidate: true,
  },

  // API响应缓存
  api: {
    maxAge: 5 * 60, // 5分钟
    staleWhileRevalidate: 60, // 1分钟
  },
}

// proxy.ts（Next.js 16：由 middleware.ts 更名，运行于 Node.js runtime）
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  const response = NextResponse.next()

  // 静态资源缓存头
  if (request.nextUrl.pathname.match(/\.(css|js|png|jpg|jpeg|gif|webp|svg|woff|woff2)$/)) {
    response.headers.set('Cache-Control', 'public, max-age=31536000, immutable')
  }

  // 页面缓存
  if (request.nextUrl.pathname.endsWith('.html') || request.nextUrl.pathname === '/') {
    response.headers.set('Cache-Control', 'public, max-age=86400, must-revalidate')
  }

  return response
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}
```

### 依赖优化

#### 📦 Vendor分离
```typescript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.optimization = {
        ...config.optimization,
        runtimeChunk: 'single',
        splitChunks: {
          chunks: 'all',
          maxInitialRequests: 25,
          minSize: 20000,
          maxSize: 244000,
          cacheGroups: {
            // React相关
            react: {
              test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
              name: 'react',
              priority: 30,
              chunks: 'all',
            },

            // React生态
            reactLibs: {
              test: /[\\/]node_modules[\\/](@react|react-)[\\/]/,
              name: 'react-libs',
              priority: 20,
              chunks: 'all',
            },

            // UI库
            ui: {
              test: /[\\/]node_modules[\\/](@radix-ui|@headlessui|@mui|@chakra-ui|framer-motion)[\\/]/,
              name: 'ui-libs',
              priority: 15,
              chunks: 'all',
            },

            // 工具库
            utils: {
              test: /[\\/]node_modules[\\/](lodash|date-fns|axios|zustand)[\\/]/,
              name: 'utils',
              priority: 10,
              chunks: 'all',
            },

            // 其他vendor
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendors',
              priority: -10,
              chunks: 'all',
            },
          },
        },
      }
    }

    return config
  },
}

module.exports = nextConfig
```

#### 🔄 动态依赖加载
```tsx
// lib/dynamic-vendor.ts
export const loadChartJs = () => import('chart.js')
export const loadMonacoEditor = () => import('monaco-editor')
export const loadPdfLib = () => import('pdf-lib')
export const loadExcelJs = () => import('exceljs')

// components/admin/ReportGenerator.tsx
'use client'

import { useState } from 'react'

export default function ReportGenerator() {
  const [excelLib, setExcelLib] = useState<any>(null)
  const [pdfLib, setPdfLib] = useState<any>(null)

  const loadLibraries = async () => {
    try {
      // 按需加载重型库
      const [excelModule, pdfModule] = await Promise.all([
        import('exceljs'),
        import('pdf-lib')
      ])

      setExcelLib(excelModule.Workbook)
      setPdfLib(pdfModule.PDFDocument)
    } catch (error) {
      console.error('Failed to load libraries:', error)
    }
  }

  return (
    <div>
      <button onClick={loadLibraries}>
        Load Report Libraries
      </button>

      {excelLib && pdfLib && (
        <div>
          <p>Libraries loaded successfully!</p>
          {/* 使用库生成报告 */}
        </div>
      )}
    </div>
  )
}
```

## 🎨 资源优化

### 图片优化

#### 🖼️ Next.js Image优化
```tsx
// components/images/OptimizedImage.tsx
import Image from 'next/image'
import { useState } from 'react'

interface OptimizedImageProps {
  src: string
  alt: string
  width?: number
  height?: number
  priority?: boolean
  fill?: boolean
  className?: string
}

export default function OptimizedImage({
  src,
  alt,
  width,
  height,
  priority = false,
  fill = false,
  className,
}: OptimizedImageProps) {
  const [isLoading, setIsLoading] = useState(true)

  return (
    <div className={`relative ${className || ''}`}>
      <Image
        src={src}
        alt={alt}
        width={width}
        height={height}
        fill={fill}
        priority={priority}
        className={`
          duration-700 ease-in-out
          ${isLoading ? 'scale-110 blur-2xl grayscale' : 'scale-100 blur-0 grayscale-0'}
        `}
        onLoadingComplete={() => setIsLoading(false)}
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
      />
    </div>
  )
}

// 使用示例
export function ProductGallery({ images }: { images: string[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {images.map((image, index) => (
        <OptimizedImage
          key={index}
          src={image}
          alt={`Product image ${index + 1}`}
          width={400}
          height={300}
          priority={index === 0} // 第一张图片优先加载
        />
      ))}
    </div>
  )
}
```

#### 📸 响应式图片策略
```tsx
// components/images/ResponsiveImage.tsx
import Image from 'next/image'

interface ResponsiveImageProps {
  src: string
  alt: string
  aspectRatio?: number
  priority?: boolean
}

export default function ResponsiveImage({
  src,
  alt,
  aspectRatio = 16 / 9,
  priority = false,
}: ResponsiveImageProps) {
  return (
    <div className="relative w-full" style={{ aspectRatio }}>
      <Image
        src={src}
        alt={alt}
        fill
        priority={priority}
        sizes="
          (max-width: 640px) 100vw,
          (max-width: 1024px) 75vw,
          50vw
        "
        style={{
          objectFit: 'cover',
        }}
      />
    </div>
  )
}

// next.config.js - 图片优化配置
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    // 启用现代格式
    formats: ['image/webp', 'image/avif'],

    // 响应式断点
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],

    // 外部图片域名（Next.js 16：images.domains 已弃用，改用 remotePatterns）
    remotePatterns: [
      { protocol: 'https', hostname: 'example.com' },
      { protocol: 'https', hostname: 'cdn.example.com' },
    ],

    // 图片质量（Next 16 起 quality 单值改为 qualities 数组）
    qualities: [85],

    // 最小化缓存时间
    minimumCacheTTL: 60,
  },
}

module.exports = nextConfig
```

### 字体优化

#### 🔤 字体加载策略
```tsx
// app/layout.tsx
import { Inter } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap', // 字体交换策略
  preload: true, // 预加载
  weight: ['400', '500', '600', '700'], // 只加载需要的字重
})

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className={inter.className}>
        {children}
      </body>
    </html>
  )
}

// lib/font-utils.ts
export const fontDisplayStrategies = {
  swap: 'font-display: swap;', // 字体交换
  block: 'font-display: block;', // 阻塞显示
  fallback: 'font-display: fallback;', // 回退
  optional: 'font-display: optional;', // 可选
}

export const generateFontFace = (fontFamily: string, src: string, display = 'swap') => `
  @font-face {
    font-family: '${fontFamily}';
    src: ${src};
    font-display: ${display};
    font-weight: normal;
    font-style: normal;
  }
`
```

#### 📝 字体子集化
```typescript
// scripts/subset-fonts.js
const fontkit = require('fontkit')
const fs = require('fs')

async function subsetFont(inputPath, outputPath, characters) {
  const font = fontkit.open(fs.readFileSync(inputPath))
  const subset = font.createSubset()

  // 添加字符到子集
  characters.split('').forEach(char => {
    subset.addGlyph(char.charCodeAt(0))
  })

  // 生成子集字体
  const subsetBuffer = subset.encode()
  fs.writeFileSync(outputPath, subsetBuffer)

  console.log(`Font subset created: ${outputPath}`)
}

// 常用字符集
const commonCharacters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?'

// 子集化字体文件
async function optimizeFonts() {
  await subsetFont(
    './fonts/Inter-Regular.ttf',
    './fonts/Inter-Regular-Subset.ttf',
    commonCharacters
  )

  await subsetFont(
    './fonts/Inter-Bold.ttf',
    './fonts/Inter-Bold-Subset.ttf',
    commonCharacters
  )
}

optimizeFonts()
```

## 📊 性能监控

### 实时监控

#### 📈 Bundle大小监控
```tsx
// lib/bundle-monitor.ts
export interface BundleMetrics {
  name: string
  size: number
  gzippedSize: number
  loadTime: number
}

class BundleMonitor {
  private metrics: Map<string, BundleMetrics> = new Map()

  // 记录Bundle加载性能
  recordBundleLoad(name: string, loadTime: number) {
    const metric = this.metrics.get(name) || { name, size: 0, gzippedSize: 0, loadTime: 0 }
    metric.loadTime = loadTime
    this.metrics.set(name, metric)
  }

  // 获取Bundle大小信息
  async getBundleSize(url: string): Promise<number> {
    try {
      const response = await fetch(url, { method: 'HEAD' })
      return parseInt(response.headers.get('content-length') || '0')
    } catch (error) {
      console.error('Failed to get bundle size:', error)
      return 0
    }
  }

  // 生成性能报告
  generateReport(): BundleMetrics[] {
    return Array.from(this.metrics.values()).sort((a, b) => b.size - a.size)
  }

  // 检查性能预算
  checkBudget(budget: { [key: string]: number }): { passed: boolean; violations: string[] } {
    const violations: string[] = []

    this.metrics.forEach((metric, name) => {
      const limit = budget[name] || budget.default || 100 * 1024 // 默认100KB
      if (metric.size > limit) {
        violations.push(`${name}: ${this.formatBytes(metric.size)} exceeds ${this.formatBytes(limit)}`)
      }
    })

    return {
      passed: violations.length === 0,
      violations
    }
  }

  private formatBytes(bytes: number): string {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }
}

export const bundleMonitor = new BundleMonitor()

// components/BundleMonitor.tsx
'use client'

import { useEffect, useState } from 'react'
import { bundleMonitor, BundleMetrics } from '@/lib/bundle-monitor'

export default function BundleMonitorDashboard() {
  const [metrics, setMetrics] = useState<BundleMetrics[]>([])
  const [budget, setBudget] = useState({
    'main.js': 100 * 1024,
    'vendors.js': 200 * 1024,
    default: 50 * 1024,
  })

  useEffect(() => {
    // 监控Bundle加载
    const observer = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.name.includes('.js')) {
          bundleMonitor.recordBundleLoad(
            entry.name.split('/').pop()!,
            entry.duration
          )
          setMetrics(bundleMonitor.generateReport())
        }
      })
    })

    observer.observe({ entryTypes: ['resource'] })

    return () => observer.disconnect()
  }, [])

  const budgetCheck = bundleMonitor.checkBudget(budget)

  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Bundle Performance Monitor</h2>

      {!budgetCheck.passed && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 rounded">
          <h3 className="font-semibold text-red-800">Budget Violations:</h3>
          <ul className="list-disc list-inside text-red-700">
            {budgetCheck.violations.map((violation, index) => (
              <li key={index}>{violation}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Bundle
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Size
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Load Time
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {metrics.map((metric) => (
              <tr key={metric.name}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {metric.name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatBytes(metric.size)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {metric.loadTime.toFixed(2)}ms
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
```

## 🚀 高级优化技术

### 微前端架构

#### 🧩 模块联邦
```tsx
// webpack.config.js (主应用)
const ModuleFederationPlugin = require('@module-federation/webpack')

module.exports = {
  webpack: (config) => {
    config.plugins.push(
      new ModuleFederationPlugin({
        name: 'shell',
        filename: 'remoteEntry.js',
        remotes: {
          dashboard: 'dashboard@http://localhost:3001/remoteEntry.js',
          admin: 'admin@http://localhost:3002/remoteEntry.js',
        },
        shared: {
          react: { singleton: true, requiredVersion: '^19.0.0' },
          'react-dom': { singleton: true, requiredVersion: '^19.0.0' },
          'next': { singleton: true, requiredVersion: '^15.0.0' },
        },
      })
    )
    return config
  },
}

// components/Dashboard.tsx
import dynamic from 'next/dynamic'

// 动态加载远程模块
const RemoteDashboard = dynamic(() => import('dashboard/Dashboard'), {
  loading: () => <div>Loading Dashboard...</div>,
  ssr: false,
})

export default function ShellApp() {
  return (
    <div>
      <header>Shell Application</header>
      <main>
        <RemoteDashboard />
      </main>
    </div>
  )
}
```

### 服务端组件优化

#### 🔄 智能缓存策略
```tsx
// app/components/ServerComponent.tsx
import { cache } from 'react'

// 缓存数据获取函数
const getPosts = cache(async (category?: string) => {
  const url = category
    ? `https://api.example.com/posts?category=${category}`
    : 'https://api.example.com/posts'

  const response = await fetch(url, {
    next: {
      revalidate: 3600, // 1小时缓存
      tags: ['posts', category || 'all']
    }
  })

  return response.json()
})

// 服务端组件
export default async function ServerComponent({ category }: { category?: string }) {
  const posts = await getPosts(category)

  return (
    <div>
      <h1>{category || 'All'} Posts</h1>
      <ul>
        {posts.map((post: any) => (
          <li key={post.id}>{post.title}</li>
        ))}
      </ul>
    </div>
  )
}

// 流式加载
import { Suspense } from 'react'

export default function Page() {
  return (
    <div>
      <h1>Blog</h1>
      <Suspense fallback={<div>Loading posts...</div>}>
        <ServerComponent />
      </Suspense>
      <Suspense fallback={<div>Loading sidebar...</div>}>
        <Sidebar />
      </Suspense>
    </div>
  )
}
```

## 📋 最佳实践清单

先确认当前构建器，再使用它支持的配置；Turbopack 与 Webpack 的选项不能直接混用。动态导入可以减少首屏工作，却可能让用户点击后等待，应检查实际网络瀑布与交互时间。

服务端组件可减少部分客户端代码，客户端仍需承担交互和相关依赖。移除未用依赖、控制重复包和按需加载后复测关键页面。微前端、边缘部署与 CDN 各有组织或交付目标，不应被列为每个应用都要勾选的打包优化步骤。

## 🔧 工具推荐

### 📊 分析工具
- **Webpack Bundle Analyzer**: 可视化Bundle分析
- **Lighthouse**: 综合性能评估
- **Bundlephobia**: 依赖包大小分析
- **Next.js Bundle Analyzer**: Next.js专用分析工具

### 🛠️ 优化工具
- **PurgeCSS**: 移除未使用的CSS
- **Imagemin**: 图片压缩优化
- **Terser**: JavaScript压缩
- **CSS Nano**: CSS优化

### 📈 监控工具
- **Sentry**: 错误和性能监控
- **Vercel Analytics**: Next.js性能分析
- **SpeedCurve**: 性能趋势监控
- **Calibre**: 持续性能监控

## 🎯 总结

Next.js 16 的打包优化生态系统为现代Web应用提供了完整的优化解决方案。通过合理运用代码分割、Tree Shaking、缓存策略和监控工具，可以构建出高性能、用户友好的现代化应用。

## 🔄 文档交叉引用

### 相关文档
- 📄 **[渲染优化](./01-rendering-optimization.md)**: 运行时性能优化和渲染策略
- 📄 **[测试工具](../development-tools/01-testing-tools.md)**: 打包测试和性能回归检测
- 📄 **[样式工具](../development-tools/02-styling-tools.md)**: CSS优化和样式打包策略
- 📄 **[包管理器](../development-tools/03-package-managers.md)**: 依赖优化和包管理
- 📄 **[调试工具](../development-tools/04-debugging-tools.md)**: 构建调试和性能分析

### 参考章节
- 📖 **[Turbopack配置](#️-nextjs-16-打包架构概览)**: 革命性打包工具配置
- 📖 **[代码分割策略](#-代码分割策略)**: 智能分割和懒加载
- 📖 **[Tree Shaking优化](#-tree-shaking-优化)**: 死代码消除和依赖优化
- 📖 **[Bundle分析](#bundle分析和监控)**: 打包分析和性能监控
- 📖 **[高级优化技术](#-高级优化技术)**: 微前端和模块联邦

---

## 📝 总结

### 核心要点回顾
1. **打包工具选择**: Turbopack(极速) → Webpack(成熟) → Esbuild(零配置)的合理选择
2. **代码分割策略**: 路由级、组件级、模块级的智能分割方案
3. **Tree Shaking优化**: ES模块、按需导入、死代码消除的最佳实践
4. **缓存优化**: 长期缓存、内容哈希、增量构建的性能优化
5. **Bundle分析**: 大小监控、性能预算、持续分析的完整体系

### 学习成果检查
- [ ] 能够选择和配置适合项目的打包工具(Turbopack/Webpack)
- [ ] 掌握代码分割和懒加载的最佳实践策略
- [ ] 熟练实施Tree Shaking优化减少打包体积
- [ ] 能够建立完善的Bundle分析和监控体系
- [ ] 理解微前端架构和模块联邦的高级优化技术

---

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

---

## 🔗 外部资源

### 官方文档
- **Next.js**: [Build Optimization](https://nextjs.org/docs/advanced-features/optimizing) - Next.js构建优化
- **Webpack**: [Optimization](https://webpack.js.org/guides/code-splitting/) - Webpack优化指南
- **Turbopack**: [Official Documentation](https://turbo.build/) - Rust编写的增量打包器
- **Bundle Analyzer**: [webpack-bundle-analyzer](https://github.com/webpack-contrib/webpack-bundle-analyzer) - 打包分析工具

### 快速参考
- **Bundlephobia**: [依赖包大小分析](https://bundlephobia.com/) - NPM包体积分析
- **Module Federation**: [微前端架构](https://module-federation.io/) - 模块联邦文档
- **Performance Budgets**: [性能预算工具](https://github.com/paulirish/performance-budget-bookmarklet) - 性能预算设置
- **Chrome DevTools**: [Coverage Analysis](https://developer.chrome.com/docs/devtools/coverage/) - 代码覆盖率分析

---

**文档状态**: ✅ 已完成 | 🚧 进行中 | 📋 计划中
**最后更新**: 2026年9月
**版本**: v1.0.0

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
