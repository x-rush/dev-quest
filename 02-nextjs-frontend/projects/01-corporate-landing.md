# Next.js 16 企业官网开发实战

## 分阶段练习与验收

**最小阶段**：先做首页与一页详情，内容结构和导航完整。

**验收结果**：窄屏可阅读、键盘可到达主要链接，直接访问详情地址成功。

**扩展顺序**：动画与营销组件最后添加，先证明内容、布局和访问方式。

建议保存一份正常输入、一份失败输入、实际输出和对应测试。先完成以上阶段再扩展正文中的完整设计；遇到省略实现或未定义依赖，应按文档上下文补齐，不能把代码片段拼接后当作已经验证的完整工程。

> 从一个可访问的内容站点开始：先交付可直接访问的首页与详情页，再逐步接入国际化、CMS、表单和可观测性。每一步都给出输入、产物和验收边界。

**目标读者**: 有React基础，希望学习企业级Next.js应用开发的开发者
**前置知识**: React基础、JavaScript ES6+、HTML/CSS、基础npm使用
**预计时长**: 2-3周

## 📚 文档元数据
| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `projects` |
| **难度** | ⭐⭐⭐ (精通)|
| **标签** | `Next.js 16` `React` `TypeScript` `内容站点` `SEO` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **内容状态** | 教学设计已编写；按本文验收条件完成本地或目标环境验证 |

## 🎯 学习目标

- 用 App Router 实现首页、服务列表和一篇可直接访问的详情页，理解路由、布局和元数据各放在哪里
- 让窄屏、键盘和屏幕阅读器都能完成主导航与联系表单；为图片和字段错误提供可理解的文本
- 为每个公开页面定义 title、description、canonical 和语言信息，并区分静态内容与按用户变化的内容
- 将内容源抽象为一个可替换的读取层；在本地先用固定数据验证页面，再决定是否接入 CMS
- 对表单在服务端检查字段、频率和来源边界，记录不含敏感内容的结果
- 把国际化、CMS、统计、邮件和部署作为扩展阶段；它们需要相应账号、服务或平台，不能由静态页面构建代替

## 📖 项目概述

### 项目背景
企业官网的核心是让访客找到、理解和联系组织。先用一组可审阅的本地内容完成信息架构；CMS、分析平台和邮件服务只是在后续替换内容来源或交付渠道，不能代替页面、导航和可访问性本身。

### 分阶段功能与完成条件

| 阶段 | 交付物 | 通过条件 |
|---|---|---|
| 1：内容与导航 | 首页、服务页、详情页与主导航 | 窄屏不横向溢出；键盘可到达主要链接；刷新详情 URL 不丢失页面 |
| 2：语义与 SEO | 每页元数据、图片替代文本、错误/空状态 | 页面标题描述与内容一致；无内容时说明原因；没有用颜色作为唯一状态提示 |
| 3：表单边界 | 联系表单、服务端校验和成功/失败反馈 | 缺字段、超长字段和重复提交得到明确 4xx/用户提示；日志不含内容和令牌 |
| 4：内容来源 | 本地数据读取层，随后可选 CMS 适配器 | 更换读取实现不改变页面契约；草稿与公开内容不会混在同一缓存结果 |
| 5：扩展 | 国际化、分析、邮件、部署 | 为每项记录使用的服务、隐私边界、验证 URL/日志和回退方式 |

### 技术选择：从最小依赖开始

| 范围 | 起步选择 | 何时增加外部工具 |
|---|---|---|
| 页面与路由 | Next.js App Router + 脚手架生成的 React/TypeScript 版本 | 页面共享的交互状态确实跨越组件边界时再评估状态库 |
| 样式 | 只选项目已配置的一种方案 | 设计令牌或隔离需求出现后再组合 Tailwind 与 CSS Modules，避免同一组件双重定义 |
| 内容 | 本地 typed data 或 Markdown | 编辑者需要独立发布、草稿与权限时再接 CMS |
| 表单 | 本地处理器与可观察的校验结果 | 要发送邮件、保存线索或防滥用时接对应服务，并使用测试凭证 |
| 发布与分析 | 本地 build 及固定测试页面 | 有真实域名、隐私政策和服务账号后再配置托管与分析平台 |

## 🏗️ 项目架构

### 目录结构
```
corporate-landing/
├── app/                          # App Router目录
│   ├── [locale]/                 # 多语言路由
│   │   ├── layout.tsx           # 根布局
│   │   ├── page.tsx             # 首页
│   │   ├── about/               # 关于我们
│   │   ├── services/            # 服务页面
│   │   ├── blog/                # 博客列表
│   │   │   └── [slug]/         # 文章详情
│   │   ├── contact/             # 联系我们
│   │   └── globals.css         # 全局样式
│   ├── api/                     # API路由
│   │   ├── contact/            # 联系表单
│   │   └── newsletter/         # 订阅服务
│   └── layout.tsx              # 根布局
├── components/                  # 组件库
│   ├── ui/                     # UI基础组件
│   ├── sections/               # 页面区块组件
│   ├── layout/                 # 布局组件
│   └── forms/                  # 表单组件
├── lib/                        # 工具函数
│   ├── cms/                    # CMS集成
│   ├── i18n/                   # 国际化
│   ├── validations/            # 表单验证
│   └── utils/                  # 通用工具
├── hooks/                      # 自定义Hooks
├── types/                      # TypeScript类型
├── public/                     # 静态资源
├── styles/                     # 样式文件
└── proxy.ts                   # 网络代理（原中间件）
```

### 技术选型理由
1. **Next.js 16**: 最新的App Router提供更好的性能和开发体验
2. **TypeScript**: 类型安全和更好的开发工具支持
3. **Tailwind CSS**: 快速响应式设计和维护性
4. **Strapi**: 灵活的内容管理和API生成
5. **Zustand**: 轻量级状态管理，避免过度复杂

## 🛠️ 实战步骤

### 步骤一：项目初始化

#### 1.1 创建Next.js项目
```bash
# 创建Next.js 16项目
npx create-next-app@latest corporate-landing --typescript --tailwind --eslint --app

# 进入项目目录
cd corporate-landing

# 安装必要依赖
npm install next-intl zustand react-hook-form @hookform/resolvers zod
npm install @vercel/analytics @types/node lucide-react framer-motion
npm install -D @types/react @types/react-dom
```

#### 1.2 配置TypeScript
**tsconfig.json**:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"],
      "@/components/*": ["./components/*"],
      "@/lib/*": ["./lib/*"],
      "@/types/*": ["./types/*"],
      "@/hooks/*": ["./hooks/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

#### 1.3 配置Tailwind CSS
**tailwind.config.ts**:
```typescript
import type { Config } from 'tailwindcss'

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
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          900: '#1e3a8a',
        },
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          900: '#111827',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out',
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
      },
    },
  },
  plugins: [],
}
export default config
```

#### 1.4 配置ESLint和Prettier
**.eslintrc.json**:
```json
{
  "extends": ["next/core-web-vitals", "next/typescript"],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "warn",
    "react-hooks/exhaustive-deps": "warn"
  }
}
```

**.prettierrc**:
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
```

### 步骤二：核心功能开发

#### 2.1 实现多语言支持
**lib/i18n/config.ts**:
```typescript
export const locales = ['en', 'zh-CN', 'zh-TW'] as const;
export type Locale = (typeof locales)[number];

export const defaultLocale: Locale = 'en';

export const localeNames = {
  en: 'English',
  'zh-CN': '简体中文',
  'zh-TW': '繁體中文',
} as const;
```

**lib/i18n/request.ts**:
```typescript
import { headers } from 'next/headers';
import { Locale } from './config';

export async function getLocale(): Promise<Locale> {
  const headersList = await headers();
  const acceptLanguage = headersList.get('accept-language');

  // 简单的语言检测逻辑
  if (acceptLanguage?.includes('zh-CN')) return 'zh-CN';
  if (acceptLanguage?.includes('zh-TW')) return 'zh-TW';

  return 'en';
}
```

**proxy.ts**（Next.js 16：原 middleware.ts）:
```typescript
import createMiddleware from 'next-intl/middleware';
import { locales, defaultLocale } from './lib/i18n/config';

export default createMiddleware({
  locales,
  defaultLocale,
  localePrefix: 'as-needed',
});

export const config = {
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)'],
};
```

#### 2.2 创建基础布局组件
**app/[locale]/layout.tsx**:
```tsx
import { NextIntlClientProvider } from 'next-intl';
import { getMessages, getTranslations } from 'next-intl/server';
import { Inter } from 'next/font/google';
import { notFound } from 'next/navigation';
import { locales } from '@/lib/i18n/config';
import '../globals.css';

const inter = Inter({ subsets: ['latin'] });

export async function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'metadata' });

  return {
    title: t('title'),
    description: t('description'),
    openGraph: {
      title: t('title'),
      description: t('description'),
      type: 'website',
    },
  };
}

export default async function RootLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!locales.includes(locale as any)) {
    notFound();
  }

  const messages = await getMessages();

  return (
    <html lang={locale}>
      <body className={inter.className}>
        <NextIntlClientProvider messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
```

#### 2.3 实现导航组件
**components/layout/Navbar.tsx**:
```tsx
'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X, Globe } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useLocale, useTranslations } from 'next-intl';
import { locales, localeNames } from '@/lib/i18n/config';

const navigation = [
  { name: 'home', href: '/' },
  { name: 'about', href: '/about' },
  { name: 'services', href: '/services' },
  { name: 'blog', href: '/blog' },
  { name: 'contact', href: '/contact' },
];

export function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const pathname = usePathname();
  const locale = useLocale();
  const t = useTranslations('navigation');

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const toggleMenu = () => setIsOpen(!isOpen);

  return (
    <nav
      className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-white/95 backdrop-blur-md shadow-md'
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href={`/${locale}`} className="flex items-center">
            <span className="text-2xl font-bold text-primary-600">
              Company
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={`/${locale}${item.href}`}
                className={`text-sm font-medium transition-colors hover:text-primary-600 ${
                  pathname === `/${locale}${item.href}`
                    ? 'text-primary-600'
                    : 'text-gray-700'
                }`}
              >
                {t(item.name)}
              </Link>
            ))}

            {/* Language Selector */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  <Globe className="w-4 h-4 mr-2" />
                  {localeNames[locale as keyof typeof localeNames]}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                {locales.map((lang) => (
                  <DropdownMenuItem key={lang} asChild>
                    <Link href={pathname.replace(`/${locale}`, `/${lang}`)}>
                      {localeNames[lang]}
                    </Link>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleMenu}
              aria-label="Toggle menu"
            >
              {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-white rounded-lg shadow-lg mt-2">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  href={`/${locale}${item.href}`}
                  className={`block px-3 py-2 rounded-md text-base font-medium ${
                    pathname === `/${locale}${item.href}`
                      ? 'text-primary-600 bg-primary-50'
                      : 'text-gray-700 hover:text-primary-600 hover:bg-gray-50'
                  }`}
                  onClick={() => setIsOpen(false)}
                >
                  {t(item.name)}
                </Link>
              ))}

              {/* Mobile Language Selector */}
              <div className="px-3 py-2 border-t">
                <p className="text-sm font-medium text-gray-700 mb-2">
                  {t('language')}
                </p>
                <div className="space-y-1">
                  {locales.map((lang) => (
                    <Link
                      key={lang}
                      href={pathname.replace(`/${locale}`, `/${lang}`)}
                      className={`block px-2 py-1 text-sm rounded ${
                        lang === locale
                          ? 'text-primary-600 bg-primary-50'
                          : 'text-gray-600 hover:text-primary-600'
                      }`}
                    >
                      {localeNames[lang]}
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
```

#### 2.4 实现首页Hero区域
**components/sections/Hero.tsx**:
```tsx
'use client';

import { useState, useEffect } from 'react';
import { ArrowRight, Play, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useTranslations } from 'next-intl';
import { motion } from 'framer-motion';

export function Hero() {
  const t = useTranslations('hero');
  const [currentTextIndex, setCurrentTextIndex] = useState(0);

  const rotatingTexts = [
    t('rotating.innovation'),
    t('rotating.excellence'),
    t('rotating.growth'),
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTextIndex((prev) => (prev + 1) % rotatingTexts.length);
    }, 3000);

    return () => clearInterval(interval);
  }, [rotatingTexts.length]);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50 to-white">
        <div className="absolute inset-0 bg-[url('/hero-pattern.svg')] opacity-10" />
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-gray-900 mb-6">
            <span className="block">{t('title.line1')}</span>
            <span className="block text-primary-600">
              {t('title.line2')}
            </span>
          </h1>

          <div className="h-12 mb-6">
            <motion.p
              key={currentTextIndex}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
              className="text-xl md:text-2xl text-gray-600"
            >
              {rotatingTexts[currentTextIndex]}
            </motion.p>
          </div>

          <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
            {t('description')}
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Button size="lg" className="text-lg px-8 py-6">
              {t('cta.primary')}
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
            <Button variant="outline" size="lg" className="text-lg px-8 py-6">
              <Play className="mr-2 w-5 h-5" />
              {t('cta.secondary')}
            </Button>
          </div>
        </motion.div>

        {/* Scroll Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 1 }}
          className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
        >
          <ChevronDown className="w-6 h-6 text-gray-400 animate-bounce" />
        </motion.div>
      </div>

      {/* Decorative Elements */}
      <div className="absolute top-20 left-10 w-72 h-72 bg-primary-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob" />
      <div className="absolute top-40 right-10 w-72 h-72 bg-yellow-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000" />
      <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000" />
    </section>
  );
}
```

#### 2.5 实现服务展示组件
**components/sections/Services.tsx**:
```tsx
'use client';

import { useState } from 'react';
import {
  Code2,
  Database,
  Cloud,
  Shield,
  Smartphone,
  Zap,
  ArrowRight
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useTranslations } from 'next-intl';
import { motion } from 'framer-motion';

const services = [
  {
    icon: Code2,
    titleKey: 'services.web.title',
    descriptionKey: 'services.web.description',
    featuresKey: 'services.web.features',
  },
  {
    icon: Database,
    titleKey: 'services.data.title',
    descriptionKey: 'services.data.description',
    featuresKey: 'services.data.features',
  },
  {
    icon: Cloud,
    titleKey: 'services.cloud.title',
    descriptionKey: 'services.cloud.description',
    featuresKey: 'services.cloud.features',
  },
  {
    icon: Shield,
    titleKey: 'services.security.title',
    descriptionKey: 'services.security.description',
    featuresKey: 'services.security.features',
  },
  {
    icon: Smartphone,
    titleKey: 'services.mobile.title',
    descriptionKey: 'services.mobile.description',
    featuresKey: 'services.mobile.features',
  },
  {
    icon: Zap,
    titleKey: 'services.optimization.title',
    descriptionKey: 'services.optimization.description',
    featuresKey: 'services.optimization.features',
  },
];

export function Services() {
  const t = useTranslations();
  const [hoveredService, setHoveredService] = useState<number | null>(null);

  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            {t('services.title')}
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            {t('services.subtitle')}
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {services.map((service, index) => {
            const Icon = service.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                onHoverStart={() => setHoveredService(index)}
                onHoverEnd={() => setHoveredService(null)}
              >
                <Card className={`h-full transition-all duration-300 cursor-pointer ${
                  hoveredService === index
                    ? 'shadow-xl scale-105 border-primary-200'
                    : 'shadow-md hover:shadow-lg'
                }`}>
                  <CardHeader>
                    <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                      <Icon className="w-6 h-6 text-primary-600" />
                    </div>
                    <CardTitle className="text-xl">
                      {t(service.titleKey)}
                    </CardTitle>
                    <CardDescription>
                      {t(service.descriptionKey)}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2 mb-6">
                      {t.raw(service.featuresKey).map((feature: string, idx: number) => (
                        <li key={idx} className="flex items-center text-sm text-gray-600">
                          <div className="w-1.5 h-1.5 bg-primary-600 rounded-full mr-3" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                    <Button variant="outline" className="w-full">
                      {t('services.learnMore')}
                      <ArrowRight className="ml-2 w-4 h-4" />
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
```

### 步骤三：高级特性实现

#### 3.1 集成Strapi CMS
**lib/cms/client.ts**:
```typescript
import qs from 'qs';

const CMS_URL = process.env.CMS_URL || 'http://localhost:1337';

export interface CmsResponse<T> {
  data: T;
  meta: {
    pagination: {
      page: number;
      pageSize: number;
      pageCount: number;
      total: number;
    };
  };
}

export interface Post {
  id: number;
  attributes: {
    title: string;
    slug: string;
    content: string;
    excerpt: string;
    coverImage?: {
      data: {
        attributes: {
          url: string;
          alternativeText?: string;
        };
      };
    };
    publishedAt: string;
    locale: string;
  };
}

class CmsClient {
  private baseUrl: string;

  constructor(baseUrl: string = CMS_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, query?: any): Promise<CmsResponse<T>> {
    const url = `${this.baseUrl}/api${endpoint}${query ? `?${qs.stringify(query)}` : ''}`;

    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${process.env.CMS_TOKEN}`,
        'Content-Type': 'application/json',
      },
      next: { revalidate: 3600 }, // 缓存1小时
    });

    if (!response.ok) {
      throw new Error(`CMS request failed: ${response.statusText}`);
    }

    return response.json();
  }

  async getPosts(locale: string = 'en', page: number = 1, pageSize: number = 10) {
    return this.request<Post[]>('/posts', {
      locale,
      populate: ['coverImage'],
      pagination: {
        page,
        pageSize,
      },
      sort: ['publishedAt:desc'],
    });
  }

  async getPost(slug: string, locale: string = 'en') {
    return this.request<Post[]>('/posts', {
      locale,
      filters: { slug },
      populate: ['coverImage'],
    });
  }

  async getPage(slug: string, locale: string = 'en') {
    return this.request('/pages', {
      locale,
      filters: { slug },
      populate: ['components'],
    });
  }
}

export const cmsClient = new CmsClient();
```

#### 3.2 实现博客列表页面
**app/[locale]/blog/page.tsx**:
```tsx
import { Metadata } from 'next';
import { getTranslations, setRequestLocale } from 'next-intl/server';
import { notFound } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import { zhCN, enUS } from 'date-fns/locale';
import { cmsClient, type Post } from '@/lib/cms/client';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Calendar, Clock, ArrowRight } from 'lucide-react';

interface BlogPageProps {
  params: Promise<{ locale: string }>;
  searchParams: Promise<{ page?: string }>;
}

export async function generateMetadata({ params }: BlogPageProps): Promise<Metadata> {
  const { locale } = await params;
  setRequestLocale(locale);

  const t = await getTranslations({ locale, namespace: 'blog' });

  return {
    title: t('title'),
    description: t('description'),
  };
}

export default async function BlogPage({ params, searchParams }: BlogPageProps) {
  const { locale } = await params;
  const { page: pageParam } = await searchParams;
  const page = parseInt(pageParam || '1');
  setRequestLocale(locale);

  const t = await getTranslations({ locale, namespace: 'blog' });

  try {
    const postsResponse = await cmsClient.getPosts(locale, page, 6);
    const posts = postsResponse.data;
    const pagination = postsResponse.meta.pagination;

    if (posts.length === 0 && page > 1) {
      notFound();
    }

    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          {/* Header */}
          <div className="text-center mb-16">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              {t('title')}
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              {t('description')}
            </p>
          </div>

          {/* Posts Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
            {posts.map((post) => (
              <Card key={post.id} className="overflow-hidden hover:shadow-lg transition-shadow duration-300">
                {post.attributes.coverImage?.data && (
                  <div className="aspect-video relative">
                    <Image
                      src={`${process.env.CMS_URL}${post.attributes.coverImage.data.attributes.url}`}
                      alt={post.attributes.coverImage.data.attributes.alternativeText || post.attributes.title}
                      fill
                      className="object-cover"
                    />
                  </div>
                )}
                <CardHeader>
                  <div className="flex items-center text-sm text-gray-500 mb-2">
                    <Calendar className="w-4 h-4 mr-1" />
                    {new Date(post.attributes.publishedAt).toLocaleDateString(locale)}
                    <Clock className="w-4 h-4 ml-4 mr-1" />
                    {formatDistanceToNow(new Date(post.attributes.publishedAt), {
                      addSuffix: true,
                      locale: locale === 'zh-CN' ? zhCN : enUS,
                    })}
                  </div>
                  <CardTitle className="line-clamp-2">
                    {post.attributes.title}
                  </CardTitle>
                  <CardDescription className="line-clamp-3">
                    {post.attributes.excerpt}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href={`/${locale}/blog/${post.attributes.slug}`}>
                    <Button variant="outline" className="w-full">
                      {t('readMore')}
                      <ArrowRight className="ml-2 w-4 h-4" />
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          {pagination.pageCount > 1 && (
            <div className="flex justify-center">
              <div className="flex space-x-2">
                {page > 1 && (
                  <Link href={`/${locale}/blog?page=${page - 1}`}>
                    <Button variant="outline">{t('pagination.previous')}</Button>
                  </Link>
                )}

                <span className="flex items-center px-4 py-2 text-sm text-gray-700">
                  {t('pagination.pageInfo', {
                    current: page,
                    total: pagination.pageCount,
                  })}
                </span>

                {page < pagination.pageCount && (
                  <Link href={`/${locale}/blog?page=${page + 1}`}>
                    <Button variant="outline">{t('pagination.next')}</Button>
                  </Link>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  } catch (error) {
    console.error('Failed to fetch blog posts:', error);
    notFound();
  }
}
```

#### 3.3 实现联系表单
**components/forms/ContactForm.tsx**:
```tsx
'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useTranslations } from 'next-intl';
import { Mail, Phone, MapPin, Send, CheckCircle, AlertCircle } from 'lucide-react';

const contactSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  company: z.string().optional(),
  phone: z.string().optional(),
  subject: z.string().min(5, 'Subject must be at least 5 characters'),
  message: z.string().min(10, 'Message must be at least 10 characters'),
});

type ContactFormData = z.infer<typeof contactSchema>;

export function ContactForm() {
  const t = useTranslations('contact');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ContactFormData>({
    resolver: zodResolver(contactSchema),
  });

  const onSubmit = async (data: ContactFormData) => {
    setIsSubmitting(true);
    setSubmitStatus('idle');

    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        setSubmitStatus('success');
        reset();
      } else {
        setSubmitStatus('error');
      }
    } catch (error) {
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Contact Information */}
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            {t('title')}
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            {t('description')}
          </p>

          <div className="space-y-6">
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <Mail className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                  {t('info.email.title')}
                </h3>
                <p className="text-gray-600">{t('info.email.value')}</p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <Phone className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                  {t('info.phone.title')}
                </h3>
                <p className="text-gray-600">{t('info.phone.value')}</p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <MapPin className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                  {t('info.address.title')}
                </h3>
                <p className="text-gray-600">{t('info.address.value')}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Contact Form */}
        <Card>
          <CardHeader>
            <CardTitle>{t('form.title')}</CardTitle>
            <CardDescription>{t('form.description')}</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                    {t('form.name')} *
                  </label>
                  <Input
                    id="name"
                    {...register('name')}
                    className={errors.name ? 'border-red-500' : ''}
                    placeholder={t('form.namePlaceholder')}
                  />
                  {errors.name && (
                    <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                    {t('form.email')} *
                  </label>
                  <Input
                    id="email"
                    type="email"
                    {...register('email')}
                    className={errors.email ? 'border-red-500' : ''}
                    placeholder={t('form.emailPlaceholder')}
                  />
                  {errors.email && (
                    <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-1">
                    {t('form.company')}
                  </label>
                  <Input
                    id="company"
                    {...register('company')}
                    placeholder={t('form.companyPlaceholder')}
                  />
                </div>

                <div>
                  <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
                    {t('form.phone')}
                  </label>
                  <Input
                    id="phone"
                    {...register('phone')}
                    placeholder={t('form.phonePlaceholder')}
                  />
                </div>
              </div>

              <div>
                <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">
                  {t('form.subject')} *
                </label>
                <Input
                  id="subject"
                  {...register('subject')}
                  className={errors.subject ? 'border-red-500' : ''}
                  placeholder={t('form.subjectPlaceholder')}
                />
                {errors.subject && (
                  <p className="mt-1 text-sm text-red-600">{errors.subject.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">
                  {t('form.message')} *
                </label>
                <Textarea
                  id="message"
                  rows={5}
                  {...register('message')}
                  className={errors.message ? 'border-red-500' : ''}
                  placeholder={t('form.messagePlaceholder')}
                />
                {errors.message && (
                  <p className="mt-1 text-sm text-red-600">{errors.message.message}</p>
                )}
              </div>

              {/* Submit Status */}
              {submitStatus === 'success' && (
                <div className="flex items-center p-4 bg-green-50 border border-green-200 rounded-lg">
                  <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                  <p className="text-green-800">{t('form.success')}</p>
                </div>
              )}

              {submitStatus === 'error' && (
                <div className="flex items-center p-4 bg-red-50 border border-red-200 rounded-lg">
                  <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                  <p className="text-red-800">{t('form.error')}</p>
                </div>
              )}

              <Button
                type="submit"
                disabled={isSubmitting}
                className="w-full"
              >
                {isSubmitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    {t('form.sending')}
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4 mr-2" />
                    {t('form.submit')}
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

#### 3.4 实现API路由处理联系表单
**app/api/contact/route.ts**:
```typescript
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import nodemailer from 'nodemailer';

const contactSchema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
  company: z.string().optional(),
  phone: z.string().optional(),
  subject: z.string().min(5),
  message: z.string().min(10),
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { name, email, company, phone, subject, message } = contactSchema.parse(body);

    // 配置邮件发送
    const transporter = nodemailer.createTransport({
      host: process.env.SMTP_HOST,
      port: parseInt(process.env.SMTP_PORT || '587'),
      secure: process.env.SMTP_SECURE === 'true',
      auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS,
      },
    });

    // 发送给管理者的邮件
    const adminEmail = await transporter.sendMail({
      from: process.env.SMTP_FROM,
      to: process.env.ADMIN_EMAIL,
      subject: `New Contact Form: ${subject}`,
      html: `
        <h2>New Contact Form Submission</h2>
        <p><strong>Name:</strong> ${name}</p>
        <p><strong>Email:</strong> ${email}</p>
        ${company ? `<p><strong>Company:</strong> ${company}</p>` : ''}
        ${phone ? `<p><strong>Phone:</strong> ${phone}</p>` : ''}
        <p><strong>Subject:</strong> ${subject}</p>
        <p><strong>Message:</strong></p>
        <p>${message.replace(/\n/g, '<br>')}</p>
      `,
    });

    // 发送确认邮件给用户
    const userEmail = await transporter.sendMail({
      from: process.env.SMTP_FROM,
      to: email,
      subject: 'Thank you for contacting us',
      html: `
        <h2>Thank you for contacting us!</h2>
        <p>Dear ${name},</p>
        <p>We have received your message and will get back to you within 24 hours.</p>
        <p>Here's a copy of your message:</p>
        <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
          <p><strong>Subject:</strong> ${subject}</p>
          <p><strong>Message:</strong></p>
          <p>${message.replace(/\n/g, '<br>')}</p>
        </div>
        <p>Best regards,<br />The Team</p>
      `,
    });

    return NextResponse.json(
      { message: 'Contact form submitted successfully' },
      { status: 200 }
    );
  } catch (error) {
    console.error('Contact form error:', error);

    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { message: 'Invalid form data', errors: error.issues },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

#### 3.5 页面元数据完善与 error / loading / not-found 文件约定

> 📖 呼应字典：[错误与加载状态约定](../reference/framework-patterns/11-error-loading-patterns.md)

官网是 SEO 权重最重的场景。3.2 已为博客页实现 `generateMetadata`，这里把元数据补全到根布局，并加上 App Router 的三个文件约定，让官网在分享卡片、容错与 404 场景都有兜底。

**根布局元数据（app/[locale]/layout.tsx，在现有 RootLayout 中补充导出）**：

```typescript
import type { Metadata } from 'next';

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;

  return {
    metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? 'https://example.com'),
    title: {
      default: 'Acme Corp',
      template: '%s | Acme Corp',
    },
    description: '全球领先的企业服务提供商',
    alternates: {
      canonical: `/${locale}`,
    },
    openGraph: {
      siteName: 'Acme Corp',
      type: 'website',
    },
  };
}
```

**加载兜底（app/[locale]/about/loading.tsx）**——营销页视觉素材多，进入时给骨架：

```tsx
export default function Loading() {
  return (
    <div className="mx-auto max-w-5xl animate-pulse space-y-8 px-4 py-16">
      <div className="h-12 w-2/3 rounded bg-gray-200" />
      <div className="h-64 rounded-xl bg-gray-200" />
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-40 rounded-lg bg-gray-200" />
        ))}
      </div>
    </div>
  );
}
```

**错误边界（app/[locale]/error.tsx）**——必须是客户端组件：

```tsx
'use client';

export default function LocaleError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div role="alert" className="mx-auto max-w-xl px-4 py-24 text-center">
      <h2 className="text-2xl font-bold">页面出错了</h2>
      <p className="mt-2 text-gray-500">请稍后重试；问题持续存在请联系管理员。</p>
      {error.digest && <p className="mt-1 text-xs text-gray-400">ID: {error.digest}</p>}
      <button
        onClick={reset}
        className="mt-6 rounded-md bg-blue-600 px-6 py-2 text-white"
      >
        重试
      </button>
    </div>
  );
}
```

**404 约定（app/[locale]/not-found.tsx）**——承接 3.2 中 CMS 查不到数据时调用的 `notFound()`：

```tsx
import Link from 'next/link';

export default function LocaleNotFound() {
  return (
    <div className="mx-auto max-w-xl px-4 py-24 text-center">
      <h2 className="text-3xl font-bold">404</h2>
      <p className="mt-2 text-gray-500">页面不存在或已下线</p>
      <Link href="/" className="mt-6 inline-block text-blue-600 underline">
        返回首页
      </Link>
    </div>
  );
}
```

要点（详见上方字典）：`error.tsx` 不捕获同层 `layout.tsx` 抛出的错误——本项目在 RootLayout 中做的 locale 校验 `notFound()` 会向上冒泡到父级约定；仅靠 `error.tsx` 无法兜住根布局崩溃，需另配 `app/global-error.tsx`（自带 `<html>`/`<body>`）作为最后防线；`loading.tsx` 作用于整个路由段，营销页想只对慢图片流式渲染应使用 `<Suspense>`。

### 步骤四：测试和优化

#### 4.1 配置测试环境
**jest.config.js**:
```javascript
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  collectCoverageFrom: [
    'components/**/*.{js,jsx,ts,tsx}',
    'lib/**/*.{js,jsx,ts,tsx}',
    'app/**/*.{js,jsx,ts,tsx}',
    '!app/layout.tsx',
    '!app/**/layout.tsx',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
}

module.exports = createJestConfig(customJestConfig)
```

**jest.setup.js**:
```javascript
import '@testing-library/jest-dom'

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
    }
  },
  usePathname() {
    return '/'
  },
}))

// Mock next-intl
jest.mock('next-intl', () => ({
  useTranslations: () => (key: string) => key,
  useLocale: () => 'en',
  getTranslations: () => Promise.resolve((key: string) => key),
  getMessages: () => Promise.resolve({}),
}))
```

#### 4.2 组件测试示例
**__tests__/components/Navbar.test.tsx**:
```tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { Navbar } from '@/components/layout/Navbar'

// Mock usePathname
jest.mock('next/navigation', () => ({
  usePathname: () => '/en',
}))

describe('Navbar', () => {
  it('renders navigation links', () => {
    render(<Navbar />)

    expect(screen.getByText('home')).toBeInTheDocument()
    expect(screen.getByText('about')).toBeInTheDocument()
    expect(screen.getByText('services')).toBeInTheDocument()
  })

  it('toggles mobile menu', () => {
    render(<Navbar />)

    const menuButton = screen.getByRole('button', { name: /toggle menu/i })
    expect(menuButton).toBeInTheDocument()

    // Initially menu should be closed
    expect(screen.queryByText('language')).not.toBeInTheDocument()

    // Click to open menu
    fireEvent.click(menuButton)
    expect(screen.getByText('language')).toBeInTheDocument()

    // Click to close menu
    fireEvent.click(menuButton)
    expect(screen.queryByText('language')).not.toBeInTheDocument()
  })
})
```

#### 4.3 性能优化配置
**next.config.js**:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Next.js 15+：serverComponentsExternalPackages 移至顶层 serverExternalPackages
  serverExternalPackages: ['date-fns'],
  images: {
    // Next.js 16：images.domains 已弃用，远程域名改用 remotePatterns
    remotePatterns: [
      { protocol: 'https', hostname: 'your-cms-domain.com' },
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
  httpAgentOptions: {
    keepAlive: true,
  },
}

module.exports = nextConfig
```

### 步骤五：部署和上线

#### 5.1 环境变量配置
**.env.local**:
```bash
# CMS Configuration
CMS_URL=http://localhost:1337
CMS_TOKEN=your-cms-api-token

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SMTP_FROM=noreply@yourcompany.com
ADMIN_EMAIL=admin@yourcompany.com

# Analytics
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
NEXT_PUBLIC_VERCEL_ANALYTICS=true

# Other
NEXT_PUBLIC_SITE_URL=https://yourcompany.com
```

#### 5.2 Vercel部署配置
**vercel.json**:
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["sin1"],
  "functions": {
    "app/api/**/*.ts": {
      "maxDuration": 30
    }
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        }
      ]
    },
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "s-maxage=86400"
        }
      ]
    }
  ]
}
```

#### 5.3 CI/CD配置
**.github/workflows/deploy.yml**:
```yaml
name: Deploy to Vercel

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run tests
      run: npm test

    - name: Run linting
      run: npm run lint

    - name: Build project
      run: npm run build
      env:
        NEXT_PUBLIC_SITE_URL: ${{ secrets.NEXT_PUBLIC_SITE_URL }}

    - name: Deploy to Vercel
      uses: amondnet/vercel-action@v25
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.ORG_ID }}
        vercel-project-id: ${{ secrets.PROJECT_ID }}
        scope: ${{ secrets.VERCEL_ORG_ID }}
```

## 💡 关键技术点

### 1. Next.js 16 App Router
- 使用App Router替代Pages Router，获得更好的性能和开发体验
- 实现流式渲染和服务器组件
- 掌握路由组和动态路由的使用

### 2. 国际化解决方案
- 使用next-intl实现多语言支持
- 动态路由和中间件配置
- 语言检测和切换功能

### 3. CMS集成
- Strapi Headless CMS集成
- 类型安全的API客户端
- 内容缓存和优化策略

### 4. 性能优化
- 图片优化和懒加载
- 代码分割和动态导入
- 缓存策略和CDN配置

### 5. 表单处理
- React Hook Form + Zod验证
- 邮件发送功能
- 错误处理和用户反馈

## 🎨 UI/UX设计

### 设计原则
- **简洁现代**: 采用简洁的设计语言，突出内容
- **品牌一致性**: 统一的色彩和字体系统
- **可访问性**: 遵循WCAG 2.1标准
- **微交互**: 适度的动画和过渡效果

### 组件设计系统
```typescript
// tokens.ts - 设计令牌
export const colors = {
  primary: {
    50: '#eff6ff',
    100: '#dbeafe',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
    900: '#1e3a8a',
  },
  // 其余颜色按同一命名规则补充；不要把未定义 token 用作组件样式。
} as const

export const spacing = {
  xs: '0.5rem',
  sm: '1rem',
  md: '1.5rem',
  lg: '2rem',
  xl: '3rem',
} as const

export const typography = {
  fontFamily: {
    sans: ['Inter', 'system-ui', 'sans-serif'],
  },
  fontSize: {
    xs: '0.75rem',
    sm: '0.875rem',
    base: '1rem',
    lg: '1.125rem',
    xl: '1.25rem',
    '2xl': '1.5rem',
    '3xl': '1.875rem',
    '4xl': '2.25rem',
  },
} as const
```

## 📱 响应式设计

### 移动优先策略
- 使用Tailwind CSS的响应式断点
- 触摸友好的交互设计
- 性能优化的移动体验

### 关键断点
```css
/* 移动设备 */
@media (max-width: 640px) { }

/* 平板设备 */
@media (min-width: 641px) and (max-width: 1024px) { }

/* 桌面设备 */
@media (min-width: 1025px) { }
```

## ⚡ 性能优化

### 1. 代码分割
- 动态导入非关键组件
- 路由级别的代码分割
- 第三方库按需加载

### 2. 图片优化
- Next.js Image组件使用
- 响应式图片配置
- 懒加载和预加载策略

### 3. 缓存策略
```typescript
// 页面级缓存
export const revalidate = 3600; // 1小时

// 数据获取缓存
const data = await fetch('/api/data', {
  next: { revalidate: 60 } // 1分钟
});
```

## 🔒 安全考虑

### 1. 数据验证
- 前端和后端双重验证
- Zod schema验证
- XSS防护

### 2. 安全头配置
- CSP (Content Security Policy)
- HSTS (HTTP Strict Transport Security)
- 其他安全相关HTTP头

### 3. API安全
- Rate limiting
- CORS配置
- 输入清理和验证

## 🧪 测试策略

### 测试金字塔
```
    E2E Tests (少量)
   /             \
Integration Tests (适量)
/                 \
Unit Tests (大量)
```

### 测试工具链
- **单元测试**: Jest + React Testing Library
- **集成测试**: Jest + MSW
- **E2E测试**: Playwright
- **视觉回归测试**: Chromatic

### 测试覆盖率目标
- 代码覆盖率: 80%+
- 分支覆盖率: 80%+
- 函数覆盖率: 90%+

## 🚀 部署方案

### Vercel部署
```bash
# 安装Vercel CLI
npm i -g vercel

# 部署到预览环境
vercel

# 部署到生产环境
vercel --prod
```

### 环境配置
- 开发环境: 本地开发
- 预览环境: 自动部署每个PR
- 生产环境: 主分支自动部署

### 监控和分析
- Vercel Analytics
- Google Analytics
- 错误监控和日志

## 🔄 文档交叉引用

### 相关文档
- 📄 **[02-ecommerce-store.md](./02-ecommerce-store.md)**: 电商应用项目实战
- 📄 **[03-dashboard-analytics.md](./03-dashboard-analytics.md)**: 数据仪表板项目实战
- 📄 **[04-saas-platform.md](./04-saas-platform.md)**: SaaS平台项目实战

### 参考章节
- 📖 **[Framework Deep Dive - Next.js](../frameworks/01-nextjs-16-complete.md)**: Next.js核心特性深度学习
- 📖 **[Styling - Tailwind CSS](../basics/05-styling-with-tailwind.md)**: Tailwind CSS快速参考
- 📖 **[API Integration](../basics/06-data-fetching-basics.md)**: API集成最佳实践

## 📝 总结

### 核心要点回顾

官网交付的边界是“内容能被正确找到、理解和更新”。App Router 的页面、布局与元数据应按 URL 和受众组织；每个可索引页面定义 title、description、canonical、语言和社交分享预览，避免多个路径指向同一内容却互相竞争搜索结果。预览、草稿和未发布 CMS 内容必须与公开缓存隔离。

国际化不是只替换文案。路由 locale、HTML `lang`、日期/数字格式、缺失翻译回退、`hreflang` 与 CMS 内容语言必须保持一致；用户从语言 A 切换到 B 时，应留在语义相同的页面或明确说明该内容没有翻译，不能悄悄跳到首页。

性能从可观察的页面路径开始：优化首屏图片尺寸与 `alt` 文本，延后非关键脚本，区分静态内容的再验证与个性化内容的动态渲染。联系表单和 CMS webhook 均在服务端校验输入、限制速率、记录安全的关联信息；客户端校验只改善体验，不替代防刷、CSRF/来源策略或密钥保护。

### 学习成果检查

- [ ] 用两种语言访问同一内容，检查 URL、`lang`、标题、日期格式和 `hreflang`；缺失译文按预定回退策略显示，不丢失原页面上下文。
- [ ] 对公开、草稿与预览内容分别请求，确认草稿不能进入公开响应或 CDN 缓存；发布更新后按定义的再验证路径可见。
- [ ] 用键盘和屏幕阅读器完成导航与联系表单，图片有符合内容目的的替代文本，错误消息与对应字段关联。
- [ ] 记录代表性首屏的图片大小、关键请求和可交互时间；移除或延后一个非关键脚本后比较数据，而非只宣称“已优化”。
- [ ] 对联系表单发送缺字段、超长字段和重复请求，服务端拒绝无效输入并限制滥用，日志不包含表单敏感内容或 CMS 令牌。

## 🤝 贡献与反馈

### 贡献指南
欢迎对本项目实战文档提出改进建议：
- 🐛 **Bug报告**: 发现文档错误或不准确之处
- 💡 **功能建议**: 提出新的实战场景或技术点
- 📝 **内容贡献**: 分享您的实战经验和最佳实践

### 反馈渠道
- GitHub Issues: [项目Issues页面]
- Email: dev-quest@example.com
- 社区讨论: [开发者社区链接]

## 🔗 外部资源

### 官方文档
- [Next.js 16 Documentation](https://nextjs.org/docs)
- [React 19 Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

### 学习资源
- [Next.js Learn Course](https://nextjs.org/learn)
- [React Patterns](https://reactpatterns.com/)
- [Modern Web Development](https://web.dev/)

### 工具和平台
- [Vercel Platform](https://vercel.com/)
- [Strapi CMS](https://strapi.io/)
- [Figma Design](https://www.figma.com/)

---

**文档状态**: ✅ 已完成 | 🚧 进行中 | 📋 计划中
**最后更新**: 2026年9月
**版本**: v1.0.0

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
