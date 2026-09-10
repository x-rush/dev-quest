# 端到端测试 — Maestro 与 Detox

> **文档简介**: 用 E2E 测试守护真实设备上的完整用户旅程：以 Maestro 为主线（YAML 流程、免写代码、CI 友好），对比 Detox 给出选型依据
>
> **目标读者**: 已建立单测/组件测试体系、需要自动化回归核心流程的开发者
>
> **前置知识**: 已完成 [单元测试](./01-unit-testing.md) 与 [组件测试](./02-component-testing.md)；本地能跑起 debug 构建

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 操作指南（testing） |
| **难度** | ⭐⭐ |
| **标签** | `#Maestro` `#Detox` `#E2E` `#CI` |
| **更新日期** | 2026年9月 |

## 🎯 学习目标

- ✅ 安装 Maestro 并编写第一个 YAML 流程
- ✅ 覆盖"启动 → 输入 → 核心操作 → 断言"的完整旅程
- ✅ 在 CI 中跑 E2E 冒烟测试
- ✅ 能根据团队情况在 Maestro 与 Detox 间做选型

## 🧭 选型：Maestro vs Detox

| 维度 | Maestro | Detox |
|------|---------|-------|
| 编写方式 | YAML 声明式，无需写测试代码 | JS/TS 测试代码（Jest 集成） |
| 同步机制 | 基于 UI 自动化层，偶发不稳定 | **灰盒同步**，等 JS 空闲，最稳定 |
| 上手成本 | 极低，装 CLI 即用 | 需配置构建变体与 Xcode/Gradle |
| 执行速度 | 较慢（截图/坐标驱动） | 快（进程内通信） |
| 适用场景 | 核心流程冒烟、跨团队共建 | 复杂交互的深度回归 |

**结论**：个人项目与中小团队从 **Maestro** 起步；大型 RN 项目且重度依赖复杂手势/并发场景再引入 Detox。

## 🛠️ Maestro 快速上手

```bash
# 安装（macOS/Linux）
curl -Ls "https://get.maestro.mobile.dev" | bash

# 启动模拟器并安装 debug 构建（Expo 开发构建或 preview 包）
# 然后运行流程
maestro test .maestro/todo.yaml
```

### 第一个流程：待办旅程

```yaml
# .maestro/todo.yaml —— 声明式描述用户旅程（对应 projects/01）
appId: com.example.todoapp          # app.json 中 package/bundleIdentifier
---
- launchApp                          # 启动并等待首帧
- assertVisible: "待办清单"           # 首屏断言

# 添加一条待办
- tapOn: "今天要做点什么？"            # 点输入框
- inputText: "写 E2E 测试"
- tapOn: "添加"
- assertVisible: "写 E2E 测试"        # 新增项出现在列表

# 切换完成态
- tapOn: "写 E2E 测试"
- assertVisible: "✓ 写 E2E 测试"

# 删除
- tapOn: "删除"
- assertNotVisible: "写 E2E 测试"     # queryBy* 语义的 E2E 版
```

### 进阶：权限弹窗、网络等待与子流程

```yaml
# .maestro/weather.yaml —— 含权限与网络的旅程（对应 projects/02）
appId: com.example.todoapp
---
- launchApp
# 定位权限系统弹窗：按平台实际按钮文案点按
- runFlow:
    when:
      visible: "仅在使用中允许"
    commands:
      - tapOn: "仅在使用中允许"
# 等待天气数据渲染：正则匹配温度格式，容忍加载耗时
- assertVisible:
    text: ".*°C"
    regex: true

# 子流程复用：把公共步骤抽成 partial 供多条流程引用
- runFlow:
    file: ./partials/login.yaml
# 截图留档（CI 产物，排查失败用）
- takeScreenshot: weather-loaded
```

```bash
# 在所有已连接设备上并行跑（三端适配验证时好用）
maestro test -e APP_ID=com.example.todoapp .maestro/
```

## 🤖 CI 集成

```yaml
# .github/workflows/e2e.yml 精简示例
jobs:
  e2e:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npx expo prebuild --platform android   # 生成原生工程
      - run: cd android && ./gradlew assembleDebug  # 打 debug 包
      - run: |
          curl -Ls "https://get.maestro.mobile.dev" | bash
          maestro test .maestro/todo.yaml
```

**策略建议**：CI 只跑 1-3 条关键冒烟流程（登录/下单/支付），完整回归放本地或夜间任务——E2E 慢且脆，数量要克制。

## ✅ 最佳实践

- ✅ **E2E 只测"核心旅程"**，分支细节交给组件测试，金字塔不能倒置
- ✅ **断言文案要稳定**：给关键节点设计不易改动的锚文本，或加 `testID` 兜底
- ✅ **失败自动截图**（`takeScreenshot`），CI 上没有真机屏幕可看
- ❌ **不要用 E2E 测视觉样式**，截图 diff 维护成本极高
- ❌ **不要在 E2E 里依赖真实后端数据**，用测试环境/stub 服务，避免数据漂移误报

## ❓ 常见问题

**Q1: Dev Client 构建能跑 Maestro 吗？**
A: 能，Maestro 面向任何已安装的 app；debug 构建记得先启动 Metro 或直接测 preview 包。

**Q2: 鸿蒙端能做 E2E 吗？**
A: RNOH 应用跑在鸿蒙设备上可用 ArkUI 测试框架/hdc 自动化，生态独立于 Maestro/Detox，见 [RNOH 字典](../reference/language-concepts/05-harmonyos-rnoh-api.md)。

**Q3: 断言偶发失败（flaky）怎么治？**
A: 三板斧：显式等待替代固定 sleep、稳定测试数据、CI 层失败重跑。持续 flaky 的流程说明 UI 有真实时序问题，优先修产品。

---

## 🔗 相关文档

- 📖 [CLI 命令与调试速查表](../reference/quick-references/01-cli-and-debug-cheatsheet.md) — 构建/安装命令全集
- 📖 [故障排除](../reference/quick-references/02-troubleshooting.md) — 白屏等首帧问题排查
- 📄 [待办应用实战](../projects/01-todo-app.md) — todo.yaml 所测旅程的实现
- 📄 [天气应用实战](../projects/02-weather-app.md) — 权限弹窗与网络等待场景出处
- 🚀 [生产级移动应用](../projects/04-production-mobile-app.md) — E2E 纳入 CI 门禁的完整链路
- 🚀 [EAS Build 构建流程](../deployment/01-eas-build.md) — 为 E2E 产出构建物的构建体系
