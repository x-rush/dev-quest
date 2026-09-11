# dev client 与 expo-updates — 运行模型与更新通道

> **难度**: ⭐⭐ | **前置**: 了解 Expo 两条运行载体（[frameworks/04-devtools](../../frameworks/04-devtools.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#dev client` `#Expo Go` `#expo-updates` `#runtime version` |
| **更新日期** | `2026年9月` |

## 📌 定义

JS 代码如何"跑进"真机 App？两种载体、一条更新通道：

- **Expo Go**：官方提供的**通用预览壳**，内置一套固定的原生模块。只能加载"全部依赖都在壳内"的纯 JS 项目——适合零依赖快速预览
- **dev client（development build）**：用**你自己的依赖**编译出来的调试壳（`npx expo run:ios` / `run:android` 或 EAS 构建开发档）。含任何三方原生模块的项目必须用它
- **expo-updates（OTA）**：App 内嵌一份 JS bundle 作为基线，运行时按 channel/runtime version 拉取远端更新包。**只能更新 JS 与资产，原生二进制永远不变**
- **runtime version**：更新兼容性的"锁"——原生代码指纹决定的版本号；App 只接受相同 runtime version 的更新包，保证 OTA 不与二进制错配

**分工记忆**：Expo Go = 别人的壳 + 你的 JS；dev client = 你的壳 + 你的 JS；生产包 = 你的壳 + 商店签名 + OTA 通道。

## 📖 语法/签名

```bash
# 生成并使用 dev client（含三方原生依赖时的标配）
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
      const check = await Updates.checkForUpdateAsync();
      if (check.isAvailable) {
        await Updates.fetchUpdateAsync();        // 下载更新包
        await Updates.reloadAsync();             // 以新包重载（或提示用户下次启动生效）
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

## 🔗 相关条目

- 📄 [调试与性能工具链](../../frameworks/04-devtools.md) — dev client 的日常使用
- 📄 [OTA 更新与可观测性](../../deployment/03-ota-updates-observability.md) — 发布策略与监控
- 📄 [EAS Build 操作指南](../../deployment/01-eas-build.md) — 开发档/生产档构建
- 📄 [Config Plugins 与 prebuild](./03-config-plugins-prebuild.md) — 原生依赖如何进入壳工程

*延伸: Expo 官方文档 "Development builds" · "EAS Update" · "runtime version"*
