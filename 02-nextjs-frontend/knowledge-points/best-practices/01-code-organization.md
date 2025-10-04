# 代码组织最佳实践

## 📚 概述

良好的代码组织是构建可维护、可扩展应用的基础。本指南涵盖了 Next.js 项目中的目录结构、组件组织、模块化设计等最佳实践。

## 🏗️ 项目目录结构

### 推荐目录结构
**现代化的 Next.js 项目结构**

```
my-nextjs-app/
├── README.md
├── .env.local                    # 环境变量
├── .gitignore
├── next.config.js               # Next.js 配置
├── package.json
├── tsconfig.json
├── tailwind.config.js           # Tailwind CSS 配置
├── .eslintrc.json               # ESLint 配置
├── .prettierrc                  # Prettier 配置
├── turbo.json                   # Turborepo 配置 (如果使用)
├── pnpm-workspace.yaml          # pnpm 工作区配置
├──
├── public/                      # 静态资源
│   ├── icons/
│   ├── images/
│   ├── locales/                 # 国际化文件
│   └── manifest.json
├──
├── src/                         # 源代码
│   ├── app/                     # Next.js 13+ App Router
│   │   ├── (auth)/             # 路由组 - 认证页面
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── (dashboard)/        # 路由组 - 仪表板
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── api/                 # API 路由
│   │   │   ├── auth/
│   │   │   ├── users/
│   │   │   └── posts/
│   │   ├── globals.css
│   │   ├── layout.tsx           # 根布局
│   │   └── page.tsx             # 首页
│   │
│   ├── components/              # 组件库
│   │   ├── ui/                  # 基础 UI 组件
│   │   │   ├── button/
│   │   │   ├── input/
│   │   │   ├── modal/
│   │   │   └── index.ts
│   │   ├── forms/               # 表单组件
│   │   ├── layout/              # 布局组件
│   │   ├── features/            # 功能组件
│   │   │   ├── auth/
│   │   │   ├── blog/
│   │   │   └── user-profile/
│   │   └── charts/              # 图表组件
│   │
│   ├── lib/                    # 工具库和配置
│   │   ├── utils/               # 通用工具函数
│   │   │   ├── api.ts
│   │   │   ├── auth.ts
│   │   │   ├── date.ts
│   │   │   ├── format.ts
│   │   │   └── validation.ts
│   │   ├── hooks/               # 自定义 Hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useLocalStorage.ts
│   │   │   └── useDebounce.ts
│   │   ├── providers/           # Context Providers
│   │   │   ├── theme-provider.tsx
│   │   │   ├── auth-provider.tsx
│   │   │   └── query-provider.tsx
│   │   ├── db/                  # 数据库配置
│   │   │   ├── prisma.ts
│   │   │   └── migrations/
│   │   ├── validations/         # 数据验证
│   │   │   └── schemas.ts
│   │   └── constants/           # 常量定义
│   │       ├── api.ts
│   │       └── routes.ts
│   │
│   ├── styles/                  # 样式文件
│   │   ├── globals.css
│   │   ├── components.css
│   │   └── variables.css        # CSS 变量
│   │
│   ├── types/                   # TypeScript 类型定义
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   ├── ui.ts
│   │   └── index.ts
│   │
│   └── data/                   # 静态数据
│       ├── blog/
│       └── mock/
│
├── docs/                        # 项目文档
├── scripts/                     # 构建脚本
├── tests/                       # 测试文件
├── .husky/                      # Git hooks
└── .vscode/                     # VS Code 配置
    ├── settings.json
    └── extensions.json
```

### 特性驱动目录结构
**按功能模块组织代码**

```
src/
├── features/                    # 功能模块
│   ├── authentication/
│   │   ├── components/
│   │   │   ├── LoginForm/
│   │   │   ├── RegisterForm/
│   │   │   └── PasswordReset/
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   └── useLogin.ts
│   │   ├── services/
│   │   │   └── authService.ts
│   │   ├── types/
│   │   │   └── auth.types.ts
│   │   └── index.ts
│   │
│   ├── blog/
│   │   ├── components/
│   │   │   ├── BlogList/
│   │   │   ├── BlogPost/
│   │   │   └── BlogEditor/
│   │   ├── hooks/
│   │   │   ├── useBlogPosts.ts
│   │   │   └── useBlogEditor.ts
│   │   ├── services/
│   │   │   └── blogService.ts
│   │   ├── types/
│   │   │   └── blog.types.ts
│   │   └── index.ts
│   │
│   └── user-profile/
│       ├── components/
│       ├── hooks/
│       ├── services/
│       └── types/
│
├── shared/                      # 共享代码
│   ├── components/              # 通用组件
│   ├── hooks/                   # 通用 hooks
│   ├── utils/                   # 通用工具
│   └── types/                   # 通用类型
│
└── app/                         # Next.js 页面
    ├── (auth)/
    ├── dashboard/
    └── blog/
```

## 🧩 组件组织

### 组件分类
**按功能和可复用性分类组件**

```typescript
// src/components/ui/index.ts
// 基础 UI 组件导出

export { default as Button } from './button';
export { default as Input } from './input';
export { default as Modal } from './modal';
export { default as Badge } from './badge';
export { default as Spinner } from './spinner';
export { default as Card } from './card';

// src/components/forms/index.ts
// 表单组件导出

export { default as FormField } from './form-field';
export { default as Form } from './form';
export { default as FormError } from './form-error';

// src/components/index.ts
// 主导出文件

export * from './ui';
export * from './forms';
export * from './layout';
export * from './features';
```

### 组件命名规范
**统一的组件命名和组织**

```typescript
// ✅ 好的组件命名
// src/components/ui/button/
export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', children, onClick, disabled, ...props }, ref) => {
    const baseClasses = 'font-medium rounded-md transition-colors';
    const variantClasses = {
      primary: 'bg-blue-600 text-white hover:bg-blue-700',
      secondary: 'bg-gray-600 text-white hover:bg-gray-700',
      outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50',
    };
    const sizeClasses = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
    };

    return (
      <button
        ref={ref}
        className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]}`}
        onClick={onClick}
        disabled={disabled}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

// 组件样式文件
// src/components/ui/button/button.module.css
.button {
  @apply inline-flex items-center justify-center;
}

.button--primary {
  @apply bg-blue-600 text-white;
}

.button--secondary {
  @apply bg-gray-600 text-white;
}
```

### 组件组合模式
**通过组合构建复杂组件**

```typescript
// src/components/ui/input/Input.tsx
export interface InputProps {
  label?: string;
  error?: string;
  helper?: string;
  required?: boolean;
  type?: 'text' | 'email' | 'password' | 'number';
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helper,
  required,
  type = 'text',
  placeholder,
  value,
  onChange,
}) => {
  return (
    <div className="form-field">
      {label && (
        <label className="form-label">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <input
        type={type}
        className={`form-input ${error ? 'error' : ''}`}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
      />
      {error && <span className="form-error">{error}</span>}
      {helper && <span className="form-helper">{helper}</span>}
    </div>
  );
};

// src/components/forms/FormField.tsx
interface FormFieldProps {
  name: string;
  label?: string;
  required?: boolean;
  type?: 'text' | 'email' | 'password';
  placeholder?: string;
  helper?: string;
}

export const FormField: React.FC<FormFieldProps> = ({
  name,
  label,
  required,
  type = 'text',
  placeholder,
  helper,
}) => {
  const {
    register,
    formState: { errors },
  } = useFormContext();

  const error = errors[name]?.message as string | undefined;

  return (
    <Input
      label={label}
      error={error}
      helper={helper}
      required={required}
      type={type}
      placeholder={placeholder}
      {...register(name)}
    />
  );
};
```

## 📦 模块化设计

### 模块导出策略
**清晰的模块导出模式**

```typescript
// src/lib/utils/api.ts
interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export class ApiClient {
  private baseUrl: string;
  private headers: Record<string, string>;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.headers = {
      'Content-Type': 'application/json',
    };
  }

  setAuthToken(token: string) {
    this.headers.Authorization = `Bearer ${token}`;
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      headers: this.headers,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async post<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}

// 默认导出
export default new ApiClient(process.env.NEXT_PUBLIC_API_URL!);

// 具体 API 服务
export const userService = {
  getProfile: () => apiClient.get<User>('/user/profile'),
  updateProfile: (data: UpdateProfileData) => apiClient.post<User>('/user/profile', data),
};

// src/lib/utils/index.ts
export { default as apiClient } from './api';
export { userService } from './api';
export { formatDate } from './date';
export { validateEmail } from './validation';
export type { ApiResponse } from './api';
```

### 模块依赖管理
**清晰的依赖关系和循环避免**

```typescript
// ✅ 好的依赖结构
// src/lib/auth/index.ts
export { AuthService } from './auth.service';
export { useAuth } from './use-auth';
export { AuthProvider } from './auth-provider';
export type { User, AuthState } from './auth.types';

// src/lib/hooks/useAuth.ts
import { AuthService } from '../auth/auth.service';
import { User } from '../auth/auth.types';

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 初始化认证状态
    const initAuth = async () => {
      try {
        const currentUser = await AuthService.getCurrentUser();
        setUser(currentUser);
      } catch (error) {
        console.error('Auth initialization failed:', error);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true);
    try {
      const user = await AuthService.login(email, password);
      setUser(user);
      return user;
    } catch (error) {
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    await AuthService.logout();
    setUser(null);
  }, []);

  return { user, loading, login, logout };
};

// ❌ 避免循环依赖
// 错误示例：
// a.ts 导入 b.ts
// b.ts 导入 a.ts

// 正确示例：使用依赖注入
// src/lib/auth/auth.service.ts
export class AuthService {
  constructor(private apiClient: ApiClient) {}
}

// src/lib/api/client.ts
export class ApiClient {
  // 不依赖 AuthService
}
```

## 🔧 工具函数组织

### 工具函数分类
**按功能分类的工具函数**

```typescript
// src/lib/utils/date.ts
export const formatDate = (date: Date | string, format: string = 'YYYY-MM-DD'): string => {
  const d = new Date(date);
  // 格式化逻辑
  return d.toISOString().split('T')[0];
};

export const isToday = (date: Date | string): boolean => {
  const today = new Date();
  const checkDate = new Date(date);
  return checkDate.toDateString() === today.toDateString();
};

export const addDays = (date: Date, days: number): Date => {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
};

// src/lib/utils/validation.ts
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePassword = (password: string): {
  isValid: boolean;
  errors: string[];
} => {
  const errors: string[] = [];

  if (password.length < 8) {
    errors.push('Password must be at least 8 characters');
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }

  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }

  if (!/\d/.test(password)) {
    errors.push('Password must contain at least one number');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

// src/lib/utils/format.ts
export const formatCurrency = (
  amount: number,
  currency: string = 'USD',
  locale: string = 'en-US'
): string => {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
  }).format(amount);
};

export const formatPhoneNumber = (phone: string): string => {
  // 美国电话号码格式化
  const cleaned = phone.replace(/\D/g, '');
  const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
  if (match) {
    return `(${match[1]}) ${match[2]}-${match[3]}`;
  }
  return phone;
};

// src/lib/utils/index.ts
export * from './date';
export * from './validation';
export * from './format';
export * from './storage';
export * from './string';
```

### 高阶工具函数
**复用性强的高级工具函数**

```typescript
// src/lib/utils/async.ts
export const withRetry = async <T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> => {
  let lastError: Error;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
      }
    }
  }

  throw lastError!;
};

export const withTimeout = <T>(
  fn: () => Promise<T>,
  timeoutMs: number
): Promise<T> => {
  return Promise.race([
    fn(),
    new Promise<never>((_, reject) => {
      setTimeout(() => reject(new Error('Operation timed out')), timeoutMs);
    }),
  ]);
};

export const debounce = <T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout;

  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
};

export const throttle = <T extends (...args: any[]) => any>(
  fn: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      fn(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

// src/lib/utils/promise.ts
export const createPromise = <T>(): {
  promise: Promise<T>;
  resolve: (value: T) => void;
  reject: (error: Error) => void;
} => {
  let resolve: (value: T) => void;
  let reject: (error: Error) => void;

  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });

  return { promise, resolve: resolve!, reject: reject! };
};

export const allSettled = async <T>(
  promises: Promise<T>[]
): Promise<{ fulfilled: T[]; rejected: Error[] }> => {
  const results = await Promise.allSettled(promises);

  return results.reduce(
    (acc, result) => {
      if (result.status === 'fulfilled') {
        acc.fulfilled.push(result.value);
      } else {
        acc.rejected.push(result.reason);
      }
      return acc;
    },
    { fulfilled: [] as T[], rejected: [] as Error[] }
  );
};
```

## 📝 类型定义组织

### 类型定义结构
**清晰的 TypeScript 类型组织**

```typescript
// src/types/api.types.ts
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

export interface ErrorResponse {
  success: false;
  error: string;
  code: string;
  details?: any;
}

// src/types/auth.types.ts
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: 'user' | 'admin';
  createdAt: string;
  updatedAt: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
  remember?: boolean;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

// src/types/ui.types.ts
export interface Theme {
  mode: 'light' | 'dark';
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    surface: string;
    text: string;
  };
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

// src/types/index.ts
export * from './api.types';
export * from './auth.types';
export * from './ui.types';
export * from './blog.types';
```

### 类型守卫和验证
**类型安全的运行时验证**

```typescript
// src/types/guards.ts
export const isString = (value: unknown): value is string => {
  return typeof value === 'string';
};

export const isNumber = (value: unknown): value is number => {
  return typeof value === 'number' && !isNaN(value);
};

export const isBoolean = (value: unknown): value is boolean => {
  return typeof value === 'boolean';
};

export const isObject = (value: unknown): value is Record<string, any> => {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
};

export const isArray = (value: unknown): value is any[] => {
  return Array.isArray(value);
};

// 特定类型守卫
export const isUser = (value: unknown): value is User => {
  if (!isObject(value)) return false;

  const user = value as Record<string, any>;
  return (
    isString(user.id) &&
    isString(user.email) &&
    isString(user.name) &&
    ['user', 'admin'].includes(user.role)
  );
};

export const isApiResponse = <T = any>(
  value: unknown
): value is ApiResponse<T> => {
  if (!isObject(value)) return false;

  const response = value as Record<string, any>;
  return (
    typeof response.success === 'boolean' &&
    (response.data === undefined || response.success)
  );
};
```

## 🎯 导入导出策略

### 导入规范
**清晰的导入顺序和格式**

```typescript
// ✅ 推荐的导入顺序
// 1. React 相关
import React, { useState, useEffect, useCallback } from 'react';
import { NextPage, GetServerSideProps } from 'next';
import { useRouter } from 'next/router';

// 2. 第三方库
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { Button, Input } from 'antd';

// 3. 项目内部模块 - 绝对路径
import { AuthService } from '@/lib/auth/auth.service';
import { useAuth } from '@/lib/hooks/useAuth';
import { Button as CustomButton } from '@/components/ui/button';
import { formatDate } from '@/lib/utils/date';

// 4. 相对路径导入
import { LoginForm } from './LoginForm';
import { loginSchema } from './validations';

// 5. 类型导入
import type { User, LoginRequest } from '@/types/auth.types';

// ✅ 动态导入
const LazyComponent = React.lazy(() => import('./LazyComponent'));

// ✅ 类型导入
import type { MouseEvent } from 'react';

// ❌ 避免的导入方式
// import * as React from 'react'; // 避免命名空间导入
// import { a, b, c, d, e, f, g, h, i, j } from 'large-module'; // 避免一次导入太多
```

### 导出策略
**清晰的导出模式和命名**

```typescript
// ✅ 命名导出 + 默认导出
export { validateEmail, validatePassword } from './validation';
export { formatDate, addDays } from './date';
export { default as apiClient } from './client';

// ✅ 类型导出
export type { User, AuthState } from './auth.types';

// ✅ 重新导出
export { Button, Input, Modal } from '@/components/ui';
export { useAuth, useLocalStorage } from '@/lib/hooks';

// ✅ 批量导出
export * from './constants';
export * as Utils from './utils';

// 组件导出
export interface ButtonProps {
  // ...
}

export const Button: React.FC<ButtonProps> = ({ children, ...props }) => {
  // ...
};

export default Button;

// 库的导出
// src/index.ts
export { default as Button } from './components/Button';
export { Input } from './components/Input';
export { Modal } from './components/Modal';
export { useAuth } from './hooks/useAuth';
export { AuthService } from './services/AuthService';
export type { User, AuthState } from './types';
```

## 📋 最佳实践清单

### 目录结构
- [ ] 使用特性驱动的目录结构
- [ ] 按功能和复用性分类组件
- [ ] 保持清晰的层级关系
- [ ] 使用一致的命名约定
- [ ] 避免过深的嵌套结构

### 组件组织
- [ ] 单一职责原则
- [ ] 组件组合优于继承
- [ ] 清晰的 props 接口
- [ ] 合理的组件大小
- [ ] 统一的导出模式

### 模块化设计
- [ ] 清晰的模块边界
- [ ] 避免循环依赖
- [ ] 合理的导出策略
- [ ] 模块化工具函数
- [ ] 统一的类型定义

### 导入导出
- [ ] 一致的导入顺序
- [ ] 优先使用绝对路径
- [ ] 避免命名空间导入
- [ ] 使用类型导入
- [ ] 合理的动态导入

## 📖 总结

良好的代码组织是项目成功的关键：

### 核心原则：
1. **清晰的结构**: 目录结构清晰易懂
2. **模块化设计**: 功能模块化，职责分离
3. **一致性**: 命名和组织风格一致
4. **可维护性**: 便于理解和修改
5. **可扩展性**: 便于添加新功能

### 实施要点：
1. **选择合适的目录结构**: 根据项目规模选择
2. **建立命名规范**: 团队统一遵循
3. **使用路径别名**: 简化导入路径
4. **模块化设计**: 避免过度耦合
5. **类型安全**: 充分利用 TypeScript

### 工具支持：
1. **ESLint**: 代码质量检查
2. **Prettier**: 代码格式化
3. **路径映射**: VS Code 跳转支持
4. **Git Hooks**: 提交前检查
5. **文档生成**: 自动生成 API 文档

通过良好的代码组织，可以显著提升项目的可维护性和团队协作效率。