# node:crypto 加密速查

> **文档简介**: `node:crypto` 高频 API 的字典式速查——哈希摘要、HMAC、安全随机、AES-GCM 加解密闭环、scrypt 密码散列与时序安全比较，示例以 Node 24 API 为背景，当前运行验证范围以质量报告为准

> **目标读者**: 需要落地上传校验、签名、加密存储的开发者

> **前置知识**: [内置模块导航表](./01-core-modules.md)（`node:` 前缀导入）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐⭐ |
| **标签** | `#crypto` `#哈希` `#AES-GCM` `#scrypt` `#安全随机` |
| **更新日期** | `2026年9月` |

</details>

## 1. 哈希与 HMAC

### 定义
哈希把任意数据映射成固定长度摘要（不可逆）；HMAC 在哈希基础上加入密钥，用于验证"消息来自持有密钥的一方"。

### API 表

| API | 签名 | 用途 |
|-----|------|------|
| `createHash(algorithm)` | `.update(data).digest('hex')` | 文件校验、内容寻址（sha256） |
| `hash(algorithm, data, outputEncoding?)` | 默认返回 hex 字符串；传 `'buffer'` 得 Buffer | Node 21.7+ 单发计算，无流开销 |
| `createHmac(algorithm, key)` | `.update(data).digest('hex')` | API 签名、Webhook 验签 |

### 示例

```ts
import { createHash, createHmac, hash } from "node:crypto";

createHash("sha256").update("hello").digest("hex");   // 64 位十六进制
hash("sha256", "hello");                              // 等价的一次性写法（默认也返回 hex 字符串，第三参传 'buffer' 得 Buffer）

// Webhook 验签（GitHub/Stripe 模式）
const expected = createHmac("sha256", process.env.WEBHOOK_SECRET!)
  .update(rawBody)
  .digest("hex");
```

## 2. 安全随机

### 定义
三个 CSPRNG（密码学安全随机源）入口：字节、整数、UUID。

```ts
import { randomBytes, randomInt, randomUUID } from "node:crypto";

randomBytes(16);                 // 16 字节 Buffer（IV、盐、token 用它）
randomBytes(16).toString("hex"); // 32 字符十六进制串
randomInt(0, 10);                // [0, 10) 整数——含头不含尾
randomUUID();                    // UUID v4；按 RFC 4122 的版本位应为 '4'，可用下方命令自行检查
```

### 陷阱
- ❌ **用 `Math.random()` 做任何安全用途**（token、盐、抽签）——它是可预测的伪随机数，不是 CSPRNG
- ✅ 一切安全场景用 `randomBytes`/`randomInt`；仅需唯一性用 `randomUUID()`
- ❌ `randomInt(0, 10)` 期待得到 10——区间左闭右开，上界取不到

## 3. 对称加密：AES-256-GCM 最小闭环

### 定义
AES-GCM 是带认证的对称加密：密文被篡改时解密直接失败，无需额外再算 HMAC。生产对称加密的默认选择。

### 参数速查（请在目标 Node 版本自行验证）

| 参数 | 长度 | 生成方式 |
|------|------|---------|
| key | 32 字节（aes-256） | `randomBytes(32)`，由 KDF 派生或 KMS 下发 |
| iv | 12 字节 | `randomBytes(12)`，**每次加密必须换新** |
| authTag | 16 字节 | 解密前必须 `setAuthTag` |

### 完整闭环示例（以本机 Node 24 运行结果为准）

```ts
import { createCipheriv, createDecipheriv, randomBytes } from "node:crypto";

const key = randomBytes(32);              // 主密钥（实际存 KMS/环境变量）
const iv = randomBytes(12);               // 每条消息独立 IV

// 加密
const cipher = createCipheriv("aes-256-gcm", key, iv);
const ciphertext = Buffer.concat([cipher.update("秘密消息", "utf8"), cipher.final()]);
const tag = cipher.getAuthTag();

// 解密
const decipher = createDecipheriv("aes-256-gcm", key, iv);
decipher.setAuthTag(tag);
const plaintext = Buffer.concat([decipher.update(ciphertext), decipher.final()])
  .toString("utf8");                      // "秘密消息"

// 篡改检测：密文翻转 1 位后解密直接抛错（认证失败）；update 的输出在 final 成功前不能使用
```

存储布局惯例：`iv ‖ tag ‖ ciphertext` 三段拼在一起落库，解密时按固定长度切出。

### 陷阱
- ❌ **IV 复用**（同一 key 下重复 IV）——GCM 下会泄露认证密钥，等同密码学灾难
- ✅ IV 用 `randomBytes(12)` 每次生成，与密文一起存储（IV 不是秘密）
- ❌ 忘记 `setAuthTag` 就 `final()`——抛错；本例使用 16 字节标签；若协议使用其他受支持长度，必须核对 authTagLength 及版本要求，不能把“未显式指定长度的兼容行为弃用”误读为所有短标签 API 一概不可用
- ❌ ECB/CBC 无认证模式自行拼 HMAC——能选 GCM 就选 GCM，不要手搓组合

## 4. 密码散列：scrypt

### 定义
密码散列必须用**故意慢**的 KDF（scrypt/argon2/bcrypt），抵御暴力破解；普通 sha256 速度太快，绝不能存密码。

```ts
import { scryptSync, randomBytes, timingSafeEqual } from "node:crypto";

const salt = randomBytes(16);                    // 每用户独立盐
const derived = scryptSync(password, salt, 32);  // 32 字节派生密钥
// 存库：salt + derived（盐不是秘密，和散列一起存）

// 登录校验：同盐重算，timingSafeEqual 比较
const candidate = scryptSync(input, salt, 32);
timingSafeEqual(candidate, derived);             // true/false
```

- 同一密码 + 同一盐 → 结果确定（可复算），换盐则完全不同
- scrypt 还有 N/r/p 成本参数与 `node:crypto` 的异步版本（`scrypt`），高并发注册场景用异步避免阻塞
- Argon2id 的内置支持与稳定性需按具体 Node 版本核对；选择 KDF 时同时评估成本、实现成熟度与迁移方案

## 5. 时序安全比较：timingSafeEqual

### 定义
普通字符串比较没有恒定时间保证；timingSafeEqual 为等长字节提供时序安全比较，但完整协议的其他步骤仍可能形成侧信道。

```ts
import { timingSafeEqual } from "node:crypto";

timingSafeEqual(bufA, bufB);   // 参数必须是 Buffer/TypedArray 且等长
```

### 陷阱
- ❌ 长度不等的两个 Buffer 直接传入——**抛 RangeError**，而长度本身就是信息泄露
- ✅ 先比较长度（长度泄露可接受），或先对输入做一次哈希统一长度再比较：

```ts
import { createHash } from "node:crypto";
const norm = (s: string) => createHash("sha256").update(s).digest();
timingSafeEqual(norm(a), norm(b));
```

- 适用对象：API 密钥、签名、token 校验；普通业务字段比较不需要

<!-- full-library-explanation -->
## 加密流程的安全性取决于协议与密钥生命周期

前置是 Buffer、随机数和错误处理。哈希不提供身份认证，攻击者可以同时修改消息和普通摘要；HMAC 需要双方妥善保管共享密钥。Webhook 验签应使用协议指定的原始字节和签名布局，不能将解析后的 JSON 再 stringify 后假定字节相同；还要检查时间戳、事件 ID 与重放窗口。

GCM 解密时 update 可能先返回尚未认证的明文字节，只有 final 成功才能接受整条消息，因此不要在认证完成前处理或发送这些字节。记录格式要包含算法版本、密钥标识、IV、认证标签和密文，方便轮换；IV 在同一密钥下必须避免重复，随机生成仍需控制每个密钥的使用量。timingSafeEqual 只约束比较操作，不会让周围的查询、错误分支和日志自动具有恒定时间。

练习：对闭环示例的密文、标签、IV 分别翻转一个字节，解密都应拒绝；错误路径不得返回 update 得到的部分明文。再让两份格式不同但语义相同的 JSON 参与 HMAC，摘要应不同，借此理解原始字节的重要性。密码散列保存算法、成本参数、盐与结果，登录成功后可按策略迁移成本；对外服务优先异步 KDF 并限制并发，不能让攻击者耗尽线程池。

## 🔗 相关文档

- 📄 **[全局对象速查](../language-concepts/09-globals-reference.md)** — WebCrypto `crypto` 全局与 `node:crypto` 的分工
- 📄 **[进程生命周期](./07-process-lifecycle.md)** — 密钥从环境变量安全注入
- 📄 **[生态库精选](./02-ecosystem-libs.md)** — argon2、jsonwebtoken 等三方补充
- 🌐 **[Node.js 官方文档: Crypto](https://nodejs.org/docs/latest/api/crypto.html)** — 算法与参数权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
