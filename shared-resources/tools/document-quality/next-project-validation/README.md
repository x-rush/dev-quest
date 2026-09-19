# Next.js 首项目片段验证

此目录保存 `../verify_next_first_project.mjs` 的验证依赖。需 Node.js 24+、pnpm 11；`package.json` 固定直接依赖，`pnpm-lock.yaml` 固定依赖树。它们只用于文档片段验证，不代表学习者 Next.js 工程的依赖配置。

从仓库根运行：

```bash
pnpm --dir shared-resources/tools/document-quality/next-project-validation install --frozen-lockfile --ignore-scripts
node shared-resources/tools/document-quality/verify_next_first_project.mjs
```

验证器直接读取仓库 `02-nextjs-frontend/basics/08-first-project.md` 的第一个 TSX 块，在内存转译并执行 React + JSDOM 验证。没有依赖仓库外的源文件或 `verification-lab`。报告输出到 `../reports/next-first-project-2026-09-19.json`，记录片段 SHA256、运行时和验证项目。

验证边界：覆盖首次读取门禁、空列表、正常保存、空白拒绝、重挂载后读取、损坏数据保护和写入异常时保留输入及列表。不执行 TypeScript 语义检查、Next.js 构建、hydration 或真实浏览器测试；DOM 通过不能替代这些验证。
