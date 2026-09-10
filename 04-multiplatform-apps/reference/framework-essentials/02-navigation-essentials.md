# React Navigation API 速查 — 导航器、linking 与深链

> **难度**: ⭐ | **前置**: 已读过导航教程（[05-navigation](../../basics/05-navigation.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#ReactNavigation` `#深链` `#linking` `#API速查` |
| **更新日期** | `2026年9月` |

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
| `navigate(name, params)` | 去重跳转：栈内已有同名页则回退到它 |
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

useFocusEffect(
  useCallback(() => {
    refetch();
    return () => pausePolling();
  }, [refetch]),
);
```

**陷阱**: Stack 返回不销毁页面组件（保留滚动位置），Tab 页常驻——依赖"卸载清理"的逻辑在这两处不成立，需用 focus/blur 事件。

## 深链调试速查

```bash
# Android 模拟器
adb shell am start -W -a android.intent.action.VIEW -d "myapp://detail/42"

# iOS 模拟器
xcrun simctl openurl booted "myapp://detail/42"

# 鸿蒙（want 调试经 DevEco 或 hdc shell aa start）
hdc shell aa start -a EntryAbility -b com.example.app
```

## 🔗 相关文档

- 📄 **[Expo 要点](./01-expo-essentials.md)**: expo-router 是本 API 的封装层
- 📄 **[TS 类型模式](../language-concepts/04-typescript-patterns.md)**: ParamList 类型化
- 📄 **[RN 核心 API 字典](../language-concepts/01-rn-core-api.md)**: Linking 底层 API
- 📄 **[导航基础教程](../../basics/05-navigation.md)**: 系统学习路径

*延伸: React Navigation 官方文档 reactnavigation.org*
