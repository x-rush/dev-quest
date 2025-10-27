# 高级性能调优完整指南

> **文档简介**: Next.js 15 + React 19 企业级高级性能调优指南，涵盖内存管理、并发优化、网络优化、缓存策略、预加载技术等深度优化策略

> **目标读者**: 高级前端工程师、性能专家、技术架构师、DevOps工程师

> **前置知识**: Next.js 15深度掌握、React 19高级特性、Web性能基础、Chrome DevTools高级使用

> **预计时长**: 10-15小时

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `advanced-topics/performance` |
| **难度** | ⭐⭐⭐⭐⭐ (5/5星) |
| **标签** | `#performance-optimization` `#advanced-optimization` `#memory-management` `#caching` `#nextjs15` `#react19` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标

- 掌握高级内存管理和垃圾回收优化策略
- 实施React 19并发特性的性能优化
- 建立多层级缓存体系和智能预加载机制
- 实现网络层优化和资源加载策略
- 构建生产级性能监控和自动优化系统

## 📖 概述

本指南深入探讨Next.js 15应用的高级性能优化技术，涵盖从内存管理到网络传输的全方位优化策略。通过实际代码示例和最佳实践，帮助企业级应用达到极致性能标准。

## 🧠 内存管理优化

### 📊 内存泄漏检测和预防

```typescript
// app/lib/memory-manager.ts
class MemoryManager {
  private memoryUsage: Map<string, number> = new Map()
  private observers: MutationObserver[] = []
  private intervals: NodeJS.Timeout[] = []
  private eventListeners: Array<{ target: EventTarget; event: string; handler: Function }> = []

  constructor() {
    this.setupMemoryMonitoring()
    this.setupAutoCleanup()
  }

  // 内存使用监控
  private setupMemoryMonitoring() {
    if (typeof window !== 'undefined' && 'memory' in performance) {
      const monitorMemory = () => {
        const memory = (performance as any).memory
        const memoryInfo = {
          usedJSHeapSize: memory.usedJSHeapSize,
          totalJSHeapSize: memory.totalJSHeapSize,
          jsHeapSizeLimit: memory.jsHeapSizeLimit,
          timestamp: Date.now()
        }

        this.memoryUsage.set('current', memoryInfo.usedJSHeapSize)

        // 检测内存泄漏
        this.detectMemoryLeak(memoryInfo)

        // 发送到分析服务
        this.reportMemoryUsage(memoryInfo)
      }

      // 每5秒监控一次
      setInterval(monitorMemory, 5000)
      monitorMemory() // 立即执行一次
    }
  }

  // 内存泄漏检测
  private detectMemoryLeak(memoryInfo: any) {
    const threshold = 50 * 1024 * 1024 // 50MB
    const previousUsage = this.memoryUsage.get('previous') || 0

    if (memoryInfo.usedJSHeapSize - previousUsage > threshold) {
      console.warn('Potential memory leak detected:', {
        current: memoryInfo.usedJSHeapSize,
        previous: previousUsage,
        increase: memoryInfo.usedJSHeapSize - previousUsage
      })

      // 触发内存清理
      this.triggerMemoryCleanup()
    }

    this.memoryUsage.set('previous', memoryInfo.usedJSHeapSize)
  }

  // 自动清理机制
  private setupAutoCleanup() {
    // 页面卸载时清理
    window.addEventListener('beforeunload', () => {
      this.cleanup()
    })

    // 页面隐藏时清理
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.cleanup()
      }
    })
  }

  // 注册需要管理的资源
  public registerObserver(observer: MutationObserver) {
    this.observers.push(observer)
  }

  public setInterval(callback: Function, delay: number): NodeJS.Timeout {
    const interval = setInterval(callback, delay)
    this.intervals.push(interval)
    return interval
  }

  public addEventListener(target: EventTarget, event: string, handler: Function) {
    target.addEventListener(event, handler as EventListener)
    this.eventListeners.push({ target, event, handler })
  }

  // 手动触发清理
  public triggerMemoryCleanup() {
    // 清理未使用的组件
    this.cleanupUnusedComponents()

    // 强制垃圾回收（如果支持）
    if (window.gc) {
      window.gc()
    }
  }

  private cleanupUnusedComponents() {
    // 实现组件清理逻辑
    const unusedElements = document.querySelectorAll('[data-cleanup="true"]')
    unusedElements.forEach(element => {
      element.remove()
    })
  }

  // 完全清理
  public cleanup() {
    // 断开观察者
    this.observers.forEach(observer => observer.disconnect())
    this.observers = []

    // 清理定时器
    this.intervals.forEach(interval => clearInterval(interval))
    this.intervals = []

    // 移除事件监听器
    this.eventListeners.forEach(({ target, event, handler }) => {
      target.removeEventListener(event, handler as EventListener)
    })
    this.eventListeners = []
  }

  private async reportMemoryUsage(memoryInfo: any) {
    try {
      await fetch('/api/analytics/memory', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          memory: memoryInfo,
          url: window.location.href,
          timestamp: Date.now()
        })
      })
    } catch (error) {
      console.error('Failed to report memory usage:', error)
    }
  }

  // 获取内存统计
  public getMemoryStats() {
    if (typeof window !== 'undefined' && 'memory' in performance) {
      const memory = (performance as any).memory
      return {
        used: memory.usedJSHeapSize,
        total: memory.totalJSHeapSize,
        limit: memory.jsHeapSizeLimit,
        usagePercentage: (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100
      }
    }
    return null
  }
}

// 全局内存管理器
export const memoryManager = new MemoryManager()
```

### 🔄 组件级内存优化

```typescript
// app/hooks/useMemoryOptimized.ts
import { useEffect, useRef, useCallback } from 'react'

interface MemoryOptimizedOptions {
  cleanupOnUnmount?: boolean
  debounceCleanup?: number
  maxMemoryUsage?: number
}

export function useMemoryOptimized<T = any>(
  factory: () => T,
  options: MemoryOptimizedOptions = {}
) {
  const {
    cleanupOnUnmount = true,
    debounceCleanup = 1000,
    maxMemoryUsage = 10 * 1024 * 1024 // 10MB
  } = options

  const instanceRef = useRef<T | null>(null)
  const cleanupTimerRef = useRef<NodeJS.Timeout>()

  // 延迟创建实例
  const getInstance = useCallback(() => {
    if (!instanceRef.current) {
      instanceRef.current = factory()

      // 监控内存使用
      if (maxMemoryUsage) {
        const checkMemoryUsage = () => {
          const stats = memoryManager.getMemoryStats()
          if (stats && stats.used > maxMemoryUsage) {
            console.warn('Component memory usage exceeds threshold:', stats)
            cleanupInstance()
          }
        }

        memoryManager.setInterval(checkMemoryUsage, 5000)
      }
    }
    return instanceRef.current
  }, [factory, maxMemoryUsage])

  // 清理实例
  const cleanupInstance = useCallback(() => {
    if (instanceRef.current) {
      // 如果实例有清理方法，调用它
      if (typeof instanceRef.current === 'object' &&
          'cleanup' in instanceRef.current &&
          typeof instanceRef.current.cleanup === 'function') {
        (instanceRef.current as any).cleanup()
      }

      instanceRef.current = null
    }
  }, [])

  // 防抖清理
  const scheduleCleanup = useCallback(() => {
    if (cleanupTimerRef.current) {
      clearTimeout(cleanupTimerRef.current)
    }

    cleanupTimerRef.current = setTimeout(() => {
      cleanupInstance()
    }, debounceCleanup)
  }, [cleanupInstance, debounceCleanup])

  useEffect(() => {
    return () => {
      if (cleanupOnUnmount) {
        cleanupInstance()
      }
      if (cleanupTimerRef.current) {
        clearTimeout(cleanupTimerRef.current)
      }
    }
  }, [cleanupOnUnmount, cleanupInstance])

  return {
    instance: getInstance(),
    cleanup: cleanupInstance,
    scheduleCleanup
  }
}

// 内存优化的大数据组件
export function MemoryOptimizedDataTable({ data }: { data: any[] }) {
  const [visibleData, setVisibleData] = useState(data.slice(0, 100))
  const [startIndex, setStartIndex] = useState(0)
  const containerRef = useRef<HTMLDivElement>(null)

  // 虚拟滚动优化
  const { instance: intersectionObserver } = useMemoryOptimized(
    () => new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            loadMoreData()
          }
        })
      },
      { threshold: 0.1 }
    )
  )

  // 智能数据加载
  const loadMoreData = useCallback(() => {
    const nextIndex = startIndex + 100
    if (nextIndex < data.length) {
      const newData = data.slice(nextIndex, nextIndex + 100)
      setVisibleData(prev => [...prev, ...newData])
      setStartIndex(nextIndex)
    }
  }, [data, startIndex])

  useEffect(() => {
    if (containerRef.current && intersectionObserver) {
      intersectionObserver.observe(containerRef.current)
    }

    return () => {
      if (intersectionObserver) {
        intersectionObserver.disconnect()
      }
    }
  }, [intersectionObserver])

  return (
    <div className="memory-optimized-data-table">
      <div className="table-container">
        {/* 只渲染可见的数据行 */}
        {visibleData.map((row, index) => (
          <div key={index} className="table-row">
            {/* 渲染行内容 */}
          </div>
        ))}
      </div>

      {/* 触发加载更多的元素 */}
      <div ref={containerRef} className="load-more-trigger">
        Loading more data...
      </div>
    </div>
  )
}
```

## ⚡ React 19 并发优化

### 🔄 Concurrent Features 深度应用

```typescript
// app/components/ConcurrentRenderer.tsx
import { Suspense, useTransition, useDeferredValue, startTransition } from 'react'

interface ConcurrentRendererProps {
  data: any[]
  renderItem: (item: any, index: number) => React.ReactNode
  fallback?: React.ReactNode
}

export function ConcurrentRenderer({
  data,
  renderItem,
  fallback = <div>Loading...</div>
}: ConcurrentRendererProps) {
  const [isPending, startTransition] = useTransition()
  const [filter, setFilter] = useState('')
  const deferredFilter = useDeferredValue(filter)

  // 过滤数据
  const filteredData = useMemo(() => {
    return data.filter(item =>
      item.name.toLowerCase().includes(deferredFilter.toLowerCase())
    )
  }, [data, deferredFilter])

  // 处理输入变化
  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // 使用 startTransition 标记非紧急更新
    startTransition(() => {
      setFilter(e.target.value)
    })
  }

  return (
    <div className="concurrent-renderer">
      <input
        type="text"
        placeholder="Filter items..."
        onChange={handleFilterChange}
        className="filter-input"
      />

      {isPending && (
        <div className="loading-indicator">
          Updating results...
        </div>
      )}

      <Suspense fallback={fallback}>
        <div className="results-container">
          {filteredData.map((item, index) => (
            <React.Fragment key={item.id}>
              {renderItem(item, index)}
            </React.Fragment>
          ))}
        </div>
      </Suspense>
    </div>
  )
}

// 高级并发数据加载
export function AdvancedConcurrentDataLoader() {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  // 并发数据获取
  const loadData = async (endpoints: string[]) => {
    setLoading(true)
    setError(null)

    try {
      // 并发请求多个数据源
      const promises = endpoints.map(async (endpoint) => {
        const response = await fetch(endpoint)
        if (!response.ok) {
          throw new Error(`Failed to fetch ${endpoint}`)
        }
        return response.json()
      })

      // 等待所有请求完成
      const results = await Promise.allSettled(promises)

      // 处理结果
      const successfulResults = results
        .filter((result): result is PromiseFulfilledResult<any> => result.status === 'fulfilled')
        .map(result => result.value)

      const failedResults = results.filter((result): result is PromiseRejectedResult => result.status === 'rejected')

      if (failedResults.length > 0) {
        console.warn('Some requests failed:', failedResults)
      }

      startTransition(() => {
        setData(successfulResults.flat())
      })
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="advanced-concurrent-loader">
      <button onClick={() => loadData(['/api/data1', '/api/data2', '/api/data3'])}>
        Load Data Concurrently
      </button>

      {loading && <div>Loading data...</div>}
      {error && <div>Error: {error.message}</div>}

      <Suspense fallback={<div>Rendering data...</div>}>
        <ConcurrentRenderer
          data={data}
          renderItem={(item, index) => (
            <div key={item.id} className="data-item">
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </div>
          )}
        />
      </Suspense>
    </div>
  )
}
```

### 🎯 Server Components 并发优化

```typescript
// app/components/ConcurrentServerComponent.tsx
import { cache } from 'react'

// 缓存数据获取函数
const getCachedData = cache(async (id: string) => {
  const response = await fetch(`https://api.example.com/data/${id}`)
  if (!response.ok) {
    throw new Error('Failed to fetch data')
  }
  return response.json()
})

// 并发服务器组件
async function ConcurrentServerComponent({ ids }: { ids: string[] }) {
  // 并发获取数据
  const dataPromises = ids.map(id => getCachedData(id))
  const results = await Promise.all(dataPromises)

  return (
    <div className="concurrent-server-component">
      {results.map((data, index) => (
        <ServerDataItem key={data.id} data={data} index={index} />
      ))}
    </div>
  )
}

// 服务器数据项组件
async function ServerDataItem({ data, index }: { data: any; index: number }) {
  // 模拟延迟
  await new Promise(resolve => setTimeout(resolve, Math.random() * 1000))

  return (
    <div className="server-data-item" style={{ animationDelay: `${index * 0.1}s` }}>
      <h3>{data.title}</h3>
      <p>{data.description}</p>
      <small>Loaded at: {new Date().toLocaleTimeString()}</small>
    </div>
  )
}

// 流式渲染组件
export function StreamingComponent() {
  return (
    <div className="streaming-container">
      <Suspense fallback={<div>Loading section 1...</div>}>
        <AsyncSection1 />
      </Suspense>

      <Suspense fallback={<div>Loading section 2...</div>}>
        <AsyncSection2 />
      </Suspense>

      <Suspense fallback={<div>Loading section 3...</div>}>
        <AsyncSection3 />
      </Suspense>
    </div>
  )
}

async function AsyncSection1() {
  const data = await fetch('https://api.example.com/section1').then(r => r.json())
  return <section>{data.content}</section>
}

async function AsyncSection2() {
  const data = await fetch('https://api.example.com/section2').then(r => r.json())
  return <section>{data.content}</section>
}

async function AsyncSection3() {
  const data = await fetch('https://api.example.com/section3').then(r => r.json())
  return <section>{data.content}</section>
}
```

## 🚀 高级缓存策略

### 📊 多层级缓存系统

```typescript
// app/lib/advanced-cache-manager.ts
interface CacheConfig {
  ttl: number
  maxSize: number
  strategy: 'lru' | 'fifo' | 'lfu'
}

class AdvancedCacheManager {
  private memoryCache: Map<string, CacheEntry>
  private cacheConfig: CacheConfig
  private accessOrder: string[] = []
  private accessCount: Map<string, number> = new Map()

  constructor(config: CacheConfig) {
    this.cacheConfig = config
    this.memoryCache = new Map()
    this.setupCacheCleanup()
  }

  // 设置缓存
  async set(key: string, value: any, customTTL?: number): Promise<void> {
    const ttl = customTTL || this.cacheConfig.ttl
    const entry: CacheEntry = {
      value,
      timestamp: Date.now(),
      ttl,
      accessCount: 1
    }

    // 检查缓存大小限制
    if (this.memoryCache.size >= this.cacheConfig.maxSize) {
      this.evictCache()
    }

    this.memoryCache.set(key, entry)
    this.updateAccessOrder(key)
    this.accessCount.set(key, 1)

    // 异步持久化到localStorage
    this.persistToStorage(key, entry)
  }

  // 获取缓存
  async get(key: string): Promise<any | null> {
    // 先从内存缓存获取
    let entry = this.memoryCache.get(key)

    if (entry) {
      if (this.isExpired(entry)) {
        this.memoryCache.delete(key)
        this.accessOrder = this.accessOrder.filter(k => k !== key)
        this.accessCount.delete(key)
        return null
      }

      // 更新访问信息
      entry.accessCount++
      this.updateAccessOrder(key)
      this.accessCount.set(key, entry.accessCount)

      return entry.value
    }

    // 从localStorage获取
    entry = await this.getFromStorage(key)
    if (entry && !this.isExpired(entry)) {
      // 重新加载到内存缓存
      this.memoryCache.set(key, entry)
      this.updateAccessOrder(key)
      this.accessCount.set(key, 1)
      return entry.value
    }

    return null
  }

  // 缓存淘汰策略
  private evictCache() {
    switch (this.cacheConfig.strategy) {
      case 'lru':
        this.evictLRU()
        break
      case 'lfu':
        this.evictLFU()
        break
      case 'fifo':
        this.evictFIFO()
        break
    }
  }

  private evictLRU() {
    const lruKey = this.accessOrder[0]
    if (lruKey) {
      this.memoryCache.delete(lruKey)
      this.accessOrder.shift()
      this.accessCount.delete(lruKey)
      this.removeFromStorage(lruKey)
    }
  }

  private evictLFU() {
    let lfuKey: string | null = null
    let minAccessCount = Infinity

    for (const [key, count] of this.accessCount) {
      if (count < minAccessCount) {
        minAccessCount = count
        lfuKey = key
      }
    }

    if (lfuKey) {
      this.memoryCache.delete(lfuKey)
      this.accessOrder = this.accessOrder.filter(k => k !== lfuKey)
      this.accessCount.delete(lfuKey)
      this.removeFromStorage(lfuKey)
    }
  }

  private evictFIFO() {
    const firstKey = this.accessOrder[0]
    if (firstKey) {
      this.memoryCache.delete(firstKey)
      this.accessOrder.shift()
      this.accessCount.delete(firstKey)
      this.removeFromStorage(firstKey)
    }
  }

  private updateAccessOrder(key: string) {
    this.accessOrder = this.accessOrder.filter(k => k !== key)
    this.accessOrder.push(key)
  }

  private isExpired(entry: CacheEntry): boolean {
    return Date.now() - entry.timestamp > entry.ttl
  }

  private async persistToStorage(key: string, entry: CacheEntry) {
    try {
      const storageKey = `cache_${key}`
      localStorage.setItem(storageKey, JSON.stringify(entry))
    } catch (error) {
      console.warn('Failed to persist cache to storage:', error)
    }
  }

  private async getFromStorage(key: string): Promise<CacheEntry | null> {
    try {
      const storageKey = `cache_${key}`
      const item = localStorage.getItem(storageKey)
      return item ? JSON.parse(item) : null
    } catch (error) {
      console.warn('Failed to get cache from storage:', error)
      return null
    }
  }

  private removeFromStorage(key: string) {
    try {
      const storageKey = `cache_${key}`
      localStorage.removeItem(storageKey)
    } catch (error) {
      console.warn('Failed to remove cache from storage:', error)
    }
  }

  private setupCacheCleanup() {
    // 定期清理过期缓存
    setInterval(() => {
      for (const [key, entry] of this.memoryCache) {
        if (this.isExpired(entry)) {
          this.memoryCache.delete(key)
          this.accessOrder = this.accessOrder.filter(k => k !== key)
          this.accessCount.delete(key)
        }
      }
    }, 60000) // 每分钟清理一次
  }

  // 缓存统计
  getStats() {
    return {
      size: this.memoryCache.size,
      maxSize: this.cacheConfig.maxSize,
      hitRate: this.calculateHitRate(),
      memoryUsage: this.calculateMemoryUsage()
    }
  }

  private calculateHitRate(): number {
    // 实现命中率计算逻辑
    return 0 // 占位符
  }

  private calculateMemoryUsage(): number {
    // 实现内存使用计算逻辑
    return 0 // 占位符
  }
}

interface CacheEntry {
  value: any
  timestamp: number
  ttl: number
  accessCount: number
}

// 分布式缓存管理器
export class DistributedCacheManager extends AdvancedCacheManager {
  private redisClient: any // Redis客户端

  constructor(config: CacheConfig, redisClient?: any) {
    super(config)
    this.redisClient = redisClient
  }

  async setWithDistributedSync(key: string, value: any, customTTL?: number) {
    // 设置本地缓存
    await this.set(key, value, customTTL)

    // 同步到Redis
    if (this.redisClient) {
      try {
        await this.redisClient.setex(key, customTTL || this.cacheConfig.ttl, JSON.stringify(value))
      } catch (error) {
        console.warn('Failed to sync to Redis:', error)
      }
    }
  }

  async getWithDistributedSync(key: string): Promise<any | null> {
    // 先从本地缓存获取
    let value = await this.get(key)

    if (value) {
      return value
    }

    // 从Redis获取
    if (this.redisClient) {
      try {
        const redisValue = await this.redisClient.get(key)
        if (redisValue) {
          value = JSON.parse(redisValue)
          // 回写到本地缓存
          await this.set(key, value)
        }
      } catch (error) {
        console.warn('Failed to get from Redis:', error)
      }
    }

    return value
  }
}

// 使用示例
export const apiCache = new AdvancedCacheManager({
  ttl: 5 * 60 * 1000, // 5分钟
  maxSize: 100,        // 最大100个条目
  strategy: 'lru'      // LRU淘汰策略
})
```

### 🎯 智能预加载系统

```typescript
// app/lib/smart-preloader.ts
class SmartPreloader {
  private preloadedResources: Set<string> = new Set()
  private preloadQueue: Array<() => Promise<void>> = []
  private isPreloading = false

  constructor() {
    this.setupIntersectionObserver()
    this.setupIdleCallback()
  }

  // 智能预加载决策
  shouldPreload(resource: PreloadResource): boolean {
    // 检查网络状况
    const connection = (navigator as any).connection
    if (connection) {
      const isSlowConnection = connection.effectiveType === 'slow-2g' ||
                              connection.effectiveType === '2g' ||
                              connection.saveData

      if (isSlowConnection && !resource.priority) {
        return false
      }
    }

    // 检查设备内存
    if ('deviceMemory' in navigator && (navigator as any).deviceMemory < 4) {
      if (!resource.priority) {
        return false
      }
    }

    // 检查电池状态
    if ('getBattery' in navigator) {
      (navigator as any).getBattery().then((battery: any) => {
        if (battery.level < 0.2 && !battery.charging && !resource.priority) {
          return false
        }
      })
    }

    return true
  }

  // 添加预加载任务
  addPreloadTask(resource: PreloadResource) {
    if (!this.shouldPreload(resource)) {
      return
    }

    const task = () => this.preloadResource(resource)

    if (resource.priority === 'high') {
      // 高优先级立即执行
      this.executeTask(task)
    } else {
      // 低优先级加入队列
      this.preloadQueue.push(task)
      this.processQueue()
    }
  }

  // 预加载资源
  private async preloadResource(resource: PreloadResource) {
    if (this.preloadedResources.has(resource.url)) {
      return
    }

    try {
      switch (resource.type) {
        case 'image':
          await this.preloadImage(resource)
          break
        case 'script':
          await this.preloadScript(resource)
          break
        case 'style':
          await this.preloadStyle(resource)
          break
        case 'font':
          await this.preloadFont(resource)
          break
        case 'data':
          await this.preloadData(resource)
          break
      }

      this.preloadedResources.add(resource.url)
    } catch (error) {
      console.warn('Failed to preload resource:', resource.url, error)
    }
  }

  private async preloadImage(resource: PreloadResource) {
    const img = new Image()
    img.src = resource.url

    return new Promise((resolve, reject) => {
      img.onload = resolve
      img.onerror = reject
    })
  }

  private async preloadScript(resource: PreloadResource) {
    const link = document.createElement('link')
    link.rel = 'preload'
    link.as = 'script'
    link.href = resource.url

    if (resource.integrity) {
      link.integrity = resource.integrity
    }

    document.head.appendChild(link)
  }

  private async preloadStyle(resource: PreloadResource) {
    const link = document.createElement('link')
    link.rel = 'preload'
    link.as = 'style'
    link.href = resource.url
    document.head.appendChild(link)
  }

  private async preloadFont(resource: PreloadResource) {
    const link = document.createElement('link')
    link.rel = 'preload'
    link.as = 'font'
    link.type = 'font/woff2'
    link.crossOrigin = 'anonymous'
    link.href = resource.url
    document.head.appendChild(link)
  }

  private async preloadData(resource: PreloadResource) {
    await fetch(resource.url, {
      method: 'GET',
      headers: resource.headers || {},
      cache: 'force-cache'
    })
  }

  // 处理预加载队列
  private async processQueue() {
    if (this.isPreloading || this.preloadQueue.length === 0) {
      return
    }

    this.isPreloading = true

    while (this.preloadQueue.length > 0) {
      const task = this.preloadQueue.shift()!
      await this.executeTask(task)
    }

    this.isPreloading = false
  }

  private async executeTask(task: () => Promise<void>) {
    try {
      await task()
    } catch (error) {
      console.warn('Preload task failed:', error)
    }
  }

  // 设置空闲时间预加载
  private setupIdleCallback() {
    if ('requestIdleCallback' in window) {
      (window as any).requestIdleCallback(() => {
        this.processQueue()
      })
    } else {
      // 回退方案
      setTimeout(() => {
        this.processQueue()
      }, 100)
    }
  }

  // 设置视口交集观察器
  private setupIntersectionObserver() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const element = entry.target as HTMLElement
          const preloadUrl = element.dataset.preload

          if (preloadUrl) {
            this.addPreloadTask({
              url: preloadUrl,
              type: element.dataset.preloadType as PreloadResource['type'] || 'data',
              priority: 'medium'
            })
          }
        }
      })
    }, {
      rootMargin: '50px' // 提前50px开始预加载
    })

    // 观察带有data-preload属性的元素
    document.querySelectorAll('[data-preload]').forEach(element => {
      observer.observe(element)
    })
  }

  // 预加载下一页面的资源
  preloadNextPageResources(nextPageUrl: string) {
    // 基于当前页面模式预测下一页面的资源
    const commonResources = [
      { url: '/api/navigation', type: 'data' as const, priority: 'high' as const },
      { url: '/styles/common.css', type: 'style' as const, priority: 'high' as const },
      { url: '/images/hero-bg.webp', type: 'image' as const, priority: 'medium' as const }
    ]

    commonResources.forEach(resource => {
      this.addPreloadTask(resource)
    })
  }
}

interface PreloadResource {
  url: string
  type: 'image' | 'script' | 'style' | 'font' | 'data'
  priority?: 'high' | 'medium' | 'low'
  integrity?: string
  headers?: Record<string, string>
}

// 全局智能预加载器
export const smartPreloader = new SmartPreloader()
```

## 🌐 网络层优化

### ⚡ 请求优化和批处理

```typescript
// app/lib/network-optimizer.ts
class NetworkOptimizer {
  private requestQueue: Map<string, QueuedRequest> = new Map()
  private batchConfig: BatchConfig
  private activeRequests: Map<string, Promise<any>> = new Map()

  constructor(config: BatchConfig) {
    this.batchConfig = config
    this.setupBatchProcessor()
  }

  // 批量请求处理
  async batchRequest<T>(requests: BatchRequest<T>[]): Promise<T[]> {
    const batchKey = this.generateBatchKey(requests)

    // 检查是否有相同的批量请求正在进行
    if (this.activeRequests.has(batchKey)) {
      return this.activeRequests.get(batchKey)
    }

    const batchPromise = this.processBatchRequest(requests)
    this.activeRequests.set(batchKey, batchPromise)

    try {
      const result = await batchPromise
      return result
    } finally {
      this.activeRequests.delete(batchKey)
    }
  }

  private async processBatchRequest<T>(requests: BatchRequest<T>[]): Promise<T[]> {
    // 根据请求类型选择批处理策略
    const batchedRequests = this.groupRequestsByType(requests)
    const results: T[] = []

    for (const [type, typeRequests] of batchedRequests) {
      switch (type) {
        case 'graphql':
          const graphqlResults = await this.batchGraphQLRequests(typeRequests)
          results.push(...graphqlResults)
          break
        case 'rest':
          const restResults = await this.batchRESTRequests(typeRequests)
          results.push(...restResults)
          break
        case 'fetch':
          const fetchResults = await this.batchFetchRequests(typeRequests)
          results.push(...fetchResults)
          break
      }
    }

    return results
  }

  private async batchGraphQLRequests<T>(requests: BatchRequest<T>[]): Promise<T[]> {
    // 合并GraphQL查询
    const batchedQuery = this.combineGraphQLQueries(requests)

    try {
      const response = await fetch('/api/graphql', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...this.batchConfig.headers
        },
        body: JSON.stringify({ query: batchedQuery })
      })

      if (!response.ok) {
        throw new Error('GraphQL batch request failed')
      }

      const result = await response.json()
      return this.extractGraphQLResults(result, requests)
    } catch (error) {
      console.error('GraphQL batch request error:', error)
      throw error
    }
  }

  private async batchRESTRequests<T>(requests: BatchRequest<T>[]): Promise<T[]> {
    // 使用multipart/mixed批量REST请求
    const boundary = '----formdata-batch-' + Math.random().toString(36)
    const body = this.createMultipartBody(requests, boundary)

    try {
      const response = await fetch('/api/batch', {
        method: 'POST',
        headers: {
          'Content-Type': `multipart/mixed; boundary=${boundary}`,
          ...this.batchConfig.headers
        },
        body
      })

      if (!response.ok) {
        throw new Error('REST batch request failed')
      }

      return this.parseMultipartResponse(response, boundary)
    } catch (error) {
      console.error('REST batch request error:', error)
      throw error
    }
  }

  private combineGraphQLQueries<T>(requests: BatchRequest<T>[]): string {
    // 合并多个GraphQL查询为一个批量查询
    return requests.map((req, index) => {
      return `${req.operationName}: ${req.query}`
    }).join('\n')
  }

  private extractGraphQLResults<T>(result: any, requests: BatchRequest<T>[]): T[] {
    // 从GraphQL批量响应中提取各个请求的结果
    return requests.map(req => {
      const operationResult = result.data[req.operationName]
      return operationResult || null
    })
  }

  // 请求重试机制
  async requestWithRetry<T>(
    requestFn: () => Promise<T>,
    options: RetryOptions = {}
  ): Promise<T> {
    const {
      maxRetries = 3,
      retryDelay = 1000,
      backoffMultiplier = 2,
      retryCondition = (error: any) => true
    } = options

    let lastError: any

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        return await requestFn()
      } catch (error) {
        lastError = error

        if (attempt === maxRetries || !retryCondition(error)) {
          throw error
        }

        const delay = retryDelay * Math.pow(backoffMultiplier, attempt)
        await this.sleep(delay)
      }
    }

    throw lastError
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  // 设置批量处理器
  private setupBatchProcessor() {
    setInterval(() => {
      this.processBatchQueue()
    }, this.batchConfig.batchInterval)
  }

  private async processBatchQueue() {
    if (this.requestQueue.size === 0) {
      return
    }

    const requests = Array.from(this.requestQueue.values())
    this.requestQueue.clear()

    try {
      await this.batchRequest(requests)
    } catch (error) {
      console.error('Batch processing error:', error)
      // 重新加入队列进行重试
      requests.forEach(request => {
        if (request.retryCount < this.batchConfig.maxRetries) {
          request.retryCount++
          this.requestQueue.set(request.key, request)
        }
      })
    }
  }

  private generateBatchKey<T>(requests: BatchRequest<T>[]): string {
    return requests
      .map(req => `${req.type}:${req.url || req.endpoint}`)
      .sort()
      .join('|')
  }

  private groupRequestsByType<T>(requests: BatchRequest<T>[]): Map<string, BatchRequest<T>[]> {
    const grouped = new Map<string, BatchRequest<T>[]>()

    requests.forEach(req => {
      const type = req.type
      if (!grouped.has(type)) {
        grouped.set(type, [])
      }
      grouped.get(type)!.push(req)
    })

    return grouped
  }
}

interface BatchConfig {
  maxBatchSize: number
  batchInterval: number
  headers: Record<string, string>
  maxRetries: number
}

interface BatchRequest<T> {
  key: string
  type: 'graphql' | 'rest' | 'fetch'
  url?: string
  endpoint?: string
  query?: string
  operationName?: string
  variables?: any
  retryCount?: number
}

interface QueuedRequest extends BatchRequest<any> {
  timestamp: number
  retryCount: number
}

interface RetryOptions {
  maxRetries?: number
  retryDelay?: number
  backoffMultiplier?: number
  retryCondition?: (error: any) => boolean
}

// 网络优化实例
export const networkOptimizer = new NetworkOptimizer({
  maxBatchSize: 10,
  batchInterval: 100,
  headers: {
    'Accept': 'application/json',
    'Cache-Control': 'max-age=300'
  },
  maxRetries: 3
})
```

## 🔄 文档交叉引用

### 相关文档
- 📄 **[Core Web Vitals优化](./01-core-web-vitals.md)**: 深入了解性能指标优化策略
- 📄 **[性能测试指南](../../testing/04-performance-testing.md)**: 掌握性能测试和分析方法
- 📄 **[渲染优化策略](../knowledge-points/performance-optimization/01-rendering-optimization.md)**: 学习SSR/SSG/ISR优化技术
- 📄 **[打包优化技术](../knowledge-points/performance-optimization/02-bundle-optimization.md)**: 深入了解代码分割和Bundle优化

### 参考章节
- 📖 **[本模块其他章节]**: [Web安全最佳实践](../security/01-security-best-practices.md)中的性能安全考量
- 📖 **[其他模块相关内容]**: [监控和分析](../../deployment/04-monitoring-analytics.md)中的性能监控实践

## 📝 总结

### 核心要点回顾
1. **内存管理优化**: 内存泄漏检测、组件级优化、自动清理机制
2. **React 19并发优化**: Concurrent Features深度应用、Server Components并发渲染
3. **高级缓存策略**: 多层级缓存系统、智能预加载、分布式缓存
4. **网络层优化**: 请求批处理、重试机制、智能预加载决策
5. **生产级优化**: 性能监控、自动优化、持续改进流程

### 学习成果检查
- [ ] 是否掌握了高级内存管理和垃圾回收优化技术？
- [ ] 是否能够实施React 19并发特性的性能优化？
- [ ] 是否建立了多层级缓存体系和智能预加载机制？
- [ ] 是否实现了网络层优化和资源加载策略？
- [ ] 是否具备了构建生产级性能优化系统的能力？

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

### 📖 官方文档
- 📚 **[React 19并发文档](https://react.dev/learn/concurrent-features)**: React并发特性完整指南
- ⚡ **[Next.js性能优化](https://nextjs.org/docs/advanced-features/measuring-performance)**: Next.js官方性能优化文档
- 🎯 **[Web性能最佳实践](https://web.dev/fast/)**: Google Web性能优化指南

### 🛠️ 工具和库
- 🔍 **[Chrome DevTools Memory](https://developer.chrome.com/docs/devtools/memory/)**: 内存分析工具
- 📊 **[React DevTools Profiler](https://react.dev/learn/react-developer-tools#profiler)**: React性能分析工具
- 🚀 **[Bundle Analyzer](https://webpack.js.org/analysis/)**: Bundle分析工具

### 📱 性能参考
- 📈 **[内存管理最佳实践](https://web.dev/memory-management/)**: Web内存管理指南
- 🎯 **[并发模式指南](https://react.dev/learn/concurrent-rendering)**: React并发渲染深度指南
- 🔧 **[缓存策略设计](https://web.dev/http-caching/)**: HTTP缓存策略最佳实践

---

**文档状态**: ✅ 已完成 | 🚧 进行中 | 📋 计划中
**最后更新**: 2025年10月
**版本**: v1.0.0