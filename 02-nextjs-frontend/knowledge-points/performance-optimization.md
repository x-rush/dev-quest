# 性能优化速查手册

## Core Web Vitals 优化

### LCP (Largest Contentful Paint)

#### 图片优化

```typescript
// 1. 使用 Next.js Image 组件
import Image from 'next/image';

function ProductImage({ src, alt, width, height }) {
  return (
    <div className="image-container">
      <Image
        src={src}
        alt={alt}
        width={width}
        height={height}
        priority={true} // 关键图片优先加载
        placeholder="blur"
        blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        style={{ maxWidth: '100%', height: 'auto' }}
      />
    </div>
  );
}

// 2. 图片预加载
function preloadImages() {
  if (typeof window !== 'undefined') {
    const images = [
      '/hero-image.jpg',
      '/product-1.jpg',
      '/product-2.jpg'
    ];

    images.forEach(src => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.as = 'image';
      link.href = src;
      document.head.appendChild(link);
    });
  }
}

// 3. 响应式图片
function ResponsiveImage({ image }) {
  return (
    <Image
      src={image.url}
      alt={image.alt}
      width={image.width}
      height={image.height}
      sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
      srcSet={`
        ${image.url}?w=300 300w,
        ${image.url}?w=600 600w,
        ${image.url}?w=900 900w,
        ${image.url}?w=1200 1200w
      `}
    />
  );
}
```

#### 字体优化

```typescript
// 1. 使用 Next.js 字体优化
import { Inter, Roboto } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
  weight: ['400', '500', '600', '700'],
});

const roboto = Roboto({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-roboto',
  weight: ['300', '400', '500', '700'],
});

// 2. 字体预加载
function preloadFonts() {
  if (typeof window !== 'undefined') {
    const fontLink = document.createElement('link');
    fontLink.rel = 'preload';
    fontLink.as = 'font';
    fontLink.href = '/fonts/custom-font.woff2';
    fontLink.crossOrigin = 'anonymous';
    document.head.appendChild(fontLink);
  }
}

// 3. CSS 变量优化
const fontStyles = `
  :root {
    --font-primary: ${inter.style.fontFamily};
    --font-secondary: ${roboto.style.fontFamily};
  }

  body {
    font-family: var(--font-primary);
  }

  h1, h2, h3 {
    font-family: var(--font-secondary);
  }
`;
```

#### 关键 CSS 内联

```typescript
// layout.tsx
export default function RootLayout({ children }) {
  return (
    <html>
      <head>
        <style jsx global>{`
          /* 关键 CSS */
          body {
            margin: 0;
            font-family: var(--font-primary);
            line-height: 1.6;
          }

          .hero-section {
            min-height: 80vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          }
        `}</style>
      </head>
      <body>{children}</body>
    </html>
  );
}
```

### INP (Interaction to Next Paint)

#### 事件处理优化

```typescript
// 1. 使用防抖和节流
import { useCallback, useRef } from 'react';

function useDebounce<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const timeoutRef = useRef<NodeJS.Timeout>();

  return useCallback(
    (...args: Parameters<T>) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      timeoutRef.current = setTimeout(() => {
        callback(...args);
      }, delay);
    },
    [callback, delay]
  ) as T;
}

function useThrottle<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const lastCallRef = useRef<number>(0);

  return useCallback(
    (...args: Parameters<T>) => {
      const now = Date.now();
      if (now - lastCallRef.current >= delay) {
        lastCallRef.current = now;
        callback(...args);
      }
    },
    [callback, delay]
  ) as T;
}

// 使用示例
function SearchComponent() {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce((term: string) => {
    // 执行搜索
    performSearch(term);
  }, 300);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const term = e.target.value;
    setSearchTerm(term);
    debouncedSearch(term);
  };

  return (
    <input
      type="text"
      value={searchTerm}
      onChange={handleInputChange}
      placeholder="Search..."
    />
  );
}
```

#### 虚拟滚动

```typescript
import { useState, useEffect, useRef, useCallback } from 'react';

interface VirtualScrollProps {
  items: any[];
  itemHeight: number;
  containerHeight: number;
  renderItem: (item: any, index: number) => React.ReactNode;
}

function VirtualScroll({
  items,
  itemHeight,
  containerHeight,
  renderItem,
}: VirtualScrollProps) {
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleScroll = useCallback(() => {
    if (containerRef.current) {
      setScrollTop(containerRef.current.scrollTop);
    }
  }, []);

  useEffect(() => {
    const container = containerRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, [handleScroll]);

  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(
    startIndex + Math.ceil(containerHeight / itemHeight) + 1,
    items.length - 1
  );

  const offsetY = startIndex * itemHeight;
  const visibleItems = items.slice(startIndex, endIndex + 1);

  return (
    <div
      ref={containerRef}
      style={{
        height: containerHeight,
        overflow: 'auto',
        position: 'relative',
      }}
    >
      <div
        style={{
          height: items.length * itemHeight,
          position: 'relative',
        }}
      >
        <div
          style={{
            position: 'absolute',
            top: offsetY,
            width: '100%',
          }}
        >
          {visibleItems.map((item, index) => (
            <div
              key={startIndex + index}
              style={{ height: itemHeight }}
            >
              {renderItem(item, startIndex + index)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// 使用示例
function LongList() {
  const items = Array.from({ length: 10000 }, (_, i) => ({
    id: i,
    name: `Item ${i}`,
  }));

  return (
    <VirtualScroll
      items={items}
      itemHeight={50}
      containerHeight={400}
      renderItem={(item) => (
        <div style={{ padding: '10px', borderBottom: '1px solid #eee' }}>
          {item.name}
        </div>
      )}
    />
  );
}
```

#### 时间切片

```typescript
import { useCallback, useRef } from 'react';

function useTimeSlice<T>(
  items: T[],
  processItem: (item: T) => void,
  chunkSize: number = 50
) {
  const isProcessingRef = useRef(false);
  const currentIndexRef = useRef(0);

  const processChunk = useCallback(() => {
    if (currentIndexRef.current >= items.length) {
      isProcessingRef.current = false;
      return;
    }

    const endIndex = Math.min(
      currentIndexRef.current + chunkSize,
      items.length
    );

    // 处理当前批次
    for (let i = currentIndexRef.current; i < endIndex; i++) {
      processItem(items[i]);
    }

    currentIndexRef.current = endIndex;

    // 使用 requestAnimationFrame 继续处理下一批次
    if (currentIndexRef.current < items.length) {
      requestAnimationFrame(processChunk);
    } else {
      isProcessingRef.current = false;
    }
  }, [items, processItem, chunkSize]);

  const startProcessing = useCallback(() => {
    if (!isProcessingRef.current) {
      isProcessingRef.current = true;
      currentIndexRef.current = 0;
      requestAnimationFrame(processChunk);
    }
  }, [processChunk]);

  return { startProcessing };
}

// 使用示例
function LargeDataProcessor() {
  const largeData = Array.from({ length: 10000 }, (_, i) => ({
    id: i,
    data: `Data ${i}`,
  }));

  const [processedItems, setProcessedItems] = useState<any[]>([]);

  const processData = useCallback((item: any) => {
    // 模拟耗时操作
    const processed = {
      ...item,
      processed: true,
      timestamp: Date.now(),
    };

    setProcessedItems(prev => [...prev, processed]);
  }, []);

  const { startProcessing } = useTimeSlice(largeData, processData);

  return (
    <div>
      <button onClick={startProcessing}>
        Process Large Dataset
      </button>
      <div>
        Processed: {processedItems.length} / {largeData.length}
      </div>
    </div>
  );
}
```

### CLS (Cumulative Layout Shift)

#### 尺寸预留

```typescript
// 1. 图片尺寸预留
function ImageWithPlaceholder({ src, alt, width, height }) {
  return (
    <div style={{ width, height, position: 'relative' }}>
      <Image
        src={src}
        alt={alt}
        width={width}
        height={height}
        placeholder="blur"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
        }}
      />
    </div>
  );
}

// 2. 动态内容尺寸预留
function DynamicContent({ content }) {
  const [isLoading, setIsLoading] = useState(true);
  const [contentHeight, setContentHeight] = useState(0);

  useEffect(() => {
    // 预估内容高度
    setContentHeight(400); // 根据内容类型预估
    setIsLoading(false);
  }, []);

  return (
    <div style={{ minHeight: contentHeight }}>
      {isLoading ? (
        <div style={{ height: contentHeight }}>
          <LoadingSkeleton />
        </div>
      ) : (
        <div>{content}</div>
      )}
    </div>
  );
}

// 3. 广告和第三方内容
function AdPlaceholder({ adId }) {
  return (
    <div style={{
      width: '300px',
      height: '250px',
      backgroundColor: '#f0f0f0',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <span>Advertisement</span>
      {/* 广告脚本会填充这个容器 */}
    </div>
  );
}
```

#### 字体加载优化

```typescript
// 1. 字体预加载
function FontPreloader() {
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const fonts = [
        { family: 'Inter', weight: '400', style: 'normal' },
        { family: 'Inter', weight: '600', style: 'normal' },
      ];

      fonts.forEach(font => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'font';
        link.href = `/fonts/${font.family}-${font.weight}-${font.style}.woff2`;
        link.crossOrigin = 'anonymous';
        document.head.appendChild(link);
      });
    }
  }, []);

  return null;
}

// 2. 字体加载策略
const fontLoadingStrategy = `
  @font-face {
    font-family: 'Inter';
    src: url('/fonts/inter-400-normal.woff2') format('woff2');
    font-display: swap;
    font-weight: 400;
  }

  @font-face {
    font-family: 'Inter';
    src: url('/fonts/inter-600-normal.woff2') format('woff2');
    font-display: swap;
    font-weight: 600;
  }

  /* 系统字体后备 */
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }

  /* 字体加载完成后切换 */
  .fonts-loaded body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }
`;

// 3. 字体加载检测
function useFontLoading(fontFamily: string) {
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const checkFont = () => {
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      if (!context) return false;

      context.font = '20px ' + fontFamily;
      context.fillText='Test';
      const metrics = context.measureText('Test');

      return metrics.width > 0;
    };

    const interval = setInterval(() => {
      if (checkFont()) {
        setIsLoaded(true);
        clearInterval(interval);
        document.documentElement.classList.add('fonts-loaded');
      }
    }, 100);

    return () => clearInterval(interval);
  }, [fontFamily]);

  return isLoaded;
}
```

## Bundle 优化

### 代码分割

```typescript
// 1. 路由级别代码分割
// app/dashboard/page.tsx
import dynamic from 'next/dynamic';

const DashboardChart = dynamic(
  () => import('@/components/DashboardChart'),
  {
    loading: () => <div>Loading chart...</div>,
    ssr: false // 如果组件需要浏览器 API
  }
);

const AnalyticsPanel = dynamic(
  () => import('@/components/AnalyticsPanel'),
  { loading: () => <div>Loading analytics...</div> }
);

export default function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>
      <DashboardChart />
      <AnalyticsPanel />
    </div>
  );
}

// 2. 组件级别代码分割
const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <LoadingSpinner />,
  ssr: false,
});

// 3. 条件加载
const AdminPanel = dynamic(
  () => import('./AdminPanel'),
  {
    loading: () => null,
    ssr: false
  }
);

function App({ user }) {
  return (
    <div>
      <Header />
      <MainContent />
      {user?.isAdmin && <AdminPanel />}
    </div>
  );
}
```

### 懒加载

```typescript
// 1. 图片懒加载
function LazyImage({ src, alt, ...props }) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [imageRef, inView] = useInView({
    triggerOnce: true,
    threshold: 0.1,
  });

  return (
    <div ref={imageRef} style={{ position: 'relative' }}>
      {inView ? (
        <Image
          src={src}
          alt={alt}
          {...props}
          onLoad={() => setIsLoaded(true)}
          style={{
            opacity: isLoaded ? 1 : 0,
            transition: 'opacity 0.3s',
          }}
        />
      ) : (
        <div style={{
          width: props.width,
          height: props.height,
          backgroundColor: '#f0f0f0'
        }} />
      )}
    </div>
  );
}

// 2. 模块懒加载
function useLazyModule<T>(importFn: () => Promise<T>) {
  const [module, setModule] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const loadModule = useCallback(async () => {
    if (module) return module;

    setLoading(true);
    setError(null);

    try {
      const result = await importFn();
      setModule(result);
      return result;
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load module'));
      throw err;
    } finally {
      setLoading(false);
    }
  }, [importFn, module]);

  return { module, loading, error, loadModule };
}

// 3. 数据懒加载
function useLazyData<T>(
  fetchFn: () => Promise<T>,
  dependencies: any[] = []
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await fetchFn();
      setData(result);
      return result;
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load data'));
      throw err;
    } finally {
      setLoading(false);
    }
  }, dependencies);

  return { data, loading, error, loadData };
}
```

### Tree Shaking

```typescript
// 1. ES6 模块导入
// 好的做法
import { specificFunction } from './utils';
// 而不是
import * as utils from './utils';

// 2. 条件导入
async function loadFeature() {
  if (process.env.FEATURE_ENABLED === 'true') {
    const { FeatureModule } = await import('./features/feature-module');
    return new FeatureModule();
  }
  return null;
}

// 3. 副作用标记
// package.json
{
  "sideEffects": false
}

// 或者标记有副作用的文件
{
  "sideEffects": [
    "./src/polyfills.js",
    "*.css"
  ]
}

// 4. 按需导入大型库
import { debounce } from 'lodash-es';
// 而不是
import _ from 'lodash';

// 5. 使用动态导入减少初始包大小
function loadHeavyLibrary() {
  return import('heavy-library').then(module => {
    return module.default;
  });
}
```

### Bundle 分析

```typescript
// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer({
  // 其他配置...
});

// 自定义分析脚本
// scripts/analyze-bundle.js
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

async function analyzeBundle() {
  console.log('Running bundle analysis...');

  // 运行 Next.js 分析
  await new Promise((resolve) => {
    exec('ANALYZE=true npm run build', (error) => {
      if (error) {
        console.error('Analysis failed:', error);
      } else {
        console.log('Bundle analysis completed');
      }
      resolve();
    });
  });

  // 读取分析结果
  const clientStats = JSON.parse(
    fs.readFileSync(path.join(__dirname, '.next/stats-client.json'), 'utf8')
  );

  // 分析并输出建议
  const recommendations = generateRecommendations(clientStats);
  console.log('Optimization recommendations:');
  recommendations.forEach(rec => console.log(`- ${rec}`));
}

function generateRecommendations(stats) {
  const recommendations = [];

  // 检查包大小
  const totalSize = stats.assets.reduce((sum, asset) => sum + asset.size, 0);
  if (totalSize > 500 * 1024) { // 500KB
    recommendations.push('Consider code splitting to reduce initial bundle size');
  }

  // 检查重复模块
  const moduleCounts = {};
  stats.modules.forEach(module => {
    moduleCounts[module.name] = (moduleCounts[module.name] || 0) + 1;
  });

  Object.entries(moduleCounts).forEach(([name, count]) => {
    if (count > 1) {
      recommendations.push(`Duplicate module detected: ${name} (${count} times)`);
    }
  });

  // 检查大型依赖
  const largeModules = stats.modules
    .filter(module => module.size > 100 * 1024) // 100KB
    .sort((a, b) => b.size - a.size);

  largeModules.slice(0, 5).forEach(module => {
    recommendations.push(`Large module: ${module.name} (${(module.size / 1024).toFixed(2)}KB)`);
  });

  return recommendations;
}

analyzeBundle();
```

## 缓存策略

### 浏览器缓存

```typescript
// 1. Service Worker 缓存
// public/sw.js
const CACHE_NAME = 'my-app-cache-v1';
const urlsToCache = [
  '/',
  '/static/js/main.js',
  '/static/css/main.css',
  '/offline.html'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});

// 2. 缓存策略配置
function configureCacheHeaders() {
  const cacheRules = [
    {
      pattern: /\.(js|css|png|jpg|jpeg|gif|svg|ico)$/,
      maxAge: 31536000, // 1年
      immutable: true
    },
    {
      pattern: /\.(woff|woff2|ttf|eot)$/,
      maxAge: 31536000, // 1年
      immutable: true
    },
    {
      pattern: '/api/data/',
      maxAge: 3600, // 1小时
      staleWhileRevalidate: 86400 // 1天
    }
  ];

  return cacheRules;
}

// 3. IndexedDB 缓存
class IndexedDBCache {
  constructor(dbName, storeName) {
    this.dbName = dbName;
    this.storeName = storeName;
  }

  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, 1);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains(this.storeName)) {
          db.createObjectStore(this.storeName, { keyPath: 'key' });
        }
      };
    });
  }

  async set(key, value, ttl = null) {
    const transaction = this.db.transaction([this.storeName], 'readwrite');
    const store = transaction.objectStore(this.storeName);

    const item = {
      key,
      value,
      timestamp: Date.now(),
      ttl
    };

    return store.put(item);
  }

  async get(key) {
    const transaction = this.db.transaction([this.storeName], 'readonly');
    const store = transaction.objectStore(this.storeName);

    return new Promise((resolve, reject) => {
      const request = store.get(key);

      request.onsuccess = () => {
        const item = request.result;

        if (!item) {
          resolve(null);
          return;
        }

        // 检查 TTL
        if (item.ttl && Date.now() - item.timestamp > item.ttl) {
          this.delete(key);
          resolve(null);
          return;
        }

        resolve(item.value);
      };

      request.onerror = () => reject(request.error);
    });
  }

  async delete(key) {
    const transaction = this.db.transaction([this.storeName], 'readwrite');
    const store = transaction.objectStore(this.storeName);
    return store.delete(key);
  }
}
```

### CDN 缓存

```typescript
// 1. CDN 配置
const cdnConfig = {
  // 静态资源缓存规则
  staticAssets: {
    pattern: /\.(js|css|png|jpg|jpeg|gif|svg|woff|woff2|ttf|eot|ico)$/,
    edgeCacheTTL: 31536000, // 1年
    browserCacheTTL: 604800, // 1周
    compression: true,
    optimization: 'auto'
  },

  // API 响应缓存规则
  apiResponses: {
    pattern: '/api/',
    edgeCacheTTL: 300, // 5分钟
    browserCacheTTL: 60, // 1分钟
    vary: ['Accept-Encoding', 'Authorization']
  },

  // 页面缓存规则
  pages: {
    pattern: '/',
    edgeCacheTTL: 3600, // 1小时
    browserCacheTTL: 300, // 5分钟
    compression: true
  }
};

// 2. 缓存键生成
function generateCacheKey(request) {
  const url = new URL(request.url);
  const normalizedUrl = url.pathname + url.search;

  // 添加版本信息
  const version = process.env.BUILD_VERSION || 'dev';

  // 添加设备类型
  const userAgent = request.headers.get('user-agent') || '';
  const isMobile = /Mobile|Android|iPhone/.test(userAgent);

  return `${version}:${normalizedUrl}:${isMobile ? 'mobile' : 'desktop'}`;
}

// 3. 缓存失效策略
class CacheInvalidationStrategy {
  constructor() {
    this.cacheKeys = new Map();
  }

  // 当内容更新时使缓存失效
  async invalidateOnUpdate(contentType, id) {
    const keysToInvalidate = [];

    // 找到相关的缓存键
    for (const [key, metadata] of this.cacheKeys) {
      if (metadata.contentType === contentType &&
          (metadata.id === id || metadata.relatedIds?.includes(id))) {
        keysToInvalidate.push(key);
      }
    }

    // 使缓存失效
    await Promise.all(
      keysToInvalidate.map(key => this.invalidate(key))
    );
  }

  // 批量缓存失效
  async batchInvalidate(patterns) {
    const promises = patterns.map(pattern => {
      return this.invalidateByPattern(pattern);
    });

    return Promise.all(promises);
  }

  // 按模式失效
  async invalidateByPattern(pattern) {
    const keysToInvalidate = [];

    for (const key of this.cacheKeys.keys()) {
      if (pattern.test(key)) {
        keysToInvalidate.push(key);
      }
    }

    await Promise.all(
      keysToInvalidate.map(key => this.invalidate(key))
    );
  }

  async invalidate(key) {
    // 实现具体的缓存失效逻辑
    // 可能是调用 CDN API 或本地缓存清理
  }
}
```

### API 缓存

```typescript
// 1. HTTP 缓存头设置
function setCacheHeaders(response, strategy) {
  const headers = new Headers(response.headers);

  switch (strategy) {
    case 'immutable':
      headers.set('Cache-Control', 'public, max-age=31536000, immutable');
      break;

    case 'long-term':
      headers.set('Cache-Control', 'public, max-age=86400');
      break;

    case 'short-term':
      headers.set('Cache-Control', 'public, max-age=3600');
      break;

    case 'no-cache':
      headers.set('Cache-Control', 'no-cache, no-store, must-revalidate');
      break;

    case 'stale-while-revalidate':
      headers.set('Cache-Control', 'public, max-age=60, stale-while-revalidate=600');
      break;
  }

  headers.set('ETag', generateETag(response.body));

  return new Response(response.body, {
    ...response,
    headers
  });
}

// 2. 请求缓存
class APICache {
  constructor() {
    this.cache = new Map();
    this.inProgressRequests = new Map();
  }

  async get(key, fetchFn, options = {}) {
    const {
      ttl = 300000, // 5分钟
      staleWhileRevalidate = 600000, // 10分钟
      forceRefresh = false
    } = options;

    // 检查缓存
    const cached = this.cache.get(key);

    if (cached && !forceRefresh) {
      const { data, timestamp, ttl: cachedTTL } = cached;

      // 缓存仍然有效
      if (Date.now() - timestamp < cachedTTL) {
        return data;
      }

      // 使用陈旧数据，同时在后台刷新
      if (Date.now() - timestamp < cachedTTL + staleWhileRevalidate) {
        this.refreshInBackground(key, fetchFn, options);
        return data;
      }
    }

    // 避免重复请求
    if (this.inProgressRequests.has(key)) {
      return this.inProgressRequests.get(key);
    }

    // 发起新请求
    const requestPromise = fetchFn();
    this.inProgressRequests.set(key, requestPromise);

    try {
      const data = await requestPromise;

      // 缓存结果
      this.cache.set(key, {
        data,
        timestamp: Date.now(),
        ttl
      });

      return data;
    } finally {
      this.inProgressRequests.delete(key);
    }
  }

  async refreshInBackground(key, fetchFn, options) {
    try {
      const data = await fetchFn();
      this.cache.set(key, {
        data,
        timestamp: Date.now(),
        ttl: options.ttl
      });
    } catch (error) {
      console.error('Background refresh failed:', error);
    }
  }

  invalidate(key) {
    this.cache.delete(key);
  }

  clear() {
    this.cache.clear();
  }
}

// 3. 缓存键生成器
class CacheKeyGenerator {
  static generate(url, options = {}) {
    const normalizedUrl = this.normalizeUrl(url);
    const paramsHash = this.hashObject(options.params || {});
    const authHash = options.auth ? this.hashString(options.auth) : '';

    return `${normalizedUrl}:${paramsHash}:${authHash}`;
  }

  static normalizeUrl(url) {
    const parsedUrl = new URL(url);
    parsedUrl.searchParams.sort();
    return parsedUrl.toString();
  }

  static hashObject(obj) {
    return this.hashString(JSON.stringify(obj));
  }

  static hashString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // 转换为 32 位整数
    }
    return hash.toString(36);
  }
}
```

## 性能监控

### 性能指标收集

```typescript
// 1. Web Vitals 监控
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

class PerformanceMonitor {
  constructor() {
    this.metrics = [];
    this.init();
  }

  init() {
    if (typeof window === 'undefined') return;

    // 监控 Core Web Vitals
    getCLS(this.logMetric);
    getFID(this.logMetric);
    getFCP(this.logMetric);
    getLCP(this.logMetric);
    getTTFB(this.logMetric);

    // 监控自定义指标
    this.setupCustomMetrics();
  }

  logMetric = (metric) => {
    console.log('Performance metric:', metric);
    this.metrics.push(metric);

    // 发送到分析服务
    this.sendToAnalytics(metric);
  };

  setupCustomMetrics() {
    // 页面加载时间
    window.addEventListener('load', () => {
      const navigation = performance.getEntriesByType('navigation')[0];
      if (navigation) {
        this.logMetric({
          name: 'page_load_time',
          value: navigation.loadEventEnd - navigation.loadEventStart,
          id: this.generateId(),
        });
      }
    });

    // 首次渲染时间
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.name === 'first-contentful-paint') {
          this.logMetric({
            name: 'first_contentful_paint',
            value: entry.startTime,
            id: this.generateId(),
          });
        }
      }
    });

    observer.observe({ entryTypes: ['paint'] });

    // 长任务监控
    const longTaskObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        this.logMetric({
          name: 'long_task',
          value: entry.duration,
          id: this.generateId(),
        });
      }
    });

    longTaskObserver.observe({ entryTypes: ['longtask'] });
  }

  generateId() {
    return Math.random().toString(36).substr(2, 9);
  }

  sendToAnalytics(metric) {
    // 发送到分析服务
    if (typeof navigator.sendBeacon === 'function') {
      const data = new Blob([JSON.stringify(metric)], { type: 'application/json' });
      navigator.sendBeacon('/api/analytics', data);
    }
  }

  getMetrics() {
    return this.metrics;
  }

  getMetricsSummary() {
    const summary = {};

    this.metrics.forEach(metric => {
      if (!summary[metric.name]) {
        summary[metric.name] = {
          count: 0,
          sum: 0,
          avg: 0,
          min: Infinity,
          max: -Infinity
        };
      }

      const stat = summary[metric.name];
      stat.count++;
      stat.sum += metric.value;
      stat.avg = stat.sum / stat.count;
      stat.min = Math.min(stat.min, metric.value);
      stat.max = Math.max(stat.max, metric.value);
    });

    return summary;
  }
}

// 2. React 性能监控
function usePerformanceMonitoring(componentName) {
  const renderCount = useRef(0);
  const renderTimes = useRef([]);

  useEffect(() => {
    renderCount.current++;
    const startTime = performance.now();

    return () => {
      const renderTime = performance.now() - startTime;
      renderTimes.current.push(renderTime);

      // 记录慢渲染
      if (renderTime > 16) { // 超过一帧的时间
        console.warn(`Slow render detected in ${componentName}:`, {
          renderTime,
          renderCount: renderCount.current,
        });
      }
    };
  });

  const getPerformanceStats = () => {
    const times = renderTimes.current;
    return {
      renderCount: renderCount.current,
      averageRenderTime: times.reduce((a, b) => a + b, 0) / times.length,
      maxRenderTime: Math.max(...times),
      minRenderTime: Math.min(...times),
    };
  };

  return { getPerformanceStats };
}

// 3. 网络性能监控
class NetworkMonitor {
  constructor() {
    this.requests = new Map();
    this.setupNetworkMonitoring();
  }

  setupNetworkMonitoring() {
    if (typeof window === 'undefined') return;

    // 拦截 fetch
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      const startTime = performance.now();
      const url = args[0];

      try {
        const response = await originalFetch(...args);
        const endTime = performance.now();
        const duration = endTime - startTime;

        this.recordRequest({
          url,
          method: args[1]?.method || 'GET',
          status: response.status,
          duration,
          size: response.headers.get('content-length'),
          timestamp: startTime,
        });

        return response;
      } catch (error) {
        const endTime = performance.now();
        this.recordRequest({
          url,
          method: args[1]?.method || 'GET',
          status: 0,
          duration: endTime - startTime,
          error: error.message,
          timestamp: startTime,
        });
        throw error;
      }
    };

    // 拦截 XMLHttpRequest
    const originalXHROpen = XMLHttpRequest.prototype.open;
    const originalXHRSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function(...args) {
      this._url = args[1];
      this._method = args[0];
      return originalXHROpen.apply(this, args);
    };

    XMLHttpRequest.prototype.send = function(...args) {
      const startTime = performance.now();

      this.addEventListener('loadend', () => {
        const endTime = performance.now();
        const duration = endTime - startTime;

        NetworkMonitor.getInstance().recordRequest({
          url: this._url,
          method: this._method,
          status: this.status,
          duration,
          size: this.getResponseHeader('content-length'),
          timestamp: startTime,
        });
      });

      return originalXHRSend.apply(this, args);
    };
  }

  recordRequest(request) {
    const key = `${request.method}:${request.url}`;
    const existing = this.requests.get(key) || [];

    this.requests.set(key, [...existing, request]);
  }

  getNetworkStats() {
    const stats = {
      totalRequests: 0,
      averageResponseTime: 0,
      slowestRequest: null,
      errorRate: 0,
      totalDataTransfer: 0,
    };

    let totalDuration = 0;
    let errorCount = 0;
    let totalSize = 0;
    let slowestRequest = null;

    for (const requests of this.requests.values()) {
      requests.forEach(request => {
        stats.totalRequests++;
        totalDuration += request.duration;
        totalSize += parseInt(request.size) || 0;

        if (request.status >= 400) {
          errorCount++;
        }

        if (!slowestRequest || request.duration > slowestRequest.duration) {
          slowestRequest = request;
        }
      });
    }

    stats.averageResponseTime = totalDuration / stats.totalRequests;
    stats.slowestRequest = slowestRequest;
    stats.errorRate = (errorCount / stats.totalRequests) * 100;
    stats.totalDataTransfer = totalSize;

    return stats;
  }

  static getInstance() {
    if (!NetworkMonitor.instance) {
      NetworkMonitor.instance = new NetworkMonitor();
    }
    return NetworkMonitor.instance;
  }
}
```

### 性能优化工具

```typescript
// 1. 性能预算检查
class PerformanceBudget {
  constructor(budgets) {
    this.budgets = {
      totalSize: 500 * 1024, // 500KB
      javascriptSize: 200 * 1024, // 200KB
      cssSize: 50 * 1024, // 50KB
      imageCount: 10,
      requestCount: 20,
      ...budgets
    };
  }

  async checkBudget() {
    const metrics = await this.collectMetrics();
    const violations = [];

    Object.entries(this.budgets).forEach(([key, limit]) => {
      const value = metrics[key];
      if (value > limit) {
        violations.push({
          metric: key,
          value,
          limit,
          percentage: ((value / limit) * 100).toFixed(2) + '%'
        });
      }
    });

    return {
      passed: violations.length === 0,
      violations,
      metrics
    };
  }

  async collectMetrics() {
    if (typeof window === 'undefined') {
      return this.getServerMetrics();
    }

    return this.getClientMetrics();
  }

  getClientMetrics() {
    const resources = performance.getEntriesByType('resource');

    const metrics = {
      totalSize: 0,
      javascriptSize: 0,
      cssSize: 0,
      imageCount: 0,
      requestCount: resources.length
    };

    resources.forEach(resource => {
      const size = resource.transferSize || 0;
      metrics.totalSize += size;

      if (resource.name.endsWith('.js')) {
        metrics.javascriptSize += size;
      } else if (resource.name.endsWith('.css')) {
        metrics.cssSize += size;
      } else if (resource.name.match(/\.(jpg|jpeg|png|gif|svg|webp)$/)) {
        metrics.imageCount++;
      }
    });

    return metrics;
  }

  async getServerMetrics() {
    // 实现服务器端指标收集
    return {};
  }
}

// 2. 性能分析工具
class PerformanceProfiler {
  constructor() {
    this.profiles = new Map();
    this.currentProfile = null;
  }

  startProfile(name) {
    if (this.currentProfile) {
      console.warn('Profile already in progress:', this.currentProfile.name);
      return;
    }

    this.currentProfile = {
      name,
      startTime: performance.now(),
      marks: [],
      measures: []
    };

    console.log(`Profile started: ${name}`);
  }

  mark(markName) {
    if (!this.currentProfile) {
      console.warn('No profile in progress');
      return;
    }

    const mark = {
      name: markName,
      time: performance.now()
    };

    this.currentProfile.marks.push(mark);
    performance.mark(`${this.currentProfile.name}:${markName}`);
  }

  measure(measureName, startMark, endMark) {
    if (!this.currentProfile) {
      console.warn('No profile in progress');
      return;
    }

    try {
      performance.measure(
        `${this.currentProfile.name}:${measureName}`,
        `${this.currentProfile.name}:${startMark}`,
        `${this.currentProfile.name}:${endMark}`
      );

      const measures = performance.getEntriesByName(
        `${this.currentProfile.name}:${measureName}`
      );

      const measure = measures[measures.length - 1];

      this.currentProfile.measures.push({
        name: measureName,
        duration: measure.duration,
        startTime: measure.startTime
      });
    } catch (error) {
      console.error('Measure failed:', error);
    }
  }

  endProfile() {
    if (!this.currentProfile) {
      console.warn('No profile in progress');
      return;
    }

    const endTime = performance.now();
    const duration = endTime - this.currentProfile.startTime;

    const profile = {
      ...this.currentProfile,
      endTime,
      duration,
      measures: this.currentProfile.measures.map(measure => ({
        ...measure,
        percentage: ((measure.duration / duration) * 100).toFixed(2) + '%'
      }))
    };

    this.profiles.set(this.currentProfile.name, profile);
    this.currentProfile = null;

    console.log(`Profile completed: ${profile.name}`);
    console.log(`Total duration: ${duration.toFixed(2)}ms`);

    profile.measures.forEach(measure => {
      console.log(`  ${measure.name}: ${measure.duration.toFixed(2)}ms (${measure.percentage})`);
    });

    return profile;
  }

  getProfile(name) {
    return this.profiles.get(name);
  }

  getAllProfiles() {
    return Array.from(this.profiles.values());
  }

  exportProfile(name) {
    const profile = this.profiles.get(name);
    if (!profile) return null;

    return {
      name: profile.name,
      duration: profile.duration,
      measures: profile.measures,
      timestamp: profile.startTime
    };
  }
}

// 3. 性能优化建议生成器
class PerformanceOptimizer {
  constructor() {
    this.rules = this.loadOptimizationRules();
  }

  loadOptimizationRules() {
    return [
      {
        name: 'large_images',
        condition: (metrics) => {
          const largeImages = metrics.resources.filter(
            r => r.type === 'image' && r.size > 100 * 1024
          );
          return largeImages.length > 0;
        },
        suggestion: (metrics) => {
          const largeImages = metrics.resources.filter(
            r => r.type === 'image' && r.size > 100 * 1024
          );
          return {
            priority: 'high',
            message: `Found ${largeImages.length} large images (>100KB). Consider compressing or using modern formats.`,
            details: largeImages.map(img => ({
              url: img.name,
              size: img.size,
              format: img.name.split('.').pop()
            }))
          };
        }
      },
      {
        name: 'unused_css',
        condition: (metrics) => {
          return metrics.cssSize > 50 * 1024;
        },
        suggestion: (metrics) => ({
          priority: 'medium',
          message: `CSS size is ${metrics.cssSize / 1024}KB. Consider removing unused CSS.`,
          action: 'Run CSS optimization tools'
        })
      },
      {
        name: 'render_blocking_resources',
        condition: (metrics) => {
          return metrics.renderBlockingResources > 3;
        },
        suggestion: (metrics) => ({
          priority: 'high',
          message: `Found ${metrics.renderBlockingResources} render-blocking resources.`,
          action: 'Defer non-critical CSS and JavaScript'
        })
      },
      {
        name: 'slow_first_paint',
        condition: (metrics) => {
          return metrics.firstContentfulPaint > 2000;
        },
        suggestion: (metrics) => ({
          priority: 'high',
          message: `First Contentful Paint is ${metrics.firstContentfulPaint}ms.`,
          action: 'Optimize critical rendering path'
        })
      }
    ];
  }

  async analyze(metrics) {
    const suggestions = [];

    for (const rule of this.rules) {
      if (rule.condition(metrics)) {
        const suggestion = rule.suggestion(metrics);
        suggestions.push(suggestion);
      }
    }

    return suggestions.sort((a, b) => {
      const priorityOrder = { 'high': 3, 'medium': 2, 'low': 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
  }

  generateReport(metrics, suggestions) {
    return {
      summary: {
        totalSuggestions: suggestions.length,
        highPriority: suggestions.filter(s => s.priority === 'high').length,
        mediumPriority: suggestions.filter(s => s.priority === 'medium').length,
        lowPriority: suggestions.filter(s => s.priority === 'low').length,
      },
      metrics,
      suggestions,
      timestamp: Date.now()
    };
  }
}
```

这个性能优化速查手册涵盖了现代前端应用性能优化的各个方面，包括 Core Web Vitals、Bundle 优化、缓存策略和性能监控等关键技术。每个部分都提供了实用的代码示例和最佳实践，可以作为开发过程中的参考指南。