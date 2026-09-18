# 安全实践：安全头、注入防护与密钥管理

> **文档简介**: 系统梳理 Node 后端的纵深防御清单——HTTP 安全头、SQL/命令/路径注入的防护原理、认证体系加固与密钥全生命周期管理
>
> **目标读者**: 服务即将暴露公网、需要建立安全基线的中高级后端开发者
>
> **前置知识**: [认证服务实战](../../projects/02-auth-service.md)、[Hono 进阶](../../frameworks/02-hono-advanced.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#security` `#secure-headers` `#injection` `#secrets` `#owasp` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 阅读目标

- 理解常见防护的作用与限制，并为具体服务建立可验证的安全基线
- 理解注入类攻击的共同原理：**数据与代码的边界被打破**
- 建立密钥管理的纪律：不进代码、不进日志、可轮换

## 1. 安全头与中间件基线

```bash
# 无需额外安装：hono/secure-headers、hono/cors、hono/body-limit 全部内置
```

```typescript
// src/app.ts —— 防护中间件的标准站位
import { secureHeaders } from 'hono/secure-headers';
import { cors } from 'hono/cors';
import { bodyLimit } from 'hono/body-limit';

app.use(secureHeaders({
  contentSecurityPolicy: { defaultSrc: ["'none'"], frameAncestors: ["'none'"] },
})); // 纯 API 响应示例；提供 HTML 页面时应按实际资源配置 CSP

app.use('/api/*', cors({
  origin: ['https://app.example.com'], // 白名单，绝不用 '*' 配合凭据
  credentials: true,                   // 允许携带 cookie（refresh token 场景）
  allowMethods: ['GET', 'POST', 'PATCH', 'DELETE'],
}));

// 请求体大小限制同样是安全边界：防大 payload 打爆内存
app.use('/api/*', bodyLimit({ maxSize: 100 * 1024 })); // 100kb
```

`secureHeaders()` 默认并不设置适合所有应用的 CSP，需要显式配置；遇到前端资源加载报 CSP 错误时，按需放宽单项而非整体关闭。

## 2. 注入防护：统一原理是"数据不当代码执行"

### SQL 注入

Prisma 的查询构造器默认参数化——**这就是用 ORM 的第一安全收益**：

```typescript
// ✅ 安全：参数化查询，用户输入永远只是"数据"
const user = await prisma.user.findFirst({
  where: { email: validated.email }, // validated 来自 Zod 校验后的请求体
});

// ⚠️ 危险：字符串拼接原始 SQL，$queryRawUnsafe + 模板拼接一律视为红旗
const users = await prisma.$queryRawUnsafe(
  `SELECT * FROM users WHERE name = '${validated.name}'`, // 注入点！
);

// ✅ 确需原生 SQL 时：tagged template 形式自动参数化
const users = await prisma.$queryRaw`
  SELECT * FROM users WHERE name = ${validated.name}
`;
```

原始 SQL 的列名不能用值占位符代替。ORM 的 `orderBy` 对象由框架解释；动态字段仍应限制在业务允许的白名单中：

```typescript
const SORTABLE = { createdAt: 'createdAt', title: 'title' } as const;
const field = SORTABLE[validated.sort as keyof typeof SORTABLE] ?? 'createdAt';
```

### 命令注入

```typescript
// ❌ 反例：用户输入直接拼进 shell
exec(`convert ${userInput}.png out.jpg`);

// execFile 默认不经过 shell，但仍须防工具自身的选项、路径或协议注入
import { execFile } from 'node:child_process';
execFile('convert', [validatedInputPath, validatedOutputPath]); // 两个路径需由服务端按受控文件 ID 生成
```

### 路径穿越

```typescript
// ❌ 反例：拼接用户提供的文件名
const filePath = path.join(UPLOAD_DIR, c.req.param('name')); // "../../.env" 直接逃逸

// 使用服务端生成的固定格式 ID；UPLOAD_DIR 必须为受控目录。
const id = c.req.param('name');
if (!/^[a-f0-9]{32}$/.test(id)) throw new HttpError(400, '非法文件 ID');
// 此处还必须查询文件所有者并验证当前用户的访问权限。
const filePath = path.join(path.resolve(UPLOAD_DIR), id);
```

登录、文件上传、JWT 的专项实现见认证服务与 Hono 进阶文档；限流防暴力破解见生产级 API。

## 3. 密钥管理全生命周期

**密钥由专门的密钥存储管理，应用仅在必要的运行时范围读取。** 提交进 git 的密钥等于公开：

```text
生产密钥的正确旅程：
  保管：云厂商 Secrets Manager / Vault / 1Password Connect
  注入：CI 的 secrets.* → 部署时挂为环境变量（或挂载文件）
  使用：启动时 env schema 校验（长度/格式），进程内只留一份
  轮换：支持双密钥并行验证期 → 切换 → 移除旧密钥
  泄漏应急：立即轮换 > 追责复盘；git 历史里的密钥必须视为已泄漏
```

```typescript
// 启动即校验（见 projects/04 的 env.ts），这里补充密钥的专用检查
JWT_ACCESS_SECRET: z.string().min(32)
  .refine((s) => !/^(test|dev|change|secret)/i.test(s), '禁止使用示例密钥'),
```

配套纪律：

- `.env*` 全部进 `.gitignore`，仓库只放 `.env.example`（键名无值）
- 日志系统 redact authorization/cookie/token 字段（见 [`../../deployment/03-observability.md`](../../deployment/03-observability.md)）
- JWT 密钥与 refresh 密钥分离；签名算法显式指定（防 `alg: none` 攻击）

```typescript
// 显式算法 + 受众校验
jwt.verify(token, env.JWT_ACCESS_SECRET, {
  algorithms: ['HS256'], // 不写 algorithms 时某些库接受攻击者指定的算法
  audience: 'todo-api',
  issuer: 'https://auth.example.com',
});
```

## 4. 依赖与运行时

```bash
pnpm audit --prod                        # 已知漏洞扫描，CI 中定期执行
pnpm outdated                            # 过时依赖清单
```

- 选择受支持的基础镜像；`node:24-alpine` 仍会移动，需要可重复部署时锁定摘要并制定更新流程
- 容器非 root 运行 + 资源限额（见 [`../../deployment/01-docker-deployment.md`](../../deployment/01-docker-deployment.md)）
- 错误响应不回堆栈与内部路径——500 只说"服务器内部错误"

## 5. 安全面清单（上线前逐项打勾）

- [ ] secureHeaders() 已挂载，CSP 按业务最小放宽
- [ ] CORS 白名单，未开启通配凭据
- [ ] 全部 SQL 经参数化；原生查询已审计
- [ ] 文件使用受控 ID 映射，完成所有权校验，并明确符号链接与目录写入权限
- [ ] 子进程避免 shell 拼接，限制可执行文件、参数选项和可访问路径
- [ ] 限流覆盖全站 + 认证接口独立收紧
- [ ] 密钥零落库零落码零落日志，轮换预案可执行
- [ ] `pnpm audit` 无高危未修复项

<!-- full-library-explanation -->
## 从攻击输入走到明确的拒绝条件

防护必须对应具体边界。参数化 SQL 隔离值与 SQL 语法，但不能代替对象授权：`WHERE id = ?` 很安全地查询出别人的订单，仍然是越权。CORS 限制浏览器读取跨源响应，不能阻止脚本客户端调用接口，也不能单独防 CSRF。

路径校验需要先确定接口接受的是文件 ID 还是相对路径。本页采用服务器生成的 ID，并把它映射到受控目录；该目录不允许不可信用户建立符号链接。若允许任意目录层级或存在并发写入者，字符串前缀检查不足以解决符号链接和检查后替换问题。

**练习**：用两个用户分别创建文件，验证用户 B 即使知道用户 A 的合法文件 ID 也无法下载；再尝试 `../`、带前导 `-` 的命令参数、无效 JWT 与缺少受众的 JWT。验收需要具体拒绝状态及服务端日志，不记录原始令牌。32 个重复字符可以通过长度检查，却不代表密钥具有足够随机性；密钥应由密码学安全随机源产生。

参考：[Hono 安全头默认项](https://hono.dev/docs/middleware/builtin/secure-headers)、[OWASP 授权原则](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)。

## 🔗 相关文档

- 📄 [认证服务实战](../../projects/02-auth-service.md) — 双令牌与哈希的完整实现
- 📄 [生产级 Node.js API](../../projects/04-production-nodejs-api.md) — 限流与配置校验
- 📄 [可观测性](../../deployment/03-observability.md) — 日志脱敏与告警
- 📖 [后端生态库精选](../../reference/library-guides/02-ecosystem-libs.md) — 安全相关库速查


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
