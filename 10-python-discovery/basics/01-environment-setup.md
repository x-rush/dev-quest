# Python 环境搭建 — uv 与现代工具链

> **文档简介**: 从零搭建 Python 3.14 开发环境，掌握 uv 包管理器、虚拟环境、ruff 代码检查与 VS Code 配置
>
> **目标读者**: 有其他语言经验、首次系统学习 Python 的开发者
>
> **前置知识**: 基本命令行操作，了解包管理器概念（npm/cargo/go mod 任一即可）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#环境搭建` `#uv` `#虚拟环境` `#ruff` `#工具链` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 安装并验证 Python 3.14 环境
- ✅ 使用 uv 创建项目、管理虚拟环境与依赖
- ✅ 理解虚拟环境为何必要，以及它与 venv/pip 的关系
- ✅ 配置 ruff 完成代码格式化与静态检查
- ✅ 在 VS Code 中获得类型提示、调试与格式化一体化体验

---

## 1. 安装 Python 3.14

2026 年的当前稳定版本为 Python 3.14 系列（维护版 3.14.7），新项目建议直接使用 **Python 3.14**。推荐用 uv 统一管理 Python 版本本身：

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

安装 uv 后，Python 解释器也交给它管理：

```bash
# 安装指定版本的解释器
uv python install 3.14

# 查看可用与已安装版本
uv python list
```

验证安装：

```bash
uv python find 3.14     # 输出解释器路径
uv run python --version # Python 3.14.x
```

> 💡 uv 兼容 venv/pip 工作流但快 10-100 倍，且能替你下载管理多个 Python 版本，避免污染系统解释器。

---

## 2. 为什么需要虚拟环境

Python 的第三方包默认装进**全局解释器**。两个项目若依赖同一包的不同版本，就会冲突。虚拟环境为每个项目提供隔离的包目录：

```
项目A (pydantic 2.12)  ─┐
                       ├─ 各自独立的 site-packages
项目B (pydantic 2.13) ─┘
```

传统做法是 `python -m venv .venv` + 手动 `activate`；uv 把这一切简化为自动完成。

---

## 3. 用 uv 创建第一个项目

```bash
mkdir demo && cd demo
uv init --python 3.14   # 生成 pyproject.toml、.python-version、main.py
```

生成的 `pyproject.toml` 是项目的唯一事实来源（类似 `package.json`）：

```toml
[project]
name = "demo"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = []
```

添加依赖并运行：

```bash
uv add rich          # 安装并写入 dependencies，自动创建 .venv
uv add --dev ruff    # 开发依赖写入 dependency-groups
uv run main.py       # 在项目环境中运行脚本
```

**常用命令速览**：

| 命令 | 作用 |
|------|------|
| `uv add <pkg>` | 添加运行依赖 |
| `uv remove <pkg>` | 移除依赖 |
| `uv lock` | 锁定精确版本（生成 uv.lock） |
| `uv sync` | 按 lock 文件还原环境 |
| `uv run <cmd>` | 在项目环境中执行命令 |
| `uv pip install <pkg>` | 兼容 pip 习惯用法 |

> ⚠️ 陷阱：`uv run` 才会使用项目虚拟环境；直接敲 `python main.py` 用的是系统解释器，会报"找不到模块"。

---

## 4. 传统方案：venv + pip（需要认识）

团队或旧项目仍可能使用 venv，必须能看懂：

```bash
python -m venv .venv          # 创建虚拟环境
source .venv/bin/activate     # Linux/macOS 激活（Windows: .venv\Scripts\activate）
pip install requests          # 此时的 pip 安装到 .venv
deactivate                    # 退出虚拟环境
```

导出依赖用 `pip freeze > requirements.txt`，还原用 `pip install -r requirements.txt`。uv 同样支持这套流程（`uv venv`、`uv pip install`），可无缝迁移。

---

## 5. ruff：一个工具管格式与检查

ruff 用 Rust 编写，整合了 Black（格式化）、isort（导入排序）、flake8（代码检查）三大工具的功能：

```bash
uv run ruff check .       # 静态检查（未用变量、未定义名、常见 bug）
uv run ruff format .      # 格式化（Black 风格）
uv run ruff check --fix . # 自动修复可修复问题
```

在 `pyproject.toml` 中配置规则：

```toml
[tool.ruff]
line-length = 100
target-version = "py314"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]  # 基础/导入/升级建议/bug 警告
```

`UP` 规则组会提示现代写法，例如用 `X | None` 替代 `Optional[X]`。

---

## 6. VS Code 配置

推荐扩展：

- **Python**（微软官方）— 语言支持与调试
- **Pylance** — 基于 Pyright 的类型检查与智能提示
- **Ruff** — 保存时自动格式化与修复

工作区设置 `.vscode/settings.json`：

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports.ruff": "explicit",
      "source.fixAll.ruff": "explicit"
    }
  },
  "python.analysis.typeCheckingMode": "basic"
}
```

关键点：`defaultInterpreterPath` 指向项目 `.venv` 中的解释器，编辑器内运行、调试、提示才与命令行一致。Windows 下路径为 `.venv\\Scripts\\python.exe`。

调试：按 F5 选择"Python File"，断点、变量查看、REPL 均开箱即用。

---

## ✅ 最佳实践

- ✅ **每个项目一个虚拟环境**：uv 会在 `uv add` 时自动创建 `.venv`
- ✅ **提交 pyproject.toml 与 uv.lock**，忽略 `.venv/`（写入 .gitignore）
- ✅ **工具统一走 `uv run`**：保证 `ruff`、`pytest` 等使用项目环境
- ❌ **避免**：在系统解释器上 `pip install`；把 `.venv` 提交进 git
- 💡 **技巧**：`uvx <tool>` 可免安装直接运行工具，如 `uvx ruff check .`

---

## 🎯 练习与实践

### 练习一：搭建项目
1. 用 `uv init` 创建 `pylab` 项目，指定 Python 3.14
2. 添加 `rich` 依赖，编写脚本打印彩色表格
3. 用 `uv run ruff check --fix .` 清理代码

### 练习二：环境隔离验证
1. 在 `pylab` 中 `uv add "pydantic==2.12"`
2. 新建 `pylab2` 项目，`uv add pydantic`（最新版，2.13.x）
3. 分别运行打印版本号的脚本，确认两环境版本不同

**评估标准**：`pylab` 内 `uv run python -c "import pydantic; print(pydantic.VERSION)"` 输出 2.12.x。

---

## 🔗 相关文档

- 📄 **[第一个 Python 脚本](./02-first-script.md)** — 环境就绪后的下一步
- 📄 **[Python 关键字详解](../reference/language-concepts/01-python-keywords.md)** — 语言核心概念入口
- 📄 **[标准库导航](../reference/library-guides/01-standard-library.md)** — 了解解释器自带的能力边界
