# Next.js 与 React：并发渲染、边界与可恢复交互

## 先看框架承担哪部分职责

**React 集成**：状态更新触发新的渲染描述，副作用与外部系统同步。新 Hooks 仍要服从调用与状态归属规则，不能只按 API 名字选择。

**最小练习与预期结果**：给表单区分输入、提交中、成功和失败；失败后保留用户可恢复的输入，避免只演示成功动画。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 通过并发更新、Suspense、服务端/客户端组件边界和表单交互学习 React 在 Next.js 中的实际行为。API 是否可用取决于项目锁定的 React 与 Next.js 版本；示例应先在该版本的类型检查和关键交互中验证。

> **目标读者**: 具备React基础的中高级开发者，需要掌握React 19新特性和Next.js深度集成的技术架构师

> **前置知识**: React、Next.js、TypeScript、异步编程和 Web 性能基础；具体版本以项目锁定依赖为准。

> **预计时长**: 10-12小时

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `frameworks` |
| **难度** | ⭐⭐⭐ (精通)|
| **标签** | `#react19` `#concurrent-features` `#suspense` `#server-components` `#optimization` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 🎯 学习目标

### 🚀 并发与异步交互
- 用可观察的输入、提交、成功、失败和重试状态解释一次并发更新
- 判断 Suspense、Transition 和 deferred value 分别解决的是等待呈现、更新优先级还是展示滞后
- 区分 React 的 UI 更新能力、框架的服务端组件能力和应用的业务事务
- 通过剖析数据判断是否需要优化，而不是把并发 API 作为默认包装器

### 🏗️ Next.js 集成能力
- 为一次用户操作画出客户端事件、服务端读取/写入、缓存失效和重新渲染的路径
- 让状态有唯一归属，并在失败或竞态发生时仍能恢复用户输入
- 根据浏览器 API、交互需求与数据保密性划分客户端和服务端组件
- 用深链接、刷新、慢请求和直接调用入口验证架构选择

## 📖 概述

React 提供声明式 UI 与更新协调机制，Next.js 在其上选择路由、服务端执行和缓存边界。它们不能保证页面性能、数据一致性或权限正确：这些结果必须在具体页面、设备、网络和失败场景中测量。本章将每项特性放回一次真实交互中讨论。

## 🆕 版本核对：不要把候选 API 当作项目事实

React API 的实验状态、发布版本和框架支持会变化。开始本节前，先查看 [React 官方版本说明](https://react.dev/blog) 与项目的 `package.json`、锁文件；只有依赖解析到相应稳定版本、类型检查通过并有浏览器回归结果后，才把某个 API 放入生产路径。以下条目用于建立评估问题，不是“在所有 Next.js 项目中均可放心使用”的清单。

以下 API/能力是否稳定、是否被当前框架支持，都必须按上述步骤确认：

### View Transitions 组件稳定

`<ViewTransition>` 基于浏览器原生 View Transition API，在 `startTransition`、Suspense 揭示、`useDeferredValue` 等过渡更新中自动为元素的进入、退出、移动与缩放添加动画，无需引入第三方动画库；`addTransitionType` 可为"前进/后退"等不同过渡类型指定不同动画。

### Fragment Refs 稳定

可直接向 `<Fragment>` 传递 ref，获得 `FragmentInstance` 句柄（支持 `focus`/`blur`、事件监听、`scrollIntoView`、`IntersectionObserver`/`ResizeObserver` 观测等），无需再为挂 ref 而额外包裹一层 `<div>`：

```tsx
import { Fragment, useRef } from 'react';

function List({ items }: { items: string[] }) {
  const listRef = useRef<React.FragmentInstance>(null);
  return (
    <Fragment ref={listRef}>
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </Fragment>
  );
}
```

### React Compiler 稳定可用

React Compiler v1.0 已于 2025-10 发布稳定版，Next.js 16 内置支持（`create-next-app` 模板可选启用），自动完成组件与 Hook 的记忆化，无需手写 `useMemo`/`useCallback`/`memo`。

### 其他更新

- `browser()` 与 `use(browser())`：声明组件仅在浏览器端渲染，避免"服务端渲染后再在 Effect 中检测客户端"的绕行方案
- Trusted Types 支持：与 CSP 策略协同保障 DOM 注入安全
- Server Components 中可直接使用 Context Provider，无需额外包装组件

## 🔄 React 19 并发渲染深度解析

### 并发渲染核心原理

```typescript
// src/types/react19-concurrency.ts
export interface ConcurrentRenderingArchitecture {
  // 调度机制
  scheduler: {
    priority: '任务优先级调度 - 高优先级任务优先执行'
    timeSlicing: '时间分片 - 长任务拆分为小时间块'
    interruption: '可中断渲染 - 高优先级任务可中断低优先级任务'
    reconciliation: '协调算法 - 智能更新检测和批处理'
  }

  // 并发特性
  features: {
    suspense: 'Suspense - 异步组件渲染和错误边界'
    transitions: 'Transitions - 状态更新的优先级管理'
    deferred: 'Deferred - 延迟更新和优先级降低'
    concurrentMode: '并发模式 - 多版本UI共存'
  }

  // 性能优化
  optimizations: {
    autoBatching: '自动批处理 - 多个状态更新合并'
    selectiveHydration: '选择性水合 - 优先水合交互组件'
    reactServerComponents: '服务器组件 - 零客户端渲染'
    streamingSSR: '流式SSR - 渐进式页面加载'
  }
}
```

### 高级并发模式实现

```tsx
// src/components/advanced-concurrent-components.tsx
'use client'

import { useState, useTransition, useDeferredValue, useMemo, useCallback } from 'react'
import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'

// 复杂搜索组件
interface SearchResultsProps {
  query: string
  onResultSelect: (result: SearchResult) => void
}

interface SearchResult {
  id: string
  title: string
  description: string
  category: string
  relevance: number
}

export function AdvancedSearchComponent() {
  const [query, setQuery] = useState('')
  const [isPending, startTransition] = useTransition()
  const [searchHistory, setSearchHistory] = useState<string[]>([])

  // 延迟搜索查询，避免频繁请求
  const deferredQuery = useDeferredValue(query)

  // 记忆化搜索结果
  const searchResults = useMemo(() => {
    if (!deferredQuery) return []
    return performSearch(deferredQuery)
  }, [deferredQuery])

  // 搜索函数
  const performSearch = useCallback(async (searchQuery: string): Promise<SearchResult[]> => {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 300))

    // 模拟搜索结果
    const mockResults: SearchResult[] = [
      {
        id: '1',
        title: `搜索结果: ${searchQuery}`,
        description: `与 "${searchQuery}" 相关的详细描述`,
        category: '技术文档',
        relevance: 0.95
      },
      {
        id: '2',
        title: `${searchQuery} - 最佳实践`,
        description: `${searchQuery} 的最佳实践指南`,
        category: '教程',
        relevance: 0.88
      },
      {
        id: '3',
        title: `深入了解 ${searchQuery}`,
        description: `深入探讨 ${searchQuery} 的核心概念`,
        category: '深度文章',
        relevance: 0.76
      }
    ]

    return mockResults
  }, [])

  // 处理搜索输入
  const handleInputChange = (value: string) => {
    setQuery(value)

    // 使用transition包装搜索历史更新
    startTransition(() => {
      if (value && !searchHistory.includes(value)) {
        setSearchHistory(prev => [value, ...prev.slice(0, 9)])
      }
    })
  }

  // 处理结果选择
  const handleResultSelect = useCallback((result: SearchResult) => {
    console.log('Selected result:', result)
  }, [])

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-3xl font-bold mb-6">高级搜索组件</h1>

        {/* 搜索输入框 */}
        <div className="relative mb-6">
          <input
            type="text"
            value={query}
            onChange={(e) => handleInputChange(e.target.value)}
            placeholder="输入搜索内容..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          {isPending && (
            <div className="absolute right-3 top-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            </div>
          )}
        </div>

        {/* 搜索状态显示 */}
        <div className="mb-4 flex items-center justify-between">
          <div className="text-sm text-gray-600">
            {query && `搜索 "${query}" 的结果`}
            {isPending && ' (正在更新...)'}
          </div>
          {deferredQuery !== query && (
            <div className="text-sm text-orange-600">
              输入延迟: "{deferredQuery}"
            </div>
          )}
        </div>

        {/* 搜索结果 */}
        <ErrorBoundary fallback={<div className="text-red-600">搜索失败</div>}>
          <Suspense fallback={<SearchResultsSkeleton />}>
            <SearchResults
              results={searchResults}
              onResultSelect={handleResultSelect}
            />
          </Suspense>
        </ErrorBoundary>

        {/* 搜索历史 */}
        {searchHistory.length > 0 && (
          <div className="mt-8">
            <h3 className="text-lg font-semibold mb-3">搜索历史</h3>
            <div className="flex flex-wrap gap-2">
              {searchHistory.map((term, index) => (
                <button
                  key={index}
                  onClick={() => setQuery(term)}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
                >
                  {term}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// 搜索结果组件
function SearchResults({ results, onResultSelect }: {
  results: SearchResult[]
  onResultSelect: (result: SearchResult) => void
}) {
  if (results.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        没有找到相关结果
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {results.map((result) => (
        <div
          key={result.id}
          onClick={() => onResultSelect(result)}
          className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all cursor-pointer"
        >
          <div className="flex justify-between items-start mb-2">
            <h3 className="text-lg font-semibold text-gray-900">
              {result.title}
            </h3>
            <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
              {result.category}
            </span>
          </div>
          <p className="text-gray-600 mb-2">{result.description}</p>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${result.relevance * 100}%` }}
                />
              </div>
              <span className="text-sm text-gray-500">
                {Math.round(result.relevance * 100)}% 匹配
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

// 搜索结果骨架屏
function SearchResultsSkeleton() {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="p-4 border border-gray-200 rounded-lg">
          <div className="animate-pulse space-y-3">
            <div className="h-6 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            <div className="h-2 bg-gray-200 rounded w-full"></div>
          </div>
        </div>
      ))}
    </div>
  )
}
```

### 高级Suspense模式

```tsx
// src/components/advanced-suspense.tsx
import { Suspense, lazy, ComponentType } from 'react'
import { ErrorBoundary } from 'react-error-boundary'

// 智能懒加载组件
interface LazyComponentProps {
  fallback?: React.ReactNode
  errorFallback?: ComponentType<{ error: Error; retry: () => void }>
  delay?: number
}

export function createLazyComponent<T extends Record<string, any>>(
  importFunc: () => Promise<{ default: ComponentType<T> }>,
  options: LazyComponentProps = {}
) {
  const LazyComponent = lazy(importFunc)

  const {
    fallback = <div>Loading...</div>,
    errorFallback = DefaultErrorFallback,
    delay = 0
  } = options

  return function LazyComponentWrapper(props: T) {
    return (
      <ErrorBoundary FallbackComponent={errorFallback}>
        <Suspense fallback={delay ? <DelayedFallback delay={delay} child={fallback} /> : fallback}>
          <LazyComponent {...props} />
        </Suspense>
      </ErrorBoundary>
    )
  }
}

// 延迟显示fallback
function DelayedFallback({ delay, child }: { delay: number; child: React.ReactNode }) {
  const [showFallback, setShowFallback] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setShowFallback(true), delay)
    return () => clearTimeout(timer)
  }, [delay])

  return showFallback ? <>{child}</> : null
}

// 默认错误边界
function DefaultErrorFallback({ error, retry }: { error: Error; retry: () => void }) {
  return (
    <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
      <h3 className="text-red-800 font-medium">组件加载失败</h3>
      <p className="text-red-600 text-sm mt-1 mb-3">{error.message}</p>
      <button
        onClick={retry}
        className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
      >
        重试
      </button>
    </div>
  )
}

// 嵌套Suspense模式
export function NestedSuspenseExample() {
  return (
    <div className="space-y-8">
      {/* 外层Suspense - 页面级别 */}
      <Suspense fallback={<PageSkeleton />}>
        <PageContent>
          {/* 中层Suspense - 主要内容 */}
          <Suspense fallback={<MainContentSkeleton />}>
            <MainContent>
              {/* 内层Suspense - 子组件 */}
              <Suspense fallback={<SubComponentSkeleton />}>
                <SubComponent />
              </Suspense>

              {/* 并行Suspense - 独立组件 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Suspense fallback={<SidePanelSkeleton />}>
                  <SidePanel />
                </Suspense>
                <Suspense fallback={<RelatedContentSkeleton />}>
                  <RelatedContent />
                </Suspense>
              </div>
            </MainContent>
          </Suspense>
        </PageContent>
      </Suspense>
    </div>
  )
}

// 页面内容
function PageContent({ children }: { children: React.ReactNode }) {
  return (
    <div className="max-w-6xl mx-auto p-6">
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900">
          嵌套Suspense示例
        </h1>
        <p className="text-xl text-gray-600 mt-2">
          展示多层Suspense的加载效果
        </p>
      </header>
      {children}
    </div>
  )
}

// 主要内容
function MainContent({ children }: { children: React.ReactNode }) {
  return (
    <main className="space-y-8">
      <section className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-semibold mb-4">主要内容区域</h2>
        {children}
      </section>
    </main>
  )
}

// 子组件
async function SubComponent() {
  // 模拟异步数据获取
  await new Promise(resolve => setTimeout(resolve, 2000))

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
      <h3 className="text-xl font-semibold text-blue-900 mb-3">
        子组件内容
      </h3>
      <p className="text-blue-700">
        这是一个异步加载的子组件，展示了Suspense的嵌套效果。
      </p>
    </div>
  )
}

// 侧边面板
async function SidePanel() {
  await new Promise(resolve => setTimeout(resolve, 1500))

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-4">侧边面板</h3>
      <div className="space-y-3">
        {['项目1', '项目2', '项目3'].map((project, index) => (
          <div key={index} className="p-3 bg-white rounded border">
            <h4 className="font-medium">{project}</h4>
            <p className="text-sm text-gray-600 mt-1">
              项目描述内容
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

// 相关内容
async function RelatedContent() {
  await new Promise(resolve => setTimeout(resolve, 1000))

  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-green-900 mb-4">
        相关内容
      </h3>
      <div className="space-y-2">
        {['相关链接1', '相关链接2', '相关链接3'].map((link, index) => (
          <a
            key={index}
            href="#"
            className="block p-2 bg-white rounded border hover:bg-green-50 transition-colors"
          >
            {link}
          </a>
        ))}
      </div>
    </div>
  )
}

// 骨架屏组件
function PageSkeleton() {
  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="animate-pulse space-y-4">
        <div className="h-12 bg-gray-200 rounded w-1/3"></div>
        <div className="h-6 bg-gray-200 rounded w-1/2"></div>
      </div>
    </div>
  )
}

function MainContentSkeleton() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="h-8 bg-gray-200 rounded w-1/4"></div>
      <div className="space-y-3">
        <div className="h-4 bg-gray-200 rounded"></div>
        <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        <div className="h-4 bg-gray-200 rounded w-4/6"></div>
      </div>
    </div>
  )
}

function SubComponentSkeleton() {
  return (
    <div className="animate-pulse bg-blue-50 border border-blue-200 rounded-lg p-6">
      <div className="h-6 bg-blue-200 rounded w-1/3 mb-3"></div>
      <div className="h-4 bg-blue-200 rounded w-full"></div>
      <div className="h-4 bg-blue-200 rounded w-3/4 mt-2"></div>
    </div>
  )
}

function SidePanelSkeleton() {
  return (
    <div className="animate-pulse bg-gray-50 border border-gray-200 rounded-lg p-6">
      <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="p-3 bg-white rounded border">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    </div>
  )
}

function RelatedContentSkeleton() {
  return (
    <div className="animate-pulse bg-green-50 border border-green-200 rounded-lg p-6">
      <div className="h-6 bg-green-200 rounded w-1/4 mb-4"></div>
      <div className="space-y-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-4 bg-green-200 rounded w-full"></div>
        ))}
      </div>
    </div>
  )
}
```

## 🖥️ Server Components 深度实践

### 高级服务器组件架构

```tsx
// src/app/components/advanced-server-components.tsx
// Next.js 16：unstable_cache 已弃用，改用 "use cache" + cacheTag/cacheLife 显式缓存
import { cacheLife, cacheTag } from 'next/cache'
import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'

// 缓存策略管理器
export class ServerCacheManager {
  // 多级缓存配置（Next.js 16：以 cacheLife profile 表达缓存时长）
  private static cacheConfig = {
    // 短期缓存 - 频繁变化的数据
    shortTerm: {
      profile: 'minutes', // 分钟级
      tags: ['short-term']
    },

    // 中期缓存 - 中等频率变化的数据
    mediumTerm: {
      profile: 'hours', // 小时级
      tags: ['medium-term']
    },

    // 长期缓存 - 很少变化的数据
    longTerm: {
      profile: 'days', // 天级
      tags: ['long-term']
    }
  }

  // 创建缓存函数
  static createCachedFunction<T, Args extends any[]>(
    fn: (...args: Args) => Promise<T>,
    config: 'shortTerm' | 'mediumTerm' | 'longTerm' = 'mediumTerm'
  ) {
    const { profile, tags } = this.cacheConfig[config]

    // Next.js 16：用 "use cache" 指令替代 unstable_cache
    return async (...args: Args): Promise<T> => {
      'use cache'
      cacheLife(profile)
      cacheTag(...tags)
      return fn(...args)
    }
  }

  // 数据预加载
  static async preloadData(keys: string[]) {
    const preloadPromises = keys.map(async (key) => {
      try {
        // 这里实现具体的数据预加载逻辑
        console.log(`Preloading data for key: ${key}`)
      } catch (error) {
        console.error(`Failed to preload data for key ${key}:`, error)
      }
    })

    await Promise.allSettled(preloadPromises)
  }
}

// 高级数据获取组件
interface DataProviderProps {
  id: string
  fallback?: React.ReactNode
  errorFallback?: React.ComponentType<{ error: Error; reset: () => void }>
  cacheStrategy?: 'shortTerm' | 'mediumTerm' | 'longTerm'
}

// 缓存的数据获取函数
const getCachedArticle = ServerCacheManager.createCachedFunction(
  async (id: string) => {
    const response = await fetch(`https://api.example.com/articles/${id}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch article: ${id}`)
    }
    return response.json()
  },
  'mediumTerm'
)

const getCachedComments = ServerCacheManager.createCachedFunction(
  async (articleId: string) => {
    const response = await fetch(`https://api.example.com/articles/${articleId}/comments`)
    if (!response.ok) {
      throw new Error(`Failed to fetch comments for article: ${articleId}`)
    }
    return response.json()
  },
  'shortTerm'
)

const getCachedRelatedArticles = ServerCacheManager.createCachedFunction(
  async (articleId: string) => {
    const response = await fetch(`https://api.example.com/articles/${articleId}/related`)
    if (!response.ok) {
      throw new Error(`Failed to fetch related articles for: ${articleId}`)
    }
    return response.json()
  },
  'mediumTerm'
)

// 主要的Article服务器组件
export async function ArticleServerComponent({
  id,
  fallback,
  errorFallback
}: DataProviderProps) {
  // 并行数据获取
  const [article, relatedArticles] = await Promise.all([
    getCachedArticle(id),
    getCachedRelatedArticles(id)
  ])

  if (!article) {
    return <div>Article not found</div>
  }

  return (
    <ErrorBoundary FallbackComponent={errorFallback || DefaultErrorFallback}>
      <article className="max-w-4xl mx-auto">
        {/* 文章头部 */}
        <ArticleHeader article={article} />

        {/* 文章内容 */}
        <ArticleContent article={article} />

        {/* 相关文章 */}
        <Suspense fallback={fallback || <RelatedArticlesSkeleton />}>
          <RelatedArticles articles={relatedArticles} />
        </Suspense>

        {/* 评论区 - 异步加载 */}
        <Suspense fallback={fallback || <CommentsSkeleton />}>
          <CommentsSection articleId={id} />
        </Suspense>
      </article>
    </ErrorBoundary>
  )
}

// 文章头部
function ArticleHeader({ article }: { article: any }) {
  return (
    <header className="mb-8">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">
        {article.title}
      </h1>

      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-4">
          {article.author.avatar && (
            <img
              src={article.author.avatar}
              alt={article.author.name}
              width={40}
              height={40}
              className="rounded-full"
            />
          )}
          <div>
            <p className="font-medium">{article.author.name}</p>
            <p className="text-sm text-gray-600">
              {new Date(article.publishedAt).toLocaleDateString('zh-CN')}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded">
            {article.category}
          </span>
          <span className="text-sm text-gray-600">
            {article.readTime} 分钟阅读
          </span>
        </div>
      </div>

      {article.excerpt && (
        <p className="text-xl text-gray-600 leading-relaxed">
          {article.excerpt}
        </p>
      )}
    </header>
  )
}

// 文章内容
function ArticleContent({ article }: { article: any }) {
  return (
    <div className="prose prose-lg max-w-none mb-12">
      <div dangerouslySetInnerHTML={{ __html: article.content }} />

      {/* 文章元数据 */}
      <div className="mt-8 pt-8 border-t border-gray-200">
        <div className="flex flex-wrap gap-2">
          {article.tags.map((tag: string, index: number) => (
            <span
              key={index}
              className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full"
            >
              #{tag}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}

// 相关文章
async function RelatedArticles({ articles }: { articles: any[] }) {
  if (!articles || articles.length === 0) {
    return null
  }

  return (
    <section className="mb-12">
      <h2 className="text-2xl font-bold mb-6">相关文章</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {articles.map((article: any, index: number) => (
          <article
            key={article.id}
            className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow"
          >
            {article.coverImage && (
              <img
                src={article.coverImage}
                alt={article.title}
                width={400}
                height={200}
                className="w-full h-48 object-cover"
              />
            )}
            <div className="p-4">
              <h3 className="font-semibold text-lg mb-2 line-clamp-2">
                {article.title}
              </h3>
              <p className="text-gray-600 text-sm line-clamp-2 mb-3">
                {article.excerpt}
              </p>
              <div className="flex items-center justify-between text-sm text-gray-500">
                <span>{new Date(article.publishedAt).toLocaleDateString('zh-CN')}</span>
                <span>{article.readTime} 分钟</span>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}

// 评论区组件
async function CommentsSection({ articleId }: { articleId: string }) {
  const comments = await getCachedComments(articleId)

  return (
    <section>
      <h2 className="text-2xl font-bold mb-6">
        评论 ({comments.length})
      </h2>

      {comments.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          暂无评论，来发表第一条评论吧！
        </div>
      ) : (
        <div className="space-y-4">
          {comments.map((comment: any, index: number) => (
            <Comment key={comment.id} comment={comment} />
          ))}
        </div>
      )}

      {/* 评论表单 - 客户端组件 */}
      <CommentForm articleId={articleId} />
    </section>
  )
}

// 评论组件
function Comment({ comment }: { comment: any }) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex items-start space-x-3">
        {comment.author.avatar ? (
          <img
            src={comment.author.avatar}
            alt={comment.author.name}
            width={40}
            height={40}
            className="rounded-full"
          />
        ) : (
          <div className="w-10 h-10 bg-gray-300 rounded-full"></div>
        )}

        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-medium">{comment.author.name}</h4>
            <span className="text-sm text-gray-500">
              {new Date(comment.createdAt).toLocaleDateString('zh-CN')}
            </span>
          </div>
          <p className="text-gray-700">{comment.content}</p>
        </div>
      </div>
    </div>
  )
}

// 评论表单 - 客户端组件
function CommentForm({ articleId }: { articleId: string }) {
  return (
    <div className="mt-6 bg-white border border-gray-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-4">发表评论</h3>
      <textarea
        placeholder="写下你的评论..."
        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
        rows={4}
      />
      <div className="mt-4 flex justify-end">
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          发表评论
        </button>
      </div>
    </div>
  )
}

// 骨架屏组件
function RelatedArticlesSkeleton() {
  return (
    <section className="mb-12">
      <h2 className="text-2xl font-bold mb-6">相关文章</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="animate-pulse">
            <div className="h-48 bg-gray-200 rounded-lg mb-4"></div>
            <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded mb-1"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        ))}
      </div>
    </section>
  )
}

function CommentsSkeleton() {
  return (
    <section>
      <h2 className="text-2xl font-bold mb-6">评论</h2>
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="animate-pulse bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <div className="w-10 h-10 bg-gray-300 rounded-full"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                <div className="h-3 bg-gray-200 rounded w-full"></div>
                <div className="h-3 bg-gray-200 rounded w-3/4"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

// 默认错误回退
function DefaultErrorFallback({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
      <h3 className="text-red-800 font-medium mb-2">内容加载失败</h3>
      <p className="text-red-600 text-sm mb-3">{error.message}</p>
      <button
        onClick={reset}
        className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
      >
        重试
      </button>
    </div>
  )
}
```

## ⚡ 性能优化和最佳实践

### React 19 性能优化策略

```tsx
// src/components/performance-optimized-components.tsx
'use client'

import { memo, useMemo, useCallback, useState, useEffect } from 'react'
import { useTransition } from 'react'

// 高性能列表组件
interface OptimizedListItemProps {
  item: {
    id: string
    title: string
    description: string
    category: string
    price: number
    inStock: boolean
  }
  onSelect?: (item: any) => void
  selected?: boolean
}

export const OptimizedListItem = memo<OptimizedListItemProps>(({
  item,
  onSelect,
  selected = false
}) => {
  const handleClick = useCallback(() => {
    onSelect?.(item)
  }, [item, onSelect])

  // 记忆化价格显示
  const formattedPrice = useMemo(() => {
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY'
    }).format(item.price)
  }, [item.price])

  // 记忆化库存状态样式
  const stockStyle = useMemo(() => ({
    color: item.inStock ? 'text-green-600' : 'text-red-600',
    fontWeight: item.inStock ? 'normal' : 'bold' as const
  }), [item.inStock])

  return (
    <div
      className={`
        p-4 border rounded-lg cursor-pointer transition-all
        ${selected
          ? 'border-blue-500 bg-blue-50 shadow-md'
          : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
        }
      `}
      onClick={handleClick}
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-gray-900 flex-1 mr-4">
          {item.title}
        </h3>
        <span className="text-lg font-bold text-blue-600">
          {formattedPrice}
        </span>
      </div>

      <p className="text-gray-600 text-sm mb-3 line-clamp-2">
        {item.description}
      </p>

      <div className="flex justify-between items-center">
        <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
          {item.category}
        </span>
        <span style={stockStyle}>
          {item.inStock ? '有库存' : '缺货'}
        </span>
      </div>
    </div>
  )
})

OptimizedListItem.displayName = 'OptimizedListItem'

// 高性能过滤组件
interface PerformanceFilterProps {
  items: any[]
  onFilterChange: (filteredItems: any[]) => void
}

export function PerformanceFilter({ items, onFilterChange }: PerformanceFilterProps) {
  const [filters, setFilters] = useState({
    category: '',
    priceRange: [0, 1000] as [number, number],
    inStockOnly: false,
    searchTerm: ''
  })

  const [isPending, startTransition] = useTransition()

  // 记忆化过滤逻辑
  const filteredItems = useMemo(() => {
    return items.filter(item => {
      // 类别过滤
      if (filters.category && item.category !== filters.category) {
        return false
      }

      // 价格范围过滤
      if (item.price < filters.priceRange[0] || item.price > filters.priceRange[1]) {
        return false
      }

      // 库存过滤
      if (filters.inStockOnly && !item.inStock) {
        return false
      }

      // 搜索过滤
      if (filters.searchTerm) {
        const searchLower = filters.searchTerm.toLowerCase()
        return (
          item.title.toLowerCase().includes(searchLower) ||
          item.description.toLowerCase().includes(searchLower)
        )
      }

      return true
    })
  }, [items, filters])

  // 防抖的过滤更新
  const updateFilters = useCallback((newFilters: typeof filters) => {
    startTransition(() => {
      setFilters(newFilters)
    })
  }, [])

  // 当过滤结果变化时，通知父组件
  useEffect(() => {
    onFilterChange(filteredItems)
  }, [filteredItems, onFilterChange])

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4">高级过滤</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* 搜索框 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            搜索
          </label>
          <input
            type="text"
            value={filters.searchTerm}
            onChange={(e) => updateFilters({ ...filters, searchTerm: e.target.value })}
            placeholder="搜索商品..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* 类别选择 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            类别
          </label>
          <select
            value={filters.category}
            onChange={(e) => updateFilters({ ...filters, category: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">全部类别</option>
            <option value="electronics">电子产品</option>
            <option value="clothing">服装</option>
            <option value="books">图书</option>
            <option value="home">家居</option>
          </select>
        </div>

        {/* 价格范围 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            价格范围
          </label>
          <div className="flex items-center space-x-2">
            <input
              type="number"
              value={filters.priceRange[0]}
              onChange={(e) => updateFilters({
                ...filters,
                priceRange: [parseInt(e.target.value), filters.priceRange[1]]
              })}
              className="w-20 px-2 py-1 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
            />
            <span>-</span>
            <input
              type="number"
              value={filters.priceRange[1]}
              onChange={(e) => updateFilters({
                ...filters,
                priceRange: [filters.priceRange[0], parseInt(e.target.value)]
              })}
              className="w-20 px-2 py-1 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* 库存状态 */}
        <div className="flex items-end">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={filters.inStockOnly}
              onChange={(e) => updateFilters({ ...filters, inStockOnly: e.target.checked })}
              className="rounded text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm font-medium text-gray-700">
              仅显示有库存
            </span>
          </label>
        </div>
      </div>

      {/* 过滤状态 */}
      <div className="mt-4 flex items-center justify-between">
        <div className="text-sm text-gray-600">
          找到 {filteredItems.length} 个商品
          {isPending && <span className="ml-2 text-blue-600">(更新中...)</span>}
        </div>

        <button
          onClick={() => updateFilters({
            category: '',
            priceRange: [0, 1000],
            inStockOnly: false,
            searchTerm: ''
          })}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          重置过滤
        </button>
      </div>
    </div>
  )
}

// 虚拟滚动组件
interface VirtualScrollProps {
  items: any[]
  itemHeight: number
  containerHeight: number
  renderItem: (item: any, index: number) => React.ReactNode
}

export function VirtualScroll({
  items,
  itemHeight,
  containerHeight,
  renderItem
}: VirtualScrollProps) {
  const [scrollTop, setScrollTop] = useState(0)

  // 计算可见项目
  const visibleRange = useMemo(() => {
    const startIndex = Math.floor(scrollTop / itemHeight)
    const endIndex = Math.min(
      startIndex + Math.ceil(containerHeight / itemHeight) + 1,
      items.length - 1
    )
    return { startIndex, endIndex }
  }, [scrollTop, itemHeight, containerHeight, items.length])

  const visibleItems = useMemo(() => {
    return items.slice(visibleRange.startIndex, visibleRange.endIndex + 1)
  }, [items, visibleRange])

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop)
  }, [])

  return (
    <div
      style={{ height: containerHeight, overflow: 'auto' }}
      onScroll={handleScroll}
      className="border border-gray-200 rounded-lg"
    >
      <div style={{ height: items.length * itemHeight, position: 'relative' }}>
        {visibleItems.map((item, index) => {
          const actualIndex = visibleRange.startIndex + index
          return (
            <div
              key={item.id || actualIndex}
              style={{
                position: 'absolute',
                top: actualIndex * itemHeight,
                left: 0,
                right: 0,
                height: itemHeight
              }}
            >
              {renderItem(item, actualIndex)}
            </div>
          )
        })}
      </div>
    </div>
  )
}

// 使用示例组件
export function PerformanceExample() {
  // 生成大量测试数据
  const [items] = useState(() =>
    Array.from({ length: 10000 }, (_, i) => ({
      id: `item-${i}`,
      title: `商品 ${i + 1}`,
      description: `这是商品 ${i + 1} 的详细描述，包含了产品的特性和优势。`,
      category: ['electronics', 'clothing', 'books', 'home'][i % 4],
      price: Math.floor(Math.random() * 1000) + 10,
      inStock: Math.random() > 0.2
    }))
  )

  const [filteredItems, setFilteredItems] = useState(items)
  const [selectedItem, setSelectedItem] = useState<any>(null)

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">性能优化示例</h1>

      <PerformanceFilter
        items={items}
        onFilterChange={setFilteredItems}
      />

      {selectedItem && (
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-blue-800">
            已选择: {selectedItem.title}
          </p>
        </div>
      )}

      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold">
            商品列表 ({filteredItems.length} 项)
          </h2>
        </div>

        <VirtualScroll
          items={filteredItems}
          itemHeight={120}
          containerHeight={400}
          renderItem={(item, index) => (
            <div className="p-4">
              <OptimizedListItem
                item={item}
                selected={selectedItem?.id === item.id}
                onSelect={setSelectedItem}
              />
            </div>
          )}
        />
      </div>
    </div>
  )
}
```

## ✅ 总结

本章列出的是可在具体项目中验证的 React 与 Next.js 协作边界；读完不等于已经获得“企业级集成能力”。完成以下验收，再把相应模式带入更复杂的页面：

### 🔄 并发渲染验收
- 输入、提交、成功、失败和取消各自有可见状态；失败时保留可恢复输入且不重复写入
- 在慢请求、请求乱序和组件卸载时验证 Suspense、Transition 或 deferred value 的实际呈现结果
- 记录一个性能瓶颈的基线，确认并发处理没有掩盖数据错误或增加不必要的等待

### 🖥️ 服务端/客户端边界验收
- 刷新与深链接都能得到与客户端导航一致的权限和数据结果
- 只在需要浏览器 API 或交互的叶子组件使用客户端边界，检查敏感数据未随浏览器包发送
- 为缓存读取、写后失效和流式错误边界写出并复现测试场景

### ⚡ 性能优化最佳实践
优化前先记录一次实际交互，例如输入筛选词时哪部分计算或渲染变慢。memo、useMemo、useCallback 分别影响组件跳过或值/函数引用复用，依赖不正确会产生旧结果，使用本身也有维护成本。

大量列表可评估虚拟化，昂贵计算可减少输入范围或移到适当位置。用同一数据量比较交互延迟与提交耗时，确保修改后结果仍正确，不能把使用了某个 Hook 当作性能已经改善。

## 📚 下一步学习

- 深入学习React 19的新特性和API
- 掌握复杂的并发场景和状态管理
- 学习服务器组件的测试和调试策略
- 探索React 19在边缘计算中的应用
- 了解React 19与其他框架的集成和对比

## 🔗 相关资源链接

### 官方资源
- [React 19 官方文档](https://react.dev/)
- [React 19 Beta 发布说明](https://react.dev/blog/2024/04/25/react-19)
- [React 并发特性文档](https://react.dev/reference/react)
- [React Server Components 文档](https://react.dev/reference/rsc/server-components)

### 技术文章
- [React 19 新特性详解](https://react.dev/blog)
- [并发渲染最佳实践](https://react.dev/learn/render-and-commit)
- [Suspense 数据获取模式](https://react.dev/reference/react/Suspense)

### 工具和资源
- [React DevTools](https://react.dev/learn/react-developer-tools)
- [React 官方示例](https://react.dev/examples)

## 📚 模块内相关文档

### 同模块相关文档
- [Next.js 16 完整指南](./01-nextjs-16-complete.md) - 掌握Next.js 16的核心特性和App Router架构
- [全栈开发模式](./03-full-stack-patterns.md) - 学习如何构建完整的全栈应用
- [性能优化策略](./04-performance-optimization.md) - 深入了解应用性能调优技术

### 相关知识模块
- [测试相关模块](../testing/01-unit-testing.md) - React 19组件的单元测试策略
- [测试相关模块](../testing/03-e2e-testing.md) - Next.js应用的端到端测试实践

### 基础前置知识
- [React Hooks 模式](../reference/framework-patterns/03-client-components-patterns.md) - 深入理解React Hooks
- [JavaScript 异步编程](../reference/language-concepts/04-javascript-modern.md) - 掌握现代异步编程模式
- [TypeScript 泛型编程](../reference/language-concepts/03-typescript-types.md) - TypeScript高级类型系统

---

## ✨ 总结

### 核心技术要点
1. **并发渲染机制**: React 19的并发特性和调度算法，提供更流畅的用户体验
2. **Suspense边界管理**: 智能的异步组件加载和错误处理机制
3. **Server Components**: 零客户端JavaScript的服务端渲染组件架构
4. **性能优化策略**: memo、useMemo、useCallback等优化工具的高级应用
5. **数据流管理**: React 19与Next.js 16集成的现代数据获取和状态管理模式

### 学习成果自检
- [ ] 理解React 19并发渲染的工作原理和优势
- [ ] 掌握Suspense、Transition、Deferred等并发特性的使用
- [ ] 能够设计和实现复杂的服务器组件架构
- [ ] 熟练运用React 19的性能优化工具和模式
- [ ] 能够构建高性能的React 19与Next.js 16集成应用

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
**🏷️ 标签**: `#react19` `#concurrent-features` `#suspense` `#server-components` `#performance`
**⭐ 推荐指数**: ⭐⭐⭐

**💡 提示**: 本模块为React 19高级特性模块，建议先掌握React基础和Next.js 16基础后再进行学习。

**🎯 学习建议**:
- 建议学习周期: 2-3周
- 理论与实践时间比例: 4:6
- 重点掌握并发渲染和Server Components
- 结合实际项目进行实践和调试

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
