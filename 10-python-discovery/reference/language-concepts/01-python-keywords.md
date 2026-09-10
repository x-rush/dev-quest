# Python 关键字与软关键字详解

## 概述

Python 3.12 共有 **35 个硬关键字**与 3 个**软关键字**（`match`/`case`/`_`）。硬关键字不可用作标识符；软关键字仅在特定语法上下文中被解释为关键字，其余场景可作普通名字。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#关键字` `#语法基础` `#软关键字` |
| **更新日期** | `2026年9月` |

## 快速总览

| 分组 | 关键字 |
|------|------|
| 值与逻辑 | `True` `False` `None` `and` `or` `not` `is` `in` |
| 分支 | `if` `elif` `else` |
| 循环 | `for` `while` `break` `continue` `else` |
| 函数、类与作用域 | `def` `return` `yield` `lambda` `class` `pass` `global` `nonlocal` `del` |
| 异常 | `try` `except` `finally` `raise` `assert` |
| 导入与上下文 | `import` `from` `as` `with` |
| 异步 | `async` `await` |
| 软关键字 | `match` `case` `_` |

---

## 1. 值、逻辑与身份 — True/False/None, and/or/not, is/in

**定义**: 三个单例常量；`and`/`or`/`not` 短路求值并返回**操作数本身**而非布尔值；`is` 比较对象身份，`in` 测试成员关系。

```python
result: str | None = None
if result is None: ...                # 判 None 用 is，不用 ==
name = "" or "默认名"                  # or 短路返回第一个真值
a = [1, 2]; b = a
a is b                                # True 仅当同一对象；值比较不用 is
"py" in langs                         # 成员测试（调 __contains__/__eq__）
```

**陷阱**: `or` 默认值无法区分"缺失"与"显式传 0/空串"（精确场景用 `if key in config`）；小整数/短字符串命中 `is` 是驻留优化副作用；`bool` 是 `int` 子类（`True + True == 2`）。

---

## 2. 分支 — if/elif/else 与 match/case

**定义**: `elif` 链按序求值，表达式位置可用三元形式；3.10+ 的 `match-case` 做结构化模式匹配，`match`/`case`/`_` 是**软关键字**，也可作普通变量名。

```python
label = "hot" if temp > 30 else "cool"    # 三元表达式
match command.split():
    case ["go", direction]:               # 序列解构模式
        print(f"向 {direction} 走")
    case ["quit"] | ["exit"]: ...         # 或模式
    case _:                               # 通配模式
        print("未知命令")
match = 1                                 # ✅ 软关键字可作变量名
```

**陷阱**: `case value:` 中裸变量是**捕获模式**（赋值而非比较），匹配常量需用点号路径（`Status.OK`）或字面量；`_` 另是 REPL 上次结果与解包占位（`first, *_, last = data`）。

---

## 3. 循环 — for/while/break/continue/else

**定义**: 两种循环加两个跳转控制；**循环可带 else**：未被 `break` 打断时执行。

```python
for item in iterable:
    if item == target:
        break
else:
    print("未找到")                       # 没有 break 才执行
while queue: process(queue.pop())         # 条件循环
```

**陷阱**: `for i in range(len(lst))` 是反模式，用 `enumerate`；循环变量在结束后仍存活于作用域。

---

## 4. 函数与类 — def/return/yield/lambda/class/pass

**定义**: `def` 定义函数，函数体出现 `yield` 即为生成器函数；`lambda` 是匿名单表达式函数；`pass` 是空操作占位。

```python
def counter():
    n = 0
    while True:
        n += 1
        yield n                          # return 仅停止迭代；无 return 返回 None
class PluginBase: pass                   # 空类占位
```

**陷阱**: `lambda` 仅限单表达式，复杂逻辑一律用 `def`；生成器一次性耗尽，复用需重新调用。

---

## 5. 作用域 — global/nonlocal/del

**定义**: `global` 声明引用模块级名字；`nonlocal` 声明引用外层函数变量；`del` 解绑名字（不必然删对象）。

```python
count = 0
def bump():
    global count                         # 引用模块级名字
    count += 1
def outer():
    n = 0
    def inner(): nonlocal n; n += 1      # 引用外层函数变量
```

**陷阱**: 函数内对名字赋值即创建局部变量，除非声明 global/nonlocal——`UnboundLocalError` 的根源。

---

## 6. 异常 — try/except/finally/raise/assert

**定义**: 异常处理五件套；`assert` 用于调试断言，`-O` 下被剥离。

```python
try:
    risky()
except ValueError as e:
    raise RuntimeError("处理失败") from e
# finally: cleanup() — 无论是否异常都执行
```

**陷阱**: `assert` 做参数校验会在 `python -O` 下失效（生产校验用显式 `raise`）；裸 `except:` 连 `KeyboardInterrupt` 都吞，至少写 `except Exception:`。

---

## 7. 导入与上下文 — import/from/as, with/as

**定义**: `from ... import ...` 引入具体名字，`as` 重命名；`with` 触发上下文管理协议，保证退出时执行清理。

```python
import numpy as np
from pathlib import Path
with open("data.txt", encoding="utf-8") as f:
    text = f.read()                      # 离开块自动 close，异常也不泄漏
```

**陷阱**: `from module import *` 污染命名空间，禁止用于生产代码；循环导入用函数内延迟导入或 `if TYPE_CHECKING:`。

---

## 8. 异步 — async/await

**定义**: 定义协程与挂起点；`await` 只能出现在 `async def` 内。

```python
async def fetch() -> None:
    await asyncio.sleep(1)               # 让出事件循环
```

**陷阱**: 协程内调用阻塞函数（`time.sleep`/同步 IO）会冻结整个事件循环。

---

## 陷阱速查表

| 陷阱 | 说明 |
|------|------|
| `== None` / 用 `is` 比较值 | 改用 `is None`；`is` 只用于 None/单例 |
| 裸 `except:` | 至少 `except Exception:` |
| `assert` 做校验 | `-O` 下失效 |
| `case` 匹配变量 | 裸名是捕获模式，常量要点号访问 |
| 函数内改全局变量 | 忘写 `global` 触发 `UnboundLocalError` |

---

## 🔗 相关文档

- 📄 **[内置函数全表](./02-built-in-functions.md)** — 与关键字配合的内建能力
- 📄 **[控制流与推导式](../../basics/05-control-flow.md)** — 分支循环的教程式讲解
- 📄 **[异常处理](../../basics/06-exceptions.md)** — try/except 家族的完整用法
