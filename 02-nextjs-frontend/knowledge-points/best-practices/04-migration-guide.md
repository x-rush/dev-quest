# Next.js 迁移指南

## 📚 概述

技术迁移是项目开发中的常见需求。本指南涵盖了从其他框架到 Next.js、Next.js 版本升级、架构迁移等各种迁移场景的最佳实践和详细步骤。

## 🔄 框架迁移

### 从 Create React App 迁移
**CRA 到 Next.js 的平滑迁移**

```typescript
// 步骤 1: 创建 Next.js 项目
// npx create-next-app@latest my-next-app --typescript

// 步骤 2: 迁移组件结构
// 原 CRA 项目结构
// src/
// ├── components/
// ├── pages/
// ├── hooks/
// ├── utils/
// └── App.tsx

// 迁移到 Next.js 结构
// src/
// ├── app/
// │   ├── layout.tsx
// │   ├── page.tsx
// │   └── api/
// ├── components/
// ├── hooks/
// ├── utils/
// └── styles/

// 步骤 3: 迁移路由
// 原有的 React Router 路由
// src/pages/HomePage.tsx
// src/pages/AboutPage.tsx
// src/pages/ContactPage.tsx

// 迁移到 Next.js App Router
// src/app/page.tsx (对应 HomePage)
// src/app/about/page.tsx (对应 AboutPage)
// src/app/contact/page.tsx (对应 ContactPage)

// 步骤 4: 迁移 API 路由
// 原 API 调用
// const fetchUsers = async () => {
//   const response = await fetch('/api/users');
//   return response.json();
// };

// 迁移到 Next.js API Routes
// src/app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
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

// 步骤 5: 迁移环境变量
// .env.local (CRA)
// REACT_APP_API_URL=http://localhost:3001
// REACT_APP_ENVIRONMENT=development

// .env.local (Next.js)
// NEXT_PUBLIC_API_URL=http://localhost:3001
// NODE_ENV=development

// 使用环境变量的差异
// CRA: process.env.REACT_APP_*
// Next.js: process.env.NEXT_PUBLIC_*

// 步骤 6: 迁移样式和资源
// public/ 目录保持不变
// src/ 目录保持不变

// 步骤 7: 迁移构建脚本
// package.json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }
}

// 迁移检查清单
const migrationChecklist = {
  // 功能验证
  features: [
    '✅ 页面渲染正常',
    '✅ 路由导航正常',
    '✅ API 调用正常',
    '✅ 样式加载正常',
    '✅ 环境变量正常',
  ],

  // 性能检查
  performance: [
    '✅ 首页加载速度',
    '✅ 页面转换速度',
    '✅ API 响应速度',
    '✅ Bundle 大小优化',
  ],

  // SEO 检查
  seo: [
    '✅ 页面标题正确',
    '✅ Meta 标签完整',
    '✅ Open Graph 标签',
    '✅ 结构化数据',
  ],
};
```

### 从 Vue/React Native 迁移
**跨框架迁移策略**

```typescript
// 1. 概念映射
// Vue 组件概念 -> React 组件概念
// Vue Template -> JSX
// Vue Props -> React Props
// Vue Events -> React Props + Callbacks
// Vue Watch -> useEffect + useState
// Vue Computed -> useMemo
// Vue Router -> Next.js 路由

// 2. 组件迁移示例
// Vue 组件
// <template>
//   <div class="user-card">
//     <img :src="user.avatar" :alt="user.name" />
//     <h2>{{ user.name }}</h2>
//     <p>{{ user.email }}</p>
//     <button @click="followUser">{{ isFollowing ? 'Unfollow' : 'Follow' }}</button>
//   </div>
// </template>

// <script setup lang="ts">
// import { ref, computed } from 'vue';

// interface User {
//   id: string;
//   name: string;
//   email: string;
//   avatar: string;
// }

// const props = defineProps<{
//   user: User;
// }>();

// const isFollowing = ref(false);

// const displayName = computed(() => props.user.name || 'Unknown');

// const followUser = () => {
//   isFollowing.value = !isFollowing.value;
// };
// </script>

// 迁移到 React 组件
import { useState, useMemo, useCallback } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  avatar: string;
}

interface UserCardProps {
  user: User;
}

export function UserCard({ user }: UserCardProps) {
  const [isFollowing, setIsFollowing] = useState(false);

  const displayName = useMemo(() => {
    return user.name || 'Unknown';
  }, [user.name]);

  const handleFollowUser = useCallback(() => {
    setIsFollowing(prev => !prev);
  }, []);

  return (
    <div className="user-card">
      <img src={user.avatar} alt={user.name} />
      <h2>{displayName}</h2>
      <p>{user.email}</p>
      <button onClick={handleFollowUser}>
        {isFollowing ? 'Unfollow' : 'Follow'}
      </button>
    </div>
  );
}

// 3. 生命周期迁移
// Vue Options API -> React Hooks
// Vue beforeCreate/created -> constructor/useEffect
// Vue mounted -> useEffect with empty dependency array
// Vue beforeDestroy/unmounted -> useEffect cleanup
// Vue updated -> useEffect with dependencies

// 4. 状态管理迁移
// Vuex/Pinia -> Context API + useReducer/Zustand
```

### 从 Gatsby 迁移
**静态站点生成器迁移**

```typescript
// Gatsby 页面组件
// exports.createPage = async ({ graphql }) => {
//   const result = await graphql(`
//     query {
//       allMarkdownRemark {
//       edges {
//         node {
//           frontmatter {
//             title
//             date
//           }
//           html
//           excerpt
//         }
//       }
//     }
//   `);

//   return {
//     props: {
//       posts: result.data.allMarkdownRemark.edges,
//     },
//   };
// };

// const BlogPage = ({ data, pageContext }) => {
//   const posts = data.allMarkdownRemark.edges;

//   return (
//     <Layout>
//       <h1>Blog</h1>
//       <div className="posts-grid">
//         {posts.map(({ node }) => (
//           <article key={node.id}>
//             <h2>{node.frontmatter.title}</h2>
//             <p>{node.frontmatter.date}</p>
//             <div dangerouslySetInnerHTML={{ __html: node.html }} />
//           </article>
//         ))}
//       </div>
//     </Layout>
//   );
// };

// 迁移到 Next.js SSG
// app/blog/page.tsx
import { GetStaticProps } from 'next';
import { getAllPosts, getPostBySlug } from '@/lib/posts';

interface BlogPageProps {
  posts: {
    slug: string;
    frontmatter: {
      title: string;
      date: string;
    };
    content: string;
  }[];
}

export default function BlogPage({ posts }: BlogPageProps) {
  return (
    <div className="container">
      <h1>Blog</h1>
      <div className="posts-grid">
        {posts.map((post) => (
          <article key={post.slug}>
            <h2>{post.frontmatter.title}</h2>
            <p>{post.frontmatter.date}</p>
            <div dangerouslySetInnerHTML={{ __html: post.content }} />
          </article>
        ))}
      </div>
    </div>
  );
}

export const getStaticProps: GetStaticProps = async () => {
  const posts = getAllPosts([
    'title',
    'date',
    'slug',
    'content',
  ]);

  return {
    props: {
      posts,
    },
    revalidate: 3600, // 1 hour
  };
};
```

## 📈 版本升级

### Next.js 13 -> 14 升级
**App Router 和新特性升级**

```typescript
// 1. 升级依赖
// package.json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "typescript": "^5.0.0"
  }
}

// 2. 迁移 App Router
// 旧的 pages 路由
// pages/index.tsx
// pages/about.tsx
// pages/blog/[slug].tsx

// 新的 App Router
// app/layout.tsx (根布局)
// app/page.tsx (首页)
// app/about/page.tsx (关于页)
// app/blog/[slug]/page.tsx (博客文章)

// 3. 迁移布局
// _app.tsx (Next.js 12)
// export default function App({ Component, pageProps }: AppProps) {
//   return (
//     <Layout>
//       <Component {...pageProps} />
//     </Layout>
//   );
// }

// app/layout.tsx (Next.js 13+)
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'My App',
  description: 'Welcome to my Next.js app',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

// 4. 迁移数据获取
// getStaticProps/getServerSideProps -> async 函数
// pages/index.tsx (Next.js 12)
export async function getStaticProps() {
  const posts = await getPosts();

  return {
    props: {
      posts,
    },
  };
}

// app/page.tsx (Next.js 13+)
async function HomePage() {
  const posts = await getPosts();

  return (
    <div>
      <h1>Blog</h1>
      <PostList posts={posts} />
    </div>
  );
}

// 5. 迁移中间件
// middleware.js (Next.js 12)
// export function middleware(request) {
//   // 中间件逻辑
// }

// middleware.ts (Next.js 13+)
import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  // 中间件逻辑
  return NextResponse.next();
}

export const config = {
  matcher: ['/about/:path*', '/dashboard/:path*'],
};
```

### Next.js 14 -> 15 升级
**最新特性和升级策略**

```typescript
// 1. 升级依赖
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  }
}

// 2. 使用新的 React 19 特性
// app/components/Form.tsx
import { useFormStatus, useFormState } from 'react-dom';

export function ContactForm() {
  const [state, formAction, isPending] = useFormState(async (prevState, formData) => {
    try {
      const response = await submitContactForm(formData);
      return { success: true, message: 'Form submitted successfully!' };
    } catch (error) {
      return { success: false, message: error.message };
    }
  });

  return (
    <form action={formAction}>
      <input type="text" name="name" required />
      <input type="email" name="email" required />
      <textarea name="message" required />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Submitting...' : 'Submit'}
      </button>

      {state.message && (
        <p className={state.success ? 'text-green-600' : 'text-red-600'}>
          {state.message}
        </p>
      )}
    </form>
  );
}

// 3. 使用 Server Actions
// app/actions/actions.ts
'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string;
  const content = formData.get('content') as string;

  try {
    // 数据库操作
    const post = await savePost({ title, content });

    // 重新验证缓存
    revalidatePath('/posts');
    revalidatePath('/');

    // 重定向到新帖子
    redirect(`/posts/${post.id}`);
  } catch (error) {
    throw new Error('Failed to create post');
  }
}

// 4. 优化性能特性
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // Turbopack
    turbo: {
      // Turbopack 配置
    },
    // 优化包导入
    optimizePackageImports: ['lucide-react', '@radix-ui/react-icons'],
  },
};

module.exports = nextConfig;
```

## 🏗️ 架构迁移

### CSR 到 SSR/SSG 迁移
**客户端渲染到服务端渲染**

```typescript
// 1. 分析现有组件
// 客户端渲染组件
import { useState, useEffect } from 'react';

function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser(userId)
      .then(setUser)
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>User not found</div>;

  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}

// 2. 迁移到 SSR
// pages/[id].tsx
import { GetServerSideProps } from 'next';
import { getUser } from '@/lib/api';

export default function UserProfile({ user }: { user: User }) {
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}

export const getServerSideProps: GetServerSideProps = async ({ params }) => {
  const user = await getUser(params.id);

  if (!user) {
    return {
      notFound: true,
    };
  }

  return {
    props: {
      user,
    },
  };
}

// 3. 迁移到 SSG
// pages/[id].tsx
import { GetStaticProps, GetStaticPaths } from 'next';
import { getUser, getUserSlugs } from '@/lib/api';

export default function UserProfile({ user }: { user: User }) {
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}

export const getStaticPaths: GetStaticPaths = async () => {
  const paths = await getUserSlugs();

  return {
    paths,
    fallback: 'blocking',
  };
};

export const getStaticProps: GetStaticProps = async ({ params }) => {
  const user = await getUser(params.id);

  if (!user) {
    return {
      notFound: true,
    };
  }

  return {
    props: {
      user,
    },
    revalidate: 3600, // 1 hour
  };
};
```

### Monorepo 迁移
**单体应用到 Monorepo 迁移**

```typescript
// 1. 创建 Turborepo 配置
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": [
    "next",
    "react",
    "react-dom",
    "typescript",
    "eslint",
    "prettier"
  ],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**"],
      "cache": true
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {
      "outputs": []
    },
    "test": {
      "outputs": ["coverage/**"],
      "cache": false
    }
  }
}

// 2. 重组目录结构
// monorepo/
// ├── apps/
// │   ├── web/ (Next.js 应用)
// │   └── mobile/ (React Native 应用)
// ├── packages/
// │   ├── ui/ (共享 UI 组件)
// │   ├── utils/ (共享工具函数)
//   │   └── types/ (共享类型定义)
// ├── tools/
// │   ├── eslint-config/
// │   └── tsconfig/
// └── package.json

// 3. 设置工作区
// package.json (根目录)
{
  "name": "monorepo",
  "private": true,
  "workspaces": [
    "apps/*",
    "packages/*"
  ],
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "lint": "turbo run lint",
    "test": "turbo run test"
  },
  "devDependencies": {
    "turbo": "latest",
    "@changesets/cli": "^2.26.0",
    "eslint": "^8.0.0",
    "prettier": "^3.0.0",
    "typescript": "^5.0.0"
  }
}

// 4. 更新应用引用
// apps/web/package.json
{
  "name": "@monorepo/web",
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "@monorepo/ui": "workspace:*",
    "@monorepo/utils": "workspace:*",
    "@monorepo/types": "workspace:*"
  }
}

// apps/web/app/page.tsx
import { Button } from '@monorepo/ui';
import { formatDate } from '@monorepo/utils';
import type { User } from '@monorepo/types';

export default function HomePage() {
  return (
    <div>
      <Button onClick={() => console.log('Clicked')}>
        Click me
      </Button>
    </div>
  );
}
```

## 🔧 数据迁移

### 数据库迁移
**安全的数据结构迁移**

```typescript
// lib/database/migrations/migration-manager.ts
import { Client } from 'pg';
import { Migration } from './migration';

export class MigrationManager {
  private client: Client;
  private migrations: Migration[] = [];

  constructor(client: Client) {
    this.client = client;
  }

  registerMigration(migration: Migration): void {
    this.migrations.push(migration);
  }

  async runMigrations(): Promise<void> {
    console.log('🚀 Starting database migrations...');

    try {
      // 创建迁移记录表
      await this.createMigrationsTable();

      // 获取已执行的迁移
      const executedMigrations = await this.getExecutedMigrations();

      for (const migration of this.migrations) {
        if (!executedMigrations.includes(migration.id)) {
          console.log(`📋 Running migration: ${migration.name}`);

          // 开始事务
          await this.client.query('BEGIN');

          try {
            await migration.up(this.client);
            await this.markMigrationExecuted(migration.id);
            await this.client.query('COMMIT');

            console.log(`✅ Migration completed: ${migration.name}`);
          } catch (error) {
            await this.client.query('ROLLBACK');
            throw error;
          }
        }
      }

      console.log('✅ All migrations completed successfully');
    } catch (error) {
      console.error('❌ Migration failed:', error);
      throw error;
    }
  }

  private async createMigrationsTable(): Promise<void> {
    await this.client.query(`
      CREATE TABLE IF NOT EXISTS migrations (
        id VARCHAR(255) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
  }

  private async getExecutedMigrations(): Promise<string[]> {
    const result = await this.client.query(
      'SELECT id FROM migrations'
    );
    return result.rows.map(row => row.id);
  }

  private async markMigrationExecuted(migrationId: string): Promise<void> {
    await this.client.query(
      'INSERT INTO migrations (id, name) VALUES ($1, $2) ON CONFLICT (id) DO NOTHING',
      [migrationId, migrationId]
    );
  }
}

// lib/database/migrations/migration.ts
export interface Migration {
  id: string;
  name: string;
  up: (client: Client) => Promise<void>;
  down?: (client: Client) => Promise<void>;
}

// 迁移示例
// lib/database/migrations/001_create_users_table.ts
import { Client } from 'pg';

export const migration: Migration = {
  id: '001_create_users_table',
  name: 'Create users table',

  async up(client: Client): Promise<void> {
    await client.query(`
      CREATE TABLE users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        email VARCHAR(255) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
  },

  async down(client: Client): Promise<void> {
    await client.query('DROP TABLE IF EXISTS users');
  },
};
```

### API 版本迁移
**渐进式 API 升级**

```typescript
// lib/api/versioning.ts
import { NextRequest, NextResponse } from 'next/server';

interface APIVersion {
  version: string;
  handler: (request: NextRequest) => Promise<NextResponse>;
  deprecated?: boolean;
  deprecationDate?: Date;
}

export class APIVersioning {
  private versions: Map<string, APIVersion> = new Map();

  constructor() {
    this.registerVersion('v1', {
      version: '1.0.0',
      handler: this.handleV1Request,
    });
    this.registerVersion('v2', {
      version: '2.0.0',
      handler: this.handleV2Request,
    });
  }

  registerVersion(version: string, config: Omit<APIVersion, 'version'>): void {
    this.versions.set(version, config);
  }

  getVersion(request: NextRequest): APIVersion | null {
    const pathname = request.nextUrl.pathname;
    const versionMatch = pathname.match(/^\/api\/v(\d+)/);

    if (versionMatch) {
      const version = versionMatch[1];
      return this.versions.get(`v${version}`);
    }

    return this.versions.get('v1'); // 默认版本
  }

  async handleRequest(request: NextRequest): Promise<NextResponse> {
    const version = this.getVersion(request);

    if (!version) {
      return NextResponse.json(
        { error: 'Unsupported API version' },
        { status: 400 }
      );
    }

    // 添加版本响应头
    const response = await version.handler(request);
    response.headers.set('API-Version', version.version);

    // 添加弃用警告
    if (version.deprecated) {
      response.headers.set(
        'Deprecation-Warning',
        `This API version is deprecated. Please upgrade to a newer version.`
      );
    }

    return response;
  }

  private async handleV1Request(request: NextRequest): Promise<NextResponse> {
    return NextResponse.json({
      message: 'API v1',
      data: [],
    });
  }

  private async handleV2Request(request: NextRequest): Promise<NextResponse> {
    return NextResponse.json({
      message: 'API v2',
      data: [],
    });
  }
}

// app/api/[...]/route.ts
import { APIVersioning } from '@/lib/api/versioning';

const versioning = new APIVersioning();

export async function GET(request: NextRequest) {
  return versioning.handleRequest(request);
}

export async function POST(request: NextRequest) {
  return versioning.handleRequest(request);
}
```

## 📱 迁移工具

### 迁移脚本
**自动化迁移脚本**

```typescript
// scripts/migration-helper.ts
import { execSync } from 'child_process';
import { existsSync, readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

interface MigrationConfig {
  source: string;
  target: string;
  patterns: {
    [key: string]: string | RegExp;
  };
  replacements: {
    [key: string]: string | ((match: string) => string);
  };
}

export class MigrationHelper {
  private config: MigrationConfig;

  constructor(config: MigrationConfig) {
    this.config = config;
  }

  runMigration(): void {
    console.log('🔄 Starting migration...');

    try {
      // 备份原始文件
      this.backupFiles();

      // 执行文件转换
      this.transformFiles();

      // 更新配置文件
      this.updateConfigs();

      // 清理临时文件
      this.cleanup();

      console.log('✅ Migration completed successfully!');
    } catch (error) {
      console.error('❌ Migration failed:', error);
      this.rollback();
    }
  }

  private backupFiles(): void {
    const backupDir = '.migration-backup';

    if (!existsSync(backupDir)) {
      execSync(`mkdir -p ${backupDir}`);
    }

    console.log('📦 Backing up files...');
    execSync(`cp -r ${this.config.source} ${backupDir}`);
  }

  private transformFiles(): void {
    const files = this.getFiles(this.config.source);

    for (const file of files) {
      this.transformFile(file);
    }
  }

  private getFiles(dir: string): string[] {
    const files: string[] = [];
    const items = execSync(`find ${dir} -type f`).toString().split('\n');

    items.forEach(item => {
      if (item.trim()) {
        files.push(item);
      }
    });

    return files;
  }

  private transformFile(filePath: string): void {
    let content = readFileSync(filePath, 'utf8');
    const relativePath = filePath.replace(this.config.source, '');

    // 检查文件是否匹配模式
    const shouldTransform = Object.entries(this.config.patterns).some(
      ([pattern]) => {
        if (typeof pattern === 'string') {
          return relativePath.includes(pattern);
        }
        return pattern.test(relativePath);
      }
    );

    if (!shouldTransform) return;

    // 执行替换
    Object.entries(this.config.replacements).forEach(([pattern, replacement]) => {
      if (typeof replacement === 'string') {
        content = content.replace(new RegExp(pattern, 'g'), replacement);
      } else {
        content = content.replace(new RegExp(pattern, 'g'), replacement);
      }
    });

    const targetPath = filePath.replace(this.config.source, this.config.target);
    const targetDir = require('path').dirname(targetPath);

    if (!existsSync(targetDir)) {
      execSync(`mkdir -p ${targetDir}`);
    }

    writeFileSync(targetPath, content);
  }

  private updateConfigs(): void {
    // 更新 package.json
    this.updatePackageJson();

    // 更新 tsconfig.json
    this.updateTsConfig();
  }

  private updatePackageJson(): void {
    const packageJsonPath = join(this.config.target, 'package.json');

    if (existsSync(packageJsonPath)) {
      const packageJson = JSON.parse(readFileSync(packageJsonJson, 'utf8'));

      // 更新依赖版本
      if (packageJson.dependencies) {
        packageJson.dependencies.next = '^15.0.0';
        packageJson.dependencies.react = '^19.0.0';
      }

      if (packageJson.devDependencies) {
        packageJson.devDependencies.typescript = '^5.0.0';
      }

      // 更新脚本
      if (packageJson.scripts) {
        packageJson.scripts.dev = 'next dev';
        packageJson.scripts.build = 'next build';
      }

      writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));
    }
  }

  private updateTsConfig(): void {
    const tsConfigPath = join(this.config.target, 'tsconfig.json');

    if (existsSync(tsConfigPath)) {
      let content = readFileSync(tsConfigPath, 'utf8');

      // 更新配置
      content = content.replace(
        '"target": "es5"',
        '"target": "es2020"'
      );

      writeFileSync(tsConfigPath, content);
    }
  }

  private cleanup(): void {
    console.log('🧹 Cleaning up...');
    // 清理临时文件和备份
  }

  private rollback(): void {
    console.log('🔙 Rolling back changes...');

    try {
      execSync(`rm -rf ${this.config.target}`);
      execSync(`mv .migration-backup ${this.config.target}`);
      console.log('✅ Rollback completed');
    } catch (error) {
      console.error('❌ Rollback failed:', error);
    }
  }
}

// 使用示例
// scripts/migrate-to-next15.ts
import { MigrationHelper } from './migration-helper';

const migration = new MigrationHelper({
  source: './old-project',
  target: './next-project',
  patterns: {
    'component.ts': 'component.tsx',
    'page.js': 'page.tsx',
    'api': 'app/api',
  },
  replacements: {
    'from \'react\'': 'from \'react\'',
    'useState, useEffect': 'import { useState, useEffect } from \'react\'',
    'export default function': 'export default function',
    'componentDidMount': 'useEffect(() => {}, [])',
    'this.state =': 'const [state, setState] = useState(',
    'this.setState(': 'setState(',
    'render() {': 'return (',
  },
});

migration.runMigration();
```

### 测试验证
**迁移后的测试验证**

```typescript
// scripts/migration-tests.ts
import { execSync } from 'child_process';
import { existsSync } from 'fs';

interface TestCase {
  name: string;
  test: () => boolean | Promise<boolean>;
  expected: string;
}

export class MigrationTests {
  private tests: TestCase[] = [
    {
      name: 'Check if Next.js build works',
      test: () => {
        try {
          execSync('npm run build', { stdio: 'pipe' });
          return true;
        } catch {
          return false;
        }
      },
      expected: 'Next.js build should complete successfully',
    },
    {
      name: 'Check if TypeScript compilation works',
      test: () => {
        try {
          execSync('npx tsc --noEmit', { stdio: 'pipe' });
          return true;
        } catch {
          return false;
        }
      },
      expected: 'TypeScript compilation should complete without errors',
    },
    {
      name: 'Check if all pages exist',
      test: () => {
        const requiredPages = [
          'app/page.tsx',
          'app/layout.tsx',
        ];

        return requiredPages.every(page =>
          existsSync(`src/${page}`)
        );
      },
      expected: 'All required pages should exist',
    },
    {
      name: 'Check if API routes work',
      test: async () => {
        try {
          const response = await fetch('http://localhost:3000/api/test');
          return response.ok;
        } catch {
          return false;
        }
      },
      expected: 'API routes should respond correctly',
    },
  ];

  async runTests(): Promise<boolean> {
    console.log('🧪 Running migration tests...');

    let allPassed = true;

    for (const test of this.tests) {
      console.log(`📋 Testing: ${test.name}`);

      try {
        const result = await test.test();
        if (result) {
          console.log(`✅ ${test.test.expected}`);
        } else {
          console.log(`❌ ${test.test.expected}`);
          allPassed = false;
        }
      } catch (error) {
        console.log(`❌ ${test.test.expected} - ${error}`);
        allPassed = false;
      }
    }

    if (allPassed) {
      console.log('✅ All tests passed! Migration successful.');
    } else {
      console.log('❌ Some tests failed. Please check the migration.');
    }

    return allPassed;
  }
}

// 使用示例
// scripts/test-migration.ts
import { MigrationTests } from './migration-tests';

async function testMigration() {
  const tests = new MigrationTests();
  const passed = await tests.runTests();

  process.exit(passed ? 0 : 1);
}

testMigration();
```

## 📋 迁移检查清单

### 迁移前准备
- [ ] 备份现有代码
- [ ] 创建迁移计划
- [ ] 准备测试环境
- [ ] 确保依赖可用
- [ ] 制定回滚计划

### 数据迁移
- [ ] 数据库备份
- [ ] 迁移脚本测试
- [ ] 数据验证
- [] 性能测试
- [ ] 回滚方案验证

### 代码迁移
- [ ] 语法兼容性检查
- **组件迁移测试**
- [ ] 路由迁移验证
- [ ] 状态管理迁移
- [ ] API 接口测试
- [ ] 样式文件更新

### 功能验证
- [ ] 核心功能测试
- [ ] 用户界面验证
- [ ] API 响应测试
- [ ] 性能指标对比
- [ ] 兼容性测试
- [ ] 安全性验证

### 部署验证
- [ ] 生产环境测试
- [ ] 监控指标检查
- [ ] 错误日志验证
- [ ] 回滚流程测试
- [ ] 团队培训
- [ ] 文档更新

## 📖 总结

迁移项目是一个复杂的过程，需要 careful planning 和执行：

### 迁移策略：
1. **评估分析**: 全面评估现有系统
2. **制定计划**: 详细迁移计划和路线图
3. **准备充分**: 备份、测试环境、工具准备
4. **分步执行**: 渐进式迁移降低风险
5. **充分测试**: 多层次测试确保质量
6. **监控支持**: 实时监控和快速响应

### 关键要点：
1. **数据安全**: 数据备份和迁移安全
2. **功能完整**: 迁移后功能完整
3. **性能优化**: 迁移后性能提升
4. **用户体验**: 保持良好的用户体验
5. **团队协作**: 充分的沟通和培训

### 工具支持：
1. **迁移脚本**: 自动化迁移工具
2. **测试工具**: 验证迁移结果
3. **监控工具**: 监控迁移过程
4. **文档工具**: 更新项目文档
5. **回滚工具**: 快速回滚机制

通过系统性的迁移流程，可以大大降低迁移风险，确保项目平稳过渡到新的技术栈。记住，迁移是一个过程，需要持续的关注和优化。