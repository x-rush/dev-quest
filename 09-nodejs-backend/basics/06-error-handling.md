# 错误处理与进程稳定性

## 先理解，再动手

业务错误、外部服务错误和程序缺陷需要不同响应。统一入口映射错误有利于一致，但不能把内部堆栈直接返回客户端。

**本节自测**：模拟不存在资源与未知异常，对比客户端响应和服务端日志。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

客户端得到稳定错误契约；日志保留诊断信息，未知异常不能伪装成成功。

</details>

> **文档简介**: 建立 Node 后端的完整错误处理体系——错误传播、异步错误捕获、Hono 集中式错误出口（onError）与进程级兜底

> **目标读者**: 已了解 Hono 路由与中间件、准备让服务"生产可用"的开发者

> **前置知识**: [路由与中间件](./05-http-routing.md)，[异步编程](./04-async-promises.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 教程（basics） |
| **难度** | ⭐ |
| **标签** | `#错误处理` `#onError` `#uncaughtException` `#稳定性` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- 区分操作性错误与程序员错误并分别对待
- 在同步、Promise、回调三种语境中正确传播错误
- 实现 `app.onError` 集中式错误出口与统一错误响应格式
- 配置 `uncaughtException` / `unhandledRejection` 进程兜底

## 🔍 两类错误，两种策略

| 类型 | 例子 | 策略 |
|------|------|------|
| **操作性错误**（预期内） | 数据库连不上、文件不存在、请求超时、输入非法 | 记日志、降级、返回 4xx/5xx，服务继续运行 |
| **程序员错误**（Bug） | 未定义变量、类型用错、逻辑漏判 | 修复代码；进程不可信，应崩溃重启 |

这个区分是 Node 错误处理的基石：**不要试图捕获 Bug 后继续运行**，状态可能已损坏。

## 🛠️ 错误传播：三种语境

### 同步代码：throw + try/catch

```ts
function parseConfig(raw: string) {
  const cfg = JSON.parse(raw); // 可能同步抛出
  return cfg;
}

try {
  parseConfig(badJson);
} catch (err) {
  console.error("配置解析失败", err);
}
```

### Promise/async-await：自动传播

`async` 函数内 throw 会变成 Promise rejection，沿 await 链向上传播——**但必须有人接住**：

```ts
async function bootstrap() {
  await connectDb();     // 失败 → rejection 传给调用方
}
// ✅ 在调用处捕获
bootstrap().catch((err) => {
  console.error("启动失败", err);
  process.exit(1);
});
```

Hono 的进步：路由处理器抛出的错误（含 async rejection）自动转发给 `app.onError`，无需手写 try/catch，也不需要老框架时代的 async 包装补丁。

### 可直接运行的错误因果链示例（Node.js）

这段是上面包装规则的无框架最小版。它只验证 `Error` 的 `cause` 会保留原始错误对象；日志工具是否展开 cause 链仍取决于日志工具的序列化配置。

```js
class ServiceError extends Error {
  constructor(message, options = {}) {
    super(message, { cause: options.cause });
    this.name = "ServiceError";
  }
}

const root = new Error("database unavailable");
const wrapped = new ServiceError("query failed", { cause: root });
console.log(`${wrapped.name}|${wrapped.message}|${wrapped.cause.message}`);
```

### 回调式 API：error-first 约定

遗留回调式 API 遵循 `(err, result)` 首参错误约定——不处理也不传出的回调错误会变成 `uncaughtException`。现代代码应改用 `node:fs/promises` 等 Promise 版本。

### 错误包装保留因果链

```ts
class ServiceError extends Error {
  constructor(message: string, options?: { code?: string; cause?: unknown }) {
    super(message, { cause: options?.cause }); // Error cause 标准属性
    this.name = "ServiceError";
  }
}

try {
  await db.query(sql);
} catch (err) {
  throw new ServiceError("查询任务失败", { code: "DB_ERROR", cause: err });
  // cause 保留原始堆栈，排查时不丢失根因
}
```

## 🛠️ Hono 集中式错误处理

### 注册错误出口：app.onError

与"四参错误中间件"的老模式不同，Hono 的错误出口是一个显式注册点，且**注册位置无关**（写在前在后都拦截全站）：

```ts
import { Hono } from "hono";
import type { ContentfulStatusCode } from "hono/utils/http-status";

interface AppError extends Error {
  status?: number;
  code?: string;
}

const app = new Hono();

app.onError((err, c) => {
  // AppError 是 interface（编译期被擦除），不能用于 instanceof；按结构断言取 status。
  // c.json 的第二参要求 ContentfulStatusCode，动态计算出的 number 需显式收窄。
  const status = ((err as AppError).status ?? 500) as ContentfulStatusCode;

  // 500 及以上必须记录；4xx 属于客户端问题，按需记录
  if (status >= 500) {
    console.error(`[500] ${c.req.method} ${c.req.path}`, err);
  }

  return c.json(
    {
      error: {
        code: (err as AppError).code ?? "INTERNAL_ERROR",
        message:
          status >= 500 && process.env.NODE_ENV === "production"
            ? "服务器内部错误"        // 生产环境不泄露内部细节
            : err.message,
      },
    },
    status,
  );
});

// 未匹配路由的 404 不是错误：单独注册 notFound 出口
app.notFound((c) => c.json({ error: { code: "NOT_FOUND" } }, 404));
```

### 业务错误统一抛出

```ts
class HttpError extends Error {
  status: number;
  code: string;
  constructor(status: number, message: string, code: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

// 路由中只管抛
app.get("/users/:id", async (c) => {
  const user = await db.findUser(c.req.param("id"));
  if (!user) {
    throw new HttpError(404, "用户不存在", "USER_NOT_FOUND");
  }
  return c.json(user);
});
// Hono 自动把 throw 的错误送进 onError
```

## 🛠️ 进程级兜底

任何逃逸的错误最终到达进程层。**默认策略：记日志、清理、退出，交给进程管理器重启**。

```ts
// src/fatal.ts —— 在应用入口最先 import
import process from "node:process";

process.on("uncaughtException", (err) => {
  console.error("未捕获异常，进程即将退出", err);
  process.exit(1);
});

process.on("unhandledRejection", (reason) => {
  console.error("未处理的 Promise 拒绝", reason);
  process.exit(1);
});

process.on("SIGTERM", () => console.log("收到 SIGTERM")); // 优雅退出见 02-first-server
```

要点：

- `uncaughtException` 后 **Node 文档明确不建议继续运行**——正确姿势是退出并让 systemd/K8s 重启
- `unhandledRejection` 的默认处理曾随 Node 版本变化，也可由 `--unhandled-rejections` 改写；不要把某个默认模式当作恢复策略。入口应记录失败并以受监督的方式退出。
- 兜底处理器里只做同步日志，不要再启动可能抛错的异步操作

## 🎨 最佳实践

在应用边界统一错误响应形状，业务内部保留可区分的原因。能恢复的操作在局部处理，未知错误交给边界兜底；“统一出口”不意味着所有代码只能有一个 catch。

cause 链帮助保留底层原因，日志经过脱敏后记录上下文，客户端只得到安全消息。对无法保证继续运行正确的进程状态制定退出与监督重启策略，但不能把普通请求异常都当作必须崩溃。测试错误发生后是否返回预期状态且没有留下部分写入。

## ❓ 常见问题

### Q1: 我的 async 路由抛错，客户端拿到的是什么？

**A**: Hono 默认返回 500 文本。注册 `app.onError` 后由你接管格式；也可能是你在处理器里 try/catch 吞掉了错误后没返回响应。

### Q2: 错误日志里堆栈很乱看不到根因？

**A**: 用 `err.cause` 层层包装后，打印顶层错误不会带出 cause 堆栈。日志库（如 pino）序列化时记得开启 err 序列化器输出 cause 链。

## 🎯 练习与实践

### 练习一：给路由加上完整错误流

**任务要求**:
1. 在 05 课的任务清单 API 上实现 `HttpError` 与 `app.onError`
2. 制造三类错误：校验失败（400）、查不到资源（404）、模拟数据库宕机（503）
3. 验证三者都从同一出口输出统一格式

### 练习二：可观察的崩溃

**挑战任务**:
- 写一个每 100 次请求抛一次 `uncaughtException` 的"故障服务"
- 观察：进程退出后，验证由进程管理器（systemd 或 docker `restart: always`）自动拉起

**提示**: 容器场景在 Dockerfile 的 CMD 直接跑 node，重启交给编排层。

---

## 🔗 相关文档

- 📄 **[路由与中间件](./05-http-routing.md)** — 中间件抛错与洋葱模型的交互语义
- 📄 **[Stream 与 Worker](./07-streams-workers.md)** — 流中的错误传播与 `pipeline` 兜底
- 📄 **[常见故障排除](../reference/quick-references/02-troubleshooting.md)** — 内存泄漏与崩溃排查


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
