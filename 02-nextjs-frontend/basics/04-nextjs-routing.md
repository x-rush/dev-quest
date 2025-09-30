# Next.js 路由系统 - App Router 深度解析

## 概述

Next.js 15 的路由系统是其最强大的特性之一。与传统的 PHP 框架路由不同，Next.js 采用了基于文件系统的路由机制，特别是 App Router 模式，它提供了更灵活、更强大的路由和布局能力。

## 从 PHP 路由到 Next.js 路由的对比

### 传统 PHP 路由
```php
// PHP 路由示例 (使用某个框架)
Route::get('/users', 'UserController@index');
Route::get('/users/{id}', 'UserController@show');
Route::post('/users', 'UserController@store');
Route::put('/users/{id}', 'UserController@update');
Route::delete('/users/{id}', 'UserController@destroy');
```

### Next.js 文件系统路由
```
app/
├── users/
│   ├── page.tsx           # GET /users
│   ├── [id]/
│   │   └── page.tsx       # GET /users/[id]
│   └── layout.tsx         # users 页面组的布局
└── layout.tsx             # 根布局
```

## App Router 基础

### 1. 路由结构

```
app/
├── layout.tsx             # 根布局
├── page.tsx               # 首页 (GET /)
├── about/
│   ├── layout.tsx         # about 页面组布局
│   └── page.tsx           # GET /about
├── blog/
│   ├── layout.tsx         # blog 页面组布局
│   ├── page.tsx           # GET /blog
│   ├── [slug]/
│   │   └── page.tsx       # GET /blog/[slug]
│   └── categories/
│       └── [category]/
│           └── page.tsx   # GET /blog/categories/[category]
└── api/
    └── users/
        └── route.ts       # API 路由
```

### 2. 基本路由组件

#### Page 组件
```tsx
// app/page.tsx
export default function HomePage() {
  return (
    <main>
      <h1>欢迎来到 Next.js 15</h1>
      <p>这是首页内容</p>
    </main>
  );
}

// app/about/page.tsx
export default function AboutPage() {
  return (
    <div>
      <h1>关于我们</h1>
      <p>这里是关于页面的内容</p>
    </div>
  );
}
```

#### Layout 组件
```tsx
// app/layout.tsx
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body>
        <header>
          <nav>
            <a href="/">首页</a>
            <a href="/about">关于</a>
            <a href="/blog">博客</a>
          </nav>
        </header>
        <main>{children}</main>
        <footer>
          <p>&copy; 2025 Next.js 应用</p>
        </footer>
      </body>
    </html>
  );
}
```

## 动态路由

### 1. 动态段
```tsx
// app/users/[id]/page.tsx
interface UserPageProps {
  params: {
    id: string;
  };
}

export default function UserPage({ params }: UserPageProps) {
  return (
    <div>
      <h1>用户详情</h1>
      <p>用户 ID: {params.id}</p>
    </div>
  );
}
```

### 2. 多个动态段
```tsx
// app/blog/[category]/[slug]/page.tsx
interface BlogPostPageProps {
  params: {
    category: string;
    slug: string;
  };
}

export default function BlogPostPage({ params }: BlogPostPageProps) {
  return (
    <div>
      <h1>博客文章</h1>
      <p>分类: {params.category}</p>
      <p>文章: {params.slug}</p>
    </div>
  );
}
```

### 3. 可选段
```tsx
// app/shop/[[...filter]]/page.tsx
interface ShopPageProps {
  params: {
    filter?: string[];
  };
}

export default function ShopPage({ params }: ShopPageProps) {
  const filters = params.filter || [];

  return (
    <div>
      <h1>商店</h1>
      <p>筛选条件: {filters.join(' / ') || '全部'}</p>
    </div>
  );
}
```

## 导航组件

### 1. Link 组件
```tsx
import Link from 'next/link';

function Navigation() {
  return (
    <nav>
      <Link href="/">首页</Link>
      <Link href="/about">关于</Link>
      <Link href="/blog">博客</Link>
      <Link href="/users/1">用户 1</Link>
    </nav>
  );
}

// 动态 Link
function UserLink({ id, name }: { id: string; name: string }) {
  return (
    <Link href={`/users/${id}`}>
      {name}
    </Link>
  );
}

// 使用对象配置
function AdvancedLink() {
  return (
    <Link
      href={{
        pathname: '/users/[id]',
        query: { id: '1', tab: 'profile' },
      }}
    >
      用户详情
    </Link>
  );
}
```

### 2. useRouter Hook
```tsx
'use client';

import { useRouter } from 'next/navigation';

function UserActions() {
  const router = useRouter();

  const goToUser = (id: string) => {
    router.push(`/users/${id}`);
  };

  const replaceUser = (id: string) => {
    router.replace(`/users/${id}`);
  };

  const goBack = () => {
    router.back();
  };

  const goForward = () => {
    router.forward();
  };

  const refreshPage = () => {
    router.refresh();
  };

  return (
    <div>
      <button onClick={() => goToUser('1')}>查看用户 1</button>
      <button onClick={() => replaceUser('2')}>替换为用户 2</button>
      <button onClick={goBack}>返回</button>
      <button onClick={goForward}>前进</button>
      <button onClick={refreshPage}>刷新</button>
    </div>
  );
}
```

### 3. usePathname Hook
```tsx
'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';

function ActiveLink({ href, children }: { href: string; children: React.ReactNode }) {
  const pathname = usePathname();
  const isActive = pathname === href;

  return (
    <Link href={href} className={isActive ? 'active' : ''}>
      {children}
    </Link>
  );
}

function Navigation() {
  return (
    <nav>
      <ActiveLink href="/">首页</ActiveLink>
      <ActiveLink href="/about">关于</ActiveLink>
      <ActiveLink href="/blog">博客</ActiveLink>
    </nav>
  );
}
```

## 路由组和布局

### 1. 路由组布局
```tsx
// app/(auth)/layout.tsx
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="auth-layout">
      <div className="auth-sidebar">
        <h2>认证页面</h2>
        <nav>
          <a href="/login">登录</a>
          <a href="/register">注册</a>
        </nav>
      </div>
      <div className="auth-content">
        {children}
      </div>
    </div>
  );
}

// app/(auth)/login/page.tsx
export default function LoginPage() {
  return (
    <div>
      <h1>登录</h1>
      {/* 登录表单 */}
    </div>
  );
}

// app/(auth)/register/page.tsx
export default function RegisterPage() {
  return (
    <div>
      <h1>注册</h1>
      {/* 注册表单 */}
    </div>
  );
}
```

### 2. 并行路由
```tsx
// app/@analytics/layout.tsx
export default function AnalyticsLayout({
  analytics,
  modal,
}: {
  analytics: React.ReactNode;
  modal: React.ReactNode;
}) {
  return (
    <div>
      {analytics}
      {modal}
    </div>
  );
}

// app/@analytics/page.tsx
export default function AnalyticsPage() {
  return (
    <div>
      <h1>分析数据</h1>
      {/* 分析内容 */}
    </div>
  );
}

// app/@analytics/@modal/page.tsx
export default function ModalPage() {
  return (
    <div className="modal">
      <h2>模态框内容</h2>
      {/* 模态框内容 */}
    </div>
  );
}
```

### 3. 拦截路由
```tsx
// app/(..)photo/[id]/page.tsx
export default function PhotoPage({ params }: { params: { id: string } }) {
  return (
    <div className="photo-modal">
      <h1>照片 {params.id}</h1>
      {/* 照片详情 */}
    </div>
  );
}

// 使用拦截路由
import Link from 'next/link';

function PhotoGrid() {
  return (
    <div className="photo-grid">
      {[1, 2, 3, 4, 5].map(id => (
        <Link key={id} href={`/photo/${id}`}>
          <img src={`/photos/${id}.jpg`} alt={`照片 ${id}`} />
        </Link>
      ))}
    </div>
  );
}
```

## 中间件

### 1. 基本中间件
```ts
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  console.log('中间件执行:', request.url);

  // 重定向示例
  if (request.nextUrl.pathname.startsWith('/admin')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // 添加请求头
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set('x-custom-header', 'custom-value');

  return NextResponse.next({
    request: {
      headers: requestHeaders,
    },
  });
}

// 匹配配置
export const config = {
  matcher: [
    /*
     * 匹配所有请求路径，除了:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
```

### 2. 认证中间件
```ts
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // 检查用户是否已认证
  const token = request.cookies.get('auth-token')?.value;

  const protectedPaths = ['/dashboard', '/profile', '/settings'];
  const isProtectedPath = protectedPaths.some(path =>
    request.nextUrl.pathname.startsWith(path)
  );

  if (isProtectedPath && !token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // 如果用户已登录且访问登录页面，重定向到仪表板
  if (request.nextUrl.pathname === '/login' && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}
```

## 生成元数据

### 1. 静态元数据
```tsx
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: '我的 Next.js 应用',
  description: '使用 Next.js 15 构建的现代化应用',
  keywords: ['Next.js', 'React', 'TypeScript'],
  authors: [{ name: '开发者姓名' }],
  openGraph: {
    title: '我的 Next.js 应用',
    description: '使用 Next.js 15 构建的现代化应用',
    type: 'website',
    locale: 'zh_CN',
  },
  twitter: {
    card: 'summary_large_image',
    title: '我的 Next.js 应用',
    description: '使用 Next.js 15 构建的现代化应用',
  },
};

export default function Page() {
  return <div>页面内容</div>;
}
```

### 2. 动态元数据
```tsx
import { Metadata, ResolvingMetadata } from 'next';

interface PageProps {
  params: { id: string };
  searchParams: { [key: string]: string | string[] | undefined };
}

export async function generateMetadata(
  { params }: PageProps,
  parent: ResolvingMetadata
): Promise<Metadata> {
  // 获取用户数据
  const user = await getUser(params.id);

  return {
    title: `${user.name} - 用户详情`,
    description: `查看 ${user.name} 的详细信息`,
    openGraph: {
      title: `${user.name} 的个人资料`,
      description: `${user.name} 是我们的重要用户`,
      images: [user.avatarUrl],
    },
  };
}

async function getUser(id: string) {
  // 模拟 API 调用
  return {
    id,
    name: '张三',
    avatarUrl: 'https://example.com/avatar.jpg',
  };
}

export default function UserPage({ params }: PageProps) {
  return <div>用户 {params.id} 的详情</div>;
}
```

## 路由处理器

### 1. 基本 API 路由
```ts
// app/api/users/route.ts
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const page = searchParams.get('page') || '1';
    const limit = searchParams.get('limit') || '10';

    // 获取用户数据
    const users = await getUsers(page, limit);

    return NextResponse.json({
      success: true,
      data: users,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: users.length,
      },
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: '获取用户失败' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();

    // 验证请求数据
    if (!body.name || !body.email) {
      return NextResponse.json(
        { success: false, error: '姓名和邮箱是必填项' },
        { status: 400 }
      );
    }

    // 创建用户
    const newUser = await createUser(body);

    return NextResponse.json({
      success: true,
      data: newUser,
    }, { status: 201 });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: '创建用户失败' },
      { status: 500 }
    );
  }
}
```

### 2. 动态 API 路由
```ts
// app/api/users/[id]/route.ts
import { NextResponse } from 'next/server';

interface RouteParams {
  params: {
    id: string;
  };
}

export async function GET(request: Request, { params }: RouteParams) {
  try {
    const user = await getUserById(params.id);

    if (!user) {
      return NextResponse.json(
        { success: false, error: '用户不存在' },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      data: user,
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: '获取用户失败' },
      { status: 500 }
    );
  }
}

export async function PUT(request: Request, { params }: RouteParams) {
  try {
    const body = await request.json();
    const updatedUser = await updateUser(params.id, body);

    return NextResponse.json({
      success: true,
      data: updatedUser,
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: '更新用户失败' },
      { status: 500 }
    );
  }
}

export async function DELETE(request: Request, { params }: RouteParams) {
  try {
    await deleteUser(params.id);

    return NextResponse.json({
      success: true,
      message: '用户删除成功',
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: '删除用户失败' },
      { status: 500 }
    );
  }
}
```

## 路由参数和搜索参数

### 1. 获取路由参数
```tsx
// app/products/[category]/[productId]/page.tsx
interface ProductPageProps {
  params: {
    category: string;
    productId: string;
  };
  searchParams: {
    [key: string]: string | string[] | undefined;
  };
}

export default function ProductPage({ params, searchParams }: ProductPageProps) {
  const { category, productId } = params;
  const color = searchParams.color as string;
  const size = searchParams.size as string;

  return (
    <div>
      <h1>产品详情</h1>
      <p>分类: {category}</p>
      <p>产品 ID: {productId}</p>
      {color && <p>颜色: {color}</p>}
      {size && <p>尺寸: {size}</p>
    </div>
  );
}
```

### 2. 生成静态参数
```tsx
// app/blog/[slug]/page.tsx
import { GetStaticPaths, GetStaticProps } from 'next';

interface BlogPostProps {
  params: {
    slug: string;
  };
}

// 生成静态路径
export async function generateStaticParams() {
  const posts = await getAllBlogPosts();

  return posts.map((post) => ({
    slug: post.slug,
  }));
}

// 获取静态 props
export async function generateStaticProps({ params }: BlogPostProps) {
  const post = await getBlogPostBySlug(params.slug);

  return {
    props: {
      post,
    },
  };
}

export default function BlogPostPage({ params }: BlogPostProps) {
  const post = await getBlogPostBySlug(params.slug);

  if (!post) {
    return <div>文章不存在</div>;
  }

  return (
    <div>
      <h1>{post.title}</h1>
      <div>{post.content}</div>
    </div>
  );
}
```

## 路由高级特性

### 1. 路由处理程序
```ts
// app/api/upload/route.ts
import { NextResponse } from 'next/server';
import { writeFile } from 'fs/promises';
import path from 'path';

export async function POST(request: Request) {
  try {
    const data = await request.formData();
    const file: File | null = data.get('file') as unknown as File;

    if (!file) {
      return NextResponse.json({ success: false, error: '没有文件' });
    }

    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);

    // 保存文件
    const filename = file.name;
    const filepath = path.join(process.cwd(), 'uploads', filename);
    await writeFile(filepath, buffer);

    return NextResponse.json({
      success: true,
      filename: filename,
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: '上传失败' },
      { status: 500 }
    );
  }
}
```

### 2. 路由配置
```ts
// next.config.ts
/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://api.example.com/:path*',
      },
    ];
  },
  async redirects() {
    return [
      {
        source: '/old-page',
        destination: '/new-page',
        permanent: true,
      },
    ];
  },
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,OPTIONS,PATCH,DELETE,POST,PUT' },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
```

## 实战示例

### 1. 完整的用户管理路由系统
```tsx
// app/users/page.tsx
import Link from 'next/link';

async function getUsers() {
  // 模拟 API 调用
  return [
    { id: '1', name: '张三', email: 'zhangsan@example.com' },
    { id: '2', name: '李四', email: 'lisi@example.com' },
    { id: '3', name: '王五', email: 'wangwu@example.com' },
  ];
}

export default async function UsersPage() {
  const users = await getUsers();

  return (
    <div className="users-page">
      <h1>用户列表</h1>

      <div className="actions">
        <Link href="/users/new" className="btn btn-primary">
          新增用户
        </Link>
      </div>

      <table className="users-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>姓名</th>
            <th>邮箱</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.id}</td>
              <td>{user.name}</td>
              <td>{user.email}</td>
              <td>
                <Link href={`/users/${user.id}`} className="btn btn-sm">
                  查看
                </Link>
                <Link href={`/users/${user.id}/edit`} className="btn btn-sm">
                  编辑
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

```tsx
// app/users/[id]/page.tsx
import Link from 'next/link';
import { notFound } from 'next/navigation';

interface UserPageProps {
  params: {
    id: string;
  };
}

async function getUser(id: string) {
  // 模拟 API 调用
  const users = [
    { id: '1', name: '张三', email: 'zhangsan@example.com', role: 'admin' },
    { id: '2', name: '李四', email: 'lisi@example.com', role: 'user' },
    { id: '3', name: '王五', email: 'wangwu@example.com', role: 'user' },
  ];

  return users.find(user => user.id === id);
}

export default async function UserPage({ params }: UserPageProps) {
  const user = await getUser(params.id);

  if (!user) {
    notFound();
  }

  return (
    <div className="user-page">
      <div className="page-header">
        <h1>用户详情</h1>
        <Link href="/users" className="btn btn-secondary">
          返回列表
        </Link>
      </div>

      <div className="user-details">
        <div className="detail-item">
          <label>ID:</label>
          <span>{user.id}</span>
        </div>
        <div className="detail-item">
          <label>姓名:</label>
          <span>{user.name}</span>
        </div>
        <div className="detail-item">
          <label>邮箱:</label>
          <span>{user.email}</span>
        </div>
        <div className="detail-item">
          <label>角色:</label>
          <span>{user.role}</span>
        </div>
      </div>

      <div className="page-actions">
        <Link href={`/users/${user.id}/edit`} className="btn btn-primary">
          编辑用户
        </Link>
        <Link href={`/users/${user.id}/delete`} className="btn btn-danger">
          删除用户
        </Link>
      </div>
    </div>
  );
}
```

```tsx
// app/users/new/page.tsx
'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';

export default function NewUserPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    role: 'user',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        router.push('/users');
      } else {
        alert('创建用户失败');
      }
    } catch (error) {
      console.error('创建用户失败:', error);
      alert('创建用户失败');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="new-user-page">
      <div className="page-header">
        <h1>新增用户</h1>
      </div>

      <form onSubmit={handleSubmit} className="user-form">
        <div className="form-group">
          <label htmlFor="name">姓名</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="email">邮箱</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="role">角色</label>
          <select
            id="role"
            name="role"
            value={formData.role}
            onChange={handleChange}
          >
            <option value="user">用户</option>
            <option value="admin">管理员</option>
          </select>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary">
            创建用户
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => router.push('/users')}
          >
            取消
          </button>
        </div>
      </form>
    </div>
  );
}
```

## 下一步

掌握 Next.js 路由系统后，你可以继续学习：

1. **样式解决方案** - 学习 Tailwind CSS 和现代样式方案
2. **数据获取** - 掌握 Server Components 和客户端数据获取
3. **状态管理** - 学习 Zustand、Jotai 等现代状态管理库
4. **API 集成** - 学习与后端 API 的集成方式

---

*Next.js 的路由系统是其核心特性之一，掌握 App Router 将帮助你构建现代化的 Web 应用。*