# 进阶项目：文件存储服务（上传 + S3 兼容存储）

## 分阶段练习与验收

**最小阶段**：先上传一份小文件并通过 ID 下载。

**验收结果**：大小与类型限制生效，未知 ID 404，文件键不由不可信路径直接决定。

**扩展顺序**：再增加流式上传、对象存储和失败清理；记录元数据与对象不同步时如何恢复。

建议保存一份正常输入、一份失败输入、实际输出和对应测试。先完成以上阶段再扩展正文中的完整设计；遇到省略实现或未定义依赖，应按文档上下文补齐，不能把代码片段拼接后当作已经验证的完整工程。

> **文档简介**: 构建文件存储服务——从本地 multipart 上传升级到 S3 兼容对象存储（MinIO/阿里云 OSS/R2 均适用），掌握预签名 URL 与流式上传下载
>
> **目标读者**: 已完成入门项目、接触过 multipart 表单上传的中级后端开发者
>
> **前置知识**: [Hono 进阶](../frameworks/02-hono-advanced.md) 的文件上传一节、[Stream 管道与多线程](../basics/07-streams-workers.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#s3` `#minio` `#presigned-url` `#stream` `#实战项目` |
| **更新日期** | `2026年9月` |

</details>

Stream API 的完整字典见 [`../reference/language-concepts/04-streams-api.md`](../reference/language-concepts/04-streams-api.md)。

## 🎯 项目目标

- 理解"经服务端中转"与"客户端直传"两种上传架构的取舍
- 用 aws-sdk v3 对接任意 S3 兼容存储（本地用 MinIO 开发）
- 实现预签名 URL 直传与流式下载，服务端不落盘

## 1. 架构决策：中转 vs 直传

| 方案 | 流程 | 适用 |
|------|------|------|
| 经服务端 | 客户端 → Hono(parseBody) → S3 | 小文件、需服务端加工（缩略图/病毒扫描） |
| 预签名直传 | 服务端签发 URL → 客户端 PUT S3 | 大文件、高并发上传（推荐默认） |

服务端只做**签发与记录**，字节流不过 Node 进程——这是 Node 单线程模型下的正确姿势。

## 2. 环境与客户端初始化

```bash
docker run -d --name minio -p 9000:9000 -p 9001:9001 \
  minio/minio server /data --console-address ":9001"
pnpm add @aws-sdk/client-s3 @aws-sdk/s3-request-presigner
```

```typescript
// src/lib/s3.ts —— S3 兼容客户端：换 endpoint 即可切换 MinIO/OSS/R2
import { S3Client } from '@aws-sdk/client-s3';

export const s3 = new S3Client({
  region: process.env.S3_REGION ?? 'us-east-1',
  endpoint: process.env.S3_ENDPOINT ?? 'http://localhost:9000', // MinIO 本地端点
  forcePathStyle: true, // MinIO 必须用 path-style 寻址
  credentials: {
    accessKeyId: process.env.S3_ACCESS_KEY_ID!,
    secretAccessKey: process.env.S3_SECRET_ACCESS_KEY!,
  },
});

export const BUCKET = process.env.S3_BUCKET ?? 'dev-uploads';
```

## 3. 预签名直传：签发 + 确认

```typescript
// src/services/storage-service.ts
import {
  PutObjectCommand,
  GetObjectCommand,
  DeleteObjectCommand,
} from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';
import crypto from 'node:crypto';
import { prisma } from '../lib/prisma.js';
import { HttpError } from '../lib/http-error.js';
import { s3, BUCKET } from '../lib/s3.js';

const ALLOWED = new Map([
  ['image/png', '.png'],
  ['image/jpeg', '.jpg'],
  ['application/pdf', '.pdf'],
]);

/** 生成 5 分钟有效的 PUT 预签名 URL；对象 key 服务端说了算 */
export async function createUploadUrl(mimetype: string, sizeBytes: number) {
  if (!ALLOWED.has(mimetype)) throw new HttpError(415, '不支持的文件类型');
  if (sizeBytes > 50 * 1024 * 1024) throw new HttpError(413, '文件超过 50MB 上限');

  const ext = ALLOWED.get(mimetype)!;
  const key = `uploads/${new Date().toISOString().slice(0, 10)}/${crypto.randomUUID()}${ext}`;

  const uploadUrl = await getSignedUrl(
    s3,
    new PutObjectCommand({ Bucket: BUCKET, Key: key, ContentType: mimetype }),
    { expiresIn: 300 }, // 5 分钟内必须完成上传
  );

  // 先登记 pending 记录，确认后再置 ready
  const record = await prisma.file.create({
    data: { key, mimetype, sizeBytes, status: 'pending' },
  });

  return { fileId: record.id, uploadUrl, key };
}
```

```typescript
// src/routes/files.ts
import { Hono } from 'hono';
import { z } from 'zod';
import { requireAuth } from '../middleware/auth.js';
import * as storage from '../services/storage-service.js';

export const filesApp = new Hono();

/** 第一步：申请上传凭证 */
filesApp.post('/upload-url', requireAuth, async (c) => {
  const { mimetype, sizeBytes } = z
    .object({ mimetype: z.string(), sizeBytes: z.number().int().positive() })
    .parse(await c.req.json());
  return c.json(await storage.createUploadUrl(mimetype, sizeBytes));
});

/** 第二步：客户端 PUT 成功后回调确认 */
filesApp.post('/:id/confirm', requireAuth, async (c) => {
  const file = await storage.confirmUpload(c.req.param('id'));
  return c.json(file);
});

// 装配：app.route('/files', filesApp)
```

客户端用法（浏览器/Node 通用）：

```typescript
// 两段式直传
const { fileId, uploadUrl } = await fetch('/files/upload-url', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ mimetype: fileBlob.type, sizeBytes: fileBlob.size }),
}).then(r => r.json());
await fetch(uploadUrl, { method: 'PUT', body: fileBlob, headers: { 'Content-Type': fileBlob.type } });
await fetch(`/files/${fileId}/confirm`, { method: 'POST' });
```

## 4. 流式下载：服务端不落盘

```typescript
import type { Context } from 'hono';

/** 通过服务端下载：S3 Body 转 Web ReadableStream 交给 c.body()，内存占用恒定 */
export async function streamFile(key: string, c: Context) {
  const obj = await s3.send(new GetObjectCommand({ Bucket: BUCKET, Key: key }));

  return c.body(obj.Body!.transformToWebStream(), 200, {
    'Content-Type': obj.ContentType ?? 'application/octet-stream',
    'Content-Length': String(obj.ContentLength ?? 0),
  }); // Hono 原生支持流式响应体，背压自动处理
}
```

大文件下载也可以完全绕开服务端——签发 GET 预签名 URL 让客户端直连：

```typescript
export async function createDownloadUrl(key: string) {
  return getSignedUrl(s3, new GetObjectCommand({ Bucket: BUCKET, Key: key }), {
    expiresIn: 600, // 下载链接 10 分钟有效
  });
}
```

## 5. 分片上传（大文件）

超过 100MB 用 multipart upload，失败可续传：

```typescript
import { CreateMultipartUploadCommand, UploadPartCommand } from '@aws-sdk/client-s3';

// 1) 初始化 → 返回 uploadId；2) 每个分片签发 PutObject 预签名（带 PartNumber 与 uploadId）；
// 3) 客户端并发 PUT 分片；4) CompleteMultipartUploadCommand 合并。
// @aws-sdk/lib-storage 的 Upload 类封装了以上全部，中小场景直接用它。
```

## ✅ 最佳实践与陷阱

文件上传先校验用户对目标位置的权限，服务端生成对象 key，并限制允许的类型与大小。预签名 URL 在有效期内是一种访问能力，应限定对象、操作和时限，不能在签发后就忽略泄漏风险。

大文件采用有背压的流式传输，客户端中断或下游失败时清理未完成对象。给外部客户端的下载地址必须可达且符合访问策略，不能直接假定内部服务 endpoint 可用。测试超限、重名、过期和中断，而不只检查小文件上传成功。

## 🔗 相关文档

- 📄 [Hono 进阶：文件上传](../frameworks/02-hono-advanced.md) — parseBody 本地上传
- 📖 [Stream API 速查](../reference/language-concepts/04-streams-api.md) — pipeline 与背压字典
- 📄 [Stream 管道与多线程](../basics/07-streams-workers.md) — 流式处理的教程版
- 📄 [生产级 Node.js API](04-production-nodejs-api.md) — 精通路径的收官项目


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
