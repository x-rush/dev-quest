# Advanced Caching - Next.js 15 现代缓存策略与实践

## 📋 概述

Advanced Caching 是现代前端性能优化的关键策略。Next.js 15 提供了强大的缓存API和工具，包括数据缓存、路由缓存、静态资源缓存等。本文将深入探讨如何在 Next.js 15 项目中实施全面的高级缓存策略。

## 🎯 缓存策略基础

### 1. 缓存类型对比

```typescript
// types/caching-strategies.ts
export type CacheType =
  | 'data-cache'         // 数据缓存
  | 'route-cache'        // 路由缓存
  | 'static-cache'       // 静态资源缓存
  | 'client-cache'       // 客户端缓存
  | 'edge-cache'         // 边缘缓存
  | 'browser-cache'      // 浏览器缓存
  | 'cdn-cache'          // CDN缓存

export interface CacheStrategy {
  type: CacheType;
  description: string;
  ttl: number; // Time To Live (seconds)
  granularity: 'global' | 'user' | 'request';
  invalidation: 'manual' | 'automatic' | 'time-based';
  useCases: string[];
}

export const cacheStrategies: CacheStrategy[] = [
  {
    type: 'data-cache',
    description: '缓存数据库查询和API响应',
    ttl: 3600,
    granularity: 'global',
    invalidation: 'automatic',
    useCases: ['静态数据', '用户配置', '产品信息']
  },
  {
    type: 'route-cache',
    description: '缓存页面路由和渲染结果',
    ttl: 7200,
    granularity: 'global',
    invalidation: 'time-based',
    useCases: ['静态页面', '博客文章', '产品页面']
  },
  {
    type: 'static-cache',
    description: '缓存CSS、JS、图片等静态资源',
    ttl: 86400,
    granularity: 'global',
    invalidation: 'time-based',
    useCases: ['样式文件', '脚本文件', '图片资源']
  },
  {
    type: 'client-cache',
    description: '客户端内存中的缓存',
    ttl: 1800,
    granularity: 'user',
    invalidation: 'manual',
    useCases: ['用户数据', '表单状态', 'UI状态']
  },
  {
    type: 'edge-cache',
    description: '边缘网络缓存',
    ttl: 300,
    granularity: 'request',
    invalidation: 'automatic',
    useCases: ['个性化内容', 'A/B测试', '地理位置数据']
  },
  {
    type: 'browser-cache',
    description: '浏览器本地缓存',
    ttl: 86400,
    granularity: 'user',
    invalidation: 'time-based',
    useCases: ['静态资源', 'API响应', '离线数据']
  },
  {
    type: 'cdn-cache',
    description: 'CDN节点缓存',
    ttl: 3600,
    granularity: 'global',
    invalidation: 'manual',
    useCases: ['全球用户', '大型文件', '热门内容']
  }
];
```

### 2. 缓存配置管理

```typescript
// lib/cache-manager.ts
import { unstable_cache } from 'next/cache';
import { CacheStrategy } from '@/types/caching-strategies';

export interface CacheConfig {
  data: {
    defaultTTL: number;
    tags: string[];
    revalidate: number;
  };
  route: {
    defaultTTL: number;
    dynamicRoutes: string[];
    staticRoutes: string[];
  };
  static: {
    maxAge: number;
    sMaxAge: number;
    immutable: boolean;
  };
  client: {
    maxSize: number;
    ttl: number;
    strategies: 'memory' | 'localstorage' | 'indexeddb';
  };
}

export const defaultCacheConfig: CacheConfig = {
  data: {
    defaultTTL: 3600,
    tags: ['default'],
    revalidate: 3600
  },
  route: {
    defaultTTL: 7200,
    dynamicRoutes: ['/products/[id]', '/users/[id]', '/posts/[slug]'],
    staticRoutes: ['/', '/about', '/contact']
  },
  static: {
    maxAge: 86400,
    sMaxAge: 86400,
    immutable: true
  },
  client: {
    maxSize: 100, // MB
    ttl: 1800,
    strategies: 'memory'
  }
};

export class CacheManager {
  private config: CacheConfig;

  constructor(config: CacheConfig = defaultCacheConfig) {
    this.config = config;
  }

  // 数据缓存包装器
  createDataCache<T>(
    key: string,
    fetchFn: () => Promise<T>,
    options?: {
      ttl?: number;
      tags?: string[];
      revalidate?: number;
    }
  ): () => Promise<T> {
    const cacheKey = `data:${key}`;
    const ttl = options?.ttl || this.config.data.defaultTTL;
    const tags = options?.tags || this.config.data.tags;
    const revalidate = options?.revalidate || this.config.data.revalidate;

    return unstable_cache(fetchFn, [cacheKey], {
      ttl: ttl * 1000,
      tags: tags,
      revalidate: revalidate
    });
  }

  // 路由缓存包装器
  createRouteCache(
    path: string,
    options?: {
      ttl?: number;
      revalidate?: number;
    }
  ): void {
    const isDynamic = this.config.route.dynamicRoutes.some(route =>
      this.isDynamicRoute(path, route)
    );

    if (isDynamic) {
      // 动态路由使用ISR
      this.setRouteRevalidate(path, options?.revalidate || this.config.route.defaultTTL);
    } else {
      // 静态路由完全缓存
      this.setStaticRouteCache(path);
    }
  }

  private isDynamicRoute(path: string, routePattern: string): boolean {
    const regexPattern = routePattern
      .replace(/\[.*?\]/g, '([^/]+)')
      .replace(/\//g, '\\/');

    const regex = new RegExp(`^${regexPattern}$`);
    return regex.test(path);
  }

  private setRouteRevalidate(path: string, revalidate: number): void {
    // 在Next.js中，这通常通过文件系统配置
    console.log(`Setting ISR for ${path} with revalidate: ${revalidate}s`);
  }

  private setStaticRouteCache(path: string): void {
    console.log(`Setting static cache for ${path}`);
  }

  // 缓存失效
  async invalidateCache(tags: string[]): Promise<void> {
    const { revalidateTag } = await import('next/cache');

    for (const tag of tags) {
      revalidateTag(tag);
    }

    console.log(`Cache invalidated for tags: ${tags.join(', ')}`);
  }

  // 缓存统计
  getCacheStats(): CacheStats {
    // 简化实现，实际应该从缓存系统获取
    return {
      totalKeys: 0,
      hitRate: 0,
      missRate: 0,
      size: 0,
      expiredKeys: 0
    };
  }

  // 缓存清理
  async clearCache(pattern?: string): Promise<void> {
    if (pattern) {
      console.log(`Clearing cache matching pattern: ${pattern}`);
    } else {
      console.log('Clearing all cache');
    }

    // 实际实现需要调用缓存系统的清理API
  }
}

interface CacheStats {
  totalKeys: number;
  hitRate: number;
  missRate: number;
  size: number; // in bytes
  expiredKeys: number;
}
```

## 🚀 数据缓存策略

### 1. 高级数据缓存实现

```typescript
// lib/advanced-data-cache.ts
import { unstable_cache } from 'next/cache';
import { CacheManager } from './cache-manager';

export interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
  version: string;
  metadata: Record<string, any>;
}

export class AdvancedDataCache<T> {
  private cacheManager: CacheManager;
  private prefix: string;
  private defaultTTL: number;
  private version: string;

  constructor(
    prefix: string,
    options: {
      defaultTTL?: number;
      version?: string;
    } = {}
  ) {
    this.cacheManager = new CacheManager();
    this.prefix = prefix;
    this.defaultTTL = options.defaultTTL || 3600;
    this.version = options.version || '1.0.0';
  }

  // 带有版本控制的缓存
  async get(
    key: string,
    fetchFn: () => Promise<T>,
    options?: {
      ttl?: number;
      tags?: string[];
      forceRefresh?: boolean;
      staleWhileRevalidate?: boolean;
    }
  ): Promise<T> {
    const fullKey = `${this.prefix}:${key}`;
    const cacheTags = options?.tags || [this.prefix];
    const ttl = options?.ttl || this.defaultTTL;

    if (options?.forceRefresh) {
      await this.cacheManager.invalidateCache(cacheTags);
    }

    if (options?.staleWhileRevalidate) {
      return this.getWithStaleWhileRevalidate(fullKey, fetchFn, { ttl, tags: cacheTags });
    }

    const cachedFetchFn = this.cacheManager.createDataCache(
      fullKey,
      fetchFn,
      { ttl, tags: cacheTags }
    );

    return cachedFetchFn();
  }

  // Stale-While-Revalidate 模式
  private async getWithStaleWhileRevalidate(
    key: string,
    fetchFn: () => Promise<T>,
    options: { ttl: number; tags: string[] }
  ): Promise<T> {
    try {
      // 尝试从缓存获取
      const cachedFetchFn = this.cacheManager.createDataCache(
        key,
        fetchFn,
        options
      );

      return await cachedFetchFn();
    } catch (error) {
      // 缓存失败，直接获取
      console.warn('Cache miss, fetching fresh data:', error);
      return fetchFn();
    }
  }

  // 分页数据缓存
  async getPaginatedData(
    key: string,
    page: number,
    limit: number,
    fetchFn: (page: number, limit: number) => Promise<{ data: T[]; total: number }>,
    options?: {
      ttl?: number;
      prefetchNext?: boolean;
    }
  ): Promise<{ data: T[]; total: number; hasNext: boolean }> {
    const cacheKey = `${key}:page:${page}:limit:${limit}`;
    const result = await this.get(cacheKey, () => fetchFn(page, limit), {
      ttl: options?.ttl
    });

    const hasNext = result.total > page * limit;

    // 预取下一页
    if (options?.prefetchNext && hasNext) {
      this.prefetchPage(key, page + 1, limit, fetchFn);
    }

    return {
      data: result.data,
      total: result.total,
      hasNext
    };
  }

  private async prefetchPage(
    key: string,
    page: number,
    limit: number,
    fetchFn: (page: number, limit: number) => Promise<{ data: T[]; total: number }>
  ): Promise<void> {
    try {
      const cacheKey = `${key}:page:${page}:limit:${limit}`;
      await this.get(cacheKey, () => fetchFn(page, limit), {
        ttl: this.defaultTTL
      });
    } catch (error) {
      console.warn('Failed to prefetch page:', error);
    }
  }

  // 实时数据缓存
  createRealtimeCache(
    key: string,
    fetchFn: () => Promise<T>,
    options: {
      ttl?: number;
      updateInterval?: number;
    } = {}
  ): {
    getCurrent: () => Promise<T>;
    subscribe: (callback: (data: T) => void) => () => void;
  } {
    const ttl = options.ttl || this.defaultTTL;
    const updateInterval = options.updateInterval || 30000; // 30秒
    const subscribers = new Set<(data: T) => void>();

    // 定时更新数据
    const updateData = async () => {
      try {
        const freshData = await this.get(key, fetchFn, {
          ttl,
          forceRefresh: true
        });

        subscribers.forEach(callback => callback(freshData));
      } catch (error) {
        console.error('Failed to update realtime data:', error);
      }
    };

    // 启动定时更新
    const intervalId = setInterval(updateData, updateInterval);

    return {
      getCurrent: () => this.get(key, fetchFn, { ttl }),
      subscribe: (callback: (data: T) => void) => {
        subscribers.add(callback);

        // 返回取消订阅函数
        return () => {
          subscribers.delete(callback);
          if (subscribers.size === 0) {
            clearInterval(intervalId);
          }
        };
      }
    };
  }

  // 批量缓存操作
  async batchGet(
    keys: string[],
    fetchFn: (key: string) => Promise<T>,
    options?: { ttl?: number }
  ): Promise<Map<string, T>> {
    const results = new Map<string, T>();

    // 并行获取所有数据
    const promises = keys.map(async (key) => {
      try {
        const data = await this.get(key, () => fetchFn(key), options);
        results.set(key, data);
      } catch (error) {
        console.error(`Failed to get data for key ${key}:`, error);
      }
    });

    await Promise.all(promises);

    return results;
  }

  // 缓存预热
  async warmup(
    keys: string[],
    fetchFn: (key: string) => Promise<T>,
    options?: { ttl?: number; concurrency?: number }
  ): Promise<void> {
    const concurrency = options?.concurrency || 5;
    const ttl = options?.ttl || this.defaultTTL;

    // 分批处理以避免过载
    for (let i = 0; i < keys.length; i += concurrency) {
      const batch = keys.slice(i, i + concurrency);

      await Promise.all(
        batch.map(key =>
          this.get(key, () => fetchFn(key), { ttl })
            .catch(error => console.error(`Warmup failed for ${key}:`, error))
        )
      );

      // 批次间延迟
      if (i + concurrency < keys.length) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    }

    console.log(`Cache warmup completed for ${keys.length} keys`);
  }
}
```

### 2. 智能缓存策略

```typescript
// lib/intelligent-cache.ts
import { AdvancedDataCache } from './advanced-data-cache';

export interface CacheDecision {
  shouldCache: boolean;
  ttl: number;
  strategy: 'cache-first' | 'network-first' | 'stale-while-revalidate' | 'cache-only';
  reasoning: string[];
}

export class IntelligentCache<T> extends AdvancedDataCache<T> {
  private accessPatterns: Map<string, AccessPattern> = new Map();
  private costModel: CacheCostModel;

  constructor(prefix: string, options?: { defaultTTL?: number; version?: string }) {
    super(prefix, options);
    this.costModel = new CacheCostModel();
  }

  // 智能缓存决策
  async intelligentGet(
    key: string,
    fetchFn: () => Promise<T>,
    context?: {
      userId?: string;
      contentType?: string;
      accessFrequency?: 'high' | 'medium' | 'low';
      updateFrequency?: 'high' | 'medium' | 'low';
      cost?: number;
    }
  ): Promise<T> {
    const decision = this.makeCacheDecision(key, context);

    if (!decision.shouldCache) {
      console.log(`Cache bypass for ${key}: ${decision.reasoning.join(', ')}`);
      return fetchFn();
    }

    switch (decision.strategy) {
      case 'cache-first':
        return this.get(key, fetchFn, { ttl: decision.ttl });

      case 'network-first':
        try {
          const freshData = await fetchFn();
          await this.set(key, freshData, { ttl: decision.ttl });
          return freshData;
        } catch (error) {
          console.log('Network failed, falling back to cache:', error);
          return this.get(key, fetchFn, { ttl: decision.ttl });
        }

      case 'stale-while-revalidate':
        return this.get(key, fetchFn, {
          ttl: decision.ttl,
          staleWhileRevalidate: true
        });

      case 'cache-only':
        return this.get(key, fetchFn, { ttl: decision.ttl });

      default:
        return fetchFn();
    }
  }

  private makeCacheDecision(key: string, context?: any): CacheDecision {
    const reasoning: string[] = [];
    let shouldCache = true;
    let ttl = this.defaultTTL;
    let strategy: CacheDecision['strategy'] = 'cache-first';

    // 分析访问模式
    const pattern = this.accessPatterns.get(key) || this.analyzeAccessPattern(key);
    this.accessPatterns.set(key, pattern);

    // 基于访问频率调整
    if (pattern.frequency === 'high') {
      reasoning.push('High access frequency - good cache candidate');
      ttl = Math.max(ttl, 7200); // 增加TTL
      strategy = 'cache-first';
    } else if (pattern.frequency === 'low') {
      reasoning.push('Low access frequency - short cache');
      ttl = Math.min(ttl, 1800); // 减少TTL
    }

    // 基于更新频率调整
    if (context?.updateFrequency === 'high') {
      reasoning.push('High update frequency - network-first strategy');
      strategy = 'network-first';
      ttl = Math.min(ttl, 600); // 短TTL
    } else if (context?.updateFrequency === 'low') {
      reasoning.push('Low update frequency - long cache');
      ttl = Math.max(ttl, 14400); // 长TTL
    }

    // 基于内容类型调整
    if (context?.contentType === 'user-specific') {
      reasoning.push('User-specific content - user-level caching');
      ttl = Math.min(ttl, 3600); // 用户数据相对较短TTL
    }

    // 基于成本调整
    if (context?.cost && context.cost > 1000) { // 高成本操作
      reasoning.push('High cost operation - aggressive caching');
      ttl = Math.max(ttl, 14400);
      strategy = 'cache-first';
    }

    // 容量检查
    if (this.isCacheFull()) {
      reasoning.push('Cache capacity limit - selective caching');
      shouldCache = pattern.frequency === 'high';
    }

    return {
      shouldCache,
      ttl,
      strategy,
      reasoning
    };
  }

  private analyzeAccessPattern(key: string): AccessPattern {
    // 简化实现，实际应该基于历史访问数据
    return {
      frequency: 'medium',
      lastAccess: Date.now(),
      averageInterval: 300000, // 5分钟
      size: 1024 // 估算大小
    };
  }

  private isCacheFull(): boolean {
    // 简化实现
    return false;
  }

  private async set(key: string, data: T, options: { ttl: number }): Promise<void> {
    // 实现缓存设置逻辑
    console.log(`Setting cache for ${key} with TTL ${options.ttl}s`);
  }

  // 成本模型优化
  optimizeCacheStrategy(): void {
    const strategies = this.costModel.calculateOptimalStrategies(this.accessPatterns);

    console.log('Cache optimization recommendations:');
    strategies.forEach(rec => {
      console.log(`- ${rec.key}: ${rec.strategy} (TTL: ${rec.ttl}s)`);
    });
  }
}

interface AccessPattern {
  frequency: 'high' | 'medium' | 'low';
  lastAccess: number;
  averageInterval: number;
  size: number;
}

class CacheCostModel {
  calculateOptimalStrategies(patterns: Map<string, AccessPattern>): Array<{
    key: string;
    strategy: string;
    ttl: number;
  }> {
    const recommendations: Array<{
      key: string;
      strategy: string;
      ttl: number;
    }> = [];

    patterns.forEach((pattern, key) => {
      let strategy = 'cache-first';
      let ttl = 3600;

      if (pattern.frequency === 'high') {
        strategy = 'cache-first';
        ttl = 7200;
      } else if (pattern.frequency === 'low') {
        strategy = 'network-first';
        ttl = 1800;
      }

      recommendations.push({ key, strategy, ttl });
    });

    return recommendations;
  }
}
```

## 🎨 路由缓存优化

### 1. 路由级缓存策略

```typescript
// lib/route-cache.ts
import { NextRequest, NextResponse } from 'next/server';
import { CacheManager } from './cache-manager';

export interface RouteCacheConfig {
  path: string;
  strategy: 'static' | 'isr' | 'ssr' | 'edge';
  ttl?: number;
  revalidate?: number;
  tags?: string[];
  vary?: string[];
  conditions?: {
    userAgent?: boolean;
    locale?: boolean;
    authenticated?: boolean;
  };
}

export class RouteCacheManager {
  private cacheManager: CacheManager;
  private routeConfigs: Map<string, RouteCacheConfig> = new Map();

  constructor() {
    this.cacheManager = new CacheManager();
    this.initializeRouteConfigs();
  }

  private initializeRouteConfigs(): void {
    // 静态路由配置
    const staticRoutes: RouteCacheConfig[] = [
      {
        path: '/',
        strategy: 'static',
        ttl: 86400,
        tags: ['home']
      },
      {
        path: '/about',
        strategy: 'static',
        ttl: 86400,
        tags: ['about']
      },
      {
        path: '/contact',
        strategy: 'static',
        ttl: 86400,
        tags: ['contact']
      }
    ];

    // ISR路由配置
    const isrRoutes: RouteCacheConfig[] = [
      {
        path: '/blog/[slug]',
        strategy: 'isr',
        revalidate: 3600,
        tags: ['blog']
      },
      {
        path: '/products/[id]',
        strategy: 'isr',
        revalidate: 1800,
        tags: ['products']
      }
    ];

    // 边缘路由配置
    const edgeRoutes: RouteCacheConfig[] = [
      {
        path: '/api/user/[id]',
        strategy: 'edge',
        ttl: 300,
        vary: ['Accept-Language'],
        conditions: {
          authenticated: true
        }
      }
    ];

    [...staticRoutes, ...isrRoutes, ...edgeRoutes].forEach(config => {
      this.routeConfigs.set(config.path, config);
    });
  }

  // 中间件：路由缓存处理
  async handleRouteCache(request: NextRequest): Promise<NextResponse | null> {
    const { pathname } = request.nextUrl;

    // 查找匹配的路由配置
    const config = this.findMatchingRouteConfig(pathname);

    if (!config) {
      return null; // 无缓存配置，正常处理
    }

    switch (config.strategy) {
      case 'static':
        return this.handleStaticRoute(request, config);

      case 'isr':
        return this.handleISRRoute(request, config);

      case 'edge':
        return this.handleEdgeRoute(request, config);

      case 'ssr':
        return null; // SSR不缓存

      default:
        return null;
    }
  }

  private findMatchingRouteConfig(pathname: string): RouteCacheConfig | null {
    // 精确匹配
    if (this.routeConfigs.has(pathname)) {
      return this.routeConfigs.get(pathname)!;
    }

    // 模式匹配
    for (const [pattern, config] of this.routeConfigs.entries()) {
      if (this.pathMatchesPattern(pathname, pattern)) {
        return config;
      }
    }

    return null;
  }

  private pathMatchesPattern(pathname: string, pattern: string): boolean {
    // 简化的模式匹配
    if (pattern.includes('[id]')) {
      return /^\/[^\/]+\/[^\/]+$/.test(pathname);
    }

    if (pattern.includes('[slug]')) {
      return /^\/blog\/[^\/]+$/.test(pathname);
    }

    return false;
  }

  private async handleStaticRoute(
    request: NextRequest,
    config: RouteCacheConfig
  ): Promise<NextResponse> {
    // 生成缓存键
    const cacheKey = this.generateCacheKey(request, config);

    // 尝试从缓存获取
    const cached = await this.getFromCache(cacheKey);

    if (cached) {
      return this.createCachedResponse(cached, config);
    }

    return null; // 缓存未命中，正常处理
  }

  private async handleISRRoute(
    request: NextRequest,
    config: RouteCacheConfig
  ): Promise<NextResponse | null> {
    const cacheKey = this.generateCacheKey(request, config);

    // 检查缓存是否有效
    const cached = await this.getFromCache(cacheKey);

    if (cached && this.isCacheValid(cached, config)) {
      return this.createCachedResponse(cached, config);
    }

    // 后台重新验证
    if (cached) {
      this.revalidateInBackground(cacheKey, request);
      return this.createCachedResponse(cached, config);
    }

    return null;
  }

  private async handleEdgeRoute(
    request: NextRequest,
    config: RouteCacheConfig
  ): Promise<NextResponse | null> {
    // 边缘路由缓存逻辑
    const cacheKey = this.generateCacheKey(request, config);

    const cached = await this.getFromCache(cacheKey);

    if (cached) {
      return this.createCachedResponse(cached, config);
    }

    return null;
  }

  private generateCacheKey(request: NextRequest, config: RouteCacheConfig): string {
    const { pathname } = request.nextUrl;
    let key = pathname;

    // 添加vary头信息
    if (config.vary) {
      config.vary.forEach(header => {
        const value = request.headers.get(header);
        if (value) {
          key += `:${header}=${value}`;
        }
      });
    }

    // 添加条件信息
    if (config.conditions?.authenticated) {
      const authHeader = request.headers.get('authorization');
      if (authHeader) {
        key += `:auth=${authHeader.substring(0, 20)}`;
      }
    }

    return key;
  }

  private async getFromCache(key: string): Promise<CachedResponse | null> {
    // 从缓存系统获取响应
    // 简化实现
    return null;
  }

  private isCacheValid(cached: CachedResponse, config: RouteCacheConfig): boolean {
    const now = Date.now();
    const age = now - cached.timestamp;

    return age < (config.revalidate || config.ttl || 3600) * 1000;
  }

  private createCachedResponse(cached: CachedResponse, config: RouteCacheConfig): NextResponse {
    const response = new NextResponse(cached.body, {
      status: cached.status,
      headers: cached.headers
    });

    // 添加缓存头
    if (config.strategy === 'static') {
      response.headers.set('Cache-Control', `public, max-age=${config.ttl || 86400}, immutable`);
    } else if (config.strategy === 'isr') {
      response.headers.set('Cache-Control', `public, s-maxage=${config.revalidate || 3600}, stale-while-revalidate=60`);
    }

    return response;
  }

  private async revalidateInBackground(cacheKey: string, request: NextRequest): Promise<void> {
    // 后台重新验证逻辑
    console.log(`Revalidating cache for ${cacheKey}`);
  }

  // 缓存失效
  async invalidateRoute(path: string, params?: Record<string, string>): Promise<void> {
    const config = this.findMatchingRouteConfig(path);

    if (config && config.tags) {
      await this.cacheManager.invalidateCache(config.tags);
    }
  }

  // 获取路由缓存统计
  getRouteCacheStats(): RouteCacheStats {
    return {
      totalRoutes: this.routeConfigs.size,
      staticRoutes: Array.from(this.routeConfigs.values()).filter(c => c.strategy === 'static').length,
      isrRoutes: Array.from(this.routeConfigs.values()).filter(c => c.strategy === 'isr').length,
      edgeRoutes: Array.from(this.routeConfigs.values()).filter(c => c.strategy === 'edge').length
    };
  }
}

interface CachedResponse {
  body: string;
  status: number;
  headers: Record<string, string>;
  timestamp: number;
}

interface RouteCacheStats {
  totalRoutes: number;
  staticRoutes: number;
  isrRoutes: number;
  edgeRoutes: number;
}
```

## 🔄 客户端缓存管理

### 1. 客户端缓存实现

```typescript
// lib/client-cache.ts
export interface ClientCacheConfig {
  maxSize: number; // MB
  ttl: number; // seconds
  storage: 'memory' | 'localStorage' | 'indexedDB';
  compression: boolean;
  encryption: boolean;
}

export class ClientCacheManager {
  private config: ClientCacheConfig;
  private memoryCache: Map<string, CacheEntry<any>> = new Map();
  private storage: Storage | null = null;

  constructor(config: ClientCacheConfig) {
    this.config = config;
    this.initializeStorage();
  }

  private initializeStorage(): void {
    if (typeof window === 'undefined') return;

    switch (this.config.storage) {
      case 'localStorage':
        this.storage = localStorage;
        break;
      case 'indexedDB':
        this.initializeIndexedDB();
        break;
      case 'memory':
      default:
        // 内存缓存不需要额外初始化
        break;
    }
  }

  private async initializeIndexedDB(): Promise<void> {
    if (typeof window === 'undefined') return;

    try {
      const request = indexedDB.open('ClientCacheDB', 1);

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        if (!db.objectStoreNames.contains('cache')) {
          const store = db.createObjectStore('cache', { keyPath: 'key' });
          store.createIndex('timestamp', 'timestamp', { unique: false });
          store.createIndex('expires', 'expires', { unique: false });
        }
      };

      request.onsuccess = (event) => {
        console.log('IndexedDB initialized successfully');
      };

      request.onerror = (event) => {
        console.error('Failed to initialize IndexedDB:', event);
      };
    } catch (error) {
      console.error('IndexedDB not supported:', error);
    }
  }

  // 设置缓存
  async set<T>(
    key: string,
    data: T,
    options?: {
      ttl?: number;
      compression?: boolean;
      encryption?: boolean;
    }
  ): Promise<void> {
    const ttl = options?.ttl || this.config.ttl;
    const compression = options?.compression ?? this.config.compression;
    const encryption = options?.encryption ?? this.config.encryption;

    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      expires: Date.now() + ttl * 1000,
      metadata: {
        compression,
        encryption,
        size: this.calculateSize(data)
      }
    };

    // 处理压缩和加密
    let processedData = data;
    if (compression) {
      processedData = await this.compress(processedData);
    }
    if (encryption) {
      processedData = await this.encrypt(processedData);
    }

    entry.processedData = processedData;

    // 存储到相应的存储系统
    switch (this.config.storage) {
      case 'memory':
        this.memoryCache.set(key, entry);
        break;
      case 'localStorage':
        this.setToLocalStorage(key, entry);
        break;
      case 'indexedDB':
        await this.setToIndexedDB(key, entry);
        break;
    }

    // 清理过期缓存
    this.cleanup();
  }

  // 获取缓存
  async get<T>(key: string): Promise<T | null> {
    let entry: CacheEntry<T> | null = null;

    // 从存储系统获取
    switch (this.config.storage) {
      case 'memory':
        entry = this.memoryCache.get(key) || null;
        break;
      case 'localStorage':
        entry = this.getFromLocalStorage<T>(key);
        break;
      case 'indexedDB':
        entry = await this.getFromIndexedDB<T>(key);
        break;
    }

    if (!entry) {
      return null;
    }

    // 检查是否过期
    if (Date.now() > entry.expires) {
      await this.remove(key);
      return null;
    }

    // 解压缩和解密
    let data = entry.processedData || entry.data;
    if (entry.metadata?.encryption) {
      data = await this.decrypt(data);
    }
    if (entry.metadata?.compression) {
      data = await this.decompress(data);
    }

    return data as T;
  }

  // 删除缓存
  async remove(key: string): Promise<void> {
    switch (this.config.storage) {
      case 'memory':
        this.memoryCache.delete(key);
        break;
      case 'localStorage':
        this.storage?.removeItem(`cache_${key}`);
        break;
      case 'indexedDB':
        await this.removeFromIndexedDB(key);
        break;
    }
  }

  // 清理过期缓存
  private cleanup(): void {
    const now = Date.now();

    if (this.config.storage === 'memory') {
      for (const [key, entry] of this.memoryCache.entries()) {
        if (now > entry.expires) {
          this.memoryCache.delete(key);
        }
      }
    } else if (this.config.storage === 'localStorage' && this.storage) {
      for (let i = 0; i < this.storage.length; i++) {
        const key = this.storage.key(i);
        if (key?.startsWith('cache_')) {
          try {
            const entry = JSON.parse(this.storage.getItem(key)!);
            if (now > entry.expires) {
              this.storage.removeItem(key);
            }
          } catch (error) {
            // 忽略解析错误
          }
        }
      }
    }

    // 检查存储大小
    this.checkStorageSize();
  }

  private checkStorageSize(): void {
    if (this.config.storage === 'memory') {
      let totalSize = 0;
      for (const entry of this.memoryCache.values()) {
        totalSize += entry.metadata?.size || 0;
      }

      if (totalSize > this.config.maxSize * 1024 * 1024) {
        this.evictLRU();
      }
    }
  }

  private evictLRU(): void {
    // LRU淘汰算法
    const entries = Array.from(this.memoryCache.entries())
      .sort(([, a], [, b]) => a.timestamp - b.timestamp);

    const toRemove = Math.ceil(entries.length * 0.2); // 移除20%

    for (let i = 0; i < toRemove; i++) {
      this.memoryCache.delete(entries[i][0]);
    }
  }

  // LocalStorage 方法
  private setToLocalStorage(key: string, entry: CacheEntry<any>): void {
    if (!this.storage) return;

    try {
      this.storage.setItem(`cache_${key}`, JSON.stringify(entry));
    } catch (error) {
      console.error('Failed to set cache to localStorage:', error);
    }
  }

  private getFromLocalStorage<T>(key: string): CacheEntry<T> | null {
    if (!this.storage) return null;

    try {
      const item = this.storage.getItem(`cache_${key}`);
      return item ? JSON.parse(item) : null;
    } catch (error) {
      console.error('Failed to get cache from localStorage:', error);
      return null;
    }
  }

  // IndexedDB 方法
  private async setToIndexedDB(key: string, entry: CacheEntry<any>): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('ClientCacheDB', 1);

      request.onsuccess = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        const transaction = db.transaction(['cache'], 'readwrite');
        const store = transaction.objectStore('cache');

        const putRequest = store.put({ key, ...entry });

        putRequest.onsuccess = () => resolve();
        putRequest.onerror = () => reject(putRequest.error);
      };

      request.onerror = () => reject(request.error);
    });
  }

  private async getFromIndexedDB<T>(key: string): Promise<CacheEntry<T> | null> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('ClientCacheDB', 1);

      request.onsuccess = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        const transaction = db.transaction(['cache'], 'readonly');
        const store = transaction.objectStore('cache');

        const getRequest = store.get(key);

        getRequest.onsuccess = () => {
          const result = getRequest.result;
          resolve(result ? {
            data: result.data,
            timestamp: result.timestamp,
            expires: result.expires,
            metadata: result.metadata,
            processedData: result.processedData
          } : null);
        };

        getRequest.onerror = () => reject(getRequest.error);
      };

      request.onerror = () => reject(request.error);
    });
  }

  private async removeFromIndexedDB(key: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('ClientCacheDB', 1);

      request.onsuccess = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        const transaction = db.transaction(['cache'], 'readwrite');
        const store = transaction.objectStore('cache');

        const deleteRequest = store.delete(key);

        deleteRequest.onsuccess = () => resolve();
        deleteRequest.onerror = () => reject(deleteRequest.error);
      };

      request.onerror = () => reject(request.error);
    });
  }

  // 压缩和解压缩
  private async compress<T>(data: T): Promise<any> {
    // 简化实现，实际应该使用压缩库
    return data;
  }

  private async decompress<T>(data: any): Promise<T> {
    // 简化实现
    return data;
  }

  // 加密和解密
  private async encrypt<T>(data: T): Promise<any> {
    // 简化实现，实际应该使用加密库
    return data;
  }

  private async decrypt<T>(data: any): Promise<T> {
    // 简化实现
    return data;
  }

  private calculateSize(data: any): number {
    // 简化的大小估算
    return JSON.stringify(data).length * 2; // 估算字节大小
  }

  // 获取缓存统计
  async getStats(): Promise<ClientCacheStats> {
    let totalEntries = 0;
    let totalSize = 0;
    let hitRate = 0;

    switch (this.config.storage) {
      case 'memory':
        totalEntries = this.memoryCache.size;
        totalSize = Array.from(this.memoryCache.values())
          .reduce((sum, entry) => sum + (entry.metadata?.size || 0), 0);
        break;

      case 'localStorage':
        if (this.storage) {
          for (let i = 0; i < this.storage.length; i++) {
            const key = this.storage.key(i);
            if (key?.startsWith('cache_')) {
              totalEntries++;
              totalSize += this.storage.getItem(key)!.length * 2;
            }
          }
        }
        break;

      case 'indexedDB':
        // IndexedDB统计需要异步查询
        const stats = await this.getIndexedDBStats();
        totalEntries = stats.totalEntries;
        totalSize = stats.totalSize;
        break;
    }

    return {
      totalEntries,
      totalSize,
      hitRate,
      maxSize: this.config.maxSize * 1024 * 1024,
      storageType: this.config.storage
    };
  }

  private async getIndexedDBStats(): Promise<{ totalEntries: number; totalSize: number }> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('ClientCacheDB', 1);

      request.onsuccess = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        const transaction = db.transaction(['cache'], 'readonly');
        const store = transaction.objectStore('cache');

        const getAllRequest = store.getAll();

        getAllRequest.onsuccess = () => {
          const entries = getAllRequest.result;
          resolve({
            totalEntries: entries.length,
            totalSize: entries.reduce((sum: number, entry: any) =>
              sum + (entry.metadata?.size || 0), 0
            )
          });
        };

        getAllRequest.onerror = () => reject(getAllRequest.error);
      };

      request.onerror = () => reject(request.error);
    });
  }
}

interface CacheEntry<T> {
  data: T;
  processedData?: any;
  timestamp: number;
  expires: number;
  metadata?: {
    compression: boolean;
    encryption: boolean;
    size: number;
  };
}

interface ClientCacheStats {
  totalEntries: number;
  totalSize: number;
  hitRate: number;
  maxSize: number;
  storageType: 'memory' | 'localStorage' | 'indexedDB';
}
```

## 📊 缓存监控和分析

### 1. 缓存性能监控

```typescript
// lib/cache-monitor.ts
export interface CacheMetrics {
  hits: number;
  misses: number;
  hitRate: number;
  averageResponseTime: number;
  size: number;
  evictionCount: number;
  errorRate: number;
}

export interface CachePerformanceEvent {
  type: 'hit' | 'miss' | 'eviction' | 'error';
  key: string;
  timestamp: number;
  duration?: number;
  size?: number;
  error?: string;
}

export class CacheMonitor {
  private metrics: CacheMetrics = {
    hits: 0,
    misses: 0,
    hitRate: 0,
    averageResponseTime: 0,
    size: 0,
    evictionCount: 0,
    errorRate: 0
  };

  private events: CachePerformanceEvent[] = [];
  private responseTimes: number[] = [];
  private errorCount = 0;
  private totalOperations = 0;

  // 记录缓存事件
  recordEvent(event: Omit<CachePerformanceEvent, 'timestamp'>): void {
    const fullEvent: CachePerformanceEvent = {
      ...event,
      timestamp: Date.now()
    };

    this.events.push(fullEvent);
    this.updateMetrics(fullEvent);

    // 保持最近1000个事件
    if (this.events.length > 1000) {
      this.events = this.events.slice(-1000);
    }
  }

  private updateMetrics(event: CachePerformanceEvent): void {
    this.totalOperations++;

    switch (event.type) {
      case 'hit':
        this.metrics.hits++;
        if (event.duration) {
          this.responseTimes.push(event.duration);
        }
        break;

      case 'miss':
        this.metrics.misses++;
        break;

      case 'eviction':
        this.metrics.evictionCount++;
        break;

      case 'error':
        this.errorCount++;
        break;
    }

    // 计算命中率
    this.metrics.hitRate = this.metrics.hits / (this.metrics.hits + this.metrics.misses);

    // 计算平均响应时间
    if (this.responseTimes.length > 0) {
      const recentTimes = this.responseTimes.slice(-100); // 最近100次
      this.metrics.averageResponseTime =
        recentTimes.reduce((sum, time) => sum + time, 0) / recentTimes.length;
    }

    // 计算错误率
    this.metrics.errorRate = this.errorCount / this.totalOperations;
  }

  // 获取当前指标
  getCurrentMetrics(): CacheMetrics {
    return { ...this.metrics };
  }

  // 获取时间范围内的指标
  getMetricsInTimeRange(startTime: number, endTime: number): CacheMetrics {
    const eventsInRange = this.events.filter(
      event => event.timestamp >= startTime && event.timestamp <= endTime
    );

    const hits = eventsInRange.filter(e => e.type === 'hit').length;
    const misses = eventsInRange.filter(e => e.type === 'miss').length;
    const evictions = eventsInRange.filter(e => e.type === 'eviction').length;
    const errors = eventsInRange.filter(e => e.type === 'error').length;
    const total = eventsInRange.length;

    const hitEvents = eventsInRange.filter(e => e.type === 'hit' && e.duration);
    const averageResponseTime = hitEvents.length > 0
      ? hitEvents.reduce((sum, e) => sum + (e.duration || 0), 0) / hitEvents.length
      : 0;

    return {
      hits,
      misses,
      hitRate: total > 0 ? hits / total : 0,
      averageResponseTime,
      size: this.metrics.size,
      evictionCount: evictions,
      errorRate: total > 0 ? errors / total : 0
    };
  }

  // 获取热门键
  getHotKeys(limit: number = 10): Array<{
    key: string;
    accessCount: number;
    hitRate: number;
  }> {
    const keyStats = new Map<string, { hits: number; misses: number }>();

    this.events.forEach(event => {
      const current = keyStats.get(event.key) || { hits: 0, misses: 0 };

      if (event.type === 'hit') {
        current.hits++;
      } else if (event.type === 'miss') {
        current.misses++;
      }

      keyStats.set(event.key, current);
    });

    return Array.from(keyStats.entries())
      .map(([key, stats]) => ({
        key,
        accessCount: stats.hits + stats.misses,
        hitRate: stats.hits / (stats.hits + stats.misses)
      }))
      .sort((a, b) => b.accessCount - a.accessCount)
      .slice(0, limit);
  }

  // 获取性能趋势
  getPerformanceTrends(hours: number = 24): Array<{
    timestamp: number;
    hitRate: number;
    responseTime: number;
    operations: number;
  }> {
    const now = Date.now();
    const interval = hours * 60 * 60 * 1000 / 24; // 24个时间点
    const trends: Array<{
      timestamp: number;
      hitRate: number;
      responseTime: number;
      operations: number;
    }> = [];

    for (let i = 0; i < 24; i++) {
      const start = now - (24 - i) * interval;
      const end = start + interval;

      const metrics = this.getMetricsInTimeRange(start, end);
      const eventsInRange = this.events.filter(
        event => event.timestamp >= start && event.timestamp <= end
      );

      trends.push({
        timestamp: start,
        hitRate: metrics.hitRate,
        responseTime: metrics.averageResponseTime,
        operations: eventsInRange.length
      });
    }

    return trends;
  }

  // 生成性能报告
  generatePerformanceReport(): CachePerformanceReport {
    const currentMetrics = this.getCurrentMetrics();
    const trends = this.getPerformanceTrends();
    const hotKeys = this.getHotKeys();
    const errors = this.events.filter(e => e.type === 'error');

    return {
      timestamp: Date.now(),
      summary: currentMetrics,
      trends,
      hotKeys,
      errors: errors.slice(-10), // 最近10个错误
      recommendations: this.generateRecommendations(currentMetrics)
    };
  }

  private generateRecommendations(metrics: CacheMetrics): string[] {
    const recommendations: string[] = [];

    if (metrics.hitRate < 0.8) {
      recommendations.push('Cache hit rate is low. Consider adjusting TTL or cache keys.');
    }

    if (metrics.averageResponseTime > 100) {
      recommendations.push('Cache response time is high. Check for performance bottlenecks.');
    }

    if (metrics.evictionCount > 100) {
      recommendations.push('High eviction count detected. Consider increasing cache size.');
    }

    if (metrics.errorRate > 0.01) {
      recommendations.push('Cache error rate is high. Check cache configuration.');
    }

    return recommendations;
  }

  // 导出指标到监控系统
  async exportToMonitoring(service: 'prometheus' | 'datadog' | 'custom'): Promise<void> {
    const metrics = this.getCurrentMetrics();

    switch (service) {
      case 'prometheus':
        await this.exportToPrometheus(metrics);
        break;
      case 'datadog':
        await this.exportToDatadog(metrics);
        break;
      case 'custom':
        await this.exportToCustomService(metrics);
        break;
    }
  }

  private async exportToPrometheus(metrics: CacheMetrics): Promise<void> {
    // 导出到Prometheus格式的指标
    const prometheusMetrics = [
      `cache_hits_total ${metrics.hits}`,
      `cache_misses_total ${metrics.misses}`,
      `cache_hit_rate ${metrics.hitRate}`,
      `cache_average_response_time_ms ${metrics.averageResponseTime}`,
      `cache_evictions_total ${metrics.evictionCount}`,
      `cache_errors_total ${this.errorCount}`
    ].join('\n');

    console.log('Prometheus metrics:', prometheusMetrics);
  }

  private async exportToDatadog(metrics: CacheMetrics): Promise<void> {
    // 导出到Datadog格式的指标
    const datadogMetrics = {
      'cache.hits': metrics.hits,
      'cache.misses': metrics.misses,
      'cache.hit_rate': metrics.hitRate,
      'cache.average_response_time': metrics.averageResponseTime,
      'cache.evictions': metrics.evictionCount,
      'cache.errors': this.errorCount
    };

    console.log('Datadog metrics:', datadogMetrics);
  }

  private async exportToCustomService(metrics: CacheMetrics): Promise<void> {
    // 导出到自定义监控服务
    try {
      await fetch('/api/analytics/cache', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          timestamp: Date.now(),
          metrics
        })
      });
    } catch (error) {
      console.error('Failed to export cache metrics:', error);
    }
  }
}

interface CachePerformanceReport {
  timestamp: number;
  summary: CacheMetrics;
  trends: Array<{
    timestamp: number;
    hitRate: number;
    responseTime: number;
    operations: number;
  }>;
  hotKeys: Array<{
    key: string;
    accessCount: number;
    hitRate: number;
  }>;
  errors: CachePerformanceEvent[];
  recommendations: string[];
}
```

## 🎯 最佳实践和总结

### 1. 缓存策略检查清单

```typescript
// checklists/caching-best-practices.ts
export const cachingBestPracticesChecklist = [
  {
    category: '数据缓存',
    items: [
      '合理设置TTL，避免过长或过短',
      '使用标签系统进行批量失效',
      '实现Stale-While-Revalidate模式',
      '监控缓存命中率和性能'
    ]
  },
  {
    category: '路由缓存',
    items: [
      '静态页面完全缓存',
      '动态页面使用ISR',
      '用户特定页面谨慎缓存',
      '设置合适的缓存头'
    ]
  },
  {
    category: '客户端缓存',
    items: [
      '选择合适的存储策略',
      '实现数据压缩和加密',
      '定期清理过期缓存',
      '处理离线场景'
    ]
  },
  {
    category: '监控和分析',
    items: [
      '实施全面的缓存监控',
      '分析缓存命中率和响应时间',
      '识别热门和冷门数据',
      '定期生成性能报告'
    ]
  },
  {
    category: '安全性',
    items: [
      '敏感数据谨慎缓存',
      '实现适当的加密',
      '设置访问权限控制',
      '定期审计缓存内容'
    ]
  }
];

export const runCachingBestPracticesCheck = async (): Promise<void> => {
  console.log('🔍 Running Caching Best Practices Check...');

  for (const category of cachingBestPracticesChecklist) {
    console.log(`\n📋 ${category.category}:`);
    for (const item of category.items) {
      console.log(`  ✅ ${item}`);
    }
  }

  console.log('\n🎯 Caching best practices check completed!');
};
```

### 2. 缓存配置模板

```typescript
// templates/cache-config.ts
export const productionCacheConfig = {
  data: {
    defaultTTL: 3600,
    tags: ['production'],
    revalidate: 3600,
    strategies: {
      static: {
        ttl: 86400,
        revalidate: false
      },
      dynamic: {
        ttl: 1800,
        revalidate: 300
      },
      user: {
        ttl: 900,
        revalidate: 180
      }
    }
  },
  route: {
    static: {
      ttl: 86400,
      strategy: 'static'
    },
    isr: {
      ttl: 3600,
      revalidate: 1800,
      strategy: 'isr'
    },
    ssr: {
      ttl: 0,
      strategy: 'ssr'
    }
  },
  client: {
    maxSize: 50,
    ttl: 1800,
    storage: 'indexedDB',
    compression: true,
    encryption: false
  },
  monitoring: {
    enabled: true,
    exportInterval: 60000, // 1分钟
    alertThresholds: {
      hitRate: 0.8,
      responseTime: 100,
      errorRate: 0.01
    }
  }
};

export const developmentCacheConfig = {
  ...productionCacheConfig,
  data: {
    ...productionCacheConfig.data,
    defaultTTL: 300, // 开发环境较短TTL
    revalidate: 60
  },
  monitoring: {
    enabled: false // 开发环境禁用监控
  }
};
```

## 🎯 总结

Advanced Caching 是 Next.js 15 应用性能优化的核心策略。通过合理使用数据缓存、路由缓存、客户端缓存等技术，可以显著提升应用的性能和用户体验。

### 关键要点：

1. **缓存策略选择**：根据数据特性选择合适的缓存策略
2. **数据缓存**：使用Next.js 15的缓存API和工具
3. **路由缓存**：静态、ISR、SSR等不同模式的缓存策略
4. **客户端缓存**：内存、LocalStorage、IndexedDB等存储方式
5. **监控分析**：全面的缓存性能监控和分析
6. **最佳实践**：建立缓存的最佳实践和规范

### 实施建议：

- **渐进式实施**：从关键功能开始，逐步扩展缓存覆盖
- **性能监控**：建立完整的缓存监控体系
- **容量规划**：合理规划缓存容量和淘汰策略
- **安全性**：注意缓存数据的安全性和隐私保护
- **团队协作**：建立缓存管理的最佳实践

通过掌握这些高级缓存技术，可以构建出高性能、可扩展的现代Web应用。