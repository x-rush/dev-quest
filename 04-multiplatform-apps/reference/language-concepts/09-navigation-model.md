# 导航模型 — 路由、栈与页面状态机

> **难度**: ⭐ | **前置**: 读过[导航基础教程](../../basics/05-navigation.md)更佳，非必需

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#导航` `#路由` `#Stack` `#Tabs` `#深链` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

移动端导航的本质是**一棵导航器树 + 每个叶子（screen）的状态机**，与具体库无关：

- **导航器（navigator）**：管理一组 screen 的容器。三种基础拓扑，可任意嵌套：
  - **Stack（栈）**：压栈/出栈的层级关系，对应"进入详情、返回列表"
  - **Tabs（平铺）**：同级页面互切，各自保留独立状态与回退栈
  - **Drawer（抽屉）**：侧滑入口，本质是特殊动效的平铺切换
- **路由（route）**：`screen 名 + params` 的数据结构；页面切换就是路由进出各导航器的历史记录
- **params**：随路由传递的参数（可序列化值），是页面间的数据契约，**不是**全局状态
- **聚焦状态（focus）**：一个 screen 是否处于"用户正在看"的状态；被 Tab 切走或被新页面盖住时失焦，但**不卸载**

**典型嵌套**：根 Tabs → 每个 Tab 内一个 Stack → Stack 内 push 详情页。返回手势、深链、状态恢复全部由这棵树的形状决定。

## 📖 语法/签名

```tsx
// 路由操作的核心动词（库无关的心智模型）
navigation.navigate(name, params); // 导航到目标；是否复用路由由导航器、版本及身份配置决定
navigation.push(name, params);     // 压栈：即使已存在也新建一份
navigation.goBack();               // 出栈：回到历史中的上一条
navigation.popToTop();             // 清空当前栈回到栈底

// params 的读取与类型约定
type DetailParams = { id: string; from?: 'list' | 'search' };
const { id } = route.params as DetailParams;
```

```tsx
// 深链：URL ↔ 路由树的映射（scheme://tab/home/detail/42）
// 文件路由方案把上面的导航器树映射为目录结构，文件名即路由名
```

## 💡 示例

```tsx
// 聚焦状态：回到页面时刷新数据（这是移动端与 Web 最大的差异点）
import { useFocusEffect } from '@react-navigation/native';
import { useCallback } from 'react';

function FeedScreen() {
  useFocusEffect(
    useCallback(() => {
      refetch();                  // 每次聚焦执行
      return () => pausePolling(); // 失焦暂停，但组件并未卸载
    }, [refetch]),
  );
  return <FeedList />;
}
```

## ⚠️ 常见陷阱

- **navigate 与 push 混用**：连续 push 同一详情页会堆出"返回地狱"；需要回到已有路由时核对当前版本的 popTo 等明确语义
- **params 里塞大对象/函数**：params 必须可序列化（深链与状态恢复会把它变成字符串）；传 id、由目标页自取数据
- **以为离开页面 = 卸载**：Tab 切走、被盖住都只是失焦，订阅不清理会重复触发；出栈、导航树条件变化或组件身份变化都可能导致卸载
- **嵌套导航器找不到 screen**：导航操作通常先由当前导航器处理，未处理时可向父级冒泡；跨树跳转需写全目标导航器名
- **Android 返回键绕过应用内逻辑**：返回手势/返回键走的是导航器的 pop，拦截需用 preventRemove 类 API（未保存提示场景）

<!-- full-library-explanation -->
## 页面栈与应用状态的关系

同一个 Detail 组件可以在栈中出现多次，每次有不同 route key 和参数；组件名称不是实例身份。Tab 内的 Stack 保持自己的返回历史，Android 返回键则按导航树和平台规则处理。一个导航操作没有被当前导航器处理时，可能向父级冒泡，并非永远只影响最近父级。

练习：画出 Home → Detail(1) → Detail(2)，分别模拟 back、replace 和重置登录后的导航树。验收：返回不会进入已退出账户的私有页面；页面数据权限仍由服务端校验，删除导航记录不等于撤销会话。

聚焦、挂载、应用前后台是三个独立状态。页面可能挂载却未聚焦；应用进入后台时当前页面仍在导航树顶端。摄像头或轮询需要结合所需状态启停，而非只写一个“页面加载时执行”。

## 🔗 相关条目

- 📄 [导航基础教程](../../basics/05-navigation.md) — 从零建立导航的入门操作
- 📄 [React Navigation API 速查](../framework-essentials/02-navigation-essentials.md) — 导航器与 Hook 的完整清单
- 📄 [Expo 要点](../framework-essentials/01-expo-essentials.md) — 文件路由对导航树的映射
- 📄 [Hooks 速查](./03-hooks-reference.md) — useNavigation/useFocusEffect 签名

*延伸: React Navigation 官方文档 "Navigating without the navigation prop" · "Deep linking"*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
