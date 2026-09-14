# node:zlib 压缩速查

> **文档简介**: `node:zlib` 的字典式速查——gzip/deflate/brotli 三算法选择、同步与流式两种用法、HTTP 压缩中间件场景与常见报错，用法在 Node 24 实测

> **目标读者**: 给 HTTP 服务加响应压缩、处理压缩文件传输的开发者

> **前置知识**: [Stream API 速查](../language-concepts/04-streams-api.md)、[Buffer 速查](./05-buffer.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐⭐ |
| **标签** | `#zlib` `#gzip` `#brotli` `#stream` `#HTTP 压缩` |
| **更新日期** | `2026年9月` |

## 1. 三种算法与命名规律

### 定义
`node:zlib` 封装 zlib 与 Brotli 库：**gzip** 通用兼容、**deflate** 无 gzip 头（更小开销）、**brotli** 压缩率最高（静态资源首选），每个算法都有同步 Buffer 版与流式版。

| 算法 | 同步版 | 流式版 | 适用 |
|------|--------|--------|------|
| gzip | `gzipSync`/`gunzipSync` | `createGzip`/`createGunzip` | HTTP 响应压缩的默认选项 |
| deflate | `deflateSync`/`inflateSync` | `createDeflate`/`createInflate` | 自定义协议、省头开销 |
| brotli | `brotliCompressSync`/`brotliDecompressSync` | `createBrotliCompress`/`createBrotliDecompress` | 静态资源预压缩（更高压缩率） |

```ts
// Node 24 实测（12000 字节重复文本）：
gzipSync(src).length;                 // 73，往返 gunzipSync 还原 ✅
inflateSync(deflateSync(src));        // deflate 配 inflate，不是 gunzip ✅
brotliCompressSync(src).length < gzipSync(src).length;  // ✅ brotli 更小
```

### 陷阱
- ❌ 解压用错逆函数：`gunzipSync(deflateSync(x))` 抛 `Z_DATA_ERROR`（incorrect header check，实测）
- ✅ gzip↔gunzip、deflate↔inflate、brotliCompress↔brotliDecompress 成对记忆
- HTTP `Content-Encoding` 的取值只有 `gzip`/`deflate`/`br`——deflate 在实践中历史上常指 zlib 包装格式，做协议前先看对端实现

## 2. 两种用法：一次性 vs 流式

### 定义
同步版适合小数据（一次进内存）；流式版是 Transform 流，接进 `pipeline` 处理任意大小数据（Node 24 实测文件 gzip 通过）。

```ts
import { gzipSync, gunzipSync, createGzip } from "node:zlib";
import { pipeline } from "node:stream/promises";
import { createReadStream, createWriteStream } from "node:fs";

// 一次性（小数据）
const packed = gzipSync(Buffer.from("..."));
const raw = gunzipSync(packed).toString();

// 流式（大文件/网络）：边读边压边写，内存恒定
await pipeline(
  createReadStream("access.log"),
  createGzip(),
  createWriteStream("access.log.gz"),
);
```

## 3. HTTP 响应压缩场景

### 定义
按请求方支持的编码（`Accept-Encoding` 头）压缩响应体并打上 `Content-Encoding`；Hono 4 基于 Web 标准 Request/Response，手写压缩中间件的核心就是"换 body + 改头"，生产更常见的做法是交给 Nginx/CDN 统一处理。

```ts
// 概念模板：与 Web 标准框架配合的最小压缩逻辑
app.use(async (c, next) => {
  await next();
  const accepts = c.req.header("accept-encoding") ?? "";
  if (!accepts.includes("gzip")) return;
  const body = await c.res.arrayBuffer();
  const packed = gzipSync(Buffer.from(body), { level: 6 });
  c.res = new Response(packed, c.res);
  c.res.headers.set("content-encoding", "gzip");
  c.res.headers.set("content-length", String(packed.length));
});
```

- 生产更常见做法：**应用不做压缩**，让 Nginx/CDN 统一处理（缓存友好、CPU 转移）；应用层压缩适合无代理的直连服务
- `level` 0-9：越高越小越慢；动态响应常用 4-6，静态资源预压缩用 9

### 陷阱
- ❌ 对已压缩内容（图片/视频/zip）再 gzip——白白耗 CPU，体积不降反可能升
- ✅ 压缩前按 `content-type` 白名单过滤（text/*、json、js、css、svg）
- ❌ 同时手写 `content-length` 和分块流式压缩——两个机制冲突
- ✅ 拿不准就流式压缩不设 content-length（走 chunked），或一次性算好长度再发

## 🔗 相关文档

- 📄 **[Stream API 速查](../language-concepts/04-streams-api.md)** — Transform 流与 pipeline 语义
- 📄 **[Buffer 速查](./05-buffer.md)** — 压缩输入输出的字节容器
- 📄 **[第一个服务器](../../basics/02-first-server.md)** — HTTP 响应头基础
- 🌐 **[Node.js 官方文档: Zlib](https://nodejs.org/docs/latest/api/zlib.html)** — 参数（level/memLevel/窗口）权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
