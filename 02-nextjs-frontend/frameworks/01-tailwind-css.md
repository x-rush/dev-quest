# Tailwind CSS 深度指南 - 实用优先的 CSS 框架

## 概述

Tailwind CSS 是一个实用优先的 CSS 框架，它提供了大量的工具类来快速构建用户界面。与传统的 CSS 框架（如 Bootstrap）不同，Tailwind CSS 不提供预定义的组件，而是提供原子化的工具类，让开发者可以自由组合来构建自定义设计。

## 为什么选择 Tailwind CSS

### 与传统 CSS 框架的对比

| Bootstrap | Tailwind CSS |
|-----------|-------------|
| 预定义组件 | 原子化工具类 |
| 有限的定制性 | 完全可定制 |
| 相同的设计风格 | 独特的设计系统 |
| 较大的包体积 | 按需生成 CSS |
| 学习曲线平缓 | 需要掌握工具类 |

### Tailwind CSS 的优势
- **快速开发**: 无需编写自定义 CSS
- **一致性**: 统一的设计系统
- **响应式设计**: 内置响应式工具类
- **性能优化**: 按需生成，移除未使用的样式
- **可定制**: 完全可配置的设计系统

## 安装和配置

### 1. 基础安装

```bash
# 创建 Next.js 项目
npx create-next-app@latest my-app --typescript --tailwind --app

# 或者在现有项目中安装
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 2. 配置文件

```js
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      // 自定义配置
    },
  },
  plugins: [
    // 插件配置
  ],
}
```

### 3. PostCSS 配置

```js
// postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

## 核心概念

### 1. 工具类系统

```jsx
// 布局工具类
<div className="container mx-auto px-4">
  <div className="grid grid-cols-3 gap-4">
    <div className="col-span-2">主要内容</div>
    <div className="col-span-1">侧边栏</div>
  </div>
</div>

// 间距工具类
<div className="p-4">padding: 1rem</div>
<div className="px-4 py-2">水平垂直 padding</div>
<div className="m-4">margin: 1rem</div>
<div className="mt-4">上边距: 1rem</div>

// 尺寸工具类
<div className="w-full">宽度: 100%</div>
<div className="w-64">宽度: 16rem</div>
<div className="h-32">高度: 8rem</div>
<div className="max-w-7xl">最大宽度: 80rem</div>
```

### 2. 颜色系统

```jsx
// 基础颜色
<div className="bg-red-500 text-white">红色背景</div>
<div className="bg-blue-100 text-blue-900">浅蓝色背景</div>
<div className="border border-gray-300">灰色边框</div>

// 自定义颜色
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
      },
    },
  },
}

// 使用自定义颜色
<div className="bg-primary-500 text-white">主色调</div>
```

### 3. 字体系统

```jsx
// 字体大小
<h1 className="text-4xl">超大标题</h1>
<h2 className="text-2xl">大标题</h2>
<p className="text-base">普通文本</p>
<p className="text-sm">小文本</p>

// 字体粗细
<p className="font-light">细体</p>
<p className="font-normal">正常</p>
<p className="font-medium">中等</p>
<p className="font-semibold">半粗</p>
<p className="font-bold">粗体</p>

// 文本对齐
<p className="text-left">左对齐</p>
<p className="text-center">居中对齐</p>
<p className="text-right">右对齐</p>
<p className="text-justify">两端对齐</p>
```

## 响应式设计

### 1. 断点系统

```jsx
// 默认断点
// sm: 640px
// md: 768px
// lg: 1024px
// xl: 1280px
// 2xl: 1536px

// 响应式工具类
<div className="w-full sm:w-1/2 md:w-1/3 lg:w-1/4">
  响应式宽度
</div>

<div className="text-sm md:text-base lg:text-lg">
  响应式字体
</div>

<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
  响应式网格
</div>
```

### 2. 响应式状态

```jsx
// 隐藏/显示元素
<div className="hidden md:block">在桌面显示</div>
<div className="block md:hidden">在移动端显示</div>

// 响应式布局
<div className="flex flex-col md:flex-row">
  <div className="w-full md:w-1/3">侧边栏</div>
  <div className="w-full md:w-2/3">主要内容</div>
</div>
```

## 组件开发

### 1. 按钮组件

```jsx
// components/Button.jsx
import clsx from 'clsx';

const Button = ({
  children,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  className = '',
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
    outline: 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-blue-500',
    ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
    link: 'text-blue-600 hover:text-blue-800 hover:underline',
  };

  const sizes = {
    small: 'px-3 py-1.5 text-sm',
    medium: 'px-4 py-2 text-base',
    large: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={clsx(baseStyles, variants[variant], sizes[size], className)}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      )}
      {children}
    </button>
  );
};

export default Button;
```

### 2. 卡片组件

```jsx
// components/Card.jsx
import clsx from 'clsx';

const Card = ({
  children,
  className = '',
  hover = false,
  ...props
}) => {
  return (
    <div
      className={clsx(
        'bg-white rounded-lg shadow-md overflow-hidden',
        hover && 'hover:shadow-lg transition-shadow duration-300',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

const CardHeader = ({ children, className = '', ...props }) => (
  <div className={clsx('px-6 py-4 border-b border-gray-200', className)} {...props}>
    {children}
  </div>
);

const CardTitle = ({ children, className = '', ...props }) => (
  <h3 className={clsx('text-lg font-semibold text-gray-900', className)} {...props}>
    {children}
  </h3>
);

const CardDescription = ({ children, className = '', ...props }) => (
  <p className={clsx('text-sm text-gray-600 mt-1', className)} {...props}>
    {children}
  </p>
);

const CardContent = ({ children, className = '', ...props }) => (
  <div className={clsx('px-6 py-4', className)} {...props}>
    {children}
  </div>
);

const CardFooter = ({ children, className = '', ...props }) => (
  <div className={clsx('px-6 py-4 bg-gray-50 border-t border-gray-200', className)} {...props}>
    {children}
  </div>
);

Card.Header = CardHeader;
Card.Title = CardTitle;
Card.Description = CardDescription;
Card.Content = CardContent;
Card.Footer = CardFooter;

export default Card;
```

### 3. 表单组件

```jsx
// components/Input.jsx
import clsx from 'clsx';
import { forwardRef } from 'react';

const Input = forwardRef(({
  label,
  error,
  helperText,
  className = '',
  ...props
}, ref) => {
  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-sm font-medium text-gray-700">
          {label}
        </label>
      )}
      <input
        ref={ref}
        className={clsx(
          'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
          error && 'border-red-300 focus:border-red-500 focus:ring-red-500',
          className
        )}
        {...props}
      />
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
      {helperText && !error && (
        <p className="text-sm text-gray-500">{helperText}</p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;
```

## 自定义主题

### 1. 扩展配置

```js
// tailwind.config.js
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
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
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
      boxShadow: {
        'glow': '0 0 20px rgba(59, 130, 246, 0.5)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
```

### 2. 自定义插件

```js
// tailwind.config.js
const plugin = require('tailwindcss/plugin');

const aspectRatio = plugin(function ({ addUtilities, matchUtilities, theme }) {
  addUtilities({
    '.aspect-square': {
      'aspect-ratio': '1 / 1',
    },
    '.aspect-video': {
      'aspect-ratio': '16 / 9',
    },
  });

  matchUtilities(
    {
      'aspect-w': (value) => ({
        '--tw-aspect-w': value,
      }),
      'aspect-h': (value) => ({
        '--tw-aspect-h': value,
      }),
      'aspect-ratio': (value) => ({
        'aspect-ratio': value,
      }),
    },
    { values: theme('aspectRatio') }
  );
});

module.exports = {
  plugins: [
    aspectRatio,
  ],
}
```

## 高级特性

### 1. JIT 模式

```js
// tailwind.config.js
module.exports = {
  mode: 'jit',
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  // ...
}
```

### 2. 暗色模式

```js
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  // ...
}
```

```jsx
// components/DarkModeToggle.jsx
'use client';

import { useState, useEffect } from 'react';

export default function DarkModeToggle() {
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    const isDark = localStorage.getItem('darkMode') === 'true';
    setDarkMode(isDark);
    if (isDark) {
      document.documentElement.classList.add('dark');
    }
  }, []);

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    localStorage.setItem('darkMode', newDarkMode.toString());

    if (newDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  return (
    <button
      onClick={toggleDarkMode}
      className="p-2 rounded-md bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
    >
      {darkMode ? '🌙' : '☀️'}
    </button>
  );
}
```

### 3. 自定义工具类

```css
/* styles/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn {
    @apply font-medium rounded-md transition-colors;
  }

  .btn-primary {
    @apply bg-blue-600 text-white hover:bg-blue-700;
  }

  .btn-secondary {
    @apply bg-gray-200 text-gray-900 hover:bg-gray-300;
  }

  .card {
    @apply bg-white rounded-lg shadow-md overflow-hidden;
  }

  .input {
    @apply block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500;
  }
}

@layer utilities {
  .text-balance {
    text-wrap: balance;
  }

  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }

  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
}
```

## 性能优化

### 1. 按需生成

```js
// postcss.config.js
module.exports = {
  plugins: {
    '@tailwindcss/jit': {},
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

### 2. CSS 优化

```js
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  optimizeFonts: true,
  experimental: {
    optimizeCss: true,
  },
}

module.exports = nextConfig;
```

### 3. 样式分割

```jsx
// 动态导入样式
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(
  () => import('../components/HeavyComponent'),
  {
    loading: () => <div>Loading...</div>,
    ssr: false,
  }
);
```

## 实战示例

### 1. 完整的仪表板布局

```jsx
// layouts/Dashboard.jsx
import { useState } from 'react';
import { FiMenu, FiX, FiHome, FiUsers, FiSettings, FiBell } from 'react-icons/fi';
import Button from '../components/Button';
import DarkModeToggle from '../components/DarkModeToggle';

export default function DashboardLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigation = [
    { name: '仪表板', href: '/dashboard', icon: FiHome },
    { name: '用户管理', href: '/dashboard/users', icon: FiUsers },
    { name: '系统设置', href: '/dashboard/settings', icon: FiSettings },
    { name: '通知中心', href: '/dashboard/notifications', icon: FiBell },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* 移动端侧边栏遮罩 */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* 侧边栏 */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 text-gray-900 dark:text-white transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}>
        <div className="flex items-center justify-between h-16 px-4 bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
          <h1 className="text-xl font-bold">管理系统</h1>
          <Button
            variant="ghost"
            size="small"
            className="lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <FiX className="h-5 w-5" />
          </Button>
        </div>

        <nav className="mt-8">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <a
                key={item.name}
                href={item.href}
                className="flex items-center px-4 py-3 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <Icon className="mr-3 h-5 w-5" />
                {item.name}
              </a>
            );
          })}
        </nav>
      </div>

      {/* 主内容区域 */}
      <div className="lg:pl-64">
        {/* 顶部导航 */}
        <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between h-16 px-4">
            <Button
              variant="ghost"
              size="small"
              className="lg:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <FiMenu className="h-5 w-5" />
            </Button>

            <div className="flex items-center space-x-4">
              <DarkModeToggle />

              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                  A
                </div>
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">管理员</span>
              </div>
            </div>
          </div>
        </header>

        {/* 页面内容 */}
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
```

### 2. 数据表格组件

```jsx
// components/DataTable.jsx
import { useState, useMemo } from 'react';
import Button from './Button';
import Input from './Input';

function DataTable({
  data,
  columns,
  searchable = true,
  sortable = true,
  pagination = true,
  pageSize = 10,
}) {
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'ascending' });

  // 搜索和排序数据
  const filteredData = useMemo(() => {
    let filtered = data;

    // 搜索过滤
    if (searchTerm) {
      filtered = filtered.filter(item =>
        Object.values(item).some(value =>
          String(value).toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // 排序
    if (sortConfig.key) {
      filtered.sort((a, b) => {
        if (a[sortConfig.key] < b[sortConfig.key]) {
          return sortConfig.direction === 'ascending' ? -1 : 1;
        }
        if (a[sortConfig.key] > b[sortConfig.key]) {
          return sortConfig.direction === 'ascending' ? 1 : -1;
        }
        return 0;
      });
    }

    return filtered;
  }, [data, searchTerm, sortConfig]);

  // 分页
  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize;
    return filteredData.slice(startIndex, startIndex + pageSize);
  }, [filteredData, currentPage, pageSize]);

  const totalPages = Math.ceil(filteredData.length / pageSize);

  const handleSort = (key) => {
    let direction = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  const getSortIcon = (key) => {
    if (sortConfig.key !== key) return null;
    return sortConfig.direction === 'ascending' ? '↑' : '↓';
  };

  return (
    <div className="space-y-4">
      {/* 搜索栏 */}
      {searchable && (
        <div className="flex items-center space-x-4">
          <Input
            placeholder="搜索..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="max-w-sm"
          />
        </div>
      )}

      {/* 表格 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                {columns.map((column) => (
                  <th
                    key={column.key}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600"
                    onClick={() => sortable && handleSort(column.key)}
                  >
                    <div className="flex items-center space-x-1">
                      <span>{column.label}</span>
                      {sortable && getSortIcon(column.key)}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {paginatedData.map((row, index) => (
                <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  {columns.map((column) => (
                    <td key={column.key} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {column.render ? column.render(row[column.key], row) : row[column.key]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 分页 */}
      {pagination && totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-700 dark:text-gray-300">
            显示 {((currentPage - 1) * pageSize) + 1} 到 {Math.min(currentPage * pageSize, filteredData.length)} 条，共 {filteredData.length} 条
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="small"
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
            >
              上一页
            </Button>
            <span className="text-sm text-gray-700 dark:text-gray-300">
              第 {currentPage} 页，共 {totalPages} 页
            </span>
            <Button
              variant="outline"
              size="small"
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
            >
              下一页
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

export default DataTable;
```

## 最佳实践

### 1. 命名约定

```jsx
// 使用语义化的类名
<div className="flex items-center justify-between">
  <h1 className="text-2xl font-bold text-gray-900">标题</h1>
  <Button variant="primary">操作</Button>
</div>

// 避免过度嵌套
<div className="container mx-auto px-4 py-8">
  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
    {cards.map(card => (
      <div key={card.id} className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-2">{card.title}</h3>
        <p className="text-gray-600">{card.description}</p>
      </div>
    ))}
  </div>
</div>
```

### 2. 可复用组件

```jsx
// 创建可复用的布局组件
const Container = ({ children, className = '', ...props }) => (
  <div className={`container mx-auto px-4 ${className}`} {...props}>
    {children}
  </div>
);

const Section = ({ children, className = '', ...props }) => (
  <section className={`py-12 ${className}`} {...props}>
    {children}
  </section>
);

const Grid = ({ children, className = '', ...props }) => (
  <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 ${className}`} {...props}>
    {children}
  </div>
);
```

### 3. 性能考虑

```jsx
// 使用动态导入减少初始包大小
import dynamic from 'next/dynamic';

const HeavyChart = dynamic(() => import('../components/Chart'), {
  loading: () => <div>图表加载中...</div>,
  ssr: false,
});

// 按需使用工具类
<div className="hover:shadow-lg transition-shadow duration-300">
  悬停效果
</div>
```

## 下一步

掌握 Tailwind CSS 后，你可以继续学习：

1. **状态管理** - 学习 Zustand、Jotai 等现代状态管理库
2. **表单处理** - 掌握 React Hook Form 和 Zod 验证
3. **数据获取** - 学习 TanStack Query 和 SWR
4. **UI 组件库** - 学习 Radix UI 和其他组件库

---

*Tailwind CSS 是现代前端开发的强大工具，掌握它将大大提高你的开发效率和设计一致性。*