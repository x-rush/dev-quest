# Next.js 高级开发：路由、渲染、缓存与交付

## 先看框架承担哪部分职责

**Next.js 完整框架**：把路由、渲染、取数、缓存和部署拆成五个决定。先确定代码执行位置，再决定数据新鲜度，最后用测量选择优化。

**最小练习与预期结果**：选一个商品详情页，标出服务器读取、客户端交互与失效入口；刷新和直接访问都应得到符合权限与新鲜度约定的内容。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 以 App Router、服务端/客户端组件、缓存、构建和部署为主线，练习如何为页面选择执行位置和数据新鲜度。高级配置要在项目实际依赖版本和官方迁移说明中复核，不能把本文片段视为通用生产配置。

> **目标读者**: 已能完成基础 Next.js 项目，希望理解复杂页面数据流、缓存和交付取舍的开发者。

> **前置知识**: Next.js、React、TypeScript、Web 性能与部署基础；版本以当前项目的锁定依赖为准。

> **预计时长**: 12-16小时

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `frameworks` |
| **难度** | ⭐⭐⭐ (精通)|
| **标签** | `#nextjs16` `#app-router` `#server-components` `#performance` `#enterprise` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 🎯 学习目标

### 🏗️ 架构取舍
- 对一个页面说明哪些代码在服务端执行、哪些需要浏览器交互，以及这样划分的证据
- 用嵌套路由、布局、错误和加载边界表达真实的页面状态
- 在服务端组件与客户端组件之间选择数据、状态和事件的归属，避免把秘密或大量依赖带到客户端
- 将性能与部署目标量化为可测指标和可回退的发布步骤

### 🚀 高级开发能力
- 根据流量、数据一致性和团队边界评估扩展方案，而不把“可扩展”当成框架默认属性
- 用高级路由和布局解决具体导航、并行视图或拦截交互，并给出直接访问时的预期结果
- 为每类数据定义缓存键、失效触发点、陈旧窗口和写后读取行为
- 用锁定版本、构建日志、性能测量和发布回退组成可复现的开发工作流

## 📖 概述

Next.js 提供路由、渲染和构建工具，但缓存一致性、数据库事务、授权、外部服务故障和运行成本仍由应用设计承担。本章以这些工具的职责边界为中心：先把一个页面的输入、读取、缓存和错误结果做对，再比较并行路由、流式渲染或构建优化是否解决了可测的瓶颈。

## 🆕 Next.js 16 核心变化速览

从 Next.js 15 升级到 16 时，以下项目会影响日常开发。发布版本、稳定性状态和迁移命令变化较快；执行升级前，以 [Next.js 官方升级指南](https://nextjs.org/docs/app/getting-started/upgrading/version-16) 与项目锁定版本为准，并在独立分支完成构建和关键路径验收。

### 1. Turbopack 成为默认打包器

项目升级后先确认开发与生产构建实际使用的打包器，再决定是否迁移配置。不要把宣传中的构建速度比例当作本项目结果：在同一硬件、锁文件和缓存条件下记录 `next dev` 启动、一次热更新和 `next build` 的耗时与产物大小。是否仍可使用 Webpack 回退、命令名称和 `turbopack` 配置位置，均以锁定版本的官方升级指南为准。

### 2. Async Request APIs 完全异步

`params`、`searchParams`、`cookies()`、`headers()`、`draftMode()` 均为 Promise/异步 API。Next.js 15 的同步兼容层在 16 中已完全移除，同步访问会直接报错：

```tsx
export default async function Page({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ q?: string }>;
}) {
  const { slug } = await params;
  const { q } = await searchParams;
  // ...
}
```

### 3. 缓存语义：默认更少缓存

- 缓存默认值和配置项可能随版本升级改变。对每个读取路径写明它是请求时读取、预渲染还是显式缓存，并用两次读取与一次写入后的读取验证实际行为。
- 需要标签失效或写后读取时，使用当前版本文档规定的缓存 API 和参数；为失效失败、并发写入和权限不同的读取补测试。
- 不要只因为名称从 PPR 或其他实验标志迁移就假定响应更快；先测量真实页面的首字节、可交互时间和陈旧数据窗口。

### 4. Instant Navigations 与路由增强

客户端导航和预取策略会影响请求数、内存与陈旧数据。用浏览器网络面板和真实路由跳转记录“是否预取、何时失效、直接访问是否等价”，不要把“接近即时”当作未测量页面的结论。

### 5. middleware.ts 弃用，更名为 proxy.ts

`proxy.ts` 明确网络边界，运行于 Node.js runtime；导出函数更名为 `proxy`。Edge runtime 场景可暂留 `middleware.ts`（已弃用，未来移除）。

### 6. 其他 breaking/移除项

- AMP 支持移除（`useAmp`、`config.amp` 等 API 全部删除）
- `next lint` 命令移除，`next build` 不再运行 lint，直接使用 ESLint/Biome CLI
- `serverRuntimeConfig`/`publicRuntimeConfig` 移除，改用环境变量
- `next/image` 默认值变化：`minimumCacheTTL` 提升至 4 小时、`qualities` 收敛为 `[75]`、`imageSizes` 移除 16、本地带查询串的 src 需配置 `images.localPatterns`
- 最低运行时要求 Node.js 20.9+

## 🏛️ Next.js 16 架构深度解析

### 核心架构原理

```typescript
// src/types/nextjs-architecture.ts
export interface NextJSArchitecture {
  // 渲染架构
  rendering: {
    serverComponents: '服务器组件 - 零JavaScript客户端渲染'
    clientComponents: '客户端组件 - 交互性和状态管理'
    hybridRendering: '混合渲染 - 结合服务端和客户端优势'
    streaming: '流式渲染 - 渐进式页面加载'
  }

  // 路由架构
  routing: {
    appRouter: 'App Router - 基于文件系统的现代路由'
    nestedLayouts: '嵌套布局 - 复杂页面结构支持'
    parallelRoutes: '并行路由 - 多个独立布局区域'
    interceptingRoutes: '拦截路由 - 模态框和覆盖层'
  }

  // 缓存架构
  caching: {
    dataCache: '数据缓存 - 自动数据获取缓存'
    fullRouteCache: '全路由缓存 - 静态页面缓存'
    incrementalCache: '增量缓存 - ISR和重新验证'
    clientCache: '客户端缓存 - 浏览器缓存策略'
  }

  // 构建架构
  build: {
    turbopack: 'Turbopack - 下一代构建工具'
    codeSplitting: '代码分割 - 自动和手动分割'
    bundleAnalysis: '包分析 - 构建优化分析'
    assetOptimization: '资源优化 - 图片、字体、CSS优化'
  }
}
```

### App Router 深度原理

```tsx
// src/lib/app-router-core.ts
import { cache } from 'react'

// 路由段配置接口
export interface RouteSegmentConfig {
  // 动态配置
  dynamic?: 'auto' | 'force-dynamic' | 'error' | 'force-static'
  revalidate?: number | false
  runtime?: 'nodejs' | 'edge'

  // 缓存配置
  fetchCache?: 'auto' | 'force-no-store' | 'only-no-store' | 'default-no-store'
  preferredRegion?: string

  // 元数据配置
  maxDuration?: number
}

// 路由构建器
export class RouteBuilder {
  private static routeCache = new Map<string, any>()

  // 创建动态路由配置
  static createRouteConfig(config: RouteSegmentConfig) {
    return {
      // 动态渲染模式
      dynamic: config.dynamic || 'auto',

      // 重新验证策略
      revalidate: config.revalidate || false,

      // 运行时环境
      runtime: config.runtime || 'nodejs',

      // 缓存策略
      fetchCache: config.fetchCache || 'auto',

      // 区域优化
      preferredRegion: config.preferredRegion || 'auto',

      // 最大执行时间
      maxDuration: config.maxDuration || 30
    }
  }

  // 缓存路由结果
  static cacheRoute<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
    if (this.routeCache.has(key)) {
      return this.routeCache.get(key)
    }

    const result = fetcher()
    this.routeCache.set(key, result)
    return result
  }

  // 清除路由缓存
  static clearRouteCache(key?: string) {
    if (key) {
      this.routeCache.delete(key)
    } else {
      this.routeCache.clear()
    }
  }
}

// 使用示例
export const dynamicRouteConfig = RouteBuilder.createRouteConfig({
  dynamic: 'force-dynamic',
  revalidate: 60, // 60秒重新验证
  runtime: 'nodejs',
  fetchCache: 'auto',
  maxDuration: 30
})
```

### Server Components 高级模式

```tsx
// src/components/advanced-server-components.tsx
import { cache } from 'react'
import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'

// 缓存数据获取函数
const getCachedData = cache(async (id: string) => {
  const response = await fetch(`https://api.example.com/data/${id}`, {
    next: { revalidate: 3600, tags: [`data-${id}`] }
  })
  return response.json()
})

// 高级服务器组件
interface AdvancedServerComponentProps {
  id: string
  fallback?: React.ReactNode
  errorFallback?: React.ComponentType<{ error: Error; reset: () => void }>
}

export async function AdvancedServerComponent({
  id,
  fallback = <div>Loading...</div>,
  errorFallback
}: AdvancedServerComponentProps) {
  // 并行数据获取
  const [data, relatedData, metadata] = await Promise.all([
    getCachedData(id),
    getRelatedData(id),
    getMetadata(id)
  ])

  // 条件渲染
  if (!data) {
    return <div>Data not found</div>
  }

  return (
    <ErrorBoundary FallbackComponent={errorFallback || DefaultErrorFallback}>
      <Suspense fallback={fallback}>
        <ComponentContent data={data} relatedData={relatedData} metadata={metadata} />
      </Suspense>
    </ErrorBoundary>
  )
}

// 组件内容
function ComponentContent({ data, relatedData, metadata }: any) {
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-4xl font-bold">{data.title}</h1>
        <p className="text-gray-600">{metadata.description}</p>
      </header>

      <main>
        <div dangerouslySetInnerHTML={{ __html: data.content }} />
      </main>

      <aside>
        <RelatedContent data={relatedData} />
      </aside>
    </div>
  )
}

// 默认错误回退
function DefaultErrorFallback({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
      <h3 className="text-red-800 font-medium">组件加载失败</h3>
      <p className="text-red-600 text-sm mt-1">{error.message}</p>
      <button
        onClick={reset}
        className="mt-2 px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
      >
        重试
      </button>
    </div>
  )
}

// 获取相关数据
async function getRelatedData(id: string) {
  const response = await fetch(`https://api.example.com/related/${id}`)
  return response.json()
}

// 获取元数据
async function getMetadata(id: string) {
  const response = await fetch(`https://api.example.com/metadata/${id}`)
  return response.json()
}

// 相关内容组件
function RelatedContent({ data }: { data: any[] }) {
  return (
    <div className="space-y-4">
      <h3 className="text-xl font-semibold">相关内容</h3>
      {data.map((item) => (
        <div key={item.id} className="p-4 border rounded-lg">
          <h4 className="font-medium">{item.title}</h4>
          <p className="text-sm text-gray-600 mt-1">{item.excerpt}</p>
        </div>
      ))}
    </div>
  )
}
```

## 🚀 高级路由模式

### 并行路由和槽位系统

```tsx
// src/app/dashboard/@analytics/page.tsx
export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">数据分析仪表板</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="总用户数"
          value="1,234"
          change="+12%"
          trend="up"
        />
        <MetricCard
          title="活跃用户"
          value="856"
          change="+5%"
          trend="up"
        />
        <MetricCard
          title="新增用户"
          value="124"
          change="-2%"
          trend="down"
        />
        <MetricCard
          title="留存率"
          value="78%"
          change="+3%"
          trend="up"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartContainer title="用户增长趋势" />
        <ChartContainer title="活跃度分析" />
      </div>
    </div>
  )
}

// src/app/dashboard/@settings/page.tsx
export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">系统设置</h2>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">基本设置</h3>
        <SettingsForm />
      </div>
    </div>
  )
}

// src/app/dashboard/layout.tsx
import { Slot } from '@radix-ui/react-slot'

export default function DashboardLayout({
  children,
  analytics,
  settings
}: {
  children: React.ReactNode
  analytics?: React.ReactNode
  settings?: React.ReactNode
}) {
  return (
    <div className="flex h-screen bg-gray-100">
      {/* 侧边栏 */}
      <aside className="w-64 bg-white shadow-md">
        <DashboardSidebar />
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 overflow-auto">
        <div className="p-6">
          {children}
        </div>

        {/* 并行槽位 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
          <div className="lg:col-span-2 space-y-6">
            {analytics}
          </div>
          <div className="space-y-6">
            {settings}
          </div>
        </div>
      </main>
    </div>
  )
}
```

### 拦截路由和模态框系统

```tsx
// src/app/photos/[id]/page.tsx
import { notFound } from 'next/navigation'
import { getPhotoById } from '@/lib/photos'

interface PhotoPageProps {
  // Next.js 16：params 为 Promise
  params: Promise<{ id: string }>
}

export default async function PhotoPage({ params }: PhotoPageProps) {
  const { id } = await params
  const photo = await getPhotoById(id)

  if (!photo) {
    notFound()
  }

  return (
    <div className="container mx-auto py-8">
      <div className="max-w-4xl mx-auto">
        <img
          src={photo.url}
          alt={photo.title}
          className="w-full h-auto rounded-lg shadow-lg"
        />
        <h1 className="text-3xl font-bold mt-6">{photo.title}</h1>
        <p className="text-gray-600 mt-2">{photo.description}</p>
      </div>
    </div>
  )
}

// src/app/@modal/(.)photos/[id]/page.tsx
export default async function PhotoModal({ params }: PhotoPageProps) {
  const { id } = await params
  const photo = await getPhotoById(id)

  if (!photo) {
    return null
  }

  return <PhotoModalWrapper photo={photo} />
}

// src/components/PhotoModalWrapper.tsx
'use client'

import { useRouter, usePathname } from 'next/navigation'
import { createPortal } from 'react-dom'
import { useEffect } from 'react'

interface PhotoModalWrapperProps {
  photo: {
    id: string
    title: string
    url: string
    description: string
  }
}

export function PhotoModalWrapper({ photo }: PhotoModalWrapperProps) {
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        router.back()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [router])

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      router.back()
    }
  }

  // 创建Portal到body
  if (typeof document === 'undefined') {
    return null
  }

  return createPortal(
    <div
      className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-auto">
        <div className="relative">
          <img
            src={photo.url}
            alt={photo.title}
            className="w-full h-auto"
          />
          <button
            onClick={() => router.back()}
            className="absolute top-4 right-4 bg-white rounded-full p-2 shadow-lg hover:bg-gray-100"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="p-6">
          <h2 className="text-2xl font-bold">{photo.title}</h2>
          <p className="text-gray-600 mt-2">{photo.description}</p>
        </div>
      </div>
    </div>,
    document.body
  )
}
```

## ⚡ 性能优化深度实践

### 高级缓存策略

```tsx
// src/lib/advanced-caching.ts
// Next.js 16：unstable_cache 已弃用，改用 "use cache" 指令 + cacheTag/cacheLife 显式缓存
import { revalidateTag, cacheTag, cacheLife } from 'next/cache'

// 多层缓存策略
export class AdvancedCacheManager {
  // L1缓存：内存缓存（请求级别）
  private static memoryCache = new Map<string, { data: any; timestamp: number; ttl: number }>()

  // L2缓存：Next.js缓存（应用级别，"use cache" 显式声明）
  private static async fetchCached(key: string) {
    'use cache'
    cacheLife('hours') // 约1小时级别的缓存 profile
    cacheTag('dynamic')
    return await this.fetchFromSource(key)
  }

  // L3缓存：CDN缓存（边缘级别）
  private static cdnCache = new Map<string, { data: any; etag: string }>()

  // 智能缓存获取
  static async get<T>(key: string, options: {
    ttl?: number
    useMemory?: boolean
    useNext?: boolean
    useCDN?: boolean
  } = {}): Promise<T | null> {
    const {
      ttl = 300000, // 5分钟默认TTL
      useMemory = true,
      useNext = true,
      useCDN = false
    } = options

    // L1：内存缓存
    if (useMemory) {
      const memoryItem = this.memoryCache.get(key)
      if (memoryItem && Date.now() - memoryItem.timestamp < memoryItem.ttl) {
        return memoryItem.data
      }
    }

    // L2：Next.js缓存
    if (useNext) {
      try {
        const data = await this.fetchCached(key)
        if (data) {
          // 回填内存缓存
          if (useMemory) {
            this.memoryCache.set(key, {
              data,
              timestamp: Date.now(),
              ttl
            })
          }
          return data
        }
      } catch (error) {
        console.error('Next.js cache error:', error)
      }
    }

    // L3：CDN缓存
    if (useCDN) {
      const cdnItem = this.cdnCache.get(key)
      if (cdnItem) {
        return cdnItem.data
      }
    }

    return null
  }

  // 智能缓存设置
  static async set<T>(key: string, data: T, options: {
    ttl?: number
    tags?: string[]
    useMemory?: boolean
    useNext?: boolean
    useCDN?: boolean
  } = {}): Promise<void> {
    const {
      ttl = 300000,
      tags = [],
      useMemory = true,
      useNext = true,
      useCDN = false
    } = options

    // L1：内存缓存
    if (useMemory) {
      this.memoryCache.set(key, {
        data,
        timestamp: Date.now(),
        ttl
      })
    }

    // L2：Next.js缓存（通过 "use cache" 显式声明）
    if (useNext) {
      // fetchCached 内部使用 "use cache"，写入并预热 Next.js 缓存
      await this.fetchCached(key)
    }

    // L3：CDN缓存
    if (useCDN) {
      this.cdnCache.set(key, {
        data,
        etag: this.generateETag(data)
      })
    }
  }

  // 缓存失效
  static invalidate(tags: string[]): void {
    // 失效Next.js缓存（Next.js 16：revalidateTag 需传入 cacheLife profile 作为第二参数）
    tags.forEach(tag => revalidateTag(tag, 'max'))

    // 清理内存缓存
    this.memoryCache.clear()

    // 清理CDN缓存
    this.cdnCache.clear()
  }

  // 预热缓存
  static async warmup(keys: string[]): Promise<void> {
    const promises = keys.map(async (key) => {
      try {
        await this.get(key)
      } catch (error) {
        console.error(`Cache warmup failed for key ${key}:`, error)
      }
    })

    await Promise.allSettled(promises)
  }

  // 从数据源获取
  private static async fetchFromSource(key: string): Promise<any> {
    // 这里实现实际的数据获取逻辑
    const response = await fetch(`https://api.example.com/data/${key}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch data for key: ${key}`)
    }
    return response.json()
  }

  // 生成ETag
  private static generateETag(data: any): string {
    const hash = btoa(JSON.stringify(data))
    return `"${hash}"`
  }

  // 缓存统计
  static getStats() {
    return {
      memoryCache: {
        size: this.memoryCache.size,
        items: Array.from(this.memoryCache.entries()).map(([key, item]) => ({
          key,
          age: Date.now() - item.timestamp,
          ttl: item.ttl
        }))
      },
      nextCache: {
        // Next.js缓存统计需要通过其他方式获取
      },
      cdnCache: {
        size: this.cdnCache.size
      }
    }
  }
}

// 使用示例
export class DataService {
  // 获取用户数据（多层缓存）
  static async getUser(id: string): Promise<User | null> {
    return AdvancedCacheManager.get(`user:${id}`, {
      ttl: 600000, // 10分钟
      useMemory: true,
      useNext: true,
      useCDN: false
    })
  }

  // 获取文章数据（多层缓存）
  static async getArticle(slug: string): Promise<Article | null> {
    return AdvancedCacheManager.get(`article:${slug}`, {
      ttl: 1800000, // 30分钟
      tags: ['article'],
      useMemory: true,
      useNext: true,
      useCDN: true
    })
  }

  // 更新数据并缓存
  static async updateUser(user: User): Promise<void> {
    // 更新数据库
    await fetch(`/api/users/${user.id}`, {
      method: 'PUT',
      body: JSON.stringify(user)
    })

    // 更新缓存
    await AdvancedCacheManager.set(`user:${user.id}`, user, {
      ttl: 600000,
      tags: ['user'],
      useMemory: true,
      useNext: true
    })

    // 失效相关缓存
    AdvancedCacheManager.invalidate(['user-list', 'user-profile'])
  }
}
```

### 流式渲染和Suspense

```tsx
// src/components/streaming-components.tsx
import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'

// 流式页面组件
export function StreamingPage() {
  return (
    <div className="container mx-auto py-8">
      {/* 立即渲染的头部 */}
      <PageHeader />

      {/* 流式渲染的主要内容 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          {/* 主要内容 - 高优先级 */}
          <Suspense fallback={<MainContentSkeleton />}>
            <MainContent />
          </Suspense>

          {/* 相关内容 - 中优先级 */}
          <Suspense fallback={<RelatedContentSkeleton />}>
            <RelatedContent />
          </Suspense>
        </div>

        <div className="space-y-8">
          {/* 侧边栏 - 低优先级 */}
          <Suspense fallback={<SidebarSkeleton />}>
            <Sidebar />
          </Suspense>
        </div>
      </div>
    </div>
  )
}

// 页面头部（同步渲染）
function PageHeader() {
  return (
    <header className="mb-8">
      <h1 className="text-4xl font-bold text-gray-900">
        流式渲染示例
      </h1>
      <p className="text-xl text-gray-600 mt-2">
        展示Next.js 16的流式渲染能力
      </p>
    </header>
  )
}

// 主要内容（异步渲染）
async function MainContent() {
  // 模拟慢速数据获取
  const data = await fetchSlowData()

  return (
    <section className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-semibold mb-4">主要内容</h2>
      <div className="prose max-w-none">
        {data.map((item: any, index: number) => (
          <div key={index} className="mb-4">
            <h3 className="text-lg font-medium">{item.title}</h3>
            <p>{item.content}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

// 相关内容（异步渲染）
async function RelatedContent() {
  const relatedData = await fetchRelatedData()

  return (
    <section className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-semibold mb-4">相关内容</h2>
      <div className="space-y-4">
        {relatedData.map((item: any, index: number) => (
          <div key={index} className="flex items-center space-x-4 p-3 border rounded">
            <div className="w-12 h-12 bg-gray-200 rounded"></div>
            <div>
              <h4 className="font-medium">{item.title}</h4>
              <p className="text-sm text-gray-600">{item.excerpt}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

// 侧边栏（异步渲染）
async function Sidebar() {
  const sidebarData = await fetchSidebarData()

  return (
    <aside className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">侧边栏</h3>
        <div className="space-y-3">
          {sidebarData.map((item: any, index: number) => (
            <div key={index} className="p-3 bg-gray-50 rounded">
              <h4 className="font-medium text-sm">{item.title}</h4>
              <p className="text-xs text-gray-600 mt-1">{item.count} 项</p>
            </div>
          ))}
        </div>
      </div>
    </aside>
  )
}

// 骨架屏组件
function MainContentSkeleton() {
  return (
    <section className="bg-white rounded-lg shadow p-6">
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-gray-200 rounded w-1/4"></div>
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          <div className="h-4 bg-gray-200 rounded w-4/6"></div>
        </div>
        <div className="h-4 bg-gray-200 rounded w-1/4"></div>
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    </section>
  )
}

function RelatedContentSkeleton() {
  return (
    <section className="bg-white rounded-lg shadow p-6">
      <div className="animate-pulse space-y-4">
        <div className="h-6 bg-gray-200 rounded w-1/4"></div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gray-200 rounded"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function SidebarSkeleton() {
  return (
    <aside className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/4"></div>
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="p-3 bg-gray-100 rounded">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/4"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </aside>
  )
}

// 数据获取函数
async function fetchSlowData() {
  // 模拟慢速网络请求
  await new Promise(resolve => setTimeout(resolve, 2000))

  return [
    { title: '第一部分内容', content: '这是第一部分的详细内容...' },
    { title: '第二部分内容', content: '这是第二部分的详细内容...' },
    { title: '第三部分内容', content: '这是第三部分的详细内容...' }
  ]
}

async function fetchRelatedData() {
  await new Promise(resolve => setTimeout(resolve, 1500))

  return [
    { title: '相关文章1', excerpt: '相关文章的简短描述...' },
    { title: '相关文章2', excerpt: '相关文章的简短描述...' },
    { title: '相关文章3', excerpt: '相关文章的简短描述...' }
  ]
}

async function fetchSidebarData() {
  await new Promise(resolve => setTimeout(resolve, 1000))

  return [
    { title: '分类1', count: 10 },
    { title: '分类2', count: 8 },
    { title: '分类3', count: 15 },
    { title: '分类4', count: 6 }
  ]
}
```

## 🛠️ 企业级构建优化

### Turbopack 配置优化

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Turbopack配置（Next 16：顶层 turbopack 键；experimental.turbo 仅为兼容别名）
  turbopack: {
    rules: {
      // SVG文件处理
      '*.svg': {
        loaders: ['@svgr/webpack'],
        as: '*.js',
      },
    },
  },

  // 服务器组件优化（Next 15+ 移至顶层 serverExternalPackages）
  serverExternalPackages: [
    'sharp',
    'canvas',
    'jsdom'
  ],

  experimental: {
    // 优化选项
    optimizeCss: true,
    optimizeServerReact: true,
    optimizePackageImports: [
      'lucide-react',
      '@radix-ui/react-icons',
      'date-fns',
      'clsx',
      'tailwind-merge'
    ],
  },

  // Webpack配置（fallback）
  webpack: (config, { dev, isServer }) => {
    if (!dev && !isServer) {
      // 生产环境优化
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            // React相关
            react: {
              test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
              name: 'react-vendor',
              chunks: 'all',
              priority: 20,
            },

            // Next.js相关
            next: {
              test: /[\\/]node_modules[\\/]next[\\/]/,
              name: 'next-vendor',
              chunks: 'all',
              priority: 15,
            },

            // UI库
            ui: {
              test: /[\\/]node_modules[\\/](@radix-ui|lucide-react)[\\/]/,
              name: 'ui-vendor',
              chunks: 'all',
              priority: 10,
            },

            // 工具库
            utils: {
              test: /[\\/]node_modules[\\/](date-fns|clsx|tailwind-merge)[\\/]/,
              name: 'utils-vendor',
              chunks: 'all',
              priority: 5,
            },

            // 公共代码
            common: {
              name: 'common',
              minChunks: 2,
              chunks: 'all',
              enforce: true,
              priority: 1,
            },
          },
        },
      }
    }

    return config
  },

  // 图片优化
  images: {
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048],
    imageSizes: [32, 48, 64, 96, 128, 256, 384], // Next 16：16 已从默认 imageSizes 移除
    minimumCacheTTL: 60,
    dangerouslyAllowSVG: true,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },

  // 压缩配置
  compress: true,

  // 电源配置
  poweredByHeader: false,

  // 实验性功能
  logging: {
    fetches: {
      fullUrl: false,
    },
  },
}

module.exports = nextConfig
```

## ✅ 总结

本章提供的是高级能力的决策框架，不是“已经具备企业级能力”的证明。完成以下验收后，才可以说明你已在一个具体项目中掌握了对应边界：

### 🏗️ 架构验收
- 为一个页面标注 App Router 的加载、错误、未找到和直接访问行为，并用浏览器复现
- 解释每个组件为何在服务端或客户端运行，确认秘密和不必要依赖没有进入浏览器产物
- 仅在真实导航问题需要时引入并行/拦截路由，并测试刷新、深链接和后退行为
- 在慢数据与失败数据下验证 Suspense/流式边界的可见状态和可恢复结果

### ⚡ 性能验收
- 为每个缓存读取记录键、TTL、失效者和写后读取结果；不同身份或租户不能共享错误的数据
- 在固定设备、网络和数据量下保存优化前后指标与 bundle 报告，确认改动解决了目标瓶颈
- 构建命令、依赖锁定和部署环境可以从空环境复现，并能定位失败日志

### 🚀 交付验收
- 对一条受保护写操作验证服务端授权、运行时输入校验、事务失败和幂等重试
- 为外部依赖超时、缓存不可用和发布回退给出用户可见结果及运行记录
- 通过日志、指标与追踪从请求 ID 找到一次失败的入口、依赖和恢复动作

## 📚 下一步学习

- 深入学习边缘计算和Serverless架构
- 掌握微前端和模块联邦
- 学习GraphQL和Apollo集成
- 探索AI/ML集成和智能应用
- 了解WebAssembly和性能极限优化

## 🔗 相关资源链接

### 官方资源
- [Next.js 16 官方文档](https://nextjs.org/docs)
- [React 19 官方文档](https://react.dev/)
- [Next.js GitHub 仓库](https://github.com/vercel/next.js)
- [Vercel 部署平台](https://vercel.com/)

### 技术文章
- [Next.js 16 更新日志](https://nextjs.org/blog/next-16)
- [App Router 最佳实践](https://nextjs.org/docs/app/building-your-application/routing)
- [Server Components 深度解析](https://nextjs.org/docs/app/building-your-application/rendering/server-components)

### 工具和资源
- [Next.js Learn 课程](https://nextjs.org/learn)
- [Next.js 官方案例模板](https://github.com/vercel/next.js/tree/canary/examples)

## 📚 模块内相关文档

### 同模块相关文档
- [React 19 深度集成](./02-react-19-integration.md) - 学习React 19新特性与Next.js 16的集成实践
- [全栈开发模式](./03-full-stack-patterns.md) - 掌握现代全栈应用开发架构模式
- [性能优化策略](./04-performance-optimization.md) - 深入Next.js应用性能调优技术

### 相关知识模块
- [测试相关模块](../testing/01-unit-testing.md) - Next.js应用的单元测试实践
- [部署相关模块](../deployment/01-vercel-deployment.md) - Next.js应用的Vercel企业级部署

### 基础前置知识
- [React 基础概念](../reference/language-concepts/01-react-syntax-cheatsheet.md) - React核心概念回顾
- [JavaScript 现代特性](../reference/language-concepts/04-javascript-modern.md) - 现代JavaScript语法特性
- [TypeScript 入门](../reference/language-concepts/03-typescript-types.md) - TypeScript类型系统基础

---

## ✨ 总结

### 核心技术要点
1. **App Router 架构优势**: 基于React Server Components的新一代路由系统，提供更好的性能和开发体验
2. **Server Components**: 服务端渲染组件，减少客户端JavaScript负担，提升首屏加载速度
3. **Server Actions**: 简化数据Mutations操作，提供更好的类型安全和开发体验
4. **现代化构建系统**: Turbopack和SWC提供极速的构建和热重载体验
5. **性能优化特性**: 图片优化、字体优化、自动代码分割等内置优化功能

### 学习成果自检
- [ ] 理解Next.js 16的App Router架构和Pages Router的区别
- [ ] 掌握Server Components和Client Components的使用场景
- [ ] 能够使用Server Actions处理表单提交和数据变更
- [ ] 熟练运用Next.js 16的性能优化特性
- [ ] 能够独立创建和部署一个完整的Next.js 16应用

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
**🏷️ 标签**: `#nextjs16` `#react19` `#app-router` `#server-components` `#modern-web`
**⭐ 推荐指数**: ⭐⭐⭐

**💡 提示**: 本模块为Next.js 16核心模块，建议先掌握React基础后再进行学习。结合实践项目能更好地理解概念。

**🎯 学习建议**:
- 建议学习周期: 2-3周
- 理论与实践时间比例: 3:7
- 重点掌握App Router和Server Components
- 结合官方文档和社区资源深入学习

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
