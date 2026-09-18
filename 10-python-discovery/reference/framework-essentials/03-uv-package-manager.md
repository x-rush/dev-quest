# uv 包管理器 — 项目、依赖与解释器一站式工具

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#uv` `#包管理` `#锁文件` `#PEP723` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

uv 是 Rust 编写的 Python 包与项目管理器：替代 pip/venv/pip-tools 的安装与锁定职责，还能替你下载管理多个 Python 解释器本身。核心抽象是 `pyproject.toml`（声明意图）+ `uv.lock`（锁定精确依赖图），前者给人读，后者给机器复现。

## 📖 语法 / 签名

```bash
# 项目生命周期
uv init [--app|--lib] [--python 3.14]  # 生成 pyproject.toml、.python-version、main.py
uv add <pkg> [--dev]                   # 安装并写入 dependencies / dependency-groups
uv remove <pkg>                        # 移除依赖
uv lock [--upgrade]                    # 解析并生成/升级 uv.lock
uv sync [--locked|--frozen] [--no-dev] # locked 检查声明一致性；frozen 跳过锁文件更新检查
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

最后一条要求 main.py 中已定义 FastAPI 的 app；uv init 生成的默认脚本并不自动包含 Web 应用，先使用[FastAPI 最小应用](./01-fastapi-essentials.md)。

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
| 绕过 `uv run` 直接敲 `python` | 可能使用不同解释器；可以用 uv run，或显式激活/指定项目虚拟环境，关键是确认解释器路径 |
| 不提交 `uv.lock` | 团队与 CI 依赖不可复现；`.venv/` 才是忽略对象 |
| `uv sync` 无脑带 `--upgrade` | 日常同步用 `uv sync`；升级是显式动作 `uv lock --upgrade` |
| 运行依赖与开发依赖混装 | pytest/ruff/mypy 进 `--dev` 组，生产镜像才能 `--no-dev` 裁剪 |
| `uvx` 用于长生命周期环境 | uvx 在隔离的工具环境运行，可复用缓存；项目依赖应走 uv add，不能假设工具环境就是项目环境 |
| 忽视 `requires-python` 下限 | 写 `>=3.14` 却用旧解释器运行，解析期就会报错（好事，别绕过） |

<!-- full-library-explanation -->
## 声明、锁定与安装是三个状态

前置知识是虚拟环境和依赖版本。pyproject.toml 描述允许的依赖范围，uv.lock 记录解析结果，.venv 是当前机器上的安装产物。只复制 .venv 不能替代可重建的依赖声明；只改 pyproject 也不意味着运行环境已经变化。

在一个已有 uv.lock 的练习项目中，先运行 `uv sync --locked`，再执行 `uv run python -c "import sys; print(sys.executable)"`，确认命令来自项目环境。修改依赖声明后再次执行 --locked：若修改要求重新解析锁文件，它应失败，提醒你更新并审阅锁文件。

`--frozen` 使用现有锁文件而不检查它是否与声明保持最新；它不等于 --locked 的一致性检查。CI 一般需要明确选择哪一种语义，见[锁定与同步说明](https://docs.astral.sh/uv/concepts/projects/sync/)。练习：在独立副本中比较两者对过期锁文件的反应，并记录哪一步修改了哪些文件。

## 🔗 相关条目

- 📄 **[环境搭建教程](../../basics/01-environment-setup.md)** — uv 的入门工作流
- 📄 **[开发工具链](../../frameworks/04-devtools.md)** — uv 在工具链中的位置
- 📄 **[pytest 测试指南](../library-guides/03-pytest-testing.md)** — `uv add --dev pytest` 之后的事
- 📄 **[容器化部署](../../deployment/01-docker-deployment.md)** — `uv sync --frozen` 的镜像化用法


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
