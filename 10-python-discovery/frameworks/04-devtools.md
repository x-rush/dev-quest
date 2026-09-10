# 开发工具链 — uv、ruff、mypy 与 IPython

> **文档简介**: 组装 Python 3.12+ 的现代工具链：uv 管依赖与脚本、ruff 一站式检查与格式化、mypy 静态类型检查、IPython/Jupyter 交互实验与调试
>
> **目标读者**: 已完成环境搭建、想让日常开发更顺滑的开发者
>
> **前置知识**: [环境搭建](../basics/01-environment-setup.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#uv` `#ruff` `#mypy` `#IPython` `#工具链` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 熟练使用 uv 的依赖、锁文件与开发依赖工作流
- ✅ 配置 ruff 统一代码风格并自动修复问题
- ✅ 开启 mypy 让类型注解真正参与检查
- ✅ 用 IPython/Jupyter 做交互实验与事后调试

---

## 1. uv：依赖与脚本

```bash
uv init --app myapp             # 初始化项目（pyproject.toml + .python-version）
uv add fastapi                  # 添加依赖并更新 uv.lock
uv add --dev pytest ruff mypy   # 开发依赖进入 dependency-groups
uv remove fastapi               # 移除依赖
uv sync --frozen                # CI/生产：严格按锁文件还原环境
uv run pytest                   # 在项目环境中运行任意命令
uv lock --upgrade               # 升级锁文件中的版本
```

**要点**：

- `uv.lock` 必须提交进仓库——它保证团队成员与 CI 的依赖完全一致
- 单文件脚本也能声明依赖：文件头写 PEP 723 元数据（`# /// script` 块）后 `uv run script.py` 即自动装环境
- 环境异常时先 `uv sync` 重建，再查[故障排除字典](../reference/quick-references/02-troubleshooting.md)

## 2. ruff：一个工具干掉 flake8 + black + isort

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM"]   # 基础错误/pyflakes/导入排序/bugbear/现代化/简化

[tool.ruff.format]
quote-style = "double"
```

```bash
uv run ruff check .            # 静态检查
uv run ruff check --fix .      # 自动修复可修复项
uv run ruff format .           # 格式化（black 替代品）
```

**要点**：`UP` 规则会提示把旧写法升级为 3.12 现代写法（如 `X | None` 替代 `Optional[X]`）；规则含义见[关键字与语法字典](../reference/language-concepts/01-python-keywords.md)。

## 3. mypy：让类型注解真正生效

```bash
uv add --dev mypy
uv run mypy .
```

```toml
# pyproject.toml —— 渐进收紧，先跑通再逐包开启 strict
[tool.mypy]
python_version = "3.12"
check_untyped_defs = true
warn_unused_ignores = true
```

```python
def parse_port(value: str) -> int:
    if not value.isdigit():
        raise ValueError(f"非法端口: {value}")
    return int(value)

parse_port("8000")   # ✅
parse_port(8000)     # ❌ mypy: Argument 1 has incompatible type "int"; expected "str"
```

**要点**：

- 类型注解完整语法见[类型注解字典](../reference/language-concepts/05-typing-annotations.md)
- FastAPI/Pydantic 的校验与 mypy 天然协同：签名即文档即校验
- 遇到第三方库缺类型时用 `py.typed` 覆盖或按需 `# type: ignore[错误码]`，别全局豁免

## 4. IPython / Jupyter：交互实验与调试

```bash
uv add --dev ipython
uv run ipython                 # 增强版 REPL：Tab 补全、? 帮助、魔法命令
```

```python
# IPython 中的常用手法
In [1]: from decimal import Decimal
In [2]: Decimal("0.1") + Decimal("0.2")        # 快速验证语言/库行为
Out[2]: Decimal('0.3')

In [3]: %timeit [x**2 for x in range(1000)]    # 微基准（系统剖析见性能专题）
```

- **事后调试**：程序抛异常后，在 IPython 里执行 `%debug` 直接跳进异常现场检查变量
- **断点调试**：代码中写 `breakpoint()`（内建函数，见[内置函数字典](../reference/language-concepts/02-built-in-functions.md)），进入 pdb/IPython 调试器
- **Jupyter**：`uv add --dev jupyterlab` 后 `uv run jupyter lab`，适合数据分析类实验；实验性 notebook 不进生产代码目录

## ✅ 最佳实践

- 运行时依赖与开发依赖分离：pytest/ruff/mypy 一律进 `--dev` 组
- ruff + mypy 进 pre-commit 与 CI（流水线配置见[CI/CD](../deployment/02-ci-cd-pipelines.md)）
- 复杂问题排查套路：REPL 复现 → 最小代码 → 写成 pytest 回归（见[单元测试](../testing/01-unit-testing.md)）

## ❓ 常见问题

**Q1: ruff 和 mypy 功能重叠吗？**
不重叠。ruff 管代码风格与静态缺陷模式（lint），mypy 管类型正确性，两者互补且都在 CI 中运行。

**Q2: `uv run` 与手动激活虚拟环境有何区别？**
`uv run` 确保命令跑在项目锁文件定义的环境里，无需 activate，也避免误用全局解释器。

---

## 🔗 相关文档

- 📄 **[环境搭建](../basics/01-environment-setup.md)** — uv 安装与项目初始化的入门篇
- 📖 **[类型注解](../reference/language-concepts/05-typing-annotations.md)** — mypy 检查的语法基础
- 📖 **[故障排除](../reference/quick-references/02-troubleshooting.md)** — 环境与依赖问题速查
- 🧪 **[单元测试](../testing/01-unit-testing.md)** — 工具链的下一个环节
- 🚀 **[CI/CD 流水线](../deployment/02-ci-cd-pipelines.md)** — ruff/mypy/pytest 自动化
