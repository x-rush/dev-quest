# 微前端架构 - Next.js 15 现代架构实践

## 📋 概述

微前端是一种将单体前端应用分解为更小、更简单部分的架构风格，每个部分可以独立开发、测试和部署。Next.js 15 提供了强大的功能来支持微前端架构，包括模块联邦（Module Federation）、并行路由等特性。

## 🎯 微前端核心概念

### 1. 什么是微前端？

微前端架构允许将大型Web应用拆分为多个独立的、可独立部署的应用：

```
主应用 (Shell App)
├── 产品目录微应用
├── 用户管理微应用
├── 订单系统微应用
└── 支付系统微应用
```

### 2. 微前端的优势

- **独立部署**：每个微应用可以独立开发和部署
- **技术栈灵活**：不同微应用可以使用不同的技术栈
- **团队自治**：不同团队可以独立开发和维护各自的微应用
- **渐进式迁移**：可以逐步迁移和升级现有应用

## 🚀 Next.js 15 微前端实现

### 1. 使用模块联邦（Module Federation）

```typescript
// apps/shell/next.config.js
const { NextFederationPlugin } = require('@module-federation/nextjs-mf');

/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack(config, options) {
    config.plugins.push(
      new NextFederationPlugin({
        name: 'shell',
        remotes: {
          products: `products@http://localhost:3001/_next/static/${options.isServer ? 'ssr' : 'chunks'}/remoteEntry.js`,
          users: `users@http://localhost:3002/_next/static/${options.isServer ? 'ssr' : 'chunks'}/remoteEntry.js`,
          orders: `orders@http://localhost:3003/_next/static/${options.isServer ? 'ssr' : 'chunks'}/remoteEntry.js`,
        },
        shared: {
          react: { singleton: true, requiredVersion: false },
          'react-dom': { singleton: true, requiredVersion: false },
          'next/link': { singleton: true, requiredVersion: false },
          'next/router': { singleton: true, requiredVersion: false },
        },
      })
    );

    return config;
  },
};

module.exports = nextConfig;
```

```typescript
// apps/products/next.config.js
const { NextFederationPlugin } = require('@module-federation/nextjs-mf');

/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack(config, options) {
    config.plugins.push(
      new NextFederationPlugin({
        name: 'products',
        filename: 'remoteEntry.js',
        exposes: {
          './ProductList': './components/ProductList',
          './ProductDetail': './components/ProductDetail',
          './ProductSearch': './components/ProductSearch',
        },
        shared: {
          react: { singleton: true, requiredVersion: false },
          'react-dom': { singleton: true, requiredVersion: false },
          'next/link': { singleton: true, requiredVersion: false },
        },
      })
    );

    return config;
  },
};

module.exports = nextConfig;
```

### 2. 主应用集成微应用

```typescript
// apps/shell/app/page.tsx
'use client';

import dynamic from 'next/dynamic';

// 动态导入微应用组件
const ProductList = dynamic(
  () => import('products/ProductList'),
  { loading: () => <div>Loading products...</div>, ssr: false }
);

const UserManagement = dynamic(
  () => import('users/UserManagement'),
  { loading: () => <div>Loading users...</div>, ssr: false }
);

const OrderSystem = dynamic(
  () => import('orders/OrderSystem'),
  { loading: () => <div>Loading orders...</div>, ssr: false }
);

export default function HomePage() {
  return (
    <div className="shell-app">
      <header>
        <nav>
          <Link href="/">Home</Link>
          <Link href="/products">Products</Link>
          <Link href="/users">Users</Link>
          <Link href="/orders">Orders</Link>
        </nav>
      </header>

      <main>
        <Suspense fallback={<div>Loading...</div>}>
          <ProductList />
          <UserManagement />
          <OrderSystem />
        </Suspense>
      </main>
    </div>
  );
}
```

### 3. 路由级别的微前端

```typescript
// apps/shell/app/products/page.tsx
'use client';

import dynamic from 'next/dynamic';

const ProductsApp = dynamic(
  () => import('products/ProductsApp'),
  {
    loading: () => <div>Loading Products App...</div>,
    ssr: false
  }
);

export default function ProductsPage() {
  return (
    <div>
      <h1>Products</h1>
      <ProductsApp />
    </div>
  );
}

// apps/products/app/page.tsx
export default function ProductsApp() {
  return (
    <div className="products-app">
      <ProductSearch />
      <ProductList />
    </div>
  );
}
```

## 🎨 高级微前端模式

### 1. 共享组件库

```typescript
// shared-components/src/Button.tsx
import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input hover:bg-accent hover:text-accent-foreground',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'underline-offset-4 hover:underline text-primary',
      },
      size: {
        default: 'h-10 py-2 px-4',
        sm: 'h-9 px-3 rounded-md',
        lg: 'h-11 px-8 rounded-md',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);

Button.displayName = 'Button';

export { Button, buttonVariants };
```

```typescript
// shared-components/src/index.ts
export { Button } from './Button';
export { Card, CardHeader, CardContent, CardFooter } from './Card';
export { Input } from './Input';
export { Badge } from './Badge';
```

### 2. 共享状态管理

```typescript
// shared-state/src/store.ts
import { create } from 'zustand';

// 用户状态
interface UserState {
  user: User | null;
  isAuthenticated: boolean;
  login: (user: User) => void;
  logout: () => void;
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  isAuthenticated: false,
  login: (user) => set({ user, isAuthenticated: true }),
  logout: () => set({ user: null, isAuthenticated: false }),
}));

// 购物车状态
interface CartState {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  clearCart: () => void;
  getTotal: () => number;
}

export const useCartStore = create<CartState>((set, get) => ({
  items: [],
  addItem: (item) => {
    set((state) => {
      const existingItem = state.items.find(i => i.id === item.id);
      if (existingItem) {
        return {
          items: state.items.map(i =>
            i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i
          )
        };
      }
      return { items: [...state.items, { ...item, quantity: 1 }] };
    });
  },
  removeItem: (id) => {
    set((state) => ({
      items: state.items.filter(item => item.id !== id)
    }));
  },
  clearCart: () => set({ items: [] }),
  getTotal: () => {
    const { items } = get();
    return items.reduce((total, item) => total + item.price * item.quantity, 0);
  },
}));

// 主题状态
interface ThemeState {
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;
}

export const useThemeStore = create<ThemeState>((set) => ({
  theme: 'light',
  setTheme: (theme) => set({ theme }),
}));
```

### 3. 共享工具函数

```typescript
// shared-utils/src/api.ts
import axios from 'axios';

// 创建共享的axios实例
export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('auth-token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 处理认证失败
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 通用API函数
export const api = {
  get: <T>(url: string, config?: any) => apiClient.get<T>(url, config),
  post: <T>(url: string, data?: any, config?: any) => apiClient.post<T>(url, data, config),
  put: <T>(url: string, data?: any, config?: any) => apiClient.put<T>(url, data, config),
  delete: <T>(url: string, config?: any) => apiClient.delete<T>(url, config),
  patch: <T>(url: string, data?: any, config?: any) => apiClient.patch<T>(url, data, config),
};
```

## 🔄 微前端通信机制

### 1. 事件总线通信

```typescript
// shared-bus/src/EventBus.ts
class EventBus {
  private listeners: Map<string, Function[]> = new Map();

  subscribe(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);

    // 返回取消订阅函数
    return () => {
      const callbacks = this.listeners.get(event);
      if (callbacks) {
        const index = callbacks.indexOf(callback);
        if (index > -1) {
          callbacks.splice(index, 1);
        }
      }
    };
  }

  publish(event: string, data?: any) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  unsubscribe(event: string, callback: Function) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  unsubscribeAll(event: string) {
    this.listeners.delete(event);
  }
}

export const eventBus = new EventBus();

// 类型化事件
export const AppEvents = {
  USER_LOGIN: 'user:login',
  USER_LOGOUT: 'user:logout',
  CART_UPDATE: 'cart:update',
  THEME_CHANGE: 'theme:change',
  NAVIGATION: 'navigation',
} as const;

// 使用示例
// 在产品微应用中
eventBus.subscribe(AppEvents.CART_UPDATE, (data) => {
  console.log('Cart updated:', data);
});

// 在购物车微应用中
eventBus.publish(AppEvents.CART_UPDATE, {
  itemId: '123',
  quantity: 2,
});
```

### 2. 状态同步

```typescript
// shared-sync/src/StateManager.ts
class StateManager {
  private state: any = {};
  private subscribers: Map<string, Function[]> = new Map();

  setState(key: string, value: any) {
    this.state[key] = value;
    this.notifySubscribers(key, value);
  }

  getState(key: string) {
    return this.state[key];
  }

  subscribe(key: string, callback: Function) {
    if (!this.subscribers.has(key)) {
      this.subscribers.set(key, []);
    }
    this.subscribers.get(key)!.push(callback);

    return () => {
      const callbacks = this.subscribers.get(key);
      if (callbacks) {
        const index = callbacks.indexOf(callback);
        if (index > -1) {
          callbacks.splice(index, 1);
        }
      }
    };
  }

  private notifySubscribers(key: string, value: any) {
    const callbacks = this.subscribers.get(key);
    if (callbacks) {
      callbacks.forEach(callback => callback(value));
    }
  }
}

export const stateManager = new StateManager();

// 预定义状态键
export const StateKeys = {
  USER: 'user',
  THEME: 'theme',
  CART: 'cart',
  PREFERENCES: 'preferences',
} as const;
```

### 3. 共享服务层

```typescript
// shared-services/src/AuthService.ts
export class AuthService {
  private static instance: AuthService;

  private constructor() {}

  static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  async login(credentials: { email: string; password: string }) {
    const response = await api.post('/auth/login', credentials);
    const { user, token } = response.data;

    // 存储token
    localStorage.setItem('auth-token', token);

    // 更新全局状态
    useUserStore.getState().login(user);

    // 发布事件
    eventBus.publish(AppEvents.USER_LOGIN, user);

    return user;
  }

  async logout() {
    await api.post('/auth/logout');

    localStorage.removeItem('auth-token');
    useUserStore.getState().logout();
    eventBus.publish(AppEvents.USER_LOGOUT);
  }

  async getCurrentUser() {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      return null;
    }
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('auth-token');
  }
}
```

## 🎯 微前端部署策略

### 1. 独立部署配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  shell:
    build: ./apps/shell
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_BASE_URL=http://api:4000

  products:
    build: ./apps/products
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_BASE_URL=http://api:4000

  users:
    build: ./apps/users
    ports:
      - "3002:3002"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_BASE_URL=http://api:4000

  orders:
    build: ./apps/orders
    ports:
      - "3003:3003"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_BASE_URL=http://api:4000

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - shell
      - products
      - users
      - orders
```

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream shell {
        server shell:3000;
    }

    upstream products {
        server products:3001;
    }

    upstream users {
        server users:3002;
    }

    upstream orders {
        server orders:3003;
    }

    server {
        listen 80;
        server_name localhost;

        # 主应用
        location / {
            proxy_pass http://shell;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # 产品微应用
        location /products/ {
            proxy_pass http://products;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # 用户微应用
        location /users/ {
            proxy_pass http://users;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # 订单微应用
        location /orders/ {
            proxy_pass http://orders;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # 静态资源
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            proxy_pass http://shell;
            proxy_set_header Host $host;
        }
    }
}
```

### 2. CI/CD 配置

```yaml
# .github/workflows/deploy.yml
name: Deploy Micro Frontend Apps

on:
  push:
    branches: [main]

jobs:
  deploy-shell:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd apps/shell
          npm ci

      - name: Build app
        run: |
          cd apps/shell
          npm run build

      - name: Deploy to Vercel
        uses: vercel/action@v1
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID_SHELL }}
          working-directory: apps/shell

  deploy-products:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd apps/products
          npm ci

      - name: Build app
        run: |
          cd apps/products
          npm run build

      - name: Deploy to Vercel
        uses: vercel/action@v1
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID_PRODUCTS }}
          working-directory: apps/products

  deploy-users:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd apps/users
          npm ci

      - name: Build app
        run: |
          cd apps/users
          npm run build

      - name: Deploy to Vercel
        uses: vercel/action@v1
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID_USERS }}
          working-directory: apps/users

  deploy-orders:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd apps/orders
          npm ci

      - name: Build app
        run: |
          cd apps/orders
          npm run build

      - name: Deploy to Vercel
        uses: vercel/action@v1
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID_ORDERS }}
          working-directory: apps/orders
```

## 🚨 微前端最佳实践

### 1. 架构设计原则

```typescript
// shared-types/src/index.ts
// 定义共享类型
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user' | 'moderator';
}

export interface Product {
  id: string;
  name: string;
  price: number;
  description: string;
  category: string;
}

export interface CartItem {
  id: string;
  product: Product;
  quantity: number;
}

// 共享常量
export const API_ENDPOINTS = {
  AUTH: '/api/auth',
  PRODUCTS: '/api/products',
  USERS: '/api/users',
  ORDERS: '/api/orders',
} as const;

// 共享工具函数
export const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date);
};

export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};
```

### 2. 错误处理和监控

```typescript
// shared-monitoring/src/ErrorBoundary.tsx
import React from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class MicroFrontendErrorBoundary extends React.Component<
  { children: React.ReactNode },
  ErrorBoundaryState
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Micro Frontend Error:', error, errorInfo);

    // 发送错误到监控服务
    if (process.env.NODE_ENV === 'production') {
      fetch('/api/log-error', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          error: error.message,
          stack: error.stack,
          componentStack: errorInfo.componentStack,
        }),
      });
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-fallback">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false, error: null })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// 使用示例
function MicroFrontendWrapper({ children }: { children: React.ReactNode }) {
  return (
    <MicroFrontendErrorBoundary>
      <Suspense fallback={<div>Loading...</div>}>
        {children}
      </Suspense>
    </MicroFrontendErrorBoundary>
  );
}
```

### 3. 性能优化策略

```typescript
// shared-performance/src/PerformanceOptimizer.ts
export class PerformanceOptimizer {
  private static instance: PerformanceOptimizer;

  private constructor() {}

  static getInstance(): PerformanceOptimizer {
    if (!PerformanceOptimizer.instance) {
      PerformanceOptimizer.instance = new PerformanceOptimizer();
    }
    return PerformanceOptimizer.instance;
  }

  // 预加载微应用
  preloadMicroApp(appName: string) {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = 'script';
    link.href = `/${appName}/remoteEntry.js`;
    document.head.appendChild(link);
  }

  // 延迟加载微应用
  lazyLoadMicroApp(appName: string): Promise<any> {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = `/${appName}/remoteEntry.js`;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  // 监控微应用性能
  monitorMicroAppPerformance(appName: string) {
    if ('performance' in window) {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          if (entry.name.includes(appName)) {
            console.log(`${appName} performance:`, {
              duration: entry.duration,
              startTime: entry.startTime,
              type: entry.entryType,
            });
          }
        });
      });

      observer.observe({ entryTypes: ['measure', 'mark'] });
    }
  }
}
```

## 🎯 总结

Next.js 15 的微前端架构为大型应用提供了灵活、可扩展的解决方案。通过合理使用模块联邦、共享组件、状态管理和通信机制，可以构建出高度解耦、独立部署的现代Web应用。

### 关键要点：

1. **架构设计**：模块联邦、独立部署、技术栈灵活性
2. **共享资源**：组件库、状态管理、工具函数、类型定义
3. **通信机制**：事件总线、状态同步、服务层共享
4. **部署策略**：独立CI/CD、容器化部署、负载均衡
5. **最佳实践**：错误处理、性能优化、监控体系

### 实施建议：

- **渐进式迁移**：从现有应用开始，逐步拆分为微应用
- **统一规范**：制定统一的开发规范和最佳实践
- **共享治理**：建立共享资源的维护和更新机制
- **监控体系**：建立完整的性能监控和错误追踪系统

通过掌握这些微前端技术，可以构建出可维护、可扩展、高性能的现代Web应用架构。