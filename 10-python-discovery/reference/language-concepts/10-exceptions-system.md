# 异常体系 — 层级、异常链与 except*

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#异常` `#异常链` `#ExceptionGroup` `#自定义异常` |
| **更新日期** | `2026年9月` |

## 📌 定义

Python 的一切异常都是 `BaseException` 子类的**对象**：捕获即按类型匹配继承链。工程化用法是"领域异常继承 `Exception` 建立自己的层级 + `raise ... from e` 保留原因链"，让错误既可分层捕获又可完整追溯。

## 📖 语法 / 签名

```python
# 继承主干（捕获时写 Exception 及其子类，不裸捕 BaseException）
BaseException
├── KeyboardInterrupt / SystemExit / GeneratorExit
└── Exception
    ├── ValueError / KeyError / TypeError / OSError ...

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
        return json.loads(open(path, encoding="utf-8").read())
    except json.JSONDecodeError as e:
        raise CorruptStore(f"书签文件损坏: {path}") from e
        # traceback 同时展示 CorruptStore 与 "The above exception was the direct cause"
```

## ⚠️ 常见陷阱

| 陷阱 | 说明 |
|------|------|
| 裸 `except:` | 连 `KeyboardInterrupt`/`SystemExit` 都吞；至少写 `except Exception:` |
| `assert` 做参数校验 | `python -O` 下被整体剥离，生产校验用显式 `raise` |
| 丢异常链直接 `raise NewError` | 不写 `from e` 会丢失原始堆栈，排查成本翻倍 |
| 捕获后不处理不记录 | 静默吞异常让故障"消失"；确要吞用 `contextlib.suppress` 表达意图 |
| `except*` 用在同步普通场景 | `except*` 只服务异常组；普通异常用常规 `except` |
| 在 `finally` 里 return | 会吞掉正在传播的异常 |

## 🔗 相关条目

- 📄 **[异常处理教程](../../basics/06-exceptions.md)** — try 结构与自定义异常的教程视角
- 📄 **[上下文管理器](./08-context-managers.md)** — `with` 的退出机制与 `finally` 同源
- 📄 **[asyncio 并发](./09-asyncio-concurrency.md)** — TaskGroup 用 ExceptionGroup 汇报多个子任务失败
- 📄 **[故障排除](../quick-references/02-troubleshooting.md)** — 异常类问题的症状速查
