# enum — 枚举类型

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#enum` `#枚举` `#IntEnum` `#StrEnum` `#常量` `#状态机` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

enum 用"有限的、命名的常量集合"替代裸字符串与魔法数字：`OrderState.SHIPPED` 可读、可被 IDE 重构、访问不存在的成员名时抛 AttributeError（静态检查器也可能提前提示）。成员是**单例**，普通 Enum 的默认相等语义基于成员身份，可用 == 比较成员——`Color.RED == 1` 为 `False`，这是特性：防止枚举与裸值混用。状态、方向等有限集合可以使用枚举；开放字符串集合或简单布尔开关未必需要单独建枚举。

## 📖 语法 / 详解

### 定义与成员

```python
from enum import Enum, auto

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = auto()          # 此处为 3；Python 3.13+ 默认取已有最大值加一
```

成员三要素：`Color.RED.name` → `'RED'`，`Color.RED.value` → `1`，在同一个枚举类内是对应成员；重新加载模块可能创建新的类，不应称为跨加载或跨进程的全局唯一对象。

### 成员访问与比较

```python
Color.RED is Color(1)        # True：按值反查
Color["RED"] is Color.RED    # True：按名查
Color.RED == 1               # False：普通 Enum 默认不等于裸整数
Color.RED is Color.RED       # True：身份比较
Color.RED in Color           # True：成员判断
{Color.RED: "stop"}[Color.RED]   # 可哈希，可作字典键
list(Color)                  # [Color.RED, Color.GREEN, Color.BLUE] 按定义序遍历
```

### 混入型：IntEnum / StrEnum（StrEnum 在 3.11 新增）

```python
from enum import IntEnum, StrEnum

class Level(IntEnum):
    LOW = 1
    HIGH = 2

Level.HIGH > Level.LOW       # True：可与 int 比较、排序
int(Level.HIGH)              # 2

class Format(StrEnum):
    TEXT = "text"

str(Format.TEXT)             # 'text'：f"{Format.TEXT}" 直接插值
```

`IntEnum` 适合持久化/协议编码，`StrEnum` 适合替代字符串常量（header 名、状态标签）。普通 Enum 与 int/str **不**互通——这是防误用的特性，需要互操作时才选混入型。

普通 Enum 的上述相等关系是默认语义，不应推广到所有混入类或覆写了比较方法的类。IntEnum 运算后通常得到普通 int；StrEnum 的字符串操作通常得到普通 str。需要精确 str 类型的 API 可显式使用 str(member)。

### 别名、@unique 与 @verify

```python
class Loose(Enum):
    A = 1
    B = 1            # 不报错：B 成为 A 的别名（Loose.B is Loose.A，遍历只出 1 个）

from enum import unique, verify, UNIQUE, CONTINUOUS

@unique
class Strict(Enum):
    A = 1
    B = 1            # ValueError: duplicate values found in <enum 'Strict'>: B -> A
```

`@unique` 等价于 `@verify(UNIQUE)`；`CONTINUOUS` 检查整数成员值是否连续，不限于 auto 生成的值。别名机制本身合法——可用于给旧名起文档化新名。

### 枚举方法与属性

成员 value 可以是元组，配合自定义 `__init__` 拆成属性（按官方 Planet 模式）：

```python
class Planet(Enum):
    MERCURY = (3.303e+23, 2.4397e6)
    EARTH = (5.976e+24, 6.37814e6)

    def __init__(self, mass, radius):    # 每个成员的 value 元组拆入 __init__
        self.mass = mass
        self.radius = radius

    def surface_gravity(self):
        G = 6.67300E-11
        return G * self.mass / (self.radius ** 2)

round(Planet.EARTH.surface_gravity(), 1)   # 9.8
```

### 函数式 API

```python
Status = Enum("Status", "OK FAIL")                        # 空格分隔名
HttpStatus = Enum("HttpStatus", [("OK", 200), ("NOT_FOUND", 404)])   # 名值对
```

适合配置驱动、动态生成；常规代码用 class 语法更可读。

### 组合标志与版本边界

Flag 用于可组合的位标志，IntFlag 还保留整数互操作性；auto() 为标志生成二的幂。它们适合“读、写可同时开启”，而普通 Enum 更适合“一次只有一个订单状态”。判断是否包含某权限要用位运算，不能通过数值大小比较。

Python 3.12 起，枚举类的 in 检查也接受有效裸值；在旧版中对非成员查询可能抛 TypeError。跨版本的输入转换直接使用 EnumType(value) 并处理 ValueError 更明确。Python 3.13 起普通 Enum 默认 auto 取已有最大值加一；对协议和数据库持久化值应显式指定，避免重排成员后改变编码。

## 💡 示例

订单状态机：StrEnum + auto()（值自动取小写成员名：`['pending', 'shipped']`）：

```python
from enum import StrEnum, auto

class OrderState(StrEnum):
    PENDING = auto()      # 值 = 'pending'
    SHIPPED = auto()      # 值 = 'shipped'

def ship_action(state: OrderState) -> str:
    if state is OrderState.PENDING:      # 身份比较
        return "立即发货"
    return "查看物流"

ship_action(OrderState.PENDING)          # '立即发货'
f"state={OrderState.SHIPPED}"            # 'state=shipped' —— JSON/日志友好
```

## ⚠️ 常见陷阱

- ❌ **用字符串比较写状态分支**：`if status == "pending"` 拼错无警告、无补全。
  ✅ `if status is OrderState.PENDING`；外部输入先调用 OrderState(value) 并处理 ValueError；函数注解本身不会挡住非法值。
- ❌ **期待 `Color.RED == 1` 为 True**：普通 Enum 默认不等于其裸整数值（默认行为为 False）。
  ✅ 需要 int 互操作用 `IntEnum`，或显式取 `.value`。
- ❌ **重复 value 当两个成员用**：第二个静默变成别名。
  ✅ 加 `@unique` 强制唯一；确实要别名时写注释说明新旧名关系。
- ❌ **动态名/值查询不设防**：`Color["PURPLE"]` 抛 KeyError、`Color(99)` 抛 ValueError。
  ✅ 先查 `"PURPLE" in Color.__members__` 或用 try/except 包住反查。
- ❌ **在业务代码里用 `range(len(...))` 遍历成员**：绕开枚举抽象。
  ✅ 直接 `for member in Color` 或 `list(Color)`，按定义序迭代。

<!-- full-library-explanation -->
## 在输入边界把字符串转换为枚举

前置知识是类、比较和异常。枚举让合法状态有明确名字，但不会自动限制一个普通函数的实际参数。来自 JSON 的字符串需要显式转换，再进入只处理枚举的业务函数。

完整实验保存为 `states.py`，Python 3.11+ 运行：

```python
from enum import StrEnum

class State(StrEnum):
    PENDING = "pending"
    SHIPPED = "shipped"

print(State("pending") is State.PENDING)
print(State.PENDING == "pending")
try:
    State("unknown")
except ValueError:
    print("invalid state")
```

输出 `True`、`True`、`invalid state`。StrEnum 故意保留字符串互操作性，因此不能套用“枚举永远不等于裸值”的说法。

练习：即使 pending 与 shipped 都是合法成员，从 shipped 再次发货是否合理？枚举只限制状态集合，状态转移还需要业务规则，重复发货的幂等处理也需要单独设计。

## 可复现验证：成员集合与业务转移分别验证

以下两个完整 Python 3.12+ 程序不依赖其它片段。保存为 `.py` 执行，异常必须匹配预期类型，不能仅凭“出现报错”判断正确。

### 别名、查询和混入类型

<!-- library-case: python-enum-contract -->
```python
from enum import Enum, IntEnum, StrEnum, auto, unique

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = auto()
    CRIMSON = 1

assert Color(1) is Color.RED
assert Color['RED'] is Color.RED
assert Color.CRIMSON is Color.RED
assert [member.name for member in Color] == ['RED', 'GREEN', 'BLUE']
assert list(Color.__members__) == ['RED', 'GREEN', 'BLUE', 'CRIMSON']
assert Color.RED != 1
assert {Color.RED: 'stop'}[Color.CRIMSON] == 'stop'

for lookup, error_type in [(lambda: Color(99), ValueError),
                           (lambda: Color['MISSING'], KeyError)]:
    try:
        lookup()
    except error_type:
        pass
    else:
        raise AssertionError('invalid lookup succeeded')

try:
    @unique
    class Duplicate(Enum):
        A = 1
        B = 1
except ValueError:
    pass
else:
    raise AssertionError('duplicate values accepted by unique')

class Level(IntEnum):
    LOW = 1
    HIGH = 2

class Format(StrEnum):
    TEXT = auto()

assert Level.HIGH == 2
assert type(Level.HIGH + 1) is int
assert str(Format.TEXT) == 'text'
assert Format.TEXT == 'text'
assert type(Format.TEXT.upper()) is str
print('enum-contract: identity, alias, lookup, unique, mixed types')
```

输出为 `enum-contract: identity, alias, lookup, unique, mixed types`。别名在 `__members__` 中可见，但正常遍历只列规范成员；混入型成员参与计算后可能丢失枚举类型。对外协议使用 `.value` 还是字符串表示必须明确，不应依赖调试用的 repr。

### 合法状态不等于合法转移

<!-- library-case: python-enum-transition -->
```python
from enum import Flag, StrEnum, auto

class State(StrEnum):
    PENDING = 'pending'
    SHIPPED = 'shipped'
    CANCELLED = 'cancelled'

def parse_state(raw):
    if not isinstance(raw, str):
        raise TypeError('state must be text')
    return State(raw)

def ship(state):
    if not isinstance(state, State):
        raise TypeError('convert input to State first')
    if state is not State.PENDING:
        raise ValueError('only pending orders may ship')
    return State.SHIPPED

assert ship(parse_state('pending')) is State.SHIPPED
for action, expected in [
    (lambda: parse_state('unknown'), ValueError),
    (lambda: parse_state(1), TypeError),
    (lambda: ship('pending'), TypeError),
    (lambda: ship(State.SHIPPED), ValueError),
    (lambda: ship(State.CANCELLED), ValueError),
]:
    try:
        action()
    except expected:
        pass
    else:
        raise AssertionError('invalid state or transition accepted')

class Permission(Flag):
    READ = auto()
    WRITE = auto()

granted = Permission.READ | Permission.WRITE
assert (granted & Permission.READ) == Permission.READ
assert (Permission.READ & Permission.WRITE) == Permission(0)
print('enum-transition: input boundary, state rule, flags')
```

输出为 `enum-transition: input boundary, state rule, flags`。这里选择“重复发货拒绝”的业务规则；如果接口要幂等返回已发货结果，应单独定义规则并确保不重复扣库存或发送通知。枚举只表达内存状态，数据库更新还需要条件更新或事务，才能防止并发请求重复改变状态。

练习：增加 DELIVERED，先写合法转移表再修改业务函数；把 READ/WRITE 组合的枚举和订单单一状态分别建模。命名证据与复现命令见 [Node/Python 标准库验证](../../../shared-resources/tools/document-quality/reports/node-python-libraries.md)。

## 🔗 相关条目

- 📄 **[dataclass 数据类](../language-concepts/13-dataclasses.md)** — 枚举字段 + frozen 数据模型的常见组合
- 📄 **[类型注解全表](../language-concepts/05-typing-annotations.md)** — `Literal` 与 Enum 的分工对比
- 📄 **[标准库导航](./01-standard-library.md)** — 标准库场景地图
- 🌐 **[官方文档：enum](https://docs.python.org/3/library/enum.html)** — 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
