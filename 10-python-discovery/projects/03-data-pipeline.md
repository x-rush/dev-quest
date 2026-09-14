# 进阶项目 — 数据处理管道

> **文档简介**: 搭建一条"读取 → 校验 → 转换 → 汇总 → 定时执行"的数据管道，练习 Pydantic 数据校验、match 结构化分支与 APScheduler 定时任务
>
> **目标读者**: 想用 Python 做数据清洗与自动化任务的开发者
>
> **前置知识**: [高级特性](../basics/07-advanced-features.md)、[Pydantic 模型](../frameworks/01-fastapi-basics.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#数据处理` `#match` `#定时任务` `#Pydantic` |
| **更新日期** | `2026年9月` |

## 🎯 项目目标

- 解析 CSV 订单文件，逐行 Pydantic 校验，坏数据跳过不崩
- 用 `match` 语句按渠道归一化分类
- 汇总输出 JSON 报表
- APScheduler 每日定时执行

## 1. 安装

```bash
uv init --app order-pipeline && cd order-pipeline
uv add pydantic apscheduler
```

## 2. 数据模型与校验

```python
# models.py
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

class Order(BaseModel):
    order_id: str
    amount: Decimal = Field(gt=0)     # 金额必须为正
    channel: str
    currency: str = "CNY"

    @field_validator("channel")
    @classmethod
    def normalize_channel(cls, v: str) -> str:
        return v.strip().lower()
```

**要点**：金额用 `Decimal` 而非 `float`，避免浮点误差污染财务汇总（内置类型见[数据结构字典](../reference/language-concepts/03-data-structures.md)）。

## 3. 转换：match 语句

```python
# transform.py
from models import Order

def classify(order: Order) -> str:
    """match 处理结构化分支：对属性解构 + 条件守卫，比 if/elif 链清晰。"""
    match order:
        case Order(amount=a, channel="web") if a > 1000:
            return "web-大额"
        case Order(channel="web"):
            return "web"
        case Order(channel="app"):
            return "app"
        case Order(channel="分销商", currency="CNY"):
            return "cn-distributor"
        case _:
            return "other"
```

**要点**：`match` 是 3.10+ 的结构化模式匹配；类模式 `Order(channel="web")` 同时做类型检查与字段解构。

## 4. 管道主体

```python
# pipeline.py
import csv
import json
import logging
from collections import Counter
from decimal import Decimal
from pathlib import Path
from models import Order
from transform import classify

logger = logging.getLogger(__name__)

def run(input_dir: Path, output: Path) -> Path:
    orders: list[Order] = []
    skipped = 0
    for file in input_dir.glob("*.csv"):
        with file.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    orders.append(Order(**row))      # 校验失败进 except，不让整条管道崩
                except ValueError as e:
                    skipped += 1
                    logger.warning("跳过非法行 %s: %s", row, e)

    by_channel = Counter(classify(o) for o in orders)
    report = {
        "total": len(orders),
        "skipped": skipped,
        "total_amount": str(sum((o.amount for o in orders), start=Decimal("0"))),
        "classify": dict(by_channel),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    return output
```

**要点**：

- 校验交给 Pydantic，坏数据记录后跳过——管道健壮性的关键
- 汇总用 `collections.Counter`（详见[标准库字典](../reference/library-guides/01-standard-library.md)）

## 5. 定时执行：APScheduler

```python
# scheduler.py
from apscheduler.schedulers.blocking import BlockingScheduler
from pathlib import Path
from pipeline import run

sched = BlockingScheduler()

@sched.scheduled_job("cron", hour=2, minute=30)   # 每天 02:30
def nightly_report() -> None:
    out = run(Path("data/in"), Path("data/out/report.json"))
    print(f"报表已生成: {out}")

if __name__ == "__main__":
    sched.start()      # 常驻进程；服务器场景配合 systemd 托管
```

```bash
uv run python scheduler.py
```

**要点**：cron 触发器支持 `hour`/`minute` 等字段，也有 `interval` 间隔触发；容器化部署方案见[容器化](../deployment/01-docker-deployment.md)。

## 6. 验证

```bash
mkdir -p data/in
printf 'order_id,amount,channel\nA001,99.9,Web\nA002,-5,app\n' > data/in/o.csv
uv run python -c "from pathlib import Path; from pipeline import run; print(run(Path('data/in'), Path('data/out/report.json')))"
cat data/out/report.json
```

预期：`total=1`（金额 -5 的行被校验跳过）、`skipped=1`、`classify={"web": 1}`。

## 7. 扩展练习

- 增量处理：用清单文件记录已处理文件，避免重复入表
- 失败隔离：单个文件解析失败不影响其他文件，末尾汇总错误报告
- API 化：把 `run()` 包成 FastAPI 端点，支持手动触发并返回报表

---

## 🔗 相关文档

- 📄 **[高级特性](../basics/07-advanced-features.md)** — match 语句与生成器的语言基础
- 📖 **[标准库字典](../reference/library-guides/01-standard-library.md)** — csv/json/pathlib/collections 详解
- 📄 **[FastAPI 入门](../frameworks/01-fastapi-basics.md)** — Pydantic 校验的框架用法
- 🚀 **[项目：生产级 FastAPI 应用](./04-production-fastapi-app.md)** — 终极关：工程化整合
- 🧪 **[单元测试](../testing/01-unit-testing.md)** — 给 classify/run 写参数化测试
