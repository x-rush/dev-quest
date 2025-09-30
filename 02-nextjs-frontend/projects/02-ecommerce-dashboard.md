# 02 - 电商仪表板实战项目

## 目录

1. [项目概述](#项目概述)
2. [技术架构](#技术架构)
3. [项目结构](#项目结构)
4. [核心功能实现](#核心功能实现)
5. [数据可视化](#数据可视化)
6. [性能优化](#性能优化)
7. [安全性考虑](#安全性考虑)
8. [部署配置](#部署配置)
9. [扩展功能](#扩展功能)
10. [总结](#总结)

## 项目概述

构建一个功能完整的电商管理仪表板，包含销售分析、库存管理、订单处理、用户管理等核心功能。

### 功能特性

- **实时销售监控**: 销售额、订单量、转化率实时监控
- **数据分析**: 销售趋势、用户行为、产品表现分析
- **库存管理**: 库存预警、补货建议、供应商管理
- **订单处理**: 订单状态管理、退款处理、物流跟踪
- **用户管理**: 用户行为分析、客户细分、营销活动
- **财务报表**: 收入报表、成本分析、利润统计
- **多维度过滤**: 时间、地区、产品类别过滤
- **响应式设计**: 移动端适配，平板端优化

### 与传统PHP电商系统的对比

**传统PHP电商后台：**
- 页面刷新式交互
- 有限的实时数据更新
- 依赖jQuery和传统图表库
- 服务器端渲染压力

**Next.js电商仪表板：**
- 实时数据流更新
- 动态图表和交互
- 现代可视化库集成
- 客户端渲染优化

## 技术架构

### 前端技术栈

```typescript
// package.json 核心依赖
{
  "dependencies": {
    "next": "15.0.0",
    "react": "19.0.0",
    "react-dom": "19.0.0",
    "typescript": "5.0.0",

    // 状态管理
    "zustand": "^4.4.0",
    "@tanstack/react-query": "^5.0.0",

    // 数据可视化
    "recharts": "^2.8.0",
    "d3": "^7.8.0",
    "@visx/scale": "^3.5.0",

    // UI组件
    "@radix-ui/react-dialog": "^1.0.0",
    "@radix-ui/react-dropdown-menu": "^2.0.0",
    "@radix-ui/react-tabs": "^1.0.0",
    "lucide-react": "^0.292.0",

    // 表单处理
    "react-hook-form": "^7.47.0",
    "zod": "^3.22.0",

    // 日期处理
    "date-fns": "^2.30.0",
    "dayjs": "^1.11.0",

    // 实时数据
    "socket.io-client": "^4.7.0"
  }
}
```

### 数据层设计

```typescript
// lib/api/ecommerce.ts
import { createApi } from './core'

export const ecommerceApi = createApi('/api/ecommerce', {
  // 销售数据
  sales: {
    getOverview: (params: SalesParams) =>
      ecommerceApi.get('/sales/overview', { params }),
    getTrends: (params: TrendParams) =>
      ecommerceApi.get('/sales/trends', { params }),
    getTopProducts: (params: PaginationParams) =>
      ecommerceApi.get('/sales/top-products', { params }),
    getRevenueByCategory: (params: DateRangeParams) =>
      ecommerceApi.get('/sales/revenue-by-category', { params }),
  },

  // 订单管理
  orders: {
    getList: (params: OrderFilters) =>
      ecommerceApi.get('/orders', { params }),
    getById: (id: string) =>
      ecommerceApi.get(`/orders/${id}`),
    updateStatus: (id: string, status: OrderStatus) =>
      ecommerceApi.patch(`/orders/${id}/status`, { status }),
    processRefund: (id: string, data: RefundData) =>
      ecommerceApi.post(`/orders/${id}/refund`, data),
  },

  // 库存管理
  inventory: {
    getProducts: (params: InventoryFilters) =>
      ecommerceApi.get('/inventory', { params }),
    updateStock: (id: string, quantity: number) =>
      ecommerceApi.patch(`/inventory/${id}/stock`, { quantity }),
    getLowStock: () =>
      ecommerceApi.get('/inventory/low-stock'),
    getStockAlerts: () =>
      ecommerceApi.get('/inventory/alerts'),
  },

  // 用户分析
  analytics: {
    getUserBehavior: (params: DateRangeParams) =>
      ecommerceApi.get('/analytics/user-behavior', { params }),
    getCohortAnalysis: (params: CohortParams) =>
      ecommerceApi.get('/analytics/cohort', { params }),
    getCustomerSegments: () =>
      ecommerceApi.get('/analytics/customer-segments'),
  }
})
```

## 项目结构

```
ecommerce-dashboard/
├── app/
│   ├── (dashboard)/
│   │   ├── overview/
│   │   ├── sales/
│   │   ├── orders/
│   │   ├── inventory/
│   │   ├── customers/
│   │   ├── analytics/
│   │   └── layout.tsx
│   ├── api/
│   │   ├── ecommerce/
│   │   │   ├── sales/
│   │   │   ├── orders/
│   │   │   ├── inventory/
│   │   │   └── analytics/
│   │   └── webhooks/
│   ├── globals.css
│   └── layout.tsx
├── components/
│   ├── dashboard/
│   │   ├── charts/
│   │   ├── metrics/
│   │   ├── tables/
│   │   └── filters/
│   ├── inventory/
│   ├── orders/
│   ├── analytics/
│   └── shared/
├── hooks/
│   ├── use-analytics.ts
│   ├── use-realtime-data.ts
│   └── use-export-data.ts
├── lib/
│   ├── api/
│   ├── utils/
│   ├── validations/
│   └── constants/
├── store/
│   ├── dashboard.ts
│   ├── orders.ts
│   └── inventory.ts
├── types/
│   ├── ecommerce.ts
│   └── analytics.ts
└── public/
```

## 核心功能实现

### 1. 实时仪表板主页面

```typescript
// app/(dashboard)/overview/page.tsx
"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { DateRangePicker } from "@/components/shared/date-range-picker"
import { MetricCard } from "@/components/dashboard/metrics/metric-card"
import { RevenueChart } from "@/components/dashboard/charts/revenue-chart"
import { SalesTrendChart } from "@/components/dashboard/charts/sales-trend-chart"
import { TopProductsTable } from "@/components/dashboard/tables/top-products-table"
import { ActivityFeed } from "@/components/dashboard/activity-feed"
import { RealTimeAlerts } from "@/components/dashboard/real-time-alerts"
import { useDashboardStore } from "@/store/dashboard"
import { useRealTimeData } from "@/hooks/use-realtime-data"
import { formatCurrency, formatNumber } from "@/lib/utils"
import { TrendingUp, TrendingDown, AlertTriangle, Users, ShoppingCart, DollarSign } from "lucide-react"

export default function OverviewPage() {
  const [selectedPeriod, setSelectedPeriod] = useState("30d")
  const [isLoading, setIsLoading] = useState(true)

  const {
    metrics,
    trends,
    setMetrics,
    setTrends,
    lastUpdated
  } = useDashboardStore()

  // 实时数据订阅
  const { data: realTimeData } = useRealTimeData('dashboard-metrics')

  useEffect(() => {
    if (realTimeData) {
      setMetrics(realTimeData.metrics)
      setTrends(realTimeData.trends)
    }
  }, [realTimeData, setMetrics, setTrends])

  const metricCards = [
    {
      title: "Total Revenue",
      value: metrics.totalRevenue,
      change: metrics.revenueChange,
      icon: DollarSign,
      format: "currency",
    },
    {
      title: "Orders",
      value: metrics.totalOrders,
      change: metrics.ordersChange,
      icon: ShoppingCart,
      format: "number",
    },
    {
      title: "Customers",
      value: metrics.totalCustomers,
      change: metrics.customersChange,
      icon: Users,
      format: "number",
    },
    {
      title: "Conversion Rate",
      value: metrics.conversionRate,
      change: metrics.conversionChange,
      icon: TrendingUp,
      format: "percentage",
    },
  ]

  return (
    <div className="space-y-6">
      {/* 头部控制栏 */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">Dashboard Overview</h1>
          <p className="text-muted-foreground">
            Last updated: {new Date(lastUpdated).toLocaleString()}
          </p>
        </div>

        <div className="flex gap-2">
          <DateRangePicker />
          <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
            <SelectTrigger className="w-[180px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
              <SelectItem value="1y">Last year</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* 实时警报 */}
      <RealTimeAlerts />

      {/* 关键指标卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metricCards.map((metric) => (
          <MetricCard
            key={metric.title}
            title={metric.title}
            value={metric.value}
            change={metric.change}
            icon={metric.icon}
            format={metric.format}
          />
        ))}
      </div>

      {/* 主要内容区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* 收入图表 */}
          <Card>
            <CardHeader>
              <CardTitle>Revenue Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <RevenueChart data={trends.revenue} period={selectedPeriod} />
            </CardContent>
          </Card>

          {/* 销售趋势 */}
          <Card>
            <CardHeader>
              <CardTitle>Sales Trends</CardTitle>
            </CardHeader>
            <CardContent>
              <SalesTrendChart data={trends.sales} period={selectedPeriod} />
            </CardContent>
          </Card>

          {/* 热门产品 */}
          <Card>
            <CardHeader>
              <CardTitle>Top Products</CardTitle>
            </CardHeader>
            <CardContent>
              <TopProductsTable products={trends.topProducts} />
            </CardContent>
          </Card>
        </div>

        {/* 侧边栏 */}
        <div className="space-y-6">
          {/* 活动动态 */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <ActivityFeed activities={metrics.recentActivity} />
            </CardContent>
          </Card>

          {/* 库存警报 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-orange-500" />
                Low Stock Alerts
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {metrics.lowStockItems.slice(0, 5).map((item) => (
                  <div key={item.id} className="flex justify-between items-center">
                    <div>
                      <p className="font-medium">{item.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {item.stock} units left
                      </p>
                    </div>
                    <Badge variant="destructive">
                      {item.daysUntilStockout}d
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
```

### 2. 销售分析页面

```typescript
// app/(dashboard)/sales/page.tsx
"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { DateRangePicker } from "@/components/shared/date-range-picker"
import { SalesFunnelChart } from "@/components/dashboard/charts/sales-funnel-chart"
import { RevenueByCategoryChart } from "@/components/dashboard/charts/revenue-by-category-chart"
import { CustomerAcquisitionChart } from "@/components/dashboard/charts/customer-acquisition-chart"
import { GeographicHeatmap } from "@/components/dashboard/charts/geographic-heatmap"
import { SalesPerformanceTable } from "@/components/dashboard/tables/sales-performance-table"
import { ExportButton } from "@/components/shared/export-button"
import { useSalesAnalytics } from "@/hooks/use-analytics"
import { Download, Filter, Calendar } from "lucide-react"

export default function SalesPage() {
  const [selectedPeriod, setSelectedPeriod] = useState("30d")
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [selectedRegion, setSelectedRegion] = useState("all")

  const { data: salesData, isLoading } = useSalesAnalytics({
    period: selectedPeriod,
    category: selectedCategory,
    region: selectedRegion,
  })

  return (
    <div className="space-y-6">
      {/* 头部控制 */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">Sales Analytics</h1>
          <p className="text-muted-foreground">
            Comprehensive sales performance analysis
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <DateRangePicker />
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="Category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Categories</SelectItem>
              <SelectItem value="electronics">Electronics</SelectItem>
              <SelectItem value="clothing">Clothing</SelectItem>
              <SelectItem value="home">Home & Garden</SelectItem>
            </SelectContent>
          </Select>

          <Select value={selectedRegion} onValueChange={setSelectedRegion}>
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="Region" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Regions</SelectItem>
              <SelectItem value="north-america">North America</SelectItem>
              <SelectItem value="europe">Europe</SelectItem>
              <SelectItem value="asia">Asia</SelectItem>
            </SelectContent>
          </Select>

          <ExportButton
            data={salesData}
            filename="sales-analytics"
            format="csv"
          />
        </div>
      </div>

      {/* 关键指标概览 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${salesData?.totalRevenue?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              +12.5% from last period
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Conversion Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {salesData?.conversionRate || '0'}%
            </div>
            <p className="text-xs text-muted-foreground">
              +2.1% from last period
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Avg Order Value</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${salesData?.avgOrderValue?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              +5.3% from last period
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Customer Lifetime</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${salesData?.customerLifetimeValue?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              +8.7% from last period
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 详细分析标签页 */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="funnel">Sales Funnel</TabsTrigger>
          <TabsTrigger value="categories">Categories</TabsTrigger>
          <TabsTrigger value="geography">Geography</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Revenue Trend</CardTitle>
              </CardHeader>
              <CardContent>
                <RevenueByCategoryChart data={salesData?.revenueByCategory} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Customer Acquisition</CardTitle>
              </CardHeader>
              <CardContent>
                <CustomerAcquisitionChart data={salesData?.customerAcquisition} />
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Sales Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <SalesPerformanceTable data={salesData?.salesPerformance} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="funnel" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Sales Funnel Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <SalesFunnelChart data={salesData?.salesFunnel} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="categories" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Revenue by Category</CardTitle>
            </CardHeader>
            <CardContent>
              <RevenueByCategoryChart data={salesData?.revenueByCategory} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="geography" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Geographic Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <GeographicHeatmap data={salesData?.geographicData} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
```

### 3. 订单管理系统

```typescript
// app/(dashboard)/orders/page.tsx
"use client"

import { useState, useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { OrderDetails } from "@/components/orders/order-details"
import { OrderFilters } from "@/components/orders/order-filters"
import { useOrders } from "@/hooks/use-orders"
import { formatCurrency, formatDateTime } from "@/lib/utils"
import { Search, Eye, Package, Truck, CheckCircle, XCircle, Clock } from "lucide-react"
import type { Order, OrderStatus } from "@/types/ecommerce"

const statusConfig = {
  pending: { icon: Clock, color: "bg-yellow-100 text-yellow-800", label: "Pending" },
  processing: { icon: Package, color: "bg-blue-100 text-blue-800", label: "Processing" },
  shipped: { icon: Truck, color: "bg-purple-100 text-purple-800", label: "Shipped" },
  delivered: { icon: CheckCircle, color: "bg-green-100 text-green-800", label: "Delivered" },
  cancelled: { icon: XCircle, color: "bg-red-100 text-red-800", label: "Cancelled" },
}

export default function OrdersPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<OrderStatus | "all">("all")
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)

  const { data: orders, isLoading } = useOrders()

  // 过滤和搜索订单
  const filteredOrders = useMemo(() => {
    if (!orders) return []

    return orders.filter(order => {
      const matchesSearch =
        order.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        order.customer.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        order.customer.name.toLowerCase().includes(searchTerm.toLowerCase())

      const matchesStatus = statusFilter === "all" || order.status === statusFilter

      return matchesSearch && matchesStatus
    })
  }, [orders, searchTerm, statusFilter])

  const getStatusBadge = (status: OrderStatus) => {
    const config = statusConfig[status]
    const Icon = config.icon

    return (
      <Badge className={config.color}>
        <Icon className="w-3 h-3 mr-1" />
        {config.label}
      </Badge>
    )
  }

  return (
    <div className="space-y-6">
      {/* 头部 */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">Order Management</h1>
          <p className="text-muted-foreground">
            Manage and track customer orders
          </p>
        </div>

        <Button>
          Create New Order
        </Button>
      </div>

      {/* 订单统计概览 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {Object.entries(statusConfig).map(([status, config]) => {
          const count = orders?.filter(o => o.status === status).length || 0
          const Icon = config.icon

          return (
            <Card key={status}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {config.label}
                </CardTitle>
                <Icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{count}</div>
                <p className="text-xs text-muted-foreground">
                  {count} orders
                </p>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* 搜索和过滤 */}
      <Card>
        <CardHeader>
          <CardTitle>Order List</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search orders by ID, customer name, or email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            <Select value={statusFilter} onValueChange={(value) => setStatusFilter(value as OrderStatus | "all")}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                {Object.entries(statusConfig).map(([status, config]) => (
                  <SelectItem key={status} value={status}>
                    {config.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 订单表格 */}
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Order ID</TableHead>
                <TableHead>Customer</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Total</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredOrders.map((order) => (
                <TableRow key={order.id}>
                  <TableCell className="font-medium">
                    #{order.id.slice(-8)}
                  </TableCell>
                  <TableCell>
                    <div>
                      <div className="font-medium">{order.customer.name}</div>
                      <div className="text-sm text-gray-500">
                        {order.customer.email}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    {formatDateTime(order.createdAt)}
                  </TableCell>
                  <TableCell>
                    {getStatusBadge(order.status)}
                  </TableCell>
                  <TableCell className="font-medium">
                    {formatCurrency(order.total)}
                  </TableCell>
                  <TableCell>
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedOrder(order)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-4xl">
                        <DialogHeader>
                          <DialogTitle>Order Details - #{order.id.slice(-8)}</DialogTitle>
                        </DialogHeader>
                        <OrderDetails order={order} />
                      </DialogContent>
                    </Dialog>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {filteredOrders.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No orders found matching your criteria
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
```

## 数据可视化

### 1. 自定义图表组件

```typescript
// components/dashboard/charts/revenue-chart.tsx
"use client"

import { useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
  BarChart,
  Bar,
} from "recharts"
import { useTheme } from "next-themes"
import { formatCurrency } from "@/lib/utils"

interface RevenueChartProps {
  data: Array<{
    date: string
    revenue: number
    orders: number
    profit: number
  }>
  period: string
  chartType?: "line" | "area" | "bar"
}

export function RevenueChart({ data, period, chartType = "line" }: RevenueChartProps) {
  const { theme } = useTheme()

  const chartData = useMemo(() => {
    if (!data) return []

    return data.map(item => ({
      ...item,
      formattedDate: new Date(item.date).toLocaleDateString('en-US', {
        month: 'short',
        day: period === '7d' ? 'numeric' : undefined,
      }),
    }))
  }, [data, period])

  const renderChart = () => {
    switch (chartType) {
      case "area":
        return (
          <AreaChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="formattedDate" />
            <YAxis tickFormatter={(value) => `$${value/1000}k`} />
            <Tooltip
              formatter={(value: number, name: string) => [
                formatCurrency(value),
                name === 'revenue' ? 'Revenue' : name === 'profit' ? 'Profit' : 'Orders'
              ]}
            />
            <Area
              type="monotone"
              dataKey="revenue"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.1}
              strokeWidth={2}
            />
            <Area
              type="monotone"
              dataKey="profit"
              stroke="#10b981"
              fill="#10b981"
              fillOpacity={0.1}
              strokeWidth={2}
            />
          </AreaChart>
        )

      case "bar":
        return (
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="formattedDate" />
            <YAxis tickFormatter={(value) => `$${value/1000}k`} />
            <Tooltip
              formatter={(value: number) => [formatCurrency(value), 'Revenue']}
            />
            <Bar dataKey="revenue" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          </BarChart>
        )

      default:
        return (
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="formattedDate" />
            <YAxis tickFormatter={(value) => `$${value/1000}k`} />
            <Tooltip
              formatter={(value: number, name: string) => [
                formatCurrency(value),
                name === 'revenue' ? 'Revenue' : name === 'profit' ? 'Profit' : 'Orders'
              ]}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="revenue"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
            />
            <Line
              type="monotone"
              dataKey="profit"
              stroke="#10b981"
              strokeWidth={2}
              dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
            />
          </LineChart>
        )
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Revenue Trend</h3>
        <Select value={chartType} onValueChange={(value) => {
          // Handle chart type change
        }}>
          <SelectTrigger className="w-[120px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="line">Line</SelectItem>
            <SelectItem value="area">Area</SelectItem>
            <SelectItem value="bar">Bar</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          {renderChart()}
        </ResponsiveContainer>
      </div>
    </div>
  )
}
```

### 2. 实时数据图表

```typescript
// components/dashboard/charts/realtime-chart.tsx
"use client"

import { useEffect, useState, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"
import { useTheme } from "next-themes"
import { useRealTimeData } from "@/hooks/use-realtime-data"

interface RealTimeChartProps {
  metric: 'orders' | 'revenue' | 'visitors'
  title: string
  color?: string
}

export function RealTimeChart({ metric, title, color = '#3b82f6' }: RealTimeChartProps) {
  const [chartData, setChartData] = useState<Array<{ time: string; value: number }>>([])
  const maxDataPoints = 50

  const { data: realTimeData } = useRealTimeData(`realtime-${metric}`)

  useEffect(() => {
    if (realTimeData) {
      const now = new Date()
      const timeString = now.toLocaleTimeString()

      setChartData(prev => {
        const newData = [...prev, { time: timeString, value: realTimeData.value }]

        // 保持数据点数量限制
        return newData.length > maxDataPoints ? newData.slice(-maxDataPoints) : newData
      })
    }
  }, [realTimeData])

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          {title}
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-sm text-gray-500">Live</span>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[200px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
              <XAxis
                dataKey="time"
                tickFormatter={(value) => {
                  const date = new Date(`1970-01-01T${value}`)
                  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                }}
              />
              <YAxis />
              <Tooltip
                labelFormatter={(value) => `Time: ${value}`}
                formatter={(value: number) => [value.toLocaleString(), title]}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke={color}
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
```

## 性能优化

### 1. 数据获取优化

```typescript
// hooks/use-analytics.ts
import { useQuery, useInfiniteQuery } from '@tanstack/react-query'
import { analyticsApi } from '@/lib/api/analytics'

// 基础分析数据查询
export function useAnalytics(params: AnalyticsParams) {
  return useQuery({
    queryKey: ['analytics', params],
    queryFn: () => analyticsApi.getOverview(params),
    staleTime: 5 * 60 * 1000, // 5分钟
    cacheTime: 10 * 60 * 1000, // 10分钟
    refetchOnWindowFocus: false,
  })
}

// 无限滚动分页数据
export function useInfiniteAnalytics(params: AnalyticsParams) {
  return useInfiniteQuery({
    queryKey: ['analytics-infinite', params],
    queryFn: ({ pageParam = 1 }) =>
      analyticsApi.getDetailedData({ ...params, page: pageParam }),
    getNextPageParam: (lastPage) => lastPage.hasNextPage ? lastPage.nextPage : undefined,
    staleTime: 5 * 60 * 1000,
  })
}

// 实时数据订阅
export function useRealTimeAnalytics(eventType: string) {
  const [data, setData] = useState(null)

  useEffect(() => {
    const eventSource = new EventSource(`/api/analytics/stream/${eventType}`)

    eventSource.onmessage = (event) => {
      const newData = JSON.parse(event.data)
      setData(newData)
    }

    eventSource.onerror = (error) => {
      console.error('EventSource error:', error)
      eventSource.close()
    }

    return () => {
      eventSource.close()
    }
  }, [eventType])

  return { data }
}
```

### 2. 组件性能优化

```typescript
// components/dashboard/metrics/metric-card.tsx
"use client"

import { memo } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { TrendingUp, TrendingDown } from "lucide-react"
import { formatValue } from "@/lib/utils"

interface MetricCardProps {
  title: string
  value: number
  change?: number
  icon: React.ComponentType<{ className?: string }>
  format?: "currency" | "number" | "percentage"
}

export const MetricCard = memo(function MetricCard({
  title,
  value,
  change,
  icon: Icon,
  format = "number",
}: MetricCardProps) {
  const formattedValue = formatValue(value, format)
  const isPositive = change && change > 0

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-2xl font-bold">{formattedValue}</p>
            {change !== undefined && (
              <div className={`flex items-center mt-1 text-sm ${
                isPositive ? 'text-green-600' : 'text-red-600'
              }`}>
                {isPositive ? (
                  <TrendingUp className="w-4 h-4 mr-1" />
                ) : (
                  <TrendingDown className="w-4 h-4 mr-1" />
                )}
                {Math.abs(change)}%
              </div>
            )}
          </div>
          <Icon className="w-8 h-8 text-gray-400" />
        </div>
      </CardContent>
    </Card>
  )
})
```

### 3. 图表性能优化

```typescript
// components/dashboard/charts/optimized-chart.tsx
"use client"

import { memo, useMemo } from "react"
import dynamic from "next/dynamic"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

// 动态导入图表组件，减少初始包大小
const Chart = dynamic(
  () => import('recharts').then((mod) => {
    // 仅导入需要的图表组件
    const { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } = mod
    return function OptimizedChart({ data }: { data: any[] }) {
      return (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#3b82f6" />
          </LineChart>
        </ResponsiveContainer>
      )
    }
  }),
  {
    loading: () => (
      <div className="h-[300px] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    ),
    ssr: false,
  }
)

interface OptimizedChartProps {
  data: Array<{ date: string; value: number }>
  title: string
}

export const OptimizedChart = memo(function OptimizedChart({ data, title }: OptimizedChartProps) {
  // 数据预处理和记忆化
  const processedData = useMemo(() => {
    return data.map(item => ({
      ...item,
      // 添加数据处理逻辑
    }))
  }, [data])

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <Chart data={processedData} />
      </CardContent>
    </Card>
  )
})
```

## 安全性考虑

### 1. 认证和授权

```typescript
// lib/auth.ts
import { withAuth } from "next-auth/middleware"
import { NextResponse } from "next/server"

export default withAuth(
  function middleware(req) {
    const { pathname } = req.nextUrl
    const token = req.nextauth.token

    // 检查用户权限
    if (pathname.startsWith("/dashboard") && token?.role !== "admin") {
      return NextResponse.redirect(new URL("/unauthorized", req.url))
    }

    // API路由保护
    if (pathname.startsWith("/api/ecommerce")) {
      // 验证API token或session
      const authHeader = req.headers.get("authorization")
      if (!authHeader || !authHeader.startsWith("Bearer ")) {
        return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
      }
    }

    return NextResponse.next()
  },
  {
    callbacks: {
      authorized: ({ token }) => !!token,
    },
  }
)

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/api/ecommerce/:path*",
    "/admin/:path*",
  ],
}
```

### 2. 数据验证

```typescript
// lib/validations/ecommerce.ts
import { z } from "zod"

// 订单数据验证
export const OrderSchema = z.object({
  customerId: z.string().min(1, "Customer ID is required"),
  items: z.array(z.object({
    productId: z.string(),
    quantity: z.number().positive("Quantity must be positive"),
    price: z.number().positive("Price must be positive"),
  })).min(1, "Order must have at least one item"),
  shippingAddress: z.object({
    street: z.string().min(1, "Street address is required"),
    city: z.string().min(1, "City is required"),
    state: z.string().min(1, "State is required"),
    zipCode: z.string().regex(/^\d{5}(-\d{4})?$/, "Invalid ZIP code"),
    country: z.string().min(1, "Country is required"),
  }),
  paymentMethod: z.enum(["credit_card", "paypal", "bank_transfer"]),
})

// 产品数据验证
export const ProductSchema = z.object({
  name: z.string().min(1, "Product name is required").max(200),
  description: z.string().max(2000),
  price: z.number().positive("Price must be positive"),
  sku: z.string().min(1, "SKU is required").max(50),
  category: z.string().min(1, "Category is required"),
  stock: z.number().int().min(0, "Stock cannot be negative"),
  images: z.array(z.string().url()).optional(),
})

// 分析查询参数验证
export const AnalyticsQuerySchema = z.object({
  startDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Invalid start date format"),
  endDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Invalid end date format"),
  metrics: z.array(z.enum(["revenue", "orders", "customers", "conversion"])).optional(),
  groupBy: z.enum(["day", "week", "month"]).optional(),
})

export type OrderInput = z.infer<typeof OrderSchema>
export type ProductInput = z.infer<typeof ProductSchema>
export type AnalyticsQuery = z.infer<typeof AnalyticsQuerySchema>
```

## 部署配置

### 1. Vercel部署配置

```json
// vercel.json
{
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "env": {
    "DATABASE_URL": "@database_url",
    "NEXTAUTH_URL": "@nextauth_url",
    "NEXTAUTH_SECRET": "@nextauth_secret",
    "ANALYTICS_API_KEY": "@analytics_api_key",
    "REDIS_URL": "@redis_url",
    "STRIPE_SECRET_KEY": "@stripe_secret_key",
    "STRIPE_WEBHOOK_SECRET": "@stripe_webhook_secret"
  },
  "crons": [
    {
      "path": "/api/cron/analytics-daily",
      "schedule": "0 0 * * *"
    },
    {
      "path": "/api/cron/inventory-sync",
      "schedule": "0 */6 * * *"
    },
    {
      "path": "/api/cron/cache-clear",
      "schedule": "0 2 * * *"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        },
        {
          "key": "Permissions-Policy",
          "value": "camera=(), microphone=(), geolocation=()"
        }
      ]
    }
  ]
}
```

### 2. Docker配置

```dockerfile
# Dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json pnpm-lock.yaml* ./
RUN corepack enable pnpm && pnpm install --frozen-lockfile

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1

RUN corepack enable pnpm && pnpm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

## 扩展功能

### 1. 高级分析功能

```typescript
// app/(dashboard)/analytics/advanced/page.tsx
"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { CohortAnalysisChart } from "@/components/analytics/cohort-analysis-chart"
import { CustomerLifetimeValueChart } from "@/components/analytics/clv-chart"
import { ChurnPredictionChart } from "@/components/analytics/churn-prediction-chart"
import { MarketBasketAnalysis } from "@/components/analytics/market-basket-analysis"
import { RFMAnalysis } from "@/components/analytics/rfm-analysis"

export default function AdvancedAnalyticsPage() {
  const [selectedAnalysis, setSelectedAnalysis] = useState("cohort")

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Advanced Analytics</h1>
        <p className="text-muted-foreground">
          Deep dive into customer behavior and business metrics
        </p>
      </div>

      <Tabs value={selectedAnalysis} onValueChange={setSelectedAnalysis}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="cohort">Cohort Analysis</TabsTrigger>
          <TabsTrigger value="clv">Customer Lifetime Value</TabsTrigger>
          <TabsTrigger value="churn">Churn Prediction</TabsTrigger>
          <TabsTrigger value="basket">Market Basket</TabsTrigger>
        </TabsList>

        <TabsContent value="cohort" className="space-y-6">
          <CohortAnalysisChart />
        </TabsContent>

        <TabsContent value="clv" className="space-y-6">
          <CustomerLifetimeValueChart />
        </TabsContent>

        <TabsContent value="churn" className="space-y-6">
          <ChurnPredictionChart />
        </TabsContent>

        <TabsContent value="basket" className="space-y-6">
          <MarketBasketAnalysis />
          <RFMAnalysis />
        </TabsContent>
      </Tabs>
    </div>
  )
}
```

### 2. 机器学习集成

```typescript
// lib/ml/predictions.ts
export class MLService {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  // 预测客户流失
  async predictChurn(customerId: string): Promise<ChurnPrediction> {
    const response = await fetch(`${this.baseUrl}/predict/churn`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ customerId }),
    })

    if (!response.ok) {
      throw new Error('Failed to predict churn')
    }

    return response.json()
  }

  // 产品推荐
  async getRecommendations(customerId: string): Promise<ProductRecommendation[]> {
    const response = await fetch(`${this.baseUrl}/recommend/${customerId}`)

    if (!response.ok) {
      throw new Error('Failed to get recommendations')
    }

    return response.json()
  }

  // 销量预测
  async predictSales(productId: string, days: number): Promise<SalesPrediction> {
    const response = await fetch(`${this.baseUrl}/predict/sales`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ productId, days }),
    })

    if (!response.ok) {
      throw new Error('Failed to predict sales')
    }

    return response.json()
  }
}

// 使用示例
const mlService = new MLService(process.env.ML_API_URL!)

// 在组件中使用
function useCustomerChurn(customerId: string) {
  return useQuery({
    queryKey: ['churn-prediction', customerId],
    queryFn: () => mlService.predictChurn(customerId),
    staleTime: 24 * 60 * 60 * 1000, // 24小时
  })
}
```

## 总结

### 项目亮点

1. **完整的功能体系**
   - 实时数据监控和分析
   - 多维度数据可视化
   - 完整的订单和库存管理
   - 高级分析功能

2. **技术架构优势**
   - 现代化的技术栈
   - 高性能的数据处理
   - 实时数据流支持
   - 可扩展的架构设计

3. **用户体验优化**
   - 响应式设计
   - 实时数据更新
   - 直观的数据展示
   - 流畅的交互体验

4. **企业级特性**
   - 安全性考虑
   - 性能优化
   - 可扩展性设计
   - 监控和日志

### 实施建议

1. **分阶段开发**
   - 先实现核心功能
   - 逐步添加高级特性
   - 持续优化性能

2. **数据驱动决策**
   - 基于用户反馈优化
   - 数据分析指导产品改进
   - 持续监控关键指标

3. **团队协作**
   - 建立代码规范
   - 实施代码审查
   - 自动化测试和部署

### 扩展方向

1. **移动端应用**
   - React Native移动应用
   - PWA支持
   - 离线功能

2. **国际化支持**
   - 多语言支持
   - 本地化数据
   - 多货币支持

3. **AI功能增强**
   - 智能推荐系统
   - 自动化报表生成
   - 预测性分析

---

通过这个电商仪表板项目，你已经掌握了构建企业级数据分析应用的完整技能。这个项目展示了Next.js 15在数据可视化、实时处理、性能优化等方面的强大能力，可以作为其他数据驱动应用的基础模板。