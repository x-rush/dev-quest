# 端到端测试：Playwright

> **文档简介**: 用 Playwright 验证真实浏览器中的完整用户旅程：登录、表格分页、错误恢复，并覆盖"仅生产构建才会出现"的问题。
>
> **目标读者**: 需要为 Query 项目建立上线前验收防线的开发者
>
> **前置知识**: [集成测试](./03-integration-testing.md)、[CI/CD 流水线](../deployment/01-ci-cd-pipelines.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#playwright` `#e2e` `#端到端` `#验收` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 完成后你将能够

- 配置 Playwright 自动起本地服务并跑浏览器矩阵
- 复用登录态（storageState）避免每用例重复登录
- 用网络拦截模拟"后端挂了"的极端场景

> E2E 的定位：数量少、价值高——只测关键用户旅程，细节行为交给下层测试。

---

## 1. 安装与配置

```bash
npm install -D @playwright/test
npx playwright install chromium
```

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'retain-on-failure', // 失败自动留轨迹，回放排查
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile', use: { ...devices['iPhone 14'] } },
  ],
  webServer: {
    command: 'npm run dev', // 也可 npm run build && npm run preview —— E2E 建议对生产构建跑
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
})
```

**生产构建建议**：E2E 跑 `vite preview`（构建产物），才能暴露 minify、tree-shaking、环境变量注入等问题。

---

## 2. 登录态复用

登录慢且幂等——做一次，处处复用：

```ts
// e2e/auth.setup.ts
import { test as setup, expect } from '@playwright/test'

const authFile = 'e2e/.auth/user.json'

setup('authenticate', async ({ page }) => {
  await page.goto('/login')
  await page.getByLabel('邮箱').fill('demo@example.com')
  await page.getByLabel('密码').fill('demo-password')
  await page.getByRole('button', { name: '登录' }).click()
  await expect(page).toHaveURL('/dashboard')
  await page.context().storageState({ path: authFile }) // 保存 cookie + localStorage
})
```

```ts
// playwright.config.ts 追加 projects
export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /auth\.setup\.ts/ },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], storageState: 'e2e/.auth/user.json' },
      dependencies: ['setup'],
    },
  ],
})
```

---

## 3. 关键用户旅程

```ts
// e2e/dashboard.spec.ts
import { test, expect } from '@playwright/test'

test.describe('数据看板', () => {
  test('翻页后 URL 与表格同步，后退可回', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page.getByRole('table')).toBeVisible()

    await page.getByRole('button', { name: '下一页' }).click()
    await expect(page).toHaveURL(/page=2/)
    await expect(page.getByText('第 2 页')).toBeVisible()

    await page.goBack()
    await expect(page).toHaveURL(/page=1/)
  })

  test('搜索筛选缩小结果并重置页码', async ({ page }) => {
    await page.goto('/dashboard?page=3')
    await page.getByPlaceholder('搜索姓名/邮箱…').fill('alice')
    await page.getByPlaceholder('搜索姓名/邮箱…').blur()

    await expect(page).toHaveURL(/q=alice/)
    await expect(page).toHaveURL(/page=1/) // 筛选后页码重置
  })
})
```

### 网络拦截：测试错误恢复

```ts
// e2e/error-recovery.spec.ts
test('接口 500 时展示错误并可恢复', async ({ page }) => {
  // 拦截后端：只对这一个测试强制失败（MSW worker 也可在此复用）
  await page.route('**/api/users?**', (route) => route.fulfill({ status: 500 }))

  await page.goto('/dashboard')
  await expect(page.getByRole('alert')).toContainText('加载失败')

  // 解除拦截后点击重试，恢复数据
  await page.unroute('**/api/users?**')
  await page.getByRole('button', { name: '重试' }).click()
  await expect(page.getByRole('table')).toBeVisible()
})
```

### 缓存行为验证（Query 特有）

```ts
test('返回列表页命中缓存不闪烁', async ({ page }) => {
  await page.goto('/dashboard')
  await expect(page.getByRole('table')).toBeVisible()

  await page.getByRole('link', { name: '用户详情' }).first().click()
  await page.goBack()

  // staleTime 内返回：表格立即可见（无 loading 骨架）——缓存命中的可观测证据
  await expect(page.getByRole('table')).toBeVisible()
  await expect(page.getByText('加载中…')).toHaveCount(0)
})
```

---

## 4. CI 集成要点

- E2E 最慢，放流水线最后一级，仅 lint/test/build 全绿后执行
- 用 `--shard=2/2` 分片并行缩短时长（GitHub Actions matrix）
- 失败产物（trace.zip、截图、视频）作为 artifact 上传，本地 `npx playwright show-trace` 回放
- 预览环境部署后对 preview URL 跑冒烟子集（PR 验收）

---

## 🎨 最佳实践速查

E2E 优先覆盖用户风险高的完整旅程，例如登录后创建记录并在刷新后看到它；字段的详细排列组合可放在更快的测试层。通过 role/label 查找控件能靠近用户操作，但仍需额外验证键盘与读屏体验。

大多数 CI 用例应使用受控数据和隔离服务，减少第三方波动；支付等真实集成可另设有授权的沙箱契约测试。失败时保存页面、请求和日志证据，先定位原因，不把无限重试当修复。

---

## 🔗 相关文档

- 📄 **[集成测试](./03-integration-testing.md)** - 组件层细粒度验证
- 📄 **[Mock 服务](./02-mocking-server.md)** - E2E 也可复用 MSW handlers
- 📄 **[CI/CD 流水线](../deployment/01-ci-cd-pipelines.md)** - E2E 的流水线位置
- 📄 **[Vercel 部署](../deployment/02-vercel-deployment.md)** - 预览环境冒烟的部署侧
- 📄 **[数据看板](../projects/02-data-dashboard.md)** - 本文被测页面来源


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
