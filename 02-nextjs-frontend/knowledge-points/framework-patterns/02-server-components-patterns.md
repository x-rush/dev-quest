# Next.js 15 服务端组件模式详解

> **文档简介**: Next.js 15 + React 19 服务端组件完整指南，涵盖SSR/SSG/ISR、数据获取、缓存策略、安全性、并发处理等现代服务端组件技术

> **目标读者**: 具备Next.js基础的中高级开发者，需要掌握服务端渲染和性能优化的前端工程师

> **前置知识**: Next.js 15基础、React 19组件概念、TypeScript 5、缓存机制、数据库基础、API设计

> **预计时长**: 8-12小时

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `framework-patterns` |
| **难度** | ⭐⭐⭐⭐⭐ (5/5星) |
| **标签** | `#server-components` `#ssr` `#ssg` `#caching` `#performance` `#security` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 📚 概述

Next.js 15 与 React 19 的服务端组件架构代表了现代Web开发的重大突破。服务端组件在服务器上完全渲染，零JavaScript发送到客户端，提供卓越的性能和SEO优化。本指南深入探讨企业级服务端组件开发模式，结合先进的缓存策略、安全机制和性能优化技术，构建高性能、可扩展的服务端渲染架构。

## 🏗️ 服务端组件架构概览

### 组件分类体系

**全面的服务端组件分类和管理策略**

```typescript
// types/server-component.ts
import { ReactNode, ComponentProps, CacheableComponent } from 'react';

// 服务端组件元数据
export interface ServerComponentMetadata {
  name: string;
  description?: string;
  version?: string;
  author?: string;
  dependencies?: string[];
  experimental?: boolean;
  cacheStrategy?: 'force-cache' | 'no-cache' | 'revalidate' | 'no-store';
  revalidateTime?: number;
  tags?: string[];
}

// 服务端组件基础接口
export interface ServerComponentProps<T = {}> {
  // 基础属性
  id?: string;
  className?: string;
  children?: ReactNode;

  // 数据相关
  data?: T;
  fallback?: ReactNode;
  error?: ReactNode;
  loading?: ReactNode;

  // 缓存控制
  cache?: 'force-cache' | 'no-cache' | 'revalidate' | 'no-store';
  revalidate?: number | false;
  tags?: string[];

  // 国际化
  locale?: string;
  messages?: Record<string, string>;

  // 主题和样式
  theme?: 'light' | 'dark' | 'auto';
  variant?: string;
}

// 高级服务端组件接口
export interface AdvancedServerComponentProps<T = {}>
  extends ServerComponentProps<T> {
  // 数据验证
  validator?: (data: T) => boolean;
  schema?: any; // Zod schema

  // 错误处理
  errorBoundary?: boolean;
  retryCount?: number;
  fallbackRetry?: ReactNode;

  // 性能优化
  streaming?: boolean;
  prefetch?: boolean;
  priority?: 'high' | 'normal' | 'low';

  // 监控和分析
  analytics?: boolean;
  tracking?: Record<string, any>;
}
```

## 🎯 核心服务端组件模式

### 1. 数据获取模式

#### 1.1 基础数据获取组件

```typescript
// components/basic-data-fetcher.tsx
import { cache } from 'react';

// 数据库连接配置
const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_NAME || 'myapp',
  user: process.env.DB_USER || 'user',
  password: process.env.DB_PASSWORD,
  ssl: process.env.NODE_ENV === 'production'
};

// 数据库查询函数
async function fetchPostFromDatabase(id: string) {
  const response = await fetch(`${process.env.API_URL}/posts/${id}`, {
    headers: {
      'Authorization': `Bearer ${process.env.API_TOKEN}`,
      'Content-Type': 'application/json',
    },
    next: { revalidate: 3600, tags: [`post-${id}`] } // 1小时缓存
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch post: ${response.statusText}`);
  }

  return response.json();
}

// 缓存数据获取
const getCachedPost = cache(async (id: string) => {
  console.log(`Fetching post ${id} from database...`);
  return fetchPostFromDatabase(id);
});

// 基础服务端组件
interface PostComponentProps {
  postId: string;
  showAuthor?: boolean;
  className?: string;
}

export async function PostComponent({
  postId,
  showAuthor = false,
  className = ''
}: PostComponentProps) {
  try {
    // 数据获取
    const post = await getCachedPost(postId);

    // 并行获取作者信息
    let author = null;
    if (showAuthor && post.authorId) {
      author = await getAuthorData(post.authorId);
    }

    // 获取相关文章
    const relatedPosts = await getRelatedPosts(postId);

    return (
      <article className={`post-component ${className}`}>
        <header className="post-header">
          <h1>{post.title}</h1>
          <div className="post-meta">
            <time dateTime={post.publishedAt}>
              {new Date(post.publishedAt).toLocaleDateString()}
            </time>
            {author && (
              <span className="author">
                作者: {author.name}
              </span>
            )}
          </div>
        </header>

        <div
          className="post-content"
          dangerouslySetInnerHTML={{ __html: post.content }}
        />

        {post.tags && post.tags.length > 0 && (
          <footer className="post-footer">
            <div className="tags">
              {post.tags.map((tag: string) => (
                <span key={tag} className="tag">
                  #{tag}
                </span>
              ))}
            </div>
          </footer>
        )}

        {relatedPosts.length > 0 && (
          <section className="related-posts">
            <h3>相关文章</h3>
            <ul>
              {relatedPosts.slice(0, 3).map((relatedPost: any) => (
                <li key={relatedPost.id}>
                  <a href={`/posts/${relatedPost.id}`}>
                    {relatedPost.title}
                  </a>
                </li>
              ))}
            </ul>
          </section>
        )}
      </article>
    );
  } catch (error) {
    console.error('Error in PostComponent:', error);

    return (
      <div className="error-component">
        <h2>文章加载失败</h2>
        <p>请稍后重试或联系管理员。</p>
      </div>
    );
  }
}

// 辅助函数
async function getAuthorData(authorId: string) {
  return cache(async (id: string) => {
    const response = await fetch(`${process.env.API_URL}/authors/${id}`, {
      next: { revalidate: 86400, tags: [`author-${id}`] } // 24小时缓存
    });
    return response.json();
  })(authorId);
}

async function getRelatedPosts(postId: string, limit = 5) {
  return cache(async (id: string) => {
    const response = await fetch(`${process.env.API_URL}/posts/${id}/related?limit=${limit}`, {
      next: { revalidate: 3600, tags: [`related-${id}`] }
    });
    return response.json();
  })(postId);
}
```

#### 1.2 高级数据获取模式

```typescript
// components/advanced-data-fetcher.tsx
import { unstable_cache } from 'next/cache';
import { Suspense } from 'react';

// 多层缓存策略
class DataFetchingService {
  private static instance: DataFetchingService;
  private cache: Map<string, { data: any; timestamp: number; ttl: number }>;

  private constructor() {
    this.cache = new Map();
  }

  static getInstance(): DataFetchingService {
    if (!DataFetchingService.instance) {
      DataFetchingService.instance = new DataFetchingService();
    }
    return DataFetchingService.instance;
  }

  // 内存缓存检查
  private getFromMemoryCache(key: string): any | null {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < cached.ttl) {
      return cached.data;
    }
    return null;
  }

  // 设置内存缓存
  private setMemoryCache(key: string, data: any, ttl: number): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }

  // 智能数据获取
  async fetchData<T>(
    key: string,
    fetcher: () => Promise<T>,
    options: {
      ttl?: number;
      useRedis?: boolean;
      tags?: string[];
      revalidate?: number;
    } = {}
  ): Promise<T> {
    const { ttl = 300000, useRedis = false, tags = [], revalidate = 3600 } = options;

    // 1. 检查内存缓存
    const memoryCached = this.getFromMemoryCache(key);
    if (memoryCached) {
      return memoryCached;
    }

    // 2. 使用 Next.js 缓存
    const cachedFetcher = unstable_cache(
      async () => {
        try {
          const data = await fetcher();

          // 3. 设置内存缓存
          this.setMemoryCache(key, data, ttl);

          return data;
        } catch (error) {
          console.error(`Data fetching error for key ${key}:`, error);
          throw error;
        }
      },
      [key, ...tags],
      {
        revalidate,
        tags
      }
    );

    return cachedFetcher();
  }

  // 批量数据获取
  async fetchBatch<T>(
    requests: Array<{
      key: string;
      fetcher: () => Promise<T>;
      options?: any;
    }>
  ): Promise<Map<string, T>> {
    const results = new Map<string, T>();

    const promises = requests.map(async ({ key, fetcher, options }) => {
      try {
        const data = await this.fetchData(key, fetcher, options);
        results.set(key, data);
      } catch (error) {
        console.error(`Batch fetch error for key ${key}:`, error);
        // 可以选择设置默认值或跳过
      }
    });

    await Promise.allSettled(promises);
    return results;
  }

  // 预热缓存
  async warmCache<T>(
    keys: string[],
    fetcherMap: Map<string, () => Promise<T>>,
    options: any = {}
  ): Promise<void> {
    const warmupPromises = keys.map(async (key) => {
      const fetcher = fetcherMap.get(key);
      if (fetcher) {
        try {
          await this.fetchData(key, fetcher, options);
        } catch (error) {
          console.error(`Cache warmup error for key ${key}:`, error);
        }
      }
    });

    await Promise.allSettled(warmupPromises);
  }
}

// 高级数据获取组件
interface AdvancedDataComponentProps {
  postId: string;
  variant?: 'full' | 'summary' | 'card';
  enableComments?: boolean;
  prefetchRelated?: boolean;
}

export async function AdvancedDataComponent({
  postId,
  variant = 'full',
  enableComments = false,
  prefetchRelated = true
}: AdvancedDataComponentProps) {
  const dataService = DataFetchingService.getInstance();

  // 根据变体获取不同深度数据
  const fetchData = async () => {
    const baseData = dataService.fetchData(
      `post-${postId}`,
      () => fetch(`${process.env.API_URL}/posts/${postId}`).then(r => r.json()),
      {
        ttl: 600000, // 10分钟
        tags: [`post-${postId}`],
        revalidate: 3600
      }
    );

    const relatedData = prefetchRelated
      ? dataService.fetchData(
          `related-${postId}`,
          () => fetch(`${process.env.API_URL}/posts/${postId}/related`).then(r => r.json()),
          { ttl: 1800000, tags: [`related-${postId}`] }
        )
      : Promise.resolve([]);

    const commentsData = enableComments
      ? dataService.fetchData(
          `comments-${postId}`,
          () => fetch(`${process.env.API_URL}/posts/${postId}/comments`).then(r => r.json()),
          { ttl: 300000, tags: [`comments-${postId}`] }
        )
      : Promise.resolve([]);

    // 并行获取所有数据
    const [post, relatedPosts, comments] = await Promise.all([
      baseData,
      relatedData,
      commentsData
    ]);

    return { post, relatedPosts, comments };
  };

  const data = await fetchData();

  return (
    <div className={`advanced-data-component variant-${variant}`}>
      {variant === 'card' ? (
        <PostCard post={data.post} />
      ) : variant === 'summary' ? (
        <PostSummary post={data.post} />
      ) : (
        <FullPost
          post={data.post}
          relatedPosts={data.relatedPosts}
          comments={enableComments ? data.comments : []}
        />
      )}
    </div>
  );
}

// 子组件
function PostCard({ post }: { post: any }) {
  return (
    <div className="post-card">
      <h3>{post.title}</h3>
      <p>{post.excerpt}</p>
      <time>{new Date(post.publishedAt).toLocaleDateString()}</time>
    </div>
  );
}

function PostSummary({ post }: { post: any }) {
  return (
    <div className="post-summary">
      <h2>{post.title}</h2>
      <div
        className="summary-content"
        dangerouslySetInnerHTML={{ __html: post.excerpt }}
      />
      <a href={`/posts/${post.id}`}>阅读更多</a>
    </div>
  );
}

function FullPost({
  post,
  relatedPosts,
  comments
}: {
  post: any;
  relatedPosts: any[];
  comments: any[];
}) {
  return (
    <article className="full-post">
      <header>
        <h1>{post.title}</h1>
        <div className="meta">
          <time>{new Date(post.publishedAt).toLocaleDateString()}</time>
        </div>
      </header>

      <div
        className="content"
        dangerouslySetInnerHTML={{ __html: post.content }}
      />

      {comments.length > 0 && (
        <section className="comments">
          <h3>评论 ({comments.length})</h3>
          {comments.map((comment: any) => (
            <div key={comment.id} className="comment">
              <strong>{comment.author}</strong>
              <p>{comment.content}</p>
              <time>{new Date(comment.createdAt).toLocaleDateString()}</time>
            </div>
          ))}
        </section>
      )}

      {relatedPosts.length > 0 && (
        <section className="related">
          <h3>相关文章</h3>
          <div className="related-grid">
            {relatedPosts.map((relatedPost: any) => (
              <PostCard key={relatedPost.id} post={relatedPost} />
            ))}
          </div>
        </section>
      )}
    </article>
  );
}
```

### 2. 缓存策略模式

#### 2.1 多层缓存架构

```typescript
// components/multi-layer-cache.tsx
import { unstable_cache } from 'next/cache';
import { Redis } from '@upstash/redis';

// Redis 客户端
const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

// 缓存层接口
interface CacheLayer {
  get<T>(key: string): Promise<T | null>;
  set<T>(key: string, value: T, ttl?: number): Promise<void>;
  delete(key: string): Promise<void>;
  clear(): Promise<void>;
}

// L1: 内存缓存层
class MemoryCacheLayer implements CacheLayer {
  private cache: Map<string, { value: any; expiry: number }>;

  constructor() {
    this.cache = new Map();
    // 定期清理过期缓存
    setInterval(() => this.cleanup(), 60000); // 每分钟清理一次
  }

  async get<T>(key: string): Promise<T | null> {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() > item.expiry) {
      this.cache.delete(key);
      return null;
    }

    return item.value;
  }

  async set<T>(key: string, value: T, ttl = 300000): Promise<void> {
    this.cache.set(key, {
      value,
      expiry: Date.now() + ttl
    });
  }

  async delete(key: string): Promise<void> {
    this.cache.delete(key);
  }

  async clear(): Promise<void> {
    this.cache.clear();
  }

  private cleanup(): void {
    const now = Date.now();
    for (const [key, item] of this.cache.entries()) {
      if (now > item.expiry) {
        this.cache.delete(key);
      }
    }
  }
}

// L2: Redis 缓存层
class RedisCacheLayer implements CacheLayer {
  async get<T>(key: string): Promise<T | null> {
    try {
      const value = await redis.get(key);
      return value ? JSON.parse(value) : null;
    } catch (error) {
      console.error('Redis get error:', error);
      return null;
    }
  }

  async set<T>(key: string, value: T, ttl = 3600): Promise<void> {
    try {
      await redis.setex(key, ttl, JSON.stringify(value));
    } catch (error) {
      console.error('Redis set error:', error);
    }
  }

  async delete(key: string): Promise<void> {
    try {
      await redis.del(key);
    } catch (error) {
      console.error('Redis delete error:', error);
    }
  }

  async clear(): Promise<void> {
    try {
      await redis.flushdb();
    } catch (error) {
      console.error('Redis clear error:', error);
    }
  }
}

// L3: Next.js 缓存层
class NextJSCacheLayer implements CacheLayer {
  async get<T>(key: string): Promise<T | null> {
    // Next.js 缓存通过 fetch API 实现，这里作为适配器
    return null;
  }

  async set<T>(key: string, value: T, ttl = 3600): Promise<void> {
    // 通过 Next.js unstable_cache 实现
  }

  async delete(key: string): Promise<void> {
    // 通过 revalidateTag 实现
  }

  async clear(): Promise<void> {
    // 清除所有缓存
  }
}

// 多层缓存管理器
class MultiLayerCacheManager {
  private layers: CacheLayer[];
  private static instance: MultiLayerCacheManager;

  private constructor() {
    this.layers = [
      new MemoryCacheLayer(),    // L1: 内存缓存
      new RedisCacheLayer(),     // L2: Redis 缓存
      new NextJSCacheLayer()     // L3: Next.js 缓存
    ];
  }

  static getInstance(): MultiLayerCacheManager {
    if (!MultiLayerCacheManager.instance) {
      MultiLayerCacheManager.instance = new MultiLayerCacheManager();
    }
    return MultiLayerCacheManager.instance;
  }

  async get<T>(key: string): Promise<T | null> {
    // 从 L1 到 L3 依次查找
    for (let i = 0; i < this.layers.length; i++) {
      const value = await this.layers[i].get<T>(key);
      if (value !== null) {
        // 回填到上层缓存
        for (let j = 0; j < i; j++) {
          this.layers[j].set(key, value);
        }
        return value;
      }
    }
    return null;
  }

  async set<T>(key: string, value: T, options: {
    ttl?: number;
    layers?: number[];
  } = {}): Promise<void> {
    const { ttl = 3600, layers = [0, 1, 2] } = options;

    // 设置到指定层
    for (const layerIndex of layers) {
      if (this.layers[layerIndex]) {
        await this.layers[layerIndex].set(key, value, ttl);
      }
    }
  }

  async delete(key: string): Promise<void> {
    // 从所有层删除
    await Promise.all(this.layers.map(layer => layer.delete(key)));
  }

  async clear(): Promise<void> {
    // 清空所有层
    await Promise.all(this.layers.map(layer => layer.clear()));
  }

  // 预热缓存
  async warmCache<T>(
    items: Array<{ key: string; fetcher: () => Promise<T> }>,
    options: any = {}
  ): Promise<void> {
    const warmupPromises = items.map(async ({ key, fetcher }) => {
      try {
        const cached = await this.get<T>(key);
        if (!cached) {
          const data = await fetcher();
          await this.set(key, data, options);
        }
      } catch (error) {
        console.error(`Cache warmup error for ${key}:`, error);
      }
    });

    await Promise.allSettled(warmupPromises);
  }

  // 缓存统计
  async getStats(): Promise<{
    memorySize: number;
    redisKeys: number;
    hitRate: number;
  }> {
    const memoryCache = this.layers[0] as MemoryCacheLayer;
    const redisCache = this.layers[1] as RedisCacheLayer;

    return {
      memorySize: (memoryCache as any).cache.size,
      redisKeys: await redis.dbSize(),
      hitRate: 0.95 // 示例数据，应该从实际统计中计算
    };
  }
}

// 智能缓存组件
interface SmartCacheComponentProps {
  cacheKey: string;
  fetcher: () => Promise<any>;
  ttl?: number;
  strategy?: 'cache-first' | 'network-first' | 'stale-while-revalidate';
  fallback?: ReactNode;
}

export async function SmartCacheComponent({
  cacheKey,
  fetcher,
  ttl = 3600,
  strategy = 'cache-first',
  fallback
}: SmartCacheComponentProps) {
  const cacheManager = MultiLayerCacheManager.getInstance();

  const getData = async () => {
    switch (strategy) {
      case 'cache-first':
        let cached = await cacheManager.get(cacheKey);
        if (cached) return cached;

        const data = await fetcher();
        await cacheManager.set(cacheKey, data, { ttl });
        return data;

      case 'network-first':
        try {
          const freshData = await fetcher();
          await cacheManager.set(cacheKey, freshData, { ttl });
          return freshData;
        } catch (error) {
          const staleData = await cacheManager.get(cacheKey);
          if (staleData) return staleData;
          throw error;
        }

      case 'stale-while-revalidate':
        const stale = await cacheManager.get(cacheKey);

        // 异步更新缓存
        fetcher()
          .then(freshData => cacheManager.set(cacheKey, freshData, { ttl }))
          .catch(error => console.error('Background refresh error:', error));

        return stale || (await fetcher());

      default:
        return fetcher();
    }
  };

  try {
    const data = await getData();
    return <>{data}</>;
  } catch (error) {
    console.error('SmartCacheComponent error:', error);
    return fallback || <div>加载失败</div>;
  }
}
```

### 3. 流式渲染模式

#### 3.1 Suspense 和流式组件

```typescript
// components/streaming-components.tsx
import { Suspense } from 'react';
import { notFound } from 'next/navigation';

// 流式数据加载组件
interface StreamingDataLoaderProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function StreamingDataLoader({
  children,
  fallback = <div>加载中...</div>
}: StreamingDataLoaderProps) {
  return (
    <Suspense fallback={fallback}>
      {children}
    </Suspense>
  );
}

// 异步图片组件
interface AsyncImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  priority?: boolean;
  className?: string;
}

async function ImageData({ src }: { src: string }) {
  // 模拟图片处理和分析
  const imageResponse = await fetch(src);
  if (!imageResponse.ok) {
    throw new Error(`Failed to load image: ${src}`);
  }

  const imageBuffer = await imageResponse.arrayBuffer();

  // 这里可以添加图片处理逻辑，如生成缩略图、分析图片等
  const metadata = {
    size: imageBuffer.byteLength,
    type: imageResponse.headers.get('content-type'),
    lastModified: imageResponse.headers.get('last-modified')
  };

  return { src, metadata };
}

export async function AsyncImage({
  src,
  alt,
  width,
  height,
  priority = false,
  className = ''
}: AsyncImageProps) {
  try {
    const imageData = await ImageData({ src });

    return (
      <div className={`async-image ${className}`}>
        <img
          src={imageData.src}
          alt={alt}
          width={width}
          height={height}
          loading={priority ? 'eager' : 'lazy'}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'ImageObject',
              contentUrl: imageData.src,
              ...imageData.metadata
            })
          }}
        />
      </div>
    );
  } catch (error) {
    console.error('AsyncImage error:', error);
    return (
      <div className={`async-image-error ${className}`}>
        <span>图片加载失败</span>
      </div>
    );
  }
}

// 流式列表组件
interface StreamingListProps {
  dataSource: () => Promise<any[]>;
  renderItem: (item: any, index: number) => React.ReactNode;
  batchSize?: number;
  delay?: number;
  className?: string;
}

async function StreamingListContent({
  dataSource,
  renderItem,
  batchSize = 10,
  delay = 100
}: Omit<StreamingListProps, 'className'>) {
  // 分批加载数据
  const allData = await dataSource();
  const batches: any[][] = [];

  for (let i = 0; i < allData.length; i += batchSize) {
    batches.push(allData.slice(i, i + batchSize));
  }

  return (
    <div className="streaming-list">
      {batches.map((batch, batchIndex) => (
        <Suspense
          key={batchIndex}
          fallback={<div className="batch-placeholder">加载第 {batchIndex + 1} 批数据...</div>}
        >
          <BatchRenderer
            batch={batch}
            batchIndex={batchIndex}
            renderItem={renderItem}
            delay={delay}
          />
        </Suspense>
      ))}
    </div>
  );
}

async function BatchRenderer({
  batch,
  batchIndex,
  renderItem,
  delay
}: {
  batch: any[];
  batchIndex: number;
  renderItem: (item: any, index: number) => React.ReactNode;
  delay: number;
}) {
  // 模拟延迟
  if (delay > 0 && batchIndex > 0) {
    await new Promise(resolve => setTimeout(resolve, delay));
  }

  return (
    <div className="batch" data-batch={batchIndex}>
      {batch.map((item, index) => (
        <div key={index}>
          {renderItem(item, batchIndex * 10 + index)}
        </div>
      ))}
    </div>
  );
}

export function StreamingList(props: StreamingListProps) {
  return (
    <Suspense fallback={<div>准备加载列表...</div>}>
      <StreamingListContent {...props} />
    </Suspense>
  );
}

// 实时数据流组件
interface RealTimeDataStreamProps {
  endpoint: string;
  initialData?: any;
  children: (data: any) => React.ReactNode;
  fallback?: React.ReactNode;
}

async function RealTimeDataContent({
  endpoint,
  children
}: Omit<RealTimeDataStreamProps, 'initialData' | 'fallback'>) {
  // 建立服务器发送事件连接
  const response = await fetch(endpoint, {
    headers: {
      'Accept': 'text/event-stream',
      'Cache-Control': 'no-cache'
    }
  });

  if (!response.ok) {
    throw new Error(`Failed to connect to stream: ${endpoint}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('Response body is not readable');
  }

  let data = '';
  const decoder = new TextDecoder();

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      data += chunk;

      // 处理SSE数据格式
      const lines = data.split('\n');
      data = lines.pop() || ''; // 保留不完整的行

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const jsonData = line.slice(6);
          if (jsonData.trim()) {
            try {
              const parsedData = JSON.parse(jsonData);
              return children(parsedData);
            } catch (parseError) {
              console.error('JSON parse error:', parseError);
            }
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }

  throw new Error('Stream ended without data');
}

export function RealTimeDataStream({
  endpoint,
  initialData,
  children,
  fallback = <div>连接实时数据...</div>
}: RealTimeDataStreamProps) {
  return (
    <Suspense fallback={fallback}>
      <ErrorBoundary fallback={<div>实时数据连接失败</div>}>
        <RealTimeDataContent endpoint={endpoint}>
          {children}
        </RealTimeDataContent>
      </ErrorBoundary>
    </Suspense>
  );
}

// 错误边界组件
interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  { hasError: boolean; error?: Error }
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Streaming component error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <div>组件加载失败</div>;
    }

    return this.props.children;
  }
}

// 使用示例页面
export default async function StreamingDemoPage() {
  return (
    <div className="streaming-demo-page">
      <h1>流式渲染演示</h1>

      {/* 异步图片加载 */}
      <section className="demo-section">
        <h2>异步图片加载</h2>
        <StreamingDataLoader fallback={<div>图片加载中...</div>}>
          <AsyncImage
            src="https://picsum.photos/800/600"
            alt="随机图片"
            width={800}
            height={600}
            priority
          />
        </StreamingDataLoader>
      </section>

      {/* 流式列表 */}
      <section className="demo-section">
        <h2>流式列表</h2>
        <StreamingList
          dataSource={async () => {
            // 模拟大量数据
            return Array.from({ length: 100 }, (_, i) => ({
              id: i + 1,
              title: `项目 ${i + 1}`,
              description: `这是第 ${i + 1} 个项目的描述`,
              timestamp: new Date().toISOString()
            }));
          }}
          renderItem={(item, index) => (
            <div className="list-item" key={item.id}>
              <h3>{item.title}</h3>
              <p>{item.description}</p>
              <time>{new Date(item.timestamp).toLocaleString()}</time>
            </div>
          )}
          batchSize={5}
          delay={200}
        />
      </section>

      {/* 实时数据流 */}
      <section className="demo-section">
        <h2>实时数据流</h2>
        <RealTimeDataStream
          endpoint="/api/real-time-data"
          initialData={{ message: "等待实时数据..." }}
          fallback={<div>连接实时数据流...</div>}
        >
          {(data) => (
            <div className="real-time-data">
              <pre>{JSON.stringify(data, null, 2)}</pre>
            </div>
          )}
        </RealTimeDataStream>
      </section>
    </div>
  );
}
```

### 4. 安全性模式

#### 4.1 安全数据处理

```typescript
// components/secure-server-components.tsx
import { headers } from 'next/headers';
import { redirect } from 'next/navigation';
import { z } from 'zod';

// 安全配置
const SECURITY_CONFIG = {
  maxRequestSize: '10mb',
  allowedOrigins: process.env.ALLOWED_ORIGINS?.split(',') || [],
  rateLimit: {
    windowMs: 15 * 60 * 1000, // 15分钟
    max: 100 // 最多100个请求
  }
};

// 输入验证 Schema
const secureInputSchema = z.object({
  id: z.string().min(1).max(50).regex(/^[a-zA-Z0-9_-]+$/),
  action: z.enum(['view', 'edit', 'delete']),
  data: z.optional(z.any())
});

// XSS 防护
function sanitizeHtml(html: string): string {
  // 使用 DOMPurify 或类似库进行 HTML 清理
  const dangerousPatterns = [
    /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
    /on\w+\s*=/gi,
    /javascript:/gi,
    /<iframe\b[^>]*>/gi,
    /<object\b[^>]*>/gi,
    /<embed\b[^>]*>/gi
  ];

  return dangerousPatterns.reduce((clean, pattern) => {
    return clean.replace(pattern, '');
  }, html);
}

// CSRF 防护
function generateCSRFToken(): string {
  return crypto.randomUUID();
}

function validateCSRFToken(token: string): boolean {
  // 验证 CSRF token
  const storedToken = process.env.CSRF_SECRET;
  return token === storedToken;
}

// 权限检查
async function checkPermissions(userId: string, resource: string, action: string): Promise<boolean> {
  // 实现权限检查逻辑
  try {
    const response = await fetch(`${process.env.AUTH_API}/permissions/check`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.AUTH_TOKEN}`
      },
      body: JSON.stringify({
        userId,
        resource,
        action
      })
    });

    const result = await response.json();
    return result.allowed;
  } catch (error) {
    console.error('Permission check error:', error);
    return false;
  }
}

// 安全数据获取
async function secureDataFetch<T>(
  url: string,
  options: RequestInit = {},
  schema?: z.ZodSchema<T>
): Promise<T> {
  // 添加安全头
  const secureHeaders = {
    'Content-Type': 'application/json',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    ...options.headers
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers: secureHeaders
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();

    // 使用 Zod 验证数据结构
    if (schema) {
      return schema.parse(data);
    }

    return data as T;
  } catch (error) {
    console.error('Secure data fetch error:', error);
    throw error;
  }
}

// 安全服务端组件
interface SecureComponentProps {
  resourceId: string;
  action: 'view' | 'edit' | 'delete';
  className?: string;
}

export async function SecureComponent({
  resourceId,
  action,
  className = ''
}: SecureComponentProps) {
  // 获取请求头
  const headersList = headers();

  // 验证输入
  const validatedInput = secureInputSchema.parse({
    id: resourceId,
    action
  });

  // 获取用户信息
  const authHeader = headersList.get('authorization');
  if (!authHeader) {
    redirect('/login?error=unauthorized');
  }

  const user = await getUserFromToken(authHeader);
  if (!user) {
    redirect('/login?error=invalid_token');
  }

  // 检查权限
  const hasPermission = await checkPermissions(
    user.id,
    validatedInput.id,
    validatedInput.action
  );

  if (!hasPermission) {
    redirect('/unauthorized');
  }

  // 安全获取数据
  const data = await secureDataFetch(
    `${process.env.API_URL}/resources/${validatedInput.id}`,
    {
      method: 'GET',
      cache: 'no-store', // 敏感数据不缓存
      headers: {
        'X-User-ID': user.id,
        'X-Action': validatedInput.action
      }
    },
    z.object({
      id: z.string(),
      title: z.string(),
      content: z.string(),
      createdAt: z.string()
    })
  );

  // 清理内容
  const sanitizedContent = sanitizeHtml(data.content);

  return (
    <div className={`secure-component ${className}`}>
      <header className="secure-header">
        <h1>{data.title}</h1>
        <div className="security-info">
          <span className="user">用户: {user.name}</span>
          <span className="action">操作: {validatedInput.action}</span>
          <span className="timestamp">
            {new Date().toLocaleString()}
          </span>
        </div>
      </header>

      <main className="secure-content">
        <div
          className="sanitized-content"
          dangerouslySetInnerHTML={{ __html: sanitizedContent }}
        />

        {validatedInput.action === 'edit' && (
          <form action="/api/secure-update" method="POST">
            <input type="hidden" name="resourceId" value={validatedInput.id} />
            <input type="hidden" name="csrfToken" value={generateCSRFToken()} />

            <div className="form-group">
              <label htmlFor="title">标题</label>
              <input
                type="text"
                id="title"
                name="title"
                defaultValue={data.title}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="content">内容</label>
              <textarea
                id="content"
                name="content"
                defaultValue={sanitizedContent}
                rows={10}
                required
              />
            </div>

            <button type="submit">保存更改</button>
          </form>
        )}
      </main>

      <footer className="secure-footer">
        <div className="security-features">
          <span>✓ XSS 防护</span>
          <span>✓ CSRF 保护</span>
          <span>✓ 权限验证</span>
          <span>✓ 输入验证</span>
        </div>
      </footer>
    </div>
  );
}

// 获取用户信息
async function getUserFromToken(token: string): Promise<any> {
  try {
    const response = await fetch(`${process.env.AUTH_API}/user`, {
      headers: {
        'Authorization': token
      }
    });

    if (!response.ok) {
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Get user error:', error);
    return null;
  }
}

// 安全API端点
export async function POST(request: Request) {
  try {
    const body = await request.json();
    const headersList = headers();

    // 验证CSRF token
    const csrfToken = headersList.get('x-csrf-token');
    if (!csrfToken || !validateCSRFToken(csrfToken)) {
      return Response.json(
        { error: 'Invalid CSRF token' },
        { status: 403 }
      );
    }

    // 验证输入
    const validatedData = secureInputSchema.parse(body);

    // 验证用户身份
    const authHeader = headersList.get('authorization');
    if (!authHeader) {
      return Response.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const user = await getUserFromToken(authHeader);
    if (!user) {
      return Response.json(
        { error: 'Invalid user' },
        { status: 401 }
      );
    }

    // 检查权限
    const hasPermission = await checkPermissions(
      user.id,
      validatedData.id,
      validatedData.action
    );

    if (!hasPermission) {
      return Response.json(
        { error: 'Insufficient permissions' },
        { status: 403 }
      );
    }

    // 执行操作
    const result = await performSecureOperation(validatedData, user);

    return Response.json({
      success: true,
      data: result
    });

  } catch (error) {
    console.error('Secure POST error:', error);
    return Response.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

async function performSecureOperation(
  data: z.infer<typeof secureInputSchema>,
  user: any
): Promise<any> {
  // 实现具体的业务逻辑
  return {
    id: data.id,
    action: data.action,
    performedBy: user.id,
    timestamp: new Date().toISOString()
  };
}
```

这个 Next.js 15 服务端组件模式详解文档涵盖了：

1. **数据获取模式**: 基础和高级数据获取、多层缓存、并行处理
2. **缓存策略模式**: 内存、Redis、Next.js三层缓存架构
3. **流式渲染模式**: Suspense、异步加载、实时数据流
4. **安全性模式**: XSS防护、CSRF保护、权限验证、输入清理

每个模式都提供了企业级的安全实现、性能优化和错误处理机制。

---

## 🔄 文档交叉引用

### 相关文档
- 📄 **[App Router模式](./01-app-router-patterns.md)**: 深入了解Next.js 15 App Router架构和路由配置
- 📄 **[客户端组件模式](./03-client-components-patterns.md)**: 掌握客户端组件开发和交互处理
- 📄 **[数据获取模式](./04-data-fetching-patterns.md)**: 学习完整的数据获取策略和缓存优化
- 📄 **[状态管理模式](./05-state-management-patterns.md)**: 构建企业级状态管理架构

### 参考章节
- 📖 **[本模块其他章节]**: [App Router模式](./01-app-router-patterns.md#布局系统)中的布局系统部分
- 📖 **[其他模块相关内容]**: [TypeScript类型速查](../language-concepts/03-typescript-types.md)

---

## 📝 总结

### 核心要点回顾
1. **服务端组件架构**: 零JavaScript客户端负载的高性能渲染
2. **多层缓存系统**: 内存、Redis、Next.js智能缓存策略
3. **安全模式**: 企业级安全防护和数据验证机制
4. **流式渲染**: Suspense边界和异步组件加载
5. **并发处理**: Parallel和Suspense的性能优化

### 学习成果检查
- [ ] 是否理解了服务端组件与客户端组件的区别？
- [ ] 是否能够实现多层缓存策略？
- [ ] 是否掌握了服务端组件的安全模式？
- [ ] 是否能够构建流式渲染系统？
- [ ] 是否具备了企业级服务端组件开发能力？

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