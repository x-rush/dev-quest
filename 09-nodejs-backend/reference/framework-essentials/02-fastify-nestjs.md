# Fastify 与 NestJS 核心速查

> **文档简介**: Fastify 与 NestJS 两大主流框架的核心 API 速查与选型对比，含与 Express 的心智模型差异

> **目标读者**: 已掌握 Express、需要评估或上手 Fastify/NestJS 的开发者

> **前置知识**: [Express 5 核心速查](./01-express-essentials.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐⭐ |
| **标签** | `#Fastify` `#NestJS` `#框架对比` `#装饰器` |
| **更新日期** | `2026年9月` |

## 0. 框架选型对比

### 定义
三者定位：Express 是极简事实标准；Fastify 主打高性能与内置 JSON Schema；NestJS 是企业级结构化全家桶（默认可用 Fastify 作底层适配器）。

| 维度 | Express 5 | Fastify 5 | NestJS 11 |
|------|-----------|-----------|-----------|
| 心智模型 | 中间件管道 | 插件 + 钩子 + Schema | 模块/控制器/依赖注入 |
| 类型支持 | 社区类型包 | 优秀（泛型推断） | 优秀（装饰器一等公民） |
| 校验 | 配 Zod 等手接 | 内置 JSON Schema + AJV | 内置 ValidationPipe（class-validator/Zod 适配） |
| 性能 | 基准 | 显著高于 Express | 接近底层适配器 |
| 适用 | 通用小型服务、学习 | I/O 密集高性能 API | 大型团队、微服务、DDD 分层 |

## 1. Fastify 核心

### 定义
以插件系统、Schema 校验和序列化为核心的高性能 Web 框架。

### 最小服务

```ts
import Fastify from "fastify";

const app = Fastify({ logger: true });   // 内置 pino 日志
app.get("/users/:id", async (request, reply) => {
  const { id } = request.params as { id: string };
  return { id };                          // 直接返回对象 = 200 JSON
});
await app.listen({ port: 3000, host: "0.0.0.0" });
```

### Schema 校验与类型推断

```ts
const createUserOpts = {
  schema: {
    body: {
      type: "object",
      required: ["name", "email"],
      properties: { name: { type: "string", minLength: 1 }, email: { type: "string", format: "email" } },
    },
    response: { 201: { /* JSON Schema：既校验又加速序列化 */ } },
  },
} as const;

app.post("/users", createUserOpts, async (req, reply) => {
  reply.code(201);
  return { id: 1, ...req.body };
});
```

不想手写 JSON Schema：用 `fastify-type-provider-zod` 把 Zod schema 挂到路由，类型自动推断。

### 生命周期钩子与插件

```ts
// 请求生命周期（常用子集）
app.addHook("onRequest", async (req) => { /* 认证，早于 body 解析 */ });
app.addHook("preHandler", async (req) => { /* 校验后、handler 前 */ });
app.addHook("onResponse", async (req, reply) => { /* 访问日志 */ });
// 装饰器：给实例挂共享数据（如连接池）
app.decorate("db", new DbPool());
// 插件 = 封装功能的单位（自带作用域与依赖顺序）
await app.register(import("./routes/users.js"), { prefix: "/users" });
```

### 陷阱
- Fastify 对未知 Content-Type 默认报 415，JSON 之外的格式需 `app.addContentTypeParser`
- 路由注册顺序无关但**前缀冲突会抛错**（Express 是静默覆盖），重复注册路径启动即失败
- `async` 钩子必须 `await`，漏掉的 rejection 会被框架捕获并使插件加载失败

## 2. NestJS 核心

### 定义
基于装饰器与依赖注入的结构化后端框架，强制模块化分层。

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

### 校验管道与 DTO

```ts
// main.ts 全局启用（配 class-validator 或 Zod 适配器）
app.useGlobalPipes(new ValidationPipe({
  whitelist: true,        // 剥离未声明的字段
  transform: true,        // 按 DTO 类型自动转换（string → number）
}));

// create-task.dto.ts：class + 装饰器声明字段约束（@IsString、@Length、@IsIn…）
export class CreateTaskDto {
  @IsString() @Length(1, 100)
  title!: string;
}
```

### 陷阱
- 忘记把 Service 注册进 `providers` 或模块不在根模块引用链上 → 依赖注入报 `Nest can't resolve dependencies`
- 装饰器依赖 TS 实验特性：`tsconfig.json` 必须开 `"experimentalDecorators": true` 与 `"emitDecoratorMetadata": true`（Node 原生类型剥离不支持装饰器，NestJS 项目走 tsc/swc 编译）
- `NotFoundException` 等框架异常抛在 Service 层是惯例；在控制器里 try/catch 吞掉它们会破坏统一错误映射

## 3. 同一需求的写法对照

| 环节 | Express 5 | Fastify 5 | NestJS 11 |
|------|-----------|-----------|-----------|
| 路由声明 | `app.post("/tasks", h)` | `app.post("/tasks", opts, h)` | `@Post()` + `@Controller("tasks")` |
| 请求体 | `req.body`（需 json 中间件） | `req.body`（Schema 校验） | `@Body() dto`（Pipe 校验） |
| 校验 | Zod + 自写中间件 | JSON Schema/AJV 内置 | DTO + ValidationPipe |
| 错误 | 集中错误中间件 | `reply.code().send()` / setErrorHandler | 抛框架异常自动映射 |
| 日志 | pino-http 自接 | 内置 pino | Logger 或集成 pino |
| 依赖共享 | 挂 req/app | decorate + plugin | DI 注入 |

---

## 🔗 相关文档

- 📄 **[Express 5 核心速查](./01-express-essentials.md)** — 通用中间件模型基座
- 📄 **[生态库精选](../library-guides/02-ecosystem-libs.md)** — Zod/pino 等配套库
- 📄 **[第一个项目](../../basics/08-first-project.md)** — 用 Express 实现的同款 CRUD
