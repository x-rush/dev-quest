# CI/CD 流水线：GitHub Actions

> **文档简介**: 为 TanStack 前端项目搭建 GitHub Actions 流水线：lint → typecheck → test → build 四道关卡 + 依赖缓存 + E2E 分片并行。
>
> **目标读者**: 要把测试与构建固化为团队防线的开发者
>
> **前置知识**: [单元测试](../testing/01-unit-testing.md)、[端到端测试](../testing/04-e2e-testing.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#github-actions` `#ci` `#cd` `#工程化` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 完成后你将能够

- 编写带依赖缓存的多 Job 流水线
- 把 TanStack ESLint 规则与类型检查设为合并前置条件
- 让 E2E 分片并行、失败产物可下载

---

## 1. 流水线总览

```
push / PR
   │
   ├─ job: lint          # eslint（含 @tanstack/eslint-plugin-query）+ prettier
   ├─ job: typecheck     # tsc --noEmit
   ├─ job: unit          # vitest run --coverage
   └─ job: build         # vite build（产物上传 artifact）
          │
          └─ job: e2e（needs: build）  # playwright 分片并行
```

**设计原则**：前三个 Job 无依赖可并行，全部通过才允许 build；E2E 只对生产构建产物执行。

---

## 2. 主工作流

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true # 新 push 取消旧跑，省额度

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npx eslint . --max-warnings 0

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npx tsc --noEmit

  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npx vitest run --coverage
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage
          path: coverage/

  build:
    runs-on: ubuntu-latest
    needs: [lint, typecheck, unit]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npx vite build
        env:
          VITE_API_BASE_URL: ${{ vars.VITE_API_BASE_URL }}
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  e2e:
    runs-on: ubuntu-latest
    needs: [build]
    strategy:
      fail-fast: false
      matrix:
        shard: [1, 2]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: npx vite build
      - run: npx playwright test --shard=${{ matrix.shard }}/2
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report-${{ matrix.shard }}
          path: playwright-report/
```

---

## 3. TanStack 项目的 CI 专项检查

```bash
# typecheck 额外收益：routeTree.gen.ts 过期会被发现
npx tsc --noEmit

# TanStack Query 键依赖检查（编辑器之外的机器关卡）
npx eslint "src/**/*.{ts,tsx}" --max-warnings 0

# 生成路由树最新化：防止 CI 与本地生成的树不一致
npx tsr generate && git diff --exit-code
```

`routeTree.gen.ts` 的 `git diff --exit-code` 检查值得单独强调：提交过期的路由生成文件，是 TanStack Router 项目最常见的 CI 失败原因。

---

## 4. 环境变量与分支策略

- 构建期变量（`VITE_*`）打进产物，随构建环境注入；运行期变量请走接口下发或部署平台配置
- `main` 分支：跑全量流水线 + E2E；PR：跑除 E2E 外的快速集（用 `paths` 或条件控制）
- 版本发布打 tag 触发 deploy job（对接 [Vercel 部署](./02-vercel-deployment.md)）

---

## 🎨 最佳实践速查

CI 使用与项目一致的包管理器和锁文件；npm 项目用 npm ci，pnpm 项目用冻结锁文件的安装方式。缓存主要减少重复下载，实际收益需比较冷缓存与热缓存运行时间，不能承诺固定倍数。

取消旧任务适用于可重跑的分支检查；正在迁移数据库或切换生产流量的发布不能不加区分地取消。构建前端时验证产物里没有秘密：VITE_ 等注入客户端的变量应按公开数据处理，部署凭据只提供给获授权的发布步骤。

---

## 🔗 相关文档

- 📄 **[开发工具链](../frameworks/04-devtools.md)** - ESLint plugin 的规则清单
- 📄 **[端到端测试](../testing/04-e2e-testing.md)** - e2e job 的内容来源
- 📄 **[Vercel 部署](./02-vercel-deployment.md)** - 构建之后的交付环节
- 📄 **[可观测性](./03-observability.md)** - 上线后的第二道防线
- 📄 **[SaaS 后台](../projects/04-saas-admin-platform.md)** - 本流水线服务的完整项目


<!-- acceptance-exercise -->
## 练习与验收：让四道门禁分别失败一次

在练习分支依次制造 lint 错误、TypeScript 错误、失败测试和构建期缺失公开配置，每次只保留一种问题。预期相应阶段失败且发布 job 不执行。修复后用冻结锁文件重跑，并确认生成的路由树没有未提交差异。验收报告写出每个错误在哪道门被发现；若错误仍能部署，说明依赖关系或条件配置没有形成门禁。

以上是在个人或隔离测试环境中的练习，不是本轮已执行记录；实际运行范围见仓库文档质量报告。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
