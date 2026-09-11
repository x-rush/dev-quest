# 综合项目 — 命令行书签管理器（typer + rich）

> **文档简介**: 综合运用入门路径全部知识，从零构建一个命令行书签管理器：typer 定义命令、rich 美化输出、JSON 持久化、dataclass 建模、异常体系兜底
>
> **目标读者**: 已完成 basics 01-07 的学习者，需要一个收束型的实战项目
>
> **前置知识**: 全部入门文档；异步与泛型部分不涉及，可回顾[高级特性](./07-advanced-features.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#实战项目` `#typer` `#rich` `#CLI` `#JSON` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本项目后，你将能够：

- ✅ 用 typer 构建多命令 CLI，用 rich 输出表格与彩色提示
- ✅ 用 dataclass + JSON 完成数据的建模与持久化
- ✅ 组织"模型—存储—命令"三层结构的小型项目

---

## 1. 项目设计

**功能需求**：

| 命令 | 行为 |
|------|------|
| `bm add <url> --title 标题 --tag 标签` | 添加书签，URL 去重 |
| `bm list [--tag 标签]` | 表格展示，可按标签过滤 |
| `bm find 关键词` | 标题/URL 模糊搜索（基础练习实现） |
| `bm rm <序号>` | 删除指定书签 |

**技术选型**：typer（基于类型注解的 CLI 框架）+ rich（typer 已内置依赖）+ 标准库 `json`/`pathlib`。

**目录结构**：

```
bm/
├── pyproject.toml
└── bm/
    ├── __init__.py
    ├── models.py      # 数据模型（dataclass）
    ├── storage.py     # 存储层（JSON 读写 + 异常）
    └── cli.py         # 命令入口（typer）
```

初始化：

```bash
uv init --python 3.14 bm && cd bm
uv add "typer[all]"
```

`pyproject.toml` 补充入口，让 `uv run bm` 直接可用：

```toml
[project.scripts]
bm = "bm.cli:app"
```

---

## 2. 数据模型层 `models.py`

```python
"""书签数据模型。"""
from dataclasses import dataclass, field, asdict

@dataclass
class Bookmark:
    url: str
    title: str
    tags: list[str] = field(default_factory=list)

    def matches(self, keyword: str) -> bool:
        """大小写不敏感的模糊匹配。"""
        kw = keyword.lower()
        return kw in self.title.lower() or kw in self.url.lower()
```

> 回顾：`field(default_factory=list)` 规避可变默认参数陷阱（见[函数与类](./04-functions-oop.md)第 3 节）。

---

## 3. 存储层 `storage.py`

```python
"""JSON 文件存储 + 模块异常体系。"""
import json
from pathlib import Path
from .models import Bookmark

STORE_PATH = Path.home() / ".bm.json"

class StoreError(Exception):
    """存储层异常基类。"""


def load() -> list[Bookmark]:
    try:
        raw = json.loads(STORE_PATH.read_text(encoding="utf-8"))
        return [Bookmark(**item) for item in raw]
    except FileNotFoundError:
        return []                          # 首次使用，空库
    except (json.JSONDecodeError, TypeError) as e:
        raise StoreError(f"书签文件损坏: {STORE_PATH}") from e


def save(bookmarks: list[Bookmark]) -> None:
    data = [asdict(b) for b in bookmarks]
    STORE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
```

要点：数据文件字段为 `url: str`、`title: str`、`tags: list[str]`；读入时 `Bookmark(**item)` 完成字典到 dataclass 的转换；损坏数据走异常链而非静默。

---

## 4. 命令层 `cli.py`

```python
"""typer 命令入口。"""
import typer
from rich.console import Console
from rich.table import Table
from . import storage
from .models import Bookmark

app = typer.Typer(help="命令行书签管理器")
console = Console()

@app.command()
def add(url: str, title: str = "",
        tag: list[str] = typer.Option(None, "--tag", "-t")) -> None:
    """添加书签（URL 重复则拒绝）。"""
    bookmarks = storage.load()
    if any(b.url == url for b in bookmarks):
        console.print(f"[red]已存在:[/] {url}")
        raise typer.Exit(code=1)
    bookmarks.append(Bookmark(url=url, title=title or url, tags=tag or []))
    storage.save(bookmarks)
    console.print(f"[green]✓[/] 已添加 [bold]{title or url}[/]")


@app.command("list")
def list_bookmarks(tag: str | None = typer.Option(None, "--tag", "-t")) -> None:
    """列出书签，可按标签过滤。"""
    bookmarks = [b for b in storage.load() if tag is None or tag in b.tags]
    table = Table(title=f"书签 ({len(bookmarks)} 条)")
    table.add_column("序号", justify="right")
    table.add_column("标题")
    table.add_column("URL", style="cyan")
    for i, b in enumerate(bookmarks, start=1):
        table.add_row(str(i), b.title, b.url)
    console.print(table)


@app.command()
def rm(index: int) -> None:
    """按 list 显示的序号删除。"""
    bookmarks = storage.load()
    try:
        removed = bookmarks.pop(index - 1)
    except IndexError as e:
        raise typer.BadParameter(f"序号超范围: {index}") from e
    storage.save(bookmarks)
    console.print(f"[green]✓[/] 已删除 {removed.title}")
```

typer 的魔法：**函数签名即 CLI 接口**——类型注解决定参数解析方式，docstring 即 `--help` 文案，`typer.Option` 定制选项名。这正是[高级特性](./07-advanced-features.md)装饰器知识的落地。

---

## 5. 运行与验证

```bash
uv run bm add https://docs.python.org --title "Python 文档" --tag 官方
uv run bm list                    # rich 表格输出；数据落在 ~/.bm.json
uv run bm add https://docs.python.org --title x && echo $?   # 1，重复被拒
```

---

## ✅ 最佳实践

- ✅ **三层分离**：models/storage/cli 各司其职，存储可替换
- ✅ **退出码语义化**：成功 0、业务失败 1、参数错误由 typer 处理
- ✅ **用户输出与日志分离**：rich 面向人，异常栈面向调试
- ❌ **避免**：把业务逻辑写进命令函数（保持"命令=编排"）；路径集中到 `storage.STORE_PATH` 常量

---

## 🎯 练习与实践

### 基础练习
- [ ] 实现 `bm find 关键词`：复用 `Bookmark.matches()` 做模糊搜索
- [ ] 补齐 `bm export`（JSON→CSV）与 `bm list` 的添加日期列

### 进阶挑战
- [ ] 把存储层改成 `Storage` 协议（`typing.Protocol`），提供 JSON 与 SQLite 两个实现
- [ ] 为 CLI 编写 pytest 集成测试：`typer.testing.CliRunner` 调用各命令

**提示**：挑战项分别对应 [typing 注解全表](../reference/language-concepts/05-typing-annotations.md)与[标准库导航](../reference/library-guides/01-standard-library.md)的知识点。

---

## 🔗 相关文档

- 📄 **[环境搭建](./01-environment-setup.md)** — 本项目的 uv 工作流来源
- 📄 **[生态库精选](../reference/library-guides/02-ecosystem-libs.md)** — typer/rich 完整能力速查
- 📄 **[FastAPI 速查](../reference/framework-essentials/01-fastapi-essentials.md)** — 相同哲学的 Web 框架进阶
