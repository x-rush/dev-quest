# Express 5 进阶：错误处理、认证中间件与文件上传

> **文档简介**: 掌握 Express 5 后端最常用的三块工程能力——集中式错误处理中间件、JWT 认证中间件与 multer 文件上传，并给出可直接复用的代码骨架
>
> **目标读者**: 已会搭建基础路由、需要为真实项目补齐健壮性的中级后端开发者
>
> **前置知识**: [Express 基础](01-express-basics.md)、TypeScript 泛型与类型扩展、JWT 基本概念

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#express` `#error-handling` `#auth` `#file-upload` |
| **更新日期** | `2026年9月` |

错误传播模型的概念解释见 [`../basics/06-error-handling.md`](../basics/06-error-handling.md)，本文聚焦 Express 层的落地写法。

## 🎯 本节目标

- 实现覆盖全站、async 安全的集中式错误处理中间件
- 编写可复用、类型安全的 JWT 认证中间件
- 用 multer 实现受控的文件上传（类型/大小限制）

## 1. 集中式错误处理中间件

**Express 5 的关键改进**：路由处理器 `throw` 或 reject 的 Promise 会自动转发给错误中间件，不再需要 `express-async-errors` 或手工 `next(err)`。

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
// src/middleware/error-handler.ts —— 必须注册在所有路由之后
import type { Request, Response, NextFunction } from 'express';
import { HttpError } from '../lib/http-error.js';
import { ZodError } from 'zod';

export function errorHandler(err: unknown, _req: Request, res: Response, _next: NextFunction) {
  // 注意签名是 4 个参数——参数个数决定 Express 是否识别为错误中间件

  if (err instanceof ZodError) {
    return res.status(422).json({
      error: '请求参数校验失败',
      details: err.flatten().fieldErrors,
    });
  }

  if (err instanceof HttpError) {
    return res.status(err.status).json({ error: err.message, details: err.details });
  }

  // 未知错误：记录堆栈但绝不把内部细节泄漏给客户端
  console.error('[unhandled]', err);
  return res.status(500).json({ error: '服务器内部错误' });
}
```

```typescript
// src/app.ts 挂载（最后一位）
app.use(errorHandler);

// 路由里直接 throw 即可，Express 5 自动接管：
router.get('/items/:id', async (req, res) => {
  const item = await db.item.findUnique({ where: { id: req.params.id } });
  if (!item) throw notFound(`条目 ${req.params.id} 不存在`); // 无需 try/catch
  res.json(item);
});
```

## 2. JWT 认证中间件

```typescript
// src/middleware/auth.ts —— 校验 Bearer Token 并把用户挂到 req 上
import type { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { unauthorized } from '../lib/http-error.js';

export interface TokenPayload {
  sub: string; // 用户 ID
  role: 'user' | 'admin';
}

// 类型扩展：让 req.auth 拥有静态类型（模式详解见 reference 的 TS 模式文档）
declare global {
  namespace Express {
    interface Request {
      auth?: TokenPayload;
    }
  }
}

export function requireAuth(req: Request, _res: Response, next: NextFunction) {
  const header = req.headers.authorization; // 形如 "Bearer eyJhbGci..."
  if (!header?.startsWith('Bearer ')) return next(unauthorized());

  try {
    const token = header.slice(7);
    const secret = process.env.JWT_ACCESS_SECRET;
    if (!secret) throw new Error('缺少 JWT_ACCESS_SECRET');
    req.auth = jwt.verify(token, secret) as TokenPayload; // 验签通过才放行
    next();
  } catch {
    next(unauthorized('令牌无效或已过期'));
  }
}

// 角色守卫：放在 requireAuth 之后按需使用
export const requireRole = (...roles: TokenPayload['role'][]) =>
  (req: Request, _res: Response, next: NextFunction) => {
    if (!req.auth) return next(unauthorized());
    if (!roles.includes(req.auth.role)) return next(new HttpError(403, '权限不足'));
    next();
  };
```

```typescript
// 使用方式
import { requireAuth, requireRole } from './middleware/auth.js';

app.use('/admin', requireAuth, requireRole('admin'), adminRouter);
```

## 3. 文件上传：multer 实战

```bash
pnpm add multer && pnpm add -D @types/multer
```

```typescript
// src/middleware/upload.ts —— 受控的磁盘存储上传
import multer from 'multer';
import { mkdirSync } from 'node:fs';
import path from 'node:path';
import { badRequest } from '../lib/http-error.js';

const UPLOAD_DIR = path.resolve('uploads');
mkdirSync(UPLOAD_DIR, { recursive: true });

export const upload = multer({
  storage: multer.diskStorage({
    destination: (_req, _file, cb) => cb(null, UPLOAD_DIR),
    // 重命名避免路径穿越与覆盖：绝不要直接用用户提供的文件名
    filename: (_req, file, cb) => {
      const ext = path.extname(file.originalname).toLowerCase();
      cb(null, `${Date.now()}-${crypto.randomUUID()}${ext}`);
    },
  }),
  limits: { fileSize: 5 * 1024 * 1024 }, // 单文件上限 5MB
  fileFilter: (_req, file, cb) => {
    const allowed = ['.png', '.jpg', '.jpeg', '.pdf'];
    const ok = allowed.includes(path.extname(file.originalname).toLowerCase());
    cb(ok ? null : badRequest(`仅支持 ${allowed.join(', ')}`), ok);
  },
});
```

```typescript
// 路由中使用：upload.single('file') 对应表单字段名 file
router.post('/avatars', requireAuth, upload.single('file'), (req, res) => {
  if (!req.file) return void res.status(400).json({ error: '缺少文件字段 file' });
  res.status(201).json({
    id: req.file.filename,
    size: req.file.size,
    mimetype: req.file.mimetype,
  });
});
```

multer 抛出的错误会自动进入错误中间件，按需单独识别：

```typescript
// error-handler.ts 中追加
if (err instanceof multer.MulterError) {
  return res.status(413).json({ error: `上传失败: ${err.code}` }); // 如 LIMIT_FILE_SIZE
}
```

## ✅ 最佳实践与陷阱

- ✅ 错误中间件保持 4 参签名且注册在路由之后
- ✅ 用户上传文件一律重命名，禁止拼接原始文件名（路径穿越风险）
- ❌ 重复手工解析已被 `express.json()` 处理过的字段
- ❌ 把 JWT 密钥硬编码——应走环境变量（密钥管理见 [`../advanced-topics/security/01-security-practices.md`](../advanced-topics/security/01-security-practices.md)）

## 🔗 相关文档

- 📖 [Express 5 核心速查](../reference/framework-essentials/01-express-essentials.md) — 中间件与错误处理的条目式字典
- 📄 [错误处理与进程稳定性](../basics/06-error-handling.md) — 错误传播模型与进程级兜底
- 📄 [Node + TypeScript 常用模式](../reference/language-concepts/05-typescript-patterns.md) — Request 类型扩展与泛型处理器
- 📄 [认证服务实战](../projects/02-auth-service.md) — 完整的 JWT + 刷新令牌项目
