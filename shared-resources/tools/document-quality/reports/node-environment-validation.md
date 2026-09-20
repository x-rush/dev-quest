# Node 环境 ESM 最小程序验证

本报告记录 [Node.js 环境搭建](../../../../09-nodejs-backend/basics/01-environment-setup.md) 中标记为 `verify:node-environment-esm` 的完整 JavaScript 正文。运行器从 Markdown 原样提取代码，在 `node:24-bookworm-slim` 中作为 ESM 标准输入执行；程序断言 Node 主版本为 24，并输出实际版本。

它只证明这个最小 ESM 模块能在该容器的 Node 24 中执行。它不证明读者机器的 Node、fnm/nvm 自动切换、pnpm、Corepack、TypeScript 类型剥离、依赖安装、HTTP 服务或项目脚本已通过。

在仓库根目录复现：

```bash
python shared-resources/tools/document-quality/verify_node_environment.py --report shared-resources/tools/document-quality/reports/node-environment-validation.json
```
