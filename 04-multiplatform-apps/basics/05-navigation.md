# 导航基础 — React Navigation 栈/标签/抽屉

> **文档简介**: 用 React Navigation 7 搭建移动 App 的页面骨架：原生栈导航、底部标签、抽屉菜单，以及页面间参数传递
>
> **目标读者**: 已掌握组件与状态的初学者，准备把多个页面组织成完整应用
>
> **前置知识**: 完成 [04-state-hooks](./04-state-hooks.md)，了解 React Context 基本用法

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#导航` `#ReactNavigation` `#Stack` `#Tab` `#Drawer` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 安装并配置 React Navigation 的三端依赖
- ✅ 组合 Stack + Tab + Drawer 搭出主流 App 的导航结构
- ✅ 在页面间安全地传参与回调
- ✅ 理解三端导航交互差异（返回手势、物理返回键）

## 🛠️ 安装

```bash
# 核心包
npm install @react-navigation/native

# 三端原生依赖（Expo 工程用 npx expo install 代替 npm install）
npm install react-native-screens react-native-safe-area-context

# 按导航器类型追加安装
npm install @react-navigation/native-stack   # 原生栈
npm install @react-navigation/bottom-tabs    # 底部标签
npm install @react-navigation/drawer         # 抽屉（额外依赖 react-native-gesture-handler、react-native-reanimated）
```

安装完成后在入口文件用 `NavigationContainer` 包裹整棵应用树：

```tsx
// App.tsx
import { NavigationContainer } from '@react-navigation/native';

export default function App() {
  return <NavigationContainer>{/* 导航器在此嵌套 */}</NavigationContainer>;
}
```

## 🔍 核心概念：导航器的嵌套模型

**定义**: React Navigation 中每个导航器（Navigator）管理一组页面（Screen），导航器之间可以嵌套——这是搭建复杂结构的基本手段。

**典型结构**：外层原生栈做"启动页 → 主界面 → 详情页"的跳转，主界面内嵌底部标签做一级分区。

```
NativeStack
├── Splash（启动页）
├── Main（内嵌 BottomTabs）
│   ├── Home
│   ├── Discover
│   └── Profile
└── Detail（详情页，可接收参数）
```

## 💻 组合实战：Stack + Tabs

```tsx
// navigation/RootNavigator.tsx
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

import Home from '../screens/Home';
import Discover from '../screens/Discover';
import Profile from '../screens/Profile';
import Detail from '../screens/Detail';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// 一级分区：底部标签
function MainTabs() {
  return (
    <Tab.Navigator screenOptions={{ headerShown: false }}>
      <Tab.Screen name="Home" component={Home} />
      <Tab.Screen name="Discover" component={Discover} />
      <Tab.Screen name="Profile" component={Profile} />
    </Tab.Navigator>
  );
}

// 外层：原生栈
export default function RootNavigator() {
  return (
    <Stack.Navigator initialRouteName="Main">
      <Stack.Screen name="Main" component={MainTabs} options={{ headerShown: false }} />
      <Stack.Screen
        name="Detail"
        component={Detail}
        options={{ title: '详情' }}
      />
    </Stack.Navigator>
  );
}
```

抽屉导航同理，把 `MainTabs` 换成 `Drawer.Navigator` 的内容即可；抽屉需在入口引入 `gesture-handler`：

```tsx
// App.tsx 顶部（drawer 方案必须）
import 'react-native-gesture-handler';
```

## 💻 页面传参与回调

```tsx
// screens/Detail.tsx
import { View, Text, Pressable } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

// 1. 声明参数类型（类型推导详见 TS 模式文档）
type RootStackParamList = {
  Detail: { itemId: string; from?: string };
};

type Props = NativeStackScreenProps<RootStackParamList, 'Detail'>;

export default function Detail({ route, navigation }: Props) {
  const { itemId, from } = route.params;

  return (
    <View style={{ flex: 1, padding: 16 }}>
      <Text>收到参数: {itemId}{from ? `（来自${from}）` : ''}</Text>
      {/* 2. 跳转传参 */}
      <Pressable onPress={() => navigation.push('Detail', { itemId: 'next' })}>
        <Text>再压一层 Detail</Text>
      </Pressable>
      {/* 3. 返回上一页 */}
      <Pressable onPress={() => navigation.goBack()}>
        <Text>返回</Text>
      </Pressable>
    </View>
  );
}
```

```tsx
// 发起跳转的一侧
navigation.navigate('Detail', { itemId: '42', from: 'Home' });
```

**navigate vs push**: `navigate` 对栈内已有同名页面做去重（回到它），`push` 无条件压新层。详情页套详情页用 `push`，普通跳转用 `navigate`。

## 🌍 三端导航差异

| 差异点 | Android | iOS | 鸿蒙 |
|--------|---------|-----|------|
| 返回手段 | 物理返回键/手势 | 边缘滑动手势 | 侧滑/手势导航 |
| 页面切换动画 | 平台默认（栈导航自动适配） | 平台默认 | RNOH 映射为 ArkUI 页面转场 |
| 头部样式 | Material 风格 | 大标题/毛玻璃 | 鸿蒙设计规范 |
| 深链 | `intent-filter` 配置 | Universal Links | `want` 隐式跳转配置 |

处理 Android 物理返回键：

```tsx
import { BackHandler } from 'react-native';
import { useEffect } from 'react';

useEffect(() => {
  const sub = BackHandler.addEventListener('hardwareBackPress', () => {
    // 返回 true 表示已自行处理（拦截），false 交给默认返回逻辑
    return false;
  });
  return () => sub.remove();
}, []);
```

栈导航器基于 `react-native-screens` 使用原生页面容器，返回手势/返回键默认已被正确处理；仅自定义"二次返回退出"等逻辑时才需要手动监听。

## 🎨 最佳实践

### ✅ 推荐做法
- **类型集中声明**: `RootStackParamList` 放在单一文件，全 App 共享，获得完整的类型推导
- **导航层级最多三层**: Stack > Tabs > 内部 Stack，超过就考虑拆模块或用 Modal
- **动画依赖提前装好**: Reanimated 需要 babel 插件，顺序装错会导致启动崩溃

### ❌ 避免陷阱
- **在导航器外使用 `useNavigation`**: 必须在 `NavigationContainer` 之内的组件里调用
- **参数里塞大对象**: 路由参数会被序列化，只传 id，数据从 store/query 取
- **忘记 `headerShown: false`**: Tabs/Drawer 外层再套 Stack 时出现双头部

## ❓ 常见问题

### Q1: 为什么跳转后页面是空白？
**A**: 检查 Screen 的 `component` 是否真的渲染了内容；再检查是否漏装 `react-native-screens`/`safe-area-context`；iOS 新工程还需重跑 `pod install`。

### Q2: 从推送点进来直接打开某页面（冷启动深链）怎么做？
**A**: 给 `NavigationContainer` 配 `linking` 映射 URL 与路由，完整 API 见 [navigation-essentials](../reference/framework-essentials/02-navigation-essentials.md)。

### Q3: 标签栏想中间凸起一个"发布"按钮？
**A**: 用 `Tab.Screen` 自定义 `tabBarButton` 渲染自定义按钮，样式细节参考 [02-components-props](../reference/language-concepts/02-components-props.md)。

## 🎯 练习与实践

### 练习一：三层导航骨架

**任务要求**:
1. 搭建 Stack + BottomTabs 结构，Tabs 含首页/发现/我的三个页面
2. 首页列表点击跳转 Detail 并传递 id，Detail 内再 `push` 一层 Detail

**评估标准**: 返回手势/返回键在每一层都表现正确。

### 练习二：Tab 间传值

**任务要求**:
1. "我的"页面修改昵称后，切回"首页"能看到最新昵称
2. 通过全局 store 或 Context 实现（路由参数无法跨 Tab）

**提示**: Tab 页面默认不销毁，切走再切回不会重执行 useEffect，这正是需要全局状态的原因。

---

## 🔗 相关文档

- 📄 **[原生模块桥接](./06-native-modules.md)**: 下一课，深入 JS 与原生边界
- 📄 **[React Navigation API 速查](../reference/framework-essentials/02-navigation-essentials.md)**: 导航器与 `linking` 全量 API
- 📄 **[TS 类型模式](../reference/language-concepts/04-typescript-patterns.md)**: ParamList 类型推导全解
- 📄 **[Hooks 速查](../reference/language-concepts/03-hooks-reference.md)**: `useNavigation`/`useRoute` 等导航 Hook

> 💡 **学习建议**: 先用最小结构（一个 Stack）跑通，再逐层加 Tabs 和 Drawer；每加一层都在真机上验证返回手势，导航问题一定要在三端真机上确认。
