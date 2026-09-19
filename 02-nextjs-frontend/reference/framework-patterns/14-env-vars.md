# 环境变量（.env 加载顺序 / NEXT_PUBLIC_ 内联 / 类型声明）

> **模块**: `02-nextjs-frontend`
> **类型**: 字典条目（可独立查阅，按主题准备前置知识）
> **分类**: `framework-patterns`

## 📌 定义

Next.js 内置 `.env*` 文件加载（写入 `process.env`）与 `NEXT_PUBLIC_` 前缀内联机制。核心规则一句话：**无前缀变量默认不通过公开变量机制自动内联到客户端；带前缀的变量在 `next build` 时被文本替换进客户端 bundle，构建后不再随环境变化**。理解"构建期内联 vs 运行时读取"的边界，是同时保住 secret 安全与多环境部署的关键。

## 📖 语法/签名

### `.env` 文件加载顺序（官方文档原文顺序，命中即停）

| 优先级 | 文件 | 说明 |
|--------|------|------|
| 1 | `process.env` | 已存在的真实环境变量永远最高 |
| 2 | `.env.$(NODE_ENV).local` | 如 `.env.development.local` / `.env.production.local` |
| 3 | `.env.local` | 本机覆盖；**`NODE_ENV=test` 时不加载**（保证测试结果一致） |
| 4 | `.env.$(NODE_ENV)` | 如 `.env.development` / `.env.production` / `.env.test` |
| 5 | `.env` | 全环境兜底 |

> `NODE_ENV` 只允许 `production`/`development`/`test`；不手动设置时 `next dev` 自动给 `development`，其余命令给 `production`。`/src` 目录不影响：`.env*` 只从项目根目录加载。`.env*` 支持多行值与 `$VAR` 引用展开（字面 `$` 用 `\$` 转义）。

### `NEXT_PUBLIC_` 内联机制

```txt
NEXT_PUBLIC_ANALYTICS_ID=abcdefghijk
```

构建时所有 `process.env.NEXT_PUBLIC_ANALYTICS_ID` 的**静态引用**被替换为字面量，打进发给浏览器的 JS。两个边界：`process.env[varName]`、`const env = process.env; env.X` 这类**动态查找不会被内联**；构建后变量冻结——同一 Docker 镜像换环境部署不会生效。

### 类型声明（`env.d.ts`）

```ts
// env.d.ts —— 让 process.env 获得补全与检查
declare namespace NodeJS {
  interface ProcessEnv {
    NEXT_PUBLIC_API_URL: string
    DATABASE_URL: string
  }
}
```

## 💡 示例

### 服务端 secret：无前缀，只在服务器可读

```txt
# .env.local（gitignore，不入库）
DATABASE_URL=postgres://localhost:5432/app
STRIPE_SECRET_KEY=sk_test_xxxxxxxx
NEXT_PUBLIC_ANALYTICS_ID=abcdefghijk
```

```ts
// lib/db.ts —— 服务端模块
import 'server-only'
export function getDbUrl(): string {
  const url = process.env.DATABASE_URL
  if (!url) throw new Error('缺少 DATABASE_URL')
  return url
}
```

### 客户端公开变量：前缀 + 构建期内联

```tsx
'use client'
import Script from 'next/script'
export function Analytics() {
  // 构建后实际变成 const id = 'abcdefghijk'
  const id = process.env.NEXT_PUBLIC_ANALYTICS_ID
  return <Script src={`https://analytics.example.com/t.js?id=${id}`} />
}
```

### 运行时读取：单镜像多环境部署

```tsx
// app/page.tsx —— 请求时求值的环境变量（服务端动态渲染）
import { connection } from 'next/server'

export default async function Component() {
  await connection() // 显式进入动态渲染，env 才在运行时求值
  const value = process.env.RUNTIME_FEATURE_FLAG
  // ...
}
```

### 测试/脚本环境：用 `@next/env` 对齐加载规则

```ts
// vitest.setup.ts / ORM 配置 —— 让测试与 Next.js 读同一批 .env
import { loadEnvConfig } from '@next/env'

loadEnvConfig(process.cwd())
```

## ⚠️ 常见陷阱

- ❌ **以为加了 `NEXT_PUBLIC_` 的变量"服务端也能动态读"**：它两端都可用，但值在**构建时冻结**——构建后再换 `.env` 或平台变量都不生效。✅ 需要运行时可变的配置走服务端读取 + 接口下发的自建 API；`NEXT_PUBLIC_` 只放构建期就确定的公开值。
- ❌ **在客户端代码里读无前缀变量**：`process.env.STRIPE_SECRET_KEY` 在客户端 bundle 中是 `undefined`（不内联），功能静默失效。✅ 服务端专用变量不加前缀、只写服务端模块；确需下发给浏览器的非敏感值才加 `NEXT_PUBLIC_`。
- ❌ **动态查找 `NEXT_PUBLIC_` 变量**：`process.env[varName]` / `const env = process.env` 动态查找不会按公开变量机制内联；浏览器不能借此读取服务器运行时环境。✅ 始终用静态点访问 `process.env.NEXT_PUBLIC_X`。
- ❌ **`.env.local` 提交进仓库或以为测试会加载它**：`.env*.local` 按约定进 `.gitignore`（create-next-app 默认已配）；且 `NODE_ENV=test` 时 `.env.local` 被跳过。✅ 只有不含密钥的共享默认值才可按团队策略提交；推荐维护 .env.example，个人覆盖放 `.env.*.local`。
- ❌ **把 `.env*` 放进 `/src`**：Next.js 只从项目根目录加载 env 文件，`/src` 里的完全被忽略。✅ 固定放根目录。
- ❌ **不声明类型裸用 `process.env.X`**：得到 `string | undefined`（甚至 any），拼 URL 时把 `undefined` 写进请求。✅ 建 `env.d.ts` 键入 `ProcessEnv`，服务端入口处对必填变量做存在性检查（见 [TypeScript 枚举、环境声明与模块系统](../language-concepts/08-ts-declarations-modules.md)）。
- ❌ **在 next.config 里导出后以为运行时还能变**：`next.config` 里的 `env` 键同样是构建期注入。✅ 运行时配置需求用服务端读取。

## 模式不变量

- **凡进入客户端产物的值即视为公开**：机密只存在于服务端读取路径，暴露给浏览器必须是一项显式的、逐项的声明，而非默认（对照无前缀变量仅服务端可用 vs `NEXT_PUBLIC_` 前缀内联）。
- **构建期内联的值在构建后冻结**：打进 bundle 的配置不随部署环境变化，运行时可变的配置必须走服务端运行时读取路径（对照单镜像多环境部署示例、`next.config` 的 `env` 键同为构建期注入）。
- **配置来源按固定优先级命中即停**：真实环境永远压过文件，文件之间按环境粒度从特化到兜底排序，测试环境跳过本机覆盖以保证结果可复现（对照 `.env` 加载顺序表与 `NODE_ENV=test` 跳过 `.env.local`）。
- **文本替换机制要求引用可静态分析**：构建期替换只作用于静态点访问，动态查找不被替换而归于失效（对照 `process.env[varName]` 不会被内联的陷阱）。
- **必需配置在入口处显式验证**：环境变量天然可能缺失，应在服务端入口做存在性检查并补全类型，而不是在使用点静默得到 `undefined`（对照 `getDbUrl()` 存在性检查与 `env.d.ts` 类型声明）。

<!-- full-library-explanation -->
## 用配置来源、读取时机和暴露去向判断安全性

前置是环境变量、构建产物与服务端组件。没有 NEXT_PUBLIC_ 只表示不按该机制自动公开；若把密钥写入 next.config.env、返回给客户端、渲染进 HTML 或打印到公开日志，仍会泄露。给数据库模块加 import 'server-only' 可阻止误导入客户端依赖图，但不能代替审查响应字段。

env.d.ts 把字段声明为 string 不会校验部署配置，反而可能掩盖 undefined。先用启动或请求入口的解析函数检查必需值、URL 协议与允许范围，再把**解析函数返回的配置对象**交给后续代码；这只建立进程内前置条件，不等同于部署配置已经验证。服务端读取也可能发生在预渲染时，只有处于请求时执行的路径才读取该次运行环境。

**练习**：构建时设公开值 A，运行时改为 B，观察静态引用仍显示 A；服务端动态读取的无前缀值应随运行环境变化。测试缺少 DATABASE_URL，预期明确失败而不是发出含 undefined 的请求。使用虚构标记检查客户端 bundle，确认私密标记没有出现；这项检查不能替代完整泄漏审查。

依据：[环境变量](https://nextjs.org/docs/app/guides/environment-variables)、[服务端与客户端边界](https://nextjs.org/docs/app/getting-started/server-and-client-components)。

## 🔗 相关条目

- [路由段配置](./13-route-segment-config.md) —— `connection()` 触发动态渲染的环境求值边界
- [Cache Components 与 "use cache" 指令](./08-caching-patterns.md) —— 缓存键与构建期常量的关系
- [Next.js API 参考](../language-concepts/02-nextjs-api-reference.md) —— `next.config` 全貌
- [TypeScript 枚举、环境声明与模块系统](../language-concepts/08-ts-declarations-modules.md) —— `declare namespace` 语法
- 🌐 **[官方文档：Environment Variables](https://nextjs.org/docs/app/guides/environment-variables)**（本条目行为截至 Next.js 16.3 官方文档）

---
*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
