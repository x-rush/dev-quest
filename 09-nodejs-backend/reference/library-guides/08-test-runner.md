# node:test 测试运行器速查

> **文档简介**: Node 内置测试框架 `node:test` 的 API 字典——test/describe/it、assert/strict 断言、生命周期钩子、mock 计时器、子测试与命令行选项，示例在 Node 24 真实跑通

> **目标读者**: 不想引入 Jest/Vitest 依赖、快速给脚本与库写测试的开发者；以及需要理解 Vitest 底层运行模式的开发者

> **前置知识**: [内置模块导航表](./01-core-modules.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐ |
| **标签** | `#node:test` `#assert` `#mock` `#测试` |
| **更新日期** | `2026年9月` |

## 1. 定位

### 定义
`node:test` 是 Node 18+ 内置的测试框架（Node 24 下已稳定成熟），配 `node:assert/strict` 断言，零依赖覆盖单测全部基础能力。**与 Vitest 的分工**：本模块工程主线用 Vitest（快照/组件/UI 生态）；node:test 适合轻量库、脚本验证与"环境里没有依赖管理"的场景，两者心智模型几乎一致，可随时迁移。

## 2. test / describe / it

### 定义
两种组织风格：`test()` 平铺用例，或 `describe` + `it` 分组嵌套；两种可混用，子测试在结果树里呈层级展开（Node 24 实测）。

```ts
import { test, describe, it } from "node:test";
import assert from "node:assert/strict";

test("平铺用例", async (t) => {
  const result = await loadConfig();
  assert.equal(result.port, 3000);
});

describe("calc", () => {
  it("adds", () => { assert.equal(1 + 1, 2); });

  it("子测试：在用例内再分组", async (t) => {
    await t.test("inner-a", () => assert.ok(true));
    await t.test("inner-b", () => assert.ok(true));
  });
});
```

- 用例函数第一个参数是 **TestContext**（`t`），可继续 `t.test()` 建子测试、`t.mock` 建桩
- 异步用例直接 `async`，返回的 Promise 会被等待

## 3. 断言：node:assert 与 node:assert/strict

### 定义
`node:assert/strict` 把全部断言切换到严格模式（`equal` 即 `Object.is` 语义、`deepEqual` 即深度严格相等），测试里永远用 strict 入口。

```ts
import assert from "node:assert/strict";

assert.equal(actual, expected);        // Object.is 语义（strict 下）
assert.deepEqual(obj1, obj2);          // 深度严格相等（strict 下）
assert.notEqual(a, b);
assert.ok(value);                      // truthy
assert.throws(() => boom(), /err msg/);   // 抛错 + 消息正则
assert.throws(() => boom(), { code: "ERR_X" });  // 按错误属性匹配
await assert.rejects(async () => boomAsync(), /fail/);  // 异步拒绝
assert.match(str, /^abc/);             // 字符串正则
assert.fail("不应到达这里");
```

### 陷阱
- ❌ `import assert from "node:assert"`（非 strict）做测试——`equal` 是 `==` 语义，`'1' == 1` 通过，假阴性温床
- ✅ 一律 `node:assert/strict`；生产代码里的内部不变量校验才用普通 `node:assert`
- `assert.deepEqual` 在 strict 下要求**原型一致**：`Object.create(null)` 与 `{}` 不相等

## 4. 钩子

### 定义
`before/after/beforeEach/afterEach` 在 describe 内声明，作用于当前组及其子组；顶层声明则作用于整个文件（Node 24 实测按序触发）。

```ts
import { describe, it, before, beforeEach, after, afterEach } from "node:test";

describe("user repo", () => {
  let db: TestDb;

  before(async () => { db = await startTestDb(); });     // 全组一次
  beforeEach(() => db.seed());                            // 每个用例前
  afterEach(() => db.truncate());                         // 每个用例后
  after(async () => { await db.close(); });               // 全组结束

  it("queries", async () => { /* ... */ });
});
```

- `before` 拉起外部资源（测试容器、临时目录），`after` 释放；`beforeEach` 保证用例间隔离
- 钩子内的异常会让所属组内用例整体 fail，天然防"前置失败还继续跑"

## 5. Mock 计时器

### 定义
`t.mock.timers.enable({ apis: [...] })` 把 `setTimeout` 等 API 替换成可手动推进的假时钟——测试超时/重试逻辑不必真等（Node 20.4+，实测通过）。

```ts
it("重试在 10s 后触发", (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });   // 也支持 setInterval/setImmediate/Date

  let retried = false;
  setTimeout(() => { retried = true; }, 10_000);

  t.mock.timers.tick(10_000);      // 时间瞬间前进
  assert.equal(retried, true);
});
```

- 配套方法：`t.mock.timers.tick(ms)` 推进、`setInterval` 场景 `tickAll()`、恢复真实时间用 `t.mock.timers.reset()`（用例结束自动恢复）
- `t.mock` 上还有 `t.mock.method()`（记录调用）、`t.mock.fn()`（替换实现）——模拟 spies 的内置版

## 6. 命令行

### 定义
`node --test` 按约定模式发现并运行测试文件；常用旗标控制过滤与观察模式。

```bash
node --test                              # 默认发现：**/*.test.{js,mjs,cjs}、test-*.js、test/ 目录等
node --test test/calc.test.mjs           # 显式指定文件
node --test --test-name-pattern "adds"   # 按用例名过滤（实测只跑匹配的）
node --test --watch                      # 文件变化自动重跑
node --test --test-reporter=tap          # 机器可读输出（dot/spec/tap/junit）
node --test --experimental-test-coverage # 覆盖率
```

- **运行约定**：推荐在项目根目录直接 `node --test`（按默认模式发现），或显式给文件路径；把目录当位置参数传入的兼容性一般（实测有把目录当单目标运行而整体报错的情况），默认发现最稳
- 测试文件即普通 ESM 脚本：`node sample.test.mjs` 也能跑（无 TAP 汇总），说明它与运行时零耦合

## 🔗 相关文档

- 📄 **[全局对象速查](../language-concepts/09-globals-reference.md)** — `AbortSignal.timeout` 在集成测试中的超时用法
- 📄 **[node:util 工具集速查](./06-util.md)** — mock CLI 参数的 parseArgs 配合
- 📄 **[Node 一行式速查](../quick-references/01-node-cheatsheet.md)** — 测试相关 CLI 命令速查
- 🌐 **[Node.js 官方文档: test runner](https://nodejs.org/docs/latest/api/test.html)** — mock/报告器权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
