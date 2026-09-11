# 故障排除 — 常见错误与解法

> **难度**: ⭐ | **前置**: 无（按症状直接跳入查阅）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#白屏` `#签名` `#依赖冲突` `#鸿蒙适配` `#排错` |
| **更新日期** | `2026年9月` |

## 通用排查流程

1. **先看 Metro 终端**——80% 的红屏在终端里有完整堆栈
2. `npx react-native info` / `npx expo-doctor` 收集环境信息
3. 按"症状分类"对号入座下表；同类问题出现两次以上，记入个人踩坑笔记

## 白屏 / 启动类

| 症状 | 原因 | 解法 |
|------|------|------|
| 启动即白屏无报错 | `AppRegistry` 注册名与原生侧不一致 | 核对 Android `getMainComponentName()` / iOS 注册名 / 鸿蒙 `appKey` |
| 真机白屏、模拟器正常 | 设备连不上 Metro | `adb reverse tcp:8081 tcp:8081`；鸿蒙 `hdc rport tcp:8081 tcp:8081` |
| 白屏 + 黄框 "No bundle URL present" | Metro 未启动或端口被占 | 启动 Metro；结束占用 8081 端口的进程后重启 |
| 生产包正常、开发包白屏（或反之） | debug/release 配置差异 | 检查 dev support 开关与 bundle 打包配置 |
| 升级 RN 后白屏 | 新旧架构混用 / 库未适配 | 按 Upgrade Helper 升级，核对三方库适配版本 |

## 构建与签名类

### Android

| 症状 | 解法 |
|------|------|
| `SDK location not found` | 创建 `android/local.properties` 写入 `sdk.dir=/path/to/Android/sdk` |
| `Unsupported class file major version` | Gradle 与 JDK 版本不匹配，改用 JDK 17 |
| `Duplicate class` / 依赖冲突 | `./gradlew app:dependencies` 找冲突库，用 `resolutionStrategy.force` 或升级统一版本 |
| 安装失败 `INSTALL_PARSE_FAILED_NO_CERTIFICATES` | debug 签名缺失；确认 `debug.keystore` 存在且 build.gradle 引用正确 |
| 内存不足 `OutOfMemoryError` | `gradle.properties` 调大 `org.gradle.jvmargs=-Xmx4g` |

### iOS

| 症状 | 解法 |
|------|------|
| `pod install` 卡在 CDN/源 | 更换镜像源或检查网络代理；`pod repo update` |
| 头文件 not found | `rm -rf Pods Podfile.lock && pod install`；确认 Xcode Command Line Tools |
| 签名错误 "No profiles for ... were found" | Xcode → Signing & Capabilities 勾选自动签名并登录正确团队 |
| 构建报 duplicate symbols | 三方库重复链接，`pod deintegrate` 后重装 |

### 鸿蒙

| 症状 | 解法 |
|------|------|
| 签名失败 | DevEco → File → Project Structure → Signing Configs 自动签名；确认 AGC 账号已实名 |
| `hvigorw` 构建失败 | 核对 `build-profile.json5` 的 SDK API 版本与 DevEco 安装版本一致 |
| HAP 安装失败 | `hdc install` 前先卸载旧包；调试证书 profile 与设备 UDID 匹配 |

## 依赖冲突类

```bash
# 定位 npm 依赖冲突
npm ls react-native            # 谁在依赖不同版本
npm dedupe                     # 尝试自动去重

# RN 三方库版本仲裁（Expo 工程）
npx expo install --check       # 校正为 SDK 匹配版本
```

| 症状 | 解法 |
|------|------|
| `Unable to resolve module X` | `rm -rf node_modules && npm i`，必要时 `--reset-cache` 重启 Metro |
| 装了库但原生方法 undefined | 原生代码未链接进工程：重新构建原生；iOS 补跑 `pod install` |
| React 版本冲突警告 | 每个 RN 版本绑定固定 React 版本（如 RN 0.86 ↔ React 19.2），以官方版本表为准，不要单独升 React |
| 同一库两个大版本并存 | peerDependencies 冲突，升级依赖它的库或用 overrides 钉住版本 |

## 鸿蒙适配类

| 症状 | 原因 | 解法 |
|------|------|------|
| 真机运行崩溃 "library not found" | 三方库无 harmony 适配 | 换 `@react-native-ohos/*` 适配版 |
| Metro 连接失败 | 端口转发未配 | `hdc rport tcp:8081 tcp:8081` |
| 组件渲染异常（样式错乱） | ArkUI 映射差异 | 对照 RNOH 组件映射表，改用支持的样式写法 |
| 版本不匹配崩溃 | `react-native-harmony` 与 RN 版本错位 | 按 RNOH 版本映射表对齐（见 [RNOH 字典](../language-concepts/05-harmonyos-rnoh-api.md)） |
| 权限直接拒绝 | `module.json5` 未声明 | 补 `requestPermissions` 后重新签名安装 |

## 运行时类

| 症状 | 解法 |
|------|------|
| 红屏 "Invariant Violation: Text strings must be rendered within a <Text>" | `<View>` 里裸写了字符串，包上 `<Text>` |
| 列表闪烁 | `keyExtractor` 用了 index 或不稳定 key；改为业务唯一 id |
| 键盘遮挡输入框 | `KeyboardAvoidingView`（iOS padding / Android height） |
| 热更新后状态错乱 | Fast Refresh 对含副作用的模块会整页重载，属于预期行为；重逻辑移出渲染路径 |
| iOS 安全区顶到刘海 | 用 `useSafeAreaInsets` 处理，不要写死 padding |
| 深色模式部分页面不生效 | 检查是否写死颜色；用 `useColorScheme` 或主题令牌 |

## 性能类速判

| 症状 | 首查 |
|------|------|
| 列表滑动掉帧 | renderItem 重渲染（memo）→ `getItemLayout` → 图片尺寸 |
| 点击响应 >200ms | JS 线程阻塞：Profiler 定位，重活移出 JS 线程 |
| 内存持续上涨 | 未清理的订阅/定时器/动画句柄 |
| 启动慢 | bundle 体积、Hermes 是否开启、首屏请求数 |

## 🔗 相关文档

- 📄 **[CLI 命令与调试速查](./01-cli-and-debug-cheatsheet.md)**: 排错用命令
- 📄 **[RNOH 字典](../language-concepts/05-harmonyos-rnoh-api.md)**: 版本对齐与适配清单
- 📄 **[组件 Props 全表](../language-concepts/02-components-props.md)**: 列表闪烁相关 props
- 📄 **[环境搭建教程](../../basics/01-environment-setup.md)**: 环境类问题的根因预防

*延伸: React Native 官方 troubleshooting 页 · RNOH 仓库 Issue 区*
