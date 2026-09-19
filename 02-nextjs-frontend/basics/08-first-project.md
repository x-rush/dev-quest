# Next.js 16 第一个完整项目实战指南

## 首次交付入口：先完成浏览器文章草稿

本章后半部分的认证、数据库与评论属于博客扩展，不能作为第一次交付的前置。初学者先完成本节：在同一浏览器保存文章标题、拒绝空白输入、刷新后读回。这里的存储是当前站点的 `localStorage`，不是服务端数据库；换浏览器、换站点地址或清除站点数据后不会共享草稿。

**开工条件**：先按[第一个应用](./02-first-nextjs-app.md)启动自己的 App Router 工程，能打开模板页面；会 `useState`、受控输入和 `try/catch`，不熟时返回[状态管理](./07-state-management.md)。保留工程生成的根布局和锁文件，不需要先安装正文中的认证或数据库依赖。

在现有路由根目录新建 `drafts/page.tsx`：采用 `src/app` 的工程放在 `src/app/drafts/page.tsx`，采用 `app` 的工程放在 `app/drafts/page.tsx`，二者只选一个。完整内容如下：

```tsx
'use client'

import { useState } from 'react'

const storageKey = 'dev-quest-article-drafts-v1'

export default function DraftsPage() {
  const [titles, setTitles] = useState<string[]>([])
  const [draft, setDraft] = useState('')
  const [ready, setReady] = useState(false)
  const [message, setMessage] = useState('先读取已有草稿，再新增。')

  function load() {
    try {
      const raw = localStorage.getItem(storageKey)
      const saved: unknown = raw === null ? [] : JSON.parse(raw)
      if (!Array.isArray(saved) || !saved.every(
        (title): title is string => typeof title === 'string' && title.trim().length > 0,
      )) throw new Error('草稿格式无效')
      setTitles(saved)
      setReady(true)
      setMessage('读取成功。')
    } catch {
      setReady(false)
      setMessage('读取失败：检查站点存储权限或已有草稿格式；未覆盖原数据。')
    }
  }

  function save() {
    if (!ready) return
    const title = draft.trim()
    if (!title) {
      setMessage('标题不能为空。')
      return
    }
    const next = [...titles, title]
    try {
      localStorage.setItem(storageKey, JSON.stringify(next))
      setTitles(next)
      setDraft('')
      setMessage('保存成功。')
    } catch {
      setMessage('保存失败：输入与已有列表已保留，请检查站点存储后重试。')
    }
  }

  return (
    <main>
      <h1>文章草稿</h1>
      <button onClick={load}>读取已有草稿</button>
      <form onSubmit={(event) => { event.preventDefault(); save() }}>
        <label htmlFor="draft-title">文章标题</label>
        <input id="draft-title" value={draft}
          onChange={(event) => setDraft(event.target.value)} />
        <button type="submit" disabled={!ready}>保存标题</button>
      </form>
      <p role="status">{message}</p>
      {!ready ? <p>尚未读取存储。</p> : titles.length === 0 ? <p>暂无草稿。</p> : (
        <ul>{titles.map((title, index) => <li key={index}>{title}</li>)}</ul>
      )}
    </main>
  )
}
```

这里刻意用按钮触发读取：浏览器存储仅在浏览器事件里访问，首次服务端渲染不读取它；读取成功前禁止写入，避免把尚未加载的旧草稿覆盖为空列表。此练习只追加标题，不提供排序或删除，所以暂用数组位置作列表键；增加编辑、删除时应先引入稳定 ID。练习只验收单标签页，多标签页同时写入的冲突留到后续设计。

沿用工程的启动命令（npm 工程为 `npm run dev`），打开终端显示的本地地址下的 `/drafts`。交付这个页面、工程锁文件和下表的实际结果；本节没有附带已运行的浏览器验收记录。

| 操作 | 通过条件 | 失败时回查 |
|---|---|---|
| 首次打开后点击读取 | 没有保存记录时显示“暂无草稿”，保存按钮可用 | 路由 404 查[布局路由](./04-layouts-routing.md)的路由根目录；读取失败查看浏览器站点存储 |
| 保存 A、B，再提交三个空格 | 只有 A、B；空白输入提示错误，不增加记录 | 查[状态管理](./07-state-management.md)中的受控输入，确认提交前执行 `trim()` |
| 刷新页面，再点击读取 | A、B 恢复，能说明恢复来自本地存储 | 确认地址、端口和浏览器未变化；查[Web 平台 API](../reference/language-concepts/10-web-platform-apis.md)中的 Storage |
| 在开发者工具 Application/Storage 中把本练习键的值暂改成 `not-json`，再读取 | 显示读取失败，保存禁用，原值未被覆盖 | 检查 `JSON.parse` 和格式校验是否位于同一个 `try/catch`；测试后仅恢复这个键原先备份的值 |

**下一步**：通过后先按[布局路由](./04-layouts-routing.md)为草稿增加稳定 ID 和详情页，再按[数据获取](./06-data-fetching-basics.md)把读取替换成服务端接口。需要跨浏览器共享时才进入下方博客扩展并接数据库，分别重做写入失败与服务重启验收；本地草稿通过不代表认证、权限或服务端持久化已经完成。

## 博客扩展：按需求选做

## 先理解，再动手

第一个应用的目标是把一条数据链路走通。页面数量、库数量和目录层次不是完成标准。

**本节自测**：先只做列表与详情，再加入一个写操作；每步记录正常、空和失败结果。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

没有后端时明确使用模拟数据；能在同一页面临时添加不等于重启后仍有数据。

</details>

> **文档简介**: Next.js 16 从零到一完整项目实战教程，整合前面所学知识，构建一个功能完整的现代化Web应用

> **目标读者**: 完成基础学习的开发者，需要实战项目经验的前端工程师

> **前置知识**: Next.js基础、React组件、TypeScript、Tailwind CSS、数据获取、状态管理

> **预计时长**: 6-8小时

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `basics` |
| **难度** | ⭐⭐ |
| **标签** | `#project` `#full-stack` `#real-world` `#integration` `#deployment` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 🎯 学习目标

### 🚀 项目构建能力
- 整合前面所学的所有Next.js 16知识点
- 构建一个功能完整的现代化Web应用
- 掌握项目架构设计和最佳实践
- 学会代码组织和项目维护

### 🛠️ 实际开发技能
- 实现用户认证和权限管理
- 构建CRUD操作和数据管理
- 掌握响应式设计和用户体验优化
- 学会项目部署和监控

## 📖 概述

本教程将带你从零开始构建一个完整的博客平台，整合Next.js 16、React 19、TypeScript 7、Tailwind CSS 4等现代技术栈，涵盖用户认证、文章管理、评论系统、搜索功能等核心特性。

## 🏗️ 项目规划和设计

### 项目功能需求

```typescript
// src/types/project.ts
export interface ProjectRequirements {
  // 用户管理
  userManagement: {
    userRegistration: '用户注册和邮箱验证'
    userAuthentication: '登录、登出和会话管理'
    userProfile: '个人资料编辑和头像上传'
    userRoles: '普通用户和管理员权限'
  }

  // 文章管理
  articleManagement: {
    articleCRUD: '文章的创建、读取、更新、删除'
    richTextEditor: '富文本编辑器支持'
    articleCategories: '文章分类和标签系统'
    draftManagement: '草稿保存和发布管理'
    articleSearch: '全文搜索和筛选功能'
  }

  // 评论系统
  commentSystem: {
    commentCRUD: '评论的增删改查'
    nestedComments: '多级回复支持'
    commentModeration: '评论审核和管理'
    realtimeComments: '实时评论更新'
  }

  // 用户体验
  userExperience: {
    responsiveDesign: '响应式设计适配'
    darkMode: '暗色模式支持'
    loadingStates: '加载状态和骨架屏'
    errorHandling: '错误处理和用户反馈'
    performanceOptimization: '性能优化和缓存'
  }
}

// 数据模型设计
export interface User {
  id: string
  email: string
  username: string
  displayName: string
  avatar?: string
  bio?: string
  role: 'user' | 'admin'
  isActive: boolean
  emailVerified: boolean
  createdAt: Date
  updatedAt: Date
}

export interface Article {
  id: string
  title: string
  slug: string
  content: string
  excerpt: string
  coverImage?: string
  authorId: string
  author: User
  categoryId: string
  category: Category
  tags: Tag[]
  status: 'draft' | 'published' | 'archived'
  publishedAt?: Date
  createdAt: Date
  updatedAt: Date
  viewCount: number
  likeCount: number
  commentCount: number
}

export interface Category {
  id: string
  name: string
  slug: string
  description?: string
  color: string
  articleCount: number
}

export interface Tag {
  id: string
  name: string
  slug: string
  articleCount: number
}

export interface Comment {
  id: string
  content: string
  authorId: string
  author: User
  articleId: string
  parentId?: string
  replies?: Comment[]
  status: 'pending' | 'approved' | 'rejected'
  createdAt: Date
  updatedAt: Date
  likeCount: number
}
```

### 项目架构设计

```
src/
├── app/                          # App Router页面
│   ├── (auth)/                  # 认证相关页面
│   │   ├── login/
│   │   ├── register/
│   │   └── verify-email/
│   ├── (dashboard)/             # 仪表板页面
│   │   ├── profile/
│   │   ├── my-articles/
│   │   └── settings/
│   ├── admin/                   # 管理员页面
│   │   ├── articles/
│   │   ├── users/
│   │   └── comments/
│   ├── articles/                # 文章相关页面
│   │   ├── [slug]/
│   │   ├── categories/
│   │   └── tags/
│   ├── api/                     # API路由
│   │   ├── auth/
│   │   ├── articles/
│   │   ├── comments/
│   │   └── upload/
│   ├── layout.tsx              # 根布局
│   ├── page.tsx                # 首页
│   ├── loading.tsx             # 全局加载
│   ├── error.tsx               # 全局错误
│   └── not-found.tsx           # 404页面
├── components/                  # 可复用组件
│   ├── ui/                     # 基础UI组件
│   ├── layout/                 # 布局组件
│   ├── forms/                  # 表单组件
│   ├── articles/               # 文章相关组件
│   └── auth/                   # 认证相关组件
├── hooks/                      # 自定义Hooks
├── lib/                        # 工具库
├── stores/                     # 状态管理
├── types/                      # TypeScript类型定义
└── styles/                     # 样式文件
```

## 🏠 项目初始化和配置

### 创建项目

```bash
# 使用create-next-app创建项目
npx create-next-app@latest blog-platform --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

cd blog-platform

# 安装额外依赖
npm install @next-auth/prisma-adapter prisma @prisma/client
npm install next-auth@beta
npm install @hookform/resolvers react-hook-form zod
npm install @tanstack/react-query @tanstack/react-query-devtools
npm install zustand immer
npm install lucide-react @radix-ui/react-dialog
npm install date-fns clsx tailwind-merge
npm install react-hot-toast react-syntax-highlighter
```

### 环境配置

```dotenv
// .env.local
# 数据库
DATABASE_URL="file:./dev.db"

# NextAuth.js
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-secret-key-here"

# 文件上传
UPLOAD_DIR="./public/uploads"
MAX_FILE_SIZE="5242880" # 5MB

# 邮件配置
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="your-email@gmail.com"
SMTP_PASS="your-app-password"
```

### 数据库配置

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "sqlite"
  url      = env("DATABASE_URL")
}

model User {
  id            String    @id @default(cuid())
  email         String    @unique
  username      String    @unique
  displayName   String
  avatar        String?
  bio           String?
  role          Role      @default(USER)
  isActive      Boolean   @default(true)
  emailVerified Boolean   @default(false)
  passwordHash  String
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  // 关系
  articles      Article[]
  comments      Comment[]
  accounts      Account[]
  sessions      Session[]

  @@map("users")
}

model Account {
  id                String  @id @default(cuid())
  userId            String
  type              String
  provider          String
  providerAccountId String
  refresh_token     String?
  access_token      String?
  expires_at        Int?
  token_type        String?
  scope             String?
  id_token          String?
  session_state     String?

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([provider, providerAccountId])
  @@map("accounts")
}

model Session {
  id           String   @id @default(cuid())
  sessionToken String   @unique
  userId       String
  expires      DateTime
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("sessions")
}

model Category {
  id            String   @id @default(cuid())
  name          String
  slug          String   @unique
  description   String?
  color         String   @default("#3B82F6")
  articleCount  Int      @default(0)
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt

  // 关系
  articles      Article[]

  @@map("categories")
}

model Tag {
  id           String   @id @default(cuid())
  name         String
  slug         String   @unique
  articleCount Int      @default(0)
  createdAt    DateTime @default(now())

  // 关系
  articles     ArticleTag[]

  @@map("tags")
}

model Article {
  id          String    @id @default(cuid())
  title       String
  slug        String    @unique
  content     String
  excerpt     String
  coverImage  String?
  authorId    String
  categoryId  String
  status      Status    @default(DRAFT)
  publishedAt DateTime?
  createdAt   DateTime  @default(now())
  updatedAt   DateTime  @updatedAt
  viewCount   Int       @default(0)
  likeCount   Int       @default(0)

  // 关系
  author      User      @relation(fields: [authorId], references: [id])
  category    Category  @relation(fields: [categoryId], references: [id])
  tags        ArticleTag[]
  comments    Comment[]

  @@map("articles")
}

model ArticleTag {
  articleId String
  tagId     String

  article Article @relation(fields: [articleId], references: [id], onDelete: Cascade)
  tag     Tag     @relation(fields: [tagId], references: [id], onDelete: Cascade)

  @@id([articleId, tagId])
  @@map("article_tags")
}

model Comment {
  id        String   @id @default(cuid())
  content   String
  authorId  String
  articleId String
  parentId  String?
  status    Status   @default(PENDING)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  likeCount Int      @default(0)

  // 关系
  author    User      @relation(fields: [authorId], references: [id])
  article   Article   @relation(fields: [articleId], references: [id], onDelete: Cascade)
  parent    Comment?  @relation("CommentReplies", fields: [parentId], references: [id])
  replies   Comment[] @relation("CommentReplies")

  @@map("comments")
}

enum Role {
  USER
  ADMIN
}

enum Status {
  DRAFT
  PUBLISHED
  ARCHIVED
  PENDING
  APPROVED
  REJECTED
}
```

## 🔐 用户认证系统

### NextAuth.js配置

```typescript
// src/lib/auth.ts
import { NextAuthOptions } from 'next-auth'
import { PrismaAdapter } from '@next-auth/prisma-adapter'
import CredentialsProvider from 'next-auth/providers/credentials'
import { prisma } from '@/lib/prisma'
import bcrypt from 'bcryptjs'

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(prisma),
  session: {
    strategy: 'jwt'
  },
  providers: [
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        const user = await prisma.user.findUnique({
          where: { email: credentials.email }
        })

        if (!user || !user.isActive) {
          return null
        }

        const isPasswordValid = await bcrypt.compare(
          credentials.password,
          user.passwordHash
        )

        if (!isPasswordValid) {
          return null
        }

        return {
          id: user.id,
          email: user.email,
          name: user.displayName,
          role: user.role
        }
      }
    })
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = user.role
      }
      return token
    },
    async session({ session, token }) {
      if (token) {
        session.user.id = token.sub!
        session.user.role = token.role as string
      }
      return session
    }
  },
  pages: {
    signIn: '/login',
    signUp: '/register'
  }
}
```

### 认证API路由

```typescript
// src/app/api/auth/[...nextauth]/route.ts
import NextAuth from 'next-auth'
import { authOptions } from '@/lib/auth'

const handler = NextAuth(authOptions)

export { handler as GET, handler as POST }

// src/app/api/auth/register/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import bcrypt from 'bcryptjs'
import { z } from 'zod'

const registerSchema = z.object({
  email: z.string().email(),
  username: z.string().min(3).max(20),
  displayName: z.string().min(1).max(50),
  password: z.string().min(6)
})

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email, username, displayName, password } = registerSchema.parse(body)

    // 检查用户是否已存在
    const existingUser = await prisma.user.findFirst({
      where: {
        OR: [
          { email },
          { username }
        ]
      }
    })

    if (existingUser) {
      return NextResponse.json(
        { error: '用户已存在' },
        { status: 400 }
      )
    }

    // 创建新用户
    const passwordHash = await bcrypt.hash(password, 12)

    const user = await prisma.user.create({
      data: {
        email,
        username,
        displayName,
        passwordHash,
        isActive: true,
        emailVerified: false // 需要邮箱验证
      },
      select: {
        id: true,
        email: true,
        username: true,
        displayName: true,
        role: true,
        createdAt: true
      }
    })

    // TODO: 发送验证邮件

    return NextResponse.json({
      message: '注册成功，请查收验证邮件',
      user
    }, { status: 201 })

  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: '输入数据无效', details: error.issues },
        { status: 400 }
      )
    }

    console.error('Registration error:', error)
    return NextResponse.json(
      { error: '注册失败' },
      { status: 500 }
    )
  }
}
```

## 📝 文章管理系统

### 文章API路由

```typescript
// src/app/api/articles/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { z } from 'zod'

const createArticleSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(10),
  excerpt: z.string().max(500).optional(),
  categoryId: z.string(),
  tagIds: z.array(z.string()).optional(),
  status: z.enum(['DRAFT', 'PUBLISHED']).default('DRAFT')
})

// GET /api/articles - 获取文章列表
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const page = parseInt(searchParams.get('page') || '1')
    const limit = parseInt(searchParams.get('limit') || '10')
    const category = searchParams.get('category')
    const tag = searchParams.get('tag')
    const search = searchParams.get('search')
    const status = searchParams.get('status') || 'PUBLISHED'

    const where: any = { status }

    if (category) {
      where.category = { slug: category }
    }

    if (tag) {
      where.tags = {
        some: {
          tag: { slug: tag }
        }
      }
    }

    if (search) {
      where.OR = [
        { title: { contains: search } },
        { content: { contains: search } },
        { excerpt: { contains: search } }
      ]
    }

    const [articles, total] = await Promise.all([
      prisma.article.findMany({
        where,
        include: {
          author: {
            select: {
              id: true,
              username: true,
              displayName: true,
              avatar: true
            }
          },
          category: true,
          tags: {
            include: { tag: true }
          },
          _count: {
            select: {
              comments: true
            }
          }
        },
        orderBy: { publishedAt: 'desc' },
        skip: (page - 1) * limit,
        take: limit
      }),
      prisma.article.count({ where })
    ])

    return NextResponse.json({
      success: true,
      data: articles,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit)
      }
    })

  } catch (error) {
    console.error('Error fetching articles:', error)
    return NextResponse.json(
      { error: '获取文章失败' },
      { status: 500 }
    )
  }
}

// POST /api/articles - 创建文章
export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)

    if (!session) {
      return NextResponse.json(
        { error: '未授权' },
        { status: 401 }
      )
    }

    const body = await request.json()
    const { title, content, excerpt, categoryId, tagIds, status } = createArticleSchema.parse(body)

    // 生成唯一slug
    let slug = title
      .toLowerCase()
      .replace(/[^a-z0-9\u4e00-\u9fa5]/g, '-')
      .replace(/-+/g, '-')
      .trim('-')

    // 检查slug唯一性
    const existingArticle = await prisma.article.findUnique({
      where: { slug }
    })

    if (existingArticle) {
      slug += `-${Date.now()}`
    }

    const article = await prisma.article.create({
      data: {
        title,
        slug,
        content,
        excerpt: excerpt || content.substring(0, 160),
        authorId: session.user.id,
        categoryId,
        status: status as any,
        publishedAt: status === 'PUBLISHED' ? new Date() : undefined,
        tags: tagIds ? {
          create: tagIds.map(tagId => ({
            tag: { connect: { id: tagId } }
          }))
        } : undefined
      },
      include: {
        author: true,
        category: true,
        tags: {
          include: { tag: true }
        }
      }
    })

    return NextResponse.json({
      success: true,
      data: article,
      message: '文章创建成功'
    }, { status: 201 })

  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: '输入数据无效', details: error.issues },
        { status: 400 }
      )
    }

    console.error('Error creating article:', error)
    return NextResponse.json(
      { error: '创建文章失败' },
      { status: 500 }
    )
  }
}
```

### 文章组件

```tsx
// src/components/articles/ArticleCard.tsx
import Image from 'next/image'
import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { Calendar, User, MessageCircle, Eye } from 'lucide-react'
import { Article } from '@/types'

interface ArticleCardProps {
  article: Article & {
    author: {
      username: string
      displayName: string
      avatar?: string
    }
    category: {
      name: string
      color: string
    }
    tags: Array<{
      tag: {
        name: string
        slug: string
      }
    }>
    _count: {
      comments: number
    }
  }
}

export function ArticleCard({ article }: ArticleCardProps) {
  return (
    <article className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
      {/* 封面图片 */}
      {article.coverImage && (
        <Link href={`/articles/${article.slug}`}>
          <div className="relative h-48 w-full">
            <Image
              src={article.coverImage}
              alt={article.title}
              fill
              className="object-cover rounded-t-lg"
            />
          </div>
        </Link>
      )}

      <div className="p-6">
        {/* 分类和标签 */}
        <div className="flex items-center gap-2 mb-3">
          <span
            className="px-2 py-1 text-xs font-medium text-white rounded"
            style={{ backgroundColor: article.category.color }}
          >
            {article.category.name}
          </span>
          {article.tags.slice(0, 2).map(({ tag }) => (
            <Link
              key={tag.id}
              href={`/tags/${tag.slug}`}
              className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded hover:bg-gray-200 transition-colors"
            >
              #{tag.name}
            </Link>
          ))}
        </div>

        {/* 标题 */}
        <Link href={`/articles/${article.slug}`}>
          <h2 className="text-xl font-semibold text-gray-900 mb-2 hover:text-blue-600 transition-colors line-clamp-2">
            {article.title}
          </h2>
        </Link>

        {/* 摘要 */}
        <p className="text-gray-600 mb-4 line-clamp-3">
          {article.excerpt}
        </p>

        {/* 元信息 */}
        <div className="flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              {article.author.avatar ? (
                <Image
                  src={article.author.avatar}
                  alt={article.author.displayName}
                  width={20}
                  height={20}
                  className="rounded-full"
                />
              ) : (
                <div className="w-5 h-5 bg-gray-300 rounded-full" />
              )}
              <span>{article.author.displayName}</span>
            </div>

            <div className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              <span>
                {formatDistanceToNow(new Date(article.publishedAt || article.createdAt), {
                  addSuffix: true,
                  locale: zhCN
                })}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1">
              <Eye className="w-4 h-4" />
              <span>{article.viewCount}</span>
            </div>
            <div className="flex items-center gap-1">
              <MessageCircle className="w-4 h-4" />
              <span>{article._count.comments}</span>
            </div>
          </div>
        </div>
      </div>
    </article>
  )
}
```

## 🎨 主题和响应式设计

### 主题提供者

```tsx
// src/components/ThemeProvider.tsx
'use client'

import { createContext, useContext, useEffect, useState } from 'react'

type Theme = 'light' | 'dark' | 'system'

interface ThemeContextType {
  theme: Theme
  setTheme: (theme: Theme) => void
  effectiveTheme: 'light' | 'dark'
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({
  children,
  defaultTheme = 'system',
  storageKey = 'blog-theme'
}: {
  children: React.ReactNode
  defaultTheme?: Theme
  storageKey?: string
}) {
  const [theme, setTheme] = useState<Theme>(defaultTheme)
  const [effectiveTheme, setEffectiveTheme] = useState<'light' | 'dark'>('light')

  useEffect(() => {
    const stored = localStorage.getItem(storageKey) as Theme
    if (stored) {
      setTheme(stored)
    }
  }, [storageKey])

  useEffect(() => {
    const root = window.document.documentElement
    root.classList.remove('light', 'dark')

    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light'
      root.classList.add(systemTheme)
      setEffectiveTheme(systemTheme)
    } else {
      root.classList.add(theme)
      setEffectiveTheme(theme)
    }
  }, [theme])

  const value = {
    theme,
    setTheme: (theme: Theme) => {
      localStorage.setItem(storageKey, theme)
      setTheme(theme)
    },
    effectiveTheme
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}
```

## 🚀 项目部署

### 构建配置

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Turbopack 配置（顶层键）
  turbopack: {
    rules: {
      '*.svg': {
        loaders: ['@svgr/webpack'],
        as: '*.js',
      },
    },
  },

  // 图片优化
  images: {
    remotePatterns: [
      { protocol: 'http', hostname: 'localhost' },
      { protocol: 'https', hostname: 'your-domain.com' },
    ],
    formats: ['image/webp', 'image/avif'],
  },

  // 环境变量
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },

  // 重定向
  async redirects() {
    return [
      {
        source: '/home',
        destination: '/',
        permanent: true,
      },
    ]
  },

  // 头部配置
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig
```

### Vercel部署配置

```json
// vercel.json
{
  "buildCommand": "prisma generate && next build",
  "devCommand": "next dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "outputDirectory": ".next",
  "regions": ["hkg1"],
  "functions": {
    "src/app/api/**/*.ts": {
      "maxDuration": 30
    }
  },
  "env": {
    "NEXTAUTH_URL": "@next-auth-url",
    "NEXTAUTH_SECRET": "@next-auth-secret",
    "DATABASE_URL": "@database-url"
  }
}
```

## ✅ 项目总结

通过这个完整的博客平台项目，你已经学会了：

### 🏗️ 项目架构
- Next.js 16 App Router的项目结构设计
- 模块化组件和代码组织
- TypeScript类型安全和接口设计

### 🔐 认证系统
- NextAuth.js集成和配置
- 用户注册、登录、权限管理
- 会话管理和安全最佳实践

### 📝 内容管理
- CRUD操作的API设计和实现
- 富文本编辑器集成
- 文章分类和标签系统
- 搜索和筛选功能

### 🎨 用户体验
- 响应式设计和移动端适配
- 暗色模式和主题切换
- 加载状态和错误处理
- 性能优化和缓存策略

### 🚀 部署和运维
- 项目构建和环境配置
- Vercel部署和CI/CD
- 监控和日志管理

## 📚 下一步扩展

- **实时功能**: WebSocket实时评论和通知
- **SEO优化**: 动态元数据和sitemap生成
- **性能监控**: 为文章列表记录加载耗时与失败次数，先在固定数据量和网络条件下测量，再比较分页、图片尺寸等改动的影响；工具上线本身不等于性能已经改善。
- **国际化**: 多语言支持和本地化
- **测试**: 单元测试、集成测试和E2E测试
- **PWA**: 离线支持和应用安装

恭喜你完成了第一个完整的Next.js 16项目！这个项目涵盖了现代Web开发的核心概念和最佳实践，为你的开发生涯奠定了坚实的基础。继续探索更多高级特性，构建更强大的应用吧！

## 🔄 文档交叉引用

### 相关文档
- 📄 **[前一个basics文档](./07-state-management.md)**: 学习状态管理，为项目中的复杂交互做好准备
- 📄 **[相关的reference文档](../reference/framework-patterns/06-form-validation-patterns.md)**: 深入了解表单验证模式和最佳实践
- 📄 **[相关的framework-patterns文档](../reference/framework-patterns/07-authentication-flows.md)**: 快速参考认证流程和权限管理模式

### 参考章节
- 📖 **[本模块其他章节回顾]**: [环境搭建](./01-environment-setup.md) | [应用创建](./02-first-nextjs-app.md) | [TypeScript集成](./03-typescript-integration.md) | [布局路由](./04-layouts-routing.md) | [样式设计](./05-styling-with-tailwind.md) | [数据获取](./06-data-fetching-basics.md) | [状态管理](./07-state-management.md)
- 📖 **[Knowledge Points快速参考]**: [表单验证模式](../reference/framework-patterns/06-form-validation-patterns.md) | [认证流程](../reference/framework-patterns/07-authentication-flows.md)

## 📝 总结

### 项目交付回顾

完成项目的标志不是页面数量，而是从一个身份、一次写入到一次发布都能说明其边界和失败行为。

1. **路由与职责**：为每个页面标出读取数据的位置、交互组件的边界和服务端写入入口；共享布局只放真正共享的导航与外观，避免把所有状态提升到根布局。
2. **身份与授权**：登录成功只证明身份已建立。每个创建、读取、更新和删除入口都要在服务端根据当前身份检查资源归属或角色，不能只依靠隐藏按钮。
3. **CRUD 契约**：为一个核心资源定义字段、输入校验、成功响应、缺失资源与无权限的响应；写入后刷新或失效对应读取数据，避免客户端仍展示旧记录。
4. **可用性与性能**：在窄屏和宽屏完成关键流程，键盘能到达表单控件且错误可读；对加载慢、空数据和请求失败各准备明确界面状态，再测量关键页面的实际性能指标。
5. **发布与运行**：区分公开配置与密钥，构建前检查必需变量；发布记录要能关联 commit 和环境，并能通过健康检查与一条授权业务请求验证部署。

### 学习成果验收

- [ ] 画出一个核心功能的路由、读取、写入和客户端交互边界，并让陌生读者能据此找到代码入口。
- [ ] 用两个不同用户或角色尝试访问同一资源，确认服务端拒绝越权读取与写入，即使直接调用 URL 或 API。
- [ ] 对核心资源演练创建、编辑、删除、字段错误和找不到资源五种情况，记录对应状态码或用户可见结果。
- [ ] 在手机宽度、键盘操作和慢网络下完成一次关键任务，保存加载、空、错误、成功四个状态的截图或测试结果。
- [ ] 在测试环境部署不可变版本，确认未泄露密钥，并记录 commit、环境、健康检查及一条已授权业务请求结果。

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

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
