# 端到端测试指南 (End-to-End Testing Guide)

> **PHP开发者视角**: 从Selenium到Playwright的转变，了解现代E2E测试工具和最佳实践。

## 端到端测试基础

### 什么是E2E测试

端到端测试（End-to-End Testing）是模拟真实用户操作，从头到尾测试整个应用程序的测试方法。在Next.js中，E2E测试主要用于：

- 验证完整的用户流程
- 测试跨页面导航
- 验证表单提交和数据持久化
- 测试认证和授权流程
- 验证响应式设计和跨浏览器兼容性

### E2E测试的价值

1. **真实用户体验**: 模拟真实用户的操作行为
2. **跨系统测试**: 验证前端、后端、数据库的完整集成
3. **回归测试**: 确保新功能不会破坏现有功能
4. **关键业务流程**: 验证核心业务场景的正确性
5. **自动化测试**: 减少手动测试的工作量

## Playwright设置和配置

### 1. 安装和配置

```bash
# 安装Playwright
npm install -D @playwright/test

# 安装浏览器
npx playwright install

# 安装VS Code扩展（可选）
code --install-extension ms-playwright.playwright
```

### 2. 配置文件

```typescript
// playwright.config.ts
import { defineConfig, devices } from "@playwright/test"

export default defineConfig({
  testDir: "./__tests__/e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"] },
    },
    {
      name: "webkit",
      use: { ...devices["Desktop Safari"] },
    },
    {
      name: "Mobile Chrome",
      use: { ...devices["Pixel 5"] },
    },
    {
      name: "Mobile Safari",
      use: { ...devices["iPhone 12"] },
    },
  ],

  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
  },
})
```

### 3. 全局设置

```typescript
// __tests__/e2e/fixtures/auth.ts
import { test as base } from "@playwright/test"

type AuthFixtures = {
  authenticatedPage: (user?: { email: string; password: string }) => Promise<void>
}

export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ page }, use) => {
    const authenticate = async (user = { email: "test@example.com", password: "password123" }) => {
      await page.goto("/login")
      await page.fill('input[type="email"]', user.email)
      await page.fill('input[type="password"]', user.password)
      await page.click('button[type="submit"]')
      await page.waitForURL("/dashboard")
    }

    await use(authenticate)
  },
})

export { expect } from "@playwright/test"
```

## 基础E2E测试

### 1. 首页测试

```typescript
// __tests__/e2e/homepage.spec.ts
import { test, expect } from "../fixtures/auth"

test.describe("首页功能测试", () => {
  test("应该正确加载首页", async ({ page }) => {
    await page.goto("/")

    // 验证标题
    await expect(page).toHaveTitle(/My App/)

    // 验证导航栏
    await expect(page.locator("nav")).toBeVisible()
    await expect(page.locator("text=首页")).toBeVisible()
    await expect(page.locator("text=关于")).toBeVisible()
    await expect(page.locator("text=联系")).toBeVisible()

    // 验证主要内容
    await expect(page.locator("h1")).toBeVisible()
    await expect(page.locator("text=欢迎来到")).toBeVisible()
  })

  test("应该正确导航到其他页面", async ({ page }) => {
    await page.goto("/")

    // 点击关于链接
    await page.click("text=关于")
    await expect(page).toHaveURL("/about")
    await expect(page.locator("text=关于我们")).toBeVisible()

    // 返回首页
    await page.click("text=首页")
    await expect(page).toHaveURL("/")
  })

  test("应该在移动设备上显示汉堡菜单", async ({ page }) => {
    // 模拟移动设备
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto("/")

    // 验证汉堡菜单可见
    await expect(page.locator("button[aria-label='菜单']")).toBeVisible()

    // 点击汉堡菜单
    await page.click("button[aria-label='菜单']")
    await expect(page.locator("nav")).toBeVisible()
    await expect(page.locator("text=首页")).toBeVisible()
  })
})
```

### 2. 用户注册流程测试

```typescript
// __tests__/e2e/auth/register.spec.ts
import { test, expect } from "@playwright/test"

test.describe("用户注册流程", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/register")
  })

  test("应该成功注册新用户", async ({ page }) => {
    // 填写注册表单
    await page.fill('input[name="name"]', "测试用户")
    await page.fill('input[name="email"]', "newuser@example.com")
    await page.fill('input[name="password"]', "password123")
    await page.fill('input[name="confirmPassword"]', "password123")
    await page.fill('input[name="age"]', "25")

    // 提交表单
    await page.click('button[type="submit"]')

    // 验证重定向到登录页面
    await expect(page).toHaveURL("/login")
    await expect(page.locator("text=注册成功！")).toBeVisible()
  })

  test("应该验证必填字段", async ({ page }) => {
    // 尝试提交空表单
    await page.click('button[type="submit"]')

    // 验证错误消息
    await expect(page.locator("text=姓名至少需要2个字符")).toBeVisible()
    await expect(page.locator("text=请输入有效的邮箱地址")).toBeVisible()
    await expect(page.locator("text=密码至少需要6个字符")).toBeVisible()
  })

  test("应该验证邮箱格式", async ({ page }) => {
    await page.fill('input[name="email"]', "invalid-email")
    await page.click('button[type="submit"]')

    await expect(page.locator("text=请输入有效的邮箱地址")).toBeVisible()
  })

  test("应该验证密码匹配", async ({ page }) => {
    await page.fill('input[name="password"]', "password123")
    await page.fill('input[name="confirmPassword"]', "different123")
    await page.click('button[type="submit"]')

    await expect(page.locator("text=密码不匹配")).toBeVisible()
  })

  test("应该拒绝重复的邮箱", async ({ page }) => {
    // 先注册一个用户
    await page.fill('input[name="name"]', "用户1")
    await page.fill('input[name="email"]', "duplicate@example.com")
    await page.fill('input[name="password"]', "password123")
    await page.fill('input[name="confirmPassword"]', "password123")
    await page.fill('input[name="age"]', "25")
    await page.click('button[type="submit"]')

    // 等待重定向
    await page.waitForURL("/login")

    // 返回注册页面
    await page.goto("/register")

    // 尝试使用相同邮箱注册
    await page.fill('input[name="name"]', "用户2")
    await page.fill('input[name="email"]', "duplicate@example.com")
    await page.fill('input[name="password"]', "password123")
    await page.fill('input[name="confirmPassword"]', "password123")
    await page.fill('input[name="age"]', "30")
    await page.click('button[type="submit"]')

    await expect(page.locator("text=邮箱已被使用")).toBeVisible()
  })
})
```

### 3. 用户登录流程测试

```typescript
// __tests__/e2e/auth/login.spec.ts
import { test, expect } from "@playwright/test"

test.describe("用户登录流程", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login")
  })

  test("应该成功登录", async ({ page }) => {
    await page.fill('input[type="email"]', "test@example.com")
    await page.fill('input[type="password"]', "password123")
    await page.click('button[type="submit"]')

    await expect(page).toHaveURL("/dashboard")
    await expect(page.locator("text=欢迎回来")).toBeVisible()
  })

  test("应该显示错误消息当凭据无效时", async ({ page }) => {
    await page.fill('input[type="email"]', "invalid@example.com")
    await page.fill('input[type="password"]', "wrongpassword")
    await page.click('button[type="submit"]')

    await expect(page.locator("text=邮箱或密码错误")).toBeVisible()
  })

  test("应该验证必填字段", async ({ page }) => {
    await page.click('button[type="submit"]')

    await expect(page.locator("text=请输入邮箱")).toBeVisible()
    await expect(page.locator("text=请输入密码")).toBeVisible()
  })

  test("应该支持记住我功能", async ({ page }) => {
    await page.fill('input[type="email"]', "test@example.com")
    await page.fill('input[type="password"]', "password123")
    await page.check('input[name="remember"]')
    await page.click('button[type="submit"]')

    await expect(page).toHaveURL("/dashboard")

    // 验证localStorage中保存了登录状态
    const localStorage = await page.evaluate(() => {
      return window.localStorage.getItem("auth-token")
    })
    expect(localStorage).not.toBeNull()
  })

  test("应该支持OAuth登录", async ({ page }) => {
    // 点击GitHub登录按钮
    await page.click('button:has-text("使用GitHub登录")')

    // 等待重定向到GitHub
    await expect(page).toHaveURL(/github\.com/)

    // 注意：真实的OAuth测试需要模拟OAuth提供者
    // 这里只是验证重定向是否正确
  })
})
```

## 高级E2E测试场景

### 1. 博客系统完整流程测试

```typescript
// __tests__/e2e/blog/blog-workflow.spec.ts
import { test, expect } from "../fixtures/auth"

test.describe("博客系统完整流程", () => {
  test.beforeEach(async ({ authenticatedPage }) => {
    // 使用认证的fixture
    await authenticatedPage()
  })

  test("应该完成创建、编辑、删除博客的完整流程", async ({ page }) => {
    // 1. 导航到博客管理页面
    await page.goto("/dashboard/posts")
    await expect(page.locator("text=我的博客")).toBeVisible()

    // 2. 创建新博客
    await page.click('button:has-text("新建博客")')
    await expect(page).toHaveURL("/dashboard/posts/new")

    // 填写博客表单
    await page.fill('input[name="title"]', "测试博客标题")
    await page.fill('textarea[name="content"]', "这是一篇测试博客的内容...")

    // 添加标签
    await page.fill('input[placeholder="添加标签"]', "React")
    await page.press('input[placeholder="添加标签"]', "Enter")
    await page.fill('input[placeholder="添加标签"]', "Next.js")
    await page.press('input[placeholder="添加标签"]', "Enter")

    // 发布博客
    await page.click('button:has-text("发布")')

    // 验证创建成功
    await expect(page.locator("text=博客发布成功！")).toBeVisible()
    await expect(page).toHaveURL("/dashboard/posts")

    // 3. 验证博客在列表中显示
    await expect(page.locator("text=测试博客标题")).toBeVisible()

    // 4. 编辑博客
    await page.click('text=测试博客标题')
    await page.waitForURL(/\/dashboard\/posts\/\d+\/edit/)

    await page.fill('input[name="title"]', "更新后的博客标题")
    await page.fill('textarea[name="content"]', "这是更新后的博客内容...")

    await page.click('button:has-text("更新")')

    await expect(page.locator("text=博客更新成功！")).toBeVisible()

    // 5. 查看博客详情
    await page.goto("/blog")
    await expect(page.locator("text=更新后的博客标题")).toBeVisible()
    await page.click('text=更新后的博客标题')

    await expect(page).toHaveURL(/\/blog\/.+/)
    await expect(page.locator("text=这是更新后的博客内容...")).toBeVisible()

    // 6. 添加评论
    await page.fill('textarea[name="comment"]', "这是一条测试评论")
    await page.click('button:has-text("发表评论")')

    await expect(page.locator("text=这是一条测试评论")).toBeVisible()

    // 7. 返回仪表板删除博客
    await page.goto("/dashboard/posts")
    await page.click('text=更新后的博客标题')
    await page.waitForURL(/\/dashboard\/posts\/\d+\/edit/)

    await page.click('button:has-text("删除")')

    // 确认删除
    await page.click('button:has-text("确认删除")')

    await expect(page.locator("text=博客删除成功！")).toBeVisible()
    await expect(page.locator("text=更新后的博客标题")).not.toBeVisible()
  })
})
```

### 2. 电商购物流程测试

```typescript
// __tests__/e2e/ecommerce/shopping-flow.spec.ts
import { test, expect } from "../fixtures/auth"

test.describe("电商购物流程", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/")
  })

  test("应该完成完整的购物流程", async ({ page }) => {
    // 1. 浏览商品
    await expect(page.locator("text=热门商品")).toBeVisible()

    // 点击第一个商品
    await page.click('.product-card:first-child')
    await expect(page).toHaveURL(/\/products\/.+/)

    // 2. 查看商品详情
    await expect(page.locator("h1")).toBeVisible()
    await expect(page.locator("text=加入购物车")).toBeVisible()

    // 3. 选择商品选项
    await page.selectOption('select[name="size"]', "M")
    await page.selectOption('select[name="color"]', "blue")

    // 4. 添加到购物车
    await page.click('button:has-text("加入购物车")')
    await expect(page.locator("text=商品已添加到购物车")).toBeVisible()

    // 5. 继续购物
    await page.click('button:has-text("继续购物")')
    await page.goto("/")

    // 6. 添加第二个商品
    await page.click('.product-card:nth-child(2)')
    await page.click('button:has-text("加入购物车")')

    // 7. 查看购物车
    await page.click('text=购物车')
    await expect(page).toHaveURL("/cart")

    // 验证购物车商品数量
    await expect(page.locator(".cart-item")).toHaveCount(2)

    // 8. 更新商品数量
    await page.fill('.cart-item:first-child input[type="number"]', "2")
    await page.click('button:has-text("更新")')

    // 验证总价更新
    const totalPrice = await page.locator(".total-price").textContent()
    expect(totalPrice).toContain("¥")

    // 9. 结账
    await page.click('button:has-text("结账")')

    // 需要登录
    await page.click('text=登录')
    await page.fill('input[type="email"]', "test@example.com")
    await page.fill('input[type="password"]', "password123")
    await page.click('button[type="submit"]')

    // 10. 填写收货地址
    await expect(page).toHaveURL("/checkout")
    await page.fill('input[name="fullName"]', "测试用户")
    await page.fill('input[name="address"]', "测试地址123号")
    await page.fill('input[name="city"]', "测试城市")
    await page.fill('input[name="zipCode"]', "123456")
    await page.fill('input[name="phone"]', "13800138000")

    // 11. 选择支付方式
    await page.click('input[value="credit_card"]')

    // 12. 提交订单
    await page.click('button:has-text("提交订单")')

    // 13. 验证订单成功
    await expect(page).toHaveURL("/order-success")
    await expect(page.locator("text=订单提交成功！")).toBeVisible()
    await expect(page.locator("text=订单号：")).toBeVisible()

    // 14. 查看订单详情
    const orderNumber = await page.locator(".order-number").textContent()
    await page.click('button:has-text("查看订单详情")')

    await expect(page).toHaveURL(`/orders/${orderNumber}`)
    await expect(page.locator("text=订单状态：待处理")).toBeVisible()
  })
})
```

### 3. 用户资料管理测试

```typescript
// __tests__/e2e/profile/profile-management.spec.ts
import { test, expect } from "../fixtures/auth"

test.describe("用户资料管理", () => {
  test.beforeEach(async ({ authenticatedPage }) => {
    await authenticatedPage()
  })

  test("应该更新用户资料", async ({ page }) => {
    await page.goto("/profile")

    // 点击编辑资料按钮
    await page.click('button:has-text("编辑资料")')

    // 更新个人信息
    await page.fill('input[name="name"]', "更新后的姓名")
    await page.fill('input[name="bio"]', "这是更新后的个人简介")
    await page.fill('input[name="location"]', "北京")
    await page.fill('input[name="website"]', "https://example.com")

    // 保存更改
    await page.click('button:has-text("保存")')

    await expect(page.locator("text=资料更新成功！")).toBeVisible()

    // 验证更新后的信息
    await expect(page.locator("text=更新后的姓名")).toBeVisible()
    await expect(page.locator("text=这是更新后的个人简介")).toBeVisible()
    await expect(page.locator("text=北京")).toBeVisible()
    await expect(page.locator('a[href="https://example.com"]')).toBeVisible()
  })

  test("应该上传头像", async ({ page }) => {
    await page.goto("/profile")

    // 点击更换头像
    await page.click('button:has-text("更换头像")')

    // 模拟文件上传
    const fileInput = await page.locator('input[type="file"]')
    await fileInput.setInputFiles("./__tests__/fixtures/avatar.jpg")

    // 等待上传完成
    await expect(page.locator("text=头像上传成功！")).toBeVisible()

    // 验证头像已更新
    const avatar = await page.locator(".user-avatar img")
    expect(await avatar.getAttribute("src")).toContain("avatar.jpg")
  })

  test("应该更改密码", async ({ page }) => {
    await page.goto("/profile/settings")

    // 点击更改密码
    await page.click('button:has-text("更改密码")')

    // 填写密码表单
    await page.fill('input[name="currentPassword"]', "password123")
    await page.fill('input[name="newPassword"]', "newpassword123")
    await page.fill('input[name="confirmPassword"]', "newpassword123")

    // 提交更改
    await page.click('button:has-text("更改密码")')

    await expect(page.locator("text=密码更改成功！")).toBeVisible()

    // 使用新密码重新登录
    await page.click('button:has-text("退出登录")')
    await page.click('button:has-text("确认")')

    await page.goto("/login")
    await page.fill('input[type="email"]', "test@example.com")
    await page.fill('input[type="password"]', "newpassword123")
    await page.click('button[type="submit"]')

    await expect(page).toHaveURL("/dashboard")
  })
})
```

## 数据驱动测试

### 1. 参数化测试

```typescript
// __tests__/e2e/data-driven/registration-data.spec.ts
import { test, expect } from "@playwright/test"

const testUsers = [
  {
    name: "用户A",
    email: "usera@example.com",
    password: "password123",
    age: "25",
    expectedSuccess: true,
  },
  {
    name: "用户B",
    email: "userb@example.com",
    password: "password123",
    age: "30",
    expectedSuccess: true,
  },
  {
    name: "",
    email: "invalid-email",
    password: "123",
    age: "15",
    expectedSuccess: false,
  },
]

test.describe("参数化注册测试", () => {
  for (const userData of testUsers) {
    test(`应该${userData.expectedSuccess ? "成功" : "失败"}注册用户: ${userData.name || "无效数据"}`, async ({ page }) => {
      await page.goto("/register")

      await page.fill('input[name="name"]', userData.name)
      await page.fill('input[name="email"]', userData.email)
      await page.fill('input[name="password"]', userData.password)
      await page.fill('input[name="confirmPassword"]', userData.password)
      await page.fill('input[name="age"]', userData.age)

      await page.click('button[type="submit"]')

      if (userData.expectedSuccess) {
        await expect(page).toHaveURL("/login")
        await expect(page.locator("text=注册成功！")).toBeVisible()
      } else {
        await expect(page.locator(".error-message")).toBeVisible()
      }
    })
  }
})
```

### 2. 外部数据文件测试

```typescript
// __tests__/e2e/data-driven/products-data.spec.ts
import { test, expect } from "@playwright/test"
import products from "./fixtures/products.json"

test.describe("商品搜索功能", () => {
  products.forEach((product) => {
    test(`应该找到商品: ${product.name}`, async ({ page }) => {
      await page.goto("/products")

      // 搜索商品
      await page.fill('input[placeholder="搜索商品..."]', product.name)
      await page.press('input[placeholder="搜索商品..."]', "Enter")

      // 验证搜索结果
      await expect(page.locator(`text=${product.name}`)).toBeVisible()
      await expect(page.locator(`text=${product.price}`)).toBeVisible()
    })
  })
})
```

```json
// __tests__/e2e/fixtures/products.json
[
  {
    "name": "iPhone 15 Pro",
    "price": "¥8999",
    "category": "手机"
  },
  {
    "name": "MacBook Pro",
    "price": "¥15999",
    "category": "电脑"
  },
  {
    "name": "AirPods Pro",
    "price": "¥1999",
    "category": "配件"
  }
]
```

## 性能和 accessibility 测试

### 1. 性能测试

```typescript
// __tests__/e2e/performance/page-load.spec.ts
import { test, expect } from "@playwright/test"

test.describe("页面性能测试", () => {
  test("首页应该在合理时间内加载", async ({ page }) => {
    const startTime = Date.now()

    await page.goto("/")

    const loadTime = Date.now() - startTime
    console.log(`首页加载时间: ${loadTime}ms`)

    // 验证关键指标
    const performanceMetrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        firstPaint: performance.getEntriesByType('paint')[0].startTime,
      }
    })

    console.log("性能指标:", performanceMetrics)

    // 断言性能指标
    expect(performanceMetrics.domContentLoaded).toBeLessThan(1000)
    expect(performanceMetrics.loadComplete).toBeLessThan(3000)
    expect(loadTime).toBeLessThan(5000)
  })

  test("图片懒加载应该正常工作", async ({ page }) => {
    await page.goto("/products")

    // 获取所有图片
    const images = await page.locator("img[data-src]").count()
    expect(images).toBeGreaterThan(0)

    // 验证初始状态
    const initialImages = await page.locator("img[src]").count()
    expect(initialImages).toBeLessThan(images)

    // 滚动页面
    await page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight)
    })

    // 等待图片加载
    await page.waitForTimeout(1000)

    // 验证懒加载图片已加载
    const loadedImages = await page.locator("img[src]").count()
    expect(loadedImages).toBeGreaterThanOrEqual(images)
  })
})
```

### 2. Accessibility 测试

```typescript
// __tests__/e2e/accessibility/accessibility.spec.ts
import { test, expect } from "@playwright/test"
import { createHtmlReport } from "axe-html-reporter"

test.describe("无障碍测试", () => {
  test("应该符合WCAG标准", async ({ page }) => {
    await page.goto("/")

    // 注入axe-core
    await page.addScriptTag({
      url: "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.2/axe.min.js",
    })

    // 运行axe测试
    const results = await page.evaluate(async () => {
      return await (window as any).axe.run(document, {
        reporter: "v2",
      })
    })

    // 生成报告
    await createHtmlReport({
      results: results,
      options: {
        projectKey: "my-app",
      },
    })

    // 验证没有严重错误
    const violations = results.violations.filter(
      (violation: any) => violation.impact === "serious" || violation.impact === "critical"
    )

    if (violations.length > 0) {
      console.error("无障碍问题:", violations)
    }

    expect(violations).toHaveLength(0)
  })

  test("键盘导航应该正常工作", async ({ page }) => {
    await page.goto("/")

    // 使用Tab键导航
    await page.keyboard.press("Tab")

    // 验证焦点移动
    let focusedElement = await page.evaluate(() => document.activeElement?.tagName)
    expect(focusedElement).toBe("A") // 通常第一个可聚焦元素是链接

    // 继续Tab导航
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press("Tab")
      focusedElement = await page.evaluate(() => document.activeElement?.tagName)
      expect(["A", "BUTTON", "INPUT"]).toContain(focusedElement)
    }

    // 测试Enter键
    await page.keyboard.press("Enter")

    // 验证导航结果
    await expect(page).not.toHaveURL("/") // 应该已经导航到其他页面
  })

  test("应该支持屏幕阅读器", async ({ page }) => {
    await page.goto("/")

    // 验证ARIA标签
    const nav = await page.locator("nav[aria-label]")
    expect(await nav.count()).toBeGreaterThan(0)

    // 验证图片有alt文本
    const images = await page.locator("img:not([alt=''])")
    const totalImages = await page.locator("img").count()
    expect(await images.count()).toBe(totalImages)

    // 验证表单标签
    const formLabels = await page.locator("label").count()
    const formInputs = await page.locator("input, textarea, select").count()
    expect(formLabels).toBeGreaterThan(0)

    // 每个输入都应该有对应的标签
    const unlabeledInputs = await page.locator(
      "input:not([id]), input:not([aria-label]), textarea:not([id]), textarea:not([aria-label]), select:not([id]), select:not([aria-label])"
    ).count()
    expect(unlabeledInputs).toBe(0)
  })
})
```

## API测试集成

### 1. API E2E测试

```typescript
// __tests__/e2e/api/api-testing.spec.ts
import { test, expect } from "@playwright/test"
import { apiRequest } from "../../helpers/api"

test.describe("API E2E测试", () => {
  test("应该通过API完成用户管理流程", async ({ request }) => {
    // 1. 创建用户
    const createUserResponse = await apiRequest(request, {
      method: "POST",
      endpoint: "/api/users",
      data: {
        name: "API测试用户",
        email: "api-test@example.com",
        password: "password123",
        age: 25,
      },
    })

    expect(createUserResponse.status()).toBe(201)
    const userData = await createUserResponse.json()
    expect(userData.name).toBe("API测试用户")

    // 2. 获取用户列表
    const getUsersResponse = await apiRequest(request, {
      method: "GET",
      endpoint: "/api/users",
    })

    expect(getUsersResponse.status()).toBe(200)
    const usersData = await getUsersResponse.json()
    expect(usersData.users.some((user: any) => user.id === userData.id)).toBe(true)

    // 3. 更新用户
    const updateUserResponse = await apiRequest(request, {
      method: "PUT",
      endpoint: `/api/users/${userData.id}`,
      data: {
        name: "更新的API用户",
        bio: "通过API更新的用户",
      },
    })

    expect(updateUserResponse.status()).toBe(200)
    const updatedUserData = await updateUserResponse.json()
    expect(updatedUserData.name).toBe("更新的API用户")

    // 4. 删除用户
    const deleteUserResponse = await apiRequest(request, {
      method: "DELETE",
      endpoint: `/api/users/${userData.id}`,
    })

    expect(deleteUserResponse.status()).toBe(200)

    // 5. 验证用户已删除
    const verifyDeleteResponse = await apiRequest(request, {
      method: "GET",
      endpoint: `/api/users/${userData.id}`,
    })

    expect(verifyDeleteResponse.status()).toBe(404)
  })
})
```

```typescript
// __tests__/helpers/api.ts
import { APIRequestContext } from "@playwright/test"

export interface ApiRequestOptions {
  method: "GET" | "POST" | "PUT" | "DELETE"
  endpoint: string
  data?: any
  headers?: Record<string, string>
}

export async function apiRequest(
  request: APIRequestContext,
  options: ApiRequestOptions
) {
  const { method, endpoint, data, headers = {} } = options

  const requestHeaders = {
    "Content-Type": "application/json",
    ...headers,
  }

  const requestOptions: any = {
    method,
    headers: requestHeaders,
  }

  if (data && method !== "GET") {
    requestOptions.data = data
  }

  return await request.get(`/api${endpoint}`, requestOptions)
}
```

## 测试报告和CI/CD集成

### 1. 自定义报告器

```typescript
// playwright-reporter.js
const { HTMLReporter } = require("@playwright/test/reporter")

class CustomReporter {
  onBegin(config, suite) {
    console.log(`开始执行测试: ${suite.allTests().length} 个测试用例`)
  }

  onTestBegin(test) {
    console.log(`开始测试: ${test.title}`)
  }

  onTestEnd(test, result) {
    console.log(`测试结束: ${test.title} - ${result.status}`)
  }

  onEnd(result) {
    console.log(`测试完成: ${result.status}`)
    console.log(`通过: ${result.passed}`)
    console.log(`失败: ${result.failed}`)
    console.log(`跳过: ${result.skipped}`)
  }
}

module.exports = CustomReporter
```

### 2. GitHub Actions配置

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "18"

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright browsers
        run: npx playwright install --with-deps

      - name: Build application
        run: npm run build

      - name: Start application
        run: npm start &
        env:
          NODE_ENV: production

      - name: Wait for application
        run: npx wait-on http://localhost:3000

      - name: Run E2E tests
        run: npx playwright test

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test-results/
          retention-days: 30
```

## 测试最佳实践

### 1. 测试设计原则

```typescript
// 好的测试示例
test("用户应该能够成功登录", async ({ page }) => {
  // Arrange (准备)
  await page.goto("/login")

  // Act (行动)
  await page.fill('input[type="email"]', "test@example.com")
  await page.fill('input[type="password"]', "password123")
  await page.click('button[type="submit"]')

  // Assert (断言)
  await expect(page).toHaveURL("/dashboard")
  await expect(page.locator("text=欢迎回来")).toBeVisible()
})

// 不好的测试示例
test("测试登录", async ({ page }) => {
  await page.goto("/login")
  await page.fill('input[type="email"]', "test@example.com")
  await page.fill('input[type="password"]', "password123")
  await page.click('button[type="submit"]')
  // 缺少断言
})
```

### 2. 页面对象模式

```typescript
// __tests__/e2e/pages/LoginPage.ts
export class LoginPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto("/login")
  }

  async login(email: string, password: string) {
    await this.page.fill('input[type="email"]', email)
    await this.page.fill('input[type="password"]', password)
    await this.page.click('button[type="submit"]')
  }

  async getErrorMessage() {
    return await this.page.locator(".error-message").textContent()
  }
}

// __tests__/e2e/pages/DashboardPage.ts
export class DashboardPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto("/dashboard")
  }

  async getWelcomeMessage() {
    return await this.page.locator(".welcome-message").textContent()
  }
}

// 使用页面对象
test("用户登录测试", async ({ page }) => {
  const loginPage = new LoginPage(page)
  const dashboardPage = new DashboardPage(page)

  await loginPage.goto()
  await loginPage.login("test@example.com", "password123")

  await expect(page).toHaveURL("/dashboard")
  expect(await dashboardPage.getWelcomeMessage()).toContain("欢迎回来")
})
```

### 3. 测试数据管理

```typescript
// __tests__/e2e/data/TestDataManager.ts
export class TestDataManager {
  private testData = new Map<string, any>()

  setTestData(key: string, data: any) {
    this.testData.set(key, data)
  }

  getTestData(key: string) {
    return this.testData.get(key)
  }

  clearTestData() {
    this.testData.clear()
  }

  async createTestUser(userData: any) {
    const response = await fetch("http://localhost:3000/api/users", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userData),
    })

    const user = await response.json()
    this.setTestData("testUser", user)
    return user
  }

  async cleanupTestData() {
    const user = this.getTestData("testUser")
    if (user) {
      await fetch(`http://localhost:3000/api/users/${user.id}`, {
        method: "DELETE",
      })
    }
    this.clearTestData()
  }
}
```

## 总结

通过本指南，我们学习了Next.js项目中端到端测试的各个方面：

### 核心概念
- E2E测试的定义和价值
- Playwright工具的安装和配置
- 测试环境的设置和管理

### 测试类型
- 基础页面功能测试
- 用户认证流程测试
- 完整业务流程测试
- 数据驱动测试
- 性能和无障碍测试

### 高级技术
- 页面对象模式
- 测试数据管理
- API测试集成
- 自定义报告器
- CI/CD集成

### 实践技巧
- 测试设计原则
- 并行测试优化
- 测试稳定性提升
- 调试技巧

### 从PHP开发者角度
- 从Selenium到Playwright的转变
- 前端E2E测试的特殊考虑
- 现代测试工具的优势

## 🔗 相关资源链接

### 官方资源
- [Playwright 官方文档](https://playwright.dev/)
- [Playwright 测试指南](https://playwright.dev/docs/writing-tests)
- [Playwright 页面对象模式](https://playwright.dev/docs/pom)
- [Playwright CI/CD 集成](https://playwright.dev/docs/ci)

### 技术文章
- [Playwright vs Cypress 对比](https://playwright.dev/docs/why-playwright#comparisons)
- [现代E2E测试最佳实践](https://kentcdodds.com/blog/write-tests)
- [页面对象模式详解](https://martinfowler.com/bliki/PageObject.html)
- [测试数据管理策略](https://playwright.dev/docs/test-data)

### 工具和资源
- [Playwright VS Code扩展](https://marketplace.visualstudio.com/items?itemName=ms-playwright.playwright)
- [Playwright HTML报告](https://playwright.dev/docs/test-reporters#html-reporter)
- [Axe Core 无障碍测试](https://www.deque.com/axe/)
- [Testcontainers 集成](https://playwright.dev/docs/docker)

## 📚 模块内相关文档

### 同模块相关文档
- [单元测试指南](./01-unit-testing.md) - 学习单元测试和E2E测试的配合使用

### 相关知识模块
- [框架相关模块](../frameworks/03-full-stack-patterns.md) - 全栈应用的完整E2E测试策略
- [部署相关模块](../deployment/03-ci-cd-pipelines.md) - CI/CD流水线中的E2E测试自动化
- [部署相关模块](../deployment/04-monitoring-analytics.md) - E2E测试的监控和报告集成

### 基础前置知识
- [JavaScript 异步编程](../../../00-javascript-foundation/advanced/03-async-programming.md) - 异步操作测试的基础知识
- [浏览器渲染原理](../../../01-react-foundation/advanced/06-browser-rendering.md) - 理解浏览器行为对E2E测试的影响
- [React Hooks 完全指南](../../../01-react-foundation/advanced/03-react-hooks-deep-dive.md) - React组件在E2E测试中的行为

---

## ✨ 总结

### 核心技术要点
1. **Playwright框架**: 现代E2E测试工具的配置和高级特性
2. **测试策略设计**: 从用户角度设计真实的业务流程测试
3. **页面对象模式**: 提高测试可维护性和复用性的设计模式
4. **数据驱动测试**: 参数化测试和外部数据文件的使用
5. **CI/CD集成**: 自动化测试执行和报告系统

### 学习成果自检
- [ ] 理解E2E测试的价值和应用场景
- [ ] 掌握Playwright的配置和核心API使用
- [ ] 能够设计并实现完整的用户流程测试
- [ ] 熟练运用页面对象模式构建可维护的测试
- [ ] 能够集成E2E测试到CI/CD流水线中

---

## 🤝 贡献与反馈

### 贡献指南
欢迎提交Issue和Pull Request来改进本模块内容！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交变更 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

### 反馈渠道
- **问题反馈**: [GitHub Issues](https://github.com/your-username/dev-quest/issues)
- **内容建议**: [Discussion板块](https://github.com/your-username/dev-quest/discussions)
- **技术交流**: 欢迎提交PR或Issue参与讨论

### 贡献者
- Dev Quest Team - 核心内容开发
- 社区贡献者 - 内容完善和纠错

---

**📜 文档版本**: v1.0.0
**📅 最后更新**: 2025年10月
**🏷️ 标签**: `#e2e-testing` `#playwright` `#automation` `#ci-cd` `#page-objects`
**⭐ 推荐指数**: ⭐⭐⭐⭐⭐

**💡 提示**: 本模块专注于现代E2E测试实践，建议结合实际项目进行练习。

**🎯 学习建议**:
- 建议学习周期: 2-3周
- 理论与实践时间比例: 3:7
- 重点掌握Playwright和页面对象模式
- 从简单流程开始，逐步构建复杂业务场景测试