# Next.js 15 App Router 高级用法

## 📋 概述

Next.js 15 的 App Router 是一个基于 React Server Components 和 React 19 的新路由系统，它提供了更强大、更灵活的路由和渲染能力。本文将深入探讨 App Router 的高级用法和最佳实践。

## 🎯 App Router 核心概念

### 1. 文件系统路由

```
app/
├── layout.tsx          # 根布局
├── page.tsx           # 首页
├── about/
│   ├── page.tsx       # 关于页面
│   └── team/
│       └── page.tsx   # 团队页面
├── blog/
│   ├── layout.tsx     # 博客布局
│   ├── page.tsx       # 博客列表
│   └── [slug]/
│       └── page.tsx   # 博客详情
└── (auth)/
    └── login/
        └── page.tsx   # 登录页面
```

### 2. 路由元数据

```typescript
// app/layout.tsx
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'My App',
  description: 'Built with Next.js 15',
  keywords: ['nextjs', 'react', 'web development'],
  authors: [{ name: 'Your Name' }],
  creator: 'Your Company',
  publisher: 'Your Publisher',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://example.com'),
  alternates: {
    canonical: '/',
    languages: {
      'en-US': '/en-US',
      'de-DE': '/de-DE',
    },
  },
  openGraph: {
    title: 'My App',
    description: 'Built with Next.js 15',
    url: 'https://example.com',
    siteName: 'My App',
    images: [
      {
        url: '/og.png',
        width: 1200,
        height: 630,
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'My App',
    description: 'Built with Next.js 15',
    images: ['/og.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

// 动态元数据
export async function generateMetadata({
  params,
}: {
  params: { slug: string };
}): Promise<Metadata> {
  const post = await getPost(params.slug);

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: [post.image],
    },
  };
}
```

## 🚀 高级路由模式

### 1. 动态路由和捕获所有路由

```typescript
// app/blog/[slug]/page.tsx
interface BlogPostProps {
  params: {
    slug: string;
  };
}

export default async function BlogPost({ params }: BlogPostProps) {
  const post = await getPostBySlug(params.slug);

  return (
    <article>
      <h1>{post.title}</h1>
      <div>{post.content}</div>
    </article>
  );
}

// app/shop/[...slug]/page.tsx - 捕获所有路由
interface ShopPageProps {
  params: {
    slug: string[];
  };
}

export default async function ShopPage({ params }: ShopPageProps) {
  // /shop/clothing/mens -> params.slug = ['clothing', 'mens']
  const category = params.slug[0];
  const subcategory = params.slug[1];

  return (
    <div>
      <h1>Shop: {category}</h1>
      {subcategory && <p>Subcategory: {subcategory}</p>}
    </div>
  );
}

// app/[[...slug]]/page.tsx - 可选捕获所有路由
interface CatchAllPageProps {
  params: {
    slug?: string[];
  };
}

export default function CatchAllPage({ params }: CatchAllPageProps) {
  // / -> params.slug = undefined
  // /about -> params.slug = ['about']
  // /about/team -> params.slug = ['about', 'team']

  if (!params.slug) {
    return <HomePage />;
  }

  return <DynamicPage slug={params.slug} />;
}
```

### 2. 路由组和并行路由

```typescript
// app/(marketing)/layout.tsx
export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="marketing-layout">
      <nav>Marketing Navigation</nav>
      <main>{children}</main>
    </div>
  );
}

// app/(auth)/login/page.tsx
export default function LoginPage() {
  return (
    <div className="auth-page">
      <LoginForm />
    </div>
  );
}

// app/@dashboard/layout.tsx - 并行路由
export default function DashboardLayout({
  children,
  analytics,
  team,
}: {
  children: React.ReactNode;
  analytics: React.ReactNode;
  team: React.ReactNode;
}) {
  return (
    <div className="dashboard">
      <aside>
        <nav>Dashboard Nav</nav>
      </aside>
      <main>{children}</main>
      <section>{analytics}</section>
      <section>{team}</section>
    </div>
  );
}

// app/@dashboard/analytics/page.tsx
export default function AnalyticsPage() {
  return <div>Analytics Dashboard</div>;
}

// app/@dashboard/team/page.tsx
export default function TeamPage() {
  return <div>Team Management</div>;
}
```

### 3. 拦截路由

```typescript
// app/(.)photo/[id]/page.tsx - 拦截路由
export default async function PhotoPage({
  params,
}: {
  params: { id: string };
}) {
  const photo = await getPhoto(params.id);

  return (
    <div className="photo-modal">
      <img src={photo.url} alt={photo.title} />
      <h2>{photo.title}</h2>
      <p>{photo.description}</p>
    </div>
  );
}

// 在照片列表中使用
function PhotoList() {
  return (
    <div className="photo-grid">
      {photos.map(photo => (
        <Link
          key={photo.id}
          href={`/photo/${photo.id}`}
          scroll={false} // 不滚动到页面顶部
        >
          <img src={photo.thumbnail} alt={photo.title} />
        </Link>
      ))}
    </div>
  );
}
```

## 🎨 高级布局模式

### 1. 条件布局

```typescript
// app/layout.tsx
import { redirect } from 'next/navigation';

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getSession();

  if (!session) {
    redirect('/login');
  }

  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

// app/(dashboard)/layout.tsx
export default function DashboardLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  return (
    <div className="dashboard-layout">
      <Sidebar />
      <Header />
      <main className="dashboard-main">{children}</main>
    </div>
  );
}
```

### 2. 模板布局

```typescript
// app/template.tsx
'use client';

import { useState } from 'react';

export default function Template({ children }: { children: React.ReactNode }) {
  const [count, setCount] = useState(0);

  return (
    <div className="template">
      <div className="counter">
        <button onClick={() => setCount(c => c + 1)}>
          Count: {count}
        </button>
      </div>
      <div className="content">
        {children}
      </div>
    </div>
  );
}

// app/page.tsx
export default function Page() {
  return <div>Page content</div>;
}
```

### 3. 错误处理布局

```typescript
// app/error.tsx
'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // 记录错误到外部服务
    console.error(error);
  }, [error]);

  return (
    <div className="error-container">
      <h2>Something went wrong!</h2>
      <button onClick={reset}>
        Try again
      </button>
    </div>
  );
}

// app/not-found.tsx
export default function NotFound() {
  return (
    <div className="not-found">
      <h2>Page not found</h2>
      <p>Could not find requested resource</p>
      <Link href="/">Return Home</Link>
    </div>
  );
}

// app/global-error.tsx
'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body>
        <div className="global-error">
          <h2>Something went seriously wrong!</h2>
          <button onClick={reset}>Try again</button>
        </div>
      </body>
    </html>
  );
}
```

## 🔄 数据获取模式

### 1. Server Components 数据获取

```typescript
// app/blog/page.tsx
async function BlogPage() {
  const posts = await getPosts();

  return (
    <div>
      <h1>Blog</h1>
      <div className="posts">
        {posts.map(post => (
          <article key={post.id}>
            <h2>{post.title}</h2>
            <p>{post.excerpt}</p>
            <Link href={`/blog/${post.slug}`}>Read more</Link>
          </article>
        ))}
      </div>
    </div>
  );
}

// 使用缓存
async function getCachedPosts() {
  const posts = await fetch('https://api.example.com/posts', {
    next: {
      tags: ['posts'],
      revalidate: 3600, // 1小时
    },
  });

  return posts.json();
}

// 动态数据获取
async function DynamicData({ id }: { id: string }) {
  const data = await fetch(`https://api.example.com/data/${id}`, {
    cache: 'no-store',
  });

  return data.json();
}
```

### 2. 客户端数据获取

```typescript
// app/dashboard/page.tsx
'use client';

import { useQuery } from '@tanstack/react-query';

function DashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => fetch('/api/stats').then(res => res.json()),
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <h1>Dashboard</h1>
      <StatsOverview stats={stats} />
    </div>
  );
}

// 使用Server Actions
'use server';

async function createPost(formData: FormData) {
  const title = formData.get('title') as string;
  const content = formData.get('content') as string;

  await db.post.create({
    data: {
      title,
      content,
    },
  });

  revalidateTag('posts');
}

// app/posts/new/page.tsx
export default function NewPostPage() {
  return (
    <form action={createPost}>
      <input name="title" placeholder="Title" required />
      <textarea name="content" placeholder="Content" required />
      <button type="submit">Create Post</button>
    </form>
  );
}
```

### 3. 流式渲染

```typescript
// app/dashboard/page.tsx
import { Suspense } from 'react';

function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<div>Loading analytics...</div>}>
        <AnalyticsPanel />
      </Suspense>
      <Suspense fallback={<div Loading team stats...</div>}>
        <TeamStats />
      </Suspense>
    </div>
  );
}

async function AnalyticsPanel() {
  const analytics = await getAnalytics();
  return <Analytics data={analytics} />;
}

async function TeamStats() {
  const stats = await getTeamStats();
  return <TeamStatsPanel stats={stats} />;
}
```

## 🎯 高级路由功能

### 1. 路由处理程序

```typescript
// app/api/posts/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const page = searchParams.get('page') || '1';
  const limit = searchParams.get('limit') || '10';

  const posts = await getPosts({
    page: parseInt(page),
    limit: parseInt(limit),
  });

  return NextResponse.json(posts);
}

export async function POST(request: NextRequest) {
  const body = await request.json();

  const post = await createPost(body);

  return NextResponse.json(post, { status: 201 });
}

// app/api/posts/[id]/route.ts
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const post = await getPostById(params.id);

  if (!post) {
    return NextResponse.json(
      { error: 'Post not found' },
      { status: 404 }
    );
  }

  return NextResponse.json(post);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const body = await request.json();

  const post = await updatePost(params.id, body);

  return NextResponse.json(post);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  await deletePost(params.id);

  return NextResponse.json({ success: true });
}
```

### 2. 中间件

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // 路径保护
  if (request.nextUrl.pathname.startsWith('/dashboard')) {
    const token = request.cookies.get('auth-token')?.value;

    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url));
    }
  }

  // 地理重定向
  const country = request.geo?.country;
  if (country === 'CN') {
    return NextResponse.redirect(new URL('/cn', request.url));
  }

  // A/B测试
  const variant = Math.random() > 0.5 ? 'A' : 'B';
  const response = NextResponse.next();
  response.cookies.set('ab-test-variant', variant);

  // 缓存控制
  response.headers.set('Cache-Control', 'public, max-age=3600');

  return response;
}

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/api/:path*',
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
```

### 3. 生成静态页面

```typescript
// app/blog/[slug]/page.tsx
export async function generateStaticParams() {
  const posts = await getAllPosts();

  return posts.map((post) => ({
    slug: post.slug,
  }));
}

export async function generateMetadata({
  params,
}: {
  params: { slug: string };
}) {
  const post = await getPostBySlug(params.slug);

  return {
    title: post.title,
    description: post.excerpt,
  };
}
```

## 🚨 性能优化

### 1. 预渲染策略

```typescript
// app/layout.tsx
import { preload } from 'react-dom';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // 预加载重要路由
  preload('/dashboard');
  preload('/settings');

  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

// app/page.tsx
import Link from 'next/link';

export default function HomePage() {
  return (
    <div>
      <h1>Home</h1>
      <Link
        href="/dashboard"
        prefetch={true} // 预取链接
      >
        Dashboard
      </Link>
    </div>
  );
}
```

### 2. 缓存优化

```typescript
// app/api/data/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  const data = await fetchData();

  const response = NextResponse.json(data);

  // 设置缓存头
  response.headers.set('Cache-Control', 'public, max-age=3600');
  response.headers.set('CDN-Cache-Control', 'public, max-age=3600');

  return response;
}

// 使用数据缓存
async function getCachedData(key: string) {
  const cached = await cache.get(key);
  if (cached) {
    return cached;
  }

  const data = await fetchData();
  await cache.set(key, data, { ttl: 3600 });

  return data;
}
```

## 🎯 总结

Next.js 15 的 App Router 提供了强大的路由和渲染能力，通过合理使用这些高级功能，可以构建出性能优异、用户体验出色的现代Web应用。

### 关键要点：

1. **路由系统**：文件系统路由、动态路由、并行路由、拦截路由
2. **布局模式**：条件布局、模板布局、错误处理布局
3. **数据获取**：Server Components、客户端获取、流式渲染
4. **路由功能**：路由处理程序、中间件、静态生成
5. **性能优化**：预渲染、缓存策略、预取机制

对于从PHP转向Next.js的开发者来说，App Router 提供了更加现代化和灵活的开发体验，同时保持了服务端渲染的优势。通过掌握这些高级用法，可以构建出更加复杂和强大的Web应用。