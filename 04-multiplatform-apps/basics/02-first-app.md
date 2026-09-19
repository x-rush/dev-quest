# 第一个 App — 创建、Metro 与三端运行

## 先理解，再动手

开发服务器、应用进程和设备是不同参与者。设备必须能访问打包服务；原生崩溃与 JavaScript 错误也在不同日志中出现。

**本节自测**：保持设备联网启动应用，再停止打包服务观察开发模式下的变化。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

知道界面从哪里取得 bundle，并能找到相应日志；不要把通信失败误认为组件写法错误。

</details>

> **文档简介**: 从零创建一个 React Native App，理解 Metro 打包器的工作方式，并先把它运行在一个已选平台的真机或模拟器上
>
> **目标读者**: 已完成环境搭建、希望理解 RN 应用"启动链条"的初学者
>
> **前置知识**: 已按 [01-environment-setup](./01-environment-setup.md) 配置好至少一端工具链，掌握 React 函数组件基础

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#第一个应用` `#Metro` `#真机调试` `#项目结构` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 分别用 Expo 与 RN CLI 创建工程，并说清两者工程形态的差异
- ✅ 解释 Metro 把 TSX 代码送到屏幕的完整链路
- ✅ 在一个已选 Android 或 iOS 目标运行、输入和重新加载；理解鸿蒙需单独按 RNOH 工程验收
- ✅ 看懂 RN 工程的目录结构，知道改哪个文件会生效

## 🚀 创建工程

### 方式一：Expo（推荐）

```bash
npx create-expo-app@latest MyFirstApp
cd MyFirstApp
npx expo start
```

创建完成后按终端提示可尝试打开对应目标（`a` = Android，`i` = iOS，`w` = Web）。`npx expo start` 启动的是 Metro 开发服务器：首次运行前，先确保目标模拟器/设备和对应 native build 已按[环境搭建](./01-environment-setup.md)准备好。模板是否使用 Expo Router、首页在哪个文件，取决于创建时选的模板；先查看生成的项目目录再编辑。

### 方式二：RN CLI（bare）

```bash
npx @react-native-community/cli init MyFirstApp
cd MyFirstApp

# Android
npm run android

# iOS（仅 macOS；若仓库提供 Gemfile，使用它固定 CocoaPods）
bundle exec pod install --project-directory=ios
npm run ios
```

## 🔍 核心概念：Metro 与启动链路

**定义**: Metro 是 RN 官方的 JavaScript 打包器，角色类似 Web 侧的 webpack/vite。

**启动链路（四步）**:

1. **入口注册**: `App.tsx`（或入口文件）通过 `AppRegistry.registerComponent` 注册根组件
2. **打包**: Metro 根据入口和依赖图转换、解析并提供 JavaScript bundle；是否采用 Hermes、怎样生成生产产物，取决于项目和构建配置。
3. **加载**: 开发模式下，已安装的原生应用向 Metro 请求 bundle；生产构建使用随安装包或更新通道交付的 bundle。两者的网络路径、缓存和错误日志不同。
4. **渲染**: 原生宿主加载运行时，把 React Native 组件更新提交为平台原生视图。Fabric 是新架构的一部分，不应把它当成所有项目已经启用的前提。

**与 Web React 的关键差异**: RN 没有浏览器 DOM，`View`/`Text` 组件最终映射为 Android 的 `ViewGroup`/`TextView`、iOS 的 `UIView`/`UILabel`。写 `<div>` 会直接报错。

## 💻 第一个界面

打开 `app/(tabs)/index.tsx`，替换为以下代码（expo-router 页面组件：导出默认组件即可，无需 AppRegistry；`App.tsx` 仅见于 blank 模板与 bare 工程）：

```tsx
// app/(tabs)/index.tsx
import { useState } from 'react';
import {
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
  Platform,
} from 'react-native';

export default function Home() {
  const [name, setName] = useState('');
  const [greeting, setGreeting] = useState('还没有提交名字');

  function submitName() {
    const normalized = name.trim();
    setGreeting(normalized ? `欢迎，${normalized}` : '请输入名字后再提交');
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>
        你好，React Native！运行在 {Platform.OS} 上
      </Text>
      <TextInput
        style={styles.input}
        placeholder="输入你的名字"
        value={name}
        onChangeText={setName}
      />
      <TouchableOpacity
        accessibilityRole="button"
        accessibilityLabel="提交名字"
        style={styles.button}
        onPress={submitName}
      >
        <Text style={styles.buttonText}>提交</Text>
      </TouchableOpacity>
      <Text style={styles.result}>{greeting}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 24,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  },
  button: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    padding: 14,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
  },
  result: {
    marginTop: 16,
    textAlign: 'center',
  },
});
```

**可观察结果**：输入 `Ada` 后点“提交”，页面显示“欢迎，Ada”；清空输入后提交，显示“请输入名字后再提交”。保存后 Metro 会尝试通过 Fast Refresh 更新设备；能否保留组件状态取决于改动是否满足刷新边界。若更新失败或状态不符合预期，按提示完整重新加载再判断代码效果。

## 🛠️ 真机运行

### Android 真机

1. 手机开启"开发者选项 → USB 调试"
2. USB 连接电脑，`adb devices` 确认设备出现
3. `npm run android`（或 Expo 下 `npx expo run:android`）

### iOS 真机（需 macOS）

1. Xcode → Settings → Accounts 登录 Apple ID
2. 用数据线连接 iPhone，Xcode 中选择该设备作为运行目标
3. 首次运行需在设备上信任开发者证书：设置 → 通用 → VPN与设备管理

### 鸿蒙真机/模拟器

1. 从目标 RNOH 发行版的最小示例开始，确认其 RN、RNOH、DevEco 和 SDK 组合。
2. 按该示例的步骤生成或打开 `harmony/` 壳工程，连接华为真机或启动模拟器。
3. 构建、安装、启动后，再按其文档配置 Metro 连通；不要把 Android/iOS 的命令或目录结构直接套用。

RNOH 的架构细节与依赖版本匹配见 [05-harmonyos-rnoh-api](../reference/language-concepts/05-harmonyos-rnoh-api.md)。

## 📁 目录结构速读（bare 工程）

```
MyFirstApp/
├── App.tsx / index.js     # JS 入口与根组件
├── android/               # Android 原生工程（Gradle）
├── ios/                   # iOS 原生工程（Xcode + CocoaPods）
├── harmony/               # 仅在所选 RNOH 集成方案创建；不是每个 RN 工程都自带
├── metro.config.js        # Metro 打包配置
├── babel.config.js        # 语法转换配置
└── package.json           # 依赖与 npm scripts
```

日常 90% 的改动只发生在 `App.tsx` 与 `src/` 业务代码里；`android/`、`ios/`、`harmony/` 只在写原生模块或改构建配置时才打开。

## 🎨 最佳实践

第一个应用只需一个能解释清楚的界面：状态在哪里、点击如何改变状态、屏幕为何更新。逻辑增长后再拆页面与 Provider，不必先制造完整目录。用真机验证一次点击、输入和重启，确认连接的确是当前构建。

“修改不生效”先检查 Metro 进程、端口和设备连接，再考虑重置缓存。Expo prebuild 管理的原生文件可能被重新生成，修改应进入配置或插件；手工管理的原生工程则有不同维护方式，不应禁止所有 android/ios 目录修改。

## ❓ 常见问题

### Q1: 红屏 "Unable to load bundle"？
**A**: 设备与 Metro 不在同一网络（真机场景），执行 `adb reverse tcp:8081 tcp:8081` 让 Android 真机通过 USB 访问电脑的 Metro；iOS 真机在 Xcode 的 scheme 中确认 host 配置。

### Q2: 修改代码不生效？
**A**: 先确认 Metro 终端没有报错；再试 Fast Refresh 开关（模拟器摇一摇/`Cmd+D` 菜单）；最后 `--reset-cache` 重启 Metro。

### Q3: 鸿蒙真机运行白屏？
**A**: 按 RNOH 版本对齐清单核对 `react-native-harmony` 与 DevEco SDK API 版本，详见 [常见错误排查](../reference/quick-references/02-troubleshooting.md)。

## 🎯 练习与实践

### 练习一：一个平台的完整运行记录

**任务要求**:
1. 选择 Android 或 iOS 的一个模拟器或真机，运行本节 App。
2. 输入 `Ada`、提交、清空输入再提交，记录三个屏幕状态。
3. 暂停 Metro 或断开设备与开发机的连接，记录出现的现象；恢复后重新加载。
4. 若要增加第二平台，重新构建并重复上述步骤，不能只打开 Web 预览代替。

**评估标准**: 记录能够说明实际运行的平台、构建方式、输入与两个输出，以及 Metro 不可达时的表现。第二、三平台的记录是后续扩展，不是本课通过前提。

### 练习二：认识启动链路

**任务要求**:
1. 观察并记录 Metro 终端里 bundle 编译、加载的日志输出
2. 故意制造一个 JS 语法错误，观察红屏与 Metro 终端报错的对应关系

**提示**: 红屏信息与 Metro 终端日志指向同一处源码位置，养成两边对照看的习惯。

---

## 🔗 相关文档

- 📄 **[核心组件与样式](./03-components-jsx.md)**: 下一课，系统学习 View/Text/FlatList 与 Flexbox
- 📄 **[RN 核心 API 速查](../reference/language-concepts/01-rn-core-api.md)**: `AppRegistry`、`Platform` 的完整参数表
- 📄 **[Expo 要点](../reference/framework-essentials/01-expo-essentials.md)**: expo-router 文件路由规则
- 📄 **[CLI 命令与调试速查](../reference/quick-references/01-cli-and-debug-cheatsheet.md)**: `adb reverse` 等命令速查
- 📄 **[组件 Props 全表](../reference/language-concepts/02-components-props.md)**: 本文用到组件的完整属性字典

> 💡 **学习建议**: 把"设备 → Metro → 原生渲染"这条链路想清楚，后面遇到白屏、红屏、热更新失灵时，你才能快速定位是哪一环断了。


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
