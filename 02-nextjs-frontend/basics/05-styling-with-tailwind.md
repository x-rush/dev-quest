# Next.js 15 + Tailwind CSS 4 企业级样式开发完整指南

> **文档简介**: Next.js 15 与 Tailwind CSS 4 深度集成教程，涵盖现代化样式系统、响应式设计、主题定制、组件样式、性能优化等企业级CSS开发技术

> **目标读者**: 具备基础CSS知识的开发者，需要掌握现代样式系统和UI设计的前端工程师

> **前置知识**: CSS基础、Next.js基础、JavaScript基础、响应式设计概念

> **预计时长**: 4-6小时

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `basics` |
| **难度** | ⭐⭐⭐ (3/5星) |
| **标签** | `#tailwindcss` `#styling` `#responsive-design` `#theme-system` `#css-in-js` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标

### 🎨 现代样式系统掌握
- 掌握Tailwind CSS 4的核心概念和语法
- 学会构建响应式设计和移动优先布局
- 理解主题系统和设计令牌的应用
- 掌握组件样式化和样式复用模式

### 🚀 企业级开发能力
- 构建可维护的样式架构和组件库
- 实施暗色模式和多主题支持
- 掌握样式性能优化和构建策略
- 学会设计系统和品牌一致性管理

## 📖 概述

Tailwind CSS 4是功能优先的CSS框架，通过原子化类名提供快速、可定制的样式开发体验。与Next.js 15的深度集成，让现代Web应用的样式开发变得高效且一致。

## 🏗️ Tailwind CSS 4 项目配置

### 自动集成配置

```bash
# 创建项目时自动集成Tailwind CSS
npx create-next-app@latest my-tailwind-app --typescript --tailwind --eslint --app

# 或者手动添加Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### tailwind.config.ts 完整配置

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  // 内容源配置
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],

  // 主题配置
  theme: {
    extend: {
      // 颜色系统
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
          950: '#172554',
        },
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
          950: '#030712',
        },
      },

      // 字体系统
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
        display: ['Cal Sans', 'ui-sans-serif', 'system-ui'],
      },

      // 字号系统
      fontSize: {
        xs: ['0.75rem', { lineHeight: '1rem' }],
        sm: ['0.875rem', { lineHeight: '1.25rem' }],
        base: ['1rem', { lineHeight: '1.5rem' }],
        lg: ['1.125rem', { lineHeight: '1.75rem' }],
        xl: ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
        '6xl': ['3.75rem', { lineHeight: '1' }],
      },

      // 间距系统
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },

      // 圆角系统
      borderRadius: {
        '4xl': '2rem',
      },

      // 阴影系统
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
        'medium': '0 4px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        'hard': '0 10px 40px -10px rgba(0, 0, 0, 0.2), 0 2px 10px -2px rgba(0, 0, 0, 0.04)',
      },

      // 动画系统
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'bounce-soft': 'bounceSoft 0.6s ease-in-out',
      },

      // 关键帧
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        bounceSoft: {
          '0%, 20%, 53%, 80%, 100%': { transform: 'translateY(0)' },
          '40%, 43%': { transform: 'translateY(-8px)' },
          '70%': { transform: 'translateY(-4px)' },
          '90%': { transform: 'translateY(-2px)' },
        },
      },

      // 断点系统
      screens: {
        '3xl': '1600px',
      },
    },
  },

  // 插件配置
  plugins: [
    // 表单插件
    require('@tailwindcss/forms')({
      strategy: 'class',
    }),

    // 排版插件
    require('@tailwindcss/typography'),

    // 容器查询插件
    require('@tailwindcss/container-queries'),

    // 自定义插件
    function({ addUtilities, theme }: any) {
      // 添加自定义工具类
      addUtilities({
        '.text-shadow': {
          textShadow: '0 2px 4px rgba(0,0,0,0.10)',
        },
        '.text-shadow-md': {
          textShadow: '0 4px 8px rgba(0,0,0,0.12), 0 2px 4px rgba(0,0,0,0.08)',
        },
        '.backface-hidden': {
          backfaceVisibility: 'hidden',
        },
        '.transform-gpu': {
          transform: 'translate3d(0, 0, 0)',
        },
      })

      // 添加渐变文字工具类
      addUtilities({
        '.text-gradient': {
          background: 'linear-gradient(to right, #3b82f6, #8b5cf6)',
          '-webkit-background-clip': 'text',
          '-webkit-text-fill-color': 'transparent',
          'background-clip': 'text',
        },
        '.text-gradient-rainbow': {
          background: 'linear-gradient(to right, #ef4444, #f59e0b, #10b981, #3b82f6, #8b5cf6)',
          '-webkit-background-clip': 'text',
          '-webkit-text-fill-color': 'transparent',
          'background-clip': 'text',
        },
      })
    },
  ],

  // 前缀配置
  prefix: '',

  // 重要标记配置
  important: false,

  // 分离器配置
  separator: ':',

  // 核心插件配置
  corePlugins: {
    preflight: true,
  },

  // 暗色模式配置
  darkMode: ['class'],
}

export default config
```

## 🎨 基础样式模式

### 文本样式系统

```tsx
// src/components/Typography.tsx
import { cn } from '@/lib/utils'
import { cva, type VariantProps } from 'class-variance-authority'

// 标题样式变体
const headingVariants = cva('font-semibold text-gray-900 dark:text-gray-100', {
  variants: {
    size: {
      h1: 'text-4xl md:text-5xl lg:text-6xl',
      h2: 'text-3xl md:text-4xl lg:text-5xl',
      h3: 'text-2xl md:text-3xl lg:text-4xl',
      h4: 'text-xl md:text-2xl lg:text-3xl',
      h5: 'text-lg md:text-xl lg:text-2xl',
      h6: 'text-base md:text-lg lg:text-xl',
    },
    weight: {
      light: 'font-light',
      normal: 'font-normal',
      medium: 'font-medium',
      semibold: 'font-semibold',
      bold: 'font-bold',
    },
    align: {
      left: 'text-left',
      center: 'text-center',
      right: 'text-right',
      justify: 'text-justify',
    },
  },
  defaultVariants: {
    size: 'h2',
    weight: 'semibold',
    align: 'left',
  },
})

// 正文样式变体
const textVariants = cva('text-gray-700 dark:text-gray-300', {
  variants: {
    size: {
      xs: 'text-xs',
      sm: 'text-sm',
      base: 'text-base',
      lg: 'text-lg',
      xl: 'text-xl',
      '2xl': 'text-2xl',
      '3xl': 'text-3xl',
    },
    weight: {
      light: 'font-light',
      normal: 'font-normal',
      medium: 'font-medium',
      semibold: 'font-semibold',
      bold: 'font-bold',
    },
    color: {
      default: 'text-gray-700 dark:text-gray-300',
      muted: 'text-gray-500 dark:text-gray-400',
      primary: 'text-primary-600 dark:text-primary-400',
      secondary: 'text-secondary-600 dark:text-secondary-400',
      accent: 'text-accent-600 dark:text-accent-400',
    },
  },
  defaultVariants: {
    size: 'base',
    weight: 'normal',
    color: 'default',
  },
})

interface HeadingProps extends VariantProps<typeof headingVariants> {
  children: React.ReactNode
  className?: string
}

export function Heading({ children, className, size, weight, align }: HeadingProps) {
  const Tag = size as keyof JSX.IntrinsicElements

  return (
    <Tag className={cn(headingVariants({ size, weight, align }), className)}>
      {children}
    </Tag>
  )
}

interface TextProps extends VariantProps<typeof textVariants> {
  children: React.ReactNode
  className?: string
  as?: keyof JSX.IntrinsicElements
}

export function Text({ children, className, size, weight, color, as: Tag = 'p' }: TextProps) {
  return (
    <Tag className={cn(textVariants({ size, weight, color }), className)}>
      {children}
    </Tag>
  )
}
```

### 按钮样式系统

```tsx
// src/components/Button.tsx
import { forwardRef } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

// 按钮样式变体
const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none',
  {
    variants: {
      variant: {
        primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500',
        secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 focus:ring-gray-500 dark:bg-gray-800 dark:text-gray-100 dark:hover:bg-gray-700',
        outline: 'border border-gray-300 bg-transparent text-gray-700 hover:bg-gray-50 focus:ring-primary-500 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800',
        ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500 dark:text-gray-300 dark:hover:bg-gray-800',
        danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
        success: 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500',
        warning: 'bg-yellow-500 text-white hover:bg-yellow-600 focus:ring-yellow-500',
      },
      size: {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 py-2 text-sm',
        lg: 'h-12 px-6 text-base',
        xl: 'h-14 px-8 text-lg',
      },
      fullWidth: {
        true: 'w-full',
        false: 'w-auto',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
      fullWidth: false,
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean
  icon?: React.ReactNode
  iconPosition?: 'left' | 'right'
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, fullWidth, loading, icon, iconPosition = 'left', children, disabled, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, fullWidth }), className)}
        ref={ref}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        )}

        {icon && iconPosition === 'left' && !loading && (
          <span className="mr-2">{icon}</span>
        )}

        {children}

        {icon && iconPosition === 'right' && (
          <span className="ml-2">{icon}</span>
        )}
      </button>
    )
  }
)

Button.displayName = 'Button'
```

### 卡片组件样式

```tsx
// src/components/Card.tsx
import { forwardRef } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

// 卡片样式变体
const cardVariants = cva('rounded-xl border bg-white shadow-soft dark:bg-gray-900 dark:border-gray-800', {
  variants: {
    variant: {
      default: 'border-gray-200 dark:border-gray-800',
      elevated: 'border-gray-100 shadow-medium dark:border-gray-700',
      outlined: 'border-2 border-gray-300 shadow-none dark:border-gray-600',
      ghost: 'border-transparent shadow-none bg-transparent',
    },
    padding: {
      none: 'p-0',
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8',
      xl: 'p-10',
    },
    hover: {
      true: 'transition-all duration-200 hover:shadow-medium hover:-translate-y-1',
      false: '',
    },
  },
  defaultVariants: {
    variant: 'default',
    padding: 'md',
    hover: false,
  },
})

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant, padding, hover, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(cardVariants({ variant, padding, hover }), className)}
      {...props}
    />
  )
)

Card.displayName = 'Card'

// 卡片头部
export const CardHeader = forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col space-y-1.5 p-6', className)}
    {...props}
  />
))

CardHeader.displayName = 'CardHeader'

// 卡片标题
export const CardTitle = forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn('text-2xl font-semibold leading-none tracking-tight', className)}
    {...props}
  />
))

CardTitle.displayName = 'CardTitle'

// 卡片描述
export const CardDescription = forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm text-gray-500 dark:text-gray-400', className)}
    {...props}
  />
))

CardDescription.displayName = 'CardDescription'

// 卡片内容
export const CardContent = forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />
))

CardContent.displayName = 'CardContent'

// 卡片底部
export const CardFooter = forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex items-center p-6 pt-0', className)}
    {...props}
  />
))

CardFooter.displayName = 'CardFooter'
```

## 📱 响应式设计系统

### 移动优先布局

```tsx
// src/components/ResponsiveGrid.tsx
import { cn } from '@/lib/utils'

interface ResponsiveGridProps {
  children: React.ReactNode
  className?: string
  cols?: {
    sm?: number
    md?: number
    lg?: number
    xl?: number
    '2xl'?: number
  }
  gap?: {
    sm?: number
    md?: number
    lg?: number
    xl?: number
  }
}

export function ResponsiveGrid({
  children,
  className,
  cols = { sm: 1, md: 2, lg: 3, xl: 4 },
  gap = { sm: 4, md: 6, lg: 8 }
}: ResponsiveGridProps) {
  const gridClasses = cn(
    'grid',
    cols.sm && `grid-cols-${cols.sm}`,
    cols.md && `md:grid-cols-${cols.md}`,
    cols.lg && `lg:grid-cols-${cols.lg}`,
    cols.xl && `xl:grid-cols-${cols.xl}`,
    gap.sm && `gap-${gap.sm}`,
    gap.md && `md:gap-${gap.md}`,
    gap.lg && `lg:gap-${gap.lg}`,
    gap.xl && `xl:gap-${gap.xl}`,
    className
  )

  return <div className={gridClasses}>{children}</div>
}

// 使用示例
export function ProductGrid() {
  return (
    <ResponsiveGrid
      cols={{ sm: 1, md: 2, lg: 3, xl: 4 }}
      gap={{ sm: 4, md: 6, lg: 8 }}
      className="py-8"
    >
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </ResponsiveGrid>
  )
}
```

### 响应式容器

```tsx
// src/components/Container.tsx
import { cn } from '@/lib/utils'

interface ContainerProps {
  children: React.ReactNode
  className?: string
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  centered?: boolean
}

export function Container({
  children,
  className,
  size = 'lg',
  centered = true
}: ContainerProps) {
  const sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-7xl',
    xl: 'max-w-screen-xl',
    full: 'max-w-full'
  }

  return (
    <div
      className={cn(
        'w-full px-4 sm:px-6 lg:px-8',
        sizeClasses[size],
        centered && 'mx-auto',
        className
      )}
    >
      {children}
    </div>
  )
}
```

### 响应式图片

```tsx
// src/components/ResponsiveImage.tsx
import Image from 'next/image'
import { useState } from 'react'

interface ResponsiveImageProps {
  src: string
  alt: string
  width: number
  height: number
  priority?: boolean
  className?: string
  sizes?: string
  quality?: number
  fill?: boolean
}

export function ResponsiveImage({
  src,
  alt,
  width,
  height,
  priority = false,
  className = '',
  sizes = '(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw',
  quality = 75,
  fill = false
}: ResponsiveImageProps) {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(false)

  if (error) {
    return (
      <div className={cn(
        'flex items-center justify-center bg-gray-200 dark:bg-gray-800 text-gray-500',
        fill ? 'absolute inset-0' : 'w-full h-full',
        className
      )}>
        <span className="text-sm">图片加载失败</span>
      </div>
    )
  }

  return (
    <div className={cn('relative overflow-hidden', className)}>
      <Image
        src={src}
        alt={alt}
        width={fill ? undefined : width}
        height={fill ? undefined : height}
        fill={fill}
        priority={priority}
        quality={quality}
        sizes={sizes}
        className={cn(
          'transition-opacity duration-300',
          isLoading ? 'opacity-0' : 'opacity-100',
          fill ? 'object-cover' : 'w-full h-auto'
        )}
        onLoadingComplete={() => setIsLoading(false)}
        onError={() => setError(true)}
      />

      {isLoading && (
        <div className="absolute inset-0 bg-gray-200 dark:bg-gray-800 animate-pulse" />
      )}
    </div>
  )
}
```

## 🌙 主题系统实现

### 暗色模式配置

```tsx
// src/components/ThemeProvider.tsx
'use client'

import { createContext, useContext, useEffect, useState } from 'react'

type Theme = 'light' | 'dark' | 'system'

interface ThemeContextType {
  theme: Theme
  setTheme: (theme: Theme) => void
  systemTheme: 'light' | 'dark'
  effectiveTheme: 'light' | 'dark'
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({
  children,
  defaultTheme = 'system',
  storageKey = 'ui-theme',
}: {
  children: React.ReactNode
  defaultTheme?: Theme
  storageKey?: string
}) {
  const [theme, setTheme] = useState<Theme>(defaultTheme)
  const [systemTheme, setSystemTheme] = useState<'light' | 'dark'>('light')

  // 获取系统主题
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    setSystemTheme(mediaQuery.matches ? 'dark' : 'light')

    const handleChange = (e: MediaQueryListEvent) => {
      setSystemTheme(e.matches ? 'dark' : 'light')
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  // 从localStorage读取主题设置
  useEffect(() => {
    const stored = localStorage.getItem(storageKey) as Theme
    if (stored) {
      setTheme(stored)
    }
  }, [storageKey])

  // 应用主题到HTML元素
  useEffect(() => {
    const root = window.document.documentElement
    root.classList.remove('light', 'dark')

    let effectiveTheme: 'light' | 'dark'
    if (theme === 'system') {
      effectiveTheme = systemTheme
    } else {
      effectiveTheme = theme
    }

    root.classList.add(effectiveTheme)
  }, [theme, systemTheme])

  const value = {
    theme,
    setTheme: (theme: Theme) => {
      localStorage.setItem(storageKey, theme)
      setTheme(theme)
    },
    systemTheme,
    effectiveTheme: theme === 'system' ? systemTheme : theme,
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}
```

### 主题切换组件

```tsx
// src/components/ThemeToggle.tsx
'use client'

import { Moon, Sun, Monitor } from 'lucide-react'
import { useTheme } from './ThemeProvider'
import { Button } from './Button'

export function ThemeToggle() {
  const { theme, setTheme, effectiveTheme } = useTheme()

  const themes = [
    { value: 'light' as const, label: '浅色', icon: Sun },
    { value: 'dark' as const, label: '深色', icon: Moon },
    { value: 'system' as const, label: '跟随系统', icon: Monitor },
  ]

  return (
    <div className="flex items-center space-x-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
      {themes.map(({ value, label, icon: Icon }) => (
        <Button
          key={value}
          variant={theme === value ? 'primary' : 'ghost'}
          size="sm"
          onClick={() => setTheme(value)}
          className="h-8 px-2"
          title={label}
        >
          <Icon className="h-4 w-4" />
        </Button>
      ))}
    </div>
  )
}
```

## 🎯 高级样式模式

### 渐变和图案

```tsx
// src/components/GradientBackground.tsx
import { cn } from '@/lib/utils'

interface GradientBackgroundProps {
  children: React.ReactNode
  className?: string
  variant?: 'linear' | 'radial' | 'conic'
  colors: string[]
  direction?: string
  animated?: boolean
}

export function GradientBackground({
  children,
  className,
  variant = 'linear',
  colors,
  direction = 'to right',
  animated = false
}: GradientBackgroundProps) {
  const gradientClass = cn(
    'absolute inset-0',
    variant === 'linear' && `bg-gradient-${direction}`,
    variant === 'radial' && 'bg-radial-gradient',
    variant === 'conic' && 'bg-conic-gradient',
    animated && 'animate-gradient',
    className
  )

  const gradientStyle = {
    ...(variant === 'linear' && {
      backgroundImage: `linear-gradient(${direction}, ${colors.join(', ')})`
    }),
    ...(variant === 'radial' && {
      backgroundImage: `radial-gradient(circle, ${colors.join(', ')})`
    }),
    ...(variant === 'conic' && {
      backgroundImage: `conic-gradient(from 0deg, ${colors.join(', ')})`
    }),
  }

  return (
    <div className="relative overflow-hidden">
      <div
        className={gradientClass}
        style={gradientStyle}
      />
      <div className="relative z-10">
        {children}
      </div>
    </div>
  )
}

// 使用示例
export function HeroSection() {
  return (
    <GradientBackground
      colors={['#3b82f6', '#8b5cf6', '#ec4899']}
      direction="to bottom right"
      animated
    >
      <div className="py-20 text-center text-white">
        <h1 className="text-5xl font-bold mb-6">欢迎来到未来</h1>
        <p className="text-xl opacity-90">体验现代化的Web开发</p>
      </div>
    </GradientBackground>
  )
}
```

### 玻璃态效果

```tsx
// src/components/GlassEffect.tsx
import { cn } from '@/lib/utils'

interface GlassEffectProps {
  children: React.ReactNode
  className?: string
  blur?: 'sm' | 'md' | 'lg' | 'xl'
  opacity?: 'low' | 'medium' | 'high'
  border?: boolean
}

export function GlassEffect({
  children,
  className,
  blur = 'md',
  opacity = 'medium',
  border = true
}: GlassEffectProps) {
  const blurClasses = {
    sm: 'backdrop-blur-sm',
    md: 'backdrop-blur-md',
    lg: 'backdrop-blur-lg',
    xl: 'backdrop-blur-xl'
  }

  const opacityClasses = {
    low: 'bg-white/10 dark:bg-black/10',
    medium: 'bg-white/20 dark:bg-black/20',
    high: 'bg-white/30 dark:bg-black/30'
  }

  return (
    <div
      className={cn(
        'relative',
        blurClasses[blur],
        opacityClasses[opacity],
        border && 'border border-white/20 dark:border-white/10',
        'rounded-xl',
        className
      )}
    >
      {children}
    </div>
  )
}
```

## ⚡ 性能优化策略

### 样式分离和关键CSS

```tsx
// src/components/CriticalStyles.tsx
import Head from 'next/head'

export function CriticalStyles() {
  const criticalCSS = `
    /* 关键路径样式 */
    body {
      margin: 0;
      padding: 0;
      font-family: 'Inter', system-ui, sans-serif;
      line-height: 1.6;
    }

    .loading-skeleton {
      background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
      background-size: 200% 100%;
      animation: loading 1.5s infinite;
    }

    @keyframes loading {
      0% { background-position: 200% 0; }
      100% { background-position: -200% 0; }
    }

    /* 隐藏未加载的图片 */
    img:not([src]) {
      visibility: hidden;
    }
  `

  return (
    <Head>
      <style dangerouslySetInnerHTML={{ __html: criticalCSS }} />
    </Head>
  )
}
```

### PurgeCSS配置优化

```typescript
// tailwind.config.ts (生产环境优化)
const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],

  // 生产环境优化
  ...(process.env.NODE_ENV === 'production' && {
    purge: {
      enabled: true,
      content: [
        './src/**/*.{js,ts,jsx,tsx}',
        './src/pages/**/*.{html}',
      ],
      options: {
        safelist: [
          // 动态生成的类名
          /^bg-/,
          /^text-/,
          /^border-/,
          /^hover:/,
          /^focus:/,
          /^dark:/,
        ],
      },
    },
  }),
}
```

## ✅ 总结

通过本教程，你已经掌握了：

1. **配置系统**: Tailwind CSS 4的完整配置和定制
2. **组件样式**: 可复用的样式组件和变体系统
3. **响应式设计**: 移动优先的响应式布局策略
4. **主题系统**: 暗色模式和多主题支持
5. **高级效果**: 渐变、玻璃态等现代视觉效果
6. **性能优化**: 样式分离和构建优化策略

## 📚 下一步学习

- 深入学习设计系统和设计令牌
- 掌握CSS-in-JS和Tailwind的混合使用
- 学习动画和交互效果的最佳实践
- 探索无障碍设计和可访问性
- 了解样式系统的测试和维护

Tailwind CSS为Next.js应用提供了强大而灵活的样式解决方案。继续探索更多高级特性，构建更优秀的用户界面吧！

## 🔄 文档交叉引用

### 相关文档
- 📄 **[前一个basics文档](./04-layouts-routing.md)**: 学习布局和路由系统，为样式化页面结构做好准备
- 📄 **[后一个basics文档](./06-data-fetching-basics.md)**: 学习数据获取，为动态内容添加样式
- 📄 **[相关的knowledge-points文档](../knowledge-points/language-concepts/05-css-patterns.md)**: 深入了解CSS模式和最佳实践
- 📄 **[相关的knowledge-points文档](../knowledge-points/development-tools/02-styling-tools.md)**: 快速参考样式工具和插件配置

### 参考章节
- 📖 **[本模块其他章节]**: [布局路由设计](./04-layouts-routing.md#响应式布局) | [数据获取基础](./06-data-fetching-basics.md#客户端数据获取)
- 📖 **[Knowledge Points快速参考]**: [CSS模式参考](../knowledge-points/language-concepts/05-css-patterns.md) | [样式工具配置](../knowledge-points/development-tools/02-styling-tools.md)

## 📝 总结

### 核心要点回顾
1. **Tailwind配置**: 掌握tailwind.config.ts的完整配置，理解主题系统的定制方法
2. **组件样式化**: 学会创建可复用的样式组件，掌握变体系统的使用
3. **响应式设计**: 理解移动优先的设计原则，掌握响应式布局的实现
4. **主题系统**: 学会实现暗色模式和多主题支持，提升用户体验
5. **性能优化**: 掌握样式分离和构建优化策略，提升应用性能

### 学习成果检查
- [ ] 是否能够配置完整的Tailwind CSS开发环境？
- [ ] 是否掌握基础组件的样式化方法和变体系统？
- [ ] 是否理解响应式设计的实现原则和技巧？
- [ ] 是否能够实现主题切换和暗色模式功能？
- [ ] 是否掌握样式性能优化的基本策略？

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

---

**文档状态**: ✅ 已完成
**最后更新**: 2025年10月
**版本**: v1.0.0