# 项目分层与领域建模

> **文档简介**: 为什么 FastAPI 项目要分层？如何用领域建模与依赖倒置让业务逻辑独立于框架与数据库，随规模增长仍可控
>
> **目标读者**: 已写过多个小项目、想让代码结构支撑业务复杂度的开发者
>
> **前置知识**: [FastAPI 进阶（依赖注入）](../../frameworks/02-fastapi-advanced.md)、[SQLAlchemy 集成](../../frameworks/03-ecosystem-integration.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#架构` `#领域建模` `#分层` `#依赖倒置` |
| **更新日期** | `2026年9月` |

## 1. 问题：路由里长出业务逻辑

```python
# 反面模式：一个路由承担了 HTTP 解析 + 业务规则 + SQL 三种职责
@router.post("/orders")
async def create_order(payload: OrderCreate, session: AsyncSession):
    if payload.amount > 10000:            # 业务规则
        raise HTTPException(422, "超出限额")
    order = Order(**payload.model_dump()) # 数据访问
    session.add(order)
    ...
```

**症状**：单元测试必须连数据库；改表结构牵动路由层；同一条业务规则在多个端点重复出现。本质是"变化频率不同的东西耦合在一起"。

## 2. 四层结构

```text
api/           只做协议转换：HTTP ↔ Pydantic 模型，调用 service
services/      业务规则：校验、编排、事务边界
repositories/  数据访问：唯一的 SQL 所在地
models/ + schemas/   ORM 实体 / 传输对象
```

依赖方向**单向向下**：api → services → repositories → models。上层知道下层，下层对上层一无所知。

```python
# services/order_service.py —— 业务规则的唯一家
class DomainError(Exception):
    """业务异常：与 HTTP 无关，由 api 层翻译。"""

class OrderService:
    def __init__(self, repo: OrderRepository) -> None:
        self.repo = repo

    async def place_order(self, user_id: int, amount: Decimal) -> Order:
        if amount > USER_DAILY_LIMIT:
            raise DomainError("超出单日限额")
        return await self.repo.create(user_id, amount)
```

```python
# api/routes_orders.py —— 薄路由，只翻译异常为 HTTP
@router.post("/orders", status_code=201)
async def place_order(
    payload: OrderCreate,
    svc: Annotated[OrderService, Depends(get_order_service)],
) -> OrderRead:
    try:
        return await svc.place_order(payload.user_id, payload.amount)
    except DomainError as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))
```

## 3. 领域建模：实体与值对象

```python
# 领域层不依赖 SQLAlchemy/Pydantic：普通类 + 类型注解
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)                      # 不可变 = 值对象
class Money:
    amount: Decimal
    currency: str = "CNY"

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("币种不同不可相加")
        return Money(self.amount + other.amount, self.currency)

class Order:                                  # 实体：有身份、有生命周期
    def __init__(self, order_id: int, items: list[Money]) -> None:
        self.order_id = order_id
        self._items = list(items)

    @property
    def total(self) -> Money:
        return sum(self._items, start=Money(Decimal("0")))
```

**要点**：规则内聚在领域对象里（"不同币种不能相加"住在 Money 内部），测试不需要任何框架——`Money` 的加法用纯 [pytest](../../testing/01-unit-testing.md) 即可验证。建模语法基础见 [OOP 协议字典](../../reference/language-concepts/04-oop-protocols.md)。

## 4. 依赖倒置：Repository 协议

```python
# services/ports.py —— 上层定义接口（不是下层！）
from typing import Protocol

class OrderRepository(Protocol):
    async def create(self, user_id: int, amount: Decimal) -> Order: ...
    async def get(self, order_id: int) -> Order | None: ...

# repositories/sqlalchemy_repo.py —— 下层实现接口
class SqlAlchemyOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    # ...实现 Protocol 声明的两个方法

# 组合根（依赖装配处）选择具体实现
def get_order_service(session: SessionDep) -> OrderService:
    return OrderService(SqlAlchemyOrderRepository(session))
```

**收益**：service 只认识 Protocol；测试时传一个内存版实现即可，不必真连数据库——与[依赖覆盖](../../testing/02-integration-testing.md)是同一思想的两个层次。

## 5. 何时分层、何时从简

| 规模 | 建议 |
|------|------|
| 脚本 / 原型 | 单文件或两层（路由 + 存储），别过度设计 |
| 中型服务 | 本篇四层结构 |
| 多服务 / 多团队 | 引入显式领域层，各层独立包 + 明确 API |

**分层是工具不是信仰**：当"加一层"没有减少任何重复或耦合时，那层就是负担。判断标准永远是变化频率与测试成本，不是层数。

---

## 🔗 相关文档

- 🚀 **[项目：生产级 FastAPI 应用](../../projects/04-production-fastapi-app.md)** — 本篇思想的完整落地实现
- 🎓 **[asyncio 并发模型](../performance/01-async-python.md)** — 分层与并发决策的交叉点
- 📄 **[FastAPI 进阶](../../frameworks/02-fastapi-advanced.md)** — 依赖注入：分层的机制基础
- 📖 **[OOP 协议字典](../../reference/language-concepts/04-oop-protocols.md)** — dataclass/Protocol/抽象基类速查
- 🧪 **[单元测试](../../testing/01-unit-testing.md)** — 领域对象的纯函数测试
