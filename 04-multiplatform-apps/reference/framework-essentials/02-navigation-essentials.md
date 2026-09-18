# React Navigation API 速查 — 导航器、linking 与深链

> **难度**: ⭐ | **前置**: 已读过导航教程（[05-navigation](../../basics/05-navigation.md)）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#ReactNavigation` `#深链` `#linking` `#API速查` |
| **更新日期** | `2026年9月` |

</details>

## NavigationContainer / linking 配置

### 描述
导航树的根容器。`linking` 属性把 URL 映射到路由，实现"浏览器/推送 → App 内页面"的深链跳转。

### 语法和示例
```tsx
import { NavigationContainer } from '@react-navigation/native';

const linking = {
  prefixes: ['myapp://', 'https://myapp.example.com'],
  config: {
    screens: {
      Home: 'home',
      Detail: 'detail/:itemId',      // 路径参数映射
      NotFound: '*',
    },
  },
};

<NavigationContainer linking={linking} fallback={<Splash />}>
  <RootNavigator />
</NavigationContainer>
```

### 平台注册侧

| 平台 | 配置位置 |
|------|---------|
| Android | `AndroidManifest.xml` 的 `intent-filter`（scheme + host） |
| iOS | Info.plist URL Types；Universal Links 需 apple-app-site-association 文件 |
| 鸿蒙 | `module.json5` 中 `want` 隐式跳转配置（skills） |

### 陷阱
- prefixes 未在平台侧注册时，冷启动深链静默失败
- HTTPS 深链（Universal Links/App Links）需域名侧文件与原生配置同时就位，缺一不可

## navigation 对象方法速查

| 方法 | 行为 |
|------|------|
| `navigate(name, params)` | 按导航器、版本及路由身份导航；不保证回退到栈内任意同名页 |
| `push(name, params)` | 无条件压栈 |
| `replace(name, params)` | 替换当前页（登录后跳首页用） |
| `goBack()` | 返回上一层 |
| `popToTop()` | 弹回栈底 |
| `setParams(params)` | 修改当前页参数 |
| `setOptions(options)` | 动态改头部（标题/按钮） |
| `addListener('focus'/'blur', cb)` | 监听页面显隐 |
| `dispatch(StackActions.pop(n))` | 复杂栈操作 |

```tsx
navigation.setOptions({ title: route.params.title });
navigation.replace('Main');
```

## 导航器关键 Props

### NativeStack（`@react-navigation/native-stack`）

| Prop/Option | 说明 |
|-------------|------|
| `screenOptions.headerShown` | 显隐头部（嵌套 Tabs 时外层设 false） |
| `screenOptions.animation` | 转场动画 `'slide_from_right' \| 'fade' \| 'none'` |
| `screenOptions.presentation` | `'card' \| 'modal' \| 'fullScreenModal'` |
| `options.headerRight/headerLeft` | 头部自定义按钮 |
| `options.gestureEnabled` | 返回手势开关 |

### BottomTabs

| Prop/Option | 说明 |
|-------------|------|
| `screenOptions.tabBarStyle` | 标签栏样式 |
| `screenOptions.tabBarIcon` | 图标函数 `({ color, size }) => Icon` |
| `screenOptions.tabBarBadge` | 角标（未读数） |
| `screenOptions.lazy` | 惰性挂载 Tab 页，默认 true |
| `tabBarButton` | 自定义按钮（中间凸起按钮） |

### Drawer

| Prop/Option | 说明 |
|-------------|------|
| `screenOptions.drawerType` | `'front' \| 'back' \| 'slide'` |
| `screenOptions.swipeEnabled` | 侧滑开关（列表页可关闭防冲突） |
| `drawerContent` | 自定义抽屉内容组件 |

## 页面生命周期与显隐

```tsx
// Tab 切回刷新的正确姿势（useEffect 不响应 Tab 切换）
import { useFocusEffect } from '@react-navigation/native';
import { useCallback } from 'react';

useFocusEffect(
  useCallback(() => {
    refetch();
    return () => pausePolling();
  }, [refetch]),
);
```

**陷阱**: Stack push 后原页面通常保持挂载，而 pop 会移除被弹出的页面；Tab 页面通常保持挂载——依赖"卸载清理"的逻辑在这两处不成立，需用 focus/blur 事件。

## 深链调试速查

```bash
# Android 模拟器
adb shell am start -W -a android.intent.action.VIEW -d "myapp://detail/42"

# iOS 模拟器
xcrun simctl openurl booted "myapp://detail/42"

# 鸿蒙（want 调试经 DevEco 或 hdc shell aa start）
hdc shell aa start -a EntryAbility -b com.example.app
```

<!-- full-library-explanation -->
## 路由身份与页面生命周期

路由参数优先传 `itemId`，页面再按 ID 读数据。把整个可变对象塞入 params 容易产生过期副本，也不利于深链和状态持久化。类型声明用于开发检查；外部链接输入仍需运行时校验。

假设栈为 Home → Detail(1) → Detail(2)：push 会添加新路由；goBack 弹出顶部；replace 替换当前路由。`navigate` 是否复用、切换或新增要看导航器、版本和 getId 等配置，不能一律解释成回到栈中任意同名页。需要回到既有页面时，核对当前版本的 popTo 等明确操作。

练习：记录上述每次操作后的 route key、参数和栈长度，再测试冷启动深链。验收：能解释“同名页面”和“同一个路由实例”的区别；离开页面后轮询暂停，返回后只恢复一份。非顶部的已挂载页面不能只靠卸载事件停止工作。

参考：[React Navigation 迁移说明](https://reactnavigation.org/docs/upgrading-from-6.x/)。

## 🔗 相关文档

- 📄 **[Expo 要点](./01-expo-essentials.md)**: expo-router 曾基于本 API 构建（SDK 56 起已 fork React Navigation 内置）
- 📄 **[TS 类型模式](../language-concepts/04-typescript-patterns.md)**: ParamList 类型化
- 📄 **[RN 核心 API 字典](../language-concepts/01-rn-core-api.md)**: Linking 底层 API
- 📄 **[导航基础教程](../../basics/05-navigation.md)**: 系统学习路径

*延伸: React Navigation 官方文档 reactnavigation.org*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
