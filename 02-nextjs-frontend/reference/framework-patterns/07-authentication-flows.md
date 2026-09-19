# Next.js 认证流程：从会话到可审计的安全边界

> **文档简介**: 以 Next.js 与认证库为入口，说明凭据登录、OAuth、会话、授权和 MFA 如何划分责任。示例用于讲清数据流；把它接入生产前，必须按本文的验收项补齐密钥、存储、限流、审计和事件响应。

> **目标读者**: 具备Next.js基础的中高级开发者，需要构建企业级认证系统的架构师和工程师

> **前置知识**: Next.js 16基础、React 19、TypeScript 7、数据库基础、RESTful API设计

> **预计时长**: 8-12小时

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `framework-patterns` |
| **难度** | ⭐⭐⭐ (精通)|
| **标签** | `#authentication` `#nextauth` `#oauth` `#jwt` `#mfa` `#security` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 🎯 学习目标

### 🔐 认证架构
- 区分框架/认证库提供的会话编排，与应用必须自行负责的用户、角色和安全策略
- 为选择的会话方案写出令牌签发、轮换、撤销和失效规则；不要默认需要或已经有“黑名单”
- 接入一个 OAuth 提供商，并验证回调 URI、state/PKCE（适用时）和账户关联策略
- 实现基于角色的访问控制（RBAC），再决定是否真的需要细粒度权限
- 在风险和产品需求支持时实现 MFA，并验证 TOTP 的时钟窗口、恢复流程与重放处理
- 为会话与可信设备定义最小数据、保留期限和撤销入口；设备指纹不是默认安全能力

### 🚀 高级认证能力
- 为高风险入口增加可解释的限流、失败审计和人工处置规则；“威胁检测”不是复制一段中间件即可获得
- 仅在组织边界、身份源和登出语义已确定时设计 SSO 或跨端会话
- 针对 CSRF、XSS、重放等具体攻击面，说明前置条件、缓解措施和测试方法
- 为 API 选择按账号、IP、设备或租户的限流维度，并评估误伤与绕过成本
- 记录必要的安全事件，并定义访问控制、保留期和告警责任人
- 明确并发登录、会话撤销和恢复账号时的冲突规则

### 🏗️ 企业级最佳实践
认证流程不仅是登录按钮，还包括注册验证、凭据恢复、会话失效和撤销。每条路径都可能改变账号控制权，因此令牌要有使用范围与时限，错误反馈避免泄漏不必要的账号信息。

密码策略、隐私处理和多租户隔离依据实际威胁、产品范围与适用要求设计，不能用“定期过期”“支持多云”代替论证。先验证用户 A 无法访问用户 B 的资源、恢复链接不能重复使用、退出后会话按设计失效，再扩展高级能力。

## 📖 概述

### 🚀 Next.js 16 认证革命

Next.js 负责 Web 应用的路由与渲染，认证库负责部分提供商和会话流程；二者都不替应用决定谁可以访问哪条记录、泄露后怎样撤销、何时通知用户。下面的技术组合可以帮助你搭起认证流程，但不能单独证明系统安全、可扩展或合规。版本号和提供商能力应以项目锁定的依赖及其官方文档为准。

### 🏗️ 企业级认证架构

现代企业级认证架构需要超越简单的登录功能：

```mermaid
graph TB
    A[企业认证架构] --> B[认证服务层]
    A --> C[安全策略层]
    A --> D[用户体验层]
    A --> E[监控审计层]

    B --> B1[身份验证]
    B --> B2[授权管理]
    B --> B3[会话管理]
    B --> B4[多因子认证]

    C --> C1[威胁检测]
    C --> C2[速率限制]
    C --> C3[IP白名单/黑名单]
    C --> C4[异常行为监控]

    D --> D1[OAuth集成]
    D --> D2[SSO登录]
    D --> D3[自助服务]
    D --> D4[多端适配]

    E --> E1[行为审计]
    E --> E2[安全事件]
    E --> E3[合规报告]
    E --> E4[实时监控]
```

### 💡 为什么选择 Next.js 16 + NextAuth.js v5

#### 传统认证方案 vs 现代化方案

| 特性 | 传统认证 | NextAuth.js v5 + Next.js 16 |
|------|------------|---------------------------|
| **路由与回调** | 自行编排 | 可用框架路由和认证库的适配器减少样板代码 |
| **会话安全** | 取决于自行实现 | 仍取决于密钥、Cookie、过期/撤销策略和部署配置 |
| **扩展性** | 取决于架构 | 取决于会话存储、数据库、限流和负载测试，不能由库保证 |
| **OAuth 支持** | 自行接入协议 | 认证库可能提供适配器；提供商范围和配置以实际版本为准 |
| **类型检查** | 可选 | TypeScript 能检查代码接口，不能证明授权逻辑正确 |
| **监控与审计** | 自行设计 | 仍需接入日志、指标、追踪和审计存储 |
| **合规** | 依据适用要求设计 | 没有框架可以自动取得 GDPR、CCPA 或其他合规结论 |

#### 核心认证优势

**🔒 需要自行交付的安全保障**
- 明确令牌撤销或短会话策略，并测试退出、改密和账号恢复后的会话状态
- 谨慎评估设备识别的隐私影响和误判成本；不把它当作唯一认证因子
- 为异常登录定义可观测信号、阈值、处置人和误报处理
- 记录最少必要的审计事件，并保护其完整性和访问权限
- 演练告警、撤销与用户通知流程，而不是只配置监控工具

**🚀 框架能减少的重复工作**
- 用约定的路由和回调承载认证流程，但仍要配置密钥、域名、提供商和数据库
- 用 TypeScript 描述会话和用户字段，并在授权点做运行时检查
- 在客户端读取会话状态；更新与跨端同步的时机由应用定义
- 把通用 Cookie、回调和适配器接入集中管理，安全策略仍要逐条验证

**🎨 需要验证的用户体验**
- OAuth 取消、提供商拒绝、账户已关联和回调失效都有可理解且不泄密的反馈
- 会话过期、改密和主动退出后的跳转符合产品规则
- MFA 的丢失设备与恢复路径经过人工风险评审
- 各端使用同一套身份状态定义，但不假定它们天然共享会话

## 🛠️ 企业级 NextAuth.js 配置

### 1. 核心安装和配置

#### package.json 依赖管理

```json
{
  "name": "enterprise-auth-app",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint .",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "next-auth": "^5.0.0-beta.4",
    "@prisma/client": "^5.10.0",
    "@auth/prisma-adapter": "^2.0.0",
    "bcrypt": "^5.1.1",
    "zod": "^3.23.8",
    "speakeasy": "^2.0.0",
    "uuid": "^9.0.1",
    "jose": "^5.4.0"
  },
  "devDependencies": {
    "@types/node": "^20.12.7",
    "@types/react": "^18.2.74",
    "@types/react-dom": "^18.2.22",
    "@types/bcrypt": "^5.0.2",
    "@types/uuid": "^9.0.7",
    "@types/speakeasy": "^2.0.9",
    "typescript": "^5.4.5",
    "eslint": "^8.57.0",
    "eslint-config-next": "^15.0.0",
    "prisma": "^5.10.0",
    "tailwindcss": "^4.0.0",
    "autoprefixer": "^10.4.17",
    "postcss": "^8.4.38"
  }
}
```

#### lib/auth.ts - 认证配置核心

```typescript
import NextAuth from "next-auth"
import type { NextAuthConfig } from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"
import GoogleProvider from "next-auth/providers/google"
import GitHubProvider from "next-auth/providers/github"
import MicrosoftProvider from "next-auth/providers/microsoft"
import AppleProvider from "next-auth/providers/apple"
import { PrismaAdapter } from "@auth/prisma-adapter"
import { prisma } from "@/lib/prisma"
import bcrypt from "bcrypt"
import { z } from "zod"
import { validatePasswordStrength } from "@/lib/security"
import { detectThreat, logSecurityEvent } from "@/lib/security"
import { authenticateWithTOTP } from "@/lib/mfa"

export const authConfig: NextAuthConfig = {
  // Prisma适配器支持数据库持久化
  adapter: PrismaAdapter(prisma),

  // 会话配置
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30天
    updateAge: 24 * 60 * 60, // 24小时更新一次
  },

  // JWT配置
  jwt: {
    secret: process.env.NEXTAUTH_JWT_SECRET!,
    encryption: true,
    maxAge: 60 * 60 * 24 * 30, // 30天
    signingKey: process.env.NEXTAUTH_JWT_SIGNING_KEY!,
    encryptionKey: process.env.NEXTAUTH_JWT_ENCRYPTION_KEY!,
  },

  // 页面配置
  pages: {
    signIn: "/auth/signin",
    signOut: "/auth/signout",
    error: "/auth/error",
    verifyRequest: "/auth/verify-request",
    newUser: "/auth/welcome",
  },

  // 回调配置
  callbacks: {
    // JWT回调 - 在JWT创建时执行
    async jwt({ token, user, account, profile, isNewUser }) {
      // 首次登录，添加额外信息
      if (isNewUser && user) {
        logSecurityEvent({
          type: "USER_REGISTERED",
          userId: user.id,
          email: user.email!,
          provider: account?.provider || "credentials",
          timestamp: new Date().toISOString()
        })
      }

      // 添加用户权限和角色
      if (user) {
        token.role = user.role
        token.permissions = user.permissions
        token.mfaEnabled = user.mfaEnabled
        token.emailVerified = user.emailVerified
      }

      // 添加账户信息
      if (account) {
        token.provider = account.provider
        token.providerAccountId = account.providerAccountId
      }

      return token
    },

    // 会话回调 - 在每次会话检查时执行
    async session({ session, token, user }) {
      // 添加用户信息到会话
      session.user.id = token.sub!
      session.user.role = token.role as string
      session.user.permissions = token.permissions as string[]
      session.user.mfaEnabled = token.mfaEnabled as boolean
      session.user.emailVerified = token.emailVerified as boolean
      session.user.provider = token.provider as string

      return session
    },

    // 重定向回调
    async redirect({ url, baseUrl }) {
      // 允许相对URL
      if (url.startsWith("/")) return `${baseUrl}${url}`
      // 允许同一域名下的URL
      else if (new URL(url).origin === baseUrl) return url
      return baseUrl
    },

    // 入场回调
    async signIn({ user, account, profile, email, credentials }) {
      // 威胁检测（signIn 回调无 request 参数，IP/UA 采集移至 middleware 层）
      const threatResult = await detectThreat({
        email: email!
      })

      if (threatResult.blocked) {
        logSecurityEvent({
          type: "SIGN_IN_BLOCKED",
          reason: threatResult.reason,
          email: email!,
          timestamp: new Date().toISOString()
        })
        return false
      }

      // 邮箱验证检查
      if (user && !user.emailVerified && account?.provider !== "credentials") {
        return "/auth/verify-email"
      }

      // MFA强制检查
      if (user && user.mfaEnabled && account?.provider === "credentials") {
        return "/auth/mfa"
      }

      return true
    },

    // 授权回调
    async authorized({ request, auth }) {
      const pathname = request.nextUrl.pathname

      // 公共页面无需认证
      const publicPaths = [
        "/", "/home", "/about", "/pricing",
        "/blog", "/auth/signin", "/auth/signup"
      ]

      if (publicPaths.includes(pathname)) return true

      // 需要认证的页面
      return !!auth
    }
  },

  // 事件配置
  events: {
    // 登录成功事件
    async signIn(message) {
      logSecurityEvent({
        type: "SIGN_IN_SUCCESS",
        userId: message.user?.id,
        email: message.user?.email!,
        provider: message.account?.provider || "credentials",
        timestamp: new Date().toISOString()
      })
    },

    // 登出事件
    async signOut(message) {
      logSecurityEvent({
        type: "SIGN_OUT",
        userId: message.session?.user?.id,
        timestamp: new Date().toISOString()
      })
    },

    // 会话创建事件
    async session(session) {
      logSecurityEvent({
        type: "SESSION_CREATED",
        userId: session.user?.id,
        timestamp: new Date().toISOString()
      })
    },

    // 错误事件
    async error(error) {
      logSecurityEvent({
        type: "AUTH_ERROR",
        error: error.name,
        message: error.message,
        timestamp: new Date().toISOString()
      })
    }
  },

  // 提供商配置
  providers: [
    // 凭证提供商（用户名/密码）
    CredentialsProvider({
      id: "credentials",
      name: "邮箱密码登录",
      credentials: {
        email: {
          label: "邮箱地址",
          type: "email",
          placeholder: "your@email.com"
        },
        password: {
          label: "密码",
          type: "password",
          placeholder: "输入您的密码"
        },
        totpCode: {
          label: "双因子验证码（如果启用）",
          type: "text",
          placeholder: "6位数验证码",
          required: false
        }
      },
      async authorize(credentials, req) {
        const { email, password, totpCode } = credentials

        if (!email || !password) {
          throw new Error("邮箱和密码不能为空")
        }

        // 速率限制检查
        const rateLimitResult = await rateLimit('login_attempts', {
          windowMs: 15 * 60 * 1000, // 15分钟
          max: 5,
          identifier: email
        })

        if (!rateLimitResult.success) {
          logSecurityEvent({
            type: "RATE_LIMIT_EXCEEDED",
            reason: "登录尝试过多",
            email,
            timestamp: new Date().toISOString()
          })
          throw new Error("登录尝试次数过多，请15分钟后再试")
        }

        try {
          // 获取用户信息
          const user = await prisma.user.findUnique({
            where: { email: email.toLowerCase() },
            include: {
              securitySettings: true,
              loginAttempts: {
                orderBy: { createdAt: 'desc' },
                take: 5
              }
            }
          })

          // 用户不存在
          if (!user) {
            await logFailedAttempt(email, "USER_NOT_FOUND", req)
            throw new Error("邮箱或密码错误")
          }

          // 检查账户状态
          if (!user.isActive) {
            await logFailedAttempt(user.id, "ACCOUNT_DISABLED", req)
            throw new Error("账户已被禁用，请联系客服")
          }

          if (user.lockedUntil && user.lockedUntil > new Date()) {
            await logFailedAttempt(user.id, "ACCOUNT_LOCKED", req)
            throw new Error("账户已临时锁定，请稍后再试")
          }

          // 验证密码
          const isPasswordValid = await bcrypt.compare(password, user.password)
          if (!isPasswordValid) {
            await logFailedAttempt(user.id, "INVALID_PASSWORD", req)
            await checkAccountLockout(user)
            throw new Error("邮箱或密码错误")
          }

          // MFA验证
          if (user.mfaEnabled) {
            if (!totpCode) {
              // 需要MFA但未提供验证码
              return null // 返回null会触发MFA流程
            }

            const isTOTPValid = await authenticateWithTOTP(user, totpCode)
            if (!isTOTPValid) {
              await logFailedAttempt(user.id, "INVALID_MFA_CODE", req)
              throw new Error("双因子验证码错误")
            }
          }

          // 验证成功，清除失败记录
          await prisma.loginAttempt.deleteMany({
            where: { userId: user.id }
          })

          // 更新登录信息
          await prisma.user.update({
            where: { id: user.id },
            data: {
              lastLoginAt: new Date(),
              lastLoginIp: req.ip || "unknown",
              lastLoginUserAgent: req.headers.get("user-agent") || "unknown",
              loginCount: { increment: 1 }
            }
          })

          // 记录安全事件
          await logSecurityEvent({
            type: "SIGN_IN_SUCCESS",
            userId: user.id,
            email: user.email,
            provider: "credentials",
            timestamp: new Date().toISOString()
          })

          return {
            id: user.id,
            email: user.email,
            name: user.name,
            role: user.role,
            permissions: user.permissions,
            mfaEnabled: user.mfaEnabled,
            emailVerified: user.emailVerified,
            image: user.image
          }

        } catch (error) {
          console.error("认证错误:", error)
          throw error
        }
      }
    }),

    // Google OAuth
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      authorization: {
        params: {
          prompt: "consent",
          access_type: "offline",
          response_type: "code",
          scope: "openid email profile https://www.googleapis.com/auth/calendar.readonly"
        }
      },
      profile(profile) {
        return {
          id: profile.sub,
          name: profile.name,
          email: profile.email,
          image: profile.picture,
          emailVerified: profile.email_verified
        }
      }
    }),

    // GitHub OAuth
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
      authorization: {
        params: {
          scope: "read:user user:email"
        }
      },
      profile(profile) {
        return {
          id: profile.id.toString(),
          name: profile.name || profile.login,
          email: profile.email,
          image: profile.avatar_url,
          emailVerified: !!profile.email
        }
      }
    }),

    // Microsoft OAuth
    MicrosoftProvider({
      clientId: process.env.MICROSOFT_CLIENT_ID!,
      clientSecret: process.env.MICROSOFT_CLIENT_SECRET!,
      authorization: {
        params: {
          scope: "openid profile email User.Read"
        }
      },
      profile(profile) {
        return {
          id: profile.sub,
          name: profile.displayName,
          email: profile.mail,
          image: profile.photos?.[0]?.value,
          emailVerified: !!profile.mail
        }
      }
    }),

    // Apple OAuth
    AppleProvider({
      clientId: process.env.APPLE_CLIENT_ID!,
      clientSecret: {
        appleId: process.env.APPLE_CLIENT_ID!,
        teamId: process.env.APPLE_TEAM_ID!,
        privateKey: process.env.APPLE_PRIVATE_KEY!,
        keyId: process.env.APPLE_KEY_ID!,
      },
      profile(profile) {
        return {
          id: profile.sub,
          name: profile.name?.givenName && profile.name.familyName
            ? `${profile.name.givenName} ${profile.name.familyName}`
            : profile.email,
          email: profile.email,
          emailVerified: profile.email_verified
        }
      }
    }),
  ],

  // 调试配置（开发环境）
  debug: process.env.NODE_ENV === "development"
}

// 辅助函数：记录失败尝试
async function logFailedAttempt(userId: string, reason: string, req: any) {
  await prisma.loginAttempt.create({
    data: {
      userId,
      success: false,
      reason,
      ip: req.ip || "unknown",
      userAgent: req.headers.get("user-agent") || "unknown"
    }
  })

  logSecurityEvent({
    type: "SIGN_IN_FAILURE",
    userId,
    reason,
    timestamp: new Date().toISOString()
  })
}

// 辅助函数：检查账户锁定
async function checkAccountLockout(user: any) {
  const recentFailures = await prisma.loginAttempt.count({
    where: {
      userId: user.id,
      success: false,
      createdAt: {
        gte: new Date(Date.now() - 15 * 60 * 1000) // 最近15分钟
      }
    }
  })

  // 如果最近失败次数过多，锁定账户
  if (recentFailures >= 5) {
    const lockedUntil = new Date(Date.now() + 30 * 60 * 1000) // 锁定30分钟
    await prisma.user.update({
      where: { id: user.id },
      data: { lockedUntil }
    })

    logSecurityEvent({
      type: "ACCOUNT_LOCKED",
      userId: user.id,
      reason: `连续失败次数: ${recentFailures}`,
      lockedUntil: lockedUntil.toISOString(),
      timestamp: new Date().toISOString()
    })
  }
}

// 辅助函数：速率限制
async function rateLimit(key: string, options: { windowMs: number; max: number; identifier: string }) {
  const now = Date.now()
  const windowStart = now - options.windowMs

  // 检查时间窗口内的请求数量
  const requestCount = await prisma.rateLimit.count({
    where: {
      key,
      identifier: options.identifier,
      timestamp: { gte: new Date(windowStart) }
    }
  })

  if (requestCount >= options.max) {
    return { success: false, message: "请求频率过高" }
  }

  // 记录本次请求
  await prisma.rateLimit.create({
    data: {
      key,
      identifier: options.identifier,
      timestamp: new Date(now)
    }
  })

  // 清理过期的记录
  await prisma.rateLimit.deleteMany({
    where: {
      key,
      identifier: options.identifier,
      timestamp: { lt: new Date(windowStart) }
    }
  })

  return { success: true }
}

// NextAuth v5：实例化并导出路由处理器与会话工具
export const { handlers, auth, signIn, signOut } = NextAuth(authConfig)
```

### 2. Prisma 数据模型

#### prisma/schema.prisma

```prisma
// This is your Prisma schema file,
// learn more about it in the docs: https://pris.ly/d/prisma-schema

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "sqlite"
  url      = env("DATABASE_URL")
}

// 用户模型
model User {
  id              String    @id @default(cuid())
  email           String    @unique
  name            String?
  image           String?
  role            UserRole   @default(USER)
  permissions     String    // JSON数组字符串
  password        String
  emailVerified   Boolean   @default(false)
  isActive        Boolean   @default(true)
  lockedUntil     DateTime?
  mfaEnabled      Boolean   @default(false)
  mfaSecret       String?
  backupCodes     String    @default("[]") // JSON数组字符串
  lastLoginAt     DateTime?
  lastLoginIp     String?
  lastLoginUserAgent String?
  loginCount      Int       @default(0)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt

  // 关系
  accounts       Account[]
  sessions       Session[]
  securitySettings SecuritySettings?
  loginAttempts  LoginAttempt[]
  auditLogs      AuditLog[]

  @@map("users")
}

// 账户模型（用于OAuth）
model Account {
  id                String  @id @default(cuid())
  userId            String
  type              String
  provider          String
  providerAccountId  String
  refresh_token     String?
  access_token      String?
  expires_at        Int?
  token_type        String?
  scope             String?
  id_token          String?
  session_state     String?

  // 关系
  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([provider, providerAccountId])
  @@map("accounts")
}

// 会话模型
model Session {
  id           String   @id @default(cuid())
  sessionToken String   @unique
  userId       String
  expires      DateTime
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("sessions")
}

// 验证令牌模型（用于邮箱验证、密码重置等）
model VerificationToken {
  id        String   @id @default(cuid())
  identifier String   // 用户邮箱或手机号
  token     String   // 验证令牌
  expires   DateTime  // 过期时间
  createdAt DateTime  @default(now())

  @@unique([identifier, token])
  @@map("verification_tokens")
}

// 安全设置模型
model SecuritySettings {
  id                   String   @id @default(cuid())
  userId               String   @unique
  enableIPWhitelist    Boolean  @default(false)
  ipWhitelist          String   // JSON数组字符串
  enableGeoBlocking    Boolean  @default(false)
  blockedCountries     String   // JSON数组字符串（ISO国家代码）
  enableSuspiciousLogin Boolean  @default(true)
  suspiciousLoginThreshold Int      @default(3)
  sessionTimeout       Int      @default(30) // 分钟
  passwordMinLength    Int      @default(8)
  requireSpecialChars  Boolean  @default(true)
  requireNumbers       Boolean  @default(true)
  passwordHistorySize Int      @default(5)
  lastPasswordChange   DateTime?
  createdAt            DateTime  @default(now())
  updatedAt            DateTime  @updatedAt

  // 关系
  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("security_settings")
}

// 登录尝试模型
model LoginAttempt {
  id         String   @id @default(cuid())
  userId     String
  success    Boolean
  reason     String?
  ip         String?
  userAgent String?
  timestamp  DateTime  @default(now())

  // 关系
  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("login_attempts")
}

// 速率限制模型
model RateLimit {
  id         String   @id @default(cuid())
  key        String   // 限制类型：login_attempts, api_requests等
  identifier String   // 标识符：IP地址、用户ID等
  timestamp  DateTime  @default(now())

  @@unique([key, identifier, timestamp])
  @@map("rate_limits")
}

// 审计日志模型
model AuditLog {
  id          String    @id @default(cuid())
  userId      String?
  type        AuditEventType
  action      String
  resource    String?
  metadata    String?   // JSON字符串
  ipAddress   String?
  userAgent   String?
  timestamp   DateTime   @default(now())

  // 关系
  user User? @relation(fields: [userId], references: [id], onDelete: SetNull)

  @@map("audit_logs")
}

// JWT黑名单模型
model JWTBlacklist {
  id        String   @id @default(cuid())
  jti       String   @unique // JWT ID
  expires   DateTime  // JWT过期时间
  reason    String   // 加入黑名单的原因
  createdAt DateTime  @default(now())

  @@map("jwt_blacklist")
}

// IP黑名单模型
model BlacklistedIP {
  id        String   @id @default(cuid())
  ip        String   @unique
  reason    String?
  createdAt DateTime  @default(now())

  @@map("blacklisted_ips")
}

// 用户代理黑名单模型
model BlacklistedUserAgent {
  id        String   @id @default(cuid())
  userAgent String   @unique
  reason    String?
  createdAt DateTime  @default(now())

  @@map("blacklisted_user_agents")
}

// 用户权限模型
model Permission {
  id          String   @id @default(cuid())
  name        String   @unique
  description String?
  resource    String
  actions     String   // JSON数组字符串，如 ["read","write","delete","admin"]
  createdAt   DateTime  @default(now())

  @@map("permissions")
}

// 角色枚举
enum UserRole {
  USER          // 普通用户
  MODERATOR     // 版主
  ADMIN         // 管理员
  SUPER_ADMIN    // 超级管理员
}

// 审计事件类型枚举
enum AuditEventType {
  // 认证事件
  SIGN_IN_SUCCESS
  SIGN_IN_FAILURE
  SIGN_OUT
  ACCOUNT_CREATED
  ACCOUNT_UPDATED
  ACCOUNT_DELETED
  PASSWORD_CHANGED
  EMAIL_VERIFIED
  MFA_ENABLED
  MFA_DISABLED

  // 安全事件
  ACCOUNT_LOCKED
  ACCOUNT_UNLOCKED
  PASSWORD_RESET
  RATE_LIMIT_EXCEEDED
  SUSPICIOUS_ACTIVITY
  SECURITY_SETTINGS_CHANGED

  // 数据事件
  DATA_ACCESS
  DATA_MODIFIED
  DATA_DELETED
  EXPORT_GENERATED

  // 系统事件
  LOGIN_ATTEMPT_BLOCKED
  JWT_REVOKED
  PERMISSION_CHANGED
  ROLE_CHANGED
}
```

### 3. 安全工具函数

#### lib/security.ts

```typescript
import { prisma } from "@/lib/prisma"
import { AuditEventType } from "@prisma/client"
import bcrypt from "bcrypt"
import { randomUUID } from "crypto"
import { sign, verify } from "jsonwebtoken"

export interface SecurityEvent {
  type: AuditEventType
  userId?: string
  email?: string
  reason?: string
  ipAddress?: string
  userAgent?: string
  resource?: string
  action?: string
  metadata?: Record<string, any>
  timestamp: string
}

export interface ThreatDetectionResult {
  isThreat: boolean
  blocked: boolean
  risk: "low" | "medium" | "high" | "critical"
  reasons: string[]
  score: number
}

// 威胁检测
export async function detectThreat(data: {
  email: string
  ip: string
  userAgent: string
}): Promise<ThreatDetectionResult> {
  const reasons: string[] = []
  let score = 0

  // 1. 检查IP黑名单
  const isIPBlacklisted = await isIPBlacklisted(data.ip)
  if (isIPBlacklisted) {
    reasons.push("IP地址在黑名单中")
    score += 100
  }

  // 2. 检查用户代理黑名单
  const isUserAgentBlacklisted = await isUserAgentBlacklisted(data.userAgent)
  if (isUserAgentBlacklisted) {
    reasons.push("用户代理在黑名单中")
    score += 80
  }

  // 3. 检查最近失败尝试
  const recentFailures = await getRecentFailures(data.email, data.ip)
  if (recentFailures >= 5) {
    reasons.push(`最近失败尝试过多: ${recentFailures}次`)
    score += 60
  }

  // 4. 检查异常地理位置（如果有GeoIP数据库）
  const geoThreat = await checkGeoIPIrregularities(data.ip)
  if (geoThreat.isThreat) {
    reasons.push(geoThreat.reason)
    score += geoThreat.score
  }

  // 5. 检查时间模式异常
  const timeThreat = checkTimePatternAnomaly()
  if (timeThreat) {
    reasons.push("异常登录时间模式")
    score += 40
  }

  // 6. 检查用户代理异常
  const userAgentThreat = analyzeUserAgent(data.userAgent)
  if (userAgentThreat.isThreat) {
    reasons.push(userAgentThreat.reason)
    score += userAgentThreat.score
  }

  // 计算风险等级
  let risk: "low" | "medium" | "high" | "critical" = "low"
  let blocked = false

  if (score >= 200) {
    risk = "critical"
    blocked = true
  } else if (score >= 150) {
    risk = "high"
    blocked = true
  } else if (score >= 100) {
    risk = "medium"
  } else if (score >= 50) {
    risk = "low"
  }

  return {
    isThreat: score > 0,
    blocked,
    risk,
    reasons,
    score
  }
}

// IP黑名单检查
async function isIPBlacklisted(ip: string): Promise<boolean> {
  const blacklisted = await prisma.blacklistedIP.findUnique({
    where: { ip }
  })
  return !!blacklisted
}

// 用户代理黑名单检查
async function isUserAgentBlacklisted(userAgent: string): Promise<boolean> {
  const blacklisted = await prisma.blacklistedUserAgent.findUnique({
    where: { userAgent: userAgent.substring(0, 255) }
  })
  return !!blacklisted
}

// 获取最近失败尝试
async function getRecentFailures(email: string, ip: string): Promise<number> {
  const recent = new Date(Date.now() - 60 * 60 * 1000) // 最近1小时
  return await prisma.loginAttempt.count({
    where: {
      email,
      ip,
      success: false,
      timestamp: { gte: recent }
    }
  })
}

// 检查地理位置异常
async function checkGeoIPIrregularities(ip: string): Promise<{ isThreat: boolean; reason: string; score: number }> {
  // 这里应该集成GeoIP数据库（如MaxMind GeoIP2）
  // 由于示例限制，返回假数据
  return { isThreat: false, reason: "", score: 0 }
}

// 检查时间模式异常
function checkTimePatternAnomaly(): boolean {
  const hour = new Date().getHours()
  // 凌晨2-5点通常异常
  return hour >= 2 && hour <= 5
}

// 分析用户代理
function analyzeUserAgent(userAgent: string): { isThreat: boolean; reason: string; score: number } {
  const threatPatterns = [
    { pattern: /bot/i, reason: "可疑机器人", score: 30 },
    { pattern: /spider/i, reason: "爬虫程序", score: 40 },
    { pattern: /scanner/i, reason: "安全扫描器", score: 60 },
    { pattern: /curl/i, reason: "命令行工具", score: 20 },
    { pattern: /wget/i, reason: "下载工具", score: 20 }
  ]

  for (const { pattern, reason, score } of threatPatterns) {
    if (pattern.test(userAgent)) {
      return { isThreat: true, reason, score }
    }
  }

  return { isThreat: false, reason: "", score: 0 }
}

// 记录安全事件
export async function logSecurityEvent(event: SecurityEvent) {
  try {
    await prisma.auditLog.create({
      data: {
        userId: event.userId,
        type: event.type,
        action: event.action || "security_event",
        resource: event.resource,
        metadata: event.metadata ? JSON.stringify(event.metadata) : null,
        ipAddress: event.ipAddress,
        userAgent: event.userAgent,
        timestamp: new Date(event.timestamp)
      }
    })

    // 实时告警（对于高危事件）
    if (shouldTriggerAlert(event.type)) {
      await triggerSecurityAlert(event)
    }

  } catch (error) {
    console.error("记录安全事件失败:", error)
  }
}

// 是否触发告警
function shouldTriggerAlert(type: AuditEventType): boolean {
  const criticalEvents = [
    AuditEventType.ACCOUNT_LOCKED,
    AuditEventType.SIGN_IN_FAILURE, // 当频繁时
    AuditEventType.SUSPICIOUS_ACTIVITY,
    AuditEventType.RATE_LIMIT_EXCEEDED,
    AuditEventType.JWT_REVOKED
  ]
  return criticalEvents.includes(type)
}

// 触发安全告警
async function triggerSecurityAlert(event: SecurityEvent) {
  // 这里可以集成Slack、Email、短信等告警渠道
  console.log("🚨 安全告警:", event)

  // 示例：发送邮件告警
  if (process.env.SECURITY_ALERT_EMAIL) {
    await sendEmailAlert({
      to: process.env.SECURITY_ALERT_EMAIL,
      subject: `安全告警: ${event.type}`,
      body: JSON.stringify(event, null, 2)
    })
  }
}

// 发送邮件告警（示例）
async function sendEmailAlert(data: { to: string; subject: string; body: string }) {
  // 这里应该集成真实的邮件发送服务
  // 如：SendGrid、AWS SES、Nodemailer等
  console.log(`发送邮件告警到 ${data.to}: ${data.subject}`)
}

// 密码加密
export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 12) // 使用12轮salt
}

// 密码验证
export async function verifyPassword(password: string, hashedPassword: string): Promise<boolean> {
  return bcrypt.compare(password, hashedPassword)
}

// 生成JWT令牌
export function generateJWT(payload: any, secret: string, expiresIn: string = '1h'): string {
  return sign(payload, secret, { expiresIn })
}

// 验证JWT令牌
export function verifyJWT(token: string, secret: string): any {
  try {
    return verify(token, secret)
  } catch (error) {
    throw new Error("无效的JWT令牌")
  }
}

// 生成安全的随机令牌
export function generateSecureToken(length: number = 32): string {
  return randomUUID().replace(/-/g, '').substring(0, length)
}

// 验证密码强度
export function validatePasswordStrength(password: string): {
  isValid: boolean
  errors: string[]
  strength: "weak" | "medium" | "strong"
} {
  const errors: string[] = []

  if (password.length < 8) {
    errors.push("密码长度至少8位")
  }

  if (!/[a-z]/.test(password)) {
    errors.push("必须包含小写字母")
  }

  if (!/[A-Z]/.test(password)) {
    errors.push("必须包含大写字母")
  }

  if (!/\d/.test(password)) {
    errors.push("必须包含数字")
  }

  if (!/[!@#$%^&*]/.test(password)) {
    errors.push("必须包含特殊字符")
  }

  // 检查常见弱密码
  const commonPasswords = [
    "password", "123456", "qwerty", "abc123",
    "admin", "letmein", "welcome"
  ]

  if (commonPasswords.includes(password.toLowerCase())) {
    errors.push("密码过于常见")
  }

  return {
    isValid: errors.length === 0,
    errors,
    strength: calculatePasswordStrength(password)
  }
}

// 计算密码强度
function calculatePasswordStrength(password: string): "weak" | "medium" | "strong" {
  let score = 0

  // 长度得分
  score += Math.min(password.length * 4, 40)

  // 字符类型得分
  if (/[a-z]/.test(password)) score += 10
  if (/[A-Z]/.test(password)) score += 10
  if (/\d/.test(password)) score += 10
  if (/[!@#$%^&*]/.test(password)) score += 15

  // 复杂度得分
  const uniqueChars = new Set(password).size
  score += Math.min(uniqueChars * 2, 20)

  if (score >= 80) return "strong"
  if (score >= 50) return "medium"
  return "weak"
}
```

### 4. 多因子认证 (MFA)

#### lib/mfa.ts

```typescript
import speakeasy from "speakeasy"
import { prisma } from "@/lib/prisma"
import QRCode from "qrcode"

export interface MFASetupResult {
  secret: string
  qrCodeUrl: string
  backupCodes: string[]
}

export interface MFAVerifyResult {
  success: boolean
  verified: boolean
  backupUsed?: boolean
}

// 设置MFA
export async function setupMFA(userId: string): Promise<MFASetupResult> {
  // 生成新的密钥
  const secret = speakeasy.generateSecret({
    name: `Enterprise App (${userId})`,
    length: 32,
    issuer: "Your Company Name"
  })

  // 生成备用码
  const backupCodes = Array.from({ length: 10 }, () =>
    generateSecureToken(8).toUpperCase()
  )

  // 生成二维码URL
  const qrCodeUrl = await generateQRCode(secret.otpauth_url!)

  // 保存到数据库
  await prisma.user.update({
    where: { id: userId },
    data: {
      mfaSecret: secret.base32,
      backupCodes,
      mfaEnabled: false // 先不启用，等待验证
    }
  })

  // 记录安全事件
  await logSecurityEvent({
    type: AuditEventType.MFA_ENABLED,
    userId,
    action: "mfa_setup_initiated",
    timestamp: new Date().toISOString()
  })

  return {
    secret: secret.base32,
    qrCodeUrl,
    backupCodes
  }
}

// 验证MFA
export async function verifyMFA(
  userId: string,
  token: string,
  backupCode?: string
): Promise<MFAVerifyResult> {
  const user = await prisma.user.findUnique({
    where: { id: userId },
    select: { mfaSecret: true, backupCodes: true }
  })

  if (!user || !user.mfaSecret) {
    return { success: false, verified: false }
  }

  // 验证备用码
  if (backupCode) {
    const isValidBackup = user.backupCodes.includes(backupCode)
    if (isValidBackup) {
      // 移除已使用的备用码
      await prisma.user.update({
        where: { id: userId },
        data: {
          backupCodes: user.backupCodes.filter(code => code !== backupCode)
        }
      })

      await logSecurityEvent({
        type: AuditEventType.SIGN_IN_SUCCESS,
        userId,
        action: "mfa_backup_code_used",
        timestamp: new Date().toISOString()
      })

      return { success: true, verified: true, backupUsed: true }
    }
  }

  // 验证TOTP令牌
  const verified = speakeasy.totp.verify({
    secret: user.mfaSecret,
    encoding: "base32",
    token: token,
    window: 2, // 允许前后2个时间窗口
    step: 30 // 30秒步长
  })

  if (verified) {
    await logSecurityEvent({
      type: AuditEventType.SIGN_IN_SUCCESS,
      userId,
      action: "mfa_totp_verified",
      timestamp: new Date().toISOString()
    })
  }

  return {
    success: true,
    verified: !!verified
  }
}

// 启用MFA
export async function enableMFA(userId: string, token: string): Promise<boolean> {
  const result = await verifyMFA(userId, token)

  if (result.verified) {
    await prisma.user.update({
      where: { id: userId },
      data: { mfaEnabled: true }
    })

    await logSecurityEvent({
      type: AuditEventType.MFA_ENABLED,
      userId,
      action: "mfa_enabled_successfully",
      timestamp: new Date().toISOString()
    })
  }

  return result.verified
}

// 禁用MFA
export async function disableMFA(userId: string, password: string): Promise<boolean> {
  const user = await prisma.user.findUnique({
    where: { id: userId },
    select: { password: true }
  })

  if (!user) {
    return false
  }

  // 验证密码
  const isPasswordValid = await verifyPassword(password, user.password)
  if (!isPasswordValid) {
    return false
  }

  await prisma.user.update({
    where: { id: userId },
    data: {
      mfaEnabled: false,
      mfaSecret: null,
      backupCodes: []
    }
  })

  await logSecurityEvent({
    type: AuditEventType.MFA_DISABLED,
    userId,
    action: "mfa_disabled_by_user",
    timestamp: new Date().toISOString()
  })

  return true
}

// 生成二维码
async function generateQRCode(otpauthUrl: string): Promise<string> {
  try {
    return await QRCode.toDataURL(otpauthUrl, {
      width: 200,
      margin: 2,
      color: {
        dark: '#000000',
        light: '#ffffff'
      }
    })
  } catch (error) {
    console.error("生成二维码失败:", error)
    throw new Error("生成MFA二维码失败")
  }
}

// 验证TOTP令牌（用于登录）
export async function authenticateWithTOTP(user: any, token: string): Promise<boolean> {
  if (!user.mfaSecret || !user.mfaEnabled) {
    return false
  }

  const verified = speakeasy.totp.verify({
    secret: user.mfaSecret,
    encoding: "base32",
    token,
    window: 2,
    step: 30
  })

  return verified
}

// 重新生成备用码
export async function regenerateBackupCodes(userId: string, password: string): Promise<string[]> {
  const user = await prisma.user.findUnique({
    where: { id: userId },
    select: { password: true, backupCodes: true }
  })

  if (!user) {
    throw new Error("用户不存在")
  }

  // 验证密码
  const isPasswordValid = await verifyPassword(password, user.password)
  if (!isPasswordValid) {
    throw new Error("密码错误")
  }

  // 生成新的备用码
  const newBackupCodes = Array.from({ length: 10 }, () =>
    generateSecureToken(8).toUpperCase()
  )

  await prisma.user.update({
    where: { id: userId },
    data: { backupCodes: newBackupCodes }
  })

  await logSecurityEvent({
    type: AuditEventType.SECURITY_SETTINGS_CHANGED,
    userId,
    action: "backup_codes_regenerated",
    timestamp: new Date().toISOString()
  })

  return newBackupCodes
}
```

本章展示身份建立、会话、授权、MFA 与审计的可组合模式，不构成可直接上线的认证系统。接入前必须按实际身份提供商、令牌存储、数据保留、隐私法规、限流基础设施、密钥轮换和事故响应完成威胁建模与独立测试。

### 上线前必须验证的事情

1. 两个不同身份直接访问同一资源的 URL、服务端动作和 API，均不能越权读取或写入。
2. 登录失败、重置密码、MFA 失败、令牌撤销和会话过期各有统一对外错误，内部审计记录不含密码、令牌或备用码。
3. OAuth 回调验证 `state`、重定向目标和提供商声明；回调失败或重复请求不会创建错误会话。
4. 速率限制、锁定和恢复流程在隔离环境实际触发，并记录可解除路径，避免把永久锁定当作安全措施。
5. 密钥轮换、备份恢复和审计保留期由部署环境验证；文档中的数据模型不是默认合规方案。

---

## 模式不变量

- **凭证只在服务端存在与验证**：密码以单向哈希存储、比对在服务端完成，明文与哈希均不下发客户端（对照 `authorize` 的 bcrypt 比对与 `hashPassword`）。
- **认证失败是需要治理的信号**：每次失败留痕、计数并升级后果（限流、账户锁定、告警），对外错误信息不区分"用户不存在"与"密码错误"，以防账号枚举（对照 `logFailedAttempt`/`checkAccountLockout` 与统一的"邮箱或密码错误"提示）。
- **单一凭证不是充分条件**：MFA 将"知道什么"与"拥有什么"组合为强制门槛，备用码是一次性等效凭证、用后即焚（对照 MFA 节的 TOTP 验证与 backupCodes 消费）。
- **会话是带租期、可撤销的信任凭证**：令牌具备过期时间与唯一标识，撤销经黑名单即时生效，而非等待自然过期（对照 JWT 会话策略与 `JWTBlacklist` 模型）。
- **授权随身份签发、在每次访问时复核**：角色与权限在认证时写入会话，资源访问点仍须服务端复核——认证通过不等于任意操作放行（对照 jwt/session 回调的角色注入与 `authorized` 回调）。

---

## 🔄 文档交叉引用

### 相关文档
- 📄 **[表单验证模式](./06-form-validation-patterns.md)**: 深入了解登录表单和用户注册表单验证
- 📄 **[状态管理模式](./05-state-management-patterns.md)**: 学习用户状态管理和认证状态持久化
- 📄 **[数据获取模式](./04-data-fetching-patterns.md)**: 掌握API安全认证和权限验证
- 📄 **[客户端组件模式](./03-client-components-patterns.md)**: 实现认证相关的客户端交互组件

### 参考章节
- 📖 **[本模块其他章节]**: [表单验证模式](./06-form-validation-patterns.md#️-企业级表单配置)中的登录表单部分
- 📖 **[其他模块相关内容]**: [JavaScript现代语法](../language-concepts/04-javascript-modern.md)中的异步编程部分

---

## 📝 总结

### 核心要点回顾
1. **NextAuth.js v5**: 企业级认证配置和OAuth集成
2. **JWT安全系统**: 令牌加密、刷新机制、黑名单管理
3. **威胁检测**: IP限制、异常行为监控、安全事件日志
4. **多因子认证**: TOTP实现、备用码生成、二维码验证
5. **权限管理**: RBAC系统、细粒度权限控制

### 学习成果检查
- [ ] 是否理解了NextAuth.js v5的企业级配置？
- [ ] 是否能够实现JWT安全认证系统？
- [ ] 是否掌握了威胁检测和防护机制？
- [ ] 是否能够构建多因子认证系统？
- [ ] 是否具备了企业级认证系统开发能力？

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
