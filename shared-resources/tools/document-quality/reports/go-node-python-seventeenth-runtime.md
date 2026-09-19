# Go / Node.js / Python 第十七轮正文提取运行验证

Three named, complete P1 core/standard-library Markdown programs are extracted byte-for-byte from marked fences. PASS means only that each listed command has the specified stdout and no stderr.

| Case | Source | Runtime | Result |
| --- | --- | --- | --- |
| `go-control-flow-labelled-range` | `01-go-backend/reference/language-concepts/05-go-control-flow.md` | `golang:1.27` | PASS |
| `node-stream-decoder-pipeline` | `09-nodejs-backend/reference/language-concepts/04-streams-api.md` | `node:24-bookworm-slim` | PASS |
| `python-script-entry-contract` | `10-python-discovery/basics/02-first-script.md` | `python:3.14-alpine` | PASS |

## 边界

验证仅覆盖表中原样提取的完整程序与精确标准输出：Go 的 continue、switch、带标签 break 和 rune 字节索引；Node 的跨 chunk UTF-8 解码、行数和 pipeline 完成；Python 的入口参数和成功退出码。它不覆盖整篇文档、其他围栏、错误分支、网络、数据库、框架、部署、性能或平台行为。JSON 同伴报告记录来源与提取代码 SHA-256、镜像工具链、完整命令、标准输出/错误和退出码。
