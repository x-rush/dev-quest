# 原生通信：接口、线程与生命周期

前置：理解函数、Promise 和 React 组件。原生模块用来访问 JS 本身没有的设备或系统能力，例如读取应用版本。通信机制回答“如何调用”，模块实现还必须回答“在哪个线程执行、失败怎样返回、对象何时释放”。

## Bridge 与 JSI 的差别

旧桥主要通过批量异步消息交换可序列化的数据；历史上也有同步方法等例外，不应写成所有旧模块都只能回调。JSI 为 JS 引擎与原生实现提供直接交互接口，HostObject 可以向 JS 暴露原生对象行为。这不意味着任意两个运行时的内存都可以安全共享，也不意味着业务数据从此没有转换成本。

## 一个规格不等于一个实现

以下是 Codegen 输入形态示例，须放入配置过 Codegen 的 RN 原生工程，并补齐平台实现；复制一个 TS 文件不会自动创建原生模块。

```ts
// NativeDevice.ts
import type { TurboModule } from 'react-native';
import { TurboModuleRegistry } from 'react-native';

export interface Spec extends TurboModule {
  getDeviceName(): Promise<string>;
  isFeatureEnabledSync(): boolean;
}

export default TurboModuleRegistry.getEnforcing<Spec>('Device');
```

`getEnforcing` 在模块不存在时失败，适合必需能力；`get` 允许得到空值，调用前必须处理能力缺失。接口中的名称必须与原生注册一致。Codegen 只支持其规定的类型子集，不能任意使用复杂 TypeScript 类型。

## 同步、异步与取消

同步调用会让调用方等待返回，所以适合有上界的短操作。返回 Promise 只定义结果交付方式；实现是否把耗时操作移出关键线程，需要检查原生代码。页面离开后，请求可能仍在执行；要通过取消协议或忽略过期结果避免更新错误页面。

业务不应为了“更快”反复跨边界逐条读取一万个值。优先考虑有界批量接口，限制返回数据规模，并规定错误码、权限拒绝和不支持设备的结果。

## 自测：定位三类失败

1. JS 导入成功，调用时提示找不到 Device：检查构建是否包含原生模块及注册名称，热更新 JS 不能补上缺失的原生实现。
2. 方法返回 Promise 但点击仍卡住：检查方法返回 Promise 之前或原生主线程上是否执行重活。
3. 离开 A 页面再进入 B，A 的结果覆盖 B：按请求/资源身份处理过期结果，不能只靠类型声明。

练习：为读取设备信息写出“成功、权限拒绝、模块缺失、调用取消”四种契约和页面行为。验收标准是调用者不用猜测空字符串到底表示哪一种情况。

参考：[Turbo Native Modules](https://reactnative.dev/docs/turbo-native-modules-introduction)、[新架构解释](../../advanced-topics/architecture/01-new-architecture.md)。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
