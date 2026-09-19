# Next proxy.ts 类型验证与安全版本边界

核对日期：2026-09-20。临时工程中，正文“注入请求头 + 地域路由”的完整 `proxy.ts` 以 Next 16.0.0、TypeScript 5.9.3、Node 24.21.0 编译，`tsc --project tsconfig.json` 通过。

该结果只验证 `NextRequest`、`NextResponse`、重定向和响应头的类型接线；不启动 Next 开发服务器，不验证 matcher 实际拦截，也不覆盖认证或平台地域头。

**安全限制：** Next 安装时报告 16.0.0 存在已知安全问题。官方公告将 16.0.x 的修复版本列为 16.0.7；因此该临时验证版本不得作为读者安装建议。新项目应使用对应主线的已修复版本并固定锁文件，见 [官方公告](https://nextjs.org/blog/CVE-2025-66478)。
