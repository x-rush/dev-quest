# 生产级项目：SaaS 后台平台

## 分阶段练习与验收

**最小阶段**：先做一份有权限边界的资源列表与表单。

**验收结果**：切换账号或租户后缓存不泄露上一身份数据。

**扩展顺序**：路由、表格、表单只在具体需求出现时组合，避免为集成而集成。

### 先交付一条有身份边界的数据流

前置验收是 [数据看板](02-data-dashboard.md) 的分页与失败重试已通过，并能解释查询键为什么包含筛选条件。准备两个练习账号：租户 A 的 admin 和租户 B 的 viewer；各自有不同的用户列表。本篇使用 Query v5 / Router v1，Table 与 Form 沿用模块基线；下面的片段需要已配置 Provider、路由树和同源 API 的 React 工程。

第一轮只实现“登录 → 查看本租户用户 → 尝试新建 → 登出”。服务端提供以下契约，先用固定测试数据完成集成，再接真实数据库：

| 请求 | 成功输出 | 失败输出及 UI 行为 |
|---|---|---|
| `POST /api/login`，输入练习账号凭据 | 设置会话 Cookie，返回 204；随后重取会话 | 401 显示登录失败，不进入受保护页 |
| `GET /api/me` | `{ user: { id, name, role }, tenantId, expiresAt }`，expiresAt 为毫秒时间戳 | 401 视为未登录；500 显示可重试错误 |
| `GET /api/tenants/A/users` | 只返回授权租户资源 | 未登录 401；跨租户 403，不能信任 URL 中的 A |
| `POST /api/tenants/A/users` | 201 返回已创建用户 | viewer 得到 403；字段错误 400；不得写入数据 |
| `POST /api/logout` | 服务端撤销会话并清除 Cookie，204 | 网络失败显示重试；不能宣称服务端已登出 |

先使用服务端设置的 `HttpOnly`、`Secure` 会话 Cookie。服务端还需按部署方式配置 SameSite 并校验写请求的 CSRF 防护；这些属性不能由前端代码替代。测试替身只能证明界面接线，不证明权限安全。

验收后依次增加：租户切换 → 表单校验 → 审计查询 → 监控与发布。本文是架构练习路径，标题中的“生产级”是目标，不能凭几个前端守卫判定已可上线。

> **文档简介**: 综合四件套构建生产级 SaaS 管理平台：RBAC 路由守卫、认证流、按特性组织的数据层、错误边界与审计日志，交付可上线的前端架构。
>
> **目标读者**: 已完成前三个项目、需要掌握企业级前端架构的进阶开发者
>
> **前置知识**: [生态协作](../frameworks/03-ecosystem-integration.md)、[协作看板](../projects/03-collaborative-kanban.md)、[安全实践](../advanced-topics/security/01-security-practices.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#实战项目` `#saas` `#rbac` `#架构` `#生产级` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 项目目标

- 登录/登出/会话过期全链路；续期须由后端会话协议单独实现
- RBAC：角色决定"路由能不能进 + 按钮能不能点"
- 数据层按特性分域，键工厂 + 统一错误处理
- 审计日志、操作反馈、灰度发布位一一落地
- **预计时长**：3~5 天

---

## 1. 目录结构：按特性分域

```
src/
├── auth/                    # 认证与授权（全局横切）
│   ├── use-auth.ts          # 登录/登出/会话查询
│   └── permissions.ts       # 角色 → 权限矩阵
├── features/                # 业务特性（每个特性自治）
│   ├── users/
│   │   ├── api.ts           # fetch 函数
│   │   ├── keys.ts          # Query Key 工厂
│   │   ├── hooks.ts         # useXxxQuery / useXxxMutation
│   │   └── routes/          # 该特性的路由文件
│   └── billing/ ...
├── shared/                  # 与业务无关的通用件
└── router.tsx               # 路由组装与 context 注入
```

**原则**：keys.ts 永远只属于一个特性；跨特性依赖只允许"高阶特性引用低阶特性的 keys"，禁止反向。

---

## 2. 认证流：登录、会话、过期

```ts
// src/auth/use-auth.ts
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

export interface Session {
  user: { id: string; name: string; role: 'admin' | 'manager' | 'viewer' }
  tenantId: string
  expiresAt: number
}

// Cookie 是否存在由服务端判断；首次进入应用也必须请求会话。
export function useSession() {
  return useQuery({
    queryKey: ['auth', 'session'],
    queryFn: async ({ signal }): Promise<Session | null> => {
      const res = await fetch('/api/me', { credentials: 'same-origin', signal })
      if (res.status === 401) return null
      if (!res.ok) throw new Error('会话获取失败')
      return (await res.json()) as Session
    },
    staleTime: 0,
    retry: false, // 401 不该被重试放大
  })
}

export function useLogout() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/logout', { method: 'POST', credentials: 'same-origin' })
      if (!res.ok) throw new Error('登出失败，请重试')
    },
    onSuccess: async () => {
      await qc.cancelQueries()
      qc.clear()
      window.location.replace('/login')
    },
  })
}
```

登录成功后也要先取消并清除上一身份的查询，再重新读取会话、进入受保护路由。`staleTime: 0` 不是自动续期定时器；会话到期后的任意 API 都必须重新由服务端判断权限。完整边界见 [安全实践](../advanced-topics/security/01-security-practices.md)。

---

## 3. RBAC 路由守卫

```ts
// src/auth/permissions.ts
const matrix = {
  admin: ['users:read', 'users:write', 'billing:read', 'billing:write'],
  manager: ['users:read', 'users:write', 'billing:read'],
  viewer: ['users:read'],
} as const
export type Permission = (typeof matrix)[keyof typeof matrix][number]
export const can = (role: keyof typeof matrix, p: Permission) =>
  (matrix[role] as readonly string[]).includes(p)
```

```tsx
// src/routes/_protected.users.tsx —— 文件式路由的守卫写法
import { createFileRoute, redirect, notFound } from '@tanstack/react-router'

export const Route = createFileRoute('/_protected/users')({
  beforeLoad: async ({ context }) => {
    // 应用自定义依赖：在 createRootRouteWithContext 的类型与 router context 中注入；不是 Router 内置 API。
    // ensureSession 应复用 /api/me 契约，401 返回 null，网络/500 抛错交给路由错误页。
    const session = await context.ensureSession()
    if (!session) throw redirect({ to: '/login', search: { from: '/users' } })
    if (!can(session.user.role, 'users:read')) throw notFound() // 无权访问按 404 处理，不暴露路径存在性
  },
  component: UsersPage,
})
```

按钮级权限用组件封装，避免 `role === 'admin'` 散落各处：

```tsx
export function IfAllowed({ p, children }: { p: Permission; children: React.ReactNode }) {
  const { data: session } = useSession()
  if (!session || !can(session.user.role, p)) return null
  return <>{children}</>
}

// 用法：<IfAllowed p="users:write"><Button>新建用户</Button></IfAllowed>
```

---

## 4. 数据层规范与统一错误处理

```ts
// src/shared/query-client.ts
import { QueryCache, QueryClient } from '@tanstack/react-query'
import { toast } from '@/shared/toast'
import { HttpError } from '@/shared/http'

export const queryClient = new QueryClient({
  queryCache: new QueryCache({
    // 查询的全局兜底；mutation 要在调用点显示与该操作匹配的反馈。
    onError: (error) => {
      if (error instanceof HttpError && error.status === 401) {
        // 只发起一次导航；路由还应能显示返回地址。
        window.location.replace('/login')
        return
      }
      toast.error(error instanceof Error ? error.message : '请求失败，请稍后重试')
    },
  }),
  defaultOptions: {
    queries: { staleTime: 60_000, gcTime: 10 * 60_000, retry: 2 },
  },
})
```

配合 React 19 错误边界兜住渲染期异常；API 层统一封装：

```ts
// src/shared/http.ts —— JSON 响应专用；204 用独立的无返回值请求函数处理
export class HttpError extends Error {
  constructor(
    readonly status: number,
    message: string,
    readonly code?: string,
  ) {
    super(message)
    this.name = 'HttpError'
  }
}

export async function http<T>(url: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers)
  if (typeof init?.body === 'string' && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  const res = await fetch(url, {
    ...init,
    credentials: 'same-origin',
    headers,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    // status 供重试、路由和会话处理判断；code 是稳定的业务分类，不能靠翻译后的 message 分支。
    throw new HttpError(res.status, body.message ?? `请求失败 ${res.status}`, body.code)
  }
  return res.json()
}
```

错误的归属要分层：`HttpError` 保存可程序化判断的状态和业务码；查询缓存负责没有局部处理的读取失败；表单 mutation 在提交按钮旁显示字段或操作错误；路由错误边界只处理无法渲染该路由的异常。401 的导航逻辑也要避免多个并发请求重复跳转。对于 429、503 或网络异常，是否重试取决于请求是否幂等、服务端的 `Retry-After` 与用户能否安全重复操作，不能由 `retry: 2` 一概决定。

---

## 5. 上线前 checklist

先给用户列表建立键 `['tenant', session.tenantId, 'actor', session.user.id, 'users', filters]`；查询函数仍访问服务端授权后的接口，并将 Query 的 `signal` 传给 `fetch`。切换期间停止挂载旧身份页面，等待正在提交的写操作明确结束，再取消查询、清缓存、取得新会话并刷新路由。清缓存不会撤销已经发出的服务端写入。

| 可复现输入 | 预期结果 | 失败时回查 |
|---|---|---|
| A admin 登录、读取后登出，再 B viewer 登录 | 列表和 Query Devtools 中没有 A 的资源 | 查询键身份作用域、取消请求和清缓存顺序 |
| viewer 手工发送创建请求 | 服务端 403，数据库无新增行 | 服务端授权；隐藏按钮无法修复此问题 |
| 删除 Cookie 后刷新 `/users` | 会话为 null，跳登录；网络断开时显示错误而非伪装未登录 | ensureSession 的 401 与网络错误分流 |
| `/api/logout` 返回 500 | UI 报失败并允许重试，不显示“已退出” | fetch 不会因 HTTP 500 自动 reject |
| 写入成功后前端立刻断网 | 服务端已有审计记录 | 审计必须与服务端业务操作关联，不能依赖 onSuccess |

路由片段中的 `UsersPage`、`can`，以及组件片段中的 `Permission`、`useSession` 需由对应模块导入；`toast` 是项目自定义 UI。先用原生错误文本完成闭环，再接这些组件，不要把占位名称当成库导出。

- [ ] **权限**：受保护路由有 beforeLoad；写按钮有 IfAllowed；服务端逐请求验证身份、租户和权限
- [ ] **审计**：服务端记录写操作主体、租户、资源、结果和时间；前端埋点仅补充体验信息
- [ ] **缓存**：登出 `qc.clear()`；切换租户同上
- [ ] **错误**：查询全局兜底、mutation 局部反馈与路由错误边界职责分开；按 `status` / `code` 而非错误文案分支，并验证并发 401 只导航一次
- [ ] **性能**：按 Router 构建插件的代码分割配置或 `.lazy.tsx` 路由实现拆包，并检查构建产物；单独调用 `createFileRoute` 不保证自动拆包
- [ ] **交付**：CI 全绿、预览环境冒烟通过、Web Vitals 基线记录

---

## ❓ 常见坑

| 现象 | 原因 | 修复 |
|------|------|------|
| 会话过期后页面白屏 | 401 只在个别 hook 处理 | 收敛到 QueryCache.onError 全局跳转 |
| 登出后新账号看到旧数据 | 身份切换顺序或查询键有误 | 成功退出后取消请求并清缓存；键中加入身份与租户 |
| viewer 角色能点导出按钮 | 只做了路由级守卫 | 补按钮级 IfAllowed |
| 深链刷新后 404 | 可能是宿主未配置 SPA 回退，也可能是权限守卫 | 先确认请求是否到达应用，再查 await 会话与角色权限 |

---

## 🔗 相关文档

**下一步与证据**：记录上述五项的账号、请求状态和可见结果；后端权限与审计测试通过后，再进入部署文档。仅静态阅读这些片段不构成生产验证。Query 取消行为可回查[官方请求取消指南](https://tanstack.com/query/latest/docs/framework/react/guides/query-cancellation)，Router context 接线可回查[官方认证路由指南](https://tanstack.com/router/latest/docs/framework/react/guide/authenticated-routes)。

- 📄 **[生态协作](../frameworks/03-ecosystem-integration.md)** - 四件套协作基础
- 📄 **[协作看板](../projects/03-collaborative-kanban.md)** - 实时特性可直接平移进本平台
- 📄 **[安全实践](../advanced-topics/security/01-security-practices.md)** - 认证与 XSS/CSRF 完整论述
- 📄 **[缓存架构](../advanced-topics/architecture/01-cache-architecture.md)** - 多租户缓存隔离的原理
- 📄 **[CI/CD 流水线](../deployment/01-ci-cd-pipelines.md)** / **[Vercel 部署](../deployment/02-vercel-deployment.md)** - 交付链路
- 📄 **[可观测性](../deployment/03-observability.md)** - Sentry 与 Web Vitals 落地


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
