# 进程生命周期与信号速查

> **文档简介**: Node 进程从启动到退出的字典式速查——exit code、SIGTERM/SIGINT 信号处理、优雅退出模式（server.close + 超时强退）、uncaughtException/unhandledRejection 处置原则

> **目标读者**: 需要容器化部署（K8s/Docker 停机信号）、兜底全局错误、零丢请求停机的开发者

> **前置知识**: [错误处理教程](../../basics/06-error-handling.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐⭐ |
| **标签** | `#exit code` `#SIGTERM` `#优雅退出` `#uncaughtException` `#容器化` |
| **更新日期** | `2026年9月` |

</details>

## 1. 退出码

### 定义
进程退出时向父进程（容器运行时、shell、CI）返回的整数；0 表示成功，非 0 表示各类失败。编排系统靠它决定是否重启容器。

| 退出方式 | 典型退出码（请在目标 Node 版本确认） |
|---------|----------------------|
| 事件循环自然走空 | `0` |
| `process.exit(7)` | `7`（调用参数即退出码） |
| `process.exitCode = 3` 后自然退出 | `3` |
| 未捕获异常（uncaughtException） | `1` |
| 未处理 rejection（默认抛出） | `1` |
| 致命错误（如内部堆栈耗尽） | 非 0 的特定码 |

### 陷阱
- ❌ 用 `process.exit(1)` 表达"要失败了"——立即硬退，会截断 stdout 异步刷写、不会等待异步清理，exit 监听仍会同步触发
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
| SIGSTOP | Unix 作业控制 | 不可捕获 | 暂停 |
| SIGCONT | Unix 作业控制 | 可监听，平台支持有差异 | 继续运行 |

### 陷阱
- ❌ 注册了 SIGTERM 处理器却在里面永远不退出——容器等满宽限期后直接 SIGKILL，优雅停机白做
- ✅ 处理器必须保证"最终会退出"：正常路径 `server.close()` 回调退出，兜底超时强退（见下节）
- ❌ 双击两次 Ctrl+C 期待更快退出而第一次处理器还在等清理——第二次信号默认又进同一个处理器
- ✅ 用 `closing` 标志位去重，或第二次信号直接 `process.exit`

## 3. 优雅退出模式（应用集成模板）

### 定义
收到停机信号后：停止接新请求 → 等存量请求处理完 → 释放资源 → 退出；全程有超时兜底，绝不无限等待。

```ts
// 集成模板：handler 与 closeDependencies 由应用提供；此模板未在本轮执行
import { createServer } from "node:http";

const server = createServer(handler);
server.listen(3000);
let closing = false;

async function shutdown(signal: string) {
  if (closing) return;
  closing = true;
  console.log(`got ${signal}`);
  const deadline = setTimeout(() => {
    console.error("grace period exceeded");
    process.exit(1); // 最后兜底，可能截断剩余工作
  }, 10_000);
  try {
    await new Promise<void>((resolve, reject) => {
      server.close(error => error ? reject(error) : resolve());
    });
    await closeDependencies(); // 应用实现：关闭池、消费者、定时器并刷新输出
    process.exitCode = 0; // 清理后自然退出，不提前截断
    console.log("closed-clean");
    deadline.unref(); // 若遗留句柄阻止退出，期限到仍会强退
  } catch (error) {
    console.error("shutdown failed", error);
    process.exitCode = 1;
    deadline.unref();
  }
}
process.on("SIGTERM", () => { void shutdown("SIGTERM"); });
process.on("SIGINT", () => { void shutdown("SIGINT"); });
```

- Node 19+ server.close 会处理空闲连接，活跃长请求或升级连接仍需明确策略；closeAllConnections 也不替代对 WebSocket 等升级连接的单独管理
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
  // 本示例显式终止；注册监听会改变默认拒绝处理行为，不能仅记录后继续服务
  process.exit(1);
});
```

### 处置原则
- ❌ 监听 `uncaughtException` 后**不退出继续服务**——进程状态已损坏（部分写入、半完成的事务），继续跑会造成静默数据损坏
- ✅ 兜底处理器的职责只有两件事：**记录 + 安全退出**；防崩溃靠域内 try/catch 与中间件错误处理，不靠全局吞
- ✅ Node 15+ 默认会将未处理 rejection 按抛出处理；不要依赖“警告一下就过去”的旧行为。运行模式和退出码仍应在部署版本确认。
- 用 `--unhandled-rejections=warn` 可临时改回仅警告（排障期用，不上生产）

## 5. process.exit 与"defer 式"清理

### 定义
Node **没有 Go 式 defer**：`process.exit()` 瞬间终止事件循环，所有排队的异步任务（待刷写的 stdout、未完成的 fs 写、数据库 flush）**直接丢弃**。

```ts
// 管道写入可能在进程退出前未完全排空；缓冲大小受平台与运行环境影响，应在目标环境测量。
process.stdout.write("x".repeat(70_000));
process.exit(0);                       // 可能截断；具体字节数取决于平台、输出目标和时序，不能保证恰好 65536

process.stdout.write("x".repeat(70_000));
// 不调 exit：事件循环等刷写完成后自然退出，7 万字节完整到达 ✅
```

### 陷阱
- ❌ 写完日志立刻 `process.exit()`——CI 脚本日志截断、日志采集丢行的经典根因
- ✅ 让 `process.exitCode` + 事件循环自然退出；确需提前退出时给刷写留路：`process.stdout.write` 后监听 drain/finish，或直接同步的 `fs.writeSync(1, ...)`
- 异步资源登记（`process.on('beforeExit')`）只在事件循环自然空闲时触发，`process.exit` 不触发它——不要把清理逻辑寄托在 beforeExit 上

<!-- full-library-explanation -->
## 优雅关停是一个有截止时间的状态转换

前置是 HTTP 服务器、Promise、连接池和定时器。关停顺序通常是标记不再接收新工作、停止入口、等待正在处理的任务、关闭依赖、刷新必要输出，最后自然退出。数据库池若先关闭，仍在处理的请求会失败；若只调用 server.close 却保留轮询定时器或队列消费者，进程可能永不结束。关闭函数应能重复调用，并共享同一个清理过程。

正常关停与未捕获异常的处理不同。前者可以在有限预算内等待已知资源，后者可能处于不一致状态，不宜继续接流量或依赖复杂异步恢复。exit 事件只能做同步清理，beforeExit 不是所有退出路径都会发生。不同操作系统的信号支持存在差异，本页 Unix 容器信号表不能直接当作 Windows 的完整行为说明。

练习：启动一个延迟 200ms 返回的请求，在处理中触发关停函数，已有请求应按设计完成，新请求被拒绝，数据库清理发生在它之后。再制造一个永不完成的请求，截止时间必须让进程以明确失败状态结束。单测直接调用 shutdown 可验证编排；真实 SIGTERM 测试应放在支持该信号的子进程环境，避免测试进程自行退出。

## 🔗 相关文档

- 📄 **[Node 核心模块 API 速查](../language-concepts/03-node-core-api.md)** — `process` 对象成员全集
- 📄 **[错误处理教程](../../basics/06-error-handling.md)** — 日常错误处理（区别于全局兜底）
- 📄 **[node:child_process 子进程速查](./04-child-process.md)** — 父子进程退出码联动
- 📄 **[常见故障排除](../quick-references/02-troubleshooting.md)** — 进程异常退出排查
- 🌐 **[Node.js 官方文档: process](https://nodejs.org/docs/latest/api/process.html)** — 信号与退出事件权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
