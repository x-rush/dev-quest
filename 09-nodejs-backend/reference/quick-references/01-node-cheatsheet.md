# Node 一行式速查

> **文档简介**: Node CLI 命令、调试入口、npm/pnpm 脚本与环境变量的一行式速查表

> **目标读者**: 需要快速回忆命令的日常开发场景

> **前置知识**: [环境搭建](../../basics/01-environment-setup.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐ |
| **标签** | `#CLI` `#调试` `#npm-scripts` `#速查` |
| **更新日期** | `2026年9月` |

## 1. 运行与脚本

```bash
node server.js                       # 运行脚本
node                                 # 进入 REPL
node --watch server.js               # 文件变更自动重启（内置热重载）
node --watch-path=src server.js      # 限定监听目录
node --env-file=.env server.js       # 加载 .env（内置，替代 dotenv）
node --experimental-strip-types s.ts # TS 类型剥离（22.6+，22.18+ 默认）
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
node --trace-uncaught                # 未捕获异常的完整堆栈
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
node --test                          # 运行 test/ 目录下 *.test.js
node --test test/a.test.ts           # 指定文件（TS 需类型剥离）
node --test --test-name-pattern="登录" # 按名过滤用例
node --test --watch                  # 测试热重载
node --test --experimental-test-coverage  # 覆盖率
```

## 4. npm / pnpm 常用

```bash
pnpm install                         # 安装（npm install 同义）
pnpm add express                     # 添加生产依赖
pnpm add -D typescript               # 添加开发依赖
pnpm remove express
pnpm update --latest                 # 升级全部依赖
pnpm outdated                        # 查看过期依赖
pnpm why express                     # 解释依赖为什么被装上
pnpm ls --depth 0                    # 列出顶层依赖
pnpm exec prisma migrate dev         # 运行 node_modules 内二进制（npx 等价）
pnpm dlx degit user/repo             # 临时执行远程包（npx 等价）
pnpm run dev                         # 运行 scripts.dev（pnpm dev 可简写）
pnpm pkg set type=module             # 免编辑器改 package.json
pnpm store prune                     # 清理全局存储
corepack enable pnpm                 # 启用包管理器版本管理
```

package.json 常用字段一行式：

```bash
pnpm pkg set scripts.dev="node --watch src/server.ts"
pnpm pkg set engines.node=">=22"
pnpm pkg set type=module
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
kill -USR1 <pid>                                 # 对运行中进程开启调试端口
lsof -i :3000                                    # 查端口占用
ulimit -n 65535                                  # 文件句柄上限（流多时调整）
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

## 🔗 相关文档

- 📄 **[常见故障排除](./02-troubleshooting.md)** — 报错后按症状定位
- 📄 **[环境搭建](../../basics/01-environment-setup.md)** — 工具链安装配置
- 📄 **[内置模块导航表](../library-guides/01-core-modules.md)** — NODE_DEBUG 可用的模块名
