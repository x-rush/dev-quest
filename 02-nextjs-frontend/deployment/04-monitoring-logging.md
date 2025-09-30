# 监控和日志管理指南 (Monitoring & Logging Guide)

> **PHP开发者视角**: 从传统日志文件到现代监控体系的转变，了解如何构建完整的Next.js应用监控和日志系统。

## 监控和日志基础

### 为什么需要监控和日志

1. **问题发现**: 及时发现线上问题和性能瓶颈
2. **用户体验**: 监控应用性能，确保用户体验
3. **业务分析**: 了解用户行为和业务指标
4. **容量规划**: 基于数据进行资源规划
5. **故障排查**: 快速定位和解决问题

### 监控体系架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   应用监控      │    │   基础设施监控    │    │   业务监控      │
│  • 性能指标      │    │  • 服务器资源     │    │  • 用户活跃度    │
│  • 错误追踪      │    │  • 数据库状态     │    │  • 转化率        │
│  • 用户体验      │    │  • 网络状态       │    │  • 收入数据      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   日志系统       │
                    │  • 结构化日志     │
                    │  • 日志聚合       │
                    │  • 日志分析       │
                    └─────────────────┘
```

## 应用性能监控

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
    <html lang="zh-CN">
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
  const handleSignup = async () => {
    try {
      await signupUser()
      track("user_signup", {
        plan: "premium",
        source: "homepage",
      })
    } catch (error) {
      track("signup_failed", {
        error: error.message,
      })
    }
  }

  return <button onClick={handleSignup}>注册</button>
}

// 页面视图跟踪
import { usePathname } from "next/navigation"
import { useEffect } from "react"

export function usePageView() {
  const pathname = usePathname()

  useEffect(() => {
    track("page_view", {
      path: pathname,
    })
  }, [pathname])
}
```

### 2. 自定义性能监控

```typescript
// lib/monitoring.ts
interface PerformanceMetrics {
  fcp: number // First Contentful Paint
  lcp: number // Largest Contentful Paint
  fid: number // First Input Delay
  cls: number // Cumulative Layout Shift
  ttfb: number // Time to First Byte
}

export class PerformanceMonitor {
  private metrics: Partial<PerformanceMetrics> = {}

  constructor() {
    this.init()
  }

  private init() {
    if (typeof window !== "undefined") {
      this.measureFCP()
      this.measureLCP()
      this.measureFID()
      this.measureCLS()
      this.measureTTFB()
    }
  }

  private measureFCP() {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries()
      const fcp = entries[0].startTime
      this.metrics.fcp = fcp
      this.sendMetrics("fcp", fcp)
    })

    observer.observe({ entryTypes: ["paint"] })
  }

  private measureLCP() {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries()
      const lcp = entries[entries.length - 1].startTime
      this.metrics.lcp = lcp
      this.sendMetrics("lcp", lcp)
    })

    observer.observe({ entryTypes: ["largest-contentful-paint"] })
  }

  private measureFID() {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries()
      const fid = entries[0].processingStart - entries[0].startTime
      this.metrics.fid = fid
      this.sendMetrics("fid", fid)
    })

    observer.observe({ entryTypes: ["first-input"] })
  }

  private measureCLS() {
    let clsValue = 0
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (!(entry as any).hadRecentInput) {
          clsValue += (entry as any).value
        }
      }
      this.metrics.cls = clsValue
      this.sendMetrics("cls", clsValue)
    })

    observer.observe({ entryTypes: ["layout-shift"] })
  }

  private measureTTFB() {
    const navigation = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming
    const ttfb = navigation.responseStart - navigation.requestStart
    this.metrics.ttfb = ttfb
    this.sendMetrics("ttfb", ttfb)
  }

  private sendMetrics(name: string, value: number) {
    // 发送到分析服务
    if (typeof window !== "undefined") {
      fetch("/api/analytics", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          value,
          timestamp: Date.now(),
          url: window.location.href,
        }),
      })
    }
  }

  getMetrics(): PerformanceMetrics {
    return this.metrics as PerformanceMetrics
  }
}

// 使用监控器
export const performanceMonitor = new PerformanceMonitor()
```

### 3. Web Vitals集成

```typescript
// app/layout.tsx
"use client"

import { useEffect } from "react"
import { getCLS, getFID, getFCP, getLCP, getTTFB } from "web-vitals"

export function WebVitals() {
  useEffect(() => {
    const sendToAnalytics = (metric: any) => {
      // 发送到分析服务
      fetch("/api/vitals", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(metric),
      })
    }

    getCLS(sendToAnalytics)
    getFID(sendToAnalytics)
    getFCP(sendToAnalytics)
    getLCP(sendToAnalytics)
    getTTFB(sendToAnalytics)
  }, [])

  return null
}
```

## 错误监控

### 1. Sentry集成

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
import { BrowserTracing } from "@sentry/tracing"

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  integrations: [
    new BrowserTracing(),
    new Sentry.Replay({
      maskAllText: false,
      blockAllMedia: false,
    }),
  ],
  tracesSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
})

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html>
      <body>
        {children}
      </body>
    </html>
  )
}

// 错误边界组件
"use client"

import * as Sentry from "@sentry/react"
import { useEffect } from "react"

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.Component<{ error: Error; reset: () => void }>
}

export function ErrorBoundary({ children, fallback: FallbackComponent }: ErrorBoundaryProps) {
  return (
    <Sentry.ErrorBoundary fallback={FallbackComponent}>
      {children}
    </Sentry.ErrorBoundary>
  )
}

function FallbackComponent({ error, reset }: { error: Error; reset: () => void }) {
  useEffect(() => {
    // 记录错误到控制台
    console.error("Error caught by ErrorBoundary:", error)
  }, [error])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-4">出错了！</h2>
        <p className="text-gray-600 mb-4">应用遇到了一个错误，我们已经记录了这个问题。</p>
        <button
          onClick={reset}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          重试
        </button>
      </div>
    </div>
  )
}

// 全局错误处理
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

### 2. 自定义错误监控

```typescript
// lib/error-monitoring.ts
interface ErrorEvent {
  message: string
  stack?: string
  type: string
  timestamp: number
  userAgent?: string
  url?: string
  userId?: string
  context?: Record<string, any>
}

class ErrorMonitor {
  private events: ErrorEvent[] = []
  private maxEvents = 100

  track(error: Error, context?: Record<string, any>) {
    const errorEvent: ErrorEvent = {
      message: error.message,
      stack: error.stack,
      type: error.name,
      timestamp: Date.now(),
      userAgent: typeof navigator !== "undefined" ? navigator.userAgent : undefined,
      url: typeof window !== "undefined" ? window.location.href : undefined,
      context,
    }

    this.events.push(errorEvent)

    if (this.events.length > this.maxEvents) {
      this.events.shift()
    }

    // 发送到监控服务
    this.sendToService(errorEvent)
  }

  trackAPIError(error: any, requestInfo: any) {
    this.track(new Error(`API Error: ${error.message}`), {
      type: "api",
      url: requestInfo.url,
      method: requestInfo.method,
      status: error.status,
      response: error.data,
    })
  }

  trackUIError(error: Error, componentStack?: string) {
    this.track(error, {
      type: "ui",
      componentStack,
    })
  }

  private async sendToService(event: ErrorEvent) {
    try {
      await fetch("/api/errors", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(event),
      })
    } catch (err) {
      console.error("Failed to send error to monitoring service:", err)
    }
  }

  getRecentErrors(): ErrorEvent[] {
    return [...this.events]
  }

  clear() {
    this.events = []
  }
}

export const errorMonitor = new ErrorMonitor()

// 全局错误处理器
if (typeof window !== "undefined") {
  window.addEventListener("error", (event) => {
    errorMonitor.track(event.error)
  })

  window.addEventListener("unhandledrejection", (event) => {
    errorMonitor.track(new Error(event.reason))
  })
}
```

## 日志管理

### 1. 结构化日志

```typescript
// lib/logger.ts
interface LogEntry {
  level: "debug" | "info" | "warn" | "error"
  message: string
  timestamp: string
  context?: Record<string, any>
  userId?: string
  requestId?: string
}

class Logger {
  private context: Record<string, any> = {}

  withContext(context: Record<string, any>): Logger {
    const logger = new Logger()
    logger.context = { ...this.context, ...context }
    return logger
  }

  private createLogEntry(level: LogEntry["level"], message: string, context?: Record<string, any>): LogEntry {
    return {
      level,
      message,
      timestamp: new Date().toISOString(),
      context: { ...this.context, ...context },
      userId: this.context.userId,
      requestId: this.context.requestId,
    }
  }

  private sendLog(entry: LogEntry) {
    // 发送到日志服务
    if (typeof window !== "undefined") {
      // 客户端日志
      if (entry.level === "error") {
        console.error(entry)
      } else {
        console.log(entry)
      }

      // 发送到服务器
      fetch("/api/logs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(entry),
      }).catch(err => {
        console.error("Failed to send log:", err)
      })
    } else {
      // 服务器端日志
      console.log(JSON.stringify(entry))
    }
  }

  debug(message: string, context?: Record<string, any>) {
    const entry = this.createLogEntry("debug", message, context)
    this.sendLog(entry)
  }

  info(message: string, context?: Record<string, any>) {
    const entry = this.createLogEntry("info", message, context)
    this.sendLog(entry)
  }

  warn(message: string, context?: Record<string, any>) {
    const entry = this.createLogEntry("warn", message, context)
    this.sendLog(entry)
  }

  error(message: string, context?: Record<string, any>) {
    const entry = this.createLogEntry("error", message, context)
    this.sendLog(entry)
  }

  // 性能日志
  time(label: string): () => void {
    const start = Date.now()
    this.debug(`Timer started: ${label}`)

    return () => {
      const duration = Date.now() - start
      this.info(`Timer ended: ${label}`, { duration })
    }
  }
}

export const logger = new Logger()

// 使用示例
logger.info("用户登录", { userId: "123", email: "user@example.com" })

const timer = logger.time("API调用")
// ... 执行一些操作
timer()

// 带上下文的日志
const userLogger = logger.withContext({ userId: "123" })
userLogger.info("用户更新了个人资料")
```

### 2. 日志聚合和分析

```typescript
// app/api/logs/route.ts
import { NextRequest, NextResponse } from "next/server"
import { createClient } from "@supabase/supabase-js"

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_KEY!
)

export async function POST(request: NextRequest) {
  try {
    const logEntry = await request.json()

    // 存储到数据库
    const { data, error } = await supabase
      .from("logs")
      .insert([{
        level: logEntry.level,
        message: logEntry.message,
        timestamp: logEntry.timestamp,
        context: logEntry.context,
        user_id: logEntry.userId,
        request_id: logEntry.requestId,
        user_agent: logEntry.userAgent,
        url: logEntry.url,
      }])
      .select()

    if (error) {
      console.error("Failed to store log:", error)
    }

    // 实时分析
    await analyzeLog(logEntry)

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("Failed to process log:", error)
    return NextResponse.json({ error: "Failed to process log" }, { status: 500 })
  }
}

async function analyzeLog(logEntry: any) {
  // 错误率分析
  if (logEntry.level === "error") {
    const { data } = await supabase
      .from("error_metrics")
      .select("count")
      .eq("date", new Date().toISOString().split("T")[0])
      .single()

    if (!data) {
      await supabase.from("error_metrics").insert([{
        date: new Date().toISOString().split("T")[0],
        count: 1,
      }])
    } else {
      await supabase
        .from("error_metrics")
        .update({ count: data.count + 1 })
        .eq("date", new Date().toISOString().split("T")[0])
    }
  }

  // 性能分析
  if (logEntry.context?.duration) {
    await supabase.from("performance_metrics").insert([{
      timestamp: logEntry.timestamp,
      metric_name: logEntry.message,
      value: logEntry.context.duration,
      user_id: logEntry.user_id,
    }])
  }
}
```

### 3. 日志查询和分析

```typescript
// lib/log-analytics.ts
import { createClient } from "@supabase/supabase-js"

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_KEY!
)

export class LogAnalytics {
  async getErrorRate(startDate: string, endDate: string) {
    const { data, error } = await supabase
      .from("logs")
      .select("*")
      .eq("level", "error")
      .gte("timestamp", startDate)
      .lte("timestamp", endDate)

    if (error) throw error

    const totalLogs = await this.getTotalLogs(startDate, endDate)
    const errorRate = (data.length / totalLogs) * 100

    return {
      errorCount: data.length,
      totalLogs,
      errorRate: Math.round(errorRate * 100) / 100,
    }
  }

  async getPerformanceMetrics(metricName: string, startDate: string, endDate: string) {
    const { data, error } = await supabase
      .from("performance_metrics")
      .select("*")
      .eq("metric_name", metricName)
      .gte("timestamp", startDate)
      .lte("timestamp", endDate)
      .order("timestamp", { ascending: true })

    if (error) throw error

    const values = data.map(d => d.value)
    const avg = values.reduce((a, b) => a + b, 0) / values.length
    const max = Math.max(...values)
    const min = Math.min(...values)

    return {
      average: Math.round(avg * 100) / 100,
      max,
      min,
      count: values.length,
      data,
    }
  }

  async getUserActivity(userId: string, startDate: string, endDate: string) {
    const { data, error } = await supabase
      .from("logs")
      .select("*")
      .eq("user_id", userId)
      .gte("timestamp", startDate)
      .lte("timestamp", endDate)
      .order("timestamp", { ascending: false })

    if (error) throw error

    return data
  }

  async getSlowQueries(threshold: number = 1000, limit: number = 10) {
    const { data, error } = await supabase
      .from("performance_metrics")
      .select("*")
      .gte("value", threshold)
      .order("value", { ascending: false })
      .limit(limit)

    if (error) throw error

    return data
  }

  async searchLogs(query: string, startDate?: string, endDate?: string) {
    let queryBuilder = supabase
      .from("logs")
      .select("*")
      .textSearch("message", query, { type: "websearch" })

    if (startDate) {
      queryBuilder = queryBuilder.gte("timestamp", startDate)
    }

    if (endDate) {
      queryBuilder = queryBuilder.lte("timestamp", endDate)
    }

    const { data, error } = await queryBuilder
      .order("timestamp", { ascending: false })
      .limit(100)

    if (error) throw error

    return data
  }

  private async getTotalLogs(startDate: string, endDate: string) {
    const { count, error } = await supabase
      .from("logs")
      .select("*", { count: "exact", head: true })
      .gte("timestamp", startDate)
      .lte("timestamp", endDate)

    if (error) throw error

    return count || 0
  }
}

export const logAnalytics = new LogAnalytics()
```

## 基础设施监控

### 1. 服务器监控

```typescript
// lib/server-monitoring.ts
interface ServerMetrics {
  cpu: {
    usage: number
    cores: number
  }
  memory: {
    total: number
    used: number
    free: number
    usage: number
  }
  disk: {
    total: number
    used: number
    free: number
    usage: number
  }
  network: {
    bytesIn: number
    bytesOut: number
    packetsIn: number
    packetsOut: number
  }
  uptime: number
  loadAverage: number[]
}

export class ServerMonitor {
  private metrics: ServerMetrics | null = null

  async collectMetrics(): Promise<ServerMetrics> {
    if (typeof window !== "undefined") {
      // 客户端，获取基本信息
      return {
        cpu: { usage: 0, cores: navigator.hardwareConcurrency || 4 },
        memory: {
          total: 0,
          used: 0,
          free: 0,
          usage: 0,
        },
        disk: { total: 0, used: 0, free: 0, usage: 0 },
        network: { bytesIn: 0, bytesOut: 0, packetsIn: 0, packetsOut: 0 },
        uptime: 0,
        loadAverage: [0, 0, 0],
      }
    }

    // 服务器端，收集详细指标
    const metrics: ServerMetrics = {
      cpu: await this.getCPUInfo(),
      memory: await this.getMemoryInfo(),
      disk: await this.getDiskInfo(),
      network: await this.getNetworkInfo(),
      uptime: process.uptime(),
      loadAverage: this.getLoadAverage(),
    }

    this.metrics = metrics
    return metrics
  }

  private async getCPUInfo() {
    const usage = Math.random() * 100 // 模拟CPU使用率
    return {
      usage: Math.round(usage * 100) / 100,
      cores: require("os").cpus().length,
    }
  }

  private async getMemoryInfo() {
    const total = require("os").totalmem()
    const free = require("os").freemem()
    const used = total - free

    return {
      total,
      used,
      free,
      usage: Math.round((used / total) * 10000) / 100,
    }
  }

  private async getDiskInfo() {
    // 简化的磁盘信息
    const total = 100 * 1024 * 1024 * 1024 // 100GB
    const used = Math.random() * total
    const free = total - used

    return {
      total,
      used: Math.round(used),
      free: Math.round(free),
      usage: Math.round((used / total) * 10000) / 100,
    }
  }

  private async getNetworkInfo() {
    // 简化的网络信息
    return {
      bytesIn: Math.floor(Math.random() * 1000000),
      bytesOut: Math.floor(Math.random() * 1000000),
      packetsIn: Math.floor(Math.random() * 10000),
      packetsOut: Math.floor(Math.random() * 10000),
    }
  }

  private getLoadAverage(): number[] {
    if (typeof window !== "undefined") {
      return [0, 0, 0]
    }

    try {
      return require("os").loadavg()
    } catch {
      return [0, 0, 0]
    }
  }

  async getHealthStatus() {
    const metrics = await this.collectMetrics()

    const status = {
      healthy: true,
      checks: {
        cpu: metrics.cpu.usage < 80,
        memory: metrics.memory.usage < 85,
        disk: metrics.disk.usage < 90,
      },
      metrics,
    }

    status.healthy = Object.values(status.checks).every(check => check)

    return status
  }
}

export const serverMonitor = new ServerMonitor()

// 健康检查端点
// app/api/health/route.ts
import { serverMonitor } from "@/lib/server-monitoring"

export async function GET() {
  const healthStatus = await serverMonitor.getHealthStatus()

  return NextResponse.json(healthStatus, {
    status: healthStatus.healthy ? 200 : 503,
  })
}
```

### 2. 数据库监控

```typescript
// lib/database-monitoring.ts
import { PrismaClient } from "@prisma/client"

export class DatabaseMonitor {
  private prisma: PrismaClient

  constructor() {
    this.prisma = new PrismaClient()
  }

  async getConnectionMetrics() {
    try {
      const result = await this.prisma.$queryRaw`
        SELECT
          count(*) as active_connections,
          state,
          count(*) FILTER (WHERE state = 'active') as active_connections,
          count(*) FILTER (WHERE state = 'idle') as idle_connections
        FROM pg_stat_activity
        WHERE datname = current_database()
      ` as any[]

      return result[0]
    } catch (error) {
      console.error("Failed to get connection metrics:", error)
      return null
    }
  }

  async getPerformanceMetrics() {
    try {
      const result = await this.prisma.$queryRaw`
        SELECT
          schemaname,
          tablename,
          seq_scan,
          seq_tup_read,
          idx_scan,
          idx_tup_fetch,
          n_tup_ins,
          n_tup_upd,
          n_tup_del,
          n_live_tup,
          n_dead_tup
        FROM pg_stat_user_tables
        ORDER BY n_live_tup DESC
        LIMIT 10
      ` as any[]

      return result
    } catch (error) {
      console.error("Failed to get performance metrics:", error)
      return []
    }
  }

  async getSlowQueries(threshold: number = 1000) {
    try {
      const result = await this.prisma.$queryRaw`
        SELECT
          query,
          calls,
          total_time,
          mean_time,
          min_time,
          max_time,
          rows
        FROM pg_stat_statements
        WHERE mean_time > ${threshold}
        ORDER BY mean_time DESC
        LIMIT 10
      ` as any[]

      return result
    } catch (error) {
      console.error("Failed to get slow queries:", error)
      return []
    }
  }

  async getSizeMetrics() {
    try {
      const result = await this.prisma.$queryRaw`
        SELECT
          schemaname,
          tablename,
          pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
          pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
      ` as any[]

      return result
    } catch (error) {
      console.error("Failed to get size metrics:", error)
      return []
    }
  }

  async getLockInformation() {
    try {
      const result = await this.prisma.$queryRaw`
        SELECT
          locktype,
          relation::regclass as table_name,
          mode,
          pid,
          granted,
          query
        FROM pg_locks
        LEFT JOIN pg_stat_activity ON pg_locks.pid = pg_stat_activity.pid
        WHERE relation IS NOT NULL
        AND pid <> pg_backend_pid()
        ORDER BY pid
      ` as any[]

      return result
    } catch (error) {
      console.error("Failed to get lock information:", error)
      return []
    }
  }

  async getHealthStatus() {
    try {
      // 测试数据库连接
      await this.prisma.$queryRaw`SELECT 1`

      const connectionMetrics = await this.getConnectionMetrics()
      const slowQueries = await this.getSlowQueries()

      const status = {
        healthy: true,
        checks: {
          connection: true,
          connections: connectionMetrics?.active_connections < 100,
          slowQueries: slowQueries.length < 5,
        },
        metrics: {
          connections: connectionMetrics,
          slowQueriesCount: slowQueries.length,
        },
      }

      status.healthy = Object.values(status.checks).every(check => check)

      return status
    } catch (error) {
      return {
        healthy: false,
        checks: {
          connection: false,
          connections: false,
          slowQueries: false,
        },
        error: error.message,
      }
    }
  }

  async close() {
    await this.prisma.$disconnect()
  }
}

export const databaseMonitor = new DatabaseMonitor()
```

## 告警系统

### 1. 告警规则配置

```typescript
// lib/alerting.ts
interface AlertRule {
  id: string
  name: string
  condition: (metrics: any) => boolean
  severity: "low" | "medium" | "high" | "critical"
  channels: string[]
  message: string
  enabled: boolean
}

export class AlertingSystem {
  private rules: AlertRule[] = []
  private activeAlerts: Map<string, any> = new Map()

  constructor() {
    this.initializeRules()
    this.startMonitoring()
  }

  private initializeRules() {
    this.rules = [
      {
        id: "high-error-rate",
        name: "高错误率",
        condition: (metrics) => metrics.errorRate > 5,
        severity: "high",
        channels: ["slack", "email"],
        message: "错误率超过5%，当前为: {{errorRate}}%",
        enabled: true,
      },
      {
        id: "high-response-time",
        name: "响应时间过长",
        condition: (metrics) => metrics.avgResponseTime > 2000,
        severity: "medium",
        channels: ["slack"],
        message: "平均响应时间过长，当前为: {{avgResponseTime}}ms",
        enabled: true,
      },
      {
        id: "low-available-memory",
        name: "内存不足",
        condition: (metrics) => metrics.memoryUsage > 85,
        severity: "high",
        channels: ["slack", "email"],
        message: "内存使用率过高，当前为: {{memoryUsage}}%",
        enabled: true,
      },
      {
        id: "high-cpu-usage",
        name: "CPU使用率过高",
        condition: (metrics) => metrics.cpuUsage > 80,
        severity: "medium",
        channels: ["slack"],
        message: "CPU使用率过高，当前为: {{cpuUsage}}%",
        enabled: true,
      },
      {
        id: "database-connections",
        name: "数据库连接过多",
        condition: (metrics) => metrics.dbConnections > 50,
        severity: "critical",
        channels: ["slack", "email", "sms"],
        message: "数据库连接数过多，当前为: {{dbConnections}}",
        enabled: true,
      },
    ]
  }

  private startMonitoring() {
    setInterval(async () => {
      await this.checkAlerts()
    }, 60000) // 每分钟检查一次
  }

  private async checkAlerts() {
    const metrics = await this.collectMetrics()

    for (const rule of this.rules) {
      if (!rule.enabled) continue

      try {
        const shouldAlert = rule.condition(metrics)

        if (shouldAlert) {
          await this.triggerAlert(rule, metrics)
        } else {
          await this.resolveAlert(rule.id)
        }
      } catch (error) {
        console.error(`Failed to check alert rule ${rule.id}:`, error)
      }
    }
  }

  private async collectMetrics() {
    try {
      const [serverMetrics, appMetrics, dbMetrics] = await Promise.all([
        serverMonitor.collectMetrics(),
        this.getAppMetrics(),
        databaseMonitor.getConnectionMetrics(),
      ])

      return {
        ...serverMetrics,
        ...appMetrics,
        dbConnections: dbMetrics?.active_connections || 0,
      }
    } catch (error) {
      console.error("Failed to collect metrics:", error)
      return {}
    }
  }

  private async getAppMetrics() {
    // 收集应用特定指标
    return {
      errorRate: Math.random() * 10, // 模拟错误率
      avgResponseTime: Math.random() * 3000, // 模拟响应时间
    }
  }

  private async triggerAlert(rule: AlertRule, metrics: any) {
    const alertKey = `${rule.id}-${Date.now()}`

    // 避免重复告警
    if (this.activeAlerts.has(rule.id)) {
      return
    }

    const message = this.formatMessage(rule.message, metrics)

    const alert = {
      id: alertKey,
      ruleId: rule.id,
      message,
      severity: rule.severity,
      timestamp: new Date().toISOString(),
      metrics,
    }

    this.activeAlerts.set(rule.id, alert)

    // 发送告警
    for (const channel of rule.channels) {
      await this.sendNotification(channel, alert)
    }
  }

  private async resolveAlert(ruleId: string) {
    if (this.activeAlerts.has(ruleId)) {
      const alert = this.activeAlerts.get(ruleId)

      // 发送解决通知
      await this.sendNotification("slack", {
        ...alert,
        status: "resolved",
        message: `🟢 ${alert.message} (已解决)`,
        resolvedAt: new Date().toISOString(),
      })

      this.activeAlerts.delete(ruleId)
    }
  }

  private formatMessage(template: string, metrics: any): string {
    return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
      const value = metrics[key]
      return typeof value === "number" ? value.toFixed(2) : value
    })
  }

  private async sendNotification(channel: string, alert: any) {
    try {
      switch (channel) {
        case "slack":
          await this.sendSlackNotification(alert)
          break
        case "email":
          await this.sendEmailNotification(alert)
          break
        case "sms":
          await this.sendSMSNotification(alert)
          break
      }
    } catch (error) {
      console.error(`Failed to send ${channel} notification:`, error)
    }
  }

  private async sendSlackNotification(alert: any) {
    const webhookUrl = process.env.SLACK_WEBHOOK_URL

    if (!webhookUrl) return

    const payload = {
      text: alert.message,
      attachments: [
        {
          color: this.getSeverityColor(alert.severity),
          fields: [
            {
              title: "Severity",
              value: alert.severity.toUpperCase(),
              short: true,
            },
            {
              title: "Time",
              value: new Date(alert.timestamp).toLocaleString(),
              short: true,
            },
          ],
        },
      ],
    }

    await fetch(webhookUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    })
  }

  private async sendEmailNotification(alert: any) {
    // 实现邮件发送逻辑
    console.log("Email notification:", alert)
  }

  private async sendSMSNotification(alert: any) {
    // 实现短信发送逻辑
    console.log("SMS notification:", alert)
  }

  private getSeverityColor(severity: string): string {
    switch (severity) {
      case "low": return "#36a64f"
      case "medium": return "#ff9500"
      case "high": return "#ff0000"
      case "critical": return "#8b0000"
      default: return "#36a64f"
    }
  }

  getActiveAlerts(): any[] {
    return Array.from(this.activeAlerts.values())
  }

  addRule(rule: AlertRule) {
    this.rules.push(rule)
  }

  removeRule(ruleId: string) {
    this.rules = this.rules.filter(rule => rule.id !== ruleId)
  }

  toggleRule(ruleId: string, enabled: boolean) {
    const rule = this.rules.find(r => r.id === ruleId)
    if (rule) {
      rule.enabled = enabled
    }
  }
}

export const alertingSystem = new AlertingSystem()
```

## 监控仪表板

### 1. 实时监控仪表板

```typescript
// app/dashboard/monitoring/page.tsx
"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts"

interface MonitoringData {
  server: {
    cpu: number
    memory: number
    disk: number
  }
  application: {
    errorRate: number
    responseTime: number
    requests: number
  }
  database: {
    connections: number
    slowQueries: number
  }
  alerts: any[]
}

export default function MonitoringDashboard() {
  const [data, setData] = useState<MonitoringData | null>(null)
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState("1h")

  useEffect(() => {
    fetchMonitoringData()
    const interval = setInterval(fetchMonitoringData, 30000) // 30秒刷新

    return () => clearInterval(interval)
  }, [timeRange])

  const fetchMonitoringData = async () => {
    try {
      const response = await fetch(`/api/monitoring?range=${timeRange}`)
      const result = await response.json()
      setData(result)
    } catch (error) {
      console.error("Failed to fetch monitoring data:", error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64">加载中...</div>
  }

  if (!data) {
    return <div className="flex items-center justify-center h-64">无法加载数据</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">系统监控</h1>
        <div className="flex gap-2">
          {["5m", "1h", "24h", "7d"].map((range) => (
            <Button
              key={range}
              variant={timeRange === range ? "default" : "outline"}
              size="sm"
              onClick={() => setTimeRange(range)}
            >
              {range}
            </Button>
          ))}
        </div>
      </div>

      {/* 告警信息 */}
      {data.alerts.length > 0 && (
        <div className="space-y-2">
          {data.alerts.map((alert) => (
            <Alert key={alert.id} className="border-red-200">
              <AlertDescription>
                <div className="flex items-center justify-between">
                  <span>{alert.message}</span>
                  <Badge variant={alert.severity === "critical" ? "destructive" : "secondary"}>
                    {alert.severity}
                  </Badge>
                </div>
              </AlertDescription>
            </Alert>
          ))}
        </div>
      )}

      {/* 关键指标 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">CPU 使用率</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.server.cpu}%</div>
            <p className="text-xs text-muted-foreground">
              {data.server.cpu > 80 ? "🔴 高负载" : "🟢 正常"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">内存使用率</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.server.memory}%</div>
            <p className="text-xs text-muted-foreground">
              {data.server.memory > 85 ? "🔴 内存不足" : "🟢 正常"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">错误率</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.application.errorRate}%</div>
            <p className="text-xs text-muted-foreground">
              {data.application.errorRate > 5 ? "🔴 错误率过高" : "🟢 正常"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">响应时间</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.application.responseTime}ms</div>
            <p className="text-xs text-muted-foreground">
              {data.application.responseTime > 2000 ? "🔴 响应过慢" : "🟢 正常"}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 图表 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>性能趋势</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={generatePerformanceData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="cpu" stroke="#8884d8" name="CPU %" />
                <Line type="monotone" dataKey="memory" stroke="#82ca9d" name="Memory %" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>请求量趋势</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={generateRequestData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="requests" stroke="#8884d8" fill="#8884d8" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

// 生成示例数据
function generatePerformanceData() {
  return Array.from({ length: 24 }, (_, i) => ({
    time: `${i}:00`,
    cpu: Math.random() * 100,
    memory: Math.random() * 100,
  }))
}

function generateRequestData() {
  return Array.from({ length: 24 }, (_, i) => ({
    time: `${i}:00`,
    requests: Math.floor(Math.random() * 1000),
  }))
}
```

## 总结

通过本指南，我们学习了Next.js应用的监控和日志管理：

### 核心概念
- 监控体系的重要性
- 应用性能监控的指标
- 错误监控和追踪
- 日志管理的最佳实践

### 实践技能
- Vercel Analytics集成
- Sentry错误监控
- 自定义性能监控
- 结构化日志记录
- 告警系统配置

### 高级主题
- 基础设施监控
- 数据库监控
- 实时监控仪表板
- 日志分析和查询

### 从PHP开发者角度
- 从传统日志文件到现代监控体系的转变
- 前端监控的特殊考虑
- 全栈应用的监控策略

掌握监控和日志管理技能，将帮助您构建更加稳定、可靠的应用程序，及时发现和解决问题，为用户提供更好的体验。监控不仅是技术工具的使用，更是运维文化的体现。