# os 与 sys — 系统接口与解释器接口

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#os` `#sys` `#环境变量` `#argv` `#标准流` `#退出码` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

两个"搭桥"标准库，桥的两端不同：**os** 面向操作系统（进程环境、文件系统、目录、进程创建），**sys** 面向 Python 解释器自身（命令行参数、模块缓存、标准流、递归限制、退出码）。一条分界线：**问"这台机器/这个进程环境"找 os，问"解释器的运行状态"找 sys**。路径拼接新代码归 pathlib（见 [标准库导航 §3](./01-standard-library.md)）。

## 📖 语法 / 详解

### os 模块导览

| 子领域 | 代表 API | 说明 |
|--------|----------|------|
| 环境 | `os.environ` / `os.getenv("KEY", default)` | 进程环境变量映射；getenv 读可选项给默认值 |
| 路径 | `os.path.join` / `splitext` / `exists` | 字符串路径工具箱；新代码优先 pathlib |
| 目录 | `os.getcwd` / `listdir` / `mkdir` / `makedirs(..., exist_ok=True)` | makedirs 递归建目录，已存在不报错 |
| 文件 | `os.remove` / `os.rename` / `os.replace` / `os.stat` | replace 用于替换目标；跨文件系统通常会失败，不能代替跨设备复制 |
| 进程 | `os.system` / `os.spawn*` | 官方文档明确"建议改用 subprocess"（本机实测无弃用警告，见下） |

最小示例（本机 3.14.7 实测）：

```python
import os

os.environ.get("HOME")             # '/home/you'
os.getenv("MISSING", "fallback")   # 'fallback'
os.path.join("a", "b")             # 'a/b'（Windows 为 'a\\b'）
os.path.splitext("app.tar.gz")     # ('app.tar', '.gz')
os.makedirs("out/logs", exist_ok=True)   # 目录已存在不抛错
```

### sys 模块导览

| 子领域 | 代表 API | 说明 |
|--------|----------|------|
| 命令行 | `sys.argv` | `["脚本名", 参数...]`，全是 str |
| 模块 | `sys.modules` / `sys.path` | 已导入模块缓存字典 / 模块搜索路径列表 |
| 标准流 | `sys.stdout` / `sys.stderr` / `sys.stdin` | print 的默认去处；测试重定向见 [pytest 速查](./03-pytest-testing.md) |
| 退出 | `sys.exit(code)` | 抛 `SystemExit`（实测 code=2 可被 except 捕获），main() 返回值交给它 |
| 版本 | `sys.version_info` | `(3, 14, 7, ...)` 元组，可比较；别解析 sys.version 字符串 |
| 递归 | `sys.getrecursionlimit` / `setrecursionlimit` | 当前限制由 getrecursionlimit 查询；调大不能修复无限递归 |

最小示例（本机 3.14.7 实测）：

```python
import sys

sys.version_info[:3]     # (3, 14, 7)
sys.version_info >= (3, 14)   # True —— 元组比较判版本
sys.argv                 # ['app.py', '--verbose']
sys.path                 # 搜索路径列表：脚本目录、site-packages 等
sys.modules["os"]        # 已导入则命中缓存
sys.exit(2)              # 抛 SystemExit(2)
```

### 职责边界（决策表）

| 需求 | 用 | 不用 |
|------|----|------|
| 路径拼接/遍历 | `pathlib` | `os.path`（遗留兼容） |
| 环境变量读取 | `os.environ`（应用配置配 pydantic-settings） | 手写解析 |
| 调外部命令 | `subprocess.run`（见 [06-functools-subprocess](./06-functools-subprocess.md)） | `os.system`（无捕获、注入风险） |
| 退出码 / argv / 标准流 | `sys` | `os` |
| 判断平台 | `sys.platform` / `os.name` | 硬编码绝对路径 |

## 💡 示例

一个体现分工的 CLI 骨架：os 管目录与环境，sys 管参数与退出码：

```python
import json
import os
import sys

def main() -> int:
    out_dir = os.environ.get("OUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "run-meta.json")
    with open(target, "w", encoding="utf-8") as f:
        json.dump({"argv": sys.argv[1:], "python": sys.version_info[:3]}, f)
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## ⚠️ 常见陷阱

- ❌ **`os.system` 拼接用户输入**：可能引入命令注入；不方便直接捕获标准流，返回值的含义还具有平台差异。
  ✅ `subprocess.run([...], capture_output=True, check=True)`，参数列表不经 shell 解析。
- ❌ **`os.environ["KEY"]` 读可选配置**：缺键直接 `KeyError` 崩在启动深处。
  ✅ `os.getenv("KEY", default)`；必填项在应用入口集中校验。
- ❌ **手工解析 `sys.version` 字符串判版本**：脆弱且难比较。
  ✅ `sys.version_info >= (3, 14)` 元组比较（实测）。
- ❌ **用 `sys.argv` 手撸复杂 CLI**：分支爆炸、没有 help。
  ✅ 两三个参数够用即可；再多上 argparse / typer（见 [生态库精选](./02-ecosystem-libs.md)）。
- ❌ **调大 recursionlimit 当"修复"栈溢出**：默认值由实现和环境决定，调大可能增加底层栈溢出的风险。
  ✅ 优先改迭代/显式栈；确需深递归再谨慎调整并恢复。

<!-- full-library-explanation -->
## 当前目录、解释器与退出码

前置知识是终端命令和相对路径。当前工作目录由启动方式决定，并不必然等于脚本所在目录；虚拟环境选中的是解释器和包搜索路径，也不会自动改变工作目录。因此“同一文件在编辑器能运行、在终端不能运行”需要分别检查路径和解释器。

保存为 `environment.py` 后运行 `python environment.py hello`。这个版本不依赖某个固定工作目录或环境变量值，而是验证 argv、cwd 与解释器路径的契约：

<!-- node-python-p1-final-case: python-os-sys-environment-contracts -->
```python
import os
import sys
from pathlib import Path

arguments = sys.argv[1:]
same_cwd = Path.cwd() == Path(os.getcwd())
has_interpreter = bool(sys.executable)

if arguments != ["hello"] or not same_cwd or not has_interpreter:
    raise AssertionError("os/sys environment contract failed")
print(f"os-sys-environment: argv={arguments!r}; cwd={same_cwd}; executable={has_interpreter}")
```

普通 Python 解释器下预期输出 `os-sys-environment: argv=['hello']; cwd=True; executable=True`。最后一个字段只确认解释器路径非空；诊断实际环境时打印 sys.executable 的具体值，再用该解释器执行 `-m pip` 或测试命令，避免安装到另一个环境。

练习：从父目录启动脚本，观察 argv 中的参数不变而 cwd 改变。需要项目数据文件时，应明确以工作目录、脚本目录还是配置路径为基准；不要用全局 chdir 偷偷改变其他模块的相对路径语义。

## 🔗 相关条目

- 📄 **[functools 与 subprocess](./06-functools-subprocess.md)** — `os.system` 的正解是 `subprocess.run`
- 📄 **[标准库导航](./01-standard-library.md)** — pathlib/json/logging 等场景导览
- 📄 **[模块与导入系统](../language-concepts/11-modules-imports.md)** — `sys.modules`/`sys.path` 背后的导入机制
- 🌐 **[官方文档：os](https://docs.python.org/3/library/os.html)** · **[sys](https://docs.python.org/3/library/sys.html)** — 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
