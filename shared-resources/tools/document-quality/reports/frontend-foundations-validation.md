# 前端语言与 Web 标准能力验证

核验日期：2026-09-19。实测运行时：Node v24.19.0，Windows x64。

本文对应三份基础参考的八个具名完整程序；既有片段、真实浏览器 UI、CORS/Cookie、存储权限、SSR 与 TanStack 完整工程构建不在这八项执行证据之内。

## 实质修订与证据范围

| 来源 | 修订重点 | 直接运行的程序 |
|---|---|---|
| [JavaScript 核心语义](../../../../02-nextjs-frontend/reference/language-concepts/09-js-core-semantics.md) | 修正渲染与任务的关系、默认参数对象生命周期、对象展开与可迭代协议、Node 调度边界 | object-lifetimes、bindings、iteration |
| [Web 平台 API](../../../../02-nextjs-frontend/reference/language-concepts/10-web-platform-apis.md) | 区分语言内置与宿主API、取消错误处理、存储读写失败、响应结构校验、克隆与转移 | url-form、response-contract、clone |
| [TanStack 所需语言与 Web 能力](../../../../03-tanstack-stack/reference/library-guides/03-language-web-foundations.md) | 区分 ECMAScript、TS 类型、Web API、React、TanStack；建立输入与不可变更新契约 | search-input、immutable-data |

结果：**8 / 8 通过**。每个程序从原 Markdown 的 `foundation-case` 标记直接抽取，以 `node --input-type=module` 独立执行；未补函数、import、DOM 或框架替身。每项要求退出码为 0、stderr 为空、stdout 与显式期望逐字一致。错误和边界行为在示例内作为可观察结果检验。

结构错误响应测试使用真实 Response 对象，不请求网络；这验证状态、JSON/字段和正文单次消费的契约，不证明真实 HTTP 服务或浏览器行为。存储、BroadcastChannel 与页面取消另列为页面验收任务，未据 Node 输出宣称浏览器验收通过。

## 复现

从仓库根目录使用 Node 24：

```sh
node shared-resources/tools/document-quality/verify_frontend_foundations.mjs
```

可传一个报告路径作为第一个参数。默认更新 [frontend-foundations.json](frontend-foundations.json)，记录运行时、规范化为 LF 的文档 SHA-256、代码 SHA-256、源行号、原代码、预期输出和实际输出。标记缺失、重复、格式损坏或输出改变都会失败；新增程序必须同时加入显式期望。

验证器：[verify_frontend_foundations.mjs](../verify_frontend_foundations.mjs)。这份证据应与对应原文一起更新，不能在文档代码变化后继续引用旧输出作为最新结论。

## 运行时选择与失败诊断

先检查 `node --version`，必须使用本页指定的 Node 24 或更高版本，并具备原生 FormData、Response.json、structuredClone。验证器先检查这些条件；不满足时返回退出码 2 和 `ENVIRONMENT_NOT_SUPPORTED`，不执行示例，也不覆盖既有证据。

本机 PATH 曾优先命中微信开发者工具内置的 Node v16.13.1，导致 url-form、response-contract、clone 分别因缺少 FormData、Response、structuredClone 而失败。这是执行环境不满足文档前提；使用显式 Node v24.19.0 路径复跑后仍为 8 / 8 通过。Windows 可用 `Get-Command node -All` 检查同名可执行文件，随后以绝对路径执行验证器。不要为迎合旧工具链偷偷注入 polyfill，也不要降低原文期望来掩盖环境问题。
