# Next.js 16 布局和路由设计完整指南

> **文档简介**: Next.js 16 App Router 布局和路由系统深入教程，涵盖文件系统路由、嵌套布局、动态路由、路由组、并行路由等现代路由设计模式

> **目标读者**: 具备Next.js基础的开发者，需要掌握现代路由设计和布局架构的前端工程师

> **前置知识**: Next.js基础、React组件基础、TypeScript基础、文件系统概念

> **预计时长**: 4-5小时

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `basics` |
| **难度** | ⭐⭐⭐ (3/5星) |
| **标签** | `#app-router` `#layouts` `#routing` `#navigation` `#file-system` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标

### 🗺️ 路由系统掌握
- 深入理解Next.js 16 App Router的文件系统路由
- 掌握嵌套路由和布局的创建方法
- 学会动态路由和路由参数处理
- 理解路由组和路由的高级特性

### 🏗️ 布局架构设计
- 掌握共享布局和嵌套布局的设计模式
- 学会创建复杂的页面布局结构
- 理解布局状态保持和生命周期
- 掌握响应式布局和主题切换

## 📖 概述

Next.js 16的App Router基于文件系统提供了强大的路由和布局功能。通过文件夹结构自动生成路由，支持嵌套布局、动态路由、并行路由等高级特性，让复杂应用的架构变得简单直观。

## 🏗️ App Router基础架构

### 文件系统路由约定

```
src/app/
├── layout.tsx              # 根布局 (应用于整个应用)
├── page.tsx                # 首页 (/)
├── loading.tsx             # 根加载组件
├── error.tsx               # 根错误边界
├── not-found.tsx           # 根404页面
├── about/
│   ├── layout.tsx          # 关于页面布局
│   ├── page.tsx            # 关于页面 (/about)
│   └── team/
│       └── page.tsx        # 团队页面 (/about/team)
├── blog/
│   ├── layout.tsx          # 博客布局
│   ├── page.tsx            # 博客列表 (/blog)
│   ├── [slug]/
│   │   ├── page.tsx        # 文章详情 (/blog/[slug])
│   │   └── loading.tsx     # 文章加载状态
│   └── (auth)/
│       ├── layout.tsx      # 路由组布局 (不影响URL)
│       └── login/
│           └── page.tsx    # 登录页面 (/blog/login)
└── dashboard/
    ├── layout.tsx          # 仪表板布局
    ├── page.tsx            # 仪表板首页 (/dashboard)
    ├── @analytics/
    │   └── page.tsx        # 分析页面 (并行路由)
    └── @settings/
        └── page.tsx        # 设置页面 (并行路由)
```

### 根布局配置

```tsx
// src/app/layout.tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Navigation } from '@/components/Navigation'
import { Footer } from '@/components/Footer'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: {
    default: '我的Next.js应用',
    template: '%s | 我的Next.js应用'
  },
  description: '使用Next.js 16构建的现代化Web应用',
  keywords: ['Next.js', 'React', 'TypeScript', 'Web开发'],
  authors: [{ name: 'Dev Quest Team' }],
  creator: 'Dev Quest Team',
  openGraph: {
    type: 'website',
    locale: 'zh_CN',
    url: 'https://myapp.com',
    title: '我的Next.js应用',
    description: '使用Next.js 16构建的现代化Web应用',
  },
  twitter: {
    card: 'summary_large_image',
    title: '我的Next.js应用',
    description: '使用Next.js 16构建的现代化Web应用',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN" className={inter.className}>
      <body className="min-h-screen bg-gray-50 antialiased">
        <div className="flex flex-col min-h-screen">
          <Navigation />
          <main className="flex-1">
            {children}
          </main>
          <Footer />
        </div>
      </body>
    </html>
  )
}
```

## 🗺️ 基础路由模式

### 静态路由

```tsx
// src/app/about/page.tsx
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: '关于我们',
  description: '了解我们的团队和使命',
}

export default function AboutPage() {
  return (
    <div className="max-w-4xl mx-auto py-12 px-4">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">
        关于我们
      </h1>

      <div className="prose prose-lg max-w-none">
        <p className="text-xl text-gray-600 mb-6">
          我们是一个充满激情的技术团队，致力于构建优秀的Web应用。
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 my-12">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4">🎯 我们的使命</h3>
            <p className="text-gray-600">
              通过技术创新，为用户提供卓越的数字体验。
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4">🚀 我们的愿景</h3>
            <p className="text-gray-600">
              成为行业领先的技术解决方案提供商。
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
```

### 嵌套路由和布局

```tsx
// src/app/blog/layout.tsx
import { Metadata } from 'next'
import { BlogSidebar } from '@/components/BlogSidebar'

export const metadata: Metadata = {
  title: '博客',
  description: '分享技术见解和开发经验',
}

export default function BlogLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <aside className="lg:col-span-1">
          <BlogSidebar />
        </aside>
        <main className="lg:col-span-3">
          {children}
        </main>
      </div>
    </div>
  )
}

// src/app/blog/page.tsx
import Link from 'next/link'
import { blogPosts } from '@/lib/blog-data'

export default function BlogListPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        技术博客
      </h1>

      <div className="space-y-8">
        {blogPosts.map((post) => (
          <article key={post.id} className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  <Link
                    href={`/blog/${post.slug}`}
                    className="hover:text-blue-600 transition"
                  >
                    {post.title}
                  </Link>
                </h2>
                <p className="text-gray-600 mb-2">{post.excerpt}</p>
                <div className="flex items-center text-sm text-gray-500">
                  <span>{post.author}</span>
                  <span className="mx-2">•</span>
                  <time>{post.publishedAt}</time>
                </div>
              </div>
            </div>
          </article>
        ))}
      </div>
    </div>
  )
}
```

## 🔀 动态路由

### 基础动态路由

```tsx
// src/app/blog/[slug]/page.tsx
import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { getPostBySlug, getAllPostSlugs } from '@/lib/blog-data'
import { BlogContent } from '@/components/BlogContent'

interface PostPageProps {
  // Next.js 16：params 为 Promise
  params: Promise<{
    slug: string
  }>
}

// 生成静态参数
export async function generateStaticParams() {
  const posts = getAllPostSlugs()
  return posts.map((slug) => ({
    slug,
  }))
}

// 生成元数据
export async function generateMetadata({ params }: PostPageProps): Promise<Metadata> {
  const { slug } = await params
  const post = await getPostBySlug(slug)

  if (!post) {
    return {
      title: '文章不存在',
    }
  }

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      type: 'article',
      publishedTime: post.publishedAt,
      authors: [post.author],
    },
  }
}

export default async function PostPage({ params }: PostPageProps) {
  const { slug } = await params
  const post = await getPostBySlug(slug)

  if (!post) {
    notFound()
  }

  return (
    <article className="max-w-4xl mx-auto">
      <BlogContent post={post} />
    </article>
  )
}
```

### 多参数动态路由

```tsx
// src/app/users/[userId]/posts/[postId]/page.tsx
import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { getUserPost } from '@/lib/api'

interface UserPostPageProps {
  // Next.js 16：params 为 Promise
  params: Promise<{
    userId: string
    postId: string
  }>
}

export async function generateMetadata({ params }: UserPostPageProps): Promise<Metadata> {
  const { userId, postId } = await params
  const post = await getUserPost(userId, postId)

  return {
    title: post?.title || '文章不存在',
    description: post?.content?.substring(0, 160) || '',
  }
}

export default async function UserPostPage({ params }: UserPostPageProps) {
  const { userId, postId } = await params
  const post = await getUserPost(userId, postId)

  if (!post) {
    notFound()
  }

  return (
    <div className="max-w-4xl mx-auto py-8">
      <div className="mb-6">
        <nav className="text-sm text-gray-500">
          <Link href="/users" className="hover:text-gray-700">用户</Link>
          <span className="mx-2">/</span>
          <Link href={`/users/${userId}`} className="hover:text-gray-700">
            用户 {userId}
          </Link>
          <span className="mx-2">/</span>
          <span className="text-gray-900">文章 {postId}</span>
        </nav>
      </div>

      <article>
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          {post.title}
        </h1>
        <div className="text-gray-600 mb-8">
          作者：{post.author} | 发布时间：{post.publishedAt}
        </div>
        <div
          className="prose prose-lg max-w-none"
          dangerouslySetInnerHTML={{ __html: post.content }}
        />
      </article>
    </div>
  )
}
```

## 🎨 高级布局模式

### 条件布局

```tsx
// src/app/dashboard/layout.tsx
import { redirect } from 'next/navigation'
import { getServerSession } from 'next-auth'
import { DashboardSidebar } from '@/components/DashboardSidebar'
import { DashboardHeader } from '@/components/DashboardHeader'

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // 检查用户认证状态
  const session = await getServerSession()

  if (!session) {
    redirect('/login')
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <DashboardHeader user={session.user} />
      <div className="flex">
        <DashboardSidebar />
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
```

### 响应式布局

```tsx
// src/components/ResponsiveLayout.tsx
'use client'

import { useState, useEffect } from 'react'
import { Sidebar } from './Sidebar'
import { Header } from './Header'

interface ResponsiveLayoutProps {
  children: React.ReactNode
}

export function ResponsiveLayout({ children }: ResponsiveLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
      if (window.innerWidth >= 768) {
        setSidebarOpen(false)
      }
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <Header
        onMenuClick={() => setSidebarOpen(!sidebarOpen)}
        showMenuButton={isMobile}
      />

      <div className="flex">
        {/* 移动端侧边栏覆盖层 */}
        {isMobile && sidebarOpen && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-40"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* 侧边栏 */}
        <aside className={`
          ${isMobile ? 'fixed' : 'relative'}
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          md:translate-x-0
          transition-transform duration-300 ease-in-out
          w-64 h-full bg-white shadow-lg z-50
        `}>
          <Sidebar />
        </aside>

        {/* 主内容区 */}
        <main className="flex-1 min-h-0">
          {children}
        </main>
      </div>
    </div>
  )
}
```

## 🔄 路由组

### 组织路由结构

```
src/app/
├── (marketing)/              # 路由组：营销页面
│   ├── layout.tsx            # 营销页面布局
│   ├── page.tsx              # 首页 (/)
│   ├── about/
│   │   └── page.tsx          # 关于页面 (/about)
│   └── pricing/
│       └── page.tsx          # 价格页面 (/pricing)
├── (auth)/                   # 路由组：认证页面
│   ├── layout.tsx            # 认证页面布局
│   ├── login/
│   │   └── page.tsx          # 登录页面 (/login)
│   └── register/
│       └── page.tsx          # 注册页面 (/register)
└── (dashboard)/              # 路由组：仪表板页面
    ├── layout.tsx            # 仪表板布局
    ├── page.tsx              # 仪表板首页 (/dashboard)
    └── settings/
        └── page.tsx          # 设置页面 (/dashboard/settings)
```

### 路由组布局实现

```tsx
// src/app/(marketing)/layout.tsx
import { MarketingHeader } from '@/components/MarketingHeader'
import { MarketingFooter } from '@/components/MarketingFooter'

export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-white">
      <MarketingHeader />
      <main className="flex-1">
        {children}
      </main>
      <MarketingFooter />
    </div>
  )
}

// src/app/(auth)/layout.tsx
import { AuthLayout } from '@/components/AuthLayout'

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <AuthLayout>
      {children}
    </AuthLayout>
  )
}
```

## 🔀 并行路由

### 仪表板并行布局

```tsx
// src/app/dashboard/@analytics/page.tsx
export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">数据分析</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">总用户数</h3>
          <p className="text-2xl font-bold text-gray-900 mt-2">1,234</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">活跃用户</h3>
          <p className="text-2xl font-bold text-green-600 mt-2">856</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">新增用户</h3>
          <p className="text-2xl font-bold text-blue-600 mt-2">+124</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">转化率</h3>
          <p className="text-2xl font-bold text-purple-600 mt-2">3.2%</p>
        </div>
      </div>

      {/* 更多分析内容 */}
    </div>
  )
}

// src/app/dashboard/@settings/page.tsx
export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">系统设置</h2>

      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <h3 className="text-lg font-medium text-gray-900">基本设置</h3>
        </div>
        <div className="p-6 space-y-4">
          {/* 设置表单 */}
        </div>
      </div>
    </div>
  )
}

// src/app/dashboard/layout.tsx
import { DashboardNav } from '@/components/DashboardNav'

export default function DashboardLayout({
  children,
  analytics,
  settings,
}: {
  children: React.ReactNode
  analytics?: React.ReactNode
  settings?: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardNav />

      <div className="flex">
        <aside className="w-64 bg-white shadow-sm h-screen">
          {/* 侧边栏内容 */}
        </aside>

        <main className="flex-1 p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              {children}
            </div>

            <div className="space-y-6">
              {analytics}
              {settings}
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
```

## 🎯 拦截路由

### 模态框拦截路由

```tsx
// src/app/photos/[id]/page.tsx
import { notFound } from 'next/navigation'
import { getPhotoById } from '@/lib/photos'

interface PhotoPageProps {
  // Next.js 16：params 为 Promise
  params: Promise<{ id: string }>
}

export default async function PhotoPage({ params }: PhotoPageProps) {
  const { id } = await params
  const photo = await getPhotoById(id)

  if (!photo) {
    notFound()
  }

  return (
    <div className="container mx-auto py-8">
      <div className="max-w-4xl mx-auto">
        <img
          src={photo.url}
          alt={photo.title}
          className="w-full h-auto rounded-lg shadow-lg"
        />
        <h1 className="text-3xl font-bold mt-6">{photo.title}</h1>
        <p className="text-gray-600 mt-2">{photo.description}</p>
      </div>
    </div>
  )
}

// src/app/@modal/(.)photos/[id]/page.tsx
import { getPhotoById } from '@/lib/photos'
import { PhotoModal } from '@/components/PhotoModal'

interface PhotoModalProps {
  params: Promise<{ id: string }>
}

export default async function PhotoModal({ params }: PhotoModalProps) {
  const { id } = await params
  const photo = await getPhotoById(id)

  if (!photo) {
    return null
  }

  return <PhotoModal photo={photo} />
}

// src/components/PhotoModal.tsx
'use client'

import { useRouter, usePathname } from 'next/navigation'
import { createPortal } from 'react-dom'
import { useEffect } from 'react'

interface PhotoModalProps {
  photo: {
    id: string
    title: string
    url: string
    description: string
  }
}

export function PhotoModal({ photo }: PhotoModalProps) {
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        router.back()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [router])

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      router.back()
    }
  }

  if (typeof document === 'undefined') {
    return null
  }

  return createPortal(
    <div
      className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-auto">
        <div className="relative">
          <img
            src={photo.url}
            alt={photo.title}
            className="w-full h-auto"
          />
          <button
            onClick={() => router.back()}
            className="absolute top-4 right-4 bg-white rounded-full p-2 shadow-lg hover:bg-gray-100"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="p-6">
          <h2 className="text-2xl font-bold">{photo.title}</h2>
          <p className="text-gray-600 mt-2">{photo.description}</p>
        </div>
      </div>
    </div>,
    document.body
  )
}
```

## 🧭 导航和链接

### 智能导航组件

```tsx
// src/components/Navigation.tsx
'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'
import { cn } from '@/lib/utils'

interface NavItem {
  href: string
  label: string
  icon?: React.ReactNode
  children?: NavItem[]
}

const navItems: NavItem[] = [
  { href: '/', label: '首页' },
  { href: '/about', label: '关于' },
  {
    href: '/blog',
    label: '博客',
    children: [
      { href: '/blog', label: '所有文章' },
      { href: '/blog/categories', label: '分类' },
      { href: '/blog/tags', label: '标签' }
    ]
  },
  { href: '/contact', label: '联系' },
]

export function Navigation() {
  const pathname = usePathname()
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const isActive = (href: string) => {
    if (href === '/') {
      return pathname === '/'
    }
    return pathname.startsWith(href)
  }

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="text-xl font-bold text-blue-600">
            MyApp
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex space-x-8">
            {navItems.map((item) => (
              <div key={item.href} className="relative group">
                <Link
                  href={item.href}
                  className={cn(
                    'flex items-center px-3 py-2 text-sm font-medium transition-colors',
                    isActive(item.href)
                      ? 'text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-700 hover:text-blue-600'
                  )}
                >
                  {item.label}
                  {item.children && (
                    <svg className="ml-1 h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  )}
                </Link>

                {/* Dropdown Menu */}
                {item.children && (
                  <div className="absolute left-0 mt-0 w-48 bg-white border border-gray-200 rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                    {item.children.map((child) => (
                      <Link
                        key={child.href}
                        href={child.href}
                        className={cn(
                          'block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-blue-600',
                          isActive(child.href) && 'text-blue-600 bg-blue-50'
                        )}
                      >
                        {child.label}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-gray-700 hover:text-blue-600 p-2"
            >
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {isMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t">
            {navItems.map((item) => (
              <div key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    'block px-3 py-2 text-base font-medium',
                    isActive(item.href)
                      ? 'text-blue-600 bg-blue-50'
                      : 'text-gray-700 hover:text-blue-600'
                  )}
                  onClick={() => setIsMenuOpen(false)}
                >
                  {item.label}
                </Link>
                {item.children && (
                  <div className="ml-4 space-y-1">
                    {item.children.map((child) => (
                      <Link
                        key={child.href}
                        href={child.href}
                        className={cn(
                          'block px-3 py-2 text-sm',
                          isActive(child.href)
                            ? 'text-blue-600 bg-blue-50'
                            : 'text-gray-600 hover:text-blue-600'
                        )}
                        onClick={() => setIsMenuOpen(false)}
                      >
                        {child.label}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </nav>
  )
}
```

### 面包屑导航

```tsx
// src/components/Breadcrumbs.tsx
import Link from 'next/link'
import { usePathname } from 'next/navigation'

interface BreadcrumbItem {
  label: string
  href: string
}

export function Breadcrumbs() {
  const pathname = usePathname()

  const getBreadcrumbs = (): BreadcrumbItem[] => {
    const segments = pathname.split('/').filter(Boolean)
    const breadcrumbs: BreadcrumbItem[] = [
      { label: '首页', href: '/' }
    ]

    let currentPath = ''

    segments.forEach((segment) => {
      currentPath += `/${segment}`

      // 转换URL段为显示名称
      const label = segment
        .replace(/-/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase())

      breadcrumbs.push({
        label,
        href: currentPath
      })
    })

    return breadcrumbs
  }

  const breadcrumbs = getBreadcrumbs()

  if (breadcrumbs.length <= 1) {
    return null
  }

  return (
    <nav className="flex items-center space-x-2 text-sm text-gray-500 py-4">
      {breadcrumbs.map((item, index) => (
        <div key={item.href} className="flex items-center space-x-2">
          {index > 0 && (
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          )}

          {index === breadcrumbs.length - 1 ? (
            <span className="text-gray-900 font-medium">{item.label}</span>
          ) : (
            <Link
              href={item.href}
              className="hover:text-gray-700 transition-colors"
            >
              {item.label}
            </Link>
          )}
        </div>
      ))}
    </nav>
  )
}
```

## ✅ 总结

通过本教程，你已经掌握了：

1. **App Router基础**: 文件系统路由和布局的创建方法
2. **动态路由**: 参数处理和静态生成
3. **嵌套布局**: 复杂页面结构的构建
4. **路由组**: 路由的组织和管理
5. **并行路由**: 复杂页面的并行渲染
6. **拦截路由**: 模态框和覆盖层的实现
7. **导航组件**: 智能导航和面包屑的构建

## 📚 下一步学习

- 深入学习服务器组件和客户端组件
- 掌握数据获取和缓存策略
- 学习状态管理和表单处理
- 探索性能优化和SEO策略
- 了解部署和运维最佳实践

Next.js 16的路由系统为现代Web应用提供了强大而灵活的架构基础。继续探索更多高级特性，构建更优秀的应用吧！

## 🔄 文档交叉引用

### 相关文档
- 📄 **[前一个basics文档](./03-typescript-integration.md)**: 学习TypeScript集成，为路由组件添加类型安全
- 📄 **[后一个basics文档](./05-styling-with-tailwind.md)**: 学习样式系统，美化路由和布局组件
- 📄 **[相关的reference文档](../reference/framework-patterns/01-app-router-patterns.md)**: 深入了解App Router的设计模式和最佳实践
- 📄 **[相关的reference文档](../reference/framework-patterns/03-client-components-patterns.md)**: 快速参考客户端组件的路由模式

### 参考章节
- 📖 **[本模块其他章节]**: [TypeScript集成](./03-typescript-integration.md#页面和路由的类型安全) | [样式设计](./05-styling-with-tailwind.md#响应式设计系统)
- 📖 **[Knowledge Points快速参考]**: [App Router模式](../reference/framework-patterns/01-app-router-patterns.md) | [Next.js API参考](../reference/language-concepts/02-nextjs-api-reference.md)

## 📝 总结

### 核心要点回顾
1. **App Router基础**: 掌握文件系统路由的约定和布局组件的创建方法
2. **嵌套路由**: 理解嵌套布局的实现，掌握复杂页面结构的构建
3. **动态路由**: 学会创建动态路由和参数处理，理解静态生成机制
4. **路由组织**: 掌握路由组的使用，学会组织复杂的应用结构
5. **高级特性**: 理解并行路由和拦截路由，掌握高级路由模式

### 学习成果检查
- [ ] 是否理解Next.js 16 App Router的文件系统约定？
- [ ] 是否能够创建嵌套布局和共享布局组件？
- [ ] 是否掌握动态路由的创建和参数处理方法？
- [ ] 是否理解路由组和并行路由的使用场景？
- [ ] 是否能够构建智能导航和面包屑组件？

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

**文档状态**: ✅ 已完成
**最后更新**: 2026年9月
**版本**: v1.0.0