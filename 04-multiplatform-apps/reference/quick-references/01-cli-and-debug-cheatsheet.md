# CLI 命令与调试速查表

> **难度**: ⭐ | **前置**: 已完成环境搭建（[01-environment-setup](../../basics/01-environment-setup.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#CLI` `#调试` `#DevTools` `#Hermes` `#hdc` |
| **更新日期** | `2026年9月` |

## 工程生命周期命令

```bash
# 创建工程
npx create-expo-app@latest MyApp                    # Expo 路线（默认模板含 expo-router；--template default@sdk-57 可锁 SDK）
npx @react-native-community/cli init MyApp          # bare 路线（RN 0.87：Node 22+ / AGP 9 / Kotlin 2.0+）

# 启动 Metro（dev server）
npx expo start                  # Expo；--tunnel 走内网穿透
npx react-native start          # bare；--reset-cache 清缓存

# 运行到设备
npx expo run:android | run:ios  # Expo 编译原生并安装
npm run android | npm run ios   # bare 工程

# 依赖管理
npx expo install <pkg>          # Expo：自动装与 SDK 匹配的版本
npm uninstall <pkg> && npm i    # 修改原生依赖后需重新构建

# 原生工程生成/同步
npx expo prebuild               # 从 app.json 生成 android/ ios/
npx expo prebuild --clean       # 清除后重建（丢弃手工原生改动）

# 升级
npx expo install expo@latest --fix   # Expo SDK 升级
# bare: 参考 Upgrade Helper（react-native-community.github.io/upgrade-helper）
```

## 调试入口

| 手段 | 打开方式 |
|------|---------|
| 开发者菜单 | 模拟器 `Cmd+D`（iOS）/ `Cmd+M` 或摇一摇（Android）；CLI `j`（Expo） |
| React Native DevTools | 菜单 "Open React DevTools"；含 Console/Components/Network/Profiler |
| Element Inspector | 菜单 "Toggle Element Inspector"，点元素查样式 |
| Perf Monitor | 菜单打开，观察 JS/UI 双线程帧率 |
| 日志 | Metro 终端（console 输出）；`adb logcat *:S ReactNativeJS:V` |

**关于 Flipper**: Flipper 已被官方弃用并从 RN 中移除（现行版本已不可用），统一使用 React Native DevTools + Hermes 调试协议与 Expo DevTools；老项目维护时才可能遇到它。

## 设备与桥接命令（Android / adb）

```bash
adb devices                                  # 设备列表
adb reverse tcp:8081 tcp:8081                # 真机访问电脑 Metro（必会）
adb install -r app-debug.apk                 # 覆盖安装
adb logcat --pid=$(adb shell pidof com.myapp) # 只看本应用日志
adb shell input keyevent 82                  # 唤出开发者菜单（无按键设备）
adb shell am start -W -n com.myapp/.MainActivity  # 冷启动计时
```

## 设备与桥接命令（iOS / xcrun）

```bash
xcrun simctl list devices                    # 模拟器列表
xcrun simctl openurl booted "myapp://deep"   # 模拟器深链测试
xcrun simctl install booted MyApp.app        # 安装应用
xcrun simctl status_bar booted override --time "9:41"  # 改状态栏（截图用）
```

## 设备与桥接命令（鸿蒙 / hdc）

```bash
hdc list targets                             # 设备列表
hdc install entry-default-signed.hap         # 安装 HAP
hdc hilog | grep <tag>                       # 日志
hdc rport tcp:8081 tcp:8081                  # 反向端口转发（真机连 Metro）
hdc file send local remote                   # 推文件
```

## 常用调试技巧

### 定位重渲染
1. DevTools → Components 面板 → 开启 "Highlight updates"
2. Profiler 录制一次交互，看 flame graph 中超时的组件
3. 对热点组件加 `React.memo` + 稳定 props（useCallback/useMemo）

### Hermes 堆与 CPU
- React Native DevTools 的 Profiler/Console 直接连 Hermes（无需远程调试模式）
- 内存增长疑似泄漏：连续三次 GC 后拍 heap snapshot，对比留存对象

### Metro 缓存类问题
```bash
# 症状：改了没生效 / 神秘语法错误 / 模块找不到
watchman watch-del-all
rm -rf node_modules && npm i
npx react-native start --reset-cache
# iOS 追加: cd ios && rm -rf Pods && pod install
# Android 追加: cd android && ./gradlew clean
```

### 网络抓包
- DevTools Network 面板可看 RN 内 fetch/XHR
- 需要看原生层流量（原生 SDK 请求）时用 Charles/Proxyman，配信任证书（Android 7+ 需网络安全配置放行）

## 环境信息速查命令

```bash
npx react-native info          # 一次性收集环境信息（提问/排查必附）
npx expo-doctor                # Expo：检查依赖版本一致性
node -v && npm -v && java -version
```

## 🔗 相关文档

- 📄 **[故障排除](./02-troubleshooting.md)**: 按症状查解法
- 📄 **[RNOH 字典](../language-concepts/05-harmonyos-rnoh-api.md)**: hdc 命令上下文
- 📄 **[Expo 要点](../framework-essentials/01-expo-essentials.md)**: EAS 与 prebuild
- 📄 **[高级特性教程](../../basics/07-advanced-features.md)**: 性能优化的系统视角

*相关教程: [第一个 App](../../basics/02-first-app.md) 中的调试初体验*
