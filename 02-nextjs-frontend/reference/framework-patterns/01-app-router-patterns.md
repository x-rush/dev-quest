# Next.js 16 App Router 实战模式精要

> **文档简介**: Next.js 16 App Router 完整指南，涵盖文件系统路由、动态路由、并行路由、拦截路由、中间件、路由保护等现代路由技术

> **目标读者**: 具备Next.js基础的中高级开发者，需要掌握现代路由架构的前端工程师

> **前置知识**: Next.js 16基础、React 19组件概念、TypeScript 7、文件系统、HTTP协议

> **预计时长**: 6-10小时

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `framework-patterns` |
| **难度** | ⭐⭐⭐ (精通)|
| **标签** | `#app-router` `#routing` `#middleware` `#parallel-routes` `#intercepting-routes` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 📚 概述

Next.js 16 的 App Router 是革命性的路由系统，基于 React Server Components 构建了全新的应用架构。本指南深入探讨 App Router 的实战模式、高级特性和企业级应用的最佳实践。

## 🏗️ App Router 架构基础

### 文件系统路由约定

**基于文件夹结构的智能路由生成**

```typescript
// types/app-router.ts
import { ReactNode } from 'react';

// 路由段配置
export interface RouteSegmentConfig {
  // 基础配置
  segment: string;
  type: 'page' | 'layout' | 'route' | 'template' | 'loading' | 'error' | 'not-found';

  // 动态配置
  dynamic?: 'auto' | 'force-dynamic' | 'error' | 'force-static';
  revalidate?: number | false;

  // 元数据配置
  metadata?: {
    title?: string;
    description?: string;
    keywords?: string[];
    openGraph?: Record<string, any>;
  };

  // 缓存配置
  cache?: {
    tags?: string[];
    ttl?: number;
  };
}

// 路由参数类型
export interface RouteParams {
  [key: string]: string | string[];
}

// 搜索参数类型
export interface SearchParams {
  [key: string]: string | string[] | undefined;
}

// 页面属性接口
export interface PageProps {
  params: RouteParams;
  searchParams: SearchParams;
}

// 布局属性接口
export interface LayoutProps {
  children: ReactNode;
  params?: RouteParams;
  modal?: ReactNode;
}

// 模板属性接口
export interface TemplateProps {
  children: ReactNode;
  params?: RouteParams;
}
```

**标准项目结构示例**

```
app/
├── layout.tsx                    # 🏠 根布局 (HTML结构、全局样式、元数据)
├── page.tsx                      # 🏠 首页 (/)
├── loading.tsx                   # 📄 全局加载UI
├── error.tsx                     # ❌ 全局错误边界
├── not-found.tsx                 # 🔍 404页面
├── template.tsx                  # 🎨 根模板 (状态保持)
│
├── (marketing)/                  # 📢 路由组 - 不影响URL的组织
│   ├── layout.tsx                # 📱 市场营销布局
│   ├── page.tsx                  # 🏠 首页 (/)
│   ├── loading.tsx               # 📄 营销页面加载
│   ├── about/
│   │   ├── page.tsx              # 📄 关于页面 (/about)
│   │   └── team/
│   │       └── page.tsx          # 👥 团队页面 (/about/team)
│   └── contact/
│       └── page.tsx              # 📞 联系页面 (/contact)
│
├── (auth)/                       # 🔐 认证路由组
│   ├── layout.tsx                # 🎨 认证布局 (无导航)
│   ├── login/
│   │   ├── page.tsx              # 🔑 登录页面 (/login)
│   │   └── error.tsx             # ❌ 登录错误处理
│   ├── register/
│   │   └── page.tsx              # 📝 注册页面 (/register)
│   └── reset-password/
│       └── page.tsx              # 🔒 密码重置 (/reset-password)
│
├── dashboard/                    # 📊 仪表板模块
│   ├── layout.tsx                # 📱 仪表板布局 (侧边栏、顶部导航)
│   ├── page.tsx                  # 📊 仪表板首页 (/dashboard)
│   ├── loading.tsx               # 📄 仪表板加载状态
│   ├── error.tsx                 # ❌ 仪表板错误处理
│   ├── settings/
│   │   ├── page.tsx              # ⚙️ 设置页面 (/dashboard/settings)
│   │   ├── profile/
│   │   │   └── page.tsx          # 👤 个人资料 (/dashboard/settings/profile)
│   │   └── security/
│   │       └── page.tsx          # 🔒 安全设置 (/dashboard/settings/security)
│   └── analytics/
│       ├── page.tsx              # 📈 分析概览 (/dashboard/analytics)
│       ├── @reports/             # 📊 并行路由 - 报告插槽
│       │   ├── page.tsx          # 📄 默认报告
│       │   ├── sales/
│       │   │   └── page.tsx      # 💰 销售报告 (/dashboard/analytics/sales)
│       │   └── traffic/
│       │       └── page.tsx      # 🚗 流量报告 (/dashboard/analytics/traffic)
│       └── @modal/               # 🪟 拦截路由 - 模态框插槽
│           └── (..)report/
│               └── [id]/
│                   └── page.tsx  # 📄 报告详情模态框
│
├── blog/                         # 📝 博客模块
│   ├── layout.tsx                # 📱 博客布局
│   ├── page.tsx                  # 📝 博客列表 (/blog)
│   ├── [slug]/
│   │   ├── page.tsx              # 📄 博客文章 (/blog/[slug])
│   │   ├── loading.tsx           # 📄 文章加载状态
│   │   ├── error.tsx             # ❌ 文章错误处理
│   │   └── edit/
│   │       └── page.tsx          # ✏️ 编辑文章 (/blog/[slug]/edit)
│   ├── tag/
│   │   └── [tag]/
│   │       └── page.tsx          # 🏷️ 标签页面 (/blog/tag/[tag])
│   └── feed.xml                  # 📡 RSS Feed (Route Handler)
│
├── shop/                         # 🛒 电商模块
│   ├── layout.tsx                # 📱 商店布局
│   ├── page.tsx                  # 🏪 商店首页 (/shop)
│   ├── products/
│   │   ├── page.tsx              # 📦 产品列表 (/shop/products)
│   │   ├── [category]/
│   │   │   ├── page.tsx          # 📂 分类页面 (/shop/products/[category])
│   │   │   └── [id]/
│   │   │       └── page.tsx      # 📄 产品详情 (/shop/products/[category]/[id])
│   │   └── search/
│   │       └── page.tsx          # 🔍 产品搜索 (/shop/products/search)
│   └── cart/
│       ├── page.tsx              # 🛒 购物车 (/shop/cart)
│       └── checkout/
│           └── page.tsx          # 💳 结账页面 (/shop/cart/checkout)
│
├── api/                          # 🔌 API 路由
│   ├── auth/
│   │   ├── login/
│   │   │   └── route.ts          # 🔐 登录API (POST /api/auth/login)
│   │   ├── logout/
│   │   │   └── route.ts          # 🚪 登出API (POST /api/auth/logout)
│   │   └── register/
│   │       └── route.ts          # 📝 注册API (POST /api/auth/register)
│   ├── users/
│   │   ├── route.ts              # 👥 用户列表API (GET /api/users)
│   │   └── [id]/
│   │       ├── route.ts          # 👤 用户详情API (GET /api/users/[id])
│   │       └── avatar/
│   │           └── route.ts      # 🖼️ 用户头像API
│   └── posts/
│       ├── route.ts              # 📝 文章列表API (GET /api/posts)
│       └── [id]/
│           ├── route.ts          # 📄 文章详情API
│           └── comments/
│               └── route.ts      # 💬 评论API
│
└── globals.css                   # 🎨 全局样式
└── layout.tsx                    # 🏠 根布局 (重复，实际只存在一个)
```

## 🏠 根布局与模板系统

### 高级根布局配置

**企业级根布局实现**

```tsx
// app/layout.tsx
import type { Metadata, Viewport } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/next';
import { Suspense } from 'react';
import { AppProvider } from '@/components/providers/app-provider';
import { ThemeProvider } from '@/components/providers/theme-provider';
import { AuthProvider } from '@/components/providers/auth-provider';
import { ErrorBoundary } from '@/components/error/error-boundary';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { GlobalErrorBoundary } from '@/components/error/global-error-boundary';
import '@/styles/globals.css';

// 字体配置
const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
});

// 视口配置
export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0a0a0a' },
  ],
};

// 元数据配置
export const metadata: Metadata = {
  // 基础元数据
  title: {
    default: 'Dev Quest - 企业级开发学习平台',
    template: '%s | Dev Quest',
  },
  description: '现代化的全栈开发学习平台，涵盖Go、Next.js、React Native等技术栈，提供企业级实战项目和学习路径。',
  keywords: [
    '全栈开发',
    'Go语言',
    'Next.js',
    'React',
    'TypeScript',
    '企业级应用',
    '实战项目',
    '编程学习',
  ],
  authors: [{ name: 'Dev Quest Team', url: 'https://dev-quest.com' }],
  creator: 'Dev Quest Team',
  publisher: 'Dev Quest',

  // 搜索引擎优化
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

  // Open Graph
  openGraph: {
    type: 'website',
    locale: 'zh_CN',
    url: 'https://dev-quest.com',
    siteName: 'Dev Quest',
    title: 'Dev Quest - 企业级开发学习平台',
    description: '现代化的全栈开发学习平台，提供企业级实战项目和学习路径。',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Dev Quest - 企业级开发学习平台',
      },
      {
        url: '/og-image-square.png',
        width: 800,
        height: 800,
        alt: 'Dev Quest Logo',
      },
    ],
  },

  // Twitter Card
  twitter: {
    card: 'summary_large_image',
    title: 'Dev Quest - 企业级开发学习平台',
    description: '现代化的全栈开发学习平台，提供企业级实战项目和学习路径。',
    images: ['/twitter-image.png'],
    creator: '@devquest',
  },

  // 应用程序元数据
  applicationName: 'Dev Quest',
  category: 'education',
  classification: 'educational platform',

  // 验证标签（Bing 无专用键，需经 other 写原始 meta 名，生成 <meta name="msvalidate.01">）
  verification: {
    google: 'your-google-verification-code',
    yandex: 'your-yandex-verification-code',
    other: { 'msvalidate.01': 'your-bing-verification-code' },
  },

  // 图标
  icons: {
    icon: [
      { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
    ],
    apple: [
      { url: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' },
    ],
    other: [
      { rel: 'mask-icon', url: '/safari-pinned-tab.svg', color: '#5bbad5' },
    ],
  },

  // Manifest
  manifest: '/site.webmanifest',

  // 其他
  other: {
    'msapplication-TileColor': '#2b5797',
    'theme-color': '#ffffff',
  },
};

// 根布局组件
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="zh-CN"
      suppressHydrationWarning
      className={`${inter.variable} ${jetbrainsMono.variable}`}
    >
      <head>
        {/* 预连接关键资源 */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />

        {/* DNS 预解析 */}
        <link rel="dns-prefetch" href="//api.github.com" />
        <link rel="dns-prefetch" href="//vercel.com" />

        {/* 关键资源预加载 */}
        <link rel="preload" href="/fonts/inter-v12-latin-regular.woff2" as="font" type="font/woff2" crossOrigin="" />

        {/* 安全头部 */}
        <meta httpEquiv="X-Content-Type-Options" content="nosniff" />
        <meta httpEquiv="X-Frame-Options" content="DENY" />
        <meta httpEquiv="X-XSS-Protection" content="1; mode=block" />
        <meta httpEquiv="Referrer-Policy" content="strict-origin-when-cross-origin" />

        {/* 性能优化 */}
        <meta name="format-detection" content="telephone=no" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
      </head>

      <body
        className="min-h-screen bg-background font-sans antialiased"
        suppressHydrationWarning
      >
        <ErrorBoundary fallback={<GlobalErrorBoundary />}>
          <Suspense fallback={<LoadingSpinner />}>
            <AppProvider>
              <ThemeProvider
                attribute="class"
                defaultTheme="system"
                enableSystem
                disableTransitionOnChange
              >
                <AuthProvider>
                  <div className="relative flex min-h-screen flex-col">
                    <Suspense fallback={<div>Loading navigation...</div>}>
                      <Navigation />
                    </Suspense>

                    <main className="flex-1">
                      <ErrorBoundary>
                        <Suspense fallback={<PageLoadingSkeleton />}>
                          {children}
                        </Suspense>
                      </ErrorBoundary>
                    </main>

                    <Suspense fallback={<div>Loading footer...</div>}>
                      <Footer />
                    </Suspense>
                  </div>

                  <Toaster />
                  <CommandPalette />
                </AuthProvider>
              </ThemeProvider>
            </AppProvider>
          </Suspense>
        </ErrorBoundary>

        {/* 分析工具 */}
        {process.env.NODE_ENV === 'production' && (
          <>
            <Analytics />
            <SpeedInsights />
          </>
        )}
      </body>
    </html>
  );
}

// 错误边界组件：包含 onClick 事件处理器，必须放在带 'use client' 的
// 独立客户端文件中，不能内联在服务端布局文件里（布局默认是 Server Component）
// app/components/error/global-error-boundary.tsx
'use client';

export function GlobalErrorBoundary() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-red-600 mb-4">
          系统错误
        </h1>
        <p className="text-gray-600 mb-6">
          抱歉，系统遇到了意外错误。请刷新页面重试。
        </p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          刷新页面
        </button>
      </div>
    </div>
  );
}

// 页面加载骨架屏
function PageLoadingSkeleton() {
  return (
    <div className="min-h-screen animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-1/4 mb-8" />
      <div className="space-y-4">
        <div className="h-4 bg-gray-200 rounded" />
        <div className="h-4 bg-gray-200 rounded w-5/6" />
        <div className="h-4 bg-gray-200 rounded w-4/6" />
      </div>
    </div>
  );
}
```

### 模板系统实现

**状态保持的模板组件**

```tsx
// app/template.tsx
'use client';

import { ReactNode, useEffect, useRef } from 'react';
import { usePathname } from 'next/navigation';

interface TemplateProps {
  children: ReactNode;
}

export default function Template({ children }: TemplateProps) {
  const pathname = usePathname();
  const previousPathname = useRef(pathname);

  useEffect(() => {
    // 路由变化时的逻辑
    if (previousPathname.current !== pathname) {
      // 页面切换动画
      document.body.classList.add('page-transitioning');

      setTimeout(() => {
        document.body.classList.remove('page-transitioning');
      }, 300);

      // 重置滚动位置
      window.scrollTo(0, 0);

      // 更新上一个路径
      previousPathname.current = pathname;
    }
  }, [pathname]);

  return (
    <div className="template-container">
      {/* 页面过渡效果 */}
      <style jsx global>{`
        .page-transitioning {
          opacity: 0.8;
          transform: translateY(10px);
          transition: all 0.3s ease-in-out;
        }
      `}</style>

      {/* 保持状态的内容 */}
      <div className="template-content">
        {children}
      </div>

      {/* 全局通知组件 */}
      <NotificationCenter />
    </div>
  );
}

// 通知中心组件
function NotificationCenter() {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {/* 通知组件将通过 Context API 渲染 */}
    </div>
  );
}
```

## 🔀 动态路由与参数处理

### 高级动态路由实现

**类型安全的动态路由处理**

```tsx
// app/blog/[slug]/page.tsx
import { notFound, permanentRedirect } from 'next/navigation';
import { Metadata } from 'next';
import { cache } from 'react';
import { BlogPostContent } from '@/components/blog/blog-post-content';
import { BlogPostHeader } from '@/components/blog/blog-post-header';
import { BlogPostSidebar } from '@/components/blog/blog-post-sidebar';
import { CommentSection } from '@/components/blog/comment-section';
import { RelatedPosts } from '@/components/blog/related-posts';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { StructuredData } from '@/components/seo/structured-data';

// 动态路由属性接口
interface BlogPostPageProps {
  // Next.js 16：params 与 searchParams 均为 Promise，需 await 后使用
  params: Promise<{
    slug: string;
  }>;
  searchParams: Promise<{
    preview?: string;
    ref?: string;
    utm_source?: string;
    utm_medium?: string;
    utm_campaign?: string;
  }>;
}

// 缓存的博客文章获取函数
const getBlogPost = cache(async (slug: string, preview?: boolean) => {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api';
  const endpoint = preview
    ? `${baseUrl}/blog/posts/${slug}?preview=true`
    : `${baseUrl}/blog/posts/${slug}`;

  const response = await fetch(endpoint, {
    next: {
      revalidate: preview ? 0 : 3600, // 预览模式不缓存
      tags: [`blog-post-${slug}`],
    },
  });

  if (!response.ok) {
    if (response.status === 404) {
      return null;
    }
    throw new Error(`Failed to fetch blog post: ${response.statusText}`);
  }

  return response.json();
});

// 获取相关文章
const getRelatedPosts = cache(async (slug: string, category?: string) => {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api';
  const response = await fetch(`${baseUrl}/blog/posts/related/${slug}`, {
    next: {
      revalidate: 1800, // 30分钟
      tags: [`related-posts-${slug}`],
    },
  });

  if (!response.ok) {
    return [];
  }

  return response.json();
});

// 生成静态参数
export async function generateStaticParams(): Promise<{ slug: string }[]> {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api';
    const response = await fetch(`${baseUrl}/blog/posts`, {
      next: {
        revalidate: 86400, // 24小时
        tags: ['blog-posts-list'],
      },
    });

    if (!response.ok) {
      console.error('Failed to fetch blog posts for static generation');
      return [];
    }

    const posts = await response.json();

    return posts.map((post: { slug: string }) => ({
      slug: post.slug,
    }));
  } catch (error) {
    console.error('Error generating static params:', error);
    return [];
  }
}

// 生成元数据
export async function generateMetadata({
  params,
  searchParams
}: BlogPostPageProps): Promise<Metadata> {
  const { slug } = await params;
  const { preview } = await searchParams;
  const post = await getBlogPost(slug, preview === 'true');

  if (!post) {
    return {
      title: '文章未找到',
      description: '请求的文章不存在或已被删除。',
    };
  }

  const { title, excerpt, featuredImage, author, publishedAt, category } = post;
  const publishedDate = new Date(publishedAt).toISOString();

  return {
    title,
    description: excerpt,
    keywords: [category?.name, author?.name, post.tags?.join(', ')].filter(Boolean),
    authors: [{ name: author?.name }],
    creator: author?.name,
    // Metadata 顶层没有 publishTime/modifiedTime 字段，文章时间只通过 openGraph 的
    // publishedTime/modifiedTime 表达（见下方 openGraph.type: 'article'）

    openGraph: {
      title,
      description: excerpt,
      type: 'article',
      publishedTime: publishedDate,
      modifiedTime: post.updatedAt ? new Date(post.updatedAt).toISOString() : publishedDate,
      authors: [author?.name].filter(Boolean),
      section: category?.name,
      tags: post.tags || [],
      images: featuredImage ? [
        {
          url: featuredImage.url,
          width: featuredImage.width || 1200,
          height: featuredImage.height || 630,
          alt: featuredImage.alt || title,
        },
      ] : [],
    },

    twitter: {
      card: 'summary_large_image',
      title,
      description: excerpt,
      images: featuredImage ? [featuredImage.url] : [],
      creator: `@${author?.twitter || 'devquest'}`,
    },

    alternates: {
      canonical: `https://dev-quest.com/blog/${slug}`,
      languages: {
        'zh-CN': `https://dev-quest.com/blog/${slug}`,
        'en': `https://dev-quest.com/en/blog/${slug}`,
      },
    },
  };
}

// 博客文章页面组件
export default async function BlogPostPage({
  params,
  searchParams
}: BlogPostPageProps) {
  const { slug } = await params;
  const { preview } = await searchParams;

  // 获取文章数据
  const post = await getBlogPost(slug, preview === 'true');

  if (!post) {
    notFound();
  }

  // 检查文章是否已发布（非预览模式）
  if (!preview && !post.published) {
    notFound();
  }

  // 处理永久重定向
  if (post.redirectTo) {
    permanentRedirect(post.redirectTo);
  }

  // 获取相关文章
  const relatedPosts = await getRelatedPosts(slug, post.category?.slug);

  // 面包屑导航
  const breadcrumbItems = [
    { label: '首页', href: '/' },
    { label: '博客', href: '/blog' },
    { label: post.category?.name, href: `/blog/category/${post.category?.slug}` },
    { label: post.title, href: `/blog/${slug}` },
  ].filter(Boolean);

  return (
    <>
      {/* 结构化数据 */}
      <StructuredData
        type="BlogPosting"
        data={{
          headline: post.title,
          description: post.excerpt,
          image: post.featuredImage?.url,
          datePublished: new Date(post.publishedAt).toISOString(),
          dateModified: new Date(post.updatedAt).toISOString(),
          author: {
            type: 'Person',
            name: post.author?.name,
            url: post.author?.website,
          },
          publisher: {
            type: 'Organization',
            name: 'Dev Quest',
            logo: {
              type: 'ImageObject',
              url: 'https://dev-quest.com/logo.png',
            },
          },
          mainEntityOfPage: `https://dev-quest.com/blog/${slug}`,
        }}
      />

      <article className="min-h-screen">
        <div className="container mx-auto px-4 py-8">
          {/* 面包屑导航 */}
          <Breadcrumb items={breadcrumbItems} />

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 mt-8">
            {/* 主要内容区域 */}
            <div className="lg:col-span-3">
              {/* 文章头部 */}
              <BlogPostHeader post={post} preview={preview} />

              {/* 文章内容 */}
              <BlogPostContent
                content={post.content}
                tableOfContents={post.tableOfContents}
              />

              {/* 评论区 */}
              <div className="mt-12">
                <CommentSection
                  postId={post.id}
                  slug={slug}
                  initialComments={post.comments || []}
                />
              </div>

              {/* 相关文章 */}
              {relatedPosts.length > 0 && (
                <div className="mt-16">
                  <RelatedPosts posts={relatedPosts} />
                </div>
              )}
            </div>

            {/* 侧边栏 */}
            <aside className="lg:col-span-1">
              <BlogPostSidebar
                post={post}
                relatedPosts={relatedPosts}
                tableOfContents={post.tableOfContents}
              />
            </aside>
          </div>
        </div>
      </article>
    </>
  );
}

// 错误与加载兜底不能作为页面文件的命名导出（next build 类型检查会报
// not a valid Page export field），必须使用独立文件约定 error.tsx / loading.tsx

// app/blog/[slug]/error.tsx
'use client';

export default function BlogError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-red-600 mb-4">
          文章加载失败
        </h1>
        <p className="text-gray-600 mb-6">
          抱歉，无法加载这篇文章。请稍后重试。
        </p>
        <p className="text-sm text-gray-500 mb-6">
          错误详情: {error.message}
        </p>
        <button
          onClick={() => reset()}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          重试
        </button>
        <a
          href="/blog"
          className="ml-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          返回博客列表
        </a>
      </div>
    </div>
  );
}

// app/blog/[slug]/loading.tsx
export default function BlogLoading() {
  return (
    <div className="min-h-screen">
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-3/4 mb-4" />
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-8" />

          <div className="space-y-4">
            {[...Array(10)].map((_, i) => (
              <div key={i} className="h-4 bg-gray-200 rounded" />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
```

### 并行路由实现

**复杂的仪表板并行路由**

```tsx
// app/dashboard/layout.tsx
import { ReactNode } from 'react';
import { DashboardSidebar } from '@/components/dashboard/dashboard-sidebar';
import { DashboardHeader } from '@/components/dashboard/dashboard-header';
import { NotificationCenter } from '@/components/dashboard/notification-center';
import { ErrorBoundary } from '@/components/error/error-boundary';

interface DashboardLayoutProps {
  children: ReactNode;
  analytics: ReactNode;
  team: ReactNode;
  reports?: ReactNode;
  modal?: ReactNode;
}

export default function DashboardLayout({
  children,
  analytics,
  team,
  reports,
  modal,
}: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* 侧边栏 */}
      <DashboardSidebar />

      <div className="lg:pl-64">
        {/* 顶部导航 */}
        <DashboardHeader />

        {/* 主内容区域 */}
        <div className="flex">
          <main className="flex-1 p-6">
            <ErrorBoundary>
              {children}
            </ErrorBoundary>
          </main>

          {/* 右侧面板 - 并行路由 */}
          <aside className="w-80 border-l border-gray-200 bg-white p-6 space-y-6">
            <ErrorBoundary>
              {/* 分析面板 */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  实时分析
                </h3>
                {analytics}
              </div>

              {/* 团队面板 */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  团队概览
                </h3>
                {team}
              </div>

              {/* 报告面板 */}
              {reports && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    报告中心
                  </h3>
                  {reports}
                </div>
              )}
            </ErrorBoundary>
          </aside>
        </div>
      </div>

      {/* 通知中心 */}
      <NotificationCenter />

      {/* 模态框插槽 */}
      {modal}
    </div>
  );
}

// app/dashboard/@analytics/page.tsx
import { Suspense } from 'react';
import { AnalyticsOverview } from '@/components/analytics/analytics-overview';
import { TrafficChart } from '@/components/analytics/traffic-chart';
import { UserMetrics } from '@/components/analytics/user-metrics';
import { RevenueChart } from '@/components/analytics/revenue-chart';

export default function AnalyticsSlot() {
  return (
    <div className="space-y-6">
      <Suspense fallback={<div className="h-32 bg-gray-200 rounded animate-pulse" />}>
        <AnalyticsOverview />
      </Suspense>

      <div className="grid grid-cols-1 gap-6">
        <Suspense fallback={<div className="h-48 bg-gray-200 rounded animate-pulse" />}>
          <TrafficChart />
        </Suspense>

        <Suspense fallback={<div className="h-48 bg-gray-200 rounded animate-pulse" />}>
          <UserMetrics />
        </Suspense>
      </div>

      <Suspense fallback={<div className="h-64 bg-gray-200 rounded animate-pulse" />}>
        <RevenueChart />
      </Suspense>
    </div>
  );
}

// app/dashboard/@team/page.tsx
import { Suspense } from 'react';
import { TeamOverview } from '@/components/team/team-overview';
import { TeamPerformance } from '@/components/team/team-performance';
import { RecentActivities } from '@/components/team/recent-activities';

export default function TeamSlot() {
  return (
    <div className="space-y-6">
      <Suspense fallback={<div className="h-32 bg-gray-200 rounded animate-pulse" />}>
        <TeamOverview />
      </Suspense>

      <Suspense fallback={<div className="h-48 bg-gray-200 rounded animate-pulse" />}>
        <TeamPerformance />
      </Suspense>

      <Suspense fallback={<div className="h-64 bg-gray-200 rounded animate-pulse" />}>
        <RecentActivities />
      </Suspense>
    </div>
  );
}

// app/dashboard/@reports/page.tsx
import { Suspense } from 'react';
import { ReportsList } from '@/components/reports/reports-list';
import { QuickStats } from '@/components/reports/quick-stats';

export default function ReportsSlot() {
  return (
    <div className="space-y-6">
      <Suspense fallback={<div className="h-24 bg-gray-200 rounded animate-pulse" />}>
        <QuickStats />
      </Suspense>

      <Suspense fallback={<div className="h-96 bg-gray-200 rounded animate-pulse" />}>
        <ReportsList />
      </Suspense>
    </div>
  );
}
```

## 🪟 拦截路由与模态框

### 高级拦截路由实现

**模态框和覆盖层的拦截路由**

```tsx
// app/dashboard/@modal/(..)reports/[id]/page.tsx
import { notFound } from 'next/navigation';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ReportDetails } from '@/components/reports/report-details';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ReportModalProps {
  // Next.js 16：params 与 searchParams 均为 Promise
  params: Promise<{
    id: string;
  }>;
  searchParams: Promise<{
    view?: string;
    tab?: string;
  }>;
}

export default async function ReportModal({
  params,
  searchParams
}: ReportModalProps) {
  const { id } = await params;
  const report = await getReport(id);

  if (!report) {
    notFound();
  }

  const { view = 'overview', tab = 'summary' } = await searchParams;

  return (
    <Dialog open={true}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="text-xl">
              {report.title}
            </DialogTitle>
            <Button
              variant="ghost"
              size="sm"
              asChild
            >
              <a href="/dashboard">
                <X className="h-4 w-4" />
              </a>
            </Button>
          </div>
        </DialogHeader>

        <div className="mt-6">
          <ReportDetails
            report={report}
            initialView={view}
            initialTab={tab}
          />
        </div>
      </DialogContent>
    </Dialog>
  );
}

// 获取报告数据
async function getReport(id: string) {
  const response = await fetch(`${process.env.API_URL}/reports/${id}`, {
    next: {
      revalidate: 300,
      tags: [`report-${id}`],
    },
  });

  if (!response.ok) {
    return null;
  }

  return response.json();
}

// app/feed/page.tsx - 包含拦截路由的页面
import Link from 'next/link';
import Image from 'next/image';
import { PhotoGrid } from '@/components/photo/photo-grid';
import { PhotoModal } from '@/components/photo/photo-modal';

interface Photo {
  id: string;
  title: string;
  thumbnail: string;
  url: string;
  description: string;
  author: {
    name: string;
    avatar: string;
  };
  likes: number;
  comments: number;
}

export default async function FeedPage() {
  const photos = await getPhotos();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Photo Feed</h1>

      {/* 照片网格 */}
      <PhotoGrid photos={photos} />

      {/* 拦截路由插槽 */}
      <PhotoModal />
    </div>
  );
}

async function getPhotos(): Promise<Photo[]> {
  const response = await fetch(`${process.env.API_URL}/photos`, {
    next: {
      revalidate: 600,
      tags: ['photos-feed'],
    },
  });

  return response.json();
}

// components/photo/photo-modal.tsx
'use client';

import { usePathname, useRouter } from 'next/navigation';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { PhotoDetails } from './photo-details';

interface PhotoModalProps {
  children: React.ReactNode;
}

export function PhotoModal({ children }: PhotoModalProps) {
  const pathname = usePathname();
  const router = useRouter();

  // 检查是否是照片详情页面
  const isPhotoModal = pathname.startsWith('/photo/');

  if (!isPhotoModal) {
    return <>{children}</>;
  }

  const photoId = pathname.split('/')[2];

  const handleClose = () => {
    router.back();
  };

  return (
    <>
      {children}
      <Dialog open={true} onOpenChange={(open) => !open && handleClose()}>
        <DialogContent className="max-w-4xl">
          <PhotoDetails photoId={photoId} />
        </DialogContent>
      </Dialog>
    </>
  );
}
```

## 🔧 代理（Proxy）与路由保护

### 企业级代理（Proxy）实现

**复杂的认证和授权中间件**

```typescript
// proxy.ts（Next.js 16：由 middleware.ts 更名，运行于 Node.js runtime）
import { NextResponse, type NextRequest } from 'next/server';
import { jwtVerify } from 'jose';
import { createMiddleware } from 'next-intl/middleware';
import { getPathname } from '@/lib/i18n/navigation';

// JWT 密钥
const jwtSecret = new TextEncoder().encode(
  process.env.JWT_SECRET || 'your-secret-key'
);

// 用户会话接口
interface UserSession {
  id: string;
  email: string;
  role: string;
  permissions: string[];
  locale: string;
}

// 中间件配置
const middlewareConfig = {
  // 公开路由
  publicRoutes: [
    '/',
    '/login',
    '/register',
    '/forgot-password',
    '/reset-password',
    '/verify-email',
    '/api/auth/login',
    '/api/auth/register',
    '/api/auth/forgot-password',
    '/api/auth/reset-password',
    '/api/auth/verify-email',
    '/manifest.json',
    '/robots.txt',
    '/sitemap.xml',
    '/favicon.ico',
    '/_next',
    '/api/health',
  ],

  // 需要认证的路由
  protectedRoutes: [
    '/dashboard',
    '/profile',
    '/settings',
    '/admin',
    '/api/user',
    '/api/admin',
    '/api/reports',
  ],

  // 角色限制路由
  roleRoutes: {
    '/admin': ['admin'],
    '/api/admin': ['admin'],
    '/dashboard/analytics': ['admin', 'manager'],
    '/dashboard/reports': ['admin', 'manager', 'analyst'],
  },

  // 地理重定向配置
  geoRedirects: {
    '/': {
      default: '/en',
      CN: '/zh',
      US: '/en',
      JP: '/ja',
    },
  },

  // 速率限制配置
  rateLimits: {
    '/api/auth/login': { windowMs: 15 * 60 * 1000, maxRequests: 5 },
    '/api/auth/register': { windowMs: 60 * 60 * 1000, maxRequests: 3 },
    '/api/user': { windowMs: 15 * 60 * 1000, maxRequests: 100 },
    '/api/admin': { windowMs: 15 * 60 * 1000, maxRequests: 200 },
  },
};

// 主要代理函数
export default async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const response = NextResponse.next();

  try {
    // 1. CORS 处理
    const corsResponse = handleCORS(request, response);
    if (corsResponse) return corsResponse;

    // 2. 国际化中间件
    const i18nResponse = await handleInternationalization(request);
    if (i18nResponse) return i18nResponse;

    // 3. 速率限制检查
    const rateLimitResponse = await checkRateLimit(request);
    if (rateLimitResponse) return rateLimitResponse;

    // 4. 地理位置重定向
    const geoResponse = await handleGeoRedirect(request);
    if (geoResponse) return geoResponse;

    // 5. 认证检查
    const authResponse = await handleAuthentication(request);
    if (authResponse) return authResponse;

    // 6. 角色权限检查
    const roleResponse = await checkRolePermissions(request);
    if (roleResponse) return roleResponse;

    // 7. 维护模式检查
    const maintenanceResponse = await checkMaintenanceMode(request);
    if (maintenanceResponse) return maintenanceResponse;

    // 8. 添加安全头部
    addSecurityHeaders(response);

    // 9. 添加性能头部
    addPerformanceHeaders(response);

    return response;
  } catch (error) {
    console.error('Middleware error:', error);

    // 在出错时返回安全的响应
    return new NextResponse('Internal Server Error', {
      status: 500,
      headers: {
        'Content-Type': 'text/plain',
      },
    });
  }
}

// CORS 处理
function handleCORS(request: NextRequest, response: NextResponse): NextResponse | null {
  const origin = request.headers.get('origin');
  const allowedOrigins = [
    'https://dev-quest.com',
    'https://www.dev-quest.com',
    'https://admin.dev-quest.com',
  ];

  if (origin && allowedOrigins.includes(origin)) {
    response.headers.set('Access-Control-Allow-Origin', origin);
    response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    response.headers.set('Access-Control-Allow-Credentials', 'true');
  }

  // 处理预检请求
  if (request.method === 'OPTIONS') {
    return new NextResponse(null, { status: 200, headers: response.headers });
  }

  return null;
}

// 国际化处理
async function handleInternationalization(request: NextRequest): Promise<NextResponse | null> {
  const i18nMiddleware = createMiddleware({
    locales: ['en', 'zh', 'ja'],
    defaultLocale: 'en',
    localePrefix: 'as-needed',
  });

  // 检查是否是国际化路由
  if (shouldHandleI18n(request.nextUrl.pathname)) {
    return i18nMiddleware(request);
  }

  return null;
}

// 速率限制检查
async function checkRateLimit(request: NextRequest): Promise<NextResponse | null> {
  const pathname = request.nextUrl.pathname;
  const clientIP = getClientIP(request);

  // 查找匹配的速率限制规则
  for (const [path, config] of Object.entries(middlewareConfig.rateLimits)) {
    if (pathname.startsWith(path)) {
      const key = `rate-limit:${clientIP}:${path}`;

      // 这里应该连接到 Redis 或其他存储来跟踪请求计数
      // 简化实现：
      const count = await getRequestCount(key, config.windowMs);

      if (count >= config.maxRequests) {
        return new NextResponse('Too Many Requests', {
          status: 429,
          headers: {
            'Retry-After': String(Math.ceil(config.windowMs / 1000)),
            'X-RateLimit-Limit': String(config.maxRequests),
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': String(Date.now() + config.windowMs),
          },
        });
      }

      break;
    }
  }

  return null;
}

// 地理位置重定向
async function handleGeoRedirect(request: NextRequest): Promise<NextResponse | null> {
  const { pathname } = request.nextUrl;
  const country = request.headers.get('x-vercel-ip-country') // Vercel 地理信息头部;

  if (country && pathname === '/') {
    const redirectPath = middlewareConfig.geoRedirects['/'][country] ||
                      middlewareConfig.geoRedirects['/'].default;

    if (redirectPath && redirectPath !== pathname) {
      const url = new URL(redirectPath, request.url);
      return NextResponse.redirect(url);
    }
  }

  return null;
}

// 认证处理
async function handleAuthentication(request: NextRequest): Promise<NextResponse | null> {
  const { pathname } = request.nextUrl;

  // 检查是否是公开路由
  if (middlewareConfig.publicRoutes.some(route => pathname.startsWith(route))) {
    return null;
  }

  // 检查是否是受保护的路由
  if (middlewareConfig.protectedRoutes.some(route => pathname.startsWith(route))) {
    const token = request.cookies.get('auth-token')?.value;

    if (!token) {
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('redirect', pathname);
      return NextResponse.redirect(loginUrl);
    }

    try {
      const { payload } = await jwtVerify(token, jwtSecret);
      const user = payload as UserSession;

      // 检查用户是否仍然有效
      if (!await isUserValid(user.id)) {
        const loginUrl = new URL('/login', request.url);
        loginUrl.searchParams.set('redirect', pathname);
        loginUrl.searchParams.set('reason', 'invalid-user');
        return NextResponse.redirect(loginUrl);
      }

      // 将用户信息添加到请求头中
      const response = NextResponse.next();
      response.headers.set('x-user-id', user.id);
      response.headers.set('x-user-role', user.role);
      response.headers.set('x-user-locale', user.locale);

      return response;
    } catch (error) {
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('redirect', pathname);
      loginUrl.searchParams.set('reason', 'invalid-token');
      return NextResponse.redirect(loginUrl);
    }
  }

  return null;
}

// 角色权限检查
async function checkRolePermissions(request: NextRequest): Promise<NextResponse | null> {
  const { pathname } = request.nextUrl;
  const userRole = request.headers.get('x-user-role');

  // 检查是否有角色限制
  for (const [path, requiredRoles] of Object.entries(middlewareConfig.roleRoutes)) {
    if (pathname.startsWith(path) && userRole) {
      if (!requiredRoles.includes(userRole)) {
        const unauthorizedUrl = new URL('/unauthorized', request.url);
        unauthorizedUrl.searchParams.set('required', requiredRoles.join(','));
        return NextResponse.redirect(unauthorizedUrl);
      }
    }
  }

  return null;
}

// 维护模式检查
async function checkMaintenanceMode(request: NextRequest): Promise<NextResponse | null> {
  const isMaintenanceMode = process.env.MAINTENANCE_MODE === 'true';

  if (isMaintenanceMode) {
    const { pathname } = request.nextUrl;

    // 允许管理员访问
    const userRole = request.headers.get('x-user-role');
    if (userRole === 'admin') {
      return null;
    }

    // 允许访问健康检查和登录页面
    const allowedPaths = ['/login', '/api/health'];
    if (allowedPaths.includes(pathname)) {
      return null;
    }

    return NextResponse.rewrite(new URL('/maintenance', request.url));
  }

  return null;
}

// 添加安全头部
function addSecurityHeaders(response: NextResponse): void {
  // 内容安全策略
  response.headers.set(
    'Content-Security-Policy',
    "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline' https://vercel.live; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.github.com https://vercel.live;"
  );

  // 其他安全头部
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-XSS-Protection', '1; mode=block');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
}

// 添加性能头部
function addPerformanceHeaders(response: NextResponse): void {
  // 压缩
  response.headers.set('Compression', 'gzip');

  // 缓存控制
  if (response.nextUrl.pathname.startsWith('/api/')) {
    response.headers.set('Cache-Control', 'no-store, no-cache, must-revalidate');
  } else {
    response.headers.set('Cache-Control', 'public, max-age=31536000, immutable');
  }

  // 预加载提示
  response.headers.set('Link', '</api/health>; rel=preconnect');
}

// 工具函数
function getClientIP(request: NextRequest): string {
  return request.ip ||
         request.headers.get('x-forwarded-for')?.split(',')[0] ||
         request.headers.get('x-real-ip') ||
         'unknown';
}

async function getRequestCount(key: string, windowMs: number): Promise<number> {
  // 这里应该连接到 Redis 或其他存储
  // 简化实现：
  return 0;
}

async function isUserValid(userId: string): Promise<boolean> {
  // 检查用户是否仍然有效
  const response = await fetch(`${process.env.API_URL}/users/${userId}/valid`);
  return response.ok;
}

function shouldHandleI18n(pathname: string): boolean {
  // 检查路径是否需要国际化处理
  return !pathname.startsWith('/api/') &&
         !pathname.startsWith('/_next/') &&
         !pathname.includes('.') &&
         pathname !== '/favicon.ico';
}

// 中间件匹配配置
export const config = {
  matcher: [
    /*
     * 匹配所有路径除了:
     * - API 路由 (/api/*)
     * - Next.js 内部路径 (/_next/*)
     * - 静态文件 (/*.*)
     * - favicon.ico
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
```

## 📊 性能优化模式

### 缓存策略与数据预获取

**企业级缓存配置**

```typescript
// lib/cache/strategies.ts
// Next.js 16：unstable_cache 已弃用，改用 "use cache" + cacheLife/cacheTag 显式缓存
import { revalidateTag, cacheLife, cacheTag } from 'next/cache';

// 缓存策略配置（以 cacheLife profile 表达时长）
export const CacheStrategies = {
  // 短期缓存 - 频繁更新的数据
  shortTerm: {
    profile: 'minutes',
    tags: ['short-term'],
  },

  // 中期缓存 - 适度更新的数据
  mediumTerm: {
    profile: 'minutes', // 分钟级
    tags: ['medium-term'],
  },

  // 长期缓存 - 很少变化的数据
  longTerm: {
    profile: 'hours', // 小时级
    tags: ['long-term'],
  },

  // 静态数据 - 基本不变的数据
  static: {
    profile: 'days', // 天级
    tags: ['static'],
  },

  // 实时数据 - 不使用 "use cache"，保持请求时动态渲染
  realtime: {
    profile: null,
    tags: ['realtime'],
  },
};

// 缓存装饰器
export function withCache<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  options: {
    key?: string;
    profile?: string;
    tags?: string[];
  } = {}
): T {
  const cacheKey = options.key || fn.name;
  const profile = options.profile || 'minutes';
  const tags = options.tags || [];

  const cached = async (...args: Parameters<T>): Promise<Awaited<ReturnType<T>>> => {
    'use cache'
    cacheLife(profile);
    cacheTag(cacheKey, ...tags);
    return fn(...args);
  };

  return cached as T;
}

// 数据获取函数
export const fetchUsers = withCache(
  async () => {
    const response = await fetch(`${process.env.API_URL}/users`, {
      next: {
        ...CacheStrategies.mediumTerm,
        tags: ['users'],
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch users');
    }

    return response.json();
  },
  {
    key: 'users',
    profile: 'minutes',
    tags: ['users'],
  }
);

export const fetchUserById = withCache(
  async (id: string) => {
    const response = await fetch(`${process.env.API_URL}/users/${id}`, {
      next: {
        ...CacheStrategies.shortTerm,
        tags: [`user-${id}`],
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch user ${id}`);
    }

    return response.json();
  },
  {
    key: 'user-by-id',
    profile: 'minutes',
    tags: ['user-details'],
  }
);

// 缓存失效函数（Next.js 16：revalidateTag 需传入 cacheLife profile 作为第二参数）
export function invalidateCache(tags: string[]) {
  tags.forEach(tag => revalidateTag(tag, 'max'));
}

// 批量缓存失效
export function invalidateUserCache(userId: string) {
  invalidateCache(['users', `user-${userId}`, 'user-details']);
}

export function invalidatePostCache(slug: string) {
  invalidateCache(['posts', `post-${slug}`, 'blog-list']);
}
```

## 📋 最佳实践清单

路由目录表达 URL 与布局关系，路由组主要帮助组织，不是所有目录都改变地址。先画出列表、详情和登录三条用户路径，验证直接打开、刷新、返回与未登录访问，而不只测试应用内点击。

缓存键和作用域依据数据身份设计，私人数据不能进入不隔离用户的共享缓存。独立数据可以并行获取，有依赖的请求则按顺序或重构接口；预取会额外消耗资源，不是越多越快。认证提示可以在界面层完成，真正读取或修改数据的位置仍要校验权限。

## 📖 总结

App Router 是 Next.js 16 的核心特性，通过本指南我们深入探讨了：

### 核心模式：
1. **文件系统路由**: 基于文件夹结构的智能路由生成
2. **动态路由**: 类型安全的动态参数处理
3. **布局系统**: 灵活的嵌套布局和模板
4. **并行路由**: 同时渲染多个页面组件
5. **拦截路由**: 模态框和覆盖层的优雅实现
6. **中间件**: 请求处理管道的集中管理

### 把“企业级能力”落实到请求与验收

| 需求 | 在 App Router 中先做什么 | 它**不**自动保证什么 | 最小验收 |
|---|---|---|---|
| 动态参数的可靠性 | 在页面或 Route Handler 读取参数后做运行时校验；TypeScript 只描述预期形状 | URL 中的 `id` 真实存在、当前用户有读取权限 | 直接访问合法 ID、非法格式、未知 ID 三个 URL；分别得到数据、4xx 和明确的 not-found 响应。 |
| 缓存与失效 | 为共享数据设计含资源身份的 key/tag；写入成功后只失效受影响的 tag | 私人数据自动按用户隔离，或旧页面不会展示旧账户的数据 | 两个用户依次访问相同路径；登录切换后不得读到前一用户内容。修改一条记录后，列表与详情在约定窗口内都更新。 |
| 认证与授权 | 在实际读写数据的 Server Action、Route Handler 或服务层再次核验身份和资源归属 | 仅靠 middleware 重定向就阻止绕过入口，或界面隐藏按钮就完成授权 | 用无登录、普通用户、资源所有者分别请求同一写接口；记录 401/403/成功的预期。 |
| 性能 | 先测真实页面的请求瀑布、传输体积和 LCP；独立数据可并行获取，图片写明确尺寸 | 预取必然更快，或代码分割自动降低首屏成本 | 以生产构建测试首屏与慢网导航；保存基线，改变预取/图片策略后比较同一指标。 |
| 国际化 | 将 locale 放进 URL、路由段或明确的请求协商策略；文本、日期、数字各按 locale 格式化 | 翻译文件存在就有正确 URL、语言声明和搜索索引 | 直接打开每种语言 URL，检查 `<html lang>`、切换链接、日期格式和 fallback 文案。 |
| SEO | 为每条可索引资源生成对应 metadata；只为真实页面输出结构化数据 | metadata 自动让页面可索引，或所有页面都应公开 | 查看渲染后的 title、description、canonical 和 JSON-LD；未授权或无内容页面不应生成虚假的公开实体。 |

这些是各能力的边界，而不是必须同时安装的清单。第一个项目先完成一个资源的读取、not-found、权限校验和 metadata；缓存、预取、多语言和结构化数据随真实需求逐项加入，并为每项留下验收记录。

### 最佳实践：
用一个真实路径串起路由、数据和错误：直接访问详情页，应得到正确数据或明确的不存在结果；登录状态变化后不能继续读到前一个用户的内容。元数据与无障碍语义随实际页面内容检查。

结构是否合理看新增页面时需要修改多少无关代码，以及加载、错误和权限边界能否独立验证。文件组织和类型检查提供帮助，但不会自动保证安全或性能。

---

## 模式不变量

- **URL 结构由目录约定唯一派生**：路由是文件系统的投影，纯组织性的路由组只影响代码归属、不改变对外地址（对照"文件系统路由约定"中的 `(marketing)`、`(auth)` 路由组）。
- **页面是自治插槽的组合，而非单一巨石组件**：并行路由的每个插槽独立取数、独立持有加载与错误边界，一个插槽未就绪或失败不拖垮其余插槽（对照"并行路由实现"中 `@analytics`、`@team`、`@reports` 与各自的 Suspense/ErrorBoundary）。
- **同一资源只有一个 URL，模态与整页是它的两种视图**：拦截路由保证深链接直达完整页面、站内上下文导航呈现覆盖层，刷新或直接输入地址都不会丢失资源本身（对照"拦截路由与模态框"）。
- **横切安全关注点收敛于请求入口的单条管道**：CORS、限流、认证、角色、安全响应头在请求进入任何路由前按序裁决，路由与页面内部不各自重复实现（对照"代理与路由保护"的九步处理管道）。
- **缓存层级跟随数据的新鲜度需求分级，而非跟随页面分级**：同一数据按更新频率选择缓存档位并以标签标识，失效按标签精准触达，实时数据宁可放弃缓存保持请求时渲染（对照"缓存策略与数据预获取"的 shortTerm 至 static 分档与标签失效）。

---

## 🔄 文档交叉引用

### 相关文档
- 📄 **[服务端组件模式](./02-server-components-patterns.md)**: 深入了解Next.js 16服务端组件架构和缓存策略
- 📄 **[客户端组件模式](./03-client-components-patterns.md)**: 掌握客户端组件开发和状态管理模式
- 📄 **[数据获取模式](./04-data-fetching-patterns.md)**: 学习SSR/SSG/ISR等数据获取策略
- 📄 **[认证流程模式](./07-authentication-flows.md)**: 实现企业级认证和权限控制系统

### 参考章节
- 📖 **[本模块其他章节]**: [数据获取模式](./04-data-fetching-patterns.md#-服务器端数据获取模式)中的服务端数据获取部分
- 📖 **[其他模块相关内容]**: [JavaScript现代语法](../language-concepts/04-javascript-modern.md)

---

## 📝 总结

### 核心要点回顾
1. **App Router架构**: 基于React Server Components的革命性路由系统
2. **文件系统约定**: 通过文件夹结构自动生成路由配置
3. **动态路由处理**: 类型安全的参数处理和验证机制
4. **布局和模板**: 灵活的嵌套布局和页面模板系统
5. **并行和拦截路由**: 高级路由模式实现复杂UI交互

### 学习成果检查
- [ ] 是否理解了App Router的核心概念和架构设计？
- [ ] 是否能够独立配置动态路由和路由参数？
- [ ] 是否能够实现布局系统和模板继承？
- [ ] 是否掌握了并行路由和拦截路由的应用场景？
- [ ] 是否具备了构建复杂路由架构的能力？

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
**最后更新**: 2026年9月
**版本**: v1.0.0

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
