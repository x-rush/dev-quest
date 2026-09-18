# 进阶项目：认证服务（JWT + 刷新令牌）

## 分阶段练习与验收

**最小阶段**：先完成一次登录与受保护资源访问。

**验收结果**：无效凭据失败、过期令牌不能访问、刷新策略可解释。

**扩展顺序**：再设计令牌轮换与撤销；签名有效不等于请求有资源权限。

建议保存一份正常输入、一份失败输入、实际输出和对应测试。先完成以上阶段再扩展正文中的完整设计；遇到省略实现或未定义依赖，应按文档上下文补齐，不能把代码片段拼接后当作已经验证的完整工程。

> **文档简介**: 构建生产可用的认证服务——注册/登录、短效访问令牌 + 长效刷新令牌的轮换与撤销机制，覆盖密码哈希、Cookie 安全与令牌存储设计
>
> **目标读者**: 已完成入门项目、理解中间件机制的中级后端开发者
>
> **前置知识**: [Hono 进阶](../frameworks/02-hono-advanced.md) 的认证中间件、[生态集成](../frameworks/03-ecosystem-integration.md) 的 Prisma 用法

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#auth` `#jwt` `#refresh-token` `#bcrypt` `#实战项目` |
| **更新日期** | `2026年9月` |

</details>

安全攻防的全景视角见 [`../advanced-topics/security/01-security-practices.md`](../advanced-topics/security/01-security-practices.md)，本文聚焦认证服务的实现路径。

## 🎯 项目目标

- 设计双令牌体系：15 分钟 access token + 7 天 refresh token
- 实现 refresh token 轮换（rotation）与撤销，防止重放
- 密码用 bcrypt 哈希存储，接口行为符合安全默认

## 1. 令牌体系设计

| 令牌 | 有效期 | 存放位置 | 用途 |
|------|--------|---------|------|
| Access Token | 15 分钟 | 响应体（前端存内存） | 调业务 API |
| Refresh Token | 7 天 | HttpOnly Cookie | 换新 access token |

**为什么分两个**：access 短命可容忍泄漏；refresh 长命但只发给认证端点，且 HttpOnly 防 XSS 窃取。

## 2. 数据建模

```prisma
// prisma/schema.prisma
model User {
  id            String         @id @default(cuid())
  email         String         @unique
  passwordHash  String         // 只存哈希，绝不存明文
  refreshTokens RefreshToken[]
}

model RefreshToken {
  id        String    @id @default(cuid())
  tokenHash String    @unique // 存哈希不存原文：数据库泄漏也无法伪造
  userId    String
  user      User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  expiresAt DateTime
  revokedAt DateTime?         // 非 null 即已撤销
  createdAt DateTime  @default(now())

  @@index([userId])
}
```

## 3. 密码哈希与签发

```bash
pnpm add bcryptjs jsonwebtoken
pnpm add -D @types/jsonwebtoken
```

> 💡 bcryptjs 3.x **自带 TypeScript 类型**，不要安装 `@types/bcryptjs`——它已是官方废弃的 stub 包（装了反而报"deprecated"）；`jsonwebtoken` 没有自带类型，仍需 `@types/jsonwebtoken`。

> 💡 **签发与验证的双轨说明**：本文用 `jsonwebtoken` 做**签发**（`expiresIn`/`audience` 等 claims 选项表达力更好），frameworks 篇的 `hono/jwt` 做**验证**中间件——两者产出的都是标准 HS256 JWT，可直接互验（`hono/jwt` 的 `jwt()`/`verify()` 能校验 `jsonwebtoken` 签发的令牌）。想统一到单轨，改用 `hono/jwt` 的 `sign()` 签发即可，但过期时间需自己写进 payload 的 `exp` 字段。

```typescript
// src/services/auth-service.ts
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import crypto from 'node:crypto';
import { prisma } from '../lib/prisma.js';
import { unauthorized, badRequest } from '../lib/http-error.js';

const ACCESS_TTL = '15m', REFRESH_TTL_DAYS = 7;
const BCRYPT_ROUNDS = 12; // 2026 年的合理成本参数

const secrets = { access: process.env.JWT_ACCESS_SECRET! }; // 启动时 env 校验保证非空

export async function register(email: string, password: string) {
  const exists = await prisma.user.findUnique({ where: { email } });
  if (exists) throw badRequest('该邮箱已注册');
  const passwordHash = await bcrypt.hash(password, BCRYPT_ROUNDS);
  return prisma.user.create({ data: { email, passwordHash } });
}

export async function login(email: string, password: string) {
  const user = await prisma.user.findUnique({ where: { email } });
  // 统一错误信息：不区分"邮箱不存在"与"密码错误"，防止账号枚举
  if (!user || !(await bcrypt.compare(password, user.passwordHash))) {
    throw unauthorized('邮箱或密码错误');
  }
  const refreshToken = await issueRefreshToken(user.id);
  return { accessToken: signAccess(user.id, user.email), refreshToken };
}

function signAccess(userId: string, email: string) {
  return jwt.sign({ sub: userId, email }, secrets.access, {
    expiresIn: ACCESS_TTL,
    audience: 'todo-api',
  });
}

async function issueRefreshToken(userId: string) {
  const raw = crypto.randomBytes(48).toString('hex'); // 高熵随机串
  const tokenHash = crypto.createHash('sha256').update(raw).digest('hex');
  const expiresAt = new Date(Date.now() + REFRESH_TTL_DAYS * 86400_000);
  await prisma.refreshToken.create({ data: { tokenHash, userId, expiresAt } });
  return raw; // 原文只返回一次，库里只有哈希
}
```

## 4. 刷新与轮换（rotation）

每次刷新都作废旧 token、签发新 token——被盗用的旧 token 在下一次刷新时即失效：

```typescript
export async function rotateRefreshToken(rawToken: string) {
  const tokenHash = crypto.createHash('sha256').update(rawToken).digest('hex');

  const stored = await prisma.refreshToken.findUnique({
    where: { tokenHash },
    include: { user: true },
  });

  if (!stored) throw unauthorized('令牌无效');
  if (stored.revokedAt || stored.expiresAt < new Date()) {
    // 已撤销的 token 被重放：疑似被盗，撤销该用户全部会话
    await prisma.refreshToken.updateMany({
      where: { userId: stored.userId, revokedAt: null },
      data: { revokedAt: new Date() },
    });
    throw unauthorized('检测到异常会话，请重新登录');
  }

  // 轮换：作废旧记录，签发新 raw token
  await prisma.refreshToken.update({
    where: { id: stored.id }, data: { revokedAt: new Date() },
  });
  const newRaw = crypto.randomBytes(48).toString('hex');
  await prisma.refreshToken.create({
    data: {
      tokenHash: crypto.createHash('sha256').update(newRaw).digest('hex'),
      userId: stored.userId, expiresAt: new Date(Date.now() + REFRESH_TTL_DAYS * 86400_000),
    },
  });

  return { accessToken: signAccess(stored.user.id, stored.user.email) };
}

export async function logout(rawToken: string) {
  const tokenHash = crypto.createHash('sha256').update(rawToken).digest('hex');
  await prisma.refreshToken.updateMany({
    where: { tokenHash },
    data: { revokedAt: new Date() },
  });
}
```

## 5. 路由与 Cookie 设置

```typescript
// src/routes/auth.ts
import { Hono } from 'hono';
import { getCookie, setCookie, deleteCookie } from 'hono/cookie';
import { z } from 'zod';
import * as auth from '../services/auth-service.js';

export const authApp = new Hono();
const REFRESH_COOKIE = 'refresh_token';
const isProd = process.env.NODE_ENV === 'production';

const cookieOpts = {
  httpOnly: true,              // JS 不可读，防 XSS
  secure: isProd,              // 生产仅 HTTPS 传输
  sameSite: 'Strict',          // 防 CSRF
  path: '/auth',               // 只随 /auth/* 请求发送
  maxAge: 7 * 86400,           // hono/cookie 的 maxAge 单位是秒
};

authApp.post('/register', async (c) => {
  const { email, password } = z
    .object({ email: z.string().email(), password: z.string().min(8) })
    .parse(await c.req.json()); // 服务端密码最短 8 位兜底
  const user = await auth.register(email, password);
  return c.json({ id: user.id, email: user.email }, 201);
});

authApp.post('/login', async (c) => {
  const { email, password } = z // 与 register 同一口径的校验，失败抛 ZodError → onError
    .object({ email: z.string().email(), password: z.string().min(8) })
    .parse(await c.req.json());
  const { accessToken, refreshToken } = await auth.login(email, password);
  setCookie(c, REFRESH_COOKIE, refreshToken, cookieOpts); // 写入 Set-Cookie 响应头
  return c.json({ accessToken });
});

authApp.post('/refresh', async (c) => {
  const token = getCookie(c, REFRESH_COOKIE); // 从请求头解析 Cookie
  if (!token) return c.json({ error: '缺少刷新令牌' }, 401);
  return c.json(await auth.rotateRefreshToken(token));
});

authApp.post('/logout', async (c) => { // 撤销 refresh token 并清除 cookie
  await auth.logout(getCookie(c, REFRESH_COOKIE) ?? '');
  deleteCookie(c, REFRESH_COOKIE, { path: '/auth' });
  return c.body(null, 204);
});

// 装配：app.route('/auth', authApp)
```

## 6. 验收清单

- [ ] 登录后 refresh cookie 为 HttpOnly 且 path=/auth
- [ ] 旧 refresh token 刷新一次后再次使用，返回 401 且全部会话被撤销
- [ ] 错误密码与不存在邮箱返回相同错误信息
- [ ] 数据库中看不到任何明文 refresh token

## 🔗 相关文档

- 📄 [Hono 进阶：认证中间件](../frameworks/02-hono-advanced.md) — requireAuth 的完整实现
- 📄 [安全实践](../advanced-topics/security/01-security-practices.md) — 安全头、密钥管理与注入防护
- 📖 [后端生态库精选](../reference/library-guides/02-ecosystem-libs.md) — bcryptjs/jsonwebtoken 速查
- 📄 [文件存储服务](03-file-storage-service.md) — 同难度进阶项目


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
