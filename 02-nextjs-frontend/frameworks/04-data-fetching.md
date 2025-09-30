# 04 - 数据获取与缓存策略

## 目录

1. [概述](#概述)
2. [客户端数据获取](#客户端数据获取)
3. [服务端数据获取](#服务端数据获取)
4. [增量静态再生成](#增量静态再生成)
5. [数据缓存策略](#数据缓存策略)
6. [实时数据获取](#实时数据获取)
7. [性能优化](#性能优化)
8. [最佳实践](#最佳实践)
9. [项目实战](#项目实战)
10. [总结](#总结)

## 概述

Next.js 15 提供了强大的数据获取和缓存系统，让开发者能够构建高性能的数据驱动应用。

### 与PHP开发的对比

**传统PHP开发：**
- 同步数据库查询
- 手动缓存实现
- 有限的客户端状态管理
- 实时更新需要额外技术栈

**Next.js数据获取：**
- 服务端组件和客户端组件分别处理
- 自动缓存和再验证机制
- 内置数据加载状态管理
- 支持实时数据流和订阅

### Next.js 15 数据获取特性

- **并行数据获取**: 同时获取多个数据源
- **智能缓存**: 自动缓存和失效策略
- **流式渲染**: 支持服务器端流式响应
- **增量静态再生成**: 部分页面更新
- **React 19集成**: 使用新的Actions和并发特性

## 客户端数据获取

### 使用 TanStack Query

TanStack Query（原React Query）是现代React应用的数据获取首选库。

```typescript
// components/posts-list.tsx
'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

// API请求函数
const fetchPosts = async (page = 1) => {
  const response = await fetch(`/api/posts?page=${page}`)
  if (!response.ok) throw new Error('Failed to fetch posts')
  return response.json()
}

const createPost = async (newPost: { title: string; content: string }) => {
  const response = await fetch('/api/posts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(newPost),
  })
  if (!response.ok) throw new Error('Failed to create post')
  return response.json()
}

export default function PostsList() {
  const [page, setPage] = useState(1)
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')

  const queryClient = useQueryClient()

  // 获取帖子列表
  const {
    data: postsData,
    isLoading,
    isError,
    error,
    isFetching,
  } = useQuery({
    queryKey: ['posts', page],
    queryFn: () => fetchPosts(page),
    keepPreviousData: true, // 保持上一页数据
    staleTime: 5 * 60 * 1000, // 5分钟内数据不过期
    cacheTime: 10 * 60 * 1000, // 10分钟缓存
  })

  // 创建新帖子
  const createPostMutation = useMutation({
    mutationFn: createPost,
    onSuccess: () => {
      // 成功后使缓存失效
      queryClient.invalidateQueries(['posts'])
      setTitle('')
      setContent('')
    },
    onError: (error) => {
      console.error('Error creating post:', error)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (title && content) {
      createPostMutation.mutate({ title, content })
    }
  }

  if (isLoading) return <div>Loading...</div>
  if (isError) return <div>Error: {error.message}</div>

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8">Posts</h1>

      {/* 创建新帖子表单 */}
      <form onSubmit={handleSubmit} className="mb-8 p-6 bg-gray-50 rounded-lg">
        <h2 className="text-xl font-semibold mb-4">Create New Post</h2>
        <div className="space-y-4">
          <input
            type="text"
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full p-2 border rounded"
            disabled={createPostMutation.isLoading}
          />
          <textarea
            placeholder="Content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="w-full p-2 border rounded h-24"
            disabled={createPostMutation.isLoading}
          />
          <button
            type="submit"
            disabled={createPostMutation.isLoading || !title || !content}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {createPostMutation.isLoading ? 'Creating...' : 'Create Post'}
          </button>
        </div>
      </form>

      {/* 帖子列表 */}
      <div className="space-y-4">
        {postsData?.posts?.map((post: any) => (
          <div key={post.id} className="p-4 border rounded-lg">
            <h3 className="text-xl font-semibold">{post.title}</h3>
            <p className="text-gray-600 mt-2">{post.content}</p>
            <div className="text-sm text-gray-500 mt-2">
              By {post.author} • {new Date(post.createdAt).toLocaleDateString()}
            </div>
          </div>
        ))}
      </div>

      {/* 分页 */}
      <div className="mt-8 flex justify-center space-x-2">
        <button
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1 || isFetching}
          className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
        >
          Previous
        </button>
        <span className="px-4 py-2">Page {page}</span>
        <button
          onClick={() => setPage(p => p + 1)}
          disabled={!postsData?.hasMore || isFetching}
          className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
        >
          Next
        </button>
      </div>

      {isFetching && <div className="mt-4 text-center">Updating...</div>}
    </div>
  )
}
```

### 使用 SWR

SWR是Next.js团队开发的数据获取库，与Next.js有很好的集成。

```typescript
// components/swr-example.tsx
'use client'

import useSWR from 'swr'
import useSWRMutation from 'swr/mutation'

// 请求函数
const fetcher = (url: string) => fetch(url).then(res => res.json())

// 更新函数
async function updatePost(url: string, { arg }: { arg: { id: string; data: any } }) {
  const response = await fetch(`${url}/${arg.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(arg.data),
  })
  return response.json()
}

export default function SWRExample() {
  // 获取用户数据
  const { data: user, error: userError, isLoading } = useSWR(
    '/api/user',
    fetcher,
    {
      refreshInterval: 3000, // 每3秒自动刷新
      revalidateOnFocus: true, // 窗口聚焦时重新验证
    }
  )

  // 获取用户帖子
  const { data: posts } = useSWR(
    user ? `/api/posts?userId=${user.id}` : null,
    fetcher
  )

  // 更新帖子
  const { trigger: updatePostTrigger, isMutating } = useSWRMutation(
    '/api/posts',
    updatePost,
    {
      optimisticData: (currentData, { arg }) => ({
        ...currentData,
        posts: currentData.posts.map((post: any) =>
          post.id === arg.id ? { ...post, ...arg.data } : post
        ),
      }),
      populateCache: (newPost, currentData) => ({
        ...currentData,
        posts: currentData.posts.map((post: any) =>
          post.id === newPost.id ? newPost : post
        ),
      }),
      revalidate: false,
    }
  )

  const handleUpdate = async (postId: string, newData: any) => {
    try {
      await updatePostTrigger({ id: postId, data: newData })
    } catch (error) {
      console.error('Failed to update post:', error)
    }
  }

  if (isLoading) return <div>Loading...</div>
  if (userError) return <div>Error loading user</div>

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Welcome, {user?.name}</h1>

      <div className="space-y-4">
        {posts?.map((post: any) => (
          <div key={post.id} className="p-4 border rounded">
            <h3 className="font-semibold">{post.title}</h3>
            <p className="text-gray-600">{post.content}</p>
            <button
              onClick={() => handleUpdate(post.id, { title: `${post.title} (Updated)` })}
              disabled={isMutating}
              className="mt-2 px-3 py-1 bg-blue-500 text-white rounded text-sm"
            >
              Update Title
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
```

## 服务端数据获取

### 服务端组件数据获取

在Next.js 15中，服务端组件可以直接获取数据。

```typescript
// app/posts/page.tsx
import { Suspense } from 'react'
import Link from 'next/link'
import { notFound } from 'next/navigation'

// 数据获取函数
async function getPosts() {
  const res = await fetch('https://api.example.com/posts', {
    next: {
      tags: ['posts'], // 用于缓存标签
      revalidate: 3600 // 1小时后重新验证
    }
  })

  if (!res.ok) {
    throw new Error('Failed to fetch posts')
  }

  return res.json()
}

// 异步组件
async function PostsList() {
  const posts = await getPosts()

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {posts.map((post: any) => (
        <div key={post.id} className="p-6 bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
          <h2 className="text-xl font-semibold mb-2">
            <Link href={`/posts/${post.id}`} className="hover:text-blue-600">
              {post.title}
            </Link>
          </h2>
          <p className="text-gray-600 mb-4 line-clamp-3">{post.excerpt}</p>
          <div className="text-sm text-gray-500">
            By {post.author} • {new Date(post.createdAt).toLocaleDateString()}
          </div>
        </div>
      ))}
    </div>
  )
}

// 加载状态组件
function PostsLoading() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {[...Array(6)].map((_, i) => (
        <div key={i} className="p-6 bg-gray-100 rounded-lg animate-pulse">
          <div className="h-6 bg-gray-300 rounded mb-4"></div>
          <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
          <div className="h-4 bg-gray-300 rounded w-1/2"></div>
        </div>
      ))}
    </div>
  )
}

export default function PostsPage() {
  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-4xl font-bold mb-8">Blog Posts</h1>

      <Suspense fallback={<PostsLoading />}>
        <PostsList />
      </Suspense>
    </div>
  )
}
```

### 动态路由数据获取

```typescript
// app/posts/[slug]/page.tsx
import { notFound } from 'next/navigation'
import { Metadata } from 'next'

// 生成静态参数
export async function generateStaticParams() {
  const posts = await getPosts()
  return posts.slice(0, 10).map((post: any) => ({
    slug: post.slug,
  }))
}

// 生成元数据
export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const post = await getPost(params.slug)

  if (!post) {
    return {
      title: 'Post Not Found',
    }
  }

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: [post.coverImage],
    },
  }
}

// 获取单个帖子
async function getPost(slug: string) {
  const res = await fetch(`https://api.example.com/posts/${slug}`, {
    next: {
      tags: [`post-${slug}`],
      revalidate: 3600
    }
  })

  if (!res.ok) {
    return null
  }

  return res.json()
}

export default async function PostPage({ params }: { params: { slug: string } }) {
  const post = await getPost(params.slug)

  if (!post) {
    notFound()
  }

  return (
    <article className="max-w-4xl mx-auto p-6">
      <header className="mb-8">
        <h1 className="text-4xl font-bold mb-4">{post.title}</h1>
        <div className="text-gray-600 mb-4">
          By {post.author} • {new Date(post.createdAt).toLocaleDateString()}
        </div>
        {post.coverImage && (
          <img
            src={post.coverImage}
            alt={post.title}
            className="w-full h-64 object-cover rounded-lg mb-6"
          />
        )}
      </header>

      <div
        className="prose prose-lg max-w-none"
        dangerouslySetInnerHTML={{ __html: post.content }}
      />

      <div className="mt-8 pt-8 border-t">
        <h3 className="text-xl font-semibold mb-4">Related Posts</h3>
        <RelatedPosts currentPostId={post.id} category={post.category} />
      </div>
    </article>
  )
}

// 相关帖子组件
async function RelatedPosts({ currentPostId, category }: { currentPostId: string; category: string }) {
  const res = await fetch(`https://api.example.com/posts?category=${category}&exclude=${currentPostId}`, {
    next: { revalidate: 3600 }
  })

  const posts = await res.json()

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {posts.slice(0, 4).map((post: any) => (
        <Link
          key={post.id}
          href={`/posts/${post.slug}`}
          className="block p-4 border rounded hover:bg-gray-50 transition-colors"
        >
          <h4 className="font-semibold">{post.title}</h4>
          <p className="text-sm text-gray-600 mt-1 line-clamp-2">{post.excerpt}</p>
        </Link>
      ))}
    </div>
  )
}
```

## 增量静态再生成

ISR允许你在构建时生成静态页面，并在需要时重新生成。

```typescript
// app/products/page.tsx
import { Suspense } from 'react'

// ISR数据获取
async function getProducts() {
  const res = await fetch('https://api.example.com/products', {
    next: {
      revalidate: 60, // 每60秒重新生成
    }
  })

  if (!res.ok) {
    throw new Error('Failed to fetch products')
  }

  return res.json()
}

// 手动重新验证路由处理
export async function GET() {
  const res = await fetch('https://api.example.com/products/revalidate', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${process.env.API_TOKEN}` }
  })

  if (res.ok) {
    // 重新验证产品页面
    await revalidateTag('products')

    return Response.json({ revalidated: true, now: Date.now() })
  }

  return Response.json({ revalidated: false, now: Date.now() })
}

export default async function ProductsPage() {
  const products = await getProducts()

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-4xl font-bold mb-8">Products</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {products.map((product: any) => (
          <div key={product.id} className="p-4 bg-white rounded-lg shadow">
            <img
              src={product.image}
              alt={product.name}
              className="w-full h-48 object-cover rounded mb-4"
            />
            <h3 className="font-semibold">{product.name}</h3>
            <p className="text-gray-600">{product.price}</p>
            <p className="text-sm text-gray-500 mt-2">{product.description}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
```

## 数据缓存策略

### 路由缓存配置

```typescript
// lib/cache-config.ts
import { unstable_cache } from 'next/cache'

// 缓存函数示例
const getCachedData = unstable_cache(
  async (id: string) => {
    const response = await fetch(`https://api.example.com/data/${id}`)
    return response.json()
  },
  ['data-cache'], // 缓存键前缀
  {
    revalidate: 3600, // 1小时后重新验证
    tags: ['data'], // 缓存标签
  }
)

// 使用缓存函数
export async function DataComponent({ id }: { id: string }) {
  const data = await getCachedData(id)

  return <div>{data.content}</div>
}

// 手动重新验证缓存
export async function revalidateData() {
  await revalidateTag('data')
}
```

### 客户端缓存策略

```typescript
// hooks/use-cached-data.ts
'use client'

import { useQuery, useQueryClient } from '@tanstack/react-query'

export function useCachedData(key: string, fetchFn: () => Promise<any>) {
  const queryClient = useQueryClient()

  return useQuery({
    queryKey: [key],
    queryFn: fetchFn,
    staleTime: 5 * 60 * 1000, // 5分钟
    cacheTime: 30 * 60 * 1000, // 30分钟
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    onSuccess: (data) => {
      // 预取相关数据
      if (data.related) {
        queryClient.prefetchQuery({
          queryKey: ['related', data.id],
          queryFn: () => fetchRelatedData(data.id),
          staleTime: 10 * 60 * 1000,
        })
      }
    },
  })
}

// 获取相关数据
async function fetchRelatedData(id: string) {
  const response = await fetch(`/api/related/${id}`)
  return response.json()
}
```

## 实时数据获取

### 使用Server-Sent Events (SSE)

```typescript
// app/live-updates/page.tsx
'use client'

import { useEffect, useState } from 'react'

export default function LiveUpdatesPage() {
  const [updates, setUpdates] = useState<any[]>([])
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    const eventSource = new EventSource('/api/updates')

    eventSource.onopen = () => {
      setIsConnected(true)
    }

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setUpdates(prev => [data, ...prev].slice(0, 50)) // 保留最近50条
    }

    eventSource.onerror = (error) => {
      console.error('SSE error:', error)
      setIsConnected(false)
      eventSource.close()
    }

    return () => {
      eventSource.close()
    }
  }, [])

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Live Updates</h1>

      <div className={`mb-4 ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
        {isConnected ? 'Connected' : 'Disconnected'}
      </div>

      <div className="space-y-3">
        {updates.map((update, index) => (
          <div key={index} className="p-4 bg-gray-50 rounded">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-semibold">{update.title}</h3>
                <p className="text-gray-600 text-sm">{update.message}</p>
              </div>
              <span className="text-xs text-gray-500">
                {new Date(update.timestamp).toLocaleTimeString()}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// API路由处理SSE
// app/api/updates/route.ts
export async function GET(request: Request) {
  const encoder = new TextEncoder()

  const customReadable = new ReadableStream({
    async start(controller) {
      // 模拟实时数据推送
      const sendUpdate = (data: any) => {
        const message = `data: ${JSON.stringify(data)}\n\n`
        controller.enqueue(encoder.encode(message))
      }

      // 发送初始连接消息
      sendUpdate({
        type: 'connection',
        message: 'Connected to live updates',
        timestamp: new Date().toISOString()
      })

      // 模拟定期更新
      const interval = setInterval(() => {
        sendUpdate({
          type: 'update',
          title: `Update ${Date.now()}`,
          message: `Random update at ${new Date().toLocaleTimeString()}`,
          timestamp: new Date().toISOString()
        })
      }, 5000)

      // 清理连接
      request.signal.addEventListener('abort', () => {
        clearInterval(interval)
        controller.close()
      })
    },
  })

  return new Response(customReadable, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  })
}
```

### WebSocket集成

```typescript
// components/chat.tsx
'use client'

import { useEffect, useRef, useState } from 'react'

interface Message {
  id: string
  user: string
  text: string
  timestamp: Date
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // 连接WebSocket
    const ws = new WebSocket('wss://your-websocket-server.com')
    wsRef.current = ws

    ws.onopen = () => {
      setIsConnected(true)
    }

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      setMessages(prev => [...prev, message])
    }

    ws.onclose = () => {
      setIsConnected(false)
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    return () => {
      ws.close()
    }
  }, [])

  useEffect(() => {
    // 滚动到底部
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = () => {
    if (inputValue.trim() && wsRef.current) {
      const message: Message = {
        id: Date.now().toString(),
        user: 'You',
        text: inputValue,
        timestamp: new Date(),
      }

      wsRef.current.send(JSON.stringify(message))
      setInputValue('')
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="bg-gray-800 text-white p-4 flex justify-between items-center">
          <h2 className="text-lg font-semibold">Live Chat</h2>
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
        </div>

        <div className="h-96 overflow-y-auto p-4 space-y-3">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.user === 'You' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.user === 'You'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-800'
                }`}
              >
                <div className="text-sm font-medium">{message.user}</div>
                <div>{message.text}</div>
                <div className="text-xs opacity-75 mt-1">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 border-t">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Type a message..."
              className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={!isConnected}
            />
            <button
              onClick={sendMessage}
              disabled={!isConnected || !inputValue.trim()}
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
```

## 性能优化

### 数据预取

```typescript
// components/link-with-prefetch.tsx
'use client'

import Link from 'next/link'
import { useQueryClient } from '@tanstack/react-query'

interface LinkWithPrefetchProps {
  href: string
  prefetchData?: () => Promise<any>
  prefetchKey?: string[]
  children: React.ReactNode
  className?: string
}

export default function LinkWithPrefetch({
  href,
  prefetchData,
  prefetchKey,
  children,
  className
}: LinkWithPrefetchProps) {
  const queryClient = useQueryClient()

  const handleMouseEnter = async () => {
    if (prefetchData && prefetchKey) {
      // 预取数据
      queryClient.prefetchQuery({
        queryKey: prefetchKey,
        queryFn: prefetchData,
        staleTime: 10 * 60 * 1000, // 10分钟
      })
    }

    // 预取页面
    if (typeof window !== 'undefined') {
      const router = require('next/router').default
      router.prefetch(href)
    }
  }

  return (
    <Link
      href={href}
      className={className}
      onMouseEnter={handleMouseEnter}
    >
      {children}
    </Link>
  )
}

// 使用示例
export function ProductCard({ product }: { product: any }) {
  return (
    <LinkWithPrefetch
      href={`/products/${product.id}`}
      prefetchData={() => fetchProductDetails(product.id)}
      prefetchKey={['product', product.id]}
      className="block"
    >
      <div className="p-4 border rounded hover:shadow-lg transition-shadow">
        <h3>{product.name}</h3>
        <p>{product.price}</p>
      </div>
    </LinkWithPrefetch>
  )
}
```

### 懒加载和代码分割

```typescript
// components/lazy-loaded-data.tsx
'use client'

import { lazy, Suspense } from 'react'
import { useQuery } from '@tanstack/react-query'

// 懒加载组件
const LazyChart = lazy(() => import('./chart'))
const LazyTable = lazy(() => import('./table'))

// 数据获取函数
const fetchAnalyticsData = async () => {
  const response = await fetch('/api/analytics')
  return response.json()
}

// 加载状态组件
function LoadingSpinner() {
  return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    </div>
  )
}

// 错误边界组件
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="text-center p-6">
          <h2 className="text-xl font-semibold text-red-600 mb-2">Something went wrong</h2>
          <button
            onClick={() => this.setState({ hasError: false })}
            className="px-4 py-2 bg-blue-500 text-white rounded"
          >
            Try again
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

export default function LazyLoadedData() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['analytics'],
    queryFn: fetchAnalyticsData,
    staleTime: 5 * 60 * 1000,
  })

  if (isLoading) return <LoadingSpinner />
  if (error) return <div>Error loading data</div>

  return (
    <div className="space-y-8">
      {/* 懒加载图表 */}
      <ErrorBoundary>
        <Suspense fallback={<LoadingSpinner />}>
          <LazyChart data={data.chartData} />
        </Suspense>
      </ErrorBoundary>

      {/* 懒加载表格 */}
      <ErrorBoundary>
        <Suspense fallback={<LoadingSpinner />}>
          <LazyTable data={data.tableData} />
        </Suspense>
      </ErrorBoundary>
    </div>
  )
}
```

## 最佳实践

### 1. 数据获取策略选择

```typescript
// 选择合适的数据获取策略
export function DataFetchingStrategy() {
  // 服务端组件：静态内容，SEO重要
  // app/static-page/page.tsx
  async function StaticContent() {
    const data = await fetchStaticData()
    return <div>{data.content}</div>
  }

  // 客户端组件：交互式数据，频繁更新
  // components/client-data.tsx
  function InteractiveData() {
    const { data } = useQuery({
      queryKey: ['realtime-data'],
      queryFn: fetchRealtimeData,
      refetchInterval: 5000,
    })
    return <div>{data?.value}</div>
  }

  // 混合策略：服务端预取，客户端更新
  // components/hybrid-data.tsx
  function HybridData({ initialData }: { initialData: any }) {
    const { data } = useQuery({
      queryKey: ['hybrid-data'],
      queryFn: fetchUpdatedData,
      initialData,
      staleTime: 30 * 1000,
    })
    return <div>{data.value}</div>
  }
}
```

### 2. 错误处理和重试

```typescript
// hooks/use-data-with-retry.ts
'use client'

import { useQuery } from '@tanstack/react-query'

export function useDataWithRetry<T>(
  queryKey: string[],
  queryFn: () => Promise<T>,
  options: {
    retryCount?: number
    retryDelay?: number
    onError?: (error: Error) => void
  } = {}
) {
  return useQuery({
    queryKey,
    queryFn,
    retry: (failureCount, error: Error) => {
      // 只重试网络错误，不重试4xx错误
      if (error.message.includes('404') || error.message.includes('400')) {
        return false
      }
      return failureCount < (options.retryCount || 3)
    },
    retryDelay: (attemptIndex) => {
      // 指数退避
      return Math.min(1000 * 2 ** attemptIndex, options.retryDelay || 30000)
    },
    onError: options.onError,
  })
}

// 使用示例
function UserProfile({ userId }: { userId: string }) {
  const { data, error, isLoading } = useDataWithRetry(
    ['user', userId],
    () => fetchUser(userId),
    {
      retryCount: 3,
      retryDelay: 10000,
      onError: (error) => {
        console.error('Failed to load user:', error)
        // 可以在这里触发错误报告
      },
    }
  )

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error loading user profile</div>

  return <div>Welcome, {data.name}</div>
}
```

### 3. 缓存策略优化

```typescript
// lib/cache-strategy.ts
'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

// 智能缓存策略
export function useSmartCache<T>(
  key: string[],
  fetchFn: () => Promise<T>,
  options: {
    // 数据类型
    dataType?: 'static' | 'dynamic' | 'realtime'
    // 用户交互频率
    interactionFrequency?: 'low' | 'medium' | 'high'
    // 数据重要性
    importance?: 'low' | 'medium' | 'high'
  } = {}
) {
  const { dataType = 'dynamic', interactionFrequency = 'medium', importance = 'medium' } = options

  // 根据数据类型设置缓存策略
  const cacheStrategy = {
    static: {
      staleTime: 60 * 60 * 1000, // 1小时
      cacheTime: 24 * 60 * 60 * 1000, // 24小时
      refetchOnWindowFocus: false,
      refetchOnReconnect: false,
    },
    dynamic: {
      staleTime: 5 * 60 * 1000, // 5分钟
      cacheTime: 30 * 60 * 1000, // 30分钟
      refetchOnWindowFocus: true,
      refetchOnReconnect: true,
    },
    realtime: {
      staleTime: 0,
      cacheTime: 5 * 60 * 1000, // 5分钟
      refetchInterval: 5000, // 5秒
      refetchOnWindowFocus: true,
      refetchOnReconnect: true,
    },
  }

  return useQuery({
    queryKey: key,
    queryFn: fetchFn,
    ...cacheStrategy[dataType],
  })
}

// 数据更新策略
export function useOptimisticUpdate<T>(
  key: string[],
  updateFn: (data: T) => Promise<T>
) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: updateFn,
    onMutate: async (newData) => {
      // 取消正在进行的查询
      await queryClient.cancelQueries(key)

      // 获取当前数据快照
      const previousData = queryClient.getQueryData(key)

      // 乐观更新
      queryClient.setQueryData(key, newData)

      return { previousData }
    },
    onError: (err, newData, context) => {
      // 发生错误时回滚
      if (context?.previousData) {
        queryClient.setQueryData(key, context.previousData)
      }
    },
    onSettled: () => {
      // 无论成功失败都重新获取数据
      queryClient.invalidateQueries(key)
    },
  })
}
```

## 项目实战

### 完整的数据驱动仪表板

```typescript
// app/dashboard/page.tsx
import { Suspense } from 'react'
import { Metadata } from 'next'
import { notFound } from 'next/navigation'

// 动态导入客户端组件
const DashboardClient = dynamic(() => import('@/components/dashboard-client'), {
  ssr: false,
  loading: () => <DashboardLoading />
})

// 服务端数据获取
async function getDashboardData() {
  const [stats, recentActivity, notifications] = await Promise.all([
    fetch('https://api.example.com/stats', { next: { revalidate: 300 } }), // 5分钟
    fetch('https://api.example.com/activity', { next: { revalidate: 60 } }), // 1分钟
    fetch('https://api.example.com/notifications', { next: { revalidate: 30 } }), // 30秒
  ])

  if (!stats.ok || !recentActivity.ok || !notifications.ok) {
    throw new Error('Failed to fetch dashboard data')
  }

  return {
    stats: await stats.json(),
    recentActivity: await recentActivity.json(),
    notifications: await notifications.json(),
  }
}

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: 'Dashboard | Your App',
    description: 'Real-time dashboard with analytics and insights',
  }
}

export default async function DashboardPage() {
  const initialData = await getDashboardData()

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">Welcome back! Here's what's happening today.</p>
        </div>

        <Suspense fallback={<DashboardLoading />}>
          <DashboardClient initialData={initialData} />
        </Suspense>
      </div>
    </div>
  )
}

// 加载状态组件
function DashboardLoading() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white p-6 rounded-lg shadow animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-4 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-4 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
```

```typescript
// components/dashboard-client.tsx
'use client'

import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'

// 数据获取函数
const fetchDashboardStats = async () => {
  const response = await fetch('/api/dashboard/stats')
  if (!response.ok) throw new Error('Failed to fetch stats')
  return response.json()
}

const fetchRecentActivity = async () => {
  const response = await fetch('/api/dashboard/activity')
  if (!response.ok) throw new Error('Failed to fetch activity')
  return response.json()
}

const fetchNotifications = async () => {
  const response = await fetch('/api/dashboard/notifications')
  if (!response.ok) throw new Error('Failed to fetch notifications')
  return response.json()
}

const markNotificationRead = async (id: string) => {
  const response = await fetch(`/api/dashboard/notifications/${id}/read`, {
    method: 'POST',
  })
  if (!response.ok) throw new Error('Failed to mark notification as read')
  return response.json()
}

export default function DashboardClient({ initialData }: { initialData: any }) {
  const [timeRange, setTimeRange] = useState('7d')
  const queryClient = useQueryClient()

  // 实时数据获取
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats', timeRange],
    queryFn: fetchDashboardStats,
    initialData: initialData.stats,
    refetchInterval: 30000, // 30秒刷新
  })

  const { data: activity, isLoading: activityLoading } = useQuery({
    queryKey: ['dashboard-activity'],
    queryFn: fetchRecentActivity,
    initialData: initialData.recentActivity,
    refetchInterval: 60000, // 1分钟刷新
  })

  const { data: notifications, isLoading: notificationsLoading } = useQuery({
    queryKey: ['dashboard-notifications'],
    queryFn: fetchNotifications,
    initialData: initialData.notifications,
    refetchInterval: 30000, // 30秒刷新
  })

  // 标记通知为已读
  const markAsReadMutation = useMutation({
    mutationFn: markNotificationRead,
    onMutate: async (id) => {
      // 乐观更新
      const previousNotifications = queryClient.getQueryData(['dashboard-notifications'])
      queryClient.setQueryData(['dashboard-notifications'], (old: any) => ({
        ...old,
        notifications: old.notifications.map((n: any) =>
          n.id === id ? { ...n, isRead: true } : n
        ),
      }))

      return { previousNotifications }
    },
    onError: (error, id, context) => {
      // 回滚
      if (context?.previousNotifications) {
        queryClient.setQueryData(['dashboard-notifications'], context.previousNotifications)
      }
      toast.error('Failed to mark notification as read')
    },
    onSuccess: () => {
      toast.success('Notification marked as read')
    },
  })

  // 处理时间范围变化
  const handleTimeRangeChange = (range: string) => {
    setTimeRange(range)
  }

  return (
    <div className="space-y-6">
      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Revenue"
          value={`$${stats?.revenue?.toLocaleString() || 0}`}
          change={stats?.revenueChange}
          icon="💰"
          loading={statsLoading}
        />
        <StatCard
          title="Active Users"
          value={stats?.activeUsers?.toLocaleString() || 0}
          change={stats?.usersChange}
          icon="👥"
          loading={statsLoading}
        />
        <StatCard
          title="Conversion Rate"
          value={`${stats?.conversionRate || 0}%`}
          change={stats?.conversionChange}
          icon="📈"
          loading={statsLoading}
        />
        <StatCard
          title="Avg. Session"
          value={stats?.avgSession || '0m'}
          change={stats?.sessionChange}
          icon="⏱️"
          loading={statsLoading}
        />
      </div>

      {/* 时间范围选择器 */}
      <div className="flex justify-end">
        <div className="inline-flex rounded-md shadow-sm" role="group">
          {['1d', '7d', '30d', '90d'].map((range) => (
            <button
              key={range}
              onClick={() => handleTimeRangeChange(range)}
              className={`px-4 py-2 text-sm font-medium border ${
                timeRange === range
                  ? 'bg-blue-500 text-white border-blue-500'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 最近活动 */}
        <ActivityList activity={activity?.items || []} loading={activityLoading} />

        {/* 通知 */}
        <NotificationsList
          notifications={notifications?.notifications || []}
          loading={notificationsLoading}
          onMarkAsRead={markAsReadMutation.mutate}
        />
      </div>
    </div>
  )
}

// 统计卡片组件
function StatCard({ title, value, change, icon, loading }: any) {
  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
        <div className="h-8 bg-gray-200 rounded w-1/2"></div>
      </div>
    )
  }

  const isPositive = change?.startsWith('+')

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900 mt-2">{value}</p>
          {change && (
            <p className={`text-sm mt-2 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {change} from last period
            </p>
          )}
        </div>
        <div className="text-3xl">{icon}</div>
      </div>
    </div>
  )
}

// 活动列表组件
function ActivityList({ activity, loading }: { activity: any[]; loading: boolean }) {
  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-4 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b">
        <h2 className="text-lg font-semibold">Recent Activity</h2>
      </div>
      <div className="divide-y">
        {activity.map((item) => (
          <div key={item.id} className="p-4">
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  {item.type === 'user' && '👤'}
                  {item.type === 'sale' && '💰'}
                  {item.type === 'system' && '⚙️'}
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">{item.title}</p>
                <p className="text-sm text-gray-500">{item.description}</p>
              </div>
              <div className="text-sm text-gray-500">
                {new Date(item.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// 通知列表组件
function NotificationsList({
  notifications,
  loading,
  onMarkAsRead
}: {
  notifications: any[];
  loading: boolean;
  onMarkAsRead: (id: string) => void
}) {
  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-4 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b">
        <h2 className="text-lg font-semibold">Notifications</h2>
      </div>
      <div className="divide-y">
        {notifications.map((notification) => (
          <div
            key={notification.id}
            className={`p-4 ${!notification.isRead ? 'bg-blue-50' : ''}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-sm font-medium text-gray-900">
                  {notification.title}
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  {notification.message}
                </p>
                <p className="text-xs text-gray-500 mt-2">
                  {new Date(notification.createdAt).toLocaleString()}
                </p>
              </div>
              {!notification.isRead && (
                <button
                  onClick={() => onMarkAsRead(notification.id)}
                  className="ml-4 px-3 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  Mark as read
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
```

## 总结

### 关键要点

1. **数据获取策略**
   - 服务端组件适合静态内容和SEO优化
   - 客户端组件适合交互式和实时数据
   - 混合策略结合两者优势

2. **缓存管理**
   - Next.js自动缓存和手动控制
   - TanStack Query的客户端缓存
   - 智能缓存策略根据数据类型调整

3. **性能优化**
   - 数据预取和并行获取
   - 懒加载和代码分割
   - 增量静态再生成

4. **实时功能**
   - Server-Sent Events简单实时更新
   - WebSocket双向通信
   - 自动重连和错误处理

### 最佳实践总结

- **选择合适的工具**: TanStack Query适合大多数场景，SWR适合简单需求
- **合理设置缓存**: 根据数据更新频率设置staleTime
- **错误处理**: 实现重试机制和错误边界
- **用户体验**: 提供加载状态和乐观更新
- **性能监控**: 监控数据获取性能和缓存命中率

### 下一步学习

- 深入学习GraphQL和Apollo Client
- 探索离线数据同步策略
- 学习数据分析和可视化
- 实现高级缓存策略

---

通过这个文档，你已经掌握了Next.js 15中完整的数据获取和缓存策略。这些知识将帮助你构建高性能、实时响应的现代化Web应用。记住选择合适的数据获取策略，优化缓存配置，并提供良好的用户体验。