# Rendering Optimization - Next.js 15 现代渲染性能优化

## 📋 概述

Rendering Optimization 是现代前端性能优化的核心策略之一。Next.js 15 提供了多种渲染模式和优化技术，包括 Server Components、Client Components、Streaming SSR 等。本文将深入探讨如何在 Next.js 15 项目中实施全面的渲染性能优化策略。

## 🎯 渲染模式理解

### 1. 渲染模式对比

```typescript
// types/rendering-modes.ts
export type RenderingMode =
  | 'server-components'    // 服务器组件
  | 'client-components'    // 客户端组件
  | 'streaming-ssr'        // 流式SSR
  | 'static-site'          // 静态站点生成
  | 'incremental-static'   // 增量静态生成
  | 'edge-rendering'       // 边缘渲染

export interface RenderingStrategy {
  mode: RenderingMode;
  description: string;
  useCase: string[];
  benefits: string[];
  limitations: string[];
}

export const renderingStrategies: RenderingStrategy[] = [
  {
    mode: 'server-components',
    description: '在服务器上渲染组件，减少客户端JavaScript包大小',
    useCase: ['内容展示', '数据获取', 'SEO敏感页面'],
    benefits: ['更小的包大小', '更好的SEO', '更快的首屏加载'],
    limitations: ['不能使用浏览器API', '有限的交互性']
  },
  {
    mode: 'client-components',
    description: '在客户端渲染组件，支持完整的交互功能',
    useCase: ['交互式UI', '状态管理', '浏览器API依赖'],
    benefits: ['完全的交互性', '浏览器API访问', '状态管理'],
    limitations: ['较大的包大小', '客户端JavaScript依赖']
  },
  {
    mode: 'streaming-ssr',
    description: '流式服务器端渲染，逐步发送HTML',
    useCase: ['大型页面', '动态内容', '实时数据'],
    benefits: ['更快的首屏显示', '更好的用户体验', '渐进式加载'],
    limitations: ['服务器负载', '实现复杂度']
  },
  {
    mode: 'static-site',
    description: '构建时生成静态HTML，部署到CDN',
    useCase: ['博客', '文档', '营销页面'],
    benefits: ['极快的加载速度', '低成本部署', '高可用性'],
    limitations: ['静态内容', '构建时间长']
  },
  {
    mode: 'incremental-static',
    description: '增量静态生成，按需更新页面',
    useCase: ['电商产品', '新闻文章', '用户配置文件'],
    benefits: ['静态性能', '动态更新', '自动失效'],
    limitations: ['配置复杂', '缓存管理']
  },
  {
    mode: 'edge-rendering',
    description: '在边缘网络渲染，降低延迟',
    useCase: ['全球化应用', '个性化内容', 'A/B测试'],
    benefits: ['低延迟', '地理分布', '高可用性'],
    limitations: ['冷启动问题', '内存限制']
  }
];
```

### 2. 渲染模式选择器

```typescript
// lib/rendering-optimizer.ts
import { RenderingMode, renderingStrategies } from '@/types/rendering-modes';

export interface RenderingDecision {
  mode: RenderingMode;
  confidence: number;
  reasoning: string[];
  alternative: RenderingMode[];
}

export class RenderingOptimizer {
  decideRenderingMode(
    componentType: 'page' | 'layout' | 'component',
    requirements: {
      needsInteractivity: boolean;
      hasDynamicData: boolean;
      needsBrowserAPI: boolean;
      seoCritical: boolean;
      realTimeUpdates: boolean;
      globalAudience: boolean;
    }
  ): RenderingDecision {
    const scores: Record<RenderingMode, number> = {
      'server-components': 0,
      'client-components': 0,
      'streaming-ssr': 0,
      'static-site': 0,
      'incremental-static': 0,
      'edge-rendering': 0
    };

    const reasoning: string[] = [];

    // 根据需求评分
    if (requirements.needsInteractivity) {
      scores['client-components'] += 3;
      reasoning.push('需要交互性，偏向客户端组件');
    }

    if (requirements.hasDynamicData) {
      scores['streaming-ssr'] += 2;
      scores['incremental-static'] += 2;
      reasoning.push('有动态数据，考虑流式SSR或ISR');
    }

    if (requirements.needsBrowserAPI) {
      scores['client-components'] += 3;
      reasoning.push('需要浏览器API，必须使用客户端组件');
    }

    if (requirements.seoCritical) {
      scores['server-components'] += 2;
      scores['static-site'] += 2;
      reasoning.push('SEO关键，优先服务器渲染');
    }

    if (requirements.realTimeUpdates) {
      scores['client-components'] += 2;
      scores['streaming-ssr'] += 1;
      reasoning.push('需要实时更新，考虑客户端或流式渲染');
    }

    if (requirements.globalAudience) {
      scores['edge-rendering'] += 2;
      scores['static-site'] += 1;
      reasoning.push('全球受众，考虑边缘渲染或静态站点');
    }

    // 组件类型权重
    if (componentType === 'page') {
      scores['server-components'] += 2;
      scores['static-site'] += 1;
    } else if (componentType === 'component') {
      scores['client-components'] += 1;
    }

    // 找出最佳模式
    const bestMode = Object.entries(scores)
      .sort(([,a], [,b]) => b - a)[0][0] as RenderingMode;

    const confidence = scores[bestMode] / 10; // 归一化置信度

    const alternatives = Object.entries(scores)
      .filter(([mode, score]) => mode !== bestMode && score > 0)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 2)
      .map(([mode]) => mode as RenderingMode);

    return {
      mode: bestMode,
      confidence,
      reasoning,
      alternative: alternatives
    };
  }

  generateRenderingStrategy(
    componentPath: string,
    analysis: {
      imports: string[];
      hooks: string[];
      browserAPIs: string[];
      dataSources: string[];
      userInteractions: string[];
    }
  ): {
    recommendedMode: RenderingMode;
    implementation: string;
    performanceTips: string[];
  } {
    const requirements = {
      needsInteractivity: analysis.userInteractions.length > 0,
      hasDynamicData: analysis.dataSources.length > 0,
      needsBrowserAPI: analysis.browserAPIs.length > 0,
      seoCritical: componentPath.includes('/blog/') || componentPath.includes('/docs/'),
      realTimeUpdates: analysis.hooks.includes('useEffect') && analysis.dataSources.some(ds => ds.includes('websocket')),
      globalAudience: true // 默认全球化
    };

    const decision = this.decideRenderingMode('component', requirements);

    const implementation = this.generateImplementationCode(decision.mode, analysis);
    const performanceTips = this.getPerformanceTips(decision.mode);

    return {
      recommendedMode: decision.mode,
      implementation,
      performanceTips
    };
  }

  private generateImplementationCode(mode: RenderingMode, analysis: any): string {
    switch (mode) {
      case 'server-components':
        return `'use client';

import { db } from '@/lib/db';

export default async function ServerComponent() {
  const data = await db.query('SELECT * FROM table');

  return (
    <div>
      {/* 服务器渲染内容 */}
      {data.map(item => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  );
}`;

      case 'client-components':
        return `'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';

export default function ClientComponent() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    const response = await fetch('/api/data');
    const result = await response.json();
    setData(result);
    setLoading(false);
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <Button onClick={fetchData}>Refresh</Button>
      {data.map(item => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  );
}`;

      case 'streaming-ssr':
        return `import { Suspense } from 'react';
import { ServerComponent } from './server-component';
import { ClientComponent } from './client-component';

export default function StreamingPage() {
  return (
    <div>
      <h1>Streaming SSR Example</h1>

      <Suspense fallback={<div>Loading server content...</div>}>
        <ServerComponent />
      </Suspense>

      <Suspense fallback={<div>Loading client content...</div>}>
        <ClientComponent />
      </Suspense>
    </div>
  );
}`;

      default:
        return '// Default implementation';
    }
  }

  private getPerformanceTips(mode: RenderingMode): string[] {
    const tips: Record<RenderingMode, string[]> = {
      'server-components': [
        '避免在服务器组件中使用客户端特性',
        '使用React 19的Server Components优化',
        '合理使用缓存策略',
        '减少服务器到客户端的数据传输'
      ],
      'client-components': [
        '使用React.memo优化重渲染',
        '合理使用useMemo和useCallback',
        '代码分割大型组件',
        '优化状态管理'
      ],
      'streaming-ssr': [
        '使用Suspense边界优化加载体验',
        '优先加载关键内容',
        '优化数据获取策略',
        '使用React 19的并发特性'
      ],
      'static-site': [
        '在构建时预渲染所有页面',
        '使用ISR进行增量更新',
        '优化构建性能',
        '使用CDN缓存'
      ],
      'incremental-static': [
        '合理设置revalidate时间',
        '使用on-demand revalidation',
        '优化数据获取策略',
        '监控缓存命中率'
      ],
      'edge-rendering': [
        '优化冷启动时间',
        '使用边缘缓存',
        '减少计算复杂度',
        '合理使用内存'
      ]
    };

    return tips[mode] || [];
  }
}
```

## 🚀 服务器组件优化

### 1. 服务器组件最佳实践

```typescript
// components/optimized-server-component.tsx
import { db } from '@/lib/db';
import { cache } from 'react';

// 使用React.cache缓存数据获取
const getData = cache(async (id: string) => {
  const data = await db.query('SELECT * FROM posts WHERE id = ?', [id]);
  return data[0];
});

interface OptimizedServerComponentProps {
  postId: string;
}

export async function OptimizedServerComponent({ postId }: OptimizedServerComponentProps) {
  // 并行数据获取
  const [post, comments, author] = await Promise.all([
    getData(postId),
    getComments(postId),
    getAuthor(postId)
  ]);

  return (
    <article className="max-w-4xl mx-auto p-6">
      <header className="mb-8">
        <h1 className="text-4xl font-bold mb-4">{post.title}</h1>
        <div className="flex items-center gap-4 text-gray-600">
          <span>By {author.name}</span>
          <span>•</span>
          <time>{new Date(post.createdAt).toLocaleDateString()}</time>
        </div>
      </header>

      <div
        className="prose prose-lg max-w-none mb-8"
        dangerouslySetInnerHTML={{ __html: post.content }}
      />

      <section className="border-t pt-8">
        <h2 className="text-2xl font-semibold mb-6">Comments ({comments.length})</h2>

        <div className="space-y-6">
          {comments.map(comment => (
            <Comment key={comment.id} comment={comment} />
          ))}
        </div>
      </section>
    </article>
  );
}

// 内联服务器组件
function Comment({ comment }: { comment: any }) {
  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
          {comment.author.name[0]}
        </div>
        <div>
          <div className="font-semibold">{comment.author.name}</div>
          <div className="text-sm text-gray-500">
            {new Date(comment.createdAt).toLocaleDateString()}
          </div>
        </div>
      </div>
      <p className="text-gray-800">{comment.content}</p>
    </div>
  );
}

// 辅助函数
async function getComments(postId: string) {
  const comments = await db.query('SELECT * FROM comments WHERE postId = ?', [postId]);
  return comments;
}

async function getAuthor(postId: string) {
  const post = await getData(postId);
  const author = await db.query('SELECT * FROM users WHERE id = ?', [post.authorId]);
  return author[0];
}
```

### 2. 服务器组件缓存策略

```typescript
// lib/server-component-cache.ts
import { unstable_cache } from 'next/cache';
import { db } from '@/lib/db';

// 带有标签的缓存
export const cachedPostQuery = unstable_cache(
  async (id: string) => {
    console.log('Cache miss for post:', id);
    const post = await db.query('SELECT * FROM posts WHERE id = ?', [id]);
    return post[0];
  },
  ['post'], // 缓存键前缀
  {
    tags: ['posts'], // 缓存标签
    revalidate: 3600, // 1小时后重新验证
  }
);

// 用户特定缓存
export const cachedUserQuery = unstable_cache(
  async (userId: string) => {
    console.log('Cache miss for user:', userId);
    const user = await db.query('SELECT * FROM users WHERE id = ?', [userId]);
    return user[0];
  },
  ['user'],
  {
    tags: [`user-${userId}`],
    revalidate: 1800, // 30分钟
  }
);

// 列表缓存
export const cachedPostsList = unstable_cache(
  async (page: number = 1, limit: number = 10) => {
    console.log('Cache miss for posts list');
    const offset = (page - 1) * limit;
    const posts = await db.query(
      'SELECT * FROM posts ORDER BY createdAt DESC LIMIT ? OFFSET ?',
      [limit, offset]
    );
    return posts;
  },
  ['posts-list'],
  {
    tags: ['posts', 'posts-list'],
    revalidate: 600, // 10分钟
  }
);

// 缓存失效工具
export async function revalidatePostTags(postId: string) {
  const { revalidateTag } = await import('next/cache');

  // 失效相关标签
  revalidateTag('posts');
  revalidateTag(`post-${postId}`);
  revalidateTag('posts-list');

  console.log('Cache revalidated for post:', postId);
}

export async function revalidateUserTags(userId: string) {
  const { revalidateTag } = await import('next/cache');

  revalidateTag(`user-${userId}`);

  console.log('Cache revalidated for user:', userId);
}
```

## 🎨 客户端组件优化

### 1. 优化的客户端组件模式

```typescript
// components/optimized-client-component.tsx
'use client';

import { useState, useEffect, useMemo, useCallback, memo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { debounce } from 'lodash-es';

interface OptimizedClientComponentProps {
  initialData?: any;
  userId: string;
}

// 使用memo避免不必要的重渲染
export const OptimizedClientComponent = memo(function OptimizedClientComponent({
  initialData,
  userId
}: OptimizedClientComponentProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({});

  const queryClient = useQueryClient();

  // 使用React Query进行数据获取
  const { data, isLoading, error } = useQuery({
    queryKey: ['user-data', userId, filters],
    queryFn: async () => {
      const response = await fetch(`/api/users/${userId}/data?${new URLSearchParams(filters)}`);
      return response.json();
    },
    initialData,
    staleTime: 5 * 60 * 1000, // 5分钟内数据保持新鲜
    cacheTime: 10 * 60 * 1000, // 10分钟缓存
  });

  // 使用useMemo优化计算
  const filteredData = useMemo(() => {
    if (!data) return [];

    return data.filter((item: any) =>
      item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.description.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [data, searchTerm]);

  // 使用useCallback优化函数引用
  const handleSearch = useCallback(
    debounce((term: string) => {
      setSearchTerm(term);
    }, 300),
    []
  );

  const handleFilterChange = useCallback((newFilters: any) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  // 数据变更处理
  const updateMutation = useMutation({
    mutationFn: async (updatedData: any) => {
      const response = await fetch(`/api/users/${userId}/data`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedData)
      });
      return response.json();
    },
    onSuccess: (updatedData) => {
      // 更新缓存
      queryClient.setQueryData(['user-data', userId, filters], updatedData);

      // 乐观更新
      queryClient.setQueryData(['user-data', userId, filters], (old: any) => ({
        ...old,
        ...updatedData
      }));
    },
  });

  // 滚动性能优化
  const handleScroll = useCallback((event: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = event.currentTarget;

    if (scrollTop + clientHeight >= scrollHeight - 100) {
      // 加载更多数据
      queryClient.prefetchQuery({
        queryKey: ['user-data', userId, { ...filters, page: (filters as any).page + 1 }],
        queryFn: () => fetch(`/api/users/${userId}/data?page=${(filters as any).page + 1}`).then(res => res.json())
      });
    }
  }, [queryClient, userId, filters]);

  if (isLoading) return <div className="animate-pulse">Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div className="optimized-client-component">
      <div className="search-section mb-6">
        <input
          type="text"
          placeholder="Search..."
          onChange={(e) => handleSearch(e.target.value)}
          className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <div className="filters-section mb-6">
        <FilterControls
          filters={filters}
          onFilterChange={handleFilterChange}
        />
      </div>

      <div
        className="data-section overflow-y-auto max-h-96"
        onScroll={handleScroll}
      >
        {filteredData.map((item: any) => (
          <DataItem
            key={item.id}
            item={item}
            onUpdate={(updatedItem) => updateMutation.mutate(updatedItem)}
          />
        ))}
      </div>
    </div>
  );
});

// 子组件优化
const FilterControls = memo(function FilterControls({
  filters,
  onFilterChange
}: {
  filters: any;
  onFilterChange: (filters: any) => void;
}) {
  return (
    <div className="flex gap-4 flex-wrap">
      <select
        value={filters.status || ''}
        onChange={(e) => onFilterChange({ status: e.target.value })}
        className="p-2 border rounded"
      >
        <option value="">All Status</option>
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
      </select>

      <select
        value={filters.category || ''}
        onChange={(e) => onFilterChange({ category: e.target.value })}
        className="p-2 border rounded"
      >
        <option value="">All Categories</option>
        <option value="tech">Technology</option>
        <option value="business">Business</option>
      </select>
    </div>
  );
});

const DataItem = memo(function DataItem({
  item,
  onUpdate
}: {
  item: any;
  onUpdate: (item: any) => void;
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(item.name);

  const handleSave = useCallback(() => {
    onUpdate({ ...item, name: editValue });
    setIsEditing(false);
  }, [item, editValue, onUpdate]);

  return (
    <div className="data-item p-4 border-b hover:bg-gray-50">
      {isEditing ? (
        <div className="flex gap-2">
          <input
            type="text"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            className="flex-1 p-2 border rounded"
          />
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Save
          </button>
          <button
            onClick={() => setIsEditing(false)}
            className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
          >
            Cancel
          </button>
        </div>
      ) : (
        <div className="flex justify-between items-center">
          <div>
            <h3 className="font-semibold">{item.name}</h3>
            <p className="text-gray-600">{item.description}</p>
          </div>
          <button
            onClick={() => setIsEditing(true)}
            className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
          >
            Edit
          </button>
        </div>
      )}
    </div>
  );
});
```

### 2. 状态管理优化

```typescript
// lib/optimized-state-manager.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

interface State {
  user: {
    data: any | null;
    loading: boolean;
    error: string | null;
  };
  posts: {
    data: any[];
    loading: boolean;
    error: string | null;
    filters: {
      search: string;
      category: string;
      status: string;
    };
  };
  ui: {
    theme: 'light' | 'dark';
    sidebarOpen: boolean;
    notifications: Array<{
      id: string;
      message: string;
      type: 'success' | 'error' | 'warning';
      timestamp: number;
    }>;
  };
}

interface Actions {
  setUser: (user: any) => void;
  setUserLoading: (loading: boolean) => void;
  setUserError: (error: string | null) => void;

  setPosts: (posts: any[]) => void;
  setPostsLoading: (loading: boolean) => void;
  setPostsError: (error: string | null) => void;
  setPostsFilters: (filters: Partial<State['posts']['filters']>) => void;

  setTheme: (theme: 'light' | 'dark') => void;
  toggleSidebar: () => void;
  addNotification: (notification: Omit<State['ui']['notifications'][0], 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
}

// 使用Zustand创建优化的状态管理
export const useStore = create<State & Actions>()(
  devtools(
    persist(
      immer((set, get) => ({
        // 初始状态
        user: {
          data: null,
          loading: false,
          error: null,
        },
        posts: {
          data: [],
          loading: false,
          error: null,
          filters: {
            search: '',
            category: '',
            status: '',
          },
        },
        ui: {
          theme: 'light',
          sidebarOpen: false,
          notifications: [],
        },

        // 动作
        setUser: (user) => {
          set((state) => {
            state.user.data = user;
            state.user.loading = false;
            state.user.error = null;
          });
        },

        setUserLoading: (loading) => {
          set((state) => {
            state.user.loading = loading;
          });
        },

        setUserError: (error) => {
          set((state) => {
            state.user.error = error;
            state.user.loading = false;
          });
        },

        setPosts: (posts) => {
          set((state) => {
            state.posts.data = posts;
            state.posts.loading = false;
            state.posts.error = null;
          });
        },

        setPostsLoading: (loading) => {
          set((state) => {
            state.posts.loading = loading;
          });
        },

        setPostsError: (error) => {
          set((state) => {
            state.posts.error = error;
            state.posts.loading = false;
          });
        },

        setPostsFilters: (filters) => {
          set((state) => {
            state.posts.filters = { ...state.posts.filters, ...filters };
          });
        },

        setTheme: (theme) => {
          set((state) => {
            state.ui.theme = theme;
          });
        },

        toggleSidebar: () => {
          set((state) => {
            state.ui.sidebarOpen = !state.ui.sidebarOpen;
          });
        },

        addNotification: (notification) => {
          set((state) => {
            state.ui.notifications.push({
              ...notification,
              id: Date.now().toString(),
              timestamp: Date.now(),
            });
          });
        },

        removeNotification: (id) => {
          set((state) => {
            state.ui.notifications = state.ui.notifications.filter(
              (n) => n.id !== id
            );
          });
        },
      })),
      {
        name: 'app-storage',
        partialize: (state) => ({
          ui: {
            theme: state.ui.theme,
          },
        }),
      }
    ),
    {
      name: 'app-store',
    }
  )
);

// 选择器优化，避免不必要的重渲染
export const useUser = () => useStore((state) => state.user);
export const usePosts = () => useStore((state) => state.posts);
export const useUI = () => useStore((state) => state.ui);
export const usePostsFilters = () => useStore((state) => state.posts.filters);

export const useFilteredPosts = () => {
  const posts = useStore((state) => state.posts.data);
  const filters = useStore((state) => state.posts.filters);

  return useMemo(() => {
    return posts.filter(post => {
      const matchesSearch = !filters.search ||
        post.title.toLowerCase().includes(filters.search.toLowerCase()) ||
        post.content.toLowerCase().includes(filters.search.toLowerCase());

      const matchesCategory = !filters.category || post.category === filters.category;
      const matchesStatus = !filters.status || post.status === filters.status;

      return matchesSearch && matchesCategory && matchesStatus;
    });
  }, [posts, filters]);
};
```

## 🔄 流式渲染优化

### 1. Suspense 和流式SSR

```typescript
// app/blog/[slug]/page.tsx
import { Suspense } from 'react';
import { notFound } from 'next/navigation';
import { LoadingPost, LoadingComments, LoadingRelatedPosts } from '@/components/loading';
import { PostContent } from '@/components/post-content';
import { PostComments } from '@/components/post-comments';
import { RelatedPosts } from '@/components/related-posts';

interface BlogPostPageProps {
  params: { slug: string };
}

export default async function BlogPostPage({ params }: BlogPostPageProps) {
  // 预取数据
  const postData = getPostData(params.slug);
  const commentsData = getPostComments(params.slug);
  const relatedPostsData = getRelatedPosts(params.slug);

  return (
    <div className="blog-post-page max-w-4xl mx-auto p-6">
      <Suspense fallback={<LoadingPost />}>
        {/* 主要内容优先加载 */}
        <PostContent postPromise={postData} />
      </Suspense>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-12">
        <div className="lg:col-span-2">
          <Suspense fallback={<LoadingComments />}>
            {/* 评论区延迟加载 */}
            <PostComments commentsPromise={commentsData} />
          </Suspense>
        </div>

        <div className="lg:col-span-1">
          <Suspense fallback={<LoadingRelatedPosts />}>
            {/* 相关文章最后加载 */}
            <RelatedPosts postsPromise={relatedPostsData} />
          </Suspense>
        </div>
      </div>
    </div>
  );
}

// 流式数据获取组件
async function getPostData(slug: string) {
  const response = await fetch(`${process.env.API_URL}/posts/${slug}`, {
    next: {
      revalidate: 3600, // 1小时
      tags: [`post-${slug}`]
    }
  });

  if (!response.ok) {
    notFound();
  }

  return response.json();
}

async function getPostComments(slug: string) {
  const response = await fetch(`${process.env.API_URL}/posts/${slug}/comments`, {
    next: {
      revalidate: 1800, // 30分钟
      tags: [`comments-${slug}`]
    }
  });

  return response.json();
}

async function getRelatedPosts(slug: string) {
  const response = await fetch(`${process.env.API_URL}/posts/${slug}/related`, {
    next: {
      revalidate: 7200, // 2小时
      tags: ['related-posts']
    }
  });

  return response.json();
}
```

### 2. 渐进式增强组件

```typescript
// components/progressive-enhancement.tsx
'use client';

import { useState, useEffect, Suspense } from 'react';
import { ErrorBoundary } from 'react-error-boundary';

interface ProgressiveEnhancementProps {
  children: React.ReactNode;
  fallback: React.ReactNode;
  ssrOnly?: React.ReactNode;
  loading?: React.ReactNode;
  errorFallback?: React.ReactNode;
}

export function ProgressiveEnhancement({
  children,
  fallback,
  ssrOnly,
  loading = <div>Loading...</div>,
  errorFallback = <div>Something went wrong</div>
}: ProgressiveEnhancementProps) {
  const [isClient, setIsClient] = useState(false);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  // SSR阶段
  if (!isClient) {
    return ssrOnly || fallback;
  }

  // 客户端渲染
  if (hasError) {
    return errorFallback;
  }

  return (
    <ErrorBoundary
      FallbackComponent={() => {
        useEffect(() => setHasError(true), []);
        return errorFallback;
      }}
    >
      <Suspense fallback={loading}>
        {children}
      </Suspense>
    </ErrorBoundary>
  );
}

// 使用示例
export function UserProfile({ userId }: { userId: string }) {
  return (
    <ProgressiveEnhancement
      ssrOnly={
        <div className="animate-pulse">
          <div className="h-32 bg-gray-200 rounded-full mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      }
      fallback={
        <div className="text-center py-8">
          <div className="text-gray-500">Profile not available</div>
        </div>
      }
    >
      <ActualUserProfile userId={userId} />
    </ProgressiveEnhancement>
  );
}

function ActualUserProfile({ userId }: { userId: string }) {
  // 实际的用户配置文件组件
  return <div>Actual user profile content</div>;
}
```

## 📊 渲染性能监控

### 1. 渲染性能分析工具

```typescript
// lib/rendering-performance-monitor.ts
export class RenderingPerformanceMonitor {
  private metrics: RenderingMetric[] = [];
  private observer: PerformanceObserver | null = null;

  constructor() {
    this.initializeMonitoring();
  }

  private initializeMonitoring(): void {
    if (typeof window === 'undefined') return;

    // 监控长任务
    if ('PerformanceObserver' in window) {
      this.observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach(entry => {
          if (entry.entryType === 'longtask') {
            this.trackLongTask(entry as PerformanceEntry & { duration: number });
          } else if (entry.entryType === 'measure') {
            this.trackCustomMetric(entry as PerformanceEntry & { duration: number });
          }
        });
      });

      this.observer.observe({ entryTypes: ['longtask', 'measure'] });
    }

    // 监控渲染时间
    this.monitorRenderingTime();
  }

  private trackLongTask(entry: PerformanceEntry & { duration: number }): void {
    const metric: RenderingMetric = {
      type: 'longtask',
      name: entry.name,
      duration: entry.duration,
      timestamp: Date.now(),
      metadata: {
        entryType: entry.entryType,
        startTime: entry.startTime
      }
    };

    this.metrics.push(metric);
    this.analyzeMetric(metric);
  }

  private trackCustomMetric(entry: PerformanceEntry & { duration: number }): void {
    const metric: RenderingMetric = {
      type: 'custom',
      name: entry.name,
      duration: entry.duration,
      timestamp: Date.now(),
      metadata: {
        entryType: entry.entryType,
        startTime: entry.startTime
      }
    };

    this.metrics.push(metric);
  }

  private monitorRenderingTime(): void {
    // 监控组件渲染时间
    const originalRender = window.requestAnimationFrame;
    let renderStartTime = 0;

    window.requestAnimationFrame = (callback: FrameRequestCallback) => {
      return originalRender.call(window, (timestamp: number) => {
        if (renderStartTime === 0) {
          renderStartTime = timestamp;
        }

        const result = callback(timestamp);

        if (timestamp - renderStartTime > 16) { // 超过一帧
          this.trackRenderTime(timestamp - renderStartTime);
        }

        renderStartTime = 0;
        return result;
      });
    };
  }

  private trackRenderTime(duration: number): void {
    const metric: RenderingMetric = {
      type: 'render',
      name: 'frame_render',
      duration,
      timestamp: Date.now(),
      metadata: {
        frameTime: duration,
        fps: Math.round(1000 / duration)
      }
    };

    this.metrics.push(metric);

    if (duration > 100) { // 长帧渲染
      console.warn(`Long frame detected: ${duration}ms`);
    }
  }

  private analyzeMetric(metric: RenderingMetric): void {
    // 分析性能指标
    if (metric.type === 'longtask' && metric.duration > 50) {
      console.warn(`Long task detected: ${metric.name} - ${metric.duration}ms`);
    }

    // 发送到分析服务
    this.sendToAnalytics(metric);
  }

  private async sendToAnalytics(metric: RenderingMetric): Promise<void> {
    try {
      await fetch('/api/analytics/rendering', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(metric)
      });
    } catch (error) {
      console.error('Failed to send rendering metric:', error);
    }
  }

  startMeasure(name: string): () => void {
    if (typeof performance === 'undefined') {
      return () => {};
    }

    performance.mark(`${name}-start`);

    return () => {
      performance.mark(`${name}-end`);
      performance.measure(name, `${name}-start`, `${name}-end`);
    };
  }

  getMetrics(): RenderingMetric[] {
    return [...this.metrics];
  }

  getRenderingSummary(): RenderingSummary {
    const longTasks = this.metrics.filter(m => m.type === 'longtask');
    const renderTasks = this.metrics.filter(m => m.type === 'render');
    const customMetrics = this.metrics.filter(m => m.type === 'custom');

    return {
      totalLongTasks: longTasks.length,
      averageLongTaskDuration: longTasks.length > 0
        ? longTasks.reduce((sum, task) => sum + task.duration, 0) / longTasks.length
        : 0,
      maxLongTaskDuration: Math.max(...longTasks.map(task => task.duration), 0),
      averageFrameTime: renderTasks.length > 0
        ? renderTasks.reduce((sum, task) => sum + task.duration, 0) / renderTasks.length
        : 0,
      worstFrameTime: Math.max(...renderTasks.map(task => task.duration), 0),
      customMetricsCount: customMetrics.length
    };
  }

  destroy(): void {
    if (this.observer) {
      this.observer.disconnect();
    }
  }
}

interface RenderingMetric {
  type: 'longtask' | 'render' | 'custom';
  name: string;
  duration: number;
  timestamp: number;
  metadata?: Record<string, any>;
}

interface RenderingSummary {
  totalLongTasks: number;
  averageLongTaskDuration: number;
  maxLongTaskDuration: number;
  averageFrameTime: number;
  worstFrameTime: number;
  customMetricsCount: number;
}

// 使用Hook
export function useRenderingPerformance() {
  const [monitor] = useState(() => new RenderingPerformanceMonitor());

  useEffect(() => {
    return () => {
      monitor.destroy();
    };
  }, [monitor]);

  return {
    measure: monitor.startMeasure.bind(monitor),
    getMetrics: monitor.getMetrics.bind(monitor),
    getSummary: monitor.getRenderingSummary.bind(monitor)
  };
}
```

### 2. React Profiler 集成

```typescript
// components/react-profiler.tsx
'use client';

import { Profiler, ProfilerOnRenderCallback } from 'react';
import { useRenderingPerformance } from '@/lib/rendering-performance-monitor';

interface ReactProfilerProps {
  id: string;
  children: React.ReactNode;
  enabled?: boolean;
}

export function ReactProfiler({ id, children, enabled = true }: ReactProfilerProps) {
  const { measure } = useRenderingPerformance();

  const onRender: ProfilerOnRenderCallback = (
    id,
    phase,
    actualDuration,
    baseDuration,
    startTime,
    commitTime,
    interactions
  ) => {
    const endMeasure = measure(`react-${id}-${phase}`);

    // 记录渲染性能
    console.log(`[Profiler] ${id} ${phase}:`, {
      actualDuration,
      baseDuration,
      duration: actualDuration - baseDuration,
      startTime,
      commitTime,
      interactions: interactions.size
    });

    // 发送到分析服务
    if (actualDuration > 16) { // 超过一帧
      console.warn(`Slow render detected in ${id}: ${actualDuration}ms`);
    }

    endMeasure();
  };

  if (!enabled) {
    return <>{children}</>;
  }

  return (
    <Profiler id={id} onRender={onRender}>
      {children}
    </Profiler>
  );
}

// 使用示例
export function ProfiledComponent() {
  return (
    <ReactProfiler id="profiled-component">
      <div>
        {/* 组件内容 */}
      </div>
    </ReactProfiler>
  );
}
```

## 🎯 最佳实践和总结

### 1. 渲染优化检查清单

```typescript
// checklists/rendering-optimization.ts
export const renderingOptimizationChecklist = [
  {
    category: '服务器组件',
    items: [
      '正确使用服务器组件处理静态内容',
      '避免在服务器组件中使用客户端特性',
      '使用React.cache缓存数据获取',
      '合理设置缓存标签和失效策略'
    ]
  },
  {
    category: '客户端组件',
    items: [
      '使用React.memo避免不必要的重渲染',
      '合理使用useMemo和useCallback',
      '优化状态管理结构',
      '使用React Query或SWR进行数据获取'
    ]
  },
  {
    category: '流式渲染',
    items: [
      '使用Suspense边界优化加载体验',
      '优先加载关键内容',
      '实现渐进式增强',
      '合理的错误边界处理'
    ]
  },
  {
    category: '性能监控',
    items: [
      '实现渲染性能监控',
      '使用React Profiler分析性能',
      '监控长任务和帧时间',
      '定期分析性能指标'
    ]
  },
  {
    category: '代码质量',
    items: [
      '保持组件单一职责',
      '合理拆分大型组件',
      '避免过度嵌套',
      '使用类型检查'
    ]
  }
];

export const runRenderingOptimizationCheck = async (): Promise<void> => {
  console.log('🔍 Running Rendering Optimization Check...');

  for (const category of renderingOptimizationChecklist) {
    console.log(`\n📋 ${category.category}:`);
    for (const item of category.items) {
      console.log(`  ✅ ${item}`);
    }
  }

  console.log('\n🎯 Rendering optimization check completed!');
};
```

### 2. 性能预算和目标

```typescript
// lib/rendering-budget.ts
export interface RenderingBudget {
  serverComponent: {
    renderTime: number; // 服务器渲染时间
    dataSize: number;   // 传输数据大小
  };
  clientComponent: {
    renderTime: number; // 客户端渲染时间
    reRenderTime: number; // 重渲染时间
    bundleSize: number; // 包大小
  };
  streaming: {
    firstPaint: number; // 首次绘制时间
    interactiveTime: number; // 可交互时间
    completeTime: number; // 完成时间
  };
}

export const defaultRenderingBudget: RenderingBudget = {
  serverComponent: {
    renderTime: 100,    // 100ms
    dataSize: 50 * 1024 // 50KB
  },
  clientComponent: {
    renderTime: 16,     // 16ms (一帧)
    reRenderTime: 8,    // 8ms
    bundleSize: 100 * 1024 // 100KB
  },
  streaming: {
    firstPaint: 1000,   // 1s
    interactiveTime: 2000, // 2s
    completeTime: 3000  // 3s
  }
};

export class RenderingBudgetChecker {
  private budget: RenderingBudget;
  private monitor: RenderingPerformanceMonitor;

  constructor(budget: RenderingBudget = defaultRenderingBudget) {
    this.budget = budget;
    this.monitor = new RenderingPerformanceMonitor();
  }

  async checkRenderingBudget(): Promise<RenderingBudgetCheckResult> {
    const violations: RenderingBudgetViolation[] = [];

    // 检查服务器组件性能
    const serverMetrics = await this.getServerMetrics();
    if (serverMetrics.renderTime > this.budget.serverComponent.renderTime) {
      violations.push({
        type: 'serverComponent',
        metric: 'renderTime',
        actual: serverMetrics.renderTime,
        budget: this.budget.serverComponent.renderTime,
        severity: 'high'
      });
    }

    // 检查客户端组件性能
    const clientMetrics = this.getClientMetrics();
    if (clientMetrics.averageRenderTime > this.budget.clientComponent.renderTime) {
      violations.push({
        type: 'clientComponent',
        metric: 'renderTime',
        actual: clientMetrics.averageRenderTime,
        budget: this.budget.clientComponent.renderTime,
        severity: 'medium'
      });
    }

    // 检查流式渲染性能
    const streamingMetrics = await this.getStreamingMetrics();
    if (streamingMetrics.firstPaint > this.budget.streaming.firstPaint) {
      violations.push({
        type: 'streaming',
        metric: 'firstPaint',
        actual: streamingMetrics.firstPaint,
        budget: this.budget.streaming.firstPaint,
        severity: 'high'
      });
    }

    return {
      passed: violations.length === 0,
      violations,
      summary: this.generateSummary(violations)
    };
  }

  private async getServerMetrics(): Promise<{ renderTime: number; dataSize: number }> {
    // 从性能监控获取服务器指标
    const summary = this.monitor.getRenderingSummary();

    return {
      renderTime: summary.averageLongTaskDuration,
      dataSize: 0 // 需要从网络请求获取
    };
  }

  private getClientMetrics(): React.ComponentProps<typeof useRenderingPerformance> {
    // 从性能监控获取客户端指标
    const summary = this.monitor.getRenderingSummary();

    return {
      averageRenderTime: summary.averageFrameTime,
      worstRenderTime: summary.worstFrameTime,
      reRenderCount: 0
    } as any;
  }

  private async getStreamingMetrics(): Promise<{ firstPaint: number; interactiveTime: number; completeTime: number }> {
    if (typeof performance === 'undefined') {
      return { firstPaint: 0, interactiveTime: 0, completeTime: 0 };
    }

    const paint = performance.getEntriesByType('paint');
    const fcp = paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0;

    return {
      firstPaint: fcp,
      interactiveTime: fcp + 1000, // 估算
      completeTime: fcp + 2000 // 估算
    };
  }

  private generateSummary(violations: RenderingBudgetViolation[]): string {
    if (violations.length === 0) {
      return 'All rendering metrics within budget';
    }

    const summary = violations.map(v =>
      `${v.type}.${v.metric}: ${v.actual}ms > ${v.budget}ms`
    ).join(', ');

    return `Budget violations detected: ${summary}`;
  }
}

interface RenderingBudgetCheckResult {
  passed: boolean;
  violations: RenderingBudgetViolation[];
  summary: string;
}

interface RenderingBudgetViolation {
  type: 'serverComponent' | 'clientComponent' | 'streaming';
  metric: string;
  actual: number;
  budget: number;
  severity: 'high' | 'medium' | 'low';
}
```

## 🎯 总结

Rendering Optimization 是 Next.js 15 应用性能优化的核心策略。通过合理使用服务器组件、客户端组件、流式渲染等技术，可以显著提升应用的渲染性能和用户体验。

### 关键要点：

1. **渲染模式选择**：根据使用场景选择合适的渲染模式
2. **服务器组件**：减少客户端包大小，提升首屏性能
3. **客户端组件**：优化交互性和状态管理
4. **流式渲染**：使用Suspense实现渐进式加载
5. **性能监控**：持续监控和优化渲染性能
6. **最佳实践**：建立渲染优化的标准和规范

### 实施建议：

- **渐进式优化**：从最影响性能的问题开始
- **性能预算**：设定合理的性能目标和限制
- **监控体系**：建立完整的性能监控和分析体系
- **团队协作**：建立渲染优化的最佳实践

通过掌握这些渲染优化技术，可以构建出高性能、用户友好的现代Web应用。