# Java / Node.js / Python 异常正文提取验证

从三篇 P1 基础页面各提取一个完整代码围栏并实际运行。验证仅覆盖命名围栏，未覆盖框架、网络、进程级崩溃策略或整篇文档。

| Case | Document | Result |
| --- | --- | --- |
| `java-try-with-resources-suppressed` | `08-java-revisited/basics/06-exceptions.md` | PASS |
| `node-error-cause` | `09-nodejs-backend/basics/06-error-handling.md` | PASS |
| `python-exception-chain-context-manager` | `10-python-discovery/basics/06-exceptions.md` | PASS |

JSON 记录提取源码 SHA-256、实际命令、stdout/stderr、退出码和 `passed` 字段。
