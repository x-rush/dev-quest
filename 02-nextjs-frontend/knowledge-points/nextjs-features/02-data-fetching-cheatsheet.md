# Next.js 数据获取速查手册

## 📚 概述

Next.js 15 提供了多种数据获取方式，包括服务器组件、客户端组件、API 路由、缓存策略等。本手册涵盖了所有数据获取相关的 API 和最佳实践。

## 🏗️ 服务器组件数据获取

### 基础数据获取
**在服务器组件中直接获取数据**

```typescript
// app/posts/page.tsx
async function getPosts() {
  const res = await fetch('https://api.example.com/posts');
  if (!res.ok) {
    throw new Error('Failed to fetch posts');
  }
  return res.json();
}

export default async function PostsPage() {
  const posts = await getPosts();

  return (
    <div>
      <h1>Posts</h1>
      <ul>
        {posts.map((post: any) => (
          <li key={post.id}>
            <h3>{post.title}</h3>
            <p>{post.excerpt}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### 带参数的数据获取
**处理动态路由参数**

```typescript
// app/posts/[slug]/page.tsx
interface PostPageProps {
  params: {
    slug: string;
  };
}

async function getPost(slug: string) {
  const res = await fetch(`https://api.example.com/posts/${slug}`);
  if (!res.ok) {
    return null;
  }
  return res.json();
}

export default async function PostPage({ params }: PostPageProps) {
  const post = await getPost(params.slug);

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
  const posts = await fetch('https://api.example.com/posts').then(res => res.json());

  return posts.map((post: any) => ({
    slug: post.slug,
  }));
}
```

### 搜索参数处理
**处理 URL 查询参数**

```typescript
// app/search/page.tsx
interface SearchPageProps {
  searchParams: {
    q?: string;
    category?: string;
    sort?: 'new' | 'popular';
    page?: string;
  };
}

async function searchItems(params: SearchPageProps['searchParams']) {
  const searchParams = new URLSearchParams();

  if (params.q) searchParams.set('q', params.q);
  if (params.category) searchParams.set('category', params.category);
  if (params.sort) searchParams.set('sort', params.sort);
  if (params.page) searchParams.set('page', params.page);

  const res = await fetch(
    `https://api.example.com/search?${searchParams.toString()}`
  );

  if (!res.ok) {
    throw new Error('Failed to search items');
  }

  return res.json();
}

export default async function SearchPage({ searchParams }: SearchPageProps) {
  const results = await searchItems(searchParams);

  return (
    <div>
      <h1>Search Results</h1>
      {searchParams.q && <p>Query: {searchParams.q}</p>}
      <SearchResults results={results} />
    </div>
  );
}
```

## 💾 缓存策略

### Fetch 缓存选项
**控制数据缓存行为**

```typescript
// 强制缓存 (默认)
async function getCachedData() {
  const res = await fetch('https://api.example.com/data', {
    cache: 'force-cache',
  });
  return res.json();
}

// 不缓存
async function getFreshData() {
  const res = await fetch('https://api.example.com/data', {
    cache: 'no-store',
  });
  return res.json();
}

// 重新验证缓存
async function getDataWithRevalidation() {
  const res = await fetch('https://api.example.com/data', {
    next: {
      revalidate: 3600, // 1小时后重新验证
    },
  });
  return res.json();
}

// 基于标签的重新验证
async function getDataWithTag() {
  const res = await fetch('https://api.example.com/posts', {
    next: {
      tags: ['posts'],
    },
  });
  return res.json();
}

// 时间和标签组合
async function getPostWithTags(slug: string) {
  const res = await fetch(`https://api.example.com/posts/${slug}`, {
    next: {
      revalidate: 3600,
      tags: ['posts', `post-${slug}`],
    },
  });
  return res.json();
}
```

### 手动重新验证
**按需重新验证数据**

```typescript
// app/api/revalidate/route.ts
import { revalidateTag, revalidatePath } from 'next/cache';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const { tag, path } = await request.json();

  if (tag) {
    revalidateTag(tag);
    return NextResponse.json({ revalidated: true, tag });
  }

  if (path) {
    revalidatePath(path);
    return NextResponse.json({ revalidated: true, path });
  }

  return NextResponse.json({ error: 'Invalid request' }, { status: 400 });
}

// 使用示例
async function revalidatePosts() {
  const res = await fetch('/api/revalidate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tag: 'posts' }),
  });
  return res.json();
}
```

## 🔄 客户端数据获取

### useEffect 数据获取
**传统的客户端数据获取模式**

```typescript
'use client';

import { useState, useEffect } from 'react';

interface Data {
  id: number;
  title: string;
  body: string;
}

function DataComponent() {
  const [data, setData] = useState<Data[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const res = await fetch('/api/data');
        if (!res.ok) {
          throw new Error('Failed to fetch data');
        }
        const result = await res.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>Data</h1>
      <ul>
        {data.map(item => (
          <li key={item.id}>
            <h3>{item.title}</h3>
            <p>{item.body}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### SWR 集成
**使用 SWR 进行数据获取**

```typescript
'use client';

import useSWR from 'swr';

const fetcher = async (url: string) => {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error('Failed to fetch data');
  }
  return res.json();
};

function UserList() {
  const { data, error, isLoading, mutate } = useSWR(
    '/api/users',
    fetcher,
    {
      revalidateOnFocus: true,
      revalidateOnReconnect: true,
      refreshInterval: 30000, // 30秒自动刷新
      dedupingInterval: 10000,
    }
  );

  const handleCreateUser = async (userData: any) => {
    // 乐观更新
    mutate(
      async (currentUsers: any[]) => {
        const res = await fetch('/api/users', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(userData),
        });
        const newUser = await res.json();
        return currentUsers ? [...currentUsers, newUser] : [newUser];
      },
      false // 不重新验证
    );
  };

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h1>Users</h1>
      <ul>
        {data?.map((user: any) => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>
      <button onClick={() => handleCreateUser({ name: 'New User' })}>
        Add User
      </button>
    </div>
  );
}

// 条件获取
function UserProfile({ userId }: { userId: string }) {
  const { data, error } = useSWR(
    userId ? `/api/users/${userId}` : null,
    fetcher
  );

  if (!userId) return <div>Please select a user</div>;
  if (error) return <div>Error loading user</div>;
  if (!data) return <div>Loading...</div>;

  return <div>{data.name}</div>;
}
```

### TanStack Query 集成
**使用 TanStack Query 进行数据管理**

```typescript
'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// 获取用户列表
function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const res = await fetch('/api/users');
      if (!res.ok) {
        throw new Error('Failed to fetch users');
      }
      return res.json();
    },
    staleTime: 5 * 60 * 1000, // 5分钟
    cacheTime: 10 * 60 * 1000, // 10分钟
  });
}

// 创建用户
function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (userData: any) => {
      const res = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      });
      if (!res.ok) {
        throw new Error('Failed to create user');
      }
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

// 在组件中使用
function UserManager() {
  const { data: users, isLoading, error } = useUsers();
  const createUser = useCreateUser();

  const handleCreateUser = (userData: any) => {
    createUser.mutate(userData);
  };

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h1>Users</h1>
      <ul>
        {users?.map((user: any) => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>
      <button onClick={() => handleCreateUser({ name: 'New User' })}>
        Add User
      </button>
      {createUser.isPending && <p>Creating user...</p>}
      {createUser.error && <p>Error: {createUser.error.message}</p>}
    </div>
  );
}
```

## 🛠️ API 路由

### 基础 API 路由
**创建 RESTful API 端点**

```typescript
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

// 验证 schema
const createUserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
});

// GET 请求
export async function GET() {
  try {
    const users = await getUsersFromDatabase();
    return NextResponse.json(users);
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch users' },
      { status: 500 }
    );
  }
}

// POST 请求
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const validatedData = createUserSchema.parse(body);

    const newUser = await createUserInDatabase(validatedData);

    return NextResponse.json(newUser, { status: 201 });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid data', details: error.errors },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { error: 'Failed to create user' },
      { status: 500 }
    );
  }
}

// 数据库操作函数
async function getUsersFromDatabase() {
  // 实际的数据库查询
  return [
    { id: 1, name: 'John Doe', email: 'john@example.com' },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com' },
  ];
}

async function createUserInDatabase(userData: any) {
  // 实际的数据库插入
  return {
    id: Date.now(),
    ...userData,
    createdAt: new Date().toISOString(),
  };
}
```

### 动态 API 路由
**处理动态参数**

```typescript
// app/api/users/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';

// GET 单个用户
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const user = await getUserById(params.id);

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    return NextResponse.json(user);
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch user' },
      { status: 500 }
    );
  }
}

// PUT 更新用户
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json();
    const updatedUser = await updateUserById(params.id, body);

    if (!updatedUser) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    return NextResponse.json(updatedUser);
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to update user' },
      { status: 500 }
    );
  }
}

// DELETE 用户
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const deleted = await deleteUserById(params.id);

    if (!deleted) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({ message: 'User deleted successfully' });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to delete user' },
      { status: 500 }
    );
  }
}
```

### 流式响应
**处理大型数据集**

```typescript
// app/api/stream-data/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      try {
        for (let i = 0; i < 100; i++) {
          const data = { id: i, message: `Item ${i}` };
          const chunk = `data: ${JSON.stringify(data)}\n\n`;
          controller.enqueue(encoder.encode(chunk));

          // 模拟延迟
          await new Promise(resolve => setTimeout(resolve, 100));
        }

        controller.close();
      } catch (error) {
        controller.error(error);
      }
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}

// 客户端消费流式数据
'use client';

import { useEffect, useState } from 'react';

function StreamComponent() {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    const eventSource = new EventSource('/api/stream-data');

    eventSource.onmessage = (event) => {
      const newData = JSON.parse(event.data);
      setData(prev => [...prev, newData]);
    };

    eventSource.onerror = (error) => {
      console.error('EventSource failed:', error);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <div>
      <h1>Streaming Data</h1>
      <ul>
        {data.map(item => (
          <li key={item.id}>{item.message}</li>
        ))}
      </ul>
    </div>
  );
}
```

## 🔄 Server Actions

### 表单处理
**使用 Server Actions 处理表单提交**

```typescript
// app/actions.ts
'use server';

import { z } from 'zod';
import { redirect } from 'next/navigation';

const formSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email address'),
  message: z.string().min(10, 'Message must be at least 10 characters'),
});

export async function submitContactForm(formData: FormData) {
  const validatedFields = formSchema.safeParse({
    name: formData.get('name'),
    email: formData.get('email'),
    message: formData.get('message'),
  });

  if (!validatedFields.success) {
    return {
      error: 'Invalid form data',
      details: validatedFields.error.flatten().fieldErrors,
    };
  }

  try {
    // 处理表单提交
    await saveContactForm(validatedFields.data);

    return { success: true, message: 'Form submitted successfully' };
  } catch (error) {
    return { error: 'Failed to submit form' };
  }
}

export async function createProduct(prevState: any, formData: FormData) {
  const name = formData.get('name') as string;
  const price = formData.get('price') as string;
  const description = formData.get('description') as string;

  try {
    const product = await saveProduct({
      name,
      price: parseFloat(price),
      description,
    });

    redirect(`/products/${product.id}`);
  } catch (error) {
    return { error: 'Failed to create product' };
  }
}
```

### Server Actions 在组件中使用
**在 React 组件中使用 Server Actions**

```typescript
// app/contact/page.tsx
import { submitContactForm } from '../actions';
import { useFormState } from 'react-dom';

function ContactForm() {
  const [state, formAction] = useFormState(submitContactForm, null);

  return (
    <form action={formAction} className="contact-form">
      <div>
        <label htmlFor="name">Name</label>
        <input type="text" id="name" name="name" required />
        {state?.details?.name && (
          <span className="error">{state.details.name[0]}</span>
        )}
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input type="email" id="email" name="email" required />
        {state?.details?.email && (
          <span className="error">{state.details.email[0]}</span>
        )}
      </div>

      <div>
        <label htmlFor="message">Message</label>
        <textarea id="message" name="message" required />
        {state?.details?.message && (
          <span className="error">{state.details.message[0]}</span>
        )}
      </div>

      {state?.error && (
        <div className="error-message">{state.error}</div>
      )}

      {state?.success && (
        <div className="success-message">{state.message}</div>
      )}

      <button type="submit">Send Message</button>
    </form>
  );
}

// 使用 useActionState (React 19)
'use client';

import { useActionState } from 'react';
import { createProduct } from '../actions';

function ProductForm() {
  const [state, action, isPending] = useActionState(createProduct, null);

  return (
    <form action={action}>
      <input type="text" name="name" placeholder="Product name" required />
      <input type="number" name="price" placeholder="Price" required />
      <textarea name="description" placeholder="Description" />

      {state?.error && <div className="error">{state.error}</div>}

      <button type="submit" disabled={isPending}>
        {isPending ? 'Creating...' : 'Create Product'}
      </button>
    </form>
  );
}
```

### 乐观更新
**使用 useOptimistic 进行乐观更新**

```typescript
// app/todos/page.tsx
import { useOptimistic } from 'react';
import { addTodo } from '../actions';

function TodoList({ todos }: { todos: Todo[] }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo: Todo) => [...state, { ...newTodo, id: `temp-${Date.now()}`, optimistic: true }]
  );

  return (
    <div>
      <h2>Todos</h2>
      <form
        action={async (formData) => {
          const text = formData.get('text') as string;
          addOptimisticTodo({ text, completed: false, id: '' });
          await addTodo(text);
        }}
      >
        <input type="text" name="text" placeholder="Add a todo..." />
        <button type="submit">Add Todo</button>
      </form>

      <ul>
        {optimisticTodos.map(todo => (
          <li key={todo.id} className={todo.optimistic ? 'optimistic' : ''}>
            {todo.text}
            {todo.optimistic && <span className="pending">Pending...</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## 🔧 高级数据获取模式

### 数据预加载
**在导航前预加载数据**

```typescript
// components/PostLink.tsx
import Link from 'next/link';
import { preload } from 'react-dom';

const preloadPost = (slug: string) => {
  preload(`/api/posts/${slug}`, () =>
    fetch(`/api/posts/${slug}`).then(res => res.json())
  );
};

function PostLink({ post }: { post: { slug: string; title: string } }) {
  return (
    <Link
      href={`/blog/${post.slug}`}
      onMouseEnter={() => preloadPost(post.slug)}
    >
      {post.title}
    </Link>
  );
}
```

### 缓存策略模式
**实现智能缓存策略**

```typescript
// lib/data-cache.ts
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

class DataCache {
  private cache = new Map<string, CacheEntry<any>>();

  async get<T>(
    key: string,
    fetcher: () => Promise<T>,
    ttl: number = 5 * 60 * 1000 // 5分钟默认TTL
  ): Promise<T> {
    const entry = this.cache.get(key);
    const now = Date.now();

    if (entry && (now - entry.timestamp) < entry.ttl) {
      return entry.data;
    }

    const data = await fetcher();
    this.cache.set(key, { data, timestamp: now, ttl });

    return data;
  }

  invalidate(key: string) {
    this.cache.delete(key);
  }

  clear() {
    this.cache.clear();
  }

  // 批量获取
  async getBatch<T>(
    keys: string[],
    fetcher: (key: string) => Promise<T>,
    ttl?: number
  ): Promise<T[]> {
    const promises = keys.map(key => this.get(key, () => fetcher(key), ttl));
    return Promise.all(promises);
  }
}

export const dataCache = new DataCache();

// 使用示例
async function getPostsWithCache() {
  return dataCache.get(
    'posts',
    () => fetch('/api/posts').then(res => res.json()),
    10 * 60 * 1000 // 10分钟
  );
}
```

### 错误处理和重试
**健壮的错误处理机制**

```typescript
// lib/data-fetcher.ts
interface FetchOptions extends RequestInit {
  retries?: number;
  retryDelay?: number;
  cache?: RequestCache;
}

async function robustFetch(
  url: string,
  options: FetchOptions = {}
): Promise<Response> {
  const {
    retries = 3,
    retryDelay = 1000,
    cache = 'default',
    ...fetchOptions
  } = options;

  let lastError: Error;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const response = await fetch(url, {
        ...fetchOptions,
        cache,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response;
    } catch (error) {
      lastError = error as Error;

      if (attempt < retries) {
        // 指数退避
        const delay = retryDelay * Math.pow(2, attempt);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError!;
}

// 自定义 Hook
export function useRobustFetch<T>(url: string, options?: FetchOptions) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await robustFetch(url, options);
      const result = await response.json();

      setData(result);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [url, options]);

  useEffect(() => {
    execute();
  }, [execute]);

  return { data, loading, error, refetch: execute };
}
```

## 📋 最佳实践

### 数据获取策略选择
```typescript
// 静态生成 - 适用于不经常变化的内容
export async function generateStaticProps() {
  const posts = await getStaticPosts();
  return { props: { posts } };
}

// 服务器端渲染 - 适用于个性化内容
export async function getServerSideProps(context) {
  const user = await getUserFromCookie(context.req);
  const posts = await getPersonalizedPosts(user.id);
  return { props: { user, posts } };
}

// 客户端获取 - 适用于交互式数据
function InteractiveComponent() {
  const { data, error } = useSWR('/api/realtime-data', fetcher);
  // ...
}
```

### 性能优化建议
1. **使用适当的缓存策略**
2. **实现数据预加载**
3. **优化 API 响应大小**
4. **使用流式传输处理大数据**
5. **实现智能重试机制**
6. **监控和优化数据获取性能**

## 📖 总结

Next.js 15 提供了灵活而强大的数据获取生态系统：

1. **服务器组件**: 直接在服务器上获取数据
2. **客户端组件**: 使用传统的数据获取模式
3. **API 路由**: 构建后端 API
4. **Server Actions**: 处理表单和状态变更
5. **缓存策略**: 优化数据加载性能
6. **错误处理**: 构建健壮的应用

选择合适的数据获取策略取决于你的具体需求、数据类型和性能要求。