# 路由、中间件与请求校验

## 先理解，再动手

路由定位处理者，中间件提供公共前后处理，校验把不可信输入转成业务可用值。TypeScript 类型不会验证请求体。

**本节自测**：POST 接收标题，分别发合法 JSON、空标题和损坏 JSON。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

应有不同的解析或校验失败路径；服务函数只在输入满足契约后运行。

</details>

> **文档简介**: 掌握 Hono 路由组织、洋葱中间件的执行模型，以及用 Zod 做类型安全的请求校验

> **目标读者**: 已跑通第一个 Hono 服务、准备构建真实 API 的开发者

> **前置知识**: [第一个服务器](./02-first-server.md)，TypeScript 基本类型

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 教程（basics） |
| **难度** | ⭐ |
| **标签** | `#路由` `#中间件` `#Zod` `#请求校验` `#Hono` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- 用子应用模块化组织路由并提取路径参数
- 解释洋葱模型的执行语义与 `await next()` 的三种结局
- 为接口加上认证、日志等横切关注点
- 用 Zod 校验请求并把解析结果桥接为 TypeScript 类型

## 🔍 路由：方法 + 路径 + 处理器

### 基本路由与路径参数

```ts
import { Hono } from "hono";

const app = new Hono();

// 路径参数 c.req.param()；查询字符串 c.req.query()
app.get("/posts/:postId/comments", (c) => {
  const postId = c.req.param("postId");
  const limit = Number(c.req.query("limit") ?? 10);
  return c.json({ postId, limit });
});

// 多种 HTTP 方法
app.post("/posts", (c) => c.json({ id: "new" }, 201));

// 带正则约束的参数：只有纯数字才命中
app.delete("/posts/:id{[0-9]+}", (c) => c.json({ deleted: c.req.param("id") }));

// 未匹配路由的兜底：app.notFound（不是通配符路由）
app.notFound((c) => c.json({ error: "路由不存在" }, 404));
```

### 子应用拆分：真实项目的组织方式

Hono 没有独立的 Router 构造器——**每个路由模块就是一个 `Hono` 实例**：

```ts
// src/routes/users.ts（目录含 index.ts 挂载总路由，users/posts 为子应用）
import { Hono } from "hono";
export const usersApp = new Hono();
usersApp.get("/", listUsers);
usersApp.get("/:id", getUser);
usersApp.post("/", createUser);
```

```ts
// src/routes/index.ts —— 总路由聚合，server 装配时 app.route("/api", apiApp)
import { Hono } from "hono";
import { usersApp } from "./users.js";
import { postsApp } from "./posts.js";

export const apiApp = new Hono();
apiApp.route("/users", usersApp);
apiApp.route("/posts", postsApp);
```

## 🔍 中间件：洋葱模型流水线

### 执行模型

中间件是 `(c, next) => Promise` 函数，按注册顺序"进入"，逆序"返回"——`await next()` 两侧代码分别对应请求进站与响应出站：

```ts
// 1) await next()      → 进入下一个中间件，之后还能修改响应
// 2) 抛出错误          → 跳过后续逻辑，直达 app.onError
// 3) 不调用 next 也不返回响应 → 请求悬挂（响应须在该中间件内结束）
app.use(async (c, next) => {
  const start = performance.now();
  await next();
  const ms = performance.now() - start;
  c.res.headers.set("X-Response-Time", `${ms.toFixed(1)}ms`); // next() 之后改响应
});
```

洋葱模型相比线性管道的优势：**进站与出站逻辑写在同一个函数里**，计时、清理、事务包裹都不需要"前中间件 + 后中间件"两个文件。

### 常见中间件形态

```ts
// 内置：开发期日志
import { logger } from "hono/logger";
app.use(logger());

// 自定义认证中间件
import type { MiddlewareHandler } from "hono";

// Context 变量需要显式类型：中间件与 app 标注同一 Env 泛型（全局增强写法见 [TypeScript 模式](../reference/language-concepts/05-typescript-patterns.md)）
type Env = { Variables: { user: User } };

const requireAuth: MiddlewareHandler<Env> = async (c, next) => {
  const token = c.req.header("Authorization")?.replace("Bearer ", "");
  if (!token) return c.json({ error: "未认证" }, 401);
  c.set("user", verifyToken(token));   // 写入 Context 变量
  await next();
};

// 作用域挂载：只保护某个路由组（app 需以同一 Env 创建：new Hono<Env>()）
app.use("/api/admin/*", requireAuth);
// 或路由级
app.get("/me", requireAuth, (c) => c.json({ user: c.get("user") }));
```

顺序即语义：认证必须在读取 `c.get("user")` 的处理器之前；`bodyLimit` 必须在解析请求体之前。

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

### zValidator：校验中间件的官方姿势

社区官方推荐的 `@hono/zod-validator` 把校验挂进路由，校验后的数据通过 `c.req.valid()` 取回（类型自动收窄）：

```bash
pnpm add -D @hono/zod-validator
```

```ts
import { zValidator } from "@hono/zod-validator";

app.post("/users", zValidator("json", CreateUserSchema), (c) => {
  const data = c.req.valid("json"); // CreateUserInput 类型，无需再断言
  return c.json(createUser(data), 201);
});
```

校验失败时默认返回 400；要定制错误响应，给 `zValidator` 传第三个回调参数（模式详解见 [TypeScript 模式](../reference/language-concepts/05-typescript-patterns.md)）。

不想引入中间件也可以手写——在处理器里 `safeParse` 后把 `ZodError` 抛给 `app.onError` 统一输出（见 [错误处理](./06-error-handling.md)）。

完整 API 速查见 [Zod 与生态库指南](../reference/library-guides/02-ecosystem-libs.md)。

## 🎨 最佳实践

路由按资源或业务边界组织，读请求、校验、调用服务和写响应各有明确责任，不用文件超过某行数就强制拆分。客户端的 JSON、路径和查询参数都属于待验证输入，转换成功还要检查范围及业务合法性。

中间件适合提取和验证身份，但“当前用户能否修改这条记录”的授权通常还涉及业务数据。统一字段错误响应让前端能定位输入问题；用非法参数、无身份、跨用户和成功请求分别验收。

## ❓ 常见问题

### Q1: 请求体一直是空对象/抛错？

**A**: 确认请求头 `Content-Type: application/json` 与 `c.req.json()` 配套；`parseBody()` 只用于 multipart 表单，两者不能混用。

### Q2: `c.req.query("page")` 类型为什么是 `string | undefined`？

**A**: 查询串天然是字符串。用 `z.coerce.number()` 或 `Number(...)` 显式转换，并给默认值兜底。

## 🎯 练习与实践

### 练习一：任务清单 API

**任务要求**:
1. 用子应用实现 `/api/tasks` 的 GET/POST/PATCH/DELETE
2. 每个接口配 Zod schema（含分页参数校验）+ zValidator
3. 加一个记录耗时的中间件（进站记时间，出站写 `X-Response-Time` 头）

### 练习二：中间件依赖链

**挑战任务**:
- 实现 `requireRole("admin")` 中间件工厂，依赖认证中间件先执行
- 故意颠倒注册顺序，观察并解释报错行为

**提示**: 角色信息从认证中间件写入的 `c.get("user")` 读取。

---

## 🔗 相关文档

- 📄 **[错误处理](./06-error-handling.md)** — 校验错误与业务错误的统一出口
- 📄 **[Hono 4 核心速查](../reference/framework-essentials/01-hono-essentials.md)** — 路由/中间件 API 字典
- 📄 **[TypeScript 模式](../reference/language-concepts/05-typescript-patterns.md)** — zValidator 类型推导与泛型处理器


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
