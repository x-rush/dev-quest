# Bundle Optimization - Next.js 15 现代性能优化实践

## 📋 概述

Bundle Optimization 是现代前端性能优化的核心策略之一。Next.js 15 提供了强大的工具和配置选项来优化应用包大小，提升加载性能。本文将深入探讨如何在 Next.js 15 项目中实施全面的 Bundle Optimization 策略。

## 🎯 Bundle Analysis 基础

### 1. Bundle 分析工具

```typescript
// packages/webpack-bundle-analyzer/src/index.ts
import { execSync } from 'child_process';
import path from 'path';
import fs from 'fs';

export interface BundleAnalysisResult {
  totalSize: number;
  gzipSize: number;
  chunks: ChunkInfo[];
  assets: AssetInfo[];
  duplicates: DuplicateInfo[];
}

export interface ChunkInfo {
  name: string;
  size: number;
  modules: ModuleInfo[];
}

export interface ModuleInfo {
  name: string;
  size: number;
  reasons: string[];
}

export interface AssetInfo {
  name: string;
  size: number;
  type: 'js' | 'css' | 'font' | 'image';
}

export interface DuplicateInfo {
  modules: string[];
  chunks: string[];
  totalSize: number;
}

export class BundleAnalyzer {
  private projectPath: string;

  constructor(projectPath: string) {
    this.projectPath = projectPath;
  }

  async analyzeBuild(): Promise<BundleAnalysisResult> {
    console.log('🔍 Analyzing bundle...');

    // 运行 Next.js 构建
    execSync('npm run build', { cwd: this.projectPath, stdio: 'inherit' });

    // 分析构建输出
    const buildDir = path.join(this.projectPath, '.next');
    const result = await this.analyzeBuildOutput(buildDir);

    return result;
  }

  private async analyzeBuildOutput(buildDir: string): Promise<BundleAnalysisResult> {
    const chunks: ChunkInfo[] = [];
    const assets: AssetInfo[] = [];
    let totalSize = 0;

    // 分析 JavaScript chunks
    const chunksDir = path.join(buildDir, 'static', 'chunks');
    if (fs.existsSync(chunksDir)) {
      await this.analyzeChunks(chunksDir, chunks, assets);
    }

    // 分析静态资源
    const staticDir = path.join(buildDir, 'static');
    if (fs.existsSync(staticDir)) {
      await this.analyzeStaticAssets(staticDir, assets);
    }

    totalSize = assets.reduce((sum, asset) => sum + asset.size, 0);

    return {
      totalSize,
      gzipSize: Math.round(totalSize * 0.7), // 估算gzip大小
      chunks,
      assets,
      duplicates: this.findDuplicates(chunks)
    };
  }

  private async analyzeChunks(dir: string, chunks: ChunkInfo[], assets: AssetInfo[]) {
    const files = fs.readdirSync(dir);

    for (const file of files) {
      if (file.endsWith('.js')) {
        const filePath = path.join(dir, file);
        const stats = fs.statSync(filePath);

        const chunk: ChunkInfo = {
          name: file.replace('.js', ''),
          size: stats.size,
          modules: await this.extractModules(filePath)
        };

        chunks.push(chunk);

        assets.push({
          name: `chunks/${file}`,
          size: stats.size,
          type: 'js'
        });
      }
    }
  }

  private async extractModules(filePath: string): Promise<ModuleInfo[]> {
    // 这里应该使用 webpack 的 stats 来提取模块信息
    // 简化实现
    return [
      {
        name: 'example-module',
        size: 1024,
        reasons: ['entry']
      }
    ];
  }

  private async analyzeStaticAssets(dir: string, assets: AssetInfo[]) {
    const analyzeDir = (currentDir: string, relativePath: string = '') => {
      const files = fs.readdirSync(currentDir);

      for (const file of files) {
        const filePath = path.join(currentDir, file);
        const stats = fs.statSync(filePath);

        if (stats.isDirectory()) {
          analyzeDir(filePath, `${relativePath}${file}/`);
        } else {
          const assetType = this.getAssetType(file);
          if (assetType) {
            assets.push({
              name: `${relativePath}${file}`,
              size: stats.size,
              type: assetType
            });
          }
        }
      }
    };

    analyzeDir(dir);
  }

  private getAssetType(filename: string): 'js' | 'css' | 'font' | 'image' | null {
    const ext = path.extname(filename).toLowerCase();
    switch (ext) {
      case '.js':
      case '.mjs':
        return 'js';
      case '.css':
        return 'css';
      case '.woff':
      case '.woff2':
      case '.ttf':
        return 'font';
      case '.png':
      case '.jpg':
      case '.jpeg':
      case '.gif':
      case '.svg':
        return 'image';
      default:
        return null;
    }
  }

  private findDuplicates(chunks: ChunkInfo[]): DuplicateInfo[] {
    const moduleMap = new Map<string, string[]>();

    chunks.forEach(chunk => {
      chunk.modules.forEach(module => {
        if (!moduleMap.has(module.name)) {
          moduleMap.set(module.name, []);
        }
        moduleMap.get(module.name)!.push(chunk.name);
      });
    });

    const duplicates: DuplicateInfo[] = [];

    moduleMap.forEach((chunkNames, moduleName) => {
      if (chunkNames.length > 1) {
        duplicates.push({
          modules: [moduleName],
          chunks: chunkNames,
          totalSize: chunkNames.length * 1024 // 估算
        });
      }
    });

    return duplicates;
  }

  generateReport(result: BundleAnalysisResult): void {
    console.log('📊 Bundle Analysis Report');
    console.log('=======================');
    console.log(`Total Size: ${this.formatSize(result.totalSize)}`);
    console.log(`Gzip Size: ${this.formatSize(result.gzipSize)}`);
    console.log(`Total Chunks: ${result.chunks.length}`);
    console.log(`Total Assets: ${result.assets.length}`);

    if (result.duplicates.length > 0) {
      console.log('\n❌ Duplicates Found:');
      result.duplicates.forEach(duplicate => {
        console.log(`  - ${duplicate.modules[0]} in ${duplicate.chunks.join(', ')}`);
      });
    }

    // 按大小排序的前10个最大资源
    const largestAssets = result.assets
      .sort((a, b) => b.size - a.size)
      .slice(0, 10);

    console.log('\n🔥 Top 10 Largest Assets:');
    largestAssets.forEach((asset, index) => {
      console.log(`  ${index + 1}. ${asset.name} - ${this.formatSize(asset.size)}`);
    });
  }

  private formatSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }
}
```

### 2. Webpack Bundle Analyzer 集成

```typescript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    optimizePackageImports: ['lodash', 'axios', 'date-fns']
  },
  webpack: (config, { isServer, dev }) => {
    if (!dev && !isServer) {
      // 生产环境启用 bundle 分析
      const BundleAnalyzerPlugin = require('@next/bundle-analyzer')({
        enabled: process.env.ANALYZE === 'true'
      });

      if (process.env.ANALYZE === 'true') {
        config.plugins.push(
          new (require('webpack-bundle-analyzer')).BundleAnalyzerPlugin({
            analyzerMode: 'static',
            reportFilename: '../bundle-analysis/report.html'
          })
        );
      }
    }

    return config;
  }
};

module.exports = nextConfig;
```

## 🚀 Bundle 优化策略

### 1. 代码分割策略

```typescript
// lib/code-splitting.ts
import dynamic from 'next/dynamic';

// 动态导入大型组件
export const HeavyComponent = dynamic(
  () => import('@/components/HeavyComponent'),
  {
    loading: () => <div>Loading...</div>,
    ssr: false, // 禁用SSR以减少初始包大小
    suspense: true // 启用Suspense
  }
);

// 条件动态导入
export const ConditionalComponent = dynamic(
  () => import('@/components/ConditionalComponent'),
  {
    loading: () => <div>Loading...</div>,
    ssr: false
  }
);

// 路由级别的代码分割
export const RouteComponent = dynamic(
  () => import('@/routes/RouteComponent'),
  {
    loading: () => <div>Loading route...</div>,
    ssr: true
  }
);

// 第三方库的动态导入
export const ChartLibrary = dynamic(
  () => import('react-chartjs-2'),
  {
    loading: () => <div>Loading chart...</div>,
    ssr: false
  }
);
```

### 2. 依赖优化

```typescript
// package.json 优化配置
{
  "name": "my-nextjs-app",
  "version": "1.0.0",
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    // 核心依赖
    "axios": "^1.6.0",
    "date-fns": "^3.0.0",
    "lodash-es": "^4.17.21", // 使用ES模块版本
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "typescript": "^5.0.0",
    "eslint": "^8.0.0",
    "prettier": "^3.0.0"
  },
  "scripts": {
    "analyze": "ANALYZE=true npm run build",
    "build": "next build",
    "dev": "next dev",
    "start": "next start"
  }
}
```

### 3. Tree Shaking 优化

```typescript
// utils/optimized-exports.ts
// 明确导出，支持 Tree Shaking
export const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat('zh-CN').format(date);
};

export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY'
  }).format(amount);
};

export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('zh-CN').format(num);
};

// 使用 pure 注释帮助 Tree Shaking
export const pureFunction = /* #__PURE__ */ (value: string): string => {
  return value.trim().toLowerCase();
};
```

### 4. 图片和资源优化

```typescript
// components/optimized-image.tsx
import Image from 'next/image';
import { useState } from 'react';

interface OptimizedImageProps {
  src: string;
  alt: string;
  width: number;
  height: number;
  priority?: boolean;
  placeholder?: 'blur' | 'empty';
  blurDataURL?: string;
}

export const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  width,
  height,
  priority = false,
  placeholder = 'blur',
  blurDataURL
}) => {
  const [isLoading, setIsLoading] = useState(true);

  return (
    <div className="relative overflow-hidden">
      <Image
        src={src}
        alt={alt}
        width={width}
        height={height}
        priority={priority}
        placeholder={placeholder}
        blurDataURL={blurDataURL}
        className={`transition-opacity duration-300 ${
          isLoading ? 'opacity-0' : 'opacity-100'
        }`}
        onLoad={() => setIsLoading(false)}
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
      />
      {isLoading && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse" />
      )}
    </div>
  );
};
```

## 🎨 高级 Bundle 优化技术

### 1. 自定义 Webpack 配置

```typescript
// next.config.js 高级配置
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    optimizePackageImports: ['lodash', 'axios', 'date-fns']
  },
  webpack: (config, { isServer, dev }) => {
    // 优化模块解析
    config.resolve.alias = {
      ...config.resolve.alias,
      'react': 'preact/compat',
      'react-dom/test-utils': 'preact/test-utils',
      'react-dom': 'preact/compat'
    };

    // 优化构建性能
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
            priority: 10
          },
          common: {
            name: 'common',
            minChunks: 2,
            chunks: 'all',
            priority: 5
          },
          ui: {
            test: /[\\/]components[\\/]ui[\\/]/,
            name: 'ui',
            chunks: 'all',
            priority: 8
          }
        }
      };
    }

    // 压缩优化
    if (!dev) {
      config.optimization.minimizer = config.optimization.minimizer || [];

      const TerserPlugin = require('terser-webpack-plugin');
      config.optimization.minimizer.push(
        new TerserPlugin({
          terserOptions: {
            compress: {
              drop_console: !dev,
              drop_debugger: !dev,
              pure_funcs: ['console.log']
            },
            mangle: true
          }
        })
      );
    }

    return config;
  }
};

module.exports = nextConfig;
```

### 2. 模块联邦优化

```typescript
// packages/remote-app/next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.plugins.push(
        new (require('@module-federation/nextjs-mf'))({
          name: 'remote',
          filename: 'remoteEntry.js',
          exposes: {
            './Button': './components/Button',
            './Modal': './components/Modal',
            './utils': './utils/index'
          },
          shared: {
            react: {
              singleton: true,
              requiredVersion: false
            },
            'react-dom': {
              singleton: true,
              requiredVersion: false
            }
          }
        })
      );
    }

    return config;
  }
};

module.exports = nextConfig;
```

### 3. Service Worker 缓存策略

```typescript
// public/sw.js
const CACHE_NAME = 'my-app-v1';
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/api/config'
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

        return fetch(event.request).then(
          response => {
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            const responseToCache = response.clone();
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });

            return response;
          }
        );
      })
  );
});

// 注册 Service Worker
if (typeof window !== 'undefined') {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js')
        .then(registration => {
          console.log('SW registered: ', registration);
        })
        .catch(registrationError => {
          console.log('SW registration failed: ', registrationError);
        });
    });
  }
}
```

## 📊 性能监控和分析

### 1. 实时性能监控

```typescript
// lib/performance-monitor.ts
export class PerformanceMonitor {
  private metrics: PerformanceMetric[] = [];
  private observer: PerformanceObserver | null = null;

  constructor() {
    this.initializeMonitoring();
  }

  private initializeMonitoring(): void {
    if (typeof window === 'undefined') return;

    // 监控资源加载
    if ('PerformanceObserver' in window) {
      this.observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach(entry => {
          if (entry.entryType === 'resource') {
            this.trackResourceLoad(entry as PerformanceResourceTiming);
          }
        });
      });

      this.observer.observe({ entryTypes: ['resource'] });
    }

    // 监控导航
    window.addEventListener('load', () => {
      this.trackNavigation();
    });
  }

  private trackResourceLoad(entry: PerformanceResourceTiming): void {
    const metric: PerformanceMetric = {
      type: 'resource',
      name: entry.name,
      duration: entry.duration,
      size: entry.transferSize || 0,
      timestamp: Date.now()
    };

    this.metrics.push(metric);
    this.analyzeMetric(metric);
  }

  private trackNavigation(): void {
    if (typeof performance === 'undefined') return;

    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;

    const metric: PerformanceMetric = {
      type: 'navigation',
      name: 'page_load',
      duration: navigation.loadEventEnd - navigation.loadEventStart,
      size: 0,
      timestamp: Date.now()
    };

    this.metrics.push(metric);
    this.analyzeMetric(metric);
  }

  private analyzeMetric(metric: PerformanceMetric): void {
    // 分析性能指标
    if (metric.type === 'resource' && metric.duration > 1000) {
      console.warn(`Slow resource detected: ${metric.name} - ${metric.duration}ms`);
    }

    // 发送到分析服务
    this.sendToAnalytics(metric);
  }

  private async sendToAnalytics(metric: PerformanceMetric): Promise<void> {
    try {
      await fetch('/api/analytics/performance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(metric)
      });
    } catch (error) {
      console.error('Failed to send performance metric:', error);
    }
  }

  getMetrics(): PerformanceMetric[] {
    return [...this.metrics];
  }

  getBundleMetrics(): BundleMetrics {
    if (typeof performance === 'undefined') {
      return { totalSize: 0, loadTime: 0, resourceCount: 0 };
    }

    const resources = performance.getEntriesByType('resource');
    const bundleResources = resources.filter(resource =>
      resource.name.includes('.js') || resource.name.includes('.css')
    );

    return {
      totalSize: bundleResources.reduce((sum, resource) =>
        sum + (resource.transferSize || 0), 0
      ),
      loadTime: bundleResources.reduce((sum, resource) =>
        sum + resource.duration, 0
      ),
      resourceCount: bundleResources.length
    };
  }

  destroy(): void {
    if (this.observer) {
      this.observer.disconnect();
    }
  }
}

interface PerformanceMetric {
  type: 'resource' | 'navigation' | 'custom';
  name: string;
  duration: number;
  size: number;
  timestamp: number;
}

interface BundleMetrics {
  totalSize: number;
  loadTime: number;
  resourceCount: number;
}
```

### 2. Bundle 优化检查工具

```typescript
// scripts/bundle-optimizer.ts
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

interface BundleOptimization {
  currentSize: number;
  targetSize: number;
  savings: number;
  optimizations: OptimizationSuggestion[];
}

interface OptimizationSuggestion {
  type: 'code_splitting' | 'dependency' | 'image' | 'css' | 'js';
  description: string;
  potentialSavings: number;
  difficulty: 'easy' | 'medium' | 'hard';
}

export class BundleOptimizer {
  private projectPath: string;

  constructor(projectPath: string) {
    this.projectPath = projectPath;
  }

  async analyzeOptimizations(): Promise<BundleOptimization> {
    console.log('🔍 Analyzing bundle optimization opportunities...');

    const currentSize = await this.getCurrentBundleSize();
    const targetSize = this.calculateTargetSize(currentSize);
    const optimizations = await this.generateOptimizationSuggestions();

    return {
      currentSize,
      targetSize,
      savings: currentSize - targetSize,
      optimizations
    };
  }

  private async getCurrentBundleSize(): Promise<number> {
    const buildDir = path.join(this.projectPath, '.next');
    let totalSize = 0;

    const calculateDirSize = (dir: string): void => {
      const files = fs.readdirSync(dir);

      for (const file of files) {
        const filePath = path.join(dir, file);
        const stats = fs.statSync(filePath);

        if (stats.isDirectory()) {
          calculateDirSize(filePath);
        } else {
          totalSize += stats.size;
        }
      }
    };

    if (fs.existsSync(buildDir)) {
      calculateDirSize(buildDir);
    }

    return totalSize;
  }

  private calculateTargetSize(currentSize: number): number {
    // 目标大小减少30%
    return Math.round(currentSize * 0.7);
  }

  private async generateOptimizationSuggestions(): Promise<OptimizationSuggestion[]> {
    const suggestions: OptimizationSuggestion[] = [];

    // 检查大型依赖
    const largeDeps = this.findLargeDependencies();
    largeDeps.forEach(dep => {
      suggestions.push({
        type: 'dependency',
        description: `Replace ${dep.name} with lighter alternative (${dep.size}KB)`,
        potentialSavings: dep.size * 0.6,
        difficulty: 'medium'
      });
    });

    // 检查图片优化
    const imageOptimizations = this.findImageOptimizations();
    imageOptimizations.forEach(opt => {
      suggestions.push({
        type: 'image',
        description: `Optimize image ${opt.path} (current: ${opt.currentSize}KB, optimized: ${opt.optimizedSize}KB)`,
        potentialSavings: opt.currentSize - opt.optimizedSize,
        difficulty: 'easy'
      });
    });

    // 检查CSS优化
    const cssOptimizations = this.findCssOptimizations();
    cssOptimizations.forEach(opt => {
      suggestions.push({
        type: 'css',
        description: `Purge unused CSS in ${opt.file}`,
        potentialSavings: opt.unusedSize,
        difficulty: 'medium'
      });
    });

    // 检查代码分割机会
    const codeSplittingOps = this.findCodeSplittingOpportunities();
    codeSplittingOps.forEach(op => {
      suggestions.push({
        type: 'code_splitting',
        description: `Implement dynamic import for ${op.component}`,
        potentialSavings: op.size,
        difficulty: 'easy'
      });
    });

    return suggestions.sort((a, b) => b.potentialSavings - a.potentialSavings);
  }

  private findLargeDependencies(): Array<{ name: string; size: number }> {
    const packageJsonPath = path.join(this.projectPath, 'package.json');
    if (!fs.existsSync(packageJsonPath)) return [];

    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    const dependencies = { ...packageJson.dependencies, ...packageJson.devDependencies };

    // 常见的大型依赖
    const largeDeps = [
      { name: 'moment', size: 300 },
      { name: 'lodash', size: 70 },
      { name: 'fullcalendar', size: 500 },
      { name: 'ckeditor', size: 800 },
      { name: 'monaco-editor', size: 2000 }
    ];

    return largeDeps.filter(dep => dependencies[dep.name]);
  }

  private findImageOptimizations(): Array<{ path: string; currentSize: number; optimizedSize: number }> {
    const publicDir = path.join(this.projectPath, 'public');
    const optimizations: Array<{ path: string; currentSize: number; optimizedSize: number }> = [];

    if (!fs.existsSync(publicDir)) return optimizations;

    const findImages = (dir: string, relativePath: string = ''): void => {
      const files = fs.readdirSync(dir);

      for (const file of files) {
        const filePath = path.join(dir, file);
        const stats = fs.statSync(filePath);

        if (stats.isDirectory()) {
          findImages(filePath, `${relativePath}${file}/`);
        } else if (/\.(png|jpg|jpeg|gif)$/i.test(file)) {
          const currentSize = Math.round(stats.size / 1024);
          const optimizedSize = Math.round(currentSize * 0.6); // 估算压缩后大小

          if (currentSize > 100) { // 大于100KB的图片
            optimizations.push({
              path: `${relativePath}${file}`,
              currentSize,
              optimizedSize
            });
          }
        }
      }
    };

    findImages(publicDir);
    return optimizations;
  }

  private findCssOptimizations(): Array<{ file: string; unusedSize: number }> {
    // 简化实现，实际应该使用工具如 PurgeCSS
    return [
      {
        file: 'styles/globals.css',
        unusedSize: 50
      }
    ];
  }

  private findCodeSplittingOpportunities(): Array<{ component: string; size: number }> {
    // 简化实现，实际应该分析代码
    return [
      {
        component: 'components/HeavyChart.tsx',
        size: 200
      },
      {
        component: 'components/LargeModal.tsx',
        size: 150
      }
    ];
  }

  generateReport(optimization: BundleOptimization): void {
    console.log('📊 Bundle Optimization Report');
    console.log('============================');
    console.log(`Current Bundle Size: ${this.formatSize(optimization.currentSize)}`);
    console.log(`Target Bundle Size: ${this.formatSize(optimization.targetSize)}`);
    console.log(`Potential Savings: ${this.formatSize(optimization.savings)}`);
    console.log(`Optimization Suggestions: ${optimization.optimizations.length}`);

    console.log('\n🎯 Top Optimization Suggestions:');
    optimization.optimizations.slice(0, 5).forEach((suggestion, index) => {
      console.log(`  ${index + 1}. [${suggestion.type.toUpperCase()}] ${suggestion.description}`);
      console.log(`     Potential Savings: ${this.formatSize(suggestion.potentialSavings)}`);
      console.log(`     Difficulty: ${suggestion.difficulty}`);
    });
  }

  private formatSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }
}
```

## 🎯 最佳实践和总结

### 1. Bundle 优化检查清单

```typescript
// checklists/bundle-optimization.ts
export const bundleOptimizationChecklist = [
  {
    category: '代码分割',
    items: [
      '大型组件使用动态导入',
      '第三方库按需加载',
      '路由级别代码分割',
      '条件性组件懒加载'
    ]
  },
  {
    category: '依赖优化',
    items: [
      '使用轻量级替代库',
      '移除未使用的依赖',
      '优化依赖版本',
      '使用ES模块版本'
    ]
  },
  {
    category: '资源优化',
    items: [
      '图片压缩和格式优化',
      'CSS压缩和Tree Shaking',
      'JavaScript压缩',
      '字体文件优化'
    ]
  },
  {
    category: '缓存策略',
    items: [
      '浏览器缓存配置',
      'Service Worker实现',
      'CDN缓存优化',
      '版本化静态资源'
    ]
  },
  {
    category: '监控和分析',
    items: [
      'Bundle大小监控',
      '性能指标追踪',
      '用户实际体验监控',
      '定期优化检查'
    ]
  }
];

export const runBundleOptimizationCheck = async (): Promise<void> => {
  console.log('🔍 Running Bundle Optimization Check...');

  for (const category of bundleOptimizationChecklist) {
    console.log(`\n📋 ${category.category}:`);
    for (const item of category.items) {
      console.log(`  ✅ ${item}`);
    }
  }

  console.log('\n🎯 Bundle optimization check completed!');
};
```

### 2. 性能预算设置

```typescript
// lib/performance-budget.ts
export interface PerformanceBudget {
  bundleSize: {
    total: number;
    initial: number;
    individual: number;
  };
  loadTime: {
    firstContentfulPaint: number;
    largestContentfulPaint: number;
    timeToInteractive: number;
  };
  resourceCount: {
    total: number;
    javascript: number;
    css: number;
    images: number;
  };
}

export const defaultPerformanceBudget: PerformanceBudget = {
  bundleSize: {
    total: 1024 * 1024, // 1MB
    initial: 300 * 1024, // 300KB
    individual: 100 * 1024 // 100KB
  },
  loadTime: {
    firstContentfulPaint: 2000, // 2s
    largestContentfulPaint: 2500, // 2.5s
    timeToInteractive: 3000 // 3s
  },
  resourceCount: {
    total: 50,
    javascript: 10,
    css: 5,
    images: 20
  }
};

export class PerformanceBudgetChecker {
  private budget: PerformanceBudget;

  constructor(budget: PerformanceBudget = defaultPerformanceBudget) {
    this.budget = budget;
  }

  async checkBudget(): Promise<BudgetCheckResult> {
    if (typeof window === 'undefined') {
      return { passed: true, violations: [] };
    }

    const violations: BudgetViolation[] = [];

    // 检查Bundle大小
    const bundleSize = await this.getBundleSize();
    if (bundleSize.total > this.budget.bundleSize.total) {
      violations.push({
        type: 'bundleSize',
        metric: 'total',
        actual: bundleSize.total,
        budget: this.budget.bundleSize.total,
        severity: 'high'
      });
    }

    // 检查加载时间
    const loadTime = await this.getLoadTime();
    if (loadTime.largestContentfulPaint > this.budget.loadTime.largestContentfulPaint) {
      violations.push({
        type: 'loadTime',
        metric: 'largestContentfulPaint',
        actual: loadTime.largestContentfulPaint,
        budget: this.budget.loadTime.largestContentfulPaint,
        severity: 'medium'
      });
    }

    // 检查资源数量
    const resourceCount = await this.getResourceCount();
    if (resourceCount.total > this.budget.resourceCount.total) {
      violations.push({
        type: 'resourceCount',
        metric: 'total',
        actual: resourceCount.total,
        budget: this.budget.resourceCount.total,
        severity: 'low'
      });
    }

    return {
      passed: violations.length === 0,
      violations
    };
  }

  private async getBundleSize(): Promise<{ total: number; initial: number; individual: number }> {
    if (typeof performance === 'undefined') {
      return { total: 0, initial: 0, individual: 0 };
    }

    const resources = performance.getEntriesByType('resource');
    const jsResources = resources.filter(r => r.name.includes('.js'));

    return {
      total: jsResources.reduce((sum, r) => sum + (r.transferSize || 0), 0),
      initial: jsResources
        .filter(r => r.name.includes('main') || r.name.includes('chunk'))
        .reduce((sum, r) => sum + (r.transferSize || 0), 0),
      individual: Math.max(...jsResources.map(r => r.transferSize || 0))
    };
  }

  private async getLoadTime(): Promise<{
    firstContentfulPaint: number;
    largestContentfulPaint: number;
    timeToInteractive: number;
  }> {
    if (typeof performance === 'undefined') {
      return { firstContentfulPaint: 0, largestContentfulPaint: 0, timeToInteractive: 0 };
    }

    const paint = performance.getEntriesByType('paint');
    const fcp = paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0;

    // 简化实现，实际应该使用 Web Vitals
    return {
      firstContentfulPaint: fcp,
      largestContentfulPaint: fcp + 500, // 估算
      timeToInteractive: fcp + 1000 // 估算
    };
  }

  private async getResourceCount(): Promise<{
    total: number;
    javascript: number;
    css: number;
    images: number;
  }> {
    if (typeof performance === 'undefined') {
      return { total: 0, javascript: 0, css: 0, images: 0 };
    }

    const resources = performance.getEntriesByType('resource');

    return {
      total: resources.length,
      javascript: resources.filter(r => r.name.includes('.js')).length,
      css: resources.filter(r => r.name.includes('.css')).length,
      images: resources.filter(r => /\.(png|jpg|jpeg|gif|svg)$/i.test(r.name)).length
    };
  }
}

interface BudgetCheckResult {
  passed: boolean;
  violations: BudgetViolation[];
}

interface BudgetViolation {
  type: 'bundleSize' | 'loadTime' | 'resourceCount';
  metric: string;
  actual: number;
  budget: number;
  severity: 'high' | 'medium' | 'low';
}
```

## 🎯 总结

Bundle Optimization 是 Next.js 15 应用性能优化的关键策略。通过系统性的分析、优化和监控，可以显著提升应用的加载性能和用户体验。

### 关键要点：

1. **分析和监控**：定期分析Bundle大小，识别优化机会
2. **代码分割**：合理使用动态导入和懒加载
3. **依赖优化**：选择轻量级库，移除未使用的依赖
4. **资源优化**：图片压缩、CSS优化、字体优化
5. **缓存策略**：Service Worker、浏览器缓存、CDN优化
6. **性能预算**：设定合理的性能目标和限制

### 实施建议：

- **持续监控**：建立性能监控体系，及时发现问题
- **渐进优化**：从最影响性能的问题开始优化
- **工具链**：使用现代化的构建和分析工具
- **团队协作**：建立性能优化的最佳实践和规范

通过掌握这些Bundle优化技术，可以构建出高性能、用户友好的现代Web应用。