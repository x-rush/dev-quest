# 测试策略与实践 (Testing Strategy & Best Practices)

> **PHP开发者视角**: 从Laravel测试体系到现代前端测试策略的转变，了解如何构建完整的测试体系。

## 测试策略概述

### 什么是测试策略

测试策略是指导项目中所有测试活动的综合性计划，它定义了：

- 测试目标和范围
- 测试类型和方法
- 测试工具和技术
- 测试流程和标准
- 团队职责分工

### 测试金字塔

```
        ^
        |
        |  E2E Tests (5-10%)
        |  (端到端测试)
        |
        |  Integration Tests (15-25%)
        |  (集成测试)
        |
        |  Unit Tests (60-80%)
        |  (单元测试)
        |
        +------------------>
          测试数量/速度
```

## 测试类型选择指南

### 1. 何时使用单元测试

**适用场景**：
- 工具函数的验证
- 组件的渲染逻辑
- 自定义Hooks的状态管理
- 数据验证函数
- 算法实现

**示例**：
```typescript
// 工具函数
describe("formatCurrency", () => {
  it("应该正确格式化货币", () => {
    expect(formatCurrency(1234.56)).toBe("¥1,234.56")
    expect(formatCurrency(0)).toBe("¥0.00")
    expect(formatCurrency(-100)).toBe("-¥100.00")
  })
})

// React组件渲染
describe("Button Component", () => {
  it("应该渲染正确的变体", () => {
    render(<Button variant="destructive">删除</Button>)
    expect(screen.getByRole("button")).toHaveClass("bg-destructive")
  })
})
```

### 2. 何时使用集成测试

**适用场景**：
- 组件间交互
- 表单提交流程
- 数据流验证
- API集成测试
- 状态管理

**示例**：
```typescript
// 表单集成测试
describe("Registration Form Integration", () => {
  it("应该成功提交注册表单", async () => {
    render(<RegistrationForm />)

    await userEvent.type(screen.getByLabelText(/邮箱/i), "test@example.com")
    await userEvent.type(screen.getByLabelText(/密码/i), "password123")
    await userEvent.click(screen.getByRole("button", { name: /注册/i }))

    await waitFor(() => {
      expect(mockToast.success).toHaveBeenCalledWith("注册成功！")
    })
  })
})
```

### 3. 何时使用E2E测试

**适用场景**：
- 关键业务流程
- 用户认证流程
- 支付流程
- 多页面导航
- 跨系统集成

**示例**：
```typescript
// 完整用户流程
test("应该完成完整的购物流程", async ({ page }) => {
  // 浏览商品
  await page.goto("/products")
  await page.click('.product-card:first-child')

  // 添加到购物车
  await page.click('button:has-text("加入购物车")')

  // 结账流程
  await page.click('button:has-text("结账")')
  await page.fill('input[name="fullName"]', "测试用户")
  await page.click('button:has-text("提交订单")')

  // 验证订单成功
  await expect(page.locator("text=订单提交成功！")).toBeVisible()
})
```

## 测试设计模式

### 1. AAA模式（Arrange-Act-Assert）

```typescript
// 好的AAA模式示例
describe("UserService", () => {
  it("应该创建用户", async () => {
    // Arrange - 准备
    const userData = {
      name: "张三",
      email: "zhangsan@example.com",
      age: 25,
    }

    // Act - 行动
    const user = await userService.createUser(userData)

    // Assert - 断言
    expect(user.id).toBeDefined()
    expect(user.name).toBe(userData.name)
    expect(user.email).toBe(userData.email)
  })
})
```

### 2. Given-When-Then模式

```typescript
// Given-When-Then模式示例
describe("用户登录", () => {
  it("应该使用有效凭据成功登录", () => {
    // Given - 给定条件
    const credentials = {
      email: "test@example.com",
      password: "password123",
    }

    // When - 执行操作
    const result = authService.login(credentials)

    // Then - 验证结果
    expect(result.success).toBe(true)
    expect(result.token).toBeDefined()
  })
})
```

### 3. 页面对象模式（Page Object Model）

```typescript
// 页面对象示例
export class LoginPage {
  constructor(private page: Page) {}

  async navigate() {
    await this.page.goto("/login")
  }

  async fillEmail(email: string) {
    await this.page.fill('input[type="email"]', email)
  }

  async fillPassword(password: string) {
    await this.page.fill('input[type="password"]', password)
  }

  async submit() {
    await this.page.click('button[type="submit"]')
  }

  async getErrorMessage() {
    return await this.page.locator(".error-message").textContent()
  }
}

// 使用页面对象
test("登录失败应该显示错误消息", async ({ page }) => {
  const loginPage = new LoginPage(page)

  await loginPage.navigate()
  await loginPage.fillEmail("invalid@example.com")
  await loginPage.fillPassword("wrongpassword")
  await loginPage.submit()

  const errorMessage = await loginPage.getErrorMessage()
  expect(errorMessage).toContain("邮箱或密码错误")
})
```

## 测试数据管理

### 1. 测试数据工厂

```typescript
// factories/user-factory.ts
export class UserFactory {
  static create(overrides?: Partial<User>): User {
    return {
      id: Math.random().toString(36).substr(2, 9),
      name: "测试用户",
      email: `test-${Math.random()}@example.com`,
      age: 25,
      bio: "这是一个测试用户",
      ...overrides,
    }
  }

  static createMany(count: number, overrides?: Partial<User>): User[] {
    return Array.from({ length: count }, () => this.create(overrides))
  }
}

// 使用工厂
describe("UserRepository", () => {
  it("应该批量创建用户", async () => {
    const users = UserFactory.createMany(5)
    const createdUsers = await userRepository.createMany(users)

    expect(createdUsers).toHaveLength(5)
    createdUsers.forEach(user => {
      expect(user.id).toBeDefined()
    })
  })
})
```

### 2. 测试数据构建器

```typescript
// builders/user-builder.ts
export class UserBuilder {
  private user: Partial<User> = {}

  withName(name: string): UserBuilder {
    this.user.name = name
    return this
  }

  withEmail(email: string): UserBuilder {
    this.user.email = email
    return this
  }

  withAge(age: number): UserBuilder {
    this.user.age = age
    return this
  }

  withBio(bio: string): UserBuilder {
    this.user.bio = bio
    return this
  }

  build(): User {
    return {
      id: Math.random().toString(36).substr(2, 9),
      name: this.user.name || "默认用户",
      email: this.user.email || "default@example.com",
      age: this.user.age || 25,
      bio: this.user.bio || "默认简介",
    }
  }
}

// 使用构建器
describe("UserService", () => {
  it("应该创建用户", async () => {
    const user = new UserBuilder()
      .withName("张三")
      .withEmail("zhangsan@example.com")
      .withAge(30)
      .build()

    const result = await userService.createUser(user)
    expect(result.name).toBe("张三")
    expect(result.email).toBe("zhangsan@example.com")
    expect(result.age).toBe(30)
  })
})
```

### 3. 测试数据清理

```typescript
// helpers/test-database.ts
export class TestDatabase {
  static async setup() {
    // 清理所有表
    await prisma.user.deleteMany()
    await prisma.post.deleteMany()
    await prisma.comment.deleteMany()

    // 创建基础测试数据
    await this.createBaseData()
  }

  static async cleanup() {
    await prisma.user.deleteMany()
    await prisma.post.deleteMany()
    await prisma.comment.deleteMany()
  }

  private static async createBaseData() {
    await prisma.user.create({
      data: {
        name: "测试用户",
        email: "test@example.com",
        age: 25,
      },
    })
  }
}

// 在测试中使用
describe("UserService Integration", () => {
  beforeEach(async () => {
    await TestDatabase.setup()
  })

  afterEach(async () => {
    await TestDatabase.cleanup()
  })

  it("应该能够创建用户", async () => {
    // 测试代码
  })
})
```

## Mock和Stub策略

### 1. Mock的使用场景

```typescript
// API调用Mock
vi.mock("@/lib/api", () => ({
  userService: {
    createUser: vi.fn(),
    getUserById: vi.fn(),
    updateUser: vi.fn(),
  },
}))

// 外部服务Mock
vi.mock("@/lib/email", () => ({
  sendEmail: vi.fn(),
}))

// 第三方库Mock
vi.mock("stripe", () => ({
  default: {
    customers: {
      create: vi.fn(),
    },
  },
}))
```

### 2. Stub的使用场景

```typescript
// 数据库Stub
const stubUserRepository = {
  findById: vi.fn(),
  save: vi.fn(),
  delete: vi.fn(),
}

// 在测试中使用
describe("UserService", () => {
  it("应该找到用户", async () => {
    const expectedUser = { id: "1", name: "张三" }
    stubUserRepository.findById.mockResolvedValue(expectedUser)

    const user = await userService.findById("1")
    expect(user).toEqual(expectedUser)
  })
})
```

### 3. 何时使用真实依赖

```typescript
// 应该使用真实依赖的场景
describe("Database Integration", () => {
  it("应该正确保存数据到数据库", async () => {
    // 使用真实的测试数据库
    const user = await userRepository.create({
      name: "张三",
      email: "zhangsan@example.com",
    })

    const savedUser = await prisma.user.findUnique({
      where: { id: user.id },
    })

    expect(savedUser).toEqual(user)
  })
})
```

## 测试覆盖率策略

### 1. 覆盖率目标设定

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80,
        },
        // 关键模块更高的覆盖率要求
        "./src/lib/utils/**/*": {
          branches: 90,
          functions: 90,
          lines: 90,
          statements: 90,
        },
        // 测试文件排除
        "./src/**/*.test.ts": {
          branches: 0,
          functions: 0,
          lines: 0,
          statements: 0,
        },
      },
    },
  },
})
```

### 2. 覆盖率报告分析

```typescript
// 脚本：生成覆盖率报告
// scripts/generate-coverage-report.ts
import { execSync } from "child_process"
import * as fs from "fs"
import * as path from "path"

export function generateCoverageReport() {
  // 运行测试并生成覆盖率报告
  execSync("npm run test:coverage", { stdio: "inherit" })

  // 读取覆盖率数据
  const coveragePath = path.join(process.cwd(), "coverage", "coverage-final.json")
  const coverageData = JSON.parse(fs.readFileSync(coveragePath, "utf-8"))

  // 分析覆盖率
  const analysis = analyzeCoverage(coverageData)

  // 生成报告
  generateReport(analysis)
}

function analyzeCoverage(data: any) {
  // 实现覆盖率分析逻辑
  return {
    totalLines: 0,
    coveredLines: 0,
    totalFunctions: 0,
    coveredFunctions: 0,
    // ...更多指标
  }
}
```

## CI/CD集成策略

### 1. GitHub Actions配置

```yaml
# .github/workflows/test.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20]

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm run test:unit

      - name: Run integration tests
        run: npm run test:integration

      - name: Run E2E tests
        run: npm run test:e2e

      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info
          flags: unittests
          name: codecov-umbrella
          fail_ci_if_error: true

  quality-gate:
    needs: test
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Check coverage threshold
        run: |
          if [ $(node -e "console.log(require('./coverage/coverage-summary.json').total.lines.pct)") -lt 80 ]; then
            echo "Coverage too low!"
            exit 1
          fi

      - name: Run linting
        run: npm run lint

      - name: Run type checking
        run: npm run type-check
```

### 2. 测试环境配置

```yaml
# docker-compose.test.yml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=test
      - DATABASE_URL=postgresql://test:test@db:5432/test_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./coverage:/app/coverage

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: test_db
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  test-runner:
    build: .
    command: npm run test:ci
    environment:
      - NODE_ENV=test
      - DATABASE_URL=postgresql://test:test@db:5432/test_db
    depends_on:
      - db
      - redis
    volumes:
      - ./coverage:/app/coverage
```

## 测试性能优化

### 1. 并行测试执行

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    // 启用并行测试
    pool: "threads",
    poolOptions: {
      threads: {
        singleThread: false,
        isolate: true,
      },
    },
    // 设置工作线程数
    maxWorkers: process.env.CI ? 2 : undefined,
    // 智能文件排序
    sequence: {
      shuffle: true,
      seed: Math.random(),
    },
  },
})
```

### 2. 测试分割和缓存

```typescript
// scripts/split-tests.ts
import * as fs from "fs"
import * as path from "path"

export function splitTests(totalShards: number, shardIndex: number) {
  const testFiles = getAllTestFiles()
  const shardSize = Math.ceil(testFiles.length / totalShards)
  const start = shardIndex * shardSize
  const end = Math.min(start + shardSize, testFiles.length)

  return testFiles.slice(start, end)
}

function getAllTestFiles() {
  const testDir = path.join(process.cwd(), "__tests__")
  const files = fs.readdirSync(testDir, { recursive: true })

  return files
    .filter((file): file is string =>
      typeof file === "string" && file.endsWith(".test.ts")
    )
    .map(file => path.join(testDir, file))
}
```

### 3. 测试缓存策略

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    // 启用测试缓存
    cache: {
      dir: "./.vitest/cache",
    },
    // 智能依赖跟踪
    includeTaskLocation: true,
    // 跳过未变更文件的测试
    changed: true,
  },
})
```

## 测试维护策略

### 1. 测试代码重构

```typescript
// 重构前：重复的测试代码
describe("UserForm", () => {
  it("应该验证姓名", async () => {
    render(<UserForm />)
    await userEvent.type(screen.getByLabelText(/姓名/i), "")
    await userEvent.click(screen.getByRole("button", { name: /提交/i }))
    expect(screen.getByText("姓名不能为空")).toBeInTheDocument()
  })

  it("应该验证邮箱", async () => {
    render(<UserForm />)
    await userEvent.type(screen.getByLabelText(/邮箱/i), "invalid")
    await userEvent.click(screen.getByRole("button", { name: /提交/i }))
    expect(screen.getByText("邮箱格式错误")).toBeInTheDocument()
  })
})

// 重构后：提取公共逻辑
describe("UserForm", () => {
  const fillAndSubmitForm = async (formData: Record<string, string>) => {
    render(<UserForm />)

    for (const [field, value] of Object.entries(formData)) {
      const input = screen.getByLabelText(new RegExp(field, "i"))
      await userEvent.type(input, value)
    }

    await userEvent.click(screen.getByRole("button", { name: /提交/i }))
  }

  it("应该验证姓名", async () => {
    await fillAndSubmitForm({ name: "" })
    expect(screen.getByText("姓名不能为空")).toBeInTheDocument()
  })

  it("应该验证邮箱", async () => {
    await fillAndSubmitForm({ email: "invalid" })
    expect(screen.getByText("邮箱格式错误")).toBeInTheDocument()
  })
})
```

### 2. 测试文档化

```typescript
// __tests__/README.md
# 测试文档

## 测试结构
- `__tests__/unit/` - 单元测试
- `__tests__/integration/` - 集成测试
- `__tests__/e2e/` - 端到端测试

## 测试命令
```bash
# 运行所有测试
npm test

# 运行单元测试
npm run test:unit

# 运行集成测试
npm run test:integration

# 运行E2E测试
npm run test:e2e

# 生成覆盖率报告
npm run test:coverage
```

## 测试约定
1. 测试文件命名：`*.test.ts`
2. 测试描述使用中文
3. 使用AAA模式组织测试
4. 每个测试用例应该独立
5. 测试数据应该隔离
```

### 3. 测试监控和报告

```typescript
// scripts/test-monitor.ts
import { execSync } from "child_process"
import * as fs from "fs"

export class TestMonitor {
  static async runTestsAndGenerateReport() {
    const startTime = Date.now()

    try {
      // 运行测试
      execSync("npm run test:ci", { stdio: "inherit" })

      // 生成报告
      const report = {
        duration: Date.now() - startTime,
        timestamp: new Date().toISOString(),
        coverage: this.getCoverageData(),
        testResults: this.getTestResults(),
      }

      // 保存报告
      fs.writeFileSync(
        "test-report.json",
        JSON.stringify(report, null, 2)
      )

      // 发送通知
      await this.sendNotification(report)
    } catch (error) {
      await this.sendErrorNotification(error)
    }
  }

  private static getCoverageData() {
    // 读取覆盖率数据
    const coverageData = JSON.parse(
      fs.readFileSync("coverage/coverage-summary.json", "utf-8")
    )
    return coverageData
  }

  private static getTestResults() {
    // 读取测试结果
    // 实现逻辑...
  }

  private static async sendNotification(report: any) {
    // 发送测试结果通知
    // 实现逻辑...
  }
}
```

## 团队测试策略

### 1. 测试职责分工

```markdown
## 测试职责矩阵

| 角色 | 单元测试 | 集成测试 | E2E测试 |
|------|----------|----------|---------|
| 前端开发 | ✅ 主要负责 | ✅ 主要负责 | ⚠️ 协助 |
| 后端开发 | ✅ 主要负责 | ✅ 主要负责 | ❌ 不负责 |
| QA工程师 | ⚠️ 协助 | ✅ 主要负责 | ✅ 主要负责 |
| DevOps | ❌ 不负责 | ⚠️ 协助 | ✅ 主要负责 |
```

### 2. 测试流程规范

```markdown
## 测试流程

### 开发阶段
1. 编写单元测试（代码覆盖率 > 80%）
2. 编写集成测试
3. 本地运行所有测试

### 代码审查
1. 检查测试覆盖率
2. 检查测试质量
3. 确保测试通过

### CI/CD阶段
1. 自动运行所有测试
2. 检查覆盖率阈值
3. 生成测试报告
4. 部署到测试环境

### 发布阶段
1. 运行完整测试套件
2. 性能测试
3. 安全测试
4. 生产环境部署
```

### 3. 测试培训和知识共享

```typescript
// docs/testing-guide.md
# 测试指南

## 新员工培训
1. 测试基础概念
2. 测试工具使用
3. 测试最佳实践
4. 团队测试规范

## 技能提升
1. 定期测试代码审查
2. 测试技术分享会
3. 测试挑战活动
4. 外部培训参与

## 工具和资源
- 测试框架文档
- 测试模式手册
- 测试案例库
- 常见问题解答
```

## 总结

通过本指南，我们学习了如何构建完整的Next.js测试策略：

### 核心概念
- 测试策略的定义和重要性
- 测试金字塔的应用
- 不同测试类型的选择

### 实践策略
- 测试设计模式
- 测试数据管理
- Mock和Stub的使用
- 覆盖率管理

### 工程实践
- CI/CD集成
- 性能优化
- 测试维护
- 团队协作

### 从PHP开发者角度
- 从Laravel测试体系的转变
- 前端测试的特殊考虑
- 现代测试工具的优势

构建完整的测试策略需要团队的共同努力和持续改进。通过合理的测试策略，可以确保代码质量，提高开发效率，降低维护成本，为用户提供更加稳定可靠的产品体验。