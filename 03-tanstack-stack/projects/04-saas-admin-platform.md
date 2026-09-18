# 生产级项目：SaaS 后台平台

## 分阶段练习与验收

**最小阶段**：先做一份有权限边界的资源列表与表单。

**验收结果**：切换账号或租户后缓存不泄露上一身份数据。

**扩展顺序**：路由、表格、表单只在具体需求出现时组合，避免为集成而集成。

建议保存一份正常输入、一份失败输入、实际输出和对应测试。先完成以上阶段再扩展正文中的完整设计；遇到省略实现或未定义依赖，应按文档上下文补齐，不能把代码片段拼接后当作已经验证的完整工程。

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

- 登录/登出/会话过期全链路，token 安全存储与自动续期
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
  expiresAt: number
}

// 会话就是一条查询：无 token 时禁用
export function useSession() {
  const token = localStorage.getItem('access_token')
  return useQuery({
    queryKey: ['auth', 'session'],
    queryFn: async () => {
      const res = await fetch('/api/me', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.status === 401) throw new Error('UNAUTHORIZED')
      if (!res.ok) throw new Error('会话获取失败')
      return (await res.json()) as Session
    },
    enabled: !!token,
    staleTime: 10 * 60_000,
    retry: false, // 401 不该被重试放大
  })
}

export function useLogout() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => fetch('/api/logout', { method: 'POST' }),
    onSettled: () => {
      localStorage.removeItem('access_token')
      qc.clear() // 登出清空一切缓存，防止下一个用户读到前任数据
    },
  })
}
```

> token 存储的完整权衡（为什么 localStorage 在 XSS 面前不是终点、何时用 HttpOnly Cookie）见 [安全实践](../advanced-topics/security/01-security-practices.md)。

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
    // context.ensureSession 由根路由 beforeLoad 注入（内部与会话查询同源）
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

export const queryClient = new QueryClient({
  queryCache: new QueryCache({
    // 全局兜底：任何查询错误都到这里，页面各自再做细化处理
    onError: (error) => {
      if ((error as Error).message === 'UNAUTHORIZED') {
        window.location.href = '/login' // 会话过期统一跳转
        return
      }
      toast.error((error as Error).message)
    },
  }),
  defaultOptions: {
    queries: { staleTime: 60_000, gcTime: 10 * 60_000, retry: 2 },
  },
})
```

配合 React 19 错误边界兜住渲染期异常；API 层统一封装：

```ts
// src/shared/http.ts —— 携带 token、处理 401、透出业务错误码
export async function http<T>(url: string, init?: RequestInit): Promise<T> {
  const token = localStorage.getItem('access_token')
  const res = await fetch(url, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...init?.headers,
    },
  })
  if (res.status === 401) throw new Error('UNAUTHORIZED')
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.message ?? `请求失败 ${res.status}`)
  }
  return res.json()
}
```

---

## 5. 上线前 checklist

- [ ] **权限**：每个路由有 beforeLoad 守卫；每个写按钮有 IfAllowed
- [ ] **审计**：所有写操作 mutation 的 onSuccess 调用 auditApi.log（谁、何时、改了什么）
- [ ] **缓存**：登出 `qc.clear()`；切换租户同上
- [ ] **错误**：QueryCache.onError 兜底 + 特性级错误边界 + Sentry 上报
- [ ] **性能**：路由级代码分割（`createFileRoute` 自动 lazy）；大表格虚拟化
- [ ] **交付**：CI 全绿、预览环境冒烟通过、Web Vitals 基线记录

---

## ❓ 常见坑

| 现象 | 原因 | 修复 |
|------|------|------|
| 会话过期后页面白屏 | 401 只在个别 hook 处理 | 收敛到 QueryCache.onError 全局跳转 |
| 登出后新账号看到旧数据 | 缓存未清空 | onSettled 里 `qc.clear()` |
| viewer 角色能点导出按钮 | 只做了路由级守卫 | 补按钮级 IfAllowed |
| 深链分享后 404 | 守卫未 await ensureSession | beforeLoad 全部 await |

---

## 🔗 相关文档

- 📄 **[生态协作](../frameworks/03-ecosystem-integration.md)** - 四件套协作基础
- 📄 **[协作看板](../projects/03-collaborative-kanban.md)** - 实时特性可直接平移进本平台
- 📄 **[安全实践](../advanced-topics/security/01-security-practices.md)** - 认证与 XSS/CSRF 完整论述
- 📄 **[缓存架构](../advanced-topics/architecture/01-cache-architecture.md)** - 多租户缓存隔离的原理
- 📄 **[CI/CD 流水线](../deployment/01-ci-cd-pipelines.md)** / **[Vercel 部署](../deployment/02-vercel-deployment.md)** - 交付链路
- 📄 **[可观测性](../deployment/03-observability.md)** - Sentry 与 Web Vitals 落地


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
