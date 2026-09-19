# node:zlib 压缩速查

> **文档简介**: `node:zlib` 的字典式速查——gzip/deflate/brotli 三算法选择、同步与流式两种用法、HTTP 压缩中间件场景与常见报错；请在项目锁定的 Node 版本运行示例确认行为。

> **目标读者**: 给 HTTP 服务加响应压缩、处理压缩文件传输的开发者

> **前置知识**: [Stream API 速查](../language-concepts/04-streams-api.md)、[Buffer 速查](./05-buffer.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐⭐ |
| **标签** | `#zlib` `#gzip` `#brotli` `#stream` `#HTTP 压缩` |
| **更新日期** | `2026年9月` |

</details>

## 1. 三种算法与命名规律

### 定义
`node:zlib` 提供压缩与解压。gzip 与默认 deflate 都使用 DEFLATE 压缩算法，但分别使用 gzip 和 zlib 封装；`deflateRaw` 才是没有这两种封装的裸 DEFLATE。Brotli 对一些文本资源有较好的压缩效果，需要按真实数据与参数测量。一次性 API 有异步回调版（可 promisify）及 Sync 同步版，也有 Transform 流版本。

| 算法 | 同步版 | 流式版 | 适用 |
|------|--------|--------|------|
| gzip | `gzipSync`/`gunzipSync` | `createGzip`/`createGunzip` | 通用压缩文件与协商后的 HTTP 响应 |
| deflate | `deflateSync`/`inflateSync` | `createDeflate`/`createInflate` | 自定义协议、省头开销 |
| deflateRaw | `deflateRawSync`/`inflateRawSync` | `createDeflateRaw`/`createInflateRaw` | 协议已明确要求裸 DEFLATE |
| brotli | `brotliCompressSync`/`brotliDecompressSync` | `createBrotliCompress`/`createBrotliDecompress` | 静态资源预压缩候选，收益需测量 |

不要写死“12000 字节压缩为 73 字节”或“Brotli 一定比 gzip 小”：输入内容、库版本和参数都会影响结果。下文完整程序用逐字节往返断言验证正确性，实际压缩率应在业务样本上测量。

Node 24 还提供 Zstd API；其稳定性标记和目标版本支持应按 [Node 24 官方 zlib 文档](https://nodejs.org/docs/latest-v24.x/api/zlib.html) 核对。本页运行案例不覆盖 Zstd。

### 陷阱
- ❌ 解压用错逆函数：`gunzipSync(deflateSync(x))` 应抛 `Z_DATA_ERROR`；错误消息会因版本而异。
- ✅ gzip↔gunzip、deflate↔inflate、brotliCompress↔brotliDecompress 成对记忆
- 本页讨论的 HTTP Content-Encoding 取值包括 `gzip`/`deflate`/`br`——deflate 在实践中历史上常指 zlib 包装格式，做协议前先看对端实现

## 2. 两种用法：一次性 vs 流式

### 定义
同步版适合能一次放入内存的小数据；流式版是 Transform 流，可接进 `pipeline` 处理大输入。请用目标文件和内存限制验证吞吐与资源占用。

```ts
import { gzipSync, gunzipSync, createGzip } from "node:zlib";
import { pipeline } from "node:stream/promises";
import { createReadStream, createWriteStream } from "node:fs";

// 一次性（小数据）
const packed = gzipSync(Buffer.from("..."));
const raw = gunzipSync(packed).toString();

// 流式（大文件/网络）：边读边压边写，缓冲受控，前提是上下游不无限保留数据
await pipeline(
  createReadStream("access.log"),
  createGzip(),
  createWriteStream("access.log.gz"),
);
```

## 3. HTTP 响应压缩场景

### 定义
按请求方接受的编码（`Accept-Encoding` 头）选择表示，并正确设置 `Content-Encoding`。Hono 4 基于 Web 标准 Request/Response；压缩涉及编码协商、响应体替换、长度与缓存头协调，应优先使用框架中间件或代理提供的能力。下面是需要安装 Hono 依赖的配置片段，不属于本页标准库命名运行案例。

```ts
// Hono 4 示例：由内置中间件处理编码协商等细节；先确认运行时支持。
import { Hono } from 'hono';
import { compress } from 'hono/compress';
const app = new Hono();
app.use('*', compress());
app.get('/hello', c => c.text('hello '.repeat(500)));
export default app;
```

部署前仍需检查代理是否已经压缩、流式响应策略及缓存头，参见 [Hono 官方压缩中间件](https://hono.dev/docs/middleware/builtin/compress)。

- 明确由应用、代理或 CDN 中哪一层负责压缩，依据缓存、动态响应、CPU 和部署拓扑决策，避免重复压缩。
- gzip/deflate 的 level 与 Brotli 的质量参数不是同一组选项。更高等级通常付出更多计算成本，但不能保证每份输入都更小；使用真实内容同时比较体积、CPU 和延迟。

### 陷阱
- ❌ 对已压缩内容（图片/视频/zip）再 gzip——白白耗 CPU，体积不降反可能升
- ✅ 压缩前按 `content-type` 白名单过滤（text/*、json、js、css、svg）
- 压缩后不能沿用原始 Content-Length；若最终长度未知，应移除它。若已知压缩后精确字节数，可以设置正确长度。
- HTTP/1.1 与 HTTP/2/3 的分帧机制不同，不要把所有流式响应都称为 chunked；Content-Length 与 HTTP/1.1 的 Transfer-Encoding: chunked 不应同时发送。

<!-- full-library-explanation -->
## 压缩节省带宽，也消耗计算和解压预算

前置是 Buffer、流与 HTTP 头。选择算法先考虑对端支持、数据类型、可用 CPU 和延迟预算。重复文本容易压缩，已压缩图片可能几乎没有收益；更高压缩等级通常更耗时，但压缩后一定更小并不是对每份输入的保证。同步 API 占用事件循环，服务热路径优先异步、流式或提前生成静态压缩资源。

HTTP 压缩需要正确解析 Accept-Encoding 的质量值，gzip;q=0 表示不接受；还要设置 Vary: Accept-Encoding，避免缓存把 gzip 响应发给不支持的客户端。已有 Content-Encoding、HEAD、无响应体状态以及压缩后的 Content-Length 都要协调。直接 includes('gzip') 加 gzipSync 不足以成为正确中间件。

练习：对同一文本执行 gzip 再 gunzip，断言字节完全一致；换成错误解压器应失败。输入是压缩文件时同时限制压缩大小、解压后大小和处理时间，避免少量输入膨胀成巨大数据。流式处理能控制缓冲，但转换器若保留全部解压结果，仍然失去内存优势。测试协商至少覆盖未提供头、gzip、gzip;q=0 和已经压缩的响应。

## 可复现验证：往返、格式错误与输出预算

下面两个完整 ESM 程序保存为 `.mjs`，在 Node 24 执行。不依赖文件或 HTTP 服务。

### 一次性解压也要限制输出

<!-- library-case: node-zlib-roundtrip -->
```js
import assert from 'node:assert/strict';
import {
  gzipSync, gunzipSync, deflateSync, inflateSync,
  deflateRawSync, inflateRawSync, brotliCompressSync, brotliDecompressSync,
} from 'node:zlib';

const source = Buffer.from('任务清单\n'.repeat(1024), 'utf8');
for (const [compress, decompress] of [
  [gzipSync, gunzipSync], [deflateSync, inflateSync],
  [deflateRawSync, inflateRawSync], [brotliCompressSync, brotliDecompressSync],
]) {
  assert.deepEqual(decompress(compress(source)), source);
}
assert.throws(() => gunzipSync(deflateSync(source)), { code: 'Z_DATA_ERROR' });
assert.throws(() => gunzipSync(gzipSync(source), { maxOutputLength: 1024 }),
  { code: 'ERR_BUFFER_TOO_LARGE' });
console.log('zlib-roundtrip: 4 formats, mismatch, output limit');
```

输出为 `zlib-roundtrip: 4 formats, mismatch, output limit`。验证的是完整原始字节，而非仅检查“没有异常”。maxOutputLength 限制一次性便利方法的输出，不是 CPU 时间上限，也不是所有流的自动上限。同步示例只用于这里的小数据，服务热路径优先异步、流式或预压缩。

### 背压与解压总量是两个限制

<!-- library-case: node-zlib-stream-limit -->
```js
import assert from 'node:assert/strict';
import { Readable, Transform, Writable } from 'node:stream';
import { pipeline } from 'node:stream/promises';
import { createGunzip, gzipSync } from 'node:zlib';

function byteLimit(maxBytes) {
  let total = 0;
  return new Transform({
    transform(chunk, encoding, callback) {
      total += chunk.length;
      if (total > maxBytes) {
        const error = new Error('decompressed data exceeds limit');
        error.code = 'ERR_OUTPUT_LIMIT';
        callback(error);
      } else callback(null, chunk);
    },
  });
}
async function unpackSize(compressed, limit) {
  let accepted = 0;
  const sink = new Writable({
    write(chunk, encoding, callback) { accepted += chunk.length; callback(); },
  });
  await pipeline(Readable.from([compressed]), createGunzip(), byteLimit(limit), sink);
  return accepted;
}

const compressed = gzipSync(Buffer.alloc(128 * 1024, 97));
assert.equal(await unpackSize(compressed, 128 * 1024), 128 * 1024);
await assert.rejects(unpackSize(compressed, 1024), { code: 'ERR_OUTPUT_LIMIT' });
await assert.rejects(unpackSize(Buffer.from('invalid gzip'), 1024),
  { code: 'Z_DATA_ERROR' });
console.log('zlib-stream: exact limit, overflow, invalid format');
```

输出为 `zlib-stream: exact limit, overflow, invalid format`。pipeline 协调背压与错误销毁，计数器限制整个作业的输出总量。超限 chunk 已被解压器生成，所以它不是零额外内存的硬隔离；实际任务还要限制输入总量、并发和时间。写文件时先写临时文件，整条管线成功后再发布，以免出错留下的半成品被当作有效文件。

练习：将上限改为原文长度减一，确认拒绝；再令其等于原文长度，确认接受。HTTP 中间件则另建矩阵验证未提供请求头、gzip、gzip;q=0、identity、HEAD、空 body 和已有 Content-Encoding；这些 HTTP 行为不在本页运行报告范围内。

命名运行记录见 [Node/Python 标准库验证](../../../shared-resources/tools/document-quality/reports/node-python-libraries.md)。

## 🔗 相关文档

- 📄 **[Stream API 速查](../language-concepts/04-streams-api.md)** — Transform 流与 pipeline 语义
- 📄 **[Buffer 速查](./05-buffer.md)** — 压缩输入输出的字节容器
- 📄 **[第一个服务器](../../basics/02-first-server.md)** — HTTP 响应头基础
- 🌐 **[Node.js 官方文档: Zlib](https://nodejs.org/docs/latest/api/zlib.html)** — 参数（level/memLevel/窗口）权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
