# 企业级数据获取模式详解

> **文档简介**: Next.js 15 + React 19 企业级数据获取完整指南，涵盖SSG/SSR/ISR、客户端获取、缓存策略、流式渲染、GraphQL、API设计等现代数据获取技术

> **目标读者**: 具备Next.js基础的中高级开发者，需要构建高性能数据获取系统的前端工程师

> **前置知识**: Next.js 15基础、React 19、TypeScript 5、HTTP协议、缓存概念、异步编程

> **预计时长**: 8-12小时

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `framework-patterns` |
| **难度** | ⭐⭐⭐⭐⭐ (5/5星) |
| **标签** | `#data-fetching` `#ssr` `#ssg` `#caching` `#performance` `#api-design` `#graphql` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 📚 概述

Next.js 15 与 React 19 提供了企业级的数据获取生态系统，涵盖服务器组件、客户端组件、API 路由、缓存策略、流式渲染等。本指南深入探讨企业级数据获取模式，结合现代工具和最佳实践，构建高性能、可扩展的数据获取架构。

## 🏗️ 数据获取架构概览

### 数据获取分类体系
**全面的数据获取策略**

```typescript
// 数据获取架构
interface DataFetchingArchitecture {
  // 服务器端数据获取
  serverSide: {
    staticGeneration: '静态生成 - 构建时预渲染';
    serverSideRendering: '服务器端渲染 - 请求时渲染';
    incrementalStaticRegeneration: '增量静态再生 - 定期更新';
    onDemandRevalidation: '按需重新验证 - 手动触发';
  };

  // 客户端数据获取
  clientSide: {
    traditionalFetching: '传统 fetch/axios 模式';
    dataFetchingLibraries: 'SWR, React Query, Apollo';
    realtimeSubscriptions: 'WebSocket, EventSource';
    optimisticUpdates: '乐观更新模式';
  };

  // 混合模式
  hybridPatterns: {
    streamingSSR: '流式服务器端渲染';
    progressiveEnhancement: '渐进式增强';
    selectiveHydration: '选择性水合';
    parallelDataFetching: '并行数据获取';
  };

  // 缓存策略
  cachingStrategies: {
    edgeCaching: '边缘缓存';
    browserCaching: '浏览器缓存';
    serverCaching: '服务器缓存';
    distributedCaching: '分布式缓存';
  };
}

// 数据获取策略选择器
export function createDataFetchingStrategy(config: {
  environment: 'server' | 'client' | 'hybrid';
  dataFreshness: 'static' | 'fresh' | 'realtime';
  performancePriority: 'speed' | 'freshness' | 'consistency';
  scale: 'small' | 'medium' | 'large';
}) {
  const strategies = {
    server: {
      static: { method: 'SSG', revalidate: 'never' },
      fresh: { method: 'SSR', revalidate: 'always' },
      realtime: { method: 'ISR', revalidate: 'frequent' },
    },
    client: {
      static: { method: 'cache-first', staleTime: 'infinite' },
      fresh: { method: 'network-only', staleTime: 0 },
      realtime: { method: 'websocket', subscription: true },
    },
    hybrid: {
      static: { method: 'SSG + CSR', hydration: 'selective' },
      fresh: { method: 'SSR + SWR', revalidate: 'background' },
      realtime: { method: 'Streaming + WS', optimization: 'edge' },
    },
  };

  return strategies[config.environment][config.dataFreshness];
}
```

## 🎯 服务器端数据获取模式

### 1. 高级静态生成 (SSG)
**企业级静态内容生成**

```typescript
// app/posts/page.tsx
import { notFound } from 'next/navigation';
import { cache } from 'react';

// 带缓存的数据库查询
const getPosts = cache(async () => {
  const response = await fetch('https://api.example.com/posts', {
    next: {
      tags: ['posts'],
      revalidate: 3600, // 1小时重新验证
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch posts');
  }

  return response.json();
});

// 带错误处理的静态生成
export async function generateStaticParams() {
  try {
    const posts = await getPosts();

    return posts.map((post: Post) => ({
      slug: post.slug,
    }));
  } catch (error) {
    console.error('Failed to generate static params:', error);
    return [];
  }
}

// 并行数据获取
async function getPostData(slug: string) {
  const [post, relatedPosts, author] = await Promise.all([
    fetch(`https://api.example.com/posts/${slug}`, {
      next: { revalidate: 3600, tags: [`post-${slug}`] }
    }).then(res => {
      if (!res.ok) throw new Error('Post not found');
      return res.json();
    }),
    fetch(`https://api.example.com/posts/${slug}/related`, {
      next: { revalidate: 7200, tags: ['related-posts'] }
    }).then(res => res.json()),
    fetch(`https://api.example.com/authors/by-post/${slug}`, {
      next: { revalidate: 86400, tags: ['authors'] }
    }).then(res => res.json()),
  ]);

  return { post, relatedPosts, author };
}

// 条件渲染和错误处理
export default async function PostPage({ params }: { params: { slug: string } }) {
  try {
    const { post, relatedPosts, author } = await getPostData(params.slug);

    if (!post) {
      notFound();
    }

    return (
      <article className="post-page">
        <header>
          <h1>{post.title}</h1>
          <div className="meta">
            <span>By {author.name}</span>
            <time>{new Date(post.publishedAt).toLocaleDateString()}</time>
          </div>
        </header>

        <div
          className="content"
          dangerouslySetInnerHTML={{ __html: post.content }}
        />

        <aside>
          <h3>Related Posts</h3>
          <RelatedPosts posts={relatedPosts} />
        </aside>
      </article>
    );
  } catch (error) {
    console.error('Failed to load post:', error);

    // 返回错误页面而不是崩溃
    return (
      <div className="error-container">
        <h1>Unable to Load Post</h1>
        <p>We're having trouble loading this content. Please try again later.</p>
        <button onClick={() => window.location.reload()}>
          Try Again
        </button>
      </div>
    );
  }
}

// 元数据生成
export async function generateMetadata({ params }: { params: { slug: string } }) {
  try {
    const { post, author } = await getPostData(params.slug);

    return {
      title: post.title,
      description: post.excerpt,
      authors: [{ name: author.name }],
      openGraph: {
        title: post.title,
        description: post.excerpt,
        images: [post.coverImage],
        publishedTime: post.publishedAt,
        modifiedTime: post.updatedAt,
      },
      twitter: {
        card: 'summary_large_image',
        title: post.title,
        description: post.excerpt,
        images: [post.coverImage],
      },
    };
  } catch (error) {
    return {
      title: 'Post Not Found',
      description: 'The requested post could not be found.',
    };
  }
}
```

### 2. 增量静态再生 (ISR)
**智能内容更新策略**

```typescript
// app/products/page.tsx
import { revalidateTag } from 'next/cache';

// 配置重新验证策略
const revalidationConfig = {
  // 高频更新的内容
  frequent: {
    revalidate: 60, // 1分钟
    tags: ['products', 'inventory'],
  },
  // 中频更新的内容
  periodic: {
    revalidate: 300, // 5分钟
    tags: ['categories', 'pricing'],
  },
  // 低频更新的内容
  stable: {
    revalidate: 3600, // 1小时
    tags: ['brands', 'specifications'],
  },
};

// 智能缓存管理
class ProductCacheManager {
  static async invalidateProduct(productId: string) {
    // 使特定产品缓存失效
    revalidateTag(`product-${productId}`);
    revalidateTag('products');
    revalidateTag('inventory');
  }

  static async invalidateCategory(categoryId: string) {
    revalidateTag(`category-${categoryId}`);
    revalidateTag('categories');
  }

  static async invalidateBrand(brandId: string) {
    revalidateTag(`brand-${brandId}`);
    revalidateTag('brands');
  }

  static async invalidateAll() {
    revalidateTag('products');
    revalidateTag('categories');
    revalidateTag('brands');
    revalidateTag('inventory');
    revalidateTag('pricing');
  }
}

// 带智能重新验证的产品获取
async function getProducts(options: {
  category?: string;
  brand?: string;
  page?: number;
  limit?: number;
  sortBy?: 'price' | 'name' | 'rating';
  sortOrder?: 'asc' | 'desc';
}) {
  const searchParams = new URLSearchParams();

  if (options.category) searchParams.set('category', options.category);
  if (options.brand) searchParams.set('brand', options.brand);
  if (options.page) searchParams.set('page', options.page.toString());
  if (options.limit) searchParams.set('limit', options.limit.toString());
  if (options.sortBy) searchParams.set('sortBy', options.sortBy);
  if (options.sortOrder) searchParams.set('sortOrder', options.sortOrder);

  const url = `https://api.example.com/products?${searchParams.toString()}`;

  const response = await fetch(url, {
    next: {
      revalidate: 300, // 5分钟重新验证
      tags: ['products', 'inventory'],
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch products');
  }

  return response.json();
}

// API 路由用于按需重新验证
// app/api/revalidate/products/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { revalidateTag } from 'next/cache';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { productId, category, brand, type } = body;

    switch (type) {
      case 'product':
        await ProductCacheManager.invalidateProduct(productId);
        break;
      case 'category':
        await ProductCacheManager.invalidateCategory(category);
        break;
      case 'brand':
        await ProductCacheManager.invalidateBrand(brand);
        break;
      case 'all':
        await ProductCacheManager.invalidateAll();
        break;
      default:
        throw new Error('Invalid revalidation type');
    }

    return NextResponse.json({
      success: true,
      message: 'Cache invalidated successfully',
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to revalidate cache' },
      { status: 500 }
    );
  }
}
```

### 3. 流式服务器端渲染
**高性能流式内容传输**

```typescript
// app/dashboard/loading.tsx
import { Skeleton } from '@/components/ui/skeleton';

export default function DashboardLoading() {
  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-10 w-32" />
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <Skeleton className="h-6 w-24 mb-4" />
          <Skeleton className="h-16 w-full" />
        </div>

        <div className="dashboard-card">
          <Skeleton className="h-6 w-32 mb-4" />
          <Skeleton className="h-24 w-full" />
        </div>

        <div className="dashboard-card">
          <Skeleton className="h-6 w-28 mb-4" />
          <Skeleton className="h-20 w-full" />
        </div>
      </div>

      <div className="dashboard-content">
        <Skeleton className="h-10 w-48 mb-6" />
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex items-center space-x-4">
              <Skeleton className="h-12 w-12 rounded-full" />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// app/dashboard/page.tsx
import { Suspense } from 'react';
import { DashboardHeader } from '@/components/dashboard/header';
import { StatsCards } from '@/components/dashboard/stats-cards';
import { RecentActivity } from '@/components/dashboard/recent-activity';
import { QuickActions } from '@/components/dashboard/quick-actions';

// 组件级别的数据获取
async function DashboardHeaderContent() {
  const userData = await getUserData();
  const notifications = await getUserNotifications();

  return <DashboardHeader user={userData} notifications={notifications} />;
}

async function StatsCardsContent() {
  const stats = await getDashboardStats();
  return <StatsCards stats={stats} />;
}

async function RecentActivityContent() {
  const activities = await getRecentActivities();
  return <RecentActivity activities={activities} />;
}

// 渐进式加载
export default async function DashboardPage() {
  return (
    <div className="dashboard">
      {/* 立即加载关键内容 */}
      <Suspense fallback={<DashboardHeaderSkeleton />}>
        <DashboardHeaderContent />
      </Suspense>

      {/* 并行加载次要内容 */}
      <div className="dashboard-content">
        <Suspense fallback={<StatsCardsSkeleton />}>
          <StatsCardsContent />
        </Suspense>

        <div className="dashboard-main">
          <div className="dashboard-section">
            <Suspense fallback={<RecentActivitySkeleton />}>
              <RecentActivityContent />
            </Suspense>
          </div>

          {/* 延迟加载低优先级内容 */}
          <Suspense fallback={<QuickActionsSkeleton />}>
            <QuickActions />
          </Suspense>
        </div>
      </div>
    </div>
  );
}

// 骨架屏组件
function DashboardHeaderSkeleton() {
  return (
    <div className="dashboard-header-skeleton">
      <Skeleton className="h-8 w-64" />
      <div className="flex space-x-4">
        <Skeleton className="h-10 w-32" />
        <Skeleton className="h-10 w-32" />
      </div>
    </div>
  );
}

function StatsCardsSkeleton() {
  return (
    <div className="stats-cards-skeleton">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="stat-card">
          <Skeleton className="h-6 w-24 mb-2" />
          <Skeleton className="h-8 w-16" />
        </div>
      ))}
    </div>
  );
}
```

## 🔄 客户端数据获取模式

### 1. 企业级 SWR 配置
**高级数据同步和缓存**

```typescript
// lib/swr-config.ts
import useSWR, { SWRConfig, SWRConfiguration } from 'swr';
import { Cache } from 'swr/_internal';

// 自定义 fetcher
const fetcher = async <T>(url: string): Promise<T> => {
  const response = await fetch(url);

  if (!response.ok) {
    const error = new Error(`HTTP error! status: ${response.status}`);
    (error as any).status = response.status;
    (error as any).response = response;
    throw error;
  }

  return response.json();
};

// 增强的缓存实现
class EnhancedCache extends Cache<any> {
  private persistKey = 'swr-cache-persist';

  constructor() {
    super();
    this.loadPersistedCache();
  }

  // 持久化缓存到 localStorage
  persistCache() {
    try {
      const cacheData = this.dump();
      localStorage.setItem(this.persistKey, JSON.stringify(cacheData));
    } catch (error) {
      console.warn('Failed to persist cache:', error);
    }
  }

  // 从 localStorage 加载缓存
  private loadPersistedCache() {
    try {
      const persistedData = localStorage.getItem(this.persistKey);
      if (persistedData) {
        const cacheData = JSON.parse(persistedData);
        this.load(cacheData);
      }
    } catch (error) {
      console.warn('Failed to load persisted cache:', error);
    }
  }

  // 清理过期缓存
  clearExpiredCache(maxAge: number = 24 * 60 * 60 * 1000) {
    const now = Date.now();
    this.keys().forEach(key => {
      const item = this.get(key);
      if (item && (now - item.createdAt) > maxAge) {
        this.delete(key);
      }
    });
    this.persistCache();
  }

  set(key: string, value: any, options?: any) {
    const result = super.set(key, value, options);
    this.persistCache();
    return result;
  }

  delete(key: string) {
    const result = super.delete(key);
    this.persistCache();
    return result;
  }
}

// 全局 SWR 配置
export const swrConfig: SWRConfiguration = {
  fetcher,

  // 缓存配置
  cache: new EnhancedCache(),

  // 重新验证策略
  revalidateOnFocus: true,
  revalidateOnReconnect: true,
  refreshInterval: 0, // 禁用自动刷新，按需控制

  // 错误处理
  shouldRetryOnError: true,
  errorRetryCount: 3,
  errorRetryInterval: 5000,

  // 加载状态
  loadingTimeout: 30000,

  // 悬停时暂停重新验证
  dedupingInterval: 2000,

  // 自定义配置
  focusThrottleInterval: 5000,
  refreshWhenHidden: false,

  // 错误处理回调
  onError: (error, key) => {
    console.error('SWR Error:', error, 'Key:', key);

    // 发送错误到监控系统
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('swr-error', {
        detail: { error, key }
      }));
    }
  },

  // 成功回调
  onSuccess: (data, key) => {
    console.log('SWR Success:', key);
  },
};

// 自定义 Hook: 用户数据
export function useUser(userId?: string) {
  const { data, error, isLoading, mutate } = useSWR<User>(
    userId ? `/api/users/${userId}` : null,
    fetcher,
    {
      revalidateOnMount: true,
      refreshInterval: 30 * 1000, // 30秒刷新
      dedupingInterval: 5000,
    }
  );

  return {
    user: data,
    isLoading,
    error,
    mutate,
    updateUser: async (updates: Partial<User>) => {
      const optimisticData = data ? { ...data, ...updates } : undefined;

      return mutate(
        async () => {
          const response = await fetch(`/api/users/${userId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates),
          });

          if (!response.ok) throw new Error('Failed to update user');
          return response.json();
        },
        {
          optimisticData,
          populateCache: true,
          rollbackOnError: true,
        }
      );
    },
  };
}

// 自定义 Hook: 实时数据
export function useRealtimeData<T>(url: string, options?: {
  refreshInterval?: number;
  enablePolling?: boolean;
}) {
  const {
    data,
    error,
    isLoading,
    mutate
  } = useSWR<T>(
    url,
    fetcher,
    {
      refreshInterval: options?.enablePolling
        ? options.refreshInterval || 5000
        : 0,
      revalidateOnFocus: options?.enablePolling ?? false,
      revalidateOnReconnect: true,
    }
  );

  return {
    data,
    isLoading,
    error,
    mutate,
    isConnected: !error && !isLoading,
  };
}

// 批量数据获取 Hook
export function useBatchData<T>(urls: string[], options?: {
  refreshInterval?: number;
  suspense?: boolean;
}) {
  const results = urls.map(url =>
    useSWR<T>(url, fetcher, {
      refreshInterval: options?.refreshInterval,
      suspense: options?.suspense,
    })
  );

  const data = results.map(result => result.data);
  const isLoading = results.some(result => result.isLoading);
  const error = results.find(result => result.error)?.error;
  const mutateAll = () => results.forEach(result => result.mutate());

  return {
    data,
    isLoading,
    error,
    mutateAll,
    isValidating: results.some(result => result.isValidating),
  };
}
```

### 2. TanStack Query 企业级配置
**强大的数据管理解决方案**

```typescript
// lib/query-client.ts
import { QueryClient } from '@tanstack/react-query';
import { defaultOptions } from './query-options';

// 创建 Query Client
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // 重试配置
      retry: (failureCount, error: any) => {
        // 4xx 错误不重试
        if (error?.status >= 400 && error?.status < 500) {
          return false;
        }

        // 网络错误重试
        if (error?.message?.includes('Network request failed')) {
          return failureCount < 5;
        }

        // 默认重试3次
        return failureCount < 3;
      },

      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),

      // 缓存配置
      staleTime: 5 * 60 * 1000, // 5分钟
      cacheTime: 10 * 60 * 1000, // 10分钟
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
      refetchOnMount: true,

      // 错误处理
      throwOnError: false,

      // 网络配置
      networkMode: 'online',
    },

    mutations: {
      retry: 1,
      networkMode: 'online',
    },
  },
});

// 错误边界
export class QueryErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Query Error Boundary caught an error:', error, errorInfo);

    // 发送错误到监控系统
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('query-error', {
        detail: { error, errorInfo }
      }));
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-fallback">
          <h2>Something went wrong</h2>
          <p>We encountered an error while loading data.</p>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// hooks/use-query-with-loading.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useCallback } from 'react';

interface UseQueryWithLoadingOptions<TData, TError> {
  queryKey: any[];
  queryFn: () => Promise<TData>;
  onSuccess?: (data: TData) => void;
  onError?: (error: TError) => void;
  staleTime?: number;
  cacheTime?: number;
}

export function useQueryWithLoading<TData = unknown, TError = Error>(
  options: UseQueryWithLoadingOptions<TData, TError>
) {
  const [isRefetching, setIsRefetching] = useState(false);

  const {
    data,
    error,
    isLoading,
    refetch,
    ...queryInfo
  } = useQuery({
    ...options,
    onSuccess: (data) => {
      setIsRefetching(false);
      options.onSuccess?.(data);
    },
    onError: (error) => {
      setIsRefetching(false);
      options.onError?.(error);
    },
  });

  const handleRefetch = useCallback(async () => {
    setIsRefetching(true);
    try {
      await refetch();
    } finally {
      setIsRefetching(false);
    }
  }, [refetch]);

  return {
    data,
    error,
    isLoading,
    isRefetching,
    refetch: handleRefetch,
    ...queryInfo,
  };
}

// hooks/use-optimistic-mutation.ts
export function useOptimisticMutation<TData, TVariables, TError = Error>(
  options: {
    mutationFn: (variables: TVariables) => Promise<TData>;
    onMutate?: (variables: TVariables) => Promise<any>;
    onSuccess?: (data: TData, variables: TVariables, context: any) => void;
    onError?: (error: TError, variables: TVariables, context: any) => void;
    onSettled?: (data: TData | undefined, error: TError | null, variables: TVariables, context: any) => void;
    invalidateQueries?: any[];
  }
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: options.mutationFn,

    onMutate: async (variables) => {
      // 取消正在进行的查询
      await queryClient.cancelQueries({ queryKey: options.invalidateQueries });

      // 保存之前的快照
      const snapshot = queryClient.getQueryData(options.invalidateQueries);

      // 执行 optimistic 更新
      const optimisticData = await options.onMutate?.(variables);

      if (optimisticData !== undefined) {
        queryClient.setQueryData(options.invalidateQueries, optimisticData);
      }

      return { snapshot, optimisticData };
    },

    onError: (error, variables, context) => {
      // 回滚到之前的状态
      if (context?.snapshot) {
        queryClient.setQueryData(options.invalidateQueries, context.snapshot);
      }

      options.onError?.(error, variables, context);
    },

    onSettled: (data, error, variables, context) => {
      // 无论成功或失败都重新获取数据
      if (options.invalidateQueries) {
        queryClient.invalidateQueries({ queryKey: options.invalidateQueries });
      }

      options.onSettled?.(data, error, variables, context);
    },

    onSuccess: options.onSuccess,
  });
}

// 实际使用示例：任务管理
interface Task {
  id: string;
  title: string;
  completed: boolean;
  createdAt: string;
  updatedAt: string;
}

export function useTasks() {
  return useQueryWithLoading({
    queryKey: ['tasks'],
    queryFn: async () => {
      const response = await fetch('/api/tasks');
      if (!response.ok) throw new Error('Failed to fetch tasks');
      return response.json();
    },
    staleTime: 2 * 60 * 1000, // 2分钟
    onError: (error) => {
      console.error('Failed to fetch tasks:', error);
    },
  });
}

export function useCreateTask() {
  return useOptimisticMutation<Task, Partial<Task>>({
    mutationFn: async (taskData) => {
      const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskData),
      });
      if (!response.ok) throw new Error('Failed to create task');
      return response.json();
    },

    onMutate: async (newTask) => {
      // 创建临时ID用于乐观更新
      const tempTask: Task = {
        id: `temp-${Date.now()}`,
        title: newTask.title || '',
        completed: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      // 乐观更新任务列表
      queryClient.setQueryData(['tasks'], (old: Task[] | undefined) =>
        old ? [...old, tempTask] : [tempTask]
      );

      return tempTask;
    },

    onSuccess: (newTask, variables, context) => {
      // 用实际数据替换临时数据
      queryClient.setQueryData(['tasks'], (old: Task[] | undefined) => {
        if (!old) return [newTask];
        return old.map(task =>
          task.id === context?.id ? newTask : task
        );
      });
    },

    invalidateQueries: ['tasks'],
  });
}
```

## 🌐 API 路由设计模式

### 1. RESTful API 架构
**企业级 API 设计**

```typescript
// app/api/v1/users/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { rateLimit } from '@/lib/rate-limit';
import { authenticate } from '@/lib/auth';
import { validateRequest } from '@/lib/validation';
import { createUser, getUsers, getUserCount } from '@/lib/users';

// 输入验证 Schema
const createUserSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name too long'),
  email: z.string().email('Invalid email address'),
  role: z.enum(['user', 'admin', 'moderator']).default('user'),
  preferences: z.object({
    theme: z.enum(['light', 'dark', 'auto']).default('auto'),
    notifications: z.boolean().default(true),
    language: z.string().default('en'),
  }).optional(),
});

const querySchema = z.object({
  page: z.coerce.number().min(1).default(1),
  limit: z.coerce.number().min(1).max(100).default(20),
  search: z.string().optional(),
  role: z.enum(['user', 'admin', 'moderator']).optional(),
  sortBy: z.enum(['name', 'email', 'createdAt', 'lastLogin']).default('createdAt'),
  sortOrder: z.enum(['asc', 'desc']).default('desc'),
});

// 认证中间件
async function requireAuth(request: NextRequest) {
  const user = await authenticate(request);
  if (!user) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    );
  }
  return user;
}

// 权限检查
function hasPermission(user: any, action: string) {
  const permissions = {
    'users:read': ['admin', 'moderator'],
    'users:write': ['admin'],
    'users:delete': ['admin'],
  };

  return permissions[action]?.includes(user.role) || false;
}

// GET /api/v1/users
export async function GET(request: NextRequest) {
  try {
    // 认证
    const user = await requireAuth(request);
    if (user instanceof NextResponse) return user;

    // 权限检查
    if (!hasPermission(user, 'users:read')) {
      return NextResponse.json(
        { error: 'Insufficient permissions' },
        { status: 403 }
      );
    }

    // 速率限制
    const rateLimitResult = await rateLimit(request, {
      windowMs: 60 * 1000, // 1分钟
      max: 100, // 最多100个请求
    });

    if (rateLimitResult instanceof NextResponse) return rateLimitResult;

    // 验证查询参数
    const { searchParams } = new URL(request.url);
    const query = querySchema.parse(Object.fromEntries(searchParams));

    // 获取用户数据
    const [users, totalCount] = await Promise.all([
      getUsers(query),
      getUserCount(query),
    ]);

    // 分页信息
    const totalPages = Math.ceil(totalCount / query.limit);
    const hasNextPage = query.page < totalPages;
    const hasPrevPage = query.page > 1;

    return NextResponse.json({
      data: users,
      pagination: {
        page: query.page,
        limit: query.limit,
        totalCount,
        totalPages,
        hasNextPage,
        hasPrevPage,
      },
      filters: {
        search: query.search,
        role: query.role,
        sortBy: query.sortBy,
        sortOrder: query.sortOrder,
      },
    });

  } catch (error) {
    console.error('GET /api/v1/users error:', error);

    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid query parameters', details: error.errors },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// POST /api/v1/users
export async function POST(request: NextRequest) {
  try {
    // 认证
    const user = await requireAuth(request);
    if (user instanceof NextResponse) return user;

    // 权限检查
    if (!hasPermission(user, 'users:write')) {
      return NextResponse.json(
        { error: 'Insufficient permissions' },
        { status: 403 }
      );
    }

    // 速率限制
    const rateLimitResult = await rateLimit(request, {
      windowMs: 60 * 1000,
      max: 10, // 创建操作限制更严格
    });

    if (rateLimitResult instanceof NextResponse) return rateLimitResult;

    // 验证请求体
    const body = await request.json();
    const validatedData = createUserSchema.parse(body);

    // 检查邮箱是否已存在
    const existingUser = await getUserByEmail(validatedData.email);
    if (existingUser) {
      return NextResponse.json(
        { error: 'Email already exists' },
        { status: 409 }
      );
    }

    // 创建用户
    const newUser = await createUser({
      ...validatedData,
      createdBy: user.id,
    });

    // 返回创建的用户（不包含敏感信息）
    const { password, ...userResponse } = newUser;

    return NextResponse.json(userResponse, { status: 201 });

  } catch (error) {
    console.error('POST /api/v1/users error:', error);

    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request body', details: error.errors },
        { status: 400 }
      );
    }

    if (error instanceof Error && error.message === 'Email already exists') {
      return NextResponse.json(
        { error: error.message },
        { status: 409 }
      );
    }

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// app/api/v1/users/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { getUserById, updateUser, deleteUser } from '@/lib/users';

const updateUserSchema = z.object({
  name: z.string().min(1).max(100).optional(),
  email: z.string().email().optional(),
  role: z.enum(['user', 'admin', 'moderator']).optional(),
  preferences: z.object({
    theme: z.enum(['light', 'dark', 'auto']).optional(),
    notifications: z.boolean().optional(),
    language: z.string().optional(),
  }).optional(),
  isActive: z.boolean().optional(),
}).partial();

// GET /api/v1/users/[id]
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const user = await requireAuth(request);
    if (user instanceof NextResponse) return user;

    if (!hasPermission(user, 'users:read')) {
      return NextResponse.json(
        { error: 'Insufficient permissions' },
        { status: 403 }
      );
    }

    const targetUser = await getUserById(params.id);
    if (!targetUser) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    // 不返回敏感信息
    const { password, ...userResponse } = targetUser;

    return NextResponse.json(userResponse);

  } catch (error) {
    console.error(`GET /api/v1/users/${params.id} error:`, error);

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// PATCH /api/v1/users/[id]
export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const user = await requireAuth(request);
    if (user instanceof NextResponse) return user;

    if (!hasPermission(user, 'users:write')) {
      return NextResponse.json(
        { error: 'Insufficient permissions' },
        { status: 403 }
      );
    }

    const body = await request.json();
    const validatedData = updateUserSchema.parse(body);

    const updatedUser = await updateUser(params.id, {
      ...validatedData,
      updatedBy: user.id,
    });

    if (!updatedUser) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    const { password, ...userResponse } = updatedUser;

    return NextResponse.json(userResponse);

  } catch (error) {
    console.error(`PATCH /api/v1/users/${params.id} error:`, error);

    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request body', details: error.errors },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// DELETE /api/v1/users/[id]
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const user = await requireAuth(request);
    if (user instanceof NextResponse) return user;

    if (!hasPermission(user, 'users:delete')) {
      return NextResponse.json(
        { error: 'Insufficient permissions' },
        { status: 403 }
      );
    }

    // 防止用户删除自己
    if (user.id === params.id) {
      return NextResponse.json(
        { error: 'Cannot delete your own account' },
        { status: 400 }
      );
    }

    const deleted = await deleteUser(params.id, user.id);

    if (!deleted) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({ message: 'User deleted successfully' });

  } catch (error) {
    console.error(`DELETE /api/v1/users/${params.id} error:`, error);

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

### 2. GraphQL API 集成
**现代 API 查询语言**

```typescript
// lib/graphql-client.ts
import { GraphQLClient } from 'graphql-request';
import { getClient } from './apollo-client';

// GraphQL 客户端配置
export const graphqlClient = new GraphQLClient(
  process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://localhost:3000/graphql',
  {
    headers: {
      'Content-Type': 'application/json',
    },
    // 错误处理
    errorPolicy: 'all',
    // 缓存配置
    fetch: async (url, options) => {
      const response = await fetch(url, {
        ...options,
        // 添加认证头
        headers: {
          ...options?.headers,
          Authorization: `Bearer ${await getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`GraphQL request failed: ${response.statusText}`);
      }

      return response;
    },
  }
);

// 获取认证 Token
async function getAuthToken(): Promise<string> {
  // 从 cookie 或 localStorage 获取 token
  if (typeof window !== 'undefined') {
    return localStorage.getItem('authToken') || '';
  }

  // 服务器端从 cookie 获取
  return '';
}

// GraphQL 查询构建器
class GraphQLQueryBuilder {
  private fields: string[] = [];
  private variables: Record<string, any> = {};
  private fragments: string[] = [];

  field(name: string, alias?: string): this {
    const field = alias ? `${alias}: ${name}` : name;
    this.fields.push(field);
    return this;
  }

  addFields(fields: string[]): this {
    this.fields.push(...fields);
    return this;
  }

  variable(name: string, type: string, value: any): this {
    this.variables[name] = value;
    return this;
  }

  addVariables(variables: Record<string, any>): this {
    Object.assign(this.variables, variables);
    return this;
  }

  fragment(name: string, on: string, fields: string): this {
    this.fragments.push(`fragment ${name} on ${on} { ${fields} }`);
    return this;
  }

  build(operation: 'query' | 'mutation' | 'subscription', name?: string): string {
    const variableDefinitions = Object.entries(this.variables)
      .map(([name, value]) => {
        const type = this.inferType(value);
        return `$${name}: ${type}`;
      })
      .join(', ');

    const operationName = name ? ` ${name}` : '';
    const variablesClause = variableDefinitions ? `(${variableDefinitions})` : '';
    const fragmentsClause = this.fragments.length > 0 ? `\n${this.fragments.join('\n')}` : '';

    return `${operation}${operationName}${variablesClause} {
      ${this.fields.join('\n  ')}${fragmentsClause}
    }`;
  }

  private inferType(value: any): string {
    if (typeof value === 'string') return 'String';
    if (typeof value === 'number') return 'Int';
    if (typeof value === 'boolean') return 'Boolean';
    if (Array.isArray(value)) return '[String]';
    return 'String';
  }
}

// 使用示例
export function buildUserQuery(userId: string) {
  return new GraphQLQueryBuilder()
    .field('user', 'userData')
    .addFields([
      'id',
      'name',
      'email',
      'avatar',
      'role',
      'createdAt',
      'updatedAt',
    ])
    .variable('id', 'String!', userId)
    .fragment('UserFields', 'User', `
      id
      name
      email
      avatar
      preferences {
        theme
        notifications
      }
    `)
    .build('query', 'GetUser');
}

// GraphQL Hooks
export function useGraphQLQuery<TData = any, TVariables = any>(
  query: string,
  variables?: TVariables,
  options?: {
    enabled?: boolean;
    suspense?: boolean;
    onSuccess?: (data: TData) => void;
    onError?: (error: Error) => void;
  }
) {
  const [data, setData] = useState<TData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(async () => {
    if (options?.enabled === false) return;

    setLoading(true);
    setError(null);

    try {
      const result = await graphqlClient.request(query, variables);
      setData(result);
      options?.onSuccess?.(result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('GraphQL request failed');
      setError(error);
      options?.onError?.(error);
    } finally {
      setLoading(false);
    }
  }, [query, variables, options]);

  useEffect(() => {
    if (options?.suspense) {
      throw execute(); // Suspense 模式
    } else {
      execute();
    }
  }, [execute]);

  return {
    data,
    loading,
    error,
    refetch: execute,
  };
}

// 实际使用示例
export function useUserProfile(userId: string) {
  const query = `
    query GetUserProfile($id: ID!) {
      user(id: $id) {
        id
        name
        email
        avatar
        role
        preferences {
          theme
          notifications
          language
        }
        stats {
          postsCount
          followersCount
          followingCount
        }
      }
    }
  `;

  return useGraphQLQuery(query, { id: userId }, {
    enabled: !!userId,
    onSuccess: (data) => {
      console.log('User profile loaded:', data);
    },
    onError: (error) => {
      console.error('Failed to load user profile:', error);
    },
  });
}

// GraphQL Mutation
export function useGraphQLMutation<TData = any, TVariables = any>(
  mutation: string,
  options?: {
    onSuccess?: (data: TData, variables: TVariables) => void;
    onError?: (error: Error, variables: TVariables) => void;
    onSettled?: (data: TData | undefined, error: Error | null, variables: TVariables) => void;
  }
) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(async (variables: TVariables) => {
    setLoading(true);
    setError(null);

    try {
      const result = await graphqlClient.request(mutation, variables);
      options?.onSuccess?.(result, variables);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('GraphQL mutation failed');
      setError(error);
      options?.onError?.(error, variables);
      throw error;
    } finally {
      setLoading(false);
      options?.onSettled?.(undefined, error, variables);
    }
  }, [mutation, options]);

  return {
    execute,
    loading,
    error,
  };
}
```

## 🔄 Server Actions 高级模式

### 1. 表单处理和数据验证
**企业级表单验证和处理**

```typescript
// app/actions/forms.ts
'use server';

import { z } from 'zod';
import { redirect } from 'next/navigation';
import { revalidateTag } from 'next/cache';
import { auth } from '@/lib/auth';
import { rateLimitAction } from '@/lib/rate-limit';
import { sendEmail } from '@/lib/email';
import { createAuditLog } from '@/lib/audit';

// 联系表单 Schema
const contactFormSchema = z.object({
  name: z.string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name must be less than 100 characters'),

  email: z.string()
    .email('Please enter a valid email address'),

  phone: z.string()
    .regex(/^[+]?[\d\s\-()]+$/, 'Please enter a valid phone number')
    .optional(),

  subject: z.string()
    .min(5, 'Subject must be at least 5 characters')
    .max(200, 'Subject must be less than 200 characters'),

  message: z.string()
    .min(10, 'Message must be at least 10 characters')
    .max(2000, 'Message must be less than 2000 characters'),

  preferredContact: z.enum(['email', 'phone'])
    .default('email'),

  consent: z.boolean()
    .refine(val => val === true, 'You must consent to data processing'),

  recaptchaToken: z.string()
    .min(1, 'reCAPTCHA verification is required'),
});

// 用户注册 Schema
const registrationSchema = z.object({
  name: z.string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name must be less than 100 characters')
    .regex(/^[a-zA-Z\s]+$/, 'Name can only contain letters and spaces'),

  email: z.string()
    .email('Please enter a valid email address')
    .toLowerCase(),

  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
      'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character'),

  confirmPassword: z.string(),

  acceptTerms: z.boolean()
    .refine(val => val === true, 'You must accept the terms and conditions'),

  marketingConsent: z.boolean().default(false),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

// 联系表单提交
export async function submitContactForm(prevState: any, formData: FormData) {
  try {
    // 速率限制
    const rateLimitResult = await rateLimitAction('contact-form', {
      windowMs: 15 * 60 * 1000, // 15分钟
      max: 5, // 最多5次提交
    });

    if (rateLimitResult) {
      return {
        success: false,
        error: 'Too many attempts. Please try again later.',
      };
    }

    // 验证 reCAPTCHA
    const recaptchaToken = formData.get('recaptchaToken') as string;
    const recaptchaValid = await validateRecaptcha(recaptchaToken);

    if (!recaptchaValid) {
      return {
        success: false,
        error: 'reCAPTCHA verification failed. Please try again.',
      };
    }

    // 解析和验证表单数据
    const rawData = {
      name: formData.get('name'),
      email: formData.get('email'),
      phone: formData.get('phone'),
      subject: formData.get('subject'),
      message: formData.get('message'),
      preferredContact: formData.get('preferredContact'),
      consent: formData.get('consent') === 'on',
      recaptchaToken,
    };

    const validatedData = contactFormSchema.parse(rawData);

    // 获取用户 IP 和 User-Agent
    const request = await getRequestContext();
    const metadata = {
      ip: request.ip,
      userAgent: request.userAgent,
      timestamp: new Date().toISOString(),
    };

    // 保存到数据库
    const contactSubmission = await saveContactSubmission({
      ...validatedData,
      metadata,
    });

    // 发送通知邮件
    await sendEmail({
      to: process.env.CONTACT_EMAIL!,
      subject: `New Contact Form: ${validatedData.subject}`,
      template: 'contact-notification',
      data: {
        ...validatedData,
        submissionId: contactSubmission.id,
      },
    });

    // 发送确认邮件给用户
    if (validatedData.preferredContact === 'email') {
      await sendEmail({
        to: validatedData.email,
        subject: 'We received your message',
        template: 'contact-confirmation',
        data: {
          name: validatedData.name,
          subject: validatedData.subject,
        },
      });
    }

    // 创建审计日志
    await createAuditLog({
      action: 'CONTACT_FORM_SUBMITTED',
      resource: 'contact-submission',
      resourceId: contactSubmission.id,
      metadata: {
        email: validatedData.email,
        ip: metadata.ip,
      },
    });

    return {
      success: true,
      message: 'Thank you for your message! We will get back to you soon.',
      submissionId: contactSubmission.id,
    };

  } catch (error) {
    console.error('Contact form submission error:', error);

    if (error instanceof z.ZodError) {
      return {
        success: false,
        error: 'Please check your input and try again.',
        fieldErrors: error.flatten().fieldErrors,
      };
    }

    if (error instanceof Error) {
      return {
        success: false,
        error: 'Something went wrong. Please try again later.',
      };
    }

    return {
      success: false,
      error: 'An unexpected error occurred.',
    };
  }
}

// 用户注册
export async function registerUser(prevState: any, formData: FormData) {
  try {
    // 速率限制
    const rateLimitResult = await rateLimitAction('registration', {
      windowMs: 60 * 60 * 1000, // 1小时
      max: 3, // 最多3次注册尝试
    });

    if (rateLimitResult) {
      return {
        success: false,
        error: 'Too many registration attempts. Please try again later.',
      };
    }

    // 解析和验证表单数据
    const rawData = {
      name: formData.get('name'),
      email: formData.get('email'),
      password: formData.get('password'),
      confirmPassword: formData.get('confirmPassword'),
      acceptTerms: formData.get('acceptTerms') === 'on',
      marketingConsent: formData.get('marketingConsent') === 'on',
    };

    const validatedData = registrationSchema.parse(rawData);

    // 检查邮箱是否已存在
    const existingUser = await getUserByEmail(validatedData.email);
    if (existingUser) {
      return {
        success: false,
        error: 'An account with this email already exists.',
      };
    }

    // 创建用户
    const newUser = await createUser({
      name: validatedData.name,
      email: validatedData.email,
      password: validatedData.password,
      marketingConsent: validatedData.marketingConsent,
    });

    // 发送欢迎邮件
    await sendEmail({
      to: validatedData.email,
      subject: 'Welcome to our platform!',
      template: 'welcome-email',
      data: {
        name: validatedData.name,
        email: validatedData.email,
      },
    });

    // 创建审计日志
    await createAuditLog({
      action: 'USER_REGISTERED',
      resource: 'user',
      resourceId: newUser.id,
      metadata: {
        email: validatedData.email,
        ip: await getClientIP(),
      },
    });

    // 重定向到登录页面
    redirect('/login?message=registration-success');

  } catch (error) {
    console.error('User registration error:', error);

    if (error instanceof z.ZodError) {
      return {
        success: false,
        error: 'Please check your input and try again.',
        fieldErrors: error.flatten().fieldErrors,
      };
    }

    return {
      success: false,
      error: 'Registration failed. Please try again later.',
    };
  }
}

// 批量操作
export async function bulkUpdateItems(formData: FormData) {
  try {
    const session = await auth();
    if (!session?.user || !['admin', 'moderator'].includes(session.user.role)) {
      return {
        success: false,
        error: 'Unauthorized',
      };
    }

    // 速率限制
    await rateLimitAction('bulk-update', {
      windowMs: 60 * 1000,
      max: 10,
    });

    const itemIds = formData.get('itemIds') as string;
    const updates = JSON.parse(formData.get('updates') as string);

    if (!itemIds || !updates) {
      return {
        success: false,
        error: 'Missing required parameters',
      };
    }

    const ids = itemIds.split(',').map(id => id.trim());

    // 执行批量更新
    const results = await Promise.allSettled(
      ids.map(id => updateItem(id, updates))
    );

    const successful = results.filter(r => r.status === 'fulfilled').length;
    const failed = results.filter(r => r.status === 'rejected').length;

    // 使相关缓存失效
    revalidateTag('items');

    // 创建审计日志
    await createAuditLog({
      action: 'BULK_UPDATE_ITEMS',
      resource: 'items',
      metadata: {
        itemCount: ids.length,
        successful,
        failed,
        updates,
        performedBy: session.user.id,
      },
    });

    return {
      success: true,
      message: `Updated ${successful} items successfully${failed > 0 ? ` (${failed} failed)` : ''}`,
      results: {
        total: ids.length,
        successful,
        failed,
      },
    };

  } catch (error) {
    console.error('Bulk update error:', error);
    return {
      success: false,
      error: 'Bulk update failed. Please try again.',
    };
  }
}

// 工具函数
async function validateRecaptcha(token: string): Promise<boolean> {
  try {
    const response = await fetch(
      `https://www.google.com/recaptcha/api/siteverify`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `secret=${process.env.RECAPTCHA_SECRET_KEY}&response=${token}`,
      }
    );

    const result = await response.json();
    return result.success;
  } catch (error) {
    console.error('reCAPTCHA validation error:', error);
    return false;
  }
}

async function getRequestContext() {
  // 在实际应用中，这里会获取请求的上下文信息
  return {
    ip: '127.0.0.1',
    userAgent: 'Mozilla/5.0...',
  };
}

async function getClientIP(): Promise<string> {
  // 获取客户端真实 IP 地址
  return '127.0.0.1';
}
```

## 📋 企业级数据获取清单

### 架构选择指南
- [ ] **静态生成 (SSG)**: 适用于静态内容、博客、文档
- [ ] **服务器端渲染 (SSR)**: 适用于个性化内容、实时数据
- [ ] **增量静态再生 (ISR)**: 适用于频繁更新但可缓存的内容
- [ ] **客户端渲染 (CSR)**: 适用于交互式应用、实时数据
- [ ] **混合模式**: 结合多种方式，优化性能和用户体验

### 性能优化
- [ ] **并行数据获取**: 使用 Promise.all 并行获取多个数据源
- [ ] **流式渲染**: 大数据集分块传输
- [ ] **缓存策略**: 合理设置缓存时间和失效策略
- [ ] **数据预加载**: 在用户交互前预加载数据
- [ ] **懒加载**: 按需加载非关键数据

### 错误处理
- [ ] **重试机制**: 指数退避重试策略
- [ ] **错误边界**: 防止单个数据获取失败影响整个应用
- [ ] **降级策略**: 在数据不可用时提供备用内容
- [ ] **用户反馈**: 清晰的错误提示和恢复选项
- [ ] **错误监控**: 集成错误监控和报警系统

### 安全考虑
- [ ] **输入验证**: 严格验证所有输入数据
- [ ] **权限控制**: 基于角色的访问控制
- [ ] **速率限制**: 防止 API 滥用
- [ ] **数据脱敏**: 不在客户端暴露敏感信息
- [ ] **审计日志**: 记录所有数据操作

## 📖 总结

Next.js 15 的数据获取生态系统提供了企业级的解决方案：

### 核心特性：
1. **多样化选择**: 从静态生成到实时获取的完整解决方案
2. **性能优化**: 内置缓存、流式渲染和并行获取
3. **开发体验**: 优秀的 TypeScript 支持和错误处理
4. **可扩展性**: 支持从小型应用到大型企业应用

### 最佳实践：
1. **合理选择**: 根据数据特性选择合适的获取策略
2. **性能优先**: 优化缓存策略和加载顺序
3. **错误处理**: 实现健壮的错误处理和恢复机制
4. **安全第一**: 严格的输入验证和权限控制

通过合理的数据获取架构，可以构建高性能、安全、可维护的 Next.js 15 企业应用。

---

## 🔄 文档交叉引用

### 相关文档
- 📄 **[服务端组件模式](./02-server-components-patterns.md)**: 深入了解服务端渲染和缓存策略
- 📄 **[客户端组件模式](./03-client-components-patterns.md)**: 掌握客户端数据获取和状态管理
- 📄 **[状态管理模式](./05-state-management-patterns.md)**: 学习React Query和Zustand数据管理
- 📄 **[认证流程模式](./07-authentication-flows.md)**: 实现API安全认证和权限控制

### 参考章节
- 📖 **[本模块其他章节]**: [服务端组件模式](./02-server-components-patterns.md#数据获取模式)中的服务端数据获取部分
- 📖 **[其他模块相关内容]**: [JavaScript现代语法](../language-concepts/04-javascript-modern.md)中的异步编程部分

---

## 📝 总结

### 核心要点回顾
1. **数据获取策略**: SSG/SSR/ISR/CSR的选择和应用场景
2. **缓存系统**: Next.js内置缓存和自定义缓存策略
3. **客户端获取**: SWR、React Query等现代数据获取库
4. **GraphQL集成**: Apollo Client和服务器端集成
5. **Server Actions**: Next.js 15的革命性数据操作模式

### 学习成果检查
- [ ] 是否理解了不同数据获取策略的适用场景？
- [ ] 是否能够实现复杂的缓存策略？
- [ ] 是否掌握了客户端数据获取库的使用？
- [ ] 是否能够集成GraphQL和REST API？
- [ ] 是否具备了企业级数据获取架构设计能力？

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

**文档状态**: ✅ 已完成 | 🚧 进行中 | 📋 计划中
**最后更新**: 2025年10月
**版本**: v1.0.0