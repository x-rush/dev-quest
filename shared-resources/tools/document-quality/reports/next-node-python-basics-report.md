# Next、Node 与 Python P1 基础页限定验证

该报告只覆盖以下从 Markdown 正文直接提取的具名程序，不代表整篇页面、Next.js 应用、外部网络或第三方依赖已经验证。

| 页面 | 程序 | 行 | 结果 |
| --- | --- | ---: | --- |
| `dev-quest/02-nextjs-frontend/basics/03-typescript-integration.md` | `next-typescript-boundary` | 871 | PASS |
| `dev-quest/09-nodejs-backend/basics/03-modules-esm.md` | `node-esm-binding` | 207 | PASS |
| `dev-quest/09-nodejs-backend/basics/02-first-server.md` | `node-first-server-routing` | 112 | PASS |
| `dev-quest/09-nodejs-backend/reference/library-guides/07-process-lifecycle.md` | `node-lifecycle-idempotent-shutdown` | 118 | PASS |
| `dev-quest/09-nodejs-backend/basics/07-streams-workers.md` | `node-stream-worker-boundaries` | 126 | PASS |
| `dev-quest/09-nodejs-backend/basics/05-http-routing.md` | `node-request-body-boundaries` | 198 | PASS |
| `dev-quest/09-nodejs-backend/basics/06-error-handling.md` | `node-error-cause-chain` | 94 | PASS |
| `dev-quest/10-python-discovery/reference/quick-references/01-python-cheatsheet.md` | `python-cheatsheet-boundaries` | 124 | PASS |
| `dev-quest/10-python-discovery/basics/03-variables-types.md` | `python-bindings-formatting` | 229 | PASS |

执行方式：代码在禁网、只读文件系统的 Docker 容器中执行。Next/TypeScript 示例使用 Node 24 的 TypeScript 类型擦除执行；它验证该示例可执行，不替代完整 `tsc` 项目检查。完整命令、哈希和标准输出见同目录 JSON 报告。
