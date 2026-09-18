# 模块与导入系统 — import、包结构与 `__main__`

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#模块` `#导入` `#包` `#__main__` `#TYPE_CHECKING` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

普通 `.py` 文件通常对应一个模块；模块也可以是内置或扩展实现。含 `__init__.py` 的目录构成普通包，命名空间包则可以不含该文件。`import` 的本质：在 `sys.modules` 缓存中查找（或首次加载执行）模块，再把名字绑定到当前命名空间。理解它是理解 `__name__ == "__main__"`、循环导入、相对导入报错的前提。

## 📖 语法 / 签名

```python
import numpy as np                     # 导入模块并起别名
from pathlib import Path               # 从模块导入具体名字
from .models import Bookmark           # 包内相对导入（同目录）
from ..shared import utils             # 上一级包
from __future__ import annotations     # 独立语法示意：实际文件中置于普通导入前，可跟在模块文档字符串后

# 模块属性
__name__      # 直接运行时为 "__main__"，被导入时为模块名
__file__      # 模块文件路径

# 入口守卫
if __name__ == "__main__":
    main()

# 仅类型检查时导入（打破运行时循环导入的标准姿势）
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models import Bookmark
```

通常首次导入会执行顶层代码，后续同名导入复用 `sys.modules`。显式 reload、不同模块身份或失败重试等情况可能再次执行，不能据此设计只能发生一次的外部副作用。

## 💡 示例

```python
# 包结构
# bm/
# ├── __init__.py
# ├── models.py
# └── cli.py
# cli.py 内：
from .models import Bookmark            # 相对导入，包内首选

# 重导出公共 API（__init__.py 内）：
from .models import Bookmark            # 让调用方 from bm import Bookmark

# 延迟导入：import 开销大或存在循环依赖时，放进函数体
def render() -> str:
    import heavy_renderer               # 首次调用才加载
    return heavy_renderer.render()
```

## ⚠️ 常见陷阱

| 陷阱 | 说明 |
|------|------|
| `from module import *` | 污染命名空间、掩盖来源，生产代码禁用 |
| 脚本直接运行时相对导入报错 | `python bm/cli.py` 没有包上下文；用 `python -m bm.cli` |
| 循环导入 | A 与 B 互相依赖尚未初始化的名字，常见结果是部分初始化模块的导入错误；抽公共依赖，必要时推迟导入，不能笼统称为死锁 |
| 模块顶层做副作用 | 读文件、建连接会在"被 import"时意外执行 |
| 隐式命名包缺 `__init__.py` | 能跑但工具链（mypy/打包）行为易出偏差；普通包显式写 |
| `if __name__` 块里堆业务逻辑 | 守卫只留"组装"，逻辑进函数才能被导入复用 |

<!-- full-library-explanation -->
## 用两个文件区分导入和执行入口

前置知识是文件路径、模块名和函数定义。在同一目录创建 `helper.py`：

```python
print("helper loaded")

def add(a, b):
    return a + b

if __name__ == "__main__":
    print(add(2, 3))
```

再创建 `main.py`：

```python
import helper
import helper
print(helper.add(3, 4))
```

运行 `python main.py` 输出 `helper loaded` 一次，然后输出 `7`；运行 `python helper.py` 输出 `helper loaded` 与 `5`。入口守卫没有阻止模块加载，而是只让其中的代码在作为入口执行时运行。

练习：在模块顶层打开数据库连接会发生什么？答案是导入时就发生副作用，即使调用方只想读取一个常量。把资源创建放入应用启动流程并显式传给使用者，测试更容易控制它的生命周期。

## 🔗 相关条目

- 📄 **[第一个脚本教程](../../basics/02-first-script.md)** — `__main__` 惯用法的教程讲解
- 📄 **[关键字详解](./01-python-keywords.md)** — `import/from/as` 关键字层视角
- 📄 **[uv 包管理器](../framework-essentials/03-uv-package-manager.md)** — 包的安装分发对应工程侧
- 📄 **[故障排除](../quick-references/02-troubleshooting.md)** — 循环导入的修复决策表


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
