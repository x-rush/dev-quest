# Vercel部署指南 (Vercel Deployment Guide)

> **PHP开发者视角**: 从传统服务器部署到现代云部署的转变，了解Vercel如何简化Next.js应用的部署流程。

## Vercel简介

### 什么是Vercel

Vercel是专为前端开发者设计的云平台，提供：

- **零配置部署**: 自动检测项目配置
- **全球CDN**: 边缘网络加速
- **Serverless函数**: 无服务器计算
- **自动SSL**: HTTPS证书自动管理
- **Git集成**: 与GitHub/GitLab无缝集成

### 为什么选择Vercel

1. **专为Next.js优化**: Vercel与Next.js同属一家公司，提供最佳支持
2. **开发体验优秀**: 预览部署、即时回滚、分支部署
3. **性能卓越**: 边缘计算、智能缓存、图片优化
4. **企业级功能**: 团队协作、权限管理、安全扫描

## 项目配置

### 1. 基础配置文件

```json
// package.json
{
  "name": "my-nextjs-app",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "15.0.0",
    "react": "19.0.0",
    "react-dom": "19.0.0"
  },
  "devDependencies": {
    "@types/node": "20.0.0",
    "@types/react": "18.0.0",
    "@types/react-dom": "18.0.0",
    "typescript": "5.0.0",
    "eslint": "8.0.0",
    "eslint-config-next": "15.0.0"
  }
}
```

```typescript
// next.config.ts
import type { NextConfig } from "next"

const nextConfig: NextConfig = {
  // 优化配置
  swcMinify: true,
  compress: true,
  poweredByHeader: false,

  // 环境变量配置
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },

  // 图片优化
  images: {
    domains: ["example.com", "assets.example.com"],
    formats: ["image/webp", "image/avif"],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // 重定向配置
  async redirects() {
    return [
      {
        source: "/old-path",
        destination: "/new-path",
        permanent: true,
      },
    ]
  },

  // 重写配置
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "https://api.example.com/:path*",
      },
    ]
  },

  // 头部配置
  async headers() {
    return [
      {
        source: "/api/:path*",
        headers: [
          { key: "Access-Control-Allow-Origin", value: "*" },
          { key: "Access-Control-Allow-Methods", value: "GET,POST,PUT,DELETE,OPTIONS" },
          { key: "Access-Control-Allow-Headers", value: "Content-Type,Authorization" },
        ],
      },
    ]
  },

  // 实验性功能
  experimental: {
    serverActions: true,
    serverComponentsExternalPackages: ["sharp"],
  },
}

export default nextConfig
```

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### 2. Vercel配置文件

```json
// vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ],
  "env": {
    "NEXT_PUBLIC_API_URL": "https://api.example.com",
    "DATABASE_URL": "@database_url",
    "NEXTAUTH_SECRET": "@nextauth_secret",
    "NEXTAUTH_URL": "@nextauth_url"
  },
  "build": {
    "env": {
      "NEXT_PUBLIC_BUILD_TIME": "${NOW}"
    }
  },
  "crons": [
    {
      "path": "/api/cleanup/expired-sessions",
      "schedule": "0 0 * * *"
    }
  ],
  "functions": {
    "app/api/**/*.ts": {
      "maxDuration": 30
    },
    "app/admin/**/*.tsx": {
      "maxDuration": 60
    }
  }
}
```

### 3. 环境变量配置

```env
# .env.local (本地开发)
DATABASE_URL="postgresql://username:password@localhost:5432/myapp"
NEXTAUTH_SECRET="your-nextauth-secret"
NEXTAUTH_URL="http://localhost:3000"
NEXT_PUBLIC_API_URL="http://localhost:3000/api"
REDIS_URL="redis://localhost:6379"

# .env.production (生产环境)
DATABASE_URL="@database_url"
NEXTAUTH_SECRET="@nextauth_secret"
NEXTAUTH_URL="@nextauth_url"
NEXT_PUBLIC_API_URL="https://api.example.com"
REDIS_URL="@redis_url"
STRIPE_SECRET_KEY="@stripe_secret_key"
AWS_ACCESS_KEY_ID="@aws_access_key_id"
AWS_SECRET_ACCESS_KEY="@aws_secret_access_key"
```

## 部署流程

### 1. 通过Vercel CLI部署

```bash
# 安装Vercel CLI
npm i -g vercel

# 登录Vercel
vercel login

# 初始化项目
vercel

# 部署到生产环境
vercel --prod

# 查看部署日志
vercel logs

# 查看部署历史
vercel ls

# 删除部署
vercel remove [deployment-url]
```

### 2. 通过Git集成部署

```bash
# 连接GitHub仓库
vercel git connect

# 创建.gitignore文件
# .gitignore
node_modules/
.next/
.env.local
.env.development.local
.env.test.local
.env.production.local
.DS_Store
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
.vercel

# 提交代码并推送
git add .
git commit -m "feat: 添加初始功能"
git push origin main
```

### 3. 分支部署策略

```yaml
# .github/workflows/vercel-preview.yml
name: Vercel Preview Deployment

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  deploy-preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Vercel
        uses: vercel/action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}

      - name: Comment PR with Preview URL
        uses: actions/github-script@v6
        with:
          script: |
            const { VERCEL_URL } = process.env
            if (VERCEL_URL) {
              github.rest.issues.createComment({
                issue_number: context.issue.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: `🚀 Preview deployment: ${VERCEL_URL}`
              })
            }
        env:
          VERCEL_URL: ${{ steps.deploy.outputs.preview-url }}
```

## 高级配置

### 1. 边缘函数

```typescript
// app/api/edge/route.ts
import { NextRequest, NextResponse } from "next/server"

export const runtime = "edge"

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const name = searchParams.get("name") || "World"

  // 在边缘节点处理请求
  const greeting = `Hello, ${name}!`
  const timestamp = new Date().toISOString()

  return NextResponse.json({
    greeting,
    timestamp,
    location: "Edge",
  })
}

export async function POST(request: NextRequest) {
  const body = await request.json()

  // 边缘处理逻辑
  const result = {
    received: body,
    processed: true,
    timestamp: new Date().toISOString(),
  }

  return NextResponse.json(result)
}
```

### 2. 中间件配置

```typescript
// middleware.ts
import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"
import { createMiddlewareClient } from "@supabase/auth-helpers-nextjs"

export async function middleware(request: NextRequest) {
  const res = NextResponse.next()
  const supabase = createMiddlewareClient({ req: request, res })

  // 刷新session
  const {
    data: { session },
  } = await supabase.auth.getSession()

  // 受保护路由
  if (request.nextUrl.pathname.startsWith("/dashboard")) {
    if (!session) {
      const redirectUrl = new URL("/login", request.url)
      redirectUrl.searchParams.set("redirectTo", request.nextUrl.pathname)
      return NextResponse.redirect(redirectUrl)
    }
  }

  // 管理员路由
  if (request.nextUrl.pathname.startsWith("/admin")) {
    if (!session || session.user.role !== "admin") {
      return NextResponse.redirect(new URL("/unauthorized", request.url))
    }
  }

  // 添加安全头部
  const requestHeaders = new Headers(request.headers)
  requestHeaders.set("x-pathname", request.nextUrl.pathname)

  // 添加缓存控制
  if (request.nextUrl.pathname.startsWith("/api/")) {
    res.headers.set("Cache-Control", "no-store, max-age=0")
  }

  return res
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
}
```

### 3. 自定义服务器配置

```typescript
// server.js
const { createServer } = require("http")
const { parse } = require("url")
const next = require("next")

const dev = process.env.NODE_ENV !== "production"
const hostname = "localhost"
const port = process.env.PORT || 3000

const app = next({ dev, hostname, port })
const handler = app.getRequestHandler()

app.prepare().then(() => {
  createServer(async (req, res) => {
    try {
      const parsedUrl = parse(req.url, true)
      await handler(req, res, parsedUrl)
    } catch (err) {
      console.error("Error occurred handling", req.url, err)
      res.statusCode = 500
      res.end("internal server error")
    }
  })
    .once("error", (err) => {
      console.error(err)
      process.exit(1)
    })
    .listen(port, () => {
      console.log(`> Ready on http://${hostname}:${port}`)
    })
})
```

## 性能优化

### 1. 图片优化

```typescript
// components/optimized-image.tsx
import Image from "next/image"
import { useState } from "react"

interface OptimizedImageProps {
  src: string
  alt: string
  width?: number
  height?: number
  priority?: boolean
  placeholder?: "blur" | "empty"
  blurDataURL?: string
}

export function OptimizedImage({
  src,
  alt,
  width = 800,
  height = 600,
  priority = false,
  placeholder = "blur",
  blurDataURL,
}: OptimizedImageProps) {
  const [isLoading, setLoading] = useState(true)

  return (
    <div className="overflow-hidden">
      <Image
        src={src}
        alt={alt}
        width={width}
        height={height}
        priority={priority}
        placeholder={placeholder}
        blurDataURL={blurDataURL}
        className={`
          duration-700 ease-in-out
          ${isLoading ? "scale-110 blur-2xl grayscale" : "scale-100 blur-0 grayscale-0"}
        `}
        onLoadingComplete={() => setLoading(false)}
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
      />
    </div>
  )
}
```

### 2. 字体优化

```typescript
// app/layout.tsx
import { Inter, Roboto_Mono } from "next/font/google"

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
})

const robotoMono = Roboto_Mono({
  subsets: ["latin"],
  variable: "--font-roboto-mono",
  display: "swap",
})

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN" className={`${inter.variable} ${robotoMono.variable}`}>
      <body>{children}</body>
    </html>
  )
}
```

### 3. 代码分割

```typescript
// 动态导入组件
import dynamic from "next/dynamic"

// 懒加载重型组件
const HeavyComponent = dynamic(() => import("@/components/HeavyComponent"), {
  loading: () => <div>加载中...</div>,
  ssr: false, // 禁用服务端渲染
})

// 条件加载组件
const AdminPanel = dynamic(
  () => import("@/components/AdminPanel"),
  { ssr: false }
)

// 带错误处理的动态导入
const ChartComponent = dynamic(
  () => import("@/components/ChartComponent"),
  {
    loading: () => <div>加载图表...</div>,
    ssr: false,
    onError: () => <div>加载失败</div>,
  }
)

export function Dashboard() {
  const [isAdmin, setIsAdmin] = useState(false)

  return (
    <div>
      <h1>仪表板</h1>

      {/* 条件渲染 */}
      {isAdmin && <AdminPanel />}

      {/* 延迟加载 */}
      <HeavyComponent />

      {/* 图表组件 */}
      <ChartComponent />
    </div>
  )
}
```

## 监控和分析

### 1. Vercel Analytics

```typescript
// 安装分析包
npm install @vercel/analytics

// app/layout.tsx
import { Analytics } from "@vercel/analytics/react"

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  )
}

// 自定义事件跟踪
import { track } from "@vercel/analytics"

export function SignupButton() {
  const handleSignup = () => {
    track("signup_clicked", {
      location: "homepage",
      plan: "pro",
    })
    // 处理注册逻辑
  }

  return <button onClick={handleSignup}>注册</button>
}
```

### 2. 错误监控

```typescript
// 安装Sentry
npm install @sentry/nextjs

// next.config.ts
const { withSentryConfig } = require("@sentry/nextjs")

const sentryConfig = {
  silent: true,
  org: "your-org",
  project: "your-project",
}

module.exports = withSentryConfig(nextConfig, sentryConfig)

// app/layout.tsx
import * as Sentry from "@sentry/nextjs"

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 1.0,
  debug: false,
  replaysOnErrorSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
})

// app/error.tsx
"use client"

import { useEffect } from "react"
import * as Sentry from "@sentry/nextjs"
import Error from "next/error"

export default function GlobalError({ error }: { error: Error }) {
  useEffect(() => {
    Sentry.captureException(error)
  }, [error])

  return (
    <html>
      <body>
        <Error statusCode={500} />
      </body>
    </html>
  )
}
```

### 3. 性能监控

```typescript
// 安装Web Vitals
npm install web-vitals

// app/layout.tsx
import { getCLS, getFID, getFCP, getLCP, getTTFB } from "web-vitals"

export function reportWebVitals(metric: any) {
  // 发送到分析服务
  if (metric.label === "web-vital") {
    console.log(metric)
    // 发送到Vercel Analytics或其他服务
  }
}

// 在组件中使用
"use client"

import { useReportWebVitals } from "next/web-vitals"

export function WebVitals() {
  useReportWebVitals((metric) => {
    // 处理性能指标
    console.log(metric)
  })

  return null
}
```

## 环境管理

### 1. 多环境配置

```typescript
// config/environment.ts
interface Environment {
  apiUrl: string
  databaseUrl: string
  redisUrl: string
  stripeKey: string
  isProduction: boolean
  isDevelopment: boolean
}

function getEnvironment(): Environment {
  const isProduction = process.env.NODE_ENV === "production"
  const isDevelopment = process.env.NODE_ENV === "development"

  return {
    apiUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000/api",
    databaseUrl: process.env.DATABASE_URL || "",
    redisUrl: process.env.REDIS_URL || "",
    stripeKey: process.env.STRIPE_SECRET_KEY || "",
    isProduction,
    isDevelopment,
  }
}

export const env = getEnvironment()
```

### 2. 环境变量验证

```typescript
// lib/env.ts
import { z } from "zod"

const envSchema = z.object({
  NODE_ENV: z.enum(["development", "production", "test"]),
  NEXTAUTH_SECRET: z.string().min(32),
  NEXTAUTH_URL: z.string().url(),
  DATABASE_URL: z.string().url(),
  REDIS_URL: z.string().url(),
  STRIPE_SECRET_KEY: z.string().min(1),
  STRIPE_WEBHOOK_SECRET: z.string().min(1),
})

declare global {
  namespace NodeJS {
    interface ProcessEnv extends z.infer<typeof envSchema> {}
  }
}

try {
  envSchema.parse(process.env)
} catch (error) {
  console.error("❌ Invalid environment variables:", error)
  process.exit(1)
}
```

## 安全配置

### 1. 安全头部

```typescript
// next.config.ts
const securityHeaders = [
  {
    key: "X-DNS-Prefetch-Control",
    value: "on",
  },
  {
    key: "Strict-Transport-Security",
    value: "max-age=63072000; includeSubDomains; preload",
  },
  {
    key: "X-Frame-Options",
    value: "SAMEORIGIN",
  },
  {
    key: "X-Content-Type-Options",
    value: "nosniff",
  },
  {
    key: "Referrer-Policy",
    value: "origin-when-cross-origin",
  },
  {
    key: "Permissions-Policy",
    value: "camera=(), microphone=(), geolocation=()",
  },
]

module.exports = {
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: securityHeaders,
      },
    ]
  },
}
```

### 2. CORS配置

```typescript
// next.config.ts
module.exports = {
  async headers() {
    return [
      {
        source: "/api/:path*",
        headers: [
          { key: "Access-Control-Allow-Origin", value: "*" },
          { key: "Access-Control-Allow-Methods", value: "GET,OPTIONS,PATCH,DELETE,POST,PUT" },
          { key: "Access-Control-Allow-Headers", value: "X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version" },
        ],
      },
    ]
  },
}
```

## 备份和恢复

### 1. 数据库备份

```yaml
# .github/workflows/backup.yml
name: Database Backup

on:
  schedule:
    - cron: "0 2 * * *" # 每天凌晨2点
  workflow_dispatch:

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - name: Install PostgreSQL client
        run: |
          sudo apt-get update
          sudo apt-get install -y postgresql-client

      - name: Backup database
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_REGION: ${{ secrets.AWS_REGION }}
          S3_BUCKET: ${{ secrets.S3_BUCKET }}
        run: |
          # 备份数据库
          pg_dump $DATABASE_URL > backup.sql

          # 压缩备份文件
          gzip backup.sql

          # 上传到S3
          aws s3 cp backup.sql.gz s3://$S3_BUCKET/backups/$(date +%Y%m%d_%H%M%S).sql.gz
```

### 2. 部署回滚

```bash
# 查看部署历史
vercel ls my-app

# 回滚到特定部署
vercel promote https://my-app-xyz.vercel.app

# 回滚到上一个版本
vercel rollback my-app

# 创建恢复点
vercel alias set my-app my-app-stable
```

## 最佳实践

### 1. 部署清单

```markdown
## 部署前检查清单

- [ ] 所有测试通过
- [ ] 环境变量配置正确
- [ ] 数据库迁移执行
- [ ] 静态资源优化
- [ ] 缓存策略配置
- [ ] 安全设置验证
- [ ] 性能指标检查
- [ ] 监控配置完成
```

### 2. 性能优化清单

```markdown
## 性能优化检查清单

### 代码优化
- [ ] 使用动态导入
- [ ] 图片优化配置
- [ ] 字体优化
- [ ] 代码分割
- [ ] 懒加载实现

### 网络优化
- [ ] CDN配置
- [ ] 缓存策略
- [ ] 压缩启用
- [ ] 预连接配置
- [ ] 预加载关键资源

### 服务器优化
- [ ] 边缘函数使用
- [ ] Serverless优化
- [ ] 数据库索引
- [ ] 查询优化
- [ ] 缓存实现
```

### 3. 安全检查清单

```markdown
## 安全检查清单

### 环境安全
- [ ] 环境变量加密
- [ ] 敏感信息保护
- [ ] 访问权限控制
- [ ] API密钥管理
- [ ] 数据库安全

### 应用安全
- [ ] 输入验证
- [ ] XSS防护
- [ ] CSRF保护
- [ ] SQL注入防护
- [ ] 认证授权

### 网络安全
- [ ] HTTPS配置
- [ ] 安全头部
- [ ] CORS配置
- [ ] 速率限制
- [ ] 防火墙配置
```

## 故障排除

### 1. 常见问题解决

```bash
# 构建失败
npm run build
# 检查TypeScript错误
npm run type-check
# 检查ESLint错误
npm run lint

# 部署失败
vercel logs --help
vercel logs my-app

# 性能问题
npx lighthouse https://my-app.vercel.app

# 内存泄漏
node --inspect node_modules/.bin/next dev
```

### 2. 调试工具

```typescript
// app/debug/route.ts
import { NextResponse } from "next/server"

export async function GET() {
  const debugInfo = {
    environment: process.env.NODE_ENV,
    version: process.env.npm_package_version,
    timestamp: new Date().toISOString(),
    memoryUsage: process.memoryUsage(),
    uptime: process.uptime(),
  }

  return NextResponse.json(debugInfo)
}
```

## 总结

通过本指南，我们学习了如何在Vercel上部署Next.js应用的各个方面：

### 核心概念
- Vercel平台的特点和优势
- 零配置部署的理念
- 现代云部署的实践

### 实践技能
- 项目配置和优化
- 部署流程自动化
- 性能优化策略
- 监控和错误处理

### 高级主题
- 边缘计算应用
- 多环境管理
- 安全配置
- 备份和恢复

### 从PHP开发者角度
- 从传统服务器部署到云部署的转变
- 现代部署工具的优势
- DevOps实践的改进

掌握Vercel部署技能，将帮助您更加高效地部署和管理Next.js应用，享受现代云平台带来的便利和优势。Vercel不仅是一个部署平台，更是现代前端开发理念的体现。