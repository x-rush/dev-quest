# 框架选型对比：Fastify、NestJS 与 Express

> **文档简介**: "何时选它"字典条目——Fastify 的性能与插件生态、NestJS 的架构哲学、Express 的历史定位，以及三者与 Hono（本模块主角）的完整选型对比

> **目标读者**: 需要为新项目做框架决策、或评估"是否偏离 Hono 主线"的开发者

> **前置知识**: [Hono 4 核心速查](./01-hono-essentials.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐⭐ |
| **标签** | `#Fastify` `#NestJS` `#Express` `#框架对比` `#选型` |
| **更新日期** | `2026年9月` |

## 0. 四框架定位与选型总览

### 定义
Node.js 后端框架的竞争本质是三种架构哲学的取舍：**轻量内核 + 中间件**（Hono/Express）、**插件 + Schema 驱动**（Fastify）、**全家桶结构化**（NestJS）。

### 选型对比表

| 维度 | Hono 4（主角） | Fastify 5 | NestJS 11 | Express 5 |
|------|---------------|-----------|-----------|-----------|
| 心智模型 | Web 标准 + 洋葱中间件 | 插件 + 钩子 + JSON Schema | 模块/控制器/依赖注入 | 中间件管道 |
| 定位一句话 | 轻量、极快、跨运行时 | Node 原生性能旗舰 | 大型工程结构框架 | 历史事实标准 |
| 类型支持 | 内置且推断优秀 | 优秀（泛型推断） | 优秀（装饰器一等公民） | 社区类型包，滞后 |
| 请求校验 | Zod validator 中间件 | 内置 JSON Schema + AJV | ValidationPipe（class-validator/Zod 适配） | 自己配 Zod 等手接 |
| 性能梯队 | 第一梯队（Routing 引擎极快） | 第一梯队 | 中游（抽象层开销） | 末游 |
| 生态位 | API 服务、边缘/Serverless、跨运行时 | 重 I/O Node 单体、Schema-first 团队 | 大型团队、微服务、DDD 分层 | 遗留系统维护 |
| **何时选它** | 新项目默认首选：类型好、依赖少、测试内置、可迁移到边缘 | schema-first 是硬需求、深度依赖 Fastify 插件生态、纯 Node 单体追求吞吐 | 团队 5 人以上、模块边界即治理需求、招聘需要统一结构 | 只为维护存量代码——2026 年新项目没有选择它的理由 |

### 一句话决策

- **个人/小团队新项目** → Hono（本模块主线）
- **吞吐敏感 + Schema 文化** → Fastify
- **大型团队工程治理** → NestJS（底层适配器仍可选 Fastify）
- **接手老代码** → Express，按了解成本迁移而非重写

## 1. Fastify：性能与插件生态

### 定义
以插件系统、内置 JSON Schema 校验/序列化为核心的高性能 Node 框架。与 Hono 同属"性能第一梯队"，差异在路线：Fastify 深耕 Node 原生生态，Hono 押注 Web 标准与跨运行时。

### 核心用法

```ts
import Fastify from "fastify";

const app = Fastify({ logger: true });   // 内置 pino 日志
app.get("/users/:id", async (request, reply) => {
  const { id } = request.params as { id: string };
  return { id };                          // 直接返回对象 = 200 JSON
});
await app.listen({ port: 3000, host: "0.0.0.0" });
```

```ts
// Schema-first：schema 既做请求校验，又加速响应序列化
const createUserOpts = {
  schema: {
    body: {
      type: "object",
      required: ["name", "email"],
      properties: { name: { type: "string", minLength: 1 }, email: { type: "string", format: "email" } },
    },
    response: { 201: { /* 响应 schema */ } },
  },
} as const;

app.post("/users", createUserOpts, async (req, reply) => {
  reply.code(201);
  return { id: 1, ...req.body };
});
// 不想手写 JSON Schema：fastify-type-provider-zod 把 Zod 挂到路由，类型自动推断
```

```ts
// 生命周期钩子与插件
app.addHook("onRequest", async (req) => { /* 认证，早于 body 解析 */ });
app.addHook("onResponse", async (req, reply) => { /* 访问日志 */ });
app.decorate("db", new DbPool());          // 装饰器：实例级共享数据
await app.register(import("./routes/users.js"), { prefix: "/users" }); // 插件封装
```

### 陷阱
- Fastify 对未知 Content-Type 默认报 415，JSON 之外的格式需 `addContentTypeParser`
- 路由前缀冲突启动即抛错（Hono/Express 是按序命中），重复注册路径同样启动失败
- `async` 钩子必须 `await`，漏掉的 rejection 会让插件加载失败

### 何时选它
- 请求/响应 schema 是团队规范或合规需求（AJV 校验 + fast-json-stringify 序列化一箭双雕）
- 深度使用 Fastify 插件生态：@fastify/jwt、@fastify/rate-limit、@fastify/swagger（文档自动生成是杀手级场景）
- 纯 Node 单体、吞吐敏感、不需要跨运行时——Hono 的跨运行时优势在此场景用不上，Fastify 的插件深度则真实有效

## 2. NestJS：装饰器、DI 与模块化架构

### 定义
基于装饰器与依赖注入的结构化后端框架，用"模块/控制器/服务"三件套强制分层。它与 Hono 的差异**不在性能而在定位**：Nest 卖的是大型工程的结构治理（约定大于配置、依赖显式、模块可复用），Hono 卖的是轻量内核下的自由组装。Nest 底层适配器可用 Express 或 Fastify，因此"选 Nest"某种意义上是选架构而非选 HTTP 引擎。

### 三件套：Module / Controller / Service

```ts
// tasks.controller.ts
import { Body, Controller, Delete, Get, Param, ParseUUIDPipe, Patch, Post, Query } from "@nestjs/common";

@Controller("tasks")
export class TasksController {
  constructor(private readonly tasksService: TasksService) {}  // 构造器注入

  @Get()
  list(@Query("status") status?: TaskStatus) {
    return this.tasksService.list(status);
  }

  @Get(":id")
  get(@Param("id", ParseUUIDPipe) id: string) {   // 内置参数校验管道
    return this.tasksService.get(id);
  }

  @Post()
  create(@Body() dto: CreateTaskDto) {            // DTO + 校验管道
    return this.tasksService.create(dto);
  }
}
```

```ts
// tasks.service.ts
import { Injectable, NotFoundException } from "@nestjs/common";

@Injectable()
export class TasksService {
  get(id: string) {
    const task = this.repo.find(id);
    if (!task) throw new NotFoundException();   // 异常 → 自动映射 HTTP 404
    return task;
  }
}
```

三件套在 `tasks.module.ts` 的 `@Module` 中登记：`controllers: [TasksController]`、`providers: [TasksService, PrismaService]`、`exports: [TasksService]`（供其他模块 import）。

```ts
// main.ts 全局校验管道（配 class-validator 或 Zod 适配器）
app.useGlobalPipes(new ValidationPipe({
  whitelist: true,        // 剥离未声明的字段
  transform: true,        // 按 DTO 类型自动转换（string → number）
}));
```

### 陷阱
- Service 未注册进 `providers` 或模块不在根模块引用链上 → `Nest can't resolve dependencies`
- 装饰器依赖 TS 实验特性：`tsconfig.json` 必须开 `"experimentalDecorators": true` 与 `"emitDecoratorMetadata": true`（Node 原生类型剥离不支持装饰器，Nest 项目必须走 tsc/swc 编译）
- `NotFoundException` 等框架异常抛在 Service 层是惯例；控制器里 try/catch 吞掉它们会破坏统一错误映射

### 与 Hono 的定位差异（写透）
- **结构来源**：Nest 把"分层、依赖、边界"写进框架——目录即架构，新人零培训上手同一结构；Hono 把这些留给项目自定（见 [服务架构与模块化单体](../../advanced-topics/architecture/01-service-architecture.md)），代价是纪律靠自觉
- **抽象成本**：Nest 的装饰器/DI/反射层让小项目显得笨重、启动慢、调试栈深；Hono 几乎无魔法，代码即所见
- **规模拐点**：当"接手的人多过写代码的人"时，Nest 的强约定开始产生净收益；独立开发者与两三人小团队的临界点通常远比想象中晚
- **混用策略**：大项目也可以"Hono 做网关 + 领域逻辑自管"——结构治理未必需要 Nest 全家桶

### 何时选它
- 团队规模大、模块所有权分散，需要框架级强制边界
- 微服务/多应用要共享统一的模块与依赖注入基建
- 招聘市场对"Nest 结构"的共识可以降低协作成本

## 3. Express：历史定位与 2026 年的现实

### 定义
Node.js 生态的第一代事实标准：极简内核 + 中间件管道。2024 年发布的 v5 修复了安全与长期悬置的 Bug（path-to-regexp v8、async rejection 自动转发），但架构形态停留在 2014 年。

### 为什么 2026 年新项目不再首选
- **性能**：中间件管道与 `req`/`res` 副作用模型在基准测试中稳定垫底；Hono/Fastify 的开销低一个量级
- **类型体验**：TypeScript 支持是社区外挂（`@types/express`），泛型链与推断远不如 Hono/Fastify 原生
- **能力密度**：JSON 解析、静态文件、安全头、Cookie、测试客户端全靠外部包拼装（body-parser、serve-static、helmet、cookie-parser、supertest）；Hono 内建以上全部
- **运行时**：绑定 Node 的 `req`/`res`，无法迁移到边缘/Serverless；Hono 的 Web 标准 API 天生可移植
- **仍有价值的场景**：维护十年以上的存量服务；团队强制要求"招聘简历上人人都写过的框架"；大量老教程/SO 答案以它为基准

### 陷阱
- v5 与 v4 语法有破坏性差异（通配符 `/{*splat}`、移除正则路由）——网上老教程混杂两代写法，照抄会踩坑
- 用它新建项目时要自行决策的安全默认项（body 限制、trust proxy、错误页）远多于现代框架

## 4. 同一需求的写法对照

| 环节 | Hono 4 | Fastify 5 | NestJS 11 | Express 5 |
|------|--------|-----------|-----------|-----------|
| 路由声明 | `app.post("/tasks", h)` | `app.post("/tasks", opts, h)` | `@Post()` + `@Controller` | `app.post("/tasks", h)` |
| 请求体 | `await c.req.json()` | `req.body`（Schema 校验） | `@Body() dto`（Pipe 校验） | `req.body`（需 json 中间件） |
| 校验 | Zod + zValidator | JSON Schema/AJV 内置 | DTO + ValidationPipe | Zod + 自写中间件 |
| 错误 | `app.onError` | `setErrorHandler` | 抛框架异常自动映射 | 四参错误中间件 |
| 日志 | hono/logger 或 pino 中间件 | 内置 pino | Logger 或集成 pino | pino-http 自接 |
| 依赖共享 | `c.set/get`（ContextVariableMap） | decorate + plugin | DI 注入 | 挂 req/app |
| 集成测试 | `app.request()` 内置 | `app.inject()` 内置 | supertest | supertest |

> 值得注意：Fastify 的 `app.inject()` 与 Hono 的 `app.request()` 是同一思想的两次实现——框架内置请求注入，测试不再需要真实端口与 supertest。

---

## 🔗 相关文档

- 📄 **[Hono 4 核心速查](./01-hono-essentials.md)** — 本模块主角的 API 字典
- 📄 **[服务架构与模块化单体](../../advanced-topics/architecture/01-service-architecture.md)** — 不依赖框架的结构治理方案
- 📄 **[生态库精选](../library-guides/02-ecosystem-libs.md)** — Zod/pino 等跨框架配套库
- 📄 **[第一个完整项目](../../basics/08-first-project.md)** — 用 Hono 实现的同款 CRUD
