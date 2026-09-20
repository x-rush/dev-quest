# Next.js 16 数据仪表板开发实战

## 分阶段练习与验收

**最小阶段**：先展示一组固定指标，再接一条真实查询。

**验收结果**：切换时间区间后数值与图表一起变化；空数据不被渲染成错误的零趋势。

**扩展顺序**：再加筛选、导出和权限，性能优化依据数据规模与测量。

建议保存一份正常输入、一份失败输入、实际输出和对应测试。先完成以上阶段再扩展正文中的完整设计；遇到省略实现或未定义依赖，应按文档上下文补齐，不能把代码片段拼接后当作已经验证的完整工程。

> 通过构建一个功能强大的数据分析和可视化仪表板，掌握现代Web数据应用开发的核心技术。本项目涵盖实时数据展示、图表可视化、数据过滤、权限管理、响应式设计等企业级数据分析应用的关键功能。

**目标读者**: 有React和Next.js基础，希望学习数据可视化和企业级仪表板开发的开发者
**前置知识**: React基础、JavaScript ES6+、TypeScript基础、数据可视化基础
**预计时长**: 3-4周

## 📚 文档元数据
| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `projects` |
| **难度** | ⭐⭐⭐ (精通)|
| **标签** | `Next.js 16` `React 19` `TypeScript` `数据可视化` `Chart.js` `D3.js` `实时数据` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标
- 构建企业级数据仪表板应用架构
- 实现多种图表和数据可视化组件
- 开发实时数据更新和WebSocket连接
- 掌握复杂的数据过滤和查询功能
- 实现权限控制和数据访问管理
- 开发响应式仪表板布局
- 实现数据导出和报表生成功能
- 掌握性能优化和大数据处理

## 📖 项目概述

### 项目背景
数据仪表板是现代企业数据分析的重要工具，需要处理大量数据、实时更新、复杂交互等挑战。本项目将构建一个功能完整的企业级数据分析仪表板。

### 核心功能
- 📊 多种图表类型（折线图、柱状图、饼图、热力图等）
- 🔄 实时数据更新和WebSocket连接
- 🔍 高级数据过滤和查询功能
- 👥 用户权限和角色管理
- 📱 响应式布局和移动端适配
- 📤 数据导出（Excel、PDF、CSV）
- 🎨 可定制的仪表板布局
- 📈 数据趋势分析和预测

### 技术栈
- **前端框架**: Next.js 16 + React 19
- **开发语言**: TypeScript
- **图表库**: Chart.js + React-Chartjs-2 + D3.js
- **状态管理**: Zustand + React Query
- **UI组件库**: Shadcn/ui + Tailwind CSS
- **实时通信**: Socket.io
- **数据处理**: date-fns + lodash
- **样式方案**: Tailwind CSS + CSS Modules
- **数据库**: PostgreSQL + Prisma ORM
- **后端API**: Next.js API Routes + tRPC

## 🏗️ 项目架构

### 目录结构
```
dashboard-analytics/
├── app/                          # App Router目录
│   ├── (dashboard)/              # 仪表板路由组
│   │   ├── dashboard/            # 仪表板主页面
│   │   │   ├── layout.tsx       # 仪表板布局
│   │   │   ├── page.tsx         # 主仪表板（Server Component + "use cache"）
│   │   │   ├── loading.tsx      # 仪表板加载兜底
│   │   │   ├── error.tsx        # 仪表板错误边界
│   │   │   ├── analytics/       # 分析页面
│   │   │   ├── reports/         # 报表页面
│   │   │   ├── settings/        # 设置页面
│   │   │   └── users/           # 用户管理
│   │   └── layout.tsx           # 仪表板组布局
│   ├── (auth)/                  # 认证路由组
│   │   ├── login/               # 登录页面
│   │   └── layout.tsx           # 认证布局
│   ├── api/                     # API路由
│   │   ├── auth/                # 认证API
│   │   ├── analytics/           # 数据分析API
│   │   ├── users/               # 用户管理API
│   │   ├── reports/             # 报表API
│   │   ├── export/              # 导出API
│   │   └── socket/              # WebSocket处理
│   ├── error.tsx                # 路由段错误边界（客户端组件）
│   ├── loading.tsx              # 路由段加载兜底
│   ├── not-found.tsx            # 404 约定页面
│   ├── globals.css              # 全局样式
│   ├── layout.tsx               # 根布局
│   └── page.tsx                 # 首页
├── components/                  # 组件库
│   ├── ui/                      # UI基础组件
│   ├── charts/                  # 图表组件
│   ├── dashboard/               # 仪表板组件
│   ├── filters/                 # 过滤器组件
│   ├── layout/                  # 布局组件
│   └── tables/                  # 表格组件
├── lib/                         # 工具函数
│   ├── db/                      # 数据库配置
│   ├── auth/                    # 认证配置
│   ├── utils/                   # 通用工具
│   ├── validations/             # 表单验证
│   ├── charts/                  # 图表工具
│   └── exports/                 # 导出工具
├── hooks/                       # 自定义Hooks
│   ├── useAuth.ts               # 认证Hook
│   ├── useSocket.ts             # WebSocket Hook
│   ├── useCharts.ts             # 图表Hook
│   └── useFilters.ts            # 过滤器Hook
├── store/                       # 状态管理
│   ├── auth.ts                  # 认证状态
│   ├── dashboard.ts             # 仪表板状态
│   ├── filters.ts               # 过滤器状态
│   └── charts.ts                # 图表状态
├── types/                       # TypeScript类型
├── prisma/                      # Prisma配置
│   ├── schema.prisma           # 数据库模型
│   └── migrations/             # 数据库迁移
├── public/                     # 静态资源
└── proxy.ts                   # 网络代理（原中间件）
```

### 数据库设计
```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String
  password  String
  role      UserRole @default(VIEWER)
  avatar    String?
  isActive  Boolean  @default(true)
  lastLogin DateTime?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // 关联
  dashboardConfigs DashboardConfig[]
  savedFilters     SavedFilter[]
  reportAccess     ReportAccess[]
  activityLog      ActivityLog[]

  @@map("users")
}

model DashboardConfig {
  id          String   @id @default(cuid())
  userId      String
  user        User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  name        String
  layout      Json     // 存储仪表板布局配置
  isDefault   Boolean  @default(false)
  isPublic    Boolean  @default(false)
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  @@map("dashboard_configs")
}

model DataSource {
  id          String         @id @default(cuid())
  name        String
  type        DataSourceType
  config      Json           // 数据源配置
  isActive    Boolean        @default(true)
  lastSync    DateTime?
  createdAt   DateTime       @default(now())
  updatedAt   DateTime       @updatedAt

  // 关联
  metrics     Metric[]
  reports     Report[]

  @@map("data_sources")
}

model Metric {
  id           String     @id @default(cuid())
  name         String
  description  String?
  type         MetricType
  dataSourceId String
  dataSource   DataSource @relation(fields: [dataSourceId], references: [id])
  config       Json       // 指标配置
  unit         String?
  format       String?
  isActive     Boolean    @default(true)
  createdAt    DateTime   @default(now())
  updatedAt    DateTime   @updatedAt

  // 关联
  chartConfigs ChartConfig[]
  reportMetrics ReportMetric[]

  @@map("metrics")
}

model ChartConfig {
  id         String     @id @default(cuid())
  name       String
  type       ChartType
  title      String?
  config     Json       // 图表配置
  metricIds  String[]   // 关联的指标ID数组
  layout     Json       // 布局配置
  isPublic   Boolean    @default(false)
  createdAt  DateTime   @default(now())
  updatedAt  DateTime   @updatedAt

  // 关联
  metrics    Metric[]

  @@map("chart_configs")
}

model Report {
  id          String      @id @default(cuid())
  name        String
  description String?
  type        ReportType
  config      Json        // 报表配置
  schedule    String?     // 定时配置
  isActive    Boolean     @default(true)
  dataSourceId String
  dataSource  DataSource  @relation(fields: [dataSourceId], references: [id])
  createdBy   String
  createdAt   DateTime    @default(now())
  updatedAt   DateTime    @updatedAt

  // 关联
  metrics     ReportMetric[]
  access      ReportAccess[]

  @@map("reports")
}

model ReportMetric {
  id      String @id @default(cuid())
  reportId String
  report  Report @relation(fields: [reportId], references: [id], onDelete: Cascade)
  metricId String
  metric  Metric @relation(fields: [metricId], references: [id])
  order   Int    @default(0)

  @@unique([reportId, metricId])
  @@map("report_metrics")
}

model ReportAccess {
  id       String @id @default(cuid())
  reportId String
  report   Report @relation(fields: [reportId], references: [id], onDelete: Cascade)
  userId   String
  user     User   @relation(fields: [userId], references: [id], onDelete: Cascade)
  role     AccessRole @default(VIEWER)

  @@unique([reportId, userId])
  @@map("report_access")
}

model SavedFilter {
  id        String   @id @default(cuid())
  userId    String
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  name      String
  config    Json     // 过滤器配置
  isDefault Boolean  @default(false)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@map("saved_filters")
}

model ActivityLog {
  id        String       @id @default(cuid())
  userId    String
  user      User         @relation(fields: [userId], references: [id])
  action    ActivityType
  resource  String       // 资源类型
  resourceId String?     // 资源ID
  details   Json?        // 详细信息
  ipAddress String?
  userAgent String?
  createdAt DateTime     @default(now())

  @@map("activity_logs")
}

// 枚举类型
enum UserRole {
  ADMIN
  ANALYST
  VIEWER
}

enum DataSourceType {
  DATABASE
  API
  FILE
  REAL_TIME
}

enum MetricType {
  COUNTER
  GAUGE
  HISTOGRAM
  TIMELINE
}

enum ChartType {
  LINE
  BAR
  PIE
  AREA
  SCATTER
  HEATMAP
  TABLE
  KPI
}

enum ReportType {
  DASHBOARD
  SUMMARY
  DETAILED
  CUSTOM
}

enum AccessRole {
  OWNER
  EDITOR
  VIEWER
}

enum ActivityType {
  LOGIN
  LOGOUT
  VIEW_DASHBOARD
  EXPORT_DATA
  CREATE_REPORT
  EDIT_CONFIG
  DELETE_RESOURCE
}
```

## 🛠️ 实战步骤

### 步骤一：项目初始化

#### 1.1 创建Next.js项目
```bash
# 创建Next.js 16项目
npx create-next-app@latest dashboard-analytics --typescript --tailwind --eslint --app

# 进入项目目录
cd dashboard-analytics

# 安装必要依赖
npm install @prisma/client prisma
npm install chart.js react-chartjs-2
npm install d3 @types/d3
npm install @tanstack/react-query zustand
npm install @radix-ui/react-select @radix-ui/react-tabs
npm install @radix-ui/react-dropdown-menu @radix-ui/react-dialog
npm install socket.io socket.io-client
npm install date-fns lodash @types/lodash
npm install react-hook-form @hookform/resolvers zod
npm install jspdf html2canvas xlsx
npm install lucide-react clsx tailwind-merge

# 安装开发依赖
npm install -D @types/node @tailwindcss/typography
npm install -D eslint-config-prettier prettier
```

#### 1.2 配置环境变量
**.env.local**:
```bash
# Database
DATABASE_URL="postgresql://username:password@localhost:5432/analytics_db"

# NextAuth
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-secret-key"

# API Keys
API_KEY_GITHUB="your-github-token"
API_KEY_ANALYTICS="your-analytics-token"

# WebSocket
SOCKET_URL="http://localhost:3001"

# External Services
REDIS_URL="redis://localhost:6379"
EMAIL_SERVICE_API_KEY="your-email-api-key"

# App Settings
NODE_ENV="development"
PORT=3000
```

#### 1.3 配置Tailwind CSS
**tailwind.config.ts**:
```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        // Dashboard specific colors
        chart: {
          1: 'hsl(var(--chart-1))',
          2: 'hsl(var(--chart-2))',
          3: 'hsl(var(--chart-3))',
          4: 'hsl(var(--chart-4))',
          5: 'hsl(var(--chart-5))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
export default config
```

**app/globals.css**:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96%;
    --secondary-foreground: 222.2 84% 4.9%;
    --muted: 210 40% 96%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96%;
    --accent-foreground: 222.2 84% 4.9%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 221.2 83.2% 53.3%;
    --radius: 0.5rem;
    --chart-1: 12 76% 61%;
    --chart-2: 173 58% 39%;
    --chart-3: 197 37% 24%;
    --chart-4: 43 74% 66%;
    --chart-5: 27 87% 67%;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 217.2 91.2% 59.8%;
    --primary-foreground: 222.2 84% 4.9%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 224.3 76.3% 94.1%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}

/* Custom dashboard styles */
.dashboard-grid {
  display: grid;
  gap: 1rem;
  grid-auto-columns: 1fr;
}

.chart-container {
  @apply bg-card rounded-lg border p-6 shadow-sm;
}

.kpi-card {
  @apply bg-gradient-to-br from-card to-card/80 rounded-lg border p-6 shadow-sm;
}

.metric-value {
  @apply text-2xl font-bold text-foreground;
}

.metric-label {
  @apply text-sm text-muted-foreground;
}

.metric-change {
  @apply text-xs font-medium;
}

.metric-change.positive {
  @apply text-green-600;
}

.metric-change.negative {
  @apply text-red-600;
}

/* Scrollbar styles */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: hsl(var(--muted));
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: hsl(var(--muted-foreground));
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: hsl(var(--border));
}
```

### 步骤二：核心功能开发

#### 2.1 实现认证系统
**lib/auth/config.ts**:
```typescript
import { type NextAuthConfig, type DefaultSession } from 'next-auth'
import { PrismaAdapter } from '@auth/prisma-adapter'
import Credentials from 'next-auth/providers/credentials'
import { z } from 'zod'
import { prisma } from '@/lib/db/prisma'
import bcrypt from 'bcryptjs'

declare module 'next-auth' {
  interface User {
    role?: string
  }
  interface Session {
    user: { id?: string; role?: string } & DefaultSession['user']
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    role?: string
  }
}

const credentialsSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
})

export const authConfig: NextAuthConfig = {
  adapter: PrismaAdapter(prisma),
  providers: [
    Credentials({
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        const parsedCredentials = credentialsSchema.safeParse(credentials)

        if (!parsedCredentials.success) {
          return null
        }

        const { email, password } = parsedCredentials.data

        const user = await prisma.user.findUnique({
          where: { email },
        })

        if (!user || !user.password || !user.isActive) {
          return null
        }

        const isPasswordValid = await bcrypt.compare(password, user.password)

        if (!isPasswordValid) {
          return null
        }

        // 更新最后登录时间
        await prisma.user.update({
          where: { id: user.id },
          data: { lastLogin: new Date() },
        })

        return {
          id: user.id,
          email: user.email,
          name: user.name,
          role: user.role,
        }
      },
    }),
  ],
  pages: {
    signIn: '/login',
    error: '/auth/error',
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = user.role
      }
      return token
    },
    async session({ session, token }) {
      if (token.sub) {
        session.user.id = token.sub
      }
      if (token.role) {
        session.user.role = token.role as string
      }
      return session
    },
    authorized({ auth, request }) {
      const isLoggedIn = !!auth?.user
      const isOnDashboard = request.nextUrl.pathname.startsWith('/dashboard')
      const isOnLoginPage = request.nextUrl.pathname === '/login'

      if (isOnLoginPage) {
        if (isLoggedIn) {
          return Response.redirect(new URL('/dashboard', request.url))
        }
        return true
      }

      if (isOnDashboard && !isLoggedIn) {
        return false
      }

      return true
    },
  },
  session: {
    strategy: 'jwt',
  },
}
```

#### 2.2 实现数据获取和处理
**lib/analytics/data-processor.ts**:
```typescript
import { MetricData, TimeRange, FilterOptions } from '@/types/analytics'
import { format, subDays, startOfDay, endOfDay } from 'date-fns'

export interface DataPoint {
  timestamp: Date
  value: number
  metadata?: Record<string, any>
}

export interface AggregatedData {
  labels: string[]
  datasets: {
    label: string
    data: number[]
    backgroundColor?: string
    borderColor?: string
    borderWidth?: number
  }[]
}

export class DataProcessor {
  /**
   * 处理原始数据并返回图表所需格式
   */
  static processChartData(
    data: DataPoint[],
    timeRange: TimeRange,
    aggregationType: 'hour' | 'day' | 'week' | 'month' = 'day'
  ): AggregatedData {
    const aggregated = this.aggregateData(data, timeRange, aggregationType)

    return {
      labels: aggregated.map(point => format(point.timestamp, aggregationType === 'hour' ? 'HH:mm' : 'MM/dd')),
      datasets: [{
        label: 'Value',
        data: aggregated.map(point => point.value),
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 2,
      }],
    }
  }

  /**
   * 聚合数据
   */
  static aggregateData(
    data: DataPoint[],
    timeRange: TimeRange,
    aggregationType: string
  ): DataPoint[] {
    const grouped = new Map<string, DataPoint[]>()

    // 按时间分组
    data.forEach(point => {
      const key = this.getTimeKey(point.timestamp, aggregationType)
      if (!grouped.has(key)) {
        grouped.set(key, [])
      }
      grouped.get(key)!.push(point)
    })

    // 聚合每个组的数据
    return Array.from(grouped.entries()).map(([key, points]) => {
      const timestamp = this.parseTimeKey(key, aggregationType)
      const value = this.calculateAggregatedValue(points)

      return { timestamp, value }
    }).sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())
  }

  /**
   * 计算聚合值
   */
  private static calculateAggregatedValue(points: DataPoint[]): number {
    if (points.length === 0) return 0

    // 默认使用平均值，可以根据需要改为求和、最大值等
    const sum = points.reduce((acc, point) => acc + point.value, 0)
    return sum / points.length
  }

  /**
   * 生成时间键
   */
  private static getTimeKey(date: Date, aggregationType: string): string {
    switch (aggregationType) {
      case 'hour':
        return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}-${date.getHours()}`
      case 'day':
        return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`
      case 'week':
        const weekStart = new Date(date)
        weekStart.setDate(date.getDate() - date.getDay())
        return `${weekStart.getFullYear()}-W${Math.ceil(weekStart.getDate() / 7)}`
      case 'month':
        return `${date.getFullYear()}-${date.getMonth()}`
      default:
        return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`
    }
  }

  /**
   * 解析时间键
   */
  private static parseTimeKey(key: string, aggregationType: string): Date {
    const parts = key.split('-')

    switch (aggregationType) {
      case 'hour':
        return new Date(
          parseInt(parts[0]),
          parseInt(parts[1]),
          parseInt(parts[2]),
          parseInt(parts[3]),
          0,
          0,
          0
        )
      case 'day':
        return new Date(parseInt(parts[0]), parseInt(parts[1]), parseInt(parts[2]))
      case 'week':
        // 简化处理，返回周一的日期
        return new Date(parseInt(parts[0]), 0, (parseInt(parts[1].replace('W', '')) - 1) * 7)
      case 'month':
        return new Date(parseInt(parts[0]), parseInt(parts[1]), 1)
      default:
        return new Date(parseInt(parts[0]), parseInt(parts[1]), parseInt(parts[2]))
    }
  }

  /**
   * 应用过滤器
   */
  static applyFilters(data: DataPoint[], filters: FilterOptions): DataPoint[] {
    let filtered = [...data]

    // 时间范围过滤
    if (filters.dateRange) {
      const { start, end } = filters.dateRange
      filtered = filtered.filter(point =>
        point.timestamp >= start && point.timestamp <= end
      )
    }

    // 数值范围过滤
    if (filters.valueRange) {
      const { min, max } = filters.valueRange
      filtered = filtered.filter(point =>
        point.value >= min && point.value <= max
      )
    }

    // 自定义过滤条件
    if (filters.customFilters) {
      filtered = filtered.filter(point => {
        return filters.customFilters!.every(filter => {
          switch (filter.type) {
            case 'greater_than':
              return point.value > filter.value
            case 'less_than':
              return point.value < filter.value
            case 'equals':
              return point.value === filter.value
            case 'not_equals':
              return point.value !== filter.value
            default:
              return true
          }
        })
      })
    }

    return filtered
  }

  /**
   * 计算统计指标
   */
  static calculateMetrics(data: DataPoint[]): {
    total: number
    average: number
    min: number
    max: number
    trend: 'up' | 'down' | 'stable'
    trendPercentage: number
  } {
    if (data.length === 0) {
      return {
        total: 0,
        average: 0,
        min: 0,
        max: 0,
        trend: 'stable',
        trendPercentage: 0,
      }
    }

    const values = data.map(point => point.value)
    const total = values.reduce((sum, value) => sum + value, 0)
    const average = total / values.length
    const min = Math.min(...values)
    const max = Math.max(...values)

    // 计算趋势
    const halfPoint = Math.floor(data.length / 2)
    const firstHalf = data.slice(0, halfPoint)
    const secondHalf = data.slice(halfPoint)

    const firstHalfAvg = firstHalf.length > 0
      ? firstHalf.reduce((sum, point) => sum + point.value, 0) / firstHalf.length
      : 0
    const secondHalfAvg = secondHalf.length > 0
      ? secondHalf.reduce((sum, point) => sum + point.value, 0) / secondHalf.length
      : 0

    let trend: 'up' | 'down' | 'stable' = 'stable'
    let trendPercentage = 0

    if (firstHalfAvg > 0) {
      const change = ((secondHalfAvg - firstHalfAvg) / firstHalfAvg) * 100
      trendPercentage = Math.abs(change)

      if (change > 5) {
        trend = 'up'
      } else if (change < -5) {
        trend = 'down'
      }
    }

    return {
      total,
      average,
      min,
      max,
      trend,
      trendPercentage,
    }
  }
}
```

#### 2.3 RSC 优先的数据获取改造

> 📖 呼应字典：[数据获取模式](../reference/framework-patterns/04-data-fetching-patterns.md)、[Cache Components与"use cache"](../reference/framework-patterns/08-caching-patterns.md)、[React 19 关键 Hooks](../reference/language-concepts/06-react-19-hooks.md)

初版实现把数据获取放在 `'use client'` 组件的 `useEffect` 里 fetch，这会让仪表板首屏经历"下载 JS → 渲染空壳 → 发起请求 → 二次渲染"的请求瀑布。Next.js 16 的推荐做法是 **RSC 优先**：页面即 Server Component，数据在服务端就绪后才进入 HTML；只有依赖浏览器交互的部分（图表 hover、过滤器联动、WebSocket 实时推送）下沉为 Client Component。

**改造前：客户端瀑布（反面示例）**

```tsx
// components/dashboard/MetricsPanel.tsx
'use client'

import { useEffect, useState } from 'react'
import type { MetricSummary } from '@/types/analytics'

export function MetricsPanel({ dashboardId }: { dashboardId: string }) {
  const [metrics, setMetrics] = useState<MetricSummary[] | null>(null)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false
    fetch(`/api/dashboards/${dashboardId}/metrics`)      // ① 浏览器请求 API 路由
      .then((res) => res.json())
      .then((data) => { if (!cancelled) setMetrics(data) }) // ④ 二次渲染
      .catch((e) => { if (!cancelled) setError(e as Error) })
    return () => { cancelled = true }
  }, [dashboardId])

  if (error) return <p role="alert">加载失败</p>
  if (!metrics) return <p>加载中…</p>                    // ②③ 空壳期
  return <MetricGrid metrics={metrics} />
}
```

问题清单：
- API 路由只是把 Prisma 查询转手一遍，多一跳 HTTP 往返
- 首屏先渲染空壳，指标数据不参与服务端流式输出
- 取数逻辑散落在客户端 bundle 中，无法使用 Cache Components 缓存

**改造后：RSC 优先**

第一步——数据函数放服务端，直接查库并用 `"use cache"` 缓存（Next.js 16 Cache Components 模式）：

```typescript
// lib/analytics/queries.ts
import { cacheTag, cacheLife } from 'next/cache'
import { db } from '@/lib/db'
import type { MetricSummary } from '@/types/analytics'

export async function getDashboardMetrics(dashboardId: string) {
  'use cache'
  cacheTag(`dashboard-${dashboardId}`, 'metrics') // 打失效标签
  cacheLife('minutes')                            // stale 5min / revalidate 1min / expire 1h

  const rows = await db.metric.findMany({
    where: { dashboardId },
    orderBy: { timestamp: 'desc' },
    take: 100,
  })
  return rows as MetricSummary[]
}
```

第二步——页面成为 Server Component，Promise 传递给交互组件、由 `<Suspense>` 流式兜底：

```tsx
// app/(dashboard)/dashboard/page.tsx
import { Suspense } from 'react'
import { getDashboardMetrics } from '@/lib/analytics/queries'
import { MetricsPanel } from '@/components/dashboard/MetricsPanel'
import { DashboardSkeleton } from '@/components/dashboard/DashboardSkeleton'

export default async function DashboardPage() {
  const metricsPromise = getDashboardMetrics('main')

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">数据概览</h1>
      <Suspense fallback={<DashboardSkeleton />}>
        <MetricsPanel metricsPromise={metricsPromise} />
      </Suspense>
    </div>
  )
}
```

第三步——交互下沉：Client Component 通过 props 接收服务端 Promise，用 React 19 的 `use()` 解包：

```tsx
// components/dashboard/MetricsPanel.tsx（改造后）
'use client'

import { use } from 'react'
import type { MetricSummary } from '@/types/analytics'

export function MetricsPanel({
  metricsPromise,
}: {
  metricsPromise: Promise<MetricSummary[]>
}) {
  const metrics = use(metricsPromise) // resolve 前组件挂起，由上层 Suspense 兜底
  return <MetricGrid metrics={metrics} />
}
```

数据变更时在 Server Action 里按标签精准失效缓存：

```typescript
// app/actions/metrics.ts
'use server'

import { updateTag } from 'next/cache'
import { db } from '@/lib/db'

export async function refreshMetrics(dashboardId: string) {
  await db.metric.sync(dashboardId)         // 业务数据同步
  updateTag(`dashboard-${dashboardId}`)     // Server Action 内"写后读"立即失效（Next.js 16）
}
```

> ⚠️ Next.js 16 中 `revalidateTag(tag)` 必须传入第二参数 `cacheLife` profile（如 `revalidateTag(tag, 'max')`，见 4.2 节）；在 Server Action 中希望用户**立刻**看到写入后的新数据，应使用 `updateTag(tag)`。

**收益对比**：

| 维度 | 改造前（useEffect fetch） | 改造后（RSC + "use cache"） |
|------|--------------------------|----------------------------|
| 请求链路 | 浏览器 → API 路由 → Prisma | 服务端直接 Prisma，少一跳 |
| 首屏 | 空壳渲染后二次拉取 | 服务端流式输出，Suspense 兜底 |
| 缓存 | 无（或手动 SWR 轮询） | cacheTag 精准失效 + cacheLife 到期过期 |
| 客户端 JS | 取数逻辑打包进 bundle | 数据层零客户端 JS |

**保留 `'use client'` 的场景**：本项目中的图表交互（2.5 的 hover/zoom）、WebSocket 实时更新（2.6 的 socket.io）与过滤器联动（2.7）依赖浏览器事件与本地 state，留在客户端才有意义——RSC 优先不是"消灭 Client Component"，而是让数据获取回到服务端。

#### 2.4 页面元数据与文件约定（metadata / error / loading / not-found）

> 📖 呼应字典：[错误与加载状态约定](../reference/framework-patterns/11-error-loading-patterns.md)、[App Router 实战模式](../reference/framework-patterns/01-app-router-patterns.md)

仪表板类产品的 SEO 权重不高，但浏览器标签、分享卡片与书签标题仍需正确的元数据；而 `error.tsx` / `loading.tsx` / `not-found.tsx` 文件约定则是仪表板可用性的底线。

**根布局元数据（app/layout.tsx）**——title 模板让每个页面只需声明自己的部分：

```typescript
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: {
    default: 'Analytics Dashboard',
    template: '%s | Analytics Dashboard',
  },
  description: '实时业务数据分析仪表板',
}
```

**页面级静态元数据（app/(dashboard)/dashboard/analytics/page.tsx）**：

```typescript
import type { Metadata } from 'next'

export const metadata: Metadata = { title: '分析' }
```

**动态元数据 + 404 触发（app/(dashboard)/dashboard/users/[userId]/page.tsx）**：

```typescript
import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { getDashboardUser } from '@/lib/analytics/queries'

interface UserPageProps {
  params: Promise<{ userId: string }>
}

export async function generateMetadata({ params }: UserPageProps): Promise<Metadata> {
  const { userId } = await params
  const user = await getDashboardUser(userId)
  if (!user) notFound() // 查不到直接走 404 约定

  return { title: `${user.name} 的数据`, description: user.role }
}
```

**加载兜底（app/(dashboard)/dashboard/loading.tsx）**——路由段挂起时自动生效：

```tsx
export default function Loading() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="h-8 w-48 rounded bg-gray-200" />
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-32 rounded-lg bg-gray-200" />
        ))}
      </div>
    </div>
  )
}
```

**错误边界（app/(dashboard)/dashboard/error.tsx）**——必须是客户端组件：

```tsx
'use client'

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div role="alert" className="p-8 text-center">
      <h2 className="text-lg font-semibold">仪表板加载失败</h2>
      {error.digest && (
        <p className="mt-1 text-sm text-gray-500">追踪 ID: {error.digest}</p>
      )}
      <button
        onClick={reset}
        className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-white"
      >
        重试
      </button>
    </div>
  )
}
```

**404 约定（app/(dashboard)/dashboard/users/[userId]/not-found.tsx）**：

```tsx
import Link from 'next/link'

export default function UserNotFound() {
  return (
    <div className="p-8 text-center">
      <h2 className="text-lg font-semibold">用户不存在</h2>
      <p className="mt-2 text-gray-500">该用户可能已被删除或无权访问</p>
      <Link href="/dashboard/users" className="mt-4 inline-block text-blue-600 underline">
        返回用户列表
      </Link>
    </div>
  )
}
```

注意事项（详见上方字典）：
- `error.tsx` 必须标注 `'use client'`，且**不捕获同层 `layout.tsx` 抛出的错误**——覆盖布局错误要把 `error.tsx` 放到父路由段，或使用 `global-error.tsx`
- `loading.tsx` 的兜底范围是整个路由段；只针对慢数据请用 2.3 的 `<Suspense>`
- `notFound()` 是控制流信号，不要用 `try/catch` 包住它
- 生产环境 `error` 对象会被脱敏，详细原因需查服务端日志与 `digest`

#### 2.5 实现图表组件
**components/charts/LineChart.tsx**:
```tsx
'use client'

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Line } from 'react-chartjs-2'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { format } from 'date-fns'
import { LoadingSpinner } from '@/components/ui/loading-spinner'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface LineChartProps {
  data: {
    labels: string[]
    datasets: Array<{
      label: string
      data: number[]
      backgroundColor?: string
      borderColor?: string
      borderWidth?: number
      fill?: boolean
    }>
  }
  title?: string
  height?: number
  isLoading?: boolean
  showGrid?: boolean
  showLegend?: boolean
  timeFormat?: string
}

export function LineChart({
  data,
  title,
  height = 300,
  isLoading = false,
  showGrid = true,
  showLegend = true,
  timeFormat = 'MM/dd',
}: LineChartProps) {
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: showLegend,
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
        },
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: '#333',
        borderWidth: 1,
        padding: 12,
        displayColors: true,
        callbacks: {
          label: (context: any) => {
            const label = context.dataset.label || ''
            const value = context.parsed.y
            return `${label}: ${value.toLocaleString()}`
          },
        },
      },
    },
    scales: {
      x: {
        display: true,
        grid: {
          display: showGrid,
          color: 'rgba(0, 0, 0, 0.05)',
        },
        ticks: {
          maxTicksLimit: 8,
        },
      },
      y: {
        display: true,
        grid: {
          display: showGrid,
          color: 'rgba(0, 0, 0, 0.05)',
        },
        ticks: {
          callback: (value: any) => value.toLocaleString(),
        },
      },
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false,
    },
    animation: {
      duration: 750,
      easing: 'easeInOutQuart' as const,
    },
    elements: {
      point: {
        radius: 4,
        hoverRadius: 6,
        hitRadius: 10,
      },
      line: {
        tension: 0.4,
      },
    },
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[300px]">
            <LoadingSpinner />
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      {(title || showLegend) && (
        <CardHeader>
          {title && <CardTitle>{title}</CardTitle>}
        </CardHeader>
      )}
      <CardContent>
        <div style={{ height }}>
          <Line data={data} options={options} />
        </div>
      </CardContent>
    </Card>
  )
}
```

**components/charts/BarChart.tsx**:
```tsx
'use client'

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar } from 'react-chartjs-2'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { LoadingSpinner } from '@/components/ui/loading-spinner'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

interface BarChartProps {
  data: {
    labels: string[]
    datasets: Array<{
      label: string
      data: number[]
      backgroundColor?: string | string[]
      borderColor?: string | string[]
      borderWidth?: number
    }>
  }
  title?: string
  height?: number
  isLoading?: boolean
  showGrid?: boolean
  showLegend?: boolean
  horizontal?: boolean
  stacked?: boolean
}

export function BarChart({
  data,
  title,
  height = 300,
  isLoading = false,
  showGrid = true,
  showLegend = true,
  horizontal = false,
  stacked = false,
}: BarChartProps) {
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: horizontal ? 'y' as const : 'x' as const,
    plugins: {
      legend: {
        display: showLegend,
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: '#333',
        borderWidth: 1,
        padding: 12,
        callbacks: {
          label: (context: any) => {
            const label = context.dataset.label || ''
            const value = context.parsed.y || context.parsed.x
            return `${label}: ${value.toLocaleString()}`
          },
        },
      },
    },
    scales: {
      x: {
        display: true,
        stacked,
        grid: {
          display: showGrid && !horizontal,
          color: 'rgba(0, 0, 0, 0.05)',
        },
        ticks: {
          maxTicksLimit: horizontal ? undefined : 8,
        },
      },
      y: {
        display: true,
        stacked,
        grid: {
          display: showGrid && horizontal,
          color: 'rgba(0, 0, 0, 0.05)',
        },
        ticks: {
          callback: (value: any) => value.toLocaleString(),
        },
      },
    },
    animation: {
      duration: 750,
      easing: 'easeInOutQuart' as const,
    },
    elements: {
      bar: {
        borderRadius: 4,
        borderSkipped: false,
      },
    },
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[300px]">
            <LoadingSpinner />
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      {(title || showLegend) && (
        <CardHeader>
          {title && <CardTitle>{title}</CardTitle>}
        </CardHeader>
      )}
      <CardContent>
        <div style={{ height }}>
          <Bar data={data} options={options} />
        </div>
      </CardContent>
    </Card>
  )
}
```

**components/charts/PieChart.tsx**:
```tsx
'use client'

import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js'
import { Pie } from 'react-chartjs-2'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { LoadingSpinner } from '@/components/ui/loading-spinner'

ChartJS.register(ArcElement, Tooltip, Legend)

interface PieChartProps {
  data: {
    labels: string[]
    datasets: Array<{
      data: number[]
      backgroundColor?: string[]
      borderColor?: string[]
      borderWidth?: number
    }>
  }
  title?: string
  height?: number
  isLoading?: boolean
  showLegend?: boolean
  showLabels?: boolean
}

export function PieChart({
  data,
  title,
  height = 300,
  isLoading = false,
  showLegend = true,
  showLabels = true,
}: PieChartProps) {
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: showLegend,
        position: 'right' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
          generateLabels: (chart: any) => {
            const data = chart.data
            if (data.labels.length && data.datasets.length) {
              const dataset = data.datasets[0]
              const total = dataset.data.reduce((a: number, b: number) => a + b, 0)

              return data.labels.map((label: string, i: number) => {
                const value = dataset.data[i]
                const percentage = ((value / total) * 100).toFixed(1)

                return {
                  text: `${label} (${percentage}%)`,
                  fillStyle: dataset.backgroundColor[i],
                  hidden: false,
                  index: i,
                }
              })
            }
            return []
          },
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: '#333',
        borderWidth: 1,
        padding: 12,
        callbacks: {
          label: (context: any) => {
            const label = context.label || ''
            const value = context.parsed
            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0)
            const percentage = ((value / total) * 100).toFixed(1)

            return `${label}: ${value.toLocaleString()} (${percentage}%)`
          },
        },
      },
    },
    animation: {
      animateRotate: true,
      animateScale: false,
      duration: 750,
      easing: 'easeInOutQuart' as const,
    },
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[300px]">
            <LoadingSpinner />
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      {(title || showLegend) && (
        <CardHeader>
          {title && <CardTitle>{title}</CardTitle>}
        </CardHeader>
      )}
      <CardContent>
        <div style={{ height }}>
          <Pie data={data} options={options} />
        </div>
      </CardContent>
    </Card>
  )
}
```

#### 2.6 实现实时数据更新
**hooks/useSocket.ts**:
```typescript
'use client'

import { useEffect, useRef, useState } from 'react'
import { io, Socket } from 'socket.io-client'
import { useSession } from 'next-auth/react'

interface UseSocketOptions {
  autoConnect?: boolean
  reconnection?: boolean
  reconnectionDelay?: number
  reconnectionAttempts?: number
}

export function useSocket(options: UseSocketOptions = {}) {
  const {
    autoConnect = true,
    reconnection = true,
    reconnectionDelay = 1000,
    reconnectionAttempts = 5,
  } = options

  const { data: session } = useSession()
  const [isConnected, setIsConnected] = useState(false)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const socketRef = useRef<Socket | null>(null)

  useEffect(() => {
    if (!session?.user) return

    const socket = io(process.env.NEXT_PUBLIC_SOCKET_URL || 'ws://localhost:3001', {
      auth: {
        token: session.user.id,
      },
      reconnection,
      reconnectionDelay,
      reconnectionAttempts,
    })

    socketRef.current = socket

    socket.on('connect', () => {
      setIsConnected(true)
      setConnectionError(null)
      console.log('Socket connected')
    })

    socket.on('disconnect', (reason) => {
      setIsConnected(false)
      console.log('Socket disconnected:', reason)
    })

    socket.on('connect_error', (error) => {
      setConnectionError(error.message)
      console.error('Socket connection error:', error)
    })

    socket.on('reconnect', (attemptNumber) => {
      console.log('Socket reconnected after', attemptNumber, 'attempts')
    })

    socket.on('reconnect_failed', () => {
      setConnectionError('Failed to reconnect to server')
      console.error('Socket reconnection failed')
    })

    if (!autoConnect) {
      socket.disconnect()
    }

    return () => {
      socket.disconnect()
      socketRef.current = null
    }
  }, [session, autoConnect, reconnection, reconnectionDelay, reconnectionAttempts])

  const connect = () => {
    if (socketRef.current && !socketRef.current.connected) {
      socketRef.current.connect()
    }
  }

  const disconnect = () => {
    if (socketRef.current) {
      socketRef.current.disconnect()
    }
  }

  const emit = (event: string, data: any) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit(event, data)
    } else {
      console.warn('Socket not connected, cannot emit event:', event)
    }
  }

  const subscribe = (event: string, callback: (data: any) => void) => {
    if (socketRef.current) {
      socketRef.current.on(event, callback)
    }

    return () => {
      if (socketRef.current) {
        socketRef.current.off(event, callback)
      }
    }
  }

  return {
    socket: socketRef.current,
    isConnected,
    connectionError,
    connect,
    disconnect,
    emit,
    subscribe,
  }
}
```

**hooks/useRealTimeData.ts**:
```typescript
'use client'

import { useState, useEffect, useCallback } from 'react'
import { useSocket } from './useSocket'
import { DataPoint } from '@/types/analytics'

interface UseRealTimeDataOptions {
  metricId: string
  timeRange?: {
    start: Date
    end: Date
  }
  updateInterval?: number
  maxDataPoints?: number
}

export function useRealTimeData({
  metricId,
  timeRange,
  updateInterval = 5000,
  maxDataPoints = 100,
}: UseRealTimeDataOptions) {
  const [data, setData] = useState<DataPoint[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  const { socket, isConnected, subscribe } = useSocket()

  // 处理新数据点
  const handleNewDataPoint = useCallback((newDataPoint: DataPoint) => {
    setData(prevData => {
      const updatedData = [...prevData, newDataPoint]

      // 应用时间范围过滤
      if (timeRange) {
        return updatedData.filter(
          point => point.timestamp >= timeRange.start && point.timestamp <= timeRange.end
        )
      }

      // 限制数据点数量
      if (maxDataPoints && updatedData.length > maxDataPoints) {
        return updatedData.slice(-maxDataPoints)
      }

      return updatedData
    })

    setLastUpdate(new Date())
    setIsLoading(false)
    setError(null)
  }, [timeRange, maxDataPoints])

  // 处理批量数据更新
  const handleBatchUpdate = useCallback((batchData: DataPoint[]) => {
    setData(prevData => {
      let updatedData = [...prevData, ...batchData]

      // 去重（基于时间戳）
      const uniqueData = updatedData.filter((point, index, self) =>
        index === self.findIndex(p => p.timestamp.getTime() === point.timestamp.getTime())
      )

      // 按时间排序
      uniqueData.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())

      // 应用时间范围过滤
      if (timeRange) {
        uniqueData = uniqueData.filter(
          point => point.timestamp >= timeRange.start && point.timestamp <= timeRange.end
        )
      }

      // 限制数据点数量
      if (maxDataPoints && uniqueData.length > maxDataPoints) {
        return uniqueData.slice(-maxDataPoints)
      }

      return uniqueData
    })

    setLastUpdate(new Date())
    setIsLoading(false)
    setError(null)
  }, [timeRange, maxDataPoints])

  // 请求历史数据
  const fetchHistoricalData = useCallback(async () => {
    if (!metricId) return

    try {
      setIsLoading(true)
      setError(null)

      const response = await fetch(`/api/analytics/metrics/${metricId}/data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          timeRange,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to fetch historical data')
      }

      const historicalData: DataPoint[] = await response.json()
      setData(historicalData)
      setLastUpdate(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsLoading(false)
    }
  }, [metricId, timeRange])

  // 订阅实时数据更新
  useEffect(() => {
    if (!isConnected || !metricId) return

    const unsubscribeNewData = subscribe(`metric:${metricId}:new`, handleNewDataPoint)
    const unsubscribeBatchUpdate = subscribe(`metric:${metricId}:batch`, handleBatchUpdate)

    return () => {
      unsubscribeNewData()
      unsubscribeBatchUpdate()
    }
  }, [isConnected, metricId, subscribe, handleNewDataPoint, handleBatchUpdate])

  // 初始化时获取历史数据
  useEffect(() => {
    fetchHistoricalData()
  }, [fetchHistoricalData])

  // 手动刷新数据
  const refresh = useCallback(() => {
    fetchHistoricalData()
  }, [fetchHistoricalData])

  // 清除数据
  const clear = useCallback(() => {
    setData([])
    setLastUpdate(null)
    setError(null)
  }, [])

  return {
    data,
    isLoading,
    error,
    lastUpdate,
    isConnected,
    refresh,
    clear,
  }
}
```

#### 2.7 实现高级过滤器
**components/filters/AdvancedFilters.tsx**:
```tsx
'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { Calendar } from '@/components/ui/calendar'
import { Badge } from '@/components/ui/badge'
import { Filter, X, Calendar as CalendarIcon } from 'lucide-react'
import { format } from 'date-fns'
import { cn } from '@/lib/utils'
import { FilterOptions, FilterPreset } from '@/types/analytics'

interface AdvancedFiltersProps {
  filters: FilterOptions
  onFiltersChange: (filters: FilterOptions) => void
  presets?: FilterPreset[]
  className?: string
}

export function AdvancedFilters({
  filters,
  onFiltersChange,
  presets = [],
  className,
}: AdvancedFiltersProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [localFilters, setLocalFilters] = useState<FilterOptions>(filters)
  const [startDate, setStartDate] = useState<Date | undefined>(
    filters.dateRange?.start
  )
  const [endDate, setEndDate] = useState<Date | undefined>(
    filters.dateRange?.end
  )

  useEffect(() => {
    setLocalFilters(filters)
    setStartDate(filters.dateRange?.start)
    setEndDate(filters.dateRange?.end)
  }, [filters])

  const applyFilters = () => {
    const updatedFilters: FilterOptions = {
      ...localFilters,
      dateRange: startDate && endDate ? { start: startDate, end: endDate } : undefined,
    }

    onFiltersChange(updatedFilters)
    setIsOpen(false)
  }

  const clearFilters = () => {
    const clearedFilters: FilterOptions = {}
    setLocalFilters(clearedFilters)
    setStartDate(undefined)
    setEndDate(undefined)
    onFiltersChange(clearedFilters)
    setIsOpen(false)
  }

  const addCustomFilter = () => {
    setLocalFilters(prev => ({
      ...prev,
      customFilters: [
        ...(prev.customFilters || []),
        { type: 'greater_than', value: 0 },
      ],
    }))
  }

  const updateCustomFilter = (index: number, filter: any) => {
    setLocalFilters(prev => ({
      ...prev,
      customFilters: prev.customFilters?.map((f, i) =>
        i === index ? filter : f
      ),
    }))
  }

  const removeCustomFilter = (index: number) => {
    setLocalFilters(prev => ({
      ...prev,
      customFilters: prev.customFilters?.filter((_, i) => i !== index),
    }))
  }

  const applyPreset = (preset: FilterPreset) => {
    onFiltersChange(preset.filters)
    setIsOpen(false)
  }

  const getActiveFilterCount = () => {
    let count = 0
    if (localFilters.dateRange) count++
    if (localFilters.valueRange) count++
    if (localFilters.customFilters) count += localFilters.customFilters.length
    return count
  }

  return (
    <div className={cn('flex items-center gap-2', className)}>
      {/* 活跃过滤器标签 */}
      {getActiveFilterCount() > 0 && (
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="flex items-center gap-1">
            <Filter className="w-3 h-3" />
            {getActiveFilterCount()} active
          </Badge>

          {localFilters.dateRange && (
            <Badge variant="outline" className="flex items-center gap-1">
              <CalendarIcon className="w-3 h-3" />
              {format(localFilters.dateRange.start, 'MMM dd')} - {format(localFilters.dateRange.end, 'MMM dd')}
              <X
                className="w-3 h-3 cursor-pointer"
                onClick={() => {
                  setLocalFilters(prev => ({ ...prev, dateRange: undefined }))
                  setStartDate(undefined)
                  setEndDate(undefined)
                }}
              />
            </Badge>
          )}
        </div>
      )}

      {/* 过滤器触发按钮 */}
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <Button variant="outline" className="flex items-center gap-2">
            <Filter className="w-4 h-4" />
            Filters
            {getActiveFilterCount() > 0 && (
              <Badge variant="secondary" className="ml-1">
                {getActiveFilterCount()}
              </Badge>
            )}
          </Button>
        </PopoverTrigger>

        <PopoverContent className="w-96 p-6" align="start">
          <div className="space-y-6">
            {/* 预设过滤器 */}
            {presets.length > 0 && (
              <div>
                <Label className="text-sm font-medium mb-2 block">Quick Presets</Label>
                <div className="grid grid-cols-2 gap-2">
                  {presets.map((preset) => (
                    <Button
                      key={preset.id}
                      variant="outline"
                      size="sm"
                      onClick={() => applyPreset(preset)}
                      className="text-left justify-start"
                    >
                      {preset.name}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {/* 日期范围选择 */}
            <div>
              <Label className="text-sm font-medium mb-2 block">Date Range</Label>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <Label className="text-xs text-muted-foreground">Start Date</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className={cn(
                          'w-full justify-start text-left font-normal',
                          !startDate && 'text-muted-foreground'
                        )}
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {startDate ? format(startDate, 'PPP') : 'Pick a date'}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={startDate}
                        onSelect={setStartDate}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>

                <div>
                  <Label className="text-xs text-muted-foreground">End Date</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className={cn(
                          'w-full justify-start text-left font-normal',
                          !endDate && 'text-muted-foreground'
                        )}
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {endDate ? format(endDate, 'PPP') : 'Pick a date'}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={endDate}
                        onSelect={setEndDate}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>
              </div>
            </div>

            {/* 数值范围过滤 */}
            <div>
              <Label className="text-sm font-medium mb-2 block">Value Range</Label>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <Label className="text-xs text-muted-foreground">Min Value</Label>
                  <Input
                    type="number"
                    placeholder="0"
                    value={localFilters.valueRange?.min || ''}
                    onChange={(e) =>
                      setLocalFilters(prev => ({
                        ...prev,
                        valueRange: {
                          ...prev.valueRange,
                          min: e.target.value ? parseFloat(e.target.value) : undefined,
                        },
                      }))
                    }
                  />
                </div>
                <div>
                  <Label className="text-xs text-muted-foreground">Max Value</Label>
                  <Input
                    type="number"
                    placeholder="1000"
                    value={localFilters.valueRange?.max || ''}
                    onChange={(e) =>
                      setLocalFilters(prev => ({
                        ...prev,
                        valueRange: {
                          ...prev.valueRange,
                          max: e.target.value ? parseFloat(e.target.value) : undefined,
                        },
                      }))
                    }
                  />
                </div>
              </div>
            </div>

            {/* 自定义过滤器 */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <Label className="text-sm font-medium">Custom Filters</Label>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={addCustomFilter}
                >
                  Add Filter
                </Button>
              </div>

              <div className="space-y-2">
                {localFilters.customFilters?.map((filter, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <Select
                      value={filter.type}
                      onValueChange={(value) =>
                        updateCustomFilter(index, { ...filter, type: value })
                      }
                    >
                      <SelectTrigger className="flex-1">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="greater_than">Greater Than</SelectItem>
                        <SelectItem value="less_than">Less Than</SelectItem>
                        <SelectItem value="equals">Equals</SelectItem>
                        <SelectItem value="not_equals">Not Equals</SelectItem>
                      </SelectContent>
                    </Select>

                    <Input
                      type="number"
                      placeholder="Value"
                      value={filter.value || ''}
                      onChange={(e) =>
                        updateCustomFilter(index, {
                          ...filter,
                          value: parseFloat(e.target.value) || 0,
                        })
                      }
                      className="flex-1"
                    />

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeCustomFilter(index)}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            {/* 操作按钮 */}
            <div className="flex justify-between">
              <Button variant="outline" onClick={clearFilters}>
                Clear All
              </Button>
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => setIsOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={applyFilters}>
                  Apply Filters
                </Button>
              </div>
            </div>
          </div>
        </PopoverContent>
      </Popover>
    </div>
  )
}
```

### 步骤三：高级特性实现

#### 3.1 实现数据导出功能
**lib/exports/export-service.ts**:
```typescript
import jsPDF from 'jspdf'
import * as XLSX from 'xlsx'
import html2canvas from 'html2canvas'
import { AggregatedData } from '@/types/analytics'

export interface ExportOptions {
  format: 'excel' | 'pdf' | 'csv' | 'png'
  filename?: string
  includeCharts?: boolean
  dateRange?: {
    start: Date
    end: Date
  }
  metadata?: {
    title?: string
    description?: string
    author?: string
  }
}

export class ExportService {
  /**
   * 导出数据到Excel文件
   */
  static async exportToExcel(
    data: any[],
    options: ExportOptions
  ): Promise<void> {
    try {
      // 创建工作簿
      const workbook = XLSX.utils.book_new()

      // 准备数据
      const worksheet = XLSX.utils.json_to_sheet(data)

      // 自动调整列宽
      const range = XLSX.utils.decode_range(worksheet['!ref'] || 'A1')
      const cols = []

      for (let C = range.s.c; C <= range.e.c; ++C) {
        const address = XLSX.utils.encode_col(C) + '1'
        const cell = worksheet[address]
        const colWidth = cell?.v ? cell.v.toString().length : 10
        cols.push({ wch: Math.min(colWidth + 2, 50) })
      }

      worksheet['!cols'] = cols

      // 添加工作表
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Data')

      // 添加元数据工作表
      if (options.metadata) {
        const metadataSheet = XLSX.utils.json_to_sheet([
          { Key: 'Title', Value: options.metadata.title || '' },
          { Key: 'Description', Value: options.metadata.description || '' },
          { Key: 'Author', Value: options.metadata.author || '' },
          { Key: 'Export Date', Value: new Date().toISOString() },
          { Key: 'Date Range', Value: options.dateRange
            ? `${options.dateRange.start.toISOString()} - ${options.dateRange.end.toISOString()}`
            : 'All time'
          },
        ])
        XLSX.utils.book_append_sheet(workbook, metadataSheet, 'Metadata')
      }

      // 生成文件名
      const filename = options.filename || `export-${Date.now()}`

      // 下载文件
      XLSX.writeFile(workbook, `${filename}.xlsx`)
    } catch (error) {
      console.error('Export to Excel failed:', error)
      throw new Error('Failed to export to Excel')
    }
  }

  /**
   * 导出数据到CSV文件
   */
  static async exportToCSV(
    data: any[],
    options: ExportOptions
  ): Promise<void> {
    try {
      // 创建工作簿
      const workbook = XLSX.utils.book_new()
      const worksheet = XLSX.utils.json_to_sheet(data)
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Data')

      // 生成文件名
      const filename = options.filename || `export-${Date.now()}`

      // 下载文件
      XLSX.writeFile(workbook, `${filename}.csv`, { bookType: 'csv' })
    } catch (error) {
      console.error('Export to CSV failed:', error)
      throw new Error('Failed to export to CSV')
    }
  }

  /**
   * 导出图表到PDF
   */
  static async exportChartToPDF(
    chartElement: HTMLElement,
    options: ExportOptions
  ): Promise<void> {
    try {
      // 捕获图表
      const canvas = await html2canvas(chartElement, {
        backgroundColor: '#ffffff',
        scale: 2,
      })

      // 创建PDF
      const pdf = new jsPDF({
        orientation: 'landscape',
        unit: 'mm',
        format: 'a4',
      })

      // 计算图片尺寸
      const imgWidth = 280
      const imgHeight = (canvas.height * imgWidth) / canvas.width

      // 添加标题
      if (options.metadata?.title) {
        pdf.setFontSize(18)
        pdf.text(options.metadata.title, 20, 20)
      }

      // 添加图片
      pdf.addImage(
        canvas.toDataURL('image/png'),
        'PNG',
        15,
        options.metadata?.title ? 30 : 15,
        imgWidth,
        imgHeight
      )

      // 添加元数据
      if (options.metadata) {
        let yPosition = imgHeight + (options.metadata?.title ? 50 : 35)

        pdf.setFontSize(10)
        pdf.text(`Generated: ${new Date().toLocaleString()}`, 20, yPosition)

        if (options.metadata.description) {
          yPosition += 10
          pdf.text(`Description: ${options.metadata.description}`, 20, yPosition)
        }

        if (options.metadata.author) {
          yPosition += 10
          pdf.text(`Author: ${options.metadata.author}`, 20, yPosition)
        }
      }

      // 保存PDF
      const filename = options.filename || `chart-export-${Date.now()}`
      pdf.save(`${filename}.pdf`)
    } catch (error) {
      console.error('Export chart to PDF failed:', error)
      throw new Error('Failed to export chart to PDF')
    }
  }

  /**
   * 导出仪表板到PDF
   */
  static async exportDashboardToPDF(
    dashboardElement: HTMLElement,
    options: ExportOptions
  ): Promise<void> {
    try {
      // 捕获整个仪表板
      const canvas = await html2canvas(dashboardElement, {
        backgroundColor: '#ffffff',
        scale: 1,
        useCORS: true,
        allowTaint: true,
      })

      // 创建PDF
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4',
      })

      // 计算图片尺寸
      const pageWidth = pdf.internal.pageSize.getWidth()
      const pageHeight = pdf.internal.pageSize.getHeight()
      const imgWidth = pageWidth - 20
      const imgHeight = (canvas.height * imgWidth) / canvas.width

      // 添加标题
      if (options.metadata?.title) {
        pdf.setFontSize(20)
        pdf.text(options.metadata.title, pageWidth / 2, 20, { align: 'center' })
      }

      // 如果图片太大，分页处理
      if (imgHeight > pageHeight - 40) {
        const pages = Math.ceil(imgHeight / (pageHeight - 40))

        for (let i = 0; i < pages; i++) {
          if (i > 0) pdf.addPage()

          const yOffset = i * (pageHeight - 40)
          const sourceY = (i * canvas.height) / pages
          const sourceHeight = canvas.height / pages

          // 创建临时canvas用于分页
          const tempCanvas = document.createElement('canvas')
          tempCanvas.width = canvas.width
          tempCanvas.height = sourceHeight

          const tempCtx = tempCanvas.getContext('2d')
          if (tempCtx) {
            tempCtx.drawImage(
              canvas,
              0,
              sourceY,
              canvas.width,
              sourceHeight,
              0,
              0,
              canvas.width,
              sourceHeight
            )

            pdf.addImage(
              tempCanvas.toDataURL('image/png'),
              'PNG',
              10,
              options.metadata?.title && i === 0 ? 30 : 10,
              imgWidth,
              (sourceHeight * imgWidth) / canvas.width
            )
          }
        }
      } else {
        // 单页显示
        pdf.addImage(
          canvas.toDataURL('image/png'),
          'PNG',
          10,
          options.metadata?.title ? 30 : 10,
          imgWidth,
          imgHeight
        )
      }

      // 添加页脚
      const totalPages = pdf.internal.getNumberOfPages()
      for (let i = 1; i <= totalPages; i++) {
        pdf.setPage(i)
        pdf.setFontSize(8)
        pdf.text(
          `Page ${i} of ${totalPages} - Generated ${new Date().toLocaleString()}`,
          pageWidth / 2,
          pageHeight - 10,
          { align: 'center' }
        )
      }

      // 保存PDF
      const filename = options.filename || `dashboard-export-${Date.now()}`
      pdf.save(`${filename}.pdf`)
    } catch (error) {
      console.error('Export dashboard to PDF failed:', error)
      throw new Error('Failed to export dashboard to PDF')
    }
  }

  /**
   * 导出图表为PNG图片
   */
  static async exportChartToPNG(
    chartElement: HTMLElement,
    options: ExportOptions
  ): Promise<void> {
    try {
      const canvas = await html2canvas(chartElement, {
        backgroundColor: '#ffffff',
        scale: 2,
      })

      // 转换为blob并下载
      canvas.toBlob((blob) => {
        if (blob) {
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `${options.filename || 'chart-export'}-${Date.now()}.png`
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          URL.revokeObjectURL(url)
        }
      }, 'image/png')
    } catch (error) {
      console.error('Export chart to PNG failed:', error)
      throw new Error('Failed to export chart to PNG')
    }
  }

  /**
   * 生成报告数据
   */
  static generateReportData(
    chartData: AggregatedData[],
    filters?: any
  ): any[] {
    const reportData: any[] = []

    chartData.forEach((chart, index) => {
      const labels = chart.labels
      const datasets = chart.datasets

      datasets.forEach((dataset) => {
        dataset.data.forEach((value, i) => {
          reportData.push({
            Chart: `Chart ${index + 1}`,
            Dataset: dataset.label,
            Label: labels[i],
            Value: value,
            Timestamp: new Date().toISOString(),
          })
        })
      })
    })

    return reportData
  }
}
```

#### 3.2 实现仪表板布局系统
**components/dashboard/DashboardGrid.tsx**:
```tsx
'use client'

import { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { GripHorizontal, Maximize2, Minimize2, X, Settings } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'
import { DashboardWidget, WidgetSize } from '@/types/dashboard'

interface DashboardGridProps {
  widgets: DashboardWidget[]
  onWidgetsChange: (widgets: DashboardWidget[]) => void
  editable?: boolean
  className?: string
}

const GRID_SIZE = 12
const ROW_HEIGHT = 80

const WIDGET_SIZES: Record<WidgetSize, { w: number; h: number }> = {
  small: { w: 3, h: 2 },
  medium: { w: 6, h: 4 },
  large: { w: 12, h: 6 },
  wide: { w: 12, h: 3 },
  tall: { w: 4, h: 8 },
}

export function DashboardGrid({
  widgets,
  onWidgetsChange,
  editable = false,
  className,
}: DashboardGridProps) {
  const [draggedWidget, setDraggedWidget] = useState<string | null>(null)
  const [resizingWidget, setResizingWidget] = useState<string | null>(null)
  const [maximizedWidget, setMaximizedWidget] = useState<string | null>(null)

  // 计算网格布局
  const calculateGridLayout = useCallback(() => {
    const occupiedCells = new Set<string>()
    const layout = widgets.map((widget) => {
      const size = WIDGET_SIZES[widget.size]
      const { x, y } = widget.position

      // 检查位置冲突
      for (let dx = 0; dx < size.w; dx++) {
        for (let dy = 0; dy < size.h; dy++) {
          const cellKey = `${x + dx}-${y + dy}`
          if (occupiedCells.has(cellKey)) {
            // 找到下一个可用位置
            let newX = x
            let newY = y
            let found = false

            for (let row = 0; row < 20 && !found; row++) {
              for (let col = 0; col < GRID_SIZE && !found; col++) {
                let canPlace = true
                for (let dx2 = 0; dx2 < size.w && canPlace; dx2++) {
                  for (let dy2 = 0; dy2 < size.h && canPlace; dy2++) {
                    const checkCell = `${col + dx2}-${row + dy2}`
                    if (occupiedCells.has(checkCell)) {
                      canPlace = false
                    }
                  }
                }
                if (canPlace) {
                  newX = col
                  newY = row
                  found = true
                }
              }
            }

            return {
              ...widget,
              position: { x: newX, y: newY },
              size,
            }
          }
        }
      }

      // 标记占用的单元格
      for (let dx = 0; dx < size.w; dx++) {
        for (let dy = 0; dy < size.h; dy++) {
          occupiedCells.add(`${x + dx}-${y + dy}`)
        }
      }

      return {
        ...widget,
        size,
      }
    })

    return layout
  }, [widgets])

  const layout = calculateGridLayout()

  // 处理拖拽开始
  const handleDragStart = (widgetId: string) => {
    if (!editable) return
    setDraggedWidget(widgetId)
  }

  // 处理拖拽结束
  const handleDragEnd = (result: any) => {
    if (!editable || !draggedWidget) return

    const { destination, source } = result
    if (!destination) return

    const newWidgets = [...widgets]
    const draggedIndex = newWidgets.findIndex(w => w.id === draggedWidget)

    if (draggedIndex !== -1) {
      const size = WIDGET_SIZES[newWidgets[draggedIndex].size]

      newWidgets[draggedIndex] = {
        ...newWidgets[draggedIndex],
        position: {
          x: destination.droppableId === 'grid' ? destination.index % GRID_SIZE : 0,
          y: Math.floor(destination.index / GRID_SIZE),
        },
      }

      onWidgetsChange(newWidgets)
    }

    setDraggedWidget(null)
  }

  // 处理大小调整
  const handleResize = (widgetId: string, newSize: WidgetSize) => {
    if (!editable) return

    const newWidgets = widgets.map(widget =>
      widget.id === widgetId
        ? { ...widget, size: newSize }
        : widget
    )

    onWidgetsChange(newWidgets)
  }

  // 处理最大化
  const handleMaximize = (widgetId: string) => {
    setMaximizedWidget(maximizedWidget === widgetId ? null : widgetId)
  }

  // 删除组件
  const handleRemove = (widgetId: string) => {
    if (!editable) return

    const newWidgets = widgets.filter(widget => widget.id !== widgetId)
    onWidgetsChange(newWidgets)
  }

  // 计算网格高度
  const gridHeight = Math.max(
    ...layout.map(widget => widget.position.y + widget.size.h),
    8
  )

  return (
    <div className={cn('relative', className)}>
      <div
        className="grid gap-4"
        style={{
          gridTemplateColumns: `repeat(${GRID_SIZE}, 1fr)`,
          gridAutoRows: `${ROW_HEIGHT}px`,
          minHeight: `${gridHeight * ROW_HEIGHT}px`,
        }}
      >
        <AnimatePresence>
          {layout.map((widget) => {
            const isMaximized = maximizedWidget === widget.id
            const isDragged = draggedWidget === widget.id
            const isResizing = resizingWidget === widget.id

            return (
              <motion.div
                key={widget.id}
                layout
                layoutId={`widget-${widget.id}`}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{
                  opacity: 1,
                  scale: 1,
                  zIndex: isMaximized ? 50 : isDragged ? 40 : 1,
                }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{
                  type: 'spring',
                  stiffness: 300,
                  damping: 30,
                }}
                className={cn(
                  'relative bg-card rounded-lg border shadow-sm overflow-hidden',
                  'group hover:shadow-md transition-shadow duration-200',
                  isMaximized && 'fixed inset-4 z-50 bg-background',
                  isDragged && 'opacity-50',
                  isResizing && 'ring-2 ring-primary',
                  editable && 'cursor-move'
                )}
                style={{
                  gridColumn: isMaximized ? '1 / -1' : `${widget.position.x + 1} / span ${widget.size.w}`,
                  gridRow: isMaximized ? '1 / -1' : `${widget.position.y + 1} / span ${widget.size.h}`,
                }}
                draggable={editable}
                onDragStart={() => handleDragStart(widget.id)}
                onDragEnd={handleDragEnd}
              >
                {/* 组件工具栏 */}
                {editable && (
                  <div className="absolute top-2 right-2 z-10 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0 bg-background/80 backdrop-blur-sm"
                        >
                          <Settings className="w-4 h-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleResize(widget.id, 'small')}>
                          Small
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleResize(widget.id, 'medium')}>
                          Medium
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleResize(widget.id, 'large')}>
                          Large
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleResize(widget.id, 'wide')}>
                          Wide
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleResize(widget.id, 'tall')}>
                          Tall
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>

                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0 bg-background/80 backdrop-blur-sm"
                      onClick={() => handleMaximize(widget.id)}
                    >
                      {isMaximized ? (
                        <Minimize2 className="w-4 h-4" />
                      ) : (
                        <Maximize2 className="w-4 h-4" />
                      )}
                    </Button>

                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0 bg-background/80 backdrop-blur-sm text-destructive hover:text-destructive"
                      onClick={() => handleRemove(widget.id)}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                )}

                {/* 拖拽手柄 */}
                {editable && !isMaximized && (
                  <div className="absolute top-2 left-2 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="h-8 w-8 bg-background/80 backdrop-blur-sm rounded flex items-center justify-center cursor-move">
                      <GripHorizontal className="w-4 h-4 text-muted-foreground" />
                    </div>
                  </div>
                )}

                {/* 组件内容 */}
                <div className="p-4 h-full overflow-auto">
                  {widget.component}
                </div>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>

      {/* 空状态 */}
      {widgets.length === 0 && (
        <div className="flex flex-col items-center justify-center h-96 text-muted-foreground">
          <div className="text-center">
            <h3 className="text-lg font-medium mb-2">No widgets yet</h3>
            <p className="text-sm">
              {editable
                ? 'Add widgets to start building your dashboard.'
                : 'No widgets available to display.'
              }
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
```

### 步骤四：测试和优化

#### 4.1 性能优化
**lib/performance/chart-optimization.ts**:
```typescript
import { useMemo, useCallback } from 'react'
import { debounce } from 'lodash'

/**
 * 图表数据优化Hook
 */
export function useChartOptimization(data: any[], options: {
  maxDataPoints?: number
  enableSampling?: boolean
  enableThrottling?: boolean
  throttleDelay?: number
} = {}) {
  const {
    maxDataPoints = 1000,
    enableSampling = true,
    enableThrottling = true,
    throttleDelay = 100,
  } = options

  // 数据采样
  const sampledData = useMemo(() => {
    if (!enableSampling || data.length <= maxDataPoints) {
      return data
    }

    const step = Math.ceil(data.length / maxDataPoints)
    return data.filter((_, index) => index % step === 0)
  }, [data, maxDataPoints, enableSampling])

  // 节流函数
  const throttledUpdate = useMemo(
    () =>
      enableThrottling
        ? debounce((callback: () => void) => callback(), throttleDelay)
        : (callback: () => void) => callback(),
    [enableThrottling, throttleDelay]
  )

  return {
    data: sampledData,
    throttledUpdate,
    isDataSampled: data.length > maxDataPoints && enableSampling,
    originalDataLength: data.length,
    sampledDataLength: sampledData.length,
  }
}

/**
 * 图表渲染优化
 */
export class ChartOptimizer {
  /**
   * 优化图表配置
   */
  static optimizeChartConfig(config: any, dataSize: number): any {
    const optimized = { ...config }

    // 根据数据量调整动画
    if (dataSize > 500) {
      optimized.animation = false
    } else if (dataSize > 100) {
      optimized.animation = {
        duration: 500,
        easing: 'linear',
      }
    }

    // 优化点的大小
    if (dataSize > 200) {
      optimized.elements = {
        ...optimized.elements,
        point: {
          radius: 2,
          hoverRadius: 4,
        },
      }
    }

    // 优化网格线
    if (dataSize > 100) {
      optimized.scales = {
        ...optimized.scales,
        x: {
          ...optimized.scales?.x,
          grid: {
            display: false,
          },
          ticks: {
            maxTicksLimit: 10,
          },
        },
        y: {
          ...optimized.scales?.y,
          grid: {
            color: 'rgba(0, 0, 0, 0.02)',
          },
          ticks: {
            maxTicksLimit: 8,
          },
        },
      }
    }

    return optimized
  }

  /**
   * 虚拟化大数据集
   */
  static virtualizeData(
    data: any[],
    viewportSize: { width: number; height: number },
    itemSize: { width: number; height: number }
  ): any[] {
    const visibleItemCount = Math.ceil(viewportSize.width / itemSize.width)
    const startIndex = Math.floor(0 / itemSize.width) // 0是滚动位置
    const endIndex = Math.min(startIndex + visibleItemCount + 1, data.length)

    return data.slice(startIndex, endIndex)
  }

  /**
   * 内存使用监控
   */
  static monitorMemoryUsage(): {
    used: number
    total: number
    percentage: number
  } {
    if (typeof window !== 'undefined' && 'memory' in performance) {
      const memory = (performance as any).memory
      return {
        used: memory.usedJSHeapSize,
        total: memory.totalJSHeapSize,
        percentage: (memory.usedJSHeapSize / memory.totalJSHeapSize) * 100,
      }
    }

    return { used: 0, total: 0, percentage: 0 }
  }

  /**
   * 清理内存
   */
  static cleanup(): void {
    // 强制垃圾回收（如果可用）
    if (typeof window !== 'undefined' && 'gc' in window) {
      (window as any).gc()
    }

    // 清理事件监听器
    // 这里应该清理所有的事件监听器
  }
}
```

#### 4.2 数据缓存策略
**lib/cache/data-cache.ts**:
```typescript
// Next.js 16：unstable_cache 已弃用，改用 "use cache" + cacheTag/cacheLife
import { revalidateTag, cacheTag, cacheLife } from 'next/cache'
import { DataPoint, FilterOptions } from '@/types/analytics'

/**
 * 数据缓存服务
 */
export class DataCacheService {
  /**
   * 缓存指标数据
   */
  static async getCachedMetricData(
    metricId: string,
    timeRange: { start: Date; end: Date },
    filters?: FilterOptions
  ): Promise<DataPoint[]> {
    'use cache'
    cacheLife('minutes') // 5分钟级缓存
    cacheTag('metric-data')

    // 这里实现实际的数据获取逻辑
    const response = await fetch(`/api/analytics/metrics/${metricId}/data`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ timeRange, filters }),
    })

    if (!response.ok) {
      throw new Error('Failed to fetch metric data')
    }

    return response.json()
  }

  /**
   * 缓存聚合数据
   */
  static async getCachedAggregatedData(
    metricIds: string[],
    aggregationType: string,
    timeRange: { start: Date; end: Date }
  ): Promise<any> {
    'use cache'
    cacheLife('minutes') // 10分钟级缓存
    cacheTag('aggregated-data')

    // 这里实现聚合数据的获取逻辑
    const response = await fetch('/api/analytics/aggregated', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        metricIds,
        aggregationType,
        timeRange,
      }),
    })

    if (!response.ok) {
      throw new Error('Failed to fetch aggregated data')
    }

    return response.json()
  }

  /**
   * 缓存仪表板配置
   */
  static async getCachedDashboardConfig(dashboardId: string): Promise<any> {
    'use cache'
    cacheLife('hours') // 1小时级缓存
    cacheTag('dashboard-config')

    // 这里实现仪表板配置的获取逻辑
    const response = await fetch(`/api/dashboards/${dashboardId}`)

    if (!response.ok) {
      throw new Error('Failed to fetch dashboard config')
    }

    return response.json()
  }

  /**
   * 清除缓存
   */
  static async clearCache(tags: string[]): Promise<void> {
    try {
      // Next.js 16：revalidateTag 需传入 cacheLife profile 作为第二参数
      tags.forEach(tag => revalidateTag(tag, 'max'))
    } catch (error) {
      console.error('Failed to clear cache:', error)
    }
  }

  /**
   * 预热缓存
   */
  static async warmupCache(metricIds: string[]): Promise<void> {
    try {
      const now = new Date()
      const timeRange = {
        start: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000), // 7天前
        end: now,
      }

      // 并行预加载所有指标数据
      await Promise.all(
        metricIds.map(metricId =>
          this.getCachedMetricData(metricId, timeRange).catch(error => {
            console.warn(`Failed to warmup cache for metric ${metricId}:`, error)
          })
        )
      )
    } catch (error) {
      console.error('Failed to warmup cache:', error)
    }
  }
}

/**
 * 内存缓存（客户端）
 */
export class MemoryCache {
  private cache = new Map<string, { data: any; expiry: number }>()
  private maxSize = 100

  set(key: string, data: any, ttl: number = 300000): void {
    // 检查缓存大小
    if (this.cache.size >= this.maxSize) {
      // 删除最旧的条目
      const firstKey = this.cache.keys().next().value
      this.cache.delete(firstKey)
    }

    this.cache.set(key, {
      data,
      expiry: Date.now() + ttl,
    })
  }

  get(key: string): any | null {
    const entry = this.cache.get(key)

    if (!entry) {
      return null
    }

    if (Date.now() > entry.expiry) {
      this.cache.delete(key)
      return null
    }

    return entry.data
  }

  delete(key: string): boolean {
    return this.cache.delete(key)
  }

  clear(): void {
    this.cache.clear()
  }

  // 定期清理过期条目
  cleanup(): void {
    const now = Date.now()
    for (const [key, entry] of this.cache.entries()) {
      if (now > entry.expiry) {
        this.cache.delete(key)
      }
    }
  }
}

// 创建全局内存缓存实例
export const memoryCache = new MemoryCache()

// 定期清理过期缓存
if (typeof window !== 'undefined') {
  setInterval(() => {
    memoryCache.cleanup()
  }, 60000) // 每分钟清理一次
}
```

### 步骤五：部署和上线

#### 5.1 环境配置
**next.config.js**:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Next.js 15+：serverComponentsExternalPackages 移至顶层 serverExternalPackages
  serverExternalPackages: ['chart.js', 'd3'],
  images: {
    // Next.js 16：images.domains 已弃用，远程域名改用 remotePatterns
    remotePatterns: [
      { protocol: 'https', hostname: 'your-api-domain.com' },
      { protocol: 'http', hostname: 'localhost' },
    ],
    formats: ['image/webp', 'image/avif'],
  },
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  poweredByHeader: false,
  compress: true,
  generateEtags: true,
  // WebSocket配置
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      }
    }
    return config
  },
  // 性能优化
  // 优化包大小
  modularizeImports: {
    'chart.js': {
      transform: 'chart.js/{{member}}',
      preventFullImport: true,
    },
    'd3': {
      transform: 'd3-{{member}}',
      preventFullImport: true,
    },
    'lucide-react': {
      transform: 'lucide-react/{{member}}',
      preventFullImport: true,
    },
  },
}

module.exports = nextConfig
```

#### 5.2 Docker配置
**Dockerfile**:
```dockerfile
# 多阶段构建
FROM node:20-alpine AS base

# 安装依赖阶段
FROM base AS deps
RUN apk add --no-cache libc6-compat python3 make g++
WORKDIR /app

# 复制包管理文件
COPY package.json package-lock.json* ./
RUN npm ci --omit=dev

# 构建阶段
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# 生成Prisma客户端
RUN npx prisma generate

# 构建应用
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

# 运行阶段
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# 复制构建产物
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# 复制Prisma相关文件
COPY --from=builder /app/prisma ./prisma
COPY --from=builder /app/node_modules/.prisma ./node_modules/.prisma

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/analytics_db
      - NEXTAUTH_URL=http://localhost:3000
      - NEXTAUTH_SECRET=your-secret-key
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: analytics_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # WebSocket服务器
  socket-server:
    build: ./socket-server
    ports:
      - "3001:3001"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://postgres:password@db:5432/analytics_db
    depends_on:
      - db
      - redis
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

## 💡 关键技术点

### 1. 数据可视化
- Chart.js和D3.js的深度应用
- 复杂图表类型的实现
- 实时数据更新和动画效果
- 响应式图表设计

### 2. 实时数据处理
- WebSocket连接管理
- 数据流优化和节流
- 大数据量处理策略
- 内存管理和垃圾回收

### 3. 仪表板架构
- 组件化设计模式
- 动态布局系统
- 状态管理策略
- 性能优化技巧

### 4. 数据导出和报表
- 多格式导出实现
- PDF生成和图片导出
- 大数据量处理
- 客户端和服务端渲染

### 5. 缓存和性能优化

先写清每一种数据的“新鲜度合同”。例如概览卡片可缓存 60 秒，但告警列表要标出“数据截至 10:32:00”，不能把一分钟前的值画成实时值；用户切换租户、时间范围或货币时，缓存键必须包含这些条件，避免 A 租户读到 B 租户结果。写入、回填或规则变更后按受影响的指标和过滤条件失效，而不是无条件清空所有缓存。

图表接口要限制一次返回的点数。七天按小时、两年按天是不同查询：服务端按时间窗聚合并返回单位与时区，客户端只渲染当前可见范围。长表使用分页或虚拟列表，但行高、加载占位和键必须稳定；筛选条件变化时取消旧请求或用请求序号拒绝旧响应，不能让慢请求覆盖新筛选结果。

验收时在固定数据量和网络延迟下记录首屏时间、切换时间范围后的请求数、图表点数与浏览器内存。优化前后比较同一场景；“接入缓存”“加了懒加载”只是实现动作，不是性能结论。

## 🎨 UI/UX设计

### 仪表板设计原则
- **数据优先**: 突出数据展示，减少干扰元素
- **一致性**: 统一的设计语言和交互模式
- **响应性**: 适应不同屏幕和设备
- **可访问性**: 支持键盘导航和屏幕阅读器

### 关键设计元素
- **颜色系统**: 使用语义化颜色表达数据状态
- **排版系统**: 清晰的信息层次
- **间距系统**: 一致的布局网格
- **交互反馈**: 及时的状态反馈

## 📱 响应式设计

### 断点策略
- **Mobile**: < 640px - 简化布局，垂直排列
- **Tablet**: 640px - 1024px - 中等密度布局
- **Desktop**: > 1024px - 完整功能布局

### 适配策略
- 图表自适应缩放
- 导航折叠和展开
- 触摸友好的交互
- 性能优化

## ⚡ 性能优化

### 1. 前端优化

把代码分割放在重型图表、导出面板等非首屏交互之后，并给动态组件提供加载和失败状态。输入筛选使用防抖减少请求，拖动缩放使用节流控制渲染频率；两者都不替代服务端的查询上限。列表虚拟化只在行数足够大且每行语义独立时采用，键盘导航和屏幕阅读器仍应能访问当前结果。

### 2. 后端优化

先从慢查询和接口指标定位：记录筛选条件、行数、耗时和返回大小。为租户、时间范围和常用过滤组合建立可解释的索引；聚合昂贵时使用预聚合表或异步刷新，并告诉前端结果的生成时间。压缩、CDN 和响应缓存适合可公开或已按用户隔离的内容，带用户权限的报表不能因为 URL 相同就共用响应。

### 3. 监控和分析

每个告警要定义指标、阈值、连续时长、负责人和排查链接。例如“报表 P95 超过 2 秒且连续 10 分钟”应附带慢查询样本和部署版本；一次短暂尖峰不应把所有人叫醒。错误事件记录匿名请求 ID、路由、租户范围和版本，不记录原始 token、邮箱或报表内容。行为分析与 A/B 测试先声明事件含义、样本范围和停止条件，未经同意不把识别性数据发送给第三方。

## 🔒 安全考虑

### 1. 数据安全

权限必须在服务端按当前身份和租户执行，不能只靠前端隐藏菜单。每个报表 API 都从会话取得租户/用户范围，再与路径或查询参数交叉检查；请求中声称的 `tenantId` 不是授权依据。对导出任务同样检查权限，并记录谁在何时导出了哪个范围。传输使用 HTTPS，密钥、连接串和第三方令牌只在服务端环境变量或密钥管理中读取，不能放进 `NEXT_PUBLIC_` 变量或图表初始数据。

### 2. 应用安全

图表标题、筛选标签和富文本备注都视为不可信输入。使用 React 的默认文本渲染，确需 HTML 时采用受审查的白名单清理，并测试 `<script>`、事件属性和恶意 URL 不会执行。修改数据的请求应校验来源、会话和 CSRF 策略；服务端验证枚举、时间范围、分页上限和数值边界，失败返回可处理的 4xx 错误，而不是把数据库或内部异常原文展示给用户。

## 🧪 测试策略

### 测试类型
1. **单元测试**: 组件和工具函数测试
2. **集成测试**: API和数据流测试
3. **E2E测试**: 完整用户流程测试
4. **性能测试**: 大数据量和高并发测试
5. **可视化测试**: 图表渲染正确性测试

### 测试工具
- Jest: 单元测试框架
- React Testing Library: React组件测试
- Playwright: E2E测试
- Artillery: 性能测试

## 🚀 部署方案

### 生产环境部署
- **前端**: Vercel/Netlify自动部署
- **后端**: Railway/DigitalOcean容器部署
- **数据库**: Supabase/PlanetScale托管数据库
- **缓存**: Redis Cloud托管缓存

### 监控和维护

为关键路径保留一组可复查的运行记录：发布版本、仪表板加载 P95、失败率、队列积压和导出耗时。报警先指向一个可操作的 runbook，再决定升级；自动化测试至少覆盖租户隔离、时间窗聚合、空数据、过期请求和导出权限。备份策略要说明恢复点目标、恢复时间目标和演练频率；“已备份”不等于确认能恢复，恢复演练必须在隔离数据上执行。

## 🔄 文档交叉引用

### 相关文档
- 📄 **[01-corporate-landing.md](./01-corporate-landing.md)**: 企业官网项目实战
- 📄 **[02-ecommerce-store.md](./02-ecommerce-store.md)**: 电商应用项目实战
- 📄 **[04-saas-platform.md](./04-saas-platform.md)**: SaaS平台项目实战

### 参考章节
- 📖 **[Framework Deep Dive - Next.js](../frameworks/01-nextjs-16-complete.md)**: Next.js核心特性深度学习
- 📖 **Data Visualization - Chart.js**: Chart.js快速参考
- 📖 **[Performance Optimization](../reference/performance-optimization/01-rendering-optimization.md)**: 性能优化最佳实践

## 📝 总结

### 核心要点回顾

仪表板首先是数据契约：每张卡片和图表应写清指标名称、单位、聚合方式、时间窗、时区、过滤条件和“无数据”的含义。例如“本周收入”必须说明是否含退款、周从何时开始、按订单创建还是支付成功计入，不能只从数据库取一个总数后赋予业务名称。

实时更新要有版本或时间戳。客户端收到推送后只应用比当前数据新的同一过滤条件结果；断线重连时从服务端重新拉取快照，而不是假设遗漏事件会自动补齐。WebSocket/SSE 只是一种传输方式，权限、租户过滤、背压和降采样仍由服务端负责。

渲染优化从数据量和交互目标出发：限制单次返回的时间粒度与点数，按可见区域请求或聚合，取消已经过期的筛选请求。图表的空状态、加载状态、错误状态和部分数据状态应彼此可见，不能用旧缓存伪装为当前实时数据。对屏幕阅读器提供表格摘要和指标文本，颜色不是表达告警的唯一信号。

### 学习成果检查

- [ ] 为一个收入、一个转化率和一个活跃用户指标写出数据口径，并用同一组原始记录人工算出预期结果；改变时区或时间边界后结果符合口径。
- [ ] 以两个不同租户和两个不同筛选条件请求图表，确认响应和缓存键不会交叉；无权限请求不能通过实时通道得到数据。
- [ ] 模拟“推送比当前快照旧”“断线后丢事件”“服务端返回部分数据”三种情况，UI 不倒退、不静默伪造完整结果，并能提示刷新状态。
- [ ] 对超过单屏承载的时间序列设置聚合或分页上限，记录渲染前后点数与交互目标，而不是只以“图表能画出来”验收。
- [ ] 键盘和屏幕阅读器用户能读取图表标题、时间范围、关键数值和告警含义；颜色变化之外存在文本或图标提示。

## 🤝 贡献与反馈

### 贡献指南
欢迎对本项目实战文档提出改进建议：
- 🐛 **Bug报告**: 发现文档错误或不准确之处
- 💡 **功能建议**: 提出新的可视化类型或功能
- 📝 **内容贡献**: 分享您的数据可视化经验

### 反馈渠道
- GitHub Issues: [项目Issues页面]
- Email: dev-quest@example.com
- 社区讨论: [开发者社区链接]

## 🔗 外部资源

### 官方文档
- [Next.js 16 Documentation](https://nextjs.org/docs)
- [Chart.js Documentation](https://www.chartjs.org/docs/)
- [D3.js Documentation](https://d3js.org/)
- [Socket.io Documentation](https://socket.io/docs/)

### 学习资源
- [Data Visualization with React](https://www.patterns.dev/posts/reactpatterns/)
- [Building Dashboards with Next.js](https://vercel.com/guides/nextjs-dashboard)
- [Real-time Data Visualization](https://www.realtimevisualization.com/)

### 工具和平台
- [Observable](https://observablehq.com/) - 数据可视化平台
- [Plotly](https://plotly.com/) - 交互式图表库
- [Grafana](https://grafana.com/) - 开源监控平台

---

**文档状态**: ✅ 已完成 | 🚧 进行中 | 📋 计划中
**最后更新**: 2026年9月
**版本**: v1.0.0

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
