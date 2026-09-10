# Node + TypeScript 常用模式

> **文档简介**: Node 后端开发中高频的 TypeScript 模式——泛型请求处理器、类型安全环境变量、Express 类型扩展、依赖注入与类型守卫

> **目标读者**: 有 TS 基础、想把 Node 后端代码类型写"严"的开发者

> **前置知识**: TypeScript 泛型基础，[路由与中间件](../../basics/05-http-routing.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐⭐ |
| **标签** | `#TypeScript` `#泛型` `#环境变量` `#类型扩展` |
| **更新日期** | `2026年9月` |

## 1. 类型安全的环境变量

### 定义
启动时集中解析并校验环境变量，导出不可变的强类型配置对象。

### 语法与示例

```ts
// src/lib/env.ts —— Zod 方案（推荐）
import { z } from "zod";

const EnvSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  PORT: z.coerce.number().int().default(3000),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
});

// 启动即校验：缺变量/格式错直接崩溃，而不是运行到一半炸掉
export const env = EnvSchema.parse(process.env);
export type Env = z.infer<typeof EnvSchema>;
```

### 陷阱
- `process.env.X` 类型是 `string | undefined`，散落在代码各处等于放弃检查——**只在一个模块读 env**
- `z.coerce.number()` 注意：`""` 会变成 0，空值场景需先判空

## 2. 泛型请求处理器（类型安全校验中间件）

### 定义
用泛型把"schema 推导出的数据类型"注入 `req`，让 handler 拿到精确类型。

### 语法与示例

```ts
import type { NextFunction, Request, Response } from "express";
import type { z } from "zod";

function validateBody<T extends z.ZodType>(schema: T) {
  return (
    req: Request<unknown, unknown, z.infer<T>>,   // 第三泛型参即 body 类型
    res: Response,
    next: NextFunction,
  ) => {
    const result = schema.safeParse(req.body);
    if (result.success) {
      req.body = result.data;
      next();
    } else {
      next({ status: 400, code: "VALIDATION_ERROR", issues: result.error.issues });
    }
  };
}

// handler 中 req.body 自动收窄为 schema 类型
app.post("/tasks", validateBody(CreateTaskSchema), (req, res) => {
  const { title, status } = req.body;   // title: string; status: "todo"|"doing"|"done"
  res.json({ title, status });
});
```

### 陷阱
- Express 的 `Request` 泛型参数依次是 `Params, ResBody, ReqBody, ReqQuery`——扩展错了位置类型就形同虚设
- 校验中间件里 `next(err)` 传对象而非 Error 实例时，错误中间件要兼容普通对象

## 3. 扩展 Express 类型声明

### 定义
用模块声明合并给 `req.user` 等自定义字段正式类型。

### 语法与示例

```ts
// types/express.d.ts（需包含在 tsconfig 中）
import type { User } from "../src/auth.js";

declare global {
  namespace Express {
    interface Request {
      user?: User;
    }
  }
}

export {};
```

```ts
// 使用处自动获得类型
app.get("/me", requireAuth, (req, res) => {
  res.json(req.user);   // User | undefined，requireAuth 保证非空
});
```

### 陷阱
- `declare global` 的文件必须至少有一个 `import/export`，否则变成脚本文件不生效
- 类型上 `user?: User` 的可空性要靠运行时中间件保证，别撒谎声明为必有值

## 4. 类型守卫与错误处理

### 定义
把 `unknown` 收窄为可用类型的函数，是 try/catch 和外部输入的标准配套。

### 语法与示例

```ts
// 自定义错误 + instanceof 守卫
export class HttpError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
  ) { super(message); }
}

export function isHttpError(e: unknown): e is HttpError {
  return e instanceof HttpError;
}

// 错误中间件中使用
const errorHandler: ErrorRequestHandler = (err, _req, res, _next) => {
  if (isHttpError(err)) {
    res.status(err.status).json({ error: { code: err.code } });
    return;
  }
  res.status(500).json({ error: { code: "INTERNAL_ERROR" } });
};

// Zod 附带的守卫
if (result.error instanceof z.ZodError) { /* 校验错误分支 */ }
```

### 陷阱
- 跨构建产物/多次打包后 `instanceof` 可能失效（不同类副本），可改用 `err.name` 判别
- 谎报的 `e is X` 守卫比没有守卫更危险，守卫逻辑必须与声明严格一致

---

## 🔗 相关文档

- 📄 **[路由与中间件](../../basics/05-http-routing.md)** — 校验中间件的教程式讲解
- 📄 **[现代 JS 语法速查](./01-js-modern-syntax.md)** — 类型守卫与判空语法
- 📄 **[第一个项目](../../basics/08-first-project.md)** — 本页模式的完整落地实例
