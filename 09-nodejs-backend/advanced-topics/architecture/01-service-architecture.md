# 服务架构：分层架构与模块化单体

> **文档简介**: 从"为什么"出发剖析 Node 后端的两种主流组织方式——经典分层架构与模块化单体，给出目录设计、依赖方向与手动依赖注入的可落地原则
>
> **目标读者**: 已交付过完整项目、开始思考代码如何随规模演进的中高级后端开发者
>
> **前置知识**: [生产级 Node.js API](../../projects/04-production-nodejs-api.md)、TypeScript 接口与泛型

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#architecture` `#layered` `#modular-monolith` `#di` |
| **更新日期** | `2026年9月` |

## 🎯 阅读目标

- 理解分层的本质是**依赖方向约束**，而非目录仪式
- 判断"该拆服务还是该做模块化单体"
- 用接口 + 手动注入实现可测试的模块边界

## 1. 分层架构：依赖只能自上而下

```
routes（接口层）     ← HTTP 协议知识：解析请求、返回响应
   ↓ 只调用
services（业务层）   ← 业务规则：这里承载产品价值
   ↓ 只调用
repositories（数据层）← 持久化知识：Prisma 查询、缓存读写
```

**核心纪律**：下层不知道上层的存在。service 里出现 `res.json` 就是分层泄漏的第一信号。

为什么值得付出这个约束？

- **可测试**：业务层不感知 Express，单元测试不需要 HTTP（见 [`../../testing/01-unit-testing.md`](../../testing/01-unit-testing.md)）
- **可替换**：换 ORM、换传输协议（REST→gRPC）时业务层不动
- **可定位**：Bug 的层级即修复的层级，减少"全文件搜索"式排障

```typescript
// 接口层：薄——只做翻译
router.post('/orders', async (req, res) => {
  const input = createOrderSchema.parse(req.body);
  const order = await orderService.create(input, req.auth!.sub);
  res.status(201).json(order);
});

// 业务层：厚——规则都在这里
export async function createOrder(input: CreateOrderInput, userId: string) {
  const cart = await cartRepo.findByUser(userId);
  if (!cart?.items.length) throw new HttpError(400, '购物车为空');

  const total = cart.items.reduce((sum, i) => sum + i.price * i.qty, 0);
  if (total > (await userRepo.getCreditLimit(userId))) {
    throw new HttpError(402, '超出信用额度'); // 业务规则，而不是 HTTP 逻辑
  }
  return orderRepo.create({ userId, items: cart.items, total });
}
```

## 2. 模块化单体：按业务切，不按技术切

分层解决"技术职责"，但项目变大后，第二个维度浮现：**业务域**。模块化单体按域垂直切割，每个域内部再分层：

```
src/
├── modules/
│   ├── auth/            # 认证域：自包含
│   │   ├── routes.ts
│   │   ├── service.ts
│   │   ├── repo.ts
│   │   └── index.ts     # 公共出口：只导出其他模块可用的部分
│   ├── orders/          # 订单域
│   │   └── ...
│   └── billing/         # 计费域
├── lib/                 # 跨域技术设施（prisma/redis/logger）
└── app.ts               # 装配：注册各模块路由
```

```typescript
// modules/auth/index.ts —— 公共出口是模块的"API 合同"
export { authService } from './service.js';
export type { AuthUser } from './types.js';
// routes.ts、repo.ts 故意不导出：外部模块禁止绕过 service 直连内部
```

**与微服务的边界**：模块化单体 = 一个进程 + 硬边界；微服务 = 多个进程 + 网络边界。判断标准：

| 信号 | 选择了模块化单体 |
|------|----------------|
| 团队 < 10 人，一个仓库可协作 | ✅ |
| 各域需要独立扩缩容（如支付突发流量） | ❌ 考虑拆出该域 |
| 跨域调用频繁、事务跨越多域 | ✅ 单体内的本地调用更简单 |
| 域间必须独立发布/独立故障隔离 | ❌ 拆服务 |

**演进路径**：模块内的 `service.ts` 就是未来的微服务原型——先在同一进程内用接口解耦，等扩缩容压力出现再把该模块连同其 repo 一起搬出去。这比一开始就微服务（分布式单体的灾难）便宜一个数量级。

## 3. 依赖注入：不引框架的轻量做法

为了"业务层不依赖具体实现"，用构造函数注入接口即可，不必上 DI 框架：

```typescript
// modules/orders/repo.ts —— 数据层接口
export interface OrderRepo {
  create(data: NewOrder): Promise<Order>;
  listByUser(userId: string): Promise<Order[]>;
}

// modules/orders/service.ts —— 业务层只认识接口
export class OrderService {
  constructor(
    private readonly orders: OrderRepo,
    private readonly payments: PaymentGateway, // 支付网关也是接口
  ) {}

  async create(input: NewOrder, userId: string) {
    const order = await this.orders.create({ ...input, userId });
    await this.payments.charge(order.total, userId);
    return order;
  }
}

// app.ts 装配：组合根（composition root）——唯一的"知道一切"的地方
import { PrismaOrderRepo } from './modules/orders/repo-prisma.js';
import { StripeGateway } from './lib/payments/stripe.js';
import { env } from './config/env.js';

const orderService = new OrderService(new PrismaOrderRepo(prisma), new StripeGateway(env));
```

收益：单测时 `new OrderService(fakeRepo, fakeGateway)` 即可，无需 Mock 库魔法；换 Prisma 为其他实现只动组合根。

## 4. 反模式清单

- ❌ **分布式单体**：拆了微服务却同步互调、共享数据库——承担了分布式的成本，没拿到隔离的收益
- ❌ **utils 垃圾场**：什么都往 `utils/` 扔——放不进任何域的逻辑值得单独想清楚归属
- ❌ **跨域 import 内部文件**：直接 import 另一个模块的 `repo.ts`——破坏边界，公共出口是唯一通道
- ❌ 过早微服务：团队、运维、可观测性没跟上时，拆分只会放大复杂度

## 🔗 相关文档

- 📄 [事件循环原理](../performance/01-event-loop.md) — 架构决策背后的运行时约束
- 📄 [认证服务实战](../../projects/02-auth-service.md) — auth 模块的完整样例
- 📖 [Node + TypeScript 常用模式](../../reference/language-concepts/05-typescript-patterns.md) — 依赖注入的类型基础
- 📄 [单元测试](../../testing/01-unit-testing.md) — 分层带来的可测试性收益
