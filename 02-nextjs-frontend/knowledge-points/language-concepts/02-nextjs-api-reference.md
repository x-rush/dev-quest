# Next.js API 参考手册

> **文档简介**: Next.js 15核心API和函数快速参考，涵盖App Router、路由处理、数据获取等关键API
>
> **目标读者**: Next.js开发者，需要快速查阅Next.js API的开发者
>
> **前置知识**: React基础、Next.js基础概念、Web开发基础
>
> **预计时长**: 20-40分钟

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `knowledge-points` |
| **难度** | ⭐⭐⭐⭐ (4/5星) |
| **标签** | `#nextjs15` `#api-reference` `#app-router` `#routing` `#cheatsheet` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

---

## 🗺️ App Router API

### 文件系统路由
```
app/
├── layout.tsx          # 根布局
├── page.tsx           # 首页
├── loading.tsx        # 加载组件
├── error.tsx          # 错误边界
├── not-found.tsx      # 404页面
├── about/
│   ├── page.tsx       # /about
│   └── loading.tsx    # /about 加载状态
├── blog/
│   ├── page.tsx       # /blog
│   └── [slug]/
│       └── page.tsx   # /blog/[slug]
└── (auth)/            # 路由组
    ├── login/
    │   └── page.tsx   # /login
    └── register/
        └── page.tsx   # /register
```

### 动态路由
```tsx
// app/blog/[slug]/page.tsx
interface BlogPostPageProps {
  params: { slug: string }
  searchParams: { [key: string]: string | string[] | undefined }
}

export default function BlogPostPage({ params, searchParams }: BlogPostPageProps) {
  return (
    <div>
      <h1>Blog Post: {params.slug}</h1>
      <p>Query: {JSON.stringify(searchParams)}</p>
    </div>
  )
}
```

### 路由组
```tsx
// app/(auth)/layout.tsx
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="auth-layout">
      <nav>Auth Navigation</nav>
      {children}
    </div>
  )
}

// app/(auth)/login/page.tsx
export default function LoginPage() {
  return <div>Login Page</div>
}
```

### 并行路由
```tsx
// app/@modal/page.tsx
export default function Modal() {
  return <div>Modal Content</div>
}

// app/layout.tsx
export default function RootLayout({
  children,
  modal,
}: {
  children: React.ReactNode
  modal: React.ReactNode
}) {
  return (
    <html>
      <body>
        {children}
        {modal}
      </body>
    </html>
  )
}
```

---

## 🔄 导航API

### useRouter Hook
```tsx
'use client'

import { useRouter } from 'next/navigation'

function NavigationComponent() {
  const router = useRouter()

  const navigateToHome = () => {
    router.push('/') // 导航到首页
  }

  const replaceWithHome = () => {
    router.replace('/') // 替换当前历史记录
  }

  const goBack = () => {
    router.back() // 返回上一页
  }

  const refreshPage = () => {
    router.refresh() // 刷新当前页面
  }

  return (
    <div>
      <button onClick={navigateToHome}>Home</button>
      <button onClick={replaceWithHome}>Replace</button>
      <button onClick={goBack}>Back</button>
      <button onClick={refreshPage}>Refresh</button>
    </div>
  )
}
```

### Link 组件
```tsx
import Link from 'next/link'

// 基础链接
function BasicLink() {
  return <Link href="/about">About Us</Link>
}

// 动态路由链接
function DynamicLink({ postId }: { postId: string }) {
  return <Link href={`/blog/${postId}`}>Read Post</Link>
}

// 带查询参数的链接
function QueryLink() {
  return <Link href="/search?q=nextjs&sort=popular">Search</Link>
}

// 程序化导航样式
function StyledLink() {
  return (
    <Link
      href="/contact"
      className="nav-link"
      prefetch={true} // 预取页面
    >
      Contact
    </Link>
  )
}
```

### usePathname Hook
```tsx
'use client'

import { usePathname } from 'next/navigation'

function CurrentPath() {
  const pathname = usePathname()
  return <div>Current path: {pathname}</div>
}

function ActiveLink({ href, children }: { href: string; children: React.ReactNode }) {
  const pathname = usePathname()
  const isActive = pathname === href

  return (
    <Link href={href} className={isActive ? 'active' : ''}>
      {children}
    </Link>
  )
}
```

---

## 📡 数据获取API

### fetch 函数
```tsx
// 在服务器组件中获取数据
async function getPost(id: string) {
  const res = await fetch(`https://api.example.com/posts/${id}`, {
    cache: 'force-cache', // 强制缓存
    next: {
      revalidate: 3600, // 1小时重新验证
      tags: ['post', id] // 缓存标签
    }
  })

  if (!res.ok) {
    throw new Error('Failed to fetch post')
  }

  return res.json()
}

// 在客户端组件中获取数据
'use client'

import { useEffect, useState } from 'react'

function PostList() {
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchPosts() {
      try {
        const res = await fetch('/api/posts')
        const data = await res.json()
        setPosts(data)
      } catch (error) {
        console.error('Failed to fetch posts:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchPosts()
  }, [])

  if (loading) return <div>Loading...</div>
  return <div>{/* 渲染posts */}</div>
}
```

### 缓存策略
```tsx
// 无缓存（每次都重新获取）
const res = await fetch('https://api.example.com/data', {
  cache: 'no-store'
})

// 强制缓存（静态数据）
const res = await fetch('https://api.example.com/static-data', {
  cache: 'force-cache'
})

// 重新验证缓存（时间过期后重新获取）
const res = await fetch('https://api.example.com/data', {
  next: { revalidate: 60 } // 60秒后重新验证
})

// 标签重新验证
const res = await fetch('https://api.example.com/posts', {
  next: { tags: ['posts'] }
})

// 手动重新验证
// revalidateTag('posts')
```

### Server Actions
```tsx
// 定义Server Action
'use server'

import { revalidatePath } from 'next/cache'

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string
  const content = formData.get('content') as string

  // 数据库操作
  await db.post.create({
    data: { title, content }
  })

  // 重新验证缓存
  revalidatePath('/blog')
  revalidateTag('posts')

  return { success: true, message: 'Post created successfully' }
}

// 在组件中使用
'use client'

import { createPost } from './actions'

function CreatePostForm() {
  async function handleSubmit(formData: FormData) {
    const result = await createPost(formData)

    if (result.success) {
      alert(result.message)
    }
  }

  return (
    <form action={handleSubmit}>
      <input name="title" required />
      <textarea name="content" required />
      <button type="submit">Create Post</button>
    </form>
  )
}
```

---

## 🎨 渲染API

### 服务器组件
```tsx
// 服务器组件（默认）
async function ServerComponent() {
  const data = await fetchData()
  return <div>{data.content}</div>
}

// 异步服务器组件
async function AsyncServerComponent() {
  const posts = await fetchPosts()
  return (
    <ul>
      {posts.map(post => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
```

### 客户端组件
```tsx
'use client'

import { useState, useEffect } from 'react'

function ClientComponent() {
  const [count, setCount] = useState(0)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return <div>Loading...</div>
  }

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  )
}
```

### 混合渲染模式
```tsx
// 服务器组件包含客户端组件
async function HybridPage() {
  const data = await fetchData() // 服务器端获取数据

  return (
    <div>
      <h1>{data.title}</h1>
      <p>{data.description}</p>
      <ClientInteractiveComponent initialData={data.items} />
    </div>
  )
}

'use client'

function ClientInteractiveComponent({ initialData }: { initialData: any[] }) {
  const [items, setItems] = useState(initialData)

  const addItem = () => {
    setItems([...items, { id: Date.now(), name: 'New Item' }])
  }

  return (
    <div>
      <button onClick={addItem}>Add Item</button>
      <ul>
        {items.map(item => (
          <li key={item.id}>{item.name}</li>
        ))}
      </ul>
    </div>
  )
}
```

---

## 🔧 配置API

### next.config.js
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // 实验性功能
  experimental: {
    // 启用Turbopack
    turbo: {
      rules: {
        '*.svg': {
          loaders: ['@svgr/webpack'],
          as: '*.js',
        },
      },
    },
    // 服务器组件
    serverComponentsExternalPackages: ['@prisma/client'],
  },

  // 图片优化
  images: {
    domains: ['example.com', 'cdn.example.com'],
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // 环境变量
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },

  // 重定向
  async redirects() {
    return [
      {
        source: '/old-path',
        destination: '/new-path',
        permanent: true,
      },
    ]
  },

  // 重写规则
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://external-api.com/:path*',
      },
    ]
  },

  // 头部配置
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,POST,PUT,DELETE,OPTIONS' },
        ],
      },
    ]
  },

  // 国际化
  i18n: {
    locales: ['en', 'zh', 'ja'],
    defaultLocale: 'en',
  },

  // 输出配置
  output: 'standalone', // 或 'export', 'static'

  // 严格模式
  reactStrictMode: true,

  // SWC压缩
  swcMinify: true,
}

module.exports = nextConfig
```

### TypeScript 配置
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/lib/*": ["./src/lib/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

---

## 📁 文件约定API

### 布局文件
```tsx
// app/layout.tsx - 根布局
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <header>Site Header</header>
        <main>{children}</main>
        <footer>Site Footer</footer>
      </body>
    </html>
  )
}

// app/blog/layout.tsx - 嵌套布局
export default function BlogLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="blog-layout">
      <aside>Blog Sidebar</aside>
      <div className="content">{children}</div>
    </div>
  )
}
```

### 加载状态
```tsx
// app/loading.tsx - 全局加载
export default function Loading() {
  return <div>Loading...</div>
}

// app/blog/loading.tsx - 特定路由加载
export default function BlogLoading() {
  return <div>Loading blog posts...</div>
}

// 使用loading.tsx
async function BlogPage() {
  const posts = await fetchPosts() // 自动显示加载状态
  return <PostList posts={posts} />
}
```

### 错误处理
```tsx
// app/error.tsx - 全局错误边界
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <button onClick={() => reset()}>Try again</button>
    </div>
  )
}

// app/not-found.tsx - 404页面
export default function NotFound() {
  return (
    <div>
      <h2>Not Found</h2>
      <p>Could not find requested resource</p>
      <Link href="/">Return Home</Link>
    </div>
  )
}
```

### 路由处理程序
```tsx
// app/api/posts/route.ts - GET POST
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const posts = await getPosts()
  return NextResponse.json(posts)
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  const post = await createPost(body)
  return NextResponse.json(post, { status: 201 })
}

// app/api/posts/[id]/route.ts - 动态API路由
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const post = await getPost(params.id)

  if (!post) {
    return NextResponse.json({ error: 'Post not found' }, { status: 404 })
  }

  return NextResponse.json(post)
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const body = await request.json()
  const post = await updatePost(params.id, body)
  return NextResponse.json(post)
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  await deletePost(params.id)
  return NextResponse.json({ success: true })
}
```

---

## 🎯 中间件API

```tsx
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // 获取路径
  const path = request.nextUrl.pathname

  // 身份验证检查
  if (path.startsWith('/dashboard') && !isAuthenticated(request)) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // 地区重定向
  const country = request.geo?.country
  if (country === 'CN' && path === '/') {
    return NextResponse.redirect(new URL('/cn', request.url))
  }

  // 添加自定义头部
  const response = NextResponse.next()
  response.headers.set('x-custom-header', 'custom-value')

  return response
}

// 配置匹配路径
export const config = {
  matcher: [
    '/dashboard/:path*',
    '/api/admin/:path*',
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}

// 辅助函数
function isAuthenticated(request: NextRequest): boolean {
  const token = request.cookies.get('auth-token')?.value
  return !!token && isValidToken(token)
}
```

---

## 🔗 相关文档

- 📄 **[Next.js 15 官方文档](https://nextjs.org/docs)**: 完整Next.js文档
- 📄 **[App Router 指南](https://nextjs.org/docs/app)**: App Router详细指南
- 📄 **[React 语法速查](./01-react-syntax-cheatsheet.md)**: React核心语法
- 📄 **[TypeScript 类型速查](./03-typescript-types.md)**: TypeScript类型系统

---

## 📝 快速参考

### 核心Hook
- `useRouter()` - 程序化导航
- `usePathname()` - 获取当前路径
- `useSearchParams()` - 获取查询参数
- `use()` - 读取Promise/Context (React 19)

### 文件约定
- `page.tsx` - 页面组件
- `layout.tsx` - 布局组件
- `loading.tsx` - 加载状态
- `error.tsx` - 错误边界
- `not-found.tsx` - 404页面
- `route.ts` - API路由

### 缓存策略
- `cache: 'force-cache'` - 强制缓存
- `cache: 'no-store'` - 无缓存
- `revalidate: number` - 时间重新验证
- `tags: string[]` - 标签重新验证

---

## 🔄 文档交叉引用

### 相关文档
- 📄 **[React语法速查表](./01-react-syntax-cheatsheet.md)**: 深入了解React组件语法和Hooks使用
- 📄 **[TypeScript类型速查](./03-typescript-types.md)**: 学习Next.js项目的类型定义和泛型
- 📄 **[现代JavaScript语法](./04-javascript-modern.md)**: 掌握Next.js开发所需的ES6+语法
- 📄 **[CSS模式速查](./05-css-patterns.md)**: 了解Next.js中的样式处理和CSS-in-JS

### 参考章节
- 📖 **[本模块其他章节]**: [framework-patterns/App Router模式](../framework-patterns/01-app-router-patterns.md)中的路由系统详解
- 📖 **[其他模块相关内容]**: [basics/布局和路由设计](../../basics/04-layouts-routing.md)中的路由实践部分

---

## 📝 总结

### 核心要点回顾
1. **App Router系统**: Next.js 15的革命性路由架构，基于文件系统约定
2. **动态路由处理**: 类型安全的参数处理和路由验证
3. **数据获取API**: fetch、Server Actions、缓存控制等核心API
4. **中间件系统**: 请求拦截、认证授权、路由保护等
5. **配置系统**: next.config.js、环境变量、TypeScript配置

### 学习成果检查
- [ ] 是否掌握了Next.js 15 App Router的核心概念？
- [ ] 是否能够配置动态路由和路由参数？
- [ ] 是否理解了Next.js的数据获取策略？
- [ ] 是否能够使用中间件进行请求处理？
- [ ] 是否具备了Next.js项目配置和优化的能力？

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
- 📖 **[Next.js 15 官方文档](https://nextjs.org/docs)**: 完整的Next.js文档
- 📖 **[App Router API 参考](https://nextjs.org/docs/app/api-reference/file-conventions)**: 文件约定API
- 📖 **[数据获取文档](https://nextjs.org/docs/app/building-your-application/data-fetching)**: 数据获取指南

### 快速参考
**路由参数类型**:
```tsx
interface Params {
  slug: string
  category: string
}

// 动态路由页面
export default function Page({ params }: { params: Params }) {
  return <div>Category: {params.category}, Slug: {params.slug}</div>
}
```

**缓存配置示例**:
```tsx
// 强制缓存
const data = await fetch('https://api.example.com/data', {
  next: { revalidate: 3600, tags: ['products'] }
})

// 无缓存
const realtime = await fetch('https://api.example.com/realtime', {
  cache: 'no-store'
})
```

---

**文档状态**: ✅ 已完成 | 🚧 进行中 | 📋 计划中
**最后更新**: 2025年10月
**版本**: v1.0.0