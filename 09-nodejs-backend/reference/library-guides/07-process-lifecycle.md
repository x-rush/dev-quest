# 进程生命周期与信号速查

> **文档简介**: Node 进程从启动到退出的字典式速查——exit code、SIGTERM/SIGINT 信号处理、优雅退出模式（server.close + 超时强退）、uncaughtException/unhandledRejection 处置原则

> **目标读者**: 需要容器化部署（K8s/Docker 停机信号）、兜底全局错误、零丢请求停机的开发者

> **前置知识**: [错误处理教程](../../basics/06-error-handling.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐⭐ |
| **标签** | `#exit code` `#SIGTERM` `#优雅退出` `#uncaughtException` `#容器化` |
| **更新日期** | `2026年9月` |

## 1. 退出码

### 定义
进程退出时向父进程（容器运行时、shell、CI）返回的整数；0 表示成功，非 0 表示各类失败。编排系统靠它决定是否重启容器。

| 退出方式 | 退出码（Node 24 实测） |
|---------|----------------------|
| 事件循环自然走空 | `0` |
| `process.exit(7)` | `7`（调用参数即退出码） |
| `process.exitCode = 3` 后自然退出 | `3` |
| 未捕获异常（uncaughtException） | `1` |
| 未处理 rejection（默认抛出） | `1` |
| 致命错误（如内部堆栈耗尽） | 非 0 的特定码 |

### 陷阱
- ❌ 用 `process.exit(1)` 表达"要失败了"——立即硬退，会截断 stdout 异步刷写、跳过所有清理钩子
- ✅ 设置 `process.exitCode = 1` 让进程走完事件循环自然退出；仅在最紧急（如配置缺失启动即失败）才用 `process.exit`
- ❌ 把业务错误映射成 exit code 写一大堆约定——容器场景 0/非 0 足够，细节交给日志

## 2. 信号：SIGTERM 与 SIGINT

### 定义
进程间单向通知；容器停止发 **SIGTERM**，终端 Ctrl+C 发 **SIGINT**，杀不掉时超时强发 **SIGKILL**（不可捕获、不可忽略）。

```ts
process.on("SIGTERM", () => { /* 优雅停机 */ });   // docker stop / k8s delete pod
process.on("SIGINT",  () => { /* Ctrl+C */ });
process.on("SIGHUP",  () => { /* 终端断开 */ });

process.kill(process.pid, "SIGTERM");   // 向进程发信号（名字叫 kill，本质是发信号）
```

| 信号 | 来源 | 可捕获 | 默认行为 |
|------|------|--------|---------|
| `SIGTERM` | 容器/kill 命令 | ✅ | 退出 |
| `SIGINT` | Ctrl+C | ✅ | 退出 |
| `SIGHUP` | 终端关闭 | ✅ | 退出 |
| `SIGKILL` | 强杀兜底 | ❌ **无法捕获** | 立即退出 |
| `SIGSTOP`/`SIGCONT` | 作业控制 | ❌ | 暂停/恢复 |

### 陷阱
- ❌ 注册了 SIGTERM 处理器却在里面永远不退出——容器等满宽限期后直接 SIGKILL，优雅停机白做
- ✅ 处理器必须保证"最终会退出"：正常路径 `server.close()` 回调退出，兜底超时强退（见下节）
- ❌ 双击两次 Ctrl+C 期待更快退出而第一次处理器还在等清理——第二次信号默认又进同一个处理器
- ✅ 用 `closing` 标志位去重，或第二次信号直接 `process.exit`

## 3. 优雅退出模式（实测模板）

### 定义
收到停机信号后：停止接新请求 → 等存量请求处理完 → 释放资源 → 退出；全程有超时兜底，绝不无限等待。

```ts
// Node 24 实测：SIGTERM 后输出 got SIGTERM -> closed-clean，退出码 0
import { createServer } from "node:http";

const server = createServer(handler);
server.listen(3000);

let closing = false;
async function shutdown(signal: string) {
  if (closing) return;            // 第二次信号去重
  closing = true;
  console.log(`got ${signal}`);

  // 1) 停止接新连接，等待存量请求完成
  server.close(() => {
    console.log("closed-clean");
    process.exit(0);
  });

  // 2) 兜底：宽限期内关不完就强退（unref 不阻止进程只等这一个定时器）
  setTimeout(() => {
    console.error("grace period exceeded, force exit");
    process.exit(1);
  }, 10_000).unref();

  // 3) 视需要：断开数据库连接池、刷新指标、通知注册中心
}
process.on("SIGTERM", () => shutdown("SIGTERM"));
process.on("SIGINT", () => shutdown("SIGINT"));
```

- keep-alive 长连接会拖住 `server.close()`：Node 19+ 的 `closeIdleConnections()` / `closeAllConnections()` 可强制收口
- K8s 场景记得让 `terminationGracePeriodSeconds` > 代码里的宽限时长

## 4. uncaughtException 与 unhandledRejection

### 定义
两个全局兜底事件：同步异常逃逸到顶层触发前者；Promise 无 catch 触发后者。**默认行为都是打印错误并退出（码 1）**。

```ts
process.on("uncaughtException", (err, origin) => {
  // origin: 'uncaughtException' | 'unhandledRejection'
  logger.fatal({ err, origin }, "uncaught");   // 先记录
  process.exit(1);                             // 再退出——状态已不可信
});

process.on("unhandledRejection", (reason) => {
  logger.error({ err: reason }, "unhandled rejection");
  // 生产建议同样记录后退出（或配合监控告警再决定）；吞掉等于埋雷
});
```

### 处置原则
- ❌ 监听 `uncaughtException` 后**不退出继续服务**——进程状态已损坏（部分写入、半完成的事务），继续跑会造成静默数据损坏
- ✅ 兜底处理器的职责只有两件事：**记录 + 安全退出**；防崩溃靠域内 try/catch 与中间件错误处理，不靠全局吞
- ✅ `unhandledRejection` 在 Node 15+ 默认就是抛出崩溃（实测退出码 1），不要依赖"警告一下就过去"的旧行为
- 用 `--unhandled-rejections=warn` 可临时改回仅警告（排障期用，不上生产）

## 5. process.exit 与"defer 式"清理

### 定义
Node **没有 Go 式 defer**：`process.exit()` 瞬间终止事件循环，所有排队的异步任务（待刷写的 stdout、未完成的 fs 写、数据库 flush）**直接丢弃**。

```ts
// Node 24 实测：stdout 接管道时，7 万字节只刷出 65536（64 KiB 缓冲边界）
process.stdout.write("x".repeat(70_000));
process.exit(0);                       // ❌ 管道下游只收到 65536 字节

process.stdout.write("x".repeat(70_000));
// 不调 exit：事件循环等刷写完成后自然退出，7 万字节完整到达 ✅
```

### 陷阱
- ❌ 写完日志立刻 `process.exit()`——CI 脚本日志截断、日志采集丢行的经典根因
- ✅ 让 `process.exitCode` + 事件循环自然退出；确需提前退出时给刷写留路：`process.stdout.write` 后监听 drain/finish，或直接同步的 `fs.writeSync(1, ...)`
- 异步资源登记（`process.on('beforeExit')`）只在事件循环自然空闲时触发，`process.exit` 不触发它——不要把清理逻辑寄托在 beforeExit 上

## 🔗 相关文档

- 📄 **[Node 核心模块 API 速查](../language-concepts/03-node-core-api.md)** — `process` 对象成员全集
- 📄 **[错误处理教程](../../basics/06-error-handling.md)** — 日常错误处理（区别于全局兜底）
- 📄 **[node:child_process 子进程速查](./04-child-process.md)** — 父子进程退出码联动
- 📄 **[常见故障排除](../quick-references/02-troubleshooting.md)** — 进程异常退出排查
- 🌐 **[Node.js 官方文档: process](https://nodejs.org/docs/latest/api/process.html)** — 信号与退出事件权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
