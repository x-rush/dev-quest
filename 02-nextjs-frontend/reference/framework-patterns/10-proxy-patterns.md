# 网络代理模式（proxy.ts）

> **模块**: `02-nextjs-frontend`
> **类型**: 字典条目（无难度门槛）
> **分类**: `framework-patterns`

## 📌 定义

`proxy.ts` 是 App Router 的网络边界约定文件，位于项目根目录（或 `src/` 下），在每个请求被路由匹配之前运行，适合处理重定向、改写 URL、注入请求头、A/B 分流、地域路由等**网络层**关注点。它由 Next.js 16 引入，替代已弃用的 `middleware.ts`：导出函数更名为 `proxy`，运行时固定为 Node.js（不再默认 Edge），命名更清晰地表达"请求代理"而非"中间件"职责。

## 📖 语法/签名

```typescript
// proxy.ts（项目根目录）
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export default function proxy(request: NextRequest) {
  // 登录保护：未认证访问仪表盘时重定向
  if (request.nextUrl.pathname.startsWith('/dashboard')) {
    if (!request.cookies.has('session')) {
      return NextResponse.redirect(new URL('/login', request.url));
    }
  }
  return NextResponse.next();
}

export const config = {
  // matcher：声明代理介入的路径范围
  matcher: ['/dashboard/:path*', '/admin/:path*'],
};
```

与 Next.js 16 配套重命名的配置项：`skipMiddlewareUrlNormalize` → `skipProxyUrlNormalize`。

## 💡 示例

```typescript
// proxy.ts —— 注入请求头 + 地域路由
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export default function proxy(request: NextRequest) {
  const country = request.headers.get('x-vercel-ip-country') ?? 'US';

  if (country === 'CN' && request.nextUrl.pathname === '/') {
    return NextResponse.redirect(new URL('/zh', request.url));
  }

  const response = NextResponse.next();
  response.headers.set('x-request-id', crypto.randomUUID());
  return response;
}
```

## ⚠️ 常见陷阱

- `proxy.ts` **不支持 Edge runtime**（固定 Node.js，不可配置）；确实依赖 Edge 的场景暂可保留 `middleware.ts`（已弃用，未来移除）
- 导出函数必须命名为 `proxy`（或使用默认导出），沿用 `middleware` 函数名不会生效
- 代理中不应做重量级鉴权/业务逻辑——那些属于 route handler、layout 或 Server Action；代理只做网络层分流
- `matcher` 未收窄会导致所有请求（含静态资源）都经过代理，拖慢全站
- 认证会话刷新等"读+写 Cookie"逻辑在代理中运行于 Node.js runtime，注意与 Edge 时代的 API 差异

## 模式不变量

- **网络层关注点与应用层关注点分层**：重定向、URL 改写、请求头注入、分流属于请求代理层；权威鉴权与业务逻辑归属路由处理层，两层职责不得互越（对照 proxy 只做网络层分流、重量级鉴权归 route handler / layout / Server Action 的约束）。
- **每个横切拦截都必须显式声明作用域**：请求级拦截默认面对全部流量，介入范围必须用路径匹配收窄，否则横切成本摊到包括静态资源在内的所有请求上（对照 `matcher` 未收窄拖慢全站的陷阱）。
- **代理层只做凭证存在性门槛，不做权威鉴权**：代理中的会话检查是轻量判断（如凭证是否存在），最终认证决策发生在更内层（对照未认证重定向示例与"代理中不做重量级鉴权"陷阱）。
- **前置拦截层的运行时由框架固定**：每请求拦截代码运行在平台固定的运行时中，编写时不能假设任意后端能力（对照 `proxy.ts` 固定 Node.js runtime、Edge 不可配置）。

## 🔗 相关条目

- [认证流程模式](./07-authentication-flows.md) —— 会话校验在代理与路由层的分工
- [App Router 实战模式](./01-app-router-patterns.md)
- [异步请求 APIs](./09-async-request-apis.md)
