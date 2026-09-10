# 路由、中间件与请求校验

> **文档简介**: 掌握 Express 5 路由组织、中间件链的执行模型，以及用 Zod 做类型安全的请求校验

> **目标读者**: 已跑通第一个 Express 服务、准备构建真实 API 的开发者

> **前置知识**: [第一个服务器](./02-first-server.md)，TypeScript 基本类型

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 教程（basics） |
| **难度** | ⭐ |
| **标签** | `#路由` `#中间件` `#Zod` `#请求校验` `#Express5` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- 用 Router 模块化组织路由并提取路径参数
- 解释中间件链的顺序语义与 `next` 的三种用法
- 为接口加上认证、日志等横切关注点
- 用 Zod 校验请求并把解析结果桥接为 TypeScript 类型

## 🔍 路由：方法 + 路径 + 处理器

### 基本路由与路径参数

```ts
import express from "express";

const app = express();

// 路径参数 req.params；查询字符串 req.query
app.get("/posts/:postId/comments", (req, res) => {
  const { postId } = req.params;
  const limit = Number(req.query.limit ?? 10);
  res.json({ postId, limit });
});

// 多种 HTTP 方法
app.post("/posts", (req, res) => res.status(201).json({ id: "new" }));
// Express 5 兜底 404（旧版 "*" 写法已废弃，改用普通中间件）
app.use((req, res) => res.status(404).json({ error: "路由不存在" }));
```

### Router 拆分：真实项目的组织方式

```ts
// src/routes/users.ts（目录含 index.ts 挂载总路由，users/posts 为子路由）
import { Router } from "express";
export const usersRouter = Router();
usersRouter.get("/", listUsers);
usersRouter.get("/:id", getUser);
usersRouter.post("/", createUser);
```

```ts
// src/routes/index.ts —— 总路由聚合，server.ts 中 app.use("/api", apiRouter)
import { Router } from "express";
import { usersRouter } from "./users.js";
import { postsRouter } from "./posts.js";
export const apiRouter = Router();
apiRouter.use("/users", usersRouter);
apiRouter.use("/posts", postsRouter);
```

## 🔍 中间件：请求的流水线

### 执行模型

中间件是 `(req, res, next) => void` 函数，按注册顺序串成链。`next()` 三种用法：

```ts
// 1) next()        → 进入下一个中间件
// 2) next(err)     → 跳过后续普通中间件，直达错误处理中间件
// 3) 不调用 next   → 请求悬挂（响应须在该中间件内结束）
app.use((req, _res, next) => {
  console.log(`${new Date().toISOString()} ${req.method} ${req.url}`);
  next();
});
```

### 常见中间件形态

```ts
// 请求体解析（内置）
app.use(express.json());

// 自定义认证中间件
function requireAuth(req, res, next) {
  const token = req.headers.authorization?.replace("Bearer ", "");
  if (!token) return res.status(401).json({ error: "未认证" });
  req.user = verifyToken(token);   // 给 req 扩展字段
  next();
}

// 作用域挂载：只保护某个路由组
app.use("/api/admin", requireAuth, adminRouter);
// 或路由级
app.get("/me", requireAuth, (req, res) => res.json({ user: req.user }));
```

中间件顺序即语义：`express.json()` 必须在读取 body 的中间件之前；认证必须在校验之前。

## 🛠️ 请求校验：Zod

不校验的接口等于裸奔——类型欺骗、注入、500 全都会来。Zod 是 Node 生态当前事实标准的校验库：**schema 即类型来源**。

```bash
pnpm add zod
```

### 定义 Schema 与推导类型

```ts
import { z } from "zod";

// 定义 schema
const CreateUserSchema = z.object({
  name: z.string().min(1).max(50),
  email: z.email(),                        // Zod 4 顶层 API（旧版 z.string().email()）
  age: z.number().int().min(0).max(150).optional(),
  role: z.enum(["admin", "member"]).default("member"),
});

// 从 schema 推导 TypeScript 类型——单一事实来源
type CreateUserInput = z.infer<typeof CreateUserSchema>;
// { name: string; email: string; age?: number; role: "admin" | "member" }
```

### 校验 body / params / query

```ts
app.post("/users", (req, res) => {
  const parsed = CreateUserSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({
      error: "请求体校验失败",
      issues: parsed.error.issues.map((i) => ({ path: i.path.join("."), message: i.message })),
    });
  }
  // parsed.data 已是类型安全的 CreateUserInput
  res.status(201).json(createUser(parsed.data));
});
```

### 类型安全的校验中间件（复用）

每个路由手写 safeParse 太啰嗦，抽一个泛型中间件（类型细节见 [TypeScript 模式](../reference/language-concepts/05-typescript-patterns.md)）：

```ts
import type { NextFunction, Request, Response } from "express";

function validateBody<T extends z.ZodType>(schema: T) {
  return (req: Request, res: Response, next: NextFunction) => {
    const result = schema.safeParse(req.body);
    if (result.success) {
      req.body = result.data;
      next();
    } else {
      res.status(400).json({ error: "VALIDATION_ERROR", issues: result.error.issues });
    }
  };
}

// 使用
app.post("/users", validateBody(CreateUserSchema), createUserHandler);
```

完整 API 速查见 [Zod 与生态库指南](../reference/library-guides/02-ecosystem-libs.md)。

## 🎨 最佳实践

- ✅ **Router 按资源拆分**：单文件路由超过 ~150 行就该拆了
- ✅ **校验失败返回 400 + 结构化 issues**：让前端能精确提示字段错误
- ✅ **Zod schema 放在离使用处最近的位置**并可复用推导类型
- ❌ **不要信任 `req.body`/`req.query`/`req.params`**：全部来自客户端，必须校验
- ❌ **不要在业务处理函数里做认证**：横切关注点交给中间件

## ❓ 常见问题

### Q1: `req.body` 是 undefined？

**A**: 忘了 `express.json()`，或注册顺序在路由之后；也可能是 Content-Type 不是 application/json。

### Q2: Express 5 中 `app.get("*")` 报错？

**A**: 通配符语法改为 path-to-regexp v8 风格：`app.get("/{*splat}")` 或直接 `app.use(notFoundHandler)` 兜底。

## 🎯 练习与实践

### 练习一：任务清单 API

**任务要求**:
1. 用 Router 实现 `/api/tasks` 的 GET/POST/PATCH/DELETE
2. 每个接口配 Zod schema（含分页参数校验）
3. 加一个记录耗时的中间件（进入时记时间，响应 finish 事件打印）

### 练习二：中间件依赖链

**挑战任务**:
- 实现 `requireRole("admin")` 中间件工厂，依赖认证中间件先执行
- 故意颠倒注册顺序，观察并解释报错行为

**提示**: 角色信息从认证中间件写入的 `req.user` 读取。

---

## 🔗 相关文档

- 📄 **[错误处理](./06-error-handling.md)** — 校验错误与业务错误的统一出口
- 📄 **[Express 5 核心速查](../reference/framework-essentials/01-express-essentials.md)** — 路由/中间件 API 字典
- 📄 **[TypeScript 模式](../reference/language-concepts/05-typescript-patterns.md)** — 泛型校验中间件的类型推导
