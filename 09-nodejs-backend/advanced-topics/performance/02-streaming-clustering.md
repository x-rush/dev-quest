# 流处理与集群：Stream 背压与多进程扩展

> **文档简介**: 解析 Node 两大扩展武器的设计原理与适用边界——用 Stream pipeline 消化无限大数据流，用 cluster/worker_threads 突破单核上限，并给出选型决策树
>
> **目标读者**: 面对大文件/高并发场景、需要水平扩展能力的中高级后端开发者
>
> **前置知识**: [事件循环原理](01-event-loop.md)、[Stream API 速查](../../reference/language-concepts/04-streams-api.md)、[Stream 管道与多线程](../../basics/07-streams-workers.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#stream` `#backpressure` `#cluster` `#worker-threads` |
| **更新日期** | `2026年9月` |

## 🎯 阅读目标

- 理解背压是"流式内存恒定"的根本机制，以及 pipeline 如何管理它
- 分清 cluster 与 worker_threads 解决的是两类不同瓶颈
- 掌握生产环境的多进程部署形态（PM2/K8s 下的取舍）

## 1. Stream：为什么内存不随数据量增长

一次读完 10GB CSV 需要 10GB+ 内存且必然 GC 风暴；流式处理则把内存压到常数级。支撑这一切的核心机制是**背压（backpressure）**：

```text
读文件(100MB/s) → 解析转换 → 网络写出(50MB/s)
                    ↑
        写出端跟不上时，往上游逐级"减速"：
        write() 返回 false → 暂停读 → 缓冲队列清空后恢复
```

**手动管理背压极易出错**（要监听 drain、暂停恢复读端），所以工程上永远用 `pipeline`：

```typescript
// 大 CSV 导入：内存占用恒定在缓冲区级别，与文件大小无关
import { createReadStream } from 'node:fs';
import { pipeline } from 'node:stream/promises';
import { Transform, type TransformCallback } from 'node:stream';
import { prisma } from '../../lib/prisma.js';

export async function importUsersCsv(filePath: string): Promise<number> {
  let total = 0;
  let batch: string[][] = [];

  const flush = async () => {
    if (batch.length === 0) return;
    await prisma.user.createMany({ data: batch.map(toUser) });
    total += batch.length;
    batch = [];
  };

  const parseLines = new Transform({
    objectMode: true,
    transform(chunk: Buffer, _enc: BufferEncoding, cb: TransformCallback) {
      for (const line of chunk.toString().split('\n')) {
        if (line.trim()) this.push(line.split(',')); // 逐行推入下游
      }
      cb(); // 数据量是否超速由下游的 highWaterMark 反压决定
    },
  });

  const batchSave = new Transform({
    objectMode: true,
    highWaterMark: 500, // 下游缓冲阈值：攒批写库，吞吐远高于逐行 insert
    transform(row: string[], _enc: BufferEncoding, cb: TransformCallback) {
      batch.push(row);
      if (batch.length >= 500) {
        flush().then(() => cb()).catch(cb); // flush 完成才放行——天然限速
      } else {
        cb();
      }
    },
    async flush(cb: TransformCallback) {
      try {
        await flush(); // 流结束前清空尾批
        cb();
      } catch (e) {
        cb(e as Error);
      }
    },
  });

  await pipeline(createReadStream(filePath), parseLines, batchSave);
  return total;
}
```

**原理要点**：`pipeline` 串联的每一段都会传播背压并统一销毁（任一环节出错，全部流被清理，不会泄漏 fd）。Web 场景同理——把 S3 文件流直接 `pipeline` 给 `res`（见 [`../../projects/03-file-storage-service.md`](../../projects/03-file-storage-service.md)），服务端内存不随文件大小波动。

## 2. cluster：突破单核上限

Node 默认只用一个核。`cluster` 用 fork 出多个进程共享同一端口：

```typescript
// server.ts —— 多进程：每核一个 worker
import cluster from 'node:cluster';
import { availableParallelism } from 'node:os';
import app from './app.js';

if (cluster.isPrimary) {
  const workers = availableParallelism(); // 容器里等于 CPU limit，恰好匹配配额
  for (let i = 0; i < workers; i++) cluster.fork();

  cluster.on('exit', (worker, code) => {
    console.error(`worker ${worker.process.pid} 退出(${code})，重启`);
    cluster.fork(); // 自愈：崩掉的 worker 自动补位
  });
} else {
  const server = app.listen(3000);
  // 优雅关闭在每个 worker 内各自生效（见 projects/04）
  process.on('SIGTERM', () => server.close());
}
```

两个必须理解的生产细节：

- **请求分发不是负载均衡**：cluster 默认由操作系统抢占式分发（除 Windows 外），连接在 worker 间分布可能不均，长连接（WebSocket）场景必须配 Nginx `least_conn` 或网关侧均衡
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
// worker.ts —— CPU 密集任务（图片压缩/大数据聚合）在独立线程执行
import { parentPort, workerData } from 'node:worker_threads';

const result = heavyCompress(workerData.filePath); // 同步也无所谓：不占主线程
parentPort!.postMessage(result);
```

```typescript
// pool.ts —— 生产推荐 piscina：线程池化 + 任务队列开箱即用
import Piscina from 'piscina';

const pool = new Piscina({
  filename: new URL('./worker.js', import.meta.url).href,
  maxThreads: 4,
});

export const compress = (filePath: string) => pool.run({ filePath });
```

**决策树**：

```text
任务是什么？
├─ I/O 密集（DB/网络/文件读写）→ 不需要多线程！优化索引/连接池/缓存即可
├─ 偶发的 CPU 突刺 → worker_threads（线程池）
└─ 整体吞吐不足（每核都忙但都是 I/O 等待）→ cluster / 水平扩容
```

## 4. 反模式与陷阱

- ❌ 把所有慢都归咎"单线程"而上 cluster——先确认不是 N+1 查询或缺索引
- ❌ worker 之间用数据库轮询传递状态——用消息传递，线程/进程边界即通信边界
- ❌ cluster 模式下继续用内存态（本地缓存当事实源、内存 session）
- ❌ 无界 `highWaterMark` 或手动 `.pipe()`——背压断裂，内存照样爆炸

## 🔗 相关文档

- 📖 [Stream API 速查](../../reference/language-concepts/04-streams-api.md) — pipeline/背压字典条目
- 📄 [事件循环原理](01-event-loop.md) — 阻塞检测先行，再谈多进程
- 📄 [Stream 管道与多线程](../../basics/07-streams-workers.md) — 教程版入门
- 📄 [文件存储服务](../../projects/03-file-storage-service.md) — 流式上传下载的实战应用
