# 流处理与集群：Stream 背压与多进程扩展

> **文档简介**: 解析 Node 两大扩展武器的设计原理与适用边界——用 Stream pipeline 分批处理大型数据流，用 cluster/worker_threads 突破单核上限，并给出选型决策树
>
> **目标读者**: 面对大文件/高并发场景、需要水平扩展能力的中高级后端开发者
>
> **前置知识**: [事件循环原理](01-event-loop.md)、[Stream API 速查](../../reference/language-concepts/04-streams-api.md)、[Stream 管道与多线程](../../basics/07-streams-workers.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#stream` `#backpressure` `#cluster` `#worker-threads` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 阅读目标

- 理解背压是"流式内存恒定"的根本机制，以及 pipeline 如何管理它
- 分清 cluster 与 worker_threads 解决的是两类不同瓶颈
- 掌握生产环境的多进程部署形态（PM2/K8s 下的取舍）

## 1. Stream：为什么内存不随数据量增长

一次读入大型 CSV 需要容纳原始数据及解析结果。采用有界缓冲、限制记录大小且不积累全部结果的流处理，可以让内存主要取决于窗口大小。支撑这一切的核心机制是**背压（backpressure）**：

```text
读文件(100MB/s) → 解析转换 → 网络写出(50MB/s)
                    ↑
        写出端跟不上时，往上游逐级"减速"：
        write() 返回 false → 暂停读 → 缓冲队列清空后恢复
```

**手动管理背压极易出错**（要监听 drain、暂停恢复读端），所以在适合的流组合中优先用 `pipeline` 或能控制消费速度的异步迭代：

先安装 `csv-parse`。下面是可复用的导入函数；由调用方传入保存一批记录的函数。解析器处理引号、跨块字符与换行，并限制单条记录大小。

```typescript
import { createReadStream } from 'node:fs';
import { pipeline } from 'node:stream/promises';
import { parse } from 'csv-parse';

type UserInput = { name: string; email: string };
export async function importUsersCsv(
  filePath: string,
  saveRows: (rows: UserInput[]) => Promise<void>,
): Promise<number> {
  let total = 0;
  await pipeline(
    createReadStream(filePath),
    parse({ columns: true, bom: true, max_record_size: 64 * 1024 }),
    async (rows) => {
      let batch: UserInput[] = [];
      for await (const row of rows) {
        if (typeof row.name !== 'string' || typeof row.email !== 'string') {
          throw new Error('CSV 必须包含 name 和 email 列');
        }
        batch.push({ name: row.name, email: row.email });
        if (batch.length === 500) {
          await saveRows(batch); // 等待完成再继续消费
          total += batch.length;
          batch = [];
        }
      }
      if (batch.length) {
        await saveRows(batch);
        total += batch.length;
      }
    },
  );
  return total;
}
```

这只验证列存在；邮箱格式、重复记录与权限属于业务校验。每批保存成功就可能已经提交：第 501 行失败不会撤销前 500 行。需要原子导入时应先进入暂存区并验证，再提交；可恢复导入则记录批次和幂等键。

**原理要点**：`pipeline` 串联的每一段都会传播背压并统一销毁（任一环节出错，全部流被清理，不会泄漏 fd）。Web 场景同理——把 S3 文件流直接 `pipeline` 给 `res`（见 [`../../projects/03-file-storage-service.md`](../../projects/03-file-storage-service.md)），服务端内存不随文件大小波动。

## 2. cluster：突破单核上限

单个 JavaScript 执行线程不能并行执行多个回调，但 Node 进程中的线程池等可以使用多个核。`cluster` 用 fork 出多个进程共享同一端口：

```typescript
// server.ts：演示共享端口。重启策略交给外部进程管理器。
import cluster from 'node:cluster';
import { availableParallelism } from 'node:os';
import { serve } from '@hono/node-server';
import app from './app.js';

if (cluster.isPrimary) {
  // 教学时限制最多 2 个；生产应同时预算 CPU、内存和数据库连接数。
  const workers = Math.min(2, availableParallelism());
  for (let i = 0; i < workers; i++) cluster.fork();
  process.once('SIGTERM', () => cluster.disconnect());
  cluster.on('exit', (worker, code) => {
    console.error(`worker ${worker.process.pid} 退出(${code})`);
  });
} else {
  const server = serve({ fetch: app.fetch, port: 3000 });
  process.once('SIGTERM', () => server.close());
}
```

这是启动结构示意；数据库池、任务队列、WebSocket 和超时兜底仍要单独关闭。不要无条件在 `exit` 时 fork，否则主动停机也会触发重启。

两个必须理解的生产细节：

- **请求分发不是负载均衡**：cluster 在 Windows 之外默认由主进程采用轮转方式分发连接，Windows 默认由操作系统分发，连接在 worker 间分布可能不均，长连接建立后固定在某个 worker；需要根据连接负载和会话要求选择网关策略
- **进程间内存隔离**：内存限流、内存 session 在多 worker 下各算各的——这就是 [`../../projects/04-production-nodejs-api.md`](../../projects/04-production-nodejs-api.md) 强制 Redis 限流的原因

> PM2 `cluster` 模式是以上逻辑的开箱即用版（`pm2 start -i max`）；K8s 部署则通常让容器内保持单进程，用 Pod 副本数做水平扩展——每种形态都要想清楚"谁在分流量"。

## 3. worker_threads：CPU 密集的正确出口

**cluster 与 worker_threads 解决的是不同问题**：

| 维度 | cluster | worker_threads |
|------|---------|---------------|
| 目标 | 提升 I/O 吞吐（多核处理更多请求） | 卸载单次 CPU 重计算 |
| 粒度 | 整个应用实例 | 单个任务/函数 |
| 通信 | 无共享（各自独立事件循环） | 可共享内存（SharedArrayBuffer）、消息传递 |

```typescript
// Piscina 的工作模块需要导出函数；heavyCompress 为业务提供的实现。
import { heavyCompress } from './compression.js';
export default function compressTask({ filePath }: { filePath: string }) {
  return heavyCompress(filePath);
}
```

```typescript
// pool.ts —— 生产推荐 piscina：线程池化 + 任务队列开箱即用
import Piscina from 'piscina';

const pool = new Piscina({
  filename: new URL('./worker.js', import.meta.url).href,
  maxThreads: 4,
  maxQueue: 32, // 超过容量时拒绝，调用方应返回可重试错误
});

export const compress = (filePath: string) => pool.run({ filePath });
```

**决策树**：

```text
任务是什么？
├─ I/O 密集（DB/网络/文件读写）→ 不需要多线程！优化索引/连接池/缓存即可
├─ 偶发的 CPU 突刺 → worker_threads（线程池）
└─ 单进程计算饱和且下游仍有容量→ cluster / 水平扩容
```

## 4. 反模式与陷阱

- ❌ 把所有慢都归咎"单线程"而上 cluster——先确认不是 N+1 查询或缺索引
- ❌ worker 之间用数据库轮询传递状态——用消息传递，线程/进程边界即通信边界
- ❌ cluster 模式下继续用内存态（本地缓存当事实源、内存 session）
- ❌ 缓冲设得过大、忽略 write() 返回值或业务层积累全部数据——内存仍可能耗尽；`.pipe()` 本身支持背压，但错误清理需额外处理

<!-- full-library-explanation -->
## 用慢消费者验证背压

背压是一种生产与消费的协商：写端达到阈值后，上游暂停提供更多数据。`highWaterMark` 是缓冲阈值，不能当作整个进程的硬内存上限。对象模式按对象数量计数，一个对象仍可能非常大；解析器和业务数组也可能另外持有数据。

**练习**：让 `saveRows` 每批延迟 100ms，分别导入 1 万与 10 万条固定大小记录，观察内存是否趋于平台，并检查最终条数。加入带逗号和引号的姓名、跨行字段及末尾无换行记录，确认解析仍正确。再让第三批保存失败，记录此前已经成功的批次，而非宣称导入全部回滚。

扩容同样需要资源预算：4 个进程各建 20 个数据库连接，就是最多 80 个连接；线程池必须限制排队任务数，否则主线程不再卡顿，却可能因排队数据耗尽内存。

依据：[Node cluster 调度](https://nodejs.org/api/cluster.html)、[Piscina 工作函数约定](https://piscinajs.dev/getting-started/Basic%20Usage/)。

## 🔗 相关文档

- 📖 [Stream API 速查](../../reference/language-concepts/04-streams-api.md) — pipeline/背压字典条目
- 📄 [事件循环原理](01-event-loop.md) — 阻塞检测先行，再谈多进程
- 📄 [Stream 管道与多线程](../../basics/07-streams-workers.md) — 教程版入门
- 📄 [文件存储服务](../../projects/03-file-storage-service.md) — 流式上传下载的实战应用


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
