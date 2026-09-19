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
`node:zlib` 封装 zlib 与 Brotli 库：**gzip** 通用兼容、**deflate** 无 gzip 头（更小开销）、**brotli** 对一些文本静态资源有较好的压缩效果，需按数据与级别测量，每个算法都有同步 Buffer 版与流式版。

| 算法 | 同步版 | 流式版 | 适用 |
|------|--------|--------|------|
| gzip | `gzipSync`/`gunzipSync` | `createGzip`/`createGunzip` | HTTP 响应压缩的默认选项 |
| deflate | `deflateSync`/`inflateSync` | `createDeflate`/`createInflate` | 自定义协议、省头开销 |
| brotli | `brotliCompressSync`/`brotliDecompressSync` | `createBrotliCompress`/`createBrotliDecompress` | 静态资源预压缩（更高压缩率） |

```ts
// 对 12000 字节重复文本的示例；压缩比例应在目标数据与 Node 版本中测量：
gzipSync(src).length;                 // 73，往返 gunzipSync 还原 ✅
inflateSync(deflateSync(src));        // deflate 配 inflate，不是 gunzip ✅
brotliCompressSync(src).length < gzipSync(src).length;  // ✅ brotli 更小
```

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
按请求方支持的编码（`Accept-Encoding` 头）压缩响应体并打上 `Content-Encoding`；Hono 4 基于 Web 标准 Request/Response，手写压缩中间件的核心就是"换 body + 改头"，生产更常见的做法是交给 Nginx/CDN 统一处理。

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

- 生产更常见做法：**应用不做压缩**，让 Nginx/CDN 统一处理（缓存友好、CPU 转移）；应用层压缩适合无代理的直连服务
- `level` 0-9：越高越小越慢；动态响应常用 4-6，静态资源预压缩用 9

### 陷阱
- ❌ 对已压缩内容（图片/视频/zip）再 gzip——白白耗 CPU，体积不降反可能升
- ✅ 压缩前按 `content-type` 白名单过滤（text/*、json、js、css、svg）
- ❌ 同时手写 `content-length` 和分块流式压缩——两个机制冲突
- ✅ 拿不准就流式压缩不设 content-length（走 chunked），或一次性算好长度再发

<!-- full-library-explanation -->
## 压缩节省带宽，也消耗计算和解压预算

前置是 Buffer、流与 HTTP 头。选择算法先考虑对端支持、数据类型、可用 CPU 和延迟预算。重复文本容易压缩，已压缩图片可能几乎没有收益；更高压缩等级通常更耗时，但压缩后一定更小并不是对每份输入的保证。同步 API 占用事件循环，服务热路径优先异步、流式或提前生成静态压缩资源。

HTTP 压缩需要正确解析 Accept-Encoding 的质量值，gzip;q=0 表示不接受；还要设置 Vary: Accept-Encoding，避免缓存把 gzip 响应发给不支持的客户端。已有 Content-Encoding、HEAD、无响应体状态以及压缩后的 Content-Length 都要协调。直接 includes('gzip') 加 gzipSync 不足以成为正确中间件。

练习：对同一文本执行 gzip 再 gunzip，断言字节完全一致；换成错误解压器应失败。输入是压缩文件时同时限制压缩大小、解压后大小和处理时间，避免少量输入膨胀成巨大数据。流式处理能控制缓冲，但转换器若保留全部解压结果，仍然失去内存优势。测试协商至少覆盖未提供头、gzip、gzip;q=0 和已经压缩的响应。

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
