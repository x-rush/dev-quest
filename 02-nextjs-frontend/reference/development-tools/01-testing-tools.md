# Next.js 16 现代测试工具完整指南

> **文档简介**: Next.js 16 现代测试工具速查指南，涵盖Vitest、Playwright、MSW、React Testing Library等现代测试工具链

> **目标读者**: 具备基础测试知识的前端开发者，需要掌握Next.js 16现代测试工具链的工程师

> **前置知识**: Next.js 16基础、TypeScript 5、测试基础概念、JavaScript ES6+

> **预计时长**: 6-8小时

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `reference` |
| **难度** | ⭐⭐⭐ (精通)|
| **标签** | `#testing` `#vitest` `#playwright` `#msw` `#react-testing-library` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 📚 概述

Next.js 16 结合现代测试工具链提供了全面的质量保证解决方案。本指南深入探讨企业级测试策略，涵盖单元测试、组件测试、端到端测试、API测试和性能测试，帮助开发团队建立可靠的质量保障体系。

## 🛠️ 测试工具生态概览

### 测试金字塔策略

```typescript
// testing/types/testing-hierarchy.ts
export interface TestingHierarchy {
  // 单元测试 - 快速、隔离、数量多
  unit: {
    tools: ['Vitest', 'Jest'];
    coverage: '70-80%';
    executionTime: '< 5ms per test';
    examples: ['Utility functions', 'Business logic', 'Data transformation'];
  };

  // 组件测试 - 中等速度、模拟依赖
  component: {
    tools: ['React Testing Library', 'Vitest', 'Storybook'];
    coverage: '50-60%';
    executionTime: '< 50ms per test';
    examples: ['UI components', 'User interactions', 'State changes'];
  };

  // 集成测试 - 较慢、真实环境
  integration: {
    tools: ['Vitest', 'Supertest', 'MSW'];
    coverage: '30-40%';
    executionTime: '< 500ms per test';
    examples: ['API integration', 'Database operations', 'Component integration'];
  };

  // E2E测试 - 最慢、完整流程
  e2e: {
    tools: ['Playwright', 'Cypress'];
    coverage: '10-20%';
    executionTime: '< 5s per test';
    examples: ['User journeys', 'Critical paths', 'Cross-browser testing'];
  };
}
```

## 🧪 Vitest 单元测试配置

### 基础配置

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    // 测试环境
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],

    // 覆盖率配置
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*'
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    },

    // 并发执行
    threads: true,
    concurrency: 4,

    // 全局设置
    globals: true,
    clearMocks: true,
    restoreMocks: true,

    // 报告器
    reporter: ['verbose', 'json', 'html'],
    outputFile: {
      json: './test-results/results.json',
      html: './test-results/results.html'
    },

    // 监听模式配置
    watchExclude: [
      'node_modules/',
      'dist/',
      '**/*.log'
    ]
  },

  // 路径解析
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/components': path.resolve(__dirname, './src/components'),
      '@/lib': path.resolve(__dirname, './src/lib'),
      '@/test': path.resolve(__dirname, './src/test')
    }
  }
});

// src/test/setup.ts
import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock Next.js router
vi.mock('next/router', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    prefetch: vi.fn(),
    reload: vi.fn(),
    pathname: '/',
    query: {},
    asPath: '/',
    events: {
      on: vi.fn(),
      off: vi.fn(),
      emit: vi.fn()
    }
  }),
  useRouterState: () => ({
    loading: false
  })
}));

// Mock Next.js navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
    prefetch: vi.fn()
  }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/',
  useParams: () => ({})
}));

// Global test utilities
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn()
}));

global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn()
}));
```

### 实用工具函数测试

```typescript
// src/lib/utils.ts
export function formatCurrency(
  amount: number,
  currency: string = 'USD',
  locale: string = 'en-US'
): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: 2
  }).format(amount);
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

export function slugify(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

// src/test/lib/utils.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { formatCurrency, debounce, slugify } from '@/lib/utils';

describe('formatCurrency', () => {
  it('should format USD currency correctly', () => {
    expect(formatCurrency(1234.56)).toBe('$1,234.56');
    expect(formatCurrency(0)).toBe('$0.00');
    expect(formatCurrency(-100)).toBe('-$100.00');
  });

  it('should format different currencies', () => {
    expect(formatCurrency(1234.56, 'EUR', 'de-DE')).toBe('1.234,56 €');
    expect(formatCurrency(1234.56, 'JPY', 'ja-JP')).toBe('￥1,234.56');
  });

  it('should handle decimal places correctly', () => {
    expect(formatCurrency(1234.5)).toBe('$1,234.50');
    expect(formatCurrency(1234.567)).toBe('$1,234.57');
  });
});

describe('debounce', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  it('should call function after specified delay', () => {
    const mockFn = vi.fn();
    const debouncedFn = debounce(mockFn, 500);

    debouncedFn();
    expect(mockFn).not.toHaveBeenCalled();

    vi.advanceTimersByTime(500);
    expect(mockFn).toHaveBeenCalledTimes(1);
  });

  it('should cancel previous calls', () => {
    const mockFn = vi.fn();
    const debouncedFn = debounce(mockFn, 500);

    debouncedFn();
    debouncedFn();
    debouncedFn();

    vi.advanceTimersByTime(500);
    expect(mockFn).toHaveBeenCalledTimes(1);
  });
});

describe('slugify', () => {
  it('should convert text to slug format', () => {
    expect(slugify('Hello World')).toBe('hello-world');
    expect(slugify('Hello, World!')).toBe('hello-world');
    expect(slugify('  Hello   World  ')).toBe('hello-world');
  });

  it('should handle special characters', () => {
    expect(slugify('Café & Restaurant')).toBe('caf-restaurant');
    expect(slugify('What\'s New?')).toBe('whats-new');
  });
});
```

## 🧩 React Testing Library 组件测试

### 组件测试模式

```typescript
// src/components/Button/Button.tsx
import React from 'react';
import { cn } from '@/lib/utils';

export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  children,
  onClick,
  className
}) => {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center rounded-md font-medium transition-colors',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
        'disabled:pointer-events-none disabled:opacity-50',
        {
          'bg-primary text-primary-foreground hover:bg-primary/90': variant === 'primary',
          'bg-secondary text-secondary-foreground hover:bg-secondary/80': variant === 'secondary',
          'bg-destructive text-destructive-foreground hover:bg-destructive/90': variant === 'danger',
          'hover:bg-accent hover:text-accent-foreground': variant === 'ghost'
        },
        {
          'h-9 px-3 text-sm': size === 'sm',
          'h-10 px-4 py-2': size === 'md',
          'h-11 px-8 text-lg': size === 'lg'
        },
        className
      )}
      disabled={disabled || loading}
      onClick={onClick}
      data-testid="button"
    >
      {loading && (
        <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
      )}
      {children}
    </button>
  );
};

// src/test/components/Button/Button.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from '@/components/Button/Button';

describe('Button Component', () => {
  it('should render button with text', () => {
    render(<Button>Click me</Button>);

    const button = screen.getByRole('button', { name: /click me/i });
    expect(button).toBeInTheDocument();
    expect(button).not.toBeDisabled();
  });

  it('should handle click events', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();

    render(<Button onClick={handleClick}>Click me</Button>);

    const button = screen.getByRole('button', { name: /click me/i });
    await user.click(button);

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('should apply variant styles correctly', () => {
    const { rerender } = render(<Button variant="primary">Primary</Button>);
    let button = screen.getByRole('button');
    expect(button).toHaveClass('bg-primary');

    rerender(<Button variant="secondary">Secondary</Button>);
    button = screen.getByRole('button');
    expect(button).toHaveClass('bg-secondary');
  });

  it('should apply size styles correctly', () => {
    const { rerender } = render(<Button size="sm">Small</Button>);
    let button = screen.getByRole('button');
    expect(button).toHaveClass('h-9');

    rerender(<Button size="lg">Large</Button>);
    button = screen.getByRole('button');
    expect(button).toHaveClass('h-11');
  });

  it('should be disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>);

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(button).toHaveClass('disabled:opacity-50');
  });

  it('should show loading state', () => {
    render(<Button loading>Loading</Button>);

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();

    const spinner = button.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('should support custom className', () => {
    render(<Button className="custom-class">Custom</Button>);

    const button = screen.getByRole('button');
    expect(button).toHaveClass('custom-class');
  });

  it('should have proper accessibility attributes', () => {
    render(<Button disabled>Disabled Button</Button>);

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('data-testid', 'button');
  });
});
```

### Hook 测试模式

```typescript
// src/hooks/useCounter.ts
import { useState, useCallback } from 'react';

export interface UseCounterOptions {
  initial?: number;
  min?: number;
  max?: number;
  step?: number;
}

export function useCounter(options: UseCounterOptions = {}) {
  const {
    initial = 0,
    min = Number.MIN_SAFE_INTEGER,
    max = Number.MAX_SAFE_INTEGER,
    step = 1
  } = options;

  const [count, setCount] = useState(initial);

  const increment = useCallback(() => {
    setCount(prev => Math.min(prev + step, max));
  }, [step, max]);

  const decrement = useCallback(() => {
    setCount(prev => Math.max(prev - step, min));
  }, [step, min]);

  const reset = useCallback(() => {
    setCount(initial);
  }, [initial]);

  const setValue = useCallback((value: number) => {
    setCount(Math.max(min, Math.min(value, max)));
  }, [min, max]);

  return {
    count,
    increment,
    decrement,
    reset,
    setValue,
    canIncrement: count < max,
    canDecrement: count > min,
    isAtMin: count === min,
    isAtMax: count === max
  };
}

// src/test/hooks/useCounter.test.tsx
import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useCounter } from '@/hooks/useCounter';

describe('useCounter', () => {
  it('should initialize with default value', () => {
    const { result } = renderHook(() => useCounter());

    expect(result.current.count).toBe(0);
    expect(result.current.canIncrement).toBe(true);
    expect(result.current.canDecrement).toBe(true);
  });

  it('should initialize with custom value', () => {
    const { result } = renderHook(() => useCounter({ initial: 5 }));

    expect(result.current.count).toBe(5);
  });

  it('should increment correctly', () => {
    const { result } = renderHook(() => useCounter());

    act(() => {
      result.current.increment();
    });

    expect(result.current.count).toBe(1);
  });

  it('should decrement correctly', () => {
    const { result } = renderHook(() => useCounter({ initial: 5 }));

    act(() => {
      result.current.decrement();
    });

    expect(result.current.count).toBe(4);
  });

  it('should respect min and max boundaries', () => {
    const { result } = renderHook(() => useCounter({
      initial: 5,
      min: 0,
      max: 10
    }));

    // Test max boundary
    act(() => {
      result.current.setValue(15);
    });
    expect(result.current.count).toBe(10);
    expect(result.current.isAtMax).toBe(true);

    // Test min boundary
    act(() => {
      result.current.setValue(-5);
    });
    expect(result.current.count).toBe(0);
    expect(result.current.isAtMin).toBe(true);
  });

  it('should reset to initial value', () => {
    const { result } = renderHook(() => useCounter({ initial: 10 }));

    act(() => {
      result.current.increment();
      result.current.increment();
    });
    expect(result.current.count).toBe(12);

    act(() => {
      result.current.reset();
    });
    expect(result.current.count).toBe(10);
  });
});
```

## 🎭 Playwright E2E 测试

### Playwright 配置

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';
import path from 'path';

export default defineConfig({
  testDir: './e2e',

  // 全局设置
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : 4,

  // 报告配置
  reporter: [
    ['html', { outputFolder: 'e2e-results/playwright-report' }],
    ['json', { outputFile: 'e2e-results/test-results.json' }],
    ['junit', { outputFile: 'e2e-results/junit-results.xml' }],
    process.env.CI ? ['github'] : ['list']
  ],

  // 全局设置
  use: {
    // 基础URL
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:3000',

    // 截图配置
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'on-first-retry',

    // 视口配置
    viewport: { width: 1280, height: 720 },

    // 忽略HTTPS错误
    ignoreHTTPSErrors: true,

    // 用户代理
    userAgent: 'Playwright E2E Tests',

    // 时区
    timezoneId: 'America/New_York',

    // 语言
    locale: 'en-US'
  },

  // 项目配置
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    // 移动设备测试
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },

    // 平板测试
    {
      name: 'Tablet',
      use: { ...devices['iPad Pro'] },
    },

    // 视觉回归测试
    {
      name: 'visual-regression',
      use: { ...devices['Desktop Chrome'] },
      testMatch: '**/*.visual.spec.ts',
    }
  ],

  // 开发服务器
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },

  // 输出目录
  outputDir: 'e2e-results/test-results/',
});
```

### E2E 测试示例

```typescript
// e2e/user-journey.spec.ts
import { test, expect } from '@playwright/test';
import { HomePage } from './pages/HomePage';
import { ProductPage } from './pages/ProductPage';
import { CartPage } from './pages/CartPage';
import { CheckoutPage } from './pages/CheckoutPage';

test.describe('Complete User Journey', () => {
  let homePage: HomePage;
  let productPage: ProductPage;
  let cartPage: CartPage;
  let checkoutPage: CheckoutPage;

  test.beforeEach(async ({ page }) => {
    homePage = new HomePage(page);
    productPage = new ProductPage(page);
    cartPage = new CartPage(page);
    checkoutPage = new CheckoutPage(page);

    // 设置测试数据
    await page.goto('/');
  });

  test('user can complete full purchase journey', async ({ page }) => {
    // 1. 浏览首页
    await expect(homePage.logo).toBeVisible();
    await expect(homePage.searchBox).toBeVisible();

    // 2. 搜索产品
    await homePage.searchFor('laptop');
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible();

    // 3. 点击第一个产品
    await page.locator('[data-testid="product-card"]').first().click();
    await expect(productPage.productTitle).toBeVisible();

    // 4. 添加到购物车
    await productPage.addToCart();
    await expect(productPage.addToCartNotification).toBeVisible();

    // 5. 查看购物车
    await productPage.goToCart();
    await expect(cartPage.cartItems).toHaveCount(1);

    // 6. 开始结账
    await cartPage.proceedToCheckout();
    await expect(checkoutPage.checkoutForm).toBeVisible();

    // 7. 填写结账信息
    await checkoutPage.fillShippingInformation({
      email: 'test@example.com',
      firstName: 'John',
      lastName: 'Doe',
      address: '123 Test St',
      city: 'Test City',
      zipCode: '12345'
    });

    // 8. 选择支付方式
    await checkoutPage.selectPaymentMethod('credit-card');
    await checkoutPage.fillPaymentInformation({
      cardNumber: '4242424242424242',
      expiryDate: '12/25',
      cvv: '123'
    });

    // 9. 提交订单
    await checkoutPage.placeOrder();

    // 10. 验证订单确认
    await expect(page.locator('[data-testid="order-confirmation"]')).toBeVisible();
    await expect(page.locator('[data-testid="order-number"]')).toContainText('ORD-');
  });

  test('user can save products to wishlist', async ({ page }) => {
    // 搜索并查看产品
    await homePage.searchFor('headphones');
    await page.locator('[data-testid="product-card"]').first().click();

    // 添加到愿望清单
    await productPage.addToWishlist();
    await expect(productPage.wishlistButton).toHaveClass(/added/);

    // 查看愿望清单
    await homePage.goToWishlist();
    await expect(page.locator('[data-testid="wishlist-items"]')).toHaveCount(1);
  });

  test('search functionality works correctly', async ({ page }) => {
    // 测试搜索建议
    await homePage.typeInSearch('lap');
    await expect(page.locator('[data-testid="search-suggestions"]')).toBeVisible();

    // 测试搜索结果
    await homePage.searchFor('laptop');
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible();

    // 测试搜索过滤器
    await homePage.applySearchFilter('brand', 'Dell');
    await expect(page.locator('[data-testid="applied-filters"]')).toContainText('Dell');

    // 测试排序
    await homePage.sortBy('price-low-high');
    const prices = await page.locator('[data-testid="product-price"]').allTextContents();
    const numericPrices = prices.map(p => parseFloat(p.replace(/[^0-9.]/g, '')));

    // 验证价格升序
    for (let i = 1; i < numericPrices.length; i++) {
      expect(numericPrices[i]).toBeGreaterThanOrEqual(numericPrices[i - 1]);
    }
  });
});

// e2e/pages/HomePage.ts
export class HomePage {
  constructor(public page: Page) {}

  get logo() {
    return this.page.locator('[data-testid="logo"]');
  }

  get searchBox() {
    return this.page.locator('[data-testid="search-input"]');
  }

  get searchButton() {
    return this.page.locator('[data-testid="search-button"]');
  }

  async searchFor(query: string) {
    await this.searchBox.fill(query);
    await this.searchButton.click();
    await this.page.waitForSelector('[data-testid="search-results"]');
  }

  async typeInSearch(query: string) {
    await this.searchBox.fill(query);
  }

  async applySearchFilter(filterType: string, value: string) {
    await this.page.locator(`[data-testid="filter-${filterType}"]`).click();
    await this.page.locator(`[data-testid="filter-option-${value}"]`).click();
  }

  async sortBy(sortOption: string) {
    await this.page.locator('[data-testid="sort-dropdown"]').click();
    await this.page.locator(`[data-testid="sort-${sortOption}"]`).click();
  }

  async goToWishlist() {
    await this.page.locator('[data-testid="wishlist-link"]').click();
  }
}

// e2e/visual-regression.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Visual Regression Tests', () => {
  test('homepage visual layout', async ({ page }) => {
    await page.goto('/');

    // 等待页面完全加载
    await page.waitForLoadState('networkidle');

    // 截取完整页面截图
    await expect(page).toHaveScreenshot('homepage-full.png');

    // 截取特定组件截图
    const header = page.locator('[data-testid="header"]');
    await expect(header).toHaveScreenshot('header.png');

    const heroSection = page.locator('[data-testid="hero-section"]');
    await expect(heroSection).toHaveScreenshot('hero-section.png');
  });

  test('product page visual layout', async ({ page }) => {
    await page.goto('/products/laptop-123');
    await page.waitForLoadState('networkidle');

    // 测试不同状态
    await expect(page).toHaveScreenshot('product-page.png');

    // 添加到购物车后
    await page.locator('[data-testid="add-to-cart"]').click();
    await expect(page).toHaveScreenshot('product-page-added-to-cart.png');
  });

  test('responsive design', async ({ page }) => {
    await page.goto('/');

    // 测试不同视口
    const viewports = [
      { width: 375, height: 667 },  // Mobile
      { width: 768, height: 1024 }, // Tablet
      { width: 1280, height: 720 }, // Desktop
      { width: 1920, height: 1080 } // Large Desktop
    ];

    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await page.waitForLoadState('networkidle');
      await expect(page).toHaveScreenshot(`responsive-${viewport.width}x${viewport.height}.png`);
    }
  });
});
```

## 🎭 MSW API 模拟

### MSW 配置

```typescript
// src/test/mocks/handlers.ts
import { http, HttpResponse } from 'msw';
import { delay } from 'msw';

// 模拟API响应数据
const mockProducts = [
  {
    id: '1',
    name: 'Laptop Pro',
    price: 1299.99,
    description: 'High-performance laptop',
    category: 'electronics'
  },
  {
    id: '2',
    name: 'Wireless Mouse',
    price: 29.99,
    description: 'Ergonomic wireless mouse',
    category: 'accessories'
  }
];

const mockUser = {
  id: '1',
  name: 'John Doe',
  email: 'john@example.com',
  avatar: 'https://example.com/avatar.jpg'
};

// API handlers
export const handlers = [
  // 产品相关API
  http.get('/api/products', async ({ request }) => {
    await delay(500); // 模拟网络延迟

    const url = new URL(request.url);
    const category = url.searchParams.get('category');
    const search = url.searchParams.get('search');

    let filteredProducts = mockProducts;

    if (category) {
      filteredProducts = filteredProducts.filter(p => p.category === category);
    }

    if (search) {
      filteredProducts = filteredProducts.filter(p =>
        p.name.toLowerCase().includes(search.toLowerCase())
      );
    }

    return HttpResponse.json({
      products: filteredProducts,
      total: filteredProducts.length
    });
  }),

  http.get('/api/products/:id', async ({ params }) => {
    await delay(300);

    const product = mockProducts.find(p => p.id === params.id);

    if (!product) {
      return new HttpResponse(null, { status: 404 });
    }

    return HttpResponse.json(product);
  }),

  // 用户认证API
  http.post('/api/auth/login', async ({ request }) => {
    await delay(1000);

    const { email, password } = await request.json() as {
      email: string;
      password: string;
    };

    if (email === 'test@example.com' && password === 'password') {
      return HttpResponse.json({
        user: mockUser,
        token: 'mock-jwt-token'
      });
    }

    return new HttpResponse(
      JSON.stringify({ error: 'Invalid credentials' }),
      { status: 401 }
    );
  }),

  http.get('/api/user/profile', () => {
    return HttpResponse.json(mockUser);
  }),

  // 购物车API
  http.post('/api/cart/items', async ({ request }) => {
    await delay(200);

    const { productId, quantity } = await request.json();

    return HttpResponse.json({
      id: Date.now().toString(),
      productId,
      quantity,
      addedAt: new Date().toISOString()
    });
  }),

  http.get('/api/cart', () => {
    return HttpResponse.json({
      items: [
        {
          id: '1',
          productId: '1',
          quantity: 1,
          product: mockProducts[0]
        }
      ],
      total: 1299.99
    });
  }),

  // 错误处理
  http.get('/api/error', () => {
    return new HttpResponse(null, { status: 500 });
  }),

  http.get('/api/slow', async () => {
    await delay(5000); // 5秒延迟
    return HttpResponse.json({ message: 'Slow response' });
  })
];

// src/test/mocks/server.ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);

// src/test/setup.ts
import '@testing-library/jest-dom';
import { server } from './mocks/server';

// 启动mock服务器
beforeAll(() => server.listen());

// 每个测试后重置handlers
afterEach(() => server.resetHandlers());

// 测试完成后关闭服务器
afterAll(() => server.close());
```

### 组件测试中的MSW使用

```typescript
// src/test/components/ProductCard/ProductCard.test.tsx
import { describe, it, expect, beforeAll, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { server } from '@/test/mocks/server';
import { HttpResponse } from 'msw';
import { ProductCard } from '@/components/ProductCard/ProductCard';

describe('ProductCard Component', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());

  it('should display product information', async () => {
    render(<ProductCard productId="1" />);

    await waitFor(() => {
      expect(screen.getByText('Laptop Pro')).toBeInTheDocument();
      expect(screen.getByText('$1299.99')).toBeInTheDocument();
      expect(screen.getByText('High-performance laptop')).toBeInTheDocument();
    });
  });

  it('should handle add to cart', async () => {
    const user = userEvent.setup();
    render(<ProductCard productId="1" />);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /add to cart/i })).toBeInTheDocument();
    });

    await user.click(screen.getByRole('button', { name: /add to cart/i }));

    await waitFor(() => {
      expect(screen.getByText(/added to cart/i)).toBeInTheDocument();
    });
  });

  it('should handle loading state', () => {
    render(<ProductCard productId="1" />);

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('should handle error state', async () => {
    server.use(
      http.get('/api/products/:id', () => {
        return new HttpResponse(null, { status: 404 });
      })
    );

    render(<ProductCard productId="999" />);

    await waitFor(() => {
      expect(screen.getByText(/product not found/i)).toBeInTheDocument();
    });
  });
});
```

## 📊 测试报告和CI/CD集成

### GitHub Actions 配置

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [20.x, 22.x]

    steps:
    - uses: actions/checkout@v4

    - name: Setup Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run linting
      run: npm run lint

    - name: Run type checking
      run: npm run type-check

    - name: Run unit tests
      run: npm run test:unit -- --coverage

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage/lcov.info
        flags: unittests
        name: codecov-umbrella

  e2e:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20.x'
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Install Playwright browsers
      run: npx playwright install --with-deps

    - name: Build application
      run: npm run build

    - name: Run E2E tests
      run: npx playwright test

    - name: Upload E2E test results
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: playwright-report
        path: e2e-results/
        retention-days: 30

  visual-regression:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'

    steps:
    - uses: actions/checkout@v4

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20.x'
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Install Playwright browsers
      run: npx playwright install --with-deps

    - name: Build application
      run: npm run build

    - name: Run visual regression tests
      run: npx playwright test --project=visual-regression

    - name: Upload visual regression results
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: visual-regression-report
        path: e2e-results/
        retention-days: 30
```

## 🔄 文档交叉引用

### 相关文档
- 📄 **[样式工具](./02-styling-tools.md)**: 测试样式组件和CSS-in-JS解决方案
- 📄 **[包管理器](./03-package-managers.md)**: 测试依赖管理和包版本控制
- 📄 **[调试工具](./04-debugging-tools.md)**: 测试环境调试和问题排查
- 📄 **[渲染优化](../performance-optimization/01-rendering-optimization.md)**: 测试驱动性能优化
- 📄 **[打包优化](../performance-optimization/02-bundle-optimization.md)**: 测试代码分割和打包策略

### 参考章节
- 📖 **[Vitest配置](#vitest-单元测试配置)**: 单元测试环境搭建
- 📖 **[React Testing Library](#react-testing-library-组件测试)**: 组件测试最佳实践
- 📖 **[Playwright配置](#playwright-e2e测试)**: 端到端测试设置
- 📖 **[MSW配置](#msw-api模拟)**: API模拟和集成测试

---

## 📝 总结

### 核心要点回顾
1. **测试金字塔**: 单元测试(70%) → 组件测试(20%) → E2E测试(10%)的合理分配策略
2. **Vitest优势**: 快速执行、TypeScript原生支持、与Vite生态无缝集成
3. **RTL理念**: 测试用户行为而非实现细节，模拟真实用户交互场景
4. **Playwright能力**: 跨浏览器E2E测试、视觉回归测试、API测试一体化
5. **MSW价值**: 完整的API模拟解决方案，支持各种网络状态和错误场景

### 学习成果检查
- [ ] 能够配置Vitest测试环境并编写有效的单元测试
- [ ] 掌握React Testing Library的最佳实践和测试模式
- [ ] 熟练使用Playwright进行端到端测试和视觉回归测试
- [ ] 能够使用MSW进行API模拟和集成测试
- [ ] 理解CI/CD集成流程和测试报告配置

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
- **Vitest**: [官方文档](https://vitest.dev/) - 快速、现代化的测试框架
- **React Testing Library**: [官方文档](https://testing-library.com/docs/react-testing-library/intro/) - React组件测试库
- **Playwright**: [官方文档](https://playwright.dev/) - 现代化E2E测试框架
- **MSW**: [官方文档](https://mswjs.io/) - API模拟和拦截库

### 快速参考
- **Jest迁移**: [从Jest迁移到Vitest](https://vitest.dev/guide/migration.html) - 迁移指南
- **测试最佳实践**: [Testing Best Practices](https://kentcdodds.com/blog/common-testing-mistakes) - 常见测试错误避免
- **Playwright vs Cypress**: [对比分析](https://www.browserstack.com/guide/playwright-vs-cypress) - 工具选择参考

---

**文档状态**: ✅ 已完成 | 🚧 进行中 | 📋 计划中
**最后更新**: 2026年9月
**版本**: v1.0.0