# Next.js 15 电商应用开发实战

> 通过构建一个功能完整的电商应用，掌握现代Web电商开发的核心技术。本项目涵盖商品展示、购物车、订单管理、支付集成、库存管理等电商系统的关键功能模块。

**目标读者**: 有Next.js基础，希望学习企业级电商应用开发的开发者
**前置知识**: Next.js基础、React状态管理、API设计、数据库基础
**预计时长**: 3-4周

## 📚 文档元数据
| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `projects` |
| **难度** | ⭐⭐⭐⭐⭐ (5/5星) |
| **标签** | `Next.js 15` `React 19` `TypeScript 5` `电商系统` `支付集成` `Stripe` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标
- 构建完整的电商前端应用架构
- 实现购物车和商品管理系统
- 集成Stripe支付系统
- 开发用户认证和权限管理
- 实现订单处理和库存管理
- 掌握电商SEO和性能优化
- 部署生产级电商应用

## 📖 项目概述

### 项目背景
电商应用是现代商业的重要组成部分，需要处理复杂的业务逻辑、高并发访问、安全支付等挑战。本项目将构建一个功能完整的B2C电商平台。

### 核心功能
- 🛍️ 商品展示和搜索系统
- 🛒 购物车和收藏夹功能
- 👤 用户注册登录和个人中心
- 💳 多种支付方式集成
- 📦 订单管理和物流追踪
- 🏷️ 优惠券和促销系统
- 📊 数据分析和报表
- 🔔 实时通知和消息系统

### 技术栈
- **前端框架**: Next.js 15 + React 19
- **开发语言**: TypeScript 5
- **状态管理**: Zustand + React Query
- **UI组件库**: Radix UI + Tailwind CSS
- **数据库**: PostgreSQL + Prisma ORM
- **支付系统**: Stripe + Webhook处理
- **认证**: NextAuth.js v5
- **文件存储**: AWS S3/Cloudinary
- **部署**: Vercel + Railway/Supabase

## 🏗️ 项目架构

### 目录结构
```
ecommerce-store/
├── app/                          # App Router目录
│   ├── (auth)/                   # 认证相关路由组
│   │   ├── login/               # 登录页面
│   │   ├── register/            # 注册页面
│   │   └── layout.tsx           # 认证布局
│   ├── (shop)/                  # 商店相关路由组
│   │   ├── products/            # 商品页面
│   │   │   ├── [slug]/         # 商品详情
│   │   │   └── category/[category]/ # 分类页面
│   │   ├── cart/               # 购物车
│   │   ├── checkout/           # 结账流程
│   │   └── layout.tsx          # 商店布局
│   ├── account/                 # 用户中心
│   │   ├── orders/             # 订单管理
│   │   ├── profile/            # 个人资料
│   │   ├── wishlist/           # 收藏夹
│   │   └── layout.tsx          # 账户布局
│   ├── admin/                   # 管理后台
│   │   ├── products/           # 商品管理
│   │   ├── orders/             # 订单管理
│   │   ├── customers/          # 客户管理
│   │   └── layout.tsx          # 管理布局
│   ├── api/                     # API路由
│   │   ├── auth/               # 认证API
│   │   ├── products/           # 商品API
│   │   ├── cart/               # 购物车API
│   │   ├── orders/             # 订单API
│   │   ├── payments/           # 支付API
│   │   └── webhooks/           # Webhook处理
│   ├── globals.css             # 全局样式
│   ├── layout.tsx              # 根布局
│   └── page.tsx                # 首页
├── components/                  # 组件库
│   ├── ui/                     # UI基础组件
│   ├── shop/                   # 商店组件
│   ├── account/                # 账户组件
│   ├── admin/                  # 管理组件
│   ├── layout/                 # 布局组件
│   └── forms/                  # 表单组件
├── lib/                        # 工具函数
│   ├── db/                     # 数据库配置
│   ├── auth/                   # 认证配置
│   ├── payments/               # 支付处理
│   ├── email/                  # 邮件服务
│   ├── validations/            # 表单验证
│   └── utils/                  # 通用工具
├── hooks/                      # 自定义Hooks
├── store/                      # 状态管理
├── types/                      # TypeScript类型
├── prisma/                     # Prisma配置
│   ├── schema.prisma           # 数据库模型
│   └── migrations/             # 数据库迁移
├── public/                     # 静态资源
└── middleware.ts              # 中间件
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
  name      String?
  password  String
  role      Role     @default(CUSTOMER)
  avatar    String?
  phone     String?
  address   Address[]
  orders    Order[]
  cartItems CartItem[]
  wishlist  WishlistItem[]
  reviews   Review[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@map("users")
}

model Address {
  id         String  @id @default(cuid())
  userId     String
  type       AddressType
  street     String
  city       String
  state      String
  zipCode    String
  country    String
  isDefault  Boolean @default(false)
  user       User    @relation(fields: [userId], references: [id], onDelete: Cascade)
  orders     Order[]
  createdAt  DateTime @default(now())
  updatedAt  DateTime @updatedAt

  @@map("addresses")
}

model Product {
  id          String   @id @default(cuid())
  name        String
  slug        String   @unique
  description String?
  price       Float
  comparePrice Float?
  cost        Float?
  sku         String   @unique
  trackInventory Boolean @default(true)
  status      ProductStatus @default(ACTIVE)
  categoryId  String
  category    Category @relation(fields: [categoryId], references: [id])
  images      ProductImage[]
  variants    ProductVariant[]
  cartItems   CartItem[]
  orderItems  OrderItem[]
  reviews     Review[]
  wishlist    WishlistItem[]
  inventory   Inventory?
  tags        ProductTag[]
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  @@map("products")
}

model Category {
  id          String     @id @default(cuid())
  name        String
  slug        String     @unique
  description String?
  image       String?
  parentId    String?
  parent      Category?  @relation("CategoryHierarchy", fields: [parentId], references: [id])
  children    Category[] @relation("CategoryHierarchy")
  products    Product[]
  createdAt   DateTime   @default(now())
  updatedAt   DateTime   @updatedAt

  @@map("categories")
}

model ProductVariant {
  id        String   @id @default(cuid())
  productId String
  product   Product  @relation(fields: [productId], references: [id], onDelete: Cascade)
  name      String
  sku       String   @unique
  price     Float
  inventory Int      @default(0)
  options   VariantOption[]
  cartItems CartItem[]
  orderItems OrderItem[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@map("product_variants")
}

model VariantOption {
  id               String           @id @default(cuid())
  productVariantId String
  productVariant   ProductVariant   @relation(fields: [productVariantId], references: [id], onDelete: Cascade)
  name             String
  value            String
  createdAt        DateTime         @default(now())

  @@map("variant_options")
}

model ProductImage {
  id        String  @id @default(cuid())
  productId String
  product   Product @relation(fields: [productId], references: [id], onDelete: Cascade)
  url       String
  alt       String?
  position  Int     @default(0)
  createdAt DateTime @default(now())

  @@map("product_images")
}

model Cart {
  id        String     @id @default(cuid())
  userId    String?    @unique
  sessionId String?    @unique
  items     CartItem[]
  expiresAt DateTime   @default(dbnow()) + interval '7 days'
  createdAt DateTime   @default(now())
  updatedAt DateTime   @updatedAt

  @@map("carts")
}

model CartItem {
  id              String          @id @default(cuid())
  cartId          String
  cart            Cart            @relation(fields: [cartId], references: [id], onDelete: Cascade)
  productId       String
  product         Product         @relation(fields: [productId], references: [id])
  productVariantId String?
  productVariant  ProductVariant? @relation(fields: [productVariantId], references: [id])
  quantity        Int
  unitPrice       Float
  createdAt       DateTime        @default(now())
  updatedAt       DateTime        @updatedAt

  @@map("cart_items")
}

model Order {
  id              String     @id @default(cuid())
  orderNumber     String     @unique
  userId          String?
  user            User?      @relation(fields: [userId], references: [id])
  email           String
  status          OrderStatus @default(PENDING)
  paymentStatus   PaymentStatus @default(PENDING)
  paymentMethod   String?
  currency        String     @default("USD")
  subtotal        Float
  tax             Float
  shipping        Float
  discount        Float      @default(0)
  total           Float
  shippingAddress Address?
  billingAddress  Address?
  items           OrderItem[]
  transactions    PaymentTransaction[]
  createdAt       DateTime   @default(now())
  updatedAt       DateTime   @updatedAt

  @@map("orders")
}

model OrderItem {
  id              String          @id @default(cuid())
  orderId         String
  order           Order           @relation(fields: [orderId], references: [id], onDelete: Cascade)
  productId       String
  product         Product         @relation(fields: [productId], references: [id])
  productVariantId String?
  productVariant  ProductVariant? @relation(fields: [productVariantId], references: [id])
  quantity        Int
  unitPrice       Float
  total           Float
  createdAt       DateTime        @default(now())

  @@map("order_items")
}

model PaymentTransaction {
  id                String               @id @default(cuid())
  orderId           String
  order             Order                @relation(fields: [orderId], references: [id], onDelete: Cascade)
  paymentIntentId   String?              @unique
  amount            Float
  currency          String
  status            PaymentTransactionStatus
  paymentMethod     String
  provider          String               @default("stripe")
  metadata          Json?
  createdAt         DateTime             @default(now())
  updatedAt         DateTime             @updatedAt

  @@map("payment_transactions")
}

model Review {
  id        String   @id @default(cuid())
  productId String
  product   Product  @relation(fields: [productId], references: [id], onDelete: Cascade)
  userId    String
  user      User     @relation(fields: [userId], references: [id])
  rating    Int
  title     String?
  content   String?
  verified  Boolean  @default(false)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@unique([productId, userId])
  @@map("reviews")
}

model WishlistItem {
  id        String   @id @default(cuid())
  userId    String
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  productId String
  product   Product  @relation(fields: [productId], references: [id], onDelete: Cascade)
  createdAt DateTime @default(now())

  @@unique([userId, productId])
  @@map("wishlist_items")
}

model Coupon {
  id          String       @id @default(cuid())
  code        String       @unique
  type        CouponType
  value       Float
  minAmount   Float?
  maxUsage    Int?
  usedCount   Int          @default(0)
  expiresAt   DateTime?
  isActive    Boolean      @default(true)
  createdAt   DateTime     @default(now())
  updatedAt   DateTime     @updatedAt

  @@map("coupons")
}

enum Role {
  CUSTOMER
  ADMIN
  SUPER_ADMIN
}

enum ProductStatus {
  ACTIVE
  DRAFT
  ARCHIVED
}

enum AddressType {
  SHIPPING
  BILLING
}

enum OrderStatus {
  PENDING
  CONFIRMED
  PROCESSING
  SHIPPED
  DELIVERED
  CANCELLED
  REFUNDED
}

enum PaymentStatus {
  PENDING
  PROCESSING
  COMPLETED
  FAILED
  REFUNDED
}

enum PaymentTransactionStatus {
  PENDING
  PROCESSING
  COMPLETED
  FAILED
  CANCELLED
}

enum CouponType {
  PERCENTAGE
  FIXED_AMOUNT
}
```

## 🛠️ 实战步骤

### 步骤一：项目初始化

#### 1.1 创建Next.js项目
```bash
# 创建Next.js 15项目
npx create-next-app@latest ecommerce-store --typescript --tailwind --eslint --app

# 进入项目目录
cd ecommerce-store

# 安装必要依赖
npm install @prisma/client prisma
npm install @auth/prisma-adapter next-auth
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
npm install @radix-ui/react-select @radix-ui/react-tabs
npm install @radix-ui/react-toast @radix-ui/react-tooltip
npm install @hookform/resolvers react-hook-form zod
npm install @tanstack/react-query zustand
npm install stripe lucide-react clsx tailwind-merge
npm install date-fns rehype-highlight remark-gfm
npm install @types/stripe @types/node

# 安装开发依赖
npm install -D @tailwindcss/typography
npm install -D eslint-config-prettier prettier
```

#### 1.2 配置Prisma
```bash
# 初始化Prisma
npx prisma init

# 创建数据库并生成迁移
npx prisma migrate dev --name init

# 生成Prisma客户端
npx prisma generate
```

#### 1.3 配置Tailwind CSS扩展
**tailwind.config.ts**:
```typescript
import type { Config } from 'tailwindcss'
import typography from '@tailwindcss/typography'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        secondary: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
        success: {
          50: '#f0fdf4',
          500: '#22c55e',
          600: '#16a34a',
        },
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',
          600: '#d97706',
        },
        error: {
          50: '#fef2f2',
          500: '#ef4444',
          600: '#dc2626',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
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
  plugins: [typography],
}
export default config
```

### 步骤二：核心功能开发

#### 2.1 实现认证系统
**lib/auth/config.ts**:
```typescript
import { NextAuthConfig } from 'next-auth'
import { PrismaAdapter } from '@auth/prisma-adapter'
import Google from 'next-auth/providers/google'
import Credentials from 'next-auth/providers/credentials'
import { z } from 'zod'
import { prisma } from '@/lib/db/prisma'
import bcrypt from 'bcryptjs'

const credentialsSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
})

export const authConfig: NextAuthConfig = {
  adapter: PrismaAdapter(prisma),
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
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

        if (!user || !user.password) {
          return null
        }

        const isPasswordValid = await bcrypt.compare(password, user.password)

        if (!isPasswordValid) {
          return null
        }

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
    signUp: '/register',
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
  },
  session: {
    strategy: 'jwt',
  },
}
```

**app/api/auth/[...nextauth]/route.ts**:
```typescript
import NextAuth from 'next-auth'
import { authConfig } from '@/lib/auth/config'

const handler = NextAuth(authConfig)

export { handler as GET, handler as POST }
```

#### 2.2 实现商品管理
**app/api/products/route.ts**:
```typescript
import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/db/prisma'
import { z } from 'zod'

const productQuerySchema = z.object({
  page: z.string().optional().transform(val => val ? parseInt(val) : 1),
  limit: z.string().optional().transform(val => val ? parseInt(val) : 12),
  category: z.string().optional(),
  search: z.string().optional(),
  sort: z.enum(['name', 'price', 'createdAt']).optional(),
  order: z.enum(['asc', 'desc']).optional(),
  minPrice: z.string().optional().transform(val => val ? parseFloat(val) : undefined),
  maxPrice: z.string().optional().transform(val => val ? parseFloat(val) : undefined),
})

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const query = productQuerySchema.parse(Object.fromEntries(searchParams))

    const where: any = {
      status: 'ACTIVE',
    }

    if (query.category) {
      where.category = {
        slug: query.category,
      }
    }

    if (query.search) {
      where.OR = [
        { name: { contains: query.search, mode: 'insensitive' } },
        { description: { contains: query.search, mode: 'insensitive' } },
      ]
    }

    if (query.minPrice !== undefined || query.maxPrice !== undefined) {
      where.price = {}
      if (query.minPrice !== undefined) {
        where.price.gte = query.minPrice
      }
      if (query.maxPrice !== undefined) {
        where.price.lte = query.maxPrice
      }
    }

    const orderBy: any = {}
    if (query.sort) {
      orderBy[query.sort] = query.order || 'asc'
    } else {
      orderBy.createdAt = 'desc'
    }

    const [products, total] = await Promise.all([
      prisma.product.findMany({
        where,
        include: {
          category: true,
          images: {
            orderBy: { position: 'asc' },
          },
          variants: {
            include: {
              options: true,
            },
          },
          reviews: {
            select: {
              rating: true,
            },
          },
        },
        orderBy,
        skip: (query.page - 1) * query.limit,
        take: query.limit,
      }),
      prisma.product.count({ where }),
    ])

    // 计算平均评分
    const productsWithRating = products.map(product => ({
      ...product,
      averageRating: product.reviews.length > 0
        ? product.reviews.reduce((sum, review) => sum + review.rating, 0) / product.reviews.length
        : 0,
      reviewCount: product.reviews.length,
      reviews: undefined, // 移除原始评论数据
    }))

    return NextResponse.json({
      products: productsWithRating,
      pagination: {
        page: query.page,
        limit: query.limit,
        total,
        pages: Math.ceil(total / query.limit),
      },
    })
  } catch (error) {
    console.error('Products API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

const createProductSchema = z.object({
  name: z.string().min(1),
  slug: z.string().min(1),
  description: z.string().optional(),
  price: z.number().positive(),
  comparePrice: z.number().positive().optional(),
  cost: z.number().positive().optional(),
  sku: z.string().min(1),
  categoryId: z.string(),
  trackInventory: z.boolean().default(true),
  images: z.array(z.object({
    url: z.string().url(),
    alt: z.string().optional(),
    position: z.number().default(0),
  })).optional(),
  variants: z.array(z.object({
    name: z.string(),
    sku: z.string(),
    price: z.number().positive(),
    inventory: z.number().default(0),
    options: z.array(z.object({
      name: z.string(),
      value: z.string(),
    })),
  })).optional(),
})

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const validatedData = createProductSchema.parse(body)

    const product = await prisma.product.create({
      data: {
        ...validatedData,
        images: {
          create: validatedData.images || [],
        },
        variants: {
          create: validatedData.variants || [],
        },
      },
      include: {
        category: true,
        images: {
          orderBy: { position: 'asc' },
        },
        variants: {
          include: {
            options: true,
          },
        },
      },
    })

    return NextResponse.json(product, { status: 201 })
  } catch (error) {
    console.error('Create product error:', error)
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid data', details: error.errors },
        { status: 400 }
      )
    }
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

#### 2.3 实现购物车功能
**lib/cart/cart.ts**:
```typescript
import { prisma } from '@/lib/db/prisma'
import { getServerSession } from 'next-auth'
import { authConfig } from '@/lib/auth/config'
import { cookies } from 'next/headers'

export interface CartItem {
  id: string
  productId: string
  productVariantId?: string
  quantity: number
  unitPrice: number
  product: {
    id: string
    name: string
    slug: string
    images: { url: string; alt?: string }[]
  }
  productVariant?: {
    id: string
    name: string
    sku: string
    options: { name: string; value: string }[]
  }
}

export interface Cart {
  id: string
  items: CartItem[]
  subtotal: number
  total: number
}

export async function getCart(): Promise<Cart> {
  const session = await getServerSession(authConfig)
  const cookieStore = cookies()
  const cartId = cookieStore.get('cartId')?.value

  let cart

  if (session?.user?.id) {
    // 用户已登录，获取用户购物车
    cart = await prisma.cart.findUnique({
      where: { userId: session.user.id },
      include: {
        items: {
          include: {
            product: {
              include: {
                images: {
                  orderBy: { position: 'asc' },
                  take: 1,
                },
              },
            },
            productVariant: {
              include: {
                options: true,
              },
            },
          },
        },
      },
    })
  } else if (cartId) {
    // 游客用户，获取会话购物车
    cart = await prisma.cart.findUnique({
      where: { sessionId: cartId },
      include: {
        items: {
          include: {
            product: {
              include: {
                images: {
                  orderBy: { position: 'asc' },
                  take: 1,
                },
              },
            },
            productVariant: {
              include: {
                options: true,
              },
            },
          },
        },
      },
    })
  }

  if (!cart) {
    return {
      id: '',
      items: [],
      subtotal: 0,
      total: 0,
    }
  }

  const subtotal = cart.items.reduce(
    (sum, item) => sum + item.unitPrice * item.quantity,
    0
  )

  return {
    id: cart.id,
    items: cart.items.map(item => ({
      ...item,
      product: {
        id: item.product.id,
        name: item.product.name,
        slug: item.product.slug,
        images: item.product.images,
      },
    })),
    subtotal,
    total: subtotal, // 这里可以添加税费和运费计算
  }
}

export async function addToCart(
  productId: string,
  quantity: number,
  productVariantId?: string
): Promise<Cart> {
  const session = await getServerSession(authConfig)
  const cookieStore = cookies()
  const cartId = cookieStore.get('cartId')?.value

  // 获取产品信息
  const product = await prisma.product.findUnique({
    where: { id: productId },
    include: {
      variants: true,
    },
  })

  if (!product) {
    throw new Error('Product not found')
  }

  let variant
  if (productVariantId) {
    variant = product.variants.find(v => v.id === productVariantId)
    if (!variant) {
      throw new Error('Product variant not found')
    }
  }

  const unitPrice = variant?.price || product.price

  let cart

  if (session?.user?.id) {
    // 用户已登录
    cart = await prisma.cart.upsert({
      where: { userId: session.user.id },
      update: {},
      create: {
        userId: session.user.id,
      },
      include: {
        items: true,
      },
    })
  } else {
    // 游客用户
    if (!cartId) {
      // 创建新购物车
      const newCart = await prisma.cart.create({
        data: {
          sessionId: crypto.randomUUID(),
          expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7天后过期
        },
      })

      cookieStore.set('cartId', newCart.sessionId!, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
        maxAge: 7 * 24 * 60 * 60, // 7天
      })

      cart = newCart
    } else {
      cart = await prisma.cart.findUnique({
        where: { sessionId: cartId },
        include: { items: true },
      })
    }
  }

  if (!cart) {
    throw new Error('Failed to create or retrieve cart')
  }

  // 检查是否已存在相同的商品
  const existingItem = cart.items.find(
    item =>
      item.productId === productId &&
      item.productVariantId === productVariantId
  )

  if (existingItem) {
    // 更新数量
    await prisma.cartItem.update({
      where: { id: existingItem.id },
      data: {
        quantity: existingItem.quantity + quantity,
      },
    })
  } else {
    // 添加新商品
    await prisma.cartItem.create({
      data: {
        cartId: cart.id,
        productId,
        productVariantId,
        quantity,
        unitPrice,
      },
    })
  }

  return getCart()
}

export async function updateCartItem(
  itemId: string,
  quantity: number
): Promise<Cart> {
  if (quantity <= 0) {
    await prisma.cartItem.delete({
      where: { id: itemId },
    })
  } else {
    await prisma.cartItem.update({
      where: { id: itemId },
      data: { quantity },
    })
  }

  return getCart()
}

export async function removeFromCart(itemId: string): Promise<Cart> {
  await prisma.cartItem.delete({
    where: { id: itemId },
  })

  return getCart()
}

export async function clearCart(): Promise<void> {
  const session = await getServerSession(authConfig)
  const cookieStore = cookies()
  const cartId = cookieStore.get('cartId')?.value

  if (session?.user?.id) {
    await prisma.cartItem.deleteMany({
      where: {
        cart: {
          userId: session.user.id,
        },
      },
    })
  } else if (cartId) {
    await prisma.cartItem.deleteMany({
      where: {
        cart: {
          sessionId: cartId,
        },
      },
    })
  }
}
```

**app/api/cart/route.ts**:
```typescript
import { NextRequest, NextResponse } from 'next/server'
import { getCart } from '@/lib/cart/cart'

export async function GET() {
  try {
    const cart = await getCart()
    return NextResponse.json(cart)
  } catch (error) {
    console.error('Get cart error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

**app/api/cart/add/route.ts**:
```typescript
import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { addToCart } from '@/lib/cart/cart'

const addToCartSchema = z.object({
  productId: z.string(),
  quantity: z.number().positive(),
  productVariantId: z.string().optional(),
})

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { productId, quantity, productVariantId } = addToCartSchema.parse(body)

    const cart = await addToCart(productId, quantity, productVariantId)

    return NextResponse.json(cart)
  } catch (error) {
    console.error('Add to cart error:', error)
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid data', details: error.errors },
        { status: 400 }
      )
    }
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

#### 2.4 实现支付集成
**lib/payments/stripe.ts**:
```typescript
import Stripe from 'stripe'
import { prisma } from '@/lib/db/prisma'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-06-20',
})

export interface CreatePaymentIntentParams {
  orderId: string
  amount: number
  currency?: string
}

export async function createPaymentIntent({
  orderId,
  amount,
  currency = 'usd',
}: CreatePaymentIntentParams) {
  try {
    // 创建支付意图
    const paymentIntent = await stripe.paymentIntents.create({
      amount: Math.round(amount * 100), // Stripe使用分为单位
      currency,
      metadata: {
        orderId,
      },
      automatic_payment_methods: {
        enabled: true,
      },
    })

    // 保存交易记录
    await prisma.paymentTransaction.create({
      data: {
        orderId,
        paymentIntentId: paymentIntent.id,
        amount,
        currency,
        status: 'PENDING',
        paymentMethod: 'stripe',
        provider: 'stripe',
      },
    })

    return {
      clientSecret: paymentIntent.client_secret,
      paymentIntentId: paymentIntent.id,
    }
  } catch (error) {
    console.error('Create payment intent error:', error)
    throw new Error('Failed to create payment intent')
  }
}

export async function confirmPayment(paymentIntentId: string) {
  try {
    const paymentIntent = await stripe.paymentIntents.retrieve(paymentIntentId)

    if (paymentIntent.status === 'succeeded') {
      // 更新交易状态
      await prisma.paymentTransaction.updateMany({
        where: {
          paymentIntentId,
        },
        data: {
          status: 'COMPLETED',
        },
      })

      // 更新订单状态
      const orderId = paymentIntent.metadata.orderId
      if (orderId) {
        await prisma.order.update({
          where: { id: orderId },
          data: {
            status: 'CONFIRMED',
            paymentStatus: 'COMPLETED',
          },
        })
      }
    }

    return paymentIntent
  } catch (error) {
    console.error('Confirm payment error:', error)
    throw new Error('Failed to confirm payment')
  }
}

export async function handleStripeWebhook(
  payload: string,
  signature: string
) {
  let event: Stripe.Event

  try {
    event = stripe.webhooks.constructEvent(
      payload,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    )
  } catch (error) {
    console.error('Webhook signature verification failed:', error)
    throw new Error('Invalid signature')
  }

  switch (event.type) {
    case 'payment_intent.succeeded':
      await handlePaymentSucceeded(event.data.object as Stripe.PaymentIntent)
      break
    case 'payment_intent.payment_failed':
      await handlePaymentFailed(event.data.object as Stripe.PaymentIntent)
      break
    default:
      console.log(`Unhandled event type: ${event.type}`)
  }

  return event
}

async function handlePaymentSucceeded(paymentIntent: Stripe.PaymentIntent) {
  const orderId = paymentIntent.metadata.orderId

  if (!orderId) {
    console.error('No order ID in payment intent metadata')
    return
  }

  await prisma.$transaction(async (tx) => {
    // 更新支付交易状态
    await tx.paymentTransaction.updateMany({
      where: {
        paymentIntentId: paymentIntent.id,
      },
      data: {
        status: 'COMPLETED',
      },
    })

    // 更新订单状态
    await tx.order.update({
      where: { id: orderId },
      data: {
        status: 'CONFIRMED',
        paymentStatus: 'COMPLETED',
      },
    })

    // 减少库存
    const order = await tx.order.findUnique({
      where: { id: orderId },
      include: {
        items: true,
      },
    })

    if (order) {
      for (const item of order.items) {
        if (item.productVariantId) {
          await tx.productVariant.update({
            where: { id: item.productVariantId },
            data: {
              inventory: {
                decrement: item.quantity,
              },
            },
          })
        } else {
          // 如果没有变体，减少主产品库存
          await tx.product.update({
            where: { id: item.productId },
            data: {
              // 这里需要在产品表中添加inventory字段
              // inventory: { decrement: item.quantity },
            },
          })
        }
      }
    }
  })

  // 发送确认邮件（这里需要实现邮件发送逻辑）
  console.log(`Payment succeeded for order: ${orderId}`)
}

async function handlePaymentFailed(paymentIntent: Stripe.PaymentIntent) {
  const orderId = paymentIntent.metadata.orderId

  if (!orderId) {
    console.error('No order ID in payment intent metadata')
    return
  }

  await prisma.$transaction(async (tx) => {
    // 更新支付交易状态
    await tx.paymentTransaction.updateMany({
      where: {
        paymentIntentId: paymentIntent.id,
      },
      data: {
        status: 'FAILED',
      },
    })

    // 更新订单状态
    await tx.order.update({
      where: { id: orderId },
      data: {
        status: 'CANCELLED',
        paymentStatus: 'FAILED',
      },
    })
  })

  // 发送失败通知邮件
  console.log(`Payment failed for order: ${orderId}`)
}
```

**app/api/payments/create-intent/route.ts**:
```typescript
import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authConfig } from '@/lib/auth/config'
import { createPaymentIntent } from '@/lib/payments/stripe'
import { prisma } from '@/lib/db/prisma'
import { z } from 'zod'

const createIntentSchema = z.object({
  orderId: z.string(),
})

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authConfig)
    if (!session?.user?.id) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    const body = await request.json()
    const { orderId } = createIntentSchema.parse(body)

    // 获取订单信息
    const order = await prisma.order.findUnique({
      where: { id: orderId },
    })

    if (!order) {
      return NextResponse.json(
        { error: 'Order not found' },
        { status: 404 }
      )
    }

    if (order.userId !== session.user.id) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    if (order.paymentStatus !== 'PENDING') {
      return NextResponse.json(
        { error: 'Order already paid or cancelled' },
        { status: 400 }
      )
    }

    const result = await createPaymentIntent({
      orderId,
      amount: order.total,
      currency: order.currency,
    })

    return NextResponse.json(result)
  } catch (error) {
    console.error('Create payment intent error:', error)
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid data', details: error.errors },
        { status: 400 }
      )
    }
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

#### 2.5 实现订单管理
**lib/orders/order.ts**:
```typescript
import { prisma } from '@/lib/db/prisma'
import { getCart } from '@/lib/cart/cart'
import { clearCart } from '@/lib/cart/cart'

export interface CreateOrderParams {
  email: string
  shippingAddressId: string
  billingAddressId?: string
  paymentMethod: string
  couponCode?: string
}

export async function createOrder({
  email,
  shippingAddressId,
  billingAddressId,
  paymentMethod,
  couponCode,
}: CreateOrderParams) {
  const cart = await getCart()

  if (cart.items.length === 0) {
    throw new Error('Cart is empty')
  }

  // 验证地址
  const shippingAddress = await prisma.address.findUnique({
    where: { id: shippingAddressId },
  })

  if (!shippingAddress) {
    throw new Error('Shipping address not found')
  }

  const billingAddress = billingAddressId
    ? await prisma.address.findUnique({
        where: { id: billingAddressId },
      })
    : shippingAddress

  if (!billingAddress) {
    throw new Error('Billing address not found')
  }

  // 计算订单总额
  const subtotal = cart.subtotal
  let tax = subtotal * 0.08 // 8% 税率
  let shipping = 0
  let discount = 0

  // 应用优惠券
  if (couponCode) {
    const coupon = await prisma.coupon.findUnique({
      where: {
        code: couponCode.toUpperCase(),
        isActive: true,
        OR: [
          { expiresAt: null },
          { expiresAt: { gt: new Date() } },
        ],
      },
    })

    if (coupon) {
      if (coupon.minAmount && subtotal < coupon.minAmount) {
        throw new Error(`Minimum order amount is $${coupon.minAmount}`)
      }

      if (coupon.maxUsage && coupon.usedCount >= coupon.maxUsage) {
        throw new Error('Coupon has reached maximum usage')
      }

      if (coupon.type === 'PERCENTAGE') {
        discount = subtotal * (coupon.value / 100)
      } else {
        discount = Math.min(coupon.value, subtotal)
      }

      // 增加优惠券使用次数
      await prisma.coupon.update({
        where: { id: coupon.id },
        data: {
          usedCount: {
            increment: 1,
          },
        },
      })
    } else {
      throw new Error('Invalid or expired coupon')
    }
  }

  // 计算运费
  if (subtotal < 50) {
    shipping = 10
  }

  const total = subtotal + tax + shipping - discount

  const order = await prisma.$transaction(async (tx) => {
    // 生成订单号
    const orderNumber = generateOrderNumber()

    // 创建订单
    const newOrder = await tx.order.create({
      data: {
        orderNumber,
        email,
        status: 'PENDING',
        paymentStatus: 'PENDING',
        paymentMethod,
        currency: 'USD',
        subtotal,
        tax,
        shipping,
        discount,
        total,
        shippingAddressId: shippingAddress.id,
        billingAddressId: billingAddress.id,
        items: {
          create: cart.items.map(item => ({
            productId: item.productId,
            productVariantId: item.productVariantId,
            quantity: item.quantity,
            unitPrice: item.unitPrice,
            total: item.unitPrice * item.quantity,
          })),
        },
      },
      include: {
        items: {
          include: {
            product: true,
            productVariant: true,
          },
        },
      },
    })

    // 检查库存
    for (const item of cart.items) {
      if (item.productVariantId) {
        const variant = await tx.productVariant.findUnique({
          where: { id: item.productVariantId },
        })

        if (!variant || variant.inventory < item.quantity) {
          throw new Error(`Insufficient inventory for ${item.product.name}`)
        }
      }
    }

    // 预留库存（可选）
    // 这里可以实现库存预留逻辑

    return newOrder
  })

  // 清空购物车
  await clearCart()

  return order
}

function generateOrderNumber(): string {
  const timestamp = Date.now().toString()
  const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0')
  return `ORD-${timestamp.slice(-6)}-${random}`
}

export async function getOrder(orderId: string, userId?: string) {
  const order = await prisma.order.findUnique({
    where: { id: orderId },
    include: {
      items: {
        include: {
          product: {
            include: {
              images: {
                orderBy: { position: 'asc' },
                take: 1,
              },
            },
          },
          productVariant: {
            include: {
              options: true,
            },
          },
        },
      },
      shippingAddress: true,
      billingAddress: true,
      transactions: true,
    },
  })

  if (!order) {
    throw new Error('Order not found')
  }

  if (userId && order.userId !== userId) {
    throw new Error('Unauthorized')
  }

  return order
}

export async function getUserOrders(userId: string, page = 1, limit = 10) {
  const skip = (page - 1) * limit

  const [orders, total] = await Promise.all([
    prisma.order.findMany({
      where: { userId },
      include: {
        items: {
          include: {
            product: {
              include: {
                images: {
                  orderBy: { position: 'asc' },
                  take: 1,
                },
              },
            },
          },
        },
      },
      orderBy: { createdAt: 'desc' },
      skip,
      take: limit,
    }),
    prisma.order.count({
      where: { userId },
    }),
  ])

  return {
    orders,
    pagination: {
      page,
      limit,
      total,
      pages: Math.ceil(total / limit),
    },
  }
}
```

### 步骤三：高级特性实现

#### 3.1 实现搜索功能
**lib/search/search.ts**:
```typescript
import { prisma } from '@/lib/db/prisma'

export interface SearchParams {
  query: string
  category?: string
  minPrice?: number
  maxPrice?: number
  sortBy?: 'name' | 'price' | 'rating' | 'createdAt'
  sortOrder?: 'asc' | 'desc'
  page?: number
  limit?: number
}

export interface SearchResult {
  products: any[]
  categories: any[]
  pagination: {
    page: number
    limit: number
    total: number
    pages: number
  }
}

export async function searchProducts(params: SearchParams): Promise<SearchResult> {
  const {
    query,
    category,
    minPrice,
    maxPrice,
    sortBy = 'createdAt',
    sortOrder = 'desc',
    page = 1,
    limit = 12,
  } = params

  const skip = (page - 1) * limit

  // 构建搜索条件
  const where: any = {
    status: 'ACTIVE',
  }

  if (query) {
    where.OR = [
      { name: { contains: query, mode: 'insensitive' } },
      { description: { contains: query, mode: 'insensitive' } },
      { sku: { contains: query, mode: 'insensitive' } },
      {
        tags: {
          some: {
            tag: {
              name: { contains: query, mode: 'insensitive' },
            },
          },
        },
      },
    ]
  }

  if (category) {
    where.category = {
      slug: category,
    }
  }

  if (minPrice !== undefined || maxPrice !== undefined) {
    where.price = {}
    if (minPrice !== undefined) {
      where.price.gte = minPrice
    }
    if (maxPrice !== undefined) {
      where.price.lte = maxPrice
    }
  }

  // 构建排序条件
  const orderBy: any = {}
  if (sortBy === 'rating') {
    // 按评分排序需要特殊处理
    orderBy.reviews = {
      _avg: {
        rating: sortOrder,
      },
    }
  } else {
    orderBy[sortBy] = sortOrder
  }

  const [products, total, categories] = await Promise.all([
    prisma.product.findMany({
      where,
      include: {
        category: true,
        images: {
          orderBy: { position: 'asc' },
          take: 1,
        },
        variants: {
          include: {
            options: true,
          },
        },
        reviews: {
          select: {
            rating: true,
          },
        },
        _count: {
          select: {
            reviews: true,
          },
        },
      },
      orderBy,
      skip,
      take: limit,
    }),
    prisma.product.count({ where }),
    // 获取相关分类
    prisma.category.findMany({
      where: {
        products: {
          some: where,
        },
      },
      include: {
        _count: {
          select: {
            products: {
              where,
            },
          },
        },
      },
      orderBy: {
        name: 'asc',
      },
    }),
  ])

  // 处理产品数据
  const processedProducts = products.map(product => ({
    ...product,
    averageRating: product.reviews.length > 0
      ? product.reviews.reduce((sum, review) => sum + review.rating, 0) / product.reviews.length
      : 0,
    reviewCount: product._count.reviews,
    reviews: undefined,
    _count: undefined,
  }))

  return {
    products: processedProducts,
    categories: categories.map(category => ({
      ...category,
      productCount: category._count.products,
      _count: undefined,
    })),
    pagination: {
      page,
      limit,
      total,
      pages: Math.ceil(total / limit),
    },
  }
}

export async function getSuggestions(query: string, limit = 5) {
  if (!query || query.length < 2) {
    return { products: [], categories: [] }
  }

  const [products, categories] = await Promise.all([
    prisma.product.findMany({
      where: {
        status: 'ACTIVE',
        name: {
          contains: query,
          mode: 'insensitive',
        },
      },
      select: {
        id: true,
        name: true,
        slug: true,
        images: {
          select: {
            url: true,
          },
          orderBy: { position: 'asc' },
          take: 1,
        },
      },
      take: limit,
    }),
    prisma.category.findMany({
      where: {
        name: {
          contains: query,
          mode: 'insensitive',
        },
      },
      select: {
        id: true,
        name: true,
        slug: true,
        image: true,
      },
      take: Math.floor(limit / 2),
    }),
  ])

  return { products, categories }
}
```

#### 3.2 实现推荐系统
**lib/recommendations/recommendations.ts**:
```typescript
import { prisma } from '@/lib/db/prisma'

export interface RecommendationParams {
  userId?: string
  productId?: string
  categoryIds?: string[]
  limit?: number
}

export async function getRecommendations({
  userId,
  productId,
  categoryIds,
  limit = 10,
}: RecommendationParams) {
  const recommendations = []

  // 基于用户行为的推荐
  if (userId) {
    const userRecommendations = await getUserBasedRecommendations(userId, limit)
    recommendations.push(...userRecommendations)
  }

  // 基于商品的协同过滤推荐
  if (productId) {
    const collaborativeRecommendations = await getCollaborativeRecommendations(productId, limit)
    recommendations.push(...collaborativeRecommendations)
  }

  // 基于分类的推荐
  if (categoryIds && categoryIds.length > 0) {
    const categoryRecommendations = await getCategoryBasedRecommendations(categoryIds, limit)
    recommendations.push(...categoryRecommendations)
  }

  // 热门商品推荐
  if (recommendations.length < limit) {
    const popularProducts = await getPopularProducts(limit - recommendations.length)
    recommendations.push(...popularProducts)
  }

  // 去重并限制数量
  const uniqueRecommendations = recommendations
    .filter((product, index, self) =>
      self.findIndex(p => p.id === product.id) === index
    )
    .slice(0, limit)

  return uniqueRecommendations
}

async function getUserBasedRecommendations(userId: string, limit: number) {
  // 获取用户购买历史
  const userOrders = await prisma.order.findMany({
    where: { userId },
    include: {
      items: {
        include: {
          product: {
            include: {
              category: true,
            },
          },
        },
      },
    },
  })

  // 提取用户偏好的分类
  const categoryPreferences = userOrders.flatMap(order =>
    order.items.map(item => item.product.categoryId)
  )

  const uniqueCategoryIds = [...new Set(categoryPreferences)]

  // 获取这些分类中的其他商品
  const recommendations = await prisma.product.findMany({
    where: {
      categoryId: { in: uniqueCategoryIds },
      status: 'ACTIVE',
      // 排除已购买的商品
      id: {
        notIn: userOrders.flatMap(order =>
          order.items.map(item => item.productId)
        ),
      },
    },
    include: {
      category: true,
      images: {
        orderBy: { position: 'asc' },
        take: 1,
      },
      reviews: {
        select: { rating: true },
      },
      _count: {
        select: { reviews: true },
      },
    },
    orderBy: [
      { reviews: { _avg: { rating: 'desc' } } },
      { _count: { reviews: 'desc' } },
    ],
    take: limit,
  })

  return recommendations.map(product => ({
    ...product,
    averageRating: product.reviews.length > 0
      ? product.reviews.reduce((sum, review) => sum + review.rating, 0) / product.reviews.length
      : 0,
    reviewCount: product._count.reviews,
    reviews: undefined,
    _count: undefined,
  }))
}

async function getCollaborativeRecommendations(productId: string, limit: number) {
  // 找到购买过此商品的用户还购买了哪些其他商品
  const relatedProducts = await prisma.orderItem.findMany({
    where: {
      productId,
    },
    include: {
      order: {
        include: {
          items: {
            include: {
              product: {
                include: {
                  category: true,
                  images: {
                    orderBy: { position: 'asc' },
                    take: 1,
                  },
                  reviews: {
                    select: { rating: true },
                  },
                  _count: {
                    select: { reviews: true },
                  },
                },
              },
            },
          },
        },
      },
    },
  })

  // 统计其他商品的购买次数
  const productFrequency = new Map<string, number>()

  relatedProducts.forEach(orderItem => {
    orderItem.order.items.forEach(item => {
      if (item.productId !== productId) {
        const current = productFrequency.get(item.productId) || 0
        productFrequency.set(item.productId, current + 1)
      }
    })
  })

  // 获取最频繁购买的商品
  const sortedProductIds = Array.from(productFrequency.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([productId]) => productId)

  if (sortedProductIds.length === 0) {
    return []
  }

  const recommendations = await prisma.product.findMany({
    where: {
      id: { in: sortedProductIds },
      status: 'ACTIVE',
    },
    include: {
      category: true,
      images: {
        orderBy: { position: 'asc' },
        take: 1,
      },
      reviews: {
        select: { rating: true },
      },
      _count: {
        select: { reviews: true },
      },
    },
  })

  // 按照购买频率排序
  const productOrder = new Map(sortedProductIds.map((id, index) => [id, index]))

  return recommendations
    .sort((a, b) => (productOrder.get(a.id) || 0) - (productOrder.get(b.id) || 0))
    .map(product => ({
      ...product,
      averageRating: product.reviews.length > 0
        ? product.reviews.reduce((sum, review) => sum + review.rating, 0) / product.reviews.length
        : 0,
      reviewCount: product._count.reviews,
      reviews: undefined,
      _count: undefined,
    }))
}

async function getCategoryBasedRecommendations(categoryIds: string[], limit: number) {
  const recommendations = await prisma.product.findMany({
    where: {
      categoryId: { in: categoryIds },
      status: 'ACTIVE',
    },
    include: {
      category: true,
      images: {
        orderBy: { position: 'asc' },
        take: 1,
      },
      reviews: {
        select: { rating: true },
      },
      _count: {
        select: { reviews: true },
      },
    },
    orderBy: [
      { reviews: { _avg: { rating: 'desc' } } },
      { _count: { reviews: 'desc' } },
    ],
    take: limit,
  })

  return recommendations.map(product => ({
    ...product,
    averageRating: product.reviews.length > 0
      ? product.reviews.reduce((sum, review) => sum + review.rating, 0) / product.reviews.length
      : 0,
    reviewCount: product._count.reviews,
    reviews: undefined,
    _count: undefined,
  }))
}

async function getPopularProducts(limit: number) {
  const recommendations = await prisma.product.findMany({
    where: {
      status: 'ACTIVE',
    },
    include: {
      category: true,
      images: {
        orderBy: { position: 'asc' },
        take: 1,
      },
      reviews: {
        select: { rating: true },
      },
      _count: {
        select: { reviews: true, orderItems: true },
      },
    },
    orderBy: [
      { _count: { orderItems: 'desc' } },
      { reviews: { _avg: { rating: 'desc' } } },
    ],
    take: limit,
  })

  return recommendations.map(product => ({
    ...product,
    averageRating: product.reviews.length > 0
      ? product.reviews.reduce((sum, review) => sum + review.rating, 0) / product.reviews.length
      : 0,
    reviewCount: product._count.reviews,
    reviews: undefined,
    _count: undefined,
  }))
}
```

### 步骤四：测试和优化

#### 4.1 API测试
**__tests__/api/products.test.ts**:
```typescript
import { createMocks } from 'node-mocks-http'
import handler from '@/app/api/products/route'

describe('/api/products', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('GET', () => {
    it('should return products with pagination', async () => {
      const { req, res } = createMocks({
        method: 'GET',
        query: {
          page: '1',
          limit: '10',
        },
      })

      await handler(req, res)

      expect(res._getStatusCode()).toBe(200)
      const data = JSON.parse(res._getData())
      expect(data).toHaveProperty('products')
      expect(data).toHaveProperty('pagination')
    })

    it('should filter products by category', async () => {
      const { req, res } = createMocks({
        method: 'GET',
        query: {
          category: 'electronics',
        },
      })

      await handler(req, res)

      expect(res._getStatusCode()).toBe(200)
      const data = JSON.parse(res._getData())
      expect(data.products).toBeDefined()
    })

    it('should search products by name', async () => {
      const { req, res } = createMocks({
        method: 'GET',
        query: {
          search: 'laptop',
        },
      })

      await handler(req, res)

      expect(res._getStatusCode()).toBe(200)
      const data = JSON.parse(res._getData())
      expect(data.products).toBeDefined()
    })
  })

  describe('POST', () => {
    it('should create a new product', async () => {
      const productData = {
        name: 'Test Product',
        slug: 'test-product',
        description: 'A test product',
        price: 99.99,
        sku: 'TEST-001',
        categoryId: 'category-id',
      }

      const { req, res } = createMocks({
        method: 'POST',
        body: productData,
      })

      await handler(req, res)

      expect(res._getStatusCode()).toBe(201)
      const data = JSON.parse(res._getData())
      expect(data.name).toBe(productData.name)
    })

    it('should validate product data', async () => {
      const invalidProductData = {
        name: '',
        price: -10,
      }

      const { req, res } = createMocks({
        method: 'POST',
        body: invalidProductData,
      })

      await handler(req, res)

      expect(res._getStatusCode()).toBe(400)
      const data = JSON.parse(res._getData())
      expect(data).toHaveProperty('error')
    })
  })
})
```

#### 4.2 性能优化
**lib/cache/cache.ts**:
```typescript
import { unstable_cache } from 'next/cache'

// 缓存产品数据
export const getCachedProducts = unstable_cache(
  async (params: any) => {
    // 这里实现获取产品数据的逻辑
    return [] // 返回产品数据
  },
  ['products'],
  {
    revalidate: 3600, // 1小时缓存
    tags: ['products'],
  }
)

// 缓存分类数据
export const getCachedCategories = unstable_cache(
  async () => {
    // 这里实现获取分类数据的逻辑
    return [] // 返回分类数据
  },
  ['categories'],
  {
    revalidate: 86400, // 24小时缓存
    tags: ['categories'],
  }
)

// 清除产品缓存
export function revalidateProducts() {
  revalidateTag('products')
}

// 清除分类缓存
export function revalidateCategories() {
  revalidateTag('categories')
}
```

### 步骤五：部署和上线

#### 5.1 环境变量配置
**.env.local**:
```bash
# Database
DATABASE_URL="postgresql://username:password@localhost:5432/ecommerce_db"

# NextAuth
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-secret-key"

# Google OAuth
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"

# Stripe
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_PUBLISHABLE_KEY="pk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."

# Email
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="your-email@gmail.com"
SMTP_PASS="your-app-password"
SMTP_FROM="noreply@yourstore.com"

# File Storage
CLOUDINARY_CLOUD_NAME="your-cloud-name"
CLOUDINARY_API_KEY="your-api-key"
CLOUDINARY_API_SECRET="your-api-secret"

# Redis (可选，用于缓存)
REDIS_URL="redis://localhost:6379"

# Analytics
NEXT_PUBLIC_GA_ID="G-XXXXXXXXXX"
```

#### 5.2 Docker配置
**Dockerfile**:
```dockerfile
# 多阶段构建
FROM node:18-alpine AS base

# 安装依赖阶段
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# 复制包管理文件
COPY package.json package-lock.json* ./
RUN npm ci --only=production

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
      - DATABASE_URL=postgresql://postgres:password@db:5432/ecommerce_db
      - NEXTAUTH_URL=http://localhost:3000
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ecommerce_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 💡 关键技术点

### 1. 电商架构设计
- 模块化的系统架构
- 数据库设计和关系建模
- 微服务化思考

### 2. 支付系统集成
- Stripe支付集成
- Webhook处理
- 交易安全和验证

### 3. 购物车和订单管理
- 复杂的购物车逻辑
- 订单状态流转
- 库存管理

### 4. 搜索和推荐
- 全文搜索实现
- 个性化推荐算法
- 性能优化

### 5. 用户认证和权限
- 多种登录方式
- 权限控制
- 安全最佳实践

## 🎨 UI/UX设计

### 电商设计原则
- **用户中心**: 以用户需求为中心的设计
- **转化导向**: 优化购买流程和转化率
- **信任建立**: 通过设计建立用户信任
- **移动优先**: 响应式设计和移动体验

### 关键页面设计
1. **首页**: 品牌展示、产品推荐、促销活动
2. **商品列表**: 筛选、排序、搜索功能
3. **商品详情**: 产品信息、评价、购买选项
4. **购物车**: 商品管理、价格计算
5. **结账流程**: 简化的多步结账
6. **用户中心**: 订单管理、个人信息

## 📱 响应式设计

### 移动端优化
- 触摸友好的交互设计
- 移动端导航优化
- 移动端结账流程简化
- PWA支持

### 关键断点设计
- 手机: < 640px
- 平板: 640px - 1024px
- 桌面: > 1024px

## ⚡ 性能优化

### 1. 前端优化
- 代码分割和懒加载
- 图片优化和CDN
- 缓存策略
- 预加载和预取

### 2. 后端优化
- 数据库查询优化
- API响应缓存
- 数据库连接池
- Redis缓存

### 3. SEO优化
- 服务端渲染
- 结构化数据
- 元标签优化
- 站点地图

## 🔒 安全考虑

### 1. 支付安全
- PCI DSS合规
- 数据加密
- 安全的支付流程
- 防欺诈措施

### 2. 数据安全
- 用户数据保护
- GDPR合规
- 安全的数据传输
- 数据备份

### 3. 应用安全
- SQL注入防护
- XSS防护
- CSRF保护
- 安全的认证

## 🧪 测试策略

### 测试类型
1. **单元测试**: 组件和函数测试
2. **集成测试**: API和数据库测试
3. **E2E测试**: 完整用户流程测试
4. **性能测试**: 负载和压力测试
5. **安全测试**: 漏洞扫描

### 测试工具
- Jest: 单元测试框架
- React Testing Library: React组件测试
- Playwright: E2E测试
- Artillery: 性能测试

## 🚀 部署方案

### 生产环境部署
- Vercel: 前端应用部署
- Railway/Heroku: 后端API部署
- Supabase/PlanetScale: 数据库托管
- Cloudinary: 文件存储

### CI/CD流程
- GitHub Actions: 自动化构建和部署
- 代码质量检查
- 自动化测试
- 生产环境部署

### 监控和分析
- 应用性能监控
- 错误追踪
- 用户行为分析
- 业务指标监控

## 🔄 文档交叉引用

### 相关文档
- 📄 **[01-corporate-landing.md](./01-corporate-landing.md)**: 企业官网项目实战
- 📄 **[03-dashboard-analytics.md](./03-dashboard-analytics.md)**: 数据仪表板项目实战
- 📄 **[04-saas-platform.md](./04-saas-platform.md)**: SaaS平台项目实战

### 参考章节
- 📖 **[Framework Deep Dive - Next.js](../frameworks/nextjs-core.md)**: Next.js核心特性深度学习
- 📖 **[Database - Prisma ORM](../knowledge-points/database/prisma.md)**: Prisma ORM快速参考
- 📖 **[Authentication - NextAuth](../knowledge-points/auth/nextauth.md)**: NextAuth.js最佳实践

## 📝 总结

### 核心要点回顾
1. **电商架构**: 掌握完整的电商系统架构设计
2. **支付集成**: 实现安全可靠的支付系统
3. **数据管理**: 复杂的业务数据建模和管理
4. **性能优化**: 电商系统性能优化策略
5. **安全防护**: 电商安全最佳实践

### 学习成果检查
- [ ] 能够独立设计和实现电商系统架构
- [ ] 掌握支付系统集成和处理流程
- [ ] 实现完整的购物车和订单管理系统
- [ ] 开发高效的搜索和推荐功能
- [ ] 部署和运维生产级电商应用

## 🤝 贡献与反馈

### 贡献指南
欢迎对本项目实战文档提出改进建议：
- 🐛 **Bug报告**: 发现文档错误或不准确之处
- 💡 **功能建议**: 提出新的实战场景或技术点
- 📝 **内容贡献**: 分享您的电商开发经验

### 反馈渠道
- GitHub Issues: [项目Issues页面]
- Email: dev-quest@example.com
- 社区讨论: [开发者社区链接]

## 🔗 外部资源

### 官方文档
- [Next.js 15 Documentation](https://nextjs.org/docs)
- [Stripe API Documentation](https://stripe.com/docs/api)
- [Prisma Documentation](https://www.prisma.io/docs/)
- [NextAuth.js Documentation](https://next-auth.js.org/)

### 学习资源
- [Building E-commerce with Next.js](https://vercel.com/guides/nextjs-ecommerce)
- [Stripe Integration Guide](https://stripe.com/docs/payments/accept-a-payment)
- [E-commerce Best Practices](https://web.dev/ecommerce/)

### 工具和平台
- [Vercel Commerce](https://github.com/vercel/commerce)
- [MedusaJS](https://medusajs.com/)
- [Saleor](https://saleor.io/)

---

**文档状态**: ✅ 已完成 | 🚧 进行中 | 📋 计划中
**最后更新**: 2025年10月
**版本**: v1.0.0