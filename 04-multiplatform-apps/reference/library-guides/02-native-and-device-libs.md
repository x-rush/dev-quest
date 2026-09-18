# 原生与设备能力库指南 — 相机/推送/存储/传感器

> **难度**: ⭐⭐ | **前置**: 了解原生模块概念（[06-native-modules](../../basics/06-native-modules.md)）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#相机` `#推送` `#存储` `#传感器` `#权限` |
| **更新日期** | `2026年9月` |

</details>

## 选型优先级

1. **Expo SDK 模块**（`expo-*`）：有则先用，配置最省心
2. **社区 harmony 适配版**（`@react-native-ohos/*`、`@react-native-oh-tpl/*`）：三端一致性的关键
3. **社区原生库**：确认标注 "New Architecture ready" 再引入
4. **自研 TurboModule**：以上都没有时（见 [原生模块教程](../../basics/06-native-modules.md)）

## 相机与媒体

| 库/模块 | 能力 | 备注 |
|---------|------|------|
| `expo-camera` | 取景、扫码 | 配置插件声明权限文案 |
| `expo-image-picker` | 相册选图、拍照 | 无需复杂权限配置 |
| `react-native-vision-camera` | 高性能相机、帧处理器 | 进阶场景；鸿蒙需适配版 |
| `expo-image` / `react-native-fast-image` | 图片缓存加载 | 列表图片优化首选 |
| `react-native-video` / `expo-video` | 播放器 | 支持字幕/缓存策略 |

```tsx
// expo-image-picker 最小示例
import * as ImagePicker from 'expo-image-picker';

const result = await ImagePicker.launchImageLibraryAsync({
  mediaTypes: ['images'],
  quality: 0.7,
  allowsEditing: true,
});
if (!result.canceled) {
  upload(result.assets[0].uri);
}
```

**陷阱**: iOS 相册/相机权限文案必须写在 Info.plist（Config Plugin 代办）；Android 13+ 细分了照片权限（READ_MEDIA_IMAGES）。

## 推送通知

| 层 | Android | iOS | 鸿蒙 |
|----|---------|-----|------|
| 通道 | FCM / 厂商通道 | APNs | 华为 Push Kit |
| RN 封装 | `@react-native-firebase/messaging` | 同左 / `expo-notifications` | HMS SDK（原生侧接入） |

```tsx
// expo-notifications 最小示例
import * as Notifications from 'expo-notifications';

// 注册并拿到推送 token（iOS 需真机 + APNs 凭据）
const token = (await Notifications.getDevicePushTokenAsync()).data;

// 前台收到通知的行为
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowBanner: true,
    shouldShowList: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});
```

**陷阱**: 部分 Xcode/系统/硬件组合支持模拟器远程通知，最终仍应在目标真机验证注册与展示；国内 Android 无 GMS 设备要走厂商通道（华为设备即 Push Kit）。

## 存储

| 方案 | 场景 | 备注 |
|------|------|------|
| `@react-native-async-storage/async-storage` | 键值 JSON | 事实标准，鸿蒙有适配版 |
| `expo-secure-store` / `react-native-keychain` | token/密钥 | 系统级加密（Keystore/Keychain） |
| `react-native-mmkv` | 高频小数据 | C++ 同步读写；鸿蒙需适配版 |
| `expo-sqlite` / `op-sqlite` | 结构化离线数据 | 离线优先 App 的底座 |

## 传感器与设备能力

| 库/模块 | 能力 |
|---------|------|
| `expo-sensors` / `react-native-sensors` | 加速度计/陀螺仪/磁力计 |
| `expo-location` / `@react-native-community/geolocation` | 定位（后台定位需单独声明） |
| `react-native-healthkit` | 健康数据（iOS HealthKit；鸿蒙对应 Health Service） |
| `react-native-biometrics` / `expo-local-authentication` | 指纹/面容/鸿蒙生物识别 |
| `expo-battery` / `expo-network` | 电量/网络状态 |

```tsx
// expo-location 最小示例
import * as Location from 'expo-location';

const { status } = await Location.requestForegroundPermissionsAsync();
if (status === 'granted') {
  const pos = await Location.getCurrentPositionAsync({});
  console.log(pos.coords.latitude, pos.coords.longitude);
}
```

## 权限处理对照

| 能力 | Android | iOS | 鸿蒙 |
|------|---------|-----|------|
| 相机 | 运行时权限 + Manifest | Info.plist + 运行时 | module.json5 + 运行时授权 API |
| 定位 | ACCESS_FINE_LOCATION | NSLocationWhenInUseUsageDescription | ohos.permission.LOCATION |
| 推送 | POST_NOTIFICATIONS（13+） | 系统通知授权与 APNs 注册分别处理 | Push Kit 授权 |
| 推荐库 | `react-native-permissions`（统一 API） | 同左 | HMS 侧单独处理 |

**陷阱**: 不同库对拒绝和不可再询问的状态命名不同；依据返回值与 canAskAgain 等字段决定是否引导到设置，不要反复弹窗。

## 鸿蒙适配检查要点

- ✅ 优先查 RNOH 适配列表确认库的 harmony 版本
- ✅ 权限写入 `module.json5` 的 `requestPermissions`
- ✅ 推送/支付/地图等华为系服务需在 AGC（AppGallery Connect）开通并配置
- ✅ 无法适配的库用 ArkTS TurboModule 自研替代

<!-- full-library-explanation -->
## 能力调用的完整状态机

以定位为例，页面至少区分未申请、申请中、允许、拒绝、无法再次弹窗、系统定位关闭、定位超时和成功。Manifest/Info.plist 声明解释应用需要什么；运行时授权表达用户当前是否同意；设备服务状态决定此刻能否获得结果。一个 granted 值覆盖不了全部情况。

推送设备 token 是路由地址，不是登录凭证。应用账户切换、token 更新和注销时要同步服务端绑定；不能把旧用户的通知继续投递到新用户会话。系统展示通知的授权与获取设备 token 也是不同环节。

练习：选一个能力，记录拒绝授权、允许后撤销、设备服务关闭三个场景。验收：页面给出能执行的下一步；拒绝后仍可使用不依赖该能力的功能；日志不记录精确位置或凭证。上文 upload 等名字是业务接入点，须自行实现上传和错误处理。

## 🔗 相关文档

- 📄 **[Expo 要点](../framework-essentials/01-expo-essentials.md)**: expo-modules 完整清单
- 📄 **[RNOH 架构](../language-concepts/05-harmonyos-rnoh-api.md)**: 适配版依赖与 ArkTS 模块
- 📄 **[原生模块桥接教程](../../basics/06-native-modules.md)**: 自研兜底方案
- 📄 **[状态与数据请求库指南](./01-state-and-data.md)**: 存储层与状态层配合
- 📄 **[故障排除](../quick-references/02-troubleshooting.md)**: 权限/签名相关报错

*延伸: React Native Directory（reactnative.directory）· RNOH 三方库适配列表*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
