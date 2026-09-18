# Node 一行式速查

> **文档简介**: Node CLI 命令、调试入口、npm/pnpm 脚本与环境变量的一行式速查表

> **目标读者**: 需要快速回忆命令的日常开发场景

> **前置知识**: [环境搭建](../../basics/01-environment-setup.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐ |
| **标签** | `#CLI` `#调试` `#npm-scripts` `#速查` |
| **更新日期** | `2026年9月` |

</details>

## 1. 运行与脚本

```bash
node server.js                       # 运行脚本
node                                 # 进入 REPL
node --watch server.js               # 文件变更后重启进程，内存状态会重建
node --watch-path=src server.js      # 限定监听目录（平台支持有限，使用前检查当前 Node 文档）
node --env-file=.env server.js       # 加载 .env（内置，替代 dotenv）
node server.ts                       # 直接运行 TS（本模块使用 Node 24 默认类型剥离；不执行类型检查）
node -e "console.log(process.version)"  # 执行一行代码
node --input-type=module -e "..."    # -e 按 ESM 解析
node --max-old-space-size=4096 s.js  # 堆内存上限 4GB（MB 单位）
```

## 2. 调试

```bash
node --inspect server.js             # 开启调试协议（默认 9229）
node --inspect-brk server.js         # 首行暂停等待调试器
```

- VS Code：`.vscode/launch.json` 用 `type: "node"` 直接 F5，无需手动 --inspect
- Chrome DevTools：`chrome://inspect` 连接 9229 端口

```bash
node --prof server.js                # V8 采样分析 → node --prof-process isolate*.log
node --cpu-prof server.js            # 生成 .cpuprofile（DevTools 可导入）
node --heap-prof server.js           # 堆采样
node --trace-warnings server.js      # 显示警告堆栈
node --trace-uncaught server.js      # 未捕获异常的完整堆栈
```

代码内一行式：

```js
console.time("db"); /* ... */ console.timeEnd("db");   // 计时
console.table(rows);                                    // 表格化输出
console.dir(obj, { depth: null });                      // 完整深度打印
process.memoryUsage().heapUsed / 1024 ** 2;             // 堆用量 MB
performance.now();                                      // 高精度时间
```

## 3. 测试（node:test）

```bash
node --test                          # 按 Node 发现规则寻找测试，或显式传文件路径
node --test test/a.test.ts           # 指定文件（TS 需类型剥离）
node --test --test-name-pattern="登录" # 按名过滤用例
node --test --watch                  # 测试热重载
node --test --experimental-test-coverage  # 覆盖率
```

## 4. npm / pnpm 常用

```bash
pnpm install                         # 安装（npm install 同义）
pnpm add hono                        # 添加生产依赖
pnpm add -D typescript               # 添加开发依赖
pnpm remove hono
pnpm update --latest                 # 可跨主版本更新；在独立变更中阅读迁移说明并验证
pnpm outdated                        # 查看过期依赖
pnpm why hono                        # 解释依赖为什么被装上
pnpm ls --depth 0                    # 列出顶层依赖
pnpm exec prisma migrate dev         # 运行 node_modules 内二进制（npx 等价）
pnpm dlx degit user/repo             # 临时执行远程包（npx 等价）
pnpm run dev                         # 运行 scripts.dev（pnpm dev 可简写）
npm pkg set type=module             # 免编辑器改 package.json
pnpm store prune                     # 清理全局存储
corepack enable pnpm                 # 启用包管理器版本管理
```

package.json 常用字段一行式：

```bash
npm pkg set scripts.dev="node --watch src/server.ts"
npm pkg set engines.node=">=24"
npm pkg set type=module
```

## 5. 环境变量

```bash
PORT=3000 node server.js                 # 单变量（Unix）
NODE_ENV=production LOG_LEVEL=warn node server.js
node --env-file=.env --env-file-if-exists=.env.local server.js
export NODE_OPTIONS="--max-old-space-size=2048"   # 传给所有 node 进程的参数
node -p "process.env.PATH"               # 查看变量
```

## 6. 诊断与进程信息

```bash
node -p "process.version"                        # 版本
node -p "JSON.stringify(process.versions)"       # 全家桶版本（v8/openssl…）
node -p "process.execPath"                       # node 二进制路径
kill -USR1 "${TARGET_PID:?先设置目标Node进程的PID}"                                 # 对运行中进程开启调试端口
lsof -i :3000                                    # 查端口占用
ulimit -n                                        # Unix：先查看当前文件句柄限制，结合泄漏排查再调整
NODE_DEBUG=http,net node server.js               # 内置模块 debug 日志
```

## 7. 一分钟健康检查清单

```bash
node -v                          # 版本符合预期？
pnpm ls --depth 0                # 依赖干净？
node --test                      # 测试绿？
node --check server.js           # 语法检查（不执行）
```

---

<!-- full-library-explanation -->
## 一行命令先确定它影响哪一层

`node --check` 只检查语法，不会执行模块、连接数据库或检查 TypeScript 类型；`node --test` 只执行被发现或显式指定的测试。两条都成功，仍不能证明服务配置完整。建议按“语法或类型 → 单元测试 → 启动 → 一条真实请求”的顺序检查，并分别保存失败信息。

包管理命令也有不同范围：install 按清单与锁文件解析依赖，update 修改依赖版本，dlx 下载并执行临时包。CI 应使用已固定的包管理器与冻结锁文件安装；不要为消除安装错误先批量升级主版本。调试端口能控制进程，只绑定可信接口，远程排障通过受控隧道访问。

**练习**：写一个语法正确但启动就抛错的脚本，对比 --check 与直接运行的退出码；再用 process.execPath 确认实际执行的是哪份 Node。Windows PowerShell 设置当前进程环境变量使用 `$env:PORT = '3000'`，Unix 的 `PORT=3000 node ...` 不能原样粘贴到 PowerShell。

## 🔗 相关文档

- 📄 **[常见故障排除](./02-troubleshooting.md)** — 报错后按症状定位
- 📄 **[环境搭建](../../basics/01-environment-setup.md)** — 工具链安装配置
- 📄 **[内置模块导航表](../library-guides/01-core-modules.md)** — NODE_DEBUG 可用的模块名


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
