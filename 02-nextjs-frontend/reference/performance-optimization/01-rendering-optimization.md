# Next.js 16 渲染性能优化完整指南

> **文档简介**: Next.js 16 渲染性能优化企业级实践指南，涵盖Core Web Vitals、SSR/SSG优化、组件渲染、图片优化、字体加载等现代性能优化技术

> **目标读者**: 具备Next.js基础的中高级开发者，需要掌握性能优化和用户体验提升的前端工程师

> **前置知识**: Next.js 16基础、React 19渲染机制、Web性能指标、浏览器渲染原理

> **预计时长**: 8-12小时

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `reference` |
| **难度** | ⭐⭐⭐⭐⭐ (5/5星) |
| **标签** | `#performance` `#optimization` `#core-web-vitals` `#rendering` `#ux` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 📚 概述

性能优化是现代 Web 应用开发的关键环节。本指南涵盖了 Next.js 应用中的渲染优化、资源加载、缓存策略、性能监控等全方位的性能优化最佳实践。

## 🎯 Core Web Vitals 优化

### LCP (Largest Contentful Paint) 优化
**优化最大内容绘制时间**

```typescript
// next.config.js - 优化配置
/** @type {import('next').NextConfig} */
const nextConfig = {
  // 启用自动优化
  optimizeFonts: true,
  optimizeImages: true,
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['lucide-react', '@radix-ui/react-icons'],
  },

  // 图片优化配置
  images: {
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 60,
  },

  // 压缩配置
  compress: true,
  poweredByHeader: false,

  // 构建优化
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendors',
              chunks: 'all',
            },
            common: {
              name: 'common',
              minChunks: 2,
              chunks: 'all',
              enforce: true,
            },
          },
        },
      };
    }
    return config;
  },
};

module.exports = nextConfig;
```

### 关键资源优化
**优先加载关键 CSS 和 JavaScript**

```typescript
// app/layout.tsx - 关键资源预加载
import { Inter } from 'next/font/google';
import { Preconnect } from '@/components/performance/Preconnect';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        {/* 字体预加载 */}
        <Preconnect href="https://fonts.googleapis.com" />
        <Preconnect href="https://fonts.gstatic.com" crossOrigin="" />

        {/* DNS 预解析 */}
        <link rel="dns-prefetch" href="//api.example.com" />

        {/* 关键资源内联 */}
        <style dangerouslySetInnerHTML={{
          __html: `
            /* 关键 CSS */
            .loading-skeleton {
              animation: skeleton-loading 1.5s infinite ease-in-out;
              background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
              background-size: 200% 100%;
            }
            @keyframes skeleton-loading {
              0% { background-position: 200% 0; }
              100% { background-position: -200% 0; }
            }
          `,
        }} />
      </head>

      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
}

// components/performance/Preconnect.tsx
import { Head } from 'next/head';

interface PreconnectProps {
  href: string;
  crossOrigin?: string;
}

export function Preconnect({ href, crossOrigin }: PreconnectProps) {
  return (
    <>
      <Head>
        <link
          rel="preconnect"
          href={href}
          crossOrigin={crossOrigin}
        />
      </Head>
    </>
  );
}
```

### 图片优化策略
**智能图片加载和优化**

```typescript
// components/performance/OptimizedImage.tsx
import Image from 'next/image';
import { useState } from 'react';
import { cn } from '@/lib/utils';

interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  priority?: boolean;
  className?: string;
  fallback?: string;
  onLoad?: () => void;
  onError?: () => void;
}

export function OptimizedImage({
  src,
  alt,
  width,
  height,
  priority = false,
  className,
  fallback = '/images/placeholder.jpg',
  onLoad,
  onError,
}: OptimizedImageProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  const handleLoad = () => {
    setIsLoading(false);
    onLoad?.();
  };

  const handleError = () => {
    setIsLoading(false);
    setHasError(true);
    onError?.();
  };

  return (
    <div className={cn('relative overflow-hidden', className)}>
      {/* 骨架屏 */}
      {isLoading && (
        <div className="absolute inset-0 loading-skeleton" />
      )}

      {/* 优化后的图片 */}
      <Image
        src={hasError ? fallback : src}
        alt={alt}
        width={width}
        height={height}
        priority={priority}
        className={cn(
          'transition-opacity duration-300',
          isLoading ? 'opacity-0' : 'opacity-100',
          className
        )}
        onLoad={handleLoad}
        onError={handleError}
        sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, 33vw"
        placeholder="blur"
        blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDABQALDAxMBAhMQEBQkLCRkKODw4ODw4MEB8QCQ4QDw8MDQwNDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0/wAARCAABAAEDASIAAhEBAxEB/8QAGwAAAgMBAQEAAAAAAAAAAAAAAABAwQFBgcICQoL/8QALhAAAgEDAwIEAwUFBAEBAAAAAAECAwQRBRIhMRNBQYGRRFSMhUUIjMkJBkbHRUmIzQvEkcpGissHS4v/EABkBAAMBAQEAAAAAAAAAAAAAAABAgMEBQYHCcf/aAAgDAQACAwEAAAAAAAAAAAAAAABAgMEBREhEjFhBxIT/8QAGhEAAgIDAAAAAAAAAAAAAAAAAAECAwQRFBFh/9oADAMBAAIRAxEAPwD3+gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
      />
    </div>
  );
}

// 图片懒加载 Hook
// hooks/useImageLazyLoad.ts
import { useState, useEffect, useRef } from 'react';

export function useImageLazyLoad(src: string) {
  const [imageSrc, setImageSrc] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setImageSrc(src);
            setIsLoading(false);
            observer.disconnect();
          }
        });
      },
      { threshold: 0.1 }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, [src]);

  return { imageSrc, isLoading, imgRef };
}
```

## ⚡ 代码分割和懒加载

### 路由级代码分割
**基于路由的智能代码分割**

```typescript
// next.config.js - 代码分割配置
const nextConfig = {
  webpack: (config, { isServer, dev }) => {
    if (!isServer && !dev) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          // 基础框架
          framework: {
            name: 'framework',
            test: /[\\/]node_modules[\\/](react|react-dom|scheduler|prop-types)[\\/]/,
            priority: 40,
            chunks: 'all',
          },

          // UI 库
          ui: {
            name: 'ui',
            test: /[\\/]node_modules[\\/](@radix-ui|@headless-ui|lucide-react|class-variance-authority|clsx|tailwind-merge)[\\/]/,
            priority: 30,
            chunks: 'all',
          },

          // 数据获取
          data: {
            name: 'data',
            test: /[\\/]node_modules[\\/](@tanstack\/react-query|axios|swr)[\\/]/,
            priority: 20,
            chunks: 'all',
          },

          // 图表库
          charts: {
            name: 'charts',
            test: /[\\/]node_modules[\\/](recharts|d3|chart\.js)[\\/]/,
            priority: 15,
            chunks: 'all',
          },

          // 工具库
          utils: {
            name: 'utils',
            test: /[\\/]node_modules[\\/](lodash|date-fns|moment|dayjs)[\\/]/,
            priority: 10,
            chunks: 'all',
          },

          // 供应商库
          vendor: {
            name: 'vendor',
            test: /[\\/]node_modules[\\/]/,
            priority: 5,
            chunks: 'async',
          },
        },
      };
    }

    return config;
  },
};

module.exports = nextConfig;
```

### 组件懒加载
**按需加载大型组件**

```typescript
// components/performance/LazyLoad.tsx
import dynamic from 'next/dynamic';
import { Suspense } from 'react';
import { LoadingSpinner } from './LoadingSpinner';

interface LazyLoadProps {
  component: () => Promise<React.ComponentType<any>>;
  fallback?: React.ReactNode;
  ssr?: boolean;
  [key: string]: any;
}

export function LazyLoad({
  component,
  fallback = <LoadingSpinner />,
  ssr = false,
  ...props
}: LazyLoadProps) {
  const DynamicComponent = dynamic(component, {
    loading: () => fallback,
    ssr,
  });

  return (
    <Suspense fallback={fallback}>
      <DynamicComponent {...props} />
    </Suspense>
  );
}

// 使用示例：懒加载图表组件
// components/charts/LazyChart.tsx
import { LazyLoad } from '@/components/performance/LazyLoad';

export function LazyChart({ data }: { data: any[] }) {
  return (
    <LazyLoad
      component={() => import('./BarChart')}
      fallback={<div className="h-64 bg-gray-100 animate-pulse rounded" />}
      data={data}
    />
  );
}

// 条件懒加载
// components/performance/ConditionalLoad.tsx
import { useState, useEffect } from 'react';
import { LazyLoad } from './LazyLoad';

interface ConditionalLoadProps {
  component: () => Promise<React.ComponentType<any>>;
  condition: boolean;
  fallback?: React.ReactNode;
  [key: string]: any;
}

export function ConditionalLoad({
  component,
  condition,
  fallback,
  ...props
}: ConditionalLoadProps) {
  const [shouldLoad, setShouldLoad] = useState(false);

  useEffect(() => {
    if (condition && !shouldLoad) {
      setShouldLoad(true);
    }
  }, [condition, shouldLoad]);

  if (!shouldLoad) {
    return <>{fallback}</>;
  }

  return (
    <LazyLoad
      component={component}
      fallback={fallback}
      {...props}
    />
  );
}

// 路由组件懒加载
// app/dashboard/analytics/page.tsx
import { ConditionalLoad } from '@/components/performance/ConditionalLoad';

export default function AnalyticsPage() {
  const [showCharts, setShowCharts] = useState(false);

  return (
    <div>
      <h1>Analytics Dashboard</h1>

      <button onClick={() => setShowCharts(true)}>
        Load Analytics Charts
      </button>

      <ConditionalLoad
        component={() => import('@/components/charts/AnalyticsChart')}
        condition={showCharts}
        fallback={
          <div className="h-96 bg-gray-100 animate-pulse rounded" />
        }
      />
    </div>
  );
}
```

### 模块预加载
**预加载关键模块**

```typescript
// lib/performance/preload.ts
export class Preloader {
  private static preloadedModules = new Set<string>();

  // 预加载模块
  static async preloadModule(modulePath: string): Promise<void> {
    if (this.preloadedModules.has(modulePath)) {
      return;
    }

    try {
      await import(modulePath);
      this.preloadedModules.add(modulePath);
    } catch (error) {
      console.warn(`Failed to preload module: ${modulePath}`, error);
    }
  }

  // 预加载关键模块
  static preloadCriticalModules(): Promise<void[]> {
    const criticalModules = [
      '@/components/ui/button',
      '@/components/ui/input',
      '@/lib/utils/api',
      '@/hooks/useAuth',
    ];

    return Promise.all(
      criticalModules.map(module => this.preloadModule(module))
    );
  }

  // 预加载图片
  static preloadImages(imageUrls: string[]): void {
    imageUrls.forEach(url => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.as = 'image';
      link.href = url;
      document.head.appendChild(link);
    });
  }

  // 预加载字体
  static preloadFonts(fontUrls: string[]): void {
    fontUrls.forEach(url => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.as = 'font';
      link.crossOrigin = 'anonymous';
      link.href = url;
      document.head.appendChild(link);
    });
  }
}

// 在应用启动时预加载
// app/layout.tsx
import { useEffect } from 'react';
import { Preloader } from '@/lib/performance/preload';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  useEffect(() => {
    // 预加载关键模块
    if (typeof window !== 'undefined') {
      Preloader.preloadCriticalModules().catch(console.error);

      // 预加载关键图片
      Preloader.preloadImages([
        '/images/hero-bg.jpg',
        '/images/logo.svg',
      ]);

      // 预加载字体
      Preloader.preloadFonts([
        '/fonts/inter-var.woff2',
      ]);
    }
  }, []);

  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

## 🚀 缓存策略优化

### 页面缓存
**多层缓存策略**

```typescript
// app/products/[id]/page.tsx
import { cacheLife, cacheTag } from 'next/cache';
import { getProduct } from '@/lib/api/products';

// 使用 "use cache" 显式缓存（Next.js 16：缓存不再默认开启）
export async function getProductCached(id: string) {
  'use cache'
  cacheLife('hours'); // 1小时级缓存
  cacheTag('product', `product-${id}`);
  return getProduct(id);
}

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const product = await getProductCached(id);

  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
    </div>
  );
}
```

### ISR 和数据缓存
**增量静态再生成**

```typescript
// app/api/revalidate/route.ts
import { revalidateTag, revalidatePath } from 'next/cache';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const body = await request.json();
  const { tag, path } = body;

  try {
    if (tag) {
      revalidateTag(tag);
      return NextResponse.json({ revalidated: true, tag });
    }

    if (path) {
      revalidatePath(path);
      return NextResponse.json({ revalidated: true, path });
    }

    return NextResponse.json(
      { error: 'Invalid request' },
      { status: 400 }
    );
  } catch (error) {
    return NextResponse.json(
      { error: 'Revalidation failed' },
      { status: 500 }
    );
  }
}

// 数据获取 with caching
// lib/api/data-cache.ts
interface CacheOptions {
  revalidate?: number;
  tags?: string[];
}

export async function fetchDataWithCache<T>(
  key: string,
  fetcher: () => Promise<T>,
  options: CacheOptions = {}
): Promise<T> {
  const cacheKey = JSON.stringify({ key, options });

  return fetchWithCache(cacheKey, fetcher, options);
}

async function fetchWithCache<T>(
  cacheKey: string,
  fetcher: () => Promise<T>,
  options: CacheOptions
): Promise<T> {
  // 这里可以实现 Redis 缓存或内存缓存
  const cached = await getFromCache(cacheKey);
  if (cached) {
    return cached;
  }

  const data = await fetcher();
  await setCache(cacheKey, data, options);

  return data;
}
```

### 客户端缓存
**使用 React Query 进行数据缓存**

```typescript
// hooks/useOptimizedData.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';

interface UseOptimizedDataOptions<T> {
  queryKey: string[];
  queryFn: () => Promise<T>;
  staleTime?: number;
  cacheTime?: number;
  refetchOnWindowFocus?: boolean;
  refetchOnReconnect?: boolean;
}

export function useOptimizedData<T>({
  queryKey,
  queryFn,
  staleTime = 5 * 60 * 1000, // 5分钟
  cacheTime = 10 * 60 * 1000, // 10分钟
  refetchOnWindowFocus = false,
  refetchOnReconnect = true,
}: UseOptimizedDataOptions<T>) {
  return useQuery({
    queryKey,
    queryFn,
    staleTime,
    cacheTime,
    refetchOnWindowFocus,
    refetchOnReconnect,
  });
}

// 带乐观更新的数据 Hook
export function useOptimisticData<T>(
  queryKey: string[],
  queryFn: () => Promise<T>,
  updateFn: (oldData: T, newData: Partial<T>) => T
) {
  const queryClient = useQueryClient();

  const { data } = useOptimizedData({
    queryKey,
    queryFn,
  });

  const mutation = useMutation({
    mutationFn: async (newData: Partial<T>) => {
      // 先更新本地状态
      queryClient.setQueryData<T>(queryKey, (oldData) => {
        if (!oldData) return newData as T;
        return updateFn(oldData, newData);
      });

      // 然后发送到服务器
      const response = await fetch('/api/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newData),
      });

      if (!response.ok) {
        // 回滚乐观更新
        queryClient.invalidateQueries({ queryKey });
        throw new Error('Update failed');
      }

      return response.json();
    },
    });

  return {
    data,
    mutation,
  };
}
```

## 📊 性能监控

### Web Vitals 监控
**实时性能指标监控**

```typescript
// lib/monitoring/web-vitals.ts
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

interface Metric {
  name: string;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  id: string;
  navigationType: string;
}

export class WebVitalsMonitor {
  private static metrics: Metric[] = [];

  static recordMetric(metric: Metric): void {
    this.metrics.push(metric);

    // 发送到分析服务
    this.sendToAnalytics(metric);

    // 控制台输出
    this.logMetric(metric);

    // 保持最近 100 个指标
    if (this.metrics.length > 100) {
      this.metrics = this.metrics.slice(-50);
    }
  }

  private static logMetric(metric: Metric): void {
    const { name, value, rating } = metric;
    const emoji = rating === 'good' ? '✅' : rating === 'needs-improvement' ? '⚠️' : '❌';
    console.log(`${emoji} ${name}: ${value} (${rating})`);
  }

  private static async sendToAnalytics(metric: Metric): Promise<void> {
    try {
      await fetch('/api/analytics/vitals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(metric),
      });
    } catch (error) {
      console.error('Failed to send metrics to analytics:', error);
    }
  }

  static getMetrics(): Metric[] {
    return [...this.metrics];
  }

  static getAverageMetrics(): Record<string, number> {
    const grouped = this.metrics.reduce((acc, metric) => {
      if (!acc[metric.name]) {
        acc[metric.name] = [];
      }
      acc[metric.name].push(metric.value);
      return acc;
    }, {} as Record<string, number[]>);

    return Object.entries(grouped).reduce((acc, [name, values]) => {
      acc[name] = values.reduce((sum, val) => sum + val, 0) / values.length;
      return acc;
    }, {} as Record<string, number>);
  }
}

// 在页面中使用
// app/layout.tsx
import { useEffect } from 'react';
import { WebVitalsMonitor } from '@/lib/monitoring/web-vitals';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  useEffect(() => {
    if (typeof window !== 'undefined') {
      // 监控所有 Core Web Vitals
      getCLS((metric) => WebVitalsMonitor.recordMetric(metric));
      getFID((metric) => WebVitalsMonitor.recordMetric(metric));
      getFCP((metric) => WebVitalsMonitor.recordMetric(metric));
      getLCP((metric) => WebVitalsMonitor.recordMetric(metric));
      getTTFB((metric) => WebVitalsMonitor.recordMetric(metric));
    }
  }, []);

  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

### 性能分析工具
**集成性能分析工具**

```typescript
// lib/monitoring/performance.ts
export class PerformanceMonitor {
  private static marks = new Map<string, number>();
  private static measures = new Map<string, PerformanceMeasure>();

  // 标记性能点
  static mark(name: string): void {
    if (typeof window !== 'undefined' && window.performance) {
      window.performance.mark(name);
      this.marks.set(name, Date.now());
    }
  }

  // 测量性能
  static measure(name: string, startMark?: string, endMark?: string): void {
    if (typeof window !== 'undefined' && window.performance) {
      try {
        window.performance.measure(name, startMark, endMark);

        const entries = window.performance.getEntriesByName(name, 'measure');
        const latestEntry = entries[entries.length - 1];

        if (latestEntry) {
          this.measures.set(name, latestEntry);
          console.log(`⏱️ ${name}: ${latestEntry.duration.toFixed(2)}ms`);
        }
      } catch (error) {
        console.error('Performance measure failed:', error);
      }
    }
  }

  // 获取性能指标
  static getMetrics(): Record<string, number> {
    const metrics: Record<string, number> = {};

    this.measures.forEach((measure) => {
      metrics[measure.name] = measure.duration;
    });

    return metrics;
  }

  // 性能分析报告
  static generateReport(): {
    timestamp: string;
    metrics: Record<string, number>;
    navigation: any;
    memory: any;
  } {
    if (typeof window !== 'undefined' && window.performance) {
      const navigation = window.performance.getEntriesByType('navigation')[0];
      const memory = (window as any).performance.memory;

      return {
        timestamp: new Date().toISOString(),
        metrics: this.getMetrics(),
        navigation: navigation ? {
          domContentLoaded: navigation.domContentLoadedEventEnd - navigation.navigationStart,
          loadComplete: navigation.loadEventEnd - navigation.navigationStart,
          firstPaint: window.performance.getEntriesByName('first-paint')[0]?.startTime,
          firstContentfulPaint: window.performance.getEntriesByName('first-contentful-paint')[0]?.startTime,
        } : {},
        memory: memory ? {
          usedJSHeapSize: memory.usedJSHeapSize,
          totalJSHeapSize: memory.totalJSHeapSize,
          jsHeapSizeLimit: memory.jsHeapSizeLimit,
        } : {},
      };
    }

    return {
      timestamp: new Date().toISOString(),
      metrics: {},
      navigation: {},
      memory: {},
    };
  }
}

// 性能监控 Hook
// hooks/usePerformance.ts
import { useEffect, useRef } from 'react';

export function usePerformance(componentName: string) {
  const mountTime = useRef<number>();

  useEffect(() => {
    mountTime.current = Date.now();
    PerformanceMonitor.mark(`${componentName}-mount`);

    return () => {
      PerformanceMonitor.mark(`${componentName}-unmount`);
      PerformanceMonitor.measure(
        `${componentName}-lifecycle`,
        `${componentName}-mount`,
        `${componentName}-unmount`
      );

      if (mountTime.current) {
        const duration = Date.now() - mountTime.current;
        console.log(`⏱️ ${componentName} mounted for: ${duration}ms`);
      }
    };
  }, [componentName]);

  const startTiming = (name: string) => {
    PerformanceMonitor.mark(`${componentName}-${name}-start`);
  };

  const endTiming = (name: string) => {
    PerformanceMonitor.mark(`${componentName}-${name}-end`);
    PerformanceMonitor.measure(
      `${componentName}-${name}`,
      `${componentName}-${name}-start`,
      `${componentName}-${name}-end`
    );
  };

  return {
    startTiming,
    endTiming,
  };
}
```

## 🎨 渲染优化

### React 优化模式
**优化 React 组件渲染**

```typescript
// hooks/useMemoizedComponent.ts
import { useMemo, useCallback } from 'react';

interface UseMemoizedComponentProps<T, P> {
  component: React.ComponentType<T>;
  props: T;
  memoProps?: (prev: P, next: P) => boolean;
  deps?: any[];
}

export function useMemoizedComponent<T, P = {}>({
  component: Component,
  props,
  memoProps,
  deps = [],
}: UseMemoizedComponentProps<T, P>) {
  return useMemo(() => {
    const MemoizedComponent = React.memo(Component, memoProps);
    return <MemoizedComponent {...props} />;
  }, [Component, props, memoProps, ...deps]);
}

// 虚拟列表优化
// components/lists/VirtualizedList.tsx
import { useMemo, useState, useEffect, useRef } from 'react';

interface VirtualizedListProps<T> {
  items: T[];
  itemHeight: number;
  containerHeight: number;
  renderItem: (item: T, index: number) => React.ReactNode;
  overscan?: number;
}

export function VirtualizedList<T>({
  items,
  itemHeight,
  containerHeight,
  renderItem,
  overscan = 5,
}: VirtualizedListProps<T>) {
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  const visibleItems = useMemo(() => {
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(
      items.length - 1,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
    );

    return items.slice(startIndex, endIndex + 1).map((item, index) => ({
      item,
      index: startIndex + index,
      style: {
        position: 'absolute',
        top: (startIndex + index) * itemHeight,
        left: 0,
        right: 0,
        height: itemHeight,
      },
    }));
  }, [items, itemHeight, containerHeight, scrollTop, overscan]);

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  }, []);

  const totalHeight = items.length * itemHeight;

  return (
    <div
      ref={containerRef}
      style={{
        height: containerHeight,
        overflow: 'auto',
        position: 'relative',
      }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        {visibleItems.map(({ item, index, style }) => (
          <div key={index} style={style}>
            {renderItem(item, index)}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 状态优化
**优化状态管理性能**

```typescript
// hooks/useOptimizedState.ts
import { useState, useCallback, useMemo } from 'react';

interface StateUpdater<T> {
  (updater: T | ((prev: T) => T)): void;
}

export function useOptimizedState<T>(
  initialState: T,
  areEqual?: (prev: T, next: T) => boolean
): [T, StateUpdater<T>] {
  const [state, setState] = useState(initialState);

  const setStateOptimized = useCallback(
    (updater: T | ((prev: T) => T)) => {
      setState((prevState) => {
        const newState = typeof updater === 'function' ? updater(prevState) : updater;

        if (areEqual && areEqual(prevState, newState)) {
          return prevState;
        }

        return newState;
      });
    },
    [areEqual]
  );

  return [state, setStateOptimized];
}

// 选择器优化
export function useSelector<T, R>(
  state: T,
  selector: (state: T) => R,
  equalityFn?: (a: R, b: R) => boolean
): R {
  return useMemo(() => {
    const selected = selector(state);
    return selected;
  }, [state, selector, equalityFn]);
}

// 使用示例
function UserProfile() {
  const [user, setUser] = useOptimizedState(
    { id: '', name: '', email: '' },
    (prev, next) => prev.id === next.id && prev.name === next.name && prev.email === next.email
  );

  const displayName = useSelector(
    user,
    (user) => user.name || user.email || 'Anonymous',
    (a, b) => a === b
  );

  return (
    <div>
      <h1>{displayName}</h1>
      <button onClick={() => setUser({ ...user, name: 'New Name' })}>
        Update Name
      </button>
    </div>
  );
}
```

## 📱 Bundle 优化

### Bundle 分析
**分析和优化打包结果**

```typescript
// scripts/analyze-bundle.js
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const nextConfig = require('../next.config.js');

async function analyzeBundle() {
  // 使用 Next.js 的分析功能
  const { execSync } = require('child_process');

  try {
    console.log('🔍 Analyzing Next.js bundle...');

    // 构建并分析
    execSync('ANALYZE=true npm run build', { stdio: 'inherit' });

    console.log('📊 Bundle analysis complete!');
  } catch (error) {
    console.error('❌ Bundle analysis failed:', error);
  }
}

// package.json scripts
{
  "scripts": {
    "build": "next build",
    "build:analyze": "ANALYZE=true next build",
    "analyze-bundle": "node scripts/analyze-bundle.js"
  }
}

// 自定义 Bundle 分析
// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer(nextConfig);
```

### Tree Shaking 优化
**消除未使用的代码**

```typescript
// lib/utils/index.ts - 确保正确导出
export * from './api';
export * from './validation';
export * from './format';
export * from './date';

// 只导出需要的内容
// lib/utils/api.ts
export const apiClient = {
  get: async (url: string) => fetch(url).then(res => res.json()),
  post: async (url: string, data: any) =>
    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(res => res.json()),
};

// 环境变量配置
// next.config.js
module.exports = {
  webpack: (config) => {
    config.optimization = {
      ...config.optimization,
      usedExports: true,
      sideEffects: false,
    };
    return config;
  },
};
```

## 📋 性能检查清单

### Core Web Vitals
- [ ] LCP < 2.5s (75% of loads)
- [ ] FID < 100ms (95% of loads)
- [ ] CLS < 0.1 (95% of loads)
- [ ] FCP < 1.8s
- [ ] TTI < 3.8s

### 代码优化
- [ ] 实施代码分割
- [ ] 使用组件懒加载
- [ ] 优化 Bundle 大小
- [ ] 启用 Tree Shaking
- [ ] 移除未使用代码
- [ ] 压缩和混淆

### 资源优化
- [ ] 优化图片加载
- [ ] 使用现代图片格式
- [ ] 实施资源缓存
- [ ] 预加载关键资源
- [ ] 优化字体加载
- [ ] 压缩静态资源

### 缓存策略
- [ ] 配置适当的缓存头
- [ ] 使用 Service Worker
- [ ] 实施 ISR/SSG
- [ ] 优化 API 缓存
- [ ] 使用 CDN
- [ ] 实施浏览器缓存

### 监控分析
- [ ] 集成 Web Vitals 监控
- [ ] 设置性能预算
- [ ] 实施实时监控
- [ ] 定期性能分析
- [ ] 监控错误率
- [ ] 用户体验追踪

## 📖 总结

性能优化是一个持续的过程，需要多方面的优化策略：

### 核心指标：
1. **Core Web Vitals**: LCP, FID, CLS
2. **First Paint**: 首次绘制时间
3. **Time to Interactive**: 可交互时间
4. **Cumulative Layout Shift**: 累积布局偏移
5. **Bundle Size**: 包大小和加载时间

### 优化策略：
1. **渲染优化**: 组件优化、虚拟化
2. **资源优化**: 图片、字体、缓存
3. **代码优化**: 分割、懒加载、Tree Shaking
4. **网络优化**: CDN、压缩、预加载
5. **监控分析**: 性能监控、分析工具

### 实施要点：
1. **测量优先**: 先测量再优化
2. **影响最大**: 优先优化影响最大的问题
3. **持续监控**: 建立性能监控体系
4. **定期评估**: 定期评估性能表现
5. **用户反馈**: 关注用户体验反馈

### 工具支持：
1. **Lighthouse**: 综合性能评估
2. **WebPageTest**: 详细性能分析
3. **Bundle Analyzer**: 打包分析
4. **Chrome DevTools**: 开发工具分析
5. **RUM**: 真实用户监控

## 🔄 文档交叉引用

### 相关文档
- 📄 **[打包优化](./02-bundle-optimization.md)**: 代码分割和打包优化策略
- 📄 **[测试工具](../development-tools/01-testing-tools.md)**: 性能测试和回归检测
- 📄 **[样式工具](../development-tools/02-styling-tools.md)**: CSS优化和样式性能
- 📄 **[包管理器](../development-tools/03-package-managers.md)**: 依赖优化和版本控制
- 📄 **[调试工具](../development-tools/04-debugging-tools.md)**: 性能调试和分析工具

### 参考章节
- 📖 **[Core Web Vitals优化](#core-web-vitals-优化)**: 用户体验指标优化
- 📖 **[代码分割](#代码分割和懒加载)**: 按需加载策略
- 📖 **[缓存策略](#缓存策略优化)**: 多层缓存体系
- 📖 **[性能监控](#性能监控)**: 实时性能指标追踪
- 📖 **[渲染优化](#渲染优化)**: React组件优化模式

---

## 📝 总结

### 核心要点回顾
1. **Core Web Vitals**: LCP、FID、CLS等关键指标的优化策略
2. **代码分割**: 路由级、组件级、模块级的智能分割方案
3. **缓存策略**: 浏览器缓存、CDN缓存、服务端缓存的多层优化
4. **性能监控**: Web Vitals监控、性能分析、用户体验追踪
5. **渲染优化**: React组件优化、虚拟化、状态管理的最佳实践

### 学习成果检查
- [ ] 能够优化Core Web Vitals指标达到Google推荐标准
- [ ] 掌握代码分割和懒加载的最佳实践
- [ ] 熟练配置多层缓存策略提升应用性能
- [ ] 能够建立完善的性能监控和分析体系
- [ ] 理解React渲染优化和状态管理的性能原则

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
- **Web.dev**: [Core Web Vitals](https://web.dev/vitals/) - 用户体验指标指南
- **Next.js**: [Performance Optimization](https://nextjs.org/docs/advanced-features/measuring-performance) - Next.js性能优化
- **React**: [Optimization](https://reactjs.org/docs/optimizing-performance.html) - React性能优化
- **Lighthouse**: [Performance Auditing](https://developer.chrome.com/docs/lighthouse/performance/) - 性能审计工具

### 快速参考
- **WebPageTest**: [在线性能测试](https://www.webpagetest.org/) - 详细性能分析
- **Bundle Analyzer**: [webpack-bundle-analyzer](https://github.com/webpack-contrib/webpack-bundle-analyzer) - 打包分析工具
- **性能预算**: [Performance Budgets](https://web.dev/performance-budgets-101/) - 性能预算设置
- **RUM工具**: [Real User Monitoring](https://web.dev/vitals-tools/) - 真实用户监控

---

**文档状态**: ✅ 已完成 | 🚧 进行中 | 📋 计划中
**最后更新**: 2025年10月
**版本**: v1.0.0