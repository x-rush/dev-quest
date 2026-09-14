# 函数参数 — 位置/关键字、*args/**kwargs 与默认值时机

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#函数` `#参数` `#keyword-only` `#positional-only` `#默认值` `#注解` |
| **更新日期** | `2026年9月` |

## 📌 定义

参数形态决定"调用方能怎么传"。Python 共四种形态（PEP 570 / PEP 3102 落地的仅位置与仅关键字）：`/` 前仅位置、中间位置或关键字、`*` 后仅关键字、外加收集用的 `*args`/`**kwargs`。默认值在**函数定义时求值一次**——这是可变默认参数陷阱的根源，也是修复 late binding 的武器。

## 📖 语法 / 详解

### 四种形态一张图

```python
def f(pos_only, /, normal, *, kw_only):
    ...
#     └─ 仅位置        └─ 位置或关键字    └─ 仅关键字
```

完整签名顺序（不可调换）：`def f(仅位置, /, 普通, *args, 仅关键字, **kwargs)`。

调用矩阵（本机 3.14.7 实测）：

```python
def f(a, /, b, *, c):
    return (a, b, c)

f(1, 2, c=3)        # (1, 2, 3)
f(1, b=2, c=3)      # (1, 2, 3)
f(x=1, b=2, c=3)    # TypeError: f() got an unexpected keyword argument 'x'
f(1, 2, 3)          # TypeError: f() takes 2 positional arguments but 3 were given
```

### 默认值：定义时求值一次

```python
import time

def log(t=time.time()): return t    # t 在 def 执行那一刻固定
log() == log()                       # True（实测）—— 所有调用共享同一时刻

def append_to(v, target=[]):         # 所有调用共享同一个 list 对象
    target.append(v)
    return target

append_to(1)    # [1]
append_to(2)    # [1, 2] —— 不是 [2]！（实测）
append_to.__defaults__   # ([1, 2],) —— 默认值就存在函数对象上（实测）
```

正确姿势是哨兵 `None` + 函数体内新建：

```python
def append_to(v, target=None):
    target = [] if target is None else target
    target.append(v)
    return target
```

### *args / **kwargs 与解包调用

```python
def report(*args, **kwargs):
    return args, kwargs

report(1, 2, mode="fast")       # ((1, 2), {'mode': 'fast'})

def area(w, h, *, unit="m2"):
    return f"{w * h} {unit}"

shape = (3, 4); opt = {"unit": "cm2"}
area(*shape, **opt)             # '12 cm2'（实测）—— 序列解包 + 字典解包
```

解包是调用侧语法：`f(*iterable)` 把序列摊开成位置参数，`f(**mapping)` 把字典摊开成关键字参数（键必须是 str 且与参数名对得上）。

### 实际用途

- **仅位置 `/`**：参数名只是实现细节，调用方不依赖名字——官方 API 用它保留将来重命名/改签名的自由，也避免参数与 `**kwargs` 的键冲突（如 `len(obj)` 不接受 `obj=...`）。
- **仅关键字 `*`**：布尔与可选参数必须写名，调用点自文档化——`sorted(data, key=..., reverse=True)` 就是范例。
- **`*args, **kwargs`**：装饰器透传任意签名（见 [06-decorators](./06-decorators.md)）、代理转发、变长聚合。

### 类型注解

注解在定义时存入 `f.__annotations__`（实测 `{'a': <class 'int'>, 'b': <class 'str'>, 'return': list[int]}`），运行时**不强制**——传 str 给 int 参数照常执行。它们是给 IDE、mypy 与 FastAPI/Pydantic 这类"注解驱动框架"看的。写法全表见 [05-typing-annotations](./05-typing-annotations.md)。

## 💡 示例

FastAPI 风格的签名设计：位置参数收主数据，仅关键字防布尔误传，注解驱动校验：

```python
def create_user(
    name: str, /
    *,                                  # 之后必须写名调用
    email: str = "",
    is_admin: bool = False,
    tags: list[str] | None = None,      # 可变默认值的正确替代
) -> dict:
    return {"name": name, "email": email, "is_admin": is_admin,
            "tags": tags or []}

create_user("ada", email="a@x.io")
# {'name': 'ada', 'email': 'a@x.io', 'is_admin': False, 'tags': []}（实测）
create_user("ada", True)
# TypeError: create_user() takes 1 positional argument but 2 were given（实测）
```

## ⚠️ 常见陷阱

- ❌ **可变默认参数**：`def f(x, acc=[])` —— 状态跨调用累积（实测 `[1, 2]`）。
  ✅ `acc=None` + 函数体内新建；dataclass 字段用 `field(default_factory=list)`（见 [13-dataclasses](./13-dataclasses.md)）。
- ❌ **默认值在调用时求值的假设**：`def log(t=time.time())` 拿到的是模块导入时刻。
  ✅ 需要运行时值就在函数体内 `t = time.time()`。
- ❌ **给仅位置参数传关键字**：`len(obj=...)` 抛 TypeError。
  ✅ `/` 之前的参数按位置传；这是官方锁定签名自由度的手段。
- ❌ **`f(*d)` 解包 dict**：摊开的是**键**，不是值。
  ✅ 字典转关键字参数用 `f(**d)`。
- ❌ **给仅关键字参数传位置值**：`f(1, 2, 3)` 抛 TypeError。
  ✅ `*` 之后一律写名，让布尔/选项参数在调用点可读。

## 🔗 相关条目

- 📄 **[装饰器](./06-decorators.md)** — `*args/**kwargs` 透传签名的标准场景
- 📄 **[闭包与作用域](./15-closures-and-scope.md)** — 默认参数 `i=i` 是 late binding 的解药
- 📄 **[类型注解全表](./05-typing-annotations.md)** — 注解写法与静态检查
- 📄 **[dataclass 数据类](./13-dataclasses.md)** — `kw_only=True` 把参数防呆搬进数据类
- 🌐 **[官方文档：More on Defining Functions](https://docs.python.org/3/tutorial/controlflow.html#more-on-defining-functions)** — 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
