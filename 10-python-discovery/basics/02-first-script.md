# 第一个 Python 脚本 — REPL 与 `__main__` 惯用法

> **文档简介**: 从交互式 REPL 到可执行脚本，理解 Python 代码的两种运行方式与 `if __name__ == "__main__"` 背后的模块机制
>
> **目标读者**: 已完成环境搭建、想跑通第一段 Python 代码的开发者
>
> **前置知识**: 已安装 Python 3.12+ 与 uv（见[环境搭建](./01-environment-setup.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#REPL` `#脚本` `#模块机制` `#入口函数` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 使用 REPL 快速验证表达式与 API
- ✅ 编写并运行第一个 `.py` 脚本
- ✅ 解释 `__name__ == "__main__"` 的原理并正确使用
- ✅ 使用类型注解写出符合现代风格的入口代码

---

## 1. REPL：即时反馈的实验场

在项目目录执行 `uv run python`（或 `uv run python -q` 简化输出）进入交互式解释器：

```python
>>> 2 ** 10
1024
>>> name = "python"
>>> name.upper()
'PYTHON'
>>> sorted("python")
['h', 'n', 'o', 'p', 't', 'y']
>>> help(str.replace)   # 随时查阅文档
```

REPL 的高效用法：

| 特性 | 说明 |
|------|------|
| `_` | 保存上一次表达式的结果 |
| Tab 补全 | 自动补全属性与方法名 |
| `help(obj)` | 查看对象文档 |
| `exit()` 或 Ctrl+D | 退出 |

> 💡 REPL 适合验证"这一行能不能这么写"；一旦代码超过 10 行，就该写进脚本文件。

---

## 2. 第一个脚本

新建 `hello.py`：

```python
"""练习脚手架：演示脚本结构与现代写法。"""

import sys


def greet(name: str, greeting: str = "Hello") -> str:
    """返回问候语。"""
    return f"{greeting}, {name}!"


def main(argv: list[str] | None = None) -> int:
    """程序入口：解析参数并打印问候。"""
    args = sys.argv[1:] if argv is None else argv
    target = args[0] if args else "World"
    print(greet(target))
    return 0  # 退出码，0 表示成功


if __name__ == "__main__":
    raise SystemExit(main())
```

运行：

```bash
uv run hello.py          # Hello, World!
uv run hello.py Python   # Hello, Python!
echo $?                  # 0（上一条命令的退出码）
```

逐点解析：

- **模块 docstring**：文件首行三引号字符串，`help(hello)` 时展示
- **类型注解**：`name: str`、`-> str` 为现代 Python 标配，编辑器据此提供提示
- **`list[str] | None`**：3.12+ 直接用内置泛型和 `|` 联合类型，无需 `typing.Optional`
- **`main` 返回退出码**：让脚本可被 shell 与 CI 判断成败

---

## 3. `__main__` 惯用法详解

`if __name__ == "__main__":` 是 Python 最著名的惯用法，机制如下：

1. Python 每个 `.py` 文件都是一个**模块**，模块有个字符串属性 `__name__`
2. **直接运行**某文件时，该文件的 `__name__` 被设为 `"__main__"`
3. 被 **import** 时，`__name__` 等于模块名（如 `"hello"`）

```python
# hello.py 底部
print(f"__name__ = {__name__}")
if __name__ == "__main__":
    main()
```

```bash
uv run hello.py                 # __name__ = __main__（会执行 main）
uv run python -c "import hello" # __name__ = hello（不会执行 main）
```

**为什么必须写它**：没有这行，`import hello` 会立即执行 `main()`——测试框架、其他模块导入时都会"误触发"程序。加上守卫后，同一文件既能被导入复用，又能直接执行。

---

## 4. 脚本 vs 模块：组织雏形

当逻辑变多，把可复用部分拆为函数/类，`__main__` 块只留"组装"：

```python
# bookmarks.py 的典型骨架
def load(path: str) -> dict[str, str]:
    ...

def add(data: dict[str, str], title: str, url: str) -> None:
    ...

def main() -> int:
    data = load("bookmarks.json")
    add(data, "Python", "https://python.org")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

这个骨架贯穿整个入门路径，第 08 篇的综合项目将扩展为命令行工具。

---

## ✅ 最佳实践

- ✅ **入口统一命名为 `main()`** 并返回退出码
- ✅ **`if __name__ == "__main__"` 里用 `raise SystemExit(main())`**，退出码可测试
- ✅ **为函数写 docstring**（第一行一句话即可）
- ❌ **避免**：模块顶层写副作用代码（读文件、发请求）
- ❌ **避免**：`if __name__ == "__main__"` 里堆业务逻辑
- 💡 **技巧**：`uv run python -i hello.py` 脚本跑完后进入 REPL，可接着调用其中函数

---

## ❓ 常见问题

### Q1: `python hello.py` 和 `python -m hello` 有区别吗？
**A**: 有。前者按路径运行；后者把 `hello` 当模块运行，会先把它所在目录加入 `sys.path`，且 `__name__` 同样是 `"__main__"`。包内脚本推荐 `-m` 方式。

### Q2: 为什么 `uv run python` 而不是直接 `python`？
**A**: `uv run` 保证使用项目 `.venv` 的解释器，直接 `python` 可能命中系统版本，依赖不一致。

---

## 🎯 练习与实践

### 练习一：改造脚本
1. 给 `greet` 增加 `punctuation: str = "!"` 参数
2. 支持 `hello.py <name> <greeting>`：第二个参数作为问候词
3. 参数缺失时返回退出码 1 并打印用法提示

### 练习二：验证模块机制
1. 在 `main()` 中加入 `print(__name__)`
2. 分别用 `uv run hello.py` 与 `uv run python -c "import hello"` 观察 `__name__`
3. 写一段话解释两种输出差异的原因

**提示**：差异来自 Python 导入系统对"主模块"的约定，与[变量与类型](./03-variables-types.md)中的对象属性机制一脉相承。

---

## 🔗 相关文档

- 📄 **[变量与类型](./03-variables-types.md)** — 理解 `str`、`list[str]` 的类型世界
- 📄 **[内置函数全表](../reference/language-concepts/02-built-in-functions.md)** — `print`、`help` 等内建能力速查
- 📄 **[Python 一行式速查](../reference/quick-references/01-python-cheatsheet.md)** — REPL 常用表达集锦
