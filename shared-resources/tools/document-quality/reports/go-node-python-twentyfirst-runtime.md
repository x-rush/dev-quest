# Go / Node.js / Python 第二十一轮正文提取运行验证

Three named complete P1 core/standard-library Markdown programs are extracted byte-for-byte from marked fences. PASS covers only each listed command and assertion.

| Case | Source | Runtime | Result |
| --- | --- | --- | --- |
| `go-io-bufio-read-contract` | `01-go-backend/reference/library-guides/10-io-bufio.md` | `golang:1.27` | PASS |
| `node-test-async-rejection` | `09-nodejs-backend/reference/library-guides/08-test-runner.md` | `node:24-bookworm-slim` | PASS |
| `python-stdlib-time-json-contract` | `10-python-discovery/reference/library-guides/01-standard-library.md` | `python:3.14-alpine` | PASS |

## 边界

验证仅覆盖表中从 Markdown 原样提取的完整程序：Go 的 final-bytes、Scanner 默认/配置 token 上限；Node 测试运行器对异步拒绝的等待；Python UTC 字符串 JSON 往返及 naive/aware 比较边界。它不覆盖整篇文档、其他围栏、网络、数据库、框架、部署、性能或平台行为。Node 的 TAP 时长由运行器生成，因此只断言通过/失败字段；JSON 同伴报告保留来源与代码 SHA-256、镜像工具链、完整命令、标准输出/错误和退出码。
