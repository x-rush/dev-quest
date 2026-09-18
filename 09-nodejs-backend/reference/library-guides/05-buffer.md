# node:buffer 二进制速查

> **文档简介**: `node:buffer` 的字典式速查——Buffer 与 Uint8Array 的关系、编码转换、alloc/allocUnsafe/from 三种创建方式差异、字节序读写与流配合，用法在 Node 24 实测

> **目标读者**: 处理文件、网络包、编码转换的开发者

> **前置知识**: [Stream API 速查](../language-concepts/04-streams-api.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐⭐ |
| **标签** | `#Buffer` `#Uint8Array` `#编码` `#字节序` |
| **更新日期** | `2026年9月` |

</details>

## 1. Buffer 与 Uint8Array 的关系

### 定义
`Buffer` 是 `Uint8Array` 的**子类**，附加了 Node 特有的编码转换与读写方法；不同 Web API 接受不同的 BufferSource、Blob 或字符串等输入类型，边界处用 `Buffer` 的视图能力自然衔接。

```ts
import { Buffer } from "node:buffer";   // 全局可用，显式导入利于类型与可读性

const buf = Buffer.from("hi");
buf instanceof Uint8Array;   // true（实测）——凡收 Uint8Array 的 API 都能收 Buffer
buf instanceof Buffer;       // true
```

| 能力 | Buffer 独有 | Uint8Array/TypedArray 通用 |
|------|------------|---------------------------|
| 编码转换 `toString('base64')` | ✅ | ❌ |
| `readUInt32BE` 等定长读写 | ✅（`DataView` 也有等价能力） | ❌ |
| `subarray`、`set`、下标访问 | ✅ | ✅ |
| 可被 Web 标准 API 接受 | ✅（因是子类） | ✅ |

## 2. 三种创建方式

### 定义
`alloc` 零填充、`allocUnsafe` 直接切未清零内存池（快但可能带旧数据）、`from` 从已有数据转换。

```ts
Buffer.alloc(4);               // <00 00 00 00>：零填充，安全默认
Buffer.alloc(4, "ab");         // 'abab'：用字符串/数字填充
Buffer.allocUnsafe(4);         // 内容不确定！必须每字节覆盖后再用
Buffer.from("hi");             // 从字符串（默认 utf8）
Buffer.from([1, 2, 3]);        // 从字节数组
Buffer.from("aGk=", "base64"); // 从指定编码解码
Buffer.from(u8arr.buffer, u8arr.byteOffset, u8arr.byteLength); // 共享当前字节范围
```

| 方式 | 内存保证 | 速度 | 用途 |
|------|---------|------|------|
| `alloc(n)` | 全零 | 稍慢（要清零） | 默认选择 |
| `allocUnsafe(n)` | **未初始化** | 最快 | 高频小对象池，写入覆盖全部字节后使用 |
| `from(data)` | 依重载而异，ArrayBuffer 重载共享底层存储 | 取决于源 | 从字符串/数组/Buffer 转换 |

### 陷阱
- ❌ `new Buffer(...)` 构造函数——已弃用（DEP0005，Node 24 实测仍可用但告警），语义含糊且不安全
- ✅ 一律 `Buffer.alloc` / `Buffer.from` / `Buffer.allocUnsafe`
- ❌ `allocUnsafe` 分配后只写入部分字节就输出——旧内存内容可能当数据泄出
- ✅ 用 `allocUnsafe` 必须保证**完整覆盖**（典型：随即整体写满的场景）

## 3. 编码转换速查

### 定义
`buf.toString([encoding])` 把字节解码成字符串，`Buffer.from(str, encoding)` 反向编码；`Buffer.byteLength(str)` 给出 utf8 字节数。

```ts
const buf = Buffer.from("你好");
buf.toString("hex");         // "e4bda0e5a5bd"
buf.toString("base64");      // "5L2g5aW9"
buf.toString("base64url");   // 同上（url-safe 变体，Node 15+）
buf.toString("utf8");        // "你好"
Buffer.byteLength("你好");   // 6（3 字节/字 × 2）
"你好".length;               // 2（UTF-16 码元数）——字符数 ≠ 字节数

// 残缺多字节字符的解码：单独切出半个字会变成替换符
Buffer.from("你好").subarray(0, 1).toString("utf8");  // "�"（乱码）
```

### 陷阱
- ❌ 对流式数据逐 chunk 直接 `chunk.toString()`——多字节字符跨 chunk 时被截断成乱码
- ✅ 用 `string_decoder`（`StringDecoder`）拼回完整字符，或累积 Buffer 后一次性解码
- ❌ `latin1`/`binary` 当 utf8 用——两者是单字节编码，中文必乱码
- ✅ 默认显式写 `"utf8"`，不要依赖默认参数省略

## 4. 字节序读写

### 定义
`readXxxBE/LE`（大端/小端）在指定偏移处按固定宽度读写整数与浮点数；跨系统协议（网络序即大端）与二进制文件格式的关键工具。

```ts
const b = Buffer.from([0x01, 0x02, 0x03, 0x04]);
b.readUInt32BE(0);    // 16909060（大端）
b.readUInt32LE(0);    // 67305985（小端）

const w = Buffer.alloc(8);
w.writeBigInt64BE(123n, 0);   // 64 位有符号整数（Node 12+）
w.readBigInt64BE(0);          // 123n
w.readUInt32BE(0);            // 0：BigInt 写入高 4 字节

b.readUInt16BE(2);            // 772，偏移 2 仍有两个字节
// b.readUInt16BE(3);         // 才会因越界抛 RangeError
```

- 命名规律：`read|write` + 类型（`UInt`/`Int`/`Float`/`BigInt`）+ 宽度 + `BE|LE`
- 同样需求在 Web 标准侧用 `DataView`；Buffer 方法书写更短，两者可混用（同一 ArrayBuffer）

## 5. 与流配合

### 定义
Buffer 是流的通货：可读流产出 Buffer chunk，可写流消费 Buffer；`Buffer.concat` 是"收集完再合并"的标准姿势。

```ts
import { createReadStream } from "node:fs";

// 整文件读入（小文件）
const chunks: Buffer[] = [];
for await (const c of createReadStream("a.bin")) chunks.push(c);
const whole = Buffer.concat(chunks);

// 大文件走 pipeline，不做全量缓冲
import { pipeline } from "node:stream/promises";
await pipeline(createReadStream("in.bin"), transform, createWriteStream("out.bin"));

Buffer.concat([Buffer.from("ab"), Buffer.from("cd")]).toString();  // "abcd"
Buffer.from("abcd").subarray(1, 3);   // 'bc'：视图共享内存，不拷贝
```

### 陷阱
- ❌ 对超大文件 `Buffer.concat` 全量入内存——OOM 的头号来源
- ✅ 大文件一律 `pipeline` 流式处理，只在确知"小"时才整体读
- `subarray` 返回的视图与原 Buffer **共享内存**，改动会互相影响；需要独立副本用 `Buffer.from(view)`（拷贝）

<!-- full-library-explanation -->
## 字节视图是否共享，必须从构造方式判断

前置是数组、引用与编码。Buffer.from(existingBuffer) 复制字节；Buffer.from(arrayBuffer,offset,length) 则建立共享视图。TypedArray 的 buffer 可能比当前视图大，直接传整个 buffer 可能包含前后不属于本视图的数据。跨边界传递时同时保留 byteOffset 和 byteLength，避免泄露或读取无关字节。

保存为 buffer.mjs 后运行：

```js
const original = Buffer.from([1, 2, 3]);
const view = original.subarray(1);
const copy = Buffer.from(view);
view[0] = 9;
console.log([...original].join(','), [...copy].join(','));
const bytes = Buffer.from([1, 2, 3, 4]);
console.log(bytes.readUInt16BE(2));
```

预期为 `1,9,3 2,3` 和 `772`。练习：把读取偏移从 2 改为 3，才会因剩余不足两个字节而报错。解析外部二进制协议先验证总长度、字段长度和字节序，再按偏移读取；长度字段本身也可能恶意夸大。字符串的 length 是 UTF-16 码元数，Buffer 长度是字节数，二者不能互换。

## 🔗 相关文档

- 📄 **[Stream API 速查](../language-concepts/04-streams-api.md)** — Buffer 在流管线中的角色
- 📄 **[node:crypto 加密速查](./03-crypto.md)** — IV/tag/密钥都是 Buffer
- 📄 **[全局对象速查](../language-concepts/09-globals-reference.md)** — Buffer 与 Web 二进制类型（Blob/ArrayBuffer）衔接
- 🌐 **[Node.js 官方文档: Buffer](https://nodejs.org/docs/latest/api/buffer.html)** — 编码与 API 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
