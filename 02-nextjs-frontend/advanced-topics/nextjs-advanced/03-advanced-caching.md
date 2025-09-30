# Next.js 15 高级缓存策略

## 📋 概述

Next.js 15 提供了强大的缓存系统，结合了 React 19 的 Server Components 和边缘计算能力，为开发者提供了细粒度的缓存控制。本文将深入探讨 Next.js 15 的高级缓存策略和最佳实践。

## 🎯 缓存架构概览

### 1. 缓存层次结构

```
客户端浏览器
    ↓ (HTTP缓存)
CDN边缘节点
    ↓ (边缘缓存)
Next.js应用层
    ↓ (数据缓存)
数据源 (数据库/API)
```

### 2. 缓存类型对比

| 缓存类型 | 作用范围 | 生命周期 | 控制方式 |
|---------|---------|---------|---------|
| **HTTP缓存** | 客户端浏览器 | 可配置 | Cache-Control头 |
| **CDN缓存** | 全球边缘节点 | 可配置 | Cache-Control头 |
| **路由缓存** | Next.js路由 | 可配置 | fetch选项 |
| **数据缓存** | 应用数据 | 可配置 | unstable_cache |
| **全页缓存** | 整个页面 | 可配置 | generateStaticParams |

## 🚀 数据缓存策略

### 1. 使用 unstable_cache

```typescript
// lib/cache.ts
import { unstable_cache } from 'next/cache';

// 基础缓存函数
export const getCachedUser = unstable_cache(
  async (userId: string) => {
    const user = await prisma.user.findUnique({
      where: { id: userId },
      include: { posts: true, comments: true }
    });
    return user;
  },
  ['user'], // 缓存标签
  {
    revalidate: 3600, // 1小时
    tags: ['user', `user-${userId}`], // 缓存标签
  }
);

// 高级缓存配置
export const getCachedPosts = unstable_cache(
  async (page: number = 1, limit: number = 10) => {
    const posts = await prisma.post.findMany({
      skip: (page - 1) * limit,
      take: limit,
      orderBy: { createdAt: 'desc' },
      include: { author: true }
    });

    return {
      posts,
      pagination: {
        page,
        limit,
        total: await prisma.post.count()
      }
    };
  },
  ['posts'], // 缓存键
  {
    revalidate: 1800, // 30分钟
    tags: ['posts', 'posts-list'],
  }
);

// 条件缓存
export const getCachedDataWithConditions = unstable_cache(
  async (key: string, conditions: any) => {
    const data = await fetchDataFromAPI(key, conditions);
    return data;
  },
  ['conditional-data'],
  {
    revalidate: (data) => {
      // 动态决定缓存时间
      return data.isFresh ? 3600 : 600;
    },
    tags: ['conditional-data'],
  }
);
```

### 2. 缓存标签系统

```typescript
// lib/cache-tags.ts
import { revalidateTag } from 'next/cache';

// 预定义缓存标签
export const CacheTags = {
  USER: 'user',
  POST: 'post',
  PRODUCT: 'product',
  SETTINGS: 'settings',
  NAVIGATION: 'navigation',
} as const;

// 标签构建器
export class CacheTagBuilder {
  static user(userId: string) {
    return `${CacheTags.USER}-${userId}`;
  }

  static post(postId: string) {
    return `${CacheTags.POST}-${postId}`;
  }

  static product(productId: string) {
    return `${CacheTags.PRODUCT}-${productId}`;
  }

  static userPosts(userId: string) {
    return `${CacheTags.USER}-posts-${userId}`;
  }
}

// 缓存刷新策略
export class CacheRefresher {
  static async refreshUser(userId: string) {
    await Promise.all([
      revalidateTag(CacheTags.USER),
      revalidateTag(CacheTagBuilder.user(userId)),
      revalidateTag(CacheTagBuilder.userPosts(userId)),
    ]);
  }

  static async refreshPost(postId: string, authorId: string) {
    await Promise.all([
      revalidateTag(CacheTags.POST),
      revalidateTag(CacheTagBuilder.post(postId)),
      revalidateTag(CacheTagBuilder.userPosts(authorId)),
    ]);
  }

  static async refreshGlobalSettings() {
    await revalidateTag(CacheTags.SETTINGS);
  }
}
```

### 3. 分层缓存策略

```typescript
// lib/layered-cache.ts
import { unstable_cache } from 'next/cache';

// 内存缓存 (Node.js环境)
class MemoryCache {
  private cache = new Map<string, { data: any; expiry: number }>();

  set(key: string, data: any, ttl: number = 300) {
    this.cache.set(key, {
      data,
      expiry: Date.now() + ttl * 1000
    });
  }

  get(key: string): any | null {
    const item = this.cache.get(key);
    if (!item || Date.now() > item.expiry) {
      this.cache.delete(key);
      return null;
    }
    return item.data;
  }

  clear() {
    this.cache.clear();
  }
}

const memoryCache = new MemoryCache();

// 分层缓存实现
export async function getWithLayeredCache<T>(
  key: string,
  fetcher: () => Promise<T>,
  options: {
    memoryTTL?: number;
    nextCacheTTL?: number;
    tags?: string[];
  } = {}
): Promise<T> {
  const { memoryTTL = 60, nextCacheTTL = 3600, tags = [] } = options;

  // 1. 检查内存缓存
  const memoryResult = memoryCache.get(key);
  if (memoryResult) {
    return memoryResult;
  }

  // 2. 检查Next.js缓存
  const cachedFetch = unstable_cache(
    async () => fetcher(),
    [key],
    {
      revalidate: nextCacheTTL,
      tags,
    }
  );

  const result = await cachedFetch();

  // 3. 存储到内存缓存
  memoryCache.set(key, result, memoryTTL);

  return result;
}

// 使用示例
export async function getProductWithCache(productId: string) {
  return getWithLayeredCache(
    `product-${productId}`,
    async () => {
      const product = await prisma.product.findUnique({
        where: { id: productId },
        include: { category: true, reviews: true }
      });
      return product;
    },
    {
      memoryTTL: 120, // 2分钟内存缓存
      nextCacheTTL: 1800, // 30分钟Next.js缓存
      tags: ['product', `product-${productId}`]
    }
  );
}
```

## 🎨 路由缓存优化

### 1. 动态路由缓存

```typescript
// app/products/[id]/page.tsx
import { unstable_cache } from 'next/cache';

async function getProduct(id: string) {
  return unstable_cache(
    async () => {
      const product = await prisma.product.findUnique({
        where: { id },
        include: {
          category: true,
          variants: true,
          reviews: {
            include: { user: true },
            orderBy: { createdAt: 'desc' },
            take: 10
          }
        }
      });
      return product;
    },
    [`product-${id}`],
    {
      revalidate: 1800, // 30分钟
      tags: ['product', `product-${id}`]
    }
  );
}

export async function generateStaticParams() {
  const products = await prisma.product.findMany({
    select: { id: true }
  });

  return products.map(product => ({
    id: product.id
  }));
}

export async function generateMetadata({ params }: { params: { id: string } }) {
  const product = await getProduct(params.id);

  return {
    title: product?.name || 'Product',
    description: product?.description,
    openGraph: {
      title: product?.name,
      description: product?.description,
      images: product?.images || []
    }
  };
}

export default async function ProductPage({ params }: { params: { id: string } }) {
  const product = await getProduct(params.id);

  if (!product) {
    notFound();
  }

  return (
    <div>
      <ProductDetails product={product} />
      <Suspense fallback={<div>Loading reviews...</div>}>
        <ProductReviews productId={params.id} />
      </Suspense>
    </div>
  );
}
```

### 2. 增量静态再生成（ISR）

```typescript
// app/blog/[slug]/page.tsx
export const revalidate = 3600; // 1小时自动重新验证

export async function generateStaticParams() {
  const posts = await prisma.post.findMany({
    select: { slug: true },
    where: { published: true }
  });

  return posts.map(post => ({
    slug: post.slug
  }));
}

// 手动触发重新验证
export async function POST(request: Request) {
  const { slug } = await request.json();

  try {
    // 1. 重新验证页面
    await revalidatePath(`/blog/${slug}`);

    // 2. 刷新相关缓存
    await Promise.all([
      revalidateTag('blog'),
      revalidateTag(`blog-${slug}`),
      revalidateTag('blog-list')
    ]);

    // 3. 刷新相关数据缓存
    const post = await prisma.post.findUnique({
      where: { slug },
      include: { author: true }
    });

    if (post) {
      await Promise.all([
        revalidateTag(`author-${post.author.id}`),
        revalidateTag(`author-posts-${post.author.id}`)
      ]);
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to revalidate' },
      { status: 500 }
    );
  }
}
```

### 3. 流式渲染与缓存

```typescript
// app/dashboard/page.tsx
import { Suspense } from 'react';
import { unstable_cache } from 'next/cache';

// 缓存统计数据
async function getCachedStats() {
  return unstable_cache(
    async () => {
      const [users, posts, comments] = await Promise.all([
        prisma.user.count(),
        prisma.post.count(),
        prisma.comment.count()
      ]);

      return { users, posts, comments };
    },
    ['dashboard-stats'],
    {
      revalidate: 600, // 10分钟
      tags: ['dashboard', 'stats']
    }
  );
}

// 缓存用户活动
async function getCachedUserActivity() {
  return unstable_cache(
    async () => {
      const activities = await prisma.userActivity.findMany({
        orderBy: { timestamp: 'desc' },
        take: 20,
        include: { user: true }
      });
      return activities;
    },
    ['user-activity'],
    {
      revalidate: 300, // 5分钟
      tags: ['dashboard', 'activity']
    }
  );
}

export default function DashboardPage() {
  return (
    <div className="dashboard">
      <h1>Dashboard</h1>

      <Suspense fallback={<StatsSkeleton />}>
        <DashboardStats />
      </Suspense>

      <Suspense fallback={<ActivitySkeleton />}>
        <UserActivity />
      </Suspense>

      <Suspense fallback={<ChartsSkeleton />}>
        <AnalyticsCharts />
      </Suspense>
    </div>
  );
}

async function DashboardStats() {
  const stats = await getCachedStats();
  return <StatsOverview stats={stats} />;
}

async function UserActivity() {
  const activities = await getCachedUserActivity();
  return <ActivityFeed activities={activities} />;
}
```

## 🔄 客户端缓存策略

### 1. SWR 客户端缓存

```typescript
// hooks/useSWRWithCache.ts
import useSWR from 'swr';
import { mutate } from 'swr';

// 自定义fetcher
const fetcher = async (url: string) => {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('Failed to fetch data');
  }
  return response.json();
};

// 增强的SWR Hook
export function useSWRWithCache<T>(
  key: string,
  fetcher: () => Promise<T>,
  options: {
    revalidateOnFocus?: boolean;
    revalidateOnReconnect?: boolean;
    refreshInterval?: number;
    dedupingInterval?: number;
    onSuccess?: (data: T) => void;
    onError?: (error: Error) => void;
  } = {}
) {
  const {
    revalidateOnFocus = false,
    revalidateOnReconnect = true,
    refreshInterval = 0,
    dedupingInterval = 2000,
    onSuccess,
    onError
  } = options;

  return useSWR<T>(
    key,
    fetcher,
    {
      revalidateOnFocus,
      revalidateOnReconnect,
      refreshInterval,
      dedupingInterval,
      onSuccess,
      onError,
      onErrorRetry: (error, key, config, revalidate, { retryCount }) => {
        if (error.status === 404) return;
        if (retryCount >= 3) return;
        setTimeout(() => revalidate({ retryCount }), 5000);
      }
    }
  );
}

// 预取函数
export function prefetchSWR<T>(key: string, data: T) {
  mutate(key, data, false);
}

// 使用示例
function UserProfile({ userId }: { userId: string }) {
  const { data: user, error, isLoading } = useSWRWithCache(
    `/api/users/${userId}`,
    () => fetch(`/api/users/${userId}`).then(res => res.json()),
    {
      revalidateOnFocus: false,
      refreshInterval: 30000, // 30秒
      onSuccess: (data) => {
        console.log('User data loaded:', data);
      }
    }
  );

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading user</div>;

  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}
```

### 2. React Query 缓存策略

```typescript
// hooks/useReactQuery.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// 查询配置
export const queryConfig = {
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5分钟
      cacheTime: 10 * 60 * 1000, // 10分钟
      retry: (failureCount, error: any) => {
        if (error.status === 404) return false;
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
    mutations: {
      retry: (failureCount, error: any) => {
        if (error.status === 400) return false;
        return failureCount < 3;
      },
    },
  },
};

// 使用React Query的Hook
export function useUserQuery(userId: string) {
  return useQuery({
    queryKey: ['users', userId],
    queryFn: async () => {
      const response = await fetch(`/api/users/${userId}`);
      if (!response.ok) throw new Error('Failed to fetch user');
      return response.json();
    },
    enabled: !!userId,
    ...queryConfig.defaultOptions.queries,
  });
}

export function useUpdateUserMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ userId, data }: { userId: string; data: any }) => {
      const response = await fetch(`/api/users/${userId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Failed to update user');
      return response.json();
    },
    onSuccess: (data, variables) => {
      // 更新缓存
      queryClient.setQueryData(['users', variables.userId], data);
      queryClient.invalidateQueries(['users']);
    },
    onError: (error, variables, context) => {
      console.error('Failed to update user:', error);
    },
    onSettled: () => {
      queryClient.invalidateQueries(['users']);
    },
  });
}
```

## 🎯 缓存监控和分析

### 1. 缓存性能监控

```typescript
// lib/cache-monitor.ts
class CacheMonitor {
  private metrics = {
    hits: 0,
    misses: 0,
    errors: 0,
    totalResponseTime: 0,
  };

  recordHit(responseTime: number) {
    this.metrics.hits++;
    this.metrics.totalResponseTime += responseTime;
  }

  recordMiss(responseTime: number) {
    this.metrics.misses++;
    this.metrics.totalResponseTime += responseTime;
  }

  recordError() {
    this.metrics.errors++;
  }

  getMetrics() {
    const totalRequests = this.metrics.hits + this.metrics.misses;
    const hitRate = totalRequests > 0 ? this.metrics.hits / totalRequests : 0;
    const averageResponseTime = totalRequests > 0
      ? this.metrics.totalResponseTime / totalRequests
      : 0;

    return {
      hits: this.metrics.hits,
      misses: this.metrics.misses,
      errors: this.metrics.errors,
      hitRate,
      averageResponseTime,
    };
  }

  reset() {
    this.metrics = {
      hits: 0,
      misses: 0,
      errors: 0,
      totalResponseTime: 0,
    };
  }
}

const cacheMonitor = new CacheMonitor();

// 监控包装器
export async function withCacheMonitoring<T>(
  key: string,
  fetcher: () => Promise<T>
): Promise<T> {
  const startTime = performance.now();

  try {
    const result = await fetcher();
    const responseTime = performance.now() - startTime;

    // 检查是否是缓存命中
    const isCacheHit = responseTime < 50; // 假设缓存响应时间小于50ms
    if (isCacheHit) {
      cacheMonitor.recordHit(responseTime);
    } else {
      cacheMonitor.recordMiss(responseTime);
    }

    return result;
  } catch (error) {
    cacheMonitor.recordError();
    throw error;
  }
}

// 缓存健康检查
export async function checkCacheHealth() {
  const metrics = cacheMonitor.getMetrics();

  // 如果命中率低于60%，发出警告
  if (metrics.hitRate < 0.6) {
    console.warn('Cache hit rate is low:', metrics.hitRate);
  }

  // 如果平均响应时间超过100ms，发出警告
  if (metrics.averageResponseTime > 100) {
    console.warn('Cache response time is high:', metrics.averageResponseTime);
  }

  return metrics;
}
```

### 2. 缓存分析工具

```typescript
// utils/cache-analyzer.ts
export class CacheAnalyzer {
  static analyzeCachePattern(keys: string[]) {
    const patterns = keys.reduce((acc, key) => {
      const pattern = key.replace(/[\d-]+/g, '*'); // 替换数字和连字符
      acc[pattern] = (acc[pattern] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return Object.entries(patterns)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10); // 返回前10个最常见的模式
  }

  static detectCacheBottlenecks(metrics: any) {
    const bottlenecks = [];

    if (metrics.hitRate < 0.5) {
      bottlenecks.push({
        type: 'low_hit_rate',
        message: 'Cache hit rate is below 50%',
        severity: 'high',
      });
    }

    if (metrics.averageResponseTime > 200) {
      bottlenecks.push({
        type: 'slow_response',
        message: 'Average cache response time is above 200ms',
        severity: 'medium',
      });
    }

    if (metrics.errorRate > 0.1) {
      bottlenecks.push({
        type: 'high_error_rate',
        message: 'Cache error rate is above 10%',
        severity: 'high',
      });
    }

    return bottlenecks;
  }

  static suggestOptimizations(analysis: any) {
    const suggestions = [];

    if (analysis.hitRate < 0.6) {
      suggestions.push({
        type: 'increase_ttl',
        message: 'Consider increasing cache TTL for frequently accessed data',
        impact: 'high',
      });
    }

    if (analysis.patterns.length > 20) {
      suggestions.push({
        type: 'consolidate_patterns',
        message: 'Too many cache patterns detected, consider consolidating',
        impact: 'medium',
      });
    }

    return suggestions;
  }
}
```

## 🚨 缓存最佳实践

### 1. 缓存策略选择指南

```typescript
// lib/cache-strategies.ts
export const CacheStrategies = {
  // 用户个人数据 - 短期缓存
  USER_DATA: {
    ttl: 300, // 5分钟
    tags: ['user'],
    staleWhileRevalidate: true,
  },

  // 产品数据 - 中期缓存
  PRODUCT_DATA: {
    ttl: 1800, // 30分钟
    tags: ['product'],
    staleWhileRevalidate: true,
  },

  // 静态内容 - 长期缓存
  STATIC_CONTENT: {
    ttl: 86400, // 24小时
    tags: ['static'],
    staleWhileRevalidate: false,
  },

  // 实时数据 - 无缓存
  REALTIME_DATA: {
    ttl: 0,
    tags: ['realtime'],
    staleWhileRevalidate: false,
  },

  // 分析数据 - 中期缓存
  ANALYTICS_DATA: {
    ttl: 3600, // 1小时
    tags: ['analytics'],
    staleWhileRevalidate: true,
  },
};

// 缓存策略工厂
export function createCacheStrategy(type: keyof typeof CacheStrategies) {
  const strategy = CacheStrategies[type];

  return {
    ...strategy,
    revalidate: strategy.ttl,
    tags: strategy.tags,
  };
}
```

### 2. 缓存失效策略

```typescript
// lib/cache-invalidation.ts
export class CacheInvalidationManager {
  private invalidationRules = new Map<string, string[]>();

  constructor() {
    this.setupInvalidationRules();
  }

  private setupInvalidationRules() {
    // 用户更新时失效相关缓存
    this.invalidationRules.set('user-updated', [
      'user',
      'user-profile',
      'user-settings',
      'user-activity',
    ]);

    // 产品更新时失效相关缓存
    this.invalidationRules.set('product-updated', [
      'product',
      'product-list',
      'product-search',
      'category-products',
    ]);

    // 订单创建时失效相关缓存
    this.invalidationRules.set('order-created', [
      'user-orders',
      'order-stats',
      'product-stock',
    ]);
  }

  async invalidateOnEvent(event: string, data: any) {
    const tags = this.invalidationRules.get(event) || [];

    await Promise.all(
      tags.map(tag => revalidateTag(tag))
    );

    // 特定事件的特殊处理
    switch (event) {
      case 'user-updated':
        await this.invalidateUserData(data.userId);
        break;
      case 'product-updated':
        await this.invalidateProductData(data.productId);
        break;
    }
  }

  private async invalidateUserData(userId: string) {
    await Promise.all([
      revalidateTag(`user-${userId}`),
      revalidateTag(`user-profile-${userId}`),
      revalidateTag(`user-orders-${userId}`),
    ]);
  }

  private async invalidateProductData(productId: string) {
    await Promise.all([
      revalidateTag(`product-${productId}`),
      revalidateTag(`product-variants-${productId}`),
      revalidateTag(`product-reviews-${productId}`),
    ]);
  }
}

export const cacheInvalidationManager = new CacheInvalidationManager();
```

## 🎯 总结

Next.js 15 的缓存系统提供了强大的功能，通过合理使用这些缓存策略，可以显著提升应用性能和用户体验。

### 关键要点：

1. **多层次缓存**：HTTP缓存、CDN缓存、应用缓存、数据缓存
2. **细粒度控制**：使用unstable_cache和缓存标签实现精确控制
3. **智能失效**：基于事件的缓存失效策略
4. **性能监控**：缓存命中率、响应时间监控和分析
5. **最佳实践**：根据数据类型选择合适的缓存策略

### 缓存策略建议：

- **用户数据**：短期缓存，快速失效
- **产品数据**：中期缓存，产品更新时失效
- **静态内容**：长期缓存，版本控制
- **实时数据**：无缓存或极短期缓存
- **分析数据**：中期缓存，定期刷新

通过掌握这些高级缓存技术，可以构建出高性能、高可用的现代Web应用。