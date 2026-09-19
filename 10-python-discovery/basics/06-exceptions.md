# 异常处理 — 异常体系与上下文管理器

## 先理解，再动手

异常表达失败，with 保证按协议退出和清理。只捕获你能够处理的异常，不能把所有失败悄悄改成空数据。

**本节自测**：处理合法整数、非法字符串，再比较 int(None) 的异常类型。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

ValueError 与 TypeError 不同；能够解释捕获范围，而不是依赖 except Exception 隐藏原因。

</details>

> **文档简介**: 理解 Python 异常类层次与 EAFP 哲学，掌握 try/except/else/finally 全结构、自定义异常设计，以及 with 上下文管理器的资源管理模型
>
> **目标读者**: 已掌握控制流、即将编写真实 I/O 代码的开发者
>
> **前置知识**: 完成[控制流与推导式](./05-control-flow.md)，了解函数与类

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#异常` `#try-except` `#上下文管理器` `#EAFP` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 描述 `BaseException → Exception → 具体异常` 的类层次
- ✅ 正确使用 try/except/else/finally 及异常链
- ✅ 设计模块级自定义异常
- ✅ 用 `with` 管理文件、锁、连接等资源，并实现自己的上下文管理器

---

## 1. 异常体系：一切皆对象

```
BaseException
├── KeyboardInterrupt      # Ctrl+C（不该被捕获）
├── SystemExit             # sys.exit() 触发
└── Exception              # 业务异常的根
    ├── ValueError         # 值类型正确但内容不合法
    ├── TypeError          # 类型用错
    ├── KeyError / IndexError
    ├── FileNotFoundError  # OSError 家族
    └── 自定义异常应挂在这里
```

两个设计要点：

- 捕获时写 `except Exception` 起步，**永远不要裸 `except:`**（会把 Ctrl+C 也吞掉）
- 捕获顺序从**具体到一般**，因为 except 按顺序命中第一个匹配项

**Python 的 EAFP 哲学**（Easier to Ask Forgiveness than Permission）：先尝试，失败再处理，与 Go/C 的先检查（LBYL）相反：

```python
# LBYL：先检查
if "price" in product and isinstance(product["price"], int):
    total += product["price"]

# EAFP：Python 地道写法
try:
    total += product["price"]
except (KeyError, TypeError):
    pass
```

---

## 2. try 的完整结构

```python
import json

def load_config(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"配置 {path} 不存在，使用默认配置")
        return {}
    except json.JSONDecodeError as e:        # as 拿到异常实例
        print(f"配置不是合法 JSON: {e}")
        return {}
    else:
        print("配置加载成功")                 # 无异常时才执行
    finally:
        print("清理动作（无论如何都执行）")
```

各块职责：

| 块 | 何时执行 | 典型用途 |
|------|------|------|
| `try` | 总是 | 可能出错的操作 |
| `except` | 匹配的异常发生 | 恢复/降级/转换 |
| `else` | try 无异常 | 成功路径逻辑（缩小 try 范围） |
| `finally` | 无论如何 | 释放资源（通常交给 with） |

**重新抛出与异常链**：

```python
def parse_int(text: str) -> int:
    try:
        return int(text)
    except ValueError as e:
        raise ValueError(f"非法数字: {text!r}") from e   # 保留原始异常
```

`raise ... from e` 在日志中同时显示两个异常栈，排查链式故障必需；`raise` 单独一行则在 except 块中原样重抛当前异常。

---

## 3. 自定义异常：建模业务错误

```python
class BookmarkError(Exception):
    """书签模块异常基类。"""

class DuplicateBookmark(BookmarkError):
    """URL 已存在。"""

class InvalidUrl(BookmarkError):
    """URL 格式不合法。"""

def add_bookmark(url: str, store: set[str]) -> None:
    if not url.startswith("http"):
        raise InvalidUrl(f"非 http(s) 地址: {url}")
    if url in store:
        raise DuplicateBookmark(f"已收藏: {url}")
    store.add(url)
```

设计准则：

- 每个模块一个异常基类，调用方可以 `except BookmarkError` 一网打尽
- 异常名以 `Error` 结尾，描述信息放进异常参数
- 库代码抛异常、命令行入口统一捕获转成退出码

---

## 4. with 与上下文管理器

资源管理的标准答案是 `with`，它在代码块退出时**保证**调用清理逻辑——无论正常结束还是异常退出：

```python
# 文件：退出时自动 close，异常也不会泄漏句柄
with open("data.txt", encoding="utf-8") as f:
    content = f.read()

# 多个资源
with open("src.txt") as src, open("dst.txt", "w") as dst:
    dst.write(src.read())
```

**自己实现上下文管理器**：`__enter__` 返回资源，`__exit__` 负责清理：

```python
import time

class Timer:
    def __enter__(self) -> "Timer":
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.cost = time.perf_counter() - self.start
        print(f"耗时 {self.cost:.3f}s")
        return False   # False=异常继续传播；True=吞掉异常（慎用）

with Timer():
    sum(range(10_000_000))
```

简单场景用 `contextlib.contextmanager` 装饰器更省事：

```python
from contextlib import contextmanager

@contextmanager
def open_db(uri: str):
    conn = create_connection(uri)   # 生成前 = __enter__
    try:
        yield conn                  # yield 的值 = as 变量
    finally:
        conn.close()                # 生成后 = __exit__
```

---

## ✅ 最佳实践

try 的范围应覆盖同一个需要处理的失败操作，而非机械限制成一行；范围过大会把后续无关错误误当作同一种输入问题。捕获尽可能明确的类型，补上下文后保留原因，或交给能够处理它的上层。

支持上下文管理协议的资源优先用 with，其他资源仍需按契约关闭。Python 中异常有时就是正常协议的一部分，如迭代结束，不应一概禁止；关键是不要吞掉未知错误或靠异常掩盖本来可清楚表达的控制流。

---

当配置文件“缺失”允许使用默认值，而内容损坏必须阻止启动时，不能用 `except Exception: return {}` 把两者合并。最小决策是只对 FileNotFoundError 返回默认配置，对 JSONDecodeError 转换为 ConfigError 并保留原因；权限错误仍交给上层处理。

**验收：** 分别使用不存在的文件、合法 JSON、损坏 JSON 和无法读取的路径；前三者应得到默认值、配置对象、带原因链的错误，第四种不能伪装成默认配置。日志可记录配置路径，但不要输出包含令牌的完整配置内容。异常链与精确捕获规则见 [Python 官方异常教程](https://docs.python.org/3/tutorial/errors.html)。

## ❓ 常见问题

### Q1: finally 和 with 都能清理资源，用哪个？
**A**: 有现成上下文管理器的资源（文件/锁/连接）用 with；finally 留给确实需要"无论如何执行"的自定义逻辑。

---

## 🎯 练习与实践

### 练习一：健壮的配置加载
1. 实现 `load_config(path)`：文件缺失返回 `{}`，JSON 损坏抛自定义异常 `ConfigError` 并用 `from e` 链接原始异常
2. 编写调用方，统一 `except ConfigError` 打印友好提示

### 练习二：实现计数上下文管理器
1. 用 `@contextmanager` 实现 `count_calls(name)`：进入计数 +1、退出打印总次数，并验证块内抛异常时计数依然正确

---

## 🔗 相关文档

- 📄 **[高级特性](./07-advanced-features.md)** — 异步世界的异常传播
- 📄 **[魔术方法与协议](../reference/language-concepts/04-oop-protocols.md)** — `__enter__`/`__exit__` 完整协议
- 📄 **[常见错误排查](../reference/quick-references/02-troubleshooting.md)** — 异常相关高频坑


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
