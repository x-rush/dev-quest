# Stream API 速查

> **文档简介**: Stream 四种类型的核心方法、事件、`pipeline` 与背压机制的字典式速查

> **目标读者**: 需要确认流 API 细节或排查流相关故障的开发者

> **前置知识**: [Stream 与 Worker 教程](../../basics/07-streams-workers.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐⭐ |
| **标签** | `#Readable` `#Writable` `#Transform` `#pipeline` `#背压` |
| **更新日期** | `2026年9月` |

## 1. 四种流类型

### 定义与代表

| 类型 | 读 | 写 | 典型实例 |
|------|:--:|:--:|---------|
| `Readable` | ✅ | — | `fs.createReadStream`、`process.stdin`、HTTP `req` |
| `Writable` | — | ✅ | `fs.createWriteStream`、`process.stdout`、HTTP `res` |
| `Duplex` | ✅ | ✅（独立通道） | TCP `net.Socket`、WebSocket |
| `Transform` | ✅ | ✅（读写关联） | `zlib.createGzip()`、自定义转换 |

### 消费 Readable 的三种方式

```ts
// 1) pipeline（推荐）：自动背压 + 错误聚合
await pipeline(readable, writable);

// 2) for await（适合逐 chunk 处理，注意手动实现背压）
for await (const chunk of readable) {
  process(chunk);
}

// 3) 事件式（老代码，易漏背压）
readable.on("data", (chunk) => process(chunk));
readable.on("end", finish); readable.on("error", fail);
```

### 陷阱
- `on("data")` 会**立即开始流动模式**，注册前错过的事件不会重放；未处理 error 会崩溃
- `readable.pause()` 后不 `resume()` 也不消费，源端会被阻塞

## 2. Writable 关键成员

### 定义
写入端 API，`write()` 返回值即背压信号。

### 语法与示例

```ts
const ok = writable.write(chunk);   // false = 内部缓冲超阈值（highWaterMark）
if (!ok) readable.pause();          // 生产端应暂停

writable.once("drain", () => {      // 缓冲清空后可继续
  readable.resume();
});

writable.end(finalChunk);           // 通知写入完成（可带最后一块与完成回调）

writable.writableLength;            // 当前缓冲字节数
writable.writableHighWaterMark;     // 缓冲阈值（默认 16KB）
writable.destroy();                 // 强制销毁，触发 close
```

### 陷阱
- `end()` 之后 `write()` 会报 `ERR_STREAM_WRITE_AFTER_END`
- 忘记 `end()` 会造成文件句柄泄漏、下游永远收不到 finish

## 3. Transform 自定义

### 定义
实现 `transform(chunk, encoding, callback)` 即可定义读写关联的转换流。

### 语法与示例

```ts
import { Transform } from "node:stream";

class LineCounter extends Transform {
  count = 0;

  // _transform：每块数据的处理
  _transform(chunk: Buffer, _enc: string, cb: (e: Error | null, d?: Buffer) => void) {
    this.count += chunk.toString().split("\n").length - 1;
    cb(null, chunk);                       // 透传
  }

  // _flush：流结束前的收尾输出
  _flush(cb: (e: Error | null, d?: Buffer) => void) {
    cb(null, Buffer.from(`共 ${this.count} 行\n`));
  }
}

await pipeline(createReadStream("app.log"), new LineCounter(), process.stdout);
```

### 陷阱
- `callback(err)` 传非 null 会终止整条 pipeline；吞掉错误等于静默丢弃数据
- `_transform` 内做异步操作时务必等完成再调 callback，否则块顺序错乱

## 4. pipeline 与 finished

### 定义
`pipeline` 是流组合的事实标准；`finished` 用于单独监听一个流的最终状态。

### 语法与示例

```ts
import { pipeline, finished } from "node:stream/promises";
import { PassThrough } from "node:stream";

// 多级转换
await pipeline(
  createReadStream("in.csv"),
  createGzip(),
  createWriteStream("out.csv.gz"),
);

// 单独等待一个流结束（HTTP 响应发送完成等场景）
await finished(res);
console.log("响应已全部刷写");

// PassThrough：既可读又可写，常用于"先拿到流、后喂数据"的解耦
const pt = new PassThrough();
processToClient(pt);        // 先把流交给消费者
pt.end(someData);           // 再写入并结束
```

### 陷阱
- 老代码的 `stream.pipe()` 只转发源流错误，下游错误静默丢失——迁移到 `pipeline`
- `pipeline` 出错时所有流被销毁，但**外部资源（临时文件）需自行清理**

## 5. 背压机制

### 定义
Writable 内部缓冲超过 `highWaterMark` 时 `write()` 返回 false，提示生产端暂停的协作协议。

### 手动实现（理解原理）

```ts
async function manualCopy(src: Readable, dst: Writable) {
  for await (const chunk of src) {
    if (!dst.write(chunk)) {
      // 缓冲已满：等待 drain 再继续写入
      await new Promise<void>((resolve) => dst.once("drain", resolve));
    }
  }
  dst.end();
}
```

### 陷阱
- 不检查返回值连续 `write` 大量数据 = 无界内存增长（最常见的流内存事故）
- HTTP 代理场景用 `req.pipe(res)` 或 `pipeline` 可自动处理背压；自写循环必须手动处理

## 6. 常用事件对照表

| 流 | 事件 | 语义 |
|----|------|------|
| Readable | `data` / `readable` | 流动模式 / 暂停模式手动 pull |
| Readable | `end` | 全部数据消费完毕 |
| Writable | `drain` | 缓冲从满转不满 |
| Writable | `finish` | `end()` 后全部刷写完成 |
| 全部 | `error` | 发生错误（未监听即崩溃） |
| 全部 | `close` | 流销毁、资源释放 |

---

## 🔗 相关文档

- 📄 **[Stream 与 Worker 教程](../../basics/07-streams-workers.md)** — 背压与 pipeline 的教学讲解
- 📄 **[Node 核心模块 API](./03-node-core-api.md)** — fs 流式创建函数
- 📄 **[常见故障排除](../quick-references/02-troubleshooting.md)** — 流内存泄漏排查
