# 模块与导入系统 — import、包结构与 `__main__`

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#模块` `#导入` `#包` `#__main__` `#TYPE_CHECKING` |
| **更新日期** | `2026年9月` |

## 📌 定义

每个 `.py` 文件是一个**模块**，含 `__init__.py` 的目录是一个**包**。`import` 的本质：在 `sys.modules` 缓存中查找（或首次加载执行）模块，再把名字绑定到当前命名空间。理解它是理解 `__name__ == "__main__"`、循环导入、相对导入报错的前提。

## 📖 语法 / 签名

```python
import numpy as np                     # 导入模块并起别名
from pathlib import Path               # 从模块导入具体名字
from .models import Bookmark           # 包内相对导入（同目录）
from ..shared import utils             # 上一级包
from __future__ import annotations     # 编译器指令，必须放文件首

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

模块首次被导入时其顶层代码执行**且仅执行一次**（之后命中 `sys.modules` 缓存）。

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
| 循环导入 | A 导 B、B 导 A 在加载期死锁；抽公共模块 / `TYPE_CHECKING` / 函数内导入 |
| 模块顶层做副作用 | 读文件、建连接会在"被 import"时意外执行 |
| 隐式命名包缺 `__init__.py` | 能跑但工具链（mypy/打包）行为易出偏差；普通包显式写 |
| `if __name__` 块里堆业务逻辑 | 守卫只留"组装"，逻辑进函数才能被导入复用 |

## 🔗 相关条目

- 📄 **[第一个脚本教程](../../basics/02-first-script.md)** — `__main__` 惯用法的教程讲解
- 📄 **[关键字详解](./01-python-keywords.md)** — `import/from/as` 关键字层视角
- 📄 **[uv 包管理器](../framework-essentials/03-uv-package-manager.md)** — 包的安装分发对应工程侧
- 📄 **[故障排除](../quick-references/02-troubleshooting.md)** — 循环导入的修复决策表
