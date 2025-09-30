# Core Web Vitals 优化策略 - Next.js 15 性能优化

## 📋 概述

Core Web Vitals 是 Google 定义的一组关键性能指标，用于衡量用户体验质量。Next.js 15 提供了强大的工具和功能来优化这些指标。本文将深入探讨如何优化 Core Web Vitals，确保应用提供出色的用户体验。

## 🎯 Core Web Vitals 指标详解

### 1. LCP (Largest Contentful Paint)

**定义**：最大内容绘制，衡量页面主要内容加载完成的时间。

**目标**：≤ 2.5秒

```typescript
// 监控LCP
function useLCPMonitor() {
  const [lcp, setLCP] = useState<number | null>(null);

  useEffect(() => {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        setLCP(lastEntry.startTime);
      });

      observer.observe({ entryTypes: ['largest-contentful-paint'] });

      return () => observer.disconnect();
    }
  }, []);

  return lcp;
}

// LCP优化策略
function LCPOptimization() {
  // 1. 预加载关键资源
  useEffect(() => {
    const preloadResources = () => {
      // 预加载字体
      const fontLink = document.createElement('link');
      fontLink.rel = 'preload';
      fontLink.as = 'font';
      fontLink.crossOrigin = 'anonymous';
      fontLink.href = '/fonts/main-font.woff2';
      document.head.appendChild(fontLink);

      // 预加载关键图片
      const imageLink = document.createElement('link');
      imageLink.rel = 'preload';
      imageLink.as = 'image';
      imageLink.href = '/images/hero-image.jpg';
      document.head.appendChild(imageLink);
    };

    preloadResources();
  }, []);

  // 2. 优化关键渲染路径
  const CriticalCSS = () => (
    <style jsx global>{`
      /* 关键CSS内联 */
      .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 400px;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .hero-content {
        color: white;
        text-align: center;
        max-width: 800px;
        padding: 2rem;
      }
    `}</style>
  );

  // 3. 使用Next.js图片优化
  const OptimizedImage = () => (
    <Image
      src="/images/hero-image.jpg"
      alt="Hero image"
      width={1200}
      height={600}
      priority // 高优先级加载
      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
      quality={85}
    />
  );

  return (
    <div>
      <CriticalCSS />
      <OptimizedImage />
    </div>
  );
}
```

### 2. FID (First Input Delay)

**定义**：首次输入延迟，衡量用户首次与页面交互时的响应速度。

**目标**：≤ 100毫秒

```typescript
// 监控FID
function useFIDMonitor() {
  const [fid, setFID] = useState<number | null>(null);

  useEffect(() => {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          if (entry.entryType === 'first-input') {
            setFID(entry.processingStart - entry.startTime);
          }
        });
      });

      observer.observe({ entryTypes: ['first-input'] });

      return () => observer.disconnect();
    }
  }, []);

  return fid;
}

// FID优化策略
function FIDOptimization() {
  // 1. 减少JavaScript执行时间
  useEffect(() => {
    // 延迟加载非关键JavaScript
    const loadNonCriticalJS = () => {
      setTimeout(() => {
        const script = document.createElement('script');
        script.src = '/js/non-critical.js';
        script.async = true;
        document.body.appendChild(script);
      }, 3000);
    };

    loadNonCriticalJS();
  }, []);

  // 2. 使用Web Workers处理复杂计算
  const useWorkerForHeavyTask = () => {
    const worker = new Worker('/workers/heavy-task.worker.js');

    worker.postMessage({ data: largeDataSet });

    worker.onmessage = (event) => {
      console.log('Worker result:', event.data);
    };

    return () => worker.terminate();
  };

  // 3. 事件处理优化
  const handleUserInteraction = useCallback((event: React.MouseEvent) => {
    // 使用requestIdleCallback处理非紧急任务
    requestIdleCallback(() => {
      // 非紧急任务
      analytics.track('user_interaction', {
        element: event.currentTarget.tagName,
        timestamp: Date.now(),
      });
    });

    // 立即响应用户操作
    setUserInteractionState(true);
  }, []);

  return (
    <button onClick={handleUserInteraction}>
      Click Me
    </button>
  );
}
```

### 3. CLS (Cumulative Layout Shift)

**定义**：累积布局偏移，衡量页面内容在加载过程中的视觉稳定性。

**目标**：≤ 0.1

```typescript
// 监控CLS
function useCLSMonitor() {
  const [cls, setCLS] = useState<number | null>(null);

  useEffect(() => {
    if ('PerformanceObserver' in window) {
      let clsValue = 0;
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.entryType === 'layout-shift' && !entry.hadRecentInput) {
            clsValue += entry.value;
            setCLS(clsValue);
          }
        });
      });

      observer.observe({ entryTypes: ['layout-shift'] });

      return () => observer.disconnect();
    }
  }, []);

  return cls;
}

// CLS优化策略
function CLSOptimization() {
  // 1. 为图片和广告预留空间
  const ImageWithPlaceholder = ({ src, alt, width, height }: {
    src: string;
    alt: string;
    width: number;
    height: number;
  }) => (
    <div style={{ width, height, backgroundColor: '#f0f0f0' }}>
      <Image
        src={src}
        alt={alt}
        width={width}
        height={height}
        layout="responsive"
        placeholder="blur"
      />
    </div>
  );

  // 2. 动态内容加载优化
  const DynamicContent = () => {
    const [content, setContent] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const loadMoreContent = async () => {
      setIsLoading(true);

      // 预先定义容器高度，避免布局偏移
      const currentHeight = document.getElementById('content-container')?.offsetHeight || 0;

      const newContent = await fetchMoreContent();

      setContent(prev => [...prev, ...newContent]);
      setIsLoading(false);
    };

    return (
      <div id="content-container" style={{ minHeight: currentHeight }}>
        {content.map((item, index) => (
          <div key={index}>{item}</div>
        ))}
        {isLoading && <div style={{ height: '100px' }}>Loading...</div>}
        <button onClick={loadMoreContent}>Load More</button>
      </div>
    );
  };

  // 3. 字体加载优化
  const FontOptimization = () => {
    useEffect(() => {
      // 预加载字体
      const fontLink = document.createElement('link');
      fontLink.rel = 'preload';
      fontLink.as = 'font';
      fontLink.crossOrigin = 'anonymous';
      fontLink.href = '/fonts/main-font.woff2';
      document.head.appendChild(fontLink);

      // 使用font-display: swap
      const style = document.createElement('style');
      style.textContent = `
        @font-face {
          font-family: 'Main Font';
          src: url('/fonts/main-font.woff2') format('woff2');
          font-display: swap;
        }
      `;
      document.head.appendChild(style);
    }, []);

    return <div style={{ fontFamily: 'Main Font, sans-serif' }}>Content</div>;
  };

  return (
    <div>
      <ImageWithPlaceholder
        src="/images/product.jpg"
        alt="Product"
        width={300}
        height={200}
      />
      <DynamicContent />
      <FontOptimization />
    </div>
  );
}
```

## 🚀 其他重要性能指标

### 1. TTFB (Time to First Byte)

**定义**：首字节时间，衡量服务器响应速度。

**目标**：≤ 600毫秒

```typescript
// TTFB优化策略
function TTFBOptimization() {
  // 1. 使用Edge Functions
  const useEdgeFunction = async () => {
    const response = await fetch('/api/data', {
      headers: {
        'Cache-Control': 'public, max-age=3600',
      },
    });
    return response.json();
  };

  // 2. 缓存优化
  const getCachedData = unstable_cache(
    async (key: string) => {
      const response = await fetch(`/api/${key}`);
      return response.json();
    },
    ['data-cache'],
    {
      revalidate: 3600, // 1小时缓存
      tags: ['data'],
    }
  );

  // 3. CDN配置
  const CDNHeaders = () => {
    // 在Next.js中间件中设置
    return new Response(JSON.stringify({ data: 'cached' }), {
      headers: {
        'Cache-Control': 'public, max-age=3600, s-maxage=3600',
        'CDN-Cache-Control': 'public, max-age=3600',
      },
    });
  };

  return (
    <div>
      {/* 使用Edge Functions优化的组件 */}
    </div>
  );
}
```

### 2. FCP (First Contentful Paint)

**定义**：首次内容绘制，衡量页面首次渲染内容的时间。

**目标**：≤ 1.8秒

```typescript
// FCP优化策略
function FCPOptimization() {
  // 1. 关键CSS提取
  const CriticalCSS = () => (
    <style jsx global>{`
      /* 首屏关键样式 */
      body {
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
      }

      .header {
        background: #fff;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      }

      .hero {
        min-height: 50vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
      }
    `}</style>
  );

  // 2. 预渲染关键内容
  const HeroSection = () => (
    <section className="hero">
      <div>
        <h1>Welcome to Our Platform</h1>
        <p>Experience the future of web development</p>
      </div>
    </section>
  );

  // 3. 延迟加载非关键内容
  const LazyLoadedContent = dynamic(
    () => import('./LazyLoadedContent'),
    {
      loading: () => <div style={{ height: '200px', backgroundColor: '#f0f0f0' }} />,
      ssr: false,
    }
  );

  return (
    <div>
      <CriticalCSS />
      <HeroSection />
      <Suspense fallback={<div>Loading more content...</div>}>
        <LazyLoadedContent />
      </Suspense>
    </div>
  );
}
```

## 🎨 实际应用优化

### 1. 图片优化

```typescript
// components/OptimizedImages.tsx
import Image from 'next/image';
import { useState } from 'react';

interface OptimizedImageProps {
  src: string;
  alt: string;
  width: number;
  height: number;
  priority?: boolean;
  className?: string;
}

export function OptimizedImage({
  src,
  alt,
  width,
  height,
  priority = false,
  className = '',
}: OptimizedImageProps) {
  const [isLoaded, setIsLoaded] = useState(false);

  return (
    <div className={`image-container ${className}`} style={{ width, height }}>
      <Image
        src={src}
        alt={alt}
        width={width}
        height={height}
        priority={priority}
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        quality={isLoaded ? 85 : 25} // 先低质量加载，再高质量显示
        onLoadingComplete={() => setIsLoaded(true)}
        placeholder="blur"
        blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/wA="
        style={{
          transition: 'filter 0.3s ease',
          filter: isLoaded ? 'none' : 'blur(10px)',
        }}
      />
    </div>
  );
}

// 图片画廊优化
export function OptimizedGallery({ images }: { images: string[] }) {
  return (
    <div className="gallery">
      {images.map((image, index) => (
        <OptimizedImage
          key={index}
          src={image}
          alt={`Gallery image ${index + 1}`}
          width={400}
          height={300}
          priority={index < 3} // 前3张图片优先加载
        />
      ))}
    </div>
  );
}
```

### 2. 字体优化

```typescript
// lib/font-optimization.ts
export function optimizeFontLoading() {
  // 1. 预加载关键字体
  const preloadFont = (fontUrl: string, fontFamily: string) => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = 'font';
    link.crossOrigin = 'anonymous';
    link.href = fontUrl;
    document.head.appendChild(link);

    // 创建字体样式
    const style = document.createElement('style');
    style.textContent = `
      @font-face {
        font-family: '${fontFamily}';
        src: url('${fontUrl}') format('woff2');
        font-display: swap;
        font-weight: 400;
        font-style: normal;
      }
    `;
    document.head.appendChild(style);
  };

  // 2. 延迟加载非关键字体
  const loadNonCriticalFont = (fontUrl: string, fontFamily: string) => {
    setTimeout(() => {
      preloadFont(fontUrl, fontFamily);
    }, 2000);
  };

  // 3. 字体观察器
  const setupFontObserver = () => {
    if ('FontFace' in window) {
      const font = new FontFace(
        'Custom Font',
        'url(/fonts/custom.woff2)',
        { display: 'swap' }
      );

      font.load().then((loadedFont) => {
        document.fonts.add(loadedFont);
        document.body.classList.add('fonts-loaded');
      });
    }
  };

  return {
    preloadFont,
    loadNonCriticalFont,
    setupFontObserver,
  };
}

// components/OptimizedText.tsx
interface OptimizedTextProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'heading' | 'body' | 'caption';
}

export function OptimizedText({ children, className = '', variant = 'body' }: OptimizedTextProps) {
  const fontClass = {
    heading: 'font-heading',
    body: 'font-body',
    caption: 'font-caption',
  }[variant];

  return (
    <span className={`${fontClass} ${className}`}>
      {children}
    </span>
  );
}
```

### 3. JavaScript优化

```typescript
// lib/js-optimization.ts
export function optimizeJavaScriptLoading() {
  // 1. 异步加载非关键JS
  const loadScriptAsync = (src: string, callback?: () => void) => {
    const script = document.createElement('script');
    script.src = src;
    script.async = true;
    script.onload = callback;
    document.body.appendChild(script);
  };

  // 2. 使用requestIdleCallback
  const loadLowPriorityScripts = () => {
    if ('requestIdleCallback' in window) {
      requestIdleCallback(() => {
        loadScriptAsync('/js/analytics.js');
        loadScriptAsync('/js/chat-widget.js');
      });
    } else {
      setTimeout(() => {
        loadScriptAsync('/js/analytics.js');
        loadScriptAsync('/js/chat-widget.js');
      }, 2000);
    }
  };

  // 3. 动态导入
  const loadComponentDynamically = async (componentName: string) => {
    const component = await import(`@/components/${componentName}`);
    return component.default;
  };

  return {
    loadScriptAsync,
    loadLowPriorityScripts,
    loadComponentDynamically,
  };
}

// components/LazyLoadedComponent.tsx
import dynamic from 'next/dynamic';

// 1. 基本懒加载
const LazyChart = dynamic(
  () => import('./Chart'),
  {
    loading: () => <div className="chart-placeholder">Loading chart...</div>,
    ssr: false,
  }
);

// 2. 条件懒加载
const ConditionalModal = dynamic(
  () => import('./Modal'),
  {
    loading: () => null,
    ssr: false,
  }
);

// 3. 带预取的懒加载
const PrefetchedComponent = dynamic(
  () => import('./PrefetchableComponent'),
  {
    loading: () => <div>Loading...</div>,
    ssr: false,
  }
);

// 使用示例
export function PerformanceOptimizedPage() {
  const [showModal, setShowModal] = useState(false);

  // 预取组件
  useEffect(() => {
    const prefetchModal = async () => {
      const modal = await import('./Modal');
      // 预取完成
    };

    if (typeof window !== 'undefined') {
      prefetchModal();
    }
  }, []);

  return (
    <div>
      <h1>Performance Optimized Page</h1>
      <LazyChart />

      <button onClick={() => setShowModal(true)}>
        Open Modal
      </button>

      {showModal && <ConditionalModal />}
    </div>
  );
}
```

## 🎯 性能监控和分析

### 1. 性能监控

```typescript
// lib/performance-monitoring.ts
export class PerformanceMonitor {
  private metrics: Map<string, number[]> = new Map();

  // 记录性能指标
  recordMetric(name: string, value: number): void {
    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }
    this.metrics.get(name)!.push(value);
  }

  // 获取指标统计
  getMetricStats(name: string): {
    count: number;
    average: number;
    min: number;
    max: number;
    p95: number;
  } {
    const values = this.metrics.get(name) || [];
    if (values.length === 0) {
      return { count: 0, average: 0, min: 0, max: 0, p95: 0 };
    }

    const sorted = [...values].sort((a, b) => a - b);
    const sum = values.reduce((a, b) => a + b, 0);

    return {
      count: values.length,
      average: sum / values.length,
      min: sorted[0],
      max: sorted[sorted.length - 1],
      p95: sorted[Math.floor(sorted.length * 0.95)],
    };
  }

  // 监控Web Vitals
  monitorWebVitals(): void {
    if ('PerformanceObserver' in window) {
      // LCP监控
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          if (entry.entryType === 'largest-contentful-paint') {
            this.recordMetric('lcp', entry.startTime);
          }
        });
      });
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

      // FID监控
      const fidObserver = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.entryType === 'first-input') {
            this.recordMetric('fid', entry.processingStart - entry.startTime);
          }
        });
      });
      fidObserver.observe({ entryTypes: ['first-input'] });

      // CLS监控
      let clsValue = 0;
      const clsObserver = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.entryType === 'layout-shift' && !entry.hadRecentInput) {
            clsValue += entry.value;
            this.recordMetric('cls', clsValue);
          }
        });
      });
      clsObserver.observe({ entryTypes: ['layout-shift'] });
    }
  }

  // 发送性能数据到分析服务
  async sendMetricsToAnalytics(): Promise<void> {
    const metrics = {
      lcp: this.getMetricStats('lcp'),
      fid: this.getMetricStats('fid'),
      cls: this.getMetricStats('cls'),
      timestamp: Date.now(),
    };

    try {
      await fetch('/api/performance-metrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(metrics),
      });
    } catch (error) {
      console.error('Failed to send performance metrics:', error);
    }
  }
}

// 使用示例
const performanceMonitor = new PerformanceMonitor();

// 在应用启动时初始化监控
if (typeof window !== 'undefined') {
  performanceMonitor.monitorWebVitals();

  // 定期发送指标
  setInterval(() => {
    performanceMonitor.sendMetricsToAnalytics();
  }, 30000); // 每30秒发送一次
}
```

### 2. 性能优化检查清单

```typescript
// lib/performance-checklist.ts
export interface PerformanceCheck {
  id: string;
  name: string;
  description: string;
  check: () => Promise<{ passed: boolean; details?: any }>;
  importance: 'high' | 'medium' | 'low';
}

export const performanceChecks: PerformanceCheck[] = [
  {
    id: 'image-optimization',
    name: 'Image Optimization',
    description: 'All images should be optimized and use modern formats',
    importance: 'high' as const,
    check: async () => {
      const images = document.querySelectorAll('img');
      let unoptimizedCount = 0;

      images.forEach((img) => {
        const src = img.src;
        if (!src.includes('.webp') && !src.includes('.avif')) {
          unoptimizedCount++;
        }
      });

      return {
        passed: unoptimizedCount === 0,
        details: { unoptimizedCount, totalImages: images.length },
      };
    },
  },
  {
    id: 'unused-javascript',
    name: 'Unused JavaScript',
    description: 'Remove unused JavaScript code',
    importance: 'high' as const,
    check: async () => {
      if ('performance' in window) {
        const resources = performance.getEntriesByType('resource');
        const jsResources = resources.filter(r => r.name.endsWith('.js'));
        const totalJSSize = jsResources.reduce((sum, r) => sum + (r as any).transferSize, 0);

        return {
          passed: totalJSSize < 500 * 1024, // 小于500KB
          details: { totalJSSize: totalJSSize / 1024 + 'KB' },
        };
      }
      return { passed: true };
    },
  },
  {
    id: 'render-blocking-resources',
    name: 'Render Blocking Resources',
    description: 'Eliminate render-blocking resources',
    importance: 'high' as const,
    check: async () => {
      const performanceEntries = performance.getEntriesByType('resource');
      const renderBlockingResources = performanceEntries.filter(entry => {
        return (entry as any).renderBlockingStatus === 'blocking';
      });

      return {
        passed: renderBlockingResources.length === 0,
        details: { blockingResources: renderBlockingResources.length },
      };
    },
  },
  {
    id: 'proper-image-sizing',
    name: 'Proper Image Sizing',
    description: 'Images should have explicit width and height',
    importance: 'medium' as const,
    check: async () => {
      const images = document.querySelectorAll('img');
      let imagesWithoutSize = 0;

      images.forEach((img) => {
        if (!img.width || !img.height) {
          imagesWithoutSize++;
        }
      });

      return {
        passed: imagesWithoutSize === 0,
        details: { imagesWithoutSize, totalImages: images.length },
      };
    },
  },
];

// 性能检查器
export class PerformanceChecker {
  async runChecks(): Promise<{
    passed: number;
    failed: number;
    results: Array<{
      check: PerformanceCheck;
      result: { passed: boolean; details?: any };
    }>;
  }> {
    const results = [];

    for (const check of performanceChecks) {
      const result = await check.check();
      results.push({ check, result });
    }

    const passed = results.filter(r => r.result.passed).length;
    const failed = results.length - passed;

    return { passed, failed, results };
  }

  generateReport(results: typeof performanceChecks): string {
    let report = '# Performance Check Report\n\n';

    const highImportance = results.filter(r => r.importance === 'high');
    const mediumImportance = results.filter(r => r.importance === 'medium');
    const lowImportance = results.filter(r => r.importance === 'low');

    report += `## High Importance (${highImportance.length})\n\n`;
    highImportance.forEach(check => {
      report += `- [ ] ${check.name}: ${check.description}\n`;
    });

    report += `\n## Medium Importance (${mediumImportance.length})\n\n`;
    mediumImportance.forEach(check => {
      report += `- [ ] ${check.name}: ${check.description}\n`;
    });

    report += `\n## Low Importance (${lowImportance.length})\n\n`;
    lowImportance.forEach(check => {
      report += `- [ ] ${check.name}: ${check.description}\n`;
    });

    return report;
  }
}
```

## 🎯 总结

Core Web Vitals 优化是提供出色用户体验的关键。通过系统性地优化 LCP、FID 和 CLS 等关键指标，可以显著提升应用性能和用户满意度。

### 关键优化策略：

1. **LCP优化**：
   - 预加载关键资源
   - 优化服务器响应时间
   - 使用CDN和缓存
   - 优化图片和字体加载

2. **FID优化**：
   - 减少JavaScript执行时间
   - 使用Web Workers处理复杂计算
   - 优化事件处理
   - 延迟加载非关键JavaScript

3. **CLS优化**：
   - 为图片和广告预留空间
   - 优化字体加载
   - 避免动态内容布局偏移
   - 使用CSS Grid和Flexbox布局

4. **监控和分析**：
   - 实时性能监控
   - 定期性能检查
   - 用户真实数据收集
   - 持续性能优化

通过实施这些策略，可以确保应用在各种网络条件和设备上都能提供出色的用户体验。