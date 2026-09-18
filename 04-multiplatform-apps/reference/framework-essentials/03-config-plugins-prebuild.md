# Config Plugins 与 prebuild — 原生工程的生成模型

> **难度**: ⭐⭐ | **前置**: 了解 Expo 工程配置（[01-expo-essentials](./01-expo-essentials.md)）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Config Plugins` `#prebuild` `#CNG` `#app.json` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

采用 CNG 的 Expo 工程可将原生目录（`android/`、`ios/`）视为**可再生产物**；手工维护原生工程的项目不适用此约定。这套模型叫 CNG（Continuous Native Generation）：

- **app.json / app.config.ts**：原生工程配置的**唯一事实来源**（应用名、图标、权限、深链 scheme、插件参数）
- **prebuild**：`npx expo prebuild` 读取配置，从模板生成原生工程；`--clean` 丢弃手工改动重新生成
- **Config Plugin**：一个配置变换函数 `(config, props) => config`，可注册修改原生文件的 mod，在 prebuild 时以声明式方式修改原生工程内容（AndroidManifest 权限、Info.plist 键值、Gradle 属性、原生文件注入）
- **EAS Build 在需要生成缺失的原生工程时执行 prebuild**，因此"本地没跑过 prebuild"不等于云端也不跑——配置必须在 app config 里，而不是改在本地原生目录里

**心智模型**：把原生目录当"编译输出"（像 `.js` 编译产物），永远改输入（app config + 插件），不改输出。

## 📖 语法/签名

```jsonc
// app.json —— plugins 数组：字符串（无参数插件）或 [名称, 参数对象]
{
  "expo": {
    "name": "MyApp",
    "scheme": "myapp",
    "plugins": [
      "expo-router",
      ["expo-camera", { "cameraPermission": "扫描二维码需要使用相机" }],
      "./plugins/with-custom-entitlements"   // 本地自定义插件
    ]
  }
}
```

```ts
// 自定义插件签名：(ExpoConfig, 插件参数) => ExpoConfig  —— 必须返回 config
import { withInfoPlist, type ConfigPlugin } from 'expo/config-plugins';

const withLsApplicationCategory: ConfigPlugin<{ category: string }> = (config, props) =>
  withInfoPlist(config, (mod) => {
    mod.modResults.LSApplicationCategoryType = props.category;
    return mod;
  });

export default withLsApplicationCategory;
```

## 💡 示例

```bash
# 日常流程：改配置 → 重新生成 → 编译
npx expo prebuild --clean          # 丢弃旧的原生目录重新生成
npx expo run:ios                   # 编译安装（Android: run:android）

# 查看插件对配置的实际改动（不落盘）
npx expo config --type prebuild | less
```

```bash
# 鸿蒙（RNOH）接入点：prebuild 出原生工程后，按 bare 流程接入
# harmony/ 壳工程不在 CNG 管辖内，版本对齐见 RNOH 字典
```

## ⚠️ 常见陷阱

- **手工改 `android/`、`ios/` 后被覆盖**：下次 prebuild --clean 会丢弃原生目录的手工修改；不能笼统认定每次 EAS 构建都会重建它们；改动必须沉淀为插件或 app config 字段
- **插件顺序有语义**：修改同一目标的插件按声明顺序叠加；文档要求"放最后"的插件（如字体、通知类）要放最后
- **改了 plugins 忘了重新 prebuild**：插件在 prebuild 阶段生效，只重启 Metro 不会有任何变化
- **权限写在原生清单里**：权限声明走插件的 props 或 app config 的 `permissions`/`infoPlist`，散落在清单里不可复现
- **以为 scheme/图标改动即时生效**：这些在生成原生工程时物化，需重新 prebuild + 重装 App

<!-- full-library-explanation -->
## 生成模型必须能重复得到同一结果

CNG 是一种工程选择，不是所有 Expo 项目的强制规则。采用它时，配置、插件、依赖锁文件和模板版本共同决定原生工程；手工维护并提交 ios/android 的项目则需要维护原生代码本身。EAS 是否运行 prebuild 也取决于提交的工程是否已有原生目录。

`--clean` 会重新生成原生目录，执行前应确认手工改动已进入版本控制或被迁移到插件。日常不应把“清掉重来”当成所有构建错误的第一步。插件可能修改文件，其效果不只是一个无副作用的普通 JS 纯函数。

练习：在可丢弃的学习工程中，用插件设置一个 Info.plist 字段，生成后记录 diff，再生成一次。验收：字段不重复追加、没有无关文件持续变化。将输入恢复后应能重新生成可解释的结果；若依赖一次性的手工修补，就还没有可复现的生成流程。

## 🔗 相关条目

- 📄 [Expo 要点](./01-expo-essentials.md) — app config 与 Expo 模块总览
- 📄 [EAS Build 操作指南](../../deployment/01-eas-build.md) — 云端构建如何消费这套配置
- 📄 [RNOH 鸿蒙适配字典](../language-concepts/05-harmonyos-rnoh-api.md) — prebuild 后的鸿蒙接入
- 📄 [dev client 与 expo-updates](./04-dev-client-and-updates.md) — 原生能力变更后的运行模型

*延伸: Expo 官方文档 "Config Plugins" · "Prebuild" · "Continuous Native Generation"*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
