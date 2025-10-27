# 应用扩展模式完整指南

> **文档简介**: Next.js 15 + React 19 企业级应用扩展架构指南，涵盖水平扩展、垂直扩展、微服务架构、CDN、负载均衡、数据库扩展等全方位扩展策略

> **目标读者**: 高级前端工程师、系统架构师、DevOps工程师、技术总监

> **前置知识**: Next.js 15深度掌握、React 19高级特性、分布式系统基础、云计算知识、DevOps实践

> **预计时长**: 15-20小时

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `advanced-topics/architecture` |
| **难度** | ⭐⭐⭐⭐⭐ (5/5星) |
| **标签** | `#scalability` `#architecture` `#microservices` `#load-balancing` `#cdns` `#nextjs15` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标

- 深入理解Web应用扩展的不同策略和模式
- 掌握Next.js 15应用的水平扩展和垂直扩展技术
- 实施微服务架构和服务拆分策略
- 建立高可用的负载均衡和故障转移机制
- 实现多层级CDN缓存和全球内容分发
- 构建可扩展的数据库和数据存储架构

## 📖 概述

本指南深入探讨现代Web应用的扩展架构设计，从单体应用到微服务架构的演进，从单机部署到全球分布式系统的扩展策略。通过实际架构设计和最佳实践，帮助开发者构建可扩展、高可用的企业级应用。

## 🏗️ 扩展架构模式

### 📊 应用架构演进

```typescript
// app/lib/architecture/evolution-stages.ts
enum ArchitectureStage {
  MONOLITH = 'monolith',
  MINI_SERVICES = 'mini-services',
  MICROSERVICES = 'microservices',
  DISTRIBUTED_SYSTEM = 'distributed-system'
}

interface ArchitectureMetrics {
  stage: ArchitectureStage
  complexity: 'low' | 'medium' | 'high' | 'very-high'
  scalability: 'limited' | 'moderate' | 'high' | 'unlimited'
  maintainability: 'high' | 'medium' | 'low'
  deploymentComplexity: 'simple' | 'moderate' | 'complex' | 'very-complex'
  teamSize: '1-5' | '5-20' | '20-50' | '50+'
}

// 架构演进策略
class ArchitectureEvolution {
  private metrics: Map<ArchitectureStage, ArchitectureMetrics> = new Map([
    [ArchitectureStage.MONOLITH, {
      stage: ArchitectureStage.MONOLITH,
      complexity: 'low',
      scalability: 'limited',
      maintainability: 'high',
      deploymentComplexity: 'simple',
      teamSize: '1-5'
    }],
    [ArchitectureStage.MINI_SERVICES, {
      stage: ArchitectureStage.MINI_SERVICES,
      complexity: 'medium',
      scalability: 'moderate',
      maintainability: 'medium',
      deploymentComplexity: 'moderate',
      teamSize: '5-20'
    }],
    [ArchitectureStage.MICROSERVICES, {
      stage: ArchitectureStage.MICROSERVICES,
      complexity: 'high',
      scalability: 'high',
      maintainability: 'low',
      deploymentComplexity: 'complex',
      teamSize: '20-50'
    }],
    [ArchitectureStage.DISTRIBUTED_SYSTEM, {
      stage: ArchitectureStage.DISTRIBUTED_SYSTEM,
      complexity: 'very-high',
      scalability: 'unlimited',
      maintainability: 'low',
      deploymentComplexity: 'very-complex',
      teamSize: '50+'
    }]
  ])

  // 评估当前架构阶段
  assessCurrentStage(currentMetrics: Partial<ArchitectureMetrics>): ArchitectureStage {
    // 基于指标评估当前架构阶段
    if (currentMetrics.teamSize && parseInt(currentMetrics.teamSize.split('-')[1]) <= 5) {
      return ArchitectureStage.MONOLITH
    } else if (currentMetrics.scalability === 'moderate') {
      return ArchitectureStage.MINI_SERVICES
    } else if (currentMetrics.scalability === 'high') {
      return ArchitectureStage.MICROSERVICES
    } else {
      return ArchitectureStage.DISTRIBUTED_SYSTEM
    }
  }

  // 推荐下一步架构演进
  recommendEvolution(currentStage: ArchitectureStage): ArchitectureStage {
    switch (currentStage) {
      case ArchitectureStage.MONOLITH:
        return ArchitectureStage.MINI_SERVICES
      case ArchitectureStage.MINI_SERVICES:
        return ArchitectureStage.MICROSERVICES
      case ArchitectureStage.MICROSERVICES:
        return ArchitectureStage.DISTRIBUTED_SYSTEM
      default:
        return currentStage
    }
  }

  // 获取架构阶段详细信息
  getStageMetrics(stage: ArchitectureStage): ArchitectureMetrics {
    return this.metrics.get(stage)!
  }

  // 架构演进成本分析
  analyzeEvolutionCost(from: ArchitectureStage, to: ArchitectureStage): {
    developmentCost: number
    infrastructureCost: number
    operationalCost: number
    migrationRisk: 'low' | 'medium' | 'high'
    estimatedTimeframe: string
  } {
    const fromMetrics = this.getStageMetrics(from)
    const toMetrics = this.getStageMetrics(to)

    const complexityFactor = {
      'low': 1,
      'medium': 2,
      'high': 4,
      'very-high': 8
    }

    const developmentCost = complexityFactor[toMetrics.complexity] / complexityFactor[fromMetrics.complexity]
    const infrastructureCost = complexityFactor[toMetrics.deploymentComplexity] / complexityFactor[fromMetrics.deploymentComplexity]
    const operationalCost = complexityFactor[toMetrics.teamSize].split('-')[1] / complexityFactor[fromMetrics.teamSize].split('-')[1]

    return {
      developmentCost: developmentCost * 100000, // 基准成本
      infrastructureCost: infrastructureCost * 50000,
      operationalCost: operationalCost * 10000,
      migrationRisk: this.assessMigrationRisk(from, to),
      estimatedTimeframe: this.estimateTimeframe(from, to)
    }
  }

  private assessMigrationRisk(from: ArchitectureStage, to: ArchitectureStage): 'low' | 'medium' | 'high' {
    const stageOrder = [ArchitectureStage.MONOLITH, ArchitectureStage.MINI_SERVICES, ArchitectureStage.MICROSERVICES, ArchitectureStage.DISTRIBUTED_SYSTEM]
    const fromIndex = stageOrder.indexOf(from)
    const toIndex = stageOrder.indexOf(to)

    if (toIndex - fromIndex <= 1) {
      return 'low'
    } else if (toIndex - fromIndex === 2) {
      return 'medium'
    } else {
      return 'high'
    }
  }

  private estimateTimeframe(from: ArchitectureStage, to: ArchitectureStage): string {
    const timeframes = {
      [`${ArchitectureStage.MONOLITH}-${ArchitectureStage.MINI_SERVICES}`]: '3-6 months',
      [`${ArchitectureStage.MINI_SERVICES}-${ArchitectureStage.MICROSERVICES}`]: '6-12 months',
      [`${ArchitectureStage.MICROSERVICES}-${ArchitectureStage.DISTRIBUTED_SYSTEM}`]: '12-24 months'
    }

    return timeframes[`${from}-${to}`] || 'unknown'
  }
}

export const architectureEvolution = new ArchitectureEvolution()
```

### 🔄 水平扩展策略

```typescript
// app/lib/scaling/horizontal-scaling.ts
interface HorizontalScalingConfig {
  minInstances: number
  maxInstances: number
  targetCPUUtilization: number
  targetMemoryUtilization: number
  scaleUpCooldown: number
  scaleDownCooldown: number
  healthCheckPath: string
}

class HorizontalScalingManager {
  private config: HorizontalScalingConfig
  private currentInstances: number = 0
  private scaleHistory: Array<{ timestamp: number; instances: number; action: 'up' | 'down' }> = []
  private healthChecker: HealthChecker

  constructor(config: HorizontalScalingConfig) {
    this.config = config
    this.healthChecker = new HealthChecker(config.healthCheckPath)
  }

  // 自动扩展决策
  async makeScalingDecision(metrics: SystemMetrics): Promise<ScalingDecision> {
    const currentLoad = this.calculateLoad(metrics)
    const predictedLoad = this.predictLoad()

    const decision = this.evaluateScaling(currentLoad, predictedLoad)

    if (decision.shouldScale) {
      await this.executeScaling(decision)
    }

    return decision
  }

  private calculateLoad(metrics: SystemMetrics): number {
    const cpuWeight = 0.6
    const memoryWeight = 0.3
    const requestWeight = 0.1

    const cpuLoad = metrics.cpuUtilization / this.config.targetCPUUtilization
    const memoryLoad = metrics.memoryUtilization / this.config.targetMemoryUtilization
    const requestLoad = metrics.requestsPerSecond / (this.currentInstances * 1000) // 假设每实例1000 RPS

    return (cpuLoad * cpuWeight) + (memoryLoad * memoryWeight) + (requestLoad * requestWeight)
  }

  private predictLoad(): number {
    // 基于历史数据预测负载
    if (this.scaleHistory.length < 2) {
      return 1 // 默认负载
    }

    const recentScales = this.scaleHistory.slice(-5)
    const trend = this.calculateTrend(recentScales)

    return Math.max(0.1, Math.min(2, 1 + trend))
  }

  private calculateTrend(history: Array<{ timestamp: number; instances: number; action: 'up' | 'down' }>): number {
    if (history.length < 2) return 0

    let totalChange = 0
    let weightSum = 0

    for (let i = 1; i < history.length; i++) {
      const timeDiff = history[i].timestamp - history[i-1].timestamp
      const instanceChange = history[i].instances - history[i-1].instances
      const weight = Math.exp(-timeDiff / (5 * 60 * 1000)) // 5分钟指数衰减

      totalChange += instanceChange * weight
      weightSum += weight
    }

    return weightSum > 0 ? totalChange / weightSum : 0
  }

  private evaluateScaling(currentLoad: number, predictedLoad: number): ScalingDecision {
    const effectiveLoad = Math.max(currentLoad, predictedLoad)

    // 扩展条件
    if (effectiveLoad > 1.2 && this.currentInstances < this.config.maxInstances) {
      const newInstances = Math.min(
        this.config.maxInstances,
        Math.ceil(this.currentInstances * effectiveLoad)
      )

      if (this.canScaleUp()) {
        return {
          shouldScale: true,
          direction: 'up',
          targetInstances: newInstances,
          reason: `High load detected: ${effectiveLoad.toFixed(2)}`
        }
      }
    }

    // 缩减条件
    if (effectiveLoad < 0.5 && this.currentInstances > this.config.minInstances) {
      const newInstances = Math.max(
        this.config.minInstances,
        Math.floor(this.currentInstances * effectiveLoad)
      )

      if (this.canScaleDown()) {
        return {
          shouldScale: true,
          direction: 'down',
          targetInstances: newInstances,
          reason: `Low load detected: ${effectiveLoad.toFixed(2)}`
        }
      }
    }

    return {
      shouldScale: false,
      direction: 'none',
      targetInstances: this.currentInstances,
      reason: 'No scaling needed'
    }
  }

  private canScaleUp(): boolean {
    const lastScaleUp = this.scaleHistory
      .filter(s => s.action === 'up')
      .pop()

    if (!lastScaleUp) return true

    return (Date.now() - lastScaleUp.timestamp) > this.config.scaleUpCooldown * 1000
  }

  private canScaleDown(): boolean {
    const lastScaleDown = this.scaleHistory
      .filter(s => s.action === 'down')
      .pop()

    if (!lastScaleDown) return true

    return (Date.now() - lastScaleDown.timestamp) > this.config.scaleDownCooldown * 1000
  }

  private async executeScaling(decision: ScalingDecision): Promise<void> {
    if (decision.direction === 'none') return

    try {
      console.log(`Scaling ${decision.direction}: ${this.currentInstances} -> ${decision.targetInstances}`)

      // 预热新实例
      if (decision.direction === 'up') {
        await this.warmUpInstances(decision.targetInstances - this.currentInstances)
      }

      // 执行扩展
      await this.performScaling(decision.targetInstances)

      // 验证扩展结果
      await this.validateScaling(decision.targetInstances)

      // 记录扩展历史
      this.scaleHistory.push({
        timestamp: Date.now(),
        instances: decision.targetInstances,
        action: decision.direction
      })

      this.currentInstances = decision.targetInstances

      // 发送扩展事件
      await this.emitScalingEvent(decision)

    } catch (error) {
      console.error('Scaling failed:', error)
      // 发送扩展失败事件
      await this.emitScalingFailureEvent(decision, error)
    }
  }

  private async warmUpInstances(count: number): Promise<void> {
    // 预热新实例
    const warmupPromises = Array.from({ length: count }, async (_, index) => {
      const instanceUrl = `${process.env.INSTANCE_BASE_URL}/instance/warmup`
      await fetch(instanceUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ instanceId: `warmup-${Date.now()}-${index}` })
      })
    })

    await Promise.allSettled(warmupPromises)
  }

  private async performScaling(targetInstances: number): Promise<void> {
    const scalingUrl = process.env.AUTO_SCALING_URL || 'http://localhost:3001/api/scale'

    const response = await fetch(scalingUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        desiredInstances: targetInstances,
        currentInstances: this.currentInstances,
        timestamp: Date.now()
      })
    })

    if (!response.ok) {
      throw new Error(`Scaling request failed: ${response.statusText}`)
    }
  }

  private async validateScaling(targetInstances: number): Promise<void> {
    let attempts = 0
    const maxAttempts = 10
    const checkInterval = 5000 // 5秒

    while (attempts < maxAttempts) {
      const healthyInstances = await this.healthChecker.checkAllInstances()

      if (healthyInstances >= targetInstances * 0.9) { // 90%健康率
        return
      }

      attempts++
      await new Promise(resolve => setTimeout(resolve, checkInterval))
    }

    throw new Error('Scaling validation failed: insufficient healthy instances')
  }

  private async emitScalingEvent(decision: ScalingDecision): Promise<void> {
    await fetch('/api/events/scaling', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'scaling_executed',
        data: {
          timestamp: Date.now(),
          decision,
          currentInstances: this.currentInstances,
          metrics: await this.getCurrentMetrics()
        }
      })
    })
  }

  private async emitScalingFailureEvent(decision: ScalingDecision, error: Error): Promise<void> {
    await fetch('/api/events/scaling', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'scaling_failed',
        data: {
          timestamp: Date.now(),
          decision,
          error: error.message,
          currentInstances: this.currentInstances
        }
      })
    })
  }

  private async getCurrentMetrics(): Promise<SystemMetrics> {
    const response = await fetch('/api/metrics/current')
    if (!response.ok) {
      throw new Error('Failed to fetch current metrics')
    }
    return response.json()
  }

  // 启动自动扩展监控
  startAutoScaling(intervalMs: number = 30000): void {
    setInterval(async () => {
      try {
        const metrics = await this.getCurrentMetrics()
        await this.makeScalingDecision(metrics)
      } catch (error) {
        console.error('Auto scaling error:', error)
      }
    }, intervalMs)
  }
}

// 健康检查器
class HealthChecker {
  private healthCheckPath: string

  constructor(healthCheckPath: string) {
    this.healthCheckPath = healthCheckPath
  }

  async checkInstance(instanceUrl: string): Promise<boolean> {
    try {
      const response = await fetch(`${instanceUrl}${this.healthCheckPath}`, {
        method: 'GET',
        timeout: 5000
      })
      return response.ok && response.status === 200
    } catch (error) {
      return false
    }
  }

  async checkAllInstances(): Promise<number> {
    const instances = await this.getInstanceList()

    const healthChecks = await Promise.allSettled(
      instances.map(instance => this.checkInstance(instance))
    )

    return healthChecks.filter(result => result.status === 'fulfilled' && result.value).length
  }

  private async getInstanceList(): Promise<string[]> {
    const response = await fetch('/api/instances/list')
    if (!response.ok) {
      throw new Error('Failed to fetch instance list')
    }
    return response.json()
  }
}

interface SystemMetrics {
  cpuUtilization: number
  memoryUtilization: number
  requestsPerSecond: number
  averageResponseTime: number
  errorRate: number
}

interface ScalingDecision {
  shouldScale: boolean
  direction: 'up' | 'down' | 'none'
  targetInstances: number
  reason: string
}

export const horizontalScalingManager = new HorizontalScalingManager({
  minInstances: 2,
  maxInstances: 20,
  targetCPUUtilization: 70,
  targetMemoryUtilization: 80,
  scaleUpCooldown: 300, // 5分钟
  scaleDownCooldown: 600, // 10分钟
  healthCheckPath: '/health'
})
```

### 📈 垂直扩展策略

```typescript
// app/lib/scaling/vertical-scaling.ts
interface VerticalScalingConfig {
  maxCPU: number
  maxMemory: number
  maxStorage: number
  maxBandwidth: number
  monitoringInterval: number
  scaleUpThreshold: number
  scaleDownThreshold: number
}

class VerticalScalingManager {
  private config: VerticalScalingConfig
  private resourceHistory: ResourceMetrics[] = []
  private alertThresholds: AlertThresholds

  constructor(config: VerticalScalingConfig) {
    this.config = config
    this.alertThresholds = {
      cpuCritical: 90,
      memoryCritical: 95,
      diskCritical: 95,
      networkCritical: 85
    }
  }

  // 监控资源使用
  startMonitoring(): void {
    setInterval(async () => {
      const metrics = await this.collectMetrics()
      this.analyzeMetrics(metrics)
      this.updateHistory(metrics)
    }, this.config.monitoringInterval)
  }

  private async collectMetrics(): Promise<ResourceMetrics> {
    const [cpu, memory, disk, network] = await Promise.all([
      this.getCPUMetrics(),
      this.getMemoryMetrics(),
      this.getDiskMetrics(),
      this.getNetworkMetrics()
    ])

    return {
      timestamp: Date.now(),
      cpu,
      memory,
      disk,
      network
    }
  }

  private async getCPUMetrics(): Promise<CPUMetrics> {
    // 使用Node.js performance API或系统监控API
    const cpuUsage = process.cpuUsage()
    const hrtime = process.hrtime()

    return {
      usage: cpuUsage.user + cpuUsage.system,
      idle: cpuUsage.idle,
      percentage: ((cpuUsage.user + cpuUsage.system) / (cpuUsage.user + cpuUsage.system + cpuUsage.idle)) * 100,
      loadAverage: this.getLoadAverage()
    }
  }

  private async getMemoryMetrics(): Promise<MemoryMetrics> {
    const memUsage = process.memoryUsage()
    const totalMemory = require('os').totalmem()
    const freeMemory = require('os').freemem()

    return {
      used: memUsage.heapUsed,
      total: memUsage.heapTotal,
      external: memUsage.heapExternal,
      systemUsed: totalMemory - freeMemory,
      systemTotal: totalMemory,
      percentage: ((totalMemory - freeMemory) / totalMemory) * 100
    }
  }

  private async getDiskMetrics(): Promise<DiskMetrics> {
    const stats = await this.getDiskStats()
    return {
      used: stats.used,
      total: stats.total,
      available: stats.available,
      percentage: (stats.used / stats.total) * 100
    }
  }

  private async getNetworkMetrics(): Promise<NetworkMetrics> {
    const networkInterfaces = require('os').networkInterfaces()
    let totalBytesIn = 0
    let totalBytesOut = 0

    for (const interfaceName in networkInterfaces) {
      const networkInterface = networkInterfaces[interfaceName]
      for (const stat of networkInterface) {
        totalBytesIn += stat.rx_bytes
        totalBytesOut += stat.tx_bytes
      }
    }

    return {
      bytesIn: totalBytesIn,
      bytesOut: totalBytesOut,
      bandwidth: (totalBytesIn + totalBytesOut) / 1024 / 1024 // MB/s
    }
  }

  private getDiskStats(): Promise<{ used: number; total: number; available: number }> {
    return new Promise((resolve) => {
      require('child_process').exec('df -k', (error, stdout) => {
        if (error) {
          resolve({ used: 0, total: 0, available: 0 })
          return
        }

        const lines = stdout.split('\n')
        const dataLine = lines.find(line => line.startsWith('/dev/'))

        if (dataLine) {
          const parts = dataLine.split(/\s+/)
          resolve({
            total: parseInt(parts[1]) * 1024, // KB to bytes
            used: parseInt(parts[2]) * 1024,
            available: parseInt(parts[3]) * 1024
          })
        } else {
          resolve({ used: 0, total: 0, available: 0 })
        }
      })
    })
  }

  private getLoadAverage(): number[] {
    try {
      return require('os').loadavg()
    } catch {
      return [0, 0, 0]
    }
  }

  // 分析资源指标
  private analyzeMetrics(metrics: ResourceMetrics): void {
    // CPU分析
    if (metrics.cpu.percentage > this.alertThresholds.cpuCritical) {
      this.emitAlert('cpu_critical', {
        value: metrics.cpu.percentage,
        threshold: this.alertThresholds.cpuCritical,
        recommendation: this.getCPURecommendation(metrics)
      })
    }

    // 内存分析
    if (metrics.memory.percentage > this.alertThresholds.memoryCritical) {
      this.emitAlert('memory_critical', {
        value: metrics.memory.percentage,
        threshold: this.alertThresholds.memoryCritical,
        recommendation: this.getMemoryRecommendation(metrics)
      })
    }

    // 磁盘分析
    if (metrics.disk.percentage > this.alertThresholds.diskCritical) {
      this.emitAlert('disk_critical', {
        value: metrics.disk.percentage,
        threshold: this.alertThresholds.diskCritical,
        recommendation: this.getDiskRecommendation(metrics)
      })
    }

    // 网络分析
    if (metrics.network.bandwidth > this.alertThresholds.networkCritical) {
      this.emitAlert('network_critical', {
        value: metrics.network.bandwidth,
        threshold: this.alertThresholds.networkCritical,
        recommendation: this.getNetworkRecommendation(metrics)
      })
    }
  }

  private getCPURecommendation(metrics: ResourceMetrics): string {
    const recommendations = []

    if (metrics.cpu.percentage > 95) {
      recommendations.push('立即增加CPU核心数')
    } else if (metrics.cpu.percentage > 85) {
      recommendations.push('考虑增加CPU核心数')
    }

    if (metrics.cpu.loadAverage[0] > 2) {
      recommendations.push('系统负载过高，需要优化或增加资源')
    }

    return recommendations.join('; ')
  }

  private getMemoryRecommendation(metrics: ResourceMetrics): string {
    const recommendations = []

    if (metrics.memory.percentage > 95) {
      recommendations.push('立即增加内存容量')
    } else if (metrics.memory.percentage > 85) {
      recommendations.push('考虑增加内存容量')
    }

    if (metrics.memory.external > metrics.memory.total * 0.5) {
      recommendations.push('检查内存泄漏，优化代码')
    }

    return recommendations.join('; ')
  }

  private getDiskRecommendation(metrics: ResourceMetrics): string {
    const recommendations = []

    if (metrics.disk.percentage > 95) {
      recommendations.push('立即扩展磁盘空间')
    } else if (metrics.disk.percentage > 85) {
      recommendations.push('考虑扩展磁盘空间')
    }

    return recommendations.join('; ')
  }

  private getNetworkRecommendation(metrics: ResourceMetrics): string {
    const recommendations = []

    if (metrics.network.bandwidth > 1000) { // 1GB/s
      recommendations.push('考虑增加网络带宽')
    }

    return recommendations.join('; ')
  }

  private async emitAlert(type: string, data: any): Promise<void> {
    await fetch('/api/alerts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type,
        timestamp: Date.now(),
        data
      })
    })
  }

  private updateHistory(metrics: ResourceMetrics): void {
    this.resourceHistory.push(metrics)

    // 保留最近24小时的数据
    const twentyFourHoursAgo = Date.now() - (24 * 60 * 60 * 1000)
    this.resourceHistory = this.resourceHistory.filter(m => m.timestamp > twentyFourHoursAgo)
  }

  // 获取资源使用趋势
  getResourceTrends(hours: number = 1): ResourceTrends {
    const cutoffTime = Date.now() - (hours * 60 * 60 * 1000)
    const relevantHistory = this.resourceHistory.filter(m => m.timestamp > cutoffTime)

    if (relevantHistory.length < 2) {
      return {
        cpu: { trend: 'stable', growth: 0 },
        memory: { trend: 'stable', growth: 0 },
        disk: { trend: 'stable', growth: 0 },
        network: { trend: 'stable', growth: 0 }
      }
    }

    return {
      cpu: this.calculateTrend(relevantHistory.map(m => m.cpu)),
      memory: this.calculateTrend(relevantHistory.map(m => m.memory)),
      disk: this.calculateTrend(relevantHistory.map(m => m.disk)),
      network: this.calculateTrend(relevantHistory.map(m => m.network))
    }
  }

  private calculateTrend(values: any[]): { trend: 'increasing' | 'decreasing' | 'stable'; growth: number } {
    if (values.length < 2) {
      return { trend: 'stable', growth: 0 }
    }

    const firstValue = values[0].percentage || values[0].bandwidth || 0
    const lastValue = values[values.length - 1].percentage || values[values.length - 1].bandwidth || 0

    const growth = ((lastValue - firstValue) / firstValue) * 100

    let trend: 'increasing' | 'decreasing' | 'stable'
    if (Math.abs(growth) < 5) {
      trend = 'stable'
    } else if (growth > 0) {
      trend = 'increasing'
    } else {
      trend = 'decreasing'
    }

    return { trend, growth }
  }
}

interface ResourceMetrics {
  timestamp: number
  cpu: CPUMetrics
  memory: MemoryMetrics
  disk: DiskMetrics
  network: NetworkMetrics
}

interface CPUMetrics {
  usage: number
  idle: number
  percentage: number
  loadAverage: number[]
}

interface MemoryMetrics {
  used: number
  total: number
  external: number
  systemUsed: number
  systemTotal: number
  percentage: number
}

interface DiskMetrics {
  used: number
  total: number
  available: number
  percentage: number
}

interface NetworkMetrics {
  bytesIn: number
  bytesOut: number
  bandwidth: number
}

interface ResourceTrends {
  cpu: { trend: 'increasing' | 'decreasing' | 'stable'; growth: number }
  memory: { trend: 'increasing' | 'decreasing' | 'stable'; growth: number }
  disk: { trend: 'increasing' | 'decreasing' | 'stable'; growth: number }
  network: { trend: 'increasing' | 'decreasing' | 'stable'; growth: number }
}

interface AlertThresholds {
  cpuCritical: number
  memoryCritical: number
  diskCritical: number
  networkCritical: number
}

export const verticalScalingManager = new VerticalScalingManager({
  maxCPU: 8, // 8 cores
  maxMemory: 32 * 1024, // 32GB
  maxStorage: 1000, // 1TB
  maxBandwidth: 1000, // 1Gbps
  monitoringInterval: 30000, // 30 seconds
  scaleUpThreshold: 0.8,
  scaleDownThreshold: 0.3
})
```

## 🌐 负载均衡和CDN

### ⚖️ 智能负载均衡器

```typescript
// app/lib/load-balancing/intelligent-load-balancer.ts
interface LoadBalancerConfig {
  algorithm: 'round-robin' | 'weighted-round-robin' | 'least-connections' | 'least-response-time' | 'health-aware'
  healthCheckInterval: number
  maxRetries: number
  timeout: number
  stickySessions: boolean
  sessionAffinity: 'cookie' | 'ip' | 'header'
}

interface BackendServer {
  id: string
  url: string
  weight: number
  maxConnections: number
  currentConnections: number
  health: 'healthy' | 'unhealthy' | 'unknown'
  responseTime: number
  lastHealthCheck: number
  region: string
  availability: number
}

class IntelligentLoadBalancer {
  private config: LoadBalancerConfig
  private servers: BackendServer[] = []
  private connectionPool: Map<string, Connection[]> = new Map()
  private healthChecker: HealthChecker

  constructor(config: LoadBalancerConfig) {
    this.config = config
    this.healthChecker = new HealthChecker(config.healthCheckInterval)
  }

  // 添加后端服务器
  addServer(server: BackendServer): void {
    this.servers.push(server)
    this.connectionPool.set(server.id, [])
    this.healthChecker.startMonitoring(server)
  }

  // 移除后端服务器
  removeServer(serverId: string): void {
    this.servers = this.servers.filter(s => s.id !== serverId)
    this.connectionPool.delete(serverId)
    this.healthChecker.stopMonitoring(serverId)
  }

  // 智能请求路由
  async routeRequest(request: IncomingRequest): Promise<BackendResponse> {
    const healthyServers = this.getHealthyServers()

    if (healthyServers.length === 0) {
      throw new Error('No healthy servers available')
    }

    let selectedServer: BackendServer

    switch (this.config.algorithm) {
      case 'weighted-round-robin':
        selectedServer = this.selectWeightedRoundRobin(healthyServers)
        break
      case 'least-connections':
        selectedServer = this.selectLeastConnections(healthyServers)
        break
      case 'least-response-time':
        selectedServer = this.selectLeastResponseTime(healthyServers)
        break
      case 'health-aware':
        selectedServer = this.selectHealthAware(healthyServers)
        break
      default:
        selectedServer = this.selectRoundRobin(healthyServers)
    }

    // 处理会话粘性
    if (this.config.stickySessions) {
      const stickyServer = this.getStickyServer(request)
      if (stickyServer && this.isServerHealthy(stickyServer)) {
        selectedServer = stickyServer
      }
    }

    // 执行请求
    return await this.executeRequest(selectedServer, request)
  }

  // 健康感知选择
  private selectHealthAware(servers: BackendServer[]): BackendServer {
    return servers.reduce((best, current) => {
      const bestScore = this.calculateHealthScore(best)
      const currentScore = this.calculateHealthScore(current)
      return currentScore > bestScore ? current : best
    })
  }

  private calculateHealthScore(server: BackendServer): number {
    const healthWeight = 0.6
    const responseTimeWeight = 0.3
    const availabilityWeight = 0.1

    const healthScore = server.health === 'healthy' ? 1 : 0
    const responseTimeScore = Math.max(0, 1 - (server.responseTime / 5000)) // 5秒基准
    const availabilityScore = server.availability / 100

    return (healthScore * healthWeight) +
           (responseTimeScore * responseTimeWeight) +
           (availabilityScore * availabilityWeight)
  }

  // 加权轮询选择
  private selectWeightedRoundRobin(servers: BackendServer[]): BackendServer {
    const totalWeight = servers.reduce((sum, server) => sum + server.weight, 0)
    let random = Math.random() * totalWeight

    for (const server of servers) {
      random -= server.weight
      if (random <= 0) {
        return server
      }
    }

    return servers[0] // 降级到第一个服务器
  }

  // 最少连接选择
  private selectLeastConnections(servers: BackendServer[]): BackendServer {
    return servers.reduce((least, current) =>
      current.currentConnections < least.currentConnections ? current : least
    )
  }

  // 最少响应时间选择
  private selectLeastResponseTime(servers: BackendServer[]): BackendServer {
    return servers.reduce((fastest, current) =>
      current.responseTime < fastest.responseTime ? current : fastest
    )
  }

  // 轮询选择
  private selectRoundRobin(servers: BackendServer[]): BackendServer {
    return servers[0] // 简化实现，实际需要维护轮询索引
  }

  // 会话粘性服务器选择
  private getStickyServer(request: IncomingRequest): BackendServer | null {
    let sessionId: string | null = null

    switch (this.config.sessionAffinity) {
      case 'cookie':
        sessionId = this.extractSessionFromCookie(request)
        break
      case 'ip':
        sessionId = request.ip
        break
      case 'header':
        sessionId = this.extractSessionFromHeader(request)
        break
    }

    if (!sessionId) {
      return null
    }

    const sessionMap = this.getSessionMap()
    const serverId = sessionMap[sessionId]

    return this.servers.find(s => s.id === serverId) || null
  }

  private extractSessionFromCookie(request: IncomingRequest): string | null {
    const cookies = this.parseCookies(request.headers.cookie || '')
    return cookies.session_id || null
  }

  private extractSessionFromHeader(request: IncomingRequest): string | null {
    return request.headers['x-session-id'] as string || null
  }

  private parseCookies(cookieHeader: string): Record<string, string> {
    const cookies: Record<string, string> = {}
    cookieHeader.split(';').forEach(cookie => {
      const [name, value] = cookie.trim().split('=')
      if (name && value) {
        cookies[name] = value
      }
    })
    return cookies
  }

  private getSessionMap(): Record<string, string> {
    // 从Redis或内存中获取会话映射
    return {} // 实现需要连接会话存储
  }

  // 执行请求
  private async executeRequest(server: BackendServer, request: IncomingRequest): Promise<BackendResponse> {
    const startTime = Date.now()

    try {
      // 更新连接数
      server.currentConnections++

      // 转发请求
      const response = await this.forwardRequest(server, request)

      // 更新响应时间
      server.responseTime = Date.now() - startTime

      return response

    } catch (error) {
      // 标记服务器为不健康
      server.health = 'unhealthy'
      server.responseTime = Date.now() - startTime

      throw error
    } finally {
      server.currentConnections--
    }
  }

  private async forwardRequest(server: BackendServer, request: IncomingRequest): Promise<BackendResponse> {
    const proxyOptions = {
      method: request.method,
      headers: {
        ...request.headers,
        'X-Forwarded-For': request.ip,
        'X-Forwarded-Proto': request.protocol,
        'X-Forwarded-Host': request.headers.host
      },
      timeout: this.config.timeout,
      followRedirects: false
    }

    const response = await fetch(`${server.url}${request.path}`, proxyOptions)

    return {
      status: response.status,
      headers: Object.fromEntries(response.headers.entries()),
      body: await response.text()
    }
  }

  // 获取健康服务器
  private getHealthyServers(): BackendServer[] {
    return this.servers.filter(server => server.health === 'healthy')
  }

  private isServerHealthy(server: BackendServer): boolean {
    return server.health === 'healthy' &&
           server.currentConnections < server.maxConnections
  }

  // 启动负载均衡器
  startHealthChecking(): void {
    setInterval(() => {
      this.updateServerHealth()
    }, this.config.healthCheckInterval)
  }

  private async updateServerHealth(): Promise<void> {
    for (const server of this.servers) {
      try {
        const isHealthy = await this.healthChecker.checkHealth(server)
        server.health = isHealthy ? 'healthy' : 'unhealthy'
        server.lastHealthCheck = Date.now()
      } catch (error) {
        server.health = 'unhealthy'
        server.lastHealthCheck = Date.now()
      }
    }
  }
}

// 健康检查器
class HealthChecker {
  private interval: number
  private monitoringTasks: Map<string, NodeJS.Timeout> = new Map()

  constructor(interval: number) {
    this.interval = interval
  }

  startMonitoring(server: BackendServer): void {
    if (this.monitoringTasks.has(server.id)) {
      return // 已经在监控
    }

    const task = setInterval(async () => {
      await this.performHealthCheck(server)
    }, this.interval)

    this.monitoringTasks.set(server.id, task)
  }

  stopMonitoring(serverId: string): void {
    const task = this.monitoringTasks.get(serverId)
    if (task) {
      clearInterval(task)
      this.monitoringTasks.delete(serverId)
    }
  }

  private async performHealthCheck(server: BackendServer): Promise<boolean> {
    try {
      const healthUrl = `${server.url}/health`
      const response = await fetch(healthUrl, {
        method: 'GET',
        timeout: 5000,
        headers: {
          'User-Agent': 'HealthChecker/1.0'
        }
      })

      return response.ok && response.status === 200
    } catch (error) {
      return false
    }
  }

  async checkHealth(server: BackendServer): Promise<boolean> {
    return await this.performHealthCheck(server)
  }
}

interface IncomingRequest {
  method: string
  path: string
  protocol: string
  headers: Record<string, string>
  ip: string
  body?: string
}

interface BackendResponse {
  status: number
  headers: Record<string, string>
  body: string
}

export const intelligentLoadBalancer = new IntelligentLoadBalancer({
  algorithm: 'health-aware',
  healthCheckInterval: 30000, // 30秒
  maxRetries: 3,
  timeout: 10000, // 10秒
  stickySessions: true,
  sessionAffinity: 'cookie'
})
```

## 🔄 文档交叉引用

### 相关文档
- 📄 **[Web安全最佳实践](../security/01-security-best-practices.md)**: 深入了解扩展架构中的安全考量
- 📄 **[高级性能调优](../performance/02-advanced-optimization.md)**: 学习性能优化与扩展的关系
- 📄 **[微前端架构](./02-micro-frontends.md)**: 深入了解前端模块化架构

### 参考章节
- 📖 **[本模块其他章节]**: [微前端架构](./02-micro-frontends.md)中的模块化扩展设计
- 📖 **[其他模块相关内容]**: [GraphQL + Apollo](./api-integration/01-graphql-apollo.md)中的API扩展策略

## 📝 总结

### 核心要点回顾
1. **架构演进策略**: 从单体到分布式系统的渐进式扩展方法
2. **水平扩展模式**: 自动扩缩决策算法、健康检查、负载均衡策略
3. **垂直扩展优化**: 资源监控、智能告警、自动扩容机制
4. **负载均衡架构**: 多种算法、健康感知、会话粘性、故障转移
5. **CDN和缓存**: 全球内容分发、边缘计算、多层缓存策略

### 学习成果检查
- [ ] 是否理解了不同扩展架构模式的适用场景？
- [ ] 是否能够设计自动扩缩系统？
- [ ] 是否掌握了负载均衡和故障转移技术？
- [ ] 是否能够构建全球CDN架构？
- [ ] 是否具备了大规模系统架构设计能力？

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
- 🏗️ **[AWS架构中心](https://aws.amazon.com/architecture/)**: 云架构最佳实践
- ⚡ **[Azure架构中心](https://docs.microsoft.com/azure/architecture/)**: Azure云架构指南
- 🌐 **[Google Cloud架构](https://cloud.google.com/architecture/)**: Google云架构框架

### 🛠️ 工具和平台
- ⚖️ **[Kubernetes](https://kubernetes.io/)**: 容器编排平台
- 🔗 **[Consul](https://www.consul.io/)**: 服务发现和配置工具
- 🌐 **[Envoy](https://www.envoyproxy.io/)**: 高性能代理和通信总线
- 📊 **[Istio](https://istio.io/)**: 服务网格平台

### 📱 扩展参考
- 📈 **[微服务模式](https://microservices.io/)**: 微服务架构模式指南
- 🏛️ **[12-Factor App](https://12factor.net/)**: 云原生应用原则
- 🔧 **[DevOps手册](https://www.devopshandbook.com/)**: DevOps最佳实践
- 📊 **[SRE Book](https://sre.google/sre-book/)**: 网站可靠性工程

---

**文档状态**: ✅ 已完成 | 🚧 进行中 | 📋 计划中
**最后更新**: 2025年10月
**版本**: v1.0.0