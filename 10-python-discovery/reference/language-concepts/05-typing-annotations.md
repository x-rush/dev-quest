# typing 注解全表 — 泛型 / Protocol / TypedDict / Pydantic 配合

## 概述

类型注解是现代 Python 的基础设施：编辑器提示、静态检查（mypy/pyright）、框架运行时校验（FastAPI/Pydantic）共同依赖它。本条目覆盖 3.12+ 推荐写法与旧写法对照，并速览 3.13/3.14 的类型系统能力（模块基线 Python 3.14）。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#typing` `#泛型` `#Protocol` `#TypedDict` `#Pydantic` |
| **更新日期** | `2026年9月` |

</details>

## 新旧写法对照（读旧代码必备）

| 旧写法（typing 模块） | 3.10+/3.12+ 写法 |
|------|------|
| `Optional[X]` | `X \| None` |
| `Union[A, B]` | `A \| B` |
| `List[int]` / `Dict[str, int]` | `list[int]` / `dict[str, int]` |
| `Tuple[int, str]` | `tuple[int, str]` |
| `Callable[[int], str]` | `Callable[[int], str]`（仍在 typing）或 `collections.abc.Callable` |
| `TypeVar("T")` + 泛型类 | `class Box[T]: ...`（PEP 695） |
| `Type[X]` | `type[X]` |
| `Iterable[T]` | `collections.abc.Iterable[T]` |

> 原则：新代码从 `builtins` 与 `collections.abc` 取泛型，`typing` 只补它独有的（Protocol、TypedDict、Annotated、TypeAlias 等）。

---

## 1. 基础注解

```python
name: str = "ada"
ids: list[int] = []
point: tuple[float, float] = (1.0, 2.0)
labels: tuple[str, ...] = ("a", "b")       # 变长元组
cache: dict[str, list[int]] = {}

def find(uid: int) -> str | None: ...       # 可空返回
def render(data: object) -> str: ...        # object 接受任何值
def callback() -> None: ...                 # 无返回（返回 None）
```

`Any` 与 `object` 的区别：`Any` 放弃检查（双向兼容），`object` 可以接收任意对象，但只能直接使用所有对象共有的操作；访问特定方法前需要类型收窄。

---

## 2. 泛型 — PEP 695 新语法（3.12+）

```python
# 泛型函数：类型变量 T 随调用流动
def first[T](items: list[T]) -> T | None:
    return items[0] if items else None

# 泛型类
class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

# 泛型别名
type Vec[T] = list[T]              # PEP 695 type 语句
```

旧语法对照：`T = TypeVar("T")`、`class Stack(Generic[T])`、`Vec = list[T]`（3.12 前）。读第三方代码两者都会遇到。

---

## 3. Protocol — 结构化子类型

**定义**: "静态鸭子类型"。不要求继承，只要求方法签名匹配。

```python
from typing import Protocol, runtime_checkable

class Closable(Protocol):
    def close(self) -> None: ...

def safe_close(resource: Closable) -> None:   # 任何有 close() 的对象都匹配
    resource.close()
```

**要点**:
- 与 ABC 的区别：调用方**无需**被检查类配合，第三方对象天然适配
- 默认仅静态检查；`@runtime_checkable` 后 `isinstance` 也只验证方法名，不验签名
- 当调用方只依赖少量行为时可用 Protocol；具体类型、现有 ABC 或普通函数参数有时更清楚，不必为每个参数创建新协议

---

## 4. TypedDict — 字典形状

```python
from typing import TypedDict, NotRequired   # NotRequired 3.11+

class UserRow(TypedDict):
    id: int
    name: str
    email: NotRequired[str]          # 可选键

u: UserRow = {"id": 1, "name": "ada"}
```

**要点**:
- 纯静态约束，运行时就是普通 dict，**不校验**
- 适用场景：函数间传递的 JSON 结构、`**kwargs` 的形状（`Unpack[UserRow]`）
- 需要运行时校验时换 Pydantic（见第 6 节）

---

## 5. 其他高频工具

```python
from typing import Annotated, Literal

# Annotated：给类型挂元数据（框架读取，检查器忽略）
UserId = Annotated[int, "必须是数据库用户 ID"]

# Literal：字面量受限类型；TypeAlias / final / overload 用时查 typing 文档
Mode = Literal["r", "w", "a"]
```

---

## 6. 3.13/3.14 类型系统增强

```python
# 3.13：TypeVar 默认值（PEP 696）——泛型未指定时落到默认类型
from typing import TypeVar

T = TypeVar("T", default=int)

class Box[T = int]:
    def get(self) -> T: ...

# 3.13：TypeIs（PEP 742）——isinstance 风格的类型收窄，语义比 TypeGuard 更直觉
from typing import TypeIs
from collections.abc import Sequence

def is_strs(items: Sequence[object]) -> TypeIs[Sequence[str]]:
    return all(isinstance(i, str) for i in items)

# 3.13：warnings.deprecated（PEP 702）——声明弃用的标准方式
from warnings import deprecated

@deprecated("改用 new_api")
def old_api() -> None: ...

# 3.14：注解惰性求值（PEP 649/749）——前向引用不再需要字符串引号
class Node:
    def link(self, other: Node) -> Node: ...   # 3.13 及以前需写 "Node"
```

**要点**：Python 3.14 改变注解的求值机制；运行时读取注解的库需要与解释器版本兼容，不能据此承诺旧代码都无需修改。TypeIs 要求收窄后的类型与输入兼容：上例使用协变的 Sequence，不能机械换成不变的 `list[object]` → `list[str]`。

---

## 7. 与 Pydantic 配合 — 运行时校验

Pydantic v2 根据注解和字段配置执行运行时解析与验证，也是 FastAPI 常用的数据模型工具。默认模式可能转换输入类型；需要拒绝转换时应明确配置严格模式：

```python
from pydantic import BaseModel, Field, field_validator

class UserIn(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=0, le=150)
    email: str | None = None
    tags: list[str] = []

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str | None) -> str | None:
        if v is not None and "@" not in v:
            raise ValueError("邮箱格式非法")
        return v

user = UserIn.model_validate({"name": "ada", "age": 36})   # dict → 模型，校验失败抛 ValidationError
print(user.model_dump())        # 模型 → dict
```

**分工**:

| 工具 | 检查时机 | 用途 |
|------|---------|------|
| dataclass | 无检查 | 程序内部数据 |
| TypedDict | 仅静态 | dict 形状约定 |
| Pydantic | 运行时强校验 | API 输入、配置、边界数据 |

---

## 陷阱速查表

| 陷阱 | 说明 |
|------|------|
| 注解错不报错 | 静态检查靠 mypy/pyright，运行时靠 Pydantic |
| 可变默认值 | Pydantic 与 dataclass 不同，会深拷贝可变默认值（安全）；习惯上仍可用 `Field(default_factory=list)` |
| `Any` 扩散 | 一个 Any 传染整条调用链，收敛到边界 |
| TypedDict 误当校验器 | 它运行时啥也不查，校验用 Pydantic |

---

<!-- full-library-explanation -->
## 把静态契约和输入验证分开

前置知识是函数参数、容器和异常。注解描述程序希望接收什么，不会让解释器自动拒绝错误值。静态检查器也只能根据代码中可见的信息推导；外部 JSON、命令行或数据库返回值仍需要运行时检查。

保存为 `annotation_boundary.py` 并运行：

```python
def double(value: int) -> int:
    return value * 2

print(double(3))
print(double("3"))  # 静态检查应报告参数类型错误；解释器仍执行

def require_int(value: object) -> int:
    if type(value) is not int:
        raise TypeError("integer required")
    return value

try:
    require_int("3")
except TypeError:
    print("rejected")
```

输出为 `6`、`33`、`rejected`。这里刻意使用 `type(value) is int` 排除布尔值，因为 Python 的 bool 是 int 子类；若业务允许整数子类，应选择相应的 `isinstance` 规则。

练习：给 `require_int` 增加范围 1–100 的检查，分别验证 `0`、`True`、`"5"`、`5`。只有最后一个应通过。类型、转换和业务约束是三个独立决策，不要用一个注解代替它们。

## 🔗 相关文档

- 📄 **[FastAPI 核心速查](../framework-essentials/01-fastapi-essentials.md)** — 注解驱动的 Web 框架
- 📄 **[高级特性](../../basics/07-advanced-features.md)** — 泛型与 Protocol 的教程视角
- 📄 **[魔术方法与协议](./04-oop-protocols.md)** — Protocol 对应的运行时协议


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
