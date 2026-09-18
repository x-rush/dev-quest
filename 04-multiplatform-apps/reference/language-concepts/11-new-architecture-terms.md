# 新架构术语字典：按职责查找

前置：读过 [通信原理](./08-bridge-principles.md)。查术语时先判断它属于执行、通信、构建还是渲染；这些名称不能互相替代。

| 术语 | 输入与输出 | 一个具体用途 | 常见误解 |
|---|---|---|---|
| Hermes | JS 程序/字节码 → 执行结果 | 运行事件处理函数 | 引擎不会自动优化业务算法 |
| JSI | JS 与原生接口调用 → 值或对象行为 | 暴露原生宿主函数 | 可同步不等于所有方法同步或线程安全 |
| TurboModule | 模块规格与实现 → JS 可调用能力 | 访问设备能力 | TS 接口文件本身不包含平台实现 |
| Fabric | React 描述与状态 → 平台视图更新 | 更新列表或文字布局 | 组件重渲染不等于全部视图重建 |
| Shadow Tree | 布局、属性等节点信息 → 布局后的树 | 计算一个 View 的尺寸位置 | 它不是浏览器 DOM |
| Codegen | 受支持的规格文件 → 接口代码 | 发现两端签名不一致 | 不能验证权限、业务规则和外部数据 |
| Yoga | 布局样式与约束 → 布局尺寸位置 | 计算 flex 布局 | 共用算法不消除字体和系统控件差异 |

## 必需模块与可选模块

这是消费端片段，前提是项目已完成原生模块注册和 Codegen，接口文件见通信原理文章。

```ts
import type { Spec } from './NativeDevice';
import { TurboModuleRegistry } from 'react-native';

const device = TurboModuleRegistry.get<Spec>('Device');
const enabled = device?.isFeatureEnabledSync() ?? false;
```

这里 `false` 明确是能力缺失时的产品兜底。对于加密、支付等不可缺少的能力，不应静默兜底；应报告当前构建不支持该操作。不要将 `get` 的可能为空结果直接当成对象调用。

## 版本与兼容性的阅读方法

先看工程实际依赖版本，再看对应版本文档和原生库支持矩阵。“新架构默认启用”和“该库在我的三端项目都正常运行”是两个结论。Expo SDK 与 RN 有兼容组合，不能凭较大的版本号随意混装。RNOH 的平台实现也应单独检查。

## 练习与反馈

把“按钮更新文字”“调用蓝牙模块”“构建时接口报错”“JS 无限循环”分别映射到上表。反馈：第一项追踪 React/Fabric，第二项看模块接口和平台实现，第三项看 Codegen 及原生构建，第四项看 JS 工作；不能都归因于 JSI。

继续阅读：[新架构解释](../../advanced-topics/architecture/01-new-architecture.md)、[RNOH](./05-harmonyos-rnoh-api.md)、[React Native 架构总览](https://reactnative.dev/architecture/landing-page)。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
