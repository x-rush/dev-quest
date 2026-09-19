# Node + TypeScript 常用模式

> **文档简介**: Node 后端开发中高频的 TypeScript 模式——zValidator 类型收窄、类型安全环境变量、Hono 类型扩展、依赖注入与类型守卫

> **目标读者**: 有 TS 基础、想把 Node 后端代码类型写"严"的开发者

> **前置知识**: TypeScript 泛型基础，[路由与中间件](../../basics/05-http-routing.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐⭐ |
| **标签** | `#TypeScript` `#泛型` `#环境变量` `#类型扩展` |
| **更新日期** | `2026年9月` |

</details>

## 1. 类型安全的环境变量

### 定义
启动时集中解析并校验环境变量，导出校验后的强类型配置对象；若需运行时不可变还要另行约束。

### 语法与示例

```ts
// src/lib/env.ts —— Zod 方案（推荐）
import { z } from "zod";

const EnvSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  PORT: z.coerce.number().int().min(1).max(65535).default(3000),
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

## 2. zValidator：schema 即类型来源

### 定义
`@hono/zod-validator` 把 Zod schema 挂进路由，校验通过后 `c.req.valid()` 直接返回精确类型——不再需要手写"泛型校验中间件"注入类型。

### 语法与示例

```ts
import { zValidator } from "@hono/zod-validator";
import { z } from "zod";

const CreateTaskSchema = z.object({
  title: z.string().min(1).max(100),
  status: z.enum(["todo", "doing", "done"]).default("todo"),
});

app.post("/tasks", zValidator("json", CreateTaskSchema), (c) => {
  const data = c.req.valid("json"); // 类型 = z.infer<typeof CreateTaskSchema>，无需断言
  return c.json(data, 201);
});
```

### 陷阱
- 校验失败默认返回 400 JSON；要定制响应格式，给 `zValidator` 传第三个 hook 回调，在其中返回自定义 `c.json(..., 422)`
- `c.req.valid("json")` 的键必须与 `zValidator` 第一参一致（`"json"` / `"query"` / `"param"`），取错位置拿不到校验结果
- 不想引入中间件时，可在处理器里 `safeParse` 后把 `ZodError` 抛给 `app.onError` 统一输出（错误出口设计见 [错误处理](../../basics/06-error-handling.md)）

## 3. 扩展 Hono 的 ContextVariableMap

### 定义
用模块声明合并给 `c.set` / `c.get` 的自定义变量正式类型——Hono 版的"扩展 Request"。

### 语法与示例

```ts
// types/hono.d.ts（需包含在 tsconfig 中）
import type { User } from "../src/auth.js";

declare module "hono" {
  interface ContextVariableMap {
    auth?: User;
  }
}

export {};
```

```ts
// 使用处自动获得类型
app.get("/me", requireAuth, (c) => {
  return c.json(c.get("auth"));   // User | undefined，requireAuth 保证非空
});
```

### 陷阱
- 对 `hono` 模块做 `declare module` 合并即可，**不需要** `declare global`——`ContextVariableMap` 是模块内接口
- 类型上 `auth?: User` 的可空性要靠运行时中间件保证，别撒谎声明为必有值
- `c.set` 的变量在同一请求作用域内对后续中间件与处理器可见，跨请求不共享

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

// 错误出口中使用（app.onError 全站唯一出口，见 [错误处理](../../basics/06-error-handling.md)）
app.onError((err, c) => {
  if (isHttpError(err)) {
    return c.json({ error: { code: err.code } }, err.status);
  }
  console.error(err); // 未知错误记日志，响应不泄露内部细节
  return c.json({ error: { code: "INTERNAL_ERROR" } }, 500);
});

// Zod 附带的守卫
if (result.error instanceof z.ZodError) { /* 校验错误分支 */ }
```

### 陷阱
- 跨构建产物/多次打包后 `instanceof` 可能失效（不同类副本），可改用 `err.name` 判别
- 谎报的 `e is X` 守卫比没有守卫更危险，守卫逻辑必须与声明严格一致

### 可复现验收：`unknown` 进入错误出口前必须被收窄

此例把一个已知 `HttpError` 和一个普通 `Error` 分别交给错误映射函数。只有守卫成功时才读取 `status` 与 `code`；未知错误得到通用的 500 响应，避免依赖断言或泄露内部信息。它不验证 Hono 的 `app.onError`、跨 bundle 的 `instanceof` 或日志传输。

```ts verify:node-typescript-error-guard
class HttpError extends Error {
  status: number;
  code: string;

  constructor(
    status: number,
    code: string,
    message: string,
  ) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

function isHttpError(error: unknown): error is HttpError {
  return error instanceof HttpError;
}

function responseFor(error: unknown): string {
  if (isHttpError(error)) {
    return `${error.status}:${error.code}`;
  }
  return "500:INTERNAL_ERROR";
}

console.log(responseFor(new HttpError(422, "INVALID_TITLE", "title is blank")));
console.log(responseFor(new Error("database unavailable")));
```

预期输出：

```text
422:INVALID_TITLE
500:INTERNAL_ERROR
```

---

<!-- full-library-explanation -->
## 静态类型与运行时校验在边界交接

前置是 TypeScript 联合类型、泛型和 JSON。interface 描述程序期望的形状，编译后通常被擦除；as User 只是告诉检查器相信你，不会检查网络返回的数据。把外部值先作为 unknown，经过 schema 或类型守卫验证，再进入业务代码，才能把“编译器允许访问”与“实际数据确实存在”连接起来。

环境变量应在启动时一次解析，给出清楚的缺失、格式和范围错误；避免打印包含密钥的整个配置。z.coerce.number 会接受空串为 0，因此正整数端口还要检查范围，不能只调用 int。schema.parse 返回值也不会因为 export const 就变成深度不可变，const 只固定绑定，嵌套对象是否可修改是另一项约定。

练习：对端口输入 undefined、空串、abc、0、3000、70000 做表驱动校验。若应用只允许 1–65535，只有缺失时采用默认值及 3000 应成功。再把未知 JSON 强制断言成 User，与真正运行 schema 校验的结果比较；测试应在缺少 id 时明确失败。依赖注入只需要把数据库或时钟接口传给构造函数，不必先引入复杂容器。

## 🔗 相关文档

- 📄 **[路由与中间件](../../basics/05-http-routing.md)** — zValidator 的教程式讲解
- 📄 **[现代 JS 语法速查](./01-js-modern-syntax.md)** — 类型守卫与判空语法
- 📄 **[第一个项目](../../basics/08-first-project.md)** — 本页模式的完整落地实例


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
