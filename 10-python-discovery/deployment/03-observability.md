# 可观测性 — structlog、Sentry 与 Prometheus

> **文档简介**: 让服务"可被看见"：structlog 结构化日志、请求 ID 全链路追踪、Sentry 错误上报、Prometheus 指标与健康检查
>
> **目标读者**: 准备运维生产服务的开发者
>
> **前置知识**: [生产级 FastAPI 应用](../projects/04-production-fastapi-app.md)、[容器化部署](./01-docker-deployment.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#structlog` `#Sentry` `#Prometheus` `#日志` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 三支柱分工

| 支柱 | 回答的问题 | 工具 |
|------|-----------|------|
| 日志 | 发生了什么，按请求追溯 | structlog |
| 指标 | 系统状态如何（QPS/延迟/错误率） | Prometheus |
| 错误追踪 | 这次报错的完整上下文与影响面 | Sentry |

---

## 1. structlog 结构化日志

```bash
uv add structlog
```

```python
# core/logging.py
import logging
import structlog

def setup_logging(debug: bool = False) -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,   # 合并请求级上下文（request_id）
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer() if not debug
            else structlog.dev.ConsoleRenderer(),      # 生产 JSON，开发彩色可读
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.DEBUG if debug else logging.INFO
        ),
    )

logger = structlog.get_logger()
```

```python
# 业务代码：键值对而非拼接字符串
logger.info("order_created", order_id=order.id,
            amount=str(order.amount), channel=order.channel)
```

**要点**：

- JSON 日志供采集系统（Loki/ELK）解析聚合；开发环境用 ConsoleRenderer 保持可读
- 禁止把密码、token 写进日志——记标识符，不记机密（见[安全实践](../advanced-topics/security/01-security-practices.md)）

## 2. 请求 ID 中间件：串起一次请求的所有日志

```python
import uuid
import structlog
from fastapi import Request

@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    structlog.contextvars.bind_contextvars(request_id=request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id     # 返给客户端，便于反馈排查
    structlog.contextvars.unbind_contextvars("request_id")
    return response
```

**要点**：日志里全带同一 `request_id`，一次请求的完整链路一条 `grep` 就能捞出来（中间件机制见[FastAPI 进阶](../frameworks/02-fastapi-advanced.md)）。

## 3. Sentry：错误自动上报

```bash
uv add "sentry-sdk[fastapi]"
```

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from core.config import settings

if settings.env == "production":
    sentry_sdk.init(
        dsn=settings.sentry_dsn,          # 密钥走环境变量，不硬编码
        environment=settings.env,
        traces_sample_rate=0.1,           # 10% 请求采样做性能追踪
        send_default_pii=False,           # 不采集个人敏感信息
        integrations=[FastApiIntegration()],
    )
```

**要点**：异常自动附带请求上下文与本地变量；采样率控制成本，全量上报只留给核心交易链路。

## 4. Prometheus 指标

```bash
uv add prometheus-fastapi-instrumentator
```

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
# 暴露 /metrics：请求计数、延迟直方图、状态码分布
```

Grafana 常用告警表达式：

```text
错误率:  rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])
P99 延迟: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

## 5. 健康检查

```python
@app.get("/health", include_in_schema=False)
async def health() -> dict[str, str]:
    # 可加数据库 ping；Docker HEALTHCHECK 与 K8s 探针都指向这里
    return {"status": "ok"}
```

## ✅ 最佳实践

先选一个失败旅程，确保能从请求标识找到相关日志、错误与耗时。指标适合观察分布和趋势，日志保留个案上下文，错误平台帮助聚合；任何工具都不会自动给出根因。

上报数据先脱敏，设置采样与保留期。告警描述用户影响及下一步排查，验证采集服务故障不会阻塞主业务或无限积压。

## ❓ 常见问题

**Q1: 多 worker 日志交错混乱？**
JSON 结构化 + request_id 天然解决交错——每行自带字段，采集端按字段聚合而非按行顺序。

**Q2: /metrics 要不要暴露公网？**
不要。仅内网/localhost 可达，或在网关层加认证，防止被爬取业务量情报。

---

## 🔗 相关文档

- 🚀 **[项目：生产级 FastAPI 应用](../projects/04-production-fastapi-app.md)** — 本篇是它的上线收尾
- 🚀 **[CI/CD 流水线](./02-ci-cd-pipelines.md)** — 部署之前的自动化门禁
- 🎓 **[安全实践](../advanced-topics/security/01-security-practices.md)** — 日志脱敏与 PII 防护
- 📄 **[FastAPI 进阶](../frameworks/02-fastapi-advanced.md)** — 中间件机制详解
- 🎓 **[性能剖析](../advanced-topics/performance/02-profiling-optimization.md)** — 指标异常后的下钻工具


<!-- acceptance-exercise -->
## 练习与验收：检查观测数据是否解释一次失败

给一个测试请求附请求标识，让依赖返回受控超时。预期用户得到约定的错误响应，结构化日志有请求标识与错误类别，延迟指标计入失败请求，错误平台能关联发布版本。验收检查日志不含 Authorization 或正文；停掉采集端后服务仍按自己的超时预算返回，不把监控故障扩大成业务故障。

以上是在个人或隔离测试环境中的练习，不是本轮已执行记录；实际运行范围见仓库文档质量报告。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
