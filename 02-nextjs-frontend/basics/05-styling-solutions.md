# Next.js 样式解决方案 - 现代前端样式开发

## 概述

样式是现代前端开发的重要组成部分。与 PHP 开发中通常使用 CSS 文件和模板引擎不同，Next.js 提供了多种现代化的样式解决方案。本指南将帮助你掌握 Tailwind CSS、CSS Modules、CSS-in-JS 等主流样式方案。

## 从 PHP 样式到 Next.js 样式的对比

### 传统 PHP 样式方式
```php
<!-- PHP 模板中的样式 -->
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="/css/style.css">
    <link rel="stylesheet" href="/css/bootstrap.min.css">
</head>
<body>
    <div class="container">
        <div class="row">
            <div class="col-md-6">
                <h1 class="title">标题</h1>
                <p class="description">描述文本</p>
            </div>
        </div>
    </div>
</body>
</html>
```

### Next.js 样式方式
```jsx
// 使用 Tailwind CSS
<div className="container mx-auto px-4">
  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div>
      <h1 className="text-2xl font-bold text-gray-900">标题</h1>
      <p className="text-gray-600">描述文本</p>
    </div>
  </div>
</div>
```

## Tailwind CSS

### 1. 安装和配置

```bash
# 安装 Tailwind CSS
npm install -D tailwindcss postcss autoprefixer

# 初始化配置文件
npx tailwindcss init -p
```

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
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
```

```js
// postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

### 2. 基础用法

```jsx
// 布局
<div className="container mx-auto px-4 py-8">
  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">卡片标题</h2>
      <p className="text-gray-600">卡片内容</p>
    </div>
  </div>
</div>

// 按钮
<button className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded">
  点击我
</button>

// 响应式设计
<div className="text-sm md:text-base lg:text-lg">
  响应式文本
</div>

// 状态样式
<input
  type="text"
  className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
  placeholder="输入文本"
/>
```

### 3. 自定义组件

```jsx
// components/Button.jsx
const Button = ({ children, variant = 'primary', size = 'md', ...props }) => {
  const baseStyles = "font-medium rounded-md transition-colors";

  const variants = {
    primary: "bg-blue-500 hover:bg-blue-600 text-white",
    secondary: "bg-gray-200 hover:bg-gray-300 text-gray-800",
    danger: "bg-red-500 hover:bg-red-600 text-white",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-base",
    lg: "px-6 py-3 text-lg",
  };

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]}`}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;
```

### 4. 暗色模式

```jsx
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  // ... 其他配置
}

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
      className="p-2 rounded-md bg-gray-200 dark:bg-gray-700"
    >
      {darkMode ? '🌙' : '☀️'}
    </button>
  );
}

// 使用暗色模式
<div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
  <h1 className="text-2xl font-bold">暗色模式示例</h1>
  <p className="text-gray-600 dark:text-gray-300">
    这是一个支持暗色模式的组件
  </p>
</div>
```

## CSS Modules

### 1. 基础用法

```css
/* components/Card.module.css */
.card {
  @apply bg-white rounded-lg shadow-md overflow-hidden;
}

.cardHeader {
  @apply px-6 py-4 border-b border-gray-200;
}

.cardTitle {
  @apply text-xl font-semibold text-gray-900;
}

.cardContent {
  @apply px-6 py-4;
}

.cardFooter {
  @apply px-6 py-4 bg-gray-50 border-t border-gray-200;
}
```

```jsx
// components/Card.jsx
import styles from './Card.module.css';

export default function Card({ title, children, footer }) {
  return (
    <div className={styles.card}>
      {title && (
        <div className={styles.cardHeader}>
          <h2 className={styles.cardTitle}>{title}</h2>
        </div>
      )}
      <div className={styles.cardContent}>
        {children}
      </div>
      {footer && (
        <div className={styles.cardFooter}>
          {footer}
        </div>
      )}
    </div>
  );
}
```

### 2. 组合使用

```css
/* components/Button.module.css */
.button {
  @apply font-medium rounded-md transition-colors cursor-pointer;
}

.primary {
  @apply bg-blue-500 hover:bg-blue-600 text-white;
}

.secondary {
  @apply bg-gray-200 hover:bg-gray-300 text-gray-800;
}

.small {
  @apply px-3 py-1.5 text-sm;
}

.medium {
  @apply px-4 py-2 text-base;
}

.large {
  @apply px-6 py-3 text-lg;
}
```

```jsx
// components/Button.jsx
import styles from './Button.module.css';

export default function Button({
  children,
  variant = 'primary',
  size = 'medium',
  className = '',
  ...props
}) {
  return (
    <button
      className={`${styles.button} ${styles[variant]} ${styles[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
```

## CSS-in-JS

### 1. Styled Components

```bash
# 安装 styled-components
npm install styled-components
```

```jsx
// components/StyledCard.jsx
import styled from 'styled-components';

const CardContainer = styled.div`
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  }
`;

const CardHeader = styled.div`
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
`;

const CardTitle = styled.h2`
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
`;

const CardContent = styled.div`
  padding: 1.5rem;
`;

const CardFooter = styled.div`
  padding: 1rem 1.5rem;
  background-color: #f9fafb;
  border-top: 1px solid #e5e7eb;
`;

export default function StyledCard({ title, children, footer }) {
  return (
    <CardContainer>
      {title && (
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
      )}
      <CardContent>{children}</CardContent>
      {footer && <CardFooter>{footer}</Footer>}
    </CardContainer>
  );
}
```

### 2. Emotion

```bash
# 安装 emotion
npm install @emotion/react @emotion/styled
```

```jsx
/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react';

const cardStyles = css`
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  }
`;

const headerStyles = css`
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
`;

export default function EmotionCard({ title, children }) {
  return (
    <div css={cardStyles}>
      {title && (
        <div css={headerStyles}>
          <h2 css={{ fontSize: '1.25rem', fontWeight: 600, margin: 0 }}>
            {title}
          </h2>
        </div>
      )}
      <div css={{ padding: '1.5rem' }}>
        {children}
      </div>
    </div>
  );
}
```

## Global Styles

### 1. 全局样式文件

```css
/* styles/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* 自定义全局样式 */
* {
  box-sizing: border-box;
}

body {
  font-family: 'Inter', sans-serif;
  line-height: 1.6;
  color: #111827;
}

/* 自定义组件样式 */
.btn {
  @apply font-medium rounded-md transition-colors cursor-pointer;
}

.btn-primary {
  @apply bg-blue-500 hover:bg-blue-600 text-white;
}

.btn-secondary {
  @apply bg-gray-200 hover:bg-gray-300 text-gray-800;
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.6s ease-out;
}
```

```jsx
// app/layout.tsx
import '../styles/globals.css';

export default function RootLayout({ children }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
```

### 2. 主题配置

```jsx
// context/ThemeContext.jsx
'use client';

import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setTheme(savedTheme);
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setTheme('dark');
    }
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
```

## 响应式设计

### 1. Tailwind 响应式设计

```jsx
// 响应式布局
<div className="container mx-auto px-4">
  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
    {items.map(item => (
      <div key={item.id} className="bg-white rounded-lg shadow p-4">
        {item.content}
      </div>
    ))}
  </div>
</div>

// 响应式导航
function ResponsiveNavigation() {
  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <span className="text-xl font-bold">Logo</span>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              <a href="#" className="text-gray-900 hover:text-blue-600 px-3 py-2">首页</a>
              <a href="#" className="text-gray-600 hover:text-blue-600 px-3 py-2">关于</a>
              <a href="#" className="text-gray-600 hover:text-blue-600 px-3 py-2">服务</a>
              <a href="#" className="text-gray-600 hover:text-blue-600 px-3 py-2">联系</a>
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button className="text-gray-600 hover:text-gray-900">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
```

### 2. CSS Modules 响应式设计

```css
/* components/ResponsiveGrid.module.css */
.grid {
  display: grid;
  gap: 1rem;
}

.grid {
  grid-template-columns: 1fr;
}

@media (min-width: 640px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 768px) {
  .grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1024px) {
  .grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
```

```jsx
// components/ResponsiveGrid.jsx
import styles from './ResponsiveGrid.module.css';

export default function ResponsiveGrid({ children }) {
  return (
    <div className={styles.grid}>
      {children}
    </div>
  );
}
```

## 动画和过渡

### 1. Tailwind 动画

```jsx
// 基础动画
<div className="animate-bounce">弹跳动画</div>
<div className="animate-pulse">脉冲动画</div>
<div className="animate-spin">旋转动画</div>

// 自定义动画
<div className="animate-fade-in">淡入动画</div>

// 过渡效果
<button className="transition-colors duration-200 hover:bg-blue-600">
  颜色过渡
</button>

<div className="transition-transform duration-300 hover:scale-105">
  缩放过渡
</div>
```

```css
/* 自定义动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}
```

### 2. Framer Motion 动画库

```bash
# 安装 framer-motion
npm install framer-motion
```

```jsx
// components/AnimatedCard.jsx
import { motion } from 'framer-motion';

export default function AnimatedCard({ title, children }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className="bg-white rounded-lg shadow-lg p-6"
    >
      <motion.h2
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="text-xl font-semibold mb-4"
      >
        {title}
      </motion.h2>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        {children}
      </motion.div>
    </motion.div>
  );
}

// 使用动画卡片
function CardList() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {[
        { title: '卡片 1', content: '内容 1' },
        { title: '卡片 2', content: '内容 2' },
        { title: '卡片 3', content: '内容 3' },
      ].map((card, index) => (
        <AnimatedCard
          key={card.title}
          title={card.title}
        >
          {card.content}
        </AnimatedCard>
      ))}
    </div>
  );
}
```

## 图标和字体

### 1. 图标库

```bash
# 安装 react-icons
npm install react-icons
```

```jsx
// 使用 react-icons
import { FaHome, FaUser, FaSettings, FaBell } from 'react-icons/fa';

function Sidebar() {
  return (
    <div className="w-64 bg-gray-800 text-white">
      <nav className="mt-10">
        <a href="#" className="flex items-center px-4 py-3 hover:bg-gray-700">
          <FaHome className="mr-3" />
          首页
        </a>
        <a href="#" className="flex items-center px-4 py-3 hover:bg-gray-700">
          <FaUser className="mr-3" />
          用户
        </a>
        <a href="#" className="flex items-center px-4 py-3 hover:bg-gray-700">
          <FaSettings className="mr-3" />
          设置
        </a>
        <a href="#" className="flex items-center px-4 py-3 hover:bg-gray-700">
          <FaBell className="mr-3" />
          通知
        </a>
      </nav>
    </div>
  );
}
```

### 2. 自定义字体

```jsx
// app/layout.tsx
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
});

export default function RootLayout({ children }) {
  return (
    <html lang="zh-CN" className={`${inter.variable} font-sans`}>
      <body>{children}</body>
    </html>
  );
}
```

```css
/* 使用自定义字体 */
.custom-heading {
  font-family: var(--font-inter);
  font-weight: 700;
}
```

## 实战示例

### 1. 完整的 UI 组件库

```jsx
// components/index.jsx
export { default as Button } from './Button';
export { default as Card } from './Card';
export { default as Input } from './Input';
export { default as Modal } from './Modal';
export { default as Navigation } from './Navigation';

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
  const baseStyles = 'font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    outline: 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-blue-500',
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

### 2. 完整的页面布局

```jsx
// components/Layout.jsx
import { useState } from 'react';
import { FaHome, FaUser, FaSettings, FaBell, FaBars, FaTimes } from 'react-icons/fa';
import Button from './Button';

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigation = [
    { name: '首页', href: '/', icon: FaHome },
    { name: '用户管理', href: '/users', icon: FaUser },
    { name: '系统设置', href: '/settings', icon: FaSettings },
    { name: '通知中心', href: '/notifications', icon: FaBell },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 移动端侧边栏遮罩 */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* 侧边栏 */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 text-white transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}>
        <div className="flex items-center justify-between h-16 px-4 bg-gray-800">
          <h1 className="text-xl font-bold">管理系统</h1>
          <Button
            variant="ghost"
            size="small"
            className="lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <FaTimes />
          </Button>
        </div>

        <nav className="mt-10">
          {navigation.map((item) => (
            <a
              key={item.name}
              href={item.href}
              className="flex items-center px-4 py-3 text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
            >
              <item.icon className="mr-3 h-5 w-5" />
              {item.name}
            </a>
          ))}
        </nav>
      </div>

      {/* 主内容区域 */}
      <div className="lg:pl-64">
        {/* 顶部导航 */}
        <header className="bg-white shadow-sm">
          <div className="flex items-center justify-between h-16 px-4">
            <Button
              variant="ghost"
              size="small"
              className="lg:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <FaBars />
            </Button>

            <div className="flex items-center space-x-4">
              {/* 通知 */}
              <Button variant="ghost" size="small">
                <FaBell className="h-5 w-5" />
              </Button>

              {/* 用户菜单 */}
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                  A
                </div>
                <span className="text-sm font-medium text-gray-700">管理员</span>
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

## 性能优化

### 1. 样式优化

```jsx
// 使用 CSS 变量进行主题化
:root {
  --primary-color: #3b82f6;
  --secondary-color: #6b7280;
  --background-color: #ffffff;
  --text-color: #111827;
}

[data-theme="dark"] {
  --primary-color: #60a5fa;
  --secondary-color: #9ca3af;
  --background-color: #111827;
  --text-color: #f9fafb;
}

// 使用 CSS 变量
.button {
  background-color: var(--primary-color);
  color: var(--text-color);
}

// 避免重复的样式定义
@layer components {
  .btn {
    @apply font-medium rounded-md transition-colors;
  }

  .btn-primary {
    @apply bg-blue-600 text-white hover:bg-blue-700;
  }

  .card {
    @apply bg-white rounded-lg shadow-md overflow-hidden;
  }
}
```

### 2. 懒加载样式

```jsx
// 动态导入样式组件
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(
  () => import('../components/HeavyComponent'),
  {
    loading: () => <div>加载中...</div>,
    ssr: false
  }
);

function Page() {
  return (
    <div>
      <h1>页面标题</h1>
      <HeavyComponent />
    </div>
  );
}
```

## 下一步

掌握样式解决方案后，你可以继续学习：

1. **框架集成** - 学习状态管理、表单处理等框架集成
2. **数据获取** - 掌握 Server Components 和 API 集成
3. **项目实战** - 构建完整的前端应用
4. **测试策略** - 学习组件测试和端到端测试

---

*样式是现代前端开发的重要组成部分，掌握多种样式解决方案将帮助你构建美观、可维护的 Web 应用。*