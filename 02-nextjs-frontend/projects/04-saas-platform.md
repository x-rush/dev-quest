# Next.js 16 SaaS平台开发实战

> 通过构建一个功能完整的企业级SaaS平台，掌握现代SaaS应用开发的核心技术和商业模式。本项目涵盖多租户架构、订阅计费、用户管理、API集成、实时协作等企业级SaaS系统的关键功能。

**目标读者**: 有Next.js和全栈开发基础，希望学习企业级SaaS平台开发的开发者
**前置知识**: Next.js基础、数据库设计、API开发、认证授权、基础业务逻辑
**预计时长**: 4-6周

## 📚 文档元数据
| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `projects` |
| **难度** | ⭐⭐⭐ (精通)|
| **标签** | `Next.js 16` `React 19` `TypeScript 7` `SaaS` `多租户` `订阅计费` `Stripe Billing` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标
- 构建多租户SaaS平台架构
- 实现完整的用户认证和权限管理系统
- 开发订阅计费和Stripe集成
- 掌握多租户数据隔离和安全
- 实现实时协作和通知系统
- 开发可定制的白标解决方案
- 掌握SaaS业务的监控和分析
- 部署和扩展生产级SaaS应用

## 📖 项目概述

### 项目背景
SaaS（Software as a Service）是现代软件行业的重要商业模式，需要处理复杂的业务逻辑、多租户架构、订阅计费、安全隔离等挑战。本项目将构建一个功能完整的企业级SaaS平台。

### 核心功能
- 🏢 多租户架构和数据隔离
- 👥 完整的用户管理和权限系统
- 💳 订阅计费和Stripe集成
- 🎨 白标和品牌定制
- 🔄 实时协作和WebSocket通信
- 📊 业务分析和报表系统
- 🔐 企业级安全和合规
- 📱 响应式和移动端适配
- 🔌 API集成和第三方服务
- 📧 邮件通知和自动化

### 技术栈
- **前端框架**: Next.js 16 + React 19
- **开发语言**: TypeScript 7
- **UI组件库**: Shadcn/ui + Tailwind CSS
- **状态管理**: Zustand + React Query
- **数据库**: PostgreSQL + Prisma ORM
- **认证**: NextAuth.js v5 + 多租户适配
- **支付系统**: Stripe + Stripe Billing
- **实时通信**: Socket.io + Redis
- **邮件服务**: Resend + React Email
- **文件存储**: AWS S3/Cloudinary
- **监控**: Sentry + LogRocket
- **部署**: Vercel + Railway + Supabase

## 🏗️ 项目架构

### 目录结构
```
saas-platform/
├── app/                          # App Router目录
│   ├── (auth)/                   # 认证路由组
│   │   ├── login/               # 登录页面
│   │   ├── register/            # 注册页面
│   │   ├── verify-email/        # 邮箱验证
│   │   ├── forgot-password/     # 忘记密码
│   │   └── layout.tsx           # 认证布局
│   ├── (app)/                   # 应用路由组
│   │   ├── dashboard/           # 仪表板
│   │   ├── settings/            # 设置页面
│   │   │   ├── profile/         # 个人资料
│   │   │   ├── billing/         # 计费管理
│   │   │   ├── team/            # 团队管理
│   │   │   ├── integrations/    # 集成管理
│   │   │   └── branding/        # 品牌定制
│   │   ├── admin/               # 管理后台
│   │   │   ├── tenants/         # 租户管理
│   │   │   ├── users/           # 用户管理
│   │   │   ├── subscriptions/   # 订阅管理
│   │   │   └── analytics/       # 平台分析
│   │   └── layout.tsx           # 应用布局
│   ├── api/                     # API路由
│   │   ├── auth/                # 认证API
│   │   ├── tenants/             # 租户API
│   │   ├── users/               # 用户API
│   │   ├── subscriptions/       # 订阅API
│   │   ├── billing/             # 计费API
│   │   ├── webhooks/            # Webhook处理
│   │   └── admin/               # 管理API
│   ├── billing/                 # 计费页面
│   │   ├── checkout/            # 结账页面
│   │   ├── success/             # 支付成功
│   │   └── cancelled/           # 支付取消
│   ├── invite/                  # 邀请页面
│   ├── globals.css              # 全局样式
│   ├── layout.tsx               # 根布局
│   └── page.tsx                 # 首页
├── components/                  # 组件库
│   ├── ui/                      # UI基础组件
│   ├── auth/                    # 认证组件
│   ├── billing/                 # 计费组件
│   ├── dashboard/               # 仪表板组件
│   ├── settings/                # 设置组件
│   ├── admin/                   # 管理组件
│   ├── layout/                  # 布局组件
│   └── forms/                   # 表单组件
├── lib/                         # 工具函数
│   ├── auth/                    # 认证配置
│   ├── db/                      # 数据库配置
│   ├── billing/                 # 计费处理
│   ├── email/                   # 邮件服务
│   ├── tenants/                 # 租户管理
│   ├── permissions/             # 权限控制
│   ├── notifications/           # 通知服务
│   └── utils/                   # 通用工具
├── hooks/                       # 自定义Hooks
├── store/                       # 状态管理
├── types/                       # TypeScript类型
├── prisma/                      # Prisma配置
│   ├── schema.prisma           # 数据库模型
│   ├── migrations/             # 数据库迁移
│   └── seed.ts                 # 种子数据
├── emails/                      # 邮件模板
├── public/                     # 静态资源
└── proxy.ts                   # 网络代理（原中间件）
```

### 多租户数据库设计
```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// 平台级模型（全局数据）
model Platform {
  id              String   @id @default(cuid())
  name            String
  domain          String   @unique
  settings        Json     @default("{}")
  stripeAccountId String?
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  // 关联
  tenants         Tenant[]
  plans           Plan[]
  platformUsers   PlatformUser[]

  @@map("platforms")
}

model Plan {
  id           String      @id @default(cuid())
  platformId   String
  platform     Platform    @relation(fields: [platformId], references: [id])
  name         String
  description  String?
  price        Float
  currency     String      @default("USD")
  interval     BillingInterval
  features     Json        @default("[]")
  stripePriceId String?
  isActive     Boolean     @default(true)
  sortOrder    Int         @default(0)
  createdAt    DateTime    @default(now())
  updatedAt    DateTime    @updatedAt

  // 关联
  subscriptions Subscription[]

  @@map("plans")
}

model PlatformUser {
  id            String    @id @default(cuid())
  platformId    String
  platform      Platform  @relation(fields: [platformId], references: [id])
  email         String
  name          String
  role          PlatformRole @default(USER)
  isActive      Boolean   @default(true)
  lastLoginAt   DateTime?
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  @@unique([platformId, email])
  @@map("platform_users")
}

// 租户级模型（每个租户的数据）
model Tenant {
  id            String   @id @default(cuid())
  platformId    String
  platform      Platform @relation(fields: [platformId], references: [id])
  name          String
  slug          String
  domain        String?
  subdomain     String?
  settings      Json     @default("{}")
  branding      Json     @default("{}")
  status        TenantStatus @default(ACTIVE)
  stripeCustomerId String?  // Stripe 客户 ID（业务代码写入）
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt

  // 关联
  users         User[]
  subscriptions Subscription[]
  invitations   Invitation[]
  projects      Project[]
  auditLogs     AuditLog[]

  @@unique([platformId, slug])
  @@map("tenants")
}

model User {
  id            String    @id @default(cuid())
  tenantId      String
  tenant        Tenant    @relation(fields: [tenantId], references: [id], onDelete: Cascade)
  platformUserId String
  email         String
  name          String
  avatar        String?
  role          UserRole  @default(MEMBER)
  status        UserStatus @default(ACTIVE)
  lastLoginAt   DateTime?
  emailVerified Boolean   @default(false)
  twoFactorEnabled Boolean @default(false)
  twoFactorSecret String?
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  // 关联
  sessions      Session[]
  invitations   Invitation[]
  projectMemberships ProjectMembership[]
  auditLogs     AuditLog[]
  notifications Notification[]

  @@unique([tenantId, email])
  @@map("users")
}

model Session {
  id           String   @id @default(cuid())
  userId       String
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  token        String   @unique
  refreshToken String?  @unique
  expiresAt    DateTime
  ipAddress    String?
  userAgent    String?
  createdAt    DateTime @default(now())

  @@map("sessions")
}

model Subscription {
  id             String           @id @default(cuid())
  tenantId       String
  tenant         Tenant           @relation(fields: [tenantId], references: [id], onDelete: Cascade)
  planId         String
  plan           Plan             @relation(fields: [planId], references: [id])
  stripeSubscriptionId String?   @unique
  status         SubscriptionStatus @default(TRIALING)
  currentPeriodStart DateTime
  currentPeriodEnd   DateTime
  cancelAtPeriodEnd  Boolean   @default(false)
  canceledAt          DateTime?
  trialEnd            DateTime?
  metadata           Json?
  createdAt          DateTime @default(now())
  updatedAt          DateTime @updatedAt

  @@map("subscriptions")
}

model Invitation {
  id           String          @id @default(cuid())
  tenantId     String
  tenant       Tenant          @relation(fields: [tenantId], references: [id], onDelete: Cascade)
  inviterId    String
  inviter      User            @relation(fields: [inviterId], references: [id])
  email        String
  role         UserRole        @default(MEMBER)
  token        String          @unique
  expiresAt    DateTime
  acceptedAt   DateTime?
  createdAt    DateTime        @default(now())
  updatedAt    DateTime        @updatedAt

  @@map("invitations")
}

model Project {
  id          String   @id @default(cuid())
  tenantId    String
  tenant      Tenant   @relation(fields: [tenantId], references: [id], onDelete: Cascade)
  name        String
  description String?
  status      ProjectStatus @default(ACTIVE)
  settings    Json     @default("{}")
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  // 关联
  members     ProjectMembership[]

  @@map("projects")
}

model ProjectMembership {
  id        String   @id @default(cuid())
  projectId String
  project   Project  @relation(fields: [projectId], references: [id], onDelete: Cascade)
  userId    String
  user      User     @relation(fields: [userId], references: [id])
  role      ProjectRole @default(MEMBER)
  joinedAt  DateTime @default(now())

  @@unique([projectId, userId])
  @@map("project_memberships")
}

model Notification {
  id        String           @id @default(cuid())
  userId    String
  user      User             @relation(fields: [userId], references: [id], onDelete: Cascade)
  type      NotificationType
  title     String
  content   String
  metadata  Json?
  isRead    Boolean          @default(false)
  createdAt DateTime         @default(now())

  @@map("notifications")
}

model AuditLog {
  id        String       @id @default(cuid())
  tenantId  String
  tenant    Tenant       @relation(fields: [tenantId], references: [id])
  userId    String?
  user      User?        @relation(fields: [userId], references: [id])
  action    AuditAction
  resource  String       // 资源类型
  resourceId String?    // 资源ID
  oldValues Json?        // 修改前的值
  newValues Json?        // 修改后的值
  ipAddress String?
  userAgent String?
  createdAt DateTime     @default(now())

  @@map("audit_logs")
}

// 枚举类型
enum PlatformRole {
  OWNER
  ADMIN
  USER
}

enum UserRole {
  OWNER
  ADMIN
  MEMBER
  VIEWER
}

enum ProjectRole {
  OWNER
  ADMIN
  MEMBER
  VIEWER
}

enum TenantStatus {
  ACTIVE
  INACTIVE
  SUSPENDED
}

enum UserStatus {
  ACTIVE
  INACTIVE
  SUSPENDED
}

enum ProjectStatus {
  ACTIVE
  ARCHIVED
  DELETED
}

enum BillingInterval {
  MONTH
  YEAR
}

enum SubscriptionStatus {
  TRIALING
  ACTIVE
  PAST_DUE
  CANCELED
  UNPAID
}

enum NotificationType {
  SYSTEM
  BILLING
  PROJECT
  INVITATION
  SECURITY
}

enum AuditAction {
  CREATE
  UPDATE
  DELETE
  LOGIN
  LOGOUT
  ACCESS
}
```

## 🛠️ 实战步骤

### 步骤一：项目初始化

#### 1.1 创建Next.js项目
```bash
# 创建Next.js 16项目
npx create-next-app@latest saas-platform --typescript --tailwind --eslint --app

# 进入项目目录
cd saas-platform

# 安装必要依赖
npm install @prisma/client prisma
npm install @auth/prisma-adapter next-auth
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
npm install @radix-ui/react-select @radix-ui/react-tabs
npm install @radix-ui/react-toast @radix-ui/react-avatar
npm install @hookform/resolvers react-hook-form zod
npm install @tanstack/react-query zustand
npm install stripe @types/stripe
npm install socket.io socket.io-client
npm install resend react-email @react-email/components
npm install lucide-react clsx tailwind-merge
npm install bcryptjs @types/bcryptjs
npm install nanoid @types/nanoid
npm install qrcode @types/qrcode
npm install date-fns lodash @types/lodash

# 安装开发依赖
npm install -D @tailwindcss/typography
npm install -D eslint-config-prettier prettier
npm install -D prisma-dbml-generator
```

#### 1.2 配置多租户Prisma
**lib/db/tenant-prisma.ts**:
```typescript
import { PrismaClient } from '@prisma/client'

// 全局Prisma客户端（用于平台级操作）
const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

export const prisma = globalForPrisma.prisma ?? new PrismaClient()

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma

// 租户特定的Prisma客户端
const tenantPrismaClients = new Map<string, PrismaClient>()

export function getTenantPrisma(tenantId: string): PrismaClient {
  if (!tenantPrismaClients.has(tenantId)) {
    // 为每个租户创建独立的数据库连接或schema
    const client = new PrismaClient({
      datasources: {
        db: {
          url: `${process.env.DATABASE_URL}?schema=tenant_${tenantId}`,
        },
      },
    })

    tenantPrismaClients.set(tenantId, client)
  }

  return tenantPrismaClients.get(tenantId)!
}

// 清理租户客户端连接
export function cleanupTenantPrisma(tenantId: string): void {
  const client = tenantPrismaClients.get(tenantId)
  if (client) {
    client.$disconnect()
    tenantPrismaClients.delete(tenantId)
  }
}

// 租户数据库操作包装器
export class TenantDB {
  constructor(private tenantId: string) {}

  get prisma() {
    return getTenantPrisma(this.tenantId)
  }

  // 事务支持
  async transaction<T>(callback: (tx: PrismaClient) => Promise<T>): Promise<T> {
    const client = this.prisma
    return client.$transaction(callback)
  }

  // 健康检查
  async healthCheck(): Promise<boolean> {
    try {
      await this.prisma.$queryRaw`SELECT 1`
      return true
    } catch (error) {
      console.error('Tenant database health check failed:', error)
      return false
    }
  }

  // 迁移检查
  async checkMigrations(): Promise<boolean> {
    try {
      // 检查必要的表是否存在
      await this.prisma.user.findFirst()
      return true
    } catch (error) {
      console.error('Tenant migration check failed:', error)
      return false
    }
  }
}
```

#### 1.3 实现多租户代理（proxy.ts）
**proxy.ts**（Next.js 16：原 middleware.ts）:
```typescript
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { getToken } from 'next-auth/jwt'
import { prisma } from '@/lib/db/prisma'

export async function proxy(request: NextRequest) {
  const token = await getToken({ req: request })
  const { pathname, host } = request.nextUrl

  // 跳过静态资源和非认证路由
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api/auth') ||
    pathname.startsWith('/login') ||
    pathname.startsWith('/register') ||
    pathname.startsWith('/billing') ||
    pathname.startsWith('/invite')
  ) {
    return NextResponse.next()
  }

  // 从子域名或路径中提取租户信息
  const hostname = host.split('.')[0]
  const pathSegments = pathname.split('/').filter(Boolean)

  let tenantSlug: string | null = null

  // 方法1: 子域名模式 (tenant.domain.com)
  if (hostname !== 'localhost' && hostname !== 'www') {
    tenantSlug = hostname
  }

  // 方法2: 路径模式 (domain.com/tenant/...)
  if (!tenantSlug && pathSegments.length > 0 && pathSegments[0] !== 'app') {
    tenantSlug = pathSegments[0]
  }

  // 如果是应用路由但没有租户信息，重定向到登录
  if (pathname.startsWith('/app') && !tenantSlug) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // 如果有租户信息，验证租户和用户权限
  if (tenantSlug) {
    try {
      const tenant = await prisma.tenant.findUnique({
        where: { slug: tenantSlug },
        include: {
          users: {
            where: {
              platformUserId: token?.sub,
            },
          },
        },
      })

      if (!tenant) {
        return NextResponse.redirect(new URL('/login', request.url))
      }

      if (tenant.status !== 'ACTIVE') {
        return NextResponse.redirect(new URL('/suspended', request.url))
      }

      // 检查用户是否有权限访问此租户
      if (!token || tenant.users.length === 0) {
        return NextResponse.redirect(new URL('/login', request.url))
      }

      const user = tenant.users[0]
      if (user.status !== 'ACTIVE') {
        return NextResponse.redirect(new URL('/login', request.url))
      }

      // 检查订阅状态
      const subscription = await prisma.subscription.findFirst({
        where: {
          tenantId: tenant.id,
          status: {
            in: ['ACTIVE', 'TRIALING'],
          },
        },
        orderBy: { createdAt: 'desc' },
      })

      if (!subscription) {
        // 重定向到计费页面
        return NextResponse.redirect(new URL('/billing', request.url))
      }

      // 在响应头中添加租户信息
      const response = NextResponse.next()
      response.headers.set('x-tenant-id', tenant.id)
      response.headers.set('x-user-id', user.id)
      response.headers.set('x-user-role', user.role)

      return response
    } catch (error) {
      console.error('Middleware error:', error)
      return NextResponse.redirect(new URL('/login', request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public (public files)
     */
    '/((?!api|_next/static|_next/image|favicon.ico|public).*)',
  ],
}
```

### 步骤二：核心功能开发

#### 2.1 实现多租户认证系统
**lib/auth/multi-tenant-adapter.ts**:
```typescript
import { Adapter } from 'next-auth/adapters'
import { prisma } from '@/lib/db/prisma'
import { getTenantPrisma } from '@/lib/db/tenant-prisma'

export function MultiTenantAdapter(tenantId?: string): Adapter {
  return {
    async createUser(user) {
      if (!tenantId) {
        throw new Error('Tenant ID is required for user creation')
      }

      const tenantDb = getTenantPrisma(tenantId)

      // 首先创建平台用户（如果不存在）
      const platformUser = await prisma.platformUser.findUnique({
        where: { email: user.email },
      })

      if (!platformUser) {
        await prisma.platformUser.create({
          data: {
            email: user.email,
            name: user.name || '',
            role: 'USER',
          },
        })
      }

      // 创建租户用户
      const tenantUser = await tenantDb.user.create({
        data: {
          email: user.email,
          name: user.name || '',
          platformUserId: platformUser?.id || '',
        },
      })

      return {
        id: tenantUser.id,
        email: tenantUser.email,
        name: tenantUser.name,
        emailVerified: tenantUser.emailVerified ? new Date() : null,
      }
    },

    async getUser(id) {
      if (!tenantId) return null

      const tenantDb = getTenantPrisma(tenantId)
      const user = await tenantDb.user.findUnique({
        where: { id },
      })

      if (!user) return null

      return {
        id: user.id,
        email: user.email,
        name: user.name,
        emailVerified: user.emailVerified ? new Date() : null,
      }
    },

    async getUserByEmail(email) {
      if (!tenantId) return null

      const tenantDb = getTenantPrisma(tenantId)
      const user = await tenantDb.user.findUnique({
        where: { email },
      })

      if (!user) return null

      return {
        id: user.id,
        email: user.email,
        name: user.name,
        emailVerified: user.emailVerified ? new Date() : null,
      }
    },

    async getUserByAccount({ providerAccountId, provider }) {
      if (!tenantId) return null

      const tenantDb = getTenantPrisma(tenantId)
      const account = await tenantDb.account.findUnique({
        where: {
          provider_providerAccountId: {
            provider,
            providerAccountId,
          },
        },
        include: {
          user: true,
        },
      })

      if (!account) return null

      return {
        id: account.user.id,
        email: account.user.email,
        name: account.user.name,
        emailVerified: account.user.emailVerified ? new Date() : null,
      }
    },

    async updateUser(user) {
      if (!tenantId) throw new Error('Tenant ID is required')

      const tenantDb = getTenantPrisma(tenantId)
      const updatedUser = await tenantDb.user.update({
        where: { id: user.id },
        data: {
          name: user.name || '',
          emailVerified: user.emailVerified?.toISOString() || null,
        },
      })

      return {
        id: updatedUser.id,
        email: updatedUser.email,
        name: updatedUser.name,
        emailVerified: updatedUser.emailVerified ? new Date() : null,
      }
    },

    async deleteUser(userId) {
      if (!tenantId) return

      const tenantDb = getTenantPrisma(tenantId)
      await tenantDb.user.delete({
        where: { id: userId },
      })
    },

    async linkAccount(account) {
      if (!tenantId) throw new Error('Tenant ID is required')

      const tenantDb = getTenantPrisma(tenantId)
      await tenantDb.account.create({
        data: {
          userId: account.userId,
          type: account.type,
          provider: account.provider,
          providerAccountId: account.providerAccountId,
          refresh_token: account.refresh_token,
          access_token: account.access_token,
          expires_at: account.expires_at,
          token_type: account.token_type,
          scope: account.scope,
          id_token: account.id_token,
          session_state: account.session_state,
        },
      })
    },

    async unlinkAccount({ providerAccountId, provider }) {
      if (!tenantId) return

      const tenantDb = getTenantPrisma(tenantId)
      await tenantDb.account.delete({
        where: {
          provider_providerAccountId: {
            provider,
            providerAccountId,
          },
        },
      })
    },

    async createSession({ sessionToken, userId, expires }) {
      if (!tenantId) throw new Error('Tenant ID is required')

      const tenantDb = getTenantPrisma(tenantId)
      const session = await tenantDb.session.create({
        data: {
          token: sessionToken,
          userId,
          expiresAt: expires,
        },
      })

      return {
        sessionToken: session.token,
        userId: session.userId,
        expires: session.expiresAt,
      }
    },

    async getSessionAndUser(sessionToken) {
      if (!tenantId) return null

      const tenantDb = getTenantPrisma(tenantId)
      const session = await tenantDb.session.findUnique({
        where: { token: sessionToken },
        include: {
          user: true,
        },
      })

      if (!session) return null

      return {
        session: {
          sessionToken: session.token,
          userId: session.userId,
          expires: session.expiresAt,
        },
        user: {
          id: session.user.id,
          email: session.user.email,
          name: session.user.name,
          emailVerified: session.user.emailVerified ? new Date() : null,
        },
      }
    },

    async updateSession({ sessionToken, userId, expires }) {
      if (!tenantId) throw new Error('Tenant ID is required')

      const tenantDb = getTenantPrisma(tenantId)
      const session = await tenantDb.session.update({
        where: { token: sessionToken },
        data: {
          userId,
          expiresAt: expires,
        },
      })

      return {
        sessionToken: session.token,
        userId: session.userId,
        expires: session.expiresAt,
      }
    },

    async deleteSession(sessionToken) {
      if (!tenantId) return

      const tenantDb = getTenantPrisma(tenantId)
      await tenantDb.session.delete({
        where: { token: sessionToken },
      })
    },
  }
}
```

#### 2.2 实现订阅计费系统
**lib/billing/subscription-service.ts**:
```typescript
import { prisma } from '@/lib/db/prisma'
import { stripe } from '@/lib/billing/stripe'
import { getTenantPrisma } from '@/lib/db/tenant-prisma'

export interface CreateSubscriptionParams {
  tenantId: string
  planId: string
  paymentMethodId?: string
  trialDays?: number
  couponCode?: string
}

export interface UpdateSubscriptionParams {
  subscriptionId: string
  planId?: string
  quantity?: number
  metadata?: Record<string, string>
}

export class SubscriptionService {
  /**
   * 创建订阅
   */
  static async createSubscription(params: CreateSubscriptionParams) {
    const { tenantId, planId, paymentMethodId, trialDays, couponCode } = params

    // 获取租户和计划信息
    const [tenant, plan] = await Promise.all([
      prisma.tenant.findUnique({ where: { id: tenantId } }),
      prisma.plan.findUnique({ where: { id: planId } }),
    ])

    if (!tenant || !plan) {
      throw new Error('Tenant or plan not found')
    }

    // 检查是否已有活跃订阅
    const existingSubscription = await prisma.subscription.findFirst({
      where: {
        tenantId,
        status: {
          in: ['TRIALING', 'ACTIVE'],
        },
      },
    })

    if (existingSubscription) {
      throw new Error('Tenant already has an active subscription')
    }

    // 创建Stripe订阅
    const stripeSubscriptionParams: any = {
      customer: tenant.stripeCustomerId || await this.createStripeCustomer(tenant),
      items: [{ price: plan.stripePriceId }],
      payment_behavior: 'default_incomplete',
      payment_settings: {
        save_default_payment_method: 'on_subscription',
      },
      expand: ['latest_invoice.payment_intent'],
    }

    // 添加试用期
    if (trialDays) {
      stripeSubscriptionParams.trial_period_days = trialDays
    }

    // 添加优惠券
    if (couponCode) {
      const coupon = await stripe.coupons.retrieve(couponCode)
      stripeSubscriptionParams.coupon = coupon.id
    }

    // 添加支付方式
    if (paymentMethodId) {
      stripeSubscriptionParams.default_payment_method = paymentMethodId
    }

    const stripeSubscription = await stripe.subscriptions.create(stripeSubscriptionParams)

    // 保存订阅到数据库
    const subscription = await prisma.subscription.create({
      data: {
        tenantId,
        planId,
        stripeSubscriptionId: stripeSubscription.id,
        status: this.mapStripeStatus(stripeSubscription.status),
        // Stripe dahlia 起 current_period_* 移至 SubscriptionItem
        currentPeriodStart: new Date(stripeSubscription.items.data[0].current_period_start * 1000),
        currentPeriodEnd: new Date(stripeSubscription.items.data[0].current_period_end * 1000),
        trialEnd: stripeSubscription.trial_end
          ? new Date(stripeSubscription.trial_end * 1000)
          : null,
        metadata: stripeSubscription.metadata,
      },
      include: {
        plan: true,
        tenant: true,
      },
    })

    // 更新租户的Stripe客户ID
    if (!tenant.stripeCustomerId) {
      await prisma.tenant.update({
        where: { id: tenantId },
        data: { stripeCustomerId: stripeSubscription.customer as string },
      })
    }

    return {
      subscription,
      clientSecret: (stripeSubscription.latest_invoice as any)?.payment_intent?.client_secret,
    }
  }

  /**
   * 更新订阅
   */
  static async updateSubscription(params: UpdateSubscriptionParams) {
    const { subscriptionId, planId, quantity, metadata } = params

    // 获取数据库中的订阅
    const subscription = await prisma.subscription.findUnique({
      where: { id: subscriptionId },
      include: { plan: true },
    })

    if (!subscription) {
      throw new Error('Subscription not found')
    }

    // 更新Stripe订阅
    const stripeSubscription = await stripe.subscriptions.retrieve(
      subscription.stripeSubscriptionId!
    )

    const updateParams: any = {}

    if (planId && planId !== subscription.planId) {
      const newPlan = await prisma.plan.findUnique({ where: { id: planId } })
      if (!newPlan) {
        throw new Error('New plan not found')
      }

      updateParams.items = [{
        id: stripeSubscription.items.data[0].id,
        price: newPlan.stripePriceId,
      }]
    }

    if (quantity !== undefined) {
      updateParams.quantity = quantity
    }

    if (metadata) {
      updateParams.metadata = { ...stripeSubscription.metadata, ...metadata }
    }

    const updatedStripeSubscription = await stripe.subscriptions.update(
      subscription.stripeSubscriptionId!,
      updateParams
    )

    // 更新数据库中的订阅
    const updatedSubscription = await prisma.subscription.update({
      where: { id: subscriptionId },
      data: {
        planId: planId || subscription.planId,
        status: this.mapStripeStatus(updatedStripeSubscription.status),
        currentPeriodStart: new Date(updatedStripeSubscription.items.data[0].current_period_start * 1000),
        currentPeriodEnd: new Date(updatedStripeSubscription.items.data[0].current_period_end * 1000),
        metadata: updatedStripeSubscription.metadata,
      },
      include: {
        plan: true,
        tenant: true,
      },
    })

    return updatedSubscription
  }

  /**
   * 取消订阅
   */
  static async cancelSubscription(subscriptionId: string, immediate = false) {
    const subscription = await prisma.subscription.findUnique({
      where: { id: subscriptionId },
    })

    if (!subscription) {
      throw new Error('Subscription not found')
    }

    if (immediate) {
      // 立即取消
      await stripe.subscriptions.del(subscription.stripeSubscriptionId!)

      await prisma.subscription.update({
        where: { id: subscriptionId },
        data: {
          status: 'CANCELED',
          canceledAt: new Date(),
        },
      })
    } else {
      // 在期末取消
      await stripe.subscriptions.update(subscription.stripeSubscriptionId!, {
        cancel_at_period_end: true,
      })

      await prisma.subscription.update({
        where: { id: subscriptionId },
        data: { cancelAtPeriodEnd: true },
      })
    }

    return true
  }

  /**
   * 恢复订阅
   */
  static async resumeSubscription(subscriptionId: string) {
    const subscription = await prisma.subscription.findUnique({
      where: { id: subscriptionId },
    })

    if (!subscription) {
      throw new Error('Subscription not found')
    }

    await stripe.subscriptions.update(subscription.stripeSubscriptionId!, {
      cancel_at_period_end: false,
    })

    await prisma.subscription.update({
      where: { id: subscriptionId },
      data: { cancelAtPeriodEnd: false },
    })

    return true
  }

  /**
   * 获取订阅使用情况
   */
  static async getSubscriptionUsage(subscriptionId: string) {
    const subscription = await prisma.subscription.findUnique({
      where: { id: subscriptionId },
      include: {
        tenant: true,
        plan: true,
      },
    })

    if (!subscription) {
      throw new Error('Subscription not found')
    }

    const tenantDb = getTenantPrisma(subscription.tenantId)

    // 根据计划特性计算使用情况
    const usage = {
      users: await tenantDb.user.count({
        where: { status: 'ACTIVE' },
      }),
      projects: await tenantDb.project.count({
        where: { status: 'ACTIVE' },
      }),
      storage: 0, // 需要实现存储统计
      apiCalls: 0, // 需要实现API调用统计
    }

    const limits = this.extractPlanLimits(subscription.plan.features)

    return {
      usage,
      limits,
      isOverLimit: Object.keys(limits).some(
        key => usage[key as keyof typeof usage] > limits[key as keyof typeof limits]
      ),
    }
  }

  /**
   * 创建Stripe客户
   */
  private static async createStripeCustomer(tenant: any) {
    const customer = await stripe.customers.create({
      name: tenant.name,
      email: tenant.settings?.email || '',
      metadata: {
        tenantId: tenant.id,
      },
    })

    // 更新租户记录
    await prisma.tenant.update({
      where: { id: tenant.id },
      data: { stripeCustomerId: customer.id },
    })

    return customer.id
  }

  /**
   * 映射Stripe状态到本地状态
   */
  private static mapStripeStatus(stripeStatus: string): SubscriptionStatus {
    const statusMap: Record<string, SubscriptionStatus> = {
      trialing: 'TRIALING',
      active: 'ACTIVE',
      past_due: 'PAST_DUE',
      canceled: 'CANCELED',
      unpaid: 'UNPAID',
      incomplete: 'PAST_DUE',
      incomplete_expired: 'CANCELED',
    }

    return statusMap[stripeStatus] || 'PAST_DUE'
  }

  /**
   * 从计划特性中提取限制
   */
  private static extractPlanLimits(features: any[]) {
    const limits: Record<string, number> = {}

    features.forEach(feature => {
      if (feature.type === 'limit') {
        limits[feature.name] = feature.value
      }
    })

    return limits
  }
}
```

#### 2.3 实现权限控制系统
**lib/permissions/rbac.ts**:
```typescript
import { User, UserRole, ProjectRole } from '@prisma/client'

export type Resource =
  | 'dashboard'
  | 'users'
  | 'projects'
  | 'billing'
  | 'settings'
  | 'analytics'
  | 'integrations'
  | 'invitations'

export type Permission =
  | 'read'
  | 'write'
  | 'delete'
  | 'admin'

export interface PermissionRule {
  resource: Resource
  permission: Permission
  condition?: (user: User, context?: any) => boolean
}

// 角色权限映射
const ROLE_PERMISSIONS: Record<UserRole, PermissionRule[]> = {
  OWNER: [
    // Owner拥有所有权限
    { resource: 'dashboard', permission: 'read' },
    { resource: 'dashboard', permission: 'write' },
    { resource: 'dashboard', permission: 'delete' },
    { resource: 'users', permission: 'read' },
    { resource: 'users', permission: 'write' },
    { resource: 'users', permission: 'delete' },
    { resource: 'projects', permission: 'read' },
    { resource: 'projects', permission: 'write' },
    { resource: 'projects', permission: 'delete' },
    { resource: 'billing', permission: 'read' },
    { resource: 'billing', permission: 'write' },
    { resource: 'settings', permission: 'read' },
    { resource: 'settings', permission: 'write' },
    { resource: 'analytics', permission: 'read' },
    { resource: 'integrations', permission: 'read' },
    { resource: 'integrations', permission: 'write' },
    { resource: 'invitations', permission: 'read' },
    { resource: 'invitations', permission: 'write' },
    { resource: 'invitations', permission: 'delete' },
  ],
  ADMIN: [
    // Admin拥有除billing管理外的所有权限
    { resource: 'dashboard', permission: 'read' },
    { resource: 'dashboard', permission: 'write' },
    { resource: 'users', permission: 'read' },
    { resource: 'users', permission: 'write' },
    { resource: 'projects', permission: 'read' },
    { resource: 'projects', permission: 'write' },
    { resource: 'projects', permission: 'delete' },
    { resource: 'billing', permission: 'read' },
    { resource: 'settings', permission: 'read' },
    { resource: 'settings', permission: 'write' },
    { resource: 'analytics', permission: 'read' },
    { resource: 'integrations', permission: 'read' },
    { resource: 'integrations', permission: 'write' },
    { resource: 'invitations', permission: 'read' },
    { resource: 'invitations', permission: 'write' },
  ],
  MEMBER: [
    // Member拥有基本权限
    { resource: 'dashboard', permission: 'read' },
    { resource: 'projects', permission: 'read' },
    { resource: 'projects', permission: 'write' },
    { resource: 'settings', permission: 'read' },
  ],
  VIEWER: [
    // Viewer只有只读权限
    { resource: 'dashboard', permission: 'read' },
    { resource: 'projects', permission: 'read' },
  ],
}

// 项目角色权限映射
const PROJECT_ROLE_PERMISSIONS: Record<ProjectRole, PermissionRule[]> = {
  OWNER: [
    { resource: 'projects', permission: 'read' },
    { resource: 'projects', permission: 'write' },
    { resource: 'projects', permission: 'delete' },
  ],
  ADMIN: [
    { resource: 'projects', permission: 'read' },
    { resource: 'projects', permission: 'write' },
  ],
  MEMBER: [
    { resource: 'projects', permission: 'read' },
    { resource: 'projects', permission: 'write' },
  ],
  VIEWER: [
    { resource: 'projects', permission: 'read' },
  ],
}

export class RBAC {
  /**
   * 检查用户是否有指定权限
   */
  static hasPermission(
    user: User,
    resource: Resource,
    permission: Permission,
    context?: any
  ): boolean {
    const userPermissions = ROLE_PERMISSIONS[user.role] || []

    const matchingPermissions = userPermissions.filter(rule =>
      rule.resource === resource && rule.permission === permission
    )

    // 如果没有匹配的权限规则，拒绝访问
    if (matchingPermissions.length === 0) {
      return false
    }

    // 检查条件
    return matchingPermissions.every(rule =>
      !rule.condition || rule.condition(user, context)
    )
  }

  /**
   * 检查用户是否有项目权限
   */
  static hasProjectPermission(
    userRole: ProjectRole,
    resource: Resource,
    permission: Permission,
    context?: any
  ): boolean {
    const projectPermissions = PROJECT_ROLE_PERMISSIONS[userRole] || []

    const matchingPermissions = projectPermissions.filter(rule =>
      rule.resource === resource && rule.permission === permission
    )

    if (matchingPermissions.length === 0) {
      return false
    }

    return matchingPermissions.every(rule =>
      !rule.condition || rule.condition(context)
    )
  }

  /**
   * 获取用户的所有权限
   */
  static getUserPermissions(user: User): PermissionRule[] {
    return ROLE_PERMISSIONS[user.role] || []
  }

  /**
   * 获取项目的所有权限
   */
  static getProjectPermissions(userRole: ProjectRole): PermissionRule[] {
    return PROJECT_ROLE_PERMISSIONS[userRole] || []
  }

  /**
   * 检查用户是否可以访问资源
   */
  static canAccess(
    user: User,
    resource: Resource,
    action: 'read' | 'write' | 'delete' | 'admin',
    context?: {
      projectId?: string
      userId?: string
      tenantId?: string
    }
  ): boolean {
    // 检查基本权限
    if (this.hasPermission(user, resource, action, context)) {
      return true
    }

    // 检查项目特定权限
    if (context?.projectId) {
      // 这里需要查询用户的角色
      // 实际实现中应该从数据库获取用户在项目中的角色
      return true // 简化实现
    }

    // 检查用户是否可以访问自己的资源
    if (context?.userId === user.id) {
      return resource === 'users' && action === 'read'
    }

    return false
  }

  /**
   * 创建权限中间件
   */
  static requirePermission(
    resource: Resource,
    permission: Permission,
    context?: any
  ) {
    return (user: User) => {
      return this.hasPermission(user, resource, permission, context)
    }
  }

  /**
   * 创建多个权限检查
   */
  static requireAnyPermission(
    permissions: Array<{ resource: Resource; permission: Permission }>
  ) {
    return (user: User) => {
      return permissions.some(({ resource, permission }) =>
        this.hasPermission(user, resource, permission)
      )
    }
  }

  /**
   * 检查订阅限制
   */
  static checkSubscriptionLimits(
    subscriptionLimits: Record<string, number>,
    currentUsage: Record<string, number>,
    resource: Resource
  ): boolean {
    switch (resource) {
      case 'users':
        return currentUsage.users < subscriptionLimits.users
      case 'projects':
        return currentUsage.projects < subscriptionLimits.projects
      case 'integrations':
        return currentUsage.integrations < subscriptionLimits.integrations
      default:
        return true
    }
  }
}

// 权限装饰器
export function RequirePermission(resource: Resource, permission: Permission) {
  return function (
    target: any,
    propertyName: string,
    descriptor: PropertyDescriptor
  ) {
    const method = descriptor.value

    descriptor.value = async function (...args: any[]) {
      const user = args[0]?.user // 假设第一个参数包含用户信息

      if (!user || !RBAC.hasPermission(user, resource, permission)) {
        throw new Error('Insufficient permissions')
      }

      return method.apply(this, args)
    }

    return descriptor
  }
}

// API权限检查中间件
export function withAuth(
  handler: (req: Request, context: any) => Promise<Response>,
  requiredPermissions?: Array<{ resource: Resource; permission: Permission }>
) {
  return async (req: Request, context: any) => {
    const user = context.user

    if (!user) {
      return new Response('Unauthorized', { status: 401 })
    }

    if (requiredPermissions) {
      const hasPermission = requiredPermissions.some(({ resource, permission }) =>
        RBAC.hasPermission(user, resource, permission, context)
      )

      if (!hasPermission) {
        return new Response('Forbidden', { status: 403 })
      }
    }

    return handler(req, context)
  }
}
```

#### 2.4 实现实时通知系统
**lib/notifications/notification-service.ts**:
```typescript
import { Server as SocketIOServer } from 'socket.io'
import { Server as HTTPServer } from 'http'
import { getTenantPrisma } from '@/lib/db/tenant-prisma'
import { NotificationType } from '@prisma/client'

export interface NotificationData {
  userId: string
  tenantId: string
  type: NotificationType
  title: string
  content: string
  metadata?: Record<string, any>
}

export interface EmailNotificationData {
  to: string
  subject: string
  template: string
  data: Record<string, any>
}

export class NotificationService {
  private static io: SocketIOServer
  private static connectedUsers = new Map<string, Set<string>>()

  /**
   * 初始化Socket.IO服务器
   */
  static initialize(server: HTTPServer) {
    this.io = new SocketIOServer(server, {
      cors: {
        origin: process.env.NODE_ENV === 'production'
          ? process.env.ALLOWED_ORIGINS?.split(',')
          : ['http://localhost:3000'],
        methods: ['GET', 'POST'],
      },
    })

    this.io.on('connection', (socket) => {
      console.log('User connected:', socket.id)

      // 用户认证
      socket.on('authenticate', async (data: { userId: string; tenantId: string; token: string }) => {
        try {
          // 这里应该验证token
          const { userId, tenantId } = data

          // 将socket ID与用户关联
          if (!this.connectedUsers.has(`${tenantId}:${userId}`)) {
            this.connectedUsers.set(`${tenantId}:${userId}`, new Set())
          }
          this.connectedUsers.get(`${tenantId}:${userId}`)!.add(socket.id)

          // 加入租户房间
          socket.join(`tenant:${tenantId}`)
          // 加入用户房间
          socket.join(`user:${userId}`)

          socket.emit('authenticated', { success: true })

          // 发送未读通知
          await this.sendUnreadNotifications(userId, tenantId)
        } catch (error) {
          socket.emit('authenticated', { success: false, error: 'Authentication failed' })
        }
      })

      // 处理断开连接
      socket.on('disconnect', () => {
        console.log('User disconnected:', socket.id)

        // 清理连接映射
        for (const [key, sockets] of this.connectedUsers.entries()) {
          sockets.delete(socket.id)
          if (sockets.size === 0) {
            this.connectedUsers.delete(key)
          }
        }
      })

      // 标记通知为已读
      socket.on('mark_notification_read', async (notificationId: string) => {
        try {
          const [tenantId, userId] = this.getUserFromSocket(socket)
          if (tenantId && userId) {
            await this.markNotificationRead(notificationId, tenantId, userId)
            socket.emit('notification_marked_read', { notificationId })
          }
        } catch (error) {
          socket.emit('error', { message: 'Failed to mark notification as read' })
        }
      })

      // 获取通知列表
      socket.on('get_notifications', async (data: { page?: number; limit?: number }) => {
        try {
          const [tenantId, userId] = this.getUserFromSocket(socket)
          if (tenantId && userId) {
            const notifications = await this.getNotifications(
              userId,
              tenantId,
              data.page || 1,
              data.limit || 20
            )
            socket.emit('notifications', notifications)
          }
        } catch (error) {
          socket.emit('error', { message: 'Failed to get notifications' })
        }
      })
    })
  }

  /**
   * 发送实时通知
   */
  static async sendNotification(data: NotificationData) {
    const { userId, tenantId, type, title, content, metadata } = data

    try {
      // 保存到数据库
      const tenantDb = getTenantPrisma(tenantId)
      const notification = await tenantDb.notification.create({
        data: {
          userId,
          type,
          title,
          content,
          metadata,
        },
      })

      // 发送实时通知
      const userSockets = this.connectedUsers.get(`${tenantId}:${userId}`)
      if (userSockets && userSockets.size > 0) {
        this.io.to(`user:${userId}`).emit('notification', {
          id: notification.id,
          type: notification.type,
          title: notification.title,
          content: notification.content,
          metadata: notification.metadata,
          isRead: notification.isRead,
          createdAt: notification.createdAt,
        })
      }

      // 发送邮件通知（如果需要）
      if (this.shouldSendEmail(type)) {
        const user = await tenantDb.user.findUnique({ where: { id: userId } })
        if (user) {
          await this.sendEmailNotification({
            to: user.email,
            subject: title,
            template: this.getEmailTemplate(type),
            data: {
              userName: user.name,
              title,
              content,
              metadata,
            },
          })
        }
      }

      return notification
    } catch (error) {
      console.error('Failed to send notification:', error)
      throw error
    }
  }

  /**
   * 发送广播通知（租户级别）
   */
  static async sendBroadcastNotification(
    tenantId: string,
    data: Omit<NotificationData, 'userId'>
  ) {
    const { type, title, content, metadata } = data

    try {
      // 获取租户所有用户
      const tenantDb = getTenantPrisma(tenantId)
      const users = await tenantDb.user.findMany({
        where: { status: 'ACTIVE' },
      })

      // 为每个用户创建通知
      const notifications = await Promise.all(
        users.map(user =>
          tenantDb.notification.create({
            data: {
              userId: user.id,
              type,
              title,
              content,
              metadata,
            },
          })
        )
      )

      // 发送实时通知
      this.io.to(`tenant:${tenantId}`).emit('broadcast_notification', {
        type,
        title,
        content,
        metadata,
        createdAt: new Date(),
      })

      return notifications
    } catch (error) {
      console.error('Failed to send broadcast notification:', error)
      throw error
    }
  }

  /**
   * 标记通知为已读
   */
  static async markNotificationRead(
    notificationId: string,
    tenantId: string,
    userId: string
  ) {
    const tenantDb = getTenantPrisma(tenantId)

    const notification = await tenantDb.notification.updateMany({
      where: {
        id: notificationId,
        userId,
      },
      data: {
        isRead: true,
      },
    })

    return notification.count > 0
  }

  /**
   * 标记所有通知为已读
   */
  static async markAllNotificationsRead(tenantId: string, userId: string) {
    const tenantDb = getTenantPrisma(tenantId)

    const result = await tenantDb.notification.updateMany({
      where: {
        userId,
        isRead: false,
      },
      data: {
        isRead: true,
      },
    })

    return result.count
  }

  /**
   * 获取通知列表
   */
  static async getNotifications(
    userId: string,
    tenantId: string,
    page: number = 1,
    limit: number = 20
  ) {
    const tenantDb = getTenantPrisma(tenantId)

    const [notifications, total] = await Promise.all([
      tenantDb.notification.findMany({
        where: {
          userId,
        },
        orderBy: {
          createdAt: 'desc',
        },
        skip: (page - 1) * limit,
        take: limit,
      }),
      tenantDb.notification.count({
        where: {
          userId,
          isRead: false,
        },
      }),
    ])

    return {
      notifications,
      unreadCount: total,
      pagination: {
        page,
        limit,
        total: notifications.length,
      },
    }
  }

  /**
   * 发送未读通知
   */
  private static async sendUnreadNotifications(userId: string, tenantId: string) {
    const notifications = await this.getNotifications(userId, tenantId, 1, 50)

    if (notifications.notifications.length > 0) {
      this.io.to(`user:${userId}`).emit('unread_notifications', {
        notifications: notifications.notifications,
        unreadCount: notifications.unreadCount,
      })
    }
  }

  /**
   * 从socket获取用户信息
   */
  private static getUserFromSocket(socket: any): [string | null, string | null] {
    for (const [key, sockets] of this.connectedUsers.entries()) {
      if (sockets.has(socket.id)) {
        return key.split(':')
      }
    }
    return [null, null]
  }

  /**
   * 判断是否需要发送邮件
   */
  private static shouldSendEmail(type: NotificationType): boolean {
    const emailTypes = [
      NotificationType.BILLING,
      NotificationType.INVITATION,
      NotificationType.SECURITY,
    ]

    return emailTypes.includes(type)
  }

  /**
   * 获取邮件模板
   */
  private static getEmailTemplate(type: NotificationType): string {
    const templates: Record<NotificationType, string> = {
      [NotificationType.SYSTEM]: 'system-notification',
      [NotificationType.BILLING]: 'billing-notification',
      [NotificationType.PROJECT]: 'project-notification',
      [NotificationType.INVITATION]: 'invitation-notification',
      [NotificationType.SECURITY]: 'security-notification',
    }

    return templates[type] || 'default-notification'
  }

  /**
   * 发送邮件通知
   */
  private static async sendEmailNotification(data: EmailNotificationData) {
    // 这里应该集成邮件服务，如Resend
    console.log('Sending email notification:', data)
    // 实际实现中应该调用邮件服务API
  }
}
```

### 步骤三：高级特性实现

#### 3.1 实现白标定制功能
**lib/branding/branding-service.ts**:
```typescript
import { prisma } from '@/lib/db/prisma'

export interface BrandingConfig {
  logo?: string
  primaryColor?: string
  secondaryColor?: string
  accentColor?: string
  fontFamily?: string
  customCSS?: string
  favicon?: string
  domain?: string
  title?: string
  description?: string
  customDomain?: string
  footerText?: string
  socialLinks?: {
    twitter?: string
    linkedin?: string
    facebook?: string
  }
}

export interface BrandingCustomization {
  id: string
  tenantId: string
  config: BrandingConfig
  isActive: boolean
  createdAt: Date
  updatedAt: Date
}

export class BrandingService {
  /**
   * 获取租户的品牌配置
   */
  static async getTenantBranding(tenantId: string): Promise<BrandingConfig> {
    const tenant = await prisma.tenant.findUnique({
      where: { id: tenantId },
      select: { branding: true },
    })

    if (!tenant) {
      throw new Error('Tenant not found')
    }

    return {
      // 默认配置
      primaryColor: '#3b82f6',
      secondaryColor: '#64748b',
      accentColor: '#f59e0b',
      fontFamily: 'Inter, sans-serif',
      title: 'SaaS Platform',
      description: 'A powerful SaaS platform for your business',
      footerText: '© 2024 Your Company. All rights reserved.',
      ...tenant.branding,
    } as BrandingConfig
  }

  /**
   * 更新租户品牌配置
   */
  static async updateTenantBranding(
    tenantId: string,
    config: Partial<BrandingConfig>
  ): Promise<BrandingConfig> {
    // 验证配置
    const validatedConfig = this.validateBrandingConfig(config)

    const tenant = await prisma.tenant.update({
      where: { id: tenantId },
      data: {
        branding: validatedConfig,
      },
    })

    return tenant.branding as BrandingConfig
  }

  /**
   * 生成CSS变量
   */
  static generateCSSVariables(config: BrandingConfig): string {
    const variables = [
      `--brand-primary: ${config.primaryColor || '#3b82f6'}`,
      `--brand-secondary: ${config.secondaryColor || '#64748b'}`,
      `--brand-accent: ${config.accentColor || '#f59e0b'}`,
      `--brand-font-family: ${config.fontFamily || 'Inter, sans-serif'}`,
    ]

    if (config.customCSS) {
      variables.push(config.customCSS)
    }

    return variables.join(';\n')
  }

  /**
   * 生成品牌化组件
   */
  static generateBrandedComponents(config: BrandingConfig): string {
    return `
      .brand-header {
        background-color: ${config.primaryColor || '#3b82f6'};
        font-family: ${config.fontFamily || 'Inter, sans-serif'};
      }

      .brand-button-primary {
        background-color: ${config.primaryColor || '#3b82f6'};
        border-color: ${config.primaryColor || '#3b82f6'};
      }

      .brand-button-secondary {
        background-color: ${config.secondaryColor || '#64748b'};
        border-color: ${config.secondaryColor || '#64748b'};
      }

      .brand-accent {
        color: ${config.accentColor || '#f59e0b'};
      }

      .brand-footer {
        background-color: ${config.secondaryColor || '#64748b'};
        color: white;
      }
    `
  }

  /**
   * 上传品牌资源
   */
  static async uploadBrandAsset(
    tenantId: string,
    type: 'logo' | 'favicon',
    file: File
  ): Promise<string> {
    // 这里应该实现文件上传逻辑
    // 可以使用AWS S3、Cloudinary等服务

    const fileName = `${tenantId}-${type}-${Date.now()}.${file.type.split('/')[1]}`
    const url = `/uploads/branding/${fileName}`

    // 保存到租户配置
    await this.updateTenantBranding(tenantId, {
      [type]: url,
    })

    return url
  }

  /**
   * 设置自定义域名
   */
  static async setCustomDomain(
    tenantId: string,
    domain: string
  ): Promise<{ status: 'pending' | 'active' | 'error'; message: string }> {
    try {
      // 验证域名格式
      if (!this.isValidDomain(domain)) {
        return {
          status: 'error',
          message: 'Invalid domain format',
        }
      }

      // 检查域名是否已被使用
      const existingTenant = await prisma.tenant.findFirst({
        where: { domain },
      })

      if (existingTenant && existingTenant.id !== tenantId) {
        return {
          status: 'error',
          message: 'Domain is already in use',
        }
      }

      // 更新租户域名
      await prisma.tenant.update({
        where: { id: tenantId },
        data: { domain },
      })

      // 这里应该配置DNS和SSL证书
      // 实际实现中需要调用域名服务商的API

      return {
        status: 'pending',
        message: 'Domain configuration in progress',
      }
    } catch (error) {
      return {
        status: 'error',
        message: 'Failed to configure custom domain',
      }
    }
  }

  /**
   * 生成品牌化邮件模板
   */
  static generateEmailTemplate(
    config: BrandingConfig,
    templateType: 'welcome' | 'invoice' | 'notification'
  ): string {
    const baseStyles = `
      <style>
        .brand-header {
          background-color: ${config.primaryColor || '#3b82f6'};
          padding: 20px;
          text-align: center;
        }
        .brand-logo {
          max-height: 40px;
        }
        .brand-footer {
          background-color: ${config.secondaryColor || '#64748b'};
          color: white;
          padding: 20px;
          text-align: center;
        }
        .brand-button {
          background-color: ${config.primaryColor || '#3b82f6'};
          color: white;
          padding: 12px 24px;
          border-radius: 4px;
          text-decoration: none;
          display: inline-block;
        }
      </style>
    `

    const templates = {
      welcome: `
        ${baseStyles}
        <div class="brand-header">
          ${config.logo ? `<img src="${config.logo}" alt="Logo" class="brand-logo">` : `<h1>${config.title || 'Welcome'}</h1>`}
        </div>
        <div style="padding: 20px;">
          <h2>Welcome to ${config.title || 'our platform'}!</h2>
          <p>Thank you for joining us. We're excited to have you on board.</p>
          <a href="#" class="brand-button">Get Started</a>
        </div>
        <div class="brand-footer">
          <p>${config.footerText || '© 2024 Your Company'}</p>
        </div>
      `,
      invoice: `
        ${baseStyles}
        <div class="brand-header">
          ${config.logo ? `<img src="${config.logo}" alt="Logo" class="brand-logo">` : `<h1>Invoice</h1>`}
        </div>
        <div style="padding: 20px;">
          <h2>Invoice from ${config.title || 'our platform'}</h2>
          <p>Your invoice is ready for review.</p>
          <a href="#" class="brand-button">View Invoice</a>
        </div>
        <div class="brand-footer">
          <p>${config.footerText || '© 2024 Your Company'}</p>
        </div>
      `,
      notification: `
        ${baseStyles}
        <div class="brand-header">
          ${config.logo ? `<img src="${config.logo}" alt="Logo" class="brand-logo">` : `<h1>Notification</h1>`}
        </div>
        <div style="padding: 20px;">
          <h2>You have a new notification</h2>
          <p>Something important requires your attention.</p>
          <a href="#" class="brand-button">View Details</a>
        </div>
        <div class="brand-footer">
          <p>${config.footerText || '© 2024 Your Company'}</p>
        </div>
      `,
    }

    return templates[templateType] || templates.notification
  }

  /**
   * 验证品牌配置
   */
  private static validateBrandingConfig(config: Partial<BrandingConfig>): Partial<BrandingConfig> {
    const validated: Partial<BrandingConfig> = {}

    if (config.primaryColor && this.isValidColor(config.primaryColor)) {
      validated.primaryColor = config.primaryColor
    }

    if (config.secondaryColor && this.isValidColor(config.secondaryColor)) {
      validated.secondaryColor = config.secondaryColor
    }

    if (config.accentColor && this.isValidColor(config.accentColor)) {
      validated.accentColor = config.accentColor
    }

    if (config.fontFamily) {
      validated.fontFamily = config.fontFamily
    }

    if (config.title && config.title.length <= 100) {
      validated.title = config.title
    }

    if (config.description && config.description.length <= 500) {
      validated.description = config.description
    }

    if (config.footerText && config.footerText.length <= 200) {
      validated.footerText = config.footerText
    }

    if (config.logo && this.isValidUrl(config.logo)) {
      validated.logo = config.logo
    }

    if (config.favicon && this.isValidUrl(config.favicon)) {
      validated.favicon = config.favicon
    }

    if (config.customDomain && this.isValidDomain(config.customDomain)) {
      validated.customDomain = config.customDomain
    }

    if (config.customCSS && config.customCSS.length <= 10000) {
      validated.customCSS = config.customCSS
    }

    return validated
  }

  /**
   * 验证颜色格式
   */
  private static isValidColor(color: string): boolean {
    const colorRegex = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/
    return colorRegex.test(color)
  }

  /**
   * 验证URL格式
   */
  private static isValidUrl(url: string): boolean {
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  }

  /**
   * 验证域名格式
   */
  private static isValidDomain(domain: string): boolean {
    const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+$/
    return domainRegex.test(domain)
  }

  /**
   * 预览品牌配置
   */
  static async previewBranding(
    tenantId: string,
    config: Partial<BrandingConfig>
  ): Promise<{
    cssVariables: string
    components: string
    emailTemplate: string
  }> {
    const currentConfig = await this.getTenantBranding(tenantId)
    const previewConfig = { ...currentConfig, ...config }

    return {
      cssVariables: this.generateCSSVariables(previewConfig),
      components: this.generateBrandedComponents(previewConfig),
      emailTemplate: this.generateEmailTemplate(previewConfig, 'welcome'),
    }
  }
}
```

#### 3.2 实现API集成系统
**lib/integrations/integration-service.ts**:
```typescript
import { prisma } from '@/lib/db/prisma'

export interface IntegrationConfig {
  type: IntegrationType
  name: string
  description?: string
  credentials: Record<string, any>
  settings: Record<string, any>
  webhookUrl?: string
  isActive: boolean
}

export enum IntegrationType {
  SLACK = 'slack',
  GOOGLE_ANALYTICS = 'google_analytics',
  ZAPIER = 'zapier',
  WEBHOOK = 'webhook',
  STRIPE = 'stripe',
  SENDGRID = 'sendgrid',
  CUSTOM = 'custom',
}

export interface IntegrationEvent {
  type: string
  data: Record<string, any>
  tenantId: string
  userId?: string
  timestamp: Date
}

export class IntegrationService {
  /**
   * 创建集成
   */
  static async createIntegration(
    tenantId: string,
    config: Omit<IntegrationConfig, 'isActive'>
  ): Promise<any> {
    // 验证集成配置
    this.validateIntegrationConfig(config.type, config.credentials, config.settings)

    const integration = await prisma.integration.create({
      data: {
        tenantId,
        type: config.type,
        name: config.name,
        description: config.description,
        credentials: config.credentials,
        settings: config.settings,
        webhookUrl: config.webhookUrl,
        isActive: true,
      },
    })

    // 测试集成连接
    await this.testIntegration(integration.id)

    return integration
  }

  /**
   * 触发集成事件
   */
  static async triggerEvent(event: IntegrationEvent): Promise<void> {
    // 获取租户的所有活跃集成
    const integrations = await prisma.integration.findMany({
      where: {
        tenantId: event.tenantId,
        isActive: true,
      },
    })

    // 并行处理所有集成
    await Promise.allSettled(
      integrations.map(integration =>
        this.processIntegrationEvent(integration, event)
      )
    )
  }

  /**
   * 处理单个集成事件
   */
  private static async processIntegrationEvent(
    integration: any,
    event: IntegrationEvent
  ): Promise<void> {
    try {
      switch (integration.type) {
        case IntegrationType.SLACK:
          await this.sendSlackNotification(integration, event)
          break
        case IntegrationType.GOOGLE_ANALYTICS:
          await this.sendGoogleAnalyticsEvent(integration, event)
          break
        case IntegrationType.ZAPIER:
          await this.sendZapierWebhook(integration, event)
          break
        case IntegrationType.WEBHOOK:
          await this.sendCustomWebhook(integration, event)
          break
        case IntegrationType.STRIPE:
          await this.processStripeEvent(integration, event)
          break
        case IntegrationType.SENDGRID:
          await this.sendSendgridEmail(integration, event)
          break
        case IntegrationType.CUSTOM:
          await this.processCustomIntegration(integration, event)
          break
        default:
          console.warn(`Unknown integration type: ${integration.type}`)
      }
    } catch (error) {
      console.error(`Failed to process event for integration ${integration.id}:`, error)

      // 记录错误日志
      await this.logIntegrationError(integration.id, event, error)
    }
  }

  /**
   * 发送Slack通知
   */
  private static async sendSlackNotification(
    integration: any,
    event: IntegrationEvent
  ): Promise<void> {
    const { webhookUrl, settings } = integration.credentials
    const { channel, username, icon_emoji } = settings

    const payload = {
      channel: channel || '#general',
      username: username || 'SaaS Platform',
      icon_emoji: icon_emoji || ':robot_face:',
      text: this.formatSlackMessage(event),
      attachments: this.createSlackAttachments(event),
    }

    const response = await fetch(webhookUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      throw new Error(`Slack webhook failed: ${response.statusText}`)
    }
  }

  /**
   * 发送Google Analytics事件
   */
  private static async sendGoogleAnalyticsEvent(
    integration: any,
    event: IntegrationEvent
  ): Promise<void> {
    const { measurementId, apiSecret } = integration.credentials

    const payload = {
      client_id: event.tenantId,
      events: [
        {
          name: event.type,
          parameters: {
            tenant_id: event.tenantId,
            user_id: event.userId,
            timestamp: event.timestamp.toISOString(),
            ...event.data,
          },
        },
      ],
    }

    const url = `https://www.google-analytics.com/mp/collect?measurement_id=${measurementId}&api_secret=${apiSecret}`

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      throw new Error(`Google Analytics request failed: ${response.statusText}`)
    }
  }

  /**
   * 发送Zapier Webhook
   */
  private static async sendZapierWebhook(
    integration: any,
    event: IntegrationEvent
  ): Promise<void> {
    const { webhookUrl } = integration.credentials

    const payload = {
      event_type: event.type,
      tenant_id: event.tenantId,
      user_id: event.userId,
      timestamp: event.timestamp.toISOString(),
      data: event.data,
    }

    const response = await fetch(webhookUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      throw new Error(`Zapier webhook failed: ${response.statusText}`)
    }
  }

  /**
   * 发送自定义Webhook
   */
  private static async sendCustomWebhook(
    integration: any,
    event: IntegrationEvent
  ): Promise<void> {
    const { url, method = 'POST', headers = {}, auth } = integration.credentials
    const { retryCount = 3, timeout = 10000 } = integration.settings

    const payload = {
      event: event.type,
      tenant_id: event.tenantId,
      user_id: event.userId,
      timestamp: event.timestamp.toISOString(),
      data: event.data,
    }

    const requestHeaders = {
      'Content-Type': 'application/json',
      ...headers,
    }

    // 添加认证头
    if (auth?.type === 'bearer') {
      requestHeaders.Authorization = `Bearer ${auth.token}`
    } else if (auth?.type === 'basic') {
      requestHeaders.Authorization = `Basic ${Buffer.from(`${auth.username}:${auth.password}`).toString('base64')}`
    }

    let lastError: Error | null = null

    for (let attempt = 1; attempt <= retryCount; attempt++) {
      try {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), timeout)

        const response = await fetch(url, {
          method,
          headers: requestHeaders,
          body: JSON.stringify(payload),
          signal: controller.signal,
        })

        clearTimeout(timeoutId)

        if (!response.ok) {
          throw new Error(`Webhook failed: ${response.statusText}`)
        }

        return // 成功，退出重试循环
      } catch (error) {
        lastError = error as Error
        console.warn(`Webhook attempt ${attempt} failed:`, error)

        if (attempt < retryCount) {
          // 指数退避
          await new Promise(resolve =>
            setTimeout(resolve, Math.pow(2, attempt) * 1000)
          )
        }
      }
    }

    throw lastError || new Error('Webhook failed after all retries')
  }

  /**
   * 测试集成连接
   */
  static async testIntegration(integrationId: string): Promise<boolean> {
    const integration = await prisma.integration.findUnique({
      where: { id: integrationId },
    })

    if (!integration) {
      throw new Error('Integration not found')
    }

    try {
      const testEvent: IntegrationEvent = {
        type: 'integration_test',
        data: { test: true },
        tenantId: integration.tenantId,
        timestamp: new Date(),
      }

      await this.processIntegrationEvent(integration, testEvent)
      return true
    } catch (error) {
      console.error('Integration test failed:', error)
      return false
    }
  }

  /**
   * 获取集成类型模板
   */
  static getIntegrationTemplate(type: IntegrationType): {
    fields: Array<{
      key: string
      label: string
      type: 'text' | 'password' | 'url' | 'number' | 'boolean'
      required: boolean
      placeholder?: string
      description?: string
    }>
    settings: Array<{
      key: string
      label: string
      type: 'text' | 'number' | 'boolean' | 'select'
      required: boolean
      options?: string[]
      defaultValue?: any
    }>
  } {
    const templates = {
      [IntegrationType.SLACK]: {
        fields: [
          {
            key: 'webhookUrl',
            label: 'Webhook URL',
            type: 'url',
            required: true,
            description: 'Your Slack incoming webhook URL',
          },
        ],
        settings: [
          {
            key: 'channel',
            label: 'Default Channel',
            type: 'text',
            required: false,
            defaultValue: '#general',
          },
          {
            key: 'username',
            label: 'Bot Username',
            type: 'text',
            required: false,
            defaultValue: 'SaaS Platform',
          },
        ],
      },
      [IntegrationType.GOOGLE_ANALYTICS]: {
        fields: [
          {
            key: 'measurementId',
            label: 'Measurement ID',
            type: 'text',
            required: true,
            placeholder: 'G-XXXXXXXXXX',
          },
          {
            key: 'apiSecret',
            label: 'API Secret',
            type: 'password',
            required: true,
          },
        ],
        settings: [],
      },
      [IntegrationType.WEBHOOK]: {
        fields: [
          {
            key: 'url',
            label: 'Webhook URL',
            type: 'url',
            required: true,
          },
        ],
        settings: [
          {
            key: 'method',
            label: 'HTTP Method',
            type: 'select',
            required: false,
            options: ['POST', 'PUT', 'PATCH'],
            defaultValue: 'POST',
          },
          {
            key: 'retryCount',
            label: 'Retry Count',
            type: 'number',
            required: false,
            defaultValue: 3,
          },
        ],
      },
    }

    return templates[type] || { fields: [], settings: [] }
  }

  /**
   * 验证集成配置
   */
  private static validateIntegrationConfig(
    type: IntegrationType,
    credentials: Record<string, any>,
    settings: Record<string, any>
  ): void {
    const template = this.getIntegrationTemplate(type)

    // 验证必填字段
    for (const field of template.fields) {
      if (field.required && !credentials[field.key]) {
        throw new Error(`Required field '${field.label}' is missing`)
      }
    }

    // 验证字段格式
    for (const field of template.fields) {
      const value = credentials[field.key]
      if (value && field.type === 'url' && !this.isValidUrl(value)) {
        throw new Error(`Field '${field.label}' must be a valid URL`)
      }
    }
  }

  /**
   * 格式化Slack消息
   */
  private static formatSlackMessage(event: IntegrationEvent): string {
    const eventTypeMap: Record<string, string> = {
      user_created: '👤 New User Created',
      subscription_created: '💳 New Subscription',
      project_created: '📁 New Project Created',
      invoice_paid: '💰 Invoice Paid',
    }

    return eventTypeMap[event.type] || `📢 ${event.type}`
  }

  /**
   * 创建Slack附件
   */
  private static createSlackAttachments(event: IntegrationEvent): any[] {
    return [
      {
        color: this.getEventColor(event.type),
        fields: [
          {
            title: 'Tenant ID',
            value: event.tenantId,
            short: true,
          },
          {
            title: 'Timestamp',
            value: event.timestamp.toLocaleString(),
            short: true,
          },
        ],
      },
    ]
  }

  /**
   * 获取事件颜色
   */
  private static getEventColor(eventType: string): string {
    const colorMap: Record<string, string> = {
      user_created: 'good',
      subscription_created: 'good',
      project_created: 'good',
      invoice_paid: 'good',
      user_deleted: 'danger',
      subscription_cancelled: 'warning',
      payment_failed: 'danger',
    }

    return colorMap[eventType] || 'good'
  }

  /**
   * 验证URL格式
   */
  private static isValidUrl(url: string): boolean {
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  }

  /**
   * 记录集成错误
   */
  private static async logIntegrationError(
    integrationId: string,
    event: IntegrationEvent,
    error: any
  ): Promise<void> {
    // 这里应该记录到数据库或日志系统
    console.error('Integration error:', {
      integrationId,
      eventType: event.type,
      tenantId: event.tenantId,
      error: error.message,
      stack: error.stack,
    })
  }

  /**
   * 处理Stripe事件（占位符）
   */
  private static async processStripeEvent(
    integration: any,
    event: IntegrationEvent
  ): Promise<void> {
    // Stripe特定的处理逻辑
  }

  /**
   * 发送SendGrid邮件（占位符）
   */
  private static async sendSendgridEmail(
    integration: any,
    event: IntegrationEvent
  ): Promise<void> {
    // SendGrid特定的处理逻辑
  }

  /**
   * 处理自定义集成（占位符）
   */
  private static async processCustomIntegration(
    integration: any,
    event: IntegrationEvent
  ): Promise<void> {
    // 自定义集成处理逻辑
  }
}
```

#### 3.3 工作区元数据与文件约定（metadata / error / loading / not-found）

> 📖 呼应字典：[错误与加载状态约定](../reference/framework-patterns/11-error-loading-patterns.md)、[网络代理（proxy.ts）](../reference/framework-patterns/10-proxy-patterns.md)

多租户 SaaS 的元数据需要跟随租户（白标）——标题、favicon 随 workspace 变化；租户访问他人资源时应走 `not-found` 约定而不是抛 500。

**工作区布局元数据（app/[workspace]/layout.tsx）**——`generateMetadata` 读取租户品牌配置：

```typescript
import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { getWorkspaceBySlug } from '@/lib/tenant';

interface WorkspaceLayoutProps {
  children: React.ReactNode;
  params: Promise<{ workspace: string }>;
}

export async function generateMetadata({ params }: WorkspaceLayoutProps): Promise<Metadata> {
  const { workspace: slug } = await params;
  const workspace = await getWorkspaceBySlug(slug);
  if (!workspace) notFound(); // 租户不存在 → 404 约定

  return {
    title: { default: workspace.name, template: `%s | ${workspace.name}` },
    description: workspace.description,
    icons: workspace.branding?.faviconUrl
      ? { icon: workspace.branding.faviconUrl }
      : undefined,
  };
}

export default async function WorkspaceLayout({ children, params }: WorkspaceLayoutProps) {
  const { workspace: slug } = await params;
  const workspace = await getWorkspaceBySlug(slug);
  if (!workspace) notFound();

  return <TenantProvider workspace={workspace}>{children}</TenantProvider>;
}
```

**加载兜底（app/[workspace]/dashboard/loading.tsx）**：

```typescript
export default function Loading() {
  return (
    <div className="animate-pulse space-y-6 p-8">
      <div className="h-8 w-56 rounded bg-gray-200" />
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-24 rounded-lg bg-gray-200" />
        ))}
      </div>
      <div className="h-96 rounded-xl bg-gray-200" />
    </div>
  );
}
```

**错误边界（app/[workspace]/error.tsx）**——必须是客户端组件，文案区分权限与故障：

```typescript
'use client';

export default function WorkspaceError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div role="alert" className="p-8 text-center">
      <h2 className="text-lg font-semibold">页面加载失败</h2>
      <p className="mt-2 text-sm text-gray-500">
        若问题持续，请联系你的工作区管理员（错误 ID: {error.digest ?? '未知'}）。
      </p>
      <button onClick={reset} className="mt-4 rounded-md bg-indigo-600 px-4 py-2 text-white">
        重试
      </button>
    </div>
  );
}
```

**404 约定（app/[workspace]/not-found.tsx）**——承接上方 `generateMetadata` 中的 `notFound()`，也覆盖租户访问他人资源被 `getWorkspaceBySlug` 拒绝的场景：

```typescript
import Link from 'next/link';

export default function WorkspaceNotFound() {
  return (
    <div className="p-8 text-center">
      <h2 className="text-lg font-semibold">工作区不存在或你无权访问</h2>
      <p className="mt-2 text-sm text-gray-500">请确认链接是否正确，或联系管理员邀请你加入。</p>
      <Link href="/" className="mt-4 inline-block text-indigo-600 underline">
        返回首页
      </Link>
    </div>
  );
}
```

**应用级最后防线（app/global-error.tsx）**——替换整个根布局，必须自带 `<html>`/`<body>`：

```typescript
'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="zh-CN">
      <body>
        <div style={{ padding: 48, textAlign: 'center' }}>
          <h2>应用暂时不可用</h2>
          <p>我们的团队已收到告警（ID: {error.digest ?? '未知'}）。</p>
          <button onClick={reset}>重试</button>
        </div>
      </body>
    </html>
  );
}
```

要点（详见上方字典）：`error.tsx` 不捕获同层 `layout.tsx` 抛出的错误——上方 WorkspaceLayout 中的 `notFound()` 会向上冒泡到父级约定，因此多租户校验建议优先放在 1.3 的 `proxy.ts`（请求进入路由前完成租户识别）；`global-error.tsx` 渲染时替换根布局，样式需内联；生产环境 `error` 对象被脱敏，排查依赖服务端日志与 `digest`。

### 步骤四：测试和优化

#### 4.1 多租户测试策略
**__tests__/multi-tenant/tenant-isolation.test.ts**:
```typescript
import { describe, it, expect, beforeEach, afterEach } from '@jest/globals'
import { prisma } from '@/lib/db/prisma'
import { getTenantPrisma, cleanupTenantPrisma } from '@/lib/db/tenant-prisma'

describe('Multi-Tenant Data Isolation', () => {
  let tenant1Id: string
  let tenant2Id: string
  let user1Id: string
  let user2Id: string

  beforeEach(async () => {
    // 创建测试租户
    const tenant1 = await prisma.tenant.create({
      data: {
        platformId: 'test-platform',
        name: 'Tenant 1',
        slug: 'tenant-1',
      },
    })

    const tenant2 = await prisma.tenant.create({
      data: {
        platformId: 'test-platform',
        name: 'Tenant 2',
        slug: 'tenant-2',
      },
    })

    tenant1Id = tenant1.id
    tenant2Id = tenant2.id

    // 为每个租户创建用户
    const tenant1Db = getTenantPrisma(tenant1Id)
    const tenant2Db = getTenantPrisma(tenant2Id)

    const user1 = await tenant1Db.user.create({
      data: {
        email: 'user1@tenant1.com',
        name: 'User 1',
        platformUserId: 'platform-user-1',
      },
    })

    const user2 = await tenant2Db.user.create({
      data: {
        email: 'user1@tenant2.com',
        name: 'User 2',
        platformUserId: 'platform-user-1',
      },
    })

    user1Id = user1.id
    user2Id = user2.id
  })

  afterEach(async () => {
    // 清理测试数据
    await prisma.tenant.deleteMany({
      where: {
        id: { in: [tenant1Id, tenant2Id] },
      },
    })

    cleanupTenantPrisma(tenant1Id)
    cleanupTenantPrisma(tenant2Id)
  })

  it('should isolate user data between tenants', async () => {
    const tenant1Db = getTenantPrisma(tenant1Id)
    const tenant2Db = getTenantPrisma(tenant2Id)

    // 获取各自租户的用户
    const tenant1Users = await tenant1Db.user.findMany()
    const tenant2Users = await tenant2Db.user.findMany()

    expect(tenant1Users).toHaveLength(1)
    expect(tenant2Users).toHaveLength(1)
    expect(tenant1Users[0].id).not.toBe(tenant2Users[0].id)
  })

  it('should prevent cross-tenant data access', async () => {
    const tenant1Db = getTenantPrisma(tenant1Id)

    // 尝试从租户1访问租户2的用户ID
    const user = await tenant1Db.user.findUnique({
      where: { id: user2Id },
    })

    expect(user).toBeNull()
  })

  it('should maintain separate project spaces', async () => {
    const tenant1Db = getTenantPrisma(tenant1Id)
    const tenant2Db = getTenantPrisma(tenant2Id)

    // 在不同租户创建同名项目
    await tenant1Db.project.create({
      data: {
        name: 'Shared Project',
        description: 'Project in tenant 1',
      },
    })

    await tenant2Db.project.create({
      data: {
        name: 'Shared Project',
        description: 'Project in tenant 2',
      },
    })

    const tenant1Projects = await tenant1Db.project.findMany()
    const tenant2Projects = await tenant2Db.project.findMany()

    expect(tenant1Projects).toHaveLength(1)
    expect(tenant2Projects).toHaveLength(1)
    expect(tenant1Projects[0].description).toBe('Project in tenant 1')
    expect(tenant2Projects[0].description).toBe('Project in tenant 2')
  })
})
```

#### 4.2 性能监控和优化
**lib/monitoring/performance-monitor.ts**:
```typescript
export interface PerformanceMetrics {
  responseTime: number
  memoryUsage: number
  cpuUsage: number
  activeConnections: number
  errorRate: number
  timestamp: Date
}

export interface AlertThresholds {
  responseTime: number
  memoryUsage: number
  cpuUsage: number
  errorRate: number
}

export class PerformanceMonitor {
  private static metrics: PerformanceMetrics[] = []
  private static alertThresholds: AlertThresholds = {
    responseTime: 1000, // 1秒
    memoryUsage: 80,   // 80%
    cpuUsage: 80,      // 80%
    errorRate: 5,      // 5%
  }

  /**
   * 记录性能指标
   */
  static recordMetrics(metrics: Partial<PerformanceMetrics>): void {
    const fullMetrics: PerformanceMetrics = {
      responseTime: 0,
      memoryUsage: 0,
      cpuUsage: 0,
      activeConnections: 0,
      errorRate: 0,
      timestamp: new Date(),
      ...metrics,
    }

    this.metrics.push(fullMetrics)

    // 保留最近1小时的数据
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000)
    this.metrics = this.metrics.filter(m => m.timestamp > oneHourAgo)

    // 检查是否需要发送警报
    this.checkAlerts(fullMetrics)
  }

  /**
   * 获取性能指标
   */
  static getMetrics(timeRange?: { start: Date; end: Date }): PerformanceMetrics[] {
    if (!timeRange) {
      return [...this.metrics]
    }

    return this.metrics.filter(
      m => m.timestamp >= timeRange.start && m.timestamp <= timeRange.end
    )
  }

  /**
   * 获取性能统计
   */
  static getPerformanceStats(): {
    avgResponseTime: number
    maxResponseTime: number
    avgMemoryUsage: number
    maxMemoryUsage: number
    avgCpuUsage: number
    maxCpuUsage: number
    avgErrorRate: number
    totalRequests: number
  } {
    if (this.metrics.length === 0) {
      return {
        avgResponseTime: 0,
        maxResponseTime: 0,
        avgMemoryUsage: 0,
        maxMemoryUsage: 0,
        avgCpuUsage: 0,
        maxCpuUsage: 0,
        avgErrorRate: 0,
        totalRequests: 0,
      }
    }

    const responseTimes = this.metrics.map(m => m.responseTime)
    const memoryUsages = this.metrics.map(m => m.memoryUsage)
    const cpuUsages = this.metrics.map(m => m.cpuUsage)
    const errorRates = this.metrics.map(m => m.errorRate)

    return {
      avgResponseTime: responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length,
      maxResponseTime: Math.max(...responseTimes),
      avgMemoryUsage: memoryUsages.reduce((a, b) => a + b, 0) / memoryUsages.length,
      maxMemoryUsage: Math.max(...memoryUsages),
      avgCpuUsage: cpuUsages.reduce((a, b) => a + b, 0) / cpuUsages.length,
      maxCpuUsage: Math.max(...cpuUsages),
      avgErrorRate: errorRates.reduce((a, b) => a + b, 0) / errorRates.length,
      totalRequests: this.metrics.length,
    }
  }

  /**
   * 设置警报阈值
   */
  static setAlertThresholds(thresholds: Partial<AlertThresholds>): void {
    this.alertThresholds = { ...this.alertThresholds, ...thresholds }
  }

  /**
   * 检查警报
   */
  private static checkAlerts(metrics: PerformanceMetrics): void {
    const alerts = []

    if (metrics.responseTime > this.alertThresholds.responseTime) {
      alerts.push({
        type: 'response_time',
        message: `Response time exceeded threshold: ${metrics.responseTime}ms`,
        severity: 'warning',
      })
    }

    if (metrics.memoryUsage > this.alertThresholds.memoryUsage) {
      alerts.push({
        type: 'memory_usage',
        message: `Memory usage exceeded threshold: ${metrics.memoryUsage}%`,
        severity: 'critical',
      })
    }

    if (metrics.cpuUsage > this.alertThresholds.cpuUsage) {
      alerts.push({
        type: 'cpu_usage',
        message: `CPU usage exceeded threshold: ${metrics.cpuUsage}%`,
        severity: 'warning',
      })
    }

    if (metrics.errorRate > this.alertThresholds.errorRate) {
      alerts.push({
        type: 'error_rate',
        message: `Error rate exceeded threshold: ${metrics.errorRate}%`,
        severity: 'critical',
      })
    }

    // 发送警报
    alerts.forEach(alert => this.sendAlert(alert))
  }

  /**
   * 发送警报
   */
  private static async sendAlert(alert: {
    type: string
    message: string
    severity: string
  }): Promise<void> {
    console.error(`[ALERT] ${alert.severity.toUpperCase()}: ${alert.message}`)

    // 这里可以集成警报服务，如：
    // - 发送邮件通知
    // - 发送Slack通知
    // - 发送SMS通知
    // - 集成监控服务（如Sentry、DataDog等）
  }

  /**
   * 监控API响应时间
   */
  static monitorApiResponse(
    req: Request,
    res: Response,
    startTime: number
  ): void {
    const responseTime = Date.now() - startTime

    this.recordMetrics({
      responseTime,
      timestamp: new Date(),
    })
  }

  /**
   * 监控内存使用
   */
  static monitorMemoryUsage(): void {
    if (typeof process !== 'undefined' && process.memoryUsage) {
      const memoryUsage = process.memoryUsage()
      const usedMemory = memoryUsage.heapUsed / 1024 / 1024 // MB
      const totalMemory = memoryUsage.heapTotal / 1024 / 1024 // MB
      const memoryUsagePercent = (usedMemory / totalMemory) * 100

      this.recordMetrics({
        memoryUsage: Math.round(memoryUsagePercent),
        timestamp: new Date(),
      })
    }
  }

  /**
   * 监控CPU使用
   */
  static monitorCpuUsage(): void {
    // CPU使用率监控需要系统特定的实现
    // 这里可以使用系统调用或第三方库
    const cpuUsage = this.getCpuUsage()

    this.recordMetrics({
      cpuUsage,
      timestamp: new Date(),
    })
  }

  /**
   * 获取CPU使用率（简化实现）
   */
  private static getCpuUsage(): number {
    // 实际实现中应该使用系统API或第三方库
    // 这里返回一个模拟值
    return Math.random() * 100
  }

  /**
   * 启动性能监控
   */
  static startMonitoring(): void {
    // 每30秒记录一次内存使用
    setInterval(() => {
      this.monitorMemoryUsage()
    }, 30000)

    // 每60秒记录一次CPU使用
    setInterval(() => {
      this.monitorCpuUsage()
    }, 60000)

    console.log('Performance monitoring started')
  }

  /**
   * 停止性能监控
   */
  static stopMonitoring(): void {
    console.log('Performance monitoring stopped')
  }

  /**
   * 生成性能报告
   */
  static generateReport(timeRange?: { start: Date; end: Date }): {
    summary: any
    metrics: PerformanceMetrics[]
    recommendations: string[]
  } {
    const metrics = this.getMetrics(timeRange)
    const stats = this.getPerformanceStats()

    const recommendations = []

    if (stats.avgResponseTime > 500) {
      recommendations.push('Consider optimizing API responses or implementing caching')
    }

    if (stats.maxMemoryUsage > 85) {
      recommendations.push('High memory usage detected. Check for memory leaks')
    }

    if (stats.avgErrorRate > 1) {
      recommendations.push('High error rate detected. Review error logs and fix issues')
    }

    return {
      summary: stats,
      metrics,
      recommendations,
    }
  }
}
```

### 步骤五：部署和上线

#### 5.1 生产环境配置
**.env.production**:
```bash
# Database
DATABASE_URL="postgresql://username:password@host:5432/saas_prod"

# NextAuth
NEXTAUTH_URL="https://yourdomain.com"
NEXTAUTH_SECRET="your-super-secret-key"

# Stripe
STRIPE_SECRET_KEY="sk_live_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
STRIPE_CONNECT_CLIENT_ID="ca_..."

# Email
RESEND_API_KEY="re_..."

# File Storage
AWS_ACCESS_KEY_ID="your-aws-access-key"
AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
AWS_REGION="us-east-1"
AWS_S3_BUCKET="your-s3-bucket"

# Redis
REDIS_URL="redis://your-redis-host:6379"

# Monitoring
SENTRY_DSN="https://your-sentry-dsn"
LOGROCKET_APP_ID="your-logrocket-id"

# Analytics
GOOGLE_ANALYTICS_ID="GA-XXXXXXXXX"

# Features
ENABLE_MULTITENANT=true
ENABLE_BILLING=true
ENABLE_INTEGRATIONS=true
ENABLE_WHITE_LABEL=true

# Security
CORS_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"
RATE_LIMIT_MAX=100
RATE_LIMIT_WINDOW=900000

# Performance
ENABLE_CACHING=true
CACHE_TTL=3600
COMPRESSION=true
```

#### 5.2 部署配置
**next.config.js**:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  serverExternalPackages: ['@prisma/client', 'stripe'],
  images: {
    remotePatterns: [
      { protocol: 'http', hostname: 'localhost' },
      { protocol: 'https', hostname: 'your-domain.com' },
      { protocol: 'https', hostname: 'your-s3-bucket.s3.amazonaws.com' },
    ],
    formats: ['image/webp', 'image/avif'],
  },
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  poweredByHeader: false,
  compress: true,
  generateEtags: true,

  // 安全头
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
      {
        source: '/api/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'no-store, must-revalidate',
          },
        ],
      },
    ]
  },

  // 重定向规则
  async redirects() {
    return [
      {
        source: '/home',
        destination: '/dashboard',
        permanent: true,
      },
    ]
  },

  // Webpack配置
  webpack: (config, { isServer, dev }) => {
    if (!dev && !isServer) {
      // 生产环境优化
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          default: {
            minChunks: 2,
            priority: -20,
            reuseExistingChunk: true,
          },
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            priority: -10,
            chunks: 'all',
          },
          common: {
            name: 'common',
            minChunks: 2,
            priority: -30,
            chunks: 'all',
            reuseExistingChunk: true,
          },
        },
      }
    }

    return config
  },
}

module.exports = nextConfig
```

## 💡 关键技术点

### 1. 多租户架构
- 数据隔离策略（Schema分离 vs Row Level Security）
- 租户识别和路由
- 资源共享和隔离
- 性能优化和扩展

### 2. 订阅计费系统
- Stripe Billing集成
- 订阅生命周期管理
- 使用量限制和监控
- 计费事件处理

### 3. 权限控制系统
- RBAC模型实现
- 细粒度权限控制
- 动态权限检查
- 审计日志

### 4. 白标解决方案
- 品牌定制系统
- 域名配置管理
- CSS变量和主题
- 邮件模板定制

### 5. 集成和API管理
- 第三方服务集成
- Webhook处理
- 事件驱动架构
- 错误处理和重试

## 🎨 UI/UX设计

### SaaS平台设计原则
- **一致性**: 统一的设计语言和交互模式
- **可访问性**: 符合WCAG标准的无障碍设计
- **国际化**: 多语言和地区支持
- **可定制性**: 品牌和主题定制能力

### 关键页面设计
1. **登录/注册**: 简洁的认证流程
2. **仪表板**: 清晰的数据展示和导航
3. **设置页面**: 分组的设置选项
4. **计费页面**: 透明的定价和订阅管理
5. **用户管理**: 直观的用户和权限管理

## 📱 响应式设计

### 移动端适配
- 触摸友好的交互设计
- 移动端导航优化
- 响应式表格和数据展示
- 离线功能支持

### 关键断点
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

## ⚡ 性能优化

### 1. 前端优化
- 代码分割和懒加载
- 图片优化和CDN
- 缓存策略
- 服务端渲染

### 2. 后端优化
- 数据库查询优化
- 连接池管理
- API响应缓存
- 负载均衡

### 3. SaaS特定优化
- 多租户资源隔离
- 数据库连接管理
- 计阅限制检查
- 使用量监控

## 🔒 安全考虑

### 1. 多租户安全
- 数据隔离验证
- 跨租户攻击防护
- 租户配置安全
- 审计和监控

### 2. 应用安全
- 认证和授权
- API安全
- 数据加密
- 安全头配置

### 3. 合规性
- GDPR合规
- 数据保护
- 隐私政策
- 安全审计

## 🧪 测试策略

### 测试类型
1. **单元测试**: 组件和函数测试
2. **集成测试**: API和数据流测试
3. **E2E测试**: 完整用户流程测试
4. **多租户测试**: 数据隔离测试
5. **性能测试**: 负载和压力测试
6. **安全测试**: 漏洞扫描和渗透测试

### 测试工具
- Jest: 单元测试框架
- Playwright: E2E测试
- Artillery: 性能测试
- OWASP ZAP: 安全测试

## 🚀 部署方案

### 生产环境部署
- **前端**: Vercel自动部署
- **后端**: Railway容器部署
- **数据库**: Supabase托管数据库
- **文件存储**: AWS S3
- **缓存**: Redis Cloud
- **监控**: Sentry + LogRocket

### 扩展策略
- 水平扩展和负载均衡
- 数据库读写分离
- CDN加速
- 微服务架构演进

## 🔄 文档交叉引用

### 相关文档
- 📄 **[01-corporate-landing.md](./01-corporate-landing.md)**: 企业官网项目实战
- 📄 **[02-ecommerce-store.md](./02-ecommerce-store.md)**: 电商应用项目实战
- 📄 **[03-dashboard-analytics.md](./03-dashboard-analytics.md)**: 数据仪表板项目实战

### 参考章节
- 📖 **[Framework Deep Dive - Next.js](../frameworks/01-nextjs-16-complete.md)**: Next.js核心特性深度学习
- 📖 **[Database - Multi-tenant Architecture](../frameworks/03-full-stack-patterns.md)**: 多租户架构最佳实践
- 📖 **[Authentication - NextAuth](../reference/framework-patterns/07-authentication-flows.md)**: NextAuth.js高级配置

## 📝 总结

### 核心要点回顾
1. **多租户架构**: 掌握企业级SaaS平台的核心架构模式
2. **订阅计费**: 实现完整的商业模式和计费系统
3. **权限管理**: 构建灵活的权限控制和访问管理系统
4. **品牌定制**: 开发可定制的白标解决方案
5. **性能优化**: SaaS应用的性能监控和优化策略

### 学习成果检查
- [ ] 能够设计和实现多租户SaaS架构
- [ ] 掌握订阅计费和商业模式实现
- [ ] 构建完整的权限管理和访问控制系统
- [ ] 开发可定制的品牌和白标解决方案
- [ ] 部署和运维生产级SaaS应用

## 🤝 贡献与反馈

### 贡献指南
欢迎对本项目实战文档提出改进建议：
- 🐛 **Bug报告**: 发现文档错误或不准确之处
- 💡 **功能建议**: 提出新的SaaS功能或商业模式
- 📝 **内容贡献**: 分享您的SaaS开发经验

### 反馈渠道
- GitHub Issues: [项目Issues页面]
- Email: dev-quest@example.com
- 社区讨论: [开发者社区链接]

## 🔗 外部资源

### 官方文档
- [Next.js 16 Documentation](https://nextjs.org/docs)
- [Stripe Billing Documentation](https://stripe.com/docs/billing)
- [Prisma Multi-tenant Guide](https://www.prisma.io/docs/guides/performance-and-optimization/multi-tenant-architecture)
- [NextAuth.js Documentation](https://next-auth.js.org/)

### 学习资源
- [SaaS Architecture Patterns](https://aws.amazon.com/saas/)
- [Multi-tenant SaaS Architecture](https://docs.microsoft.com/en-us/azure/architecture/patterns/multi-tenant-saas)
- [Building SaaS Products](https://www.saasclub.io/)

### 工具和平台
- [Vercel](https://vercel.com/) - 部署平台
- [Stripe](https://stripe.com/) - 支付和计费
- [Supabase](https://supabase.com/) - 后端即服务
- [Sentry](https://sentry.io/) - 错误监控

---

**文档状态**: ✅ 已完成 | 🚧 进行中 | 📋 计划中
**最后更新**: 2026年9月
**版本**: v1.0.0