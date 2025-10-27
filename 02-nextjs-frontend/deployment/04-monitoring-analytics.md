# Next.js 15 监控和分析完整指南

> **文档简介**: Next.js 15 现代监控和分析完整指南，涵盖Sentry错误监控、Vercel Analytics、性能分析、用户行为追踪等企业级监控解决方案

> **目标读者**: 具备Next.js基础的开发者，需要构建完整监控和分析系统的运维工程师和架构师

> **前置知识**: Next.js 15基础、生产部署经验、基础监控概念、数据分析基础

> **预计时长**: 6-8小时

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `deployment` |
| **难度** | ⭐⭐⭐⭐ (4/5星) |
| **标签** | `#monitoring` `#analytics` `#sentry` `#performance` `#error-tracking` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标

### 📊 企业级监控系统
- 掌握Sentry错误监控和性能追踪的完整配置
- 实现Vercel Analytics集成和Web Vitals监控
- 构建自定义事件追踪和用户行为分析系统
- 实现实时告警和异常处理机制
- 掌握日志聚合和分析平台建设
- 建立完整的性能监控和优化体系

### 📈 数据分析能力
- 实现用户行为追踪和转化漏斗分析
- 掌握A/B测试和特征标志管理系统
- 构建自定义仪表板和数据可视化
- 实现业务指标监控和KPI追踪
- 掌握数据隐私保护和合规要求
- 建立数据驱动的决策支持系统

### 🚀 运维最佳实践
- 实施多层次监控策略（基础设施、应用、业务）
- 掌握异常检测和根因分析技术
- 建立智能告警和自动化响应机制
- 实现容量规划和性能预测
- 掌握灾难恢复和业务连续性保障
- 建立团队协作的运维流程体系

## 📖 概述

Next.js 15 应用在生产环境中需要全面的监控和分析体系来确保稳定性、性能和用户体验。本指南深入探讨企业级监控和分析解决方案，从错误追踪到性能优化，从用户行为分析到业务指标监控，帮助你构建完整的可观测性体系。

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
```typescript
// 安装 Sentry
npm install @sentry/nextjs

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
    new Sentry.Replay({
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

// sentry.server.config.ts
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
  debug: false,
  integrations: [
    new Sentry.Integrations.Http({ tracing: true }),
    new Sentry.Integrations.Express({ app }),
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

  // 追踪性能指标
  static trackPerformance(metricName: string, value: number, unit: string = 'ms') {
    Sentry.metrics.timing(metricName, value, { unit })
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
```typescript
// lib/web-vitals.ts
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'

export interface WebVitalsMetrics {
  CLS: number // Cumulative Layout Shift
  FID: number // First Input Delay
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
    getCLS(this.handleMetric.bind(this, 'CLS'))
    getFID(this.handleMetric.bind(this, 'FID'))
    getFCP(this.handleMetric.bind(this, 'FCP'))
    getLCP(this.handleMetric.bind(this, 'LCP'))
    getTTFB(this.handleMetric.bind(this, 'TTFB'))
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
      FID: 100,
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
```typescript
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
```typescript
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
    const headersList = headers()
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

### ✅ 错误监控
- [ ] 配置Sentry完整集成
- [ ] 实现自定义错误追踪
- [ ] 设置智能告警规则
- [ ] 建立错误分类和优先级
- [ ] 实现错误趋势分析

### ✅ 性能监控
- [ ] 集成Web Vitals追踪
- [ ] 实现自定义性能监控
- [ ] 设置性能阈值告警
- [ ] 建立性能基线对比
- [ ] 实现资源加载分析

### ✅ 用户分析
- [ ] 实现事件追踪系统
- [ ] 建立转化漏斗分析
- [ ] 配置用户行为追踪
- [ ] 实现A/B测试框架
- [ ] 建立用户分群系统

### ✅ 仪表板和可视化
- [ ] 创建实时监控仪表板
- [ ] 实现自定义报告系统
- [ ] 建立趋势分析图表
- [ ] 配置移动端适配
- [ ] 实现数据导出功能

## 🎯 总结

Next.js 15 的监控和分析体系为现代Web应用提供了全面的可观测性解决方案。通过合理配置错误监控、性能追踪、用户行为分析等工具，可以构建完整的监控体系，确保应用的稳定性和持续优化。

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
- [Web性能优化基础](../../../01-react-foundation/basics/05-web-performance-basics.md) - Web性能指标和优化基础
- [浏览器渲染原理](../../../01-react-foundation/advanced/06-browser-rendering.md) - 理解性能监控的技术基础
- [数据可视化基础](../../../01-react-foundation/advanced/13-data-visualization.md) - 监控数据的可视化展示

---

## ✨ 总结

### 核心技术要点
1. **多层监控体系**: 性能、错误、用户行为的全方位监控
2. **实时错误追踪**: Sentry集成的错误监控和告警机制
3. **用户体验分析**: Web Vitals和用户行为数据的收集分析
4. **日志管理系统**: 结构化日志和集中式日志分析
5. **运维监控**: 系统资源、API性能和业务指标的监控

### 学习成果自检
- [ ] 理解现代前端监控的核心概念和体系架构
- [ ] 掌握Next.js 15应用的性能监控和优化策略
- [ ] 能够建立完整的错误监控和告警体系
- [ ] 熟练运用数据分析工具进行用户体验优化
- [ ] 能够构建企业级的监控和运维体系

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
**🏷️ 标签**: `#monitoring` `#analytics` `#error-tracking` `#performance` `#observability`
**⭐ 推荐指数**: ⭐⭐⭐⭐⭐

**💡 提示**: 本模块专注于现代前端监控和分析实践，适合需要构建完整监控体系的团队。

**🎯 学习建议**:
- 建议学习周期: 2-3周
- 理论与实践时间比例: 4:6
- 重点掌握性能监控和错误追踪
- 结合实际项目建立完整的监控体系