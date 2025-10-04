# Next.js 路由速查手册

## 📚 概述

Next.js 15 提供了强大的路由系统，包括 App Router、动态路由、嵌套路由等特性。本手册涵盖了所有路由相关的 API 和最佳实践。

## 🏗️ App Router 基础

### 文件系统路由
**基于文件结构自动生成路由**

```
app/
├── layout.tsx           # 根布局
├── page.tsx            # 首页 (/)
├── about/
│   └── page.tsx        # 关于页面 (/about)
├── blog/
│   ├── page.tsx        # 博客列表 (/blog)
│   ├── [slug]/
│   │   └── page.tsx    # 动态博客文章 (/blog/[slug])
│   └── layout.tsx      # 博客模块布局
├── dashboard/
│   ├── layout.tsx      # 仪表板布局
│   ├── page.tsx        # 仪表板首页 (/dashboard)
│   ├── settings/
│   │   └── page.tsx    # 设置页面 (/dashboard/settings)
│   └── (auth)/
│       ├── login/
│       │   └── page.tsx # 登录页面 (/login)
│       └── register/
│           └── page.tsx # 注册页面 (/register)
└── api/
    ├── users/
    │   └── route.ts    # API 路由 (/api/users)
    └── posts/
        └── [id]/
            └── route.ts # 动态 API 路由 (/api/posts/[id])
```

### 基础页面组件
**创建静态和动态页面**

```typescript
// app/page.tsx - 首页
export default function HomePage() {
  return (
    <main>
      <h1>Welcome to My App</h1>
      <p>This is the homepage</p>
    </main>
  );
}

// app/about/page.tsx - 关于页面
export default function AboutPage() {
  return (
    <div>
      <h1>About Us</h1>
      <p>Learn more about our company</p>
    </div>
  );
}

// app/blog/[slug]/page.tsx - 动态路由页面
interface BlogPostPageProps {
  params: {
    slug: string;
  };
}

export default function BlogPostPage({ params }: BlogPostPageProps) {
  return (
    <article>
      <h1>Blog Post: {params.slug}</h1>
      <p>This is a dynamic blog post page</p>
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

// 生成元数据
export async function generateMetadata({ params }: BlogPostPageProps) {
  const post = await fetch(`https://api.example.com/posts/${params.slug}`).then(res => res.json());

  return {
    title: post.title,
    description: post.excerpt,
  };
}
```

## 🎨 布局系统

### 根布局
**应用的全局布局**

```typescript
// app/layout.tsx
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'My App',
  description: 'A modern web application',
  keywords: ['nextjs', 'react', 'typescript'],
  authors: [{ name: 'Your Name' }],
  openGraph: {
    title: 'My App',
    description: 'A modern web application',
    type: 'website',
    url: 'https://myapp.com',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <header>
          <nav>
            <Link href="/">Home</Link>
            <Link href="/about">About</Link>
            <Link href="/blog">Blog</Link>
          </nav>
        </header>
        <main>{children}</main>
        <footer>
          <p>&copy; 2025 My App. All rights reserved.</p>
        </footer>
      </body>
    </html>
  );
}
```

### 嵌套布局
**特定路由段的布局**

```typescript
// app/blog/layout.tsx
export default function BlogLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="blog-layout">
      <aside>
        <BlogCategories />
        <RecentPosts />
      </aside>
      <section className="blog-content">
        {children}
      </section>
    </div>
  );
}

// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="dashboard">
      <DashboardSidebar />
      <div className="dashboard-main">
        <DashboardHeader />
        <main>{children}</main>
      </div>
    </div>
  );
}
```

## 🔄 路由导航

### Link 组件
**客户端导航**

```typescript
import Link from 'next/link';

function Navigation() {
  return (
    <nav>
      <Link href="/" className="nav-link">
        Home
      </Link>

      <Link href="/about" className="nav-link">
        About
      </Link>

      <Link href="/blog?category=tech" className="nav-link">
        Tech Blog
      </Link>

      {/* 动态路由链接 */}
      <Link href={`/blog/${post.slug}`} className="nav-link">
        {post.title}
      </Link>

      {/* 查询参数 */}
      <Link
        href="/search?q=nextjs&sort=popular"
        className="nav-link"
      >
        Search Next.js
      </Link>

      {/* 程序化导航样式 */}
      <Link
        href="/dashboard"
        className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`}
        prefetch={true}
      >
        Dashboard
      </Link>
    </nav>
  );
}

// 高级 Link 组件用法
function ProductLink({ product }: { product: Product }) {
  return (
    <Link
      href={`/products/${product.id}`}
      className="product-link"
      prefetch={product.isPopular} // 只为热门产品预取
      scroll={true} // 滚动到页面顶部
      replace={false} // 不替换历史记录
    >
      <img src={product.image} alt={product.name} />
      <h3>{product.name}</h3>
      <p>${product.price}</p>
    </Link>
  );
}
```

### useRouter Hook
**程序化导航**

```typescript
'use client';

import { useRouter, usePathname, useSearchParams } from 'next/navigation';

function NavigationComponent() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const navigateToAbout = () => {
    router.push('/about');
  };

  const navigateWithQuery = () => {
    const query = new URLSearchParams();
    query.set('category', 'tech');
    query.set('sort', 'latest');
    router.push(`/blog?${query.toString()}`);
  };

  const goBack = () => {
    router.back();
  };

  const replaceRoute = () => {
    router.replace('/dashboard');
  };

  const refreshData = () => {
    router.refresh(); // 重新获取服务器组件数据
  };

  return (
    <div>
      <p>Current path: {pathname}</p>
      <p>Search params: {searchParams.toString()}</p>

      <button onClick={navigateToAbout}>Go to About</button>
      <button onClick={navigateWithQuery}>Go to Tech Blog</button>
      <button onClick={goBack}>Go Back</button>
      <button onClick={replaceRoute}>Replace Route</button>
      <button onClick={refreshData}>Refresh Data</button>
    </div>
  );
}

// 高级导航用法
function SearchComponent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const updateSearch = (term: string) => {
    const params = new URLSearchParams(searchParams);

    if (term) {
      params.set('q', term);
    } else {
      params.delete('q');
    }

    router.push(`/search?${params.toString()}`);
  };

  const clearFilters = () => {
    router.push('/search');
  };

  return (
    <div>
      <input
        type="text"
        placeholder="Search..."
        defaultValue={searchParams.get('q') || ''}
        onChange={(e) => updateSearch(e.target.value)}
      />
      <button onClick={clearFilters}>Clear Filters</button>
    </div>
  );
}
```

## 🔀 动态路由

### 基础动态路由
**处理动态参数**

```typescript
// app/users/[id]/page.tsx
interface UserPageProps {
  params: {
    id: string;
  };
}

export default async function UserPage({ params }: UserPageProps) {
  const user = await fetchUser(params.id);

  if (!user) {
    notFound();
  }

  return (
    <div>
      <h1>{user.name}</h1>
      <p>Email: {user.email}</p>
    </div>
  );
}

// 生成静态参数
export async function generateStaticParams() {
  const users = await fetchUsers();

  return users.map((user: User) => ({
    id: user.id.toString(),
  }));
}

// app/products/[category]/[id]/page.tsx
interface ProductPageProps {
  params: {
    category: string;
    id: string;
  };
  searchParams: {
    color?: string;
    size?: string;
  };
}

export default function ProductPage({
  params,
  searchParams
}: ProductPageProps) {
  return (
    <div>
      <h1>Product Details</h1>
      <p>Category: {params.category}</p>
      <p>Product ID: {params.id}</p>
      <p>Color: {searchParams.color || 'Not specified'}</p>
      <p>Size: {searchParams.size || 'Not specified'}</p>
    </div>
  );
}
```

### 捕获所有路由
**处理动态路径段**

```typescript
// app/docs/[...slug]/page.tsx
interface DocsPageProps {
  params: {
    slug: string[];
  };
}

export default function DocsPage({ params }: DocsPageProps) {
  const { slug } = params;
  const path = slug.join('/');

  return (
    <div>
      <h1>Documentation</h1>
      <p>Current path: /docs/{path}</p>
      <nav>
        <Link href="/docs">Overview</Link>
        <Link href="/docs/getting-started">Getting Started</Link>
        <Link href="/docs/getting-started/installation">Installation</Link>
      </nav>
    </div>
  );
}

// app/shop/[...catchAll]/page.tsx - 可选捕获所有路由
interface ShopPageProps {
  params: {
    catchAll?: string[];
  };
}

export default function ShopPage({ params }: ShopPageProps) {
  const { catchAll } = params;

  if (!catchAll) {
    return <h1>Shop Homepage</h1>;
  }

  const category = catchAll[0];
  const subcategory = catchAll[1];

  return (
    <div>
      <h1>Shop</h1>
      <p>Category: {category}</p>
      {subcategory && <p>Subcategory: {subcategory}</p>}
    </div>
  );
}
```

## 🔀 路由组

### 组织路由结构
**不影响 URL 的文件夹组织**

```
app/
├── (marketing)/
│   ├── layout.tsx          # 市场营销布局
│   ├── page.tsx           # 首页 (/)
│   ├── about/
│   │   └── page.tsx       # 关于页面 (/about)
│   └── contact/
│       └── page.tsx       # 联系页面 (/contact)
├── (shop)/
│   ├── layout.tsx          # 商店布局
│   ├── products/
│   │   └── page.tsx       # 产品列表 (/products)
│   └── cart/
│       └── page.tsx       # 购物车 (/cart)
└── (auth)/
    ├── layout.tsx          # 认证布局
    ├── login/
    │   └── page.tsx       # 登录页面 (/login)
    └── register/
        └── page.tsx       # 注册页面 (/register)
```

```typescript
// app/(marketing)/layout.tsx
export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="marketing-layout">
      <MarketingHeader />
      <main>{children}</main>
      <MarketingFooter />
    </div>
  );
}

// app/(shop)/layout.tsx
export default function ShopLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="shop-layout">
      <ShopSidebar />
      <main>{children}</main>
      <ShoppingCart />
    </div>
  );
}
```

## 🔄 并行路由

### 插槽模式
**同时渲染多个页面**

```
app/
├── layout.tsx
├── page.tsx
├── @analytics/
│   └── page.tsx
├── @team/
│   └── page.tsx
└── dashboard/
    ├── layout.tsx
    ├── page.tsx
    ├── @analytics/
    │   ├── page.tsx
    │   ├── traffic/
    │   │   └── page.tsx
    │   └── sales/
    │       └── page.tsx
    └── @team/
        ├── page.tsx
        ├── members/
        │   └── page.tsx
        └── performance/
            └── page.tsx
```

```typescript
// app/dashboard/layout.tsx
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
      <nav>
        <Link href="/dashboard">Overview</Link>
        <Link href="/dashboard/analytics">Analytics</Link>
        <Link href="/dashboard/team">Team</Link>
      </nav>

      <div className="dashboard-content">
        <main>{children}</main>
        <aside className="sidebar">
          {analytics}
          {team}
        </aside>
      </div>
    </div>
  );
}

// app/dashboard/@analytics/page.tsx
export default function Analytics() {
  return (
    <div className="analytics-widget">
      <h3>Analytics Overview</h3>
      {/* 分析数据 */}
    </div>
  );
}

// app/dashboard/@team/page.tsx
export default function TeamOverview() {
  return (
    <div className="team-widget">
      <h3>Team Performance</h3>
      {/* 团队数据 */}
    </div>
  );
}
```

## 🔀 拦截路由

### 模态框和覆盖层
**在当前页面上下文中显示内容**

```
app/
├── feed/
│   ├── layout.tsx
│   ├── page.tsx
│   └── @modal/
│       └── (..)photo/
│           └── [id]/
│               └── page.tsx
├── photo/
│   ├── [id]/
│   │   └── page.tsx
│   └── layout.tsx
```

```typescript
// app/feed/page.tsx
export default function Feed() {
  return (
    <div>
      <h1>Photo Feed</h1>
      {photos.map(photo => (
        <Link key={photo.id} href={`/photo/${photo.id}`}>
          <img src={photo.thumbnail} alt={photo.title} />
        </Link>
      ))}
    </div>
  );
}

// app/feed/@modal/(..)photo/[id]/page.tsx
interface PhotoModalProps {
  params: {
    id: string;
  };
}

export default function PhotoModal({ params }: PhotoModalProps) {
  const photo = await getPhoto(params.id);

  return (
    <div className="modal">
      <div className="modal-content">
        <img src={photo.url} alt={photo.title} />
        <h2>{photo.title}</h2>
        <p>{photo.description}</p>
        <Link href="/feed">Close</Link>
      </div>
    </div>
  );
}
```

## 🔧 中间件

### 路由保护和重定向
**在页面渲染前执行代码**

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get('auth-token')?.value;

  // 保护认证路由
  if (pathname.startsWith('/dashboard') && !token) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // 重定向旧路由
  if (pathname.startsWith('/old-route')) {
    const newPath = pathname.replace('/old-route', '/new-route');
    return NextResponse.redirect(new URL(newPath, request.url));
  }

  // 添加自定义头
  const response = NextResponse.next();
  response.headers.set('x-custom-header', 'custom-value');

  return response;
}

// 匹配路径配置
export const config = {
  matcher: [
    '/dashboard/:path*',
    '/profile/:path*',
    '/old-route/:path*',
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};

// 高级中间件示例
import { auth } from './auth';

export default async function middleware(request: NextRequest) {
  const session = await auth();
  const { pathname } = request.nextUrl;

  // 公开路由
  const publicRoutes = ['/login', '/register', '/forgot-password'];
  if (publicRoutes.includes(pathname)) {
    if (session) {
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }
    return NextResponse.next();
  }

  // 需要认证的路由
  if (!session) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // 角色基础访问控制
  if (pathname.startsWith('/admin') && session.user.role !== 'admin') {
    return NextResponse.redirect(new URL('/unauthorized', request.url));
  }

  // 地理位置重定向
  const country = request.geo?.country;
  if (country && pathname === '/') {
    const localizedPath = `/${country.toLowerCase()}`;
    return NextResponse.redirect(new URL(localizedPath, request.url));
  }

  return NextResponse.next();
}
```

## 🔀 路由参数和查询

### 参数处理
**访问和操作路由参数**

```typescript
// app/search/[category]/page.tsx
interface SearchPageProps {
  params: {
    category: string;
  };
  searchParams: {
    q?: string;
    sort?: 'new' | 'popular' | 'trending';
    page?: string;
    price_min?: string;
    price_max?: string;
  };
}

export default async function SearchPage({
  params,
  searchParams
}: SearchPageProps) {
  const { category } = params;
  const {
    q: query,
    sort = 'new',
    page = '1',
    price_min,
    price_max
  } = searchParams;

  // 构建搜索参数
  const searchOptions = {
    category,
    query,
    sort,
    page: parseInt(page, 10),
    priceRange: {
      min: price_min ? parseInt(price_min, 10) : undefined,
      max: price_max ? parseInt(price_max, 10) : undefined,
    }
  };

  const results = await searchProducts(searchOptions);

  return (
    <div>
      <h1>Search Results for {category}</h1>
      {query && <p>Query: "{query}"</p>}
      <p>Sort by: {sort}</p>
      <p>Page: {page}</p>

      <ProductList products={results.products} />
      <Pagination
        current={page}
        total={results.totalPages}
        category={category}
        searchParams={searchParams}
      />
    </div>
  );
}

// 生成静态参数
export async function generateStaticParams() {
  const categories = await fetchCategories();

  return categories.map((category: Category) => ({
    category: category.slug,
  }));
}

// 生成元数据
export async function generateMetadata({
  params,
  searchParams
}: SearchPageProps) {
  const { category } = params;
  const query = searchParams.q;

  return {
    title: query
      ? `Search: ${query} in ${category}`
      : `Browse ${category}`,
    description: `Find the best ${category} products${query ? ` matching "${query}"` : ''}`,
  };
}
```

## 📋 实用工具函数

### 路由工具
**常用的路由操作函数**

```typescript
// utils/routing.ts
import { redirect } from 'next/navigation';
import { headers } from 'next/headers';

// 获取当前 URL
export function getCurrentUrl() {
  const headersList = headers();
  const host = headersList.get('host');
  const protocol = process.env.NODE_ENV === 'production' ? 'https' : 'http';
  return `${protocol}://${host}`;
}

// 安全重定向
export function safeRedirect(url: string, fallback = '/') {
  try {
    const { hostname } = new URL(url);
    const allowedHosts = [
      'localhost',
      'yourdomain.com',
      'www.yourdomain.com',
    ];

    if (allowedHosts.includes(hostname)) {
      redirect(url);
    } else {
      redirect(fallback);
    }
  } catch {
    redirect(fallback);
  }
}

// 构建查询字符串
export function buildQueryString(params: Record<string, any>) {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      searchParams.set(key, String(value));
    }
  });

  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : '';
}

// 合并查询参数
export function mergeQueryParams(
  currentParams: string,
  newParams: Record<string, any>
) {
  const searchParams = new URLSearchParams(currentParams);

  Object.entries(newParams).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      searchParams.set(key, String(value));
    }
  });

  return searchParams.toString();
}

// 分页链接生成
export function generatePaginationLinks(
  currentPage: number,
  totalPages: number,
  basePath: string
) {
  const links = [];

  // 上一页
  if (currentPage > 1) {
    links.push({
      label: 'Previous',
      href: `${basePath}?page=${currentPage - 1}`,
      active: false,
    });
  }

  // 页码
  for (let i = 1; i <= totalPages; i++) {
    if (
      i === 1 ||
      i === totalPages ||
      (i >= currentPage - 1 && i <= currentPage + 1)
    ) {
      links.push({
        label: String(i),
        href: `${basePath}?page=${i}`,
        active: i === currentPage,
      });
    } else if (i === currentPage - 2 || i === currentPage + 2) {
      links.push({
        label: '...',
        href: '#',
        active: false,
        disabled: true,
      });
    }
  }

  // 下一页
  if (currentPage < totalPages) {
    links.push({
      label: 'Next',
      href: `${basePath}?page=${currentPage + 1}`,
      active: false,
    });
  }

  return links;
}

// 使用示例
function ProductPagination({
  currentPage,
  totalPages,
  category,
  searchParams,
}: {
  currentPage: number;
  totalPages: number;
  category: string;
  searchParams: Record<string, any>;
}) {
  const basePath = `/search/${category}`;
  const links = generatePaginationLinks(currentPage, totalPages, basePath);

  return (
    <nav className="pagination">
      {links.map((link, index) => (
        <Link
          key={index}
          href={link.disabled ? '#' : link.href}
          className={`pagination-link ${link.active ? 'active' : ''} ${
            link.disabled ? 'disabled' : ''
          }`}
        >
          {link.label}
        </Link>
      ))}
    </nav>
  );
}
```

## 📖 总结

Next.js 15 的路由系统提供了强大而灵活的功能，支持从简单的静态页面到复杂的动态应用的所有需求。

### 关键要点：
1. **文件系统路由**: 基于文件夹结构自动生成路由
2. **动态路由**: 使用方括号创建动态参数
3. **布局系统**: 支持嵌套布局和共享布局
4. **导航**: Link 组件用于客户端导航，useRouter Hook 用于程序化导航
5. **高级模式**: 支持路由组、并行路由、拦截路由等高级功能
6. **中间件**: 在请求处理过程中执行代码

掌握这些路由概念和 API 将帮助你构建结构清晰、性能优秀的 Next.js 应用。