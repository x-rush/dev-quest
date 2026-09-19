# Rust / Web / Mobile P1 第九轮正文提取验证

本报告只覆盖选择时 `primary state=not_verified` 的六个 P1 基础页面。每个案例在仓库内从精确锚点开始提取 Markdown 正文，并在提取区域中断言指定文本存在；JSON 记录源文件 SHA-256、锚点与断言文本。

| Case | Source | Extracted-body assertion | Status |
| --- | --- | --- | --- |
| `rust-ownership-borrow-body` | `11-rust-cross-platform/basics/02-ownership-borrowing.md` | `let r3 = &mut s;` after borrowing-example heading | PASS |
| `next-app-router-body` | `02-nextjs-frontend/basics/02-first-nextjs-app.md` | `AboutPage` export after route-file anchor | PASS |
| `tanstack-headless-v8-body` | `03-tanstack-stack/basics/02-headless-philosophy.md` | `useReactTable` after the v8 adapter anchor | PASS |
| `react-native-fast-refresh-boundary-body` | `04-multiplatform-apps/basics/02-first-app.md` | reload boundary after Fast Refresh wording | PASS |
| `kotlin-preview-boundary-body` | `05-kotlin-compose/basics/02-first-compose-app.md` | compile-boundary wording after `@Preview` anchor | PASS |
| `swift-preview-platform-boundary-body` | `06-swift-swiftui/basics/02-first-swiftui-app.md` | device-validation boundary after macOS guard | PASS |

## 限定范围

- 这项检查只证明所列 Markdown 正文在本次源文件哈希下可被直接提取且包含所列断言；不编译或运行 Rust、Next.js、TanStack、React Native、Compose 或 SwiftUI。
- 结果不能外推为整页正确性、框架构建、浏览器或设备行为，以及外部服务行为。
