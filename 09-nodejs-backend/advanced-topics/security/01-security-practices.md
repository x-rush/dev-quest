# 安全实践：helmet、注入防护与密钥管理

> **文档简介**: 系统梳理 Node 后端的纵深防御清单——HTTP 安全头、SQL/命令/路径注入的防护原理、认证体系加固与密钥全生命周期管理
>
> **目标读者**: 服务即将暴露公网、需要建立安全基线的中高级后端开发者
>
> **前置知识**: [认证服务实战](../../projects/02-auth-service.md)、[Express 进阶](../../frameworks/02-express-advanced.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#security` `#helmet` `#injection` `#secrets` `#owasp` |
| **更新日期** | `2026年9月` |

## 🎯 阅读目标

- 一小时内建立"公网可用"的安全基线（本文清单可直接照做）
- 理解注入类攻击的共同原理：**数据与代码的边界被打破**
- 建立密钥管理的纪律：不进代码、不进日志、可轮换

## 1. 安全头与中间件基线（十分钟做完）

```bash
pnpm add helmet cors
```

```typescript
// src/app.ts —— 防护中间件的标准站位
import helmet from 'helmet';
import cors from 'cors';

app.use(helmet()); // 一次设置 12+ 个安全响应头：CSP、HSTS、X-Frame-Options 等

app.use(cors({
  origin: ['https://app.example.com'], // 白名单，绝不用 '*' 配合凭据
  credentials: true,                   // 允许携带 cookie（refresh token 场景）
  methods: ['GET', 'POST', 'PATCH', 'DELETE'],
}));

// body 解析的大小限制同样是安全边界：防大 payload 打爆内存
app.use(express.json({ limit: '100kb' }));
app.use(express.urlencoded({ extended: true, limit: '100kb' }));
```

helmet 默认值已覆盖 OWASP 安全头建议；遇到前端资源加载报 CSP 错误时，按需放宽单项而非整体关闭。

## 2. 注入防护：统一原理是"数据不当代码执行"

### SQL 注入

Prisma 的查询构造器默认参数化——**这就是用 ORM 的第一安全收益**：

```typescript
// ✅ 安全：参数化查询，用户输入永远只是"数据"
const user = await prisma.user.findFirst({
  where: { email: req.body.email },
});

// ⚠️ 危险：字符串拼接原始 SQL，$queryRawUnsafe + 模板拼接一律视为红旗
const users = await prisma.$queryRawUnsafe(
  `SELECT * FROM users WHERE name = '${req.query.name}'`, // 注入点！
);

// ✅ 确需原生 SQL 时：tagged template 形式自动参数化
const users = await prisma.$queryRaw`
  SELECT * FROM users WHERE name = ${req.query.name}
`;
```

排序字段白名单：`orderBy` 无法参数化，用枚举映射而非透传用户输入：

```typescript
const SORTABLE = { createdAt: 'createdAt', title: 'title' } as const;
const field = SORTABLE[req.query.sort as keyof typeof SORTABLE] ?? 'createdAt';
```

### 命令注入

```typescript
// ❌ 反例：用户输入直接拼进 shell
exec(`convert ${userInput}.png out.jpg`);

// ✅ 正解：execFile 不经过 shell，参数按字面传递
import { execFile } from 'node:child_process';
execFile('convert', [`${userInput}.png`, 'out.jpg']); // 即便输入是 "; rm -rf /" 也只是个文件名
```

### 路径穿越

```typescript
// ❌ 反例：拼接用户提供的文件名
const filePath = path.join(UPLOAD_DIR, req.params.name); // "../../.env" 直接逃逸

// ✅ 正解：解析后强制校验仍在基目录内
const filePath = path.resolve(UPLOAD_DIR, path.basename(req.params.name));
if (!filePath.startsWith(UPLOAD_DIR + path.sep)) throw new HttpError(400, '非法路径');
```

登录、文件上传、JWT 的专项实现见认证服务与 Express 进阶文档；限流防暴力破解见生产级 API。

## 3. 密钥管理全生命周期

**铁律：密钥只存在于运行时环境。** 提交进 git 的密钥等于公开：

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
});
```

## 4. 依赖与运行时

```bash
pnpm audit --prod                        # 已知漏洞扫描，CI 中定期执行
pnpm outdated                            # 过时依赖清单
```

- 固定基础镜像版本（`node:22-alpine` 非 `latest`）
- 容器非 root 运行 + 资源限额（见 [`../../deployment/01-docker-deployment.md`](../../deployment/01-docker-deployment.md)）
- 错误响应不回堆栈与内部路径——500 只说"服务器内部错误"

## 5. 安全面清单（上线前逐项打勾）

- [ ] helmet 已挂载，CSP 按业务最小放宽
- [ ] CORS 白名单，未开启通配凭据
- [ ] 全部 SQL 经参数化；原生查询已审计
- [ ] 文件名/路径经 `basename` + 前缀校验
- [ ] 子进程一律 `execFile`，零字符串拼接
- [ ] 限流覆盖全站 + 认证接口独立收紧
- [ ] 密钥零落库零落码零落日志，轮换预案可执行
- [ ] `pnpm audit` 无高危未修复项

## 🔗 相关文档

- 📄 [认证服务实战](../../projects/02-auth-service.md) — 双令牌与哈希的完整实现
- 📄 [生产级 Node.js API](../../projects/04-production-nodejs-api.md) — 限流与配置校验
- 📄 [可观测性](../../deployment/03-observability.md) — 日志脱敏与告警
- 📖 [后端生态库精选](../../reference/library-guides/02-ecosystem-libs.md) — 安全相关库速查
