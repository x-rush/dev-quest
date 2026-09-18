# dev client 与 expo-updates — 运行模型与更新通道

> **难度**: ⭐⭐ | **前置**: 了解 Expo 两条运行载体（[frameworks/04-devtools](../../frameworks/04-devtools.md)）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#dev client` `#Expo Go` `#expo-updates` `#runtime version` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

JS 代码如何"跑进"真机 App？两种载体、一条更新通道：

- **Expo Go**：官方提供的**通用预览壳**，内置一套固定的原生模块。可加载使用其内置原生能力及兼容 JS 库的项目，不能任意增加壳内没有的原生实现
- **dev client（development build）**：用**你自己的依赖**编译出来的调试壳（`npx expo run:ios` / `run:android` 或 EAS 构建开发档）。需要 Expo Go 未包含的原生能力时，使用包含该能力的自有构建
- **expo-updates（OTA）**：App 内嵌一份 JS bundle 作为基线，运行时按 channel/runtime version 拉取远端更新包。**只能更新 JS 与资产，原生二进制永远不变**
- **runtime version**：更新兼容性的"锁"——按所选策略生成或手动管理的兼容版本标识；App 只接受相同 runtime version 的更新包，帮助筛选兼容更新；若团队错误复用版本标识，仍可能发生错配

**分工记忆**：Expo Go = 别人的壳 + 你的 JS；dev client = 你的壳 + 你的 JS；生产包 = 你的壳 + 商店签名 + OTA 通道。

## 📖 语法/签名

```bash
# 生成并使用 dev client（在已有 Expo 工程中）
npx expo install expo-dev-client
npx expo run:ios                    # 或 run:android —— 编译出带调试协议的壳并安装
npx expo start --dev-client         # Metro 以 dev client 模式启动

# OTA 更新（expo-updates + EAS Update）
npx expo install expo-updates
eas update:configure                # 写入 app.json 的 updates/url 与 runtimeVersion 策略
eas update --branch production -m "修复文案"
```

```jsonc
// app.json —— runtime version 决定哪些 OTA 包能被接受
{
  "expo": {
    "runtimeVersion": { "policy": "appVersion" }, // 或 "fingerprint"（按原生依赖指纹）
    "updates": { "url": "https://u.expo.dev/your-project-id" }
  }
}
```

## 💡 示例

```tsx
// OTA 状态检查：启动后确认是否运行在最新更新包上
import * as Updates from 'expo-updates';
import { useEffect } from 'react';

function UpdatesChecker() {
  useEffect(() => {
    (async () => {
      if (__DEV__) return;                       // 开发环境不走 OTA
      try {
      const check = await Updates.checkForUpdateAsync();
      if (check.isAvailable) {
        await Updates.fetchUpdateAsync();        // 下载更新包
        // 已下载；在产品 UI 中提示用户，等安全时机再调用 reloadAsync。
      }
      } catch {
        // 检查失败时继续运行当前版本；记录脱敏错误供诊断。
      }
    })();
  }, []);
  return null;
}
```

## ⚠️ 常见陷阱

- **装了原生依赖还用 Expo Go**：启动即报"原生模块不存在"；出现 `expo-dev-client` 缺失提示即该换 dev client
- **以为 OTA 能更新一切**：加新原生库、改权限、改原生配置都必须走商店发版；OTA 只覆盖 JS/资产
- **runtime version 不匹配**：包发了但设备"收不到"，先核对 App 的 runtime version 与更新包是否一致（fingerprint 策略下依赖变动即换版本）
- **dev client 代码不热更**：新增原生依赖后必须重新编译壳（重跑 run:ios/android），Metro 热更新只覆盖 JS
- **更新包没灰度就全量推**：用 channel/分支分流（staging → production），坏包可回滚（重新指向旧包）

<!-- full-library-explanation -->
## 一次更新为什么能下载却不能使用

先核对项目、平台、channel 到 branch 的映射与 runtimeVersion，再看下载及启动日志。channel 是分发路由，runtimeVersion 表示兼容范围；二者不能互相替代。`appVersion` 策略需要团队在原生能力改变时正确升级版本，不能自动识别所有不兼容修改。

运行时检查更新会遇到断网、服务不可达和无可用更新，要捕获错误并允许用户继续使用现有版本。下载成功不意味着必须立即 reload；编辑表单中途重载会丢失未保存内容。示例应先呈现更新提示，选择安全时机重启。

练习：给同一开发项目制作两个原生能力不同的测试构建，只向匹配运行时发布测试更新。验收：兼容包收到更新，不兼容包仍可启动原内嵌版本；断网时不陷入白屏或重复重载。这里只在测试通道练习，发布命令会产生远端更新，不是只读检查。

## 🔗 相关条目

- 📄 [调试与性能工具链](../../frameworks/04-devtools.md) — dev client 的日常使用
- 📄 [OTA 更新与可观测性](../../deployment/03-ota-updates-observability.md) — 发布策略与监控
- 📄 [EAS Build 操作指南](../../deployment/01-eas-build.md) — 开发档/生产档构建
- 📄 [Config Plugins 与 prebuild](./03-config-plugins-prebuild.md) — 原生依赖如何进入壳工程

*延伸: Expo 官方文档 "Development builds" · "EAS Update" · "runtime version"*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
