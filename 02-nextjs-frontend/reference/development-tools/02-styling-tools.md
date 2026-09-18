# Next.js 16 现代样式工具完整指南

> **文档简介**: Next.js 16 现代样式工具速查指南，涵盖Tailwind CSS 4、CSS-in-JS、CSS Modules、Linaria、Styled Components等现代样式解决方案

> **目标读者**: 具备基础CSS知识的前端开发者，需要掌握Next.js 16现代样式工具链的UI/UX工程师

> **前置知识**: Next.js 16基础、TypeScript 7、CSS3、响应式设计基础、JavaScript ES6+

> **预计时长**: 6-8小时

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `reference` |
| **难度** | ⭐⭐⭐ (精通)|
| **标签** | `#styling` `#tailwindcss` `#css-in-js` `#styled-components` `#linaria` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 📚 概述

Next.js 16 提供了丰富的样式解决方案，从传统的CSS Modules到现代的CSS-in-JS，从原子化CSS到组件级样式系统。本指南深入探讨企业级样式架构，涵盖性能优化、主题系统、响应式设计和可维护性最佳实践。

## 🎨 Tailwind CSS 4 企业级配置

### 基础配置

先安装构建依赖：npm install -D tailwindcss @tailwindcss/postcss postcss。以下文件分别保存，根布局导入 globals.css。

```js
// postcss.config.mjs
export default { plugins: { '@tailwindcss/postcss': {} } };
```

```css
/* src/app/globals.css：Tailwind 4 使用 CSS 优先配置 */
@import "tailwindcss";
@custom-variant dark (&:where(.dark, .dark *));
@theme {
  --color-brand-500: #3b82f6;
  --color-brand-600: #2563eb;
  --color-brand-700: #1d4ed8;
  --font-sans: Inter, ui-sans-serif, system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;
  --spacing-18: 4.5rem;
  --shadow-soft: 0 2px 15px rgb(0 0 0 / 0.07);
  --breakpoint-xs: 30rem;
  --breakpoint-3xl: 100rem;
  --color-primary: var(--app-primary);
  --color-primary-foreground: white;
  --color-background: var(--app-background);
  --color-foreground: var(--app-foreground);
  --color-border: #d4d4d4;
  --color-input: #d4d4d4;
  --color-ring: #2563eb;
  --color-secondary: #f5f5f5;
  --color-secondary-foreground: #171717;
  --color-accent: #eff6ff;
  --color-accent-foreground: #171717;
  --color-destructive: #dc2626;
  --color-destructive-foreground: white;
}
:root { --app-primary: #2563eb; --app-background: white; --app-foreground: #171717; }
.dark { --app-primary: #60a5fa; --app-background: #171717; --app-foreground: #fafafa; }
@layer components {
  .card { @apply rounded-lg border border-border bg-background p-6 shadow-soft; }
}
```

字体族声明不会下载字体，需用 next/font 或已有字体文件。旧 JavaScript 配置在 v4 不会自动检测，迁移时可用 @config 显式加载受支持部分；corePlugins、separator 等旧选项不能直接沿用。容器查询已内建，按实际需要添加 forms/typography 插件，避免堆叠未使用依赖。
### 自定义组件库

```tsx
// components/ui/button.tsx
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import * as React from 'react';

// 使用 class-variance-authority 管理变体
const buttonVariants = cva(
  // 基础样式
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-md px-3',
        lg: 'h-11 rounded-md px-8',
        icon: 'h-10 w-10',
      },
      fullWidth: {
        true: 'w-full',
        false: '',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
      fullWidth: false,
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, fullWidth, asChild = false, loading, children, disabled, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button';

    return (
      <Comp
        className={buttonVariants({ variant, size, fullWidth, className })}
        ref={ref}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <svg
            className="mr-2 h-4 w-4 animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
        )}
        {children}
      </Comp>
    );
  }
);

Button.displayName = 'Button';

export { Button, buttonVariants };

// components/ui/card.tsx
import * as React from 'react';

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={`rounded-lg border bg-card text-card-foreground shadow-sm ${className}`}
    {...props}
  />
));
Card.displayName = 'Card';

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={`flex flex-col space-y-1.5 p-6 ${className}`}
    {...props}
  />
));
CardHeader.displayName = 'CardHeader';

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={`text-2xl font-semibold leading-none tracking-tight ${className}`}
    {...props}
  />
));
CardTitle.displayName = 'CardTitle';

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={`text-sm text-muted-foreground ${className}`}
    {...props}
  />
));
CardDescription.displayName = 'CardDescription';

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={`p-6 pt-0 ${className}`} {...props} />
));
CardContent.displayName = 'CardContent';

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={`flex items-center p-6 pt-0 ${className}`}
    {...props}
  />
));
CardFooter.displayName = 'CardFooter';

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent };
```

## 🎭 CSS-in-JS 解决方案

### Emotion 配置

```typescript
// src/styles/emotion.ts
import { createEmotion } from '@emotion/css/create-instance';

export const { css, injectGlobal, keyframes } = createEmotion({
  key: 'next-app',
  prefix: 'emotion-',
  stylisPlugins: [],
  // 生产环境优化
  speedy: process.env.NODE_ENV === 'production',
  // 主题配置
  theme: {
    colors: {
      primary: '#3b82f6',
      secondary: '#64748b',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
    },
    spacing: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem',
    },
    borderRadius: {
      sm: '0.125rem',
      md: '0.375rem',
      lg: '0.5rem',
      xl: '0.75rem',
    },
    shadows: {
      sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
      md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
      lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    },
  },
});

// src/styles/theme.ts
import { css } from './emotion';

export const lightTheme = css`
  --color-background: #ffffff;
  --color-foreground: #171717;
  --color-muted: #f5f5f5;
  --color-muted-foreground: #737373;
  --color-border: #e5e5e5;
  --color-input: #ffffff;
  --color-ring: #3b82f6;

  --color-primary: #3b82f6;
  --color-primary-foreground: #ffffff;

  --color-secondary: #f1f5f9;
  --color-secondary-foreground: #0f172a;

  --color-destructive: #ef4444;
  --color-destructive-foreground: #ffffff;

  --radius: 0.5rem;
`;

export const darkTheme = css`
  --color-background: #0a0a0a;
  --color-foreground: #ededed;
  --color-muted: #262626;
  --color-muted-foreground: #a3a3a3;
  --color-border: #404040;
  --color-input: #262626;
  --color-ring: #93c5fd;

  --color-primary: #3b82f6;
  --color-primary-foreground: #ffffff;

  --color-secondary: #1e293b;
  --color-secondary-foreground: #f8fafc;

  --color-destructive: #ef4444;
  --color-destructive-foreground: #ffffff;

  --radius: 0.5rem;
`;
```

// src/styles/globals.css
```css
/* 普通 CSS 不能 import TS 对象或使用模板插值，以下使用真实 CSS 变量 */
:root {
  --color-background: #ffffff;
  --color-foreground: #171717;
  --color-primary: #2563eb;
}
[data-theme="dark"] {
  --color-background: #0a0a0a;
  --color-foreground: #ededed;
  --color-primary: #60a5fa;
}

/* 全局重置 */
* {
  box-sizing: border-box;
  padding: 0;
  margin: 0;
}

html,
body {
  max-width: 100vw;
  overflow-x: hidden;
  font-family: 'Inter', system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  color: hsl(var(--foreground));
  background: linear-gradient(
      to bottom,
      transparent,
      hsl(var(--background))
    )
    hsl(var(--background));
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: hsl(var(--border));
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: hsl(var(--muted-foreground));
}

/* 选择文本样式 */
::selection {
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
}

/* 焦点样式 */
:focus-visible {
  outline: 2px solid hsl(var(--ring));
  outline-offset: 2px;
}

/* 减少动画 */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Emotion 组件示例

```tsx
// src/components/Button/Button.tsx
import { css } from '@/styles/emotion';
import styled from '@emotion/styled';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
}

const StyledButton = styled.button<ButtonProps>`
  /* 基础样式 */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border-radius: var(--radius);
  font-weight: 500;
  transition: all 0.2s ease-in-out;
  cursor: pointer;
  outline: none;
  border: 2px solid transparent;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &:focus-visible {
    outline: 2px solid hsl(var(--ring));
    outline-offset: 2px;
  }

  /* 变体样式 */
  ${({ variant = 'primary' }) => {
    switch (variant) {
      case 'primary':
        return css`
          background-color: hsl(var(--primary));
          color: hsl(var(--primary-foreground));

          &:hover:not(:disabled) {
            background-color: hsl(217.2 91.2% 59.8%);
          }

          &:active:not(:disabled) {
            background-color: hsl(217.2 91.2% 54.1%);
          }
        `;

      case 'secondary':
        return css`
          background-color: hsl(var(--secondary));
          color: hsl(var(--secondary-foreground));

          &:hover:not(:disabled) {
            background-color: hsl(215.4 16.3% 46.9%);
          }
        `;

      case 'outline':
        return css`
          background-color: transparent;
          color: hsl(var(--foreground));
          border-color: hsl(var(--border));

          &:hover:not(:disabled) {
            background-color: hsl(var(--accent));
          }
        `;

      default:
        return '';
    }
  }}

  /* 尺寸样式 */
  ${({ size = 'md' }) => {
    switch (size) {
      case 'sm':
        return css`
          height: 2.25rem;
          padding: 0 1rem;
          font-size: 0.875rem;
        `;

      case 'md':
        return css`
          height: 2.5rem;
          padding: 0 1.5rem;
          font-size: 0.875rem;
        `;

      case 'lg':
        return css`
          height: 2.75rem;
          padding: 0 2rem;
          font-size: 1rem;
        `;

      default:
        return '';
    }
  }}

  /* 全宽样式 */
  ${({ fullWidth = false }) =>
    fullWidth &&
    css`
      width: 100%;
    `}

  /* 自定义类名 */
  ${({ className }) => className}
`;

// 加载动画组件
const LoadingSpinner = styled.div`
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
`;

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  children,
  onClick,
  disabled = false,
  className,
  ...props
}) => {
  return (
    <StyledButton
      variant={variant}
      size={size}
      fullWidth={fullWidth}
      onClick={onClick}
      disabled={disabled}
      className={className}
      {...props}
    >
      {children}
    </StyledButton>
  );
};

// src/components/Button/Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
};

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    children: 'Button',
  },
};

export const Secondary: Story = {
  args: {
    variant: 'secondary',
    children: 'Secondary',
  },
};

export const Outline: Story = {
  args: {
    variant: 'outline',
    children: 'Outline',
  },
};

export const Sizes: Story = {
  render: () => (
    <div className="flex gap-4">
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
    </div>
  ),
};

export const FullWidth: Story = {
  args: {
    fullWidth: true,
    children: 'Full Width Button',
  },
};

export const Disabled: Story = {
  args: {
    disabled: true,
    children: 'Disabled',
  },
};

export const WithIcon: Story = {
  args: {
    children: (
      <>
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5ZM19 16v2" />
          <path d="M19 22h.01" />
        </svg>
        Like
      </>
    ),
  },
};
```

## 🎭 Linaria 零运行时 CSS-in-JS

### Linaria 配置

```json
// .linariarc.json
{
  "babel": {
    "presets": ["@linaria/babel-preset"],
    "plugins": ["@linaria/babel-plugin"]
  },
  "theme": "./src/styles/theme.js",
  "rules": [
    {
      "action": {
        "name": "dynamic-classname",
        "options": {
          "moduleName": "react-linaria/dynamic"
        }
      }
    }
  ],
  "output": {
    "css": "./dist/styles",
    "cssModules": "./dist/components",
    "cssFilename": "[name].css",
    "cssModulesFilename": "[name].module.css"
  }
}
```

```javascript
// linaria.config.js
module.exports = {
  preset: '@linaria/react',
  theme: {
    colors: {
      primary: '#3b82f6',
      secondary: '#64748b',
    },
  },
  rules: [
    {
      action: 'dynamic-classname',
      options: {
        moduleName: 'react-linaria/dynamic',
      },
    },
  ],
};
```

### Linaria 组件示例

```tsx
// src/components/Card/Card.tsx
import { styled } from '@linaria/react';
import { css } from '@linaria/core';

// 动态样式
const getCardStyles = css`
  border-radius: 8px;
  border: 1px solid #e5e5e5;
  background: white;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease-in-out;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  }
`;

const cardTitleStyles = css`
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #171717;
`;

const cardDescriptionStyles = css`
  color: #737373;
  line-height: 1.5;
`;

// 样式化组件
const StyledCard = styled.div`
  ${getCardStyles};
`;

const CardTitle = styled.h2`
  ${cardTitleStyles};
`;

const CardDescription = styled.p`
  ${cardDescriptionStyles};
`;

interface CardProps {
  title: string;
  description: string;
  className?: string;
}

export const Card: React.FC<CardProps> = ({ title, description, className }) => {
  return (
    <StyledCard className={className}>
      <CardTitle>{title}</CardTitle>
      <CardDescription>{description}</CardDescription>
    </StyledCard>
  );
};

// 带有动态属性的组件
// 注意：基于 props 的动态插值只能写在 styled`` 模板中（编译为 CSS 变量），
// @linaria/core 的 css`` 仅支持构建期静态提取，不支持 props 函数插值
const DynamicText = styled.span`
  color: ${props => props.color || '#171717'};
  font-size: ${props => props.size === 'large' ? '1.5rem' : '1rem'};
  font-weight: ${props => props.bold ? '600' : '400'};
`;

interface DynamicTextProps {
  color?: string;
  size?: 'normal' | 'large';
  bold?: boolean;
  children: React.ReactNode;
}

export const DynamicTextComponent: React.FC<DynamicTextProps> = ({
  color,
  size = 'normal',
  bold = false,
  children
}) => {
  return (
    <DynamicText color={color} size={size} bold={bold}>
      {children}
    </DynamicText>
  );
};
```

## 🎨 CSS Modules 最佳实践

### CSS Modules 配置

```typescript
// next.config.ts
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // 启用 CSS Modules
    cssChunking: 'strict',
  },
  webpack: (config, { isServer }) => {
    // 自定义 CSS Modules 配置
    config.module.rules.forEach((rule) => {
      if (rule.test && rule.test.toString().includes('.module.css')) {
        rule.use?.forEach((use) => {
          if (use.loader && use.loader.includes('css-loader')) {
            use.options.modules = {
              ...use.options.modules,
              // 自定义类名格式
              getLocalIdent: (context, localIdentName, localName, options) => {
                // 自定义命名规则
                const hash = createHash('md5')
                  .update(context.resourcePath)
                  .digest('hex')
                  .substring(0, 8);

                return `${localIdentName}_${hash}`;
              },
            };
          }
        });
      }
    });

    return config;
  },
};

export default nextConfig;
```

### CSS Modules 组件

```css
/* src/components/Button/Button.module.css */
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border-radius: var(--radius);
  font-weight: 500;
  transition: all 0.2s ease-in-out;
  cursor: pointer;
  outline: none;
  border: 2px solid transparent;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.button:focus-visible {
  outline: 2px solid hsl(var(--ring));
  outline-offset: 2px;
}

/* 变体 */
.primary {
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
}

.primary:hover:not(:disabled) {
  background-color: hsl(217.2 91.2% 59.8%);
}

.primary:active:not(:disabled) {
  background-color: hsl(217.2 91.2% 54.1%);
}

.secondary {
  background-color: hsl(var(--secondary));
  color: hsl(var(--secondary-foreground));
}

.secondary:hover:not(:disabled) {
  background-color: hsl(215.4 16.3% 46.9%);
}

.outline {
  background-color: transparent;
  color: hsl(var(--foreground));
  border-color: hsl(var(--border));
}

.outline:hover:not(:disabled) {
  background-color: hsl(var(--accent));
}

/* 尺寸 */
.sm {
  height: 2.25rem;
  padding: 0 1rem;
  font-size: 0.875rem;
}

.md {
  height: 2.5rem;
  padding: 0 1.5rem;
  font-size: 0.875rem;
}

.lg {
  height: 2.75rem;
  padding: 0 2rem;
  font-size: 1rem;
}

/* 全宽 */
.fullWidth {
  width: 100%;
}

/* 加载动画 */
.loading {
  position: relative;
}

.loading::after {
  content: '';
  position: absolute;
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  top: 50%;
  left: 50%;
  margin-left: -0.5rem;
  margin-top: -0.5rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 响应式 */
@media (max-width: 640px) {
  .button {
    width: 100%;
  }
}
```

```tsx
// src/components/Button/Button.tsx
import React from 'react';
import styles from './Button.module.css';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  loading?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  loading = false,
  children,
  onClick,
  disabled = false,
  className = ''
}) => {
  const classNames = [
    styles.button,
    styles[variant],
    styles[size],
    fullWidth && styles.fullWidth,
    loading && styles.loading,
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      className={classNames}
      onClick={onClick}
      disabled={disabled || loading}
      type="button"
    >
      {children}
    </button>
  );
};
```

## 🎨 响应式设计系统

### 断点系统

```typescript
// src/styles/breakpoints.ts
export const breakpoints = {
  xs: '475px',
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

export type Breakpoint = keyof typeof breakpoints;

export const mediaQueries = {
  xs: `@media (min-width: ${breakpoints.xs})`,
  sm: `@media (min-width: ${breakpoints.sm})`,
  md: `@media (min-width: ${breakpoints.md})`,
  lg: `@media (min-width: ${breakpoints.lg})`,
  xl: `@media (min-width: ${breakpoints.xl})`,
  '2xl': `@media (min-width: ${breakpoints['2xl']})`,

  // 最大宽度查询
  'max-xs': `@media (max-width: ${breakpoints.xs})`,
  'max-sm': `@media (max-width: ${breakpoints.sm})`,
  'max-md': `@media (max-width: ${breakpoints.md})`,
  'max-lg': `@media (max-width: ${breakpoints.lg})`,
  'max-xl': `@media (max-width: ${breakpoints.xl})`,

  // 范围查询
  'sm-only': `@media (min-width: ${breakpoints.sm}) and (max-width: ${breakpoints.md})`,
  'md-only': `@media (min-width: ${breakpoints.md}) and (max-width: ${breakpoints.lg})`,
  'lg-only': `@media (min-width: ${breakpoints.lg}) and (max-width: ${breakpoints.xl})`,
} as const;

// 响应式Hook
export const useBreakpoint = (breakpoint: Breakpoint) => {
  const [matches, setMatches] = React.useState(false);

  React.useEffect(() => {
    const media = window.matchMedia(`(min-width: ${breakpoints[breakpoint]})`);
    setMatches(media.matches);

    const handler = (event: MediaQueryListEvent) => {
      setMatches(event.matches);
    };

    media.addEventListener('change', handler);
    return () => media.removeEventListener('change', handler);
  }, [breakpoint]);

  return matches;
};
```

### 响应式组件示例

```tsx
// src/components/Grid/Grid.tsx
import React from 'react';
import styled from '@emotion/styled';
import { mediaQueries } from '@/styles/breakpoints';

interface GridProps {
  columns?: number | ResponsiveColumns;
  gap?: string | ResponsiveGap;
  children: React.ReactNode;
  className?: string;
}

interface ResponsiveColumns {
  xs?: number;
  sm?: number;
  md?: number;
  lg?: number;
  xl?: number;
  '2xl'?: number;
}

interface ResponsiveGap {
  xs?: string;
  sm?: string;
  md?: string;
  lg?: string;
  xl?: string;
  '2xl'?: string;
}

const StyledGrid = styled.div<GridProps>`
  display: grid;

  /* 列数配置 */
  ${({ columns = 1 }) => {
    if (typeof columns === 'number') {
      return `grid-template-columns: repeat(${columns}, 1fr);`;
    }

    let cssString = '';

    if (columns.xs) {
      cssString += `grid-template-columns: repeat(${columns.xs}, 1fr);`;
    }

    if (columns.sm) {
      cssString += `${mediaQueries.sm} { grid-template-columns: repeat(${columns.sm}, 1fr); }`;
    }

    if (columns.md) {
      cssString += `${mediaQueries.md} { grid-template-columns: repeat(${columns.md}, 1fr); }`;
    }

    if (columns.lg) {
      cssString += `${mediaQueries.lg} { grid-template-columns: repeat(${columns.lg}, 1fr); }`;
    }

    if (columns.xl) {
      cssString += `${mediaQueries.xl} { grid-template-columns: repeat(${columns.xl}, 1fr); }`;
    }

    if (columns['2xl']) {
      cssString += `${mediaQueries['2xl']} { grid-template-columns: repeat(${columns['2xl']}, 1fr); }`;
    }

    return cssString;
  }}

  /* 间距配置 */
  ${({ gap = '1rem' }) => {
    if (typeof gap === 'string') {
      return `gap: ${gap};`;
    }

    let cssString = '';

    if (gap.xs) {
      cssString += `gap: ${gap.xs};`;
    }

    if (gap.sm) {
      cssString += `${mediaQueries.sm} { gap: ${gap.sm}; }`;
    }

    if (gap.md) {
      cssString += `${mediaQueries.md} { gap: ${gap.md}; }`;
    }

    if (gap.lg) {
      cssString += `${mediaQueries.lg} { gap: ${gap.lg}; }`;
    }

    if (gap.xl) {
      cssString += `${mediaQueries.xl} { gap: ${gap.xl}; }`;
    }

    if (gap['2xl']) {
      cssString += `${mediaQueries['2xl']} { gap: ${gap['2xl']}; }`;
    }

    return cssString;
  }}

  /* 自定义类名 */
  ${({ className }) => className}
`;

export const Grid: React.FC<GridProps> = ({
  columns = 1,
  gap = '1rem',
  children,
  className,
  ...props
}) => {
  return (
    <StyledGrid
      columns={columns}
      gap={gap}
      className={className}
      {...props}
    >
      {children}
    </StyledGrid>
  );
};

// 使用示例
export const GridExample: React.FC = () => {
  return (
    <div>
      <h2>响应式网格布局</h2>

      <Grid
        columns={{
          xs: 1,
          sm: 2,
          md: 3,
          lg: 4,
          xl: 6
        }}
        gap={{
          xs: '0.5rem',
          md: '1rem',
          lg: '1.5rem'
        }}
      >
        {Array.from({ length: 12 }, (_, i) => (
          <div
            key={i}
            style={{
              padding: '1rem',
              background: '#f3f4f6',
              borderRadius: '0.5rem',
              textAlign: 'center'
            }}
          >
            项目 {i + 1}
          </div>
        ))}
      </Grid>
    </div>
  );
};
```

## 🎨 主题系统

### 主题提供者

```tsx
// src/styles/ThemeProvider.tsx
import React, { createContext, useContext, useEffect, useState } from 'react';
import { lightTheme, darkTheme } from './theme';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: Theme;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
  defaultTheme = 'light'
}) => {
  const [theme, setThemeState] = useState<Theme>(() => {
    // 从localStorage获取主题
    if (typeof window !== 'undefined') {
      const savedTheme = localStorage.getItem('theme') as Theme;
      return savedTheme || defaultTheme;
    }
    return defaultTheme;
  });

  useEffect(() => {
    // 更新DOM属性
    document.documentElement.setAttribute('data-theme', theme);

    // 保存到localStorage
    localStorage.setItem('theme', theme);

    // 更新meta标签
    const metaTheme = document.querySelector('meta[name="theme-color"]');
    if (metaTheme) {
      metaTheme.setAttribute('content', theme === 'dark' ? '#0a0a0a' : '#ffffff');
    }
  }, [theme]);

  const toggleTheme = () => {
    setThemeState(prev => prev === 'light' ? 'dark' : 'light');
  };

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// 主题切换组件
export const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      style={{
        padding: '0.5rem',
        borderRadius: '0.25rem',
        border: '1px solid hsl(var(--border))',
        background: 'hsl(var(--background))',
        color: 'hsl(var(--foreground))',
        cursor: 'pointer'
      }}
    >
      {theme === 'light' ? '🌙' : '☀️'}
    </button>
  );
};
```

## 🔄 文档交叉引用

### 相关文档
- 📄 **[测试工具](./01-testing-tools.md)**: 样式组件测试和视觉回归测试
- 📄 **[包管理器](./03-package-managers.md)**: 样式库依赖管理和版本控制
- 📄 **[调试工具](./04-debugging-tools.md)**: 样式调试和性能分析
- 📄 **[渲染优化](../performance-optimization/01-rendering-optimization.md)**: 样式优化和渲染性能
- 📄 **[打包优化](../performance-optimization/02-bundle-optimization.md)**: CSS优化和打包策略

### 参考章节
- 📖 **[Tailwind CSS配置](#-tailwind-css-4-企业级配置)**: 原子化CSS框架配置
- 📖 **[Emotion配置](#-css-in-js-解决方案)**: CSS-in-JS解决方案
- 📖 **[Linaria配置](#-linaria-零运行时-css-in-js)**: 零运行时CSS-in-JS
- 📖 **[CSS Modules](#-css-modules-最佳实践)**: 模块化CSS解决方案
- 📖 **[响应式设计](#-响应式设计系统)**: 响应式布局和媒体查询

---

## 📝 总结

### 核心要点回顾
1. **Tailwind CSS优势**: 原子化设计理念、高度可定制性、优秀的开发体验
2. **CSS-in-JS价值**: 组件级样式封装、动态样式支持、主题系统集成
3. **响应式设计**: 移动优先策略、弹性网格布局、媒体查询管理
4. **主题系统**: 设计令牌管理、深色模式支持、动态主题切换
5. **性能优化**: CSS提取、压缩优化、关键CSS内联

### 学习成果检查
- [ ] 能够配置和使用Tailwind CSS进行原子化样式开发
- [ ] 掌握Emotion等CSS-in-JS方案的配置和最佳实践
- [ ] 熟练实现响应式设计和移动优先的布局方案
- [ ] 能够构建完整的主题系统和设计令牌管理
- [ ] 理解样式性能优化和打包策略

---

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

## 🔗 外部资源

### 官方文档
- **Tailwind CSS**: [官方文档](https://tailwindcss.com/) - 原子化CSS框架
- **Emotion**: [官方文档](https://emotion.sh/docs/introduction) - CSS-in-JS库
- **Linaria**: [官方文档](https://linaria.org/) - 零运行时CSS-in-JS
- **CSS Modules**: [规范文档](https://github.com/css-modules/css-modules) - CSS模块化规范

### 快速参考
- **Styled Components**: [官方文档](https://styled-components.com/) - 流行的CSS-in-JS库
- **PostCSS**: [官方文档](https://postcss.org/) - CSS转换工具
- **设计令牌**: [Design Tokens W3C](https://www.w3.org/TR/design-tokens/) - 设计系统标准
- **响应式设计**: [响应式设计指南](https://web.dev/responsive-web-design-basics/) - 基础概念和最佳实践

---

**文档状态**: ✅ 已完成 | 🚧 进行中 | 📋 计划中
**最后更新**: 2026年9月
**版本**: v1.0.0

<!-- full-library-explanation -->
## 让样式工具的输出能被检查

前置是 CSS 层叠、构建插件和客户端边界。先让一条 bg-brand-600 在实际页面生效，检查生成 CSS 和计算样式，再扩展设计变量、组件变体与暗色主题。把几十个配置项粘贴进项目却没有消费它们，会增加排错成本，也不能证明组件体系完整。

本页 Tailwind、Emotion、Linaria 是可选方案，各自有独立的构建和 SSR 接入要求，不能把多个代码块拼进同一个配置文件。Emotion 的模板插值属于 JavaScript，不可写进普通 .css；CSS 中运行时可变值用 var(--token)，或把整段放到 Emotion Global 组件中。Linaria 抽取静态 CSS 也仍需正确配置构建插件。

**练习**：建立正常、悬停、键盘焦点、禁用四种按钮状态，给每种状态截图并检查键盘操作。删去一个 theme token，预期对应工具类失去规则，这能帮助理解变量与类名的关系。运行生产构建，检查首屏样式、主题刷新闪烁及无 JavaScript 时的基础可读性；开发热更新成功不等于 SSR 接入完成。

依据：[Tailwind 4 迁移](https://tailwindcss.com/docs/upgrade-guide)、[自定义样式](https://tailwindcss.com/docs/adding-custom-styles)、[Linaria 基础](https://github.com/callstack/linaria/blob/master/docs/BASICS.md)。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
