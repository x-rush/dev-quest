# Next.js 15 全栈开发模式完整指南

> **文档简介**: Next.js 15 企业级全栈开发实践指南，涵盖API设计、数据库集成、认证授权、实时功能、微服务等现代全栈开发技术

> **目标读者**: 具备Next.js和后端基础的中高级开发者，需要掌握现代全栈开发架构的全栈工程师

> **前置知识**: Next.js 15、React 19、TypeScript 5、数据库基础、API设计、认证授权概念

> **预计时长**: 12-16小时

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `frameworks` |
| **难度** | ⭐⭐⭐⭐⭐ (5/5星) |
| **标签** | `#full-stack` `#api-design` `#database` `#authentication` `#microservices` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标

### 🏗️ 全栈架构设计
- 掌握Next.js 15全栈应用的核心架构模式
- 学会RESTful API和GraphQL的设计与实现
- 理解数据库集成和数据建模最佳实践
- 掌握现代认证授权和安全架构

### 🚀 企业级开发能力
- 构建可扩展的微服务和分布式系统
- 实现实时功能和事件驱动架构
- 掌握DevOps和CI/CD流水线
- 学会监控、日志和运维最佳实践

## 📖 概述

Next.js 15为全栈开发提供了强大的基础设施，通过API Routes、Server Components、Middleware等特性，支持构建功能完整的企业级Web应用。本指南将深入探讨Next.js 15的全栈开发模式和最佳实践。

## 🏗️ 全栈架构深度解析

### 架构设计原则

```typescript
// src/types/fullstack-architecture.ts
export interface FullStackArchitecture {
  // 分层架构
  layers: {
    presentation: '表现层 - UI组件和页面'
    business: '业务层 - 业务逻辑和规则'
    data: '数据层 - 数据访问和持久化'
    infrastructure: '基础设施层 - 服务和工具'
  }

  // 服务架构
  services: {
    api: 'API服务 - RESTful和GraphQL接口'
    auth: '认证服务 - 用户认证和授权'
    data: '数据服务 - 数据处理和缓存'
    notification: '通知服务 - 消息和推送'
    file: '文件服务 - 文件上传和管理'
  }

  // 数据架构
  data: {
    relational: '关系型数据库 - PostgreSQL/MySQL'
    nosql: 'NoSQL数据库 - MongoDB/Redis'
    cache: '缓存层 - Redis/Memcached'
    search: '搜索引擎 - Elasticsearch'
    analytics: '分析数据库 - ClickHouse'
  }

  // 安全架构
  security: {
    authentication: '身份认证 - JWT/OAuth2'
    authorization: '权限控制 - RBAC/ABAC'
    encryption: '数据加密 - 静态/传输加密'
    validation: '数据验证 - 输入/输出验证'
    monitoring: '安全监控 - 威胁检测'
  }
}
```

### 项目架构示例

```
fullstack-app/
├── src/
│   ├── app/                          # App Router
│   │   ├── (auth)/                  # 认证页面
│   │   ├── (dashboard)/             # 仪表板
│   │   ├── api/                     # API路由
│   │   │   ├── auth/               # 认证API
│   │   │   ├── users/              # 用户API
│   │   │   ├── posts/              # 文章API
│   │   │   ├── files/              # 文件API
│   │   │   ├── notifications/      # 通知API
│   │   │   └── webhooks/           # Webhook API
│   │   ├── dashboard/               # 仪表板页面
│   │   └── admin/                   # 管理员页面
│   ├── components/                  # 组件
│   │   ├── ui/                     # 基础UI组件
│   │   ├── layout/                 # 布局组件
│   │   ├── forms/                  # 表单组件
│   │   └── charts/                 # 图表组件
│   ├── lib/                        # 工具库
│   │   ├── auth.ts                 # 认证工具
│   │   ├── db.ts                   # 数据库配置
│   │   ├── email.ts                # 邮件服务
│   │   ├── storage.ts              # 文件存储
│   │   └── utils.ts                # 通用工具
│   ├── services/                   # 业务服务
│   │   ├── auth.service.ts         # 认证服务
│   │   ├── user.service.ts         # 用户服务
│   │   ├── post.service.ts         # 文章服务
│   │   └── notification.service.ts # 通知服务
│   ├── middleware.ts                # 中间件
│   └── types/                      # 类型定义
├── prisma/                         # 数据库配置
├── docker/                         # Docker配置
├── scripts/                        # 脚本文件
└── docs/                          # 文档
```

## 🔐 认证授权系统

### NextAuth.js 企业级配置

```typescript
// src/lib/auth/config.ts
import { NextAuthOptions } from 'next-auth'
import { PrismaAdapter } from '@next-auth/prisma-adapter'
import CredentialsProvider from 'next-auth/providers/credentials'
import GoogleProvider from 'next-auth/providers/google'
import GitHubProvider from 'next-auth/providers/github'
import bcrypt from 'bcryptjs'
import { prisma } from '@/lib/db'

// 认证选项配置
export const authOptions: NextAuthOptions = {
  // 数据库适配器
  adapter: PrismaAdapter(prisma),

  // 会话配置
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30天
    updateAge: 24 * 60 * 60 // 24小时更新一次
  },

  // JWT配置
  jwt: {
    secret: process.env.NEXTAUTH_SECRET!,
    encryption: true,
    maxAge: 30 * 24 * 60 * 60
  },

  // 认证提供者
  providers: [
    // 凭证认证
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
          where: { email: credentials.email },
          include: {
            roles: true,
            permissions: true
          }
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

        // 检查账户是否被锁定
        if (user.lockedUntil && user.lockedUntil > new Date()) {
          throw new Error('账户已被锁定，请稍后再试')
        }

        // 更新最后登录时间
        await prisma.user.update({
          where: { id: user.id },
          data: {
            lastLoginAt: new Date(),
            loginAttempts: 0,
            lockedUntil: null
          }
        })

        return {
          id: user.id,
          email: user.email,
          name: user.displayName,
          role: user.roles.map(r => r.name),
          permissions: user.permissions.map(p => p.name)
        }
      }
    }),

    // Google OAuth
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      allowDangerousEmailAccountLinking: true
    }),

    // GitHub OAuth
    GitHubProvider({
      clientId: process.env.GITHUB_ID!,
      clientSecret: process.env.GITHUB_SECRET!,
      allowDangerousEmailAccountLinking: true
    })
  ],

  // 回调函数
  callbacks: {
    // JWT回调
    async jwt({ token, user, trigger, session }) {
      // 用户登录时添加额外信息
      if (user) {
        token.id = user.id
        token.role = user.role
        token.permissions = user.permissions
        token.emailVerified = user.emailVerified
      }

      // 会话更新时更新token
      if (trigger === 'update' && session) {
        token.id = session.user.id
        token.role = session.user.role
        token.permissions = session.user.permissions
      }

      return token
    },

    // 会话回调
    async session({ session, token }) {
      if (token) {
        session.user.id = token.id
        session.user.role = token.role
        session.user.permissions = token.permissions
        session.user.emailVerified = token.emailVerified
      }
      return session
    },

    // 重定向回调
    async redirect({ url, baseUrl }) {
      // 允许相对URL和同源URL
      if (url.startsWith('/')) return `${baseUrl}${url}`
      if (new URL(url).origin === baseUrl) return url
      return baseUrl
    },

    // 登录回调
    async signIn({ user, account, profile }) {
      if (account?.provider === 'credentials') {
        return true // 允许凭据登录
      }

      // OAuth登录时的额外验证
      if (account?.provider === 'google') {
        // 验证Google账户
        const allowedDomains = ['example.com', 'company.com']
        const domain = profile?.email?.split('@')[1]

        if (domain && !allowedDomains.includes(domain)) {
          throw new Error('不允许的邮箱域名')
        }
      }

      return true
    }
  },

  // 页面配置
  pages: {
    signIn: '/auth/login',
    signUp: '/auth/register',
    error: '/auth/error',
    verifyRequest: '/auth/verify-request',
    newUser: '/auth/welcome'
  },

  // 事件回调
  events: {
    // 创建用户时
    async createUser({ user }) {
      console.log('New user created:', user)
      // 发送欢迎邮件
      await sendWelcomeEmail(user.email || '')
    },

    // 登录时
    async signIn({ user, account, isNewUser }) {
      console.log('User signed in:', { user, account, isNewUser })

      if (isNewUser) {
        // 新用户引导
        await trackNewUserOnboarding(user.id)
      }
    },

    // 登出时
    async signOut({ session }) {
      console.log('User signed out:', session)
      // 清理用户相关缓存
      await clearUserCache(session.user.id)
    }
  }
}

// 权限检查函数
export function checkPermission(user: any, permission: string): boolean {
  return user?.permissions?.includes(permission) || user?.role?.includes('admin')
}

// 角色检查函数
export function checkRole(user: any, role: string): boolean {
  return user?.role?.includes(role) || user?.role?.includes('admin')
}

// 辅助函数
async function sendWelcomeEmail(email: string) {
  // 实现邮件发送逻辑
}

async function trackNewUserOnboarding(userId: string) {
  // 实现新用户引导跟踪
}

async function clearUserCache(userId: string) {
  // 实现缓存清理逻辑
}
```

### 高级权限管理

```typescript
// src/lib/auth/permissions.ts
import { NextRequest } from 'next/server'
import { getToken } from 'next-auth/jwt'
import { prisma } from '@/lib/db'

// 权限定义
export const PERMISSIONS = {
  // 用户权限
  USER_READ: 'user:read',
  USER_UPDATE_OWN: 'user:update:own',
  USER_DELETE_OWN: 'user:delete:own',

  // 文章权限
  ARTICLE_READ: 'article:read',
  ARTICLE_CREATE: 'article:create',
  ARTICLE_UPDATE_OWN: 'article:update:own',
  ARTICLE_DELETE_OWN: 'article:delete:own',
  ARTICLE_UPDATE_ANY: 'article:update:any',
  ARTICLE_DELETE_ANY: 'article:delete:any',
  ARTICLE_PUBLISH: 'article:publish',

  // 评论权限
  COMMENT_READ: 'comment:read',
  COMMENT_CREATE: 'comment:create',
  COMMENT_UPDATE_OWN: 'comment:update:own',
  COMMENT_DELETE_OWN: 'comment:delete:own',
  COMMENT_DELETE_ANY: 'comment:delete:any',

  // 管理员权限
  USER_READ_ANY: 'user:read:any',
  USER_UPDATE_ANY: 'user:update:any',
  USER_DELETE_ANY: 'user:delete:any',
  USER_ROLES_MANAGE: 'user:roles:manage',
  SYSTEM_ADMIN: 'system:admin'
} as const

export type Permission = typeof PERMISSIONS[keyof typeof PERMISSIONS]

// 角色权限映射
export const ROLE_PERMISSIONS = {
  guest: [],

  user: [
    PERMISSIONS.USER_READ,
    PERMISSIONS.USER_UPDATE_OWN,
    PERMISSIONS.USER_DELETE_OWN,
    PERMISSIONS.ARTICLE_READ,
    PERMISSIONS.ARTICLE_CREATE,
    PERMISSIONS.ARTICLE_UPDATE_OWN,
    PERMISSIONS.ARTICLE_DELETE_OWN,
    PERMISSIONS.COMMENT_READ,
    PERMISSIONS.COMMENT_CREATE,
    PERMISSIONS.COMMENT_UPDATE_OWN,
    PERMISSIONS.COMMENT_DELETE_OWN
  ],

  moderator: [
    ...ROLE_PERMISSIONS.user,
    PERMISSIONS.COMMENT_DELETE_ANY
  ],

  author: [
    ...ROLE_PERMISSIONS.user,
    PERMISSIONS.ARTICLE_PUBLISH
  ],

  editor: [
    ...ROLE_PERMISSIONS.author,
    PERMISSIONS.ARTICLE_UPDATE_ANY,
    PERMISSIONS.ARTICLE_DELETE_ANY
  ],

  admin: Object.values(PERMISSIONS)
} as const

// 权限检查中间件
export async function requireAuth(
  request: NextRequest,
  requiredPermissions: Permission[] = []
) {
  const token = await getToken({
    req: request,
    secret: process.env.NEXTAUTH_SECRET!
  })

  if (!token) {
    return {
      error: 'Unauthorized',
      status: 401
    }
  }

  // 获取用户权限
  const user = await prisma.user.findUnique({
    where: { id: token.sub },
    include: {
      roles: true,
      permissions: true
    }
  })

  if (!user || !user.isActive) {
    return {
      error: 'User not found or inactive',
      status: 401
    }
  }

  // 检查权限
  const userPermissions = user.permissions.map(p => p.name)
  const userRoles = user.roles.map(r => r.name)

  // 检查管理员权限
  if (userRoles.includes('admin')) {
    return { user }
  }

  // 检查所需权限
  const hasAllPermissions = requiredPermissions.every(permission =>
    userPermissions.includes(permission) ||
    userRoles.some(role =>
      ROLE_PERMISSIONS[role as keyof typeof ROLE_PERMISSIONS]?.includes(permission)
    )
  )

  if (!hasAllPermissions) {
    return {
      error: 'Insufficient permissions',
      status: 403
    }
  }

  return { user }
}

// 权限检查Hook (客户端)
export function usePermissions() {
  const { data: session } = useSession()

  const user = session?.user

  const hasPermission = useCallback((permission: Permission) => {
    if (!user) return false
    return user.permissions?.includes(permission) || user.role?.includes('admin')
  }, [user])

  const hasRole = useCallback((role: string) => {
    if (!user) return false
    return user.role?.includes(role) || user.role?.includes('admin')
  }, [user])

  const hasAnyPermission = useCallback((permissions: Permission[]) => {
    if (!user) return false
    return permissions.some(permission => hasPermission(permission))
  }, [hasPermission])

  const hasAllPermissions = useCallback((permissions: Permission[]) => {
    if (!user) return false
    return permissions.every(permission => hasPermission(permission))
  }, [hasPermission])

  return {
    user,
    hasPermission,
    hasRole,
    hasAnyPermission,
    hasAllPermissions
  }
}

// 权限包装器组件
interface PermissionWrapperProps {
  children: React.ReactNode
  permission?: Permission
  permissions?: Permission[]
  role?: string
  fallback?: React.ReactNode
}

export function PermissionWrapper({
  children,
  permission,
  permissions = [],
  role,
  fallback = null
}: PermissionWrapperProps) {
  const { hasPermission, hasRole } = usePermissions()

  const hasAccess = role
    ? hasRole(role)
    : permission
    ? hasPermission(permission)
    : permissions.length > 0
    ? permissions.some(p => hasPermission(p))
    : true

  if (!hasAccess) {
    return <>{fallback}</>
  }

  return <>{children}</>
}
```

## 📡 API设计与实现

### RESTful API最佳实践

```typescript
// src/app/api/v1/users/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { requireAuth } from '@/lib/auth/permissions'
import { PERMISSIONS } from '@/lib/auth/permissions'
import { updateUserSchema, paginationSchema } from '@/lib/validation'
import { prisma } from '@/lib/db'
import { rateLimit } from '@/lib/rate-limit'
import { auditLog } from '@/lib/audit'

// 输入验证schema
const updateParamsSchema = z.object({
  id: z.string().cuid()
})

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // 参数验证
    const { id } = updateParamsSchema.parse(params)

    // 权限检查
    const auth = await requireAuth(request, [PERMISSIONS.USER_READ])
    if (auth.error) {
      return NextResponse.json(
        { error: auth.error },
        { status: auth.status }
      )
    }

    // 查询用户
    const user = await prisma.user.findUnique({
      where: { id },
      select: {
        id: true,
        email: true,
        username: true,
        displayName: true,
        avatar: true,
        bio: true,
        isActive: true,
        emailVerified: true,
        roles: {
          select: {
            id: true,
            name: true,
            description: true
          }
        },
        permissions: {
          select: {
            id: true,
            name: true,
            description: true
          }
        },
        createdAt: true,
        updatedAt: true,
        lastLoginAt: true
      }
    })

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      )
    }

    // 审计日志
    await auditLog({
      action: 'USER_READ',
      userId: auth.user.id,
      targetId: id,
      metadata: { requestedBy: auth.user.id }
    })

    return NextResponse.json({
      success: true,
      data: user
    })

  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid parameters', details: error.errors },
        { status: 400 }
      )
    }

    console.error('Error fetching user:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // 参数验证
    const { id } = updateParamsSchema.parse(params)
    const body = await request.json()
    const validatedData = updateUserSchema.parse(body)

    // 权限检查 - 用户只能更新自己的信息，管理员可以更新任何人
    const auth = await requireAuth(request, [])
    if (auth.error) {
      return NextResponse.json(
        { error: auth.error },
        { status: auth.status }
      )
    }

    // 检查权限
    const canUpdate =
      auth.user.id === id ||
      auth.user.permissions.includes(PERMISSIONS.USER_UPDATE_ANY) ||
      auth.user.role.includes('admin')

    if (!canUpdate) {
      return NextResponse.json(
        { error: 'Insufficient permissions' },
        { status: 403 }
      )
    }

    // 更新用户
    const updatedUser = await prisma.user.update({
      where: { id },
      data: {
        ...validatedData,
        updatedAt: new Date()
      },
      select: {
        id: true,
        email: true,
        username: true,
        displayName: true,
        avatar: true,
        bio: true,
        updatedAt: true
      }
    })

    // 审计日志
    await auditLog({
      action: 'USER_UPDATE',
      userId: auth.user.id,
      targetId: id,
      metadata: {
        updatedFields: Object.keys(validatedData),
        updatedBy: auth.user.id
      }
    })

    return NextResponse.json({
      success: true,
      data: updatedUser,
      message: 'User updated successfully'
    })

  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid data', details: error.errors },
        { status: 400 }
      )
    }

    console.error('Error updating user:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // 参数验证
    const { id } = updateParamsSchema.parse(params)

    // 权限检查
    const auth = await requireAuth(request, [PERMISSIONS.USER_DELETE_ANY])
    if (auth.error) {
      return NextResponse.json(
        { error: auth.error },
        { status: auth.status }
      )
    }

    // 软删除用户
    const deletedUser = await prisma.user.update({
      where: { id },
      data: {
        isActive: false,
        deletedAt: new Date()
      },
      select: {
        id: true,
        email: true,
        displayName: true
      }
    })

    // 审计日志
    await auditLog({
      action: 'USER_DELETE',
      userId: auth.user.id,
      targetId: id,
      metadata: { deletedBy: auth.user.id }
    })

    return NextResponse.json({
      success: true,
      message: 'User deleted successfully'
    })

  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid parameters', details: error.errors },
        { status: 400 }
      )
    }

    console.error('Error deleting user:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

### API版本控制和文档

```typescript
// src/app/api/[...version]/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'

// 版本配置
const API_VERSIONS = {
  v1: {
    deprecationDate: null,
    sunsetDate: null,
    supported: true
  },
  v2: {
    deprecationDate: new Date('2025-12-31'),
    sunsetDate: new Date('2026-06-30'),
    supported: true
  }
} as const

const versionSchema = z.enum(['v1', 'v2'])

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const version = versionSchema.parse(searchParams.get('version') || 'v1')

    // 检查版本支持
    const versionInfo = API_VERSIONS[version]

    if (!versionInfo.supported) {
      return NextResponse.json({
        error: 'API version not supported',
        message: `Version ${version} is no longer supported`
      }, { status: 410 })
    }

    // 版本弃用警告
    if (versionInfo.deprecationDate) {
      const headers = new Headers({
        'Deprecation': 'true',
        'Sunset': versionInfo.sunsetDate.toISOString(),
        'Link': `<https://api.example.com/docs/v2>; rel="successor-version"`
      })

      return NextResponse.json({
        version,
        status: 'deprecated',
        message: `Version ${version} is deprecated and will be sunset on ${versionInfo.sunsetDate.toISOString()}`
      }, { headers })
    }

    // 返回API信息
    return NextResponse.json({
      version,
      endpoints: {
        users: `/api/${version}/users`,
        posts: `/api/${version}/posts`,
        auth: `/api/${version}/auth`
      },
      documentation: `https://api.example.com/docs/${version}`,
      changelog: `https://api.example.com/changelog/${version}`
    })

  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid version', details: error.errors },
        { status: 400 }
      )
    }

    console.error('API version error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

## 🗄️ 数据库集成和优化

### Prisma 高级配置

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// 用户表
model User {
  id            String    @id @default(cuid())
  email         String    @unique
  username      String    @unique
  displayName   String
  passwordHash  String
  avatar        String?
  bio           String?
  emailVerified Boolean   @default(false)
  isActive      Boolean   @default(true)
  lastLoginAt   DateTime?
  loginAttempts Int       @default(0)
  lockedUntil   DateTime?
  deletedAt     DateTime?

  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  // 关系
  posts         Post[]
  comments      Comment[]
  roles         UserRole[]
  permissions   UserPermission[]
  accounts      Account[]
  sessions      Session[]
  auditLogs     AuditLog[]

  @@map("users")
}

// 角色表
model Role {
  id          String   @id @default(cuid())
  name        String   @unique
  description String?
  isActive    Boolean  @default(true)
  createdAt   DateTime @default(now())

  users       UserRole[]
  permissions RolePermission[]

  @@map("roles")
}

// 权限表
model Permission {
  id          String   @id @default(cuid())
  name        String   @unique
  description String?
  resource    String
  action      String
  isActive    Boolean  @default(true)
  createdAt   DateTime @default(now())

  users       UserPermission[]
  roles       RolePermission[]

  @@map("permissions")
}

// 用户角色关联表
model UserRole {
  id        String   @id @default(cuid())
  userId    String
  roleId    String
  assignedAt DateTime @default(now())
  assignedBy String

  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  role      Role     @relation(fields: [roleId], references: [id], onDelete: Cascade)

  @@unique([userId, roleId])
  @@map("user_roles")
}

// 用户权限关联表
model UserPermission {
  id           String   @id @default(cuid())
  userId       String
  permissionId String
  grantedAt    DateTime @default(now())
  grantedBy    String

  user         User       @relation(fields: [userId], references: [id], onDelete: Cascade)
  permission   Permission @relation(fields: [permissionId], references: [id], onDelete: Cascade)

  @@unique([userId, permissionId])
  @@map("user_permissions")
}

// 角色权限关联表
model RolePermission {
  id           String   @id @default(cuid())
  roleId       String
  permissionId String
  createdAt    DateTime @default(now())

  role         Role       @relation(fields: [roleId], references: [id], onDelete: Cascade)
  permission   Permission @relation(fields: [permissionId], references: [id], onDelete: Cascade)

  @@unique([roleId, permissionId])
  @@map("role_permissions")
}

// 审计日志表
model AuditLog {
  id        String   @id @default(cuid())
  action    String
  userId    String?
  targetId  String?
  metadata  Json?
  ipAddress String?
  userAgent String?
  createdAt DateTime @default(now())

  user      User?    @relation(fields: [userId], references: [id], onDelete: SetNull)

  @@map("audit_logs")
}
```

### 数据库连接池配置

```typescript
// src/lib/db.ts
import { PrismaClient } from '@prisma/client'

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
    errorFormat: 'pretty'
  })

// 连接池配置
const poolConfig = {
  // 连接数配置
  connectionLimit: 20,
  poolTimeout: 10,
  acquireTimeoutMillis: 60000,
  createTimeoutMillis: 30000,
  destroyTimeoutMillis: 5000,
  idleTimeoutMillis: 30000,
  reapIntervalMillis: 1000,
  createRetryIntervalMillis: 200,

  // 预热配置
  eagerEmit: false,
  lazyConnect: false,

  // 健康检查
  healthCheckTimeout: 5000
}

// 数据库健康检查
export async function checkDatabaseHealth() {
  try {
    await prisma.$queryRaw`SELECT 1`
    return { status: 'healthy', timestamp: new Date().toISOString() }
  } catch (error) {
    console.error('Database health check failed:', error)
    return {
      status: 'unhealthy',
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString()
    }
  }
}

// 连接池监控
export function getConnectionPoolStats() {
  // Prisma内部连接池统计需要通过其他方式获取
  return {
    activeConnections: 'Unknown',
    idleConnections: 'Unknown',
    totalConnections: 'Unknown'
  }
}

// 查询优化工具
export class QueryOptimizer {
  // 批量操作优化
  static async batchCreate<T>(
    model: any,
    data: T[],
    batchSize: number = 100
  ): Promise<T[]> {
    const results: T[] = []

    for (let i = 0; i < data.length; i += batchSize) {
      const batch = data.slice(i, i + batchSize)
      const created = await model.createMany({
        data: batch,
        skipDuplicates: true
      })
      results.push(...created)
    }

    return results
  }

  // 智能分页
  static async smartPaginate<T>(
    model: any,
    where: any = {},
    options: {
      page?: number
      limit?: number
      orderBy?: any
      include?: any
    } = {}
  ) {
    const { page = 1, limit = 20, orderBy, include } = options
    const skip = (page - 1) * limit

    // 并行执行查询和计数
    const [items, total] = await Promise.all([
      model.findMany({
        where,
        orderBy,
        include,
        skip,
        take: limit
      }),
      model.count({ where })
    ])

    return {
      items,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit),
        hasNext: page * limit < total,
        hasPrev: page > 1
      }
    }
  }

  // 缓存查询
  static async cachedQuery<T>(
    key: string,
    queryFn: () => Promise<T>,
    ttl: number = 300 // 5分钟
  ): Promise<T> {
    // 检查缓存
    const cached = await this.getCache<T>(key)
    if (cached && !this.isCacheExpired(key, ttl)) {
      return cached
    }

    // 执行查询
    const result = await queryFn()

    // 设置缓存
    await this.setCache(key, result, ttl)

    return result
  }

  // 缓存操作
  private static async getCache<T>(key: string): Promise<T | null> {
    // 实现缓存获取逻辑
    return null
  }

  private static async setCache<T>(key: string, data: T, ttl: number): Promise<void> {
    // 实现缓存设置逻辑
  }

  private static isCacheExpired(key: string, ttl: number): boolean {
    // 实现缓存过期检查
    return true
  }
}

// 数据库迁移工具
export class MigrationManager {
  static async runMigrations() {
    try {
      // 检查迁移状态
      const migrations = await this.getPendingMigrations()

      if (migrations.length === 0) {
        console.log('No pending migrations')
        return
      }

      console.log(`Running ${migrations.length} migrations...`)

      // 执行迁移
      for (const migration of migrations) {
        await this.runMigration(migration)
        console.log(`✓ Migration ${migration.name} completed`)
      }

      console.log('All migrations completed successfully')
    } catch (error) {
      console.error('Migration failed:', error)
      throw error
    }
  }

  private static async getPendingMigrations() {
    // 实现迁移检查逻辑
    return []
  }

  private static async runMigration(migration: any) {
    // 实现单个迁移执行逻辑
  }
}
```

## ✅ 总结

通过本指南，你已经掌握了Next.js 15企业级全栈开发的核心能力：

### 🏗️ 全栈架构设计
- 分层架构设计和服务组织原则
- 认证授权系统的企业级实现
- 权限管理和安全最佳实践
- API版本控制和文档管理

### 🔐 企业级功能实现
- NextAuth.js的高级配置和扩展
- 复杂的权限控制和RBAC系统
- RESTful API的设计和实现
- 数据库优化和连接池管理

### 📊 数据管理和优化
- Prisma ORM的高级配置和优化
- 批量操作和智能分页
- 缓存策略和性能优化
- 数据迁移和版本控制

## 📚 下一步学习

- 深入学习GraphQL和Apollo Server
- 掌握微服务架构和分布式系统
- 学习实时通信和WebSocket
- 探索容器化和Kubernetes部署
- 了解监控、日志和可观测性

## 🔗 相关资源链接

### 官方资源
- [NextAuth.js 官方文档](https://next-auth.js.org/)
- [Prisma ORM 文档](https://www.prisma.io/docs/)
- [Next.js API Routes 文档](https://nextjs.org/docs/api-routes/introduction)
- [Next.js 中间件文档](https://nextjs.org/docs/advanced-features/middleware)

### 技术文章
- [企业级认证架构设计](https://next-auth.js.org/tutorials/enterprise)
- [Prisma 性能优化指南](https://www.prisma.io/docs/guides/performance-optimization)
- [RESTful API 设计最佳实践](https://restfulapi.net/)
- [PostgreSQL 数据库设计](https://www.postgresql.org/docs/)

### 工具和资源
- [Postman API 测试工具](https://www.postman.com/)
- [Prisma Studio](https://www.prisma.io/studio)
- [Database Design 工具](https://dbdiagram.io/)

## 📚 模块内相关文档

### 同模块相关文档
- [Next.js 15 完整指南](./01-nextjs-15-complete.md) - 掌握Next.js 15的API Routes和服务器功能
- [React 19 深度集成](./02-react-19-integration.md) - 学习如何在全栈应用中集成React 19特性
- [性能优化策略](./04-performance-optimization.md) - 深入了解全栈应用的性能优化

### 相关知识模块
- [测试相关模块](../testing/01-unit-testing.md) - API和数据库操作的单元测试
- [测试相关模块](../testing/03-e2e-testing.md) - 全栈应用的端到端测试策略
- [部署相关模块](../deployment/02-docker-containerization.md) - 全栈应用的容器化部署

### 基础前置知识
- [数据库设计基础](../../../01-react-foundation/basics/04-database-design.md) - 数据库设计原理和最佳实践
- [API 设计原则](../../../01-react-foundation/advanced/02-api-design-principles.md) - RESTful API设计理论
- [认证授权基础](../../../01-react-foundation/advanced/05-authentication-authorization.md) - 认证和授权的核心概念

---

## ✨ 总结

### 核心技术要点
1. **分层架构设计**: 表现层、业务层、数据层、基础设施层的清晰分离和组织
2. **认证授权系统**: NextAuth.js的企业级配置和多种认证提供者集成
3. **权限管理**: RBAC(基于角色的访问控制)和细粒度权限控制
4. **API设计**: RESTful API的最佳实践、版本控制和错误处理
5. **数据管理**: Prisma ORM的高级配置、查询优化和数据库连接池管理

### 学习成果自检
- [ ] 理解企业级全栈应用的分层架构设计原则
- [ ] 掌握NextAuth.js的配置和多种认证方式
- [ ] 能够设计和实现复杂的权限管理系统
- [ ] 熟练运用RESTful API的设计原则和最佳实践
- [ ] 能够独立构建一个功能完整的企业级全栈应用

---

## 🤝 贡献与反馈

### 贡献指南
欢迎提交Issue和Pull Request来改进本模块内容！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交变更 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

### 反馈渠道
- **问题反馈**: [GitHub Issues](https://github.com/your-username/dev-quest/issues)
- **内容建议**: [Discussion板块](https://github.com/your-username/dev-quest/discussions)
- **技术交流**: 欢迎提交PR或Issue参与讨论

### 贡献者
- Dev Quest Team - 核心内容开发
- 社区贡献者 - 内容完善和纠错

---

**📜 文档版本**: v1.0.0
**📅 最后更新**: 2025年10月
**🏷️ 标签**: `#full-stack` `#api-design` `#database` `#authentication` `#permissions`
**⭐ 推荐指数**: ⭐⭐⭐⭐⭐

**💡 提示**: 本模块为全栈开发高级模块，建议先掌握Next.js 15基础和数据库基础后再进行学习。

**🎯 学习建议**:
- 建议学习周期: 3-4周
- 理论与实践时间比例: 3:7
- 重点掌握认证授权和API设计
- 结合实际项目进行全栈开发实践