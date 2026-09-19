# 前端与 Node.js 文档代码围栏复验（2026-09-19）

本记录只说明已经做过的检查，不把片段的语法通过写成框架项目已经构建或发布。

## 全仓语法解析

使用 TypeScript 5.9.3 的 `createSourceFile(...).parseDiagnostics`，从 `extract_blocks.py` 生成的规范清单中解析所有标为 `ts`、`tsx`、`typescript`、`js`、`jsx` 或 `javascript` 的围栏：

| 结果 | 围栏数 | 含义 |
| --- | ---: | --- |
| `PASS_SYNTAX` | 1,165 | 对应围栏语言的纯语法可解析 |
| `NOT_VERIFIED_ARKTS` | 1 | OpenHarmony 的 ArkTS 壳工程示意，需 Harmony 工具链 |

四个本轮重点模块共有 1,148 个 TS/JS 类围栏：Next.js 584 个、TanStack 194 个、React Native 134 个、Node.js 236 个。解析时严格服从围栏标签：没有把 `ts` 自动改成 TSX、没有为多个 JSX 节点补包装器、没有注入导入或虚构第三方类型声明。若文档的实际代码身份改变，应改正围栏标签；不能用解析器兜底掩盖问题。

语法解析不检查包版本、类型契约、React Hook 规则、请求行为或框架集成。唯一的 ArkTS 围栏位于 `04-multiplatform-apps/reference/language-concepts/05-harmonyos-rnoh-api.md`，是 `Index.ets` 的壳工程示意；在没有 OpenHarmony SDK 与 RNOH 工程的环境中保持未验证。

## 已实际运行的限定示例

运行环境为 Node.js 24.19.0、TypeScript 5.9.3、React 19.3.0、TanStack Query 5.103.1，以及独立依赖工作区中的 jsdom 与 Testing Library。通过的七项检查记录在 [final-web-examples.json](./final-web-examples.json)：

1. LRU 缓存的淘汰、更新与非法容量；
2. Query 的 `dehydrate` / JSON / `hydrate` 往返；
3. URL 页码的未知输入和范围拒绝；
4. `DataFetcher` 与页码函数在真实依赖下的严格 TypeScript 检查；
5. 旧请求即使忽略 abort 也不能覆盖新请求；
6. HTTP 失败进入错误状态；
7. 组件卸载后取消请求且忽略迟到结果。

Node.js 参考部分另有七个独立完整示例在 Node.js 24.19.0 下运行通过，结果见 [node-reference-examples.json](./node-reference-examples.json)。这些例子覆盖现代 JavaScript、核心 API、语义、类型转换、子进程、Buffer 和内置测试运行器。

## 未由本记录验证的内容

- Next.js 的完整 `next build`、服务端组件边界、真实路由和部署；
- TanStack Router、Table、Form 与 Start 的实际应用工程；
- React Native/Expo 的 iOS、Android 或 OpenHarmony 设备构建；
- Node.js 的真实数据库、集群、外部网络、进程编排和部署；
- 未列入上述运行清单的历史片段。

这些内容仍须各自提供真实最小工程、锁定依赖和适用平台中的构建或行为证据，才能计入完整示例验收。

## 复现

从仓库根目录，准备一个仓库外的 Node 依赖工作区，并安装 TypeScript 5.9.3。将 `TYPESCRIPT_PATH` 指向其中的 `node_modules/typescript`，然后运行：

    python shared-resources/tools/code-block-verify/extract_blocks.py . /tmp/manifest.jsonl
    node shared-resources/tools/code-block-verify/verify_tsjs_syntax.mjs /tmp/manifest.jsonl /tmp/tsjs-output
    node --test shared-resources/tools/code-block-verify/test_tsjs_syntax.mjs

限定 Web 运行检查需要 React、React DOM、TypeScript、TanStack Query、jsdom 和 Testing Library：

    node shared-resources/tools/document-quality/verify_final_web_examples.mjs /path/to/dependency-workspace

Node.js 参考示例可用指定解释器重跑：

    python shared-resources/tools/document-quality/verify_node_reference_examples.py --node node --report /tmp/node-reference-examples.json
