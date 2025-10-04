# Next.js 优化速查手册

## 📚 概述

Next.js 15 提供了丰富的优化工具和技术，包括静态生成、增量静态再生、图像优化、性能监控等。本手册涵盖了所有优化相关的功能和最佳实践。

## 🚀 渲染优化

### 静态生成 (SSG)
**构建时生成静态页面**

```typescript
// app/posts/[slug]/page.tsx
interface PostPageProps {
  params: {
    slug: string;
  };
}

// 静态生成页面
export default async function PostPage({ params }: PostPageProps) {
  const post = await getPostBySlug(params.slug);

  if (!post) {
    notFound();
  }

  return (
    <article>
      <h1>{post.title}</h1>
      <p>By {post.author} on {new Date(post.publishedAt).toLocaleDateString()}</p>
      <div dangerouslySetInnerHTML={{ __html: post.content }} />
    </article>
  );
}

// 生成静态参数
export async function generateStaticParams() {
  const posts = await getAllPosts();

  return posts.map((post: Post) => ({
    slug: post.slug,
  }));
}

// 生成静态元数据
export async function generateMetadata({ params }: PostPageProps) {
  const post = await getPostBySlug(params.slug);

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: post.coverImage ? [post.coverImage] : [],
    },
    alternates: {
      canonical: `https://yourdomain.com/posts/${params.slug}`,
    },
  };
}

// 数据获取函数
async function getAllPosts(): Promise<Post[]> {
  // 实际的数据获取逻辑
  const res = await fetch('https://api.example.com/posts');
  return res.json();
}

async function getPostBySlug(slug: string): Promise<Post | null> {
  // 实际的数据获取逻辑
  const res = await fetch(`https://api.example.com/posts/${slug}`);
  if (!res.ok) return null;
  return res.json();
}
```

### 增量静态再生 (ISR)
**按需重新生成静态页面**

```typescript
// app/products/page.tsx
export const revalidate = 3600; // 1小时后重新验证

export default async function ProductsPage() {
  const products = await getProducts();

  return (
    <div>
      <h1>Products</h1>
      <ProductGrid products={products} />
    </div>
  );
}

// 使用 fetch 的 revalidate 选项
async function getProducts() {
  const res = await fetch('https://api.example.com/products', {
    next: {
      revalidate: 3600, // 1小时
    },
  });

  if (!res.ok) {
    throw new Error('Failed to fetch products');
  }

  return res.json();
}

// 基于标签的重新验证
async function getFeaturedProducts() {
  const res = await fetch('https://api.example.com/products/featured', {
    next: {
      tags: ['products', 'featured'],
    },
  });

  return res.json();
}

// 手动重新验证的 API 端点
// app/api/revalidate/route.ts
import { revalidateTag, revalidatePath } from 'next/cache';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const { tag, path } = await request.json();
  const secret = request.headers.get('authorization');

  // 验证密钥
  if (secret !== `Bearer ${process.env.REVALIDATE_SECRET}`) {
    return NextResponse.json({ error: 'Invalid secret' }, { status: 401 });
  }

  try {
    if (tag) {
      revalidateTag(tag);
      return NextResponse.json({ revalidated: true, tag });
    }

    if (path) {
      revalidatePath(path);
      return NextResponse.json({ revalidated: true, path });
    }

    return NextResponse.json({ error: 'Invalid request' }, { status: 400 });
  } catch (error) {
    return NextResponse.json({ error: 'Revalidation failed' }, { status: 500 });
  }
}
```

### 按需渲染
**根据请求动态选择渲染策略**

```typescript
// app/dashboard/page.tsx
import { headers } from 'next/headers';

export default async function DashboardPage() {
  const headersList = headers();
  const userAgent = headersList.get('user-agent') || '';
  const isBot = /bot|crawler|spider|crawling/i.test(userAgent);

  // 如果是爬虫，使用静态渲染
  if (isBot) {
    return <StaticDashboardContent />;
  }

  // 否则使用动态渲染
  return <DynamicDashboardContent />;
}

// 静态内容组件
async function StaticDashboardContent() {
  const data = await getCachedDashboardData();
  return <DashboardView data={data} isStatic={true} />;
}

// 动态内容组件
async function DynamicDashboardContent() {
  const data = await getRealTimeDashboardData();
  return <DashboardView data={data} isStatic={false} />;
}
```

## 🖼️ 图像优化

### next/image 组件
**自动图像优化和格式转换**

```typescript
import Image from 'next/image';

// 基础用法
function ProductImage({ product }: { product: Product }) {
  return (
    <Image
      src={product.imageUrl}
      alt={product.name}
      width={300}
      height={200}
      priority // 高优先级加载
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,...base64数据..."
    />
  );
}

// 响应式图像
function ResponsiveImage({ image }: { image: ImageData }) {
  return (
    <div className="relative w-full h-96">
      <Image
        src={image.url}
        alt={image.alt}
        fill
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        style={{ objectFit: 'cover' }}
        placeholder="blur"
        blurDataURL={image.blurDataURL}
      />
    </div>
  );
}

// 远程图像配置
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'example.com',
        pathname: '/images/**',
      },
      {
        protocol: 'https',
        hostname: 'cdn.example.com',
      },
    ],
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
};

module.exports = nextConfig;

// 动态图像生成
export async function generateStaticParams() {
  const products = await getProducts();

  return products.map((product: Product) => ({
    slug: product.slug,
  }));
}

export async function generateMetadata({ params }: { params: { slug: string } }) {
  const product = await getProduct(params.slug);

  return {
    openGraph: {
      images: [
        {
          url: product.imageUrl,
          width: 1200,
          height: 630,
          alt: product.name,
        },
      ],
    },
  };
}
```

### 自定义图像加载器
**集成 CDN 或外部图像服务**

```typescript
// lib/image-loader.ts
import { ImageLoader } from 'next/image';

export const cloudinaryLoader: ImageLoader = ({ src, width, quality }) => {
  const params = [
    'f_auto',
    'c_limit',
    `w_${width}`,
    `q_${quality || 'auto'}`,
  ];

  return `https://res.cloudinary.com/demo/image/upload/${params.join(',')}/${src}`;
};

export const imgixLoader: ImageLoader = ({ src, width, quality }) => {
  return `https://your-domain.imgix.net/${src}?w=${width}&q=${quality || 75}`;
};

// 在组件中使用
function OptimizedImage({ src, alt, ...props }) {
  return (
    <Image
      loader={cloudinaryLoader}
      src={src}
      alt={alt}
      {...props}
    />
  );
}

// 动态加载器选择
function SmartImage({ src, alt, provider = 'nextjs', ...props }) {
  const loaders = {
    nextjs: undefined, // 使用默认 Next.js 加载器
    cloudinary: cloudinaryLoader,
    imgix: imgixLoader,
  };

  return (
    <Image
      loader={loaders[provider]}
      src={src}
      alt={alt}
      {...props}
    />
  );
}
```

## ⚡ 性能优化

### 代码分割
**动态导入和懒加载**

```typescript
// 动态导入组件
import dynamic from 'next/dynamic';

// 基础动态导入
const DynamicComponent = dynamic(() => import('../components/HeavyComponent'));

// 带加载状态的动态导入
const DynamicComponentWithLoading = dynamic(
  () => import('../components/HeavyComponent'),
  {
    loading: () => <p>Loading component...</p>,
    ssr: false, // 禁用服务器端渲染
  }
);

// 带自定义加载组件
const CustomLoadingComponent = () => (
  <div className="flex items-center justify-center h-32">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
  </div>
);

const LazyDashboard = dynamic(
  () => import('../components/Dashboard'),
  {
    loading: CustomLoadingComponent,
  }
);

// 条件动态导入
function ConditionalComponent({ showHeavy }: { showHeavy: boolean }) {
  if (showHeavy) {
    const HeavyComponent = dynamic(() => import('../components/HeavyComponent'));
    return <HeavyComponent />;
  }

  return <LightComponent />;
}

// 在页面中使用
function DashboardPage() {
  const [showAnalytics, setShowAnalytics] = useState(false);

  return (
    <div>
      <h1>Dashboard</h1>

      <button onClick={() => setShowAnalytics(!showAnalytics)}>
        {showAnalytics ? 'Hide' : 'Show'} Analytics
      </button>

      {showAnalytics && (
        <Suspense fallback={<div>Loading analytics...</div>}>
          <LazyDashboard />
        </Suspense>
      )}
    </div>
  );
}
```

### 缓存策略
**多层级缓存优化**

```typescript
// lib/cache.ts
import { cache } from 'react';

// 内存缓存
const memoryCache = new Map<string, { data: any; expiry: number }>();

function setMemoryCache(key: string, data: any, ttl: number = 300000) { // 5分钟
  memoryCache.set(key, {
    data,
    expiry: Date.now() + ttl,
  });
}

function getMemoryCache(key: string): any | null {
  const cached = memoryCache.get(key);
  if (cached && cached.expiry > Date.now()) {
    return cached.data;
  }
  memoryCache.delete(key);
  return null;
}

// React 缓存函数
export const getCachedData = cache(async (key: string, fetcher: () => Promise<any>) => {
  // 先检查内存缓存
  const memoryData = getMemoryCache(key);
  if (memoryData) {
    return memoryData;
  }

  // React 缓存
  const data = await fetcher();

  // 存储到内存缓存
  setMemoryCache(key, data);

  return data;
});

// 使用示例
async function getProducts() {
  return getCachedData(
    'products-all',
    async () => {
      const res = await fetch('https://api.example.com/products', {
        next: { revalidate: 3600 }, // Next.js 缓存
      });
      return res.json();
    }
  );
}

// 分层缓存策略
async function getProductsWithCache() {
  const cacheKey = 'products-with-details';

  return getCachedData(cacheKey, async () => {
    // 并行获取数据
    const [products, categories, reviews] = await Promise.all([
      fetch('https://api.example.com/products').then(res => res.json()),
      fetch('https://api.example.com/categories').then(res => res.json()),
      fetch('https://api.example.com/reviews').then(res => res.json()),
    ]);

    return {
      products,
      categories,
      reviews,
      lastUpdated: Date.now(),
    };
  });
}

// 缓存失效
export function invalidateCache(key: string) {
  memoryCache.delete(key);
}
```

### 包大小优化
**减少 JavaScript 包大小**

```typescript
// tree-shaking 友好的导入
import { get, post } from 'lodash-es'; // 而不是 import _ from 'lodash'

// 使用具体的 API
import { useState, useEffect } from 'react';

// 条件导入
function loadChartLibrary() {
  return import('chart.js').then((module) => {
    return module.default;
  });
}

// 图表组件懒加载
const ChartComponent = dynamic(() => import('../components/Chart'), {
  ssr: false,
});

// 分析包大小
// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    optimizePackageImports: ['lucide-react', '@radix-ui/react-icons'],
  },
  webpack: (config, { isServer }) => {
    // 减少包大小
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }

    return config;
  },
};

module.exports = withBundleAnalyzer(nextConfig);
```

## 🔧 构建优化

### Turbopack 配置
**使用 Turbopack 加速构建**

```typescript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    turbo: {
      rules: {
        '*.svg': [
          {
            loaders: ['@svgr/webpack'],
            as: '*.js',
          },
        ],
      },
    },
  },
  // Turbopack 配置
  turbo: {
    // 自定义解析规则
    resolveAlias: {
      '@': './src',
      '@components': './src/components',
      '@lib': './src/lib',
    },
    // 排除某些包
    exclude: ['@storybook/*'],
  },
};

// 使用 Turbopack 开发
// package.json scripts
{
  "scripts": {
    "dev": "next dev --turbo",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }
}

// Turbopack 监控配置
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

### SWC 配置
**自定义 SWC 编译选项**

```typescript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    swcMinify: true,
    swcPlugins: [
      ['@swc/plugin-emotion', {}],
      ['@swc/plugin-styled-components', {}],
    ],
  },
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
    styledComponents: true,
    emotion: true,
  },
  // 自定义 SWC 配置
  swcMinify: true,
  reactStrictMode: true,
};

// .swcrc
{
  "jsc": {
    "parser": {
      "syntax": "typescript",
      "tsx": true,
      "decorators": true
    },
    "transform": {
      "react": {
        "runtime": "automatic",
        "development": process.env.NODE_ENV === "development",
        "refresh": true
      }
    },
    "target": "es2020",
    "loose": true,
    "externalHelpers": true
  },
  "env": {
    "development": {
      "jsc": {
        "transform": {
          "react": {
            "development": true,
            "refresh": true
          }
        }
      }
    }
  }
}
```

## 📊 性能监控

### Web Vitals 监控
**监控 Core Web Vitals**

```typescript
// app/layout.tsx
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/next';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}

// lib/vitals.ts
export function reportWebVitals(metric: any) {
  // 发送到分析服务
  if (process.env.NODE_ENV === 'production') {
    fetch('/api/vitals', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(metric),
    });
  } else {
    console.log('Web Vitals:', metric);
  }
}

// app/api/vitals/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const vitals = await request.json();

  // 存储到数据库或发送到监控服务
  await storeVitals(vitals);

  return NextResponse.json({ success: true });
}

// 自定义性能监控
// lib/performance-monitor.ts
export class PerformanceMonitor {
  static observeNavigation() {
    if (typeof window !== 'undefined') {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'navigation') {
            this.reportNavigationTiming(entry as PerformanceNavigationTiming);
          }
        }
      });

      observer.observe({ entryTypes: ['navigation'] });
    }
  }

  static reportNavigationTiming(entry: PerformanceNavigationTiming) {
    const metrics = {
      domContentLoaded: entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart,
      loadComplete: entry.loadEventEnd - entry.loadEventStart,
      firstPaint: 0,
      firstContentfulPaint: 0,
    };

    // 获取绘制时间
    const paintEntries = performance.getEntriesByType('paint');
    paintEntries.forEach((paint) => {
      if (paint.name === 'first-paint') {
        metrics.firstPaint = paint.startTime;
      }
      if (paint.name === 'first-contentful-paint') {
        metrics.firstContentfulPaint = paint.startTime;
      }
    });

    this.sendMetrics(metrics);
  }

  static sendMetrics(metrics: any) {
    fetch('/api/performance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...metrics,
        url: window.location.href,
        userAgent: navigator.userAgent,
        timestamp: Date.now(),
      }),
    });
  }
}

// 在组件中使用
'use client';

import { useEffect } from 'react';
import { PerformanceMonitor } from '../lib/performance-monitor';

function PerformanceTrackingComponent() {
  useEffect(() => {
    PerformanceMonitor.observeNavigation();
  }, []);

  return <div>{/* 组件内容 */}</div>;
}
```

### 运行时性能监控
**监控应用运行时性能**

```typescript
// lib/runtime-monitor.ts
export class RuntimeMonitor {
  private static instance: RuntimeMonitor;
  private metrics: any[] = [];
  private observers: PerformanceObserver[] = [];

  static getInstance(): RuntimeMonitor {
    if (!this.instance) {
      this.instance = new RuntimeMonitor();
    }
    return this.instance;
  }

  startMonitoring() {
    this.observeLongTasks();
    this.observeLayoutShift();
    this.observeLCP();
    this.observeINP();
  }

  private observeLongTasks() {
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.recordMetric({
            type: 'long-task',
            duration: entry.duration,
            startTime: entry.startTime,
          });
        }
      });

      observer.observe({ entryTypes: ['longtask'] });
      this.observers.push(observer);
    } catch (e) {
      console.warn('Long tasks not supported');
    }
  }

  private observeLayoutShift() {
    try {
      let clsValue = 0;
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!(entry as any).hadRecentInput) {
            clsValue += (entry as any).value;
          }
        }

        this.recordMetric({
          type: 'cls',
          value: clsValue,
        });
      });

      observer.observe({ entryTypes: ['layout-shift'] });
      this.observers.push(observer);
    } catch (e) {
      console.warn('Layout shift not supported');
    }
  }

  private observeLCP() {
    try {
      const observer = new PerformanceObserver((list) => {
        const lastEntry = list.getEntries().pop();
        if (lastEntry) {
          this.recordMetric({
            type: 'lcp',
            value: lastEntry.startTime,
            element: (lastEntry as any).element?.tagName,
          });
        }
      });

      observer.observe({ entryTypes: ['largest-contentful-paint'] });
      this.observers.push(observer);
    } catch (e) {
      console.warn('LCP not supported');
    }
  }

  private observeINP() {
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.recordMetric({
            type: 'inp',
            value: (entry as any).duration,
            name: (entry as any).name,
          });
        }
      });

      observer.observe({ entryTypes: ['interaction'] });
      this.observers.push(observer);
    } catch (e) {
      console.warn('INP not supported');
    }
  }

  private recordMetric(metric: any) {
    this.metrics.push({
      ...metric,
      timestamp: Date.now(),
      url: typeof window !== 'undefined' ? window.location.href : '',
    });

    // 保持最近100个指标
    if (this.metrics.length > 100) {
      this.metrics = this.metrics.slice(-50);
    }

    // 发送到服务器
    this.sendMetric(metric);
  }

  private async sendMetric(metric: any) {
    try {
      await fetch('/api/performance-metrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(metric),
      });
    } catch (error) {
      console.warn('Failed to send metric:', error);
    }
  }

  getMetrics() {
    return [...this.metrics];
  }

  stopMonitoring() {
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
  }
}

// 在应用中使用
// app/components/PerformanceMonitor.tsx
'use client';

import { useEffect } from 'react';
import { RuntimeMonitor } from '../lib/runtime-monitor';

export function PerformanceMonitor() {
  useEffect(() => {
    if (process.env.NODE_ENV === 'production') {
      const monitor = RuntimeMonitor.getInstance();
      monitor.startMonitoring();

      return () => {
        monitor.stopMonitoring();
      };
    }
  }, []);

  return null;
}
```

## 📋 优化检查清单

### 构建时优化
- [ ] 使用静态生成 (SSG) 适用于静态内容
- [ ] 配置增量静态再生 (ISR) 适用于定期更新的内容
- [ ] 启用图像优化和 WebP/AVIF 格式
- [ ] 配置代码分割和懒加载
- [ ] 优化包大小，移除未使用的代码
- [ ] 使用 Turbopack 加速开发构建

### 运行时优化
- [ ] 实施多层级缓存策略
- [ ] 使用 React.memo 和 useMemo 优化组件
- [ ] 配置 Service Worker 缓存
- [ ] 优化 API 响应时间
- [ ] 使用 CDN 分发静态资源
- [ ] 启用 Gzip/Brotli 压缩

### 性能监控
- [ ] 集成 Web Vitals 监控
- [ ] 设置 Core Web Vitals 警报
- [ ] 监控运行时性能指标
- [ ] 定期进行性能审计
- [ ] 分析真实用户监控 (RUM) 数据
- [ ] 设置性能预算

### Core Web Vitals 优化
- [ ] LCP (最大内容绘制): < 2.5s
- [ ] FID (首次输入延迟): < 100ms
- [ ] CLS (累积布局偏移): < 0.1
- [ ] INP (交互到下一次绘制): < 200ms

## 📖 总结

Next.js 15 提供了全面的优化工具和策略：

1. **渲染优化**: SSG, ISR, SSR 策略选择
2. **图像优化**: 自动格式转换和尺寸优化
3. **代码优化**: 动态导入和树摇
4. **缓存优化**: 多层缓存策略
5. **构建优化**: Turbopack 和 SWC 配置
6. **性能监控**: Web Vitals 和运行时监控

通过合理使用这些优化技术，你可以构建快速、高效的 Next.js 应用，提供优秀的用户体验。