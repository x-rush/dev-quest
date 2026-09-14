# node:crypto 加密速查

> **文档简介**: `node:crypto` 高频 API 的字典式速查——哈希摘要、HMAC、安全随机、AES-GCM 加解密闭环、scrypt 密码散列与时序安全比较，全部用法在 Node 24 实测通过

> **目标读者**: 需要落地上传校验、签名、加密存储的开发者

> **前置知识**: [内置模块导航表](./01-core-modules.md)（`node:` 前缀导入）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐⭐ |
| **标签** | `#crypto` `#哈希` `#AES-GCM` `#scrypt` `#安全随机` |
| **更新日期** | `2026年9月` |

## 1. 哈希与 HMAC

### 定义
哈希把任意数据映射成固定长度摘要（不可逆）；HMAC 在哈希基础上加入密钥，用于验证"消息来自持有密钥的一方"。

### API 表

| API | 签名 | 用途 |
|-----|------|------|
| `createHash(algorithm)` | `.update(data).digest('hex')` | 文件校验、内容寻址（sha256） |
| `hash(algorithm, data)` | 一次性返回 Buffer | Node 21.7+ 单发计算，无流开销 |
| `createHmac(algorithm, key)` | `.update(data).digest('hex')` | API 签名、Webhook 验签 |

### 示例

```ts
import { createHash, createHmac, hash } from "node:crypto";

createHash("sha256").update("hello").digest("hex");   // 64 位十六进制
hash("sha256", "hello");                              // 等价的一次性写法

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
randomUUID();                    // UUID v4（实测第 14 位恒为 '4'）
```

### 陷阱
- ❌ **用 `Math.random()` 做任何安全用途**（token、盐、抽签）——它是可预测的伪随机数，不是 CSPRNG
- ✅ 一切安全场景用 `randomBytes`/`randomInt`；仅需唯一性用 `randomUUID()`
- ❌ `randomInt(0, 10)` 期待得到 10——区间左闭右开，上界取不到

## 3. 对称加密：AES-256-GCM 最小闭环

### 定义
AES-GCM 是带认证的对称加密：密文被篡改时解密直接失败，无需额外再算 HMAC。生产对称加密的默认选择。

### 参数速查（实测）

| 参数 | 长度 | 生成方式 |
|------|------|---------|
| key | 32 字节（aes-256） | `randomBytes(32)`，由 KDF 派生或 KMS 下发 |
| iv | 12 字节 | `randomBytes(12)`，**每次加密必须换新** |
| authTag | 16 字节 | 解密前必须 `setAuthTag` |

### 完整闭环示例（Node 24 实测通过）

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

// 篡改检测：密文翻转 1 位后解密直接抛错（认证失败），不会解出脏数据
```

存储布局惯例：`iv ‖ tag ‖ ciphertext` 三段拼在一起落库，解密时按固定长度切出。

### 陷阱
- ❌ **IV 复用**（同一 key 下重复 IV）——GCM 下会泄露认证密钥，等同密码学灾难
- ✅ IV 用 `randomBytes(12)` 每次生成，与密文一起存储（IV 不是秘密）
- ❌ 忘记 `setAuthTag` 就 `final()`——抛错；tag 长度必须完整 16 字节
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
- 新项目也可以评估 argon2id（需依赖库）；内置标准库内 scrypt 是默认答案

## 5. 时序安全比较：timingSafeEqual

### 定义
普通 `===` 逐字符短路返回，攻击者可通过响应耗时逐位猜出密钥；`timingSafeEqual` 恒定时间比较，消除时序侧信道。

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

## 🔗 相关文档

- 📄 **[全局对象速查](../language-concepts/09-globals-reference.md)** — WebCrypto `crypto` 全局与 `node:crypto` 的分工
- 📄 **[进程生命周期](./07-process-lifecycle.md)** — 密钥从环境变量安全注入
- 📄 **[生态库精选](./02-ecosystem-libs.md)** — argon2、jsonwebtoken 等三方补充
- 🌐 **[Node.js 官方文档: Crypto](https://nodejs.org/docs/latest/api/crypto.html)** — 算法与参数权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
