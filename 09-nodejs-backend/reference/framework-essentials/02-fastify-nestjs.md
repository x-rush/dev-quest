# 框架选型对比：Fastify、NestJS 与 Express

> **文档简介**: "何时选它"字典条目——Fastify 的性能与插件生态、NestJS 的架构哲学、Express 的历史定位，以及三者与 Hono（本模块主角）的完整选型对比

> **目标读者**: 需要为新项目做框架决策、或评估"是否偏离 Hono 主线"的开发者

> **前置知识**: [Hono 4 核心速查](./01-hono-essentials.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐⭐ |
| **标签** | `#Fastify` `#NestJS` `#Express` `#框架对比` `#选型` |
| **更新日期** | `2026年9月` |

</details>

## 0. 四框架定位与选型总览

### 定义
Node.js 后端框架的竞争本质是三种架构哲学的取舍：**轻量内核 + 中间件**（Hono/Express）、**插件 + Schema 驱动**（Fastify）、**全家桶结构化**（NestJS）。

### 选型对比表

| 维度 | Hono 4（主角） | Fastify 5 | NestJS 11 | Express 5 |
|------|---------------|-----------|-----------|-----------|
| 心智模型 | Web 标准 + 洋葱中间件 | 插件 + 钩子 + JSON Schema | 模块/控制器/依赖注入 | 中间件管道 |
| 定位一句话 | 轻量、极快、跨运行时 | Node 原生性能旗舰 | 大型工程结构框架 | 历史事实标准 |
| 类型支持 | 内置且推断优秀 | 优秀（泛型推断） | 优秀（装饰器一等公民） | 社区维护的 @types/express |
| 请求校验 | Zod validator 中间件 | 内置 JSON Schema + AJV | ValidationPipe（class-validator/Zod 适配） | 自己配 Zod 等手接 |
| 性能评估 | 测量运行时适配器与中间件 | 测量 schema、日志和插件 | 测量底层适配器与拦截器 | 测量中间件与业务负载 |
| 生态位 | API 服务、边缘/Serverless、跨运行时 | 重 I/O Node 单体、Schema-first 团队 | 大型团队、微服务、DDD 分层 | 遗留系统维护 |
| **何时选它** | 适合偏好 Web 标准与轻量组合的项目；跨运行时仍需检查依赖 | schema-first 是硬需求、深度依赖 Fastify 插件生态、纯 Node 单体追求吞吐 | 需要统一模块、依赖注入和协作约定 | 团队熟悉其中间件生态，愿意自行制定结构与验证规范 |

### 一句话决策

- **个人/小团队新项目** → Hono（本模块主线）
- **吞吐敏感 + Schema 文化** → Fastify
- **大型团队工程治理** → NestJS（底层适配器仍可选 Fastify）
- **接手老代码** → Express，按了解成本迁移而非重写

## 1. Fastify：性能与插件生态

### 定义
以插件系统、内置 JSON Schema 校验/序列化为核心的高性能 Node 框架。与 Hono 的主要差异在组织方式与运行时取向：Fastify 深耕 Node 原生生态，Hono 押注 Web 标准与跨运行时。

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
    response: { 201: { type: "object", required: ["id", "name", "email"],
      properties: { id: { type: "number" }, name: { type: "string" }, email: { type: "string" } } } },
  },
} as const;

app.post<{ Body: { name: string; email: string } }>("/users", createUserOpts, async (req, reply) => {
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
- 同一方法和实际路由重复注册会失败；共享前缀本身是正常组织方式
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
  transform: true,        // 转换为 DTO 实例；属性转换仍需显式配置，不是所有字符串都会自动变数字
}));
```

### 陷阱
- Service 未注册进 `providers` 或模块不在根模块引用链上 → `Nest can't resolve dependencies`
- 装饰器依赖 TS 实验特性：`tsconfig.json` 必须开 `"experimentalDecorators": true` 与 `"emitDecoratorMetadata": true`（Node 原生类型剥离不支持装饰器，Nest 项目必须走 tsc/swc 编译）
- `NotFoundException` 等框架异常抛在 Service 层是惯例；控制器里 try/catch 吞掉它们会破坏统一错误映射

### 与 Hono 的定位差异（写透）
- **结构来源**：Nest 把"分层、依赖、边界"写进框架——提供统一装配约定；新人仍需理解 provider 作用域与业务边界；Hono 把这些留给项目自定（见 [服务架构与模块化单体](../../advanced-topics/architecture/01-service-architecture.md)），代价是纪律靠自觉
- **抽象成本**：Nest 的装饰器/DI/反射层让小项目显得笨重、启动慢、调试栈深；Hono 几乎无魔法，代码即所见
- **规模拐点**：当"接手的人多过写代码的人"时，Nest 的强约定开始产生净收益；独立开发者与两三人小团队的临界点通常远比想象中晚
- **混用策略**：大项目也可以"Hono 做网关 + 领域逻辑自管"——结构治理未必需要 Nest 全家桶

### 何时选它
- 团队规模大、模块所有权分散，需要框架级强制边界
- 微服务/多应用要共享统一的模块与依赖注入基建
- 招聘市场对"Nest 结构"的共识可以降低协作成本

## 3. Express：历史定位与 2026 年的现实

### 定义
Node.js 生态的第一代事实标准：极简内核 + 中间件管道。2024 年发布的 v5 修复了安全与长期悬置的 Bug（path-to-regexp v8、async rejection 自动转发），并保留以中间件为核心的组织方式。

### 如何判断 Express 是否合适

Express 5 仍可用于新项目，适合已有中间件经验、希望保持简单请求管道的团队。它内置 `express.json()`、`express.urlencoded()` 和 `express.static()`；安全头、Cookie 解析、测试工具等可另行组合。能否部署到某个 Serverless 平台取决于平台的 Node 支持和适配器，不能把 Serverless 与边缘运行时混为一谈。

选择它的成本是自行约定验证、错误响应、模块边界与类型扩展；选择其他框架也有迁移和学习成本。没有相同硬件、业务逻辑、日志与数据库负载的测量，不能断言某框架快一个数量级。参见 [Express 5 API](https://expressjs.com/en/5x/api.html)。

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

<!-- full-library-explanation -->
## 用同一个小需求比较框架，而不是比较宣传词

先实现“创建任务”：只接受非空 title，返回不含内部字段的 JSON；非法请求返回 400；缺少身份返回 401；数据库失败返回 500 并留下关联日志。比较注册路由、运行时验证、依赖替换和测试所需的代码，再决定框架是否适合团队。

Fastify 的 schema 执行运行时校验与序列化，Type Provider 才进一步把 schema 连接到 TypeScript 推断。`as` 类型断言不会安装校验器。Nest 的模块管理 provider 的可见性，但不会自动阻止任意文件 import，也不会替你决定业务边界；DTO 的属性声明本身不会验证输入，仍须校验装饰器与管道。

**练习**：选两个框架实现上述接口，为多余字段、缺字段及数据库拒绝写相同断言。记录差异来自默认行为、你写的代码还是外接插件。性能比较应再加入真实序列化和数据库延迟，不能根据 hello-world 排名替代工程选型。

参考：[Fastify Type Providers](https://fastify.dev/docs/latest/Reference/Type-Providers/)。本页 Nest 片段用于解释职责，repo、DTO 和启动装配需由项目提供。

## 🔗 相关文档

- 📄 **[Hono 4 核心速查](./01-hono-essentials.md)** — 本模块主角的 API 字典
- 📄 **[服务架构与模块化单体](../../advanced-topics/architecture/01-service-architecture.md)** — 不依赖框架的结构治理方案
- 📄 **[生态库精选](../library-guides/02-ecosystem-libs.md)** — Zod/pino 等跨框架配套库
- 📄 **[第一个完整项目](../../basics/08-first-project.md)** — 用 Hono 实现的同款 CRUD


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
