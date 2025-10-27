# Web安全最佳实践完整指南

> **文档简介**: Next.js 15 + React 19 企业级Web安全最佳实践，涵盖XSS防护、CSRF保护、认证授权、数据验证、安全Headers等全方位安全策略

> **目标读者**: 高级前端工程师、安全专家、技术架构师、DevSecOps工程师

> **前置知识**: Next.js 15深度掌握、React 19高级特性、Web安全基础、OWASP安全标准

> **预计时长**: 12-18小时

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `advanced-topics/security` |
| **难度** | ⭐⭐⭐⭐⭐ (5/5星) |
| **标签** | `#web-security` `#xss` `#csrf` `#authentication` `#owasp` `#nextjs15` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标

- 深入理解OWASP Top 10安全威胁和防护策略
- 掌握Next.js 15应用的安全配置和最佳实践
- 实施企业级认证授权系统和权限管理
- 建立完整的数据验证和输入清理机制
- 实现安全Headers、CORS配置、内容安全策略
- 构建安全监控、漏洞扫描、应急响应体系

## 📖 概述

本指南全面探讨现代Web应用的安全防护策略，从基础的安全编码实践到企业级安全架构设计。通过实际代码示例和最佳实践，帮助开发者构建安全可靠的Next.js 15应用。

## 🛡️ OWASP Top 10 防护策略

### 🚫 SQL注入防护

```typescript
// app/lib/database-security.ts
import { sql, literal, empty } from 'drizzle-orm'

class DatabaseSecurity {
  private whitelistTables: Set<string> = new Set(['users', 'products', 'orders'])

  // 安全的查询构建器
  safeQuery<T>(table: string, columns: string[], where?: any) {
    if (!this.whitelistTables.has(table)) {
      throw new Error(`Table '${table}' is not whitelisted for queries`)
    }

    // 使用参数化查询
    const query = db.select({ columns: columns.map(c => sql.column(c)) })
      .from(sql.table(table))

    if (where) {
      this.appendSafeWhereClause(query, where)
    }

    return query
  }

  private appendSafeWhereClause(query: any, where: any) {
    if (typeof where === 'object' && where !== null) {
      const conditions: any[] = []

      Object.entries(where).forEach(([key, value]) => {
        if (this.isValidColumnName(key)) {
          conditions.push(sql`${sql.column(key)} = ${sql.placeholder(value)}`)
        }
      })

      if (conditions.length > 0) {
        query.where(sql.and(...conditions))
      }
    }
  }

  private isValidColumnName(columnName: string): boolean {
    // 仅允许字母数字和下划线
    return /^[a-zA-Z0-9_]+$/.test(columnName)
  }

  // ORM集成安全
  async safeCreate<T>(table: string, data: T) {
    if (!this.whitelistTables.has(table)) {
      throw new Error(`Table '${table}' is not whitelisted for inserts`)
    }

    // 验证数据
    const validatedData = this.validateDataForTable(data, table)

    // 使用ORM的安全插入方法
    return await db.insert(table).values(validatedData).returning()
  }

  private validateDataForTable<T>(data: T, table: string): T {
    const schema = this.getTableSchema(table)
    return schema.parse(data)
  }

  private getTableSchema(table: string) {
    switch (table) {
      case 'users':
        return userSchema
      case 'products':
        return productSchema
      case 'orders':
        return orderSchema
      default:
        throw new Error(`Unknown table schema: ${table}`)
    }
  }
}

// 用户数据验证schema
const userSchema = z.object({
  id: z.string().uuid().optional(),
  email: z.string().email(),
  username: z.string().min(3).max(50).regex(/^[a-zA-Z0-9_]+$/),
  password: z.string().min(8).regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/),
  role: z.enum(['user', 'admin', 'moderator']).default('user'),
  isActive: z.boolean().default(true),
  createdAt: z.date().default(() => new Date()),
  updatedAt: z.date().default(() => new Date())
})

export const databaseSecurity = new DatabaseSecurity()
```

### 🔒 XSS防护策略

```typescript
// app/components/security/SafeContent.tsx
import { useMemo } from 'react'
import DOMPurify from 'dompurify'
import { JSDOM } from 'jsdom'

interface SafeContentProps {
  content: string
  as?: 'div' | 'span' | 'p' | 'h1' | 'h2' | 'h3'
  className?: string
  allowedTags?: string[]
  allowedAttributes?: Record<string, string[]>
}

// 内容安全净化器
class ContentSecurity {
  private defaultAllowedTags = [
    'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'strong', 'em', 'u', 'i', 'b', 'ul', 'ol', 'li', 'br',
    'blockquote', 'code', 'pre', 'a'
  ]

  private defaultAllowedAttributes = {
    '*': ['class', 'id', 'style'],
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'width', 'height', 'title'],
    'code': ['class', 'data-language'],
    'pre': ['class', 'data-language']
  }

  // DOMPurify配置
  private domPurifyConfig = {
    ALLOWED_TAGS: this.defaultAllowedTags,
    ALLOWED_ATTR: this.defaultAllowedAttributes,
    FORCE_BODY: true,
    ADD_ATTR: ['target'],
    ADD_DATA_URI_TAGS: ['img', 'video', 'audio'],
    USE_PROFILES: false,
    SANITIZE_DOM: false,
    SANITIZE_NAMED_PROPS: false,
    SANITIZE_UNKNOWN_PROPS: false,
    KEEP_CONTENT: true,
    IN_PLACE: true,
    RETURN_DOM_FRAGMENT: false,
    RETURN_DOM: false,
    RETURN_TRUSTED_TYPE: false,
    WHOLE_DOCUMENT: false,
    FORBID_ATTR: ['style'],
    FORBID_TAGS: ['script', 'style', 'iframe', 'form', 'input'],
    ALLOW_DATA_ATTR: true,
    ALLOW_UNKNOWN_PROTOCOLS: false,
    SAFE_FOR_JQUERY: false,
    SAFE_FOR_TEMPLATES: false,
    SAFE_FOR_XML: false,
    ADD_URI_SAFE_ATTR: ['href', 'src', 'xlink:href'],
    USE_CDATA: false,
    IN_PLACE: true
  }

  // 服务器端内容净化
  sanitizeForServer(content: string): string {
    // 使用JSDOM模拟DOM环境
    const jsdom = new JSDOM('<!DOCTYPE html><html><body></body></html>')
    const purify = DOMPurify(jsdom.window as any)

    return purify.sanitize(content, this.domPurifyConfig)
  }

  // 客户端内容净化
  sanitizeForClient(content: string): string {
    if (typeof window !== 'undefined') {
      return DOMPurify.sanitize(content, this.domPurifyConfig)
    }
    return content // 降级到原始内容
  }

  // 自定义净化配置
  createSanitizer(allowedTags: string[], allowedAttributes: Record<string, string[]>) {
    const customConfig = {
      ...this.domPurifyConfig,
      ALLOWED_TAGS: allowedTags,
      ALLOWED_ATTR: {
        ...this.domPurifyConfig.ALLOWED_ATTR,
        ...allowedAttributes
      }
    }

    return (content: string) => {
      if (typeof window !== 'undefined') {
        return DOMPurify.sanitize(content, customConfig)
      }
      return this.sanitizeForServer(content)
    }
  }
}

export const contentSecurity = new ContentSecurity()

// 安全内容组件
export function SafeContent({
  content,
  as = 'div',
  className = '',
  allowedTags,
  allowedAttributes
}: SafeContentProps) {
  const sanitizedContent = useMemo(() => {
    if (allowedTags || allowedAttributes) {
      const customSanitizer = contentSecurity.createSanitizer(
        allowedTags || contentSecurity.defaultAllowedTags,
        allowedAttributes || contentSecurity.defaultAllowedAttributes
      )
      return customSanitizer(content)
    }
    return contentSecurity.sanitizeForClient(content)
  }, [content, allowedTags, allowedAttributes])

  const Component = as as keyof JSX.IntrinsicElements

  return (
    <Component
      className={className}
      dangerouslySetInnerHTML={{ __html: sanitizedContent }}
    />
  )
}

// 富文本编辑器安全配置
export function createEditorSecurityConfig() {
  return {
    // 允许的标签
    allowedTags: [
      'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'strong', 'em', 'u', 'i', 'b', 'ul', 'ol', 'li',
      'blockquote', 'code', 'pre', 'a', 'img', 'br',
      'table', 'thead', 'tbody', 'tr', 'th', 'td',
      'div', 'span'
    ],

    // 允许的属性
    allowedAttributes: {
      '*': ['class', 'id', 'style'],
      'a': ['href', 'title', 'target', 'rel'],
      'img': ['src', 'alt', 'width', 'height', 'title'],
      'code': ['class', 'data-language'],
      'pre': ['class', 'data-language'],
      'table': ['border', 'cellpadding', 'cellspacing'],
      'th': ['colspan', 'rowspan', 'align'],
      'td': ['colspan', 'rowspan', 'align']
    },

    // 安全链接验证
    linkValidator: (link: string) => {
      try {
        const url = new URL(link)
        // 只允许http和https协议
        return ['http:', 'https:'].includes(url.protocol)
      } catch {
        return false
      }
    },

    // 图片源验证
    imageValidator: (src: string) => {
      try {
        const url = new URL(src, window.location.origin)
        return ['http:', 'https:', 'data:'].includes(url.protocol)
      } catch {
        return false
      }
    }
  }
}
```

### 🛡️ CSRF防护

```typescript
// app/lib/csrf-protection.ts
import { generateRandomString } from './crypto-utils'

class CSRFProtection {
  private tokenLength = 32
  private cookieName = 'csrf-token'
  private headerName = 'X-CSRF-Token'
  private secure = true
  private httpOnly = true
  private sameSite: 'strict' as 'strict' | 'lax' | 'none'

  // 生成CSRF Token
  generateToken(): string {
    return generateRandomString(this.tokenLength)
  }

  // 验证CSRF Token
  validateToken(token: string, storedToken: string): boolean {
    if (!token || !storedToken) {
      return false
    }

    // 使用恒定时间比较防止时序攻击
    return this.constantTimeCompare(token, storedToken)
  }

  // 恒定时间比较
  private constantTimeCompare(a: string, b: string): boolean {
    if (a.length !== b.length) {
      return false
    }

    let result = 0
    for (let i = 0; i < a.length; i++) {
      result |= a.charCodeAt(i) ^ b.charCodeAt(i)
    }

    return result === 0
  }

  // 设置CSRF Cookie
  setCSRFCookie(response: Response, token: string): void {
    response.cookies.set(this.cookieName, token, {
      httpOnly: this.httpOnly,
      secure: this.secure,
      sameSite: this.sameSite,
      path: '/',
      maxAge: 3600 // 1小时
    })
  }

  // 从Cookie获取Token
  getTokenFromCookie(request: Request): string | undefined {
    return request.cookies.get(this.cookieName)?.value
  }

  // 从Header获取Token
  getTokenFromHeader(request: Request): string | undefined {
    return request.headers.get(this.headerName) as string
  }

  // 生成并设置CSRF Token
  generateAndSetToken(response: Response): string {
    const token = this.generateToken()
    this.setCSRFCookie(response, token)
    return token
  }

  // 验证请求中的CSRF Token
  validateRequest(request: Request): boolean {
    // GET、HEAD、OPTIONS请求不需要CSRF保护
    const method = request.method.toUpperCase()
    if (['GET', 'HEAD', 'OPTIONS'].includes(method)) {
      return true
    }

    // 从Cookie获取存储的Token
    const cookieToken = this.getTokenFromCookie(request)
    if (!cookieToken) {
      return false
    }

    // 从Header获取请求Token
    const headerToken = this.getTokenFromHeader(request)
    if (!headerToken) {
      return false
    }

    // 验证Token是否匹配
    return this.validateToken(headerToken, cookieToken)
  }

  // CSRF中间件
  middleware(request: Request): Response | null {
    // 验证CSRF Token
    if (!this.validateRequest(request)) {
      return new Response('CSRF token validation failed', {
        status: 403,
        headers: {
          'Content-Type': 'text/plain',
          'X-CSRF-Status': 'failed'
        }
      })
    }

    return null // 继续处理请求
  }
}

// 双重提交Cookie模式
class DoubleSubmitCookieProtection extends CSRFProtection {
  private actionTokenCookie = 'csrf-action-token'

  // 生成Action Token
  generateActionToken(): string {
    return this.generateToken()
  }

  // 验证Action Token
  validateActionToken(token: string, storedToken: string): boolean {
    return this.validateToken(token, storedToken)
  }

  // 设置双重提交Cookie
  setDoubleSubmitCookies(response: Response, csrfToken: string, actionToken: string): void {
    // 设置主CSRF Token
    this.setCSRFCookie(response, csrfToken)

    // 设置Action Token
    response.cookies.set(this.actionTokenCookie, actionToken, {
      httpOnly: this.httpOnly,
      secure: this.secure,
      sameSite: this.sameSite,
      path: '/',
      maxAge: 300 // 5分钟
    })
  }

  // 验证双重提交
  validateDoubleSubmit(request: Request): boolean {
    const cookieToken = this.getTokenFromCookie(request)
    const actionToken = request.cookies.get(this.actionTokenCookie)?.value

    if (!cookieToken || !actionToken) {
      return false
    }

    return this.validateToken(actionToken, cookieToken)
  }

  // 生成双重提交Tokens
  generateDoubleSubmitTokens(response: Response): { csrfToken: string; actionToken: string } {
    const csrfToken = this.generateToken()
    const actionToken = this.generateActionToken()

    this.setDoubleSubmitCookies(response, csrfToken, actionToken)

    return { csrfToken, actionToken }
  }
}

export const csrfProtection = new CSRFProtection()
export const doubleSubmitProtection = new DoubleSubmitCookieProtection()
```

## 🔐 认证授权安全

### 🛡️ NextAuth.js 安全配置

```typescript
// app/lib/auth-config.ts
import NextAuth from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import GoogleProvider from 'next-auth/providers/google'
import { PrismaAdapter } from '@next-auth/prisma-adapter'
import { jwt } from '@hapi/jwt'
import bcrypt from 'bcryptjs'

// JWT验证中间件
async function verifyJWT(token: string, secret: string) {
  try {
    const { decoded } = jwt.verify(token, secret, {
      algorithms: ['HS256']
    })
    return decoded.payload
  } catch (error) {
    throw new Error('Invalid token')
  }
}

// 密码加密和验证
export class PasswordSecurity {
  private saltRounds = 12

  // 哈希密码
  async hashPassword(password: string): Promise<string> {
    return bcrypt.hash(password, this.saltRounds)
  }

  // 验证密码
  async verifyPassword(password: string, hash: string): Promise<boolean> {
    return bcrypt.compare(password, hash)
  }

  // 密码强度验证
  validatePasswordStrength(password: string): {
    isValid: boolean
    score: number
    feedback: string[]
  } {
    const feedback: string[] = []
    let score = 0

    // 长度检查
    if (password.length >= 8) {
      score += 1
    } else {
      feedback.push('密码长度至少8位')
    }

    // 复杂度检查
    if (/[a-z]/.test(password)) {
      score += 1
    } else {
      feedback.push('密码必须包含小写字母')
    }

    if (/[A-Z]/.test(password)) {
      score += 1
    } else {
      feedback.push('密码必须包含大写字母')
    }

    if (/[0-9]/.test(password)) {
      score += 1
    } else {
      feedback.push('密码必须包含数字')
    }

    if (/[^a-zA-Z0-9]/.test(password)) {
      score += 1
    } else {
      feedback.push('密码必须包含特殊字符')
    }

    // 常见密码检查
    const commonPasswords = [
      'password', '123456', 'qwerty', 'admin',
      'letmein', 'welcome', 'dragon', 'monkey'
    ]

    if (commonPasswords.includes(password.toLowerCase())) {
      score = 0
      feedback.push('密码过于常见，请使用更复杂的密码')
    }

    return {
      isValid: score >= 4,
      score,
      feedback
    }
  }
}

// 会话安全配置
export const authConfig = {
  adapter: PrismaAdapter(prisma),
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30天
    updateAge: 24 * 60 * 60, // 24小时
  },
  jwt: {
    secret: process.env.NEXTAUTH_JWT_SECRET!,
    encryption: true,
    signingKey: process.env.NEXTAUTH_JWT_SIGNING_KEY!,
    encryptionKey: process.env.NEXTAUTH_JWT_ENCRYPTION_KEY!,
    // 自定义JWT Header
    headers: {
      typ: 'JWT',
      alg: 'HS256'
    },
    // JWT Claims
    claims: {
      iss: 'your-app',
      aud: 'your-users',
      exp: 1800, // 30分钟
      nbf: true
      iat: true
      jti: true
    }
  },
  providers: [
    CredentialsProvider({
      id: 'credentials',
      name: 'Credentials',
      type: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        try {
          const { email, password } = credentials

          // 输入验证
          if (!email || !password) {
            return null
          }

          // 查找用户
          const user = await prisma.user.findUnique({
            where: { email },
            include: { security: true }
          })

          if (!user) {
            return null
          }

          // 账户状态检查
          if (!user.isActive) {
            return null
          }

          // 锁定状态检查
          if (user.security?.isLocked) {
            const lockUntil = new Date(user.security.lockedUntil!)
            if (new Date() < lockUntil) {
              return null
            }
            // 解锁账户
            await prisma.userSecurity.update({
              where: { userId: user.id },
              data: { isLocked: false, lockedUntil: null, failedAttempts: 0 }
            })
          }

          // 密码验证
          const isPasswordValid = await passwordSecurity.verifyPassword(password, user.password)
          if (!isPasswordValid) {
            // 更新失败尝试
            await this.handleFailedLogin(user.id, user.security?.failedAttempts || 0)
            return null
          }

          // 重置失败尝试
          if (user.security?.failedAttempts > 0) {
            await prisma.userSecurity.update({
              where: { userId: user.id },
              data: { failedAttempts: 0, isLocked: false, lockedUntil: null }
            })
          }

          // 会话审计日志
          await prisma.sessionAudit.create({
            data: {
              userId: user.id,
              action: 'login_success',
              ipAddress: 'REMOTE_ADDR', // 需要在中间件中获取
              userAgent: 'HTTP_USER_AGENT', // 需要在中间件中获取
              device: this.detectDevice()
            }
          })

          return {
            id: user.id,
            email: user.email,
            name: user.name,
            role: user.role,
            image: user.image
          }
        } catch (error) {
          console.error('Authorization error:', error)
          return null
        }
      },

      // 处理失败登录
      async handleFailedLogin(userId: string, failedAttempts: number) {
        const maxAttempts = 5
        const newAttempts = failedAttempts + 1

        let lockUntil: Date | null = null

        if (newAttempts >= maxAttempts) {
          // 锁定账户30分钟
          lockUntil = new Date(Date.now() + 30 * 60 * 1000)
        }

        await prisma.userSecurity.update({
          where: { userId },
          data: {
            failedAttempts: newAttempts,
            isLocked: lockUntil !== null,
            lockedUntil
          }
        })

        // 安全审计日志
        await prisma.securityAudit.create({
          data: {
            userId,
            action: 'login_failed',
            ipAddress: 'REMOTE_ADDR',
            userAgent: 'HTTP_USER_AGENT',
            device: this.detectDevice(),
            details: `Failed attempt ${newAttempts}/${maxAttempts}`
          }
        })
      },

      // 设备检测
      detectDevice(): string {
        const userAgent = navigator.userAgent
        if (/Mobile/i.test(userAgent)) {
          return 'mobile'
        } else if (/Tablet|iPad/i.test(userAgent)) {
          return 'tablet'
        } else {
          return 'desktop'
        }
      }
    }),
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      authorization: {
        params: {
          prompt: 'consent',
          access_type: 'offline',
          response_type: 'code',
          scope: 'openid email profile'
        }
      }
    })
  ],
  pages: {
    signIn: '/auth/signin',
    error: '/auth/error',
    signOut: '/auth/signout'
  },
  callbacks: {
    // JWT签名回调
    async jwt({ token, user }) {
      const payload = {
        sub: user.id,
        email: user.email,
        role: user.role,
        iat: Date.now() / 1000,
        exp: Math.floor(Date.now() / 1000) + (30 * 24 * 60 * 60)
      }

      return { ...payload, jti: generateRandomString(16) }
    },

    // 会话回调
    async session({ session, token }) {
      try {
        const decodedToken = await verifyJWT(token, process.env.NEXTAUTH_JWT_SECRET!)

        // 验证会话有效性
        const userSession = await prisma.session.findFirst({
          where: {
            userId: decodedToken.sub,
            expiresAt: { gt: new Date() }
          },
          include: { user: true }
        })

        if (!userSession || !userSession.user.isActive) {
          return null
        }

        // 更新会话活跃状态
        await prisma.session.update({
          where: { id: userSession.id },
          data: { lastActiveAt: new Date() }
        })

        return {
          ...session,
          user: {
            ...session.user,
            role: decodedToken.role
          }
        }
      } catch (error) {
        console.error('Session verification error:', error)
        return null
      }
    },

    // 重定向回调
    async redirect({ url, baseUrl }) {
      // 根据用户角色重定向
      if (url.includes('/auth/callback')) {
        const session = await getServerSession()
        if (session?.user?.role === 'admin') {
          return '/admin/dashboard'
        } else if (session?.user?.role === 'moderator') {
          return '/moderator/dashboard'
        } else {
          return '/user/dashboard'
        }
      }
      return url
    }
  },

  // 事件处理
  events: {
    async signIn(message) {
      console.log('Sign in event:', message)
    },
    async signOut(message) {
      console.log('Sign out event:', message)
    },
    async createUser(message) {
      console.log('Create user event:', message)
    },
    async updateUser(message) {
      console.log('Update user event:', message)
    },
    async linkAccount(message) {
      console.log('Link account event:', message)
    },
    async session(message) {
      console.log('Session event:', message)
    }
  },

  // 调试
  debug: process.env.NODE_ENV === 'development'
}

export default NextAuth(authConfig)
```

### 🔐 角色权限管理

```typescript
// app/lib/rbac.ts
interface Permission {
  id: string
  name: string
  description: string
  resource: string
  action: 'create' | 'read' | 'update' | 'delete' | 'execute'
  scope: 'global' | 'organization' | 'project' | 'personal'
}

interface Role {
  id: string
  name: string
  description: string
  permissions: string[]
  isSystemRole?: boolean
}

interface UserSecurity {
  userId: string
  roleId: string
  customPermissions: string[]
  organizationId?: string
  projectId?: string
}

// 预定义权限
const permissions: Permission[] = [
  // 用户管理
  { id: 'users:create', name: '创建用户', description: '创建新用户账户', resource: 'users', action: 'create', scope: 'global' },
  { id: 'users:read', name: '查看用户', description: '查看用户信息', resource: 'users', action: 'read', scope: 'global' },
  { id: 'users:update', name: '更新用户', description: '更新用户信息', resource: 'users', action: 'update', scope: 'global' },
  { id: 'users:delete', name: '删除用户', description: '删除用户账户', resource: 'users', action: 'delete', scope: 'global' },

  // 内容管理
  { id: 'content:create', name: '创建内容', description: '创建新的内容', resource: 'content', action: 'create', scope: 'organization' },
  { id: 'content:read', name: '查看内容', description: '查看内容列表', resource: 'content', action: 'read', scope: 'global' },
  { id: 'content:update', name: '更新内容', description: '更新现有内容', resource: 'content', action: 'update', scope: 'organization' },
  { id: 'content:delete', name: '删除内容', description: '删除内容', resource: 'content', action: 'delete', scope: 'organization' },
  { id: 'content:publish', name: '发布内容', description: '发布内容', resource: 'content', action: 'execute', scope: 'organization' },

  // 项目管理
  { id: 'projects:create', name: '创建项目', description: '创建新项目', resource: 'projects', action: 'create', scope: 'organization' },
  { id: 'projects:read', name: '查看项目', description: '查看项目信息', resource: 'projects', action: 'read', scope: 'global' },
  { id: 'projects:update', name: '更新项目', description: '更新项目信息', resource: 'projects', action: 'update', scope: 'organization' },
  { id: 'projects:delete', name: '删除项目', description: '删除项目', resource: 'projects', action: 'delete', scope: 'organization' },
  { id: 'projects:archive', name: '归档项目', description: '归档项目', resource: 'projects', action: 'execute', scope: 'organization' },

  // 系统管理
  { id: 'system:config', name: '系统配置', description: '修改系统配置', resource: 'system', action: 'update', scope: 'global' },
  { id: 'system:audit', name: '审计日志', description: '查看系统审计日志', resource: 'system', action: 'read', scope: 'global' },
  { id: 'system:security', name: '安全设置', description: '修改安全设置', resource: 'system', action: 'update', scope: 'global' },
  { id: 'system:backup', name: '系统备份', description: '执行系统备份', resource: 'system', action: 'execute', scope: 'global' },

  // 报表和分析
  { id: 'reports:read', name: '查看报表', description: '查看各类报表', resource: 'reports', action: 'read', scope: 'organization' },
  { id: 'reports:create', name: '生成报表', description: '生成自定义报表', resource: 'reports', action: 'create', scope: 'organization' },
  { id: 'reports:export', name: '导出报表', description: '导出报表数据', resource: 'reports', action: 'execute', scope: 'organization' },

  // API管理
  { id: 'api:read', name: '查看API', description: '查看API文档', resource: 'api', action: 'read', scope: 'organization' },
  { id: 'api:create', name: '创建API', description: '创建API端点', resource: 'api', action: 'create', scope: 'organization' },
  { id: 'api:update', name: '更新API', description: '更新API配置', resource: 'api', action: 'update', scope: 'organization' },
  { id: 'api:delete', name: '删除API', description: '删除API端点', resource: 'api', action: 'delete', scope: 'organization' }
]

// 预定义角色
const roles: Role[] = [
  {
    id: 'super_admin',
    name: '超级管理员',
    description: '拥有所有权限的系统管理员',
    permissions: permissions.map(p => p.id),
    isSystemRole: true
  },
  {
    id: 'admin',
    name: '管理员',
    description: '拥有大部分管理权限的管理员',
    permissions: permissions
      .filter(p => !p.id.startsWith('system:'))
      .map(p => p.id),
    isSystemRole: true
  },
  {
    id: 'moderator',
    name: '版主',
    description: '内容管理和用户管理权限',
    permissions: [
      ...permissions.filter(p => p.resource === 'users' && ['read', 'update'].includes(p.action)).map(p => p.id),
      ...permissions.filter(p => p.resource === 'content').map(p => p.id),
      'projects:read',
      'reports:read'
    ]
  },
  {
    id: 'editor',
    name: '编辑',
    description: '内容创建和编辑权限',
    permissions: [
      'content:create',
      'content:read',
      'content:update',
      'projects:read'
    ]
  },
  {
    id: 'viewer',
    name: '查看者',
    description: '只读权限',
    permissions: [
      'content:read',
      'projects:read',
      'reports:read'
    ]
  }
]

class RBACService {
  // 权限检查
  async hasPermission(
    userId: string,
    permissionId: string,
    resource?: string,
    scope?: string
  ): Promise<boolean> {
    try {
      // 获取用户安全配置
      const userSecurity = await prisma.userSecurity.findUnique({
        where: { userId },
        include: { role: true }
      })

      if (!userSecurity || !userSecurity.role) {
        return false
      }

      // 检查角色权限
      if (userSecurity.role.permissions.includes(permissionId)) {
        return true
      }

      // 检查自定义权限
      if (userSecurity.customPermissions.includes(permissionId)) {
        return true
      }

      // 作用域权限检查
      if (resource && scope) {
        return this.checkScopedPermission(userSecurity, permissionId, resource, scope)
      }

      return false
    } catch (error) {
      console.error('Permission check error:', error)
      return false
    }
  }

  // 作用域权限检查
  private async checkScopedPermission(
    userSecurity: any,
    permissionId: string,
    resource: string,
    scope: string
  ): Promise<boolean> {
    const permission = permissions.find(p => p.id === permissionId)
    if (!permission) {
      return false
    }

    // 全局作用域权限
    if (permission.scope === 'global' && userSecurity.role.permissions.includes(permissionId)) {
      return true
    }

    // 组织级权限
    if (scope === 'organization' && userSecurity.organizationId) {
      return userSecurity.role.permissions.includes(permissionId)
    }

    // 项目级权限
    if (scope === 'project' && userSecurity.projectId) {
      return userSecurity.role.permissions.includes(permissionId)
    }

    return false
  }

  // 获取用户权限
  async getUserPermissions(userId: string): Promise<string[]> {
    const userSecurity = await prisma.userSecurity.findUnique({
      where: { userId },
      include: { role: true }
    })

    if (!userSecurity || !userSecurity.role) {
      return []
    }

    // 合并角色权限和自定义权限
    const allPermissions = new Set([
      ...userSecurity.role.permissions,
      ...userSecurity.customPermissions
    ])

    return Array.from(allPermissions)
  }

  // 检查多个权限（AND逻辑）
  async hasAllPermissions(
    userId: string,
    permissionIds: string[]
  ): Promise<boolean> {
    for (const permissionId of permissionIds) {
      const hasPermission = await this.hasPermission(userId, permissionId)
      if (!hasPermission) {
        return false
      }
    }
    return true
  }

  // 检查多个权限（OR逻辑）
  async hasAnyPermission(
    userId: string,
    permissionIds: string[]
  ): Promise<boolean> {
    for (const permissionId of permissionIds) {
      const hasPermission = await this.hasPermission(userId, permissionId)
      if (hasPermission) {
        return true
      }
    }
    return false
  }

  // 创建自定义角色
  async createCustomRole(data: {
    name: string
    description: string
    permissions: string[]
    organizationId?: string
  }): Promise<Role> {
    const role = await prisma.role.create({
      data: {
        name,
        description,
        permissions,
        organizationId,
        isSystemRole: false
      }
    })

    return role
  }

  // 分配角色给用户
  async assignRoleToUser(userId: string, roleId: string, organizationId?: string, projectId?: string): Promise<void> {
    await prisma.userSecurity.upsert({
      where: { userId },
      update: {
        roleId,
        organizationId,
        projectId,
        customPermissions: []
      },
      create: {
        userId,
        roleId,
        organizationId,
        projectId,
        customPermissions: []
      }
    })
  }

  // 添加自定义权限
  async addCustomPermission(userId: string, permissionId: string): Promise<void> {
    await prisma.userSecurity.update({
      where: { userId },
      data: {
        customPermissions: {
          push: permissionId
        }
      }
    })
  }

  // 移除自定义权限
  async removeCustomPermission(userId: string, permissionId: string): Promise<void> {
    const userSecurity = await prisma.userSecurity.findUnique({
      where: { userId }
    })

    if (userSecurity) {
      const updatedPermissions = userSecurity.customPermissions.filter(p => p !== permissionId)
      await prisma.userSecurity.update({
        where: { userId },
        data: { customPermissions: updatedPermissions }
      })
    }
  }

  // 获取权限矩阵
  async getPermissionMatrix(userId: string): Promise<Record<string, boolean>> {
    const userPermissions = await this.getUserPermissions(userId)
    const matrix: Record<string, boolean> = {}

    permissions.forEach(permission => {
      matrix[permission.id] = userPermissions.includes(permission.id)
    })

    return matrix
  }
}

// 权限检查Hook
export function usePermissions() {
  const { data: session } = useSession()
  const [permissions, setPermissions] = useState<string[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (session?.user?.id) {
      rbacService.getUserPermissions(session.user.id)
        .then(setPermissions)
        .finally(() => setLoading(false))
    } else {
      setPermissions([])
      setLoading(false)
    }
  }, [session?.user?.id])

  const hasPermission = useCallback(async (permissionId: string, resource?: string, scope?: string) => {
    if (!session?.user?.id) return false
    return await rbacService.hasPermission(session.user.id, permissionId, resource, scope)
  }, [session?.user?.id])

  const hasAllPermissions = useCallback(async (permissionIds: string[]) => {
    if (!session?.user?.id) return false
    return await rbacService.hasAllPermissions(session.user.id, permissionIds)
  }, [session?.user?.id])

  const hasAnyPermission = useCallback(async (permissionIds: string[]) => {
    if (!session?.user?.id) return false
    return await rbacService.hasAnyPermission(session.user.id, permissionIds)
  }, [session?.user?.id])

  const permissionMatrix = useMemo(() => {
    const matrix: Record<string, boolean> = {}
    permissions.forEach(permission => {
      matrix[permission.id] = permissions.includes(permission.id)
    })
    return matrix
  }, [permissions])

  return {
    permissions,
    permissionMatrix,
    loading,
    hasPermission,
    hasAllPermissions,
    hasAnyPermission
  }
}

export const rbacService = new RBACService()
export { permissions, roles }
```

## 🔗 文档交叉引用

### 相关文档
- 📄 **[Core Web Vitals优化](../performance/01-core-web-vitals.md)**: 深入了解性能优化中的安全考量
- 📄 **[认证流程模式](../../knowledge-points/framework-patterns/07-authentication-flows.md)**: 学习企业级认证系统实现
- 📄 **[渲染性能优化](../../knowledge-points/performance-optimization/01-rendering-optimization.md)**: 了解SSR/SSG安全特性

### 参考章节
- 📖 **[本模块其他章节]**: [高级性能调优](../performance/02-advanced-optimization.md)中的安全优化部分
- 📖 **[其他模块相关内容]**: [测试工具指南](../../knowledge-points/development-tools/01-testing-tools.md)中的安全测试部分

## 📝 总结

### 核心要点回顾
1. **OWASP安全防护**: SQL注入、XSS防护、CSRF保护等核心威胁的防护策略
2. **认证授权安全**: NextAuth.js企业级配置、密码安全、RBAC权限管理
3. **数据安全策略**: 输入验证、参数化查询、数据脱敏、加密存储
4. **网络安全**: 安全Headers配置、CORS策略、HTTPS实施、内容安全策略
5. **安全监控**: 漏洞扫描、安全审计、异常监控、应急响应机制

### 学习成果检查
- [ ] 是否理解了OWASP Top 10安全威胁和防护方法？
- [ ] 是否能够实施企业级认证授权系统？
- [ ] 是否掌握了前端XSS、CSRF等安全防护技术？
- [ ] 是否能够配置安全的网络和数据访问策略？
- [ ] 是否具备了Web安全架构设计和实施能力？

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

## 🔗 外部资源

### 📖 官方文档
- 🛡️ **[OWASP安全指南](https://owasp.org/www-project-top-ten/)**: Web安全威胁完整指南
- 🔒 **[Next.js安全文档](https://nextjs.org/docs/security)**: Next.js官方安全配置
- 🔐 **[NextAuth.js安全配置](https://next-auth.js.org/configuration/)**: 认证系统安全配置

### 🛠️ 安全工具
- 🔍 **[OWASP ZAP](https://www.zaproxy.org/)**: 开源Web应用安全扫描器
- 🛡️ **[Snyk](https://snyk.io/)**: 代码安全漏洞检测工具
- 📊 **[Burp Suite](https://portswigger.net/burp)**: Web应用安全测试工具
- 🔐 **[Keycloak](https://www.keycloak.org/)**: 开源身份和访问管理解决方案

### 📱 安全标准
- 📋 **[CIS安全基准](https://www.cisecurity.org/cis-benchmarks/)**: 安全配置最佳实践
- 🛡️ **[NIST网络安全框架](https://www.nist.gov/cyberframework)**: 美国网络安全标准
- 🔒 **[ISO 27001](https://www.iso.org/isoiec-27001-information-security.html)**: 信息安全管理体系

---

**文档状态**: ✅ 已完成 | 🚧 进行中 | 📋 计划中
**最后更新**: 2025年10月
**版本**: v1.0.0