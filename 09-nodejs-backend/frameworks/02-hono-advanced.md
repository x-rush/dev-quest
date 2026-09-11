# Hono 4 进阶：错误处理、认证中间件与文件上传

> **文档简介**: 掌握 Hono 后端最常用的三块工程能力——集中式错误处理（onError 与 HTTPException）、JWT 认证中间件与受控文件上传，并给出可直接复用的代码骨架
>
> **目标读者**: 已会搭建基础路由、需要为真实项目补齐健壮性的中级后端开发者
>
> **前置知识**: [Hono 基础](01-hono-basics.md)、TypeScript 泛型与类型扩展、JWT 基本概念

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#hono` `#error-handling` `#auth` `#file-upload` |
| **更新日期** | `2026年9月` |

错误传播模型的概念解释见 [`../basics/06-error-handling.md`](../basics/06-error-handling.md)，本文聚焦 Hono 层的落地写法。

## 🎯 本节目标

- 用 `app.onError` 实现覆盖全站、async 安全的集中式错误处理
- 编写可复用、类型安全的 JWT 认证中间件与角色守卫
- 用 `c.req.parseBody()` 实现受控的文件上传（类型/大小限制）

## 1. 集中式错误处理：onError

**Hono 的关键设计**：任意中间件或路由处理器中 `throw` 的错误（包括 async 函数 reject 的 Promise）都会自动传播给 `app.onError` 注册的处理器——不需要 Express 式的"四参错误中间件"，也不需要任何 async 包装补丁。

```typescript
// src/lib/http-error.ts —— 携带状态码的业务错误类
export class HttpError extends Error {
  constructor(
    public readonly status: number,
    message: string,
    public readonly details?: unknown, // 可选：字段级校验错误等
  ) {
    super(message);
    this.name = 'HttpError';
  }
}

export const badRequest = (msg: string, details?: unknown) => new HttpError(400, msg, details);
export const unauthorized = (msg = '未认证') => new HttpError(401, msg);
export const notFound = (msg = '资源不存在') => new HttpError(404, msg);
```

```typescript
// src/app.ts —— app.onError：全站唯一的错误出口
import { Hono } from 'hono';
import { ZodError, flattenError } from 'zod';
import { HttpError } from './lib/http-error.js';

const app = new Hono();

app.onError((err, c) => {
  if (err instanceof ZodError) {
    return c.json(
      {
        error: '请求参数校验失败',
        details: flattenError(err).fieldErrors, // Zod 4 顶层 API
      },
      422,
    );
  }

  if (err instanceof HttpError) {
    return c.json({ error: err.message, details: err.details }, err.status);
  }

  // 未知错误：记录堆栈但绝不把内部细节泄漏给客户端
  console.error('[unhandled]', err);
  return c.json({ error: '服务器内部错误' }, 500);
});

// 路由里直接 throw 即可，Hono 自动接管：
app.get('/items/:id', async (c) => {
  const item = await db.item.findUnique({ where: { id: c.req.param('id') } });
  if (!item) throw notFound(`条目 ${c.req.param('id')} 不存在`); // 无需 try/catch
  return c.json(item);
});
```

框架自带的 `HTTPException`（`hono/http-exception`）适合在中间件里快速抛状态码；业务项目通常封装自己的 `HttpError` 携带更丰富的上下文，两者都在 `onError` 中统一收口。

## 2. JWT 认证中间件

### 方式一：内置 jwt 中间件 + Context 变量

`hono/jwt` 是框架内置的认证中间件，验签通过后自动把 payload 写入 Context 变量 `jwtPayload`：

```typescript
// src/app.ts
import { jwt } from 'hono/jwt';

// 只保护部分路由：按路径作用域挂载
app.use('/api/*', async (c, next) => {
  if (c.req.path === '/auth/login') return next(); // 白名单路径
  const auth = jwt({ secret: process.env.JWT_ACCESS_SECRET! });
  return auth(c, next);
});

// 处理器里读取
app.get('/me', (c) => c.json(c.get('jwtPayload')));
```

### 方式二：自定义认证中间件（类型安全）

需要把用户信息挂成强类型、或叠加角色判断时，自写中间件更灵活。类型扩展用模块合并 `ContextVariableMap`（模式详解见 reference 的 TS 模式文档）：

```typescript
// src/middleware/auth.ts —— 校验 Bearer Token 并把用户挂到 Context 上
import type { MiddlewareHandler } from 'hono';
import { verify } from 'hono/jwt';
import { unauthorized } from '../lib/http-error.js';

export interface TokenPayload {
  sub: string; // 用户 ID
  role: 'user' | 'admin';
}

declare module 'hono' {
  interface ContextVariableMap {
    auth?: TokenPayload;
  }
}

export const requireAuth: MiddlewareHandler = async (c, next) => {
  const header = c.req.header('Authorization'); // 形如 "Bearer eyJhbGci..."
  if (!header?.startsWith('Bearer ')) throw unauthorized();

  try {
    const token = header.slice(7);
    const secret = process.env.JWT_ACCESS_SECRET;
    if (!secret) throw new Error('缺少 JWT_ACCESS_SECRET');
    const payload = await verify(token, secret, 'HS256'); // 显式算法，防 alg 混淆
    c.set('auth', payload as TokenPayload); // 验签通过才放行
    await next();
  } catch {
    throw unauthorized('令牌无效或已过期');
  }
};

// 角色守卫：放在 requireAuth 之后按需使用
export const requireRole =
  (...roles: TokenPayload['role'][]): MiddlewareHandler =>
  async (c, next) => {
    const auth = c.get('auth');
    if (!auth) throw unauthorized();
    if (!roles.includes(auth.role)) throw new HttpError(403, '权限不足');
    await next();
  };
```

```typescript
// 使用方式
import { Hono } from 'hono';
import { requireAuth, requireRole } from './middleware/auth.js';

const adminApp = new Hono();
adminApp.use('*', requireAuth, requireRole('admin'));
app.route('/admin', adminApp);
```

## 3. 文件上传：parseBody 实战

Hono 生态没有（也不需要）multer——请求体解析内建在 `c.req.parseBody()` 中，返回 Web 标准 `FormData`，文件对象是标准的 `File`：

```typescript
// src/routes/avatars.ts —— 受控的文件上传
import { Hono } from 'hono';
import { writeFile } from 'node:fs/promises';
import path from 'node:path';
import { bodyLimit } from 'hono/body-limit';
import { badRequest } from '../lib/http-error.js';
import { requireAuth } from '../middleware/auth.js';

const UPLOAD_DIR = path.resolve('uploads');
const ALLOWED = new Set(['.png', '.jpg', '.jpeg', '.pdf']);

export const avatarsApp = new Hono()
  // 请求体大小上限 5MB：解析前拦截，防大 payload 打爆内存
  .use('*', bodyLimit({ maxSize: 5 * 1024 * 1024 }))
  .post('/avatars', requireAuth, async (c) => {
    const body = await c.req.parseBody(); // FormData
    const file = body['file'];            // 对应表单字段名 file

    if (!(file instanceof File)) throw badRequest('缺少文件字段 file');

    const ext = path.extname(file.name).toLowerCase();
    if (!ALLOWED.has(ext)) {
      throw badRequest(`仅支持 ${[...ALLOWED].join(', ')}`);
    }

    // 重命名避免路径穿越与覆盖：绝不要直接用用户提供的文件名
    const savedName = `${Date.now()}-${crypto.randomUUID()}${ext}`;
    await writeFile(path.join(UPLOAD_DIR, savedName), Buffer.from(await file.arrayBuffer()));

    return c.json({ id: savedName, size: file.size, type: file.type }, 201);
  });
```

要点：

- `parseBody()` 只解析 `multipart/form-data`；纯 JSON 用 `c.req.json()`，混用会抛错
- `file instanceof File` 判断必须保留——`parseBody` 对普通文本字段返回 `string`
- `bodyLimit` 是大小防线的第一道闸；类型校验靠扩展名 + 必要时探测 magic bytes

## ✅ 最佳实践与陷阱

- ✅ 错误处理只有 `app.onError` 一个出口；中间件里直接 `throw`，不要 `try/catch` 后吞错
- ✅ 用户上传文件一律重命名，禁止拼接原始文件名（路径穿越风险）
- ❌ 在 `await next()` 之前抛错会让洋葱"内侧"的中间件全部跳过——需要清理逻辑时用 `try/finally` 包住 `next()`
- ❌ 把 JWT 密钥硬编码——应走环境变量（密钥管理见 [`../advanced-topics/security/01-security-practices.md`](../advanced-topics/security/01-security-practices.md)）

## 🔗 相关文档

- 📖 [Hono 核心速查](../reference/framework-essentials/01-hono-essentials.md) — onError/jwt/parseBody 的条目式字典
- 📄 [错误处理与进程稳定性](../basics/06-error-handling.md) — 错误传播模型与进程级兜底
- 📄 [Node + TypeScript 常用模式](../reference/language-concepts/05-typescript-patterns.md) — ContextVariableMap 类型扩展与泛型处理器
- 📄 [认证服务实战](../projects/02-auth-service.md) — 完整的 JWT + 刷新令牌项目
