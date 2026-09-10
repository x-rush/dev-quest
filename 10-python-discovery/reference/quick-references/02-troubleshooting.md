# 常见错误排查 — 可变默认参数 / GIL / 循环导入

## 概述

Python 新手到中级最常踩的坑集合：症状 → 原因 → 修复。每条可独立跳入阅读。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#排查` `#陷阱` `#GIL` `#循环导入` |
| **更新日期** | `2026年9月` |

---

## 1. 可变默认参数

**症状**: 多次调用共享状态，列表/字典"越攒越多"。

```python
def add_item(item, items=[]):       # ❌ 默认值在定义时创建一次
    items.append(item)
    return items

add_item("a")  # ['a']；再 add_item("b") → ['a', 'b']，期望 ['b']
```

**原因**: 默认值存于函数对象的 `__defaults__`，全程只求值一次。

**修复**:

```python
def add_item(item, items: list | None = None):
    if items is None:
        items = []                  # 每次调用新建
    items.append(item)
    return items
```

---

## 2. GIL 与并发选型

**症状**: 多线程跑 CPU 密集任务，速度不升反降。

**原因**: CPython 的全局解释器锁（GIL）保证同一时刻仅一个线程执行 Python 字节码。I/O 等待会释放 GIL（多线程对网络/磁盘有效），CPU 计算不释放。

**决策表**:

| 任务类型 | 方案 |
|---------|------|
| 网络/磁盘 I/O 并发 | `asyncio`（首选）或线程池 |
| CPU 密集 | `multiprocessing` / `ProcessPoolExecutor` |
| 兼容阻塞库的过渡 | 线程池 `run_in_executor` |

```python
from concurrent.futures import ProcessPoolExecutor
with ProcessPoolExecutor() as pool:
    results = list(pool.map(cpu_heavy, inputs))
```

**附注**: Python 3.13 提供 free-threaded（no-GIL）实验构建，生态适配中；2026 年的默认解释器仍带 GIL，按上表选型即可。

---

## 3. 循环导入（circular import）

**症状**: `ImportError: cannot import name 'X' from partially initialized module`。

```python
# models.py: from storage import save      # storage 又导入 models → 死锁
# storage.py: from models import Bookmark
```

**修复**（按优先级）:

1. **抽取第三模块**：共同依赖下沉到 `base.py`（根治）
2. **类型注解延迟**：`from __future__ import annotations` + `if TYPE_CHECKING: from models import Bookmark`
3. **函数内导入**：把 import 移到调用处（局部规避，勿滥用）

---

## 4. `UnboundLocalError`

**症状**: 明明有全局变量，函数里却说未绑定。

```python
count = 0
def bump():
    count += 1        # ❌ 赋值使 count 成为局部变量，读取时未初始化
```

**修复**: 函数内写 `global count`（或改传参返回值——更推荐）。

---

## 5. 浅拷贝假象

**症状**: `b = a[:]` 后改 `b[0]`，`a[0]` 也变——切片/`copy()` 只复制外层容器。

**修复**: 嵌套结构用 `copy.deepcopy(a)`。

---

## 6. 编码与 UTF-8

**症状**: Windows 上读文件出现 `UnicodeDecodeError` 或乱码。

**原因**: `open` 不写 `encoding` 时使用平台默认编码（Windows 非 UTF-8）。

**修复**: 所有文本 IO 显式 `open(path, encoding="utf-8")`；跨平台 JSON 读写同理。

---

## 7. 浮点精度

**症状**: `0.1 + 0.2 != 0.3`。

**修复**: 比较用 `math.isclose(a, b)`；金额用 `decimal.Decimal("0.1")`（字符串初始化）。

---

## 8. `is` vs `==`

**症状**: `a = 256; b = 256; a is b` 为 True，`a = 257; b = 257` 为 False。

**原因**: 小整数缓存（-5~256）是解释器优化副作用，`is` 比较的是身份而非值。

**修复**: 值比较一律 `==`；`is` 仅用于 `is None` 等单例。

---

## 9. 迭代中修改容器

**症状**: 遍历 list 时删除元素导致跳项；遍历 dict 时增删键抛 `RuntimeError`。

**修复**: 遍历副本 `for x in list(xs):`，或用推导式构建新容器。

---

## 10. 协程里的阻塞调用

**症状**: FastAPI 服务在 `async def` 路由中调用 `requests`/`time.sleep`，整个服务卡顿。

**原因**: 事件循环单线程，无 `await` 让出则无法调度其他任务。

**修复**: 换异步等价物（httpx/`asyncio.sleep`）；无法替换时把该路由改成 `def`（自动跑线程池）。

---

## 11. `TypeError: 'NoneType' object is not ...`

**症状**: 链式调用中间某步返回了 `None`（常见于 `sort()`、`append()` 这类**原地操作**）。

```python
xs = xs.sort()        # ❌ sort 原地排序返回 None
xs = sorted(xs)       # ✅ sorted 返回新列表
```

**修复**: 牢记"原地方法返回 None"；链式前检查每步返回值。

---

## 快速定位方法论

1. **读栈底再读栈顶**：最后一行是异常类型与消息，第一段是你代码的入口
2. **最小重现**：把报错代码缩到 REPL 能复现的最小片段
3. **类型三查**：`type(x)`、`repr(x)`、`id(x)` —— 类型、内容、身份；怀疑状态污染时逐段注释二分

---

## 🔗 相关文档

- 📄 **[异常处理](../../basics/06-exceptions.md)** — 异常体系教程
- 📄 **[函数与类](../../basics/04-functions-oop.md)** — 可变默认参数的完整语境
- 📄 **[高级特性](../../basics/07-advanced-features.md)** — asyncio 阻塞问题的背景知识
