# 异常体系 — 层级、异常链与 except*

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#异常` `#异常链` `#ExceptionGroup` `#自定义异常` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

Python 的一切异常都是 `BaseException` 子类的**对象**：捕获即按类型匹配继承链。工程化用法是"领域异常继承 `Exception` 建立自己的层级 + `raise ... from e` 保留原因链"，让错误既可分层捕获又可完整追溯。

## 📖 语法 / 签名

```text
继承主干（捕获时写 Exception 及其子类，不裸捕 BaseException）
BaseException
├── KeyboardInterrupt / SystemExit / GeneratorExit
└── Exception
    ├── ValueError / KeyError / TypeError / OSError ...
```

```python
try:
    risky()
except (ValueError, KeyError) as e:     # 多类型一组
    ...
except Exception as e:
    raise DomainError("业务失败") from e  # 异常链：__cause__ 保留原始异常
    # raise ... from None：显式隐藏底层细节
finally:
    cleanup()                            # 无论成败都执行

# 异常组：一次抛多个异常（asyncio.TaskGroup 的底层机制）
try:
    ...
except* ValueError as eg: ...            # 按类型分别处理同组内的多个异常
except* KeyError as eg: ...
```

自定义异常范式：业务包一个基类 `class AppError(Exception)`，细分错误继承它（`class NotFound(AppError)`），调用方可 `except AppError` 一网打尽。

## 💡 示例

```python
class StoreError(Exception):
    """存储层异常基类。"""

class CorruptStore(StoreError): ...

import json

def load(path: str) -> list[dict]:
    try:
        with open(path, encoding="utf-8") as stream:
            value = json.load(stream)
        if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
            raise CorruptStore("书签根节点必须是对象数组")
        return value
    except json.JSONDecodeError as e:
        raise CorruptStore(f"书签文件损坏: {path}") from e
        # traceback 同时展示 CorruptStore 与 "The above exception was the direct cause"
```

## ⚠️ 常见陷阱

| 陷阱 | 说明 |
|------|------|
| 裸 `except:` | 连 `KeyboardInterrupt`/`SystemExit` 都吞；至少写 `except Exception:` |
| `assert` 做参数校验 | `python -O` 下被整体剥离，生产校验用显式 `raise` |
| 混淆隐式上下文与显式原因 | except 内直接抛新异常通常保留 `__context__`；`from e` 明确设置 `__cause__`，`from None` 只抑制默认显示，不会抹掉底层异常对象 |
| 捕获后不处理不记录 | 静默吞异常让故障"消失"；确要吞用 `contextlib.suppress` 表达意图 |
| 把 except* 等同于异步专用语法 | 同步代码也能处理异常组；普通异常会按规则包装匹配，但通常使用常规 except 更清楚 |
| 在 `finally` 里 return | 会吞掉正在传播的异常 |

<!-- full-library-explanation -->
## 区分错误类型与错误原因

前置知识是 `try/except` 和函数调用栈。错误类型告诉调用方如何响应，原因链帮助维护者解释为什么失败。例如“书签存储损坏”属于应用层问题，底层原因可能是 JSON 无法解析；调用方可以捕获应用异常，日志仍保留解析位置。

下面的完整示例保存为 `exception_chain.py` 后运行：

```python
class ConfigError(Exception):
    pass

def read_port(text):
    try:
        return int(text)
    except ValueError as cause:
        raise ConfigError("port must be an integer") from cause

try:
    read_port("abc")
except ConfigError as error:
    print(type(error).__name__)
    print(type(error.__cause__).__name__)
```

输出 `ConfigError` 和 `ValueError`。练习：把输入改成 `"8080"`，函数应返回整数且不进入 except；再补充范围验证，使 `"70000"` 触发明确的应用异常。解析成功和业务合法是两次不同判断。

## 🔗 相关条目

- 📄 **[异常处理教程](../../basics/06-exceptions.md)** — try 结构与自定义异常的教程视角
- 📄 **[上下文管理器](./08-context-managers.md)** — `with` 的退出机制与 `finally` 同源
- 📄 **[asyncio 并发](./09-asyncio-concurrency.md)** — TaskGroup 用 ExceptionGroup 汇报多个子任务失败
- 📄 **[故障排除](../quick-references/02-troubleshooting.md)** — 异常类问题的症状速查


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
