# Next.js 16 监控与分析：从信号到可处理告警

> **文档简介**: 用错误、性能、可用性和业务事件建立最小可观测闭环，重点说明数据脱敏、release 关联、告警处理和演练边界；采集工具本身不等于监控已经有效。

> **目标读者**: 具备 Next.js 基础、准备为真实项目增加错误与性能信号的开发者。

> **前置知识**: Next.js 16基础、生产部署经验、基础监控概念、数据分析基础

> **预计时长**: 6-8小时

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `deployment` |
| **难度** | ⭐⭐⭐ (精通)|
| **标签** | `#monitoring` `#analytics` `#sentry` `#performance` `#error-tracking` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 🎯 学习目标

### 📊 最小可观测闭环
- 为一个关键用户任务关联 release、路由、错误、接口延迟与业务成功结果
- 对错误上下文和日志字段做脱敏，验证令牌、Cookie、正文和个人数据不被采集
- 定义能触发处理的指标、阈值、持续窗口、负责人和运行手册
- 在隔离环境演练错误、慢依赖和恢复，而不是仅检查仪表盘有数据

### 📈 事件与分析边界
- 为每个事件说明业务目的、触发时机、去重键、允许字段和保留期限
- 区分“按钮点击”“请求发送”“服务端成功”的事件语义，不能混合计算转化
- A/B 测试、同意管理、数据出境与保留规则由产品、法务和实际平台共同决定，本文不构成合规结论

### 🚀 运维最佳实践
先选一个用户任务建立监控链，例如下单失败能关联请求、后端异常与依赖耗时。基础设施资源帮助判断容量，业务成功率帮助判断用户影响，二者一起看才能缩小原因范围。

告警应说明异常持续多久、影响什么及下一步行动，避免每次短暂波动都通知。容量预测用代表性负载和增长假设验证；恢复能力通过备份恢复与故障演练证明，而不是通过监控工具数量证明。

## 📖 概述

监控的价值在于发现并缩小一个影响用户的问题。先从一个用户旅程、一个错误信号、一个性能信号和一个业务结果开始，再根据真实决策扩展采集范围；堆叠 SDK 和图表不会自动提高稳定性或合规性。

## 🏗️ 监控架构概览

### 监控层次体系

```
┌─────────────────────────────────────────────────────────┐
│                   业务监控层                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │  转化率分析   │ │  用户行为     │ │  收入指标     │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                   应用监控层                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │  错误追踪     │ │  性能监控     │ │  API监控      │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                   基础设施监控层                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │  服务器监控   │ │  网络监控     │ │  数据库监控    │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
└─────────────────────────────────────────────────────────┘
```

## 🔍 错误监控与追踪

### Sentry 集成配置

#### 🛠️ 基础配置
```bash
# 安装 Sentry
npm install @sentry/nextjs
```

```typescript
// sentry.client.config.ts
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
  debug: false,
  replaysOnErrorSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  integrations: [
    Sentry.replayIntegration({
      maskAllText: true,
      blockAllMedia: true,
    }),
    new Sentry.BrowserTracing({
      routingInstrumentation: Sentry.reactRouterV6Instrumentation(
        React.useEffect,
        useLocation,
        useNavigationType,
        createRoutesFromChildren,
        matchRoutes
      ),
    }),
  ],
  beforeSend(event) {
    // 过滤敏感信息
    if (event.exception) {
      const error = event.exception.values?.[0]
      if (error?.value?.includes('token')) {
        return null
      }
    }
    return event
  },
})

```

```typescript
// sentry.server.config.ts
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
  debug: false,
  integrations: [
    // @sentry/nextjs v8+：HTTP 与框架追踪已默认启用，无需手动注册 Integrations.Http/Express
  ],
})
```

#### 📊 自定义错误追踪
```typescript
// lib/error-tracking.ts
import * as Sentry from '@sentry/nextjs'

export class ErrorTracking {
  // 追踪自定义错误
  static trackError(
    error: Error,
    context: Record<string, any> = {},
    level: Sentry.SeverityLevel = 'error'
  ) {
    Sentry.withScope((scope) => {
      scope.setLevel(level)
      scope.setContext('custom_context', context)
      scope.setTag('error_type', 'custom')

      Sentry.captureException(error, {
        tags: {
          component: context.component || 'unknown',
          action: context.action || 'unknown',
        },
        extra: {
          ...context,
          timestamp: new Date().toISOString(),
        },
      })
    })
  }

  // 追踪用户行为
  static trackUserAction(action: string, properties: Record<string, any>) {
    Sentry.addBreadcrumb({
      message: `User action: ${action}`,
      category: 'user',
      level: 'info',
      data: properties,
    })

    // 发送到自定义分析
    if (typeof window !== 'undefined') {
      window.gtag?.('event', action, properties)
    }
  }

  // 设置用户信息
  static setUser(user: { id: string; email?: string; username?: string }) {
    Sentry.setUser({
      id: user.id,
      email: user.email,
      username: user.username,
    })
  }

  // 清除用户信息
  static clearUser() {
    Sentry.setUser(null)
  }
}

// 使用示例
export function ComponentWithErrorHandling() {
  const handleClick = async () => {
    try {
      ErrorTracking.trackUserAction('button_click', {
        button_id: 'submit_form',
        page: '/dashboard'
      })

      await riskyOperation()

    } catch (error) {
      ErrorTracking.trackError(error as Error, {
        component: 'ComponentWithErrorHandling',
        action: 'handleClick',
        user_id: 'current_user_id',
      })
    }
  }
}
```

#### 🚨 智能告警配置
```typescript
// lib/alerting.ts
export interface AlertRule {
  id: string
  name: string
  condition: (events: Sentry.Event[]) => boolean
  severity: 'low' | 'medium' | 'high' | 'critical'
  cooldown: number // 冷却时间（秒）
  actions: AlertAction[]
}

export interface AlertAction {
  type: 'webhook' | 'email' | 'slack' | 'pagerduty'
  config: Record<string, any>
}

export class AlertManager {
  private rules: Map<string, AlertRule> = new Map()
  private lastAlerts: Map<string, number> = new Map()

  // 注册告警规则
  registerRule(rule: AlertRule) {
    this.rules.set(rule.id, rule)
  }

  // 处理新事件
  async processEvent(event: Sentry.Event) {
    const now = Date.now()

    for (const [ruleId, rule] of this.rules) {
      // 检查冷却时间
      const lastAlert = this.lastAlerts.get(ruleId)
      if (lastAlert && (now - lastAlert) < rule.cooldown * 1000) {
        continue
      }

      // 检查告警条件
      const recentEvents = await this.getRecentEvents(rule)
      if (rule.condition([event, ...recentEvents])) {
        await this.triggerAlert(rule, event)
        this.lastAlerts.set(ruleId, now)
      }
    }
  }

  // 触发告警
  private async triggerAlert(rule: AlertRule, event: Sentry.Event) {
    const payload = {
      rule: rule.name,
      severity: rule.severity,
      event: {
        id: event.event_id,
        message: event.message,
        timestamp: event.timestamp,
      },
    }

    for (const action of rule.actions) {
      try {
        await this.executeAction(action, payload)
      } catch (error) {
        console.error(`Failed to execute alert action:`, error)
      }
    }
  }

  // 执行告警动作
  private async executeAction(action: AlertAction, payload: any) {
    switch (action.type) {
      case 'webhook':
        await fetch(action.config.url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        })
        break

      case 'slack':
        await this.sendSlackAlert(action.config.webhook, payload)
        break

      case 'email':
        await this.sendEmailAlert(action.config, payload)
        break

      case 'pagerduty':
        await this.sendPagerDutyAlert(action.config, payload)
        break
    }
  }

  // 发送 Slack 告警
  private async sendSlackAlert(webhook: string, payload: any) {
    const message = {
      text: `🚨 Alert: ${payload.rule}`,
      attachments: [{
        color: this.getSeverityColor(payload.severity),
        fields: [
          { title: 'Severity', value: payload.severity, short: true },
          { title: 'Event ID', value: payload.event.id, short: true },
          { title: 'Message', value: payload.event.message, short: false },
          { title: 'Time', value: new Date(payload.event.timestamp).toLocaleString(), short: true },
        ],
      }],
    }

    await fetch(webhook, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(message),
    })
  }

  private getSeverityColor(severity: string): string {
    const colors = {
      low: 'good',
      medium: 'warning',
      high: 'danger',
      critical: '#ff0000',
    }
    return colors[severity as keyof typeof colors] || 'warning'
  }

  private async getRecentEvents(rule: AlertRule): Promise<Sentry.Event[]> {
    // 实现 Sentry API 调用获取最近事件
    return []
  }
}
```

## 📈 性能监控

### Web Vitals 追踪

#### 🎯 Core Web Vitals 配置
```tsx
// lib/web-vitals.ts
import { onCLS, onINP, onFCP, onLCP, onTTFB } from 'web-vitals'

export interface WebVitalsMetrics {
  CLS: number // Cumulative Layout Shift
  INP: number // Interaction to Next Paint
  FCP: number // First Contentful Paint
  LCP: number // Largest Contentful Paint
  TTFB: number // Time to First Byte
}

export class WebVitalsTracker {
  private static instance: WebVitalsTracker
  private metrics: Partial<WebVitalsMetrics> = {}

  static getInstance(): WebVitalsTracker {
    if (!WebVitalsTracker.instance) {
      WebVitalsTracker.instance = new WebVitalsTracker()
    }
    return WebVitalsTracker.instance
  }

  // 初始化追踪
  init() {
    onCLS(this.handleMetric.bind(this, 'CLS'))
    onINP(this.handleMetric.bind(this, 'INP'))
    onFCP(this.handleMetric.bind(this, 'FCP'))
    onLCP(this.handleMetric.bind(this, 'LCP'))
    onTTFB(this.handleMetric.bind(this, 'TTFB'))
  }

  // 处理指标数据
  private handleMetric(name: keyof WebVitalsMetrics, metric: any) {
    this.metrics[name] = metric.value

    // 发送到分析服务
    this.sendToAnalytics(name, metric)

    // 检查性能阈值
    this.checkThresholds(name, metric)
  }

  // 发送到分析服务
  private sendToAnalytics(name: string, metric: any) {
    // 发送到 Google Analytics
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', name, {
        value: Math.round(metric.value),
        metric_id: metric.id,
        metric_value: metric.value,
        metric_delta: metric.delta,
      })
    }

    // 发送到自定义分析
    fetch('/api/analytics/web-vitals', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name,
        value: metric.value,
        id: metric.id,
        url: window.location.href,
        userAgent: navigator.userAgent,
        timestamp: Date.now(),
      }),
    })
  }

  // 检查性能阈值
  private checkThresholds(name: keyof WebVitalsMetrics, metric: any) {
    const thresholds = {
      CLS: 0.1,
      INP: 200,
      FCP: 1800,
      LCP: 2500,
      TTFB: 800,
    }

    if (metric.value > thresholds[name]) {
      // 发送性能告警
      this.sendPerformanceAlert(name, metric.value, thresholds[name])
    }
  }

  // 发送性能告警
  private sendPerformanceAlert(name: string, value: number, threshold: number) {
    ErrorTracking.trackError(
      new Error(`Performance threshold exceeded for ${name}`),
      {
        metric_name: name,
        current_value: value,
        threshold,
        url: typeof window !== 'undefined' ? window.location.href : 'unknown',
        severity: value > threshold * 2 ? 'high' : 'medium',
      },
      'warning'
    )
  }

  // 获取当前指标
  getMetrics(): Partial<WebVitalsMetrics> {
    return { ...this.metrics }
  }
}

// app/layout.tsx
'use client'

import { useEffect } from 'react'
import { WebVitalsTracker } from '@/lib/web-vitals'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  useEffect(() => {
    const tracker = WebVitalsTracker.getInstance()
    tracker.init()
  }, [])

  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

#### 📊 自定义性能监控
```typescript
// lib/performance-monitor.ts
export interface PerformanceEntry {
  name: string
  startTime: number
  duration: number
  type: string
}

export class PerformanceMonitor {
  private static instance: PerformanceMonitor
  private observers: PerformanceObserver[] = []

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor()
    }
    return PerformanceMonitor.instance
  }

  // 监控资源加载
  observeResourceTiming() {
    if (typeof window === 'undefined') return

    const observer = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.entryType === 'resource') {
          this.analyzeResourceEntry(entry as PerformanceResourceTiming)
        }
      })
    })

    observer.observe({ entryTypes: ['resource'] })
    this.observers.push(observer)
  }

  // 监控长任务
  observeLongTasks() {
    if (typeof window === 'undefined') return

    const observer = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.entryType === 'longtask') {
          this.reportLongTask(entry)
        }
      })
    })

    observer.observe({ entryTypes: ['longtask'] })
    this.observers.push(observer)
  }

  // 分析资源加载
  private analyzeResourceEntry(entry: PerformanceResourceTiming) {
    const analysis = {
      name: entry.name,
      type: this.getResourceType(entry.name),
      duration: entry.duration,
      size: entry.transferSize || 0,
      cached: entry.transferSize === 0 && entry.decodedBodySize > 0,
      timing: {
        dns: entry.domainLookupEnd - entry.domainLookupStart,
        tcp: entry.connectEnd - entry.connectStart,
        ssl: entry.secureConnectionStart > 0 ? entry.connectEnd - entry.secureConnectionStart : 0,
        ttfb: entry.responseStart - entry.requestStart,
        download: entry.responseEnd - entry.responseStart,
      },
    }

    // 检查性能问题
    this.checkResourcePerformance(analysis)

    // 发送数据
    this.sendResourceData(analysis)
  }

  // 获取资源类型
  private getResourceType(url: string): string {
    if (url.match(/\.(js)$/)) return 'script'
    if (url.match(/\.(css)$/)) return 'stylesheet'
    if (url.match(/\.(png|jpg|jpeg|gif|webp|svg)$/)) return 'image'
    if (url.match(/\.(woff|woff2|ttf|eot)$/)) return 'font'
    if (url.match(/\/api\//)) return 'api'
    return 'other'
  }

  // 检查资源性能
  private checkResourcePerformance(analysis: any) {
    const thresholds = {
      script: 500,
      stylesheet: 300,
      image: 1000,
      font: 100,
      api: 2000,
    }

    const threshold = thresholds[analysis.type] || 1000
    if (analysis.duration > threshold) {
      ErrorTracking.trackError(
        new Error(`Slow resource loading: ${analysis.name}`),
        {
          resource_type: analysis.type,
          duration: analysis.duration,
          threshold,
          size: analysis.size,
          cached: analysis.cached,
        },
        'warning'
      )
    }
  }

  // 报告长任务
  private reportLongTask(entry: PerformanceEntry) {
    ErrorTracking.trackError(
      new Error(`Long task detected: ${entry.duration}ms`),
      {
        task_duration: entry.duration,
        task_start_time: entry.startTime,
        url: typeof window !== 'undefined' ? window.location.href : 'unknown',
      },
      'warning'
    )
  }

  // 发送资源数据
  private sendResourceData(data: any) {
    fetch('/api/analytics/performance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...data,
        timestamp: Date.now(),
        url: typeof window !== 'undefined' ? window.location.href : 'unknown',
      }),
    })
  }

  // 清理观察器
  disconnect() {
    this.observers.forEach(observer => observer.disconnect())
    this.observers = []
  }
}
```

## 📊 用户行为分析

### 事件追踪系统

#### 🎯 自定义事件追踪
```tsx
// lib/analytics.ts
export interface AnalyticsEvent {
  event: string
  properties: Record<string, any>
  user_id?: string
  session_id?: string
  timestamp: number
  url: string
  user_agent: string
}

export class Analytics {
  private static instance: Analytics
  private queue: AnalyticsEvent[] = []
  private sessionId: string

  constructor() {
    this.sessionId = this.generateSessionId()
  }

  static getInstance(): Analytics {
    if (!Analytics.instance) {
      Analytics.instance = new Analytics()
    }
    return Analytics.instance
  }

  // 追踪事件
  track(event: string, properties: Record<string, any> = {}) {
    const analyticsEvent: AnalyticsEvent = {
      event,
      properties,
      timestamp: Date.now(),
      url: typeof window !== 'undefined' ? window.location.href : '',
      user_agent: typeof window !== 'undefined' ? navigator.userAgent : '',
    }

    // 添加用户信息
    if (typeof window !== 'undefined') {
      analyticsEvent.session_id = this.sessionId

      // 从 localStorage 获取用户信息
      const userId = localStorage.getItem('user_id')
      if (userId) {
        analyticsEvent.user_id = userId
      }
    }

    // 立即发送或加入队列
    if (navigator.onLine) {
      this.sendEvent(analyticsEvent)
    } else {
      this.queueEvent(analyticsEvent)
    }

    // 同时发送到 Google Analytics
    this.sendToGA(event, properties)
  }

  // 追踪页面浏览
  page(path?: string, properties: Record<string, any> = {}) {
    this.track('page_view', {
      path: path || (typeof window !== 'undefined' ? window.location.pathname : ''),
      title: typeof document !== 'undefined' ? document.title : '',
      referrer: typeof document !== 'undefined' ? document.referrer : '',
      ...properties,
    })
  }

  // 追踪用户标识
  identify(userId: string, traits: Record<string, any> = {}) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('user_id', userId)
      localStorage.setItem('user_traits', JSON.stringify(traits))
    }

    this.track('identify', {
      user_id: userId,
      traits,
    })
  }

  // 发送事件到服务器
  private async sendEvent(event: AnalyticsEvent) {
    try {
      await fetch('/api/analytics/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(event),
      })
    } catch (error) {
      console.error('Failed to send analytics event:', error)
      this.queueEvent(event)
    }
  }

  // 队列事件
  private queueEvent(event: AnalyticsEvent) {
    this.queue.push(event)

    // 限制队列大小
    if (this.queue.length > 100) {
      this.queue.shift()
    }

    // 监听网络恢复
    if (typeof window !== 'undefined') {
      window.addEventListener('online', this.flushQueue.bind(this))
    }
  }

  // 刷新队列
  private async flushQueue() {
    while (this.queue.length > 0 && navigator.onLine) {
      const event = this.queue.shift()
      if (event) {
        await this.sendEvent(event)
      }
    }
  }

  // 发送到 Google Analytics
  private sendToGA(event: string, properties: Record<string, any>) {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', event, properties)
    }
  }

  // 生成会话ID
  private generateSessionId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2)
  }
}

// hooks/useAnalytics.ts
'use client'

import { useCallback } from 'react'
import { Analytics } from '@/lib/analytics'

export function useAnalytics() {
  const analytics = Analytics.getInstance()

  const track = useCallback((event: string, properties?: Record<string, any>) => {
    analytics.track(event, properties)
  }, [analytics])

  const page = useCallback((path?: string, properties?: Record<string, any>) => {
    analytics.page(path, properties)
  }, [analytics])

  const identify = useCallback((userId: string, traits?: Record<string, any>) => {
    analytics.identify(userId, traits)
  }, [analytics])

  return {
    track,
    page,
    identify,
  }
}

// 使用示例
export function ComponentWithAnalytics() {
  const { track, identify } = useAnalytics()

  const handleButtonClick = () => {
    track('button_click', {
      button_id: 'cta_button',
      location: 'hero_section',
      variant: 'primary',
    })
  }

  const handleUserLogin = (userId: string, userInfo: any) => {
    identify(userId, {
      name: userInfo.name,
      email: userInfo.email,
      plan: userInfo.plan,
    })

    track('login', {
      method: 'email',
      success: true,
    })
  }

  return (
    <div>
      <button onClick={handleButtonClick}>
        Click me!
      </button>
    </div>
  )
}
```

#### 📈 转化漏斗分析
```typescript
// lib/funnel-analytics.ts
export interface FunnelStep {
  name: string
  event_name: string
  required: boolean
  time_window?: number // 时间窗口（小时）
}

export interface FunnelDefinition {
  id: string
  name: string
  steps: FunnelStep[]
  window: number // 总时间窗口（小时）
}

export class FunnelAnalytics {
  private static instance: FunnelAnalytics
  private funnels: Map<string, FunnelDefinition> = new Map()

  static getInstance(): FunnelAnalytics {
    if (!FunnelAnalytics.instance) {
      FunnelAnalytics.instance = new FunnelAnalytics()
    }
    return FunnelAnalytics.instance
  }

  // 注册漏斗定义
  registerFunnel(funnel: FunnelDefinition) {
    this.funnels.set(funnel.id, funnel)
  }

  // 追踪漏斗事件
  trackFunnelEvent(funnelId: string, eventName: string, userId: string, properties: Record<string, any> = {}) {
    const funnel = this.funnels.get(funnelId)
    if (!funnel) return

    const step = funnel.steps.find(s => s.event_name === eventName)
    if (!step) return

    // 发送漏斗事件
    fetch('/api/analytics/funnel', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        funnel_id: funnelId,
        step_name: step.name,
        event_name: eventName,
        user_id: userId,
        properties,
        timestamp: Date.now(),
      }),
    })
  }

  // 分析漏斗转化
  async analyzeFunnel(funnelId: string, startDate: Date, endDate: Date) {
    const response = await fetch(`/api/analytics/funnel/${funnelId}/analyze?start=${startDate.getTime()}&end=${endDate.getTime()}`)
    return response.json()
  }
}

// 预定义的漏斗
export const standardFunnels: FunnelDefinition[] = [
  {
    id: 'user_registration',
    name: '用户注册漏斗',
    window: 24,
    steps: [
      { name: 'visit_signup', event_name: 'visit_signup_page', required: true },
      { name: 'start_signup', event_name: 'signup_form_start', required: true },
      { name: 'complete_signup', event_name: 'signup_complete', required: true },
      { name: 'email_verify', event_name: 'email_verified', required: false },
    ],
  },
  {
    id: 'purchase_funnel',
    name: '购买转化漏斗',
    window: 72,
    steps: [
      { name: 'product_view', event_name: 'product_view', required: true },
      { name: 'add_to_cart', event_name: 'add_to_cart', required: true },
      { name: 'checkout_start', event_name: 'checkout_start', required: true },
      { name: 'purchase_complete', event_name: 'purchase_complete', required: true },
    ],
  },
]
```

## 📊 仪表板和可视化

### 自定义仪表板

#### 📈 实时监控仪表板
```tsx
// components/Dashboard/RealTimeMetrics.tsx
'use client'

import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface MetricData {
  timestamp: number
  value: number
  label: string
}

export default function RealTimeMetrics() {
  const [metrics, setMetrics] = useState<{
    pageViews: MetricData[]
    errors: MetricData[]
    performance: MetricData[]
  }>({
    pageViews: [],
    errors: [],
    performance: [],
  })

  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const [pageViews, errors, performance] = await Promise.all([
          fetch('/api/analytics/realtime/pageviews').then(r => r.json()),
          fetch('/api/analytics/realtime/errors').then(r => r.json()),
          fetch('/api/analytics/realtime/performance').then(r => r.json()),
        ])

        setMetrics({
          pageViews: pageViews.data || [],
          errors: errors.data || [],
          performance: performance.data || [],
        })
      } catch (error) {
        console.error('Failed to fetch metrics:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchMetrics()
    const interval = setInterval(fetchMetrics, 30000) // 每30秒更新

    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return <div className="p-6">Loading metrics...</div>
  }

  return (
    <div className="space-y-6">
      {/* 页面浏览量 */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Page Views (Last Hour)</h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={metrics.pageViews}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="label"
              tickFormatter={(value) => new Date(value).toLocaleTimeString()}
            />
            <YAxis />
            <Tooltip
              labelFormatter={(value) => new Date(value).toLocaleString()}
            />
            <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 错误率 */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Error Rate (Last Hour)</h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={metrics.errors}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="label"
              tickFormatter={(value) => new Date(value).toLocaleTimeString()}
            />
            <YAxis />
            <Tooltip
              labelFormatter={(value) => new Date(value).toLocaleString()}
            />
            <Line type="monotone" dataKey="value" stroke="#ef4444" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 性能指标 */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Performance Score (Last Hour)</h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={metrics.performance}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="label"
              tickFormatter={(value) => new Date(value).toLocaleTimeString()}
            />
            <YAxis domain={[0, 100]} />
            <Tooltip
              labelFormatter={(value) => new Date(value).toLocaleString()}
            />
            <Line type="monotone" dataKey="value" stroke="#10b981" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
```

## 🔧 API 路由实现

### 分析API端点
```typescript
// app/api/analytics/events/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { headers } from 'next/headers'

export async function POST(request: NextRequest) {
  try {
    const event = await request.json()

    // 验证事件数据
    if (!event.event || !event.timestamp) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      )
    }

    // 获取客户端信息
    const headersList = await headers()
    const userAgent = headersList.get('user-agent') || ''
    const ip = headersList.get('x-forwarded-for') || headersList.get('x-real-ip') || 'unknown'

    // 增强事件数据
    const enrichedEvent = {
      ...event,
      ip,
      user_agent: userAgent,
      server_timestamp: Date.now(),
    }

    // 存储到数据库
    await storeAnalyticsEvent(enrichedEvent)

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Failed to store analytics event:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

async function storeAnalyticsEvent(event: any) {
  // 实现数据库存储逻辑
  // 这里可以使用 PostgreSQL、MongoDB 等
  console.log('Storing analytics event:', event)
}
```

## 📋 最佳实践清单

先制造一个受控错误，确认错误平台记录了对应发布版本、源码位置和请求线索，并检查敏感数据已经过滤。再故意降低一个依赖的响应速度，确认性能指标能区分前端加载与后端等待。

用户分析只采集有明确用途的事件，定义事件何时触发和如何去重，避免“按钮点击”与“操作成功”混为一谈。仪表板围绕要做的决策设计；验证一次告警到调查的过程，比勾选“智能告警、实时看板”更能证明系统可用。

## 🎯 总结

完成本章后，应能为一个关键旅程证明：异常会被正确脱敏并关联到 release，性能或依赖变慢能被区分，告警能到达负责人，恢复后可验证用户任务重新成功。更多工具只有在它们改变具体决策或缩短排障时间时才值得加入。

## 🔗 相关资源链接

### 官方资源
- [Next.js Analytics 文档](https://nextjs.org/docs/advanced-features/measuring-performance)
- [Sentry 错误监控](https://docs.sentry.io/)
- [Google Analytics](https://analytics.google.com/)
- [Vercel Analytics](https://vercel.com/docs/analytics)

### 技术文章
- [现代前端监控最佳实践](https://web.dev/vitals/)
- [错误监控和性能优化](https://sentry.io/for/next.js/)
- [用户体验指标分析](https://web.dev/learn-web-vitals/)
- [APM 实施指南](https://www.datadoghq.com/blog/apm)

### 工具和资源
- [Prometheus 监控](https://prometheus.io/)
- [Grafana 可视化](https://grafana.com/)
- [ELK Stack](https://www.elastic.co/what-is/elk-stack)
- [LogRocket 回放工具](https://www.logrocket.com/)

## 📚 模块内相关文档

### 同模块相关文档
- [Vercel部署指南](./01-vercel-deployment.md) - Vercel平台的监控和Analytics集成
- [Docker容器化部署](./02-docker-containerization.md) - 容器化应用的监控配置
- [CI/CD流水线](./03-ci-cd-pipelines.md) - CI/CD流水线的监控和报告

### 相关知识模块
- [框架相关模块](../frameworks/04-performance-optimization.md) - 性能优化和监控的深度结合
- [测试相关模块](../testing/03-e2e-testing.md) - E2E测试和监控数据的联动分析
- [测试相关模块](../testing/01-unit-testing.md) - 单元测试覆盖率和质量监控

### 基础前置知识
- [Web性能优化基础](../advanced-topics/performance/01-core-web-vitals.md) - Web性能指标和优化基础
- [浏览器渲染原理](../reference/performance-optimization/01-rendering-optimization.md) - 理解性能监控的技术基础
- [数据可视化基础](../projects/03-dashboard-analytics.md) - 监控数据的可视化展示

---

## ✨ 总结

### 交付时应能说明什么

1. **信号与问题的对应关系**：性能、错误、可用性和业务事件服务不同问题。为每个仪表盘写出数据来源、刷新或聚合窗口，以及看到异常后要采取的第一步。
2. **错误事件可定位且不泄露**：错误需要关联 release、路由、浏览器和已脱敏的上下文，才能从事件跳回对应构建的源码。令牌、Cookie、请求正文和可识别个人数据不能作为排障字段上传。
3. **性能指标有基线**：分别记录真实用户或合成测试的 LCP、INP、CLS 与接口延迟；比较优化前后时保持页面、设备档位、网络条件和样本窗口一致，避免把偶然波动当成果。
4. **告警可行动**：每条告警包含指标、阈值、持续时间、去重规则、负责人和运行手册链接。只有“监控面板有红色曲线”不等于值班人会收到并处理问题。
5. **业务事件可校验**：埋点定义事件名、触发时机、去重键和允许字段；在开发或预发布环境验证一次交互只生成预期次数的事件，再用样本记录核对。

### 学习成果验收

- [ ] 在隔离测试页面触发合成错误，确认事件包含 release 和源码定位信息，且不含敏感请求字段。
- [ ] 阻断监控采集请求后完成一次正常操作，确认观测 SDK 的失败不会阻塞产品功能。
- [ ] 在固定页面、设备与网络条件下记录一组优化前后性能数据，并说明样本数和比较窗口。
- [ ] 用可控的错误率或可用性故障触发告警，保存通知、确认时间、运行手册处置和恢复证据。
- [ ] 对一个业务事件重复操作，核对事件数量、去重规则和实际 UI 行为一致。

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
- **问题反馈**: [GitHub Issues](https://github.com/x-rush/dev-quest/issues)
- **内容建议**: [Discussion板块](https://github.com/x-rush/dev-quest/discussions)
- **技术交流**: 欢迎提交PR或Issue参与讨论

### 贡献者
- Dev Quest Team - 核心内容开发
- 社区贡献者 - 内容完善和纠错

---

**📜 文档版本**: v1.0.0
**📅 最后更新**: 2026年9月
**🏷️ 标签**: `#monitoring` `#analytics` `#error-tracking` `#performance` `#observability`
**⭐ 推荐指数**: ⭐⭐⭐

**💡 提示**: 本模块专注于现代前端监控和分析实践，适合需要构建完整监控体系的团队。

**🎯 学习建议**:
- 建议学习周期: 2-3周
- 理论与实践时间比例: 4:6
- 重点掌握性能监控和错误追踪
- 从一个错误事件、一个性能页面和一个业务事件开始建立最小观测闭环；先验证数据能定位和告警能送达，再扩大指标数量。

<!-- acceptance-exercise -->
## 练习与验收：从一个可控错误验证监控链路

在预发布页面的测试按钮中抛出合成错误，记录本次 release 标识。验收：错误平台能定位到对应构建的源码行，事件不含测试账号的 token 或表单正文。再阻断采集请求，正常页面操作仍能完成；业务事件重复上报时，检查组件重复挂载与埋点位置，而不是直接把计数当真实用户数。错误演练入口不能带入正式用户流程。

以上是在个人或隔离测试环境中的练习，不是本轮已执行记录；实际运行范围见仓库文档质量报告。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
