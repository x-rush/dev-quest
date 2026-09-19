# Python 3.14 t-string 正文围栏验证

核对日期：2026-09-20。验证在 WSL 的 asdf Python `3.14.7` 中进行；不改变用户的全局 Python 默认版本。

| 正文 | 原样抽取的含 t-string 围栏 | 检查 | 结果 |
|---|---:|---|---|
| [变量与类型](../../../../10-python-discovery/basics/03-variables-types.md) | 1 | `python -m py_compile` | PASS |
| [字符串格式化](../../../../10-python-discovery/reference/language-concepts/12-string-formatting.md) | 2 | `python -m py_compile` | PASS |

这只证明相应完整围栏在 Python 3.14.7 下能解析与编译。它不执行模板渲染、不验证第三方渲染库，也不把 Python 3.13 的不支持当作正文错误。此前全库库存扫描使用 Python 3.13.7 时出现的两项 `FAIL` 由此归类为工具链版本错配。
