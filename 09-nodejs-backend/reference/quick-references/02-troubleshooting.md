# 常见故障排除

> **文档简介**: Node 后端高频故障的症状→定位→修复速查：内存泄漏、事件循环阻塞、ESM 兼容坑、模块解析报错

> **目标读者**: 遇到线上或开发期异常、需要快速定位的 Node 开发者

> **前置知识**: [错误处理](../../basics/06-error-handling.md)，[Stream 与 Worker](../../basics/07-streams-workers.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐⭐ |
| **标签** | `#内存泄漏` `#事件循环` `#ESM` `#故障排除` |
| **更新日期** | `2026年9月` |

</details>

## 1. 内存泄漏

### 症状
RSS/heapUsed 随运行时间单调上升不回落；容器 OOMKilled；`Allocation failed - JavaScript heap out of memory` 崩溃。

### 定位

```bash
# 1) 观察趋势：两次采样对比增量
node -e "setInterval(()=>{const m=process.memoryUsage();console.log(m.rss/1024**2,'MB RSS')},5000)"
# 上面仅演示采样 API；诊断真实服务应把同样采样接入目标进程

# 2) 抓堆快照（DevTools Memory 面板对比两份快照的 Retained Size）
kill -USR1 "${TARGET_PID:?先设置目标Node进程的PID}"          # 开调试端口后用 chrome://inspect 抓快照
node --heap-prof server.js

# 3) 查 GC 行为
node --trace-gc server.js # 观察 GC 频率与回收量
```

### 高频根因

| 根因 | 典型代码 | 修复 |
|------|---------|------|
| 无界缓存 | `const cache = new Map()` 永不清理 | 用 `lru-cache` 限容量 + TTL |
| 忘记解绑监听器 | 每请求 `emitter.on(...)` | 用原函数引用 off；EventEmitter.on 不接收 signal，events.on 异步迭代器才支持取消选项 |
| 闭包持有大对象 | handler 捕获了巨大 buffer | 用完置 null / 缩小作用域 |
| 未 end 的流 | 只写不关，缓冲堆积 | `pipeline` + `end()` |
| setInterval 泄漏 | 组件销毁未 clearInterval | 可取消的 timers/promises |

**`MaxListenersExceededWarning` 是排查线索，不是泄漏的证明**。确认监听器是否随请求持续增加，以及生命周期结束后是否解除。

## 2. 事件循环阻塞

### 症状
延迟尖刺但 CPU 未满；定时器漂移；健康检查超时；日志出现明显的时间断层。

### 定位

```bash
node --cpu-prof server.js       # 复现后分析 .cpuprofile：找长任务函数
node --prof server.js           # --prof-process 输出 ticks 热点
```

代码内快速探针（事件循环延迟监测）：

```ts
import { monitorEventLoopDelay } from "node:perf_hooks";

const h = monitorEventLoopDelay({ resolution: 20 });
h.enable();
setInterval(() => {
  console.log("P99 延迟 ms:", h.percentile(99) / 1e6);
  h.reset();
}, 5_000).unref();
// 与基线比较；CPU 争抢、GC 与同步长任务都可能使延迟升高
```

### 高频根因与修复

| 根因 | 修复 |
|------|------|
| 同步 IO（`readFileSync`/`execSync`）在请求路径 | 换异步 API；启动期初始化才允许同步 |
| CPU 密集计算（JSON 大解析、图像、加密） | 移入 Worker Threads 或拆小批处理 |
| 超大 JSON.parse / stringify | 流式解析或分页 |
| `process.nextTick` 递归 | 改 `setImmediate` |
| 正则灾难性回溯 | 重写正则或改用 re2 库 |

## 3. ESM 兼容坑

### 症状与修复对照

| 报错 | 原因 | 修复 |
|------|------|------|
| `Cannot use import statement outside a module` | 无 `"type": "module"`，.js 按 CJS 解析 | 加 type 字段或改名 `.mjs` |
| `ERR_MODULE_NOT_FOUND` | ESM 相对导入缺扩展名 | 补全 `./x.js` |
| `require is not defined in ES module scope` | ESM 里用 require | `await import()` 或 `createRequire` |
| `__dirname is not defined` | ESM 无该全局 | `import.meta.dirname` |
| `ERR_REQUIRE_ESM` | CJS require 了 ESM 包 | 动态 import；Node 22+ 已支持 `require(esm)`（同步加载无顶层 await 的 ESM） |
| `ERR_UNSUPPORTED_DIR_IMPORT` | 导入目录省略 index.js | 写全 `./dir/index.js` |
| 装饰器报错 | 原生类型剥离不支持装饰器 | 走 tsc/swc 编译（NestJS 项目必然如此） |

```ts
// ESM 中的常用替代三件套
import { createRequire } from "node:module";
const require_ = createRequire(import.meta.url);
const mod = await import("./lazy.js");            // 条件/惰性加载
// __dirname / __filename → import.meta.dirname / import.meta.filename
```

## 4. 模块与依赖类报错

| 报错 | 修复 |
|------|------|
| `ERR_PACKAGE_PATH_NOT_EXPORTED` | 包的 `exports` 未开放该子路径；用官方入口或换包 |
| `MODULE_NOT_FOUND`（CJS） | 检查相对路径拼写、node_modules 是否安装、pnpm 幽灵依赖 |
| `ERR_INVALID_PACKAGE_TARGET` | 包 exports 配置错误，多为三方包 bug，锁旧版或提 issue |
| peer dependency 冲突 | `pnpm ls <pkg>` 查版本矩阵，按提示对齐主版本 |

## 5. HTTP 服务类故障

| 症状 | 排查 |
|------|------|
| `EADDRINUSE` | `lsof -i :3000` 找占用进程；或换端口 |
| `ECONNRESET` 大量出现 | 连接被重置：结合两端日志检查取消、代理与超时，不只一种原因 |
| 请求体解析失败 415 | Content-Type 与解析中间件不匹配（Fastify 对未知类型默认 415） |
| `RequestAbortedError` | 检查主动取消、超时和底层原因；配置 AbortSignal.timeout，并区分取消与网络故障 |
| `ERR_HTTP_HEADERS_SENT` | handler 中有多个响应出口，分支加 `return` |

## 6. 进程异常退出类

| 现象 | 处理 |
|------|------|
| `unhandledRejection` 崩溃 | Node 15+ 默认行为；全仓排查缺 `.catch` 的异步调用，配合 ESLint `no-floating-promises` |
| 容器重启循环 | `docker logs` / `kubectl logs --previous` 看崩溃原因；确认监听 `0.0.0.0` 而非 `127.0.0.1` |
| 优雅退出超时被杀 | `SIGTERM` 处理器里 `server.close()` + 连接池 drain，并校验宽限期配置 |
| `EMFILE` 句柄耗尽 | 流未关闭或高频短连接；`ulimit -n` 调整 + 复查 `end()`/`destroy()` |

## 7. 排障通用流程

1. **先看完整报错与堆栈**：`node --trace-warnings`、`--trace-uncaught` 补全信息
2. **二分复现**：注释业务模块定位引入点，或 `git bisect`
3. **最小复现脚本**：10 行内复现 → 判断是自身代码还是依赖
4. **查运行时差异**：本地/线上 Node 版本、`NODE_ENV`、环境变量逐项对比
5. **升级验证**：Node 24 patch 版本常含修复，`node -v` 先行确认

---

<!-- full-library-explanation -->
## 把症状变成可以推翻的假设

“内存涨”至少可能是缓存预热、业务持有对象、Buffer 占用或原生分配器保留内存。先对同一个服务采样 RSS、heapUsed、external 和请求量；另起 node -e 只能观察新进程，不能替代目标进程指标。堆快照比较应在相似负载阶段进行，快照本身也会占用内存和暂停执行。

模块解析错误同样需要分层：先记录 Node 版本、执行路径、package.json 的 type、实际导入字符串，再检查文件是否存在以及包 exports 是否允许访问。不要用“删除所有锁文件并升级”同时改变多个变量，否则无法知道修复来自哪里。

**练习**：建立两个小服务，一个保留每次请求的数据到数组，另一个只维护计数器。以相同负载观察多轮采样，比较可达对象的增长；验收是找到保留引用的位置。对 ECONNRESET 记录发生在读、写还是 TLS 建连阶段，结合两端超时和日志验证假设，不能仅凭错误名断言客户端主动断开。

## 🔗 相关文档

- 📄 **[Node 一行式速查](./01-node-cheatsheet.md)** — 本页用到的诊断命令全集
- 📄 **[错误处理教程](../../basics/06-error-handling.md)** — 进程级兜底的正确姿势
- 📄 **[模块系统与 ESM](../../basics/03-modules-esm.md)** — ESM 解析规则详解


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
