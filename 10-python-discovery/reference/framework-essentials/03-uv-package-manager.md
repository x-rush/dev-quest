# uv 包管理器 — 项目、依赖与解释器一站式工具

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#uv` `#包管理` `#锁文件` `#PEP723` |
| **更新日期** | `2026年9月` |

## 📌 定义

uv 是 Rust 编写的 Python 包与项目管理器：替代 pip/venv/pip-tools 的安装与锁定职责，还能替你下载管理多个 Python 解释器本身。核心抽象是 `pyproject.toml`（声明意图）+ `uv.lock`（锁定精确依赖图），前者给人读，后者给机器复现。

## 📖 语法 / 签名

```bash
# 项目生命周期
uv init [--app|--lib] [--python 3.14]  # 生成 pyproject.toml、.python-version、main.py
uv add <pkg> [--dev]                   # 安装并写入 dependencies / dependency-groups
uv remove <pkg>                        # 移除依赖
uv lock [--upgrade]                    # 解析并生成/升级 uv.lock
uv sync [--frozen] [--no-dev]          # 按锁文件还原环境；--frozen 严格禁改锁
uv run <cmd>                           # 在项目环境中执行任意命令（自动同步）

# 解释器管理
uv python install 3.14                 # 安装指定版本解释器
uv python list / find                  # 列出可用版本 / 定位路径

# 工具与兼容层
uvx <tool> [args]                      # 临时环境运行 CLI 工具（等价 uv tool run）
uv pip install <pkg>                   # 兼容 pip 习惯用法的接口
```

PEP 723 内联脚本元数据：单文件脚本头部写 `# /// script` 块声明依赖，`uv run script.py` 自动为其建环境。

## 💡 示例

```bash
mkdir demo && cd demo
uv init --python 3.14
uv add fastapi "uvicorn[standard]"
uv add --dev pytest ruff mypy
uv run uvicorn main:app --reload
```

```python
# analysis.py —— 自带依赖的单文件脚本
# /// script
# requires-python = ">=3.14"
# dependencies = ["httpx"]
# ///
import httpx
print(httpx.get("https://example.com").status_code)
```

```bash
uv run analysis.py      # 自动创建临时环境、装好 httpx、执行
```

## ⚠️ 常见陷阱

| 陷阱 | 说明 |
|------|------|
| 绕过 `uv run` 直接敲 `python` | 用了系统解释器，报"找不到模块"；命令一律 `uv run` 前缀 |
| 不提交 `uv.lock` | 团队与 CI 依赖不可复现；`.venv/` 才是忽略对象 |
| `uv sync` 无脑带 `--upgrade` | 日常同步用 `uv sync`；升级是显式动作 `uv lock --upgrade` |
| 运行依赖与开发依赖混装 | pytest/ruff/mypy 进 `--dev` 组，生产镜像才能 `--no-dev` 裁剪 |
| `uvx` 用于长生命周期环境 | `uvx` 是一次性工具环境；项目依赖仍走 `uv add` |
| 忽视 `requires-python` 下限 | 写 `>=3.14` 却用旧解释器运行，解析期就会报错（好事，别绕过） |

## 🔗 相关条目

- 📄 **[环境搭建教程](../../basics/01-environment-setup.md)** — uv 的入门工作流
- 📄 **[开发工具链](../../frameworks/04-devtools.md)** — uv 在工具链中的位置
- 📄 **[pytest 测试指南](../library-guides/03-pytest-testing.md)** — `uv add --dev pytest` 之后的事
- 📄 **[容器化部署](../../deployment/01-docker-deployment.md)** — `uv sync --frozen` 的镜像化用法
